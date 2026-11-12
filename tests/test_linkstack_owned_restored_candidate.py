"""Exact, no-clobber, retained candidate LinkStack ownership-adjusted restore gates."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/linkstack-owned-restored-candidate.yml"
EXPECTED = "docker.io/linkstackorg/linkstack@sha256:b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1"
OLD = "sanctum-linkstack-restore-test-20261112t105926"
NEW = "sanctum-linkstack-qualified-20261112t105926"


class OwnedCandidateContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(PLAY.read_text())[0]
        cls.tasks = cls.play["tasks"]

    def task(self, fragment):
        return next(t for t in self.tasks if fragment in t["name"])

    def test_exact_rootless_host_two_approvals_and_original_restore_distinct(self):
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        self.assertTrue(self.play["gather_facts"])
        vars = self.play["vars"]
        self.assertEqual(vars["linkstack_original_restore_volume"], OLD)
        self.assertEqual(vars["linkstack_candidate_volume"], NEW)
        g = str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for token in ("'kvin.outer.sanctum'", "'wdc2'", "'aarch64'",
                      "sanctum_linkstack_owned_candidate_restore_approved",
                      "sanctum_linkstack_candidate_private_relabel_chown_approved",
                      "not ansible_check_mode", "linkstack_original_restore_volume != linkstack_candidate_volume"):
            self.assertIn(token, g)
        self.assertIn(EXPECTED, g)
        self.assertNotIn("ansible_date_time", PLAY.read_text())

    def test_archive_and_image_verified_before_new_data_creation(self):
        tasks = [x["name"] for x in self.tasks]
        self.assertLess(tasks.index("Require byte-identical private original snapshot before cloning"),
                        tasks.index("Create only new rootless candidate volume for owned restored state"))
        self.assertLess(tasks.index("Require exact original Kvar image content and Linux ARM64"),
                        tasks.index("Create only new rootless candidate volume for owned restored state"))
        archive = str(self.task("Require byte-identical private")["ansible.builtin.assert"]["that"])
        for k in ("stat.checksum", "stat.mode", "stat.pw_name",
                  "stat.size", "stat.isreg", "stat.islnk"):
            self.assertIn(k, archive)
        check = str(self.task("Refuse reuse of any existing candidate")["ansible.builtin.assert"]["that"])
        self.assertIn("linkstack_original_restore_exists.rc == 0", check)
        self.assertIn("[1, 1, 1]", check)
        self.assertEqual(self.play["vars"]["linkstack_source_archive_bytes"], 93845504)

    def test_new_volume_only_import_and_validate_before_ownership_repair(self):
        create = self.task("Create only new rootless candidate volume")
        self.assertEqual(create["ansible.builtin.command"]["argv"],
                         ["podman", "volume", "create", "{{ linkstack_candidate_volume }}"])
        imp = self.task("Import exact verified backup")
        self.assertTrue(imp["no_log"])
        self.assertEqual(imp["ansible.builtin.command"]["argv"][:3],
                         ["podman", "volume", "import"])
        self.assertEqual(imp["ansible.builtin.command"]["argv"][3],
                         "{{ linkstack_candidate_volume }}")
        val = self.task("Privately confirm candidate SQLite")
        self.assertTrue(val["no_log"])
        self.assertIn("restored", val["ansible.builtin.command"]["argv"])
        accept = self.task("Require newly imported candidate")
        self.assertIn("sqlite_integrity", str(accept))

    def test_new_clone_only_u_z_and_namespaced_port_80_without_host_ports(self):
        group = self.task("Boot restored LinkStack with private ownership")
        self.assertIn("always", group)
        tasks = group["block"]
        net = tasks[0]["ansible.builtin.command"]["argv"]
        self.assertEqual(net[:3], ["podman", "network", "create"])
        self.assertIn("--internal", net)
        self.assertIn("--disable-dns", net)
        self.assertIn("bridge", net)
        self.assertIn("dns_enabled", str(tasks[2]["ansible.builtin.assert"]))
        run = next(t for t in tasks if t["name"].startswith("Start disposable"))
        args = run["ansible.builtin.command"]["argv"]
        self.assertTrue(run["no_log"])
        self.assertEqual(args[:2], ["podman", "run"])
        self.assertEqual(args[args.index("--volume") + 1],
                         "{{ linkstack_candidate_volume }}:/htdocs:U,Z")
        self.assertEqual(args[args.index("--sysctl") + 1],
                         "net.ipv4.ip_unprivileged_port_start=80")
        self.assertIn("no-new-privileges", args)
        self.assertIn("{{ linkstack_candidate_network }}", args)
        self.assertIn(EXPECTED, str(self.tasks[0]["ansible.builtin.assert"]["that"]))
        for forbidden in ("--publish", "-p", "--network=host", "--privileged",
                          "{{ linkstack_original_restore_volume }}:/htdocs"):
            self.assertNotIn(forbidden, args)
        self.assertNotIn("sysctl -w", PLAY.read_text())
        self.assertNotIn("ansible.posix.sysctl", PLAY.read_text())
        cleanup = group["always"]
        self.assertEqual(len(cleanup), 2)
        self.assertIn("podman", str(cleanup[0]))
        self.assertIn("network", str(cleanup[1]))
        self.assertTrue(all(x["no_log"] for x in cleanup))
        self.assertTrue(all("when" in x for x in cleanup))

    def test_true_http_with_curl_and_cleanup_required_before_candidate_report(self):
        block = self.task("Boot restored LinkStack")
        names = [x["name"] for x in block["block"]]
        self.assertLess(names.index("Require candidate is actually running before HTTP"),
                        names.index("Check restored LinkStack HTTP only from inside its isolated namespace"))
        http = next(t for t in block["block"] if t["name"].startswith("Check restored"))
        args = http["ansible.builtin.command"]["argv"]
        self.assertIn("curl", args)
        self.assertIn("http://127.0.0.1/", args)
        self.assertIn("Host: dir.nexus.sanctum", args)
        self.assertTrue(http["no_log"])
        self.assertEqual(http["retries"], 12)
        self.assertIn("'200'", str(self.task("Require HTTP 200")["ansible.builtin.assert"]["that"]))
        cleanup = self.task("Require both disposable resources")
        self.assertIn("linkstack_owned_cleanup_container", str(cleanup))
        self.assertIn("linkstack_owned_cleanup_network", str(cleanup))
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["new_candidate_volume_retained"], True)
        self.assertIs(report["original_restore_volume_unchanged"], True)
        self.assertIs(report["original_verified_backup_unchanged"], True)
        self.assertIs(report["production_ports_or_dns_or_proxy_changed"], False)
        self.assertIs(report["real_client_directory_content_or_admin_accepted"], False)

    def test_no_original_volume_removal_or_live_application_changes(self):
        text = PLAY.read_text()
        for forbidden in ("ansible.builtin.systemd_service",
                          "ansible.builtin.template", "podman pull",
                          "ansible.builtin.fetch:", "ansible.builtin.slurp:",
                          "firewall-cmd", "podman volume rm", "scp"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("linkstack:/htdocs:U,Z", text)

    def test_source_ci_tests_and_syntax_checks(self):
        ci = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_owned_restored_candidate.py", ci)
        self.assertIn("ansible/linkstack-owned-restored-candidate.yml --syntax-check", ci)


if __name__ == "__main__":
    unittest.main()
