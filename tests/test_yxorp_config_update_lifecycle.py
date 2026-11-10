"""YXORP's single-file bind mount requires a service restart on config replacement."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / "ansible/roles/yxorp/tasks/main.yml"


class YxorpUpdateLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ROLE.read_text(encoding="utf-8")
        cls.tasks = yaml.safe_load(cls.text)

    def test_validate_before_publishing_then_recreate_container_mount(self):
        names = [t["name"] for t in self.tasks]
        for required in (
            "Require Nginx configuration validation in a disposable container",
            "Publish validated Nginx configuration",
            "Install rootful YXORP Quadlet",
            "Start or reconcile YXORP using the system service manager",
            "Check the selected local-only management health endpoint",
        ):
            self.assertIn(required, names)
        ordered = [names.index(x) for x in (
            "Require Nginx configuration validation in a disposable container",
            "Publish validated Nginx configuration",
            "Install rootful YXORP Quadlet",
            "Start or reconcile YXORP using the system service manager",
            "Check the selected local-only management health endpoint",
        )]
        self.assertEqual(ordered, sorted(ordered))
        unit = next(t["ansible.builtin.systemd_service"] for t in self.tasks
                    if t["name"] == "Start or reconcile YXORP using the system service manager")
        self.assertEqual(unit["name"], "{{ yxorp_service_name }}")
        self.assertEqual(unit["daemon_reload"], "{{ yxorp_quadlet_publish.changed }}")
        self.assertEqual(
            unit["state"],
            "{{ 'restarted' if (yxorp_quadlet_publish.changed or yxorp_config_publish.changed) else 'started' }}",
        )

    def test_verify_current_file_is_actually_mounted_before_health_acceptance(self):
        names = [task["name"] for task in self.tasks]
        start = names.index("Start or reconcile YXORP using the system service manager")
        read_host = names.index(
            "Read the published YXORP configuration for post-reconcile verification")
        read_mount = names.index("Read the running container mounted YXORP configuration")
        assert_mount = names.index(
            "Require the running YXORP container uses the validated published file")
        health = names.index("Check the selected local-only management health endpoint")
        self.assertLess(start, read_host)
        self.assertLess(read_host, read_mount)
        self.assertLess(read_mount, assert_mount)
        self.assertLess(assert_mount, health)
        host = self.tasks[read_host]
        container = self.tasks[read_mount]
        check = self.tasks[assert_mount]
        self.assertEqual(host["ansible.builtin.slurp"]["src"], "{{ yxorp_active_config }}")
        self.assertTrue(host["no_log"])
        self.assertEqual(
            container["ansible.builtin.command"]["argv"],
            ["podman", "exec", "{{ yxorp_container_name }}",
             "cat", "/etc/nginx/nginx.conf"],
        )
        self.assertIs(container["ansible.builtin.command"]["strip_empty_ends"], False)
        self.assertFalse(container["changed_when"])
        self.assertTrue(container["no_log"])
        self.assertIn("hash('sha256')", check["ansible.builtin.assert"]["that"][0])
        self.assertTrue(check["no_log"])

    def test_do_not_reload_old_mounted_config_inode(self):
        self.assertNotIn("Reload running Nginx only for a validated config-only change",
                         [task["name"] for task in self.tasks])
        self.assertNotIn("nginx\n      - -s\n      - reload", self.text)
        for task in self.tasks:
            if task["name"].startswith("Start or reconcile YXORP"):
                self.assertNotIn("podman", str(task))
        quadlet = (ROOT / "ansible/roles/yxorp/templates/yxorp.container.j2").read_text(encoding="utf-8")
        self.assertIn("Network=host", quadlet)
        self.assertIn(
            "Volume={{ yxorp_active_config }}:/etc/nginx/nginx.conf:ro,Z", quadlet)
        production = yaml.safe_load(
            (ROOT / "ansible/group_vars/yxorp.yml").read_text(encoding="utf-8"))
        self.assertIs(production["yxorp_production_cutover_approved"], False)
        stage = yaml.safe_load(
            (ROOT / "ansible/vars/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))
        self.assertIs(stage["yxorp_stage_square_approved"], False)
        self.assertIs(stage["yxorp_production_cutover_approved"], False)


if __name__ == "__main__":
    unittest.main()
