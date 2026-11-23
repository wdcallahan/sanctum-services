"""One-time review of the already-running recovered and promoted Nextcloud."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/nextcloud-post-promotion-accept-on-kvin.yml"
CI = ROOT / ".github/workflows/yxorp-source-check.yml"

class PostPromotionAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text()
        cls.play = yaml.safe_load(cls.source)[0]
        cls.tasks = cls.play["tasks"]
        cls.names = [t["name"] for t in cls.tasks]

    def find(self, name):
        return next(t for t in self.tasks if name in t["name"])

    def test_exact_latched_one_time_scope(self):
        self.assertEqual(self.play["hosts"], "nextcloud")
        self.assertIs(self.play["become"], False)
        v = self.play["vars"]
        self.assertEqual(v["nextcloud_review_recovery_id"], "nextcloud-20261122t164508")
        self.assertEqual(v["nextcloud_review_expected_version"], "34.0.6.2")
        self.assertTrue(v["nextcloud_review_halt"].endswith("/.update-halted"))
        guard = "\n".join(self.find("Require exact authorized")["ansible.builtin.assert"]["that"])
        self.assertIn("nextcloud_post_promotion_accept_approved", guard)
        self.assertIn("not ansible_check_mode", guard)
        self.assertIn("kvin.outer.sanctum", guard)

    def test_read_only_checks_before_latch_release(self):
        release_name = "Release only this accepted completed promotion's failure latch"
        self.assertIn(release_name, self.names)
        release = self.find(release_name)["ansible.builtin.file"]
        self.assertEqual(release["state"], "absent")
        self.assertEqual(release["path"], "{{ nextcloud_review_halt }}")
        i = self.names.index(release_name)
        for needed in ("Require latch identifies only", "Require running candidate image",
                       "Require the actual completed", "Require HTTP and OCC",
                       "Require existing Calendar", "Require existing 8085"):
            self.assertLess(self.names.index(self.find(needed)["name"]), i)
        for t in self.tasks[:i]:
            self.assertNotIn("ansible.builtin.copy", t)
            self.assertNotIn("ansible.builtin.systemd_service", t)
            self.assertNotIn("ansible.builtin.file", t)
        self.assertIn("no_log: true", self.source)

    def test_calendar_compatibility_accepts_actual_native_6_7_not_exact_old_pin(self):
        check = self.find("Require enabled stable Calendar")
        conditions = "\\n".join(check["ansible.builtin.assert"]["that"])
        self.assertIn("enabled.calendar is defined", conditions)
        self.assertIn("enabled.calendar is match(", conditions)
        self.assertIn("ansible.builtin.version('6.7.0', '>=', version_type='pep440')", conditions)
        self.assertNotIn("enabled.calendar == '6.6.2'", self.source)
        self.assertIn("calendar_version_enabled", self.source)

    def test_no_other_mutations_or_recovery_repetition(self):
        for prohibited in ("podman pull", "podman run", "podman rm",
                           "state: restarted", "state: started",
                           "pg_restore", "pg_dump", "maintenance:mode",
                           "occ upgrade", "nextcloud-consistent-backup.yml",
                           "nextcloud-retain-on-peanut.yml"):
            self.assertNotIn(prohibited, self.source)
        self.assertEqual(len([t for t in self.tasks if "ansible.builtin.file" in t]), 1)
        self.assertIn("calendar_version_enabled", self.source)
        self.assertIn("original_persistent_mounts_preserved", self.source)

    def test_ci_source_and_syntax(self):
        w = CI.read_text()
        self.assertIn('"ansible/nextcloud-post-promotion-accept-on-kvin.yml"', w)
        self.assertIn('"tests/test_nextcloud_post_promotion_accept.py"', w)
        self.assertIn("python3 -m unittest discover -s tests -p 'test_nextcloud_post_promotion_accept.py'", w)
        self.assertIn("ansible/nextcloud-post-promotion-accept-on-kvin.yml --syntax-check", w)

if __name__ == "__main__":
    unittest.main()
