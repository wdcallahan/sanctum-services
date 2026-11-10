"""Yarn route comparison is read-only and never prints fetched page content."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/yxorp-peanut-yarn-content.yml"


class YarnComparisonContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAY.read_text(encoding="utf-8")
        cls.plays = yaml.safe_load(cls.source)

    def test_client_scope_and_production_gate(self):
        self.assertEqual(len(self.plays), 1)
        play = self.plays[0]
        self.assertEqual(play["hosts"], "yxorp")
        self.assertFalse(play["become"])
        checks = play["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", checks)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", checks)

    def test_same_anonymous_host_and_path_for_origin_and_proxy(self):
        calls = [task for task in self.plays[0]["tasks"] if "ansible.builtin.uri" in task]
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            {call["ansible.builtin.uri"]["url"] for call in calls},
            {"http://yarn.inner.sanctum/", "http://peanut.arcane.sanctum/"})
        for call in calls:
            req = call["ansible.builtin.uri"]
            self.assertEqual(req["headers"], {"Host": "yarn.nexus.sanctum"})
            self.assertFalse(req["use_proxy"])
            self.assertEqual(req["follow_redirects"], "none")
            self.assertTrue(req["return_content"])
            self.assertEqual(req["timeout"], 10)
            self.assertTrue(call["no_log"])
            self.assertIs(call["changed_when"], False)
            self.assertNotIn("body", req)
            self.assertNotIn("method", req)

    def test_safe_metadata_only_and_no_mutations(self):
        allowed = {"ansible.builtin.assert", "ansible.builtin.uri", "ansible.builtin.debug"}
        for task in self.plays[0]["tasks"]:
            self.assertTrue(set(task) & allowed)
            self.assertFalse(set(k for k in task if k.startswith("ansible.builtin.")) - allowed)
        report = self.plays[0]["tasks"][-1]["ansible.builtin.debug"]["msg"]
        self.assertIn("body_equal", report)
        self.assertIn("origin_body_length", report)
        self.assertIn("status_equal", report)
        self.assertNotIn("origin_body", report)
        self.assertNotIn("proxied_body", report)
        self.assertNotIn("content", report)


if __name__ == "__main__":
    unittest.main()
