"""Real local HTTP tests for sanitized Kuma raw-wire header inspection.

Creates only ephemeral 127.0.0.1 synthetic servers. No Sanctum hosts used.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-yxorp-kuma-wire.py"
PLAY = ROOT / "ansible/yxorp-kvin-stage-kuma-wire-observe.yml"


class RedirectServer(BaseHTTPRequestHandler):
    def do_GET(self):
        location = (
            self.server.forwarded_location
            if self.headers.get("X-Forwarded-Host")
            else self.server.location
        )
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


class KumaRawWireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text(encoding="utf-8"))[0]

    def test_source_play_is_narrow_and_read_only(self):
        p = self.play
        self.assertEqual(p["hosts"], "yxorp")
        self.assertFalse(p["become"])
        self.assertFalse(p["gather_facts"])
        self.assertEqual(p["vars_files"],
                         ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        guard = p["tasks"][0]["ansible.builtin.assert"]["that"]
        for check in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_approved | bool",
            "yxorp_stage_kuma_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "yxorp_routes[5].upstream_host == 'kvar.outer.sanctum'",
            "yxorp_routes[5].upstream_port | int == 3001",
            "yxorp_routes[5].redirect_strip_upstream_port | default(false) | bool",
        ):
            self.assertIn(check, guard)
        for task in p["tasks"]:
            mods = [name for name in task if name.startswith("ansible.builtin.")]
            self.assertEqual(len(mods), 1)
            self.assertIn(mods[0], (
                "ansible.builtin.assert", "ansible.builtin.slurp",
                "ansible.builtin.command", "ansible.builtin.debug"))
        self.assertTrue(p["tasks"][1]["no_log"])
        self.assertTrue(p["tasks"][2]["no_log"])
        self.assertTrue(p["tasks"][4]["no_log"])
        cmd = p["tasks"][4]["ansible.builtin.command"]["argv"]
        self.assertEqual(cmd[0:2], ["python3", "-c"])
        self.assertIn("tools/observe-yxorp-kuma-wire.py", cmd[2])
        self.assertEqual(cmd[3:],
                         ["kvar.outer.sanctum", "3001", "kvar.outer.sanctum",
                          "80", "127.0.0.1", "80"])
        report = p["tasks"][-1]["ansible.builtin.debug"]["msg"]
        for required in (
            "published_equals_container_mount",
            "mounted_config_has_exact_kuma_redirect_rule",
            "mounted_config_exact_redirect_rule_count",
            "direct_wire", "incumbent_wire", "candidate_wire",
            "direct_with_proxy_headers_wire",
            "candidate_wire_equals_incumbent_wire",
            "direct_changes_when_forwarded_headers_present",
            "raw_location_values_exposed", "configuration_changed",
        ):
            self.assertIn(required, report)
        self.assertIs(report["raw_location_values_exposed"], False)
        self.assertIs(report["configuration_changed"], False)
        self.assertNotIn("raw_location", report)
        self.assertNotIn("body", report)
        self.assertNotIn("cookie", report)

    def test_raw_wire_redirection_and_forwarded_origin_are_classified(self):
        servers = []
        threads = []
        try:
            for location, forwarded in (
                ("http://kvar.outer.sanctum:3001/dashboard?secret=neverprint#frag",
                 "http://kuma.nexus.sanctum/dashboard?secret=neverprint#frag"),
                ("http://kvar.outer.sanctum/dashboard?secret=neverprint#frag", None),
                ("http://127.0.0.1:80/dashboard?secret=neverprint#frag", None),
            ):
                server = ThreadingHTTPServer(("127.0.0.1", 0), RedirectServer)
                server.location = location
                server.forwarded_location = forwarded or location
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                servers.append(server)
                threads.append(thread)
            argv = [sys.executable, str(SCRIPT)]
            for server in servers:
                argv.extend(["127.0.0.1", str(server.server_port)])
            proc = subprocess.run(
                argv, text=True, capture_output=True, timeout=24, check=True)
            report = json.loads(proc.stdout)
            self.assertEqual(report["direct_wire"]["status"], 302)
            self.assertEqual(report["direct_wire"]["host_class"], "kvar_backend_host")
            self.assertEqual(report["direct_wire"]["port_class"],
                             "kuma_backend_port_3001")
            self.assertEqual(report["incumbent_wire"]["port_class"], "no_explicit_port")
            self.assertEqual(report["candidate_wire"]["host_class"], "loopback")
            self.assertEqual(report["candidate_wire"]["port_class"],
                             "stage_http_port_80")
            self.assertFalse(report["candidate_wire_equals_incumbent_wire"])
            self.assertTrue(report["direct_changes_when_forwarded_headers_present"])
            self.assertEqual(report["direct_with_proxy_headers_wire"]["host_class"],
                             "frontend")
            self.assertFalse(report["raw_location_values_exposed"])
            self.assertNotIn("neverprint", proc.stdout)
            self.assertNotIn("dashboard", proc.stdout)
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
