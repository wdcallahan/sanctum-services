"""Bounded LinkStack image-only versus restored-volume startup classification."""
from pathlib import Path
import importlib.util
import json
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/diagnose-linkstack-offline-startup.py"
PLAY = ROOT / "ansible/linkstack-offline-startup-diagnose.yml"
spec = importlib.util.spec_from_file_location("linkdiag", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SECRET = "SUPERSECRET_CONFIG_VALUE_DO_NOT_LEAK"


class LinkStackStartupDiagnostics(unittest.TestCase):
    def test_wrong_host_or_account_fails_without_any_operations(self):
        with patch.object(mod, "invoke", side_effect=AssertionError("unexpected operation")):
            for host, user in [(mod.HOST, "root"), ("kvar.outer.sanctum", mod.USER),
                               ("kvin.outer.sanctum", "nobody")]:
                self.assertEqual(mod.collect(host, user)["status"], "refused")

    def test_log_labels_exclude_credentials_logs_and_arbitrary_error_text(self):
        logs = ("PHP Fatal error: " + SECRET +
                "\nPermission denied on /htdocs/.env\n"
                "FATAL: database is locked token=" + SECRET).encode()
        self.assertEqual(mod.log_categories(logs),
                         ["permission_denied", "php_error", "sqlite_error"])
        self.assertEqual(mod.log_categories(b"Nothing recognized"), ["unclassified"])
        self.assertEqual(mod.log_categories(b"a" * (mod.MAX_OUTPUT+1)),
                         ["log_unavailable"])
        self.assertNotIn(SECRET, str(mod.log_categories(logs)))

    def test_classify_image_control_vs_restored_mount_separately(self):
        self.assertEqual(
            mod.classify({"image_only": {"status": "observed", "running": True},
                          "imported_copy": {"status": "observed", "running": False}}),
            "restored_data_or_volume_mount_specific_failure")
        self.assertEqual(
            mod.classify({"image_only": {"status": "observed", "running": False},
                          "imported_copy": {"status": "observed", "running": False}}),
            "both_exit_startup_independent_of_restored_data_possible")
        self.assertEqual(mod.classify({}), "incomplete_trials")

    def test_two_case_trial_isolated_no_raw_logs_and_cleanup(self):
        created = set()
        seen = []
        def fake(argv, timeout=20):
            seen.append(tuple(argv))
            if argv[:3] == ["podman", "image", "inspect"]:
                return 0, json.dumps([{
                    "Id": mod.IMAGE_ID, "Architecture": "arm64", "Os": "linux"}]).encode(), b""
            if len(argv) >= 4 and argv[0] == "podman" and argv[2] == "exists":
                return (0 if (argv[1], argv[3]) in created else 1), b"", b""
            if argv[:3] == ["podman", "network", "create"]:
                created.add(("network", mod.NETWORK))
                return 0, b"", b""
            if argv[:3] == ["podman", "network", "inspect"]:
                return 0, json.dumps([{"name": mod.NETWORK, "driver": "bridge",
                                       "internal": True, "dns_enabled": False}]).encode(), b""
            if argv[:3] == ["podman", "volume", "create"]:
                created.add(("volume", mod.VOLUME))
                return 0, b"", b""
            if argv[:3] == ["podman", "volume", "import"]:
                return 0, b"", b""
            if argv[:2] == ["podman", "run"]:
                created.add(("container", argv[argv.index("--name")+1]))
                return 0, b"", b""
            if argv[:3] == ["podman", "container", "inspect"]:
                name = argv[-1]
                state = {"Running": name == mod.CASES["image_only"],
                         "ExitCode": 0 if name == mod.CASES["image_only"] else 1,
                         "OOMKilled": False}
                return 0, json.dumps(state).encode(), b""
            if argv[:2] == ["podman", "exec"]:
                return 0, b"200", b""
            if argv[:2] == ["podman", "logs"]:
                return 0, ("Permission denied " + SECRET).encode(), b""
            if argv[:3] == ["podman", "rm", "--force"]:
                created.discard(("container", argv[-1]))
                return 0, b"", b""
            if argv[:3] == ["podman", "volume", "rm"]:
                created.discard(("volume", argv[-1]))
                return 0, b"", b""
            if argv[:3] == ["podman", "network", "rm"]:
                created.discard(("network", argv[-1]))
                return 0, b"", b""
            self.fail("Unexpected Podman operation " + repr(argv))
        with patch.object(mod, "invoke", side_effect=fake), \
             patch.object(mod, "check_archive", return_value=True), \
             patch.object(mod, "time") as timer:
            timer.sleep.return_value = None
            result = mod.collect(mod.HOST, mod.USER)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["reason_comparison"],
                         "restored_data_or_volume_mount_specific_failure")
        self.assertEqual(result["trials"]["image_only"]["http_status"], 200)
        self.assertFalse(result["trials"]["imported_copy"]["running"])
        self.assertEqual(result["trials"]["imported_copy"]["exit_code"], 1)
        self.assertEqual(result["trials"]["imported_copy"]["log_categories"],
                         ["permission_denied"])
        self.assertNotIn(SECRET, json.dumps(result))
        self.assertTrue(all(result["cleanup"].values()))
        self.assertEqual(created, set())
        for argv in seen:
            self.assertNotIn("--publish", argv)
            self.assertNotIn("--privileged", argv)
            self.assertNotIn("--network=host", argv)
        starts = [a for a in seen if a[:2] == ("podman", "run")]
        self.assertEqual(len(starts), 2)
        self.assertEqual(sum("--volume" in a for a in starts), 1)
        self.assertIn(mod.VOLUME + ":/htdocs", starts[1])
        self.assertNotIn("sanctum-linkstack-restore-test-20261112t105926",
                         repr(seen))
        self.assertIn("--internal", str(seen))
        self.assertIn("--disable-dns", str(seen))

    def test_incomplete_preflight_never_creates_resources(self):
        with patch.object(mod, "check_archive", return_value=False), \
             patch.object(mod, "invoke", return_value=(1, b"", b"")) as inv:
            result = mod.collect(mod.HOST, mod.USER)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["failure_phase"], "source_archive_identity")
        self.assertEqual(result["reason_comparison"], "incomplete_trials")
        self.assertTrue(all(result["cleanup"].values()))
        self.assertFalse(any(c.args[0][:2] == ["podman", "run"] for c in inv.call_args_list))

    def test_playbook_requires_explicit_new_approval_only_kvin(self):
        plays = yaml.safe_load(PLAY.read_text())
        self.assertEqual(len(plays), 1)
        p = plays[0]
        self.assertEqual(p["hosts"], "kuma")
        self.assertFalse(p["become"])
        self.assertTrue(p["gather_facts"])
        self.assertEqual(len(p["tasks"]), 5)
        conditions = str(p["tasks"][0]["ansible.builtin.assert"]["that"])
        self.assertIn("sanctum_linkstack_startup_diagnostic_approved", conditions)
        self.assertIn("inventory_hostname == 'kvin.outer.sanctum'", conditions)
        self.assertIn("ansible_facts['architecture'] == 'aarch64'", conditions)
        self.assertIn("not ansible_check_mode", conditions)
        task = p["tasks"][1]
        self.assertTrue(task["no_log"])
        self.assertIn("diagnose-linkstack-offline-startup.py",
                      task["ansible.builtin.command"]["argv"][2])
        last = str(p["tasks"][-1]["ansible.builtin.assert"]["that"])
        for key in ("temporary_network_removed", "temporary_volume_removed",
                    "image_container_removed", "data_container_removed"):
            self.assertIn(key, last)
        ci = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_offline_startup_diagnose.py", ci)
        self.assertIn("ansible/linkstack-offline-startup-diagnose.yml --syntax-check", ci)


if __name__ == "__main__":
    unittest.main()
