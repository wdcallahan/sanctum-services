"""Source contract: Kvin's HTTP80 trial must never be production by alias."""
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
STAGE_VARS = ROOT / "ansible/vars/yxorp-kvin-stage.yml"
STAGE_PLAY = ROOT / "ansible/yxorp-kvin-stage.yml"
STAGE_REMOVE = ROOT / "ansible/yxorp-kvin-stage-remove.yml"
ROLE = ROOT / "ansible/roles/yxorp/tasks/main.yml"


def read_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class KvinStageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vars = read_yaml(STAGE_VARS)
        cls.production = read_yaml(ROOT / "ansible/group_vars/yxorp.yml")
        cls.stage = read_yaml(STAGE_PLAY)[0]
        cls.remove = read_yaml(STAGE_REMOVE)[0]
        cls.role = read_yaml(ROLE)

    def test_stage_is_a_distinct_full_port_image_pinned_instance(self):
        var = self.vars
        self.assertEqual(var["yxorp_deployment_scope"], "kvin_stage")
        self.assertFalse(var["yxorp_kvin_stage_approved"])
        self.assertFalse(var["yxorp_kvin_stage_remove_approved"])
        self.assertFalse(var["yxorp_production_cutover_approved"])
        self.assertEqual(var["yxorp_bind_address"], "0.0.0.0")
        self.assertEqual(var["yxorp_host_port"], 80)
        self.assertEqual(var["yxorp_image"], self.production["yxorp_image"])
        self.assertEqual(var["yxorp_config_dir"], "/etc/sanctum-services/yxorp-kvin-stage")
        self.assertEqual(
            var["yxorp_quadlet_file"],
            "{{ yxorp_quadlet_dir }}/sanctum-yxorp-kvin-stage.container")
        self.assertEqual(var["yxorp_service_name"], "sanctum-yxorp-kvin-stage.service")
        self.assertEqual(var["yxorp_container_name"], "sanctum-yxorp-kvin-stage")
        role_defaults = read_yaml(ROOT / "ansible/roles/yxorp/defaults/main.yml")
        self.assertNotEqual(var["yxorp_config_dir"], role_defaults["yxorp_config_dir"])
        self.assertNotEqual(var["yxorp_service_name"], role_defaults["yxorp_service_name"])
        self.assertNotEqual(var["yxorp_container_name"], role_defaults["yxorp_container_name"])

    def test_stage_targets_only_kvin_and_runs_preflight_before_role(self):
        self.assertEqual(self.stage["hosts"], "yxorp")
        self.assertTrue(self.stage["gather_facts"])
        self.assertTrue(self.stage["become"])
        self.assertEqual(
            self.stage["vars_files"],
            ["../data/yxorp-routes.yml", "vars/yxorp-kvin-stage.yml"])
        self.assertEqual(self.stage["roles"], ["yxorp"])
        tasks = self.stage["pre_tasks"]
        checks = tasks[0]["ansible.builtin.assert"]["that"]
        for required in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_deployment_scope == 'kvin_stage'",
            "yxorp_kvin_stage_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "not ansible_check_mode",
            "yxorp_host_port | int == 80",
        ):
            self.assertIn(required, checks)
        self.assertLess(
            [t["name"] for t in tasks].index("Require exact Kvin stage authorization before any host changes"),
            [t["name"] for t in tasks].index("Observe any existing TCP port 80 listener"))

    def test_preflight_rejects_unowned_port_and_production_state(self):
        source = STAGE_PLAY.read_text(encoding="utf-8")
        self.assertIn("sanctum-yxorp.service", source)
        self.assertIn("sanctum-yxorp.container", source)
        self.assertIn("Refuse staging over an existing production YXORP service", source)
        self.assertIn("Refuse adopting a modified or unrelated existing Quadlet", source)
        self.assertIn("Refuse taking port 80 away from another service", source)
        self.assertIn("Refuse deleting", STAGE_REMOVE.read_text(encoding="utf-8"))
        self.assertIn("recurse: true", source)
        self.assertIn("hidden: true", source)
        self.assertIn("follow: false", source)
        # Local staging must not depend on any host firewall publication.
        # Maintenance still owns the separate LAN admission.
        self.assertNotIn("firewall-cmd", source)
        self.assertNotIn("public-zone HTTP", source)
        allowed = {"ansible.builtin.assert", "ansible.builtin.command",
                   "ansible.builtin.stat", "ansible.builtin.slurp",
                   "ansible.builtin.find"}
        for task in self.stage["pre_tasks"]:
            modules = {key for key in task if key.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= allowed, task["name"])
            if "ansible.builtin.command" in task:
                self.assertIs(task["changed_when"], False)
                argv = str(task["ansible.builtin.command"]["argv"])
                for forbidden in ("--add", "--remove", "--reload", "pull", "stop",
                                  "restart", "save", "commit"):
                    self.assertNotIn(forbidden, argv, task["name"])
        self.assertNotIn("firewall-cmd --add", source)
        self.assertNotIn("firewall-cmd --remove", source)

    def test_shared_role_has_independent_stage_gate_and_exact_scoped_paths(self):
        role = self.role[0]["ansible.builtin.assert"]["that"]
        scope = role[3]
        for part in (
            "yxorp_deployment_scope == 'peanut_trial'",
            "yxorp_deployment_scope == 'kvin_stage'",
            "yxorp_kvin_stage_approved | default(false) | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "'/etc/sanctum-services/yxorp-kvin-stage'",
            "'/etc/containers/systemd/sanctum-yxorp-kvin-stage.container'",
            "yxorp_deployment_scope == 'kvin_production'",
            "yxorp_production_cutover_approved | bool",
        ):
            self.assertIn(part, scope)
        self.assertLess(
            [t["name"] for t in self.role].index(
                "Require a specifically selected rootful HTTP 80 deployment target"),
            [t["name"] for t in self.role].index(
                "Create YXORP system configuration directory"))
        self.assertNotIn("firewall-cmd", ROLE.read_text(encoding="utf-8"))

    def test_stage_local_probe_stays_on_kvin_without_firewall_dependency(self):
        path = ROOT / "ansible/yxorp-kvin-stage-probe.yml"
        plays = read_yaml(path)
        self.assertEqual(len(plays), 1)
        kvin = plays[0]
        self.assertEqual(kvin["hosts"], "yxorp")
        self.assertEqual(kvin["vars_files"], ["vars/yxorp-kvin-stage.yml"])
        self.assertFalse(kvin["become"])
        for task in kvin["tasks"]:
            modules = {key for key in task if key.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= {
                "ansible.builtin.assert", "ansible.builtin.uri",
                "ansible.builtin.debug"}, task["name"])
            if "ansible.builtin.uri" in task:
                uri = task["ansible.builtin.uri"]
                self.assertFalse(uri["use_proxy"])
                self.assertEqual(uri["follow_redirects"], "none")
                self.assertTrue(uri["return_content"])
                self.assertEqual(uri["status_code"], [200])
                self.assertLessEqual(uri["timeout"], 10)
                self.assertTrue(task["no_log"])
                self.assertIs(task["changed_when"], False)
        source = path.read_text(encoding="utf-8")
        self.assertIn("http://yarn.inner.sanctum/", source)
        self.assertIn("url: http://127.0.0.1:80/", source)
        self.assertIn("Host: yarn.nexus.sanctum", source)
        self.assertIn("same_body", source)
        self.assertIn("same_content_type", source)
        self.assertNotIn("yxorp_test", source)
        self.assertNotIn("firewall-cmd", source)

    def test_separate_peer_probe_requires_owner_supplied_runtime_admission(self):
        path = ROOT / "ansible/yxorp-kvin-stage-peer-probe.yml"
        plays = read_yaml(path)
        self.assertEqual(len(plays), 2)
        kvin, peanut = plays
        self.assertEqual(kvin["hosts"], "yxorp")
        self.assertEqual(kvin["vars_files"], ["vars/yxorp-kvin-stage.yml"])
        self.assertTrue(kvin["become"])
        self.assertEqual(peanut["hosts"], "yxorp_test")
        self.assertFalse(peanut["become"])
        self.assertIn("Require owner-supplied runtime LAN admission",
                      [t["name"] for t in kvin["tasks"]])
        for task in kvin["tasks"]:
            modules = {key for key in task if key.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= {"ansible.builtin.assert",
                                       "ansible.builtin.command"})
            if "ansible.builtin.command" in task:
                self.assertIs(task["changed_when"], False)
                cmd = str(task["ansible.builtin.command"]["argv"])
                for forbidden in ("--add", "--remove", "--reload",
                                  "restart", "stop", "start"):
                    self.assertNotIn(forbidden, cmd)
        for task in peanut["tasks"]:
            modules = {key for key in task if key.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= {"ansible.builtin.assert", "ansible.builtin.uri",
                                       "ansible.builtin.debug"})
            if "ansible.builtin.uri" in task:
                uri = task["ansible.builtin.uri"]
                self.assertFalse(uri["use_proxy"])
                self.assertEqual(uri["follow_redirects"], "none")
                self.assertTrue(uri["return_content"])
                self.assertEqual(uri["status_code"], [200])
                self.assertLessEqual(uri["timeout"], 10)
                self.assertTrue(task["no_log"])
                self.assertIs(task["changed_when"], False)
        source = path.read_text(encoding="utf-8")
        self.assertIn("firewall-cmd, --zone=public, --query-port=80/tcp", source)
        self.assertIn("firewall-cmd, --zone=public, --query-service=http", source)
        self.assertIn("http://kvin.outer.sanctum/", source)
        self.assertIn("Host: yarn.nexus.sanctum", source)
        self.assertIn("inventory_hostname == 'peanut.arcane.sanctum'", source)
        self.assertNotIn("firewall-cmd, --zone=public, --add-port", source)

    def test_stage_removal_is_scoped_idempotent_and_never_unpublishes_dns(self):
        play = self.remove
        self.assertEqual(play["hosts"], "yxorp")
        self.assertTrue(play["become"])
        self.assertEqual(
            play["vars_files"],
            ["roles/yxorp/defaults/main.yml", "vars/yxorp-kvin-stage.yml"])
        checks = play["tasks"][0]["ansible.builtin.assert"]["that"]
        for required in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_remove_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "not ansible_check_mode",
            "yxorp_config_dir == '/etc/sanctum-services/yxorp-kvin-stage'",
            "yxorp_service_name == 'sanctum-yxorp-kvin-stage.service'",
        ):
            self.assertIn(required, checks)
        names = [task["name"] for task in play["tasks"]]
        for required in (
            "Confirm stage Quadlet owns only its declared container and mount",
            "Refuse deleting anything except the two owned Nginx configs",
            "Refuse stopping an active unit lacking an inspected Quadlet",
            "Verify stage-only unit is no longer active",
        ):
            self.assertIn(required, names)
            self.assertLess(names.index(required),
                            names.index("Report explicitly limited stage reversal"))
        self.assertLess(
            names.index("Refuse deleting anything except the two owned Nginx configs"),
            names.index("Stop only the verified stage service when active"))
        for task in play["tasks"]:
            if "ansible.builtin.file" in task:
                self.assertIn(task["ansible.builtin.file"]["path"],
                              ["{{ yxorp_quadlet_file }}", "{{ yxorp_config_dir }}"])
            if "ansible.builtin.systemd_service" in task:
                svc = task["ansible.builtin.systemd_service"]
                if "name" in svc:
                    self.assertEqual(svc["name"], "{{ yxorp_service_name }}")
        text = STAGE_REMOVE.read_text(encoding="utf-8")
        self.assertNotIn("firewall-cmd", text)
        self.assertNotIn("dnscmd", text)
        self.assertNotIn("image rm", text)
        self.assertNotIn("kvar.outer.sanctum:", text)
        self.assertIn("hidden: true", text)
        self.assertIn("follow: false", text)


if __name__ == "__main__":
    unittest.main()
