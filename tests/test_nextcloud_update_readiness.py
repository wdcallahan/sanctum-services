"""Current Kvin Nextcloud update baseline must be read-only, not a 34→35 upgrade."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/nextcloud-update-readiness.yml"
CI=ROOT/".github/workflows/yxorp-source-check.yml"

class NextcloudUpdateBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.by_name={t["name"]:t for t in cls.tasks}

    def test_exact_kvin_owner_and_approval(self):
        self.assertEqual(self.play["hosts"],"nextcloud")
        self.assertIs(self.play["become"],False)
        guards=self.tasks[0]["ansible.builtin.assert"]["that"]
        for s in ("inventory_hostname == 'kvin.outer.sanctum'",
                  "ansible_facts['user_id'] == 'wdc2'",
                  "nextcloud_update_readiness_approved | default(false) | bool",
                  "nextcloud_readiness_container == 'sanctum-nextcloud'"):
            self.assertIn(s,guards)

    def test_actual_occ_status_from_original_rootless_container(self):
        t=self.by_name["Read actual Nextcloud application status through its own CLI as www-data"]
        self.assertTrue(t["no_log"])
        self.assertIs(t["changed_when"],False)
        argv=t["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[:5],["podman","exec","--user","www-data","--workdir"])
        self.assertEqual(argv[-4:],["php","occ","status","--output=json"])
        self.assertIn("{{ nextcloud_readiness_container }}",argv)
        stat=self.by_name["Observe actual running Nextcloud container identity without revealing env"]
        self.assertTrue(stat["no_log"])
        self.assertIs(stat["changed_when"],False)
        self.assertEqual(stat["ansible.builtin.command"]["argv"][:4],
                         ["podman","inspect","--type","container"])

    def test_reports_actual_version_not_fixed_source_assumption(self):
        report=self.by_name["Report actual Nextcloud update baseline without starting an upgrade"]["ansible.builtin.debug"]["msg"]
        for field in ("actual_version","actual_installed","actual_maintenance_mode",
                      "actual_needs_db_upgrade","running_image_reference",
                      "source_image_reference","running_image_equals_source",
                      "installed_quadlet_image_equals_source",
                      "quadlet_registry_auto_update_declared"):
            self.assertIn(field,report)
        self.assertIn("nextcloud_readiness_occ.stdout",report["actual_version"])
        self.assertTrue(report["nextcloud_or_database_not_modified"])
        self.assertTrue(report["live_update_not_authorized"])

    def test_no_mutation_or_another_account_or_pg_dump(self):
        s=PLAY.read_text()
        for denied in ("podman pull","podman stop","podman run","occ upgrade",
                       "maintenance:mode", "pg_dump", "postgresql.dump",
                       "podman-auto-update", "ansible.builtin.systemd_service",
                       "ansible.builtin.copy:","ansible.builtin.template:",
                       "become: true", "firewall-cmd"):
            self.assertNotIn(denied,s)
        for task in self.tasks:
            if "ansible.builtin.assert" in task:
                self.assertFalse(
                    set(task["ansible.builtin.assert"])-{"that","fail_msg","success_msg","quiet"},
                    task["name"])

    def test_ci_source_and_syntax(self):
        w=CI.read_text()
        self.assertIn("tests/test_nextcloud_update_readiness.py",w)
        self.assertIn("ansible/nextcloud-update-readiness.yml --syntax-check",w)

if __name__=="__main__":
    unittest.main()
