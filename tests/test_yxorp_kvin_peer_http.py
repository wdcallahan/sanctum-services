"""Separate-Peanut native Kvin production proxy probe is read-only."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

class PeanutToKvinProductionContract(unittest.TestCase):
    def test_peer_play_does_not_touch_production(self):
        play=yaml.safe_load((ROOT/"ansible/yxorp-kvin-peer-http.yml").read_text())[0]
        self.assertEqual(play["hosts"],"yxorp_test")
        self.assertFalse(play["become"])
        self.assertTrue(play["gather_facts"])
        self.assertEqual(len(play["tasks"]),4)
        gate=play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'peanut.arcane.sanctum'",gate)
        command=play["tasks"][1]
        self.assertTrue(command["no_log"])
        self.assertIs(command["changed_when"],False)
        self.assertIn("observe-yxorp-kvin-from-peanut.py",command["ansible.builtin.command"]["argv"][-1])
        self.assertIn("is boolean",str(play["tasks"][2]))
        for task in play["tasks"]:
            for mutation in ("ansible.builtin.copy","ansible.builtin.file",
                             "ansible.builtin.template","ansible.builtin.uri",
                             "ansible.builtin.shell","ansible.builtin.systemd_service"):
                self.assertNotIn(mutation,task)

    def test_disambiguates_two_source_declared_kvin_addresses(self):
        code=(ROOT/"tools/observe-yxorp-kvin-from-peanut.py").read_text()
        for phrase in ("192.168.0.192","192.168.1.192",
                       "kvin.outer.sanctum","kuma.nexus.sanctum",
                       "yarn.nexus.sanctum", "proven_non_kvin_http_reachability",
                       "named_nexus_dns_cutover_accepted", "kvar_or_dns_or_firewall_changed"):
            self.assertIn(phrase,code)
        self.assertNotIn("subprocess",code)
        self.assertNotIn("requests.",code)

    def test_full_ci_qualifies_observer_syntax_and_source_contract(self):
        workflow=(ROOT/".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_yxorp_kvin_peer_http.py",workflow)
        self.assertIn("ansible/yxorp-kvin-peer-http.yml --syntax-check",workflow)

if __name__=="__main__":
    unittest.main()
