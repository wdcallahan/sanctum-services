"""Weekly backup only uses existing proven owner-scoped Kvin+Peanut jobs."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ANS = ROOT / "ansible"
WF = ROOT / ".github/workflows/yxorp-source-check.yml"


class WeeklyNextcloudSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backup = yaml.safe_load((ANS / "nextcloud-scheduled-backup.yml").read_text())
        cls.install = yaml.safe_load((ANS / "nextcloud-backup-schedule-install.yml").read_text())[0]
        cls.service = (ANS / "files/sanctum-nextcloud-backup.service").read_text()
        cls.timer = (ANS / "files/sanctum-nextcloud-backup.timer").read_text()

    def test_exact_source_then_peanut_order(self):
        self.assertEqual(self.backup[0]["hosts"], "nextcloud")
        self.assertIs(self.backup[0]["become"], False)
        self.assertEqual(
            [play["import_playbook"] for play in self.backup[1:]],
            ["nextcloud-consistent-backup.yml", "nextcloud-retain-on-peanut.yml"]
        )
        self.assertIn("nextcloud_scheduled_backup_approved",
                      self.backup[0]["tasks"][0]["ansible.builtin.assert"]["that"][-1])
        self.assertIn("nextcloud_cycle_recovery_id",
                      self.backup[2]["vars"]["nextcloud_recovery_id"])
        self.assertIn("nextcloud_scheduled_backup_approved",
                      self.backup[1]["vars"]["nextcloud_database_export_contract_approved"])

    def test_schedule_install_requires_exact_host_and_opt_in(self):
        self.assertEqual(self.install["hosts"], "nextcloud")
        self.assertIs(self.install["become"], False)
        raw = (ANS / "nextcloud-backup-schedule-install.yml").read_text()
        for required in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "ansible_facts['user_id'] == 'wdc2'",
            "nextcloud_backup_schedule_install_approved",
            "scope: user", "enabled: true", "state: started",
            "current_nextcloud_not_restarted: true",
            "immediate_backup_not_triggered: true",
        ):
            self.assertIn(required, raw)
        self.assertIn("systemd-run", raw)
        self.assertIn("--setenv=PATH=/home/wdc2/.local/bin", raw)
        self.assertIn("nextcloud:yxorp_test", raw)
        names = [t["name"] for t in self.install["tasks"]]
        self.assertLess(
            names.index("Verify unattended user-manager SSH to original Kvin and Peanut without running backup"),
            names.index("Install source-owned weekly backup service and timer without starting a backup"),
        )
        self.assertNotIn("state: restarted", raw)
        self.assertNotIn("become: true", raw)
        self.assertNotIn("pg_dump", raw)
        self.assertNotIn("podman-auto-update", raw)

    def test_weekly_timer_noncatchup_and_backup_only_service(self):
        self.assertIn("Type=oneshot", self.service)
        self.assertIn("UMask=0077", self.service)
        self.assertIn("/usr/bin/flock -n ", self.service)
        self.assertIn("ansible/nextcloud-scheduled-backup.yml", self.service)
        self.assertIn("-e nextcloud_scheduled_backup_approved=true", self.service)
        self.assertNotIn("nextcloud-maintenance-cycle.yml", self.service)
        self.assertNotIn("podman auto-update", self.service)
        self.assertNotIn("rm -", self.service)
        self.assertIn("OnCalendar=Sun *-*-* 03:30:00", self.timer)
        self.assertIn("Persistent=false", self.timer)
        self.assertIn("WantedBy=timers.target", self.timer)

    def test_ci_checks_scheduled_backup_source_and_syntax(self):
        wf = WF.read_text()
        for path in (
            "tests/test_nextcloud_backup_schedule.py",
            "ansible/nextcloud-scheduled-backup.yml",
            "ansible/nextcloud-backup-schedule-install.yml",
            "ansible/files/sanctum-nextcloud-backup.service",
            "ansible/files/sanctum-nextcloud-backup.timer",
        ):
            self.assertIn(path, wf)
        for path in (
            "ansible/nextcloud-scheduled-backup.yml",
            "ansible/nextcloud-backup-schedule-install.yml",
        ):
            self.assertIn(path + " --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
