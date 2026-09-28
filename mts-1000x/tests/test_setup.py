"""Exercise the installer in isolated directories on macOS and Linux."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "checkout with spaces"
        self.repo.mkdir()
        shutil.copy2(ROOT / "setup", self.repo / "setup")
        self.names = sorted(
            p.parent.name for p in ROOT.glob("*/SKILL.md.tmpl") if p.is_file()
        )
        for directory in ("scripts", "templates"):
            shutil.copytree(ROOT / directory, self.repo / directory)
        for name in self.names:
            shutil.copytree(ROOT / name, self.repo / name)
        self.target = self.base / "user's skills"
        self.env = {
            **os.environ,
            "HOME": str(self.base / "home"),
            "PATH": "/usr/bin:/bin",
        }
        self.env.pop("CODEX_HOME", None)

    def run_setup(self, *args, ok=True):
        result = subprocess.run(
            [str(self.repo / "setup"), *args],
            env=self.env,
            cwd=self.base,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def assert_installed(self, target):
        self.assertEqual(len(list(target.iterdir())), len(self.names))
        for name in self.names:
            link = target / name
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), (self.repo / name).resolve())
            content = (link / "SKILL.md").read_text()
            self.assertIn("\nname: " + name + "\n", content)
            self.assertIn("\ndescription: ", content)

    def test_install_repeat_and_uninstall_without_language_runtimes(self):
        for _ in range(2):
            self.run_setup("--target", str(self.target))
            self.assert_installed(self.target)
        foreign = self.target / "unrelated"
        foreign.mkdir()
        self.run_setup("--target", str(self.target), "--uninstall")
        self.assertEqual(list(self.target.iterdir()), [foreign])
        self.run_setup("--target", str(self.target), "--uninstall")

    def test_supported_and_unsupported_platforms(self):
        # Simulate the OS check; native runs exercise the host's shell utilities.
        bin_dir = self.base / "bin"
        bin_dir.mkdir()
        uname = bin_dir / "uname"
        self.env["PATH"] = str(bin_dir) + ":" + self.env["PATH"]
        for system in ("Darwin", "Linux", "FreeBSD"):
            with self.subTest(system=system):
                uname.write_text('#!/bin/sh\nprintf "%s\\n" ' + system + "\n")
                uname.chmod(0o755)
                target = self.base / system
                supported = system in ("Darwin", "Linux")
                result = self.run_setup("--target", str(target), ok=supported)
                if supported:
                    self.assert_installed(target)
                    self.run_setup("--target", str(target), "--uninstall")
                    self.assertEqual(list(target.iterdir()), [])
                else:
                    self.assertIn("Only macOS and Linux are supported", result.stderr)
                    self.assertFalse(target.exists())

    def test_default_and_codex_home(self):
        self.run_setup()
        self.assert_installed(Path(self.env["HOME"]) / ".codex/skills")
        self.env["CODEX_HOME"] = str(self.base / "custom codex")
        self.run_setup()
        self.assert_installed(Path(self.env["CODEX_HOME"]) / "skills")

    def test_project_and_relative_target(self):
        self.run_setup("--project")
        self.assert_installed(self.repo / ".agents/skills")
        self.run_setup("--target", "relative skills")
        self.assert_installed(self.base / "relative skills")

    def test_dry_run_creates_nothing_and_uninstall_preview_keeps_links(self):
        self.run_setup("--target", str(self.target), "--dry-run")
        self.assertFalse(self.target.exists())
        self.run_setup("--target", str(self.target))
        self.run_setup("--target", str(self.target), "--uninstall", "--dry-run")
        self.assert_installed(self.target)

    def test_conflicts_fail_before_installing_anything(self):
        for kind in ("file", "directory", "broken-link"):
            target = self.base / kind
            target.mkdir()
            conflict = target / self.names[-1]
            if kind == "file":
                conflict.write_text("keep")
            elif kind == "directory":
                conflict.mkdir()
            else:
                conflict.symlink_to(self.base / "missing")
            self.run_setup("--target", str(target), ok=False)
            self.assertEqual(list(target.iterdir()), [conflict])
            self.run_setup("--target", str(target), "--uninstall")
            self.assertEqual(list(target.iterdir()), [conflict])

    def test_invalid_arguments_do_not_write(self):
        for args in [
            ("--target",),
            ("--host", "claude"),
            ("--model", "gpt"),
            ("--skip-build",),
            ("--project", "--target", str(self.target)),
        ]:
            self.run_setup(*args, ok=False)
        self.assertFalse(self.target.exists())

    def test_discovers_new_skills_and_ignores_non_skill_folders(self):
        extra = self.repo / "new-skill"
        extra.mkdir()
        (extra / "SKILL.md.tmpl").write_text(
            "---\nname: {{SKILL_NAME}}\ndescription: Example\n---\n\n{{PREAMBLE}}\n"
        )
        (self.repo / "unrelated").mkdir()
        nested = self.repo / "unrelated/nested"
        nested.mkdir()
        (nested / "SKILL.md").write_text("not a root skill")
        self.names.append("new-skill")
        self.run_setup("--target", str(self.target))
        self.assert_installed(self.target)

    def test_empty_checkout_fails_without_writing(self):
        for name in self.names:
            shutil.rmtree(self.repo / name)
        result = self.run_setup("--target", str(self.target), ok=False)
        self.assertIn("No skill templates found", result.stderr)
        self.assertFalse(self.target.exists())

    def test_retired_links_are_pruned_but_foreign_links_survive(self):
        self.run_setup("--target", str(self.target))
        retired = self.target / "retired"
        retired.symlink_to(self.repo.resolve() / "retired")
        foreign = self.target / "foreign"
        foreign.symlink_to(self.base / "another-checkout/foreign")
        self.run_setup("--target", str(self.target), "--dry-run")
        self.assertTrue(retired.is_symlink())
        self.run_setup("--target", str(self.target))
        self.assertFalse(retired.is_symlink())
        self.assertTrue(foreign.is_symlink())
        retired.symlink_to(self.repo.resolve() / "retired")
        self.run_setup("--target", str(self.target), "--uninstall")
        self.assertEqual(list(self.target.iterdir()), [foreign])

    def legacy_links(self):
        self.target.mkdir()
        links = []
        for name in self.names:
            link = self.target / ("mts-1000x-" + name)
            link.symlink_to(self.repo.resolve() / name)
            links.append(link)
        return links

    def test_legacy_links_migrate_and_dry_run_preserves_them(self):
        links = self.legacy_links()
        self.run_setup("--target", str(self.target), "--dry-run")
        self.assertEqual(set(self.target.iterdir()), set(links))
        self.run_setup("--target", str(self.target))
        self.assert_installed(self.target)
        self.assertTrue(all(not link.is_symlink() for link in links))

    def test_migration_conflict_preserves_all_legacy_links(self):
        links = self.legacy_links()
        conflict = self.target / "review"
        conflict.write_text("keep")
        self.run_setup("--target", str(self.target), ok=False)
        self.assertEqual(set(self.target.iterdir()), {*links, conflict})
        self.assertTrue(all(link.is_symlink() for link in links))
        self.assertEqual(conflict.read_text(), "keep")

    def test_uninstall_removes_legacy_and_short_links_only_when_owned(self):
        self.legacy_links()
        self.target.joinpath("review").symlink_to(self.repo.resolve() / "review")
        foreign = self.target / "mts-1000x-foreign"
        foreign.symlink_to(self.base / "other/foreign")
        self.run_setup("--target", str(self.target), "--uninstall")
        self.assertEqual(list(self.target.iterdir()), [foreign])

    def run_generator(self, *args, ok=True):
        result = subprocess.run(
            [str(self.repo / "scripts/generate"), *args],
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_generation_is_deterministic_and_detects_stale_output(self):
        self.run_generator("--check")
        before = {n: (self.repo / n / "SKILL.md").read_bytes() for n in self.names}
        self.run_generator()
        self.assertEqual(
            before, {n: (self.repo / n / "SKILL.md").read_bytes() for n in self.names}
        )
        template = self.repo / "review/SKILL.md.tmpl"
        template.write_text(template.read_text() + "\nA new review instruction.\n")
        self.run_generator("--check", ok=False)
        self.run_setup("--target", str(self.target), "--dry-run")
        self.assertEqual((self.repo / "review/SKILL.md").read_bytes(), before["review"])
        self.run_setup("--target", str(self.target))
        self.assertIn(
            "A new review instruction.", (self.target / "review/SKILL.md").read_text()
        )
        self.run_generator("--check")

    def test_missing_outputs_are_regenerated_from_templates(self):
        for name in self.names:
            (self.repo / name / "SKILL.md").unlink()
        self.run_setup("--target", str(self.target))
        self.assert_installed(self.target)
        self.run_generator("--check")

    def test_shared_blocks_update_all_consumers(self):
        shared = self.repo / "templates/WORKFLOW_PREAMBLE.md"
        shared.write_text(shared.read_text() + "\nShared test instruction.\n")
        self.run_generator()
        for name in self.names:
            content = (self.repo / name / "SKILL.md").read_text()
            if name == "galaxy-brain-mts":
                self.assertNotIn("Shared test instruction.", content)
            else:
                self.assertIn("Shared test instruction.", content)

    def test_invalid_template_never_replaces_outputs_or_installs_links(self):
        first = self.repo / self.names[0] / "SKILL.md.tmpl"
        first.write_text(first.read_text() + "\nValid change.\n")
        last = self.repo / self.names[-1] / "SKILL.md.tmpl"
        last.write_text(last.read_text() + "\n{{UNKNOWN_DIRECTIVE}}\n")
        before = {n: (self.repo / n / "SKILL.md").read_bytes() for n in self.names}
        self.run_setup("--target", str(self.target), ok=False)
        self.assertFalse(self.target.exists())
        self.assertEqual(
            before, {n: (self.repo / n / "SKILL.md").read_bytes() for n in self.names}
        )

    def test_missing_references_fail_generation(self):
        (self.repo / "review/sections/plan-completion.md").unlink()
        self.assertIn("Missing or empty section", self.run_generator(ok=False).stderr)

    def test_missing_shared_block_fails_generation(self):
        (self.repo / "templates/PREAMBLE.md").unlink()
        self.run_generator(ok=False)

    def test_template_text_is_not_executed(self):
        sentinel = self.base / "should-not-exist"
        payload = '$(touch "' + str(sentinel) + '")'
        template = self.repo / "review/SKILL.md.tmpl"
        template.write_text(template.read_text() + "\n" + payload + "\n")
        self.run_generator()
        self.assertFalse(sentinel.exists())
        self.assertIn(payload, (self.repo / "review/SKILL.md").read_text())

    def test_project_state_is_shared_across_remote_protocols_without_writes(self):
        script = (
            (self.repo / "templates/PROJECT_STATE.md")
            .read_text()
            .split("```bash\n")[1]
            .split("```")[0]
        )
        paths = []
        for index, origin in enumerate(
            (
                "https://github.com/example/project.git",
                "git@github.com:example/project.git",
            )
        ):
            repo = self.base / ("project " + str(index))
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], env=self.env, check=True)
            subprocess.run(
                ["git", "-C", str(repo), "remote", "add", "origin", origin],
                env=self.env,
                check=True,
            )
            result = subprocess.run(
                ["/bin/bash", "-eu", "-c", script],
                cwd=repo,
                env=self.env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            paths.append(result.stdout.strip())
        self.assertEqual(paths[0], paths[1])
        self.assertFalse((Path(self.env["HOME"]) / ".codex").exists())

    def test_project_state_separates_unrelated_local_repositories(self):
        script = (
            (self.repo / "templates/PROJECT_STATE.md")
            .read_text()
            .split("```bash\n")[1]
            .split("```")[0]
        )
        paths = []
        for index in range(2):
            repo = self.base / ("local " + str(index))
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], env=self.env, check=True)
            result = subprocess.run(
                ["/bin/bash", "-eu", "-c", script],
                cwd=repo,
                env=self.env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            paths.append(result.stdout.strip())
        self.assertNotEqual(paths[0], paths[1])

    def test_skill_package_metadata_references_and_no_upstream_hooks(self):
        for name in self.names:
            root = self.repo / name
            content = (root / "SKILL.md").read_text()
            frontmatter = content.split("---", 2)[1]
            self.assertIn("name: " + name, frontmatter)
            self.assertRegex(frontmatter, r'description: "[^"\n]+"')
            self.assertNotRegex(content, r"\{\{[A-Z_]+")
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                self.assertIn(path.suffix, (".md", ".tmpl"))
                text = path.read_text()
                for forbidden in (
                    "gstack",
                    "bun run",
                    ".claude",
                    "gbrain",
                    "aside repl",
                ):
                    self.assertNotIn(forbidden, text.lower(), str(path))
                # Check real packaged links, not placeholders in example docs.
                for relative in re.findall(
                    r"\]\(((?:sections|specialists|references|templates|\.\./)[^ )]+\.md)\)",
                    text,
                ):
                    self.assertTrue(
                        (path.parent / relative).is_file(), (path, relative)
                    )


if __name__ == "__main__":
    unittest.main()
