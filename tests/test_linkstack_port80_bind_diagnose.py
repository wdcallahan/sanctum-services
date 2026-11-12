"""LinkStack port 80 rootless namespace differential and no-mutation contracts."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/diagnose-linkstack-port80-bind.py"
PLAY = ROOT / "ansible/linkstack-port80-bind-diagnose.yml"
spec = importlib.util.spec_from_file_location("linkport", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SECRET = "SECRET_FROM_APACHE_STDERR_NEVER_RETURN"


class Port80BindDiagnosticTests(unittest.TestCase):
    def test_classifies_bind_permission_only_if_both_markers_present(self):
        message = ("[auth] AH00072: make_sock: could not bind to address"
                   " 0.0.0.0:80 (13)Permission denied " + SECRET).encode()
        s = mod.categories(message)
        self.assertIn("listen_permission_denied", s["error_classes"])
        self.assertIn("apache_listen_socket", s["error_classes"])
        self.assertNotIn(SECRET, json.dumps(s))
        only = mod.categories(b"random Permission denied")
        self.assertNotIn("listen_permission_denied", only["error_classes"])
        self.assertIn("permission", message.decode().lower())

    def test_wrong_host_or_user_fails_before_image_or_podman_access(self):
        def explode(*args, **kwargs):
            self.fail("refused caller attempted an operation")
        for host, user in ((mod.HOST, "root"), ("kvar.outer.sanctum", mod.ACCOUNT)):
            r = mod.collect(host, user, runner=explode)
            self.assertEqual(r["status"], "refused")

    def simulated(self, rootless_override_works=True, occupied=None):
        active = set(occupied or [])
        commands = []
        def run(argv, timeout=18):
            a = tuple(argv)
            commands.append(a)
            if argv[:3] == ["podman", "image", "inspect"]:
                return 0, json.dumps([{
                    "Id": mod.IMAGE_ID, "Architecture": "arm64",
                    "Os": "linux", "Config": {"Env": ["PASSWORD="+SECRET]}
                }]).encode(), b""
            if argv[:2] == ["podman", "run"] and "--detach" in argv:
                active.add(("container", argv[argv.index("--name")+1]))
                return 0, b"", b""
            if argv[:3] in (["podman", "network", "exists"],
                            ["podman", "container", "exists"]):
                return (0 if (argv[1], argv[3]) in active else 1), b"", b""
            if argv[:3] == ["podman", "network", "create"]:
                active.add(("network", mod.NETWORK))
                return 0, b"", b""
            if argv[:3] == ["podman", "network", "inspect"]:
                return 0, json.dumps([{
                    "name": mod.NETWORK, "driver": "bridge",
                    "internal": True, "dns_enabled": False}]).encode(), b""
            if argv[:3] == ["podman", "container", "inspect"]:
                overridden = argv[-1] == mod.NAMES["namespaced_port80"]
                working = overridden and rootless_override_works
                return 0, json.dumps({
                    "Running": working, "ExitCode": 0 if working else 1,
                    "OOMKilled": False}).encode(), b""
            if argv[:2] == ["podman", "exec"]:
                return 0, b"200", b""
            if argv[:2] == ["podman", "logs"]:
                return (0, b"LINKSTACK v\nRunning Apache\n",
                        ("AH00072: make_sock could not bind: "
                         "Permission denied; "+SECRET).encode())
            if argv[:3] == ["podman", "rm", "--force"]:
                active.discard(("container", argv[-1]))
                return 0, b"", b""
            if argv[:3] == ["podman", "network", "rm"]:
                active.discard(("network", argv[-1]))
                return 0, b"", b""
            self.fail("unexpected operation "+str(argv))
        return run, commands, active

    def test_differential_and_cleanup(self):
        runner, commands, active = self.simulated()
        result = mod.collect(mod.HOST, mod.ACCOUNT, runner=runner,
                             sleeper=lambda _: None)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["comparison"],
                         "namespaced_low_port_policy_enables_startup")
        self.assertEqual(result["cases"]["baseline"]["exit_code"], 1)
        self.assertTrue(result["cases"]["namespaced_port80"]["running"])
        self.assertEqual(result["cases"]["namespaced_port80"]["http_status"], 200)
        self.assertTrue(all(result["cleanup"].values()))
        self.assertEqual(active, set())
        self.assertTrue(result["host_sysctl_unchanged"])
        self.assertFalse(result["restored_application_accepted"])
        self.assertNotIn(SECRET, json.dumps(result))
        runs = [x for x in commands if x[:2] == ("podman", "run")]
        self.assertEqual(len(runs), 2)
        self.assertNotIn("--sysctl", runs[0])
        self.assertIn("--sysctl", runs[1])
        self.assertIn(mod.SYSCTL, runs[1])
        self.assertEqual(sum("--sysctl" in a for a in runs), 1)
        for cmd in runs:
            for forbidden in ("--publish", "-p", "--network=host",
                              "--privileged", "--volume", "--cap-add"):
                self.assertNotIn(forbidden, cmd)
        network = next(x for x in commands if x[:3] == ("podman", "network", "create"))
        self.assertIn("--internal", network)
        self.assertIn("--disable-dns", network)

    def test_both_failed_does_not_claim_solution(self):
        runner, _, active = self.simulated(rootless_override_works=False)
        r = mod.collect(mod.HOST, mod.ACCOUNT, runner=runner,
                        sleeper=lambda _: None)
        self.assertEqual(r["comparison"], "both_exit_with_or_without_namespace_override")
        self.assertFalse(r["restored_application_accepted"])
        self.assertEqual(active, set())

    def test_reserved_name_collision_does_not_delete_external_resources(self):
        existing = {("container", mod.NAMES["baseline"])}
        runner, commands, active = self.simulated(occupied=existing)
        r = mod.collect(mod.HOST, mod.ACCOUNT, runner=runner)
        self.assertEqual(r["failure_phase"], "reserved_resource_name_occupied_or_unknown")
        self.assertEqual(active, existing)
        self.assertFalse(any(cmd[:3] == ("podman", "rm", "--force") for cmd in commands))
        self.assertTrue(all(r["cleanup"].values()))

    def test_explicit_kvin_gate_and_single_sanitized_report(self):
        plays = yaml.safe_load(PLAY.read_text())
        self.assertEqual(len(plays), 1)
        play = plays[0]
        self.assertEqual(play["hosts"], "kuma")
        self.assertFalse(play["become"])
        tasks = play["tasks"]
        self.assertEqual(len(tasks), 5)
        checks = str(tasks[0]["ansible.builtin.assert"]["that"])
        for part in ("'kvin.outer.sanctum'", "'aarch64'",
                     "sanctum_linkstack_namespaced_port80_diagnostic_approved",
                     "not ansible_check_mode"):
            self.assertIn(part, checks)
        self.assertTrue(tasks[1]["no_log"])
        self.assertIn("diagnose-linkstack-port80-bind.py",
                      tasks[1]["ansible.builtin.command"]["argv"][2])
        self.assertIn("temporary_network_removed", str(tasks[-1]))
        workflow = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_port80_bind_diagnose.py", workflow)
        self.assertIn("ansible/linkstack-port80-bind-diagnose.yml --syntax-check",
                      workflow)


if __name__ == "__main__":
    unittest.main()
