"""Production YXORP readiness is an observation, not an implicit cutover."""
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ansible/yxorp-kvin-readiness.yml"


class KvinReadinessContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(cls.text)[0]

    def test_exact_target_and_closed_gate(self):
        self.assertEqual(self.play["hosts"], "yxorp")
        self.assertTrue(self.play["become"])
        checks = self.play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", checks)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", checks)
        self.assertIn("yxorp_host_port | int == 80", checks)

    def test_standalone_play_loads_required_role_defaults(self):
        # Syntax checking cannot catch an undefined variable at task runtime.
        # This play intentionally doesn't execute the role whose defaults
        # contain the real production systemd unit and Quadlet paths.
        self.assertEqual(
            self.play["vars_files"], ["roles/yxorp/defaults/main.yml"])
        role_defaults = yaml.safe_load(
            (ROOT / "ansible/roles/yxorp/defaults/main.yml").read_text())
        group_vars = yaml.safe_load(
            (ROOT / "ansible/group_vars/yxorp.yml").read_text())
        self.assertFalse(set(role_defaults) & set(group_vars),
                         "vars_files has higher precedence; duplicate keys are unsafe")
        variables = dict(role_defaults)
        variables.update(group_vars)
        referenced = set(re.findall(r"\\b(yxorp_[a-z0-9_]+)\\b", self.text))
        missing = referenced - set(variables)
        self.assertFalse(missing, f"Undefined YXORP variables: {sorted(missing)}")
        self.assertEqual(
            variables["yxorp_service_name"], "sanctum-yxorp.service")
        self.assertIn("sanctum-yxorp.container", variables["yxorp_quadlet_file"])

    def test_every_task_is_read_only(self):
        allowed = {"ansible.builtin.assert", "ansible.builtin.command",
                   "ansible.builtin.stat", "ansible.builtin.debug"}
        for task in self.play["tasks"]:
            modules = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(modules), 1, task["name"])
            self.assertTrue(modules <= allowed, task["name"])
            if "ansible.builtin.command" in task:
                self.assertIs(task["changed_when"], False)
                argv = task["ansible.builtin.command"]["argv"]
                for mutating in ("--add-port", "--add-service", "--reload",
                                 "--remove-port", "restart", "start", "pull", "stop"):
                    self.assertNotIn(mutating, str(argv))

    def test_inspects_exact_rootful_image_and_both_firewall_stores(self):
        self.assertIn("podman, image, exists", self.text)
        self.assertIn("ss, -H, -ltnp", self.text)
        self.assertIn("--query-service=http", self.text)
        self.assertIn("--query-port=80/tcp", self.text)
        self.assertIn("--permanent", self.text)
        self.assertIn("qualified_rootful_image_cached", self.text)
        self.assertIn("existing_tcp80_listeners", self.text)
        self.assertNotIn("yxorp_production_cutover_approved: true", self.text)


if __name__ == "__main__":
    unittest.main()
