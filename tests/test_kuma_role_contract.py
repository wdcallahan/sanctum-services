"""Contract for safe retained Kuma staging without live mutations."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class KumaRoleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vars = yaml.safe_load(
            (ROOT / "ansible/group_vars/kuma.yml").read_text(encoding="utf8")
        )
        cls.tasks = yaml.safe_load(
            (ROOT / "ansible/roles/kuma/tasks/main.yml").read_text(encoding="utf8")
        )
        cls.quadlet = (
            ROOT / "ansible/roles/kuma/templates/kuma.container.j2"
        ).read_text(encoding="utf8")

    def test_source_requires_explicit_approval_and_image(self):
        self.assertIs(self.vars["kuma_stage_approved"], False)
        self.assertEqual(self.vars["kuma_image"], "docker.io/louislam/uptime-kuma:2")
        self.assertEqual(self.vars["kuma_host_port"], 13001)
        self.assertEqual(self.vars["kuma_bind_address"], "127.0.0.1")
        self.assertEqual(self.vars["kuma_data_volume"], "sanctum-kuma-data")
        self.assertEqual(self.vars["kuma_db_type"], "sqlite")
        self.assertIn("kuma_stage_approved | bool",
                      self.tasks[0]["ansible.builtin.assert"]["that"])
        self.assertIn("ansible_facts['architecture'] == 'aarch64'",
                      self.tasks[0]["ansible.builtin.assert"]["that"])
        self.assertIn("kuma_db_type == 'sqlite'",
                      self.tasks[0]["ansible.builtin.assert"]["that"])
        self.assertIn("kuma_image == 'docker.io/louislam/uptime-kuma:2'",
                      self.tasks[0]["ansible.builtin.assert"]["that"])

    def test_volume_and_quadlet_are_idempotent_by_design(self):
        names = [t["name"] for t in self.tasks]
        self.assertLess(names.index("Observe whether the named rootless Kuma data volume exists"),
                        names.index("Create the durable Kuma data volume when absent"))
        self.assertLess(names.index("Observe whether the chosen Kuma 2 channel is locally cached"),
                        names.index("Pull the supported Kuma 2 image channel if absent"))
        self.assertIn("Volume={{ kuma_data_volume }}:/app/data", self.quadlet)
        self.assertIn("AutoUpdate=registry", self.quadlet)
        self.assertIn("Image={{ kuma_image }}", self.quadlet)
        self.assertIn(
            "Environment=UPTIME_KUMA_DB_TYPE={{ kuma_db_type }}", self.quadlet
        )
        self.assertIn("PublishPort={{ kuma_bind_address }}:{{ kuma_host_port }}:3001/tcp",
                      self.quadlet)
        self.assertIn("Network=slirp4netns", self.quadlet)
        self.assertNotIn("firewall-cmd", str(self.tasks))
        self.assertNotIn("kuma_monitors", str(self.tasks))
        systemd = next(t["ansible.builtin.systemd_service"] for t in self.tasks
                       if "ansible.builtin.systemd_service" in t)
        # Quadlet generator applies [Install], so enabling the transient
        # generated service through systemctl is unsupported.
        self.assertNotIn("enabled", systemd)
        self.assertEqual(systemd["scope"], "user")
        self.assertIn("WantedBy=default.target", self.quadlet)

    def test_report_does_not_revoke_previously_accepted_production_state(self):
        self.assertEqual(self.tasks[-1]["name"],
                         "Report actual Kuma service deployment and bounded HTTP readiness")
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertEqual(report["desired_database_backend"], "{{ kuma_db_type }}")
        self.assertTrue(report["registry_auto_update_declared"])
        self.assertIn("banked", report["note"])
        for key in ("app_login_checked_by_this_play",
                    "saved_monitors_checked_by_this_play",
                    "recovery_checked_by_this_play"):
            self.assertIs(report[key], False)
        for key in ("administrator_and_monitor_state_accepted",
                    "backup_restore_and_recovery_accepted",
                    "named_lan_or_production_route_accepted",
                    "next_gate"):
            self.assertNotIn(key, report)


if __name__ == "__main__":
    unittest.main()
