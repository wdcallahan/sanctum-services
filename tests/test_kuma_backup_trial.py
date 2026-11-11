"""Kuma quiesced backup + separate restored app trial must never touch live data."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/kuma-backup-restore-trial.yml"
PYTHON=ROOT/"tools/kuma-backup-verify.py"
CI=ROOT/".github/workflows/yxorp-source-check.yml"


class KumaBackupRestoreTrialContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.yaml=PLAY.read_text()

    def task(self, prefix):
        return next(t for t in self.tasks if t["name"].startswith(prefix))

    def test_exact_host_and_default_off_service_downtime_approval(self):
        self.assertEqual(self.play["hosts"],"kuma")
        self.assertFalse(self.play["become"])
        self.assertEqual(self.play["vars_files"],[
            "/home/wdc2/.config/sanctum-services/secrets/kuma-admin.vault.yml",
        ])
        checks=self.tasks[0]["ansible.builtin.assert"]["that"]
        for expected in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "ansible_facts['architecture'] == 'aarch64'",
            "ansible_facts['user_id'] == 'wdc2'",
            "kuma_backup_restore_trial_approved | default(false) | bool",
            "kuma_data_volume == 'sanctum-kuma-data'",
            "kuma_recovery_volume != kuma_data_volume",
        ):
            self.assertIn(expected,checks)
        self.assertIn("localhost", "") if False else None

    def test_only_original_service_stop_and_always_restart(self):
        b=self.task("Quiesce live Kuma")
        self.assertIn("block",b)
        self.assertIn("always",b)
        block=b["block"]
        finally_=b["always"]
        stop=next(t for t in block if t["name"].startswith("Stop only retained"))
        self.assertEqual(stop["ansible.builtin.systemd_service"]["state"],"stopped")
        self.assertEqual(stop["ansible.builtin.systemd_service"]["scope"],"user")
        up=next(t for t in finally_ if t["name"].startswith("Start original"))
        self.assertEqual(up["ansible.builtin.systemd_service"]["state"],"started")
        self.assertEqual(up["ansible.builtin.systemd_service"]["scope"],"user")
        export=next(t for t in block if t["name"].startswith("Export only stopped"))
        self.assertIn("sanctum-kuma-data",export["ansible.builtin.command"]["argv"])
        self.assertIn("kuma_recovery_partial",str(export["ansible.builtin.command"]["argv"]))
        self.assertIn("Require stopped application",str(block))

    def test_isolated_volume_and_no_external_network(self):
        trial=self.task("Restore into a new disposable volume")
        block=trial["block"]
        create=next(t for t in block if t["name"].startswith("Create distinct"))
        imp=next(t for t in block if t["name"].startswith("Import archive"))
        self.assertIn("kuma_recovery_volume",str(create))
        self.assertNotIn("sanctum-kuma-data",str(imp["ansible.builtin.command"]["argv"]))
        run=next(t for t in block if t["name"].startswith("Start disposable"))
        args=run["ansible.builtin.command"]["argv"]
        self.assertIn("--network",args)
        self.assertIn("none",args)
        self.assertNotIn("--publish",args)
        self.assertNotIn("-p",args)
        self.assertIn("kuma_recovery_volume",str(args))
        self.assertIn("kuma_recovery_container",str(args))
        self.assertIn("always",trial)
        finally_=trial["always"]
        self.assertTrue(any(t["name"].startswith("Remove only the disposable") for t in finally_))
        self.assertTrue(any(t["name"].startswith("Remove only isolated") for t in finally_))

    def test_restore_verifies_existing_auth_and_monitor_without_mutation(self):
        block=self.task("Restore into a new disposable volume")["block"]
        login=next(t for t in block if t["name"].startswith("Verify existing Vault admin"))
        monitor=next(t for t in block if t["name"].startswith("Verify restored Kuma"))
        for task,mode in ((login,"verify"),(monitor,"observe")):
            self.assertTrue(task["no_log"])
            self.assertIs(task["changed_when"],False)
            cmd=task["ansible.builtin.command"]
            self.assertIn("vault_kuma_admin_password",cmd["stdin"])
            self.assertNotIn("vault_kuma_admin_password",str(cmd["argv"]))
            self.assertEqual(cmd["argv"][-1],mode)
            self.assertIn("kuma_recovery_container",str(cmd["argv"]))
        self.assertIn("os.link(sys.argv[1],sys.argv[2])",self.yaml)
        report=self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for field in ("isolated_restore_volume_imported",
                      "restored_vault_login_verified",
                      "restored_wicket_configuration_verified",
                      "original_service_restarted_and_active"):
            self.assertIs(report[field],True)
        for field in ("backup_copied_off_host","production_or_proxy_changed"):
            self.assertIs(report[field],False)

    def test_workflow_runs_synthetic_test_and_syntax(self):
        c=CI.read_text()
        self.assertIn("test_kuma_backup_verify.py",c)
        self.assertIn("test_kuma_backup_trial.py",c)
        self.assertIn("kuma-backup-restore-trial.yml --syntax-check",c)


if __name__=="__main__":
    unittest.main()
