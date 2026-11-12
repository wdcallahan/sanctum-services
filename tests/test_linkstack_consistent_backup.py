"""Default-off Kvar LinkStack snapshot guards and private archive verification."""
from pathlib import Path
import importlib.util
import io
import json
import sqlite3
import tarfile
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/linkstack-consistent-backup.yml"
VERIFY = ROOT / "tools/linkstack-archive-verify.py"
spec = importlib.util.spec_from_file_location("lsverify", VERIFY)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SECRET = b"private-linkstack-password-do-not-print"


class ArchiveVerifier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "database.sqlite"
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO sample(value) VALUES('private fixture')")
        conn.commit()
        conn.close()
        self.archive = self.root / "linkstack.tar"

    def make_archive(self, members=None):
        if members is None:
            members = [(".env", SECRET),
                       ("database/database.sqlite", self.db.read_bytes()),
                       ("images/logo.png", b"image data")]
        with tarfile.open(self.archive, "w") as tf:
            for name, blob in members:
                info = tarfile.TarInfo(name)
                info.mode = 0o600
                info.size = len(blob)
                tf.addfile(info, io.BytesIO(blob))

    def test_valid_complete_archive_reports_integrity_and_hash_only(self):
        self.make_archive()
        result = mod.inspect(self.archive)
        self.assertTrue(result["archive_verified"])
        self.assertEqual(result["sqlite_integrity"], "ok")
        self.assertEqual(result["regular_file_count"], 3)
        self.assertEqual(len(result["archive_sha256"]), 64)
        self.assertEqual(result["regular_file_bytes"],
                         len(SECRET) + self.db.stat().st_size + len(b"image data"))
        self.assertFalse(result["recovery_proven"])
        self.assertFalse(result["off_host_copy_verified"])
        self.assertNotIn(SECRET.decode(), json.dumps(result))
        self.assertNotIn(str(self.root), json.dumps(result))

    def test_missing_dot_env_is_rejected(self):
        self.make_archive([("database/database.sqlite", self.db.read_bytes())])
        with self.assertRaisesRegex(ValueError, "missing_required_state"):
            mod.inspect(self.archive)

    def test_corrupt_sqlite_is_rejected(self):
        self.make_archive([(".env", SECRET),
                           ("database/database.sqlite", b"not a sqlite db" * 30)])
        with self.assertRaises((sqlite3.Error, ValueError)):
            mod.inspect(self.archive)

    def test_path_traversal_absolute_and_duplicate_members_are_rejected(self):
        for name in ("../escaped", "/etc/passwd", "some/../../escaped"):
            self.make_archive([(".env", SECRET),
                               ("database/database.sqlite", self.db.read_bytes()),
                               (name, b"bad")])
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "unsafe_name"):
                mod.inspect(self.archive)
        self.make_archive([(".env", SECRET), (".env", SECRET),
                           ("database/database.sqlite", self.db.read_bytes())])
        with self.assertRaisesRegex(ValueError, "duplicate_member"):
            mod.inspect(self.archive)

    def test_symlink_archive_member_rejected(self):
        with tarfile.open(self.archive, "w") as tf:
            link = tarfile.TarInfo("shortcut")
            link.type = tarfile.SYMTYPE
            link.linkname = "database/database.sqlite"
            tf.addfile(link)
        with self.assertRaisesRegex(ValueError, "unsafe_member_type"):
            mod.inspect(self.archive)


