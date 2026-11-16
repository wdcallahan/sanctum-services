"""Source contract: an owner database export must be injected before any Nextcloud write."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible" / "nextcloud-consistent-backup.yml"


class NextcloudConsistentBackupContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PLAY.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.raw)[0]
        cls.tasks = cls.play["tasks"]

    def find(self, part):
        return next(t for t in self.tasks if part in t.get("name", ""))

    def test_owner_scope_and_no_host_admin_escalation(self):
        self.assertEqual(self.play["hosts"], "nextcloud")
        self.assertFalse(self.play["become"])
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", self.raw)
        self.assertIn("ansible_user == 'wdc2'", self.raw)
        self.assertIn("nextcloud_consistent_backup_approved", self.raw)
        self.assertIn("nextcloud_database_export_contract_approved", self.raw)
        self.assertIn("nextcloud_database_export_argv is defined", self.raw)
        self.assertIn("not ansible_check_mode", self.raw)

    def test_write_freeze_contains_only_owner_export_then_assembly(self):
        block = self.find("Quiesce Nextcloud and collect")
        self.assertIn("block", block)
        self.assertIn("always", block)
        steps = block["block"]
        names = [t["name"] for t in steps]
        index = lambda part: next(i for i, name in enumerate(names) if part in name)
        self.assertLess(index("Enable write-quiescing"), index("Confirm the application is actually"))
        self.assertLess(index("Require active write-quiescence"), index("Invoke ONLY"))
        self.assertLess(index("Invoke ONLY"), index("Assemble file"))
        self.assertLess(index("Assemble file"), index("Require the bundle verifier"))
        export = steps[index("Invoke ONLY")]
        self.assertEqual(export["ansible.builtin.command"]["argv"], "{{ nextcloud_database_export_argv }}")
        self.assertTrue(export["no_log"])
        self.assertNotIn("pg_dump", self.raw)
        self.assertNotIn("pg_restore", self.raw)

    def test_failure_always_restores_mode(self):
        block = self.find("Quiesce Nextcloud and collect")
        always = block["always"]
        self.assertIn("maintenance:mode", always[0]["ansible.builtin.command"]["argv"])
        self.assertIn("--off", always[0]["ansible.builtin.command"]["argv"])
        self.assertTrue(always[0]["no_log"])
        self.assertIn("status", always[1]["ansible.builtin.command"]["argv"])
        self.assertIn("ansible.builtin.assert", always[2])
        self.assertIn("not ((nextcloud_after_status.stdout | from_json).maintenance | bool)",
                      always[2]["ansible.builtin.assert"]["that"])

    def test_no_off_host_or_restore_false_claims(self):
        report = self.find("Report one locally assembled")
        msg = report["ansible.builtin.debug"]["msg"]
        self.assertIs(msg["copied_off_kvin"], False)
        self.assertIs(msg["independent_restore_tested"], False)
        self.assertIn("protected off-Kvin", msg["next_action"])
        self.assertIn("mode: '0700'", self.raw)
        self.assertIn("nextcloud_database_export_stat.stat.mode == '0600'", self.raw)


if __name__ == "__main__":
    unittest.main()
