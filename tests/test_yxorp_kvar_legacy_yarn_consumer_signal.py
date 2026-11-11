"""Read-only privacy and log-coverage tests for old Kvar NPM Yarn usage signal."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-yxorp-kvar-yarn-usage.js"
PLAY = ROOT / "ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml"


class YarnUsageSignalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text(encoding="utf-8"))[0]
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_read_only_kvar_scoped_probe(self):
        p = self.play
        self.assertEqual(p["hosts"], "npm_proxy_legacy")
        self.assertTrue(p["become"])
        self.assertTrue(p["gather_facts"])
        self.assertEqual(p["vars_files"], ["../data/yxorp-routes.yml"])
        tasks = p["tasks"]
        checks = tasks[0]["ansible.builtin.assert"]["that"]
        for guard in (
            "inventory_hostname == 'kvar.outer.sanctum'",
            "ansible_facts['fqdn'] == inventory_hostname",
            "not (yxorp_production_cutover_approved | default(false) | bool)",
            "not (yxorp_routes[7].enabled | bool)",
            "yxorp_routes[7].upstream_host == '192.168.1.110'",
        ):
            self.assertIn(guard, checks)
        command = tasks[1]["ansible.builtin.command"]["argv"]
        self.assertEqual(command[:5], [
            "podman", "exec", "nginx-proxman", "node", "-e"])
        self.assertIn("observe-yxorp-kvar-yarn-usage.js", command[5])
        self.assertTrue(tasks[1]["no_log"])
        self.assertFalse(tasks[1]["changed_when"])
        self.assertFalse(tasks[1]["failed_when"])
        self.assertIn("from_json", str(tasks[-1]))
        for task in tasks:
            modules = [x for x in task if x.startswith("ansible.builtin.")]
            self.assertEqual(len(modules), 1)
            self.assertTrue(set(modules) <= {
                "ansible.builtin.assert", "ansible.builtin.command",
                "ansible.builtin.debug"})
        self.assertNotIn("raw_access_log", self.script)
        self.assertNotIn("process.env", self.script)
        self.assertIn('const ROOT = "/data";', self.script)
        self.assertIn('MAX_BYTES_EACH = 1024 * 1024', self.script)

    def synthetic_run(self, root):
        # Only replace the fixed container root in the local synthetic
        # source copy. The Git-tracked production script remains immutable.
        injected = self.script.replace(
            'const ROOT = "/data";',
            "const ROOT = " + json.dumps(str(root)) + ";")
        self.assertNotEqual(injected, self.script)
        result = subprocess.run(
            ["node", "-e", injected], capture_output=True,
            text=True, check=True, timeout=12)
        return json.loads(result.stdout), result.stdout

    def test_bounded_current_and_rotated_log_counts_never_emit_sensitive_entries(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-npm-log-signal-") as temp:
            root = Path(temp)
            logdir = root / "logs"
            configdir = root / "nginx/proxy_host"
            logdir.mkdir()
            configdir.mkdir(parents=True)
            (configdir / "11.conf").write_text(
                "server_name yarn.inner.sanctum;\n"
                "access_log /data/logs/proxy-host-11_access.log proxy;\n",
                encoding="utf-8")
            now = datetime.now(timezone.utc)
            fmt = lambda n: (now - timedelta(days=n)).strftime(
                "[%d/%b/%Y:%H:%M:%S +0000]")
            private = '203.0.113.44 GET /private?token=DO_NOT_EXPOSE'
            (logdir / "proxy-host-11_access.log").write_text(
                fmt(2) + " " + private + "\n"
                + fmt(12) + " " + private + "\n",
                encoding="utf-8")
            (logdir / "proxy-host-11_access.log.1").write_text(
                fmt(50) + " " + private + "\n",
                encoding="utf-8")
            (logdir / "proxy-host-11_access.log.2.gz").write_bytes(b"not inspected")
            result, output = self.synthetic_run(root)
            self.assertTrue(result["generated_proxy_host_file_present"])
            self.assertTrue(result["exact_access_log_directive"])
            self.assertEqual(result["examined_plain_log_count"], 2)
            self.assertEqual(result["log_coverage"], "all_selected_files_readable")
            self.assertTrue(result["additional_or_compressed_rotations_seen"])
            self.assertFalse(result["selected_log_tail_truncated"])
            self.assertEqual(result["lines_examined_in_bounded_tails"], 3)
            self.assertEqual(result["timestamp_parseable_lines"], 3)
            self.assertEqual(result["recorded_requests_last_7_days_in_sample"], 1)
            self.assertEqual(result["recorded_requests_last_30_days_in_sample"], 2)
            self.assertFalse(result["current_client_use_proven"])
            self.assertFalse(result["safe_to_retire_proven"])
            self.assertFalse(result["raw_logs_urls_ips_cookies_exposed"])
            self.assertFalse(result["configuration_changed"])
            for sensitive in ("DO_NOT_EXPOSE", "203.0.113.44",
                              "/private", "token=", "GET"):
                self.assertNotIn(sensitive, output)

    def test_no_logs_is_unknown_not_permission_to_retire(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-no-logs-") as temp:
            result, _ = self.synthetic_run(Path(temp))
            self.assertEqual(
                result["log_coverage"], "no_current_or_plain_rotation")
            self.assertEqual(result["recorded_requests_last_30_days_in_sample"], 0)
            self.assertFalse(result["safe_to_retire_proven"])
            self.assertFalse(result["current_client_use_proven"])
            self.assertEqual(result["exact_access_log_directive"], "not_observed")


if __name__ == "__main__":
    unittest.main()
