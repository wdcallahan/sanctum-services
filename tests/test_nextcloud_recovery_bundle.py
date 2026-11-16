"""Synthetic, offline tests of Nextcloud recovery-bundle integrity gates."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "nextcloud_recovery_bundle", ROOT / "tools/nextcloud-recovery-bundle.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class NextcloudRecoveryBundle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "snapshot"
        self.root.mkdir(mode=0o700)
        self.manifest = {
            "schema": module.SCHEMA,
            "source_host": "kvin.outer.sanctum",
            "data_directory": "/var/www/html/data",
            "database": "nextcloud",
            "artifacts": {},
        }
        self.build_archive("application", {
            "config/config.php": b"<?php $secret='private';",
            "data/alice/files/example.txt": b"private Nextcloud document",
            "custom_apps/calendar/appinfo/info.xml": b"<info/>",
        })
        self.build_archive("credentials", {
            "postgresql-password": b"private database password",
            "postgresql-database": b"nextcloud",
            "postgresql-username": b"nextcloud",
            "nextcloud.env": b"PRIVATE=PRIVATE",
        })
        self.write_payload("database", b"PGDMP" + b"fixture-only" * 20)
        self.save_manifest()

    def write_payload(self, kind, content):
        filename = module.ARTIFACTS[kind][0]
        path = self.root / filename
        path.write_bytes(content)
        path.chmod(0o600)
        self.manifest["artifacts"][kind] = {
            "filename": filename,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(content).hexdigest(),
        }

    def build_archive(self, kind, items):
        filename = module.ARTIFACTS[kind][0]
        dest = self.root / filename
        with tarfile.open(dest, "w") as archive:
            for name, contents in items.items():
                info = tarfile.TarInfo(name)
                info.size = len(contents)
                archive.addfile(info, io.BytesIO(contents))
        dest.chmod(0o600)
        self.write_payload(kind, dest.read_bytes())

    def save_manifest(self):
        p = self.root / "manifest.json"
        p.write_text(json.dumps(self.manifest))
        p.chmod(0o600)

    def test_good_bundle_reports_integrity_only_not_recovery(self):
        report = module.verify(self.root)
        self.assertTrue(report["archive_and_dump_hashes_match_manifest"])
        for status in ("consistent_snapshot_proven", "database_restore_tested",
                       "independent_off_host_retention_proven", "application_restore_accepted"):
            self.assertFalse(report[status])
        self.assertNotIn("private database password", json.dumps(report))
        self.assertNotIn("private Nextcloud document", json.dumps(report))

    def test_reject_tampered_payload_and_unrecognized_database(self):
        db = self.root / "nextcloud-postgresql.dump"
        db.write_bytes(db.read_bytes() + b"unexpected")
        with self.assertRaisesRegex(ValueError, "payload_checksum_mismatch"):
            module.verify(self.root)
        self.write_payload("database", b"NOT-PGDMP" * 10)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "unrecognized_pg_dump_header"):
            module.verify(self.root)

    def test_refuse_unexpected_instance_or_artifact_names(self):
        self.manifest["data_directory"] = "/tmp/guessed-data"
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "unexpected_instance_identity"):
            module.verify(self.root)
        self.manifest["data_directory"] = "/var/www/html/data"
        self.manifest["artifacts"]["application"]["filename"] = "../secret.tar"
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "invalid_artifact_metadata"):
            module.verify(self.root)

    def test_missing_content_does_not_count_as_full_instance(self):
        self.build_archive("application", {
            "config/config.php": b"private config",
            "custom_apps/calendar/manifest.xml": b"<app/>",
        })
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "missing_archive_state"):
            module.verify(self.root)

    def test_archive_traversal_and_links_refused_even_if_hashes_match(self):
        self.build_archive("application", {
            "config/config.php": b"private",
            "data/user/file.txt": b"private",
            "custom_apps/calendar/appinfo/info.xml": b"safe",
            "../../escape": b"bad",
        })
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "unsafe_archive_path"):
            module.verify(self.root)
        dst = self.root / "nextcloud-html.tar"
        with tarfile.open(dst, "w") as archive:
            for name in ("config/config.php", "data", "custom_apps"):
                info = tarfile.TarInfo(name)
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                archive.addfile(info)
        self.write_payload("application", dst.read_bytes())
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "unsafe_archive_member"):
            module.verify(self.root)

    def test_private_permissions_and_no_symlink_payload(self):
        db = self.root / "nextcloud-postgresql.dump"
        db.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "payload_permissions"):
            module.verify(self.root)
        db.chmod(0o600)
        db.unlink()
        db.symlink_to(self.root / "manifest.json")
        with self.assertRaisesRegex(ValueError, "missing_or_linked_payload"):
            module.verify(self.root)

    def test_no_app_runtime_or_postgresql_calls_in_verifier(self):
        source = (ROOT / "tools/nextcloud-recovery-bundle.py").read_text()
        for forbidden in ("import subprocess", "subprocess.run(", "os.system(",
                          "podman exec", "pg_restore ", "pg_dump ",
                          "tar.extractall(", "shutil.rmtree("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
