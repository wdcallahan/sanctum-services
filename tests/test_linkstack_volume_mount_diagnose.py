"""Isolated cloned-volume differential: port 80, SELinux :Z, and :U,Z safety."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/diagnose-linkstack-volume-mount.py"
PLAYBOOK = ROOT / "ansible/linkstack-volume-mount-diagnose.yml"
spec = importlib.util.spec_from_file_location("mountprobe", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SECRET = "PRIVATE_CONFIG_VALUE_MUST_NEVER_APPEAR"


def fake_runtime(occupied=None):
    created = {("volume", mod.ACCEPTED_VOLUME)} | set(occupied or ())
    commands = []
    def runner(args, timeout=25):
        commands.append(tuple(args))
        if args[:3] in (["podman", "network", "exists"],
                        ["podman", "volume", "exists"],
                        ["podman", "container", "exists"]):
            return (0 if (args[1], args[3]) in created else 1), b"", b""
        if args[:3] == ["podman", "network", "create"]:
            created.add(("network", mod.NETWORK))
            return 0, b"", b""
        if args[:3] == ["podman", "network", "inspect"]:
            return 0, json.dumps([{"name": mod.NETWORK, "driver": "bridge",
                                   "internal": True, "dns_enabled": False}]).encode(), b""
        if args[:3] == ["podman", "volume", "create"]:
            created.add(("volume", mod.VOLUME))
            return 0, b"", b""
        if args[:3] == ["podman", "volume", "import"]:
            return 0, b"", b""
        if args[:3] == ["podman", "rm", "--force"]:
            created.discard(("container", args[-1]))
            return 0, b"", b""
        if args[:3] == ["podman", "volume", "rm"]:
            created.discard(("volume", args[-1]))
            return 0, b"", b""
        if args[:3] == ["podman", "network", "rm"]:
            created.discard(("network", args[-1]))
            return 0, b"", b""
        raise AssertionError("unapproved diagnostic operation " + repr(args))
    return runner, commands, created


class LinkStackMountedVolumeDiagnosis(unittest.TestCase):
    def test_privilege_or_host_mismatch_refuses_before_any_call(self):
        with patch.object(mod, "invoke", side_effect=AssertionError("unexpected operation")):
            for host, user in ((mod.HOST, "root"), ("kvar.outer.sanctum", mod.ACCOUNT)):
                self.assertEqual(mod.collect(host, user)["status"], "refused")

    def test_log_classifier_shows_known_categories_never_private_data(self):
        raw = ("PHP Fatal error: " + SECRET +
               " sqlite database is locked; Permission denied on /htdocs/.env").encode()
        result = mod.summarize_log(b"LINKSTACK v\nRunning Apache", raw)
        self.assertIn("sqlite_error", result["error_categories"])
        self.assertIn("php_fatal", result["error_categories"])
        self.assertIn("permission_denied", result["error_categories"])
        self.assertTrue(result["stderr_present"])
        self.assertTrue(result["apache_launch_reached"])
        self.assertNotIn(SECRET, json.dumps(result))
        self.assertEqual(mod.summarize_log(b"", b"")["error_categories"],
                         ["unclassified"])

    def test_differential_classification_distinguishes_relabel_and_ownership(self):
        mk = lambda running: {"status": "observed", "running": running,
                              "http_status": 200 if running else None}
        base = {"image_only": mk(True), "plain": mk(False),
                "relabel": mk(False), "ownership": mk(False)}
        self.assertEqual(mod.comparison(base), "restored_data_startup_still_unresolved")
        base["relabel"] = mk(True)
        self.assertEqual(mod.comparison(base), "private_selinux_relabel_restores_http")
        base["relabel"] = mk(False)
        base["ownership"] = mk(True)
        self.assertEqual(mod.comparison(base),
                         "ownership_repair_after_relabel_restores_http")
        base["plain"] = mk(True)
        self.assertEqual(mod.comparison(base), "unmodified_clone_serves_http")
        base["image_only"] = mk(False)
        self.assertEqual(mod.comparison(base), "image_only_control_not_accepted")

    def test_run_case_has_exact_sysctl_and_mutates_only_disposable_clone(self):
        commands = []
        def fake(args, timeout=25):
            commands.append(args)
            if args[:2] == ["podman", "run"]:
                return 0, b"", b""
            if args[:3] == ["podman", "container", "inspect"]:
                return 0, json.dumps({"Running": True, "ExitCode": 0,
                                      "OOMKilled": False}).encode(), b""
            if args[:2] == ["podman", "exec"]:
                return 0, b"200", b""
            if args[:2] == ["podman", "logs"]:
                return 0, b"Running Apache", b""
            self.fail("Unexpected command " + repr(args))
        with patch.object(mod, "invoke", side_effect=fake), \
             patch.object(mod.time, "sleep", return_value=None):
            for label in mod.CASES:
                result = mod.run_case(label, mod.NETWORK)
                self.assertEqual(result["http_status"], 200)
        run = [x for x in commands if x[:2] == ["podman", "run"]]
        self.assertEqual(len(run), 4)
        for args in run:
            self.assertIn("--sysctl", args)
            self.assertIn(mod.SYSCTL, args)
            self.assertIn(mod.NETWORK, args)
            self.assertIn("no-new-privileges", args)
            for forbidden in ("--publish", "--privileged", "--cap-add",
                              "--network=host", mod.ACCEPTED_VOLUME):
                self.assertNotIn(forbidden, str(args))
        self.assertNotIn("--volume", run[0])
        self.assertEqual(run[1][run[1].index("--volume")+1],
                         mod.VOLUME + ":/htdocs")
        self.assertEqual(run[2][run[2].index("--volume")+1],
                         mod.VOLUME + ":/htdocs:Z")
        self.assertEqual(run[3][run[3].index("--volume")+1],
                         mod.VOLUME + ":/htdocs:U,Z")

    def test_private_cloned_metadata_has_no_file_content_or_absolute_path(self):
        with tempfile.TemporaryDirectory() as parent:
            volume = Path(parent) / mod.VOLUME / "_data"
            (volume / "database").mkdir(parents=True)
            (volume / ".env").write_text(SECRET)
            (volume / "version.json").write_text(SECRET)
            (volume / "database" / "database.sqlite").write_text(SECRET)
            with patch.object(mod, "invoke", return_value=(0, str(volume).encode(), b"")):
                result = mod.volume_markers()
            self.assertEqual(result["status"], "observed")
            self.assertEqual(result["markers"][".env"]["kind"], "regular")
            self.assertEqual(result["markers"]["database"]["kind"], "directory")
            self.assertNotIn(SECRET, json.dumps(result))
            self.assertNotIn(parent, json.dumps(result))

    def test_cloned_only_cleanup_success_and_no_accepted_volume_mutation(self):
        fake, commands, active = fake_runtime()
        stages = []
        def trial(label, network):
            self.assertEqual(network, mod.NETWORK)
            stages.append(label)
            active.add(("container", mod.CASES[label]))
            if label == "plain":
                return {"status": "observed", "running": False, "http_status": None}
            return {"status": "observed", "running": True, "http_status": 200}
        def metadata():
            return {"status": "observed", "markers": {}}
        with patch.object(mod, "invoke", side_effect=fake), \
             patch.object(mod, "exact_archive", return_value=True), \
             patch.object(mod, "exact_image", return_value=True), \
             patch.object(mod, "volume_markers", side_effect=metadata), \
             patch.object(mod, "run_case", side_effect=trial):
            result = mod.collect(mod.HOST, mod.ACCOUNT)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["comparison"], "private_selinux_relabel_restores_http")
        self.assertEqual(stages, ["image_only", "plain", "relabel"])
        self.assertEqual(result["cases"]["ownership"]["status"],
                         "skipped_prior_case_served_http")
        # No :U recursive chown when :Z alone is sufficient.
        self.assertEqual(active, {("volume", mod.ACCEPTED_VOLUME)})
        self.assertTrue(all(result["cleanup"].values()))
        self.assertTrue(result["source_archive_unchanged"])
        self.assertTrue(result["accepted_restore_volume_unchanged"])
        self.assertFalse(result["restored_application_accepted"])
        self.assertNotIn(mod.ACCEPTED_VOLUME,
                         repr([x for x in commands if x[2] in ("rm", "import", "create")
                               if len(x) >= 3]))

    def test_all_stages_run_only_when_cloned_data_needs_ownership_repair(self):
        fake, commands, active = fake_runtime()
        stages = []
        def trial(label, network):
            stages.append(label)
            active.add(("container", mod.CASES[label]))
            working = label in ("image_only", "ownership")
            return {"status": "observed", "running": working,
                    "http_status": 200 if working else None}
        with patch.object(mod, "invoke", side_effect=fake), \
             patch.object(mod, "exact_archive", return_value=True), \
             patch.object(mod, "exact_image", return_value=True), \
             patch.object(mod, "volume_markers",
                          return_value={"status": "observed", "markers": {}}), \
             patch.object(mod, "run_case", side_effect=trial):
            report = mod.collect(mod.HOST, mod.ACCOUNT)
        self.assertEqual(report["status"], "observed")
        self.assertEqual(stages, list(mod.CASES))
        self.assertEqual(report["comparison"],
                         "ownership_repair_after_relabel_restores_http")
        self.assertTrue(all(report["cleanup"].values()))
        self.assertEqual(active, {("volume", mod.ACCEPTED_VOLUME)})

    def test_reserved_names_collision_does_not_delete_others(self):
        occupied = {("container", mod.CASES["plain"])}
        fake, commands, active = fake_runtime(occupied)
        with patch.object(mod, "invoke", side_effect=fake), \
             patch.object(mod, "exact_archive", return_value=True), \
             patch.object(mod, "exact_image", return_value=True):
            result = mod.collect(mod.HOST, mod.ACCOUNT)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["failure_phase"],
                         "temporary_name_already_used_or_unavailable")
        self.assertEqual(active, occupied | {("volume", mod.ACCEPTED_VOLUME)})
        self.assertFalse(any(a[:3] == ("podman", "rm", "--force") for a in commands))
        self.assertTrue(all(result["cleanup"].values()))

    def test_ansible_scope_and_two_approvals_and_ci(self):
        plays = yaml.safe_load(PLAYBOOK.read_text())
        self.assertEqual(len(plays), 1)
        p = plays[0]
        self.assertEqual(p["hosts"], "kuma")
        self.assertFalse(p["become"])
        self.assertEqual(len(p["tasks"]), 5)
        conditions = str(p["tasks"][0]["ansible.builtin.assert"]["that"])
        for s in ("'kvin.outer.sanctum'", "'wdc2'", "'aarch64'",
                  "sanctum_linkstack_clone_mount_diagnostic_approved",
                  "sanctum_linkstack_disposable_relabel_chown_approved",
                  "not ansible_check_mode"):
            self.assertIn(s, conditions)
        command = p["tasks"][1]
        self.assertTrue(command["no_log"])
        self.assertIn("diagnose-linkstack-volume-mount.py",
                      command["ansible.builtin.command"]["argv"][2])
        self.assertIn("clone_volume_removed", str(p["tasks"][-1]))
        wf = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_volume_mount_diagnose.py", wf)
        self.assertIn("ansible/linkstack-volume-mount-diagnose.yml --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
