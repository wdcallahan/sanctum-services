#!/usr/bin/env python3
"""Exercise the actual Search stage opt-in and report under synthetic Ansible.

Runs on distinct local fixture host identities. Never contacts Sanctum.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
stage = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))[0]
probe = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage-search-probe.yml").read_text(encoding="utf-8"))[0]
routes = yaml.safe_load(
    (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8"))["yxorp_routes"]

names = [
    "Require approved Square staging",
    "Enable only Square alongside Yarn",
    "Require approved Prism staging",
    "Enable only Prism in addition",
    "Require Search staging",
    "Enable only Search in addition",
]
selected = [
    next(t for t in stage["pre_tasks"] if t["name"].startswith(name))
    for name in names
]
report = next(t for t in probe["tasks"] if t["name"].startswith("Report only"))

cases = [
    ("all_four", True, True, True,
     ["yarn.nexus.sanctum", "square.nexus.sanctum",
      "joule.nexus.sanctum", "search.nexus.sanctum"]),
    ("previous_three", True, True, False,
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum"]),
    ("square_only", True, False, False,
     ["yarn.nexus.sanctum", "square.nexus.sanctum"]),
    ("default_yarn", False, False, False, ["yarn.nexus.sanctum"]),
]
plays = []
for name, square, prism, search, expected in cases:
    plays.append({
        "name": "Execute exact staged route projections: " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_routes": routes,
            "yxorp_stage_square_approved": square,
            "yxorp_stage_prism_approved": prism,
            "yxorp_stage_search_approved": search,
            "expected": expected,
        },
        "tasks": selected + [{
            "name": "Require exactly the opted-in stage route set",
            "ansible.builtin.assert": {
                "that": [
                    "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == expected",
                    "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == (8 - expected | length)",
                ]
            },
        }],
    })

plays.append({
    "name": "Evaluate actual Search reporter on synthetic equal HTTP200 responses",
    "hosts": "search_report",
    "gather_facts": False,
    "vars": {
        "yxorp_search_stage_responses": {
            "results": [
                {"item": {"name": "direct_backend"}, "status": 200, "content_type": "text/html"},
                {"item": {"name": "incumbent_kvar_npm"}, "status": 200, "content_type": "text/html"},
                {"item": {"name": "candidate_kvin_stage"}, "status": 200, "content_type": "text/html"},
            ]
        }
    },
    "tasks": [report],
})

with tempfile.TemporaryDirectory(prefix="yxorp-search-") as temp:
    folder = Path(temp)
    inventory = folder / "hosts.yml"
    playbook = folder / "fixture.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"}
            for name in [c[0] for c in cases] + ["search_report"]
        }}
    }), encoding="utf-8")
    playbook.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(playbook)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    for expected in (
        '"candidate_status": 200',
        '"incumbent_status": 200',
        '"direct_status": 200',
        '"all_three_have_http_response": true',
        '"candidate_and_incumbent_status_equal": true',
        '"candidate_content_type_equals_incumbent": true',
        '"candidate_redirect_equals_incumbent": "not_comparable"',
        '"configuration_changed": false',
    ):
        if expected not in output:
            print("Missing Search report:", expected)
            print(output)
            raise SystemExit(1)
print("PASS: real Ansible ran four staged route selections and the Search reporter")
