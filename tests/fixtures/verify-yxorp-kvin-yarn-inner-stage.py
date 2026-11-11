#!/usr/bin/env python3
"""Execute eighth old NPM Yarn selection in isolated REAL Ansible, no hosts."""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
stage = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage.yml").read_text(encoding="utf-8")
)[0]
routes = yaml.safe_load(
    (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8")
)["yxorp_routes"]
prefixes = (
    "Require approved Square staging", "Enable only Square alongside Yarn",
    "Require approved Prism staging", "Enable only Prism in addition",
    "Require Search staging", "Enable only Search in addition",
    "Require LinkStack stage", "Enable only interim LinkStack",
    "Require Kuma stage", "Enable only interim Kuma",
    "Require Pi-hole staging", "Enable only interim Pi-hole",
    "Require existing Yarn inner vhost", "Enable only eighth existing Yarn inner",
)
selected = [
    next(t for t in stage["pre_tasks"] if t["name"].startswith(prefix))
    for prefix in prefixes
]
flags = (
    "yxorp_stage_square_approved", "yxorp_stage_prism_approved",
    "yxorp_stage_search_approved", "yxorp_stage_dir_approved",
    "yxorp_stage_kuma_approved", "yxorp_stage_pihole_approved",
    "yxorp_stage_yarn_inner_approved",
)
names = [
    "yarn.nexus.sanctum", "square.nexus.sanctum",
    "joule.nexus.sanctum", "search.nexus.sanctum",
    "dir.nexus.sanctum", "kuma.nexus.sanctum",
    "pihole.nexus.sanctum", "yarn.inner.sanctum",
]
cases = (
    ("eight", (True,) * 7, names),
    ("seven", (True,) * 6 + (False,), names[:7]),
    ("default", (False,) * 7, names[:1]),
    # Deliberate invalid choice: no previously selected seven hosts.
    ("refuse_without_seven", (False,) * 6 + (True,), None),
)
plays = []
for label, approvals, expected in cases:
    if expected is None:
        continue
    plays.append({
        "name": "Reproduce only expected vhosts for " + label,
        "hosts": label,
        "gather_facts": False,
        "vars": {
            "yxorp_routes": routes,
            **dict(zip(flags, approvals)),
            "expected": expected,
        },
        "tasks": selected + [{
            "name": "Assert selected hosts and disabled count " + label,
            "ansible.builtin.assert": {
                "that": [
                    "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == expected",
                    "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == (8 - expected | length)",
                ]
            },
        }],
    })
# The invalid eighth opt-in must be rejected before any real role changes.
gate = next(t for t in selected if t["name"].startswith(
    "Require existing Yarn inner vhost"))
plays.append({
    "name": "Assert illegal eighth selection is refused in check-only trial",
    "hosts": "refuse_without_seven",
    "gather_facts": False,
    "vars": {"yxorp_routes": routes, **dict(zip(flags, cases[3][1]))},
    "tasks": [{
        "name": "Attempt exact eighth source gate only",
        "block": [gate, {
            "name": "Mark missing seven-route prerequisite as unexpected pass",
            "ansible.builtin.fail": {
                "msg": "Eighth route guard incorrectly accepted missing prior hosts"
            },
        }],
        "rescue": [{
            "name": "Verify actual stage assert refused missing seven routes",
            "ansible.builtin.assert": {
                "that": [
                    "ansible_failed_task.name == 'Require existing Yarn inner vhost as eighth isolated Kvin stage route'",
                ]
            },
        }],
    }],
})

with tempfile.TemporaryDirectory(prefix="yxorp-yarn-inner-selection-") as td:
    root = Path(td)
    inventory, playbook = root / "inventory.yml", root / "playbook.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"} for name, _, _ in cases
        }},
    }), encoding="utf-8")
    playbook.write_text(yaml.safe_dump(plays, sort_keys=False),
                        encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(playbook)],
        cwd=ROOT, text=True, capture_output=True, timeout=120,
    )
    if result.returncode:
        print(result.stdout, result.stderr)
        raise SystemExit(result.returncode)
    if result.stdout.count("All assertions passed") < len(cases):
        print(result.stdout)
        raise SystemExit("Missing expected eighth route selection assertions")
print("PASS: real Ansible selected Yarn-only, seven, eight, and rejected illegal eighth-only")
