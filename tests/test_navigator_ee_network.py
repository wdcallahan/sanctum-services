"""The Services Navigator runtime must connect to native Kvin, not EE loopback."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class NavigatorNetworkContract(unittest.TestCase):
    def test_ee_uses_the_qualified_host_network_namespace(self):
        config = yaml.safe_load((ROOT / "ansible-navigator.yml").read_text())
        options = config["ansible-navigator"]["execution-environment"]["container-options"]
        self.assertEqual(options, ["--net=host"])

    def test_ssh_inventory_keeps_dns_owned_address(self):
        inventory = yaml.safe_load((ROOT / "ansible/inventory/hosts.yml").read_text())
        node = inventory["all"]["children"]["nextcloud"]["hosts"]["kvin.outer.sanctum"]
        self.assertEqual(node["ansible_user"], "wdc2")
        self.assertNotIn("ansible_host", node)
        self.assertNotIn("ansible_connection", node)


if __name__ == "__main__":
    unittest.main()
