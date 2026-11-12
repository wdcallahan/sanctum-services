"""Image-only LinkStack startup static readiness and controlled Podman runtime variants."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/diagnose-linkstack-image-runtime.py"
PLAY = ROOT / "ansible/linkstack-image-runtime-diagnose.yml"
spec = importlib.util.spec_from_file_location("runtime", SCRIPT)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
SECRET = "PRIVATE_SENTINEL_MUST_NOT_BE_PRINTED"


def fake_runner(existing_at_start=None, exit_default=False):
    """Fixed fake Podman runtime. No real resource access."""
    existing = set(existing_at_start or ())
    calls = []

    def runner(argv, timeout=20):
        args = tuple(argv)
        calls.append(args)
        if argv[:3] == ["podman", "image", "inspect"]:
            record = {"Id": runtime.IMAGE_ID, "Architecture": "arm64", "Os": "linux",
                      "Config": {"User": "apache:apache",
                                 "Cmd": ["docker-entrypoint.sh"],
                                 "WorkingDir": "/htdocs",
                                 "Env": ["PASSWORD=" + SECRET]}}
            return 0, json.dumps([record]).encode(), b""
        if argv[:2] == ["podman", "run"] and "--rm" in argv:
            if argv[argv.index("--entrypoint")+1] == "/bin/sh":
                return 0, json.dumps({
                    "version_readable": 1, "php_ini_writable": 0,
                    "htdocs_writable": 1, "apache_executable": 1
                }).encode(), b""
            return 0, b"", b""
        if argv[:3] in (["podman", "network", "exists"],
                         ["podman", "container", "exists"]):
            return (0 if (argv[1], argv[3]) in existing else 1), b"", b""
        if argv[:3] == ["podman", "network", "create"]:
            existing.add(("network", runtime.NETWORK))
            return 0, b"", b""
        if argv[:3] == ["podman", "network", "inspect"]:
            return 0, json.dumps([{"name": runtime.NETWORK, "driver": "bridge",
                                   "internal": True, "dns_enabled": False}]).encode(), b""
        if argv[:2] == ["podman", "run"] and "--detach" in argv:
            existing.add(("container", argv[argv.index("--name")+1]))
            return 0, b"", b""
        if argv[:3] == ["podman", "container", "inspect"]:
            is_restricted = argv[-1] == runtime.NAMES["restricted"]
            return 0, json.dumps({
                "Running": not is_restricted and not exit_default,
                "ExitCode": 1 if is_restricted or exit_default else 0,
                "OOMKilled": False
            }).encode(), b""
        if argv[:2] == ["podman", "exec"]:
            return 0, b"200", b""
        if argv[:2] == ["podman", "logs"]:
            log = ("+ ----- +\n| Running Apache |\n"
                   "can't create configuration " + SECRET).encode()
            return 0, log, b""
        if argv[:3] == ["podman", "rm", "--force"]:
            existing.discard(("container", argv[-1]))
            return 0, b"", b""
        if argv[:3] == ["podman", "network", "rm"]:
            existing.discard(("network", argv[-1]))
            return 0, b"", b""
        raise AssertionError("Unexpected command " + repr(argv))
    return runner, calls, existing


class ImageStartupRuntimeDiagnostics(unittest.TestCase):
    def test_wrong_host_or_account_refused_before_any_execution(self):
        with patch.object(runtime, "run", side_effect=AssertionError("no command permitted")):
            for host, account in [(runtime.HOST, "root"),
                                  ("kvar.outer.sanctum", runtime.ACCOUNT),
                                  ("other", "root")]:
                self.assertEqual(runtime.collect(host, account)["status"], "refused")

    def test_error_taxonomy_and_entrypoint_stage_flags_never_echo_raw_logs(self):
        raw = (b"LINKSTACK v\nUpdating Configuration: Apache Base\n"
               b"Running Apache\ncan't create PHP INI because " + SECRET.encode())
        summary = runtime.classification(raw)
        self.assertEqual(summary["error_categories"], ["cannot_create_file"])
        self.assertTrue(summary["version_banner_seen"])
        self.assertTrue(summary["config_update_seen"])
        self.assertTrue(summary["apache_launch_banner_seen"])
        self.assertNotIn(SECRET, json.dumps(summary))

    def test_static_files_and_apache_syntax_are_observed_without_private_bytes(self):
        runner, _, _ = fake_runner()
        with patch.object(runtime, "run", side_effect=runner):
            report = runtime.static_prerequisites()
            syntax = runtime.apache_syntax()
        self.assertEqual(report["status"], "observed")
        self.assertTrue(report["version_readable"])
        self.assertFalse(report["php_ini_writable"])
        self.assertEqual(syntax["status"], "observed")
        self.assertTrue(syntax["syntax_valid"])
        self.assertNotIn(SECRET, json.dumps(report) + json.dumps(syntax))

    def test_two_image_only_cases_isolate_added_no_new_privileges_effect(self):
        runner, calls, existing = fake_runner()
        with patch.object(runtime, "run", side_effect=runner), \
             patch.object(runtime.time, "sleep", return_value=None):
            report = runtime.collect(runtime.HOST, runtime.ACCOUNT)
        self.assertEqual(report["status"], "observed")
        self.assertEqual(report["comparison"], "only_no_new_privileges_variant_exits")
        self.assertEqual(report["cases"]["restricted"]["exit_code"], 1)
        self.assertFalse(report["cases"]["restricted"]["running"])
        self.assertTrue(report["cases"]["podman_default"]["running"])
        self.assertEqual(report["cases"]["podman_default"]["http_status"], 200)
        self.assertEqual(report["cases"]["restricted"]["log"]["error_categories"],
                         ["cannot_create_file"])
        self.assertEqual(report["static_prerequisites"]["php_ini_writable"], False)
        self.assertTrue(all(report["cleanup"].values()))
        self.assertEqual(existing, set())
        self.assertNotIn(SECRET, json.dumps(report))
        starts = [argv for argv in calls if argv[:2] == ("podman", "run")
                  and "--detach" in argv]
        self.assertEqual(len(starts), 2)
        self.assertIn("no-new-privileges", starts[0])
        self.assertNotIn("no-new-privileges", starts[1])
        for argv in starts:
            self.assertNotIn("--volume", argv)
            self.assertNotIn("--publish", argv)
            self.assertNotIn("--privileged", argv)
            self.assertIn(runtime.NETWORK, argv)
        creates = [argv for argv in calls
                   if argv[:3] == ("podman", "network", "create")]
        self.assertEqual(len(creates), 1)
        self.assertIn("--internal", creates[0])
        self.assertIn("--disable-dns", creates[0])

    def test_both_exit_is_not_falsely_accepted_as_restored_application(self):
        runner, _, _ = fake_runner(exit_default=True)
        with patch.object(runtime, "run", side_effect=runner), \
             patch.object(runtime.time, "sleep", return_value=None):
            report = runtime.collect(runtime.HOST, runtime.ACCOUNT)
        self.assertEqual(report["comparison"], "both_exit_common_image_startup")
        self.assertFalse(report["application_recovery_accepted"])
        self.assertTrue(report["original_saved_volumes_unchanged"])
        self.assertTrue(report["kvar_and_production_untouched"])

    def test_refuse_occupied_identity_without_removing_existing_resource(self):
        # The reserved container name is occupied before start.
        prior = {("container", runtime.NAMES["restricted"])}
        runner, calls, existing = fake_runner(existing_at_start=prior)
        with patch.object(runtime, "run", side_effect=runner):
            report = runtime.collect(runtime.HOST, runtime.ACCOUNT)
        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["failure_phase"], "reserved_container_identity_occupied")
        self.assertEqual(existing, prior)
        self.assertFalse(any(argv[:3] == ("podman", "rm", "--force") for argv in calls))
        self.assertFalse(any(argv[:3] == ("podman", "network", "rm") for argv in calls))
        self.assertTrue(all(report["cleanup"].values()))

    def test_source_playbook_and_ci_gate(self):
        plays = yaml.safe_load(PLAY.read_text())
        self.assertEqual(len(plays), 1)
        p = plays[0]
        self.assertEqual(p["hosts"], "kuma")
        self.assertFalse(p["become"])
        self.assertTrue(p["gather_facts"])
        self.assertEqual(len(p["tasks"]), 5)
        conditions = str(p["tasks"][0]["ansible.builtin.assert"]["that"])
        for expected in ("'kvin.outer.sanctum'", "'wdc2'", "'aarch64'",
                         "sanctum_linkstack_image_runtime_diagnostic_approved",
                         "not ansible_check_mode"):
            self.assertIn(expected, conditions)
        job = p["tasks"][1]
        self.assertTrue(job["no_log"])
        self.assertTrue(job["changed_when"])
        self.assertIn("diagnose-linkstack-image-runtime.py",
                      job["ansible.builtin.command"]["argv"][2])
        last = str(p["tasks"][-1]["ansible.builtin.assert"]["that"])
        for field in ("restricted_container_removed", "default_container_removed",
                      "internal_network_removed"):
            self.assertIn(field, last)
        workflow = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_image_runtime_diagnose.py", workflow)
        self.assertIn("ansible/linkstack-image-runtime-diagnose.yml --syntax-check", workflow)


if __name__ == "__main__":
    unittest.main()
