#!/usr/bin/env python3
"""Read-only, bounded Kvar LinkStack/Pi-hole recovery prerequisites.

The script runs in one fixed Podman privilege namespace, selects only the
named surviving application, and emits no environment, app files, headers,
passwords, container logs, private mounts, or arbitrary Podman inspect JSON.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import pwd
import re
import socket
import subprocess

HOST = "kvar.outer.sanctum"
CHOICES = {
    "linkstack": {"account": "wdc2", "scope": "rootless", "unit": "linkstack.service"},
    "pihole": {"account": "root", "scope": "rootful", "unit": "pihole.service"},
}
CONTAINER_FORMAT = ('{"name":{{json .Name}},"image_name":{{json .ImageName}},'
                    '"image_id":{{json .Image}},"running":{{json .State.Running}},'
                    '"ports":{{json .NetworkSettings.Ports}},"mounts":{{json .Mounts}}}')
IMAGE_FORMAT = ('{"id":{{json .Id}},"digest":{{json .Digest}},'
                '"repo_digests":{{json .RepoDigests}},'
                '"os":{{json .Os}},"arch":{{json .Architecture}}}')
SAFE_REF = re.compile(r"^[A-Za-z0-9_.:/@-]{1,250}$")
SAFE_VOLUME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}$")
SAFE_PATH = re.compile(r"^/[A-Za-z0-9_./-]{1,199}$")
SAFE_ID = re.compile(r"^(?:sha256:)?[a-f0-9]{64}$")
SAFE_UNIT_PATH_PREFIXES = (
    "/home/wdc2/.config/containers/systemd/",
    "/etc/containers/systemd/",
    "/etc/systemd/system/",
    "/usr/lib/systemd/system/",
)


def query(argv):
    """Return only a bounded in-memory observation; never return stderr."""
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, text=True,
                           capture_output=True, check=False, timeout=12)
        if p.returncode or len(p.stdout) > 262144:
            return None
        return p.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None


def parse_json(value):
    try:
        return json.loads(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def safe_mounts(raw):
    if not isinstance(raw, list) or len(raw) > 32:
        return None
    result = []
    for m in raw:
        if not isinstance(m, dict):
            return None
        dest = m.get("Destination")
        mtype = m.get("Type")
        name = m.get("Name") or None
        if (not isinstance(dest, str) or not SAFE_PATH.fullmatch(dest)
                or mtype not in ("volume", "bind", "tmpfs")
                or (name is not None and
                    (not isinstance(name, str) or not SAFE_VOLUME.fullmatch(name)))
                or not isinstance(m.get("RW"), bool)):
            return None
        result.append({"destination": dest, "type": mtype,
                       "volume_name": name if mtype == "volume" else None,
                       "read_write": m["RW"]})
    return sorted(result, key=lambda m: m["destination"])


def safe_ports(raw):
    if not isinstance(raw, dict) or len(raw) > 24:
        return None
    result = []
    for internal, bindings in raw.items():
        if not isinstance(internal, str) or not re.fullmatch(r"\d{1,5}/(tcp|udp)", internal):
            return None
        if int(internal.split("/")[0]) > 65535:
            return None
        if bindings is None:
            continue
        if not isinstance(bindings, list) or len(bindings) > 8:
            return None
        for binding in bindings:
            if not isinstance(binding, dict):
                return None
            port = binding.get("HostPort")
            address = binding.get("HostIp") or "0.0.0.0"
            if not isinstance(port, str) or not port.isdecimal() or not 1 <= int(port) <= 65535:
                return None
            try:
                ipaddress.ip_address(address)
            except ValueError:
                return None
            result.append({"container_port": internal, "host_port": int(port),
                           "host_ip": address})
    return sorted(result, key=lambda x: (x["container_port"], x["host_port"], x["host_ip"]))


def safe_unit(raw):
    if raw is None or len(raw) > 4096:
        return {"status": "unknown"}
    fields = {}
    for line in raw.splitlines():
        if "=" not in line:
            return {"status": "unknown"}
        key, value = line.split("=", 1)
        if key not in ("LoadState", "ActiveState", "UnitFileState", "SourcePath") or key in fields:
            return {"status": "unknown"}
        fields[key] = value
    if set(fields) != {"LoadState", "ActiveState", "UnitFileState", "SourcePath"}:
        return {"status": "unknown"}
    path = fields["SourcePath"]
    source = (path if any(path.startswith(prefix) for prefix in SAFE_UNIT_PATH_PREFIXES)
              and SAFE_PATH.fullmatch(path) else None)
    if any(not re.fullmatch(r"[a-zA-Z_-]{1,40}", fields[k]) for k in
           ("LoadState", "ActiveState", "UnitFileState")):
        return {"status": "unknown"}
    return {"status": "observed" if fields["LoadState"] == "loaded" else "partial",
            "load": fields["LoadState"], "active": fields["ActiveState"],
            "enabled": fields["UnitFileState"], "quadlet_source": source}


def collect(service, host, account, runner=query):
    if service not in CHOICES:
        return {"status": "refused", "reason": "unselected_service"}
    cfg = CHOICES[service]
    if host != HOST or account != cfg["account"]:
        return {"status": "refused", "reason": "wrong_host_or_privilege_namespace"}
    result = {
        "schema": "sanctum-kvar-survivor-source/v1", "observer": host,
        "service": service, "scope": cfg["scope"], "container": service,
        "configuration_changed": False, "data_or_credential_contents_read": False,
        "host_or_app_mutation_performed": False, "backup_restore_accepted": False,
    }

    raw = parse_json(runner(["podman", "container", "inspect", "--format",
                             CONTAINER_FORMAT, service]))
    if not isinstance(raw, dict) or raw.get("name", "").lstrip("/") != service:
        return dict(result, status="partial", reason="container_identity_unavailable")
    image_id, image_ref = raw.get("image_id"), raw.get("image_name")
    mounts, ports = safe_mounts(raw.get("mounts")), safe_ports(raw.get("ports"))
    if (not isinstance(image_id, str) or not SAFE_ID.fullmatch(image_id)
            or not isinstance(image_ref, str) or not SAFE_REF.fullmatch(image_ref)
            or not isinstance(raw.get("running"), bool)
            or mounts is None or ports is None):
        return dict(result, status="partial", reason="bounded_container_metadata_unavailable")
    result.update({"container_running": raw["running"], "image_reference": image_ref,
                   "image_id": image_id, "mounts": mounts, "port_mappings": ports})
    img = parse_json(runner(["podman", "image", "inspect", "--format", IMAGE_FORMAT, image_id]))
    if isinstance(img, dict):
        digest_list = img.get("repo_digests")
        digests = (sorted({v for v in digest_list
                           if isinstance(v, str) and
                           re.fullmatch(r"[A-Za-z0-9_.:/-]{1,170}@sha256:[a-f0-9]{64}", v)})
                   if isinstance(digest_list, list) and len(digest_list) <= 20 else [])
        if (img.get("os") == "linux" and img.get("arch") in ("arm64", "amd64")
                and isinstance(img.get("id"), str)
                and SAFE_ID.fullmatch(img["id"])):
            result.update({"image_platform": "linux/" + img["arch"],
                           "repo_digests": digests})
    command = ["systemctl"]
    if cfg["scope"] == "rootless":
        command.append("--user")
    command += ["show", cfg["unit"], "--no-pager",
                "-p", "LoadState", "-p", "ActiveState",
                "-p", "UnitFileState", "-p", "SourcePath"]
    result["service_unit"] = safe_unit(runner(command))
    result["status"] = ("observed" if "image_platform" in result
                        and result["service_unit"]["status"] == "observed"
                        else "partial")
    result["next_gate"] = ("qualify immutable image and safe consistent volume backup,"
                           " then restore to isolated Kvin application")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", choices=sorted(CHOICES), required=True)
    args = parser.parse_args()
    result = collect(args.service, socket.getfqdn(),
                     pwd.getpwuid(os.geteuid()).pw_name)
    print(json.dumps(result, sort_keys=True))
    if result["status"] == "refused":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
