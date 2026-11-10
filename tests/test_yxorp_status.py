"""Source guard: Peanut YXORP status inspection is read-only and client-aware."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "ansible/yxorp-peanut-status.yml"


class PeanutStatusContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plays = yaml.safe_load(STATUS.read_text(encoding="utf-8"))

    def test_two_distinct_real_hosts_are_observed(self):
        self.assertEqual([p["hosts"] for p in self.plays], ["yxorp_test", "yxorp"])
        self.assertTrue(self.plays[0]["become"])
        self.assertFalse(self.plays[1]["become"])
        peanut_guard = self.plays[0]["tasks"][0]["ansible.builtin.assert"]["that"]
        kvin_guard = self.plays[1]["tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn("inventory_hostname == 'peanut.arcane.sanctum'", peanut_guard)
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", kvin_guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", peanut_guard)
        self.assertIn("not (yxorp_production_cutover_approved | bool)", kvin_guard)

    def test_only_nonmutating_tasks_and_bounded_http(self):
        permitted = {
            "ansible.builtin.assert", "ansible.builtin.command",
            "ansible.builtin.stat", "ansible.builtin.uri", "ansible.builtin.debug",
        }
        for play in self.plays:
            for task in play["tasks"]:
                module = next(k for k in task if k.startswith("ansible.builtin."))
                self.assertIn(module, permitted, task["name"])
                if module in ("ansible.builtin.command", "ansible.builtin.uri"):
                    self.assertIs(task["changed_when"], False, task["name"])
                if module == "ansible.builtin.command":
                    argv = task[module]["argv"]
                    self.assertNotIn("--add-", str(argv))
                    self.assertNotIn("--remove-", str(argv))
                    self.assertNotIn("--reload", str(argv))
                if module == "ansible.builtin.uri":
                    request = task[module]
                    self.assertEqual(request["timeout"], 5)
                    self.assertFalse(request["use_proxy"])
                    self.assertEqual(request["url"].split(":80")[0].split("//")[-1],
                                     "127.0.0.1" if play["hosts"] == "yxorp_test"
                                     else "peanut.arcane.sanctum")

    def test_observes_both_service_and_network_admission(self):
        local = STATUS.read_text(encoding="utf-8")
        for fragment in ("systemctl", "ss, -H, -ltn", "--query-port=80/tcp",
                         "--query-service=http", "trial_marker_present",
                         "local_yxorp_ready", "peer_yxorp_ready"):
            self.assertIn(fragment, local)
        self.assertNotIn("--timeout=4h", local)
        self.assertNotIn("state: started", local)
        self.assertNotIn("state: stopped", local)


if __name__ == "__main__":
    unittest.main()
