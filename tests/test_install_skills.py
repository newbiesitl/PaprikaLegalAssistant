"""Behavioral checks for preserving existing local work during installation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install_skills.py"
spec = importlib.util.spec_from_file_location("legal_skill_install", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        for name in installer.LEGAL_SKILLS:
            p = self.root / "skills" / name
            p.mkdir(parents=True)
            (p / "SKILL.md").write_text(f"---\nname: {name}\ndescription: A test fixture.\n---\nBody.\n")
            (p / "references").mkdir()
            (p / "references/example.txt").write_text("Example / 範例\n", encoding="utf-8")

    def test_plan_does_not_create_state_and_install_is_idempotent(self):
        installer.install(self.root, dry_run=True)
        self.assertFalse((self.root / ".local").exists())
        self.assertFalse((self.root / ".agents").exists())
        installer.install(self.root)
        before = (self.root / ".local/legal-skill-install.json").read_bytes()
        again = installer.install(self.root)
        self.assertTrue(all(p["action"] == "unchanged" for p in again["skills"]))
        self.assertEqual(before, (self.root / ".local/legal-skill-install.json").read_bytes())

    def test_unmanaged_destination_is_preserved(self):
        p = self.root / ".agents/skills/legal-study"
        p.mkdir(parents=True)
        (p / "user.txt").write_text("Keep this")
        with self.assertRaises(installer.InstallError):
            installer.install(self.root)
        self.assertEqual("Keep this", (p / "user.txt").read_text())
        self.assertFalse((self.root / ".local").exists())

    def test_local_modification_blocks_without_overwrite(self):
        installer.install(self.root)
        p = self.root / ".agents/skills/legal-translation/SKILL.md"
        p.write_text("My edited procedure")
        with self.assertRaises(installer.InstallError):
            installer.install(self.root)
        self.assertEqual("My edited procedure", p.read_text())

    def test_pending_exact_copy_is_recovered_but_unknown_copy_is_not(self):
        installer.install(self.root)
        p = self.root / ".local/legal-skill-install.json"
        state = json.loads(p.read_text())
        state["skills"]["legal-study"]["status"] = "pending"
        p.write_text(json.dumps(state))
        result = installer.install(self.root)
        self.assertEqual("recover", result["skills"][0]["action"])
        self.assertEqual("installed", json.loads(p.read_text())["skills"]["legal-study"]["status"])

    def test_symlink_destination_is_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.root / ".agents").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this test host")
        with self.assertRaises(installer.InstallError):
            installer.install(self.root)
        self.assertEqual([], list(outside.iterdir()))


if __name__ == "__main__":
    unittest.main()
