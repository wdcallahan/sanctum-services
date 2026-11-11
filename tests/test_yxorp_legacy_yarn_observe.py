"""Last old Yarn alias is read-only and deliberately not an eighth stage route."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-yxorp-legacy-yarn.py"
PLAY = ROOT / "ansible/yxorp-kvin-legacy-yarn-observe.yml"


class LocalYarnHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(self.server.result_status)
        self.send_header("Location", "/app/" if self.server.result_status == 302 else "")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


class LegacyYarnObserve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text(encoding="utf-8"))[0]

    def test_last_route_is_disabled_and_probe_has_no_service_mutations(self):
        route = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"][7]
        self.assertEqual((route["hostname"], route["upstream_host"],
                          route["upstream_port"], route["enabled"]),
                         ("yarn.inner.sanctum", "192.168.1.110", 80, False))
        p = self.play
        self.assertEqual(p["hosts"], "yxorp")
        self.assertFalse(p["gather_facts"])
        self.assertFalse(p["become"])
        self.assertEqual(
            p["vars_files"],
            ["vars/yxorp-kvin-stage.yml", "../data/yxorp-routes.yml"])
        guard = p["tasks"][0]["ansible.builtin.assert"]["that"]
        for text in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_kvin_stage_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "not (yxorp_routes[7].enabled | bool)",
            "yxorp_routes[7].hostname == 'yarn.inner.sanctum'",
            "yxorp_routes[7].upstream_host == '192.168.1.110'",
        ):
            self.assertIn(text, guard)
        command = p["tasks"][1]
        self.assertTrue(command["no_log"])
        self.assertIs(command["changed_when"], False)
        self.assertIs(command["failed_when"], False)
        argv = command["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[:2], ["python3", "-c"])
        self.assertIn("observe-yxorp-legacy-yarn.py", argv[2])
        self.assertEqual(len(argv), 3)
        self.assertIn("from_json", str(p["tasks"][-1]))
        for task in p["tasks"]:
            commands = {k for k in task if k.startswith("ansible.builtin.")}
            self.assertEqual(len(commands), 1)
            self.assertTrue(commands <= {
                "ansible.builtin.assert", "ansible.builtin.command",
                "ansible.builtin.debug"})

    def test_real_local_http_statuses_and_safe_alias_report(self):
        spec = importlib.util.spec_from_file_location("legacy_yarn", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        servers, threads = [], []
        try:
            for code in (200, 504, 302):
                server = ThreadingHTTPServer(("127.0.0.1", 0), LocalYarnHTTP)
                server.result_status = code
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                servers.append(server)
                threads.append(thread)
            real_connection = module.http.client.HTTPConnection
            mapping = {
                "192.168.1.110": servers[0].server_port,
                "yarn.inner.sanctum": servers[0].server_port,
                "kvar.outer.sanctum": servers[1].server_port,
                "127.0.0.1": servers[2].server_port,
            }
            def local_connection(host, port, timeout=6):
                self.assertEqual(port, 80)
                return real_connection("127.0.0.1", mapping[host], timeout=timeout)
            stdout = io.StringIO()
            with patch.object(module.http.client, "HTTPConnection",
                              side_effect=local_connection), \
                 patch.object(module.sys, "argv", ["-c"]), \
                 contextlib.redirect_stdout(stdout):
                module.main()
            result = json.loads(stdout.getvalue())
            probes = result["probes"]
            self.assertEqual(probes["legacy_direct_by_ip"]["http_status"], 200)
            self.assertEqual(probes["legacy_direct_by_dns_name"]["http_status"], 200)
            self.assertEqual(probes["legacy_through_incumbent_npm"]["http_status"], 504)
            self.assertEqual(probes["new_name_through_accepted_kvin_stage"]["http_status"], 302)
            self.assertEqual(probes["new_name_through_accepted_kvin_stage"]["redirect_kind"], "relative")
            self.assertFalse(result["new_kvin_legacy_route_activated"])
            self.assertFalse(result["configuration_changed"])
            self.assertFalse(result["sensitive_response_values_exposed"])
            self.assertNotIn("Location", stdout.getvalue())
            self.assertNotIn("/app/", stdout.getvalue())
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
