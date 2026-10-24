"""Regression coverage for safe, reproducible plugin archive staging."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_plugin.py"
spec = importlib.util.spec_from_file_location("legal_plugin_builder", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PluginBuildTests(unittest.TestCase):
    def test_predictable_temp_symlink_is_preserved_and_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            root = work / "source"
            root.mkdir()
            (root / "plugin.json").write_text(
                json.dumps({"name": "example-legal", "version": "0.1.0"}),
                encoding="utf-8",
            )
            (root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
            (root / "THIRD_PARTY_NOTICES.md").write_text("Fixture notices\n", encoding="utf-8")
            (root / "provenance").mkdir()
            for index in range(9):
                skill = root / "skills" / f"workflow-{index}"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("Synthetic skill / 範例技能\n", encoding="utf-8")

            output = work / "release.zip"
            victim = work / "unrelated-notes.txt"
            marker = b"Preserve this unrelated file."
            victim.write_bytes(marker)
            predictable = output.with_suffix(output.suffix + ".tmp")
            try:
                predictable.symlink_to(victim)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable on this test host")

            first = builder.build(root, output)
            first_bytes = output.read_bytes()
            self.assertEqual(marker, victim.read_bytes())
            self.assertTrue(predictable.is_symlink())
            self.assertEqual(victim, predictable.readlink())
            self.assertFalse(output.is_symlink())
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())

            second = builder.build(root, output)
            self.assertEqual(first["sha256"], second["sha256"])
            self.assertEqual(first_bytes, output.read_bytes())
            self.assertEqual(marker, victim.read_bytes())
            self.assertTrue(predictable.is_symlink())


if __name__ == "__main__":
    unittest.main()
