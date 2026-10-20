"""Static contract for Nextcloud's read-only host-firewall ownership handoff.

Run from repo root with: python3 -m unittest discover -s tests
PyYAML is installed with the supported Ansible controller/EE.
"""

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / "ansible/roles/nextcloud/tasks/main.yml"
VARIABLES = ROOT / "ansible/group_vars/nextcloud.yml"


class MaintenanceFirewallPrerequisiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = yaml.safe_load(ROLE.read_text(encoding="utf-8"))
        cls.variables = yaml.safe_load(VARIABLES.read_text(encoding="utf-8"))

    def test_services_never_manages_firewalld(self) -> None:
        self.assertFalse(
            any("ansible.posix.firewalld" in task for task in self.tasks),
            "Host firewall changes belong to Maintenance, not Services.",
        )
        privileged = [task["name"] for task in self.tasks if task.get("become") is True]
        self.assertEqual(
            privileged,
            [
                "Observe Maintenance-owned runtime admission for Nextcloud",
                "Observe Maintenance-owned permanent admission for Nextcloud",
            ],
            "Privilege escalation is limited to read-only firewalld port queries.",
        )

    def test_preflight_is_before_all_app_mutations(self) -> None:
        names = [task["name"] for task in self.tasks]
        prerequisites = (
            "Observe the active firewall zone for Kvin's service interface",
            "Observe Maintenance-owned runtime admission for Nextcloud",
            "Observe Maintenance-owned permanent admission for Nextcloud",
            "Require Maintenance's live and durable Nextcloud firewall prerequisite",
        )
        for name in prerequisites:
            self.assertIn(name, names)
            self.assertLess(names.index(name), names.index("Create the application storage directory"))
        self.assertEqual(
            len([task for task in self.tasks if task["name"] == prerequisites[-1]]), 1
        )

    def test_both_firewall_stores_and_zone_are_read_only(self) -> None:
        tasks = {task["name"]: task for task in self.tasks}
        prefix = "Observe Maintenance-owned "
        runtime = tasks[prefix + "runtime admission for Nextcloud"]
        permanent = tasks[prefix + "permanent admission for Nextcloud"]
        zone = tasks["Observe the active firewall zone for Kvin's service interface"]
        for task in (runtime, permanent, zone):
            self.assertEqual(task.get("changed_when"), False)
            self.assertEqual(task.get("failed_when"), False)
            self.assertEqual(task.get("check_mode"), False)
            self.assertIn("ansible.builtin.command", task)
        self.assertNotIn("become", zone)
        self.assertIs(runtime.get("become"), True)
        self.assertIs(permanent.get("become"), True)
        self.assertIn("--query-port={{ nextcloud_host_port }}/tcp", runtime["ansible.builtin.command"]["argv"])
        self.assertIn("--query-port={{ nextcloud_host_port }}/tcp", permanent["ansible.builtin.command"]["argv"])
        self.assertIn("--permanent", permanent["ansible.builtin.command"]["argv"])
        self.assertNotIn("--permanent", runtime["ansible.builtin.command"]["argv"])
        self.assertIn("--get-zone-of-interface={{ nextcloud_firewall_interface }}", zone["ansible.builtin.command"]["argv"])

    def test_missing_prerequisite_fails_with_owner_remediation(self) -> None:
        tasks = {task["name"]: task for task in self.tasks}
        task = tasks["Require Maintenance's live and durable Nextcloud firewall prerequisite"]
        checks = task["ansible.builtin.assert"]["that"]
        expected = (
            "nextcloud_firewall_interface_zone.rc == 0",
            "nextcloud_firewall_interface_zone.stdout | trim == nextcloud_firewall_zone",
            "nextcloud_firewall_runtime_port.rc == 0",
            "nextcloud_firewall_permanent_port.rc == 0",
        )
        self.assertEqual(checks, list(expected))
        failure = task["ansible.builtin.assert"]["fail_msg"]
        self.assertIn("playbooks/configure-kvin-firewall.yml", failure)
        self.assertIn("docs/runbooks/kvin-service-firewall.md", failure)
        self.assertIn("Services does not open host firewall ports", failure)

    def test_source_matches_existing_kvin_zone_and_port(self) -> None:
        self.assertEqual(self.variables["nextcloud_host_port"], 8085)
        self.assertEqual(self.variables["nextcloud_firewall_zone"], "public")
        self.assertEqual(self.variables["nextcloud_firewall_interface"], "eth0")


if __name__ == "__main__":
    unittest.main()
