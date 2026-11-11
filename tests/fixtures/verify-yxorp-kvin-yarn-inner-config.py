#!/usr/bin/env python3
"""Run the ACTUAL eighth-Yarn mounted-config predicates in local real Ansible.

This catches subtly over-escaped regex and count errors which syntax-only
checks cannot see. No Sanctum hosts, Podman containers or DNS are contacted.
"""
import base64
from pathlib import Path
import subprocess
import tempfile

from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[2]
probe = yaml.safe_load(
    (ROOT / "ansible/yxorp-kvin-stage-yarn-inner-probe.yml").read_text()
)[0]
classifier = next(
    task for task in probe["tasks"]
    if task["name"] == "Classify the installed eighth Yarn route without disclosing config"
)
routes = yaml.safe_load((ROOT / "data/yxorp-routes.yml").read_text())["yxorp_routes"]
for route in routes:
    route["enabled"] = True
template = Environment(
    loader=FileSystemLoader(str(ROOT / "ansible/roles/yxorp/templates")),
    undefined=StrictUndefined,
).get_template("nginx.conf.j2")
correct = template.render(yxorp_routes=routes)

old = "server_name yarn.inner.sanctum;"
new = "server_name yarn.nexus.sanctum;"
backend = "proxy_pass http://192.168.1.110:80;"
for marker in (old, new, backend):
    if correct.count(marker) != 1:
        raise SystemExit("Incorrect base synthetic Nginx config marker: " + marker)

cases = {
    "correct": (correct, correct, [True, True, True, True]),
    "missing_old": (correct, correct.replace(old, "server_name yarn.unexpected.sanctum;"),
                    [False, False, True, True]),
    "duplicate_old": (correct, correct.replace(old, old + "\n    " + old),
                      [False, False, True, True]),
    "missing_new": (correct, correct.replace(new, "server_name yarn.missing.sanctum;"),
                    [False, True, False, True]),
    "wrong_backend": (correct, correct.replace(backend, "proxy_pass http://192.168.1.111:80;"),
                      [False, True, True, False]),
    "mount_drift": (correct, correct + "\n# harmless drift\n",
                    [False, True, True, True]),
}
plays = []
labels = [
    "published_equals_container_mount",
    "old_vhost_present_once",
    "new_vhost_present_once",
    "exact_old_backend_present_once",
]
for name, (host_config, mounted_config, expectations) in cases.items():
    plays.append({
        "name": "Evaluate actual Yarn classifier for " + name,
        "hosts": name,
        "gather_facts": False,
        "vars": {
            "yxorp_yarn_eighth_host_config": {
                "content": base64.b64encode(host_config.encode("utf-8")).decode("ascii")
            },
            "yxorp_yarn_eighth_container_config": {"stdout": mounted_config},
            "expected": dict(zip(labels, expectations)),
        },
        "tasks": [
            classifier,
            {
                "name": "Assert actual classifier matches expected " + name,
                "ansible.builtin.assert": {
                    "that": [
                        "(yxorp_yarn_eighth_configuration." + label
                        + " | bool) == expected." + label
                        for label in labels
                    ]
                },
            },
        ],
    })

with tempfile.TemporaryDirectory(prefix="yxorp-yarn-config-predicates-") as td:
    root = Path(td)
    inventory, playbook = root / "hosts.yml", root / "playbook.yml"
    inventory.write_text(
        yaml.safe_dump({"all": {"hosts": {
            key: {"ansible_connection": "local"} for key in cases
        }}}, sort_keys=False), encoding="utf-8",
    )
    playbook.write_text(yaml.safe_dump(plays, sort_keys=False), encoding="utf-8")
    run = subprocess.run(
        ["ansible-playbook", "-i", str(inventory), str(playbook)],
        cwd=ROOT, text=True, capture_output=True, timeout=100,
    )
    if run.returncode or run.stdout.count("All assertions passed") < len(cases):
        print(run.stdout, run.stderr)
        raise SystemExit(run.returncode or "Live Ansible config classification incomplete")
print("PASS: real Ansible exact Yarn line counts, missing/duplicate routes, "
      "wrong upstream and host/container drift")
