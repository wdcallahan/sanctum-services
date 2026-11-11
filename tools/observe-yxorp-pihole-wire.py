#!/usr/bin/env python3
"""Read-only Pi-hole three-path HTTP root and /admin/ wire comparison.

All requests are bounded and keep their original Location header; unlike
Ansible's uri result, no relative redirect is resolved against the test
connection address. Output contains only statuses, metadata equality and
safe redirect kinds. No raw Location, content-type value, cookie, body,
query, credentials, error detail or unexpected hostname is printed.
"""
import http.client
import json
import sys
from urllib.parse import urlsplit

FRONTEND = "pihole.nexus.sanctum"
PATHS = (("root", "/"), ("admin", "/admin/"))


def request(host, port, path):
    connection = http.client.HTTPConnection(host, port, timeout=5)
    try:
        connection.request("GET", path, headers={"Host": FRONTEND})
        response = connection.getresponse()
        result = {
            "status": int(response.status),
            "location": response.getheader("Location", "") or "",
            "type": (response.getheader("Content-Type", "") or "")
                    .split(";", 1)[0].strip().lower(),
            "outcome": "http_response",
        }
        response.close()
        return result
    except (OSError, TimeoutError, http.client.HTTPException, ValueError):
        return {"status": -1, "location": "", "type": "", "outcome": "not_observed"}
    finally:
        connection.close()


def location_kind(location):
    if not location:
        return "absent"
    try:
        parsed = urlsplit(location)
        if parsed.scheme and parsed.hostname:
            return "absolute"
        if not parsed.scheme and not parsed.netloc:
            return "relative"
        return "other"
    except (ValueError, TypeError):
        return "invalid"


def compare(direct, incumbent, candidate):
    have_http = all(
        r["outcome"] == "http_response"
        for r in (direct, incumbent, candidate)
    )
    can_compare_redirect = bool(incumbent["location"] and candidate["location"])
    return {
        "direct_status": direct["status"],
        "incumbent_status": incumbent["status"],
        "candidate_status": candidate["status"],
        "all_three_have_http_response": have_http,
        "candidate_and_incumbent_status_equal":
            candidate["status"] == incumbent["status"] if have_http else "not_comparable",
        "candidate_and_direct_status_equal":
            candidate["status"] == direct["status"] if have_http else "not_comparable",
        "candidate_and_incumbent_media_type_equal":
            candidate["type"] == incumbent["type"] if have_http else "not_comparable",
        "direct_redirect_kind": location_kind(direct["location"]),
        "incumbent_redirect_kind": location_kind(incumbent["location"]),
        "candidate_redirect_kind": location_kind(candidate["location"]),
        "candidate_and_incumbent_raw_location_equal":
            (candidate["location"] == incumbent["location"])
            if can_compare_redirect else "not_comparable",
        "candidate_and_direct_raw_location_equal":
            (candidate["location"] == direct["location"])
            if direct["location"] and candidate["location"] else "not_comparable",
    }


def main(argv):
    if len(argv) != 6:
        raise SystemExit("Expected fixed direct, incumbent, stage host/port pairs")
    try:
        hosts = (argv[0], argv[2], argv[4])
        ports = (int(argv[1]), int(argv[3]), int(argv[5]))
    except ValueError:
        raise SystemExit("Port must be numeric")
    if not all(1 <= port <= 65535 for port in ports):
        raise SystemExit("Invalid port")
    observed = {}
    for label, path in PATHS:
        direct, incumbent, candidate = (
            request(host, port, path) for host, port in zip(hosts, ports)
        )
        observed[label] = compare(direct, incumbent, candidate)
    print(json.dumps({
        "frontend": FRONTEND,
        "paths": observed,
        "application_migrated_to_kvin": False,
        "configuration_changed": False,
        "raw_headers_bodies_and_urls_exposed": False,
        "limitation": (
            "Anonymous GET / and /admin/ wire statuses/MIME/redirect only. "
            "Pi-hole login, UI assets, resolver/DNS blocking, client settings, "
            "data restore, Kvin firewall and production cutover not tested."
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
