#!/usr/bin/env python3
"""Execute actual LinkStack stage tasks and reporter under synthetic Ansible.

Four route selection states run on isolated local fixture hosts. No network,
SSH, HTTP requests, Podman, or remote mutations.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
stage = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))[0]
probe = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage-dir-probe.yml").read_text(encoding="utf-8"))[0]
routes = yaml.safe_load(
    (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8"))["yxorp_routes"]
names = (
    "Require approved Square staging", "Enable only Square alongside Yarn",
    "Require approved Prism staging", "Enable only Prism in addition",
    "Require Search staging", "Enable only Search in addition",
    "Require LinkStack stage", "Enable only interim LinkStack",
)
selected = [next(t for t in stage["pre_tasks"] if t["name"].startswith(name))
            for name in names]
report = next(t for t in probe["tasks"] if t["name"].startswith("Report only"))

cases = [
    ("all_five", (True, True, True, True),
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum",
      "search.nexus.sanctum", "dir.nexus.sanctum"]),
    ("previous_four", (True, True, True, False),
     ["yarn.nexus.sanctum", "square.nexus.sanctum",
      "joule.nexus.sanctum", "search.nexus.sanctum"]),
    ("square_only", (True, False, False, False),
     ["yarn.nexus.sanctum", "square.nexus.sanctum"]),
    ("default_yarn", (False, False, False, False),
     ["yarn.nexus.sanctum"]),
]
plays = []
for name, flags, expected in cases:
    plays.append({
        "name": "Execute exact stage flags: " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_routes": routes,
            **dict(zip((
                "yxorp_stage_square_approved", "yxorp_stage_prism_approved",
                "yxorp_stage_search_approved", "yxorp_stage_dir_approved"),
                flags)),
            "expected": expected,
        },
        "tasks": selected + [{
            "name": "Confirm no unapproved route enabled",
            "ansible.builtin.assert": {
                "that": [
                    "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == expected",
                    "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == (8 - expected | length)"
                ]
            }
        }]
    })
plays.append({
    "name": "Exercise actual LinkStack report with synthetic three-way HTTP200",
    "hosts": "dir_report",
    "gather_facts": False,
    "vars": {
        "yxorp_dir_stage_responses": {
            "results": [
                {"item": {"name": n}, "status": 200, "content_type": "text/html"}
                for n in ("direct_backend", "incumbent_kvar_npm", "candidate_kvin_stage")
            ]
        }
    },
    "tasks": [report]
})

with tempfile.TemporaryDirectory(prefix="yxorp-dir-stage-") as tmp:
    d = Path(tmp)
    inventory = d / "hosts.yml"
    playbook = d / "fixture.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"}
            for name in [c[0] for c in cases] + ["dir_report"]
        }}
    }), encoding="utf-8")
    playbook.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(["ansible-playbook", "-i", str(inventory),
                             str(playbook)], cwd=ROOT, text=True,
                            capture_output=True, check=False)
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    for required in (
        '"candidate_status": 200', '"incumbent_status": 200',
        '"direct_status": 200', '"all_three_have_http_response": true',
        '"candidate_content_type_equals_incumbent": true',
        '"candidate_redirect_equals_incumbent": "not_comparable"',
        '"application_migrated_to_kvin": false',
        '"configuration_changed": false',
    ):
        if required not in output:
            print("Missing sanitized LinkStack report:", required)
            print(output)
            raise SystemExit(1)
print("PASS: exact fifth-route projection and reporter under real synthetic Ansible")
