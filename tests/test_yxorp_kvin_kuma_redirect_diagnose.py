"""Read-only, non-disclosing contracts for Kuma redirect root-cause classification."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml"


class KumaRedirectDiagnosisContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PROBE.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.text)[0]

    def test_scope_and_read_only_modules(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertFalse(self.play["become"])
        self.assertFalse(self.play["gather_facts"])
        self.assertEqual(self.play["vars_files"], [
            "vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        guard = self.play["tasks"][0]["ansible.builtin.assert"]["that"]
        for check in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_approved | bool",
            "yxorp_stage_square_approved | bool",
            "yxorp_stage_prism_approved | bool",
            "yxorp_stage_search_approved | bool",
            "yxorp_stage_dir_approved | bool",
            "yxorp_stage_kuma_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "yxorp_routes[5].upstream_host == 'kvar.outer.sanctum'",
            "yxorp_routes[5].upstream_port | int == 3001",
        ):
            self.assertIn(check, guard)
        for task in self.play["tasks"]:
            modules = [k for k in task if k.startswith("ansible.builtin.")]
            self.assertEqual(len(modules), 1)
            self.assertIn(modules[0], (
                "ansible.builtin.assert", "ansible.builtin.uri",
                "ansible.builtin.debug"))
        self.assertNotIn("firewall-cmd", self.text)
        self.assertNotIn("state: restarted", self.text)

    def test_bounded_exact_three_path_no_log_requests(self):
        task = self.play["tasks"][1]
        uri = task["ansible.builtin.uri"]
        self.assertEqual(uri["method"], "GET")
        self.assertEqual(uri["headers"]["Host"], "kuma.nexus.sanctum")
        self.assertFalse(uri["use_proxy"])
        self.assertFalse(uri["return_content"])
        self.assertEqual(uri["follow_redirects"], "none")
        self.assertEqual(uri["timeout"], 8)
        self.assertTrue(task["no_log"])
        self.assertFalse(task["changed_when"])
        self.assertFalse(task["failed_when"])
        self.assertEqual(
            [(x["name"], x["url"]) for x in task["loop"]],
            [
                ("direct_kuma_backend", "http://kvar.outer.sanctum:3001/"),
                ("incumbent_kvar_npm", "http://kvar.outer.sanctum/"),
                ("candidate_kvin_stage", "http://127.0.0.1:80/"),
            ])

    def test_safe_classification_report(self):
        report = self.play["tasks"][-1]["ansible.builtin.debug"]["msg"]
        for name in (
            "direct_redirect_host_class",
            "incumbent_redirect_host_class",
            "candidate_redirect_host_class",
            "direct_redirect_port_class",
            "incumbent_redirect_port_class",
            "candidate_redirect_port_class",
            "candidate_and_incumbent_host_equal",
            "candidate_and_direct_host_equal",
            "direct_and_incumbent_host_equal",
            "candidate_and_incumbent_query_equal",
            "candidate_and_incumbent_redirect_equal",
            "configuration_changed",
            "raw_host_url_port_cookie_body_exposed",
        ):
            self.assertIn(name, report)
        self.assertIs(report["configuration_changed"], False)
        self.assertIs(report["raw_host_url_port_cookie_body_exposed"], False)
        for name in ("location", "url", "raw_redirect", "cookie", "response_body",
                     "observed_hostname", "observed_port", "query_value"):
            self.assertNotIn(name, report)
        self.assertIn("urlsplit('hostname')", self.text)
        self.assertIn("urlsplit('port')", self.text)
        self.assertIn("'stage_http_port_80'", self.text)
        self.assertIn("'kuma_backend_port_3001'", self.text)


if __name__ == "__main__":
    unittest.main()
