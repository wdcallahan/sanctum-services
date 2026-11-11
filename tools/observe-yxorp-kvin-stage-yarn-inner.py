#!/usr/bin/env python3
"""Bounded read-only real-wire acceptance for eighth Yarn NPM vhost on Kvin.

Compare raw HTTP from the old origin and the Kvin stage using the same
Host: yarn.inner.sanctum, then check new yarn.nexus.sanctum remains live
and an unmatched Host is denied. Kvar NPM's old upstream path times out;
do NOT turn absence of an incumbent HTTP response into a false parity
requirement. Print no response bodies, raw headers, cookies or redirects.
"""
import hashlib
import http.client
import json
import socket
from urllib.parse import urlsplit

OLD = "yarn.inner.sanctum"
NEW = "yarn.nexus.sanctum"
UNKNOWN = "yxorp-unmatched-observer.invalid"
MAX_BYTES = 512 * 1024


def get(address, host_header):
    conn = http.client.HTTPConnection(address, 80, timeout=6)
    try:
        conn.request("GET", "/", headers={"Host": host_header, "Connection": "close"})
        resp = conn.getresponse()
        status = int(resp.status)
        mime = (resp.getheader("Content-Type", "") or "").split(";", 1)[0].strip().lower()
        location = resp.getheader("Location", "") or ""
        data = resp.read(MAX_BYTES + 1)
        complete = len(data) <= MAX_BYTES
        return {
            "outcome": "http_response",
            "status": status,
            "mime": mime,
            "raw_location": location,
            "body_complete": complete,
            "body_size": len(data) if complete else -1,
            "body_sha256": hashlib.sha256(data).digest() if complete else None,
        }
    except http.client.RemoteDisconnected:
        return {"outcome": "closed_without_http"}
    except (socket.timeout, TimeoutError):
        return {"outcome": "timeout"}
    except (OSError, http.client.HTTPException, ValueError):
        return {"outcome": "no_http_response"}
    finally:
        conn.close()


def location_kind(value):
    if not value:
        return "absent"
    try:
        parsed = urlsplit(value)
        if parsed.scheme and parsed.hostname:
            return "absolute"
        if not parsed.scheme and not parsed.netloc:
            return "relative"
        return "other"
    except ValueError:
        return "invalid"


def public(result):
    return {
        "outcome": result["outcome"],
        "status": result.get("status", -1),
        "body_complete": result.get("body_complete", False),
        "body_bytes": result.get("body_size", -1),
        "redirect_kind": location_kind(result.get("raw_location", "")),
    }


def comparisons(direct, staged_old, staged_new, unmatched):
    d_http = direct["outcome"] == "http_response"
    s_http = staged_old["outcome"] == "http_response"
    both = d_http and s_http
    bounded = both and direct["body_complete"] and staged_old["body_complete"]
    redirect_compare = both and bool(
        direct["raw_location"] or staged_old["raw_location"]
    )
    return {
        "old_origin_http_200": d_http and direct["status"] == 200,
        "old_stage_http_200": s_http and staged_old["status"] == 200,
        "new_stage_http_200": staged_new["outcome"] == "http_response"
        and staged_new["status"] == 200,
        "old_status_equals_direct": (
            staged_old["status"] == direct["status"]
            if both else "not_comparable"
        ),
        "old_media_type_equals_direct": (
            staged_old["mime"] == direct["mime"] if both else "not_comparable"
        ),
        "old_complete_body_identical_to_direct": (
            staged_old["body_sha256"] == direct["body_sha256"]
            and staged_old["body_size"] == direct["body_size"]
            if bounded else "not_comparable"
        ),
        "old_redirect_exact_wire_equals_direct": (
            staged_old["raw_location"] == direct["raw_location"]
            if redirect_compare else "not_comparable"
        ),
        "unknown_host_denied_without_http_response":
            unmatched["outcome"] == "closed_without_http",
    }


def main():
    # No input arguments: fixed paths and Host headers are source-owned.
    direct = get("192.168.1.110", OLD)
    staged_old = get("127.0.0.1", OLD)
    staged_new = get("127.0.0.1", NEW)
    unmatched = get("127.0.0.1", UNKNOWN)
    result = {
        "observer": "kvin.outer.sanctum",
        "frontend": OLD,
        "direct_origin": public(direct),
        "staged_existing_name": public(staged_old),
        "staged_new_name": public(staged_new),
        "unmatched_stage": public(unmatched),
        "checks": comparisons(direct, staged_old, staged_new, unmatched),
        "old_incumbent_http_not_qualified": True,
        "application_or_dns_migrated": False,
        "configuration_changed": False,
        "raw_http_headers_bodies_and_credentials_exposed": False,
        "limitation": (
            "Anonymous bounded GET / with raw Location and complete-body equality "
            "up to 512 KiB from Kvin. No attempt to claim broken incumbent "
            "Kvar NPM parity; no authenticated client use, LAN firewall, "
            "application restore, DNS or production cutover."
        ),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
