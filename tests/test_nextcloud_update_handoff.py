"""No per-app update timer: use existing rootless Podman schedule with a causal hook."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
ANS=ROOT/"ansible"
WF=ROOT/".github/workflows/yxorp-source-check.yml"

class NextcloudSharedPodmanUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file=ANS/"nextcloud-update-handoff-install.yml"
        cls.play=yaml.safe_load(cls.file.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.raw=cls.file.read_text()
        cls.service=(ANS/"files/sanctum-nextcloud-maintenance-update.service").read_text()
        cls.backup=(ANS/"files/sanctum-nextcloud-backup.service").read_text()
        cls.handoff=(ANS/"files/podman-auto-update-nextcloud-handoff.conf").read_text()

    def test_single_update_scheduler_and_explicit_approval(self):
        self.assertEqual(self.play["hosts"],"nextcloud")
        self.assertIs(self.play["become"],False)
        guards=str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for s in ("kvin.outer.sanctum","nextcloud_shared_update_handoff_approved",
                  "nextcloud_complete_restore_qualified_in_source","not ansible_check_mode"):
            self.assertIn(s,guards)
        self.assertIn("is-active, podman-auto-update.timer",self.raw)
        self.assertIn("is-enabled, podman-auto-update.timer",self.raw)
        self.assertIn("is-enabled, sanctum-nextcloud-backup.timer",self.raw)
        self.assertIn("is-enabled, sanctum-nextcloud-maintenance-update.timer",self.raw)
        self.assertIn("Refuse unsafe activation or duplicate Nextcloud update timer",self.raw)
        self.assertIn("AutoUpdate=registry' not in existing_quadlet_lines",self.raw)

    def test_supported_native_on_success_handoff(self):
        self.assertEqual(self.handoff.count("OnSuccess=sanctum-nextcloud-maintenance-update.service"),1)
        self.assertNotIn("OnCalendar=",self.handoff)
        self.assertIn("podman-auto-update.service.d",self.raw)
        self.assertIn("OnSuccess, --value",self.raw)
        self.assertIn("daemon_reload: true",self.raw)
        self.assertIn("scope: user",self.raw)
        self.assertIn("shared_scheduler: podman-auto-update.timer",self.raw)
        self.assertIn("first_natural_shared_update_handoff_not_yet_observed: true",self.raw)
        self.assertNotIn("state: restarted",self.raw)
        self.assertNotIn("state: started",self.raw)

    def test_existing_backup_gate_and_lock_survive_without_new_timer(self):
        lock=".nextcloud-cycle.lock"
        self.assertIn("ansible/nextcloud-maintenance-cycle.yml",self.service)
        self.assertIn(lock,self.service)
        self.assertIn(lock,self.backup)
        self.assertIn("/usr/bin/flock -n",self.service)
        self.assertIn("-e nextcloud_maintenance_cycle_approved=true",self.service)
        self.assertIn("-e nextcloud_maintenance_activation_approved=true",self.service)
        self.assertFalse((ANS/"files/sanctum-nextcloud-maintenance-update.timer").exists())
        self.assertFalse((ANS/"nextcloud-update-schedule-install.yml").exists())
        self.assertFalse((ROOT/"tests/test_nextcloud_update_schedule.py").exists())

    def test_ci_checks_current_path_and_syntax(self):
        w=WF.read_text()
        self.assertIn('"ansible/nextcloud-update-handoff-install.yml"',w)
        self.assertIn('"ansible/files/podman-auto-update-nextcloud-handoff.conf"',w)
        self.assertIn('"tests/test_nextcloud_update_handoff.py"',w)
        self.assertIn("python3 -m unittest discover -s tests -p 'test_nextcloud_update_handoff.py'",w)
        self.assertIn("ansible/nextcloud-update-handoff-install.yml --syntax-check",w)
        self.assertNotIn("test_nextcloud_update_schedule.py",w)
        self.assertNotIn("nextcloud-update-schedule-install.yml",w)

if __name__=="__main__":
    unittest.main()
