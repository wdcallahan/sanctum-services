"""Live LinkStack Kvin migration: only its own existing data and rootless Quadlet."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PB=ROOT/"ansible/linkstack-kvin-auto-update.yml"
NEW=ROOT/"ansible/files/sanctum-linkstack-kvin-managed.container"
OLD=ROOT/"ansible/files/sanctum-linkstack-kvin-candidate.container"
CI=ROOT/".github/workflows/yxorp-source-check.yml"


class LinkStackMovingRegistrySource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PB.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.by_name={t["name"]:t for t in cls.tasks}
        cls.source=NEW.read_text()

    def test_approved_exact_existing_service_and_rootless_identity(self):
        self.assertEqual(self.play["hosts"],"kuma")
        self.assertIs(self.play["become"],False)
        v=self.play["vars"]
        self.assertEqual(v["linkstack_update_service"],
                         "sanctum-linkstack-kvin-candidate.service")
        self.assertEqual(v["linkstack_update_container"],
                         "sanctum-linkstack-kvin-candidate")
        self.assertEqual(v["linkstack_update_volume"],
                         "sanctum-linkstack-qualified-20261112t105926")
        self.assertEqual(v["linkstack_update_new_image"],
                         "docker.io/linkstackorg/linkstack:latest")
        preflight=self.tasks[0]["ansible.builtin.assert"]["that"]
        for expected in ("inventory_hostname == 'kvin.outer.sanctum'",
                         "ansible_facts['architecture'] == 'aarch64'",
                         "ansible_facts['user_id'] == 'wdc2'",
                         "sanctum_linkstack_kvin_auto_update_approved | default(false) | bool"):
            self.assertIn(expected,preflight)

    def test_desired_current_quadlet_preserves_unrelated_backends(self):
        q=self.source
        for token in ("Image=docker.io/linkstackorg/linkstack:latest",
                      "AutoUpdate=registry",
                      "ContainerName=sanctum-linkstack-kvin-candidate",
                      "Volume=sanctum-linkstack-qualified-20261112t105926:/htdocs:Z",
                      "PublishPort=127.0.0.1:18081:80/tcp",
                      "Sysctl=net.ipv4.ip_unprivileged_port_start=80",
                      "NoNewPrivileges=true",
                      "Environment=HTTP_SERVER_NAME=localhost"):
            self.assertIn(token+"\n",q)
        for bad in ("Pull=never", "0.0.0.0", "Network=host",
                    "Volume=linkstack:", ":U,Z", "Privileged=true",
                    "ExecStart=", "MYSQL_PASSWORD=", "APP_KEY="):
            self.assertNotIn(bad,q)
        for key in ("Image=", "AutoUpdate=", "Volume=", "PublishPort="):
            self.assertEqual(q.count(key),1,key)
        self.assertIn("Image=docker.io/linkstackorg/linkstack@sha256:",OLD.read_text())
        self.assertIn("Pull=never",OLD.read_text())

    def test_before_image_change_current_data_and_image_are_accepted(self):
        names=list(self.by_name)
        check=names.index("Require original running container image and same persistent volume")
        pull=names.index("Pull supported moving LinkStack image without touching running instance")
        self.assertLess(check,pull)
        original=self.by_name["Require original immutable installed LinkStack Quadlet before update"]
        self.assertIn("vars",original)
        self.assertNotIn("vars",original["ansible.builtin.assert"])
        guard=original["ansible.builtin.assert"]["that"]
        self.assertTrue(any("Pull=never" in c for c in guard))
        self.assertTrue(any("linkstack_update_old_image" in c for c in guard))
        self.assertTrue(any("linkstack_update_volume" in c for c in guard))
        image=self.by_name["Require supported Linux ARM64 image content is actually cached"]
        self.assertTrue(any("Architecture" in c and "arm64" in c
                            for c in image["ansible.builtin.assert"]["that"]))
        self.assertIn("podman",str(self.by_name["Pull supported moving LinkStack image without touching running instance"]))

    def test_only_one_approved_live_restart_and_explicit_rollback_attempt(self):
        task=self.by_name["Replace only existing LinkStack Quadlet and restart its single rootless service"]
        blk=task["block"]
        rescue=task["rescue"]
        write=next(t for t in blk if t["name"]=="Install moving image and registry auto-update LinkStack Quadlet")
        self.assertEqual(write["ansible.builtin.copy"]["src"],
                         "{{ linkstack_update_new_source }}")
        self.assertEqual(write["ansible.builtin.copy"]["dest"],
                         "{{ linkstack_update_quadlet }}")
        restart=next(t for t in blk if t["name"].startswith("Restart only LinkStack"))
        self.assertEqual(restart["ansible.builtin.systemd_service"]["scope"],"user")
        self.assertEqual(restart["ansible.builtin.systemd_service"]["state"],"restarted")
        self.assertTrue(restart["ansible.builtin.systemd_service"]["daemon_reload"])
        old=next(t for t in rescue if t["name"].startswith("Restore only the original pinned"))
        self.assertEqual(old["ansible.builtin.copy"]["src"],
                         "{{ linkstack_update_old_source }}")
        fallback=next(t for t in rescue if t["name"].startswith("Attempt to restart only original"))
        self.assertEqual(fallback["ansible.builtin.systemd_service"]["scope"],"user")
        self.assertEqual(fallback["ansible.builtin.systemd_service"]["state"],"restarted")
        self.assertIn("ansible.builtin.fail",rescue[-1])
        self.assertIn("NOT automatically rolled back",rescue[-1]["ansible.builtin.fail"]["msg"])

    def test_no_unrelated_changes_and_report_does_not_overclaim(self):
        raw=PB.read_text()
        for bad in ("kvar.outer.sanctum", "firewall-cmd", "become: true",
                    "scope: system", "podman volume rm", "podman volume import",
                    "ansible.builtin.iptables:", "ansible.builtin.template:",
                    "db.sqlite", "mysql"):
            self.assertNotIn(bad,raw)
        report=self.by_name["Report actual Kvin LinkStack moving registry update deployment"]["ansible.builtin.debug"]["msg"]
        self.assertTrue(report["no_dns_proxy_firewall_or_other_services_changed"])
        self.assertTrue(report["authenticated_directory_admin_not_tested_in_this_play"])
        self.assertTrue(report["future_scheduled_registry_refresh_not_yet_observed"])
        self.assertTrue(report["local_sqlite_backup_and_peanut_retention_accepted"])

    def test_assert_actions_never_receive_unsupported_vars_keyword(self):
        def visit(items):
            for t in items:
                if "ansible.builtin.assert" in t:
                    self.assertFalse(
                        set(t["ansible.builtin.assert"])-{"that","fail_msg","success_msg","quiet"},
                        t["name"])
                for k in ("block","rescue","always"):
                    visit(t.get(k,[]))
        visit(self.tasks)

    def test_ci_full_suite_checks_this_deployment(self):
        workflow=CI.read_text()
        self.assertIn("ansible/linkstack-kvin-auto-update.yml --syntax-check",workflow)
        self.assertIn("test_linkstack_kvin_auto_update.py",workflow)


if __name__=="__main__":
    unittest.main()
