"""Source contracts for nonfatal Kvin stage/direct-Yarn comparison."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ansible/yxorp-kvin-yarn-transport-diagnose.yml"


class KvinYarnTransportDiagnosisContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        plays = yaml.safe_load(cls.text)
        assert len(plays) == 1
        cls.play = plays[0]
        cls.tasks = cls.play["tasks"]

    def test_read_only_exact_observer_and_closed_cutover(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertFalse(self.play["become"])
        self.assertFalse(self.play["gather_facts"])
        self.assertEqual(self.play["vars_files"], ["vars/yxorp-kvin-stage.yml"])
        guard = self.tasks[0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", guard)
        self.assertIn("yxorp_deployment_scope == 'kvin_stage'", guard)
        self.assertIn("yxorp_kvin_stage_approved | bool", guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", guard)
        allowed = {"ansible.builtin.assert", "ansible.builtin.uri",
                   "ansible.builtin.command", "ansible.builtin.debug"}
        for task in self.tasks:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= allowed, task["name"])
            if "ansible.builtin.command" in task:
                self.assertIs(task["changed_when"], False)
                self.assertIs(task["failed_when"], False)
        self.assertNotIn("firewall-cmd", self.text)
        self.assertNotIn("state: restarted", self.text)
        self.assertNotIn("ansible.builtin.file:", self.text)
        self.assertNotIn("ansible.builtin.template:", self.text)

    def test_four_fixed_bounded_independent_observations(self):
        task = next(t for t in self.tasks if t["name"].startswith("Independently probe"))
        uri = task["ansible.builtin.uri"]
        self.assertEqual(uri["url"], "{{ item.url }}")
        self.assertEqual(uri["headers"]["Host"], "{{ item.host_header }}")
        self.assertEqual(uri["method"], "GET")
        self.assertIs(uri["use_proxy"], False)
        self.assertEqual(uri["follow_redirects"], "none")
        self.assertTrue(uri["return_content"])
        self.assertEqual(uri["status_code"], [200])
        self.assertEqual(uri["timeout"], 7)
        self.assertIs(task["changed_when"], False)
        self.assertIs(task["failed_when"], False)
        self.assertTrue(task["no_log"])
        entries = task["loop"]
        self.assertEqual(
            [(i["name"], i["url"]) for i in entries], [
                ("stage_health", "http://127.0.0.1:80/__yxorp_health"),
                ("stage_yarn", "http://127.0.0.1:80/"),
                ("origin_hostname", "http://yarn.inner.sanctum/"),
                ("origin_literal_ip", "http://192.168.1.110/"),
            ])
        self.assertEqual(
            [x["host_header"] for x in entries[1:]],
            ["yarn.nexus.sanctum"] * 3)

    def test_dns_and_output_sanitization(self):
        resolve = next(t for t in self.tasks if t["name"].startswith("Look up actual Yarn"))
        self.assertEqual(resolve["ansible.builtin.command"]["argv"],
                         ["getent", "ahostsv4", "yarn.inner.sanctum"])
        self.assertTrue(resolve["no_log"])
        self.assertFalse(resolve["changed_when"])
        self.assertFalse(resolve["failed_when"])
        report = next(t for t in self.tasks if t["name"].startswith("Report only"))
        fields = report["ansible.builtin.debug"]["msg"]
        for field in ("stage_unit_active", "stage_health_status",
                      "stage_health_ready", "stage_yarn_status",
                      "direct_hostname_status", "direct_literal_ip_status",
                      "host_resolution_includes_previously_accepted_ip",
                      "stage_and_direct_hostname_bodies_equal_if_both_200",
                      "stage_and_direct_ip_bodies_equal_if_both_200",
                      "configuration_changed"):
            self.assertIn(field, fields)
        self.assertNotIn("raw_origin", fields)
        self.assertNotIn("origin_body", fields)
        self.assertNotIn("error_text", fields)
        self.assertNotIn("stdout", fields)
        self.assertIn("not_comparable", self.text)
        self.assertNotIn("register: uri", self.text)


if __name__ == "__main__":
    unittest.main()
