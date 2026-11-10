#!/usr/bin/env python3
"""Execute exact sixth-route projection and redirect metadata via real Ansible.

All hosts and URLs are synthetic fixture values. No live network or
service actions; synthetic GET responses are injected into report task.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
stage = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage.yml").read_text(encoding="utf-8"))[0]
probe = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage-kuma-probe.yml").read_text(encoding="utf-8"))[0]
routes = yaml.safe_load(
    (ROOT / "data/yxorp-routes.yml").read_text(encoding="utf-8"))["yxorp_routes"]
prefixes = (
    "Require approved Square staging", "Enable only Square alongside Yarn",
    "Require approved Prism staging", "Enable only Prism in addition",
    "Require Search staging", "Enable only Search in addition",
    "Require LinkStack stage", "Enable only interim LinkStack",
    "Require Kuma stage", "Enable only interim Kuma",
)
selected = [
    next(t for t in stage["pre_tasks"] if t["name"].startswith(name))
    for name in prefixes
]
report = next(t for t in probe["tasks"] if t["name"].startswith("Report only"))

cases = [
    ("all_six", (True, True, True, True, True),
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum",
      "search.nexus.sanctum", "dir.nexus.sanctum", "kuma.nexus.sanctum"]),
    ("previous_five", (True, True, True, True, False),
     ["yarn.nexus.sanctum", "square.nexus.sanctum", "joule.nexus.sanctum",
      "search.nexus.sanctum", "dir.nexus.sanctum"]),
    ("default_yarn", (False, False, False, False, False),
     ["yarn.nexus.sanctum"]),
]
plays = []
for name, flags, enabled in cases:
    plays.append({
        "name": "Evaluate selected Kvin stage route set " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_routes": routes,
            **dict(zip(
                ("yxorp_stage_square_approved", "yxorp_stage_prism_approved",
                 "yxorp_stage_search_approved", "yxorp_stage_dir_approved",
                 "yxorp_stage_kuma_approved"), flags)),
            "expected": enabled,
        },
        "tasks": selected + [{
            "name": "Verify exact enabled set without additional legacy hosts",
            "ansible.builtin.assert": {
                "that": [
                    "(yxorp_routes | selectattr('enabled', 'equalto', true) | map(attribute='hostname') | list) == expected",
                    "(yxorp_routes | selectattr('enabled', 'equalto', false) | list | length) == (8 - expected | length)",
                ]
            },
        }],
    })

# Use an invented .invalid synthetic backend hostname, deliberately
# different port normalization to prove classification doesn't demand
# candidate/direct Location equality when matching NPM is the goal.
scenarios = (
    ("port_changed",
     "http://example.invalid:3001/dashboard",
     "http://example.invalid/dashboard",
     "http://example.invalid:3001/dashboard",
     False, "declared_backend_port", "no_explicit_port", True),
    ("incumbent_equal",
     "http://example.invalid:3001/dashboard",
     "http://example.invalid/dashboard",
     "http://example.invalid/dashboard",
     True, "no_explicit_port", "no_explicit_port", True),
    ("no_redirect",
     "", "", "",
     "not_comparable", "not_comparable", "not_comparable", "not_comparable"),
)
for name, direct, incumbent, candidate, equal, cport, nport, path_equal in scenarios:
    status = 200 if name == "no_redirect" else 302
    observations = {
        "results": [
            {"item": {"name": key}, "status": status, "content_type": "text/html",
             **({"location": location} if location else {})}
            for key, location in (
                ("direct_backend", direct),
                ("incumbent_kvar_npm", incumbent),
                ("candidate_kvin_stage", candidate),
            )
        ]
    }
    plays.append({
        "name": "Kuma report synthetic " + name,
        "hosts": "report_" + name,
        "gather_facts": False,
        "vars": {
            "yxorp_kuma_stage_responses": observations,
        },
        "tasks": [report, {
            "name": "Assert redirected and nonredirected safe Kuma metadata",
            "ansible.builtin.assert": {
                "that": [
                    "report_result.msg.candidate_redirect_equals_incumbent == expected_equal",
                    "report_result.msg.candidate_redirect_port_class == expected_candidate_port",
                    "report_result.msg.incumbent_redirect_port_class == expected_incumbent_port",
                    "report_result.msg.candidate_redirect_path_equals_incumbent == expected_path",
                ]
            },
            "vars": {
                "expected_equal": equal,
                "expected_candidate_port": cport,
                "expected_incumbent_port": nport,
                "expected_path": path_equal,
            },
        }],
    })
    # debug does not register unless explicitly set on the injected
    # report task. This doesn't change the role or production playbook.
    plays[-1]["tasks"][0] = {**report, "register": "report_result"}

with tempfile.TemporaryDirectory(prefix="yxorp-kuma-stage-") as tmp:
    folder = Path(tmp)
    inventory = folder / "hosts.yml"
    playbook = folder / "fixture.yml"
    hostnames = [c[0] for c in cases] + ["report_" + c[0] for c in scenarios]
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            name: {"ansible_connection": "local"} for name in hostnames
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
    for required in (
        '"candidate_status": 302',
        '"candidate_redirect_port_class": "declared_backend_port"',
        '"incumbent_redirect_port_class": "no_explicit_port"',
        '"candidate_redirect_path_equals_incumbent": true',
        '"candidate_redirect_equals_incumbent": false',
        '"candidate_redirect_equals_incumbent": "not_comparable"',
        '"application_migrated_to_kvin": false',
    ):
        if required not in output:
            print("Missing Kuma synthetic safe field:", required)
            print(output)
            raise SystemExit(1)
print("PASS: Kvin route states and Kuma distinct-port/equal/non-redirect synthetic reports")
