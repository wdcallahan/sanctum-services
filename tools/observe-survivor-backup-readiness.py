#!/usr/bin/env python3
"""Kvar survivor backup readiness: metadata only, no state changes.

Read the fixed installed Quadlet privately to classify update ownership,
read exact named Podman-volume free space, and check Kvin storage headroom.
Never display arbitrary config, mount paths, secrets, images or raw commands.
"""
import argparse
import os
from pathlib import Path
import pwd
import re
import socket
import stat
import subprocess

HOSTS = {
    "linkstack": {
        "host": "kvar.outer.sanctum", "user": "wdc2",
        "unit": "/home/wdc2/.config/containers/systemd/linkstack.container",
        "image": "docker.io/linkstackorg/linkstack:latest",
        "volume": "linkstack", "user_timer": True,
    },
    "pihole": {
        "host": "kvar.outer.sanctum", "user": "root",
        "unit": "/etc/containers/systemd/pihole.container",
        "image": "docker.io/pihole/pihole:latest",
        "volume": "systemd-pihole_etc-pihole", "user_timer": False,
    },
    "kvin-storage": {"host": "kvin.outer.sanctum", "user": "wdc2"},
}
SAFE_POLICY = {"registry", "local", "none"}
SAFE_PULL = {"always", "missing", "newer", "never", "true", "false"}
MAX_QUADLET_BYTES = 65536
BASELINE_REGULAR_BYTES = 1395192558  # Accepted November 12, 2026 scan, not a backup.
STAGING_RESERVE_BYTES = BASELINE_REGULAR_BYTES * 2 + 1073741824


def query(argv):
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=12, check=False)
        if p.returncode or len(p.stdout) > 8192:
            return None
        return p.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None


def unit_policy(path, expected_image, expected_user):
    """Read privately; return only bounded update/source-policy classifications."""
    target = Path(path)
    try:
        info = target.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_size > MAX_QUADLET_BYTES
                or info.st_uid != pwd.getpwnam(expected_user).pw_uid):
            return {"status": "partial", "reason": "unexpected_unit_file"}
        data = target.read_text("utf-8")
    except (OSError, UnicodeError, KeyError):
        return {"status": "partial", "reason": "quadlet_unavailable"}
    if len(data.encode("utf-8")) > MAX_QUADLET_BYTES:
        return {"status": "partial", "reason": "oversize_quadlet"}
    section = ""
    items = {"Image": [], "AutoUpdate": [], "Pull": []}
    label_disclosed = False
    for line in data.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if re.fullmatch(r"\[[A-Za-z0-9-]+\]", stripped):
            section = stripped[1:-1]
            continue
        if section != "Container" or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key, value = key.strip(), value.strip()
        if key in items:
            items[key].append(value)
        elif key in ("PodmanArgs", "Label") and "io.containers.autoupdate" in value:
            # Do not interpret arbitrary command lines or print label values.
            label_disclosed = True
    if len(items["Image"]) != 1 or items["Image"][0] != expected_image:
        return {"status": "partial", "reason": "quadlet_image_contract_drift"}
    if len(items["AutoUpdate"]) > 1 or len(items["Pull"]) > 1:
        return {"status": "partial", "reason": "duplicate_update_directive"}
    mode = items["AutoUpdate"][0] if items["AutoUpdate"] else "unspecified"
    pull = items["Pull"][0] if items["Pull"] else "unspecified"
    if (mode not in SAFE_POLICY | {"unspecified"}
            or pull not in SAFE_PULL | {"unspecified"}):
        return {"status": "partial", "reason": "unrecognized_update_policy"}
    return {"status": "observed", "source_image_matches_running_tag": True,
            "quadlet_auto_update": mode, "quadlet_pull_policy": pull,
            "extra_autoupdate_label_present": label_disclosed,
            "source_file_read_privately": True, "credential_values_returned": False}


def timer_policy(raw):
    if not isinstance(raw, str) or len(raw) > 4096:
        return {"status": "unknown"}
    vals = {}
    for item in raw.splitlines():
        if "=" not in item:
            return {"status": "unknown"}
        key, value = item.split("=", 1)
        if key not in ("LoadState", "ActiveState", "UnitFileState") or key in vals:
            return {"status": "unknown"}
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", value):
            return {"status": "unknown"}
        vals[key] = value
    return {"status": "observed", **vals} if len(vals) == 3 else {"status": "unknown"}


def available_bytes(path):
    try:
        v = os.statvfs(path)
        return {"status": "observed", "available_bytes": v.f_frsize * v.f_bavail}
    except OSError:
        return {"status": "unknown"}


def source_volume_space(raw, name):
    if not isinstance(raw, str) or len(raw) > 512:
        return {"status": "unknown"}
    mount = Path(raw.strip())
    if (not mount.is_absolute() or mount.name != "_data"
            or mount.parent.name != name):
        return {"status": "unknown"}
    try:
        info = mount.lstat()
        if not stat.S_ISDIR(info.st_mode):
            return {"status": "unknown"}
    except OSError:
        return {"status": "unknown"}
    return available_bytes(mount)


def collect(service, host, account, run=query, quadlet=unit_policy,
            space=available_bytes):
    entry = HOSTS.get(service)
    if not entry or entry["host"] != host or entry["user"] != account:
        return {"status": "refused", "reason": "incorrect_host_user_or_service"}
    base = {
        "schema": "sanctum-survivor-backup-readiness/v1",
        "observer": host, "service": service,
        "configuration_changed": False, "application_interrupted": False,
        "app_content_or_password_returned": False, "data_exported": False,
        "backup_or_restore_accepted": False
    }
    if service == "kvin-storage":
        home = space("/home/wdc2")
        rootful_storage = space("/var/lib/containers/storage")
        home_ok = (home.get("status") == "observed"
                   and home["available_bytes"] >= STAGING_RESERVE_BYTES)
        return {**base, "status": "observed" if home_ok else "partial",
                "home_staging": home, "rootful_store": rootful_storage,
                "accepted_source_regular_file_bytes": BASELINE_REGULAR_BYTES,
                "minimum_staging_free_bytes": STAGING_RESERVE_BYTES,
                "home_staging_headroom_established": home_ok,
                "recovery_destination_independence_accepted": False}
    q = quadlet(entry["unit"], entry["image"], entry["user"])
    args = ["systemctl"]
    if entry["user_timer"]:
        args.append("--user")
    args += ["show", "podman-auto-update.timer", "--no-pager",
             "-p", "LoadState", "-p", "ActiveState", "-p", "UnitFileState"]
    timer = timer_policy(run(args))
    vol = source_volume_space(
        run(["podman", "volume", "inspect", "--format", "{{.Mountpoint}}",
             entry["volume"]]), entry["volume"])
    return {**base,
            "status": ("observed" if q["status"] == "observed"
                       and timer["status"] == "observed"
                       and vol["status"] == "observed" else "partial"),
            "unit_update_policy": q, "podman_auto_update_timer": timer,
            "source_volume_filesystem": vol,
            "automatic_update_cause_proven": False,
            "application_backup_consistency_established": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", choices=sorted(HOSTS), required=True)
    args = parser.parse_args()
    report = collect(args.service, socket.getfqdn(),
                     pwd.getpwuid(os.geteuid()).pw_name)
    import json
    print(json.dumps(report, sort_keys=True))
    if report["status"] == "refused":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
