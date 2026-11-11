#!/usr/bin/env python3
"""Bounded, read-only production YXORP peer-client observation from Peanut.

Peanut is a separate Arcane LAN host. Tests both Kvin addresses present
in Maintenance source contracts without depending on Nexus DNS's old
Kvar mapping. Does not publish DNS, open firewalls, or return page data.
"""
import http.client
import json
import socket

PROXY_ADDRESSES = ("192.168.0.192", "192.168.1.192")
KUMA_HOST = "kuma.nexus.sanctum"
YARN_HOST = "yarn.nexus.sanctum"


def lookup_kvin():
    try:
        addresses = sorted({
            info[4][0] for info in socket.getaddrinfo(
                "kvin.outer.sanctum", 80, family=socket.AF_INET,
                type=socket.SOCK_STREAM,
            )
        })
        return {"outcome": "resolved", "addresses": addresses}
    except (OSError, ValueError):
        return {"outcome": "failed", "addresses": []}


def probe(address, hostname):
    conn = http.client.HTTPConnection(address, 80, timeout=6)
    try:
        conn.request("GET", "/", headers={
            "Host": hostname, "Connection": "close",
        })
        res = conn.getresponse()
        # Bound the read, never emit body, headers or cookies.
        res.read(65537)
        return {"outcome": "http", "status": int(res.status)}
    except (socket.timeout, TimeoutError):
        return {"outcome": "timeout", "status": None}
    except ConnectionRefusedError:
        return {"outcome": "refused", "status": None}
    except http.client.RemoteDisconnected:
        return {"outcome": "closed_without_http", "status": None}
    except (OSError, http.client.HTTPException, ValueError):
        return {"outcome": "transport_error", "status": None}
    finally:
        conn.close()


def main():
    outcome = {}
    for address in PROXY_ADDRESSES:
        kuma = probe(address, KUMA_HOST)
        yarn = probe(address, YARN_HOST)
        outcome[address] = {
            "kuma": kuma,
            "yarn": yarn,
            "qualified_http": kuma["outcome"] == "http"
            and kuma["status"] in (200, 302)
            and yarn["outcome"] == "http"
            and yarn["status"] == 200,
        }
    dns = lookup_kvin()
    qualified = [addr for addr in PROXY_ADDRESSES
                 if outcome[addr]["qualified_http"]]
    result = {
        "observer": "peanut.arcane.sanctum",
        "production_proxy": "sanctum-yxorp.service",
        "kvin_name_resolution": dns,
        "direct_address_results": outcome,
        "qualified_peer_client_addresses": qualified,
        "proven_non_kvin_http_reachability": bool(qualified),
        "named_nexus_dns_cutover_accepted": False,
        "browser_login_or_websocket_accepted": False,
        "configuration_changed": False,
        "kvar_or_dns_or_firewall_changed": False,
        "raw_headers_bodies_credentials_exposed": False,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
