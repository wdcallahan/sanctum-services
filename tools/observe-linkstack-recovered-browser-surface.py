#!/usr/bin/env python3
"""Compare recovered LinkStack anonymous browser-facing HTTP without revealing data.

Fixed Kvin rootless observer. GET only / and a bounded set of *same-site*
CSS/JS resources and, if discovered on both public pages, a login link.
Compare existing Kvar :8081, Kvar NPM HTTP:80, and the restored Kvin
loopback-only candidate :18081. Never print response body, HTML, login
URL, redirect, cookie, title, asset name, or a content hash.
"""
from html.parser import HTMLParser
import http.client
import json
import posixpath
import pwd
import socket
import sys
from urllib.parse import urlsplit, unquote

HOST = "kvin.outer.sanctum"
ACCOUNT = "wdc2"
FRONTEND = "dir.nexus.sanctum"
ENDPOINTS = (
    ("kvar_origin", "kvar.outer.sanctum", 8081),
    ("kvar_npm", "kvar.outer.sanctum", 80),
    ("kvin_recovered", "127.0.0.1", 18081),
)
MAX_BODY = 512 * 1024
MAX_ASSETS_PER_KIND = 1
MAX_LINKS = 500
KNOWN_MEDIA = {
    "text/html": "html",
    "text/css": "css",
    "application/javascript": "javascript",
    "text/javascript": "javascript",
    "image/png": "image",
    "image/jpeg": "image",
    "image/svg+xml": "image",
}


def safe_path(raw):
    """Never follow absolute external or special links or any query/fragment."""
    if not isinstance(raw, str) or not raw or len(raw) > 512:
        return None
    if any(c in raw for c in ("\r", "\n", "\\", "\x00")):
        return None
    try:
        parsed = urlsplit(raw)
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            return None
        if parsed.scheme and parsed.scheme.lower() != "http":
            return None
        if parsed.netloc and (parsed.hostname or "").lower() != FRONTEND:
            return None
        if parsed.port not in (None, 80):
            return None
        path = parsed.path
        if not path or path.startswith("//"):
            return None
        if not path.startswith("/"):
            path = "/" + path
        decoded = unquote(path)
        if len(decoded) > 512 or any(
                token in (".", "..") for token in decoded.split("/")):
            return None
        if "?" in decoded or "#" in decoded or "\\" in decoded:
            return None
        if any(ord(c) < 32 for c in decoded):
            return None
        if posixpath.normpath(decoded) != path.rstrip("/") and path != "/":
            return None
        return path
    except (ValueError, UnicodeError):
        return None


class PublicLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.assets = {"css": set(), "javascript": set()}
        self.logins = set()
        self.anchors = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a":
            self.anchors += 1
            path = safe_path(values.get("href"))
            if path and (path == "/login" or path == "/admin"
                         or path == "/admin/login"):
                self.logins.add(path)
        elif tag == "link" and "stylesheet" in (
                values.get("rel", "").lower().split()):
            path = safe_path(values.get("href"))
            if path and path.lower().endswith(".css"):
                self.assets["css"].add(path)
        elif tag == "script":
            path = safe_path(values.get("src"))
            if path and path.lower().endswith(".js"):
                self.assets["javascript"].add(path)


def request(host, port, path):
    # Returned body is PRIVATE internal state; call site only prints bounded
    # categories/equality and discards contents. No auth cookies or redirects.
    conn = http.client.HTTPConnection(host, port, timeout=6)
    try:
        conn.request("GET", path, headers={
            "Host": FRONTEND, "Connection": "close",
            "X-Forwarded-Host": FRONTEND,
            "X-Forwarded-Proto": "http",
        })
        response = conn.getresponse()
        raw = response.read(MAX_BODY + 1)
        mime = (response.getheader("Content-Type", "") or "").split(";", 1)[0]
        location = response.getheader("Location", "") or ""
        status = int(response.status)
        return {
            "outcome": "http", "status": status,
            "media": KNOWN_MEDIA.get(mime.lower().strip(), "other"),
            "content": raw if len(raw) <= MAX_BODY else None,
            "complete": len(raw) <= MAX_BODY,
            "location": location,
        }
    except (OSError, TimeoutError, http.client.HTTPException, ValueError):
        return {"outcome": "error", "status": None, "media": "unknown",
                "content": None, "complete": False, "location": ""}
    finally:
        conn.close()


def safe_summary(response):
    return {"outcome": response["outcome"], "status": response["status"],
            "media_class": response["media"],
            "complete_within_bound": response["complete"]}


