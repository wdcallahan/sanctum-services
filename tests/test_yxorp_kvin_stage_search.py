"""Contract for default-off Search canary over the accepted Kvin stage routes."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"
PROBE = ROOT / "ansible/yxorp-kvin-stage-search-probe.yml"
VARS = ROOT / "ansible/vars/yxorp-kvin-stage.yml"
ROUTES = ROOT / "data/yxorp-routes.yml"


class SearchStageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.variables = yaml.safe_load(VARS.read_text(encoding="utf-8"))
        cls.routes = yaml.safe_load(ROUTES.read_text(encoding="utf-8"))["yxorp_routes"]

    def test_search_default_off_and_exact_disabled_upstream(self):
        for name in (
            "yxorp_stage_square_approved",
            "yxorp_stage_prism_approved",
            "yxorp_stage_search_approved",
            "yxorp_production_cutover_approved",
        ):
            self.assertIs(self.variables[name], False)
        self.assertEqual(
            [x["hostname"] for x in self.routes if x["enabled"]],
            ["yarn.nexus.sanctum"])
        self.assertEqual(
            (self.routes[3]["hostname"], self.routes[3]["upstream_host"],
             self.routes[3]["upstream_port"], self.routes[3]["websocket"],
             self.routes[3]["enabled"]),
            ("search.nexus.sanctum", "kvin.outer.sanctum", 8083, False, False))

    def test_search_only_opt_in_after_square_and_prism_and_before_role(self):
        tasks = self.stage["pre_tasks"]
        names = [t["name"] for t in tasks]
        a = names.index("Enable only Square alongside Yarn in this Kvin stage invocation")
        b = names.index("Enable only Prism in addition to accepted Yarn and Square on Kvin")
        c = names.index("Require Search staging on top of Yarn Square and Prism only")
        d = names.index("Enable only Search in addition to three accepted Kvin stage routes")
        self.assertLess(a, b)
        self.assertLess(b, c)
        self.assertLess(c, d)
        self.assertEqual(self.stage["roles"], ["yxorp"])
        checks = tasks[c]["ansible.builtin.assert"]["that"]
        self.assertEqual(
            tasks[c]["when"], "yxorp_stage_search_approved | default(false) | bool")
        self.assertEqual(
            tasks[d]["when"], "yxorp_stage_search_approved | default(false) | bool")
        for item in (
            "yxorp_stage_square_approved | bool",
            "yxorp_stage_prism_approved | bool",
            "yxorp_routes | length == 8",
            "yxorp_routes[3].hostname == 'search.nexus.sanctum'",
            "not (yxorp_routes[3].enabled | bool)",
            "yxorp_routes[3].upstream_host == 'kvin.outer.sanctum'",
            "yxorp_routes[3].upstream_port | int == 8083",
            "not (yxorp_routes[3].websocket | bool)",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum', 'joule.nexus.sanctum']",
        ):
            self.assertIn(item, checks)
        selection = tasks[d]["ansible.builtin.set_fact"]["yxorp_routes"]
        self.assertIn("combine({'enabled': true})", selection)
        self.assertIn("yxorp_routes[4:]", selection)
        self.assertNotIn("firewall-cmd", STAGE.read_text(encoding="utf-8"))

    def test_anonymous_bounded_nonfatal_three_target_probe(self):
        p = self.probe
        self.assertEqual(p["hosts"], "yxorp")
        self.assertFalse(p["become"])
        self.assertFalse(p["gather_facts"])
        self.assertEqual(p["vars_files"],
                         ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        tasks = p["tasks"]
        guard = tasks[0]["ansible.builtin.assert"]["that"]
        for item in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_approved | bool",
            "yxorp_stage_square_approved | bool",
            "yxorp_stage_prism_approved | bool",
            "yxorp_stage_search_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
        ):
            self.assertIn(item, guard)
        t = tasks[1]
        uri = t["ansible.builtin.uri"]
        self.assertEqual(uri["method"], "GET")
        self.assertEqual(uri["headers"]["Host"], "search.nexus.sanctum")
        self.assertFalse(uri["use_proxy"])
        self.assertEqual(uri["follow_redirects"], "none")
        self.assertFalse(uri["return_content"])
        self.assertEqual(uri["timeout"], 8)
        self.assertEqual(
            [(i["name"], i["url"]) for i in t["loop"]],
            [
                ("direct_backend", "http://kvin.outer.sanctum:8083/"),
                ("incumbent_kvar_npm", "http://kvar.outer.sanctum/"),
                ("candidate_kvin_stage", "http://127.0.0.1:80/"),
            ],
        )
        self.assertIs(t["changed_when"], False)
        self.assertIs(t["failed_when"], False)
        self.assertTrue(t["no_log"])
        report = tasks[-1]["ansible.builtin.debug"]["msg"]
        for item in (
            "direct_status", "incumbent_status", "candidate_status",
            "candidate_and_incumbent_status_equal",
            "candidate_content_type_equals_incumbent",
            "candidate_redirect_equals_incumbent",
            "all_three_have_http_response",
            "configuration_changed", "limitation",
        ):
            self.assertIn(item, report)
        self.assertNotIn("cookie", report)
        self.assertNotIn("body", report)
        allowed = {"ansible.builtin.assert", "ansible.builtin.uri", "ansible.builtin.debug"}
        for task in tasks:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1)
            self.assertTrue(modules <= allowed)


if __name__ == "__main__":
    unittest.main()
