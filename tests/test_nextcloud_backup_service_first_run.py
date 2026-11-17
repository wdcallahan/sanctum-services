"""The installed user one-shot is exercised once and independently verified.

This is distinct from the accepted original manual backup and from
accepting a future natural Sunday timer firing.
"""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/nextcloud-backup-service-first-run.yml"
WF=ROOT/".github/workflows/yxorp-source-check.yml"


class FirstNativeWeeklyWorker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=PLAY.read_text()
        cls.play=yaml.safe_load(cls.raw)[0]
        cls.tasks=cls.play["tasks"]
        cls.by_name={task["name"]: task for task in cls.tasks}
        cls.names=list(cls.by_name)

    def test_exact_kvin_and_explicit_live_snapshot_approval(self):
        self.assertEqual(self.play["hosts"],"nextcloud")
        self.assertIs(self.play["become"],False)
        guards=self.tasks[0]["ansible.builtin.assert"]["that"]
        for s in ("inventory_hostname == 'kvin.outer.sanctum'",
                  "ansible_facts['user_id'] == 'wdc2'",
                  "nextcloud_first_backup_run_approved | default(false) | bool",
                  "not ansible_check_mode"):
            self.assertIn(s,guards)
        self.assertNotIn("become: true",self.raw)

    def test_uses_installed_weekly_oneshot_not_direct_backup_or_updater(self):
        t=self.by_name["Start only the installed backup oneshot and wait for its actual completion"]
        self.assertEqual(t["ansible.builtin.command"]["argv"], [
            "systemctl","--user","start","{{ nextcloud_first_backup_service }}"
        ])
        self.assertGreaterEqual(t["async"],1200)
        self.assertGreater(t["poll"],0)
        self.assertTrue(t["changed_when"])
        self.assertIn("sanctum-nextcloud-backup.service",self.raw)
        self.assertIn("sanctum-nextcloud-backup.timer",self.raw)
        self.assertNotIn("maintenance:mode,",self.raw)
        self.assertNotIn("podman pull",self.raw)
        self.assertNotIn("pg_dump",self.raw)
        self.assertNotIn("state: restarted",self.raw)

    def test_proves_a_new_recovery_id_and_real_oneshot_result(self):
        def idx(part):
            return next(i for i,n in enumerate(self.names) if part in n)
        self.assertLess(idx("Record pre-run actual Kvin"),idx("Start only the installed"))
        self.assertLess(idx("Start only the installed"),idx("Find completed Kvin"))
        self.assertLess(idx("Find completed Kvin"),idx("Select one fresh"))
        self.assertLess(idx("Select one fresh"),idx("Independently read private"))
        self.assertIn("ExecMainStatus=0",self.raw)
        self.assertIn("Result=success",self.raw)
        self.assertIn("nextcloud_first_fresh_paths | length == 1",self.raw)
        self.assertIn("file_type: directory",self.raw)
        self.assertIn("nextcloud-[0-9]{8}t[0-9]{6}",self.raw)

    def test_genuine_offhost_verification_no_secrets(self):
        manifest=self.by_name["Independently read private source and Peanut manifest metadata"]
        self.assertEqual(manifest["delegate_to"],"{{ item }}")
        self.assertEqual(manifest["ansible.builtin.stat"]["checksum_algorithm"],"sha256")
        self.assertTrue(manifest["no_log"])
        verify=self.by_name["Verify each actual protected recovery bundle using the qualified verifier"]
        self.assertEqual(verify["delegate_to"],"{{ item }}")
        self.assertIn("nextcloud-recovery-bundle.py",str(verify["ansible.builtin.command"]["argv"]))
        self.assertTrue(verify["no_log"])
        report=self.by_name[
            "Report actual installed weekly Nextcloud backup service execution and Peanut recovery acceptance"
        ]["ansible.builtin.debug"]["msg"]
        for k in ("actual_installed_service_executed", "independent_peanut_bundle_verified",
                  "same_manifest_sha256_on_both_hosts","software_update_not_run",
                  "full_application_restore_not_claimed","real_weekly_timer_firing_not_yet_observed"):
            self.assertIs(report[k],True)

    def test_ci_runs_contract_and_ansible_syntax(self):
        wf=WF.read_text()
        self.assertIn("tests/test_nextcloud_backup_service_first_run.py",wf)
        self.assertIn("ansible/nextcloud-backup-service-first-run.yml --syntax-check",wf)


if __name__=="__main__":
    unittest.main()
