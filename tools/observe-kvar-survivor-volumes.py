#!/usr/bin/env python3
"""Bounded, metadata-only preflight for Kvar survivors' named Podman volumes.

No volume file bytes are opened, no secret values shown, no backup attempted,
and no services, files, container mounts, or DNS configuration are changed.
"""
import argparse
import json
import os
from pathlib import Path
import pwd
import re
import socket
import stat
import subprocess

HOST = "kvar.outer.sanctum"
VOLUMES = {
    "linkstack": {"account": "wdc2",
                  "volumes": ["linkstack"],
                  "markers": {"linkstack": (".env", "database/database.sqlite")}},
    "pihole": {"account": "root",
               "volumes": ["systemd-pihole_etc-pihole",
                           "systemd-pihole_etc-dnsmasq"],
               "markers": {
                   "systemd-pihole_etc-pihole": ("pihole.toml", "gravity.db", "pihole-FTL.db"),
                   "systemd-pihole_etc-dnsmasq": (),
               }},
}
MAX_ENTRIES = 100000
MAX_DEPTH = 24
PATH_LIMIT = 512


def query(argv):
    try:
        p = subprocess.run(argv, input=None, capture_output=True, text=True,
                           timeout=15, check=False, stdin=subprocess.DEVNULL)
        if p.returncode or len(p.stdout) > 4096:
            return None
        return p.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None


def safe_volume_mount(raw, name):
    if (not isinstance(raw, str) or not raw.startswith("/")
            or len(raw) > PATH_LIMIT or "\n" in raw or "\x00" in raw):
        return None
    path = Path(raw)
    if path.name != "_data" or path.parent.name != name:
        return None
    try:
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) or path.is_symlink():
            return None
        return path
    except OSError:
        return None


def marker_presence(root, rel):
    path = root / rel
    try:
        if not path.is_relative_to(root):
            return "unknown"
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            return "regular_file"
        if stat.S_ISDIR(info.st_mode):
            return "directory"
        if stat.S_ISLNK(info.st_mode):
            return "symlink"
        return "other"
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "unknown"


def scan(root):
    """Iterative lstat walk: never follow symlinks; bail out if unbounded."""
    total, files, dirs, links, others = 0, 0, 0, 0, 0
    todo = [(root, 0)]
    entries = 0
    try:
        while todo:
            parent, depth = todo.pop()
            if depth > MAX_DEPTH:
                return {"status": "depth_limit"}
            with os.scandir(parent) as scanned:
                for entry in scanned:
                    entries += 1
                    if entries > MAX_ENTRIES:
                        return {"status": "entry_limit"}
                    info = entry.stat(follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        dirs += 1
                        todo.append((Path(entry.path), depth + 1))
                    elif stat.S_ISREG(info.st_mode):
                        files += 1
                        total += info.st_size
                    elif stat.S_ISLNK(info.st_mode):
                        links += 1
                    else:
                        others += 1
    except OSError:
        return {"status": "unreadable"}
    return {"status": "observed", "regular_files": files, "directories": dirs,
            "symlinks": links, "special_entries": others,
            "total_regular_file_bytes": total}


def collect(service, host, account, runner=query):
    if service not in VOLUMES:
        return {"status": "refused", "reason": "unknown_service"}
    cfg = VOLUMES[service]
    if host != HOST or account != cfg["account"]:
        return {"status": "refused", "reason": "wrong_host_or_account"}
    report = {
        "schema": "sanctum-kvar-volume-preflight/v1",
        "observer": HOST, "service": service,
        "scope": "rootful" if account == "root" else "rootless",
        "configuration_changed": False, "file_contents_read": False,
        "data_exported": False, "backup_restore_accepted": False,
        "volumes": [],
    }
    for name in cfg["volumes"]:
        mount = safe_volume_mount(
            runner(["podman", "volume", "inspect", "--format",
                    "{{.Mountpoint}}", name]), name)
        row = {"name": name, "status": "partial"}
        if mount is None:
            row["reason"] = "volume_mountpoint_unavailable"
        else:
            row["scan"] = scan(mount)
            row["known_file_markers"] = {
                m: marker_presence(mount, m) for m in cfg["markers"][name]
            }
            row["status"] = ("observed"
                             if row["scan"]["status"] == "observed"
                             else "partial")
        report["volumes"].append(row)
    report["status"] = ("observed"
                         if all(v["status"] == "observed" for v in report["volumes"])
                         else "partial")
    report["next_gate"] = ("design quiesced consistent backup and private off-host "
                           "retention; do not confuse a metadata scan with a backup")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--service", choices=sorted(VOLUMES), required=True)
    args = p.parse_args()
    result = collect(args.service, socket.getfqdn(),
                     pwd.getpwuid(os.geteuid()).pw_name)
    print(json.dumps(result, sort_keys=True))
    if result["status"] == "refused":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
