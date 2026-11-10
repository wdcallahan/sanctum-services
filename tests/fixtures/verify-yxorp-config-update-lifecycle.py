#!/usr/bin/env python3
"""Exercise the actual YXORP mount-drift decision and service-state expression.

Synthetic isolated local Ansible hosts; no Podman, systemd, or Sanctum contact.
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
detect = next(task for task in role
              if task["name"] ==
              "Detect an obsolete mounted Nginx file even when host files are unchanged")
state_expression = unit["state"]

HOST_CONFIG = "server_name yarn.nexus.sanctum;\nserver_name square.nexus.sanctum;\n"
HOST_BASE64 = "c2VydmVyX25hbWUgeWFybi5uZXh1cy5zYW5jdHVtOwpzZXJ2ZXJfbmFtZSBzcXVhcmUubmV4dXMuc2FuY3R1bTsK"
YARN_ONLY = "server_name yarn.nexus.sanctum;\n"

# config_changed, quadlet_changed, old mounted content, container visible,
# expected stale flag, desired systemd state
scenarios = [
    ("only_config_changed", True, False, YARN_ONLY, True, True, "restarted"),
    ("only_quadlet_changed", False, True, HOST_CONFIG, True, False, "restarted"),
    ("both_changed", True, True, HOST_CONFIG, True, False, "restarted"),
    ("unchanged_and_aligned", False, False, HOST_CONFIG, True, False, "started"),
    ("already_stale_but_host_unchanged", False, False, YARN_ONLY, True, True, "restarted"),
    ("stopped_container_unchanged", False, False, "", False, False, "started"),
]
inventory = {"all": {"hosts": {
    name: {"ansible_connection": "local"}
    for name, *_ in scenarios
}}}
plays = []
for name, config_changed, quadlet_changed, mounted_text, running, stale, expected in scenarios:
    plays.append({
        "name": f"Evaluate actual YXORP remount lifecycle: {name}",
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_config_publish": {"changed": config_changed},
            "yxorp_quadlet_publish": {"changed": quadlet_changed},
            "yxorp_prestart_host_config": {"content": HOST_BASE64},
            "yxorp_prestart_container_config": {
                "rc": 0 if running else 1,
                "stdout": mounted_text,
            },
            "target_state": state_expression,
            "expected_state": expected,
            "expected_stale": stale,
        },
        "tasks": [
            detect,
            {
                "name": "Require exact service action and mount-drift detection",
                "ansible.builtin.assert": {
                    "that": [
                        "yxorp_mount_stale | bool == expected_stale",
                        "target_state == expected_state",
                    ],
                    "fail_msg": "YXORP mount-drift or state decision was incorrect",
                },
            },
        ],
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

print(
    "PASS: actual Ansible mount drift + systemd state expressions cover "
    f"{len(scenarios)} independent scenarios including prior stale drift"
)
