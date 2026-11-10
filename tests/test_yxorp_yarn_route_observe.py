"""The Kvar/Kvin selected-path comparator cannot mutate either production host."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/yxorp-yarn-route-observe.yml"


class YarnRouteObservationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PLAY.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.raw)[0]

    def test_two_exact_inventory_observers_and_no_privilege_escalation(self):
        self.assertEqual(self.play["hosts"], "yxorp:npm_proxy_legacy")
        self.assertTrue(self.play["gather_facts"])
        self.assertFalse(self.play["become"])
        guard = self.play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("ansible_play_hosts_all | length == 2", guard)
        self.assertIn("not ansible_check_mode", guard)
        self.assertIn(
            "inventory_hostname in ['kvin.outer.sanctum', 'kvar.outer.sanctum']",
            guard)

    def test_queries_only_exact_yarn_and_known_arcane_control_destinations(self):
        calls = [task for task in self.play["tasks"]
                 if "ansible.builtin.command" in task]
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            [t["ansible.builtin.command"]["argv"] for t in calls],
            [["ip", "-4", "-j", "route", "get", "192.168.1.110"],
             ["ip", "-4", "-j", "route", "get", "192.168.3.3"]])
        for task in calls:
            self.assertIs(task["changed_when"], False)
            self.assertIs(task["failed_when"], False)
            self.assertNotIn("no_log", task)

    def test_no_route_or_firewall_writes_and_metadata_only(self):
        permitted = {"ansible.builtin.assert", "ansible.builtin.command",
                     "ansible.builtin.debug"}
        for task in self.play["tasks"]:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1)
            self.assertTrue(modules <= permitted)
        report = self.play["tasks"][-1]["ansible.builtin.debug"]["msg"]
        for key in ("yarn_selected_gateway", "yarn_selected_source",
                    "yarn_selected_interface", "control_selected_gateway",
                    "control_selected_source", "configuration_changed"):
            self.assertIn(key, report)
        self.assertFalse(report["configuration_changed"])
        self.assertNotIn("firewall-cmd", self.raw)
        self.assertNotIn("route add", self.raw)
        self.assertNotIn("route del", self.raw)


if __name__ == "__main__":
    unittest.main()
