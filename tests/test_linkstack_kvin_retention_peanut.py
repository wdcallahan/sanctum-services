"""Independent Peanut retention of native accepted Nov17 Kvin LinkStack archive."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PB=ROOT/"ansible/linkstack-kvin-retain-on-peanut.yml"
CI=ROOT/".github/workflows/yxorp-source-check.yml"
SHA="301ee0eeee9de17a96ec1dc0292dbeaa059bceb3b7d45eed7426523727efbe05"
NAME="linkstack-kvin-20261117t105833.tar"

class LinkStackKvinRetentionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PB.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.by_name={t["name"]:t for t in cls.tasks}

    def test_exact_accepted_recovery_artifact_and_peanut_host(self):
        self.assertEqual(self.play["hosts"],"yxorp_test")
        self.assertIs(self.play["become"],False)
        vars=self.play["vars"]
        self.assertEqual(vars["linkstack_retention_filename"],NAME)
        self.assertEqual(vars["linkstack_retention_sha256"],SHA)
        self.assertEqual(vars["linkstack_retention_size"],93849600)
        checks=self.tasks[0]["ansible.builtin.assert"]["that"]
        for expected in (
            "inventory_hostname == 'peanut.arcane.sanctum'",
            "ansible_facts['fqdn'] == inventory_hostname",
            "not ansible_check_mode",
            "sanctum_linkstack_kvin_retain_on_peanut_approved | default(false) | bool"
        ):
            self.assertIn(expected,checks)

    def test_source_validation_is_local_to_kvin(self):
        self.assertEqual(self.by_name["Observe actual Ansible controller FQDN"]["delegate_to"],"localhost")
        check=self.by_name["Require current Kvin source controller and owner"]["ansible.builtin.assert"]["that"]
        self.assertIn("linkstack_retention_controller.stdout | trim == 'kvin.outer.sanctum'",check)
        stat=self.by_name["Read and independently hash the accepted Kvin backup file"]
        self.assertEqual(stat["delegate_to"],"localhost")
        self.assertEqual(stat["ansible.builtin.stat"]["checksum_algorithm"],"sha256")
        assertions=self.by_name["Require actual exact current Kvin snapshot before transfer"]["ansible.builtin.assert"]["that"]
        self.assertIn("linkstack_retention_local_stat.stat.size | int == linkstack_retention_size | int",assertions)
        self.assertIn("linkstack_retention_local_stat.stat.checksum == linkstack_retention_sha256",assertions)

    def test_copy_has_no_live_linkstack_or_network_side_effects(self):
        move=self.by_name["Copy only actual November 17 Kvin LinkStack archive over managed SSH"]
        self.assertIs(move["diff"],False)
        self.assertEqual(move["ansible.builtin.copy"]["mode"],"0600")
        self.assertIs(move["ansible.builtin.copy"]["force"],False)
        content=PB.read_text()
        for forbidden in ("systemd_service:", "firewall-cmd", "podman stop", "podman run",
                          "podman pull", "podman volume rm", "podman volume import",
                          "ansible.builtin.template:", "become: true"):
            self.assertNotIn(forbidden,content)

    def test_retained_bytes_and_sqlite_are_both_checked_on_peanut(self):
        stat=self.by_name["Independently hash actual LinkStack archive on Peanut"]
        self.assertNotIn("delegate_to",stat)
        self.assertEqual(stat["ansible.builtin.stat"]["checksum_algorithm"],"sha256")
        assertions=self.by_name["Require exact Peanut bytes, SHA256, private file mode and owner"]["ansible.builtin.assert"]["that"]
        self.assertIn("linkstack_retention_remote_stat.stat.checksum == linkstack_retention_sha256",assertions)
        self.assertIn("linkstack_retention_remote_stat.stat.mode == '0600'",assertions)
        verify=self.by_name["Independently verify retained LinkStack SQLite archive on Peanut"]
        self.assertTrue(verify["no_log"])
        self.assertEqual(verify["ansible.builtin.command"]["argv"][:3],["python3","-c","{{ linkstack_retention_validator }}"])
        checks=self.by_name["Require independently readable retained SQLite and configuration"]["ansible.builtin.assert"]["that"]
        self.assertIn("(linkstack_retention_remote_validation.stdout | from_json).sqlite_integrity == 'ok'",checks)
        report=self.by_name["Report real LinkStack off-Kvin retention on Peanut"]["ansible.builtin.debug"]["msg"]
        self.assertTrue(report["hash_and_sqlite_verified_on_peanut"])
        self.assertTrue(report["restore_to_independent_host_not_retested_by_copy"])

    def test_assert_arguments_are_task_level_not_module_level(self):
        allowed={"that","fail_msg","success_msg","quiet"}
        for task in self.tasks:
            if "ansible.builtin.assert" in task:
                self.assertEqual(set(task["ansible.builtin.assert"])-allowed,set(),task["name"])

    def test_ci_covers_real_playbook(self):
        wf=CI.read_text()
        self.assertIn("test_linkstack_kvin_retention_peanut.py",wf)
        self.assertIn("ansible/linkstack-kvin-retain-on-peanut.yml --syntax-check",wf)

if __name__=="__main__":
    unittest.main()
