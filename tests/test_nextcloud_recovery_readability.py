"""Read-only recovery-input traversal checks without disclosing content."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

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
        with self.assertRaises(ValueError):
            module.check(self.html, self.private)


if __name__ == "__main__":
    unittest.main()
