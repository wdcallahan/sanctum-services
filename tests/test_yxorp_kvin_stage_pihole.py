"""Pi-hole seventh-stage source contract and real wire HTTP synthetic checks."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WIRE = ROOT / "tools/observe-yxorp-pihole-wire.py"
PROBE = ROOT / "ansible/yxorp-kvin-stage-pihole-probe.yml"
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"


class PiHoleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/admin/":
            self.send_response(302)
            self.send_header("Location", self.server.admin_redirect)
        else:
            self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=UTF-8")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


class PiHoleStageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]
        cls.probe = yaml.safe_load(PROBE.read_text(encoding="utf-8"))[0]
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8"))["yxorp_routes"]
        cls.defaults = yaml.safe_load(
            (ROOT / "ansible/vars/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))

    def test_pihole_opt_in_off_and_kvar_ui_origin(self):
        self.assertIs(self.defaults["yxorp_stage_pihole_approved"], False)
        self.assertIs(self.defaults["yxorp_production_cutover_approved"], False)
        self.assertEqual([r["hostname"] for r in self.routes if r["enabled"]],
                         ["yarn.nexus.sanctum"])
        p = self.routes[6]
        self.assertEqual(
            (p["hostname"], p["upstream_scheme"], p["upstream_host"],
             p["upstream_port"], p["websocket"], p["enabled"]),
            ("pihole.nexus.sanctum", "http", "kvar.outer.sanctum",
             82, False, False))

    def test_pi_hole_only_added_after_six_previous(self):
        tasks = self.stage["pre_tasks"]
        names = [t["name"] for t in tasks]
        prior = names.index("Enable only interim Kuma with five previously accepted Kvin routes")
        gate = names.index("Require Pi-hole staging on top of six approved Kvin stage routes")
        select = names.index("Enable only interim Pi-hole with six retained Kvin stage routes")
        self.assertLess(prior, gate)
        self.assertLess(gate, select)
        self.assertEqual(self.stage["roles"], ["yxorp"])
        self.assertEqual(tasks[gate]["when"], "yxorp_stage_pihole_approved | default(false) | bool")
        self.assertEqual(tasks[select]["when"], "yxorp_stage_pihole_approved | default(false) | bool")
        checks = tasks[gate]["ansible.builtin.assert"]["that"]
        for expected in (
            "yxorp_stage_kuma_approved | bool",
            "yxorp_routes | length == 8",
            "yxorp_routes[6].hostname == 'pihole.nexus.sanctum'",
            "not (yxorp_routes[6].enabled | bool)",
            "yxorp_routes[6].upstream_host == 'kvar.outer.sanctum'",
            "yxorp_routes[6].upstream_port | int == 82",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum', 'joule.nexus.sanctum', 'search.nexus.sanctum', 'dir.nexus.sanctum', 'kuma.nexus.sanctum']",
        ):
            self.assertIn(expected, checks)
        select_expr = tasks[select]["ansible.builtin.set_fact"]["yxorp_routes"]
        self.assertIn("combine({'enabled': true})", select_expr)
        self.assertIn("yxorp_routes[7:]", select_expr)

    def test_probe_is_read_only_bounded_and_uses_raw_wire(self):
        self.assertEqual(self.probe["hosts"], "yxorp")
        self.assertFalse(self.probe["become"])
        self.assertFalse(self.probe["gather_facts"])
        tasks = self.probe["tasks"]
        for flag in ("yxorp_kvin_stage_approved", "yxorp_stage_pihole_approved"):
            self.assertIn(flag + " | bool", tasks[0]["ansible.builtin.assert"]["that"])
        command = tasks[1]
        self.assertTrue(command["no_log"])
        self.assertFalse(command["failed_when"])
        self.assertFalse(command["changed_when"])
        argv = command["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[0:2], ["python3", "-c"])
        self.assertIn("observe-yxorp-pihole-wire.py", argv[2])
        self.assertEqual(argv[3:], [
            "kvar.outer.sanctum", "82", "kvar.outer.sanctum",
            "80", "127.0.0.1", "80",
        ])
        self.assertIn("from_json", str(tasks[-1]))
        for task in tasks:
            modules = [key for key in task if key.startswith("ansible.builtin.")]
            self.assertEqual(len(modules), 1)
            self.assertIn(modules[0], (
                "ansible.builtin.assert", "ansible.builtin.command",
                "ansible.builtin.debug"))

    def test_raw_header_relative_redirect_equality_and_difference(self):
        servers, threads = [], []
        try:
            for redirect in (
                "/admin/login?test=keep#fragment",
                "/admin/login?test=keep#fragment",
                "/admin/login?test=keep#fragment",
            ):
                server = ThreadingHTTPServer(("127.0.0.1", 0), PiHoleHandler)
                server.admin_redirect = redirect
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                servers.append(server)
                threads.append(thread)
            cmd = [sys.executable, str(WIRE)]
            for server in servers:
                cmd.extend(["127.0.0.1", str(server.server_port)])
            first = subprocess.run(cmd, capture_output=True, text=True,
                                   timeout=40, check=True)
            result = json.loads(first.stdout)
            self.assertEqual(result["paths"]["root"]["direct_status"], 404)
            self.assertEqual(result["paths"]["root"]["candidate_status"], 404)
            self.assertTrue(result["paths"]["root"]["candidate_and_incumbent_status_equal"])
            self.assertEqual(result["paths"]["root"]["candidate_and_incumbent_raw_location_equal"],
                             "not_comparable")
            self.assertEqual(result["paths"]["admin"]["direct_status"], 302)
            self.assertTrue(result["paths"]["admin"]["candidate_and_incumbent_raw_location_equal"])
            self.assertTrue(result["paths"]["admin"]["candidate_and_incumbent_media_type_equal"])
            self.assertEqual(result["paths"]["admin"]["candidate_redirect_kind"], "relative")
            self.assertFalse(result["raw_headers_bodies_and_urls_exposed"])
            self.assertNotIn("test=keep", first.stdout)
            self.assertNotIn("/admin/login", first.stdout)
            servers[-1].admin_redirect = "/admin/wrong?test=keep#fragment"
            second = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=40, check=True)
            changed = json.loads(second.stdout)
            self.assertFalse(changed["paths"]["admin"]["candidate_and_incumbent_raw_location_equal"])
            self.assertTrue(changed["paths"]["admin"]["candidate_and_incumbent_status_equal"])
            self.assertNotIn("wrong", second.stdout)
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