class LinkStackBackupPlaybook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plays = yaml.safe_load(PLAY.read_text())
        cls.play = cls.plays[0]
        cls.tasks = cls.play["tasks"]

    def task(self, name):
        return next(x for x in self.tasks if x["name"].startswith(name))

    def test_exact_kvar_rootless_and_default_off_gate(self):
        self.assertEqual(len(self.plays), 1)
        self.assertEqual(self.play["hosts"], "npm_proxy_legacy")
        self.assertFalse(self.play["become"])
        self.assertTrue(self.play["gather_facts"])
        gate = self.tasks[0]["ansible.builtin.assert"]["that"]
        for required in [
            "inventory_hostname == 'kvar.outer.sanctum'",
            "ansible_facts['user_id'] == 'wdc2'",
            "sanctum_linkstack_consistent_backup_approved | default(false) | bool",
            "not ansible_check_mode",
        ]:
            self.assertIn(required, gate)
        self.assertEqual(self.play["vars"]["linkstack_expected_image_id"],
                         "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65")

    def test_live_source_is_checked_before_stop_and_backup_collision_prevented(self):
        preflight = self.task("Refuse changed image")
        checks = str(preflight["ansible.builtin.assert"]["that"])
        for expected in ("linkstack_expected_image_id", "mounts", "port_mappings",
                         "image_reference", "service_unit.quadlet_source",
                         "container_running"):
            self.assertIn(expected, checks)
        self.assertIn("linkstack_backup_outputs", str(self.task("Require fresh names")))
        reserve = self.task("Atomically reserve")
        self.assertIn("os.O_EXCL", str(reserve["ansible.builtin.command"]["argv"]))

    def test_only_linkstack_service_stopped_and_always_restarted(self):
        transaction = self.task("Stop only incumbent LinkStack")
        self.assertIn("always", transaction)
        changed = []
        for task in transaction["block"]:
            module = task.get("ansible.builtin.systemd_service")
            if module:
                changed.append(module)
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["name"], "linkstack.service")
        self.assertEqual(changed[0]["scope"], "user")
        self.assertEqual(changed[0]["state"], "stopped")
        finally_tasks = transaction["always"]
        start = next(t for t in finally_tasks if "ansible.builtin.systemd_service" in t)
        self.assertEqual(start["ansible.builtin.systemd_service"]["name"],
                         "linkstack.service")
        self.assertEqual(start["ansible.builtin.systemd_service"]["scope"], "user")
        self.assertEqual(start["ansible.builtin.systemd_service"]["state"], "started")
        self.assertIn("linkstack_backup_restarted",
                      str(finally_tasks))
        export = next(t for t in transaction["block"]
                      if t["name"].startswith("Export only"))
        argv = export["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[:4], ["podman", "volume", "export", "linkstack"])
        self.assertTrue(export["no_log"])

    def test_restart_must_preserve_exact_image_and_volume_identity(self):
        observer = self.task("Privately observe original image")
        self.assertTrue(observer["no_log"])
        self.assertIs(observer["changed_when"], False)
        checks = str(self.task("Refuse claiming clean backup")["ansible.builtin.assert"]["that"])
        for field in ("linkstack_expected_image_id", "image_reference",
                      "mounts", "port_mappings", "container_running"):
            self.assertIn(field, checks)
        names = [task["name"] for task in self.tasks]
        self.assertLess(names.index("Refuse claiming clean backup if restart changed original image or mount"),
                        names.index("Privately validate exported SQLite and complete safe archive"))

    def test_no_post_snapshot_restore_or_other_hosts_and_no_secret_output(self):
        text = PLAY.read_text()
        self.assertNotIn("podman volume import", text)
        self.assertNotIn("systemctl --system", text)
        self.assertNotIn("pihole.service", text)
        self.assertNotIn("nginx-proxman", text)
        self.assertNotIn("ansible.builtin.fetch:", text)
        self.assertNotIn("ansible.builtin.slurp:", text)
        validate = self.task("Privately validate exported SQLite")
        self.assertTrue(validate["no_log"])
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["archive_copied_off_kvar"], False)
        self.assertIs(report["isolated_kvin_restore_accepted"], False)
        self.assertIs(report["pihole_or_npm_or_dns_or_proxy_changed"], False)

    def test_ci_checks_validator_and_playbook_syntax(self):
        wf = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_consistent_backup.py", wf)
        self.assertIn("ansible/linkstack-consistent-backup.yml --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