def compare(a, b):
    if (a["outcome"] != "http" or b["outcome"] != "http"
            or not a["complete"] or not b["complete"]):
        return {"status_equal": "not_comparable",
                "media_equal": "not_comparable",
                "body_equal": "not_comparable",
                "redirect_equal": "not_comparable"}
    return {
        "status_equal": a["status"] == b["status"],
        "media_equal": a["media"] == b["media"],
        "body_equal": a["content"] == b["content"],
        "redirect_equal": (a["location"] == b["location"])
        if a["location"] or b["location"] else "not_applicable",
    }


def parse_public_root(response):
    if (response["outcome"] != "http" or response["status"] != 200
            or response["media"] != "html" or response["content"] is None):
        return None
    parser = PublicLinks()
    try:
        parser.feed(response["content"].decode("utf-8", "replace"))
        if parser.anchors > MAX_LINKS:
            return None
        return parser
    except (ValueError, UnicodeError):
        return None


def observe(get=request):
    root = {name: get(host, port, "/") for name, host, port in ENDPOINTS}
    old = root["kvar_origin"]
    proxy = root["kvar_npm"]
    new = root["kvin_recovered"]
    a, b = parse_public_root(old), parse_public_root(new)
    result = {
        "schema": "sanctum-linkstack-anonymous-browser-surface/v1",
        "observer": HOST, "frontend": FRONTEND,
        "root": {name: safe_summary(data) for name, data in root.items()},
        "root_origin_to_recovered": compare(old, new),
        "root_incumbent_npm_to_recovered": compare(proxy, new),
        "root_incumbent_to_origin": compare(proxy, old),
        "public_html_parsed": bool(a and b),
        "public_links": {
            "origin_anchor_count": a.anchors if a else None,
            "recovered_anchor_count": b.anchors if b else None,
            "anchor_counts_equal": a.anchors == b.anchors if a and b else "not_comparable",
        },
        "public_assets": {},
        "login_surface": {"status": "not_discovered_on_both"},
        "public_directory_exact_body_equal": (
            old["content"] == new["content"]
            if old["complete"] and new["complete"] and
            old["media"] == new["media"] == "html" and
            old["status"] == new["status"] == 200
            else "not_comparable"),
        "application_data_or_credentials_exposed": False,
        "authenticated_admin_accepted": False,
        "real_named_browser_session_accepted": False,
        "production_route_switched": False,
        "configuration_changed": False,
        "limitation": "Anonymous GET only; dynamic page bytes may differ. Browser session, login, private dashboard, asset rendering, cutover and rollback remain separate.",
    }
    if a and b:
        for kind in ("css", "javascript"):
            common = sorted(a.assets[kind] & b.assets[kind])
            samples = []
            for path in common[:MAX_ASSETS_PER_KIND]:
                observations = {
                    name: get(host, port, path)
                    for name, host, port in ENDPOINTS
                }
                samples.append({
                    "path_disclosed": False,
                    "responses": {name: safe_summary(data)
                                  for name, data in observations.items()},
                    "origin_to_recovered": compare(
                        observations["kvar_origin"], observations["kvin_recovered"]),
                    "incumbent_to_recovered": compare(
                        observations["kvar_npm"], observations["kvin_recovered"]),
                })
            result["public_assets"][kind] = {
                "origin_count": len(a.assets[kind]),
                "recovered_count": len(b.assets[kind]),
                "shared_count": len(common),
                "samples": samples,
            }
        common_login = sorted(a.logins & b.logins)
        if common_login:
            # One explicitly discovered anonymous link; do not follow redirects
            # or submit credentials/forms. No actual path is reported.
            path = common_login[0]
            response = {name: get(host, port, path)
                        for name, host, port in ENDPOINTS}
            result["login_surface"] = {
                "status": "anonymous_get_observed",
                "path_disclosed": False,
                "responses": {name: safe_summary(v)
                              for name, v in response.items()},
                "origin_to_recovered": compare(
                    response["kvar_origin"], response["kvin_recovered"]),
            }
    return result


def main():
    if socket.getfqdn() != HOST or pwd.getpwuid(__import__("os").geteuid()).pw_name != ACCOUNT:
        print(json.dumps({"schema": "sanctum-linkstack-anonymous-browser-surface/v1",
                          "status": "refused", "reason": "wrong_host_or_account"}))
        raise SystemExit(2)
    print(json.dumps(observe(), sort_keys=True))


if __name__ == "__main__":
    main()
