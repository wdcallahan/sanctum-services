"""Contract tests for ordered, fail-closed Nextcloud patch updates.

Source-only tests do not claim a native DB or app restore, and do not permit
a timer or a 34-to-35 production upgrade.
"""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ANS = ROOT / "ansible"
WF = ROOT / ".github/workflows/yxorp-source-check.yml"


class NextcloudMaintenanceCycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = yaml.safe_load((ANS / "nextcloud-maintenance-cycle.yml").read_text())
        cls.preflight = yaml.safe_load((ANS / "nextcloud-maintenance-preflight.yml").read_text())[0]
        cls.activate = yaml.safe_load((ANS / "nextcloud-maintenance-activate.yml").read_text())[0]
        cls.backup = yaml.safe_load((ANS / "nextcloud-consistent-backup.yml").read_text())[0]
        cls.peanut = yaml.safe_load((ANS / "nextcloud-retain-on-peanut.yml").read_text())[0]
        cls.preflight_names = [t["name"] for t in cls.preflight["tasks"]]
        cls.activation_names = [t["name"] for t in cls.activate["tasks"]]

    def test_order_and_skip_for_no_op(self):
        self.assertEqual([s["import_playbook"] for s in self.orchestrator], [
            "nextcloud-maintenance-preflight.yml",
            "nextcloud-consistent-backup.yml",
            "nextcloud-retain-on-peanut.yml",
            "nextcloud-maintenance-activate.yml",
        ])
        self.assertNotIn("when", self.orchestrator[0])
        for step in self.orchestrator[1:]:
            self.assertIn("nextcloud_cycle_update_needed", step["when"])
            self.assertIn("hostvars['kvin.outer.sanctum']", step["when"])
        self.assertIn("nextcloud_cycle_recovery_id",
                      self.orchestrator[2]["vars"]["nextcloud_recovery_id"])
        self.assertIn("nextcloud_maintenance_cycle_approved",
                      self.orchestrator[1]["vars"]["nextcloud_consistent_backup_approved"])

    def test_preflight_guards_branch_version_and_existing_service(self):
        self.assertEqual(self.preflight["hosts"], "nextcloud")
        self.assertIs(self.preflight["become"], False)
        self.assertEqual(self.preflight["vars"]["nextcloud_cycle_candidate"],
                         "docker.io/library/nextcloud:34.0-apache")
        raw = (ANS / "nextcloud-maintenance-preflight.yml").read_text()
        for requirement in (
            "nextcloud_maintenance_cycle_approved",
            "ansible_facts['architecture'] == 'aarch64'",
            "ansible_facts['user_id'] == 'wdc2'",
            "State.Running",
            "AutoUpdate=registry",
            "nextcloud_cycle_candidate_php",
            ".major | int == 34",
            ".minor | int == 0",
            ".patch | int >=",
            "nextcloud_cycle_update_needed",
            "nextcloud_cycle_backup_stamp",
        ):
            self.assertIn(requirement, raw)
        for flag in ("--rm", "--pull=never", "--network=none", "--read-only"):
            self.assertIn(flag, raw)
        self.assertIn(".update-halted", raw)
        self.assertIn("Refuse an unattended retry", raw)
        self.assertNotIn("maintenance:mode", raw)
        self.assertNotIn("systemd_service:", raw)
        self.assertNotIn("pg_dump", raw)

    def test_activation_cross_play_inputs_are_persisted_host_facts(self):
        # A preflight play's vars disappear at the next play boundary.
        # Every activation input coming from preflight must be a set_fact
        # key, rather than an incidental play-local variable.
        import re
        facts = set()
        for task in self.preflight["tasks"]:
            facts.update(task.get("ansible.builtin.set_fact", {}))
        activation_local = set(self.activate["vars"])
        guard = self.activate["tasks"][0]["ansible.builtin.assert"]["that"]
        referenced = set(re.findall(r"\bnextcloud_cycle_[a-z_]+\b", "\n".join(guard)))
        external_receipts = {"nextcloud_cycle_backup_verified", "nextcloud_cycle_peanut_verified"}
        self.assertEqual(referenced - activation_local - external_receipts - facts, set())
        self.assertIn("nextcloud_cycle_candidate_channel", facts)
        self.assertNotIn("nextcloud_cycle_candidate == ", "\n".join(guard))
        for task in self.preflight["tasks"]:
            if "nextcloud_cycle_candidate_channel" in task.get("ansible.builtin.set_fact", {}):
                self.assertEqual(task["ansible.builtin.set_fact"]["nextcloud_cycle_candidate_channel"],
                                 "{{ nextcloud_cycle_candidate }}")
                break
        else:
            self.fail("Candidate channel was not persisted")

    def test_new_backup_receipt_used_not_historical_recovery_id(self):
        snap = (ANS / "nextcloud-consistent-backup.yml").read_text()
        retain = (ANS / "nextcloud-retain-on-peanut.yml").read_text()
        self.assertIn("nextcloud_cycle_backup_stamp | default(", snap)
        self.assertIn("nextcloud_cycle_backup_verified: true", snap)
        self.assertIn("nextcloud_cycle_recovery_id", snap)
        self.assertIn("nextcloud_cycle_peanut_verified: true", retain)
        self.assertIn("hostvars['kvin.outer.sanctum'].nextcloud_cycle_recovery_id", retain)
        self.assertIn("archive_and_dump_hashes_match_manifest", retain)

    def test_activation_no_restore_proof_no_live_update(self):
        raw = (ANS / "nextcloud-maintenance-activate.yml").read_text()
        self.assertEqual(self.activate["hosts"], "nextcloud")
        self.assertIs(self.activate["become"], False)
        self.assertIs(type(yaml.safe_load((ANS / "group_vars/nextcloud.yml").read_text())["nextcloud_complete_restore_qualified_in_source"]), bool)
        self.assertIn("nextcloud_complete_restore_qualified_in_source", (ANS / "nextcloud-maintenance-preflight.yml").read_text())
        guards = self.activate["tasks"][0]["ansible.builtin.assert"]["that"]
        s = "\n".join(guards)
        for x in (
            "nextcloud_maintenance_activation_approved",
            "nextcloud_complete_restore_qualified_in_source",
            "nextcloud_cycle_backup_verified",
            "nextcloud_cycle_peanut_verified",
            "nextcloud_cycle_update_needed",
        ):
            self.assertIn(x, s)
        self.assertIn("state: restarted", raw)
        self.assertIn("Calendar 6.6.2", raw)
        self.assertIn("without unsafe image downgrade", raw)
        self.assertIn("Persist failed application-upgrade latch", raw)
        self.assertIn(".update-halted", raw)
        self.assertNotIn("pg_restore", raw)
        self.assertNotIn("pg_dump", raw)
        self.assertNotIn("podman-auto-update", raw)
        self.assertNotIn("ansible.builtin.shell:", raw)

    def test_managed_quadlet_holds_existing_storage_and_no_independent_timer(self):
        text = (ANS / "files/sanctum-nextcloud-kvin-maintenance.container").read_text()
        self.assertIn("Image=docker.io/library/nextcloud:34.0-apache", text)
        self.assertIn("Pull=never", text)
        self.assertIn("Network=slirp4netns", text)
        self.assertIn("PublishPort=0.0.0.0:8085:80/tcp", text)
        self.assertIn("Volume=/home/wdc2/srv/sanctum-services/nextcloud/html:/var/www/html", text)
        self.assertEqual(len([s for s in text.splitlines() if s.startswith("Volume=")]), 4)
        self.assertNotIn("\nAutoUpdate=registry", text)
        self.assertIn("Restart=always", text)

    def test_no_invalid_assert_options(self):
        for play in (self.preflight, self.activate, self.backup, self.peanut):
            def walk(tasks):
                for task in tasks:
                    if "ansible.builtin.assert" in task:
                        self.assertFalse(
                            set(task["ansible.builtin.assert"]) -
                            {"that", "fail_msg", "success_msg", "quiet"},
                            task["name"],
                        )
                    for nested in ("block", "rescue", "always"):
                        if nested in task:
                            walk(task[nested])
            walk(play["tasks"])

    def test_ci_checks_full_cycle_and_two_new_plays(self):
        text = WF.read_text()
        self.assertIn("tests/test_nextcloud_maintenance_cycle.py", text)
        for p in (
            "nextcloud-maintenance-preflight.yml",
            "nextcloud-maintenance-activate.yml",
            "nextcloud-maintenance-cycle.yml",
        ):
            self.assertIn("ansible/" + p + " --syntax-check", text)


if __name__ == "__main__":
    unittest.main()
