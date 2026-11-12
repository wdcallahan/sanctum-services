"""LinkStack transfer/isolated import contract: no changes to Kvar or live Kvin."""
import importlib.util
import sqlite3
from pathlib import Path
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/linkstack-transfer-isolated-data-restore.yml"
VALIDATOR = ROOT / "tools/linkstack-archive-verify.py"
spec = importlib.util.spec_from_file_location("verify", VALIDATOR)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class RestoredDataValidator(unittest.TestCase):
    def test_imported_volume_validates_sqlite_and_marker_without_returning_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "database").mkdir()
            (root / ".env").write_text("APP_KEY=TOPSECRET\n")
            db = root / "database" / "database.sqlite"
            conn = sqlite3.connect(db)
            conn.execute("create table linkstack_private (token text)")
            conn.execute("insert into linkstack_private values ('TOPSECRET')")
            conn.commit()
            conn.close()
            result = verify.inspect_restored_volume(root)
            self.assertTrue(result["isolated_imported_volume_integrity_verified"])
            self.assertEqual(result["sqlite_integrity"], "ok")
            self.assertFalse(result["restored_application_boot_verified"])
            self.assertFalse(result["browser_content_and_admin_accepted"])
            self.assertNotIn("TOPSECRET", str(result))

    def test_missing_invalid_or_symlinked_restored_state_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                verify.inspect_restored_volume(root)
            (root / "database").mkdir()
            (root / "database" / "database.sqlite").write_text("invalid" * 30)
            (root / ".env").write_text("secret")
            with self.assertRaises((ValueError, sqlite3.Error)):
                verify.inspect_restored_volume(root)
            (root / ".env").unlink()
            (root / ".env").symlink_to("/etc/passwd")
            with self.assertRaises(ValueError):
                verify.inspect_restored_volume(root)


class TransferSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plays = yaml.safe_load(PLAY.read_text())
        cls.source, cls.target = cls.plays
        cls.source_tasks = cls.source["tasks"]
        cls.target_tasks = cls.target["tasks"]

    def task(self, fragment, source=False):
        ts = self.source_tasks if source else self.target_tasks
        return next(t for t in ts if fragment in t["name"])

    def test_two_scoped_hosts_and_two_distinct_approvals(self):
        self.assertEqual(len(self.plays), 2)
        self.assertEqual(self.source["hosts"], "npm_proxy_legacy")
        self.assertEqual(self.target["hosts"], "kuma")
        for p in self.plays:
            self.assertFalse(p["become"])
        g0 = str(self.source_tasks[0]["ansible.builtin.assert"]["that"])
        g1 = str(self.target_tasks[0]["ansible.builtin.assert"]["that"])
        for required in ("'kvar.outer.sanctum'", "sanctum_linkstack_offhost_transfer_approved",
                         "not ansible_check_mode"):
            self.assertIn(required, g0)
        for required in ("'kvin.outer.sanctum'", "sanctum_linkstack_isolated_volume_restore_approved",
                         "sanctum_linkstack_offhost_transfer_approved",
                         "linkstack_snapshot_source_validated", "not ansible_check_mode"):
            self.assertIn(required, g1)
        self.assertNotIn("sanctum_linkstack_consistent_backup_approved", g0)
        self.assertEqual(self.source["vars"]["linkstack_snapshot_sha256"],
                         self.target["vars"]["linkstack_snapshot_sha256"])
        self.assertEqual(self.source["vars"]["linkstack_snapshot_size"], 93845504)
        self.assertEqual(self.source["vars"]["linkstack_snapshot_size"],
                         self.target["vars"]["linkstack_snapshot_size"])

    def test_source_archive_sha256_private_identity_required_before_any_copy(self):
        checks = str(self.task("Refuse wrong LinkStack source", source=True)
                     ["ansible.builtin.assert"]["that"])
        for value in ("stat.isreg", "stat.islnk", "stat.pw_name", "stat.mode",
                      "stat.size", "stat.checksum"):
            self.assertIn(value, checks)
        self.assertIn("get_checksum", self.task("Stat the original", source=True)
                      ["ansible.builtin.stat"])
        self.assertTrue(self.task("Mark source archive", source=True)
                        ["ansible.builtin.set_fact"]["linkstack_snapshot_source_validated"])

    def test_ssh_only_exact_file_on_legacy_management_port_and_private_destination(self):
        reserve = self.task("Atomically reserve")
        self.assertIn("os.O_EXCL", str(reserve["ansible.builtin.command"]["argv"]))
        scp = self.task("Copy only the named snapshot")
        self.assertTrue(scp["no_log"])
        argv = scp["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[0], "scp")
        for value in ("-B", "-P", "10022", "BatchMode=yes",
                      "StrictHostKeyChecking=yes", "ConnectTimeout=10"):
            self.assertIn(value, argv)
        self.assertIn("kvar.outer.sanctum", str(argv))
        self.assertNotIn("-T", argv)
        self.assertNotIn("-r", argv)
        pub = self.task("Promote verified Kvin archive")
        self.assertIn("os.link(", str(pub))
        permissions = self.task("Reject incomplete, altered")
        for value in ("stat.pw_name", "stat.mode", "stat.checksum", "stat.size"):
            self.assertIn(value, str(permissions))

    def test_restoration_only_to_new_rootless_volume_with_no_running_app(self):
        gate = self.task("Refuse replacing any existing Kvin volume")
        self.assertIn("rc == 1", str(gate))
        create = self.task("Create only an isolated")
        self.assertEqual(create["ansible.builtin.command"]["argv"][:3],
                         ["podman", "volume", "create"])
        imp = self.task("Import verified archive")
        self.assertTrue(imp["no_log"])
        self.assertEqual(imp["ansible.builtin.command"]["argv"][:3],
                         ["podman", "volume", "import"])
        self.assertIn("linkstack_restore_volume",
                      str(imp["ansible.builtin.command"]["argv"]))
        self.assertNotIn("podman run", PLAY.read_text())
        self.assertNotIn("ansible.builtin.systemd_service", PLAY.read_text())
        for forbidden in ("podman pull", "podman volume rm", "pihole.service",
                          "nginx", "firewalld", "ansible.builtin.uri:"):
            self.assertNotIn(forbidden, PLAY.read_text())
        report = self.target_tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["restored_linkstack_app_boot_accepted"], False)
        self.assertIs(report["independent_disaster_recovery_backup_accepted"], False)
        self.assertIs(report["production_proxy_dns_or_pihole_changed"], False)
        self.assertIs(report["kvar_original_application_or_volume_changed"], False)

    def test_verified_imported_sqlite_and_no_ui_overclaim(self):
        check = self.task("Privately verify restored SQLite")
        self.assertTrue(check["no_log"])
        self.assertEqual(check["ansible.builtin.command"]["argv"][-2],
                         "restored")
        assertions = str(self.task("Require isolated restored data integrity")["ansible.builtin.assert"])
        self.assertIn("isolated_imported_volume_integrity_verified", assertions)
        self.assertIn("restored_application_boot_verified", assertions)
        self.assertIn("browser_content_and_admin_accepted", assertions)

    def test_source_ci_includes_transfer_tests_and_ansible_syntax(self):
        ci = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_transfer_isolated_restore.py", ci)
        self.assertIn("ansible/linkstack-transfer-isolated-data-restore.yml --syntax-check", ci)


if __name__ == "__main__":
    unittest.main()
