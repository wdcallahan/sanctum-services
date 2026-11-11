"""Eighth existing NPM Yarn route: safe staging and actual bounded-wire check."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import contextlib
import json
from pathlib import Path
import socket
import threading
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"
PROBE = ROOT / "ansible/yxorp-kvin-stage-yarn-inner-probe.yml"
HELPER = ROOT / "tools/observe-yxorp-kvin-stage-yarn-inner.py"


class YarnEcho(BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.headers.get("Host", "")
        if host == "yxorp-unmatched-observer.invalid":
            self.close_connection = True
            return
        if host == "yarn.nexus.sanctum":
            payload = b"new-name-control"
        else:
            payload = self.server.body
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass


class EighthYarnContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]
        cls.defaults = yaml.safe_load(
            (ROOT / "ansible/vars/yxorp-kvin-stage.yml").read_text(encoding="utf-8")
        )

    def test_eighth_is_existing_proxy_host_not_dns_policy(self):
        self.assertIs(self.defaults["yxorp_stage_yarn_inner_approved"], False)
        self.assertIs(self.defaults["yxorp_production_cutover_approved"], False)
        self.assertEqual(
            [r["hostname"] for r in self.routes if r["enabled"]],
            ["yarn.nexus.sanctum"],
        )
        old = self.routes[7]
        self.assertEqual(
            (old["hostname"], old["upstream_scheme"], old["upstream_host"],
             old["upstream_port"], old["websocket"], old["enabled"]),
            ("yarn.inner.sanctum", "http", "192.168.1.110", 80, False, False),
        )

    def test_eighth_projection_requires_exact_prior_seven(self):
        tasks = self.stage["pre_tasks"]
        names = [t["name"] for t in tasks]
        seventh = names.index(
            "Enable only interim Pi-hole with six retained Kvin stage routes"
        )
        guard = names.index(
            "Require existing Yarn inner vhost as eighth isolated Kvin stage route"
        )
        select = names.index(
            "Enable only eighth existing Yarn inner vhost with seven prior stage routes"
        )
        self.assertLess(seventh, guard)
        self.assertLess(guard, select)
        self.assertEqual(self.stage["roles"], ["yxorp"])
        for idx in (guard, select):
            self.assertEqual(tasks[idx]["when"],
                             "yxorp_stage_yarn_inner_approved | default(false) | bool")
        checks = tasks[guard]["ansible.builtin.assert"]["that"]
        for expected in (
            "yxorp_stage_pihole_approved | bool",
            "yxorp_routes | length == 8",
            "yxorp_routes[7].hostname == 'yarn.inner.sanctum'",
            "not (yxorp_routes[7].enabled | bool)",
            "yxorp_routes[7].upstream_host == '192.168.1.110'",
            "yxorp_routes[7].upstream_port | int == 80",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum', 'joule.nexus.sanctum', 'search.nexus.sanctum', 'dir.nexus.sanctum', 'kuma.nexus.sanctum', 'pihole.nexus.sanctum']",
        ):
            self.assertIn(expected, checks)
        expression = tasks[select]["ansible.builtin.set_fact"]["yxorp_routes"]
        self.assertIn("yxorp_routes[:7]", expression)
        self.assertIn("combine({'enabled': true})", expression)
        self.assertNotIn("yxorp_routes[8:]", expression)

    def test_probe_read_only_exact_kvin_and_eighth(self):
        play = self.probe
        self.assertEqual(play["hosts"], "yxorp")
        self.assertIs(play["become"], False)
        self.assertIs(play["gather_facts"], False)
        tasks = play["tasks"]
        guards = tasks[0]["ansible.builtin.assert"]["that"]
        for check in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "yxorp_stage_yarn_inner_approved | bool",
            "not (yxorp_production_cutover_approved | bool)",
            "not (yxorp_routes[7].enabled | bool)",
        ):
            self.assertIn(check, guards)
        commands = [t for t in tasks if "ansible.builtin.command" in t]
        self.assertEqual(len(commands), 2)
        self.assertTrue(all(t["no_log"] for t in commands))
        self.assertTrue(all(t["changed_when"] is False for t in commands))
        helper = commands[-1]["ansible.builtin.command"]["argv"]
        self.assertEqual(helper[:2], ["python3", "-c"])
        self.assertIn("observe-yxorp-kvin-stage-yarn-inner.py", helper[2])
        self.assertEqual(len(helper), 3)
        task_names = [t["name"] for t in tasks]
        self.assertLess(
            task_names.index("Report only eighth Yarn route configuration and wire acceptance metadata"),
            task_names.index("Require real eighth route behavior and mounted config acceptance"),
        )
        self.assertIn("old_complete_body_identical_to_direct", str(tasks[-1]))
        self.assertIn("unknown_host_denied_without_http_response", str(tasks[-1]))

    def test_actual_local_http_comparator_avoids_normalized_uri(self):
        spec = importlib.util.spec_from_file_location("yxorp_yarn_inner", HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        servers, threads = [], []
        try:
            for body in (b"yarn-content", b"yarn-content"):
                server = ThreadingHTTPServer(("127.0.0.1", 0), YarnEcho)
                server.body = body
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                servers.append(server)
                threads.append(thread)
            origin_port, stage_port = [x.server_port for x in servers]
            real_connection = module.http.client.HTTPConnection
            def local_conn(host, port, timeout=6):
                self.assertEqual(port, 80)
                target_port = origin_port if host == "192.168.1.110" else stage_port
                self.assertIn(host, ("192.168.1.110", "127.0.0.1"))
                return real_connection("127.0.0.1", target_port, timeout=timeout)
            def run():
                out = io.StringIO()
                with patch.object(module.http.client, "HTTPConnection",
                                  side_effect=local_conn), contextlib.redirect_stdout(out):
                    module.main()
                return json.loads(out.getvalue()), out.getvalue()
            okay, printed = run()
            checks = okay["checks"]
            self.assertTrue(checks["old_origin_http_200"])
            self.assertTrue(checks["old_stage_http_200"])
            self.assertTrue(checks["new_stage_http_200"])
            self.assertTrue(checks["old_complete_body_identical_to_direct"])
            self.assertTrue(checks["unknown_host_denied_without_http_response"])
            self.assertFalse(okay["raw_http_headers_bodies_and_credentials_exposed"])
            self.assertFalse(okay["configuration_changed"])
            self.assertNotIn("yarn-content", printed)
            self.assertNotIn("new-name-control", printed)
            servers[1].body = b"wrong-upstream-content"
            wrong, _ = run()
            self.assertFalse(wrong["checks"]["old_complete_body_identical_to_direct"])
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
