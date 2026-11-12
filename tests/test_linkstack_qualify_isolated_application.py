"""LinkStack pinned image and disposable internal-only network restored-app contract."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT / "ansible/linkstack-qualify-isolated-application.yml"
IMAGES = ROOT / "data/container-image-candidates.yml"
EXPECTED = ("docker.io/linkstackorg/linkstack@sha256:"
            "b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1")
SOURCE_IMAGE_ID = "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"


class LinkStackRestoredAppTrial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plays = yaml.safe_load(PLAY.read_text())
        cls.play = cls.plays[0]
        cls.tasks = cls.play["tasks"]
        cls.candidate = yaml.safe_load(IMAGES.read_text())["linkstack_candidate"]

    def task(self, prefix):
        return next(t for t in self.tasks if t["name"].startswith(prefix))

    def test_pinned_source_registry_candidate_is_arm64_and_original_image(self):
        self.assertEqual(self.candidate["image"], EXPECTED)
        self.assertEqual(self.candidate["platform"], "linux/arm64")
        self.assertEqual(self.candidate["status"], "registry_only")
        self.assertEqual(self.candidate["source_running_image_id"], SOURCE_IMAGE_ID)
        self.assertEqual(self.candidate["tag_at_lookup"], "latest")

    def test_exact_rootless_kvin_and_separate_approvals(self):
        self.assertEqual(len(self.plays), 1)
        self.assertEqual(self.play["hosts"], "kuma")
        self.assertFalse(self.play["become"])
        self.assertTrue(self.play["gather_facts"])
        self.assertEqual(self.play["vars_files"], ["../data/container-image-candidates.yml"])
        g = self.tasks[0]["ansible.builtin.assert"]["that"]
        for required in [
            "inventory_hostname == 'kvin.outer.sanctum'",
            "ansible_facts['fqdn'] == inventory_hostname",
            "ansible_facts['architecture'] == 'aarch64'",
            "ansible_facts['user_id'] == 'wdc2'",
            "not ansible_check_mode",
            "sanctum_linkstack_image_qualification_approved | default(false) | bool",
            "sanctum_linkstack_offline_application_trial_approved | default(false) | bool",
            "not (sanctum_linkstack_cutover_approved | default(false) | bool)",
            "linkstack_trial_volume != 'linkstack'",
            "linkstack_candidate.image == '" + EXPECTED + "'",
        ]:
            self.assertIn(required, g)
        self.assertEqual(self.play["vars"]["linkstack_trial_volume"],
                         "sanctum-linkstack-restore-test-20261112t105926")
        self.assertEqual(self.play["vars"]["linkstack_trial_network"],
                         "sanctum-linkstack-internal-trial-20261112t105926")

    def test_restored_volume_must_exist_and_pass_sqlite_before_image_pull(self):
        names = [t["name"] for t in self.tasks]
        self.assertLess(names.index("Require only the exact isolated imported test volume already exists"),
                        names.index("Observe whether pinned Linux ARM64 image is already in Kvin rootless cache"))
        inspect = self.task("Confirm restored SQLite")
        self.assertTrue(inspect["no_log"])
        self.assertEqual(inspect["ansible.builtin.command"]["argv"][-2], "restored")
        g = str(self.task("Require isolated saved state actually contains valid")["ansible.builtin.assert"])
        for item in ("isolated_imported_volume_integrity_verified", "sqlite_integrity",
                     "configuration_file_present"):
            self.assertIn(item, g)
        self.assertIn("rc == 0", str(self.task("Refuse any missing")["ansible.builtin.assert"]))

    def test_exact_image_cache_and_real_php_runtime_only(self):
        inspect = self.task("Inspect exactly the pinned cached image")
        self.assertTrue(inspect["no_log"])
        self.assertEqual(inspect["ansible.builtin.command"]["argv"][:3],
                         ["podman", "image", "inspect"])
        pull = self.task("Pull only the exact immutable image digest")
        self.assertTrue(pull["no_log"])
        self.assertEqual(pull["ansible.builtin.command"]["argv"][:2],
                         ["podman", "pull"])
        self.assertIn("linkstack_image_present.rc == 1", pull["when"])
        checks = str(self.task("Require actual linux arm64")["ansible.builtin.assert"]["that"])
        for item in ("Architecture", "arm64", "Os", "linux",
                     "linkstack_candidate.source_running_image_id", "Id"):
            self.assertIn(item, checks)
        run = self.task("Verify actual PHP 8.3")
        args = run["ansible.builtin.command"]["argv"]
        for item in ("--rm", "--network", "none", "--read-only",
                     "no-new-privileges", "--pull", "never",
                     "/usr/bin/php83", "--version"):
            self.assertIn(item, args)
        self.assertTrue(run["no_log"])
        self.assertIs(run["changed_when"], False)

    def test_disposable_app_never_uses_external_network_or_live_volume(self):
        block = self.task("Boot disposable LinkStack")
        self.assertIn("always", block)
        steps = block["block"]
        start = next(t for t in steps if t["name"].startswith("Start an isolated"))
        self.assertTrue(start["no_log"])
        args = start["ansible.builtin.command"]["argv"]
        for item in ("--detach", "--name", "--network",
                     "--pull", "never", "--volume",
                     "sanctum-linkstack-restore-test-20261112t105926:/htdocs"):
            if item == "sanctum-linkstack-restore-test-20261112t105926:/htdocs":
                self.assertIn("linkstack_trial_volume", " ".join(map(str,args)))
                self.assertIn(":/htdocs", " ".join(map(str,args)))
            else:
                self.assertIn(item,args)
        self.assertIn("{{ linkstack_trial_network }}", args)
        self.assertNotIn("none", args)
        for forbidden in ("-p", "--publish", "--network=host", "linkstack:/htdocs", "--privileged"):
            self.assertNotIn(forbidden,args)
        http = next(t for t in steps if t["name"].startswith("Observe application HTTP"))
        command = http["ansible.builtin.command"]["argv"]
        self.assertIn("curl",command)
        self.assertIn("Host: dir.nexus.sanctum",command)
        self.assertIn("http://127.0.0.1/",command)
        self.assertTrue(http["no_log"])
        self.assertFalse(http["failed_when"])
        cleanup = block["always"][0]
        self.assertIn("when",cleanup)
        self.assertIn("linkstack_trial_started",cleanup["when"])
        self.assertIn("linkstack_trial_container", str(cleanup["ansible.builtin.command"]["argv"]))
        self.assertTrue(cleanup["no_log"])
        net_cleanup = block["always"][1]
        self.assertEqual(net_cleanup["ansible.builtin.command"]["argv"][:3],
                         ["podman", "network", "rm"])
        self.assertIn("linkstack_trial_network", str(net_cleanup))
        self.assertTrue(net_cleanup["no_log"])

    def test_internal_bridge_created_only_for_trial_without_dns_or_external_route(self):
        block = self.task("Boot disposable LinkStack")
        tasks = block["block"]
        create = next(t for t in tasks if t["name"].startswith("Create only a disposable"))
        cmd = create["ansible.builtin.command"]["argv"]
        self.assertEqual(cmd[:3], ["podman", "network", "create"])
        self.assertIn("--internal", cmd)
        self.assertIn("--disable-dns", cmd)
        self.assertIn("bridge", cmd)
        self.assertTrue(create["no_log"])
        verify = next(t for t in tasks if t["name"].startswith("Require network is exactly"))
        clauses = str(verify["ansible.builtin.assert"]["that"])
        for flag in ("driver", "bridge", "internal", "dns_enabled",
                     "linkstack_trial_network"):
            self.assertIn(flag, clauses)
        preflight = self.task("Require unoccupied unique temporary internal network identity")
        self.assertIn("linkstack_trial_network_present.rc == 1",
                      str(preflight["ansible.builtin.assert"]["that"]))
        self.assertLess([t["name"] for t in tasks].index(create["name"]),
                        [t["name"] for t in tasks].index("Start an isolated restored-app trial container without publishing a port"))

    def test_trial_checks_process_alive_before_internal_http(self):
        block = self.task("Boot disposable LinkStack")
        names = [t["name"] for t in block["block"]]
        self.assertLess(names.index("Refuse HTTP acceptance if restored app has already exited"),
                        names.index("Observe application HTTP response using configured internal loopback"))
        inspect = next(t for t in block["block"] if t["name"].startswith("Inspect only whether"))
        self.assertIn(".State.Running", str(inspect["ansible.builtin.command"]))
        self.assertTrue(inspect["no_log"])
        self.assertTrue(block["always"][0]["no_log"])
        self.assertTrue(block["always"][1]["no_log"])

    def test_no_production_app_proxy_or_kvar_mutation_and_report_truthfulness(self):
        text = PLAY.read_text()
        for forbidden in ("ansible.builtin.systemd_service:",
                          "ansible.builtin.template:", "ansible.builtin.copy:",
                          "firewall-cmd", "ansible.builtin.uri:",
                          "podman volume import", "podman volume rm", "scp",
                          "ansible.builtin.fetch:", "ansible.builtin.slurp:"):
            self.assertNotIn(forbidden,text)
        report = self.tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertIs(report["kvar_source_or_services_changed"],False)
        self.assertIs(report["production_proxy_dns_or_firewall_changed"],False)
        self.assertIs(report["live_client_directory_or_admin_accepted"],False)
        self.assertIs(report["independent_disaster_recovery_backup_accepted"],False)
        self.assertIs(report["isolated_restored_volume_retained"],True)
        self.assertIs(report["temporary_internal_network_removed"],True)
        self.assertIs(report["isolated_only_internal_network_used"],True)

    def test_ci_runs_source_check_and_syntax_check(self):
        wf = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_qualify_isolated_application.py", wf)
        self.assertIn("ansible/linkstack-qualify-isolated-application.yml --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
