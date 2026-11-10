"""Source-only reversibility guard for the Peanut HTTP 80 rootful test."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class StageRemovalContract(unittest.TestCase):
    def test_removal_is_explicit_and_scoped(self):
        play = yaml.safe_load(
            (ROOT / "ansible/yxorp-peanut-remove.yml").read_text())
        self.assertEqual(len(play), 1)
        self.assertEqual(play[0]["hosts"], "yxorp_test")
        self.assertTrue(play[0]["become"])
        tasks = play[0]["tasks"]
        start = tasks[0]["ansible.builtin.assert"]["that"]
        self.assertIn("yxorp_peanut_remove_approved | default(false) | bool", start)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", start)
        self.assertIn("yxorp_bind_address == '0.0.0.0'", start)
        self.assertIn("yxorp_host_port | int == 80", start)
        names = [item["name"] for item in tasks]
        self.assertLess(names.index("Refuse a changed or unrelated Peanut Quadlet"),
                        names.index("Stop the existing stage service, if active"))
        self.assertLess(names.index("Refuse removing directories with any unknown contents"),
                        names.index("Stop the existing stage service, if active"))
        source = (ROOT / "ansible/yxorp-peanut-remove.yml").read_text()
        self.assertNotIn("image rm", source)
        self.assertIn("firewall-cmd", source)
        self.assertIn("--remove-port=80/tcp", source)
        self.assertIn("/run/sanctum-yxorp-peanut-http80-trial-owned", source)
        self.assertIn("Confirm that this marker owns only the recorded public TCP 80 test rule",
                      names)
        self.assertLess(names.index("Remove only the temporary public TCP 80 runtime rule we added"),
                        names.index("Remove only the verified trial ownership marker"))
        self.assertNotIn("--permanent", source)
        self.assertNotIn("dnscmd", source)


if __name__ == "__main__":
    unittest.main()
