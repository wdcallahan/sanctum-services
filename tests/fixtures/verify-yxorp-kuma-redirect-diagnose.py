#!/usr/bin/env python3
"""Run actual Ansible Kuma sanitized reporter on synthetic HTTP response sets.

No sockets, external HTTP calls, Podman, or target hosts involved.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
p = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml")
    .read_text(encoding="utf-8"))[0]
report = next(
    task for task in p["tasks"]
    if task["name"].startswith("Report only Kuma redirect host classes"))

scenarios = [
    (
        "candidate_frontend_port80",
        ["http://kvar.outer.sanctum:3001/dashboard",
         "http://kvar.outer.sanctum/dashboard",
         "http://kuma.nexus.sanctum:80/dashboard"],
        {
            "direct_redirect_host_class": "kvar_backend_host",
            "incumbent_redirect_host_class": "kvar_backend_host",
            "candidate_redirect_host_class": "frontend",
            "direct_redirect_port_class": "kuma_backend_port_3001",
            "incumbent_redirect_port_class": "no_explicit_port",
            "candidate_redirect_port_class": "stage_http_port_80",
            "direct_and_incumbent_host_equal": True,
            "candidate_and_direct_host_equal": False,
            "candidate_and_incumbent_host_equal": False,
            "candidate_and_incumbent_path_equal": True,
            "candidate_and_incumbent_redirect_equal": False,
            "all_three_redirect": True,
        },
    ),
    (
        "candidate_direct_backend_redirect",
        ["http://kvar.outer.sanctum:3001/dashboard",
         "http://kvar.outer.sanctum/dashboard",
         "http://kvar.outer.sanctum:3001/dashboard"],
        {
            "candidate_redirect_host_class": "kvar_backend_host",
            "candidate_redirect_port_class": "kuma_backend_port_3001",
            "candidate_and_direct_host_equal": True,
            "candidate_and_incumbent_host_equal": True,
            "candidate_and_incumbent_redirect_equal": False,
            "all_three_redirect": True,
        },
    ),
    (
        "candidate_matches_incumbent",
        ["http://kvar.outer.sanctum:3001/dashboard",
         "http://kvar.outer.sanctum/dashboard",
         "http://kvar.outer.sanctum/dashboard"],
        {
            "candidate_redirect_host_class": "kvar_backend_host",
            "candidate_redirect_port_class": "no_explicit_port",
            "candidate_and_incumbent_host_equal": True,
            "candidate_and_incumbent_redirect_equal": True,
            "all_three_redirect": True,
        },
    ),
    (
        "not_redirecting",
        ["", "", ""],
        {
            "direct_redirect_host_class": "absent",
            "candidate_redirect_host_class": "absent",
            "candidate_redirect_port_class": "absent",
            "candidate_and_incumbent_host_equal": "not_comparable",
            "candidate_and_incumbent_redirect_equal": "not_comparable",
            "all_three_redirect": False,
        },
    ),
]
plays = []
for name, locs, expected in scenarios:
    statuses = [200, 200, 200] if name == "not_redirecting" else [302, 302, 302]
    results = [{
        "item": {"name": key}, "status": status, "content_type": "text/html",
        **({"location": loc} if loc else {}),
    } for key, status, loc in zip(
        ("direct_kuma_backend", "incumbent_kvar_npm", "candidate_kvin_stage"),
        statuses, locs)]
    plays.append({
        "name": "Synthetic Kuma redirect category " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_kuma_authority_observations": {"results": results},
            "expected": expected,
        },
        "tasks": [
            {**report, "register": "classified"},
            {
                "name": "Require exact safe redirect classes",
                "ansible.builtin.assert": {
                    "that": [
                        "classified.msg[item.key] == item.value",
                    ]
                },
                "loop": [{"key": k, "value": v} for k, v in expected.items()],
                "loop_control": {"label": "{{ item.key }}"},
            },
        ],
    })
with tempfile.TemporaryDirectory(prefix="yxorp-kuma-redirect-") as tmp:
    root = Path(tmp)
    inventory = root / "inventory.yml"
    playbook = root / "fixture.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"}
            for name, _, _ in scenarios
        }}
    }, sort_keys=False), encoding="utf-8")
    playbook.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(playbook)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    for token in (
        '"candidate_redirect_host_class": "frontend"',
        '"candidate_redirect_port_class": "stage_http_port_80"',
        '"candidate_redirect_host_class": "kvar_backend_host"',
        '"candidate_redirect_port_class": "kuma_backend_port_3001"',
        '"candidate_and_incumbent_redirect_equal": true',
        '"candidate_redirect_host_class": "absent"',
        '"raw_host_url_port_cookie_body_exposed": false',
    ):
        if token not in output:
            print("Missing safe synthetic redirect category:", token)
            print(output)
            raise SystemExit(1)
print("PASS: actual Ansible evaluated four bounded Kuma redirect classification cases")
