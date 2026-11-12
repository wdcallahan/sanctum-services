#!/usr/bin/env python3
"""Kvin-only, image-only test of Apache low-port permissions in rootless Podman.

One ephemeral internal/no-DNS bridge; two uniquely named containers. Compare
ordinary rootless startup to --sysctl net.ipv4.ip_unprivileged_port_start=80
INSIDE ONLY the second container's network namespace. No host sysctl write,
volumes, host network, published ports, Kvar access, or secrets/raw log output.
"""
import json
import os
import pwd
import re
import socket
import subprocess
import sys
import time

HOST = "kvin.outer.sanctum"
ACCOUNT = "wdc2"
IMAGE = ("docker.io/linkstackorg/linkstack@sha256:"
         "b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1")
IMAGE_ID = "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"
PREFIX = "sanctum-linkstack-port80-probe-20261112t105926"
NETWORK = PREFIX + "-internal"
NAMES = {"baseline": PREFIX + "-baseline",
         "namespaced_port80": PREFIX + "-port80"}
SYSCTL = "net.ipv4.ip_unprivileged_port_start=80"
MAX_OUTPUT = 131072
PATTERNS = {
    "listen_permission_denied": (
        r"(?:permission denied|operation not permitted|eacces)",
        r"(?:make_sock|ah00072|could not bind|listen)"),
    "apache_log_open": (r"ah00015|unable to open logs",),
    "apache_listen_socket": (r"ah00072|ah00026|make_sock|could not bind",),
    "apache_startup_config_failed": (r"ah00016|configuration failed",),
}
STAGES = {
    "entrypoint_started": b"LINKSTACK v",
    "apache_launch_reached": b"Running Apache",
}

class Refusal(Exception):
    def __init__(self, phase):
        self.phase = phase


def invoke(argv, timeout=18):
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                           timeout=timeout, check=False)
        if len(p.stdout) + len(p.stderr) > MAX_OUTPUT:
            return -1, b"", b""
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired):
        return -1, b"", b""


def parse(raw):
    try:
        return json.loads(raw)
    except (TypeError, ValueError, UnicodeError):
        return None


