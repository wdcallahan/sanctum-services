"""Regression contract: new project agents must not silently restore rejected policy.

Only assert *wanted runtime policy* and the actual Nextcloud restore contract.
Historical immutable image IDs and bounded cache/offline fixtures may remain.
"""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ANS = ROOT / "ansible"
WF = ROOT / ".github/workflows/yxorp-source-check.yml"


class NewPixelColdStart(unittest.TestCase):
    def test_new_agents_are_directed_to_existing_policies_and_current_frontier(self):
        entry = (ROOT / "AGENTS.md").read_text()
        readme = (ROOT / "README.md").read_text()
        for needed in (
            "Nova-Pixel-Project-Interface-Standard.md",
            "sanctum-maintenance/issues/38",
            "sanctum-maintenance/issues/17",
            "PROJECT_LEAD_INTRODUCTION.md",
            "already accepted",
            "WITHDRAWN command",
            "EXTERNAL OWNER DEPENDENCY",
        ):
            self.assertIn(needed, entry)
        self.assertIn("[AGENTS.md](AGENTS.md)", readme)
        self.assertIn("no user command", readme)
        self.assertIn("sanctum-maintenance/issues/38", readme)

    def test_wanted_images_use_advancing_release_channels_not_frozen_digests(self):
        image_cases = (
            ("group_vars/yxorp.yml", "yxorp_image", "docker.io/library/nginx:stable-alpine"),
            ("group_vars/kuma.yml", "kuma_image", "docker.io/louislam/uptime-kuma:2"),
            ("group_vars/nextcloud.yml", "nextcloud_image", "docker.io/library/nextcloud:34.0-apache"),
        )
        for file, key, expected in image_cases:
            with self.subTest(file=file):
                actual = yaml.safe_load((ANS / file).read_text())[key]
                self.assertEqual(actual, expected)
                self.assertNotIn("@sha256:", actual)
        linkstack = (ANS / "files/sanctum-linkstack-kvin-managed.container").read_text()
        self.assertIn("Image=docker.io/linkstackorg/linkstack:latest", linkstack)
        self.assertIn("AutoUpdate=registry", linkstack)
        self.assertNotIn("Image=docker.io/linkstackorg/linkstack@sha256:", linkstack)

    def test_stateful_nextcloud_update_is_automatic_only_after_consistent_backup(self):
        managed = (ANS / "files/sanctum-nextcloud-kvin-maintenance.container").read_text()
        backup_timer = (ANS / "files/sanctum-nextcloud-backup.timer").read_text()
        updater = (ANS / "nextcloud-maintenance-cycle.yml").read_text()
        install = (ANS / "nextcloud-update-schedule-install.yml").read_text()
        self.assertIn("Image=docker.io/library/nextcloud:34.0-apache", managed)
        self.assertIn("Pull=never", managed)
        self.assertNotIn("AutoUpdate=registry", managed)
        self.assertIn("OnCalendar=Sun *-*-* 03:30:00", backup_timer)
        self.assertIn("nextcloud-consistent-backup.yml", updater)
        self.assertIn("nextcloud-retain-on-peanut.yml", updater)
        self.assertIn("nextcloud-maintenance-activate.yml", updater)
        self.assertIn("nextcloud_complete_restore_qualified_in_source", install)
        self.assertIn("nextcloud_complete_restore_qualified_in_source: false", (ANS / "group_vars/nextcloud.yml").read_text())
        # 34.0.5 frozen source is allowed ONLY as a historical migration
        # baseline, not as the desired updater channel.
        config = yaml.safe_load((ANS / "group_vars/nextcloud.yml").read_text())
        self.assertIn("@sha256:", config["nextcloud_original_frozen_image"])

    def test_recovery_trial_cannot_download_a_rejected_owner_digest(self):
        play = yaml.safe_load((ANS / "nextcloud-isolated-db-trial-on-peanut.yml").read_text())[0]
        src = (ANS / "nextcloud-isolated-db-trial-on-peanut.yml").read_text()
        self.assertEqual(play["vars"]["nextcloud_db_trial_pg_image"], "docker.io/library/postgres:18")
        self.assertNotIn("postgres@sha256:", src)
        names = [task["name"] for task in play["tasks"]]
        owner = "Refuse restore unless Maintenance's actual helper uses the moving PostgreSQL major channel"
        cache = "Cache only supported PostgreSQL 18 major channel when separately approved and absent"
        restore = "Invoke ONLY the Maintenance-owned isolated Nextcloud PostgreSQL restore helper"
        for name in (owner, cache, restore):
            self.assertIn(name, names)
        self.assertLess(names.index(owner), names.index(cache))
        self.assertLess(names.index(owner), names.index(restore))
        self.assertIn("nextcloud_isolated_db_image_cache_approved", src)
        self.assertIn("nextcloud_db_trial_owner_image_contract.stdout", src)

    def test_ci_enforces_regression_contract(self):
        workflow = WF.read_text()
        self.assertIn('"AGENTS.md"', workflow)
        self.assertIn('"tests/test_sanctum_policy_bootstrap.py"', workflow)
        self.assertIn(
            "python3 -m unittest discover -s tests -p 'test_sanctum_policy_bootstrap.py'",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
