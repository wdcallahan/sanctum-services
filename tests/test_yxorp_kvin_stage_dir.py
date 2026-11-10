"""Contract for interim LinkStack/Kvar-backed stage canary."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"
PROBE = ROOT / "ansible/yxorp-kvin-stage-dir-probe.yml"
VARS = ROOT / "ansible/vars/yxorp-kvin-stage.yml"
ROUTES = ROOT / "data/yxorp-routes.yml"


class InterimLinkStackStage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.variables = yaml.safe_load(VARS.read_text(encoding="utf-8"))
        cls.routes = yaml.safe_load(ROUTES.read_text(encoding="utf-8"))["yxorp_routes"]

    def test_disabled_by_default_and_origin_still_kvar(self):
        for flag in (
            "yxorp_stage_square_approved", "yxorp_stage_prism_approved",
            "yxorp_stage_search_approved", "yxorp_stage_dir_approved",
            "yxorp_production_cutover_approved",
        ):
            self.assertIs(self.variables[flag], False)
        self.assertEqual([r["hostname"] for r in self.routes if r["enabled"]],
                         ["yarn.nexus.sanctum"])
        d = self.routes[4]
        self.assertEqual((d["hostname"], d["upstream_scheme"],
                          d["upstream_host"], d["upstream_port"],
                          d["websocket"], d["enabled"]),
                         ("dir.nexus.sanctum", "http", "kvar.outer.sanctum",
                          8081, False, False))

    def test_fifth_route_guard_follows_four_previous_projections(self):
        tasks = self.stage["pre_tasks"]
        names = [task["name"] for task in tasks]
        prior = names.index("Enable only Search in addition to three accepted Kvin stage routes")
        guard = names.index("Require LinkStack stage on top of four accepted local HTTP hosts")
        select = names.index(
            "Enable only interim LinkStack with the four accepted Kvin stage routes")
        self.assertLess(prior, guard)
        self.assertLess(guard, select)
        self.assertEqual(self.stage["roles"], ["yxorp"])
        self.assertEqual(tasks[guard]["when"], "yxorp_stage_dir_approved | default(false) | bool")
        self.assertEqual(tasks[select]["when"], "yxorp_stage_dir_approved | default(false) | bool")
        for check in (
            "yxorp_stage_square_approved | bool",
            "yxorp_stage_prism_approved | bool",
            "yxorp_stage_search_approved | bool",
            "yxorp_routes | length == 8",
            "yxorp_routes[4].hostname == 'dir.nexus.sanctum'",
            "not (yxorp_routes[4].enabled | bool)",
            "yxorp_routes[4].upstream_host == 'kvar.outer.sanctum'",
            "yxorp_routes[4].upstream_port | int == 8081",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum', 'joule.nexus.sanctum', 'search.nexus.sanctum']",
        ):
            self.assertIn(check, tasks[guard]["ansible.builtin.assert"]["that"])
        projection = tasks[select]["ansible.builtin.set_fact"]["yxorp_routes"]
        self.assertIn("combine({'enabled': true})", projection)
        self.assertIn("yxorp_routes[5:]", projection)
        self.assertNotIn("firewall-cmd", STAGE.read_text(encoding="utf-8"))

    def test_private_read_only_exact_three_path_probe(self):
        p = self.probe
        self.assertEqual(p["hosts"], "yxorp")
        self.assertFalse(p["become"])
        self.assertFalse(p["gather_facts"])
        self.assertEqual(p["vars_files"],
                         ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        ts = p["tasks"]
        guard = ts[0]["ansible.builtin.assert"]["that"]
        for check in ("inventory_hostname == 'kvin.outer.sanctum'",
                      "yxorp_kvin_stage_approved | bool",
                      "yxorp_stage_dir_approved | bool",
                      "not (yxorp_production_cutover_approved | bool)"):
            self.assertIn(check, guard)
        t = ts[1]
        uri = t["ansible.builtin.uri"]
        self.assertEqual(uri["headers"]["Host"], "dir.nexus.sanctum")
        self.assertEqual(uri["method"], "GET")
        self.assertIs(uri["use_proxy"], False)
        self.assertEqual(uri["follow_redirects"], "none")
        self.assertIs(uri["return_content"], False)
        self.assertEqual(uri["timeout"], 8)
        self.assertEqual(
            [(item["name"], item["url"]) for item in t["loop"]],
            [("direct_backend", "http://kvar.outer.sanctum:8081/"),
             ("incumbent_kvar_npm", "http://kvar.outer.sanctum/"),
             ("candidate_kvin_stage", "http://127.0.0.1:80/")])
        self.assertIs(t["no_log"], True)
        self.assertIs(t["changed_when"], False)
        self.assertIs(t["failed_when"], False)
        report = ts[-1]["ansible.builtin.debug"]["msg"]
        for field in (
            "candidate_status", "incumbent_status", "direct_status",
            "all_three_have_http_response", "candidate_and_incumbent_status_equal",
            "candidate_content_type_equals_incumbent", "candidate_redirect_equals_incumbent",
            "application_migrated_to_kvin", "configuration_changed", "limitation"
        ):
            self.assertIn(field, report)
        self.assertIs(report["application_migrated_to_kvin"], False)
        self.assertNotIn("cookie", report)
        self.assertNotIn("body", report)
        for task in ts:
            mods = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(mods), 1)
            self.assertTrue(mods <= {"ansible.builtin.assert",
                                     "ansible.builtin.uri", "ansible.builtin.debug"})


if __name__ == "__main__":
    unittest.main()
