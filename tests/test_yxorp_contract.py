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
        cls.peanut = yaml.safe_load(
            (ROOT / "ansible/group_vars/yxorp_test.yml").read_text(encoding="utf8")
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

    def test_imported_npm_default_routes_remain_disabled(self):
        by_name = {r["hostname"]: r for r in self.routes}
        self.assertEqual(len(by_name), 8)
        self.assertEqual(set(by_name), {
            "yarn.nexus.sanctum", "square.nexus.sanctum",
            "joule.nexus.sanctum", "search.nexus.sanctum",
            "dir.nexus.sanctum", "kuma.nexus.sanctum",
            "pihole.nexus.sanctum", "yarn.inner.sanctum",
        })
        self.assertEqual(
            (by_name["pihole.nexus.sanctum"]["upstream_host"],
             by_name["pihole.nexus.sanctum"]["upstream_port"]),
            ("kvar.outer.sanctum", 82),
        )
        self.assertEqual(
            (by_name["yarn.inner.sanctum"]["upstream_host"],
             by_name["yarn.inner.sanctum"]["upstream_port"]),
            ("192.168.1.110", 80),
        )
        self.assertFalse(by_name["pihole.nexus.sanctum"]["enabled"])
        self.assertFalse(by_name["yarn.inner.sanctum"]["enabled"])
        self.assertNotIn("yxorp.nexus.sanctum", by_name)

    def test_separate_real_http_80_peanut_and_production_contract(self):
        self.assertEqual(self.defaults["yxorp_bind_address"], "0.0.0.0")
        self.assertEqual(self.defaults["yxorp_host_port"], 80)
        self.assertEqual(self.defaults["yxorp_deployment_scope"], "kvin_production")
        self.assertIs(self.defaults["yxorp_production_cutover_approved"], False)
        self.assertRegex(self.defaults["yxorp_image"],
                         r"^docker.io/library/nginx@sha256:[a-f0-9]{64}$")
        self.assertEqual(self.peanut["yxorp_deployment_scope"], "peanut_trial")
        self.assertEqual(self.peanut["yxorp_bind_address"], "0.0.0.0")
        self.assertEqual(self.peanut["yxorp_host_port"], 80)
        self.assertTrue(self.peanut["yxorp_peanut_test_approved"])
        self.assertEqual(self.peanut["yxorp_image"],
                         "docker.io/library/nginx:stable-alpine")
        self.assertEqual(self.peanut["yxorp_service_name"],
                         "sanctum-yxorp-peanut-test.service")
        self.assertIn("peanut.arcane.sanctum",
                      yaml.safe_load((ROOT / "ansible/inventory/hosts.yml").read_text())
                      ["all"]["children"]["yxorp_test"]["hosts"])
        task_text = (ROOT / "ansible/roles/yxorp/tasks/main.yml").read_text()
        self.assertIn("yxorp_peanut_test_approved", task_text)
        self.assertIn("yxorp_production_cutover_approved | bool", task_text)
        self.assertLess(task_text.index("Require a specifically selected rootful HTTP 80"),
                        task_text.index("Create YXORP system configuration directory"))
        self.assertIn("- bridge", task_text)
        self.assertNotIn("firewall-cmd", task_text)

    def test_peanut_preflight_requires_real_lan_http(self):
        source = (ROOT / "ansible/yxorp-peanut-preflight.yml").read_text()
        preflight = yaml.safe_load(source)[0]
        self.assertEqual(preflight["hosts"], "yxorp_test")
        self.assertTrue(preflight["become"])
        names = [t["name"] for t in preflight["tasks"]]
        self.assertIn("Refuse taking port 80 from another host service", names)
        self.assertIn("Require public-LAN HTTP admission before installing a test listener",
                      names)
        self.assertNotIn("state: present", source)
        self.assertNotIn("state: started", source)
        self.assertNotIn("firewall-cmd --add", source)

    def test_quadlet_rootful_bridge_and_no_https(self):
        quadlet = (ROOT / "ansible/roles/yxorp/templates/yxorp.container.j2").read_text()
        nginx = (ROOT / "ansible/roles/yxorp/templates/nginx.conf.j2").read_text()
        self.assertIn("Network=bridge", quadlet)
        self.assertIn("PublishPort={{ yxorp_bind_address }}", quadlet)
        self.assertNotIn("443", quadlet)
        self.assertNotIn("ssl_certificate", nginx)
        self.assertIn("proxy_set_header Host $host", nginx)
        self.assertIn("proxy_set_header X-Forwarded-Scheme $scheme", nginx)
        self.assertIn("proxy_set_header Upgrade $http_upgrade", nginx)
        self.assertIn("return 444", nginx)
        self.assertIn("WantedBy=multi-user.target", quadlet)
        stage = next(t for t in self.tasks
                     if t["name"] == "Start or reconcile YXORP using the system service manager")
        self.assertNotIn("enabled", stage["ansible.builtin.systemd_service"])


if __name__ == "__main__":
    unittest.main()
