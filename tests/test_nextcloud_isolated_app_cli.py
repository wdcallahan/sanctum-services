"""Recovered Nextcloud CLI uses only the Maintenance-created no-network database."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
ANS=ROOT/"ansible"
PLAY=ANS/"nextcloud-isolated-app-cli-trial-on-peanut.yml"
WF=ROOT/".github/workflows/yxorp-source-check.yml"


class IsolatedNextcloudAppCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=PLAY.read_text()
        cls.play=yaml.safe_load(cls.raw)[0]
        cls.tasks=cls.play["tasks"]
        cls.names=[v["name"] for v in cls.tasks]

    def find(self,fragment):
        return next(v for v in self.tasks if fragment in v["name"])

    def test_exact_peanut_rootless_no_prod_approval(self):
        self.assertEqual(self.play["hosts"],"yxorp_test")
        self.assertIs(self.play["become"],False)
        self.assertEqual(self.play["vars_files"],["group_vars/nextcloud.yml"])
        s=str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for x in ("peanut.arcane.sanctum","user_id","nextcloud_isolated_app_trial_approved",
                  "not ansible_check_mode","nextcloud_app_trial_image",
                  "nextcloud:34"):
            self.assertIn(x,self.raw)
        self.assertNotIn("become: true",self.raw)
        self.assertNotIn("kvin.outer.sanctum",self.raw)

    def test_refuses_running_without_networkless_owner_database(self):
        s=self.raw
        for x in ("nextcloud_app_trial_receipt",
                  "isolated_database_ready_for_application",
                  "container_id is match('^[a-f0-9]{64}$')",
                  "HostConfig.NetworkMode == 'none'",
                  "io.sanctum.nextcloud-restore",
                  "password_file == nextcloud_app_trial_password_file",
                  "production_database_contacted"):
            self.assertIn(x,s)
        self.assertNotIn("'--network=host'",s)
        self.assertNotIn("slirp4netns",s)
        self.assertNotIn("PublishPort",s)
        self.assertNotIn("podman exec sanctum-nextcloud",s)

    def test_supported_runtime_channel_without_code_sync_or_implicit_pull(self):
        p=self.play
        self.assertEqual(p["vars"]["nextcloud_app_trial_image"],"{{ nextcloud_image }}")
        self.assertIn("--pull=never",p["vars"]["nextcloud_app_trial_container_prefix"])
        self.assertIn("--read-only",p["vars"]["nextcloud_app_trial_container_prefix"])
        self.assertIn("--cap-drop=all",p["vars"]["nextcloud_app_trial_container_prefix"])
        self.assertIn("--user=www-data",p["vars"]["nextcloud_app_trial_container_prefix"])
        self.assertIn("--entrypoint=php",p["vars"]["nextcloud_app_trial_container_prefix"])
        self.assertNotIn("nextcloud@sha256:",self.raw)
        self.assertIn('argv: [podman, pull, "{{ nextcloud_app_trial_image }}"]',self.raw)
        self.assertIn("nextcloud_app_trial_runtime_id, 'occ'",self.raw)
        self.assertIn("34[.]0[.]5",self.raw)
        self.assertNotIn("occ', 'upgrade'",self.raw)

    def test_writes_only_steered_private_trial_copy(self):
        name="Create PRIVATE restored-app-only DB configuration overlay under rootless user namespace"
        task=self.find(name)
        argv=task["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[:4],["podman","unshare","python3","-c"])
        self.assertIn("nextcloud-isolated-config.py",argv[4])
        self.assertTrue(task["no_log"])
        order=self.names
        self.assertLess(order.index("Refuse connecting to a nonisolated PostgreSQL or dead test database"),
                        order.index(name))
        self.assertLess(order.index("Require compatible 34.0 runtime before preparing restored app"),
                        order.index(name))
        self.assertLess(order.index(name),
                        order.index("Run only restored Nextcloud occ status inside networkless DB namespace"))
        for x in ("--network=container:",":/var/www/html:Z","occ', 'status'",
                  "occ', 'app:list'","Calendar","full_app_restore_not_yet_accepted: true"):
            self.assertIn(x,self.raw)

    def test_failed_occ_reports_bounded_diagnostics_without_raw_console_output(self):
        task = self.find("Run only restored Nextcloud occ status")
        self.assertTrue(task["no_log"])
        self.assertFalse(task["failed_when"])
        saved = self.find("Save raw OCC failure")
        self.assertTrue(saved["no_log"])
        self.assertEqual(saved["ansible.builtin.copy"]["mode"], "0600")
        self.assertFalse(saved["diff"])
        report = self.find("Report bounded OCC failure")
        msg = report["ansible.builtin.debug"]["msg"]
        self.assertIn("regex_findall", msg["known_error_categories"])
        self.assertNotIn("stdout", msg)
        self.assertNotIn("stderr", msg)
        self.assertIn("overlay_created", self.raw)

    def test_report_does_not_overclaim_auth_or_files(self):
        report=self.find("Report actual networkless Nextcloud recovered application CLI and Calendar trial")[
            "ansible.builtin.debug"]["msg"]
        for k in ("restored_nextcloud_occ_status_passed",
                  "restored_calendar_app_enabled",
                  "completely_isolated_network_namespace",
                  "no_network_path_to_production_kvin_postgresql",
                  "no_http_listener_or_browser_session_started",
                  "authenticated_login_not_yet_tested",
                  "restored_user_files_in_app_not_yet_tested",
                  "full_app_restore_not_yet_accepted",
                  "live_nextcloud_or_shared_postgresql_not_changed"):
            self.assertIs(report[k],True)

    def test_ci_contract(self):
        w=WF.read_text()
        self.assertIn("tests/test_nextcloud_isolated_app_cli.py",w)
        self.assertIn("tests/test_nextcloud_isolated_config.py",w)
        self.assertIn("ansible/nextcloud-isolated-app-cli-trial-on-peanut.yml --syntax-check",w)


if __name__=="__main__":
    unittest.main()
