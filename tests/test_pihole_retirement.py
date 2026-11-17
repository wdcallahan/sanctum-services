"""Intentional permanent retirement: tests never execute the live deletion script."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/retire-pihole-kvin.sh"
CI = ROOT / ".github/workflows/yxorp-source-check.yml"

class PiHoleRetiredPolicy(unittest.TestCase):
    def test_retirement_script_syntax(self):
        r = subprocess.run(["bash", "-n", str(SCRIPT)], check=False)
        self.assertEqual(r.returncode, 0)

    def test_scoped_kvin_only_rootful_removal(self):
        c = SCRIPT.read_text()
        for term in (
            'kvin.outer.sanctum', 'SUDO_USER:-', '"wdc2"',
            'sanctum-pihole-kvin.service',
            '/etc/containers/systemd/sanctum-pihole-kvin.container',
            'sanctum-pihole-etc-20261112t161524',
            'sanctum-pihole-dnsmasq-20261112t161524',
            'systemctl stop "$unit"',
            'systemctl daemon-reload',
            'podman container rm --force "$container"',
            'podman volume rm "$volume"',
        ):
            self.assertIn(term, c)
        self.assertNotIn("podman volume prune", c)
        self.assertNotIn("systemctl reboot", c)
        self.assertNotIn("firewall-cmd", c)
        self.assertNotIn("podman system prune", c)
        self.assertNotIn("podman volume rm -f", c)

    def test_no_restoration_source_or_ci_reinsertion(self):
        for retired in (
            "ansible/pihole-consistent-backup.yml",
            "ansible/pihole-kvin-deploy.yml",
            "ansible/pihole-kvin-restore.yml",
            "ansible/files/sanctum-pihole-kvin.container",
            "tools/stream-pihole-snapshot.py",
            "tools/pihole-archive-verify.py",
        ):
            self.assertFalse((ROOT / retired).exists(), retired)
        ci = CI.read_text()
        self.assertIn("test_pihole_retirement.py", ci)
        self.assertIn("retire-pihole-kvin.sh", ci)
        self.assertNotIn("ansible/pihole-kvin-deploy.yml --syntax-check", ci)
        self.assertNotIn("test_pihole_kvin_deploy.py'", ci)

if __name__ == "__main__":
    unittest.main()
