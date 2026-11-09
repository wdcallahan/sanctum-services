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
        self.assertEqual(self.vars["kuma_image"], "")
        self.assertEqual(self.vars["kuma_host_port"], 13001)
        self.assertEqual(self.vars["kuma_bind_address"], "127.0.0.1")
        self.assertEqual(self.vars["kuma_data_volume"], "sanctum-kuma-data")
        self.assertIn("kuma_stage_approved | bool",
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
        self.assertIn("PublishPort={{ kuma_bind_address }}:{{ kuma_host_port }}:3001/tcp",
                      self.quadlet)
        self.assertIn("Network=slirp4netns", self.quadlet)
        self.assertNotIn("firewall-cmd", str(self.tasks))
        self.assertNotIn("kuma_monitors", str(self.tasks))


if __name__ == "__main__":
    unittest.main()
