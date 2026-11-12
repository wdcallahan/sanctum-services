#!/usr/bin/env python3
"""Classify LinkStack's failed isolated startup without exposing application data.

Only Kvin/wdc2. Reuses a verified private backup, but imports a NEW temporary
copy; never mounts the previously accepted restore volume or a production
volume. Runs two disposable containers on one temporary internal/no-DNS
network: (1) image-only, (2) a fresh copy of saved /htdocs. Project only
bounded process/HTTP/log categories. No raw logs, configuration or content.
All created resources are cleaned in finally. No production ports.
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
USER = "wdc2"
IMAGE = ("docker.io/linkstackorg/linkstack@sha256:"
         "b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1")
IMAGE_ID = "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"
ARCHIVE = ("/home/wdc2/.local/share/sanctum-services/backups/linkstack/"
           "linkstack-20261112t105926.tar")
ARCHIVE_SIZE = 93845504
ARCHIVE_SHA = "a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa"
PREFIX = "sanctum-linkstack-diag-20261112t105926"
NETWORK = PREFIX + "-internal"
VOLUME = PREFIX + "-copy"
CASES = {"image_only": PREFIX + "-image", "imported_copy": PREFIX + "-data"}
ERROR_TAGS = (
    ("permission_denied", ("permission denied", "operation not permitted", "eacces")),
    ("read_only", ("read-only file system", "readonly database")),
    ("missing_path", ("no such file or directory", "file not found")),
    ("apache_config", ("syntax error on line", "ah00526", "invalid command")),
    ("apache_bind", ("ah00072", "address already in use", "could not bind")),
    ("sqlite_error", ("sqlite", "sqlstate", "database is locked")),
    ("php_error", ("php fatal error", "uncaught exception", "php parse error")),
    ("pid_file", ("httpd.pid", "pid file")),
)
MAX_OUTPUT = 262144

class ProbeFailure(Exception):
    def __init__(self, phase):
        self.phase = phase


def invoke(argv, timeout=20):
    try:
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                           timeout=timeout, check=False)
        if len(r.stdout) > MAX_OUTPUT or len(r.stderr) > MAX_OUTPUT:
            return -1, b"", b""
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.TimeoutExpired):
        return -1, b"", b""


def parsed_json(value):
    try:
        return json.loads(value)
    except (ValueError, UnicodeError, TypeError):
        return None


def log_categories(raw):
    if not isinstance(raw, (bytes, bytearray)) or len(raw) > MAX_OUTPUT:
        return ["log_unavailable"]
    low = raw.decode("utf-8", "replace").lower()
    return sorted({label for label, terms in ERROR_TAGS
                   if any(term in low for term in terms)}) or ["unclassified"]


def check_archive():
    p = Path(ARCHIVE)
    try:
        st = p.lstat()
        if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != 0o600:
            return False
        if st.st_uid != os.geteuid() or st.st_size != ARCHIVE_SIZE:
            return False
        h = hashlib.sha256()
        with p.open("rb") as handle:
            for piece in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(piece)
        return h.hexdigest() == ARCHIVE_SHA
    except OSError:
        return False


def verify_cached_image():
    code, output, _ = invoke(["podman", "image", "inspect", IMAGE])
    images = parsed_json(output)
    if code or not isinstance(images, list) or len(images) != 1:
        return False
    i = images[0]
    return (isinstance(i, dict)
            and i.get("Id") == IMAGE_ID
            and i.get("Architecture") == "arm64"
            and i.get("Os") == "linux")


def absent(kind, name):
    code, _, _ = invoke(["podman", kind, "exists", name])
    return code == 1


def observe_trial(label, name, network, volume=None):
    argv = ["podman", "run", "--detach", "--name", name,
            "--network", network, "--pull", "never",
            "--security-opt", "no-new-privileges"]
    if volume:
        argv += ["--volume", volume + ":/htdocs"]
    argv += ["--env", "HTTP_SERVER_NAME=localhost", IMAGE]
    code, _, _ = invoke(argv, timeout=35)
    if code != 0:
        return {"status": "start_command_failed", "running": False,
                "exit_code": None, "oom_killed": None,
                "http_status": None, "log_categories": ["unavailable"]}
    time.sleep(2)
    code, stdout, _ = invoke(["podman", "container", "inspect",
                              "--format", "{{json .State}}", name])
    state = parsed_json(stdout)
    if code or not isinstance(state, dict):
        return {"status": "inspect_unavailable", "running": None,
                "exit_code": None, "oom_killed": None,
                "http_status": None, "log_categories": ["unavailable"]}
    running = state.get("Running")
    exit_code = state.get("ExitCode")
    oom = state.get("OOMKilled")
    if not isinstance(running, bool):
        running = None
    if not isinstance(exit_code, int) or not 0 <= exit_code <= 255:
        exit_code = None
    if not isinstance(oom, bool):
        oom = None
    http_code = None
    if running is True:
        rc, text, _ = invoke(["podman", "exec", name, "curl", "--silent",
                              "--output", "/dev/null", "--max-time", "5",
                              "--write-out", "%{http_code}",
                              "--header", "Host: dir.nexus.sanctum",
                              "http://127.0.0.1/"], timeout=10)
        val = text.decode("ascii", "ignore").strip()
        if rc == 0 and re.fullmatch(r"[1-5][0-9]{2}", val):
            http_code = int(val)
    rc, logs, _ = invoke(["podman", "logs", "--tail", "100", name])
    categories = log_categories(logs) if rc == 0 else ["log_unavailable"]
    return {"status": "observed", "running": running, "exit_code": exit_code,
            "oom_killed": oom, "http_status": http_code,
            "log_categories": categories}


def collect(host, user):
    if host != HOST or user != USER:
        return {"status": "refused", "reason": "wrong_host_or_account"}
    report = {"schema": "sanctum-linkstack-startup-diagnosis/v1",
              "observer": host,
              "source_archive_unchanged": True,
              "accepted_restore_volume_unchanged": True,
              "kvar_untouched": True,
              "production_services_or_network_changed": False,
              "private_logs_or_app_contents_returned": False,
              "application_boot_accepted": False,
              "trials": {},
              "cleanup": {"image_container_removed": False,
                          "data_container_removed": False,
                          "temporary_volume_removed": False,
                          "temporary_network_removed": False},
              "status": "partial"}
    stage = "preflight"
    made = {"network": False, "volume": False,
            "image_only": False, "imported_copy": False}
    try:
        if not check_archive():
            raise ProbeFailure("source_archive_identity")
        if not verify_cached_image():
            raise ProbeFailure("pinned_image_identity")
        for kind, name in (("network", NETWORK), ("volume", VOLUME)):
            if not absent(kind, name):
                raise ProbeFailure("reserved_name_not_empty")
        for name in CASES.values():
            if not absent("container", name):
                raise ProbeFailure("reserved_name_not_empty")
        stage = "network_create"
        rc, _, _ = invoke(["podman", "network", "create", "--driver", "bridge",
                           "--internal", "--disable-dns", NETWORK])
        if rc:
            raise ProbeFailure(stage)
        made["network"] = True
        rc, stdout, _ = invoke(["podman", "network", "inspect", NETWORK])
        nets = parsed_json(stdout)
        if (rc or not isinstance(nets, list) or len(nets) != 1
                or nets[0].get("name") != NETWORK
                or nets[0].get("driver") != "bridge"
                or nets[0].get("internal") is not True
                or nets[0].get("dns_enabled") is not False):
            raise ProbeFailure("internal_network_contract")
        stage = "temporary_volume_create"
        rc, _, _ = invoke(["podman", "volume", "create", VOLUME])
        if rc:
            raise ProbeFailure(stage)
        made["volume"] = True
        rc, _, _ = invoke(["podman", "volume", "import", VOLUME, ARCHIVE], timeout=90)
        if rc:
            raise ProbeFailure("temporary_volume_import")
        for label, name in CASES.items():
            stage = "trial_" + label
            # If Podman creates a container but run returns nonzero, finally
            # still checks this exact unique name and removes it.
            report["trials"][label] = observe_trial(
                label, name, NETWORK, VOLUME if label == "imported_copy" else None)
            exists_code, _, _ = invoke(["podman", "container", "exists", name])
            if exists_code == 0:
                made[label] = True
        report["status"] = "observed"
    except ProbeFailure as ex:
        report["failure_phase"] = ex.phase
    except Exception:
        report["failure_phase"] = "unexpected_internal_error"
    finally:
        # Cleanup only the four unique names, never global Podman objects.
        for label in ("imported_copy", "image_only"):
            name = CASES[label]
            rc, _, _ = invoke(["podman", "container", "exists", name])
            if made[label] or rc == 0:
                rc, _, _ = invoke(["podman", "rm", "--force", name])
                report["cleanup"]["data_container_removed" if label == "imported_copy"
                                  else "image_container_removed"] = rc == 0
            else:
                report["cleanup"]["data_container_removed" if label == "imported_copy"
                                  else "image_container_removed"] = True
        for kind, name, result_name in (
            ("volume", VOLUME, "temporary_volume_removed"),
            ("network", NETWORK, "temporary_network_removed")):
            rc, _, _ = invoke(["podman", kind, "exists", name])
            if made[kind] or rc == 0:
                verb = "rm"
                result, _, _ = invoke(["podman", kind, verb, name])
                report["cleanup"][result_name] = result == 0
            else:
                report["cleanup"][result_name] = True
    if not all(report["cleanup"].values()):
        report["status"] = "cleanup_incomplete"
    report["reason_comparison"] = classify(report["trials"])
    return report


def classify(trials):
    a = trials.get("image_only")
    b = trials.get("imported_copy")
    if not a or not b:
        return "incomplete_trials"
    if a.get("status") != "observed" or b.get("status") != "observed":
        return "incomplete_trials"
    if a["running"] is False and b["running"] is False:
        return "both_exit_startup_independent_of_restored_data_possible"
    if a["running"] is True and b["running"] is False:
        return "restored_data_or_volume_mount_specific_failure"
    if a["running"] is False and b["running"] is True:
        return "image_seed_only_failure"
    if a["running"] is True and b["running"] is True:
        return "both_running_compare_http_statuses"
    return "unknown_process_state"


def main():
    report = collect(socket.getfqdn(), pwd.getpwuid(os.geteuid()).pw_name)
    print(json.dumps(report, sort_keys=True))
    if report["status"] == "refused":
        sys.exit(2)


if __name__ == "__main__":
    main()
