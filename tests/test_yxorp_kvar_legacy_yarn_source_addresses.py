"""Exact NPM source IP address output without raw HTTP logs or secrets."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-yxorp-kvar-yarn-source-addresses.js"
PLAY = ROOT / "ansible/yxorp-kvar-legacy-yarn-source-addresses.yml"


class LoggedYarnSourceAddresses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.play = yaml.safe_load(PLAY.read_text(encoding="utf-8"))[0]

    def test_guard_and_no_raw_log_output(self):
        play = self.play
        self.assertEqual(play["hosts"], "npm_proxy_legacy")
        self.assertTrue(play["gather_facts"])
        self.assertTrue(play["become"])
        self.assertEqual(play["vars_files"], ["../data/yxorp-routes.yml"])
        tasks = play["tasks"]
        guards = tasks[0]["ansible.builtin.assert"]["that"]
        for guard in (
            "inventory_hostname == 'kvar.outer.sanctum'",
            "ansible_facts['fqdn'] == inventory_hostname",
            "not (yxorp_production_cutover_approved | default(false) | bool)",
            "not (yxorp_routes[7].enabled | bool)",
            "yxorp_routes[7].hostname == 'yarn.inner.sanctum'",
            "yxorp_routes[7].upstream_host == '192.168.1.110'",
        ):
            self.assertIn(guard, guards)
        command = tasks[1]
        self.assertTrue(command["no_log"])
        self.assertFalse(command["changed_when"])
        self.assertFalse(command["failed_when"])
        args = command["ansible.builtin.command"]["argv"]
        self.assertEqual(args[:5],
                         ["podman", "exec", "nginx-proxman", "node", "-e"])
        self.assertIn("observe-yxorp-kvar-yarn-source-addresses.js", args[5])
        self.assertEqual(len(args), 6)
        for task in tasks:
            mods = [key for key in task if key.startswith("ansible.builtin.")]
            self.assertEqual(len(mods), 1)
            self.assertIn(mods[0], (
                "ansible.builtin.assert", "ansible.builtin.command",
                "ansible.builtin.debug"))
        self.assertIn("MAX_BYTES = 1024 * 1024", self.script)
        self.assertIn("MAX_DISTINCT = 24", self.script)
        self.assertNotIn("process.env", self.script)

    def synthetic(self, root):
        rewritten = self.script.replace(
            'const ROOT = "/data";',
            "const ROOT = " + json.dumps(str(root)) + ";",
        )
        self.assertNotEqual(rewritten, self.script)
        proc = subprocess.run(["node", "-e", rewritten],
                              text=True, capture_output=True, check=True,
                              timeout=12)
        return json.loads(proc.stdout), proc.stdout

    def test_exact_sources_revealed_without_sensitive_request_fields(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-yarn-ips-") as tmp:
            root = Path(tmp)
            logs = root / "logs"
            logs.mkdir()
            when = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime(
                "[%d/%b/%Y:%H:%M:%S +0000]")
            data = [
                (["192.168.0.192"] * 3 + ["192.168.0.65"] * 2
                 + ["192.168.0.70"])
            ][0]
            (logs / "proxy-host-11_access.log").write_text(
                "".join(
                    f'{when} [Client {addr}] GET /private?k=secret-token-123\n'
                    for addr in data
                ),
                encoding="utf-8",
            )
            parsed, output = self.synthetic(root)
            self.assertEqual(parsed["requests_with_recent_timestamps"], 6)
            self.assertEqual(parsed["distinct_source_addresses_seen"], 3)
            self.assertFalse(parsed["source_address_list_truncated"])
            self.assertEqual(parsed["sampled_logs_readable"], 1)
            self.assertEqual(parsed["unclassified_recent_entries"], 0)
            sources = parsed["sources_last_30_days"]
            self.assertEqual(
                {r["source_ip"]: (r["requests"], r["classification"])
                 for r in sources},
                {
                    "192.168.0.192": (3, "known_kvin_observer"),
                    "192.168.0.65": (2, "other_observed_source"),
                    "192.168.0.70": (1, "other_observed_source"),
                },
            )
            self.assertTrue(parsed["source_ips_exposed_intentionally"])
            self.assertFalse(
                parsed["raw_http_requests_cookies_urls_and_log_lines_exposed"])
            self.assertFalse(parsed["safe_to_retire_proven"])
            self.assertFalse(parsed["configuration_changed"])
            self.assertNotIn("secret-token-123", output)
            self.assertNotIn("/private", output)
            self.assertNotIn("GET", output)

    def test_ambiguous_log_field_does_not_guess_source(self):
        with tempfile.TemporaryDirectory(prefix="yxorp-yarn-unknownip-") as tmp:
            root = Path(tmp)
            logs = root / "logs"
            logs.mkdir()
            when = datetime.now(timezone.utc).strftime(
                "[%d/%b/%Y:%H:%M:%S +0000]")
            (logs / "proxy-host-11_access.log").write_text(
                when + " [Client 192.168.0.91] [Client 192.168.0.65] GET /\n"
                + when + " [Sent-to 192.168.0.7] GET /\n",
                encoding="utf-8",
            )
            parsed, _ = self.synthetic(root)
            self.assertEqual(parsed["unclassified_recent_entries"], 2)
            self.assertEqual(parsed["sources_last_30_days"], [])
            self.assertFalse(parsed["safe_to_retire_proven"])


if __name__ == "__main__":
    unittest.main()
