"""Source contract for explicit, non-destructive Kuma candidate reversal."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

class KumaStageRemoval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(
            (ROOT / "ansible/kuma-stage-remove.yml").read_text(encoding="utf8")
        )[0]
        cls.tasks = cls.play["tasks"]

    def test_exact_rootless_kvin_and_separate_approval(self):
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        checks = self.tasks[0]["ansible.builtin.assert"]["that"]
        for required in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "ansible_facts['architecture'] == 'aarch64'",
            "kuma_stage_remove_approved | default(false) | bool",
            "not (kuma_stage_approved | default(false) | bool)",
            "kuma_quadlet_file == '/home/wdc2/.config/containers/systemd/sanctum-kuma.container'",
            "kuma_data_volume == 'sanctum-kuma-data'",
        ):
            self.assertIn(required, checks)

    def test_reversal_inspects_before_stopping_or_deleting(self):
        names = [t["name"] for t in self.tasks]
        self.assertLess(
            names.index("Require the installed Quadlet to be the exact owned candidate"),
            names.index("Stop the exact candidate user service only when active"),
        )
        self.assertLess(
            names.index("Stop the exact candidate user service only when active"),
            names.index("Remove only the verified candidate Quadlet generator input"),
        )
        stop = next(t["ansible.builtin.systemd_service"] for t in self.tasks
                    if t["name"] == "Stop the exact candidate user service only when active")
        self.assertEqual(stop["scope"], "user")
        self.assertNotIn("enabled", stop)
        removal = next(t["ansible.builtin.file"] for t in self.tasks
                       if t["name"] == "Remove only the verified candidate Quadlet generator input")
        self.assertEqual(removal["state"], "absent")
        self.assertEqual(removal["path"], "{{ kuma_quadlet_file }}")

    def test_no_volume_image_host_or_production_mutations(self):
        source = (ROOT / "ansible/kuma-stage-remove.yml").read_text(encoding="utf8")
        for forbidden in ("podman volume rm", "podman volume prune", "podman rmi",
                          "firewall-cmd", "yxorp_routes", "kvar.outer.sanctum"):
            self.assertNotIn(forbidden, source)
        msg = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for key in ("data_volume_deleted", "cached_image_deleted",
                    "kvar_service_changed", "yxorp_changed", "dns_or_host_firewall_changed"):
            self.assertIs(msg[key], False)

if __name__ == "__main__":
    unittest.main()
