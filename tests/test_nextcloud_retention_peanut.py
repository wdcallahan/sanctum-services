"""Source-only tests for explicit off-Kvin Nextcloud recovery point retention."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/nextcloud-retain-on-peanut.yml"

class NextcloudRetainToPeanut(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]

    def task(self, title):
        return next(t for t in self.tasks if title in t["name"])

    def test_real_peanut_host_and_distinct_approval(self):
        self.assertEqual(self.play["hosts"], "yxorp_test")
        self.assertIs(self.play["become"], False)
        checks=self.task("Require exact Peanut")["ansible.builtin.assert"]["that"]
        for fragment in ("inventory_hostname == 'peanut.arcane.sanctum'",
                         "ansible_user == 'wdc2'",
                         "nextcloud_retain_to_peanut_approved",
                         "nextcloud_recovery_id",
                         "not ansible_check_mode"):
            self.assertTrue(any(fragment in x for x in checks),fragment)
        self.assertEqual(self.play["vars"]["nextcloud_retention_files"],
                         ["manifest.json","nextcloud-html.tar","nextcloud-private.tar","nextcloud-postgresql.dump"])
        self.assertTrue(self.play["vars"]["nextcloud_retention_local"].startswith("{{ nextcloud_retention_root_local"))

    def test_kvin_only_controller_verified_before_copy(self):
        task=self.task("Identify the Ansible controller")
        self.assertEqual(task["delegate_to"],"localhost")
        checks=self.task("Require controller is Kvin")["ansible.builtin.assert"]["that"]
        self.assertTrue(any("kvin.outer.sanctum" in x for x in checks))

    def test_hashes_verified_at_source_and_destination(self):
        src=self.task("Check complete local application")
        self.assertEqual(src["delegate_to"],"localhost")
        self.assertIn("tools/nextcloud-recovery-bundle.py",
                      " ".join(src["ansible.builtin.command"]["argv"]))
        names=[t["name"] for t in self.tasks]
        self.assertLess(names.index("Check complete local application recovery bundle"),
                        names.index("Copy exactly the four recovery artifacts over managed SSH"))
        self.assertLess(names.index("Copy exactly the four recovery artifacts over managed SSH"),
                        names.index("Verify independent actual bytes directly on Peanut using the same source verifier"))
        remote=self.task("Verify independent actual bytes")["ansible.builtin.command"]["argv"]
        self.assertIn("tools/nextcloud-recovery-bundle.py",str(remote))
        c=self.task("Copy exactly the four")["ansible.builtin.copy"]
        self.assertEqual(c["mode"],"0600")
        self.assertIs(c["force"],False)
        self.assertTrue(self.task("Copy exactly the four")["no_log"])

    def test_no_database_writes_or_service_restart(self):
        raw=PLAY.read_text()
        for forbidden in ("pg_restore", "maintenance:mode", "systemctl restart",
                          "podman stop", "become: true", "firewall-cmd",
                          "state: restarted", "kvar.outer.sanctum"):
            self.assertNotIn(forbidden,raw)
        report=self.task("Report actual off-host retention")["ansible.builtin.debug"]["msg"]
        self.assertTrue(report["hashes_and_archive_structures_verified_on_peanut"])
        self.assertFalse(report["database_restore_verified"])
        self.assertFalse(report["nextcloud_application_restore_accepted"])

if __name__=="__main__":
    unittest.main()
