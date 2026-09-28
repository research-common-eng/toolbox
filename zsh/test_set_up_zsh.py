import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MOCK_COMMAND = r"""
import json
import os
from pathlib import Path
import subprocess
import sys
name = Path(sys.argv[0]).name
with open(os.environ["ZSH_TEST_LOG"], "a") as log:
    log.write(json.dumps([name, *sys.argv[1:]]) + "\n")
if name == os.environ.get("ZSH_TEST_FAIL"):
    sys.exit(17)
if name == "uname":
    print(os.environ["ZSH_TEST_OS"])
elif name == "id":
    print(os.environ["ZSH_TEST_UID"])
elif name == "sudo":
    sys.exit(subprocess.call(sys.argv[1:]))
elif name == "curl":
    print("exit 0")
"""


class ZshSetupTests(unittest.TestCase):
    def check_setup(self, platform, uid, location, fail=""):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source tree/zsh"
            shutil.copytree(Path(__file__).resolve().parent, source)
            install_home = root / "test home"
            install_home.mkdir()
            mock_bin = root / "bin"
            mock_bin.mkdir()
            # Only filesystem commands are real; no packages are installed.
            for name in ("bash", "sh", "cat", "cp", "mkdir", "dirname"):
                (mock_bin / name).symlink_to(shutil.which(name))
            for name in ("uname", "id", "brew", "apt-get", "sudo", "curl"):
                stub = mock_bin / name
                stub.write_text(f"#!{sys.executable}\n" + MOCK_COMMAND)
                stub.chmod(0o755)
            env = {
                "HOME": os.fspath(install_home),
                "PATH": os.fspath(mock_bin),
                "ZSH_TEST_OS": platform,
                "ZSH_TEST_UID": uid,
                "ZSH_TEST_LOG": os.fspath(root / "commands.log"),
                "ZSH_TEST_FAIL": fail,
            }
            cwd = {"repo": source.parent, "zsh": source, "elsewhere": root}[location]
            script = os.path.relpath(source / "set_up_zsh.sh", cwd)
            result = subprocess.run(
                ["/bin/bash", script],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=20,
            )
            if fail:
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((install_home / ".zshrc").exists())
                return
            self.assertEqual(result.returncode, 0, result.stderr)
            for config in (source / ".zsh").iterdir():
                self.assertEqual(
                    (install_home / ".zsh" / config.name).read_bytes(),
                    config.read_bytes(),
                )
            self.assertEqual(
                (install_home / ".config/starship.toml").read_bytes(),
                (source / ".config/starship.toml").read_bytes(),
            )
            self.assertIn(
                "source $HOME/.zsh/misc.zsh", (install_home / ".zshrc").read_text()
            )
            calls = [
                json.loads(line)
                for line in (root / "commands.log").read_text().splitlines()
            ]
            manager = "brew" if platform == "Darwin" else "apt-get"
            installs = [call for call in calls if call[:2] == [manager, "install"]]
            self.assertEqual(len(installs), 1)
            for package in (
                "fzf",
                "zoxide",
                "zsh-autosuggestions",
                "zsh-syntax-highlighting",
            ):
                self.assertIn(package, installs[0])
            if platform == "Linux":
                self.assertIn(["apt-get", "update"], calls)
                self.assertIn("zsh", installs[0])
                self.assertIn(
                    ["curl", "-fsSL", "https://starship.rs/install.sh"], calls
                )
                self.assertEqual(any(call[0] == "sudo" for call in calls), uid != "0")
                self.assertFalse(any(call[0] == "brew" for call in calls))

    def test_macos_and_linux_from_different_directories(self):
        for platform, uid in (("Darwin", "1000"), ("Linux", "0"), ("Linux", "1000")):
            for location in ("repo", "zsh", "elsewhere"):
                with self.subTest(platform=platform, uid=uid, cwd=location):
                    self.check_setup(platform, uid, location)

    def test_install_failures_stop_before_configuration(self):
        for platform, command in (
            ("Darwin", "brew"),
            ("Linux", "apt-get"),
            ("Linux", "curl"),
        ):
            with self.subTest(command=command):
                self.check_setup(platform, "0", "elsewhere", fail=command)


if __name__ == "__main__":
    unittest.main()
