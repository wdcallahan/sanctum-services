#!/usr/bin/env python3
"""Execute the actual sanitized diagnostic report with synthetic Ansible data.

No connected hosts, DNS lookups, HTTP requests or application content.
This catches Jinja filter/variable mistakes syntax-check alone misses.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ansible/yxorp-kvin-yarn-transport-diagnose.yml"
play = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))[0]
report = next(x for x in play["tasks"] if x["name"].startswith("Report only"))
response_set = [
    {"item": {"name": "stage_health"}, "status": 200, "content": "yxorp-ready\n"},
    {"item": {"name": "stage_yarn"}, "status": 200, "content": "synthetic-body"},
    {"item": {"name": "origin_hostname"}, "status": -1,
     "msg": "Connection failure: timed out"},
    {"item": {"name": "origin_literal_ip"}, "status": 200,
     "content": "synthetic-body"},
]
fixture = [{
    "name": "Exercise production diagnostic result formatting against synthetic data",
    "hosts": "localhost",
    "gather_facts": False,
    "vars": {
        "kvin_yarn_diag_stage_unit": {"rc": 0},
        "kvin_yarn_diag_dns": {"rc": 0, "stdout_lines": [
            "192.168.1.110 STREAM yarn.inner.sanctum",
            "192.168.1.110 DGRAM yarn.inner.sanctum",
        ]},
        "kvin_yarn_diag_responses": {"results": response_set},
    },
    "tasks": [report],
}]

with tempfile.TemporaryDirectory(prefix="yxorp-yarn-report-") as directory:
    target = Path(directory) / "synthetic.yml"
    target.write_text(yaml.safe_dump(fixture, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", "localhost,", str(target), "-c", "local"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)

    checks = [
        '"stage_health_ready": true',
        '"stage_yarn_status": 200',
        '"direct_hostname_status": -1',
        '"direct_literal_ip_status": 200',
        '"host_resolution_includes_previously_accepted_ip": true',
        '"host_resolution_unique_ipv4_count": 1',
        '"stage_and_direct_hostname_bodies_equal_if_both_200": "not_comparable"',
        '"stage_and_direct_ip_bodies_equal_if_both_200": true',
        '"direct_hostname_outcome": "timeout"',
        '"configuration_changed": false',
    ]
    missing = [fragment for fragment in checks if fragment not in output]
    if missing:
        print("Synthetic report output failed expected fields:", missing)
        print(output)
        raise SystemExit(1)

print("PASS: real Ansible evaluated Kvin Yarn diagnostic output with synthetic mixed success/timeouts")
