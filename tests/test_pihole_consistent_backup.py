"""Private Pi-hole complete-volume archive validation and quiesced recovery contract."""
from pathlib import Path
import importlib.util
import io
import json
import os
import sqlite3
import tarfile
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools/pihole-archive-verify.py"
PLAY = ROOT / "ansible/pihole-consistent-backup.yml"
spec = importlib.util.spec_from_file_location("verify", VERIFY)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SECRET = b"VERY_PRIVATE_PIHOLE_API_PASSWORD_MUST_NOT_LEAK"


class PiHoleArchiveVerifier(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive = self.root / "pihole.tar"
        self.db = self.root / "original.db"
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE x (secret TEXT)")
        conn.execute("INSERT INTO x (secret) VALUES (?)", (SECRET.decode(),))
        conn.commit()
        conn.close()

    def create(self, members):
        with tarfile.open(self.archive, "w") as tar:
            for name, payload in members:
                member = tarfile.TarInfo(name)
                if payload is None:
                    member.type = tarfile.DIRTYPE
                    member.mode = 0o700
                    tar.addfile(member)
                else:
                    member.size = len(payload)
                    member.mode = 0o600
                    tar.addfile(member, io.BytesIO(payload))
        self.archive.chmod(0o600)

    def full(self):
        return [("./", None), ("pihole.toml", SECRET),
                ("gravity.db", self.db.read_bytes()),
                ("pihole-FTL.db", self.db.read_bytes()),
                ("other/config.txt", SECRET)]

    def test_complete_rootful_pihole_archive_passes_full_sqlite_integrity(self):
        self.create(self.full())
        r = mod.inspect("etc-pihole", self.archive)
        self.assertEqual(r["schema"], "sanctum-pihole-volume-archive/v1")
        self.assertEqual(r["volume_role"], "etc-pihole")
        self.assertTrue(r["archive_verified"])
        self.assertTrue(r["required_state_present"])
        self.assertEqual(r["sqlite_integrity"], "ok")
        self.assertEqual(r["regular_file_count"], 4)
        self.assertEqual(len(r["archive_sha256"]), 64)
        self.assertFalse(r["archive_contents_returned"])
        self.assertFalse(r["off_host_copy_accepted"])
        self.assertFalse(r["restored_application_accepted"])
        self.assertNotIn(SECRET.decode(), json.dumps(r))
        self.assertNotIn(self.temporary.name, json.dumps(r))

    def test_empty_dnsmasq_archive_is_required_and_valid(self):
        self.create([("./", None)])
        r = mod.inspect("etc-dnsmasq", self.archive)
        self.assertTrue(r["archive_verified"])
        self.assertEqual(r["regular_file_bytes"], 0)
        self.assertEqual(r["regular_file_count"], 0)
        self.assertEqual(r["sqlite_integrity"], "not_applicable")
        self.assertFalse(r["required_state_present"])

    def test_dnsmasq_unexpected_data_fails_closed(self):
        self.create([("custom.conf", SECRET)])
        with self.assertRaisesRegex(ValueError, "dnsmasq_volume_no_longer_empty"):
            mod.inspect("etc-dnsmasq", self.archive)

    def test_missing_config_and_corrupt_gravity_sqlite_refused(self):
        data = [m for m in self.full() if m[0] != "pihole.toml"]
        self.create(data)
        with self.assertRaisesRegex(ValueError, "missing_required_pihole_state"):
            mod.inspect("etc-pihole", self.archive)
        broken = []
        for name, content in self.full():
            broken.append((name, b"not an sqlite file" * 100
                           if name == "gravity.db" else content))
        self.create(broken)
        with self.assertRaises((sqlite3.Error, ValueError)):
            mod.inspect("etc-pihole", self.archive)

    def test_path_traversal_and_duplicate_and_symlinks_are_refused(self):
        for bad in ("../secret", "/etc/shadow", "nested/../../secret"):
            self.create(self.full() + [(bad, SECRET)])
            with self.subTest(name=bad), self.assertRaisesRegex(
                    ValueError, "unsafe_tar_path"):
                mod.inspect("etc-pihole", self.archive)
        self.create(self.full() + [("pihole.toml", SECRET)])
        with self.assertRaisesRegex(ValueError, "duplicate_archive_path"):
            mod.inspect("etc-pihole", self.archive)
        with tarfile.open(self.archive, "w") as tar:
            marker = tarfile.TarInfo("gravity.db")
            marker.type = tarfile.SYMTYPE
            marker.linkname = "/etc/shadow"
            tar.addfile(marker)
        self.archive.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "unsupported_tar_member_type"):
            mod.inspect("etc-pihole", self.archive)

    def test_wrong_private_archive_ownership_mode_size_fail(self):
        self.create(self.full())
        self.archive.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "unsafe_or_unavailable"):
            mod.inspect("etc-pihole", self.archive)
        self.archive.chmod(0o600)
        bad = self.root / "symlink.tar"
        bad.symlink_to(self.archive)
        with self.assertRaisesRegex(ValueError, "unsafe_or_unavailable"):
            mod.inspect("etc-pihole", bad)
        with self.assertRaisesRegex(ValueError, "unsupported_volume_identity"):
            mod.inspect("made-up-volume", self.archive)


class PiHoleSameStopSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plays = yaml.safe_load(PLAY.read_text())
        cls.play = cls.plays[0]
        cls.tasks = cls.play["tasks"]

    def task(self, prefix):
        return next(t for t in self.tasks if t["name"].startswith(prefix))

    def test_exact_rootful_kvar_and_separate_dns_downtime_approval(self):
        self.assertEqual(len(self.plays), 1)
        self.assertEqual(self.play["hosts"], "npm_proxy_legacy")
        self.assertTrue(self.play["become"])
        self.assertTrue(self.play["gather_facts"])
        checks = str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for expected in ("'kvar.outer.sanctum'", "'root'",
                         "sanctum_pihole_consistent_backup_approved",
                         "sanctum_pihole_dns_interruption_approved",
                         "not ansible_check_mode"):
            self.assertIn(expected, checks)
        self.assertIn("ansible_facts['date_time']['iso8601_basic_short']",
                      self.play["vars"]["pihole_stamp"])
        self.assertNotIn("ansible_date_time", PLAY.read_text())

    def test_preflight_rejects_runtime_drift_before_any_service_stop(self):
        terms = str(self.task("Refuse image drift")["ansible.builtin.assert"]["that"])
        for phrase in ("pihole_expected_image_id", "image_reference",
                       "service_unit.quadlet_source", "container_running",
                       "mounts", "port_mappings"):
            self.assertIn(phrase, terms)
        names = [t["name"] for t in self.tasks]
        self.assertLess(names.index("Refuse image drift or different rootful Pi-hole persistence before downtime"),
                        names.index("Quiesce original Pi-hole for both complete same-stop exports"))

    def test_both_rootful_volumes_exported_while_stopped_with_always_restart(self):
        block = self.task("Quiesce original Pi-hole")
        stops = [t for t in block["block"] if
                 t.get("ansible.builtin.systemd_service", {}).get("state") == "stopped"]
        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0]["ansible.builtin.systemd_service"]["name"], "pihole.service")
        exports = [t for t in block["block"]
                   if t["name"].startswith("Export original stopped rootful")]
        self.assertEqual(len(exports), 2)
        self.assertEqual([e["ansible.builtin.command"]["argv"][3] for e in exports],
                         ["systemd-pihole_etc-pihole", "systemd-pihole_etc-dnsmasq"])
        self.assertTrue(all(e["no_log"] for e in exports))
        always = block["always"]
        self.assertEqual(always[0]["ansible.builtin.systemd_service"]["state"], "started")
        self.assertEqual(always[0]["ansible.builtin.systemd_service"]["name"], "pihole.service")
        self.assertIn("pihole_restarted", str(always))
        self.assertIn("still stopped", str(block))

    def test_private_no_clobber_archives_and_validator_after_restart(self):
        reserve = self.task("Reserve both private volume tar partials")
        self.assertTrue(reserve["no_log"])
        self.assertIn("os.O_EXCL", str(reserve["ansible.builtin.command"]["argv"]))
        stat = self.task("Require both exported archives are private root-owned files")
        self.assertTrue(stat["ansible.builtin.stat"]["follow"] is False)
        guards = str(self.task("Reject wrong type")["ansible.builtin.assert"]["that"])
        for word in ("isreg", "islnk", "pw_name", "mode", "size"):
            self.assertIn(word, guards)
        val = [self.task("Privately verify etc-pihole"),
               self.task("Privately verify configured empty dnsmasq")]
        self.assertTrue(all(t["no_log"] for t in val))
        self.assertIn("pihole-archive-verify.py", self.play["vars"]["pihole_validator"])
        self.assertIn("os.link(", str(self.task("Publish validated etc-pihole")))
        self.assertIn("os.link(", str(self.task("Publish validated dnsmasq")))

    def test_backup_never_touches_others_or_claims_offhost_restore(self):
        text = PLAY.read_text()
        for forbidden in ("scope: user", "linkstack.service",
                          "ansible.builtin.fetch:", "ansible.builtin.slurp:",
                          "podman volume import", "podman volume rm", "podman pull"):
            self.assertNotIn(forbidden, text)
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["off_host_copy_accepted"], False)
        self.assertIs(report["isolated_kvin_pihole_recovery_accepted"], False)
        self.assertIs(report["real_client_dns_filtering_accepted"], False)
        self.assertIs(report["other_kvar_or_kvin_service_changed"], False)
        self.assertIs(report["dns_authority_or_firewall_or_proxy_changed"], False)

    def test_full_services_ci_runs_backup_tests_and_syntax(self):
        wf = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_pihole_consistent_backup.py", wf)
        self.assertIn("ansible/pihole-consistent-backup.yml --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