def categories(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_OUTPUT:
        return {"error_classes": ["unavailable"], **{k: False for k in STAGES}}
    lower = raw.decode("utf-8", "replace").lower()
    keys = set()
    for label, expressions in PATTERNS.items():
        if (label == "listen_permission_denied"
                and not all(re.search(term, lower) for term in expressions)):
            continue
        if label != "listen_permission_denied" and not any(
                re.search(term, lower) for term in expressions):
            continue
        keys.add(label)
    return {"error_classes": sorted(keys) or ["unclassified"],
            **{k: value.lower() in raw.lower() for k, value in STAGES.items()}}


def verify_image(runner=invoke):
    rc, out, _ = runner(["podman", "image", "inspect", IMAGE])
    obj = parse(out)
    if (rc != 0 or not isinstance(obj, list) or len(obj) != 1
            or not isinstance(obj[0], dict)):
        return False
    im = obj[0]
    return (im.get("Id") == IMAGE_ID and im.get("Architecture") == "arm64"
            and im.get("Os") == "linux")


def no_existing_resources(runner=invoke):
    for kind, name in [("network", NETWORK)] + [
            ("container", name) for name in NAMES.values()]:
        rc, _, _ = runner(["podman", kind, "exists", name])
        if rc != 1:
            return False
    return True


def run_case(name, network, allow_port80, runner=invoke, sleeper=time.sleep):
    cmd = ["podman", "run", "--detach", "--name", name,
           "--network", network, "--pull", "never"]
    if allow_port80:
        cmd += ["--sysctl", SYSCTL]
    cmd += ["--env", "HTTP_SERVER_NAME=localhost", IMAGE]
    rc, _, raw_error = runner(cmd, timeout=35)
    if rc:
        return {"status": "start_command_failed",
                "running": None, "exit_code": None, "oom_killed": None,
                "http_status": None, "log": categories(raw_error)}
    sleeper(2)
    rc, output, _ = runner(["podman", "container", "inspect",
                            "--format", "{{json .State}}", name])
    state = parse(output)
    if rc or not isinstance(state, dict):
        return {"status": "container_state_unavailable",
                "running": None, "exit_code": None, "oom_killed": None,
                "http_status": None, "log": categories(None)}
    running = state.get("Running")
    code = state.get("ExitCode")
    oom = state.get("OOMKilled")
    running = running if type(running) is bool else None
    code = code if type(code) is int and 0 <= code <= 255 else None
    oom = oom if type(oom) is bool else None
    http = None
    if running:
        call_rc, data, _ = runner(
            ["podman", "exec", name, "curl", "--silent", "--output",
             "/dev/null", "--max-time", "5", "--write-out", "%{http_code}",
             "--header", "Host: dir.nexus.sanctum", "http://127.0.0.1/"],
            timeout=10)
        txt = data.decode("ascii", "ignore").strip()
        if call_rc == 0 and re.fullmatch(r"[1-5][0-9]{2}", txt):
            http = int(txt)
    logs_rc, stdout, stderr = runner(["podman", "logs", "--tail", "100", name])
    log = categories(stdout + b"\n" + stderr) if logs_rc == 0 else categories(None)
    log["stderr_present"] = bool(stderr) if logs_rc == 0 else False
    return {"status": "observed", "running": running, "exit_code": code,
            "oom_killed": oom, "http_status": http, "log": log}


def compare(cases):
    a = cases.get("baseline", {})
    b = cases.get("namespaced_port80", {})
    if a.get("status") != "observed" or b.get("status") != "observed":
        return "incomplete_or_sysctl_unavailable"
    if a.get("running") is False and b.get("running") is True:
        return "namespaced_low_port_policy_enables_startup"
    if a.get("running") is False and b.get("running") is False:
        return "both_exit_with_or_without_namespace_override"
    if a.get("running") is True and b.get("running") is True:
        return "both_start_successfully"
    return "inconclusive"


def collect(host, user, runner=invoke, sleeper=time.sleep):
    if host != HOST or user != ACCOUNT:
        return {"status": "refused", "reason": "wrong_host_or_account"}
    result = {
        "schema": "sanctum-linkstack-namespaced-bind-diagnostic/v1",
        "observer": host,
        "host_sysctl_unchanged": True,
        "application_volumes_unchanged": True,
        "kvar_and_production_untouched": True,
        "private_logs_or_data_returned": False,
        "restored_application_accepted": False,
        "status": "partial",
        "cases": {},
        "cleanup": {
            "baseline_container_removed": False,
            "namespaced_port80_container_removed": False,
            "temporary_network_removed": False,
        },
    }
    qualified = False
    attempted = {"network": False, **{key: False for key in NAMES}}
    try:
        if not verify_image(runner):
            raise Refusal("exact_cached_image_identity")
        if not no_existing_resources(runner):
            raise Refusal("reserved_resource_name_occupied_or_unknown")
        qualified = True
        attempted["network"] = True
        rc, _, _ = runner(["podman", "network", "create", "--driver", "bridge",
                            "--internal", "--disable-dns", NETWORK])
        if rc:
            raise Refusal("temporary_network_create")
        rc, data, _ = runner(["podman", "network", "inspect", NETWORK])
        net = parse(data)
        if (rc or not isinstance(net, list) or len(net) != 1
                or not isinstance(net[0], dict)
                or net[0].get("name") != NETWORK
                or net[0].get("driver") != "bridge"
                or net[0].get("internal") is not True
                or net[0].get("dns_enabled") is not False):
            raise Refusal("temporary_network_not_internal")
        for key, name in NAMES.items():
            attempted[key] = True
            result["cases"][key] = run_case(
                name, NETWORK, key == "namespaced_port80", runner, sleeper)
        result["status"] = "observed"
    except Refusal as error:
        result["failure_phase"] = error.phase
    except Exception:
        result["failure_phase"] = "unexpected_internal_error"
    finally:
        for key, name in NAMES.items():
            outkey = key + "_container_removed"
            if not qualified or not attempted[key]:
                result["cleanup"][outkey] = True
                continue
            rc, _, _ = runner(["podman", "container", "exists", name])
            if rc == 0:
                removed, _, _ = runner(["podman", "rm", "--force", name])
                result["cleanup"][outkey] = removed == 0
            elif rc == 1:
                result["cleanup"][outkey] = True
        if not qualified or not attempted["network"]:
            result["cleanup"]["temporary_network_removed"] = True
        else:
            rc, _, _ = runner(["podman", "network", "exists", NETWORK])
            if rc == 0:
                removed, _, _ = runner(["podman", "network", "rm", NETWORK])
                result["cleanup"]["temporary_network_removed"] = removed == 0
            elif rc == 1:
                result["cleanup"]["temporary_network_removed"] = True
    if not all(result["cleanup"].values()):
        result["status"] = "cleanup_incomplete"
    result["comparison"] = compare(result["cases"])
    return result


def main():
    report = collect(socket.getfqdn(), pwd.getpwuid(os.geteuid()).pw_name)
    print(json.dumps(report, sort_keys=True))
    if report["status"] == "refused":
        sys.exit(2)


if __name__ == "__main__":
    main()
