"""No production config or DB credentials may be used for isolated Nextcloud."""
from contextlib import ExitStack
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import stat
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"tools/nextcloud-isolated-config.py"
WF=ROOT/".github/workflows/yxorp-source-check.yml"
spec=importlib.util.spec_from_file_location("nextcloud_trial_config",SOURCE)
trial=importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


class IsolatedConfigContract(unittest.TestCase):
    def test_password_is_exact_owner_token_and_no_production_settings(self):
        password="a"*64
        php=trial.php_overlay(password)
        self.assertIn("'dbhost' => '127.0.0.1'",php)
        self.assertIn("'dbname' => 'nextcloud_restore'",php)
        self.assertIn("'dbuser' => 'nextcloud_restore'",php)
        self.assertIn("'dbpassword' => '"+password+"'",php)
        self.assertIn("'maintenance' => false",php)
        self.assertIn("'trusted_domains' => ['127.0.0.1', 'localhost']",php)
        self.assertNotIn("db.nexus.sanctum",php)
        self.assertNotIn("square.nexus.sanctum",php)
        for invalid in ("b"*63, "hello", "c"*64+"\n", "c"*63+"'"):
            with self.assertRaises(trial.Refusal):
                trial.php_overlay(invalid)

    def test_receipt_requires_network_none_owner_link_and_no_production_contact(self):
        with TemporaryDirectory() as temp:
            base=Path(temp)
            p=base/"postgresql-trial-password"
            p.write_text("a"*64+"\n")
            p.chmod(0o600)
            receipt=base/"postgresql-trial.json"
            expected={
                "status":"isolated_database_ready_for_application",
                "container_id":"b"*64,
                "password_file":str(p),
                "database":"nextcloud_restore",
                "username":"nextcloud_restore",
                "host":"127.0.0.1",
                "port":5432,
                "network":"container:"+"b"*64,
                "restored_application_tables":14,
                "application_started":False,
                "production_database_contacted":False,
            }
            def write(x):
                receipt.write_text(json.dumps(x))
                receipt.chmod(0o600)
            write(expected)
            self.assertEqual(trial.load_receipt(receipt,p),("b"*64,14))
            for key,wrong in [
                ("network","bridge"),("host","db.nexus.sanctum"),
                ("status","isolated_database_restore_passed"),
                ("application_started",True),
                ("production_database_contacted",True),
                ("password_file","/tmp/not-approved"),
                ("restored_application_tables",0),
            ]:
                changed=dict(expected)
                changed[key]=wrong
                write(changed)
                with self.assertRaises(trial.Refusal):
                    trial.load_receipt(receipt,p)
            write(expected)
            receipt.chmod(0o644)
            with self.assertRaises(trial.Refusal):
                trial.load_receipt(receipt,p)

    def test_one_time_file_owner_mode_and_no_rewrite_of_original_config(self):
        with TemporaryDirectory() as temp:
            base=Path(temp)
            rid="nextcloud-20261116t233618"
            trial_dir=base/rid
            html=trial_dir/"html"
            config=html/"config"
            handoff=trial_dir/"postgresql-trial"
            config.mkdir(parents=True)
            handoff.mkdir()
            trial_dir.chmod(0o700)
            original=config/"config.php"
            original.write_text("<?php $CONFIG=['dbhost'=>'production'];")
            password=handoff/"postgresql-trial-password"
            password.write_text("a"*64+"\n")
            password.chmod(0o600)
            receipt=handoff/"postgresql-trial.json"
            receipt.write_text(json.dumps({
                "status":"isolated_database_ready_for_application",
                "container_id":"b"*64,
                "password_file":str(password),
                "database":"nextcloud_restore",
                "username":"nextcloud_restore",
                "host":"127.0.0.1",
                "port":5432,
                "network":"container:"+"b"*64,
                "restored_application_tables":99,
                "application_started":False,
                "production_database_contacted":False,
            }))
            receipt.chmod(0o600)
            with ExitStack() as stack:
                stack.enter_context(patch.object(trial,"ROOT",base))
                stack.enter_context(patch.object(trial.socket,"getfqdn",return_value=trial.HOST))
                stack.enter_context(patch.object(trial.os,"geteuid",return_value=0))
                fake_chown=stack.enter_context(patch.object(trial.os,"fchown"))
                result=trial.prepare(rid,html,password)
                self.assertEqual(result["status"],"isolated_nextcloud_config_ready")
                self.assertEqual(result["restored_application_tables"],99)
                self.assertTrue(result["password_written_only_into_private_isolated_override"])
                self.assertEqual(fake_chown.call_args.args[1:],(33,33))
                output=config/trial.NAME
                self.assertEqual(stat.S_IMODE(output.stat().st_mode),0o600)
                self.assertIn("'dbname' => 'nextcloud_restore'",output.read_text())
                self.assertEqual(original.read_text(),"<?php $CONFIG=['dbhost'=>'production'];")
                with self.assertRaises(trial.Refusal):
                    trial.prepare(rid,html,password)

    def test_path_and_override_drift_refused(self):
        self.assertNotIn("subprocess.run(",SOURCE.read_text())
        self.assertNotIn("os.system(",SOURCE.read_text())
        self.assertIn("O_EXCL",SOURCE.read_text())
        self.assertIn("O_NOFOLLOW",SOURCE.read_text())
        self.assertIn("os.fchown(target.fileno(), 33, 33)",SOURCE.read_text())
        self.assertIn("glob(\"*.config.php\")",SOURCE.read_text())
        self.assertIn("nextcloud-restore-trials",SOURCE.read_text())
        self.assertNotIn("srv/sanctum-services/nextcloud/html",SOURCE.read_text())

    def test_ci_runs_unit_contract(self):
        wf=WF.read_text()
        self.assertIn("tests/test_nextcloud_isolated_config.py",wf)


if __name__=="__main__":
    unittest.main()
