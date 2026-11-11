"""Production YXORP promotion: exact eight names, Kuma-only backend change."""
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
        assert stages.index("Require old Kvin port-80 stage already removed with its own runbook") < stages.index("Render exactly eight production routes with only Kuma retargeted")

    def test_only_known_source_manifest_promoted(self):
        self.assertEqual([r["hostname"] for r in self.manifest if r["enabled"]],
                         ["yarn.nexus.sanctum"])
        prod=self.play["vars"]
        self.assertEqual(prod["yxorp_production_kuma_http"],"http://127.0.0.1:13001/")
        self.assertEqual(prod["yxorp_production_routes"],[])
        project=next(t for t in self.tasks if t["name"].startswith("Render exactly eight"))
        self.assertEqual(project["loop"],"{{ yxorp_routes }}")
        expression=project["ansible.builtin.set_fact"]["yxorp_production_routes"]
        self.assertIn("combine({'enabled': true})",expression)
        self.assertIn("'upstream_host': '127.0.0.1'",expression)
        self.assertIn("'upstream_port': 13001",expression)
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

    def test_real_ansible_projection_fixture_and_source_ci(self):
        c=CI.read_text()
        self.assertIn("test_yxorp_production_promotion.py",c)
        self.assertIn("verify-yxorp-production-routes.py",c)
        self.assertIn("ansible/yxorp.yml --syntax-check",c)


if __name__=="__main__":
    unittest.main()
