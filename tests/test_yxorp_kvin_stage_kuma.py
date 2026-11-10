"""Exact opt-in, no production changes, private Kuma redirect classification."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"
PROBE = ROOT / "ansible/yxorp-kvin-stage-kuma-probe.yml"


class KumaStageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.vars = yaml.safe_load(
            (ROOT / "ansible/vars/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8"))["yxorp_routes"]

    def test_default_off_and_legacy_kuma_not_migrated(self):
        for name in ("yxorp_stage_square_approved", "yxorp_stage_prism_approved",
                     "yxorp_stage_search_approved", "yxorp_stage_dir_approved",
                     "yxorp_stage_kuma_approved", "yxorp_production_cutover_approved"):
            self.assertIs(self.vars[name], False)
        self.assertEqual(
            [r["hostname"] for r in self.routes if r["enabled"]],
            ["yarn.nexus.sanctum"])
        k = self.routes[5]
        self.assertEqual(
            (k["hostname"], k["upstream_scheme"], k["upstream_host"],
             k["upstream_port"], k["websocket"], k["enabled"]),
            ("kuma.nexus.sanctum", "http", "kvar.outer.sanctum", 3001, True, False))

    def test_only_interim_kuma_after_five_and_before_role(self):
        tasks = self.stage["pre_tasks"]
        names = [t["name"] for t in tasks]
        previous = names.index("Enable only interim LinkStack with the four accepted Kvin stage routes")
        guard = names.index("Require Kuma stage on top of five accepted local HTTP routes")
        opt = names.index("Enable only interim Kuma with five previously accepted Kvin routes")
        self.assertLess(previous, guard)
        self.assertLess(guard, opt)
        self.assertEqual(self.stage["roles"], ["yxorp"])
        self.assertEqual(tasks[guard]["when"], "yxorp_stage_kuma_approved | default(false) | bool")
        self.assertEqual(tasks[opt]["when"], "yxorp_stage_kuma_approved | default(false) | bool")
        checks = tasks[guard]["ansible.builtin.assert"]["that"]
        for expected in (
            "yxorp_stage_square_approved | bool",
            "yxorp_stage_prism_approved | bool",
            "yxorp_stage_search_approved | bool",
            "yxorp_stage_dir_approved | bool",
            "yxorp_routes | length == 8",
            "yxorp_routes[5].hostname == 'kuma.nexus.sanctum'",
            "not (yxorp_routes[5].enabled | bool)",
            "yxorp_routes[5].upstream_host == 'kvar.outer.sanctum'",
            "yxorp_routes[5].upstream_port | int == 3001",
            "yxorp_routes[5].websocket | bool",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum', 'joule.nexus.sanctum', 'search.nexus.sanctum', 'dir.nexus.sanctum']",
        ):
            self.assertIn(expected, checks)
        projection = tasks[opt]["ansible.builtin.set_fact"]["yxorp_routes"]
        self.assertIn("combine({'enabled': true})", projection)
        self.assertIn("yxorp_routes[6:]", projection)
        self.assertNotIn("firewall-cmd", STAGE.read_text(encoding="utf-8"))

    def test_private_nonfatal_exact_three_path_root_redirect_observer(self):
        play = self.probe
        self.assertEqual(play["hosts"], "yxorp")
        self.assertFalse(play["become"])
        self.assertFalse(play["gather_facts"])
        self.assertEqual(play["vars_files"],
                         ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        tasks = play["tasks"]
        checks = tasks[0]["ansible.builtin.assert"]["that"]
        for required in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_approved | bool",
            "yxorp_stage_kuma_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
        ):
            self.assertIn(required, checks)
        request = tasks[1]
        uri = request["ansible.builtin.uri"]
        self.assertEqual(uri["method"], "GET")
        self.assertEqual(uri["headers"]["Host"], "kuma.nexus.sanctum")
        self.assertFalse(uri["use_proxy"])
        self.assertEqual(uri["follow_redirects"], "none")
        self.assertFalse(uri["return_content"])
        self.assertEqual(uri["timeout"], 8)
        self.assertEqual(
            [(x["name"], x["url"]) for x in request["loop"]],
            [
                ("direct_backend", "http://kvar.outer.sanctum:3001/"),
                ("incumbent_kvar_npm", "http://kvar.outer.sanctum/"),
                ("candidate_kvin_stage", "http://127.0.0.1:80/"),
            ])
        self.assertFalse(request["changed_when"])
        self.assertFalse(request["failed_when"])
        self.assertTrue(request["no_log"])
        report = tasks[-1]["ansible.builtin.debug"]["msg"]
        for key in (
            "direct_status", "incumbent_status", "candidate_status",
            "candidate_and_incumbent_status_equal",
            "candidate_redirect_equals_incumbent",
            "candidate_redirect_path_equals_incumbent",
            "candidate_redirect_host_equals_incumbent",
            "candidate_redirect_scheme_equals_incumbent",
            "candidate_redirect_port_class", "incumbent_redirect_port_class",
            "application_migrated_to_kvin", "limitation",
        ):
            self.assertIn(key, report)
        self.assertIs(report["application_migrated_to_kvin"], False)
        self.assertNotIn("url", report)
        self.assertNotIn("cookie", report)
        self.assertNotIn("body", report)
        for task in tasks:
            modules = {x for x in task if x.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1)
            self.assertTrue(modules <= {
                "ansible.builtin.assert", "ansible.builtin.uri", "ansible.builtin.debug"})


if __name__ == "__main__":
    unittest.main()
