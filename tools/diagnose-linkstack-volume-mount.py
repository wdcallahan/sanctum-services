#!/usr/bin/env python3
"""Diagnose LinkStack restored-volume startup after the PROVEN port-80 fix.

Rootless wdc2 on Kvin only. Never mount or mutate the accepted restore volume.
Verify exact private local snapshot, import it to a uniquely named disposable
volume, then compare:
  image_only: pinned image, no mounted data
  plain: image + imported clone
  relabel: same clone privately relabeled for the new container (:Z)
  ownership: same clone with :U,Z (recursive ownership repair).
All four use the same isolated internal/no-DNS bridge and per-CONTAINER
net.ipv4.ip_unprivileged_port_start=80. No host ports or global sysctl.
The potentially expensive :U operation touches ONLY the disposable clone.
No raw stderr, logs, .env contents, paths, database or credentials emitted.
"""
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import socket
import stat
import subprocess
import sys
import time

HOST = "kvin.outer.sanctum"
ACCOUNT = "wdc2"
IMAGE = ("docker.io/linkstackorg/linkstack@sha256:"
         "b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1")
IMAGE_ID = "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"
ARCHIVE = ("/home/wdc2/.local/share/sanctum-services/backups/linkstack/"
           "linkstack-20261112t105926.tar")
ARCHIVE_SHA = "a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa"
ARCHIVE_BYTES = 93845504
ACCEPTED_VOLUME = "sanctum-linkstack-restore-test-20261112t105926"
PREFIX = "sanctum-linkstack-volume-diag-20261112t105926"
VOLUME = PREFIX + "-clone"
NETWORK = PREFIX + "-internal"
CASES = {
    "image_only": PREFIX + "-image",
    "plain": PREFIX + "-plain",
    "relabel": PREFIX + "-relabel",
    "ownership": PREFIX + "-ownership",
}
SYSCTL = "net.ipv4.ip_unprivileged_port_start=80"
MAX_LOG_BYTES = 131072
ERRORS = {
    "apache_bind_denied": (r"ah00072|make_sock|could not bind",),
    "permission_denied": (r"permission denied|operation not permitted|eacces",),
    "apache_log_open": (r"ah00015|unable to open logs",),
    "file_missing": (r"no such file|file not found|not found",),
    "read_only": (r"read.only file system|readonly database",),
    "sqlite_error": (r"sqlite|sqlstate|database is locked",),
    "php_fatal": (r"php fatal|uncaught exception|php parse error",),
    "apache_config": (r"ah00526|syntax error|invalid command|ah00016",),
    "php_environment": (r"invalid.*app.key|missing.*app.key|no application encryption key",),
}
STAGES = {
    "entrypoint_started": b"LINKSTACK v",
    "apache_launch_reached": b"Running Apache",
}
MARKERS = (".env", "version.json", "database", "database/database.sqlite")


class Refused(Exception):
    def __init__(self, phase):
        self.phase = phase


def invoke(argv, timeout=25):
    try:
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                           timeout=timeout, check=False)
        if len(r.stdout) + len(r.stderr) > MAX_LOG_BYTES:
            return -1, b"", b""
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.TimeoutExpired):
        return -1, b"", b""


def parse(blob):
    try:
        return json.loads(blob)
    except (ValueError, TypeError, UnicodeError):
        return None


def summarize_log(stdout, stderr):
    raw = stdout + b"\n" + stderr
    if len(raw) > MAX_LOG_BYTES:
        return {"error_categories": ["unavailable"], "stderr_present": False,
                **{k: False for k in STAGES}}
    text = raw.decode("utf-8", "replace").lower()
    found = sorted(key for key, patterns in ERRORS.items()
                   if any(re.search(pattern, text) for pattern in patterns))
    return {
        "error_categories": found or ["unclassified"],
        "stderr_present": bool(stderr),
        **{key: value.lower() in raw.lower() for key, value in STAGES.items()},
    }


def exact_archive():
    p = Path(ARCHIVE)
    try:
        info = p.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_size != ARCHIVE_BYTES):
            return False
        digest = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest() == ARCHIVE_SHA
    except OSError:
        return False


def exact_image():
    rc, data, _ = invoke(["podman", "image", "inspect", IMAGE])
    images = parse(data)
    return (rc == 0 and isinstance(images, list) and len(images) == 1
            and isinstance(images[0], dict)
            and images[0].get("Id") == IMAGE_ID
            and images[0].get("Architecture") == "arm64"
            and images[0].get("Os") == "linux")


def exists(kind, name):
    rc, _, _ = invoke(["podman", kind, "exists", name])
    return rc  # 0=exists, 1=absent, anything else=unknown


