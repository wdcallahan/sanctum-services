"""Read-only source contract for the Kvin Nginx single-file mount diagnosis."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ansible/yxorp-kvin-stage-mounted-config-observe.yml"


class KvinSquareMountObservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        plays = yaml.safe_load(cls.text)
        assert len(plays) == 1
        cls.play = plays[0]
        cls.tasks = cls.play["tasks"]

    def test_exact_stage_target_and_read_only_privileges(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertTrue(self.play["become"])
        self.assertFalse(self.play["gather_facts"])
        self.assertEqual(self.play["vars_files"], ["vars/yxorp-kvin-stage.yml"])
        assert_task = self.tasks[0]["ansible.builtin.assert"]["that"]
        for check in [
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_deployment_scope == 'kvin_stage'",
            "yxorp_kvin_stage_approved | bool",
            "yxorp_stage_square_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "yxorp_container_name == 'sanctum-yxorp-kvin-stage'",
        ]:
            self.assertIn(check, assert_task)
        allowed = {"ansible.builtin.assert", "ansible.builtin.command",
                   "ansible.builtin.slurp", "ansible.builtin.debug"}
        for task in self.tasks:
            modules = {key for key in task if key.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= allowed)
            if "ansible.builtin.command" in task:
                self.assertIs(task["changed_when"], False)
                self.assertIs(task["failed_when"], False)
        for forbidden in ("ansible.builtin.copy:", "ansible.builtin.file:",
                          "ansible.builtin.template:", "ansible.builtin.systemd_service:",
                          "firewall-cmd", "daemon-reload", "nginx -s reload",
                          "state: restarted", "podman restart", "podman stop"):
            self.assertNotIn(forbidden, self.text)

    def test_actual_published_and_mounted_config_observed_without_exposing_content(self):
        host = next(t for t in self.tasks if t["name"].startswith("Read the published"))
        cand = next(t for t in self.tasks if t["name"].startswith("Read the validated"))
        mounted = next(t for t in self.tasks if t["name"].startswith("Read the bind-mounted"))
        self.assertEqual(host["ansible.builtin.slurp"]["src"], "{{ yxorp_active_config }}")
        self.assertEqual(cand["ansible.builtin.slurp"]["src"], "{{ yxorp_candidate_config }}")
        self.assertTrue(host["no_log"])
        self.assertTrue(cand["no_log"])
        self.assertEqual(
            mounted["ansible.builtin.command"]["argv"],
            ["podman", "exec", "{{ yxorp_container_name }}", "cat", "/etc/nginx/nginx.conf"],
        )
        self.assertTrue(mounted["no_log"])
        output = next(t for t in self.tasks if t["name"].startswith("Report only"))
        fields = output["ansible.builtin.debug"]["msg"]
        for name in [
            "stage_unit_active", "host_active_has_square_vhost",
            "candidate_has_square_vhost", "stage_host_active_equals_candidate",
            "running_container_read_succeeded",
            "container_mount_has_square_vhost", "host_active_equals_container_mount",
            "container_mount_has_yarn_vhost", "square_curl_exit_code",
            "square_curl_http_code", "unknown_host_curl_exit_code",
            "unknown_host_curl_http_code", "no_service_or_config_change",
        ]:
            self.assertIn(name, fields)
        for field in ("raw_config", "location", "cookie", "stderr", "stdout"):
            self.assertNotIn(field, fields)

    def test_exact_bounded_no_response_curl_classification(self):
        tasks = [t for t in self.tasks if t["name"].startswith("Observe ") and
                 ("host-header" in t["name"] or "unmatched host" in t["name"])]
        self.assertEqual(len(tasks), 2)
        for task in tasks:
            args = task["ansible.builtin.command"]["argv"]
            self.assertTrue(task["no_log"])
            self.assertIn("--noproxy", args)
            self.assertIn("--output", args)
            self.assertIn("/dev/null", args)
            self.assertIn("--connect-timeout", args)
            self.assertIn("--max-time", args)
            self.assertIn("http://127.0.0.1:80/", args)
            self.assertEqual(args[args.index("--max-time") + 1], "7")
        self.assertIn("Host: square.nexus.sanctum",
                      tasks[0]["ansible.builtin.command"]["argv"])
        self.assertIn("Host: unmatched-test.invalid",
                      tasks[1]["ansible.builtin.command"]["argv"])


if __name__ == "__main__":
    unittest.main()
