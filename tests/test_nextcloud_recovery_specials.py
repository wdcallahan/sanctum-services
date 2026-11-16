"""Synthetic, read-only tests for private-safe Nextcloud special-entry classification."""
import importlib.util
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "nextcloud_recovery_specials", ROOT / "tools/nextcloud-recovery-specials.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class NextcloudRecoverySpecials(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "html"
        self.root.mkdir()
        for name in ("config", "data", "custom_apps", "other_place"):
            (self.root / name).mkdir()
        (self.root / "data" / "alice.txt").write_text("PRIVATE-Alice-Document")

    def test_classifies_special_members_and_link_targets_without_paths(self):
        (self.root / "data" / "inside").symlink_to("alice.txt")
        (self.root / "custom_apps" / "to_data").symlink_to("../data", target_is_directory=True)
        (self.root / "config" / "outside").symlink_to(self.root.parent, target_is_directory=True)
        (self.root / "config" / "missing").symlink_to("../unavailable-value")
        os.mkfifo(self.root / "data" / "pipe")

        report = module.classify(self.root)
        self.assertEqual(report["status"], "classified")
        self.assertEqual(report["special_entry_count"], 5)
        self.assertEqual(report["special_entry_types"]["symbolic_link"], 4)
        self.assertEqual(report["special_entry_types"]["fifo"], 1)
        self.assertEqual(report["special_entry_areas"]["data"]["fifo"], 1)
        self.assertEqual(report["special_entry_areas"]["custom_apps"]["symbolic_link"], 1)
        self.assertEqual(report["special_entry_areas"]["config"]["symbolic_link"], 2)
        self.assertEqual(report["symbolic_link_classification"]["absolute"], 1)
        self.assertEqual(report["symbolic_link_classification"]["relative"], 3)
        self.assertEqual(report["symbolic_link_classification"]["inside_root"], 2)
        self.assertEqual(report["symbolic_link_classification"]["outside_root"], 1)
        self.assertEqual(report["symbolic_link_classification"]["dangling"], 1)
        encoded = json.dumps(report)
        for sensitive in ("PRIVATE-Alice", "alice.txt", "to_data", str(self.root), "unavailable-value"):
            self.assertNotIn(sensitive, encoded)
        self.assertFalse(report["backup_created"])
        self.assertFalse(report["application_or_database_changed"])

    def test_plain_tree_is_reported_as_plain(self):
        report = module.classify(self.root)
        self.assertEqual(report["special_entry_count"], 0)
        self.assertEqual(report["ordinary_file_count"], 1)
        self.assertEqual(report["ordinary_directory_count"], 4)

    def test_symlinked_root_is_refused(self):
        linked = self.root.parent / "linked"
        linked.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "invalid_source_root"):
            module.classify(linked)

    def test_socket_is_special_and_never_opened(self):
        unix_socket_path = self.root / "other_place" / "hidden.sock"
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(unix_socket_path))
            result = module.classify(self.root)
        self.assertEqual(result["special_entry_types"]["socket"], 1)
        self.assertEqual(result["special_entry_areas"]["other"]["socket"], 1)

    def test_linked_directory_is_not_recursively_followed(self):
        external = self.root.parent / "external"
        external.mkdir()
        (external / "PRIVATE-ESCAPE").write_text("do not traverse")
        (self.root / "data" / "link_to_external").symlink_to(external, target_is_directory=True)
        result = module.classify(self.root)
        self.assertEqual(result["ordinary_file_count"], 1)
        self.assertEqual(result["special_entry_count"], 1)
        self.assertEqual(result["symbolic_link_classification"]["outside_root"], 1)


if __name__ == "__main__":
    unittest.main()
