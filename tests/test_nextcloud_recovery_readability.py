"""Read-only recovery-input traversal checks without disclosing content."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("nextcloud_readability", ROOT / "tools/nextcloud-recovery-readability.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Readability(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.html = root / "html"
        self.private = root / "private"
        for directory in (self.html / "config", self.html / "data" / "user" / "files",
                          self.html / "custom_apps", self.private):
            directory.mkdir(parents=True, exist_ok=True)
        (self.html / "config" / "config.php").write_text("CONFIDENTIAL-CONFIG")
        (self.html / "data" / "user" / "files" / "document.txt").write_text("CONFIDENTIAL-USER-DATA")
        for filename in module.producer.REQUIRED_PRIVATE:
            (self.private / filename).write_text("CONFIDENTIAL-CREDENTIAL")

    def test_scan_reports_counts_without_secret_content(self):
        report = module.check(self.html, self.private)
        self.assertEqual(report["html_regular_files"], 2)
        self.assertGreaterEqual(report["html_directories"], 4)
        self.assertEqual(report["private_required_files_readable"], 4)
        self.assertTrue(report["source_tree_readable_for_assembler_at_scan_time"])
        self.assertFalse(report["application_interrupted"])
        self.assertFalse(report["recovery_bundle_created"])
        self.assertFalse(report["consistent_snapshot_proven"])
        self.assertNotIn("CONFIDENTIAL", str(report))
        self.assertNotIn(str(self.html), str(report))
        self.assertNotIn(str(self.private), str(report))

    def test_linked_content_refuses_whole_tree(self):
        (self.html / "data" / "link").symlink_to(self.private, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "unsafe_source_member"):
            module.check(self.html, self.private)

    def test_missing_secret_refuses(self):
        (self.private / "postgresql-password").unlink()
        with self.assertRaises(module.SourceAccessRefused) as error:
            module.check(self.html, self.private)
        self.assertEqual(error.exception.stage, "private_inputs")
        self.assertEqual(error.exception.reason, "nonregular_or_linked_source")

    def test_private_symlink_is_categorized_without_exposing_target(self):
        password = self.private / "postgresql-password"
        password.unlink()
        password.symlink_to(self.html / "data" / "user" / "files" / "document.txt")
        with self.assertRaises(module.SourceAccessRefused) as error:
            module.check(self.html, self.private)
        self.assertEqual(error.exception.stage, "private_inputs")
        self.assertEqual(error.exception.reason, "nonregular_or_linked_source")
        self.assertNotIn(str(self.html), str(error.exception))

    def test_html_permission_failure_identifies_stage_without_private_path(self):
        private_path = str(self.html / "data" / "user" / "files" / "document.txt")
        with mock.patch.object(module.producer, "sorted_tree",
                               side_effect=PermissionError(private_path)):
            with self.assertRaises(module.SourceAccessRefused) as error:
                module.check(self.html, self.private)
        self.assertEqual(error.exception.stage, "html_tree")
        self.assertEqual(error.exception.reason, "permission_denied")
        self.assertNotIn(private_path, str(error.exception))

    def test_unrecognized_os_error_cannot_escape_as_a_path(self):
        error = OSError("private file: /home/user/secret-key.txt")
        self.assertEqual(module.safe_reason(error), "filesystem_error")
        self.assertEqual(module.safe_reason(ValueError("private value")), "invalid_source")


if __name__ == "__main__":
    unittest.main()
