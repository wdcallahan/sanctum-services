"""Kuma's actual accepted SQLite archive can be retained without service changes."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/kuma-retain-on-peanut.yml"
ARCHIVE = "sanctum-kuma-20261111t144137.tar"
SHA = "97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648"


class KumaOffhostRetention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text())[0]
        cls.tasks = cls.play["tasks"]
        cls.by_name = {t["name"]: t for t in cls.tasks}

    def test_fixed_peanut_approved_target_and_original_archive(self):
        self.assertEqual(self.play["hosts"], "yxorp_test")
        self.assertIs(self.play["become"], False)
        v = self.play["vars"]
        self.assertEqual(v["kuma_retention_archive_name"], ARCHIVE)
        self.assertEqual(v["kuma_retention_archive_sha256"], SHA)
        conditions = self.by_name["Require Peanut-only operation with explicit owner approval"]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'peanut.arcane.sanctum'", conditions)
        self.assertIn("kuma_retain_on_peanut_approved | default(false) | bool", conditions)

    def test_exact_kvin_controller_and_both_end_hash_checks(self):
        identity = self.by_name["Identify controller before opening the local Kvin archive"]
        self.assertEqual(identity["delegate_to"], "localhost")
        source = self.by_name["Stat actual Kvin source archive and compute its SHA256"]
        self.assertEqual(source["delegate_to"], "localhost")
        self.assertEqual(source["ansible.builtin.stat"]["checksum_algorithm"], "sha256")
        self.assertIn("kuma_retention_local_stat.stat.checksum == kuma_retention_archive_sha256",
                      self.by_name["Require the exact previously accepted unmodified source archive"]["ansible.builtin.assert"]["that"])
        target = self.by_name["Independently compute retained Peanut archive SHA256"]
        self.assertNotIn("delegate_to", target)
        self.assertEqual(target["ansible.builtin.stat"]["checksum_algorithm"], "sha256")
        self.assertIn("kuma_retention_remote_stat.stat.checksum == kuma_retention_archive_sha256",
                      self.by_name["Require actual independent archive bytes and private permissions"]["ansible.builtin.assert"]["that"])

    def test_no_database_mutation_and_transfer_metadata_visible(self):
        copy = self.by_name["Copy one already-qualified Kuma volume archive to Peanut"]
        self.assertIs(copy["diff"], False)
        self.assertEqual(copy["ansible.builtin.copy"]["mode"], "0600")
        self.assertIs(copy["ansible.builtin.copy"]["force"], False)
        self.assertFalse(copy.get("no_log", False))
        raw = PLAY.read_text()
        for forbidden in ("podman stop", "podman run", "podman volume rm",
                          "pg_restore", "maintenance:mode", "scope: user",
                          "systemctl restart", "become: true", "vault.key"):
            self.assertNotIn(forbidden, raw)
        report = self.by_name["Report genuine Kuma off-host copy without overclaiming full recovery"]["ansible.builtin.debug"]["msg"]
        self.assertTrue(report["copy_verified_on_peanut"])
        self.assertFalse(report["complete_disaster_recovery_accepted"])


if __name__ == "__main__":
    unittest.main()
