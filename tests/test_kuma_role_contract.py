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
        self.assertEqual(self.vars["kuma_image"], (
            "docker.io/louislam/uptime-kuma@sha256:"
            "302aceeca2db79617f195a7549f7c8dfb05375a274b1092c59d81c1fb61a9ab9"
        ))
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
        self.assertIn("kuma_image | default('') is match('^.+@sha256:[0-9a-f]{64}$')",
                      self.tasks[0]["ansible.builtin.assert"]["that"])

    def test_volume_and_quadlet_are_idempotent_by_design(self):
        names = [t["name"] for t in self.tasks]
        self.assertLess(names.index("Observe whether the named rootless Kuma data volume exists"),
                        names.index("Create the durable Kuma data volume when absent"))
        self.assertLess(names.index("Observe whether the exact Kuma image exists"),
                        names.index("Pull the exact pinned image if absent"))
        self.assertIn("Volume={{ kuma_data_volume }}:/app/data", self.quadlet)
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

    def test_stage_reports_only_bounded_http_not_monitor_or_recovery_acceptance(self):
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["stage_approved"], True)
        self.assertIs(report["initial_http_only"], True)
        self.assertIs(report["database_and_admin_setup_accepted"], False)
        self.assertEqual(report["desired_database_backend"], "{{ kuma_db_type }}")
        for key in ("administrator_and_monitor_state_accepted",
                    "backup_restore_and_recovery_accepted",
                    "named_lan_or_production_route_accepted"):
            self.assertIs(report[key], False)


if __name__ == "__main__":
    unittest.main()
