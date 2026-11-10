#!/usr/bin/env python3
"""Execute stage-only Square route selection and sanitized status report in real Ansible.

Only synthetic localhost variables. Never connects to Kvin, Kvar, or a backend.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGE = yaml.safe_load((ROOT / "ansible/yxorp-kvin-stage.yml").read_text())
PROBE = yaml.safe_load((ROOT / "ansible/yxorp-kvin-stage-square-probe.yml").read_text())
ROUTES = yaml.safe_load((ROOT / "data/yxorp-routes.yml").read_text())["yxorp_routes"]
pre = STAGE[0]["pre_tasks"]
selected = [next(t for t in pre if t["name"].startswith(p)) for p in
            ("Require approved Square staging", "Enable only Square")]
report = next(t for t in PROBE[0]["tasks"] if t["name"].startswith("Report only"))
check_on = {
    "name": "Verify exactly Yarn and Square enabled in opt-in stage",
    "ansible.builtin.assert": {
        "that": [
            "(yxorp_routes | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum', 'joule.nexus.sanctum', 'search.nexus.sanctum', 'dir.nexus.sanctum', 'kuma.nexus.sanctum', 'pihole.nexus.sanctum', 'yarn.inner.sanctum']",
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum', 'square.nexus.sanctum']",
            "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == 6",
        ],
    },
}
check_off = {
    "name": "Verify original default still enables only Yarn",
    "ansible.builtin.assert": {
        "that": [
            "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == ['yarn.nexus.sanctum']",
            "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == 7",
        ]
    }
}
fixture = [
    {
        "name": "Stage Square only when opted-in",
        "hosts": "localhost",
        "gather_facts": False,
        "vars": {"yxorp_routes": ROUTES, "yxorp_stage_square_approved": True},
        "tasks": selected + [check_on],
    },
    {
        "name": "Preserve Yarn-only default when no Square opt-in",
        "hosts": "localhost",
        "gather_facts": False,
        "vars": {"yxorp_routes": ROUTES, "yxorp_stage_square_approved": False},
        "tasks": selected + [check_off],
    },
    {
        "name": "Render actual Square diagnostic from synthetic anonymous HTTP responses",
        "hosts": "localhost",
        "gather_facts": False,
        "vars": {
            "yxorp_square_stage_responses": {
                "results": [
                    {"item": {"name": "direct_backend"}, "status": 302,
                     "location": "http://square.nexus.sanctum/apps/files/"},
                    {"item": {"name": "incumbent_kvar_npm"}, "status": 302,
                     "location": "http://square.nexus.sanctum/apps/files/"},
                    {"item": {"name": "candidate_kvin_stage"}, "status": 302,
                     "location": "http://square.nexus.sanctum/apps/files/"},
                ]
            }
        },
        "tasks": [report],
    },
]
with tempfile.TemporaryDirectory(prefix="yxorp-square-stage-") as tmp:
    path = Path(tmp) / "square-stage-fixture.yml"
    path.write_text(yaml.safe_dump(fixture, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", "localhost,", str(path), "-c", "local"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    expected = [
        '"candidate_status": 302',
        '"candidate_and_incumbent_status_equal": true',
        '"candidate_location_equals_incumbent": true',
        '"configuration_changed": false',
    ]
    missing = [e for e in expected if e not in output]
    if missing:
        print("Square synthetic verification did not render expected result", missing)
        print(output)
        raise SystemExit(1)
print("PASS: real Ansible selected only Square+Yarn when opted in; default retains Yarn-only; sanitized report evaluates")