def volume_markers():
    """Metadata only. Exact disposable clone mountpoint, no data reads."""
    rc, raw, _ = invoke(["podman", "volume", "inspect",
                         "--format", "{{.Mountpoint}}", VOLUME])
    if rc:
        return {"status": "unavailable"}
    mount = Path(raw.decode("utf-8", "replace").strip())
    if (not mount.is_absolute() or not str(mount).endswith("/" + VOLUME + "/_data")
            or mount.is_symlink() or not mount.is_dir()):
        return {"status": "unexpected_mountpoint"}
    checks = {}
    for name in (".",) + MARKERS:
        path = mount if name == "." else mount / name
        try:
            metadata = path.lstat()
            # Never return user data, file paths, file bytes or labels.
            checks["volume_root" if name == "." else name] = {
                "kind": ("symlink" if stat.S_ISLNK(metadata.st_mode)
                         else "directory" if stat.S_ISDIR(metadata.st_mode)
                         else "regular" if stat.S_ISREG(metadata.st_mode)
                         else "other"),
                "mode": format(stat.S_IMODE(metadata.st_mode), "04o"),
                "owner_matches_rootless_login": metadata.st_uid == os.geteuid(),
                "owner_uid": metadata.st_uid,
                "owner_gid": metadata.st_gid,
            }
        except OSError:
            checks["volume_root" if name == "." else name] = {"kind": "unavailable"}
    return {"status": "observed", "markers": checks}


def run_case(label, network):
    name = CASES[label]
    argv = ["podman", "run", "--detach", "--name", name,
            "--network", network, "--sysctl", SYSCTL, "--pull", "never",
            "--security-opt", "no-new-privileges"]
    if label != "image_only":
        suffix = {"plain": "", "relabel": ":Z", "ownership": ":U,Z"}[label]
        argv += ["--volume", VOLUME + ":/htdocs" + suffix]
    argv += ["--env", "HTTP_SERVER_NAME=localhost", IMAGE]
    rc, _, stderr = invoke(argv, timeout=110 if label == "ownership" else 45)
    if rc:
        return {"status": "run_failed", "running": None, "exit_code": None,
                "oom_killed": None, "http_status": None,
                "log": summarize_log(b"", stderr)}
    time.sleep(3)
    rc, stdout, _ = invoke(["podman", "container", "inspect",
                            "--format", "{{json .State}}", name])
    state = parse(stdout)
    if rc or not isinstance(state, dict):
        return {"status": "state_unknown", "running": None,
                "exit_code": None, "oom_killed": None, "http_status": None,
                "log": summarize_log(b"", b"")}
    running = state.get("Running") if type(state.get("Running")) is bool else None
    exit_code = state.get("ExitCode") if type(state.get("ExitCode")) is int else None
    oom = state.get("OOMKilled") if type(state.get("OOMKilled")) is bool else None
    http = None
    if running is True:
        curl_rc, output, _ = invoke(
            ["podman", "exec", name, "curl", "--silent", "--output", "/dev/null",
             "--max-time", "5", "--write-out", "%{http_code}", "--header",
             "Host: dir.nexus.sanctum", "http://127.0.0.1/"], timeout=12)
        text = output.decode("ascii", "ignore").strip()
        if curl_rc == 0 and re.fullmatch(r"[1-5]\d\d", text):
            http = int(text)
    logs_rc, out, err = invoke(["podman", "logs", "--tail", "100", name])
    return {"status": "observed", "running": running,
            "exit_code": exit_code if exit_code is not None and 0 <= exit_code <= 255 else None,
            "oom_killed": oom, "http_status": http,
            "log": summarize_log(out, err) if logs_rc == 0
                    else summarize_log(b"", b"")}


def comparison(cases):
    if "image_only" not in cases or cases["image_only"].get("http_status") != 200:
        return "image_only_control_not_accepted"
    for name in ("plain", "relabel", "ownership"):
        if name not in cases:
            return "incomplete"
    def works(case):
        result = cases[case]
        return result.get("status") == "observed" and result.get("running") is True \
            and result.get("http_status") == 200
    if works("plain"):
        return "unmodified_clone_serves_http"
    if works("relabel"):
        return "private_selinux_relabel_restores_http"
    if works("ownership"):
        return "ownership_repair_after_relabel_restores_http"
    return "restored_data_startup_still_unresolved"


