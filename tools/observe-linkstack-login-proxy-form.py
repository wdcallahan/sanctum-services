#!/usr/bin/env python3
"""Classify LinkStack /login and Firefox HTTP proxy request-form compatibility.

One rootless Kvin observer. GET only /login on fixed endpoints; never
send forms, passwords, session cookies, authorization or raw URLs. The
candidate's absolute-form request-target simulates an SSH-forwarded HTTP
forward proxy while preserving Host: dir.nexus.sanctum. The terminal
receives only numeric statuses, named MIME kinds and redirect/cookie
policy categories; HTML, Location, cookies, CSRF and credentials are
never exposed. Does not follow any redirect.
"""
import http.client
import json
import os
import pwd
import socket
import sys
from urllib.parse import urlsplit

HOST = "kvin.outer.sanctum"
ACCOUNT = "wdc2"
FRONTEND = "dir.nexus.sanctum"
PATH = "/login"
ENDPOINTS = {
    "kvar_direct": ("kvar.outer.sanctum", 8081),
    "kvar_npm": ("kvar.outer.sanctum", 80),
    "kvin_loopback": ("127.0.0.1", 18081),
}
MAX_BODY = 262144
MIME = {"text/html": "html", "text/plain": "plain",
        "application/json": "json"}


def classify_redirect(raw):
    if not raw:
        return {"kind": "absent", "host": "absent", "scheme": "absent"}
    try:
        p = urlsplit(raw)
        if p.scheme and p.hostname:
            host = ("frontend" if p.hostname.lower() == FRONTEND
                    else "loopback" if p.hostname.lower() in ("localhost", "127.0.0.1")
                    else "unexpected_host")
            scheme = p.scheme.lower() if p.scheme.lower() in ("http", "https") else "other"
            return {"kind": "absolute", "host": host, "scheme": scheme}
        if not p.scheme and not p.netloc and p.path.startswith("/"):
            return {"kind": "relative", "host": "relative", "scheme": "relative"}
    except (ValueError, UnicodeError):
        pass
    return {"kind": "unexpected", "host": "unknown", "scheme": "unknown"}


def classify_cookies(headers):
    values = [value for name, value in headers if name.lower() == "set-cookie"]
    domain_values = []
    secure = False
    http_only = False
    same_site = set()
    for value in values:
        # Parse only attribute names and finite flags; never expose cookie
        # names, values, or arbitrary attribute text.
        for attr in value.split(";")[1:]:
            name, _, val = attr.strip().partition("=")
            key = name.strip().lower()
            if key == "domain":
                domain_values.append(val.lstrip(".").lower() == FRONTEND)
            elif key == "secure":
                secure = True
            elif key == "httponly":
                http_only = True
            elif key == "samesite":
                opt = val.strip().lower()
                same_site.add(opt if opt in ("strict", "lax", "none") else "other")
    return {
        "set_cookie_present": bool(values),
        "domain_attribute_present": bool(domain_values),
        "domain_attributes_match_frontend": (all(domain_values)
                                               if domain_values else "not_applicable"),
        "secure_attribute_present": secure,
        "http_only_attribute_present": http_only,
        "samesite_categories": sorted(same_site),
    }


def request(host, port, absolute_form=False):
    conn = http.client.HTTPConnection(host, port, timeout=8)
    try:
        target = ("http://" + FRONTEND + PATH) if absolute_form else PATH
        conn.putrequest("GET", target, skip_host=True)
        conn.putheader("Host", FRONTEND)
        conn.putheader("Connection", "close")
        conn.endheaders()
        res = conn.getresponse()
        status = int(res.status)
        content_type = (res.getheader("Content-Type", "") or "").split(";", 1)[0]
        redirect = classify_redirect(res.getheader("Location", "") or "")
        cookie = classify_cookies(res.getheaders())
        # Drain at most a bounded body to release socket; never emit it.
        complete = len(res.read(MAX_BODY + 1)) <= MAX_BODY
        return {
            "outcome": "http", "status": status,
            "mime_class": MIME.get(content_type.strip().lower(), "other"),
            "redirect": redirect, "cookie_policy": cookie,
            "body_complete_within_bound": complete,
        }
    except (OSError, TimeoutError, http.client.HTTPException, ValueError):
        return {
            "outcome": "transport_error", "status": None,
            "mime_class": "unavailable", "redirect": classify_redirect(""),
            "cookie_policy": classify_cookies([]),
            "body_complete_within_bound": False,
        }
    finally:
        conn.close()


def compatible(direct, absolute):
    if direct["outcome"] != "http" or absolute["outcome"] != "http":
        return False
    return (
        direct["status"] == absolute["status"]
        and direct["mime_class"] == absolute["mime_class"]
        and direct["redirect"] == absolute["redirect"]
        and direct["cookie_policy"] == absolute["cookie_policy"]
        and direct["body_complete_within_bound"]
        and absolute["body_complete_within_bound"]
    )


def observe(get=request):
    cases = {
        "kvar_direct": get(*ENDPOINTS["kvar_direct"]),
        "kvar_npm": get(*ENDPOINTS["kvar_npm"]),
        "kvin_direct": get(*ENDPOINTS["kvin_loopback"]),
        "kvin_absolute_proxy_form": get(*ENDPOINTS["kvin_loopback"], absolute_form=True),
    }
    direct = cases["kvin_direct"]
    absform = cases["kvin_absolute_proxy_form"]
    return {
        "schema": "sanctum-linkstack-anonymous-login-proxy-form/v1",
        "observer": HOST,
        "frontend": FRONTEND,
        "endpoint": "official_admin_login",
        "cases": cases,
        "candidate_proxy_request_compatible": compatible(direct, absform),
        "login_status_equal_to_kvar_direct": (
            direct["status"] == cases["kvar_direct"]["status"]
            if direct["outcome"] == cases["kvar_direct"]["outcome"] == "http"
            else "not_comparable"),
        "login_status_equal_to_kvar_npm": (
            direct["status"] == cases["kvar_npm"]["status"]
            if direct["outcome"] == cases["kvar_npm"]["outcome"] == "http"
            else "not_comparable"),
        "raw_urls_headers_cookies_or_html_returned": False,
        "password_or_form_submitted": False,
        "authenticated_admin_accepted": False,
        "real_named_firefox_session_accepted": False,
        "firefox_proxy_or_ssh_tunnel_created": False,
        "production_service_or_dns_modified": False,
        "limitation": (
            "Anonymous GET /login only. HTTP absolute-form compatibility "
            "does not prove Firefox proxy behavior or authenticated login."
        ),
    }


def main():
    if socket.getfqdn() != HOST or pwd.getpwuid(os.geteuid()).pw_name != ACCOUNT:
        print(json.dumps({"schema": "sanctum-linkstack-anonymous-login-proxy-form/v1",
                          "observer": HOST, "status": "refused"}))
        raise SystemExit(2)
    print(json.dumps(observe(), sort_keys=True))


if __name__ == "__main__":
    main()
