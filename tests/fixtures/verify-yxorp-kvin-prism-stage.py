#!/usr/bin/env python3
"""Execute exact Square and Prism stage projection and Prism report in real Ansible.

Synthetic isolated localhost identities, no Sanctum network/Podman access.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGE = yaml.safe_load((ROOT / "ansible/yxorp-kvin-stage.yml").read_text())[0]
PROBE = yaml.safe_load((ROOT / "ansible/yxorp-kvin-stage-prism-probe.yml").read_text())[0]
ROUTES = yaml.safe_load((ROOT / "data/yxorp-routes.yml").read_text())["yxorp_routes"]
pre = STAGE["pre_tasks"]
selected = [next(t for t in pre if t["name"].startswith(part)) for part in (
    "Require approved Square staging",
    "Enable only Square alongside Yarn",
    "Require approved Prism staging",
    "Enable only Prism in addition",
)]
report = next(t for t in PROBE["tasks"] if t["name"].startswith("Report only"))

def check_enabled(enabled):
    return {
        "name": "Require the precise selected route set",
        "ansible.builtin.assert": {
            "that": [
                "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == expected",
                "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == (8 - expected | length)",
            ],
        },
    }

cases = [
    ("prism_enabled", True, True,
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum"]),
    ("square_only", True, False,
     ["yarn.nexus.sanctum", "square.nexus.sanctum"]),
    ("source_default", False, False,
     ["yarn.nexus.sanctum"]),
]
plays = [
    {
        "name": "Exercise stage route selection " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_routes": ROUTES,
            "yxorp_stage_square_approved": square,
            "yxorp_stage_prism_approved": prism,
            "expected": expected,
        },
        "tasks": selected + [check_enabled(expected)],
    }
    for name, square, prism, expected in cases
]
plays.append({
    "name": "Render actual Prism response comparison with synthetic results",
    "hosts": "prism_report",
    "gather_facts": False,
    "vars": {
        "yxorp_prism_stage_responses": {
            "results": [
                {"item": {"name": "direct_backend"}, "status": 200,
                 "content_type": "text/html"},
                {"item": {"name": "incumbent_kvar_npm"}, "status": 200,
                 "content_type": "text/html"},
                {"item": {"name": "candidate_kvin_stage"}, "status": 200,
                 "content_type": "text/html"},
            ],
        },
    },
    "tasks": [report],
})
with tempfile.TemporaryDirectory(prefix="yxorp-prism-stage-") as tmp:
    root = Path(tmp)
    inventory = root / "hosts.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"}
            for name in [x[0] for x in cases] + ["prism_report"]
        }},
    }), encoding="utf-8")
    play = root / "fixture.yml"
    play.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(play)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    for expected in (
        '"candidate_status": 200',
        '"incumbent_status": 200',
        '"candidate_and_incumbent_status_equal": true',
        '"candidate_content_type_equals_incumbent": true',
        '"candidate_redirect_equals_incumbent": "not_comparable"',
        '"configuration_changed": false',
    ):
        if expected not in output:
            print("Missing synthetic Prism report:", expected)
            print(output)
            raise SystemExit(1)
print("PASS: real Ansible executed Kvin Prism+Square opt-in, Square-only and Yarn-only defaults; Prism report")
