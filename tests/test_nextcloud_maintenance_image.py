"""Source policy: stage and examine Nextcloud 34 without updating the live instance."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible" / "nextcloud-qualify-maintenance-image.yml"
WORKFLOW = ROOT / ".github" / "workflows" / "yxorp-source-check.yml"


class NextcloudImageStage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text())[0]
        cls.tasks = cls.play["tasks"]
        cls.names = [t["name"] for t in cls.tasks]
        cls.by_name = {t["name"]: t for t in cls.tasks}
        cls.raw = PLAY.read_text()

    def test_explicit_host_owner_and_approval(self):
        self.assertEqual(self.play["hosts"], "nextcloud")
        self.assertIs(self.play["become"], False)
        self.assertEqual(
            self.play["vars"]["nextcloud_maintenance_candidate"],
            "docker.io/library/nextcloud:34.0-apache",
        )
        guards = self.tasks[0]["ansible.builtin.assert"]["that"]
        for expected in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "ansible_facts['user_id'] == 'wdc2'",
            "ansible_facts['architecture'] == 'aarch64'",
            "not ansible_check_mode",
            "nextcloud_candidate_stage_approved | default(false) | bool",
        ):
            self.assertIn(expected, guards)

    def test_guard_before_pull_and_no_live_update_commands(self):
        idx = lambda fragment: next(
            i for i, name in enumerate(self.names) if fragment in name
        )
        self.assertLess(idx("Require live image identity"), idx("Pull only official"))
        self.assertLess(idx("Refuse candidate work"), idx("Pull only official"))
        self.assertLess(idx("Pull only official"), idx("Inspect cached"))
        self.assertLess(idx("Inspect cached"), idx("Read shipped candidate"))
        assert_names = [task for task in self.tasks if "ansible.builtin.assert" in task]
        for task in assert_names:
            self.assertFalse(
                set(task["ansible.builtin.assert"]) - {"that", "fail_msg", "success_msg", "quiet"},
                task["name"],
            )
        for forbidden in (
            "ansible.builtin.systemd_service:",
            "ansible.builtin.copy:",
            "ansible.builtin.template:",
            "ansible.builtin.file:",
            "maintenance:mode",
            "pg_dump",
            "podman-auto-update",
            "occ upgrade",
        ):
            self.assertNotIn(forbidden, self.raw)

    def test_cache_only_candidate_not_private_data(self):
        pull = next(t for t in self.tasks if t["name"].startswith("Pull only"))
        self.assertEqual(
            pull["ansible.builtin.command"]["argv"],
            ["podman", "pull", "{{ nextcloud_maintenance_candidate }}"],
        )
        self.assertTrue(pull["no_log"])
        command = self.by_name[
            "Read shipped candidate application version in a disposable networkless runtime"
        ]["ansible.builtin.command"]["argv"]
        for expected in ("--rm", "--pull=never", "--network=none", "--read-only",
                         "--security-opt=no-new-privileges", "--entrypoint", "php"):
            self.assertIn(expected, command)
        self.assertIn("/usr/src/nextcloud/version.php", command[-1])
        self.assertNotIn("--volume", command)
        self.assertNotIn("--publish", command)

    def test_version_family_and_source_validation(self):
        guards = str(self.by_name[
            "Require candidate remains on the same maintenance release family"
        ]["ansible.builtin.assert"]["that"])
        self.assertIn(".major | int == 34", guards)
        self.assertIn(".minor | int == 0", guards)
        self.assertIn(".patch | int >=", guards)
        report = self.by_name[
            "Report actual independent Nextcloud 34 maintenance image qualification"
        ]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["cached_image_staged_only"], True)
        self.assertIs(report["live_upgrade_not_authorized"], True)
        self.assertIs(report["original_nextcloud_not_restarted"], True)

    def test_workflow_runs_source_and_syntax(self):
        ci = WORKFLOW.read_text()
        self.assertIn("tests/test_nextcloud_maintenance_image.py", ci)
        self.assertIn(
            "ansible/nextcloud-qualify-maintenance-image.yml --syntax-check", ci
        )


if __name__ == "__main__":
    unittest.main()
