#!/usr/bin/env python3
"""Read-only, value-redacting inspection of generated Kvar NPM behavior.

Never emit raw Nginx config, application headers, credentials, URLs, proxy
variables, custom snippets or database state. Report only bounded filenames,
content SHA256, directive *names*, safe location path names, and boolean flags.
This complements (does not repeat) Maintenance's upstream-name projection.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys

HOST = "kvar.outer.sanctum"
CONTAINER = "nginx-proxman"
MAX_FILE = 262144
MAX_HOST_FILES = 64
MAX_CUSTOM_FILES = 32
HOST_FILE = re.compile(r"^[0-9]{1,6}\.conf$")
SAFE_PATH = re.compile(r"^/[A-Za-z0-9/_~.\\-]{0,127}$")
DIRECTIVE = re.compile(r"^\s*([a-z][a-z0-9_]*)\s+(.*?)\s*;\s*(?:#.*)?$")
LOCATION = re.compile(r"^\s*location\s+(?:(?:=|\\^~|~|~\\*)\s+)?(\S+)\s*\{(?:\s*#.*)?\s*$")
HEADER = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,63}$")

# Common directives are expected but values are NEVER exported.
SENSITIVE = {"auth_basic", "auth_basic_user_file", "auth_request",
             "allow", "deny", "satisfy", "limit_req", "limit_conn",
             "auth_jwt", "modsecurity", "geo", "map"}
REDIRECTS = {"return", "rewrite", "proxy_redirect", "error_page"}
SECURE = {"ssl_certificate", "ssl_certificate_key", "ssl_verify_client",
          "ssl_client_certificate", "ssl_protocols"}
TIMEOUTS = {"proxy_read_timeout", "proxy_send_timeout",
            "proxy_connect_timeout", "client_body_timeout"}
PROXY_DIRECTIVES = {"proxy_pass", "proxy_set_header", "proxy_hide_header",
                    "proxy_cookie_path", "proxy_cookie_domain",
                    "proxy_buffering", "proxy_request_buffering"}
CUSTOM_DIRS = ("root_top.conf", "root.conf", "http_top.conf", "http.conf",
               "events.conf", "stream.conf", "server_proxy.conf",
               "server_redirect.conf", "server_stream.conf",
               "server_stream_tcp.conf", "server_stream_udp.conf",
               "server_dead.conf")
OTHER_DIRS = ("default_host", "redirection_host", "dead_host", "stream")


def _read_capped_regular(path: Path) -> bytes:
    mode = path.lstat().st_mode
    if not stat.S_ISREG(mode) or path.stat().st_size > MAX_FILE:
        raise ValueError("unsafe_file_type_or_size")
    with path.open("rb") as stream:
        value = stream.read(MAX_FILE + 1)
    if len(value) > MAX_FILE:
        raise ValueError("oversized_file")
    return value


def inspect_proxy_config(data: bytes) -> dict:
    """Return metadata only, never raw sensitive directive values."""
    payload = data.decode("utf-8", errors="strict")
    directives = {}
    named_headers = set()
    sensitive = set()
    redirects = set()
    tls = set()
    timeout = set()
    location_paths = set()
    unnamed_location_count = 0
    custom_includes = 0
    include_count = 0
    websocket = False
    other_lines = 0
    for line in payload.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or clean in {"{", "}"}:
            continue
        location = LOCATION.fullmatch(line)
        if location:
            raw_path = location.group(1)
            if SAFE_PATH.fullmatch(raw_path):
                location_paths.add(raw_path)
            else:
                unnamed_location_count += 1
            continue
        if clean.endswith("{"):
            # Includes conditional/advanced nginx blocks; no values printed.
            other_lines += 1
            continue
        matched = DIRECTIVE.fullmatch(line)
        if not matched:
            # Unexpected syntax or multi-line directive: preserve uncertainty.
            other_lines += 1
            continue
        key, raw_value = matched.groups()
        directives[key] = directives.get(key, 0) + 1
        if key == "proxy_set_header":
            first = raw_value.split(None, 1)[0] if raw_value.split() else ""
            if HEADER.fullmatch(first):
                named_headers.add(first)
                if first.lower() in {"upgrade", "connection"}:
                    websocket = True
            else:
                other_lines += 1
        if key == "add_header":
            first = raw_value.split(None, 1)[0] if raw_value.split() else ""
            if HEADER.fullmatch(first):
                named_headers.add(first)
            else:
                other_lines += 1
        if key == "include":
            include_count += 1
            if "/data/nginx/custom/" in raw_value or "custom/" in raw_value:
                custom_includes += 1
        if key in SENSITIVE:
            sensitive.add(key)
        if key in REDIRECTS:
            redirects.add(key)
        if key in SECURE or (key == "listen" and "443" in raw_value):
            tls.add(key)
        if key in TIMEOUTS:
            timeout.add(key)
    return {
        "directive_names": sorted(directives),
        "directive_counts": dict(sorted(directives.items())),
        "header_names_only": sorted(named_headers),
        "locations_safe_path_names": sorted(location_paths),
        "locations_redacted_or_unsupported": unnamed_location_count,
        "conditional_or_unclassified_line_count": other_lines,
        "sensitive_policy_directive_names": sorted(sensitive),
        "redirect_directive_names": sorted(redirects),
        "tls_directive_names": sorted(tls),
        "timeout_directive_names": sorted(timeout),
        "websocket_header_detected": websocket,
        "include_count": include_count,
        "custom_include_count": custom_includes,
        "needs_manual_behavior_review": bool(
            unnamed_location_count or other_lines or sensitive or redirects or tls
            or any(loc != "/" for loc in location_paths)),
    }


def _directory_files(path: Path, limit: int, file_pattern: re.Pattern) -> list[Path]:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("directory_missing_or_unsafe")
    entries = sorted(path.iterdir())
    if len(entries) > limit:
        raise ValueError("file_count_outside_scope")
    if any(not file_pattern.fullmatch(item.name) for item in entries):
        raise ValueError("unexpected_directory_entry")
    return entries


def inspect_data_root(root: Path) -> dict:
    """Restricted inspection of known NPM generated config directories."""
    nginx = root / "nginx"
    proxy_dir = nginx / "proxy_host"
    files = _directory_files(proxy_dir, MAX_HOST_FILES, HOST_FILE)
    if not files:
        raise ValueError("no_generated_proxy_hosts")
    proxy_hosts = []
    partial = False
    for path in files:
        try:
            contents = _read_capped_regular(path)
            row = inspect_proxy_config(contents)
            row.update({"file": path.name, "sha256": hashlib.sha256(contents).hexdigest(),
                        "status": "observed"})
        except (OSError, ValueError, UnicodeError):
            partial = True
            row = {"file": path.name, "status": "unknown",
                   "reason": "file_unreadable_or_invalid"}
        proxy_hosts.append(row)

    extra_dirs = {}
    for dirname in OTHER_DIRS:
        p = nginx / dirname
        if not p.exists() and not p.is_symlink():
            extra_dirs[dirname] = {"status": "absent", "file_count": 0}
            continue
        try:
            names = _directory_files(p, MAX_HOST_FILES, HOST_FILE)
            extra_dirs[dirname] = {"status": "observed", "file_count": len(names)}
        except (OSError, ValueError):
            partial = True
            extra_dirs[dirname] = {"status": "unknown"}

    custom = nginx / "custom"
    custom_snippets = []
    if custom.exists() or custom.is_symlink():
        try:
            entries = _directory_files(custom, MAX_CUSTOM_FILES,
                re.compile(r"^[A-Za-z0-9_.-]+\.conf$"))
            for path in entries:
                data = _read_capped_regular(path)
                if data.strip():
                    custom_snippets.append({
                        "file": path.name if path.name in CUSTOM_DIRS else "unrecognized_custom_file",
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "size": len(data)
                    })
        except (OSError, ValueError):
            partial = True
            custom_snippets.append({"status": "unknown", "reason": "custom_scope_invalid"})

    return {
        "schema": "sanctum-yxorp-npm-behavior/v1",
        "source_host": HOST, "source_scope": "rootful_NPM_generated_config",
        "status": "partial" if partial else "observed",
        "proxy_hosts": proxy_hosts,
        "other_host_type_counts": extra_dirs,
        "nonempty_custom_config_files": custom_snippets,
        "configuration_changed": False,
        "credential_values_included": False,
        "limitations": [
            "Only generated on-disk configuration was observed; no NPM database or active nginx -T.",
            "Directive values, secrets, custom config bodies and arbitrary paths are never exported.",
            "Default shared include files are not expanded; flags indicate manual review, not parity.",
            "This is not live request/response, access-policy efficacy or client acceptance.",
        ],
    }


def discover_data_mount() -> Path:
    try:
        proc = subprocess.run(
            ["podman", "inspect", "--format", "{{json .Mounts}}", CONTAINER],
            capture_output=True, text=True, check=False, timeout=15,
            stdin=subprocess.DEVNULL,
        )
        if proc.returncode or len(proc.stdout) > 32768:
            raise ValueError("podman_inspect_unavailable")
        mounts = json.loads(proc.stdout)
        if not isinstance(mounts, list) or len(mounts) > 12:
            raise ValueError("unexpected_mount_shape")
        found = [m.get("Source") for m in mounts
                 if m.get("Destination") == "/data" and m.get("RW") is True]
        if len(found) != 1 or not isinstance(found[0], str):
            raise ValueError("unique_writable_data_mount_not_observed")
        path = Path(found[0])
        if not path.is_absolute() or path.is_symlink() or not path.is_dir():
            raise ValueError("invalid_data_mount")
        return path
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, TypeError) as exc:
        raise ValueError("cannot_locate_npm_data") from exc


def main() -> int:
    if os.geteuid() != 0 or socket.getfqdn() != HOST:
        print(json.dumps({"status": "refused", "reason": "requires_root_on_exact_kvar"}))
        return 2
    try:
        report = inspect_data_root(discover_data_mount())
    except (OSError, ValueError) as exc:
        # Structured reason only; never disclose local mount/secret paths.
        print(json.dumps({"status": "unknown", "reason": str(exc)}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
