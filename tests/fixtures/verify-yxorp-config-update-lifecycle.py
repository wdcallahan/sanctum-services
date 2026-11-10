#!/usr/bin/env python3
"""Exercise the role's exact service-state expression with synthetic Ansible facts.

No service commands and no Sanctum host contacts.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
role = yaml.safe_load(
    (ROOT / "ansible/roles/yxorp/tasks/main.yml").read_text(encoding="utf-8"))
unit = next(task["ansible.builtin.systemd_service"] for task in role
            if task["name"] == "Start or reconcile YXORP using the system service manager")
state_expression = unit["state"]

scenarios = [
    ("only_config_changed", True, False, "restarted"),
    ("only_quadlet_changed", False, True, "restarted"),
    ("both_changed", True, True, "restarted"),
    ("neither_changed", False, False, "started"),
]
inventory = {"all": {"hosts": {name: {"ansible_connection": "local"}
                                for name, _, _, _ in scenarios}}}
plays = []
for name, config_changed, quadlet_changed, expected in scenarios:
    plays.append({
        "name": f"Evaluate actual YXORP remount lifecycle {name}",
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_config_publish": {"changed": config_changed},
            "yxorp_quadlet_publish": {"changed": quadlet_changed},
            "target_state": state_expression,
            "expected_state": expected,
        },
        "tasks": [{
            "name": "Require exact service action for this state",
            "ansible.builtin.assert": {
                "that": ["target_state == expected_state"],
                "fail_msg": "YXORP lifecycle state expression did not match expected behavior",
            }
        }],
    })

with tempfile.TemporaryDirectory(prefix="yxorp-state-contract-") as temp:
    root = Path(temp)
    inv = root / "inventory.yml"
    play = root / "scenarios.yml"
    inv.write_text(yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8")
    play.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inv), str(play)],
        cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)
    if result.stdout.count("All assertions passed") != len(scenarios):
        print(result.stdout)
        raise SystemExit("Missing real-Ansible scenario assertions")

print("PASS: actual YXORP state expression restarts on config/Quadlet changes and stays idempotent otherwise")
