"""Kvin LinkStack one-time source-managed loopback candidate staging contract."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/linkstack-kvin-loopback-stage.yml"
QUADLET = ROOT / "ansible/files/sanctum-linkstack-kvin-candidate.container"
DIGEST = ("docker.io/linkstackorg/linkstack@sha256:"
          "b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1")
VOLUME = "sanctum-linkstack-qualified-20261112t105926"
RECOVERY = "sanctum-linkstack-restore-test-20261112t105926"
IMAGE_ID = "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"


class LinkStackCandidateStaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PLAY.read_text()
        cls.plays = yaml.safe_load(cls.raw)
        cls.play = cls.plays[0]
        cls.tasks = cls.play["tasks"]
        cls.source = QUADLET.read_text()

    def task(self, name):
        return next(t for t in self.tasks if t["name"].startswith(name))

    def test_immutable_source_quadlet_is_loopback_only_and_rootless(self):
        q = self.source
        for line in (
            "[Unit]", "[Container]", "[Service]", "[Install]",
            "Image=" + DIGEST,
            "ContainerName=sanctum-linkstack-kvin-candidate",
            "Volume=" + VOLUME + ":/htdocs:Z",
            "PublishPort=127.0.0.1:18081:80/tcp",
            "Sysctl=net.ipv4.ip_unprivileged_port_start=80",
            "NoNewPrivileges=true", "Pull=never",
            "Environment=HTTP_SERVER_NAME=localhost",
            "WantedBy=default.target",
        ):
            self.assertIn(line + "\n", q)
        for forbidden in ("0.0.0.0", "Network=host", "AutoUpdate=registry",
                          "Volume=" + RECOVERY, "Volume=linkstack:", ":U,Z",
                          "PublishPort=80:", "User=root", "UserNS=host",
                          "Privileged=true", "ExecStart="):
            self.assertNotIn(forbidden, q)
        self.assertEqual(q.count("PublishPort="), 1)
        self.assertEqual(q.count("Volume="), 1)
        self.assertEqual(q.count("Sysctl="), 1)
        self.assertNotIn("MYSQL_PASSWORD", q)
        self.assertNotIn("APP_KEY=", q)

    def test_operator_must_approve_new_rootless_kvin_loopback_service(self):
        self.assertEqual(len(self.plays), 1)
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        self.assertTrue(self.play["gather_facts"])
        v = self.play["vars"]
        self.assertEqual(v["linkstack_candidate_port"], 18081)
        self.assertEqual(v["linkstack_candidate_image"], DIGEST)
        self.assertEqual(v["linkstack_candidate_volume"], VOLUME)
        self.assertEqual(v["linkstack_original_restore_volume"], RECOVERY)
        self.assertEqual(v["linkstack_original_image_id"], IMAGE_ID)
        check = str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for expected in (
            "'kvin.outer.sanctum'", "'aarch64'", "'wdc2'",
            "sanctum_linkstack_loopback_candidate_stage_approved",
            "not ansible_check_mode",
            "not (sanctum_linkstack_cutover_approved",
            "not (sanctum_linkstack_offhost_transfer_approved",
            "not (sanctum_linkstack_candidate_private_relabel_chown_approved",
        ):
            self.assertIn(expected, check)
        self.assertNotIn("ansible_date_time", self.raw)

    def test_prior_data_image_and_new_resource_identity_preflight(self):
        names = [t["name"] for t in self.tasks]
        install_idx = names.index(
            "Install only the source-managed loopback candidate Quadlet")
        preflight = (
            "Refuse missing or substituted recovered persistence",
            "Require recovered owned candidate data integrity before any service installation",
            "Require no image drift before staging a persistent Quadlet",
            "Refuse adopting an existing unmanaged candidate Quadlet",
            "Confirm no existing candidate container will be replaced",
            "Refuse touching an already running candidate or similarly named unit",
            "Require entire candidate port unoccupied before binding loopback",
            "Refuse unsafe existing user Quadlet directory",
        )
        for name in preflight:
            self.assertLess(names.index(name), install_idx)
        guard = str(self.task("Require recovered owned candidate data")["ansible.builtin.assert"])
        self.assertIn("sqlite_integrity", guard)
        self.assertIn("configuration_file_present", guard)
        check = str(self.task("Require no image drift")["ansible.builtin.assert"])
        self.assertIn("linkstack_original_image_id", check)
        self.assertIn("Architecture", check)
        port = self.task("Observe any existing listener")
        self.assertEqual(port["ansible.builtin.command"]["argv"][:3],
                         ["ss", "-H", "-ltn"])

    def test_only_new_quadlet_installed_no_existing_service_adopted(self):
        source = self.task("Install only the source-managed")
        opts = source["ansible.builtin.copy"]
        self.assertEqual(opts["src"], "files/sanctum-linkstack-kvin-candidate.container")
        self.assertEqual(opts["mode"], "0644")
        self.assertIs(opts["force"], False)
        assert_new = str(self.task("Require a newly installed")["ansible.builtin.assert"])
        self.assertIn("linkstack_stage_installed.changed", assert_new)
        start = self.task("Start only the newly installed")
        args = start["ansible.builtin.systemd_service"]
        self.assertEqual(args["scope"], "user")
        self.assertEqual(args["state"], "started")
        self.assertIs(args["daemon_reload"], True)
        self.assertIn("user_uid", start["environment"]["XDG_RUNTIME_DIR"])
        self.assertIn("linkstack_candidate_service", args["name"])
        self.assertNotIn("ansible.builtin.systemd_service:\n    name: pihole", self.raw)

    def test_service_identity_and_port_verified_after_start_before_http(self):
        steps = [t["name"] for t in self.tasks]
        self.assertLess(steps.index("Require actual running candidate with exact immutable image and intended named volume"),
                        steps.index("Probe recovered candidate HTTP only from Kvin local loopback"))
        self.assertLess(steps.index("Require published candidate is loopback-only"),
                        steps.index("Probe recovered candidate HTTP only from Kvin local loopback"))
        checks = str(self.task("Require actual running candidate")["ansible.builtin.assert"])
        for phrase in ("Image", "State.Running", "Mounts", "Destination", "linkstack_candidate_volume"):
            self.assertIn(phrase, checks)
        self.assertIn("'127.0.0.1:18081'",
                      str(self.task("Require published candidate")["ansible.builtin.assert"]["that"]))
        http = self.task("Probe recovered candidate HTTP")
        self.assertTrue(http["no_log"])
        u = http["ansible.builtin.uri"]
        self.assertEqual(u["url"], "http://127.0.0.1:18081/")
        self.assertEqual(u["headers"]["Host"], "dir.nexus.sanctum")
        self.assertFalse(u["use_proxy"])
        self.assertEqual(u["status_code"], [200])
        self.assertEqual(u["follow_redirects"], "none")
        self.assertFalse(u["return_content"])

    def test_no_legacy_proxy_cutover_firewall_or_volume_mutations(self):
        for s in ("firewall-cmd", "ansible.posix.firewalld",
                  "ansible.builtin.slurp:", "podman volume import",
                  "podman volume rm", "ansible.builtin.fetch:",
                  "scp", "podman pull", "sysctl -w", "ansible.posix.sysctl",
                  "ansible.builtin.template:"):
            self.assertNotIn(s, self.raw)
        msg = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        for key in ("original_restored_volume_preserved",
                    "original_snapshot_preserved", "host_sysctl_unchanged",
                    "candidate_not_available_on_lan"):
            self.assertIs(msg[key], True)
        for key in ("kvar_linkstack_pihole_or_npm_changed",
                    "yxorp_proxy_or_dns_or_firewall_changed",
                    "real_named_browser_directory_and_admin_accepted",
                    "independent_disaster_recovery_backup_accepted"):
            self.assertIs(msg[key], False)

    def test_workflow_runs_tests_and_ansible_syntax(self):
        workflow = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_kvin_loopback_stage.py", workflow)
        self.assertIn("ansible/linkstack-kvin-loopback-stage.yml --syntax-check",
                      workflow)


if __name__ == "__main__":
    unittest.main()
