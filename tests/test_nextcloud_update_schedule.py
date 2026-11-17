"""Automatic patch cadence is source-managed but gated behind real restoration."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
ANS=ROOT/"ansible"
WF=ROOT/".github/workflows/yxorp-source-check.yml"


class NextcloudDailyPatchTimer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load((ANS/"nextcloud-update-schedule-install.yml").read_text())[0]
        cls.service=(ANS/"files/sanctum-nextcloud-maintenance-update.service").read_text()
        cls.timer=(ANS/"files/sanctum-nextcloud-maintenance-update.timer").read_text()
        cls.backup=(ANS/"files/sanctum-nextcloud-backup.service").read_text()
        cls.group=yaml.safe_load((ANS/"group_vars/nextcloud.yml").read_text())

    def test_install_is_opt_in_and_refuses_unproven_recovery(self):
        self.assertEqual(self.play["hosts"],"nextcloud")
        self.assertIs(self.play["become"],False)
        self.assertIs(self.group["nextcloud_complete_restore_qualified_in_source"],False)
        g=str(self.play["tasks"][0]["ansible.builtin.assert"]["that"])
        for s in ("kvin.outer.sanctum","user_id","nextcloud_complete_restore_qualified_in_source",
                  "nextcloud_update_schedule_install_approved","not ansible_check_mode"):
            self.assertIn(s,g)
        raw=(ANS/"nextcloud-update-schedule-install.yml").read_text()
        self.assertIn("sanctum-nextcloud-backup.timer",raw)
        self.assertIn("Pull=never",raw)
        self.assertIn("AutoUpdate=registry",raw)
        self.assertIn("ImageName == nextcloud_image",raw)
        self.assertIn("scope: user",raw)
        self.assertIn("nextcloud_not_restarted_by_timer_install: true",raw)
        for forbidden in ("state: restarted","podman pull","maintenance:mode","pg_dump"):
            self.assertNotIn(forbidden,raw)

    def test_daily_and_weekly_jobs_share_same_mutex_and_distinct_cadences(self):
        lock=".nextcloud-cycle.lock"
        self.assertIn("/usr/bin/flock -n ",self.service)
        self.assertIn(lock,self.service)
        self.assertIn(lock,self.backup)
        self.assertIn("ansible/nextcloud-maintenance-cycle.yml",self.service)
        self.assertIn("-e nextcloud_maintenance_cycle_approved=true",self.service)
        self.assertIn("-e nextcloud_maintenance_activation_approved=true",self.service)
        self.assertIn("OnCalendar=*-*-* 04:15:00",self.timer)
        self.assertIn("Persistent=false",self.timer)
        self.assertIn("WantedBy=timers.target",self.timer)
        self.assertNotIn("AutoUpdate=registry",self.timer)
        self.assertNotIn("rm -",self.service)

    def test_full_source_and_syntax_ci(self):
        w=WF.read_text()
        for p in ("tests/test_nextcloud_update_schedule.py",
                  "ansible/nextcloud-update-schedule-install.yml",
                  "ansible/files/sanctum-nextcloud-maintenance-update.service",
                  "ansible/files/sanctum-nextcloud-maintenance-update.timer"):
            self.assertIn(p,w)
        self.assertIn("ansible/nextcloud-update-schedule-install.yml --syntax-check",w)


if __name__=="__main__":
    unittest.main()
