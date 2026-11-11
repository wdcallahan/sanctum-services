#!/usr/bin/env python3
"""Execute only stage route projection tasks in local synthetic real Ansible."""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
stage = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))[0]
routes = yaml.safe_load(
    (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8"))["yxorp_routes"]

prefixes = (
    "Require approved Square staging", "Enable only Square alongside Yarn",
    "Require approved Prism staging", "Enable only Prism in addition",
    "Require Search staging", "Enable only Search in addition",
    "Require LinkStack stage", "Enable only interim LinkStack",
    "Require Kuma stage", "Enable only interim Kuma",
    "Require Pi-hole staging", "Enable only interim Pi-hole",
)
selected = [
    next(t for t in stage["pre_tasks"] if t["name"].startswith(prefix))
    for prefix in prefixes
]
flag_names = (
    "yxorp_stage_square_approved", "yxorp_stage_prism_approved",
    "yxorp_stage_search_approved", "yxorp_stage_dir_approved",
    "yxorp_stage_kuma_approved", "yxorp_stage_pihole_approved",
)
cases = (
    ("seven", (True,) * 6,
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum",
      "search.nexus.sanctum", "dir.nexus.sanctum", "kuma.nexus.sanctum",
      "pihole.nexus.sanctum"]),
    ("six", (True,) * 5 + (False,),
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum",
      "search.nexus.sanctum", "dir.nexus.sanctum", "kuma.nexus.sanctum"]),
    ("default", (False,) * 6, ["yarn.nexus.sanctum"]),
)
plays = []
for name, flags, expected in cases:
    plays.append({
        "name": "Test in-memory stage selection " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_routes": routes,
            **dict(zip(flag_names, flags)),
            "expected": expected,
        },
        "tasks": selected + [{
            "name": "Verify exact enabled hostnames and all other names disabled",
            "ansible.builtin.assert": {
                "that": [
                    "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == expected",
                    "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == (8 - expected | length)",
                ]
            },
        }],
    })

with tempfile.TemporaryDirectory(prefix="yxorp-pihole-stage-") as tmp:
    root = Path(tmp)
    inventory = root / "hosts.yml"
    play = root / "play.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"} for name, _, _ in cases
        }}
    }, sort_keys=False), encoding="utf-8")
    play.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(play)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        print(result.stdout, result.stderr)
        raise SystemExit(result.returncode)
    if result.stdout.count("All assertions passed") < len(cases):
        print(result.stdout)
        raise SystemExit("Synthetic Pi-hole route selection failed")
print("PASS: real Ansible selected only seven, six or Yarn-only Kvin stage routes")
