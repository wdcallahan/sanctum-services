"""Read-only source proof for Kvar LinkStack and Pi-hole recovery discovery."""
import importlib.util
import json
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "survivor", ROOT / "tools/observe-kvar-survivors.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IMAGE_ID = "a" * 64
SENTINEL = "PRIVATE_SENTINEL_DO_NOT_EMIT"


def observation_runner(service, account="wdc2", bad_mount=False):
    calls = []
    def runner(argv):
        calls.append(argv)
        if argv[:3] == ["podman", "container", "inspect"]:
            data = {
                "name": service,
                "image_name": "docker.io/example/" + service + ":1.2.3",
                "image_id": IMAGE_ID,
                "running": True,
                "ports": {"80/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8081"}]},
                "mounts": [{"Destination": "/htdocs" if service == "linkstack" else "/etc/pihole",
                            "Type": "volume", "Name": ("linkstack" if service == "linkstack"
                                                         else ("secret@" + SENTINEL if bad_mount else "pihole")),
                            "RW": True, "Source": SENTINEL}],
            }
            return json.dumps(data)
        if argv[:3] == ["podman", "image", "inspect"]:
            return json.dumps({
                "id": IMAGE_ID, "digest": "sha256:" + "b" * 64,
                "repo_digests": ["docker.io/example/" + service + "@sha256:" + "b" * 64],
                "os": "linux", "arch": "arm64", "Labels": {"PASSWORD": SENTINEL}
            })
        if argv[0] == "systemctl":
            return ("\n".join([
                "LoadState=loaded", "ActiveState=active", "UnitFileState=enabled",
                "SourcePath=" + ("/home/wdc2/.config/containers/systemd/linkstack.container"
                                 if service == "linkstack" else "/etc/containers/systemd/pihole.container"),
            ]) + "\n")
        raise AssertionError("Unexpected command " + str(argv))
    return runner, calls


