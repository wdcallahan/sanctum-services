"""Read-only direct YXORP backend discovery before any name cutover."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/yxorp-upstreams-observe.yml"


class YxorpUpstreamsObserveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.source)[0]
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]

    def test_exact_client_closed_cutover_and_same_declaration(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertFalse(self.play["become"])
        self.assertFalse(self.play["gather_facts"])
        self.assertEqual(self.play["vars_files"], ["../data/yxorp-routes.yml"])
        guard = self.play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", guard)
        self.assertEqual(len(self.routes), 8)
        self.assertEqual(sum(bool(r["enabled"]) for r in self.routes), 1)

    def test_anonymous_same_host_bounded_read_only_get_per_route(self):
        play = self.play
        probe = next(t for t in play["tasks"] if "ansible.builtin.uri" in t)
        module = probe["ansible.builtin.uri"]
        self.assertEqual(module["method"], "GET")
        self.assertEqual(module["headers"], {"Host": "{{ item.hostname }}"})
        self.assertEqual(module["url"], "http://{{ item.upstream_host }}:{{ item.upstream_port }}/")
        self.assertFalse(module["use_proxy"])
        self.assertEqual(module["follow_redirects"], "none")
        self.assertFalse(module["return_content"])
        self.assertEqual(module["timeout"], 6)
        self.assertTrue(probe["no_log"])
        self.assertIs(probe["changed_when"], False)
        self.assertIs(probe["failed_when"], False)
        self.assertEqual(probe["loop"], "{{ yxorp_routes }}")

    def test_no_lifecycle_or_firewall_changes_and_no_content_logs(self):
        for task in self.play["tasks"]:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1)
            self.assertTrue(
                modules <= {"ansible.builtin.assert", "ansible.builtin.uri",
                            "ansible.builtin.debug"})
        output = next(t for t in self.play["tasks"]
                      if t["name"].startswith("Report sanitized HTTP"))
        self.assertEqual(
            output["loop"], "{{ yxorp_upstream_probe.results }}")
        report = output["ansible.builtin.debug"]["msg"]
        self.assertIn("observed_http_status", report)
        self.assertIn("enabled_in_desired_source", report)
        for excluded in ("content", "cookies", "set_cookie", "location",
                         "msg", "body"):
            self.assertNotIn(excluded, report)
        self.assertNotIn("state: started", self.source)
        self.assertNotIn("state: present", self.source)
        self.assertNotIn("firewall-cmd", self.source)


if __name__ == "__main__":
    unittest.main()
