"""Native Kuma 2.5.9 Wicket monitor contract: guarded, idempotent, and no alerts."""
from pathlib import Path
import unittest
import yaml

BASE=Path(__file__).resolve().parents[1]
P=BASE/"ansible/kuma-monitors.yml"
J=BASE/"tools/kuma-reconcile-monitors.js"
CI=BASE/".github/workflows/yxorp-source-check.yml"

class TestKumaMonitorSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(P.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.js=J.read_text()

    def test_guard_and_single_desired_target(self):
        self.assertEqual(self.play["hosts"],"kuma")
        self.assertFalse(self.play["become"])
        self.assertEqual(self.play["vars_files"],[
            "/home/wdc2/.config/sanctum-services/secrets/kuma-admin.vault.yml"])
        checks=self.tasks[0]["ansible.builtin.assert"]["that"]
        self.assertIn("kuma_monitors_approved | default(false) | bool",checks)
        self.assertIn("ansible_facts['user_id'] == 'wdc2'",checks)
        wanted=self.tasks[1]["ansible.builtin.assert"]["that"]
        self.assertIn("kuma_monitors_desired | length == 1",wanted)
        self.assertIn("kuma_monitors_desired[0].key == 'wicket_ollama'",wanted)

    def test_bounded_authenticated_socket_reconciliation(self):
        write=next(t for t in self.tasks if t["name"].startswith("Reconcile wanted monitor"))
        self.assertTrue(write["no_log"])
        self.assertIn("vault_kuma_admin_password",write["ansible.builtin.command"]["stdin"])
        self.assertNotIn("vault_kuma_admin_password",str(write["ansible.builtin.command"]["argv"]))
        self.assertIn("changed",write["changed_when"])
        for ev in ['ack("login"','ack("getMonitorList"','ack("getMonitor"','ack("add"','ack("editMonitor"']:
            self.assertIn(ev,self.js)
        self.assertIn("duplicate_monitor_refused",self.js)
        self.assertIn("existing_notification_refused",self.js)
        self.assertIn("actual_up_accepted:false",self.js)
        self.assertIn("notifications_attached:false",self.js)
        for forbidden in ("sqlite3", "firewall-cmd", "kvar.outer.sanctum"):
            self.assertNotIn(forbidden,P.read_text())

    def test_read_only_actual_heartbeat_on_existing_monitor_repeat(self):
        observe=next(t for t in self.tasks if t["name"].startswith("Read the retained Kuma heartbeat"))
        self.assertTrue(observe["no_log"])
        self.assertIs(observe["changed_when"],False)
        self.assertEqual(observe["ansible.builtin.command"]["argv"][-1],"observe")
        self.assertIn('ack("getMonitorBeats",1,1)',self.js)
        self.assertIn('const saved=await getMonitor(1)',self.js)
        self.assertIn('recent&&code===1',self.js)
        report=self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIn("kuma_monitor_heartbeat.stdout",report["actual_up_accepted"])
        self.assertIn("kuma_monitor_heartbeat.stdout",report["latest_status_in_kuma"])

    def test_full_source_ci_runs_monitor_contract(self):
        s=CI.read_text()
        self.assertIn("test_kuma_monitors.py",s)
        self.assertIn("verify-kuma-monitor-reconcile.js",s)
        self.assertIn("ansible/kuma-monitors.yml --syntax-check",s)

if __name__=="__main__": unittest.main()
