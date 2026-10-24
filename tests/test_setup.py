"""Safety and repeatability checks for the real dependency preparation boundary.

Fixtures replace only the pinned bytes, so the tests need no network or account.
"""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "setup.py"
SPEC = importlib.util.spec_from_file_location("legal_setup", MODULE_PATH)
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-setup-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repository with spaces"
        self.repo.mkdir()
        (self.repo / ".gitignore").write_text("/.local/\n", encoding="utf-8")
        (self.repo / "onboarding").mkdir()
        real_lock = json.loads((MODULE_PATH.parents[1] / setup.LOCK_FILE).read_text(encoding="utf-8"))
        self.dep = real_lock["paprika_inc"].copy()
        self.archive = self.root / "release.zip"
        self.write_archive()

    def write_archive(self, extra=()):
        with zipfile.ZipFile(self.archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("paprika-inc/plugin.json", json.dumps({"name": "paprika-inc", "version": "0.3.4"}))
            archive.writestr("paprika-inc/skills/paprika-inc/scripts/inc.mjs", "// inert fixture\n")
            archive.writestr("paprika-inc/LICENSE", "fixture license\n")
            for path, body in extra:
                archive.writestr(path, body)
        self.dep["archive_size"] = self.archive.stat().st_size
        self.dep["archive_sha256"] = setup.digest(self.archive)
        (self.repo / setup.LOCK_FILE).write_text(json.dumps({"schema_version": 1, "paprika_inc": self.dep}), encoding="utf-8")

    def target(self):
        return setup.dependency_directory(self.repo, self.dep)

    def test_verified_prepare_is_idempotent_and_does_not_install(self):
        first = setup.prepare(self.repo, self.dep, self.archive)
        receipt = self.target() / "receipt.json"
        previous_time = receipt.stat().st_mtime_ns
        second = setup.prepare(self.repo, self.dep, self.archive)
        self.assertEqual(first["state"], "prepared")
        self.assertEqual(second["state"], "reused")
        self.assertFalse(second["globally_installed"])
        self.assertFalse(second["account_connected"])
        self.assertEqual(receipt.stat().st_mtime_ns, previous_time)
        self.assertEqual(setup.verify_prepared(self.target(), self.dep), Path(second["inc_helper"]))

    def test_checksum_mismatch_does_not_leave_a_prepared_dependency(self):
        self.archive.write_bytes(self.archive.read_bytes() + b"changed")
        with self.assertRaisesRegex(setup.SetupError, "SHA256 mismatch"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertFalse(self.target().exists())
        self.assertFalse(list(self.target().parent.glob("*.lock")))
        self.assertFalse(list(self.target().parent.glob("*.staging-*")))

    def test_modified_dependency_is_preserved_and_rejected(self):
        setup.prepare(self.repo, self.dep, self.archive)
        helper = self.target() / "paprika-inc/skills/paprika-inc/scripts/inc.mjs"
        helper.write_text("// owner modification\n", encoding="utf-8")
        with self.assertRaises(setup.SetupError):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertEqual(helper.read_text(encoding="utf-8"), "// owner modification\n")

    def test_extra_file_is_preserved_and_rejected(self):
        setup.prepare(self.repo, self.dep, self.archive)
        extra = self.target() / "paprika-inc/owner-note.txt"
        extra.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(setup.SetupError, "extra files"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertEqual(extra.read_text(encoding="utf-8"), "keep")

    def test_unmanaged_destination_is_not_overwritten(self):
        self.target().mkdir(parents=True)
        marker = self.target() / "owner.txt"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaises(setup.SetupError):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_traversal_is_rejected_before_extraction(self):
        self.write_archive([("paprika-inc/../../escaped.txt", "bad")])
        with self.assertRaisesRegex(setup.SetupError, "traversal"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertFalse(self.target().exists())
        self.assertFalse((self.repo / ".local/dependencies/escaped.txt").exists())

    def test_archive_symlink_is_rejected(self):
        link = zipfile.ZipInfo("paprika-inc/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.write_archive([(link, "../../outside")])
        with self.assertRaisesRegex(setup.SetupError, "symlinks"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertFalse(self.target().exists())

    def test_case_collision_is_rejected(self):
        self.write_archive([("paprika-inc/license", "different")])
        with self.assertRaisesRegex(setup.SetupError, "case-colliding"):
            setup.prepare(self.repo, self.dep, self.archive)

    def test_portability_hazards_are_rejected(self):
        for value in ("/absolute", "paprika-inc/../escape", "paprika-inc/C:stream", "paprika-inc/CON.txt", "paprika-inc/trailing.", "paprika-inc\\bad"):
            with self.subTest(value=value), self.assertRaises(setup.SetupError):
                setup.member_path(value, "paprika-inc")

    def test_symlink_in_destination_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.repo / ".local").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is not permitted on this host")
        with self.assertRaisesRegex(setup.SetupError, "symlink"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertEqual(list(outside.iterdir()), [])

    def test_existing_lock_is_not_removed_or_stolen(self):
        self.target().parent.mkdir(parents=True)
        lock = self.target().parent / ".0.3.4.prepare.lock"
        lock.write_text("other run", encoding="utf-8")
        with self.assertRaisesRegex(setup.SetupError, "lock exists"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertEqual(lock.read_text(encoding="utf-8"), "other run")

    def test_plan_has_no_filesystem_or_network_side_effects(self):
        with patch.object(setup, "download", side_effect=AssertionError("network called")), contextlib.redirect_stdout(io.StringIO()) as output:
            code = setup.main(["--repo", str(self.repo), "plan"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output.getvalue())["read_only"])
        self.assertFalse((self.repo / ".local").exists())

    def test_doctor_reports_pending_without_mutation(self):
        with patch.object(setup, "executable_version", return_value={"available": False}):
            result = setup.doctor(self.repo, self.dep)
        self.assertFalse(result["local_inc_commands_ready"])
        self.assertEqual(result["dependency"]["state"], "not_prepared")
        self.assertFalse((self.repo / ".local").exists())

    def test_unignored_destination_is_blocked(self):
        (self.repo / ".gitignore").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(setup.SetupError, "gitignore"):
            setup.prepare(self.repo, self.dep, self.archive)
        self.assertFalse((self.repo / ".local").exists())

    def test_lock_cannot_redirect_download_to_arbitrary_server(self):
        value = json.loads((self.repo / setup.LOCK_FILE).read_text(encoding="utf-8"))
        value["paprika_inc"]["archive_url"] = "https://example.invalid/arbitrary.zip"
        (self.repo / setup.LOCK_FILE).write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(setup.SetupError, "metadata"):
            setup.load_dependency(self.repo)

    def test_failed_download_cleans_only_its_staging_files(self):
        with patch.object(setup, "download", side_effect=setup.SetupError("offline")):
            with self.assertRaisesRegex(setup.SetupError, "offline"):
                setup.prepare(self.repo, self.dep)
        self.assertFalse(self.target().exists())
        self.assertEqual(list(self.target().parent.iterdir()), [])

    def test_research_source_must_match_the_pack_that_will_install(self):
        skill = self.repo / "skills/paper-lookup/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("reviewed fixture", encoding="utf-8")
        pack_path = self.target() / "paprika-inc/runtime/skill-packs/research-core/pack.json"
        pack_path.parent.mkdir(parents=True)
        pack_path.write_text(json.dumps({"skills": ["paper-lookup"], "files": [{"path": "paper-lookup/SKILL.md", "sha256": setup.digest(skill)}]}), encoding="utf-8")
        self.dep["research_pack_sha256"] = setup.digest(pack_path)
        setup.verify_research_source(self.repo, self.target(), self.dep)
        skill.write_text("local source change", encoding="utf-8")
        with self.assertRaisesRegex(setup.SetupError, "Canonical research source differs"):
            setup.verify_research_source(self.repo, self.target(), self.dep)

    def test_extra_research_source_is_not_silently_ignored(self):
        skill = self.repo / "skills/paper-lookup/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("reviewed fixture", encoding="utf-8")
        pack_path = self.target() / "paprika-inc/runtime/skill-packs/research-core/pack.json"
        pack_path.parent.mkdir(parents=True)
        pack_path.write_text(json.dumps({"skills": ["paper-lookup"], "files": [{"path": "paper-lookup/SKILL.md", "sha256": setup.digest(skill)}]}), encoding="utf-8")
        self.dep["research_pack_sha256"] = setup.digest(pack_path)
        (skill.parent / "extra.txt").write_text("owner addition", encoding="utf-8")
        with self.assertRaisesRegex(setup.SetupError, "extra files"):
            setup.verify_research_source(self.repo, self.target(), self.dep)


if __name__ == "__main__":
    unittest.main()
