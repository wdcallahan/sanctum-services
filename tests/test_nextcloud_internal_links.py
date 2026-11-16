"""Archive-metadata-only link checks: preserve internal links, deny tar escapes."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "nextcloud_bundle", ROOT / "tools/nextcloud-recovery-bundle.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MARKERS = {"config/config.php", "data", "custom_apps"}
BASE = [
    ("file", "config/config.php", b"private config"),
    ("dir", "config", None),
    ("dir", "data", None),
    ("dir", "custom_apps", None),
    ("dir", "apps", None),
    ("file", "data/file.txt", b"private data"),
    ("dir", "custom_apps/calendar", None),
    ("file", "custom_apps/calendar/app.txt", b"calendar"),
]


class InternalLinkContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "app.tar"

    def make_tar(self, extra=(), kind="application"):
        with tarfile.open(self.archive, "w") as archive:
            for type_name, name, data in [*BASE, *extra]:
                info = tarfile.TarInfo(name)
                if type_name == "file":
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
                elif type_name == "dir":
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    archive.addfile(info)
                elif type_name == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = data
                    archive.addfile(info)
                elif type_name == "hardlink":
                    info.type = tarfile.LNKTYPE
                    info.linkname = data
                    archive.addfile(info)
                else:
                    raise AssertionError("bad fixture kind")
        return module.verify_tar(self.archive, MARKERS,
                                 allow_internal_links=(kind == "application"))

    def test_internal_file_directory_and_multihop_links_accepted(self):
        links = [
            ("symlink", "apps/direct", "../data/file.txt"),
            ("symlink", "apps/calendar", "../custom_apps/calendar"),
            ("symlink", "apps/alias", "direct"),
            ("symlink", "apps/alias_dir", "calendar"),
        ]
        self.assertEqual(self.make_tar(links), 4)

    def test_absolute_link_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe_archive_member"):
            self.make_tar([("symlink", "apps/bad", "/etc/passwd")])

    def test_relative_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe_archive_member"):
            self.make_tar([("symlink", "apps/bad", "../../../etc/passwd")])

    def test_missing_internal_target_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing_internal_link_target"):
            self.make_tar([("symlink", "apps/missing", "../data/not-backed-up.txt")])

    def test_cyclic_links_rejected(self):
        with self.assertRaisesRegex(ValueError, "cyclic_or_excessive_archive_links"):
            self.make_tar([
                ("symlink", "apps/a", "b"),
                ("symlink", "apps/b", "a"),
            ])

    def test_archive_member_beneath_link_rejected_regardless_of_order(self):
        with self.assertRaisesRegex(ValueError, "archive_path_descends_through_link"):
            self.make_tar([
                ("file", "apps/alias/file.txt", b"reparented"),
                ("symlink", "apps/alias", "../custom_apps/calendar"),
            ])

    def test_symlink_target_cannot_follow_file_as_directory(self):
        with self.assertRaisesRegex(ValueError, "archive_link_target_not_directory"):
            self.make_tar([("symlink", "apps/wrong", "../data/file.txt/hidden")])

    def test_hardlink_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe_archive_member"):
            self.make_tar([("hardlink", "apps/alias", "../data/file.txt")])

    def test_symlink_not_allowed_in_credential_archive(self):
        with self.assertRaisesRegex(ValueError, "unsafe_archive_member"):
            self.make_tar([("symlink", "apps/direct", "../data/file.txt")],
                          kind="credentials")

    def test_required_config_symlink_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_archive_member"):
            self.make_tar([("symlink", "config/config.php", "../data/file.txt")])

    def test_duplicate_archive_members_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_archive_member"):
            self.make_tar([("file", "data/file.txt", b"replacement")])

    def test_symlink_is_not_extractable_by_this_verifier(self):
        source = (ROOT / "tools/nextcloud-recovery-bundle.py").read_text()
        self.assertNotIn("extractall(", source)
        self.assertNotIn("extractfile(", source)
        self.assertNotIn("os.symlink(", source)
        self.assertNotIn("subprocess.run(", source)


if __name__ == "__main__":
    unittest.main()
