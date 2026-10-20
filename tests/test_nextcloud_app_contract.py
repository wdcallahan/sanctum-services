"""Static guardrails for Nextcloud's pinned third-party app management."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
ANSIBLE = ROOT / "ansible"


class NextcloudAppsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = yaml.safe_load((ANSIBLE / "nextcloud-apps.yml").read_text())
        cls.site = yaml.safe_load((ANSIBLE / "site.yml").read_text())
        cls.apps_play = yaml.safe_load((ANSIBLE / "apps.yml").read_text())
        cls.main = yaml.safe_load(
            (ANSIBLE / "roles/nextcloud_apps/tasks/main.yml").read_text()
        )
        cls.manage = yaml.safe_load(
            (ANSIBLE / "roles/nextcloud_apps/tasks/manage.yml").read_text()
        )

    def test_manifest_empty_by_default_not_an_unplanned_install(self):
        self.assertEqual(self.manifest["nextcloud_extra_apps"], [])

    def test_site_reconciles_after_base_role_and_installer(self):
        play = self.site[0]
        self.assertIn("nextcloud-apps.yml", play["vars_files"])
        self.assertEqual(play["roles"][0], "nextcloud")
        self.assertEqual(play["roles"][1]["role"], "nextcloud_apps")
        self.assertTrue(any("nextcloud_status" in expr for expr in
                            play["roles"][1]["when"]))

    def test_app_only_playbook_does_not_redeploy_container(self):
        self.assertIn("nextcloud-apps.yml", self.apps_play[0]["vars_files"])
        role_imports = [
            task["ansible.builtin.import_role"]["name"]
            for task in self.apps_play[0]["tasks"]
            if "ansible.builtin.import_role" in task
        ]
        self.assertEqual(role_imports, ["nextcloud_apps"])

    def test_no_appstore_latest_install_or_forced_compatibility(self):
        combined = repr(self.main) + repr(self.manage)
        self.assertNotIn("app:install", combined)
        self.assertNotIn("app:update", combined)
        self.assertNotIn("app:remove", combined)
        self.assertNotIn("--force", combined)
        self.assertIn("app:enable", combined)
        self.assertIn("app:disable", combined)
        self.assertIn("sha256:", combined)

    def test_read_state_before_mutations(self):
        names = [task["name"] for task in self.main]
        self.assertLess(names.index("Reject drift in any already installed pinned app"),
                        names.index("Reconcile approved applications one at a time"))
        self.assertIn("app:list", repr(self.main))


if __name__ == "__main__":
    unittest.main()
