"""Exercise the real private Vault password-entry shell UX without secrets."""
from pathlib import Path
import os
import stat
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/kuma-set-vault-password.sh"


class KumaVaultPasswordEntryTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="kuma-vault-ux-")
        self.addCleanup(self.tempdir.cleanup)
        self.home = Path(self.tempdir.name)
        self.secrets = self.home / ".config/sanctum-services/secrets"
        self.secrets.mkdir(parents=True)
        (self.secrets / "vault.key").write_text("dummy-only-for-ci\n", encoding="utf-8")
        self.target = self.secrets / "kuma-admin.vault.yml"
        navigator = self.home / ".local/bin/ansible-navigator"
        navigator.parent.mkdir(parents=True)
        navigator.write_text(textwrap.dedent("""\
            #!/usr/bin/env python3
            import os
            import sys
            data = sys.stdin.read()
            if os.environ.get("FAKE_VAULT_FAIL"):
                sys.exit(7)
            if not data:
                sys.exit(8)
            print("vault_kuma_admin_password: !vault |")
            print("  $ANSIBLE_VAULT;1.1;AES256")
            print("  ci-only-encrypted-placeholder")
        """), encoding="utf-8")
        navigator.chmod(0o700)

    def invoke(self, stdin, **extra_env):
        return subprocess.run(
            ["bash", str(SCRIPT)],
            input=stdin, capture_output=True, text=True,
            env={**os.environ, "HOME": str(self.home), **extra_env},
            timeout=15,
        )

    def test_first_create_with_short_chosen_password_and_confirm(self):
        result = self.invoke("shortPass7!\nshortPass7!\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Passwords matched.", result.stdout)
        self.assertTrue(self.target.exists())
        self.assertIn("vault_kuma_admin_password: !vault |", self.target.read_text())
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
        self.assertNotIn("shortPass7!", result.stdout + result.stderr)
        self.assertNotIn("shortPass7!", self.target.read_text())

    def test_mismatch_preserves_existing_encrypted_file(self):
        self.target.write_text("old-encrypted-value", encoding="utf-8")
        result = self.invoke("first\nsecond\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_text(), "old-encrypted-value")

    def test_correction_replaces_existing_encrypted_file(self):
        self.target.write_text("old-encrypted-value", encoding="utf-8")
        result = self.invoke("chosen7\nchosen7\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("old-encrypted-value", self.target.read_text())

    def test_failed_encryption_preserves_existing_encrypted_file(self):
        self.target.write_text("old-encrypted-value", encoding="utf-8")
        result = self.invoke("chosen7\nchosen7\n", FAKE_VAULT_FAIL="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_text(), "old-encrypted-value")
        self.assertEqual(list(self.secrets.glob(".kuma-vault.*")), [])

    def test_empty_password_refused(self):
        result = self.invoke("\n\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.target.exists())

    def test_secret_file_not_leaked_into_source(self):
        source = SCRIPT.read_text()
        self.assertIn("Confirm Kuma password:", source)
        self.assertNotIn("length >= 16", source)
        self.assertNotIn("16+ characters", source)
        self.assertNotIn("kuma-admin.json", source)
        self.assertIn("mv -f", source)


if __name__ == "__main__":
    unittest.main()
