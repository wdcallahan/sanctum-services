"""Production YXORP projection: eight names, Kuma plus reversible app targets."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
PROD=ROOT/"ansible/yxorp.yml"
ROUTES=ROOT/"data/yxorp-routes.yml"
STAGE=ROOT/"ansible/yxorp-kvin-stage.yml"
STAGE_REMOVE=ROOT/"ansible/yxorp-kvin-stage-remove.yml"
ROLE_DEFAULTS=ROOT/"ansible/roles/yxorp/defaults/main.yml"
CI=ROOT/".github/workflows/yxorp-source-check.yml"


class ProductionPromotionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PROD.read_text())[0]
        cls.manifest=yaml.safe_load(ROUTES.read_text())["yxorp_routes"]
        cls.tasks=cls.play["pre_tasks"]

    def test_exact_host_gate_and_stage_removed_before_role(self):
        self.assertEqual(self.play["hosts"],"yxorp")
        self.assertTrue(self.play["become"])
        self.assertTrue(self.play["gather_facts"])
        self.assertEqual(self.play["roles"],["yxorp"])
        assert self.play["vars_files"]==["../data/yxorp-routes.yml"]
        gate=self.tasks[0]["ansible.builtin.assert"]["that"]
        for expr in ("inventory_hostname == 'kvin.outer.sanctum'",
                     "yxorp_deployment_scope == 'kvin_production'",
                     "yxorp_production_cutover_approved | bool",
                     "yxorp_routes | length == 8",
                     "not ansible_check_mode"):
            self.assertIn(expr,gate)
        names=[r["hostname"] for r in self.manifest]
        self.assertEqual(sorted(names),sorted(self.play["vars"]["yxorp_production_expected_names"]))
        self.assertEqual(len(names),8)
        stages=[t["name"] for t in self.tasks]
        for name in ("Observe stage Quadlet without following links",
                     "Observe old rootful stage service before acquiring port 80",
                     "Require old Kvin port-80 stage already removed with its own runbook",
                     "Require new retained Kuma actually responds on its private Kvin listener"):
            self.assertIn(name,stages)
        assert stages.index("Require old Kvin port-80 stage already removed with its own runbook") < stages.index("Render exactly eight production routes with Kuma and selected LinkStack and Pi-hole backends")

    def test_only_known_source_manifest_promoted(self):
        self.assertEqual([r["hostname"] for r in self.manifest if r["enabled"]],
                         ["yarn.nexus.sanctum"])
        prod=self.play["vars"]
        self.assertEqual(prod["yxorp_production_kuma_http"],"http://127.0.0.1:13001/")
        self.assertEqual(prod["yxorp_production_routes"],[])
        self.assertEqual(prod["yxorp_production_linkstack_backend"],"kvin")
        self.assertEqual(prod["yxorp_production_pihole_backend"],"kvin")
        project=next(t for t in self.tasks if t["name"].startswith("Render exactly eight"))
        self.assertEqual(project["loop"],"{{ yxorp_routes }}")
        expression=project["ansible.builtin.set_fact"]["yxorp_production_routes"]
        self.assertIn("combine({'enabled': true})",expression)
        self.assertIn("'upstream_host': '127.0.0.1'",expression)
        self.assertIn("'upstream_port': 13001",expression)
        self.assertIn("'upstream_port': (18081 if yxorp_production_linkstack_backend == 'kvin' else 8081)",expression)
        self.assertIn("item.hostname == 'dir.nexus.sanctum'",expression)
        self.assertIn("item.hostname == 'pihole.nexus.sanctum'",expression)
        self.assertIn("'192.168.0.192' if yxorp_production_pihole_backend == 'kvin'",expression)
        self.assertIn("kvar.outer.sanctum",expression)
        self.assertIn("http://127.0.0.1:18081/",PROD.read_text())
        self.assertIn("http://192.168.0.192:82/admin/",PROD.read_text())
        self.assertIn("http://127.0.0.1/admin/",PROD.read_text())
        self.assertIn("status_code: [200]",PROD.read_text())
        self.assertIn("if item.hostname == 'kuma.nexus.sanctum'",expression)
        self.assertIn("else {}",expression)
        promote=next(t for t in self.tasks if t["name"].startswith("Promote verified"))
        self.assertEqual(promote["ansible.builtin.set_fact"]["yxorp_routes"],
                         "{{ yxorp_production_routes }}")
        # Do not allow production to accidentally inherit stage-only rootful paths.
        defaults=yaml.safe_load(ROLE_DEFAULTS.read_text())
        self.assertEqual(defaults["yxorp_service_name"],"sanctum-yxorp.service")
        self.assertNotEqual(defaults["yxorp_service_name"],
                            yaml.safe_load((ROOT/"ansible/vars/yxorp-kvin-stage.yml").read_text())["yxorp_service_name"])
        self.assertNotIn("firewall-cmd",PROD.read_text())
        self.assertNotIn("data/dns.yml",PROD.read_text())
        pihole=next(t for t in self.tasks if t["name"].startswith("Require real restored Kvin Pi-hole"))
        self.assertEqual(pihole["when"],"yxorp_production_pihole_backend == 'kvin'")
        self.assertEqual(pihole["ansible.builtin.uri"]["status_code"],[200,301,302,303])
        post=next(t for t in self.play["post_tasks"] if t["name"].startswith("Verify real production Pi-hole"))
        self.assertEqual(post["ansible.builtin.uri"]["status_code"],[200,301,302,303])

    def test_explicit_production_reversal_preserves_incumbent_and_app_data(self):
        path=ROOT/"ansible/yxorp-production-remove.yml"
        reverse=yaml.safe_load(path.read_text())[0]
        self.assertEqual(reverse["hosts"],"yxorp")
        self.assertTrue(reverse["become"])
        self.assertEqual(reverse["vars_files"],["roles/yxorp/defaults/main.yml"])
        guard=reverse["tasks"][0]["ansible.builtin.assert"]["that"]
        for clause in ("inventory_hostname == 'kvin.outer.sanctum'",
                       "yxorp_deployment_scope == 'kvin_production'",
                       "yxorp_production_remove_approved | default(false) | bool",
                       "not (yxorp_production_cutover_approved | bool)"):
            self.assertIn(clause,guard)
        text=path.read_text()
        self.assertIn("sanctum-yxorp.service",text)
        self.assertNotIn("sanctum-yxorp-kvin-stage",text)
        self.assertNotIn("podman volume rm",text)
        self.assertNotIn("firewall-cmd",text)
        self.assertIn("Kvar is untouched",text)
        names=[task["name"] for task in reverse["tasks"]]
        self.assertIn("Stop only the verified production service when active",names)
        self.assertIn("Remove only the verified production Quadlet",names)
        self.assertIn("Require no production service still running",names)

    def test_existing_yarn_failure_cannot_abort_linkstack_acceptance(self):
        """Existing Yarn timeout was incorrectly failing an otherwise working LinkStack deployment."""
        post=self.play["post_tasks"]
        yarn=next(t for t in post if t["name"]=="Observe existing Yarn route without blocking unrelated service updates")
        linkstack=next(t for t in post if t["name"]=="Verify normal production LinkStack route responds through YXORP")
        self.assertLess(post.index(yarn),post.index(linkstack))
        self.assertIs(yarn["failed_when"],False)
        self.assertIs(yarn["changed_when"],False)
        self.assertEqual(yarn["ansible.builtin.uri"]["timeout"],8)
        report=next(t for t in post if t["name"]=="Report bounded Kvin YXORP production listener readiness")
        data=report["ansible.builtin.debug"]["msg"]
        self.assertIn("yarn_frontend_accepted",data)
        self.assertIn("default(-1)",data["yarn_frontend_http_response"])
        self.assertIn("preexisting Yarn path not responding",data["yarn_frontend_note"])

    def test_real_ansible_projection_fixture_and_source_ci(self):
        c=CI.read_text()
        self.assertIn("test_yxorp_production_promotion.py",c)
        self.assertIn("verify-yxorp-production-routes.py",c)
        self.assertIn("ansible/yxorp.yml --syntax-check",c)


if __name__=="__main__":
    unittest.main()
