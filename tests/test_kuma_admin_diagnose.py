"""No-secret, no-write source contract for native Kuma bootstrap diagnosis."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class KumaAdminDiagnosticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "ansible/kuma-admin-diagnose.yml").read_text()
        cls.play = yaml.safe_load(cls.source)[0]
        cls.tasks = cls.play["tasks"]
        cls.script = (ROOT / "tools/kuma-admin-init.js").read_text()

    def test_guard_only_kvin_and_private_vault(self):
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        self.assertEqual(self.play["vars_files"], [
            "/home/wdc2/.config/sanctum-services/secrets/kuma-admin.vault.yml",
        ])
        guard = self.tasks[0]["ansible.builtin.assert"]["that"]
        for expr in ("inventory_hostname == 'kvin.outer.sanctum'",
                     "kuma_admin_diagnose_approved | default(false) | bool",
                     "kuma_image == kuma_admin_expected_image"):
            self.assertIn(expr, guard)

    def test_uses_exact_version_password_checker_without_mutations(self):
        self.assertIn('passwordStrength(credentials.password).value !== "Too weak"', self.script)
        self.assertIn('if (mode === "diagnose")', self.script)
        diag = next(t for t in self.tasks if t["name"].startswith("Privately classify"))
        self.assertTrue(diag["no_log"])
        self.assertFalse(diag["changed_when"])
        self.assertIn("vault_kuma_admin_password", diag["ansible.builtin.command"]["stdin"])
        self.assertEqual(diag["ansible.builtin.command"]["argv"][-1], "diagnose")
        self.assertNotIn("setup", diag["ansible.builtin.command"]["argv"])
        self.assertNotIn("login", diag["ansible.builtin.command"]["argv"])
        for task in self.tasks:
            for forbidden_module in ("ansible.builtin.copy",
                                     "ansible.builtin.file",
                                     "ansible.builtin.script"):
                self.assertNotIn(forbidden_module, task)
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for field in ("administrator_created_or_changed", "authentication_attempted",
                      "database_or_monitor_changed", "vault_secret_changed"):
            self.assertIs(report[field], False)


if __name__ == "__main__":
    unittest.main()
