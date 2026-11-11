#!/usr/bin/env python3
"""Observe only raw HTTP Location *classes* across three Kuma paths.

Do not emit a Location, hostname, query, body, cookie, raw exception or
unrecognized network value. HTTPConnection reads the response header
directly, without redirect following or urllib/Ansible URI normalization.

Usage: observe-yxorp-kuma-wire.py backend-host backend-port
       incumbent-host incumbent-port candidate-host candidate-port

Ansible play fixes all six operands and runs with no_log. Test suites may
provide loopback synthetic endpoints. No filesystem or service mutations.
"""
import http.client
import json
import sys
from urllib.parse import urlsplit

FRONTEND = "kuma.nexus.sanctum"
KNOWN = {
    "kuma.nexus.sanctum": "frontend",
    "kvar.outer.sanctum": "kvar_backend_host",
    "kvin.outer.sanctum": "kvin_host",
    "127.0.0.1": "loopback",
    "localhost": "loopback",
}


def observe(host, port, forwarded=False):
    conn = http.client.HTTPConnection(host, port, timeout=6)
    headers = {"Host": FRONTEND}
    if forwarded:
        headers.update({
            "X-Real-IP": "127.0.0.1",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Host": FRONTEND,
            "X-Forwarded-Proto": "http",
            "X-Forwarded-Scheme": "http",
        })
    try:
        conn.request("GET", "/", headers=headers)
        response = conn.getresponse()
        status = int(response.status)
        loc = response.getheader("Location", "") or ""
        response.close()
        return {"status": status, "location": loc, "outcome": "http_response"}
    except (TimeoutError, OSError, http.client.HTTPException, ValueError):
        return {"status": -1, "location": "", "outcome": "not_observed"}
    finally:
        conn.close()


def classify(record):
    location = record["location"]
    if not location:
        return {"status": record["status"], "outcome": record["outcome"],
                "host_class": "absent", "port_class": "absent",
                "absolute": False}
    try:
        parsed = urlsplit(location)
        host = (parsed.hostname or "").lower()
        port = parsed.port
        absolute = bool(parsed.scheme and host)
        if not host:
            host_class = "relative"
        else:
            host_class = KNOWN.get(host, "other")
        if not host:
            port_class = "not_comparable"
        elif port is None:
            port_class = "no_explicit_port"
        elif port == 80:
            port_class = "stage_http_port_80"
        elif port == 3001:
            port_class = "kuma_backend_port_3001"
        else:
            port_class = "other_explicit_port"
        return {"status": record["status"], "outcome": record["outcome"],
                "host_class": host_class, "port_class": port_class,
                "absolute": absolute}
    except (ValueError, TypeError):
        return {"status": record["status"], "outcome": record["outcome"],
                "host_class": "invalid", "port_class": "invalid",
                "absolute": False}


def main(argv):
    if len(argv) != 6:
        raise SystemExit("Need exactly three fixed host/port pairs")
    hosts = (argv[0], argv[2], argv[4])
    try:
        ports = tuple(int(v) for v in (argv[1], argv[3], argv[5]))
    except ValueError:
        raise SystemExit("Port arguments must be numeric")
    if not all(1 <= port <= 65535 for port in ports):
        raise SystemExit("Invalid port")
    direct = observe(hosts[0], ports[0])
    incumbent = observe(hosts[1], ports[1])
    candidate = observe(hosts[2], ports[2])
    # Synthetic fixed forwarded-header request to the SAME known backend;
    # determines whether upstream Location generation changes based on
    # standard X-Forwarded-* headers, without touching proxy configuration.
    forwarded_direct = observe(hosts[0], ports[0], forwarded=True)
    records = {
        "direct_wire": classify(direct),
        "incumbent_wire": classify(incumbent),
        "candidate_wire": classify(candidate),
        "direct_with_proxy_headers_wire": classify(forwarded_direct),
        "candidate_wire_equals_incumbent_wire": (
            candidate["location"] == incumbent["location"]
            if candidate["location"] and incumbent["location"]
            else "not_comparable"
        ),
        "candidate_wire_equals_direct_wire": (
            candidate["location"] == direct["location"]
            if candidate["location"] and direct["location"]
            else "not_comparable"
        ),
        "direct_changes_when_forwarded_headers_present": (
            forwarded_direct["location"] != direct["location"]
            if forwarded_direct["location"] and direct["location"]
            else "not_comparable"
        ),
        "raw_location_values_exposed": False,
        "configuration_changed": False,
    }
    print(json.dumps(records, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
