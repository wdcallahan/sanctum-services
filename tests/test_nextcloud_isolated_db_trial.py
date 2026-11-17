"""Bounded cross-owner Nextcloud DB restore contract; no shared databases.

The actual PostgreSQL restore implementation belongs exclusively to
Sanctum Maintenance and is executed only on Peanut after new approval.
"""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
ANS=ROOT/"ansible"
PLAY=ANS/"nextcloud-isolated-db-trial-on-peanut.yml"
WF=ROOT/".github/workflows/yxorp-source-check.yml"


class PeanutIsolatedDatabaseTrial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=PLAY.read_text()
        cls.play=yaml.safe_load(cls.raw)[0]
        cls.tasks=cls.play["tasks"]
        cls.names=[x["name"] for x in cls.tasks]
        cls.tasks_by_name={x["name"]:x for x in cls.tasks}

    def get(self,piece):
        return next(v for v in self.tasks if piece in v["name"])

    def test_owner_and_separate_mutating_restore_approvals(self):
        self.assertEqual(self.play["hosts"],"yxorp_test")
        self.assertIs(self.play["become"],False)
        checks=self.get("Require exact rootless Peanut")["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'peanut.arcane.sanctum'",checks)
        self.assertIn("ansible_facts['user_id'] == 'wdc2'",checks)
        self.assertIn("nextcloud_isolated_db_trial_approved | default(false) | bool",checks)
        self.assertIn("nextcloud_maintenance_restore_contract_approved | default(false) | bool",checks)
        self.assertIn("not ansible_check_mode",checks)
        self.assertIn("^nextcloud-[0-9]{8}t[0-9]{6}$",str(checks))
        self.assertNotIn("become: true",self.raw)

    def test_uses_owner_helper_not_own_pg_commands(self):
        self.assertEqual(
            self.play["vars"]["nextcloud_db_trial_owner_helper"],
            "/home/wdc2/src/sanctum-maintenance/tools/restore-nextcloud-postgresql",
        )
        self.assertEqual(
            self.play["vars"]["nextcloud_db_trial_pg_image"],
            "docker.io/library/postgres:18",
        )
        invoke=self.get("Invoke ONLY the Maintenance-owned")
        argv=invoke["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[0],"python3")
        self.assertIn("nextcloud_db_trial_owner_helper",argv[1])
        self.assertIn("nextcloud_db_trial_bundle",argv[2])
        self.assertIn("nextcloud_db_trial_password_file",argv[-1])
        self.assertGreaterEqual(invoke["async"],1800)
        self.assertTrue(invoke["no_log"])
        for forbidden in ("pg_restore", "CREATE DATABASE",
                          "systemctl", "state: restarted", "become: true"):
            self.assertNotIn(forbidden,self.raw)
        self.assertNotIn("postgres@sha256:",self.raw)
        self.assertIn("Refuse restore unless Maintenance's actual helper uses the moving PostgreSQL major channel",self.names)
        self.assertIn("nextcloud_db_trial_owner_image_contract.stdout",self.raw)
        self.assertIn("runpy.run_path(sys.argv[1])",self.raw)
        self.assertLess(
            self.names.index("Refuse restore unless Maintenance's actual helper uses the moving PostgreSQL major channel"),
            self.names.index("Cache only supported PostgreSQL 18 major channel when separately approved and absent"),
        )
        self.assertIn("nextcloud_isolated_db_image_cache_approved | default(false) | bool",self.raw)
        self.assertIn("podman, pull, \"{{ nextcloud_db_trial_pg_image }}\"",self.raw)
        self.assertIn("podman, image, inspect",self.raw)
        self.assertIn("postgres [(]PostgreSQL[)] 18",self.raw)
        self.assertIn("--network=none",self.raw)
        self.assertIn("--pull=never",self.raw)

    def test_prior_file_stage_and_fresh_private_handoff_checked_before_write(self):
        before=self.names.index("Require previously accepted isolated files and a fresh owner-private handoff")
        verify=self.names.index("Require verified application files and PostgreSQL custom dump")
        image=self.names.index("Refuse unknown or incompatible PostgreSQL image before touching private handoff")
        created=self.names.index("Create only a fresh private handoff directory under previously staged files")
        invoked=self.names.index("Invoke ONLY the Maintenance-owned isolated Nextcloud PostgreSQL restore helper")
        self.assertLess(before,verify)
        self.assertLess(verify,image)
        self.assertLess(image,created)
        self.assertLess(created,invoked)
        self.assertIn("nextcloud-recovery-bundle.py",self.raw)
        self.assertIn("archive_and_dump_hashes_match_manifest",self.raw)
        self.assertIn("nextcloud_db_trial_existing.results[4].stat.isdir",self.raw)
        self.assertIn("not (nextcloud_db_trial_existing.results[7].stat.exists",self.raw)
        self.assertIn("mode: '0700'",self.raw)

    def test_owner_receipt_and_container_network_none_proof(self):
        self.assertIn("isolated_database_ready_for_application",self.raw)
        self.assertIn("container:",self.raw)
        self.assertIn("HostConfig.NetworkMode == 'none'",self.raw)
        self.assertIn("io.sanctum.nextcloud-restore",self.raw)
        self.assertIn("restored_application_tables",self.raw)
        self.assertIn("production_database_contacted",self.raw)
        self.assertIn("stat.mode",self.raw)
        self.assertIn("'0600'",self.raw)
        report=self.get("Report actual independent Nextcloud-only PostgreSQL trial ready")[
            "ansible.builtin.debug"]["msg"]
        for key in ("isolated_postgresql_ready","owner_handoff_private",
                    "shared_production_database_unmodified",
                    "production_kvin_not_contacted","restored_nextcloud_application_not_started",
                    "full_app_restore_not_yet_accepted"):
            self.assertIn(key,report)
        self.assertIs(report["full_app_restore_not_yet_accepted"],True)

    def test_ci_runs_contract_and_syntax(self):
        w=WF.read_text()
        self.assertIn("tests/test_nextcloud_isolated_db_trial.py",w)
        self.assertIn("ansible/nextcloud-isolated-db-trial-on-peanut.yml --syntax-check",w)


if __name__=="__main__":
    unittest.main()
