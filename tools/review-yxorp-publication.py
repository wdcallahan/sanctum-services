#!/usr/bin/env python3
"""Compare Maintenance's *redacted* NPM route projection to proposed YXORP source.

Read-only. No router, proxy, DNS or application is contacted, and this tool
never writes changes or assumes default NPM routes prove complete parity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml

HOST = re.compile(r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$")
SCHEMES = {"http", "https"}


def compare(report: dict[str, Any], declared: dict[str, Any]) -> dict[str, Any]:
    root = report.get("kvar_rootful", {})
    if root.get("host") != "kvar.outer.sanctum" or root.get("scope") != "rootful":
        raise ValueError("Report lacks the exact Kvar rootful observation")
    proxies = [c for c in root.get("containers", []) if "proxy_routes" in c]
    if len(proxies) != 1:
        raise ValueError("Expected exactly one observed rootful NPM route owner")
    owner = proxies[0]
    observed_set = owner["proxy_routes"]
    if observed_set.get("status") != "observed":
        raise ValueError("NPM proxy-host files were not observed completely")
    observations: dict[str, dict[str, Any]] = {}
    partial: list[str] = []
    for row in observed_set.get("routes", []):
        fname = str(row.get("file", "unknown"))
        upstream = row.get("default_upstream") or {}
        names = upstream.get("server_names")
        scheme = upstream.get("forward_scheme")
        host = upstream.get("server")
        port = upstream.get("port")
        if (row.get("status") != "projected" or row.get("duplicate_fields")
                or not isinstance(names, list) or not names
                or scheme not in SCHEMES or not isinstance(host, str)
                or not HOST.fullmatch(host) or not str(port).isdigit()
                or not 1 <= int(port) <= 65535):
            partial.append(fname)
            continue
        for name in names:
            if not isinstance(name, str) or not HOST.fullmatch(name):
                partial.append(fname + ":unsupported_server_name")
                continue
            if name in observations:
                partial.append(fname + ":duplicate_hostname")
                continue
            observations[name] = {
                "upstream_scheme": scheme,
                "upstream_host": host,
                "upstream_port": int(port),
                "source_file": fname,
                "source_sha256": row.get("sha256"),
            }
    planned: dict[str, dict[str, Any]] = {}
    for item in declared.get("yxorp_routes", []):
        name = item["hostname"]
        if name in planned:
            raise ValueError("Duplicate desired hostname " + name)
        planned[name] = item
    mismatches: list[dict[str, Any]] = []
    for name in sorted(set(planned) & set(observations)):
        actual = observations[name]
        expected = planned[name]
        fields = ["upstream_scheme", "upstream_host", "upstream_port"]
        difference = {field: {"observed": actual[field],
                              "proposed": expected[field]}
                      for field in fields if actual[field] != expected[field]}
        if difference:
            mismatches.append({"hostname": name, "differences": difference,
                               "enabled": expected["enabled"]})
    return {
        "schema": "sanctum-yxorp-npm-comparison/v1",
        "observation_scope": "generated_NPM_default_upstreams_only",
        "source_host": "kvar.outer.sanctum",
        "observed_host_count": len(observations),
        "proposed_host_count": len(planned),
        "observed_not_in_proposal": sorted(set(observations) - set(planned)),
        "proposal_not_in_observation": sorted(set(planned) - set(observations)),
        "proposed_upstream_differences": mismatches,
        "partial_or_unsupported_files": sorted(set(partial)),
        "observed_default_routes": observations,
        "review_required": bool(partial or mismatches
                                or set(planned) != set(observations)),
        "limitations": [
            "This observer omits custom locations, includes, headers, access policy, redirects and real client behavior.",
            "A match does not prove Nginx behavior or end-to-end application acceptance.",
            "No configuration has been changed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True,
                        help="Maintenance reports/cutover-service-publications.json")
    parser.add_argument("--declared", type=Path,
                        default=Path("data/yxorp-routes.yml"))
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf8"))
        declared = yaml.safe_load(args.declared.read_text(encoding="utf8"))
        result = compare(report, declared)
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        print("Refused incomplete/invalid route evidence: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
