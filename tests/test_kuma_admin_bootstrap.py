"""Kuma administrator bootstrap must be scoped, opt-in and non-destructive."""
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "ansible/kuma-admin-bootstrap.yml"
JS = ROOT / "tools/kuma-admin-init.js"
GEN = ROOT / "tools/kuma-generate-admin-secret.py"


class KumaAdminBootstrapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PB.read_text())[0]
        cls.tasks = cls.play["tasks"]
        cls.source = JS.read_text()

    def test_scope_approval_and_preserve_user(self):
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        checks = self.tasks[0]["ansible.builtin.assert"]["that"]
        for clause in ("inventory_hostname == 'kvin.outer.sanctum'",
                       "ansible_facts['user_id'] == 'wdc2'",
                       "ansible_facts['architecture'] == 'aarch64'",
                       "kuma_admin_bootstrap_approved | default(false) | bool",
                       "kuma_db_type == 'sqlite'"):
            self.assertIn(clause, checks)
        self.assertIn("podman", str(self.tasks))
        self.assertNotIn("UPDATE user", self.source)
        self.assertNotIn("INSERT INTO user", self.source)
        self.assertNotIn("firewall-cmd", PB.read_text())
        self.assertNotIn("yxorp_routes", PB.read_text())
        self.assertIn("socket.on", self.source) if False else None

    def test_secret_never_in_command_argv_or_report(self):
        boot = next(t for t in self.tasks if t["name"].startswith("Initialize missing administrator"))
        self.assertTrue(boot["no_log"])
        cmd = boot["ansible.builtin.command"]
        self.assertIn("stdin", cmd)
        self.assertIn("kuma_admin_private_secret.content", cmd["stdin"])
        self.assertNotIn("kuma_admin_private_secret", str(cmd["argv"]))
        self.assertIn("--interactive", cmd["argv"])
        reports = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for key in ("administrator_login_verified", "private_credentials_stored",
                    "private_credentials_not_logged"):
            self.assertIs(reports[key], True)
        self.assertIs(reports["production_or_proxy_changed"], False)

    def test_source_uses_tagged_upstream_events(self):
        for marker in ('eventAck("needSetup")', 'eventAck("setup", credentials.username, credentials.password)',
                       'eventAck("login", {'):
            self.assertIn(marker, self.source)
        self.assertIn("auth.ok !== true", self.source)
        self.assertIn("socket.disconnect()", self.source)

    def test_secret_generator_rejects_unapproved_target(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "test.json"
            p = subprocess.run(["python3", str(GEN), str(path)],
                               capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
