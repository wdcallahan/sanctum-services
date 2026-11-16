"""Offline synthetic tests for the Nextcloud private bundle producer."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("nextcloud_assemble", ROOT / "tools/nextcloud-recovery-assemble.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NextcloudRecoveryAssemble(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        base = Path(self.workspace.name)
        self.html = base / "html"
        self.private = base / "private"
        self.dump = base / "nextcloud.dump"
        self.output = base / "bundle"
        for path in (self.html / "config", self.html / "data" / "alice" / "files",
                     self.html / "custom_apps" / "calendar", self.private):
            path.mkdir(parents=True, exist_ok=True)
        (self.html / "config" / "config.php").write_text("PRIVATE CONFIG")
        (self.html / "data" / "alice" / "files" / "example.txt").write_text("PRIVATE DATA")
        (self.html / "custom_apps" / "calendar" / "marker").write_text("app")
        for name in module.REQUIRED_PRIVATE:
            (self.private / name).write_text("SECRET " + name)
        self.dump.write_bytes(b"PGDMP" + b"NOT A REAL DATABASE" * 3)

    def assemble(self):
        return module.assemble(self.html, self.private, self.dump, self.output)

    def test_private_bundle_is_assembled_and_integrity_validated(self):
        result = self.assemble()
        self.assertTrue(result["archive_and_dump_hashes_match_manifest"])
        self.assertTrue(result["nextcloud_required_paths_present_in_archive"])
        self.assertFalse(result["consistent_snapshot_proven"])
        self.assertFalse(result["database_restore_tested"])
        self.assertFalse(result["application_restore_accepted"])
        self.assertFalse(result["independent_off_host_retention_proven"])
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
        for path in self.output.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        with tarfile.open(self.output / "nextcloud-html.tar") as archive:
            names = archive.getnames()
            self.assertIn("data/alice/files/example.txt", names)
            self.assertIn("custom_apps/calendar/marker", names)
            self.assertIn("config/config.php", names)
        with tarfile.open(self.output / "nextcloud-private.tar") as archive:
            self.assertEqual(set(archive.getnames()), set(module.REQUIRED_PRIVATE))
        text = json.dumps(result)
        self.assertNotIn("PRIVATE CONFIG", text)
        self.assertNotIn("PRIVATE DATA", text)
        self.assertNotIn("SECRET", text)

    def test_missing_required_state_rejected_before_output(self):
        (self.html / "config" / "config.php").unlink()
        with self.assertRaises(ValueError):
            self.assemble()
        self.assertFalse(self.output.exists())

    def test_contained_relative_links_are_preserved_and_verified(self):
        (self.html / "apps").mkdir()
        (self.html / "apps" / "calendar").symlink_to(
            "../custom_apps/calendar", target_is_directory=True)
        (self.html / "apps" / "config").symlink_to("../config/config.php")
        report = self.assemble()
        self.assertTrue(report["archive_and_dump_hashes_match_manifest"])
        self.assertEqual(report["internal_relative_symlinks_verified"], 2)
        with tarfile.open(self.output / "nextcloud-html.tar") as archive:
            directory_link = archive.getmember("apps/calendar")
            self.assertTrue(directory_link.issym())
            self.assertEqual(directory_link.linkname, "../custom_apps/calendar")
            file_link = archive.getmember("apps/config")
            self.assertTrue(file_link.issym())
            self.assertEqual(file_link.linkname, "../config/config.php")
            self.assertFalse(any(name.startswith("apps/calendar/") for name in archive.getnames()))

    def test_external_absolute_link_never_enters_archive(self):
        (self.html / "data" / "escape").symlink_to(self.private, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "unsafe_source_link"):
            self.assemble()
        self.assertFalse((self.output / "manifest.json").exists())

    def test_internal_absolute_link_rejected_even_when_target_contained(self):
        (self.html / "custom_apps" / "bad").symlink_to(
            self.html / "config" / "config.php")
        with self.assertRaisesRegex(ValueError, "unsafe_source_link"):
            self.assemble()

    def test_internal_dangling_link_rejected(self):
        (self.html / "custom_apps" / "bad").symlink_to("../missing")
        with self.assertRaisesRegex(ValueError, "unsafe_source_link"):
            self.assemble()

    def test_cyclic_links_rejected(self):
        (self.html / "custom_apps" / "a").symlink_to("b")
        (self.html / "custom_apps" / "b").symlink_to("a")
        with self.assertRaisesRegex(ValueError, "unsafe_source_link"):
            self.assemble()

    def test_special_fifo_rejected(self):
        os.mkfifo(self.html / "data" / "unarchiveable")
        with self.assertRaisesRegex(ValueError, "unsafe_source_member"):
            self.assemble()

    def test_relative_lexical_escape_not_accepted(self):
        (self.html / "data" / "escape").symlink_to(
            "../../../" + self.html.name + "/config/config.php")
        with self.assertRaisesRegex(ValueError, "unsafe_source_link"):
            self.assemble()

    def test_linked_private_credential_is_rejected_before_output(self):
        path = self.private / "postgresql-password"
        path.unlink()
        path.symlink_to(self.dump)
        with self.assertRaisesRegex(ValueError, "nonregular_or_linked_source"):
            self.assemble()
        self.assertFalse(self.output.exists())

    def test_unreadable_subtree_fails_closed_instead_of_silent_skip(self):
        def unreadable_walk(root, followlinks=False, onerror=None):
            self.assertIsNotNone(onerror)
            onerror(PermissionError("unreadable private subtree"))
            yield ()  # os.walk is a generator; error occurs during iteration

        with mock.patch.object(module.os, "walk", side_effect=unreadable_walk):
            with self.assertRaises(PermissionError):
                self.assemble()
        self.assertFalse((self.output / "manifest.json").exists())

    def test_output_cannot_be_inside_application_source(self):
        with self.assertRaisesRegex(ValueError, "output_inside_source"):
            module.assemble(self.html, self.private, self.dump, self.html / "backup")
        self.assertFalse((self.html / "backup").exists())

    def test_existing_output_never_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / "keep"
        sentinel.write_text("unchanged")
        with self.assertRaisesRegex(ValueError, "output_already_exists"):
            self.assemble()
        self.assertEqual(sentinel.read_text(), "unchanged")

    def test_non_custom_database_rejected_without_false_success(self):
        self.dump.write_bytes(b"plain text isn't custom pg dump")
        with self.assertRaisesRegex(ValueError, "database_dump_not_custom_format"):
            self.assemble()
        self.assertFalse((self.output / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
