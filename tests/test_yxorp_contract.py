"""Source-only YXORP contract; python3 -m unittest discover -s tests."""
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class YxorpContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = yaml.safe_load(
            (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf8")
        )["yxorp_routes"]
        cls.defaults = yaml.safe_load(
            (ROOT / "ansible/group_vars/yxorp.yml").read_text(encoding="utf8")
        )
        cls.tasks = yaml.safe_load(
            (ROOT / "ansible/roles/yxorp/tasks/main.yml").read_text(encoding="utf8")
        )

    def test_unique_safe_routes(self):
        names = [route["hostname"] for route in self.routes]
        self.assertEqual(len(names), len(set(names)))
        for route in self.routes:
            self.assertRegex(route["hostname"], r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$")
            self.assertRegex(route["upstream_host"], r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$")
            self.assertEqual(route["upstream_scheme"], "http")
            self.assertTrue(1 <= route["upstream_port"] <= 65535)
            self.assertIsInstance(route["websocket"], bool)
            self.assertIsInstance(route["enabled"], bool)

    def test_yarn_only_initially_enabled_and_distinct(self):
        enabled = [r["hostname"] for r in self.routes if r["enabled"]]
        self.assertEqual(enabled, ["yarn.nexus.sanctum"])
        yarn = self.routes[0]
        self.assertEqual((yarn["upstream_host"], yarn["upstream_port"]),
                         ("yarn.inner.sanctum", 80))
        self.assertNotEqual(yarn["hostname"], yarn["upstream_host"])

    def test_no_untested_production_listener_or_mutable_image(self):
        self.assertEqual(self.defaults["yxorp_bind_address"], "127.0.0.1")
        self.assertEqual(self.defaults["yxorp_host_port"], 18080)
        self.assertIs(self.defaults["yxorp_production_cutover_approved"], False)
        self.assertEqual(self.defaults["yxorp_image"], "")
        task_text = (ROOT / "ansible/roles/yxorp/tasks/main.yml").read_text()
        self.assertIn("yxorp_production_cutover_approved | bool", task_text)
        self.assertIn("-t", task_text)
        self.assertLess(task_text.index("Require Nginx configuration validation"),
                        task_text.index("Publish validated Nginx configuration"))
        self.assertNotIn("firewall-cmd", task_text)

    def test_quadlet_rootful_bridge_and_no_https(self):
        quadlet = (ROOT / "ansible/roles/yxorp/templates/yxorp.container.j2").read_text()
        nginx = (ROOT / "ansible/roles/yxorp/templates/nginx.conf.j2").read_text()
        self.assertIn("Network=bridge", quadlet)
        self.assertIn("PublishPort={{ yxorp_bind_address }}", quadlet)
        self.assertNotIn("443", quadlet)
        self.assertNotIn("ssl_certificate", nginx)
        self.assertIn("proxy_set_header Host $host", nginx)
        self.assertIn("proxy_set_header Upgrade $http_upgrade", nginx)
        self.assertIn("return 444", nginx)


if __name__ == "__main__":
    unittest.main()
