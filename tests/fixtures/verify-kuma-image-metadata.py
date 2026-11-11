#!/usr/bin/env python3
"""Exercise the production Kuma image-inspect predicates with real local Ansible.

Podman documents the image Id as a bare 64-character hex string, distinct
from the sha256:-prefixed Digest. Do not connect to Sanctum or run Podman.
"""
import json
from pathlib import Path
import subprocess
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[2]
play = yaml.safe_load((ROOT / "ansible/kuma-qualify-image.yml").read_text())[0]
guard = next(
    task for task in play["tasks"]
    if task["name"] == "Require native Linux ARM64 metadata and real loaded image"
)
full_id = "a" * 64
valid = {"Architecture": "arm64", "Os": "linux", "Id": full_id}
cases = {
    "documented_podman_id": ([valid], True),
    "incorrect_prefixed_id": ([{**valid, "Id": "sha256:" + full_id}], False),
    "truncated_id": ([{**valid, "Id": "a" * 63}], False),
    "wrong_architecture": ([{**valid, "Architecture": "amd64"}], False),
    "wrong_operating_system": ([{**valid, "Os": "windows"}], False),
    "missing_image": ([], False),
    "multiple_images": ([valid, valid], False),
}
plays = []
for name, (inspect, expected_acceptance) in cases.items():
    plays.append({
        "name": "Evaluate actual Kuma inspect guard: " + name,
        "hosts": "localhost",
        "connection": "local",
        "gather_facts": False,
        "vars": {
            "kuma_qualify_image_info": {"stdout": json.dumps(inspect)},
            "expected_acceptance": expected_acceptance,
        },
        "tasks": [
            {
                **guard,
                "register": "image_guard_result",
                "ignore_errors": True,
                "no_log": True,
            },
            {
                "name": "Verify real Ansible guard outcome: " + name,
                "ansible.builtin.assert": {
                    "that": [
                        "(image_guard_result.failed | default(false) | bool)"
                        " != (expected_acceptance | bool)"
                    ],
                },
            },
        ],
    })

with tempfile.TemporaryDirectory(prefix="kuma-image-metadata-") as td:
    playbook = Path(td) / "check.yml"
    playbook.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    run = subprocess.run(
        ["ansible-playbook", "-i", "localhost,", "-c", "local", str(playbook)],
        cwd=ROOT, capture_output=True, text=True, timeout=100,
    )
    if run.returncode or run.stdout.count("All assertions passed") < len(cases):
        print(run.stdout, run.stderr)
        raise SystemExit(run.returncode or "Actual Kuma metadata guard did not classify cases")
print("PASS: real Ansible accepts documented Podman Id and rejects"
      " prefixed/truncated IDs, wrong platform, missing or duplicate images")
