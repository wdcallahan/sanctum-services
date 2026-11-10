"""Legacy Kvar NPM equivalence check must be anonymous, bounded and read-only."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/yxorp-incumbent-parity.yml"


class YxorpIncumbentParityContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.source)[0]
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]

    def test_legacy_scope_and_closed_production_gate(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertFalse(self.play["become"])
        self.assertFalse(self.play["gather_facts"])
        self.assertEqual(self.play["vars_files"], ["../data/yxorp-routes.yml"])
        self.assertIn("rejectattr('hostname', 'equalto', 'yarn.nexus.sanctum')",
                      self.play["vars"]["yxorp_legacy_routes"])
        self.assertEqual(len(self.routes), 8)
        self.assertEqual(len([r for r in self.routes
                              if r["hostname"] != "yarn.nexus.sanctum"]), 7)
        self.assertTrue(all(not r["enabled"] for r in self.routes
                            if r["hostname"] != "yarn.nexus.sanctum"))
        guard = self.play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", guard)

    def test_four_bounded_anonymous_gets_no_logs(self):
        calls = [t for t in self.play["tasks"] if "ansible.builtin.uri" in t]
        self.assertEqual(len(calls), 4)
        self.assertEqual(calls[0]["loop"], "{{ yxorp_legacy_routes }}")
        self.assertEqual(calls[1]["loop"], "{{ yxorp_legacy_routes }}")
        self.assertEqual(
            {calls[0]["ansible.builtin.uri"]["url"],
             calls[1]["ansible.builtin.uri"]["url"]},
            {"http://{{ item.upstream_host }}:{{ item.upstream_port }}/",
             "http://kvar.outer.sanctum/"})
        self.assertEqual(
            {calls[2]["ansible.builtin.uri"]["url"],
             calls[3]["ansible.builtin.uri"]["url"]},
            {"http://kvar.outer.sanctum:82/admin/",
             "http://kvar.outer.sanctum/admin/"})
        for i, task in enumerate(calls):
            module = task["ansible.builtin.uri"]
            self.assertTrue(task["no_log"], task["name"])
            self.assertIs(task["changed_when"], False, task["name"])
            self.assertIs(task["failed_when"], False, task["name"])
            self.assertEqual(module["method"], "GET")
            self.assertFalse(module["use_proxy"])
            self.assertEqual(module["follow_redirects"], "none")
            self.assertFalse(module["return_content"])
            self.assertEqual(module["timeout"], 6)
            self.assertNotIn("body", module)
            self.assertEqual(module["headers"]["Host"],
                             "{{ item.hostname }}" if i < 2
                             else "pihole.nexus.sanctum")

    def test_no_sensitive_redirects_or_mutations(self):
        for task in self.play["tasks"]:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <=
                            {"ansible.builtin.assert", "ansible.builtin.uri",
                             "ansible.builtin.debug"}, task["name"])
        for task in self.play["tasks"]:
            if "ansible.builtin.debug" not in task:
                continue
            report = task["ansible.builtin.debug"]["msg"]
            if not isinstance(report, dict):
                continue
            for forbidden in ("location", "content", "cookies", "set_cookie", "body"):
                self.assertNotIn(forbidden, report)
        self.assertNotIn("firewall-cmd", self.source)
        self.assertNotIn("state: started", self.source)
        self.assertNotIn("state: present", self.source)
        self.assertNotIn("yxorp_production_cutover_approved: true", self.source)


if __name__ == "__main__":
    unittest.main()
