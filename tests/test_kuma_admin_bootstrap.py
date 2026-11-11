"""Kuma admin bootstrap must use existing Vault state, not generate passwords."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "ansible/kuma-admin-bootstrap.yml"
JS = ROOT / "tools/kuma-admin-init.js"
NAV = ROOT / "ansible-navigator.yml"
CONFIG = ROOT / "ansible.cfg"


class KumaAdminBootstrapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PB.read_text(encoding="utf-8"))[0]
        cls.tasks = cls.play["tasks"]
        cls.source = JS.read_text(encoding="utf-8")

    def test_scope_approval_and_private_vault_source(self):
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        self.assertEqual(self.play["vars_files"], [
            "/home/wdc2/.config/sanctum-services/secrets/kuma-admin.vault.yml"
        ])
        checks = self.tasks[0]["ansible.builtin.assert"]["that"]
        for clause in ("inventory_hostname == 'kvin.outer.sanctum'",
                       "ansible_facts['user_id'] == 'wdc2'",
                       "ansible_facts['architecture'] == 'aarch64'",
                       "kuma_admin_bootstrap_approved | default(false) | bool",
                       "kuma_db_type == 'sqlite'"):
            self.assertIn(clause, checks)
        self.assertIn("vault_password_file = /home/wdc2/.config/sanctum-services/secrets/vault.key",
                      CONFIG.read_text(encoding="utf-8"))
        self.assertIn("podman", str(self.tasks))
        self.assertNotIn("UPDATE user", self.source)
        self.assertNotIn("INSERT INTO user", self.source)
        for forbidden in ("firewall-cmd", "yxorp_routes", "kuma-generate-admin-secret",
                          "kuma-admin.json"):
            self.assertNotIn(forbidden, PB.read_text(encoding="utf-8"))
        self.assertNotIn("vault_kuma_admin_password", NAV.read_text(encoding="utf-8"))

    def test_only_read_vault_and_send_password_privately_via_stdin(self):
        check = next(task for task in self.tasks
                     if task["name"].startswith("Require a nonempty, suitably long Vault"))
        self.assertTrue(check["no_log"])
        init = next(task for task in self.tasks
                    if task["name"].startswith("Initialize missing administrator"))
        self.assertTrue(init["no_log"])
        cmd = init["ansible.builtin.command"]
        self.assertIn("vault_kuma_admin_password", cmd["stdin"])
        self.assertIn("to_json", cmd["stdin"])
        self.assertNotIn("vault_kuma_admin_password", str(cmd["argv"]))
        self.assertIn("--interactive", cmd["argv"])
        self.assertFalse(init["changed_when"] is False)
        assert not any("ansible.builtin.copy" in t or "ansible.builtin.script" in t
                       for t in self.tasks)
        msg = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for key in ("administrator_login_verified", "encrypted_credentials_loaded",
                    "private_credentials_not_logged"):
            self.assertIs(msg[key], True)
        for key in ("credentials_generated_or_changed", "credentials_written_to_host",
                    "production_or_proxy_changed", "password_rotation_accepted"):
            self.assertIs(msg[key], False)

    def test_uses_actual_kuma_259_protocol_and_fails_closed(self):
        for marker in ('eventAck("needSetup")',
                       'eventAck("setup", credentials.username, credentials.password)',
                       'eventAck("login", {', "auth.ok !== true",
                       "socket.disconnect()"):
            self.assertIn(marker, self.source)
        assert "require(\"node:fs\").readFileSync(0" in self.source
        assert "if (needsSetup)" in self.source

    def test_no_local_generator_is_part_of_supported_design(self):
        self.assertFalse((ROOT / "tools/kuma-generate-admin-secret.py").exists())
        self.assertNotIn("generate_admin_secret",
                         (ROOT / ".github/workflows/yxorp-source-check.yml").read_text())


if __name__ == "__main__":
    unittest.main()