def collect(host, user):
    if host != HOST or user != ACCOUNT:
        return {"status": "refused", "reason": "wrong_host_or_account"}
    result = {
        "schema": "sanctum-linkstack-volume-mount-diagnostic/v1",
        "observer": host, "status": "partial",
        "source_archive_unchanged": True,
        "accepted_restore_volume_unchanged": True,
        "host_sysctl_unchanged": True,
        "kvar_and_production_untouched": True,
        "private_content_or_raw_logs_returned": False,
        "restored_application_accepted": False,
        "cloned_volume_metadata": {"status": "not_checked"},
        "cases": {},
        "cleanup": {key + "_container_removed": False for key in CASES} |
                   {"clone_volume_removed": False, "internal_network_removed": False},
    }
    # Cleanup only names confirmed absent before any changes.
    qualified = False
    attempted = {"network": False, "volume": False, **{label: False for label in CASES}}
    try:
        if not exact_archive():
            raise Refused("exact_private_archive_identity")
        if not exact_image():
            raise Refused("pinned_arm64_image_identity")
        if exists("volume", ACCEPTED_VOLUME) != 0:
            raise Refused("accepted_volume_not_present")
        if any(exists(kind, name) != 1
               for kind, name in [("network", NETWORK), ("volume", VOLUME)] +
               [("container", item) for item in CASES.values()]):
            raise Refused("temporary_name_already_used_or_unavailable")
        qualified = True
        attempted["network"] = True
        rc, _, _ = invoke(["podman", "network", "create", "--driver", "bridge",
                           "--internal", "--disable-dns", NETWORK])
        if rc:
            raise Refused("internal_network_create")
        rc, stdout, _ = invoke(["podman", "network", "inspect", NETWORK])
        net = parse(stdout)
        if (rc or not isinstance(net, list) or len(net) != 1
                or not isinstance(net[0], dict)
                or net[0].get("name") != NETWORK
                or net[0].get("driver") != "bridge"
                or net[0].get("internal") is not True
                or net[0].get("dns_enabled") is not False):
            raise Refused("isolated_network_contract")
        attempted["volume"] = True
        rc, _, _ = invoke(["podman", "volume", "create", VOLUME])
        if rc:
            raise Refused("clone_volume_create")
        rc, _, _ = invoke(["podman", "volume", "import", VOLUME, ARCHIVE], timeout=100)
        if rc:
            raise Refused("clone_volume_import")
        result["cloned_volume_metadata"] = volume_markers()
        if result["cloned_volume_metadata"]["status"] != "observed":
            raise Refused("clone_metadata_unavailable")
        for label in CASES:
            attempted[label] = True
            result["cases"][label] = run_case(label, NETWORK)
            # Remove each case before the next potentially relabels/re-owns
            # its private disposable clone.
            code = exists("container", CASES[label])
            if code == 0:
                removed, _, _ = invoke(["podman", "rm", "--force", CASES[label]])
                result["cleanup"][label + "_container_removed"] = removed == 0
                if removed:
                    raise Refused("trial_container_cleanup_failed")
            elif code == 1:
                result["cleanup"][label + "_container_removed"] = True
            else:
                raise Refused("trial_container_state_unknown")
            if label == "image_only" and result["cases"][label].get("http_status") != 200:
                raise Refused("image_only_control_no_longer_responds")
        result["status"] = "observed"
    except Refused as error:
        result["failure_phase"] = error.phase
    except Exception:
        result["failure_phase"] = "unexpected_internal_error"
    finally:
        for label, name in CASES.items():
            key = label + "_container_removed"
            if not qualified or not attempted[label]:
                result["cleanup"][key] = True
                continue
            rc = exists("container", name)
            if rc == 0:
                done, _, _ = invoke(["podman", "rm", "--force", name])
                result["cleanup"][key] = done == 0
            elif rc == 1:
                result["cleanup"][key] = True
            else:
                result["cleanup"][key] = False
        for kind, name, flag, report_key in [
            ("volume", VOLUME, "volume", "clone_volume_removed"),
            ("network", NETWORK, "network", "internal_network_removed"),
        ]:
            if not qualified or not attempted[flag]:
                result["cleanup"][report_key] = True
                continue
            rc = exists(kind, name)
            if rc == 0:
                done, _, _ = invoke(["podman", kind, "rm", name], timeout=100)
                result["cleanup"][report_key] = done == 0
            elif rc == 1:
                result["cleanup"][report_key] = True
            else:
                result["cleanup"][report_key] = False
    if not all(result["cleanup"].values()):
        result["status"] = "cleanup_incomplete"
    result["comparison"] = comparison(result["cases"])
    return result


def main():
    result = collect(socket.getfqdn(), pwd.getpwuid(os.geteuid()).pw_name)
    print(json.dumps(result, sort_keys=True))
    if result["status"] == "refused":
        sys.exit(2)


if __name__ == "__main__":
    main()
