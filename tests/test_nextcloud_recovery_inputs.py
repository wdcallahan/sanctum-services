"""Guardrails for the non-mutating, Kvin-only Nextcloud recovery check."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/nextcloud-recovery-inputs.yml"


class NextcloudRecoveryInputsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text())[0]
        cls.tasks = cls.play["tasks"]

    def test_scope_and_expected_inputs(self):
        self.assertEqual(self.play["hosts"], "nextcloud")
        self.assertFalse(self.play["become"])
        assertions = " ".join(self.tasks[0]["ansible.builtin.assert"]["that"])
        self.assertIn("kvin.outer.sanctum", assertions)
        self.assertIn("ansible_user == 'wdc2'", assertions)
        files = self.play["vars"]["nextcloud_recovery_files"]
        names = {item["name"] for item in files}
        self.assertEqual(len(files), 10)
        self.assertIn("instance_config", names)
        self.assertIn("database_password_file", names)
        self.assertIn("quadlet_source", names)

    def test_read_only_and_redacted(self):
        allowed = {"ansible.builtin.assert", "ansible.builtin.stat",
                   "ansible.builtin.command", "ansible.builtin.uri",
                   "ansible.builtin.debug"}
        for task in self.tasks:
            actions = {key for key in task if key.startswith("ansible.builtin.")}
            self.assertEqual(len(actions), 1)
            self.assertTrue(actions <= allowed)
        stat = next(t for t in self.tasks if "ansible.builtin.stat" in t)
        self.assertTrue(stat["no_log"])
        self.assertFalse(stat["ansible.builtin.stat"]["get_checksum"])
        self.assertFalse(stat["ansible.builtin.stat"]["follow"])
        command = next(t for t in self.tasks if "ansible.builtin.command" in t)
        self.assertEqual(command["ansible.builtin.command"]["argv"][:3],
                         ["systemctl", "--user", "is-active"])
        self.assertFalse(command["changed_when"])
        uri = next(t for t in self.tasks if "ansible.builtin.uri" in t)
        self.assertEqual(uri["ansible.builtin.uri"]["method"], "GET")
        self.assertTrue(uri["no_log"])

    def test_no_false_backup_claim(self):
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for name in ("database_snapshot_observed", "off_host_backup_observed",
                     "restore_qualified", "application_interrupted",
                     "configuration_changed"):
            self.assertIs(report[name], False)
        self.assertEqual(report["default_data_path_is_authoritative"],
                         "unknown_until_config_review")


if __name__ == "__main__":
    unittest.main()
