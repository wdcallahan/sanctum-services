"""Source-only reversibility guard for the rootful YXORP loopback stage."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class StageRemovalContract(unittest.TestCase):
    def test_removal_is_explicit_and_scoped(self):
        play = yaml.safe_load(
            (ROOT / "ansible/yxorp-remove-stage.yml").read_text())
        self.assertEqual(len(play), 1)
        self.assertEqual(play[0]["hosts"], "yxorp")
        self.assertTrue(play[0]["become"])
        tasks = play[0]["tasks"]
        start = tasks[0]["ansible.builtin.assert"]["that"]
        self.assertIn("yxorp_stage_remove_approved | default(false) | bool", start)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", start)
        self.assertIn("yxorp_bind_address == '127.0.0.1'", start)
        self.assertIn("yxorp_host_port | int == 18080", start)
        names = [item["name"] for item in tasks]
        self.assertLess(names.index("Refuse a changed or production-scope Quadlet"),
                        names.index("Stop the existing stage service, if active"))
        self.assertLess(names.index("Refuse removing directories with any unknown contents"),
                        names.index("Stop the existing stage service, if active"))
        source = (ROOT / "ansible/yxorp-remove-stage.yml").read_text()
        self.assertNotIn("image rm", source)
        self.assertNotIn("firewall-cmd", source)
        self.assertNotIn("dnscmd", source)


if __name__ == "__main__":
    unittest.main()
