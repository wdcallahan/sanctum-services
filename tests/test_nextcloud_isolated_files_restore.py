"""Source-only contract for staging a private Nextcloud recovery bundle on Peanut.

The play is intentionally not a database or live application restore.
"""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible" / "nextcloud-isolated-files-restore.yml"


class IsolatedNextcloudFilesRestore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.source)[0]
        cls.tasks = cls.play["tasks"]

    def find(self, name_fragment):
        return next(task for task in self.tasks if name_fragment in task["name"])

    def test_only_peanut_with_explicit_approval_and_named_source(self):
        self.assertEqual(self.play["hosts"], "yxorp_test")
        self.assertIs(self.play["become"], False)
        guard = self.find("Require exact nonproduction host")["ansible.builtin.assert"]["that"]
        for term in (
            "inventory_hostname == 'peanut.arcane.sanctum'",
            "ansible_user == 'wdc2'",
            "not ansible_check_mode",
            "nextcloud_isolated_file_restore_approved",
            "nextcloud_retained_bundle is defined",
            "nextcloud_isolated_recovery_id is defined",
        ):
            self.assertTrue(any(term in check for check in guard), term)
        self.assertNotIn("kvin.outer.sanctum", self.source)
        self.assertNotIn("npm_proxy_legacy", self.source)

    def test_verified_before_writes_and_no_overwrite(self):
        names = [task["name"] for task in self.tasks]
        checked = next(i for i, n in enumerate(names) if "Privately verify complete" in n)
        created = next(i for i, n in enumerate(names) if "Create private restore-trial" in n)
        unpacked = next(i for i, n in enumerate(names) if "Restore only the verified HTML" in n)
        self.assertLess(checked, created)
        self.assertLess(created, unpacked)
        self.assertIn("not (nextcloud_isolated_paths.results[1].stat.exists",
                      self.find("Require existing bundle")["ansible.builtin.assert"]["that"][3])
        verifier = self.find("Privately verify complete")["ansible.builtin.command"]["argv"]
        self.assertEqual(verifier[:3], ["python3", "-c", verifier[2]])
        self.assertIn("tools/nextcloud-recovery-bundle.py", str(self.find("Privately verify complete")))
        self.assertTrue(self.find("Privately verify complete")["no_log"])

    def test_restores_only_two_tar_archives_under_rootless_namespace(self):
        for phrase, tar_name, root_name in (
            ("Restore only the verified HTML", "nextcloud-html.tar", "nextcloud_isolated_html"),
            ("Restore only the verified private-input", "nextcloud-private.tar", "nextcloud_isolated_private"),
        ):
            task = self.find(phrase)
            argv = task["ansible.builtin.command"]["argv"]
            self.assertEqual(argv[:3], ["podman", "unshare", "tar"])
            self.assertIn("--numeric-owner", argv)
            self.assertIn("--preserve-permissions", argv)
            self.assertIn(tar_name, " ".join(argv))
            self.assertIn(root_name, " ".join(argv))
            self.assertTrue(task["no_log"])
        self.assertNotIn("pg_restore", self.source)
        self.assertNotIn("postgresql.dump", self.source)
        self.assertNotIn("podman run", self.source)
        self.assertNotIn("podman exec", self.source)
        self.assertNotIn("systemd_service", self.source)
        self.assertNotIn("state: started", self.source)
        self.assertNotIn("become: true", self.source)

    def test_report_does_not_claim_usable_application(self):
        report = self.find("Report filesystem-only")["ansible.builtin.debug"]["msg"]
        for expected_false in (
            "restore_application_accepted", "live_nextcloud_untouched", "postgres_cluster_untouched",
        ):
            if expected_false == "restore_application_accepted":
                self.assertIs(report[expected_false], False)
            else:
                self.assertIs(report[expected_false], True)
        self.assertIs(report["database_dump_not_imported"], True)
        self.assertIs(report["nextcloud_container_not_started"], True)


if __name__ == "__main__":
    unittest.main()
