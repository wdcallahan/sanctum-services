"""Source protections for opt-in Square-only Kvin stage promotion and probe."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"
PROBE = ROOT / "ansible/yxorp-kvin-stage-square-probe.yml"


class KvinStageSquareContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.manifest = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]
        cls.stage_vars = yaml.safe_load(
            (ROOT / "ansible/vars/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))

    def test_undeployed_default_still_only_yarn(self):
        self.assertIs(self.stage_vars["yxorp_stage_square_approved"], False)
        self.assertIs(self.stage_vars["yxorp_production_cutover_approved"], False)
        self.assertEqual(
            [x["hostname"] for x in self.manifest if x["enabled"]],
            ["yarn.nexus.sanctum"])
        self.assertEqual(len(self.manifest), 8)
        self.assertEqual(self.manifest[1]["hostname"], "square.nexus.sanctum")
        self.assertIs(self.manifest[1]["enabled"], False)

    def test_opt_in_preflight_before_any_role_and_no_production_flag_changes(self):
        pre = self.stage["pre_tasks"]
        review = next(t for t in pre if t["name"].startswith("Require approved Square staging"))
        project = next(t for t in pre if t["name"].startswith("Enable only Square"))
        self.assertEqual(review["when"], "yxorp_stage_square_approved | default(false) | bool")
        self.assertEqual(project["when"], "yxorp_stage_square_approved | default(false) | bool")
        checks = review["ansible.builtin.assert"]["that"]
        for expected in [
            "yxorp_routes | length == 8",
            "yxorp_routes[0].hostname == 'yarn.nexus.sanctum'",
            "yxorp_routes[1].hostname == 'square.nexus.sanctum'",
            "not (yxorp_routes[1].enabled | bool)",
            "yxorp_routes[1].upstream_host == 'kvin.outer.sanctum'",
            "yxorp_routes[1].upstream_port | int == 8085",
        ]:
            self.assertIn(expected, checks)
        self.assertIn("combine({'enabled': true})",
                      project["ansible.builtin.set_fact"]["yxorp_routes"])
        self.assertLess(pre.index(review), pre.index(project))
        self.assertEqual(self.stage["roles"], ["yxorp"])
        self.assertNotIn("firewall-cmd", STAGE.read_text(encoding="utf-8"))
        self.assertNotIn("yxorp_production_cutover_approved: true",
                         STAGE.read_text(encoding="utf-8"))

    def test_read_only_three_specific_square_requests_and_sanitized_report(self):
        self.assertEqual(self.probe["hosts"], "yxorp")
        self.assertFalse(self.probe["become"])
        self.assertEqual(
            self.probe["vars_files"],
            ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        tasks = self.probe["tasks"]
        guard = tasks[0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", guard)
        self.assertIn("yxorp_stage_square_approved | bool", guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", guard)
        task = next(t for t in tasks if t["name"].startswith("Independently request"))
        request = task["ansible.builtin.uri"]
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["headers"]["Host"], "square.nexus.sanctum")
        self.assertIs(request["use_proxy"], False)
        self.assertEqual(request["follow_redirects"], "none")
        self.assertIs(request["return_content"], False)
        self.assertLessEqual(request["timeout"], 8)
        self.assertIs(task["changed_when"], False)
        self.assertIs(task["failed_when"], False)
        self.assertIs(task["no_log"], True)
        self.assertEqual([(x["name"],x["url"]) for x in task["loop"]], [
            ("direct_backend", "http://kvin.outer.sanctum:8085/"),
            ("incumbent_kvar_npm", "http://kvar.outer.sanctum/"),
            ("candidate_kvin_stage", "http://127.0.0.1:80/"),
        ])
        allowed = {"ansible.builtin.assert", "ansible.builtin.uri",
                   "ansible.builtin.debug"}
        for task in tasks:
            keys = [k for k in task if k.startswith("ansible.builtin.")]
            self.assertEqual(len(keys), 1, task["name"])
            self.assertIn(keys[0], allowed)
        debug = next(t for t in tasks if t["name"].startswith("Report only"))
        fields = debug["ansible.builtin.debug"]["msg"]
        for key in ["direct_status", "incumbent_status", "candidate_status",
                    "candidate_and_incumbent_status_equal",
                    "candidate_location_equals_incumbent",
                    "configuration_changed", "limitation"]:
            self.assertIn(key, fields)
        for key in ["cookie", "redirect_value", "location_url", "body"]:
            self.assertNotIn(key, fields)
        self.assertNotIn("firewall-cmd", PROBE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
