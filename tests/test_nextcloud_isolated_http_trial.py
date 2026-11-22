"""The isolated HTTP rehearsal neither exposes a host port nor leaks credentials."""
from pathlib import Path
import subprocess
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/nextcloud-isolated-http-trial-on-peanut.yml"
PHP = ROOT / "tools/nextcloud-isolated-http.php"

class HttpTrial(unittest.TestCase):
    def test_source_contract(self):
        raw = PLAY.read_text()
        p = yaml.safe_load(raw)[0]
        self.assertEqual(p["hosts"], "yxorp_test")
        self.assertFalse(p["become"])
        self.assertTrue(p["vars_prompt"][1]["private"])
        self.assertIn("--network=container:", raw)
        self.assertIn("HostConfig.NetworkMode == 'none'", raw)
        self.assertIn("--entrypoint=apache2-foreground", raw)
        self.assertIn("--pull=never", raw)
        self.assertNotIn("--publish", raw)
        self.assertNotIn("--network=host", raw)
        b = next(t for t in p["tasks"] if "block" in t)
        probe = next(t for t in b["block"] if "Authenticate and read" in t["name"])
        self.assertTrue(probe["no_log"])
        self.assertIn("password", probe["ansible.builtin.command"]["stdin"])
        self.assertNotIn("nextcloud_trial_password", str(probe["ansible.builtin.command"]["argv"]))
        self.assertIn("http_container.stdout", str(b["always"]))
        self.assertIn("restored_file_read_passed", raw)
        self.assertIn("calendar_query_passed", raw)

    def test_php_syntax_and_paths(self):
        subprocess.run(["php","-l",str(PHP)],check=True,capture_output=True,text=True)
        code = 'define("NEXTCLOUD_HTTP_TEST", true); require $argv[1]; $p="/remote.php/dav/files/test/"; if (davpath($p."test.txt",$p)!==$p."test.txt" || davpath($p."%2e%2e/no",$p)!==null || davpath("/wrong",$p)!==null) exit(1);'
        subprocess.run(["php","-r",code,str(PHP)],check=True)

if __name__ == "__main__":
    unittest.main()
