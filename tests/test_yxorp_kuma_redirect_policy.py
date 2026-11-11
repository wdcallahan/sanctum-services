"""Kuma's explicitly declared legacy NPM redirect authority policy only."""
from pathlib import Path
import unittest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/yxorp-routes.yml"
TEMPLATES = ROOT / "ansible/roles/yxorp/templates"
STAGE = ROOT / "ansible/yxorp-kvin-stage.yml"


class KumaRedirectPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = yaml.safe_load(DATA.read_text(encoding="utf-8"))["yxorp_routes"]
        cls.stage = yaml.safe_load(STAGE.read_text(encoding="utf-8"))[0]

    def test_only_kuma_has_declared_port_normalization(self):
        true_routes = [
            route["hostname"] for route in self.routes
            if route.get("redirect_strip_upstream_port", False)
        ]
        self.assertEqual(true_routes, ["kuma.nexus.sanctum"])
        for route in self.routes:
            if "redirect_strip_upstream_port" in route:
                self.assertIsInstance(route["redirect_strip_upstream_port"], bool)
        kuma = self.routes[5]
        self.assertFalse(kuma["enabled"])
        self.assertEqual(
            (kuma["hostname"], kuma["upstream_scheme"],
             kuma["upstream_host"], kuma["upstream_port"]),
            ("kuma.nexus.sanctum", "http", "kvar.outer.sanctum", 3001),
        )

    def test_explicit_redirect_rule_generated_only_for_kuma(self):
        routes = [{**route, "enabled": True} for route in self.routes]
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATES)),
            undefined=StrictUndefined,
        )
        result = env.get_template("nginx.conf.j2").render(yxorp_routes=routes)
        expected = (
            "proxy_redirect http://kvar.outer.sanctum:3001/ "
            "http://kvar.outer.sanctum/;"
        )
        self.assertEqual(result.count("\n            proxy_redirect "), 1)
        self.assertEqual(result.count(expected), 1)
        before, after = result.split("server_name kuma.nexus.sanctum;")
        self.assertNotIn("proxy_redirect ", before)
        self.assertIn(expected, after.split("server_name pihole.nexus.sanctum;")[0])
        self.assertNotIn("proxy_redirect ", after.split("server_name pihole.nexus.sanctum;")[1])
        self.assertIn("proxy_set_header Host $host;", result)
        self.assertIn("proxy_set_header X-Forwarded-Scheme $scheme;", result)
        self.assertIn("proxy_set_header Upgrade $http_upgrade;", result)

    def test_stage_guards_explicit_policy_before_publishing(self):
        pre = self.stage["pre_tasks"]
        checks = next(
            task for task in pre
            if task["name"] ==
            "Require Kuma stage on top of five accepted local HTTP routes"
        )["ansible.builtin.assert"]["that"]
        self.assertIn(
            "yxorp_routes[5].redirect_strip_upstream_port | default(false) | bool",
            checks,
        )
        self.assertIn(
            "yxorp_routes[5].upstream_host == 'kvar.outer.sanctum'", checks,
        )
        self.assertIn(
            "yxorp_routes[5].upstream_port | int == 3001", checks,
        )


if __name__ == "__main__":
    unittest.main()
