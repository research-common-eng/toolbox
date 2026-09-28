import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tomlkit
from configure_agentsview import configure

MOCK_COMMAND = r"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
name = Path(sys.argv[0]).name
with open(os.environ["STARTUP_TEST_LOG"], "a") as log:
    log.write(json.dumps([name, *sys.argv[1:]]) + "\n")
if name == "nohup":
    Path(os.environ["STARTUP_TEST_PID"]).write_text(str(os.getpid()))
    if os.environ["STARTUP_TEST_CRASH"] == "1":
        sys.exit(23)
    time.sleep(30)
elif name == "sleep":
    time.sleep(0.5)
elif name == "curl":
    print("exit 0")
elif name == "uv":
    sys.exit(subprocess.call([sys.executable, *sys.argv[3:]]))
elif name == "agentsview":
    import tomlkit
    config = tomlkit.parse((Path(os.environ["HOME"]) / ".agentsview/config.toml").read_text())
    assert config["public_url"] == "http://127.0.0.1:9000"
    assert config["daemon_idle_timeout"] == "0s"
elif name == "bash" and len(sys.argv) > 1:
    sys.exit(subprocess.call(["/bin/bash", *sys.argv[1:]]))
"""


class StartupTests(unittest.TestCase):
    def check_startup(
        self, location, setup_status=0, check_handoff=False, server_crash=False
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "source tree"
            (repo / "runpod").mkdir(parents=True)
            shutil.copyfile(
                Path(__file__).with_name("configure_agentsview.py"),
                repo / "runpod/configure_agentsview.py",
            )
            (repo / "zsh").mkdir()
            (repo / "codex").mkdir()
            shutil.copyfile(
                Path(__file__).resolve().parent.parent / "codex/config.toml",
                repo / "codex/config.toml",
            )
            script = repo / "runpod/startup.sh"
            script.write_text(
                Path(__file__)
                .with_name("startup.sh")
                .read_text()
                .replace("/workspace/logs", str(root / "logs"))
            )
            (repo / "zsh/set_up_zsh.sh").write_text(
                f'printf "shared setup ran\\n"\nexit {setup_status}\n'
            )
            mock_bin = root / "bin"
            mock_bin.mkdir()
            for name in ("dirname", "date", "sh", "cat", "grep", "mkdir", "cp"):
                (mock_bin / name).symlink_to(shutil.which(name))
            for name in (
                "sudo",
                "npm",
                "curl",
                "bash",
                "nohup",
                "sleep",
                "uv",
                "agentsview",
            ):
                stub = mock_bin / name
                stub.write_text(f"#!{sys.executable}\n" + MOCK_COMMAND)
                stub.chmod(0o755)
            log_path = root / "commands.log"
            install_home = root / "test home"
            install_home.mkdir()
            bashrc = install_home / ".bashrc"
            bashrc.write_text("# Existing configuration\n")
            env = {
                "PATH": str(mock_bin),
                "HOME": str(install_home),
                "STARTUP_TEST_LOG": str(log_path),
                "STARTUP_TEST_PID": str(root / "server.pid"),
                "STARTUP_TEST_CRASH": str(int(server_crash)),
            }
            cwd = {"repo": repo, "runpod": repo / "runpod", "elsewhere": root}[location]
            result = subprocess.run(
                ["/bin/bash", os.path.relpath(script, cwd)],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=20,
            )

            def stop_server():
                pid_file = root / "server.pid"
                if pid_file.exists():
                    try:
                        os.kill(int(pid_file.read_text()), signal.SIGTERM)
                    except ProcessLookupError:
                        pass

            stop_server()
            expected_status = setup_status or int(server_crash)
            self.assertEqual(result.returncode, expected_status, result.stderr)
            self.assertEqual(result.stdout.count("shared setup ran"), 1)
            calls = [json.loads(line) for line in log_path.read_text().splitlines()]
            self.assertIn(["sudo", "apt", "install", "-y", "screen", "tmux"], calls)
            downloads = [call for call in calls if call[0] == "curl"]
            expected_downloads = [["curl", "-LsSf", "https://astral.sh/uv/install.sh"]]
            if expected_status == 0:
                expected_downloads.append(
                    ["curl", "-fsSL", "https://agentsview.io/install.sh"]
                )
            self.assertEqual(downloads, expected_downloads)
            self.assertEqual(["bash"] in calls, expected_status == 0)
            self.assertEqual(
                ["agentsview", "daemon", "start"] in calls, expected_status == 0
            )
            self.assertEqual(
                "Pod setup complete" in result.stderr, expected_status == 0
            )
            self.assertTrue(bashrc.read_text().startswith("# Existing configuration\n"))
            marker = "# Start Zsh in interactive Bash sessions."
            self.assertEqual(bashrc.read_text().count(marker), int(setup_status == 0))

            if setup_status == 0:
                self.assertIn(
                    ["sudo", "add-apt-repository", "-y", "ppa:jgmath2000/et"], calls
                )
                self.assertTrue((root / "logs/default/etserver.log").exists())
                if server_crash:
                    self.assertIn(
                        "ERROR: etserver exited during startup", result.stderr
                    )
                else:
                    self.assertIn("Eternal Terminal server started (PID", result.stderr)

            if check_handoff:
                subprocess.run(
                    ["/bin/bash", str(script)],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=20,
                )
                stop_server()
                self.assertEqual(bashrc.read_text().count(marker), 1)

                def run_bash(interactive):
                    return subprocess.run(
                        [
                            "/bin/bash",
                            "--noprofile",
                            "--norc",
                            "-ic" if interactive else "-c",
                            '. "$HOME/.bashrc"; printf "bash remained"',
                        ],
                        cwd=root,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=20,
                    )

                # Without Zsh, an interactive shell remains usable.
                self.assertEqual(run_bash(True).stdout, "bash remained")
                zsh = mock_bin / "zsh"
                zsh.write_text(f"#!{sys.executable}\n" + MOCK_COMMAND)
                zsh.chmod(0o755)
                self.assertEqual(run_bash(False).stdout, "bash remained")
                self.assertEqual(run_bash(True).stdout, "")
                env["ZSH_VERSION"] = "test-zsh"
                self.assertEqual(run_bash(True).stdout, "bash remained")
                calls = [json.loads(line) for line in log_path.read_text().splitlines()]
                self.assertEqual(
                    [call for call in calls if call[0] == "zsh"], [["zsh", "-i"]]
                )

    def test_shared_setup_from_different_directories(self):
        for location in ("repo", "runpod", "elsewhere"):
            with self.subTest(location=location):
                self.check_startup(location)

    def test_etserver_startup_failure_stops_setup(self):
        self.check_startup("elsewhere", server_crash=True)

    def test_shared_setup_failure_stops_startup(self):
        self.check_startup("elsewhere", setup_status=17)

    def test_bashrc_handoff_is_guarded_and_not_duplicated(self):
        self.check_startup("elsewhere", check_handoff=True)


class AgentsviewConfigTests(unittest.TestCase):
    def test_updates_root_keys_and_preserves_other_configuration(self):
        originals = [
            "",
            '# Keep this comment\n"public_url"= "old" # URL comment\n'
            "daemon_idle_timeout = '5m'\nother = true\n",
            '[server]\npublic_url = "nested"\ndaemon_idle_timeout = "10m"\n',
            'public_url = "old"\n[server]\nport = 8080\n',
            'note = """\n[not_a_table]\npublic_url = "text"\n"""\n',
        ]
        for original in originals:
            with self.subTest(original=original), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "config.toml"
                if original:
                    path.write_text(original)
                expected = tomlkit.parse(original).unwrap()
                expected.update(
                    public_url="http://127.0.0.1:9000", daemon_idle_timeout="0s"
                )
                configure(path)
                result = path.read_text()
                self.assertEqual(tomlkit.parse(result).unwrap(), expected)
                if "# Keep this comment" in original:
                    self.assertIn("# Keep this comment", result)
                    self.assertIn("# URL comment", result)
                configure(path)
                self.assertEqual(path.read_text(), result)

    def test_invalid_config_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            original = 'public_url = "one"\npublic_url = "two"\n'
            path.write_text(original)
            with self.assertRaises(tomlkit.exceptions.ParseError):
                configure(path)
            self.assertEqual(path.read_text(), original)


if __name__ == "__main__":
    unittest.main()
