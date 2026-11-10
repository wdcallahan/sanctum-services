"""Bounded, read-only diagnosis of incumbent NPM Yarn's stalled route."""
from pathlib import Path
import re
import unittest

from jinja2 import Environment, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/yxorp-npm-path-diagnose.yml"


class NpmPathDiagnosisContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text(encoding="utf-8")
        cls.plays = yaml.safe_load(cls.source)
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]

    def test_only_two_exact_targets_and_qualified_hosts(self):
        self.assertEqual([p["hosts"] for p in self.plays],
                         ["yxorp", "npm_proxy_legacy"])
        self.assertFalse(self.plays[0]["become"])
        self.assertTrue(self.plays[1]["become"])
        self.assertEqual(self.plays[0]["vars_files"], ["../data/yxorp-routes.yml"])
        expr = self.plays[0]["vars"]["yxorp_redirect_targets"]
        selected = Environment(undefined=StrictUndefined).compile_expression(
            expr.removeprefix("{{").removesuffix("}}").strip()
        )(yxorp_routes=self.routes)
        self.assertEqual(
            {r["hostname"] for r in selected},
            {"kuma.nexus.sanctum", "pihole.nexus.sanctum"})
        self.assertTrue(all(not r["enabled"] for r in selected))
        self.assertIn("not (yxorp_production_cutover_approved | bool)",
                      self.plays[0]["tasks"][0]["ansible.builtin.assert"]["that"])
        self.assertIn("inventory_hostname == 'kvar.outer.sanctum'",
                      self.plays[1]["tasks"][0]["ansible.builtin.assert"]["that"])

    def test_only_get_requests_and_unmodified_existing_npm_container(self):
        for play in self.plays:
            for task in play["tasks"]:
                modules = {k for k in task if k.startswith("ansible.builtin.")}
                self.assertEqual(len(modules), 1, task["name"])
                self.assertTrue(modules <= {
                    "ansible.builtin.assert", "ansible.builtin.uri",
                    "ansible.builtin.command", "ansible.builtin.debug",
                }, task["name"])
                if "ansible.builtin.uri" in task:
                    request = task["ansible.builtin.uri"]
                    self.assertEqual(request["method"], "GET")
                    self.assertFalse(request["use_proxy"])
                    self.assertEqual(request["follow_redirects"], "none")
                    self.assertFalse(request["return_content"])
                    self.assertEqual(request["timeout"], 6)
                    self.assertTrue(task["no_log"])
                    self.assertIs(task["changed_when"], False)
                    self.assertIs(task["failed_when"], False)
                if "ansible.builtin.command" in task:
                    self.assertTrue(task["no_log"])
                    self.assertIs(task["changed_when"], False)
                    self.assertIs(task["failed_when"], False)
                    command = task["ansible.builtin.command"]["argv"]
                    self.assertEqual(command[:5],
                                     ["podman", "exec", "nginx-proxman",
                                      "node", "-e"])
                    script = command[5]
                    self.assertIn("hostname: '192.168.1.110'", script)
                    self.assertIn("Host: 'yarn.inner.sanctum'", script)
                    self.assertIn("timeout: 6000", script)
                    self.assertIn("response.destroy()", script)
                    self.assertNotIn("process.env", script)
                    self.assertNotIn("console.error", script)

    def test_only_sanitized_results_and_redirect_components(self):
        kvin = next(t["ansible.builtin.debug"]["msg"]
                    for t in self.plays[0]["tasks"]
                    if t["name"].startswith("Report authority"))
        for field in ("explicit_ports_equal", "fragments_equal",
                      "authority_equal", "usernames_equal", "passwords_equal"):
            self.assertIn(field, kvin)
        for forbidden in ("dlocation", "nlocation", "direct_location",
                          "incumbent_location", "raw_header", "raw_body"):
            self.assertNotIn(forbidden, kvin)
        kvar = self.plays[1]["tasks"][-1]["ansible.builtin.debug"]["msg"]
        self.assertIn("container_outcome", kvar)
        self.assertIn("host_http_status", kvar)
        for forbidden in ("stdout", "stderr", "content", "cookies", "error"):
            self.assertNotIn(forbidden, kvar)
        self.assertNotIn("firewall-cmd", self.source)
        self.assertNotIn("podman run", self.source)
        self.assertNotIn("state: present", self.source)
        self.assertNotIn("state: started", self.source)
        self.assertNotIn("yxorp_production_cutover_approved: true", self.source)

    def test_node_output_must_match_an_anchored_allowlist(self):
        report = self.plays[1]["tasks"][-1]["vars"]["node_probe"]
        self.assertIn("http_response|timeout|connect_failure", report)
        self.assertIn("not_observed", report)
        self.assertIn("from_json", report)
        self.assertIn("match('^", report)


if __name__ == "__main__":
    unittest.main()
