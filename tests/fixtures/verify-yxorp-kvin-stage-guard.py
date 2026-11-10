#!/usr/bin/env python3
"""Exercise the deployed role's exact authorization expression with real Ansible.

Synthetic inventory uses local connections, no Sanctum host or service contact.
A rejection case passes only if the actual guard expression evaluates false.
"""
from pathlib import Path
import subprocess
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[2]
ROLE = ROOT / "ansible/roles/yxorp/tasks/main.yml"
stage_guard = yaml.safe_load(ROLE.read_text(encoding="utf-8"))[0][
    "ansible.builtin.assert"]["that"][3]

DIGEST = "docker.io/library/nginx@sha256:564a09935b00f058ca1b28c742169ba817499baa0479807bf7f373fe2804fbf7"
STAGE = {
    "yxorp_deployment_scope": "kvin_stage",
    "yxorp_kvin_stage_approved": True,
    "yxorp_production_cutover_approved": False,
    "yxorp_image": DIGEST,
    "yxorp_config_dir": "/etc/sanctum-services/yxorp-kvin-stage",
    "yxorp_quadlet_file": "/etc/containers/systemd/sanctum-yxorp-kvin-stage.container",
    "yxorp_service_name": "sanctum-yxorp-kvin-stage.service",
    "yxorp_container_name": "sanctum-yxorp-kvin-stage",
}
PRODUCTION = {
    **STAGE,
    "yxorp_deployment_scope": "kvin_production",
    "yxorp_kvin_stage_approved": False,
    "yxorp_production_cutover_approved": True,
}
PEANUT = {
    **STAGE,
    "yxorp_deployment_scope": "peanut_trial",
    "yxorp_image": "docker.io/library/nginx:stable-alpine",
    "yxorp_peanut_test_approved": True,
    "yxorp_kvin_stage_approved": False,
}
cases = [
    ("stage authorized with production still closed", "kvin.outer.sanctum", STAGE, True),
    ("stage not approved", "kvin.outer.sanctum", {**STAGE, "yxorp_kvin_stage_approved": False}, False),
    ("stage cannot inherit production approval", "kvin.outer.sanctum", {**STAGE, "yxorp_production_cutover_approved": True}, False),
    ("stage refuses wrong Quadlet", "kvin.outer.sanctum", {**STAGE, "yxorp_quadlet_file": "/etc/containers/systemd/sanctum-yxorp.container"}, False),
    ("stage refuses wrong config path", "kvin.outer.sanctum", {**STAGE, "yxorp_config_dir": "/etc/sanctum-services/yxorp"}, False),
    ("stage refuses wrong inventory host", "peanut.arcane.sanctum", STAGE, False),
    ("existing production authorization remains separate", "kvin.outer.sanctum", PRODUCTION, True),
    ("existing Peanut trial authorization remains valid", "peanut.arcane.sanctum", PEANUT, True),
    ("Peanut trial refuses Kvin stage identity", "kvin.outer.sanctum", PEANUT, False),
]

inventory = {"all": {"hosts": {
    "kvin.outer.sanctum": {"ansible_connection": "local"},
    "peanut.arcane.sanctum": {"ansible_connection": "local"},
}}}
plays = []
for description, host, variables, should_accept in cases:
    expression = stage_guard if should_accept else f"not ({stage_guard})"
    plays.append({
        "name": f"Assert role gate: {description}",
        "hosts": host,
        "gather_facts": False,
        "vars": variables,
        "tasks": [{
            "name": f"Real Ansible role guard must {'accept' if should_accept else 'reject'}",
            "ansible.builtin.assert": {"that": [expression]},
        }],
    })

with tempfile.TemporaryDirectory(prefix="yxorp-guard-") as temporary:
    folder = Path(temporary)
    (folder / "inventory.yml").write_text(
        yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8")
    (folder / "cases.yml").write_text(
        yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    outcome = subprocess.run(
        ["ansible-playbook", "-i", str(folder / "inventory.yml"),
         str(folder / "cases.yml")],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if outcome.returncode:
        print(outcome.stdout)
        print(outcome.stderr)
        raise SystemExit(outcome.returncode)

print(f"PASS: actual YXORP role gate evaluated under Ansible for {len(cases)} cases; no live hosts contacted")
