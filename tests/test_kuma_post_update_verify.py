"""Only read-only app/monitor acceptance after advancing Kuma's supported v2 image."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/kuma-post-update-verify.yml"
CI=ROOT/".github/workflows/yxorp-source-check.yml"

class KumaPostUpdateVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.names=[t["name"] for t in cls.tasks]

    def task(self,name):
        return self.tasks[self.names.index(name)]

    def test_exact_owner_and_explicit_read_only_approval(self):
        self.assertEqual(self.play["hosts"],"kuma")
        self.assertIs(self.play["become"],False)
        self.assertEqual(self.play["vars_files"],[
            "/home/wdc2/.config/sanctum-services/secrets/kuma-admin.vault.yml"])
        checks=self.tasks[0]["ansible.builtin.assert"]["that"]
        for expected in ("inventory_hostname == 'kvin.outer.sanctum'",
                         "ansible_facts['user_id'] == 'wdc2'",
                         "kuma_post_update_verify_approved | default(false) | bool",
                         "kuma_image == 'docker.io/louislam/uptime-kuma:2'",
                         "kuma_data_volume == 'sanctum-kuma-data'"):
            self.assertIn(expected,checks)
        policy=self.task("Require installed v2 registry update declaration and preserved volume")["ansible.builtin.assert"]["that"]
        self.assertTrue(any("AutoUpdate=registry" in x for x in policy))
        self.assertTrue(any("Volume=sanctum-kuma-data" in x for x in policy))

    def test_login_and_monitor_are_authenticated_read_only(self):
        login=self.task("Authenticate the existing administrator WITHOUT creating a user")
        monitor=self.task("Observe existing Wicket monitor and saved heartbeat WITHOUT reconciliation")
        for t,operation in ((login,"verify"),(monitor,"observe")):
            self.assertTrue(t["no_log"])
            self.assertIs(t["changed_when"],False)
            cmd=t["ansible.builtin.command"]
            self.assertEqual(cmd["argv"][-1],operation)
            self.assertIn("vault_kuma_admin_password",cmd["stdin"])
            self.assertNotIn("vault_kuma_admin_password",str(cmd["argv"]))
        app=ROOT/"tools/kuma-reconcile-monitors.js"
        js=app.read_text()
        self.assertIn('if(mode==="observe")',js)
        self.assertIn('const saved=await getMonitor(1)',js)
        self.assertIn('ack("getMonitorBeats",1,1)',js)

    def test_no_mutation_and_truthful_scope(self):
        s=PLAY.read_text()
        for bad in ("ansible.builtin.file:", "ansible.builtin.copy:",
                    "state: restarted", "systemctl restart", "podman pull",
                    "podman run", "podman stop", "podman volume import",
                    "podman volume rm", "ansible.builtin.template:",
                    "monitor_reconcile_approved"):
            self.assertNotIn(bad,s)
        report=self.task("Report bounded post-update original administrator and monitor acceptance")["ansible.builtin.debug"]["msg"]
        self.assertTrue(report["original_admin_login_verified"])
        self.assertTrue(report["existing_wicket_monitor_config_verified"])
        self.assertFalse(report["service_or_database_modified_by_test"])
        self.assertFalse(report["monitor_reconciled_or_changed_by_test"])
        self.assertTrue(report["scheduled_auto_update_history_not_checked_by_this_play"])
        self.assertTrue(report["historically_accepted_named_client_and_backup_tests_not_repeated"])

    def test_all_active_admin_and_monitor_entrypoints_follow_v2_channel(self):
        digest="docker.io/louislam/uptime-kuma@sha256:302aceeca2db79617f195a7549f7c8dfb05375a274b1092c59d81c1fb61a9ab9"
        for file in ("ansible/kuma-monitors.yml","ansible/kuma-admin-bootstrap.yml",
                     "ansible/kuma-admin-diagnose.yml"):
            c=(ROOT/file).read_text()
            self.assertNotIn(digest,c,file)
            self.assertIn("docker.io/louislam/uptime-kuma:2",c,file)
        workflow=CI.read_text()
        self.assertIn("test_kuma_post_update_verify.py",workflow)
        self.assertIn("ansible/kuma-post-update-verify.yml --syntax-check",workflow)

if __name__=="__main__":
    unittest.main()
