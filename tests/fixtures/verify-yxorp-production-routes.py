#!/usr/bin/env python3
"""Run production YXORP projection with actual Ansible, never Kvin."""
from pathlib import Path
import subprocess
import tempfile

import yaml

ROOT=Path(__file__).resolve().parents[2]
source=yaml.safe_load((ROOT/"ansible/yxorp.yml").read_text())[0]
routes=yaml.safe_load((ROOT/"data/yxorp-routes.yml").read_text())["yxorp_routes"]
task=next(t for t in source["pre_tasks"]
          if t["name"]=="Render exactly eight production routes with Kuma and selected LinkStack backends")
select=next(t for t in source["pre_tasks"]
            if t["name"]=="Promote verified full production manifest for the existing YXORP role")
expected={r["hostname"]:dict(r) for r in routes}
for r in expected.values():
    r["enabled"]=True
expected["kuma.nexus.sanctum"]["upstream_host"]="127.0.0.1"
expected["kuma.nexus.sanctum"]["upstream_port"]=13001

for backend in ("kvin", "kvar"):
    selected=[dict(r) for r in expected.values()]
    for r in selected:
        if r["hostname"]=="dir.nexus.sanctum":
            r["upstream_host"]="127.0.0.1" if backend=="kvin" else "kvar.outer.sanctum"
            r["upstream_port"]=18081 if backend=="kvin" else 8081
    play={
      "name":"Synthetic execution of actual production route projection",
      "hosts":"localhost","gather_facts":False,
      "vars":{**source["vars"],"yxorp_routes":routes,
              "yxorp_production_linkstack_backend":backend,
              "expected_yxorp_routes":selected},
      "tasks":[task,select,{
        "name":"Demand exact eight names, Kuma target and reversible LinkStack alone",
        "ansible.builtin.assert":{"that":[
          "yxorp_routes == expected_yxorp_routes",
          "yxorp_routes | length == 8",
          "yxorp_routes | selectattr('enabled','equalto',true) | list | length == 8",
          "yxorp_routes | selectattr('hostname', 'equalto', 'kuma.nexus.sanctum') | map(attribute='upstream_host') | list == ['127.0.0.1']",
        ]}
      }]
    }
    with tempfile.TemporaryDirectory(prefix="yxorp-production-projection-") as tmp:
        path=Path(tmp)/"test.yml"
        path.write_text(yaml.safe_dump([play],sort_keys=False))
        p=subprocess.run(["ansible-playbook","-i","localhost,","-c","local",str(path)],
                         cwd=ROOT,capture_output=True,text=True,check=False,timeout=50)
        if p.returncode:
            print(p.stdout);print(p.stderr)
            raise SystemExit(p.returncode)
print("PASS: both Kvin and Kvar LinkStack targets project exactly; other six origins are unchanged")
