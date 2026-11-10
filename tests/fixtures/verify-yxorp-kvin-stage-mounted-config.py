#!/usr/bin/env python3
"""Execute the exact stage mount-comparison report against fake Ansible data.

No connections to Sanctum, Podman, DNS, HTTP, or real host files.
"""
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ansible/yxorp-kvin-stage-mounted-config-observe.yml"
report = next(x for x in yaml.safe_load(SOURCE.read_text(encoding="utf-8"))[0]["tasks"]
              if x["name"].startswith("Report only"))
SQUARE_AND_YARN = "c2VydmVyX25hbWUgeWFybi5uZXh1cy5zYW5jdHVtOwpzZXJ2ZXJfbmFtZSBzcXVhcmUubmV4dXMuc2FuY3R1bTsK"
YARN_ONLY = "server_name yarn.nexus.sanctum;\n"

def inputs(container_text, square_rc, square_http):
    return {
        "yxorp_stage_unit": {"rc": 0},
        "yxorp_host_active": {"content": SQUARE_AND_YARN},
        "yxorp_host_candidate": {"content": SQUARE_AND_YARN},
        "yxorp_container_config": {"rc": 0, "stdout": container_text},
        "yxorp_square_curl": {"rc": square_rc, "stdout": square_http},
        "yxorp_unknown_curl": {"rc": 52, "stdout": "000"},
    }

plays = [
    {
        "name": "Simulate stale inode mounted inside Nginx container",
        "hosts": "mount_stale",
        "gather_facts": False,
        "vars": inputs(YARN_ONLY, 52, "000"),
        "tasks": [report],
    },
    {
        "name": "Simulate correctly updated Nginx file mount",
        "hosts": "mount_aligned",
        "gather_facts": False,
        "vars": inputs(
            "server_name yarn.nexus.sanctum;\nserver_name square.nexus.sanctum;\n",
            0, "302"),
        "tasks": [report],
    },
]

with tempfile.TemporaryDirectory(prefix="yxorp-config-mount-") as temporary:
    folder = Path(temporary)
    inventory = folder / "hosts.yml"
    inventory.write_text(yaml.safe_dump({
        "all": {"hosts": {
            "mount_stale": {"ansible_connection": "local"},
            "mount_aligned": {"ansible_connection": "local"},
        }}
    }), encoding="utf-8")
    path = folder / "fixture.yml"
    path.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(path)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    expected = [
        '"host_active_has_square_vhost": true',
        '"candidate_has_square_vhost": true',
        '"container_mount_has_yarn_vhost": true',
        '"container_mount_has_square_vhost": false',
        '"host_active_equals_container_mount": false',
        '"container_mount_has_square_vhost": true',
        '"host_active_equals_container_mount": true',
        '"square_curl_exit_code": 52',
        '"square_curl_http_code": "000"',
        '"square_curl_exit_code": 0',
        '"square_curl_http_code": "302"',
        '"unknown_host_curl_exit_code": 52',
        '"no_service_or_config_change": true',
    ]
    missing = [fragment for fragment in expected if fragment not in output]
    if missing:
        print("Missing synthetic output checks:", missing)
        print(output)
        raise SystemExit(1)
print("PASS: exact mount-inspection report distinguished stale and current synthetic inode views")
