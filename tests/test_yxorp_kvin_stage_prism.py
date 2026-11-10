"""Source contract: only the approved Kvin stage can add Prism after Yarn+Square."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"
PROBE = ROOT / "ansible/yxorp-kvin-stage-prism-probe.yml"
VARS = ROOT / "ansible/vars/yxorp-kvin-stage.yml"
ROUTES = ROOT / "data/yxorp-routes.yml"


class PrismStageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.variables = yaml.safe_load(VARS.read_text(encoding="utf-8"))
        cls.routes = yaml.safe_load(ROUTES.read_text(encoding="utf-8"))["yxorp_routes"]

    def test_prism_opt_in_default_false_and_manifest_still_yarn_only(self):
        self.assertIs(self.variables["yxorp_stage_prism_approved"], False)
        self.assertIs(self.variables["yxorp_stage_square_approved"], False)
        self.assertIs(self.variables["yxorp_production_cutover_approved"], False)
        self.assertEqual(
            [r["hostname"] for r in self.routes if r["enabled"]],
            ["yarn.nexus.sanctum"])
        self.assertEqual(
            (self.routes[2]["hostname"], self.routes[2]["upstream_host"],
             self.routes[2]["upstream_port"], self.routes[2]["websocket"],
             self.routes[2]["enabled"]),
            ("joule.nexus.sanctum", "kvin.outer.sanctum", 8084, True, False))

    def test_only_prism_projection_after_square_and_before_role(self):
        tasks = self.stage["pre_tasks"]
        names = [t["name"] for t in tasks]
        square = names.index("Enable only Square alongside Yarn in this Kvin stage invocation")
        gate = names.index("Require approved Prism staging on top of Yarn and Square only")
        prism = names.index("Enable only Prism in addition to accepted Yarn and Square on Kvin")
        self.assertLess(square, gate)
        self.assertLess(gate, prism)
        self.assertEqual(self.stage["roles"], ["yxorp"])
        check = tasks[gate]
        self.assertEqual(check["when"], "yxorp_stage_prism_approved | default(false) | bool")
        assert_list = check["ansible.builtin.assert"]["that"]
        for item in (
            "yxorp_stage_square_approved | bool",
            "yxorp_routes[2].hostname == 'joule.nexus.sanctum'",
            "not (yxorp_routes[2].enabled | bool)",
            "yxorp_routes[2].upstream_host == 'kvin.outer.sanctum'",
            "yxorp_routes[2].upstream_port | int == 8084",
            "yxorp_routes[2].websocket | bool",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum']",
        ):
            self.assertIn(item, assert_list)
        projection = tasks[prism]
        self.assertEqual(projection["when"], "yxorp_stage_prism_approved | default(false) | bool")
        self.assertIn("combine({'enabled': true})",
                      projection["ansible.builtin.set_fact"]["yxorp_routes"])
        self.assertIn("yxorp_routes[3:]",
                      projection["ansible.builtin.set_fact"]["yxorp_routes"])
        self.assertNotIn("firewall-cmd", STAGE.read_text(encoding="utf-8"))

    def test_probe_three_exact_host_header_paths_nonfatal_and_private(self):
        self.assertEqual(self.probe["hosts"], "yxorp")
        self.assertFalse(self.probe["become"])
        self.assertFalse(self.probe["gather_facts"])
        self.assertEqual(self.probe["vars_files"],
                         ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        tasks = self.probe["tasks"]
        guard = tasks[0]["ansible.builtin.assert"]["that"]
        for requirement in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_approved | bool",
            "yxorp_stage_square_approved | bool",
            "yxorp_stage_prism_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
        ):
            self.assertIn(requirement, guard)
        observe = tasks[1]
        uri = observe["ansible.builtin.uri"]
        self.assertEqual(uri["method"], "GET")
        self.assertEqual(uri["headers"]["Host"], "joule.nexus.sanctum")
        self.assertFalse(uri["use_proxy"])
        self.assertEqual(uri["follow_redirects"], "none")
        self.assertFalse(uri["return_content"])
        self.assertEqual(uri["timeout"], 8)
        self.assertEqual(
            [(r["name"], r["url"]) for r in observe["loop"]],
            [
                ("direct_backend", "http://kvin.outer.sanctum:8084/"),
                ("incumbent_kvar_npm", "http://kvar.outer.sanctum/"),
                ("candidate_kvin_stage", "http://127.0.0.1:80/"),
            ],
        )
        self.assertFalse(observe["failed_when"])
        self.assertFalse(observe["changed_when"])
        self.assertTrue(observe["no_log"])
        report = tasks[-1]["ansible.builtin.debug"]["msg"]
        for field in ("candidate_status", "incumbent_status", "direct_status",
                      "candidate_and_incumbent_status_equal",
                      "candidate_content_type_equals_incumbent",
                      "candidate_redirect_equals_incumbent",
                      "configuration_changed", "limitation"):
            self.assertIn(field, report)
        for field in ("raw_location", "response_body", "cookie", "error_details"):
            self.assertNotIn(field, report)
        allowed = {"ansible.builtin.assert", "ansible.builtin.uri",
                   "ansible.builtin.debug"}
        for t in tasks:
            modules = {k for k in t if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1)
            self.assertTrue(modules <= allowed)


if __name__ == "__main__":
    unittest.main()
