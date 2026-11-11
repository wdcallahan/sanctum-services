"""Safe, fixed source classification for old Yarn NPM log consumer signals."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-yxorp-kvar-yarn-source-classes.js"
PLAY = ROOT / "ansible/yxorp-kvar-legacy-yarn-source-classes.yml"


class LegacyYarnSourceClasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(PLAY.read_text(encoding="utf-8"))[0]

    def test_strict_read_only_scope(self):
        play = self.play
        self.assertEqual(play["hosts"], "npm_proxy_legacy")
        self.assertTrue(play["gather_facts"])
        self.assertTrue(play["become"])
        self.assertEqual(play["vars_files"], ["../data/yxorp-routes.yml"])
        tasks = play["tasks"]
        checks = tasks[0]["ansible.builtin.assert"]["that"]
        for required in (
            "inventory_hostname == 'kvar.outer.sanctum'",
            "ansible_facts['fqdn'] == inventory_hostname",
            "not (yxorp_production_cutover_approved | default(false) | bool)",
            "not (yxorp_routes[7].enabled | bool)",
            "yxorp_routes[7].hostname == 'yarn.inner.sanctum'",
            "yxorp_routes[7].upstream_host == '192.168.1.110'",
        ):
            self.assertIn(required, checks)
        cmd = tasks[1]["ansible.builtin.command"]["argv"]
        self.assertEqual(cmd[:5], [
            "podman", "exec", "nginx-proxman", "node", "-e"
        ])
        self.assertIn("observe-yxorp-kvar-yarn-source-classes.js", cmd[5])
        self.assertEqual(len(cmd), 6)
        self.assertTrue(tasks[1]["no_log"])
        self.assertFalse(tasks[1]["changed_when"])
        self.assertFalse(tasks[1]["failed_when"])
        self.assertIn("from_json", str(tasks[-1]))
        for task in tasks:
            mods = [k for k in task if k.startswith("ansible.builtin.")]
            self.assertEqual(len(mods), 1)
            self.assertIn(mods[0], (
                "ansible.builtin.assert", "ansible.builtin.command",
                "ansible.builtin.debug"))
        self.assertIn('const ROOT = "/data";', self.script)
        self.assertIn('const MAX_BYTES = 1024 * 1024;', self.script)
        self.assertIn('const NAMES = ["proxy-host-11_access.log", "proxy-host-11_access.log.1"];', self.script)
        self.assertNotIn("process.env", self.script)

    def run_synthetic(self, root):
        script = self.script.replace('const ROOT = "/data";',
                                     "const ROOT = " + json.dumps(str(root)) + ";")
        self.assertNotEqual(script, self.script)
        proc = subprocess.run(["node", "-e", script], text=True,
                              capture_output=True, check=True, timeout=12)
        return json.loads(proc.stdout), proc.stdout

    def test_fixed_source_classes_never_print_addresses_or_paths(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-yarn-source-") as tmp:
            root = Path(tmp)
            logs = root / "logs"
            logs.mkdir()
            now = datetime.now(timezone.utc)
            def when(days):
                return (now - timedelta(days=days)).strftime(
                    "[%d/%b/%Y:%H:%M:%S +0000]")
            lines = [
                f'{when(1)} [Client 192.168.0.192] GET /secret?k=SHOULD_NOT_PRINT',
                f'{when(2)} [Client 192.168.0.192] GET /admin?token=SHOULD_NOT_PRINT',
                f'{when(1)} [Client 192.168.0.7] GET /',
                f'{when(1)} [Client 127.0.0.1] GET /',
                f'{when(3)} [Client 198.51.100.35] GET /private',
                f'{when(4)} UNKNOWN-CLIENT-FORMAT GET /secret',
                f'{when(45)} [Client 198.51.100.35] GET /old',
            ]
            (logs / "proxy-host-11_access.log").write_text(
                "\n".join(lines[:6]) + "\n", encoding="utf-8")
            (logs / "proxy-host-11_access.log.1").write_text(
                lines[6] + "\n", encoding="utf-8")
            data, printed = self.run_synthetic(root)
            self.assertEqual(data["sample_files_read"], 2)
            self.assertFalse(data["samples_truncated"])
            self.assertEqual(data["lines_examined"], 7)
            self.assertEqual(data["entries_last_30_days"], 6)
            kinds = data["observed_source_classes_last_30_days"]
            self.assertEqual(kinds["known_kvin_observer"], 2)
            self.assertEqual(kinds["known_kvar_host"], 1)
            self.assertEqual(kinds["known_kvar_loopback"], 1)
            self.assertEqual(kinds["other_observed_source"], 1)
            self.assertEqual(kinds["unclassified_format"], 1)
            self.assertFalse(data["all_classified_sources_known_tests"])
            self.assertFalse(data["real_client_dependency_proven"])
            self.assertFalse(data["safe_to_retire_proven"])
            self.assertFalse(data["raw_ips_urls_log_lines_exposed"])
            self.assertFalse(data["configuration_changed"])
            for sensitive in ("192.168.0.192", "198.51.100.35",
                              "192.168.0.7", "127.0.0.1",
                              "SHOULD_NOT_PRINT", "/private", "/secret"):
                self.assertNotIn(sensitive, printed)

    def test_unclassified_source_is_not_relabelled_as_known_test(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-yarn-unknown-") as tmp:
            root = Path(tmp)
            logs = root / "logs"
            logs.mkdir()
            when = datetime.now(timezone.utc).strftime(
                "[%d/%b/%Y:%H:%M:%S +0000]")
            (logs / "proxy-host-11_access.log").write_text(
                when + " [Sent-to 192.168.0.192] GET /somepath\n"
                + when + " [Client 192.168.0.192] GET /\n",
                encoding="utf-8")
            data, _ = self.run_synthetic(root)
            kinds = data["observed_source_classes_last_30_days"]
            self.assertEqual(kinds["unclassified_format"], 1)
            self.assertEqual(kinds["known_kvin_observer"], 1)
            self.assertFalse(data["all_classified_sources_known_tests"])
            self.assertFalse(data["safe_to_retire_proven"])

    def test_missing_log_keeps_retirement_unapproved(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-yarn-empty-") as tmp:
            data, _ = self.run_synthetic(Path(tmp))
            self.assertEqual(data["sample_files_read"], 0)
            self.assertEqual(data["entries_last_30_days"], 0)
            self.assertFalse(data["all_classified_sources_known_tests"])
            self.assertFalse(data["safe_to_retire_proven"])


if __name__ == "__main__":
    unittest.main()
