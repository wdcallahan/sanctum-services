"""The ordinary Nextcloud installer cannot silently bypass the recovery-gated updater."""
from pathlib import Path
import unittest

from jinja2 import Template
import yaml

ROOT = Path(__file__).resolve().parents[1]
ANS = ROOT / "ansible"


class RoleUpdaterContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load((ANS / "group_vars/nextcloud.yml").read_text())
        cls.role_tasks = yaml.safe_load((ANS / "roles/nextcloud/tasks/main.yml").read_text())
        cls.task_names = [t["name"] for t in cls.role_tasks]

    def test_desired_image_is_supported_within_major_maintenance_channel(self):
        self.assertEqual(self.config["nextcloud_image"], "docker.io/library/nextcloud:34.0-apache")
        self.assertTrue(self.config["nextcloud_original_frozen_image"].startswith(
            "docker.io/library/nextcloud@sha256:"))
        self.assertIs(self.config["nextcloud_complete_restore_qualified_in_source"], False)

    def test_generic_site_refuses_uncoordinated_image_change_before_any_write(self):
        guard_name = "Refuse ordinary site deployment that would bypass backup-gated image update"
        self.assertIn(guard_name, self.task_names)
        index = self.task_names.index(guard_name)
        self.assertLess(index, self.task_names.index("Create the application storage directory"))
        self.assertLess(index, self.task_names.index("Install Nextcloud Quadlet"))
        self.assertLess(index, self.task_names.index("Observe the active firewall zone for Kvin's service interface"))
        guard = str(self.role_tasks[index]["ansible.builtin.assert"]["that"])
        self.assertIn("'Image=' ~ nextcloud_image", guard)
        self.assertIn("Pull=never", guard)
        self.assertIn("AutoUpdate=registry", guard)
        self.assertIn("nextcloud_role_existing_quadlet.stat.exists", guard)

    def test_managed_source_exactly_matches_canonical_role_template(self):
        template = (ANS / "roles/nextcloud/templates/nextcloud.container.j2").read_text()
        rendered = Template(template).render(
            nextcloud_image=self.config["nextcloud_image"],
            nextcloud_host_port=self.config["nextcloud_host_port"],
            nextcloud_html_dir="/home/wdc2/srv/sanctum-services/nextcloud/html",
            nextcloud_private_config_dir="/home/wdc2/.config/sanctum-services/nextcloud",
        )
        managed = (ANS / "files/sanctum-nextcloud-kvin-maintenance.container").read_text()
        self.assertEqual(rendered.strip(), managed.strip())
        self.assertIn("Pull=never", managed)
        self.assertNotIn("\nAutoUpdate=registry", managed)

    def test_one_time_qualifier_uses_original_frozen_reference(self):
        play = (ANS / "nextcloud-qualify-maintenance-image.yml").read_text()
        self.assertIn("nextcloud_original_frozen_image", play)
        self.assertNotIn("nextcloud_image is match", play)


if __name__ == "__main__":
    unittest.main()
