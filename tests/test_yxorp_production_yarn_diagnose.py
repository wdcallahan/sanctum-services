"""Read-only native Kvin production Yarn diagnostic, separate from mutation."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/yxorp-production-yarn-diagnose.yml"
HELPER=ROOT/"tools/observe-yxorp-production-yarn.py"
CI=ROOT/".github/workflows/yxorp-source-check.yml"

class ProductionYarnObserver(unittest.TestCase):
    def test_native_observer_safe_and_non_mutating(self):
        play=yaml.safe_load(PLAY.read_text())[0]
        self.assertEqual(play["hosts"],"yxorp")
        self.assertIs(play["become"],False)
        self.assertTrue(play["gather_facts"])
        self.assertEqual(len(play["tasks"]),6)
        expected=[
          "ansible.builtin.assert",
          "ansible.builtin.command",
          "ansible.builtin.assert",
          "ansible.builtin.command",
          "ansible.builtin.assert",
          "ansible.builtin.debug",
        ]
        self.assertEqual([next(k for k in task if k.startswith("ansible.builtin."))
                          for task in play["tasks"]], expected)
        guard=play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'",guard)
        self.assertIn("yxorp_deployment_scope == 'kvin_production'",guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)",guard)
        observer=play["tasks"][3]
        self.assertIs(observer["changed_when"],False)
        self.assertIs(observer["no_log"],True)
        self.assertIn("observe-yxorp-production-yarn.py",
                      observer["ansible.builtin.command"]["argv"][-1])
        self.assertIn("ansible/yxorp-production-yarn-diagnose.yml --syntax-check",
                      CI.read_text())

    def test_direct_ip_dns_and_both_proxied_names_without_secrets(self):
        src=HELPER.read_text()
        for literal in ("192.168.1.110","yarn.inner.sanctum",
                        "yarn.nexus.sanctum","kuma.nexus.sanctum",
                        "socket.getaddrinfo","http.client.HTTPConnection",
                        "production_proxy_new_host","production_proxy_old_host",
                        "origin_by_ip_new_host","production_proxy_kuma_control",
                        "contents_headers_cookies_exposed"):
            self.assertIn(literal,src)
        self.assertNotIn("podman run",src)
        self.assertNotIn("firewall-cmd",src)
        self.assertNotIn("write_text",src)


if __name__=="__main__":
    unittest.main()
