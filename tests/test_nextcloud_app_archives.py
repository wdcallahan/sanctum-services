"""Standard-library regression tests for third-party Nextcloud release vetting."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest


VALIDATOR = (Path(__file__).resolve().parents[1] /
             "ansible/roles/nextcloud_apps/files/validate_archive.py")
SPEC = importlib.util.spec_from_file_location("nc_archive_validator", VALIDATOR)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def make_archive(path, app_id="calendar", version="6.6.2",
                 low=33, high=35, malicious=False, link=False):
    metadata = (f"<info><id>{app_id}</id><version>{version}</version>"
                f"<dependencies><nextcloud min-version='{low}' "
                f"max-version='{high}'/></dependencies></info>").encode()
    with tarfile.open(path, "w:gz") as archive:
        item = tarfile.TarInfo(f"{app_id}/appinfo/info.xml")
        item.size = len(metadata)
        archive.addfile(item, io.BytesIO(metadata))
        if malicious:
            bad = tarfile.TarInfo("../outside")
            bad.size = 1
            archive.addfile(bad, io.BytesIO(b"x"))
        if link:
            bad = tarfile.TarInfo(f"{app_id}/link")
            bad.type = tarfile.SYMTYPE
            bad.linkname = "/etc/passwd"
            archive.addfile(bad)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "app.tar.gz"

    def tearDown(self):
        self.tmp.cleanup()

    def test_exact_release_and_compatible_nextcloud(self):
        make_archive(self.path)
        validator.validate(str(self.path), "calendar", "6.6.2", 34)

    def test_reject_wrong_id(self):
        make_archive(self.path)
        with self.assertRaisesRegex(ValueError, "app id mismatch|unexpected archive"):
            validator.validate(str(self.path), "contacts", "6.6.2", 34)

    def test_reject_wrong_version(self):
        make_archive(self.path)
        with self.assertRaisesRegex(ValueError, "version mismatch"):
            validator.validate(str(self.path), "calendar", "6.6.1", 34)

    def test_reject_incompatible_server(self):
        make_archive(self.path)
        with self.assertRaisesRegex(ValueError, "exceeds app maximum"):
            validator.validate(str(self.path), "calendar", "6.6.2", 36)

    def test_reject_path_traversal(self):
        make_archive(self.path, malicious=True)
        with self.assertRaisesRegex(ValueError, "unsafe or unexpected"):
            validator.validate(str(self.path), "calendar", "6.6.2", 34)

    def test_reject_symlinks(self):
        make_archive(self.path, link=True)
        with self.assertRaisesRegex(ValueError, "unsafe or unexpected"):
            validator.validate(str(self.path), "calendar", "6.6.2", 34)


if __name__ == "__main__":
    unittest.main()
