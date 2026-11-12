"""Pi-hole Kvar-to-Kvin real archive transfer and rootful volume import contract."""
from pathlib import Path
import ast
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/pihole-kvin-restore.yml"
HELPER=ROOT/"tools/stream-pihole-snapshot.py"
CI=ROOT/".github/workflows/yxorp-source-check.yml"

class PiHoleKvinRestoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]

    def test_exact_kvin_and_exclusive_approval(self):
        self.assertEqual(self.play["hosts"],"yxorp")
        self.assertFalse(self.play["become"])
        guard=str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for x in ("kvin.outer.sanctum","aarch64","wdc2",
                  "sanctum_pihole_kvin_restore_approved","not ansible_check_mode"):
            self.assertIn(x,guard)
        self.assertEqual(len(self.play["vars"]["pihole_kvin_restore_items"]),2)
        self.assertEqual([v["type"] for v in self.play["vars"]["pihole_kvin_restore_items"]],
                         ["etc-pihole","etc-dnsmasq"])

    def test_no_broad_backup_mutation_and_distinct_rootful_volume_import(self):
        src=PLAY.read_text()
        self.assertNotIn("pihole.service",src)
        self.assertNotIn("podman volume rm",src)
        self.assertNotIn("firewall-cmd",src)
        self.assertNotIn("yxorp_production_cutover_approved",src)
        self.assertIn("podman",src)
        transfer=next(t for t in self.tasks if t["name"].startswith("Stream and verify"))
        self.assertTrue(transfer["no_log"])
        precheck=next(t for t in self.tasks if t["name"].startswith("Require distinct rootful"))
        self.assertTrue(precheck["become"])
        assert_names=[t["name"] for t in self.tasks]
        self.assertLess(assert_names.index("Refuse overwriting an existing volume or partial prior import"),
                        assert_names.index("Create two rootful Kvin destination volumes without touching old services"))
        imp=next(t for t in self.tasks if t["name"].startswith("Import exact"))
        self.assertTrue(imp["become"])
        self.assertTrue(imp["no_log"])
        self.assertEqual(imp["ansible.builtin.command"]["argv"][:3],["podman","volume","import"])

    def test_remote_stream_never_outputs_private_content_or_overwrites_existing_archives(self):
        ast.parse(HELPER.read_text())
        script=HELPER.read_text()
        for word in ("BatchMode=yes","StrictHostKeyChecking=yes","sudo",'"-n"',
                     "os.O_EXCL", "hashlib.sha256", "spec[\"sha256\"]",
                     "spec[\"bytes\"]", "os.rename(partial, dest)"):
            self.assertIn(word,script)
        self.assertNotIn("shell=True",script)
        self.assertNotIn("chmod 777",script)
        self.assertNotIn("stderr=subprocess.PIPE",script)
        self.assertIn("pihole-etc-20261112t161524.tar",script)
        self.assertIn("pihole-dnsmasq-20261112t161524.tar",script)

    def test_source_ci_includes_real_playbook_syntax(self):
        wf=CI.read_text()
        self.assertIn("test_pihole_kvin_restore.py",wf)
        self.assertIn("ansible/pihole-kvin-restore.yml --syntax-check",wf)

if __name__=="__main__":
    unittest.main()
