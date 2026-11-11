"""Native Kuma image-cache qualification must not become an app deployment."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
QUALIFY = ROOT / "ansible/kuma-qualify-image.yml"
CANDIDATES = ROOT / "data/container-image-candidates.yml"


class KumaImageQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(QUALIFY.read_text(encoding="utf-8"))[0]
        cls.image = yaml.safe_load(CANDIDATES.read_text(encoding="utf-8"))["kuma_candidate"]

    def test_candidate_is_existing_arm64_registry_metadata_not_installed(self):
        self.assertEqual(self.image["status"], "registry_only")
        self.assertEqual(self.image["platform"], "linux/arm64")
        self.assertEqual(self.image["tag_at_lookup"], "2.5.9")
        self.assertEqual(self.image["image"], (
            "docker.io/louislam/uptime-kuma@sha256:"
            "302aceeca2db79617f195a7549f7c8dfb05375a274b1092c59d81c1fb61a9ab9"
        ))

    def test_narrow_kvin_rootless_approval(self):
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertTrue(self.play["gather_facts"])
        self.assertFalse(self.play["become"])
        self.assertEqual(self.play["vars_files"],
                         ["../data/container-image-candidates.yml"])
        tasks = self.play["tasks"]
        first = tasks[0]["ansible.builtin.assert"]["that"]
        for clause in (
            "inventory_hostname == 'kvin.outer.sanctum'",
            "ansible_facts['fqdn'] == inventory_hostname",
            "ansible_facts['architecture'] == 'aarch64'",
            "kuma_image_qualification_approved | default(false) | bool",
            "not (kuma_stage_approved | default(false) | bool)",
            "kuma_candidate.tag_at_lookup == '2.5.9'",
            "kuma_candidate.platform == 'linux/arm64'",
            "kuma_candidate.status == 'registry_only'",
        ):
            self.assertIn(clause, first)
        self.assertIn("is match('^docker.io/louislam/uptime-kuma@sha256:",
                      "\n".join(first))

    def test_only_rootless_cached_image_pull_and_offline_disposable_runtime(self):
        tasks = self.play["tasks"]
        names = [t["name"] for t in tasks]
        self.assertLess(names.index("Require exact Kvin rootless-only cache qualification and closed app stage"),
                        names.index("Pull the exact arm64 digest into the rootless image cache only when missing"))
        self.assertLess(names.index("Inspect the exact cached image privately"),
                        names.index("Verify Node starts inside a disposable offline rootless candidate"))
        cmds = [t for t in tasks if "ansible.builtin.command" in t]
        self.assertEqual(len(cmds), 4)
        self.assertEqual(cmds[0]["ansible.builtin.command"]["argv"][:3],
                         ["podman", "image", "exists"])
        self.assertEqual(cmds[1]["ansible.builtin.command"]["argv"][:2],
                         ["podman", "pull"])
        self.assertIn("kuma_qualify_image_exists.rc == 1", cmds[1]["when"])
        self.assertTrue(cmds[1]["no_log"])
        self.assertEqual(cmds[2]["ansible.builtin.command"]["argv"][:3],
                         ["podman", "image", "inspect"])
        cmd = cmds[3]["ansible.builtin.command"]["argv"]
        self.assertEqual(cmd[:3], ["podman", "run", "--rm"])
        for constraint in ("none", "--read-only", "no-new-privileges",
                           "--entrypoint", "node", "--version"):
            self.assertIn(constraint, cmd)
        self.assertTrue(cmds[3]["no_log"])
        self.assertFalse(cmds[3]["changed_when"])
        for task in tasks:
            mods = [k for k in task if k.startswith("ansible.builtin.")]
            self.assertEqual(len(mods), 1)
            self.assertIn(mods[0], ("ansible.builtin.assert",
                                     "ansible.builtin.command",
                                     "ansible.builtin.debug"))
        source = QUALIFY.read_text(encoding="utf-8")
        for forbidden in ("systemd_service", "state: restarted",
                          "firewall-cmd", "podman volume create",
                          "quadlet", "yxorp_routes", "dnsmasq"):
            self.assertNotIn(forbidden, source.lower())
        reported = tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(reported["application_installed"], False)
        self.assertIs(reported["host_or_network_changed"], False)
        self.assertIs(reported["persistent_data_or_volume_changed"], False)

    def test_node_version_regex_has_no_double_backslash(self):
        checks = next(task for task in self.play["tasks"]
                      if task["name"] == "Require the native runtime actually executed")
        self.assertIn(
            "kuma_qualify_node.stdout is match('^v[0-9]+[.][0-9]+[.][0-9]+$')",
            checks["ansible.builtin.assert"]["that"],
        )
        self.assertNotIn("\\", str(checks))


if __name__ == "__main__":
    unittest.main()