class KvarSurvivors(unittest.TestCase):
    def test_scoped_rootless_identity_and_no_private_material(self):
        run, commands = observation_runner("linkstack")
        r = module.collect("linkstack", "kvar.outer.sanctum", "wdc2", runner=run)
        self.assertEqual(r["status"], "observed")
        self.assertTrue(r["container_running"])
        self.assertEqual(r["mounts"][0]["volume_name"], "linkstack")
        self.assertEqual(r["image_platform"], "linux/arm64")
        self.assertEqual(len(r["repo_digests"]), 1)
        self.assertTrue(r["service_unit"]["quadlet_source"].endswith("linkstack.container"))
        self.assertNotIn(SENTINEL, json.dumps(r))
        self.assertFalse(r["backup_restore_accepted"])
        self.assertFalse(r["host_or_app_mutation_performed"])
        self.assertEqual([c[0] for c in commands], ["podman", "podman", "systemctl"])
        self.assertEqual(commands[-1][1], "--user")
        self.assertTrue(all("inspect" in c for c in commands if c[0] == "podman"))

    def test_rootful_namespace_and_unknown_secrets_fail_closed(self):
        run, commands = observation_runner("pihole", account="root", bad_mount=True)
        result = module.collect("pihole", "kvar.outer.sanctum", "root", runner=run)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["reason"], "bounded_container_metadata_unavailable")
        self.assertNotIn(SENTINEL, json.dumps(result))
        self.assertEqual([c[0] for c in commands], ["podman"])

    def test_rootful_valid_metadata_cannot_read_application_data(self):
        run, commands = observation_runner("pihole", account="root")
        result = module.collect("pihole", "kvar.outer.sanctum", "root", runner=run)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["service_unit"]["quadlet_source"],
                         "/etc/containers/systemd/pihole.container")
        self.assertEqual(commands[-1][0], "systemctl")
        self.assertNotIn("--user", commands[-1])
        self.assertFalse(result["data_or_credential_contents_read"])

    def test_image_id_failure_retries_local_tag_only_when_id_matches(self):
        run, calls = observation_runner("linkstack")
        def fallback(argv):
            if argv[:3] == ["podman", "image", "inspect"] and argv[-1] == IMAGE_ID:
                return None
            return run(argv)
        r = module.collect("linkstack", "kvar.outer.sanctum", "wdc2", runner=fallback)
        self.assertEqual(r["status"], "observed")
        self.assertEqual(r["image_probe"]["attempts"], [
            {"selector": "container_image_id", "status": "command_unavailable"},
            {"selector": "local_image_reference", "status": "matched_container_image"}])
        self.assertEqual(calls[-2][0], "podman")
        self.assertTrue(calls[-2][-1].endswith("linkstack:1.2.3"))

    def test_newer_local_latest_tag_must_not_pin_running_image(self):
        run, calls = observation_runner("linkstack")
        def changed_image(argv):
            if argv[:3] == ["podman", "image", "inspect"] and argv[-1] == IMAGE_ID:
                return None
            if argv[:3] == ["podman", "image", "inspect"]:
                d = json.loads(run(argv))
                d["id"] = "c" * 64
                return json.dumps(d)
            return run(argv)
        r = module.collect("linkstack", "kvar.outer.sanctum", "wdc2", runner=changed_image)
        self.assertEqual(r["status"], "partial")
        self.assertEqual(r["image_probe"]["attempts"][-1]["status"], "different_local_image")
        self.assertFalse(r["image_probe"]["pullable_digest_known"])
        self.assertNotIn("repo_digests", r)

    def test_missing_repo_digest_preserves_partial_without_inventing_pull_ref(self):
        run, _ = observation_runner("pihole")
        def no_remote_digest(argv):
            raw = run(argv)
            if argv[:3] == ["podman", "image", "inspect"]:
                d = json.loads(raw)
                d["repo_digests"] = []
                return json.dumps(d)
            return raw
        r = module.collect("pihole", "kvar.outer.sanctum", "root", runner=no_remote_digest)
        self.assertEqual(r["status"], "partial")
        self.assertEqual(r["image_probe"]["attempts"][0]["status"], "matched_container_image")
        self.assertFalse(r["image_probe"]["pullable_digest_known"])
        self.assertEqual(r["repo_digests"], [])
        self.assertEqual(r["image_platform"], "linux/arm64")

    def test_image_inspection_output_invalid_does_not_leak_raw_data(self):
        run, _ = observation_runner("linkstack")
        def invalid(argv):
            if argv[:3] == ["podman", "image", "inspect"]:
                return SENTINEL
            return run(argv)
        r = module.collect("linkstack", "kvar.outer.sanctum", "wdc2", runner=invalid)
        self.assertEqual(r["status"], "partial")
        self.assertNotIn(SENTINEL, json.dumps(r))
        self.assertEqual(r["image_probe"]["attempts"][0]["status"], "invalid_output")

    def test_wrong_host_or_account_refuses_before_query(self):
        def forbidden(argv):
            self.fail("Refused selection must not run host commands")
        for name, host, account in [
            ("linkstack", "kvin.outer.sanctum", "wdc2"),
            ("linkstack", "kvar.outer.sanctum", "root"),
            ("pihole", "kvar.outer.sanctum", "wdc2"),
            ("unknown", "kvar.outer.sanctum", "root"),
        ]:
            r = module.collect(name, host, account, runner=forbidden)
            self.assertEqual(r["status"], "refused")

    def test_transport_unavailable_does_not_invent_an_empty_container(self):
        r = module.collect("linkstack", "kvar.outer.sanctum",
                           "wdc2", runner=lambda _: None)
        self.assertEqual(r["status"], "partial")
        self.assertNotIn("mounts", r)
        self.assertFalse(r["backup_restore_accepted"])

    def test_two_play_contract_uses_existing_legacy_inventory_only(self):
        plays = yaml.safe_load((ROOT / "ansible/kvar-survivors-source.yml").read_text())
        self.assertEqual(len(plays), 2)
        self.assertEqual([p["hosts"] for p in plays],
                         ["npm_proxy_legacy", "npm_proxy_legacy"])
        self.assertEqual([p["become"] for p in plays], [False, True])
        for play, service in zip(plays, ("linkstack", "pihole")):
            self.assertFalse(play["gather_facts"])
            tasks = play["tasks"]
            self.assertEqual(len(tasks), 4)
            self.assertIn("kvar.outer.sanctum",
                          str(tasks[0]["ansible.builtin.assert"]["that"]))
            command = tasks[1]
            self.assertTrue(command["no_log"])
            self.assertIs(command["changed_when"], False)
            self.assertIn("observe-kvar-survivors.py",
                          command["ansible.builtin.command"]["argv"][2])
            self.assertEqual(command["ansible.builtin.command"]["argv"][-1], service)
            for task in tasks:
                for mutation in (
                    "ansible.builtin.copy", "ansible.builtin.file",
                    "ansible.builtin.template", "ansible.builtin.shell",
                    "ansible.builtin.systemd_service", "ansible.builtin.service",
                ):
                    self.assertNotIn(mutation, task)

    def test_ci_must_run_full_source_checks_and_syntax(self):
        ci = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_kvar_survivors_source.py", ci)
        self.assertIn("ansible/kvar-survivors-source.yml --syntax-check", ci)


if __name__ == "__main__":
    unittest.main()
