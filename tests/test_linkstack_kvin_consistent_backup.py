"""Current Kvin LinkStack backup captures the LIVE SQLite before rolling updates."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/linkstack-kvin-consistent-backup.yml"
CI=ROOT/".github/workflows/yxorp-source-check.yml"


class CurrentKvinLinkStackBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.by_name={t["name"]:t for t in cls.tasks}

    def test_exact_host_service_and_live_volume(self):
        self.assertEqual(self.play["hosts"],"kuma")
        self.assertIs(self.play["become"],False)
        v=self.play["vars"]
        self.assertEqual(v["linkstack_live_service"],"sanctum-linkstack-kvin-candidate.service")
        self.assertEqual(v["linkstack_live_container"],"sanctum-linkstack-kvin-candidate")
        self.assertEqual(v["linkstack_live_volume"],"sanctum-linkstack-qualified-20261112t105926")
        self.assertIn("linkstackorg/linkstack@sha256:",v["linkstack_live_image"])
        conditions=self.tasks[0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'",conditions)
        self.assertIn("sanctum_linkstack_kvin_backup_approved | default(false) | bool",conditions)

    def test_quiesce_and_always_restore_only_source_service(self):
        action=self.by_name["Quiesce only live LinkStack for a consistent SQLite volume export"]
        self.assertIn("block",action)
        self.assertIn("always",action)
        stop=action["block"][0]["ansible.builtin.systemd_service"]
        self.assertEqual(stop["name"],"{{ linkstack_live_service }}")
        self.assertEqual(stop["state"],"stopped")
        self.assertEqual(stop["scope"],"user")
        export=next(t for t in action["block"] if "volume export" in t["name"])
        self.assertIn("{{ linkstack_live_volume }}",export["ansible.builtin.command"]["argv"])
        self.assertIn("{{ linkstack_backup_partial }}",export["ansible.builtin.command"]["argv"])
        restart=action["always"][0]["ansible.builtin.systemd_service"]
        self.assertEqual(restart["name"],"{{ linkstack_live_service }}")
        self.assertEqual(restart["state"],"started")
        self.assertEqual(restart["scope"],"user")

    def test_only_native_app_data_is_exported_without_changes_to_other_services(self):
        s=PLAY.read_text()
        for forbidden in ("systemctl restart", "firewall-cmd",
                          "kvar.outer.sanctum", "pihole", "podman volume rm",
                          "podman volume import", "ansible.builtin.template:",
                          "scope: system", "ansible.builtin.iptables"):
            self.assertNotIn(forbidden,s)
        validation=self.by_name[
            "Require verified complete LinkStack archive and SQLite integrity"
        ]["ansible.builtin.assert"]["that"]
        self.assertIn("(linkstack_validated.stdout | from_json).archive_verified | bool",validation)
        self.assertIn("(linkstack_validated.stdout | from_json).sqlite_integrity == 'ok'",validation)
        self.assertIn("(linkstack_validated.stdout | from_json).archive_sha256 == linkstack_backup_stat.stat.checksum",validation)

    def test_asserts_have_only_supported_module_arguments(self):
        permitted={"that","fail_msg","success_msg","quiet"}
        for t in self.tasks:
            if "ansible.builtin.assert" in t:
                self.assertFalse(set(t["ansible.builtin.assert"])-permitted,t["name"])
            for k in ("block","always"):
                for subt in t.get(k,[]):
                    if "ansible.builtin.assert" in subt:
                        self.assertFalse(set(subt["ansible.builtin.assert"])-permitted,subt["name"])

    def test_ci_checks_new_backup(self):
        c=CI.read_text()
        self.assertIn("ansible/linkstack-kvin-consistent-backup.yml --syntax-check",c)
        self.assertIn("test_linkstack_kvin_consistent_backup.py",c)


if __name__=="__main__":
    unittest.main()
