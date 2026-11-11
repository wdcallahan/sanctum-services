#!/usr/bin/env python3
"""Bounded read-only transport/status of OLD yarn.inner.sanctum route.

Caller fixes known hostname/IP and ports. Does not use URI normalization,
follow redirects, log bodies, reveal headers, credentials or raw errors.
This does not establish whether any clients still use the legacy name.
"""
import http.client
import json
import sys
from urllib.parse import urlsplit

ORIGIN_IP = "192.168.1.110"
ORIGIN_NAME = "yarn.inner.sanctum"
INCUMBENT = "kvar.outer.sanctum"
STAGE = "127.0.0.1"
NEW_FRONTEND = "yarn.nexus.sanctum"


def observe(address, host_header):
    connection = http.client.HTTPConnection(address, 80, timeout=6)
    try:
        connection.request("GET", "/", headers={"Host": host_header})
        response = connection.getresponse()
        status = int(response.status)
        loc = response.getheader("Location", "") or ""
        media = (response.getheader("Content-Type", "") or "").split(";", 1)[0].strip().lower()
        response.close()
        kind = "absent"
        if loc:
            try:
                part = urlsplit(loc)
                kind = "absolute" if part.scheme and part.hostname else (
                    "relative" if not part.scheme and not part.netloc else "other")
            except (ValueError, TypeError):
                kind = "invalid"
        return {"outcome": "http_response", "http_status": status,
                "redirect_kind": kind, "media_type": media}
    except (TimeoutError, OSError, http.client.HTTPException, ValueError) as err:
        # Classify stable network failures; do not expose raw exception or DNS.
        msg = str(type(err).__name__).lower()
        if isinstance(err, (TimeoutError,)): outcome = "timeout"
        elif "gaierror" in msg: outcome = "resolution_failure"
        elif "refused" in msg or "connectionrefusederror" in msg: outcome = "connect_failure"
        else: outcome = "no_http_response"
        return {"outcome": outcome, "http_status": -1,
                "redirect_kind": "not_observed", "media_type": ""}
    finally:
        connection.close()


def main():
    # No caller-provided addresses: all four destinations are source-owned.
    if len(sys.argv) != 1:
        raise SystemExit("No arguments accepted")
    paths = {
        "legacy_direct_by_ip": observe(ORIGIN_IP, ORIGIN_NAME),
        "legacy_direct_by_dns_name": observe(ORIGIN_NAME, ORIGIN_NAME),
        "legacy_through_incumbent_npm": observe(INCUMBENT, ORIGIN_NAME),
        "new_name_through_accepted_kvin_stage": observe(STAGE, NEW_FRONTEND),
        "legacy_host_header_against_origin_ip": observe(ORIGIN_IP, NEW_FRONTEND),
    }
    public = {}
    for key, item in paths.items():
        public[key] = {
            "outcome": item["outcome"],
            "http_status": item["http_status"],
            "redirect_kind": item["redirect_kind"],
            "media_type_present": bool(item["media_type"]),
        }
    a = paths["legacy_direct_by_ip"]
    b = paths["legacy_through_incumbent_npm"]
    c = paths["legacy_host_header_against_origin_ip"]
    public["legacy_origin_and_incumbent_status_equal_if_http"] = (
        a["http_status"] == b["http_status"]
        if a["outcome"] == "http_response" and b["outcome"] == "http_response"
        else "not_comparable"
    )
    public["origin_legacy_and_new_host_header_status_equal_if_http"] = (
        a["http_status"] == c["http_status"]
        if a["outcome"] == "http_response" and c["outcome"] == "http_response"
        else "not_comparable"
    )
    print(json.dumps({
        "observer": "kvin.outer.sanctum",
        "frontend": ORIGIN_NAME,
        "legacy_manifest_enabled": False,
        "new_kvin_legacy_route_activated": False,
        "probes": public,
        "sensitive_response_values_exposed": False,
        "configuration_changed": False,
        "limitation": (
            "One-off anonymous GET / reachability only, from Kvin. "
            "Does not establish traffic from Kvar NPM namespace, client usage, "
            "content identity, sessions, retirement suitability, DNS authority "
            "or production cutover."
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
