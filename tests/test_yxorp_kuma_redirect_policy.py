"""Regression: do not rewrite equal relative Kuma Location headers unnecessarily."""
from pathlib import Path
import unittest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[1]


class KumaRelativeRedirectContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
        )["yxorp_routes"]
        cls.stage = yaml.safe_load(
            (ROOT / "ansible/yxorp-kvin-stage.yml").read_text(encoding="utf-8")
        )[0]

    def test_manifest_does_not_carry_unnecessary_absolute_redirect_policy(self):
        self.assertEqual(
            [r["hostname"] for r in self.routes if r["enabled"]],
            ["yarn.nexus.sanctum"],
        )
        self.assertEqual(
            [(r["hostname"], r["redirect_strip_upstream_port"])
             for r in self.routes if "redirect_strip_upstream_port" in r],
            [],
        )
        k = self.routes[5]
        self.assertEqual(
            (k["hostname"], k["upstream_host"], k["upstream_port"], k["enabled"]),
            ("kuma.nexus.sanctum", "kvar.outer.sanctum", 3001, False),
        )

    def test_no_special_proxy_redirect_in_actual_template(self):
        env = Environment(
            loader=FileSystemLoader(str(ROOT / "ansible/roles/yxorp/templates")),
            undefined=StrictUndefined,
        )
        rendered = env.get_template("nginx.conf.j2").render(
            yxorp_routes=[{**r, "enabled": True} for r in self.routes])
        self.assertNotIn("proxy_redirect ", rendered)
        self.assertIn("server_name kuma.nexus.sanctum;", rendered)
        self.assertIn("proxy_set_header Host $host;", rendered)
        self.assertIn("proxy_set_header X-Forwarded-Scheme $scheme;", rendered)

    def test_stage_does_not_require_obsolete_policy(self):
        task = next(t for t in self.stage["pre_tasks"] if
                    t["name"] == "Require Kuma stage on top of five accepted local HTTP routes")
        checks = task["ansible.builtin.assert"]["that"]
        self.assertNotIn(
            "yxorp_routes[5].redirect_strip_upstream_port | default(false) | bool",
            checks)
        self.assertIn("yxorp_routes[5].upstream_host == 'kvar.outer.sanctum'", checks)
        self.assertIn("yxorp_routes[5].upstream_port | int == 3001", checks)


if __name__ == "__main__":
    unittest.main()
