"""Guard exact read-only discrepancy classifications and redirect secrecy."""
from pathlib import Path
import unittest

from jinja2 import Environment, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/yxorp-discrepancies-observe.yml"


class YxorpDiscrepancyObservationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.source)[0]
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]

    def test_actual_jinja_selects_only_two_declared_disabled_routes(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertFalse(self.play["become"])
        self.assertEqual(self.play["vars_files"], ["../data/yxorp-routes.yml"])
        expression = self.play["vars"]["yxorp_redirect_targets"]
        expression = expression.removeprefix("{{").removesuffix("}}").strip()
        targets = Environment(undefined=StrictUndefined).compile_expression(
            expression)(yxorp_routes=self.routes)
        self.assertEqual(
            {t["hostname"] for t in targets},
            {"kuma.nexus.sanctum", "pihole.nexus.sanctum"})
        self.assertTrue(all(not t["enabled"] for t in targets))
        guard = self.play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", guard)

    def test_two_matching_redirect_http_requests_and_no_log(self):
        calls = [t for t in self.play["tasks"] if "ansible.builtin.uri" in t]
        self.assertEqual(len(calls), 2)
        for task in calls:
            req = task["ansible.builtin.uri"]
            self.assertTrue(task["no_log"])
            self.assertIs(task["changed_when"], False)
            self.assertIs(task["failed_when"], False)
            self.assertEqual(task["loop"], "{{ yxorp_redirect_targets }}")
            self.assertEqual(req["timeout"], 6)
            self.assertEqual(req["method"], "GET")
            self.assertFalse(req["use_proxy"])
            self.assertEqual(req["follow_redirects"], "none")
            self.assertFalse(req["return_content"])
            self.assertEqual(req["headers"], {"Host": "{{ item.hostname }}"})
            self.assertNotIn("body", req)
            self.assertIn("'/admin/' if item.hostname == 'pihole.nexus.sanctum' else '/'",
                          req["url"])
        self.assertIn("item.upstream_host", calls[0]["ansible.builtin.uri"]["url"])
        self.assertIn("http://kvar.outer.sanctum", calls[1]["ansible.builtin.uri"]["url"])

    def test_only_curl_exit_code_no_raw_stderr_and_bounded(self):
        commands = [t for t in self.play["tasks"] if "ansible.builtin.command" in t]
        self.assertEqual(len(commands), 1)
        task = commands[0]
        args = task["ansible.builtin.command"]["argv"]
        self.assertTrue(task["no_log"])
        self.assertIs(task["changed_when"], False)
        self.assertIs(task["failed_when"], False)
        for s in ("--max-time", "7", "--connect-timeout", "3",
                  "--output", "/dev/null", "--noproxy", "*",
                  "Host: yarn.inner.sanctum"):
            self.assertIn(s, args)
        self.assertEqual(args[-1], "http://kvar.outer.sanctum/")
        self.assertNotIn("stderr", self.source[self.source.index(
            "- name: Report only curl's safe numeric outcome"):])

    def test_no_host_mutations_no_full_location_output(self):
        allowed = {"ansible.builtin.uri", "ansible.builtin.assert",
                   "ansible.builtin.debug", "ansible.builtin.command"}
        for task in self.play["tasks"]:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1)
            self.assertTrue(modules <= allowed)
        report = next(t for t in self.play["tasks"]
                      if t["name"].startswith("Report redirect shapes"))
        fields = report["ansible.builtin.debug"]["msg"]
        for forbidden in ("direct_location", "incumbent_location", "direct_host",
                          "incumbent_host", "redirect_path", "redirect_query",
                          "content", "cookies"):
            self.assertNotIn(forbidden, fields)
        self.assertIn("redirect_paths_equal", fields)
        self.assertIn("redirect_values_equal", fields)
        self.assertIn("direct_host_class", fields)
        self.assertIn("incumbent_host_class", fields)
        self.assertIn("urlsplit('hostname')", self.source)
        self.assertNotIn("state: present", self.source)
        self.assertNotIn("firewall-cmd", self.source)


if __name__ == "__main__":
    unittest.main()
