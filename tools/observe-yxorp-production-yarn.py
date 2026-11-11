#!/usr/bin/env python3
"""Read-only production YXORP Yarn path classification, from Kvin.

Compare the same live Host header through rootful host-network Nginx with
direct Yarn-by-IP and Yarn-by-DNS. No application source changes, no
passwords, no raw headers/bodies, and no Kvar service contact.
"""
import http.client
import json
import socket

ORIGIN_NAME = "yarn.inner.sanctum"
ORIGIN_IP = "192.168.1.110"
NEW = "yarn.nexus.sanctum"
OLD = "yarn.inner.sanctum"
KUMA = "kuma.nexus.sanctum"
TIMEOUT_SECONDS = 6
MAX_BODY = 64 * 1024


def read_get(address, host):
    conn = http.client.HTTPConnection(address, 80, timeout=TIMEOUT_SECONDS)
    try:
        conn.request("GET", "/", headers={"Host": host, "Connection": "close"})
        reply = conn.getresponse()
        # Never output actual content or headers; we only classify status.
        bounded = reply.read(MAX_BODY + 1)
        return {
            "outcome": "http_response",
            "status": int(reply.status),
            "response_within_64k": len(bounded) <= MAX_BODY,
        }
    except (socket.timeout, TimeoutError):
        return {"outcome": "timeout", "status": None}
    except socket.gaierror:
        return {"outcome": "resolution_failed", "status": None}
    except ConnectionRefusedError:
        return {"outcome": "connection_refused", "status": None}
    except http.client.RemoteDisconnected:
        return {"outcome": "closed_without_http", "status": None}
    except (OSError, http.client.HTTPException, ValueError):
        return {"outcome": "connection_or_protocol_error", "status": None}
    finally:
        conn.close()


def dns_view():
    try:
        addresses = sorted({
            r[4][0]
            for r in socket.getaddrinfo(ORIGIN_NAME, 80,
                                        family=socket.AF_INET,
                                        type=socket.SOCK_STREAM)
        })
        return {"outcome": "resolved", "addresses": addresses,
                "matches_declared_origin": addresses == [ORIGIN_IP]}
    except (OSError, ValueError):
        return {"outcome": "resolution_failed", "addresses": [],
                "matches_declared_origin": False}


def classify(result):
    origin_by_ip = result["origin_by_ip_new_host"]
    by_name = result["origin_by_name_new_host"]
    proxy_new = result["production_proxy_new_host"]
    proxy_old = result["production_proxy_old_host"]
    kuma = result["production_proxy_kuma_control"]
    if kuma["outcome"] != "http_response":
        return "proxy_listener_or_general_routing_unconfirmed"
    if origin_by_ip["outcome"] != "http_response":
        return "yarn_origin_unreachable_from_kvin_ip"
    if by_name["outcome"] != "http_response" and not result["yarn_dns"]["matches_declared_origin"]:
        return "kvin_yarn_name_resolution_or_named_origin_path"
    if proxy_new["outcome"] != "http_response":
        return "production_new_yarn_proxy_path_unreachable"
    if proxy_old["outcome"] != "http_response":
        return "production_legacy_yarn_proxy_path_unreachable"
    if proxy_new["status"] != origin_by_ip["status"]:
        return "production_new_yarn_http_status_differs_from_origin"
    return "current_production_yarn_proxy_http_path_answers"


def main():
    result = {
        "observer": "kvin.outer.sanctum",
        "production_listener_only": True,
        "yarn_dns": dns_view(),
        "origin_by_ip_new_host": read_get(ORIGIN_IP, NEW),
        "origin_by_name_new_host": read_get(ORIGIN_NAME, NEW),
        "origin_by_ip_old_host": read_get(ORIGIN_IP, OLD),
        "production_proxy_new_host": read_get("127.0.0.1", NEW),
        "production_proxy_old_host": read_get("127.0.0.1", OLD),
        "production_proxy_kuma_control": read_get("127.0.0.1", KUMA),
        "configuration_changed": False,
        "kvar_or_dns_or_firewall_changed": False,
        "contents_headers_cookies_exposed": False,
    }
    result["classification"] = classify(result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
