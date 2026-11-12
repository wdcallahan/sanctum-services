"""Kvar survivor data preflight only observes metadata; never exports volume data."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "volume", ROOT / "tools/observe-kvar-survivor-volumes.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SECRET = b"THIS_IS_A_PRIVATE_CREDENTIAL_VALUE"


class VolumeReadiness(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.roots = {}
        for name in ("linkstack", "systemd-pihole_etc-pihole",
                     "systemd-pihole_etc-dnsmasq"):
            path = base / name / "_data"
            path.mkdir(parents=True)
            self.roots[name] = path
        link = self.roots["linkstack"]
        (link / "database").mkdir()
        (link / "database" / "database.sqlite").write_bytes(SECRET)
        (link / ".env").write_bytes(SECRET)
        (link / "shortcut").symlink_to(link / "database")
        pihole = self.roots["systemd-pihole_etc-pihole"]
        (pihole / "pihole.toml").write_bytes(SECRET)
        (pihole / "gravity.db").write_bytes(SECRET)
        (pihole / "pihole-FTL.db").write_bytes(SECRET)

    def runner(self, calls):
        def run(argv):
            calls.append(argv)
            if argv[:3] != ["podman", "volume", "inspect"]:
                raise AssertionError("Unexpected volume tool access")
            name = argv[-1]
            return str(self.roots[name])
        return run

    def test_rootless_linkstack_scans_files_without_reading_contents(self):
        calls = []
        r = module.collect("linkstack", "kvar.outer.sanctum", "wdc2",
                           runner=self.runner(calls))
        self.assertEqual(r["status"], "observed")
        self.assertEqual(len(r["volumes"]), 1)
        vol = r["volumes"][0]
        self.assertEqual(vol["known_file_markers"]["database/database.sqlite"],
                         "regular_file")
        self.assertEqual(vol["known_file_markers"][".env"], "regular_file")
        self.assertEqual(vol["scan"]["symlinks"], 1)
        self.assertEqual(vol["scan"]["regular_files"], 2)
        self.assertEqual(vol["scan"]["total_regular_file_bytes"], 2 * len(SECRET))
        self.assertFalse(r["data_exported"])
        self.assertFalse(r["backup_restore_accepted"])
        self.assertFalse(r["file_contents_read"])
        self.assertNotIn(SECRET.decode(), json.dumps(r))
        self.assertNotIn(self.temp.name, json.dumps(r))
        self.assertEqual(calls[0][:3], ["podman", "volume", "inspect"])

    def test_rootful_pihole_only_two_fixed_volumes(self):
        calls = []
        r = module.collect("pihole", "kvar.outer.sanctum", "root",
                           runner=self.runner(calls))
        self.assertEqual(r["status"], "observed")
        self.assertEqual([v["name"] for v in r["volumes"]],
                         ["systemd-pihole_etc-pihole", "systemd-pihole_etc-dnsmasq"])
        self.assertEqual(r["volumes"][0]["known_file_markers"]["gravity.db"],
                         "regular_file")
        self.assertEqual(r["volumes"][1]["scan"]["regular_files"], 0)
        self.assertEqual(len(calls), 2)
        self.assertNotIn(SECRET.decode(), json.dumps(r))

    def test_host_account_and_service_mismatch_refused_before_any_access(self):
        def forbidden(_):
            self.fail("Refused input may not query Podman")
        for name, host, account in [
            ("pihole", "kvar.outer.sanctum", "wdc2"),
            ("linkstack", "kvar.outer.sanctum", "root"),
            ("linkstack", "kvin.outer.sanctum", "wdc2"),
            ("unknown", "kvar.outer.sanctum", "root"),
        ]:
            self.assertEqual(module.collect(name, host, account, runner=forbidden)["status"],
                             "refused")

    def test_volume_missing_or_unbounded_cannot_be_accepted(self):
        unknown = module.collect("linkstack", "kvar.outer.sanctum", "wdc2",
                                 runner=lambda _: None)
        self.assertEqual(unknown["status"], "partial")
        self.assertEqual(unknown["volumes"][0]["reason"],
                         "volume_mountpoint_unavailable")
        self.assertNotIn("mountpoint", unknown["volumes"][0])
        original = module.MAX_ENTRIES
        module.MAX_ENTRIES = 1
        try:
            r = module.collect("linkstack", "kvar.outer.sanctum", "wdc2",
                               runner=self.runner([]))
            self.assertEqual(r["status"], "partial")
            self.assertEqual(r["volumes"][0]["scan"]["status"], "entry_limit")
        finally:
            module.MAX_ENTRIES = original

    def test_mountpoint_must_have_exact_volume_parent_and_no_symlink(self):
        path = self.roots["linkstack"]
        self.assertIsNone(module.safe_volume_mount(str(path.parent), "linkstack"))
        self.assertIsNone(module.safe_volume_mount(str(path), "pihole"))
        link = path.parent.parent / "alternate"
        link.symlink_to(path)
        self.assertIsNone(module.safe_volume_mount(str(link), "linkstack"))

    def test_Ansible_two_scoped_plays_and_CI_contract(self):
        plays = yaml.safe_load((ROOT / "ansible/kvar-survivors-source.yml").read_text())
        self.assertEqual(len(plays), 2)
        self.assertEqual([p["become"] for p in plays], [False, True])
        for p, name in zip(plays, ("linkstack", "pihole")):
            self.assertEqual(p["hosts"], "npm_proxy_legacy")
            self.assertEqual(len(p["tasks"]), 7)
            command = p["tasks"][4]
            self.assertTrue(command["no_log"])
            self.assertIs(command["changed_when"], False)
            self.assertIn("observe-kvar-survivor-volumes.py",
                          command["ansible.builtin.command"]["argv"][2])
            self.assertEqual(command["ansible.builtin.command"]["argv"][-1], name)
            self.assertIn("not ", str(p["tasks"][5]["ansible.builtin.assert"]["that"]))
        workflow = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_kvar_survivor_volumes.py", workflow)
        self.assertIn("ansible/kvar-survivors-source.yml --syntax-check", workflow)


if __name__ == "__main__":
    unittest.main()
