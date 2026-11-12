"""Kvar/Kvin backup readiness: metadata, no mutation, no config-value leaks."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "readiness", ROOT / "tools/observe-survivor-backup-readiness.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SENTINEL = "CREDENTIAL_VALUE_MUST_NEVER_APPEAR"


class SurvivorBackupReadiness(unittest.TestCase):
    def test_private_quadlet_policy_rejects_secret_values_in_output(self):
        with tempfile.TemporaryDirectory() as d:
            unit = Path(d) / "linkstack.container"
            unit.write_text(
                "[Container]\nImage=docker.io/linkstackorg/linkstack:latest\n"
                "AutoUpdate=registry\nPull=missing\n"
                "Environment=PASSWORD=" + SENTINEL + "\n"
                "PodmanArgs=--label=io.containers.autoupdate=registry\n"
                "Volume=linkstack:/htdocs\n"
            )
            with patch("pwd.getpwnam", return_value=SimpleNamespace(pw_uid=os.getuid())):
                data = mod.unit_policy(str(unit), "docker.io/linkstackorg/linkstack:latest",
                                       "wdc2")
            self.assertEqual(data["status"], "observed")
            self.assertEqual(data["quadlet_auto_update"], "registry")
            self.assertEqual(data["quadlet_pull_policy"], "missing")
            self.assertTrue(data["extra_autoupdate_label_present"])
            self.assertFalse(data["credential_values_returned"])
            self.assertNotIn(SENTINEL, json.dumps(data))
            with patch("pwd.getpwnam", return_value=SimpleNamespace(pw_uid=os.getuid())):
                wrong = mod.unit_policy(str(unit), "docker.io/pihole/pihole:latest", "wdc2")
            self.assertEqual(wrong["status"], "partial")
            self.assertEqual(wrong["reason"], "quadlet_image_contract_drift")

    def test_disallowed_symlink_and_duplicate_policy_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            real = Path(d) / "pihole.container"
            real.write_text("[Container]\nImage=docker.io/pihole/pihole:latest\n"
                            "AutoUpdate=registry\nAutoUpdate=local\n")
            link = Path(d) / "alias.container"
            link.symlink_to(real)
            with patch("pwd.getpwnam", return_value=SimpleNamespace(pw_uid=os.getuid())):
                r = mod.unit_policy(str(link), "docker.io/pihole/pihole:latest", "root")
                d = mod.unit_policy(str(real), "docker.io/pihole/pihole:latest", "root")
            self.assertEqual(r["reason"], "unexpected_unit_file")
            self.assertEqual(d["reason"], "duplicate_update_directive")

    def test_exact_volume_space_without_disclosing_mountpoint(self):
        with tempfile.TemporaryDirectory() as parent:
            vol = Path(parent) / "systemd-pihole_etc-pihole" / "_data"
            vol.mkdir(parents=True)
            out = mod.source_volume_space(str(vol), "systemd-pihole_etc-pihole")
            self.assertEqual(out["status"], "observed")
            self.assertGreater(out["available_bytes"], 0)
            self.assertNotIn(str(vol), json.dumps(out))
            self.assertEqual(mod.source_volume_space(str(vol), "linkstack")["status"],
                             "unknown")

    def test_kvar_rootful_update_and_free_space_both_observed(self):
        with tempfile.TemporaryDirectory() as parent:
            vol = Path(parent) / "systemd-pihole_etc-pihole" / "_data"
            vol.mkdir(parents=True)
            commands = []
            def runner(args):
                commands.append(args)
                if args[:2] == ["systemctl", "show"]:
                    return "LoadState=loaded\nActiveState=active\nUnitFileState=enabled\n"
                if args[:3] == ["podman", "volume", "inspect"]:
                    return str(vol)
                self.fail("Unapproved command " + repr(args))
            def quadlet(*args):
                self.assertEqual(args[0], "/etc/containers/systemd/pihole.container")
                return {"status": "observed", "quadlet_auto_update": "registry",
                        "source_image_matches_running_tag": True}
            r = mod.collect("pihole", "kvar.outer.sanctum", "root",
                            run=runner, quadlet=quadlet)
            self.assertEqual(r["status"], "observed")
            self.assertFalse(r["automatic_update_cause_proven"])
            self.assertFalse(r["application_interrupted"])
            self.assertFalse(r["data_exported"])
            self.assertFalse(r["backup_or_restore_accepted"])
            self.assertEqual(len(commands), 2)
            self.assertFalse(any("--user" in c for c in commands))
            self.assertNotIn(str(vol), json.dumps(r))

    def test_kvin_capacity_is_minimum_for_staging_not_restore_acceptance(self):
        home = mod.BASELINE_REGULAR_BYTES * 4
        def roomy(path):
            return {"status": "observed",
                    "available_bytes": home if path == "/home/wdc2" else 0}
        r = mod.collect("kvin-storage", "kvin.outer.sanctum", "wdc2",
                        run=lambda _: self.fail("No Podman needed for Kvin capacity"),
                        space=roomy)
        self.assertEqual(r["status"], "observed")
        self.assertTrue(r["home_staging_headroom_established"])
        self.assertFalse(r["recovery_destination_independence_accepted"])
        self.assertFalse(r["backup_or_restore_accepted"])
        small = mod.collect("kvin-storage", "kvin.outer.sanctum", "wdc2",
                            space=lambda _: {"status": "observed", "available_bytes": 12})
        self.assertEqual(small["status"], "partial")
        self.assertFalse(small["home_staging_headroom_established"])

    def test_unknown_timer_preserves_partial_even_when_volume_is_healthy(self):
        with tempfile.TemporaryDirectory() as parent:
            vol = Path(parent) / "linkstack" / "_data"
            vol.mkdir(parents=True)
            result = mod.collect(
                "linkstack", "kvar.outer.sanctum", "wdc2",
                run=lambda argv: str(vol) if argv[0] == "podman" else None,
                quadlet=lambda *_: {"status": "observed"})
            self.assertEqual(result["status"], "partial")
            self.assertEqual(result["podman_auto_update_timer"]["status"], "unknown")

    def test_wrong_host_or_privilege_refuses_before_read(self):
        def fail(*args):
            self.fail("Refused preflight must not touch host")
        for svc, host, user in [
            ("linkstack", "kvin.outer.sanctum", "wdc2"),
            ("pihole", "kvar.outer.sanctum", "wdc2"),
            ("kvin-storage", "kvar.outer.sanctum", "wdc2"),
            ("unknown", "kvar.outer.sanctum", "root")]:
            result = mod.collect(svc, host, user, run=fail, quadlet=fail, space=fail)
            self.assertEqual(result["status"], "refused")

    def test_three_scoped_read_only_plays_are_source_qualified(self):
        plays = yaml.safe_load((ROOT / "ansible/kvar-survivor-backup-readiness.yml").read_text())
        self.assertEqual([p["hosts"] for p in plays],
                         ["npm_proxy_legacy", "npm_proxy_legacy", "kuma"])
        self.assertEqual([p["become"] for p in plays], [False, True, False])
        for p in plays:
            self.assertEqual(len(p["tasks"]), 4)
            raw = p["tasks"][1]
            self.assertTrue(raw["no_log"])
            self.assertIs(raw["changed_when"], False)
            self.assertIn("observe-survivor-backup-readiness.py",
                          raw["ansible.builtin.command"]["argv"][2])
            for t in p["tasks"]:
                for key in ("ansible.builtin.copy", "ansible.builtin.shell",
                            "ansible.builtin.file", "ansible.builtin.systemd_service",
                            "ansible.builtin.service"):
                    self.assertNotIn(key, t)
        wf = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_kvar_survivor_backup_readiness.py", wf)
        self.assertIn("ansible/kvar-survivor-backup-readiness.yml --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
