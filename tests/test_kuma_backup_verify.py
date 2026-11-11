"""Verify offline Kuma archive/isolated-restored SQLite inspector using fixtures."""
from pathlib import Path
import io
import json
import sqlite3
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/kuma-backup-verify.py"


class KumaBackupInspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="kuma-backup-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "kuma.db"
        with sqlite3.connect(self.db) as conn:
            conn.executescript("""
              CREATE TABLE user (username TEXT NOT NULL);
              CREATE TABLE monitor (
                id INTEGER, name TEXT, type TEXT, method TEXT, url TEXT,
                interval INTEGER, active INTEGER, accepted_statuscodes_json TEXT
              );
              CREATE TABLE monitor_notification (monitor_id INTEGER);
              INSERT INTO user VALUES ('sanctum-admin');
              INSERT INTO monitor VALUES (1,'Wicket Ollama','http','GET',
                'http://wicket.arcane.sanctum:11435/healthz',60,1,'["200-299"]');
            """)
        self.tar = self.root / "archive.tar"
        with tarfile.open(self.tar, "w") as tf:
            tf.add(self.db, arcname="./kuma.db")

    def run_check(self, mode, path):
        return subprocess.run(["python3", str(SCRIPT), mode, str(path)],
                              capture_output=True, text=True, timeout=10)

    def test_archive_and_isolated_volume_contract(self):
        for mode, path in (("archive", self.tar), ("restored", self.root)):
            p = self.run_check(mode, path)
            self.assertEqual(p.returncode, 0, p.stderr)
            d = json.loads(p.stdout)
            self.assertEqual(d["sqlite_integrity"], "ok")
            self.assertIs(d["administrator_record_present"], True)
            self.assertIs(d["wicket_monitor_persisted"], True)
            self.assertIs(d["notification_subscriptions_absent"], True)

    def test_missing_database_refused(self):
        with tarfile.open(self.tar, "w") as tf:
            payload = b"nothing"
            info = tarfile.TarInfo("not-the-database")
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
        p = self.run_check("archive", self.tar)
        self.assertNotEqual(p.returncode, 0)

    def test_refuses_path_traversal(self):
        with tarfile.open(self.tar, "w") as tf:
            tf.add(self.db, arcname="kuma.db")
            payload = b"unsafe"
            info = tarfile.TarInfo("../unsafe")
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
        p = self.run_check("archive", self.tar)
        self.assertNotEqual(p.returncode, 0)

    def test_refuses_missing_admin_or_monitor(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM user")
        p = self.run_check("restored", self.root)
        self.assertNotEqual(p.returncode, 0)

    def test_refuses_attached_notifications(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO monitor_notification VALUES (1)")
        p = self.run_check("restored", self.root)
        self.assertNotEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
