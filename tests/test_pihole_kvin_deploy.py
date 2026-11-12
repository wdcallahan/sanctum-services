"""Kvin restored Pi-hole runs as the actual rootful LAN service, not a test."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PLAY=ROOT/"ansible/pihole-kvin-deploy.yml"
QUADLET=ROOT/"ansible/files/sanctum-pihole-kvin.container"
CI=ROOT/".github/workflows/yxorp-source-check.yml"
DIGEST="13089e5c4d33c5cd8eb7b011949a380145f3ff1405dea24c81dd54dcb255b792"

class PiHoleKvinDeployTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text())[0]
        cls.tasks=cls.play["tasks"]
        cls.quadlet=QUADLET.read_text()

    def task(self,prefix):
        return next(t for t in self.tasks if t["name"].startswith(prefix))

    def test_rootful_exact_kvin_and_opt_in(self):
        self.assertTrue(self.play["become"])
        self.assertEqual(self.play["hosts"],"yxorp")
        conditions=str(self.tasks[0]["ansible.builtin.assert"]["that"])
        for item in ("kvin.outer.sanctum","aarch64","root","wdc2",
                     "192.168.0.192","sanctum_pihole_kvin_deploy_approved",
                     "not ansible_check_mode"):
            self.assertIn(item,conditions)
        self.assertEqual(len(self.play["vars"]["pihole_kvin_volumes"]),2)

    def test_real_rootful_lan_quadlet_and_restored_data(self):
        q=self.quadlet
        self.assertIn(f"ghcr.io/pi-hole/pihole@sha256:{DIGEST}",q)
        self.assertIn(f"ghcr.io/pi-hole/pihole@sha256:{DIGEST}",PLAY.read_text())
        self.assertNotIn(":latest",q)
        self.assertIn("Pull=never",q)
        for expected in ("Volume=sanctum-pihole-etc-20261112t161524:/etc/pihole:Z",
                         "Volume=sanctum-pihole-dnsmasq-20261112t161524:/etc/dnsmasq.d:Z",
                         "PublishPort=192.168.0.192:53:53/tcp",
                         "PublishPort=192.168.0.192:53:53/udp",
                         "PublishPort=192.168.0.192:82:80/tcp",
                         "Environment=FTLCONF_dns_listeningMode=ALL"):
            self.assertIn(expected,q)
        self.assertNotIn("Network=host",q)
        self.assertIn("WantedBy=multi-user.target",q)

    def test_image_qualified_and_runtime_service_only(self):
        src=PLAY.read_text()
        self.assertIn("64c81b3c8132f3e7ae56925a1668d2cfa5a53c509c43b4c1cc71591e0f42c3d8",src)
        self.assertIn("regex_replace('^sha256:', '')",src)
        self.assertIn("arm64",src)
        self.assertIn("files/sanctum-pihole-kvin.container",src)
        svc=self.task("Start or reconcile only")["ansible.builtin.systemd_service"]
        self.assertEqual(svc["name"],"{{ pihole_kvin_unit }}")
        self.assertIn("pihole_kvin_quadlet_written.changed",svc["state"])
        self.assertIn("http://192.168.0.192:82/admin/",src)
        for forbidden in ("kvar.outer.sanctum", "pihole.service", "firewall-cmd",
                          "podman volume rm","sanctum_yxorp_dns_publish_approved"):
            # Kvar's name occurs only as a report field/comment; no action targets it.
            if forbidden == "kvar.outer.sanctum":
                self.assertEqual(src.count("kvar.outer.sanctum"),0)
            else:
                self.assertNotIn(forbidden,src)

    def test_ci_runs_tests_and_syntax(self):
        src=CI.read_text()
        self.assertIn("test_pihole_kvin_deploy.py",src)
        self.assertIn("ansible/pihole-kvin-deploy.yml --syntax-check",src)

if __name__=="__main__":
    unittest.main()
