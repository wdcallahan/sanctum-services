#!/usr/bin/env python3
"""Pinpoint common LinkStack image startup failure without touching saved data.

Kvin rootless only. Inspect the exact already-pulled digest; run bounded
read-only *classification* checks inside ephemeral, unmounted containers; then
compare startup with no-new-privileges versus normal rootless Podman. Both
use one temporary --internal --disable-dns bridge, zero host ports and NO
application volumes. Suppress all subprocess output except finite categories.
"""
import json
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
PREFIX = "sanctum-linkstack-runtime-diag-20261112t105926"
NETWORK = PREFIX + "-internal"
NAMES = {"restricted": PREFIX + "-restricted",
         "podman_default": PREFIX + "-default"}
MAX_CAPTURE = 131072
ERROR_PATTERNS = {
    "permission_denied": (r"permission denied", r"operation not permitted", r"eacces"),
    "cannot_create_file": (r"can't create", r"cannot create", r"failed to create"),
    "cannot_open_file": (r"can't open", r"cannot open", r"error opening"),
    "missing_file": (r"no such file", r"not found", r"missing file"),
    "apache_config": (r"ah00526", r"syntax error", r"invalid command"),
    "apache_bind": (r"ah00072", r"could not bind", r"address already in use"),
    "apache_module": (r"cannot load", r"failed to load", r"module .* not found"),
    "apache_pid": (r"httpd\.pid", r"pid file"),
    "php_error": (r"php fatal", r"uncaught exception", r"parse error"),
    "readonly": (r"read.only file system", r"readonly database"),
    "segmentation_fault": (r"segmentation fault", r"core dumped"),
}
STAGES = {
    "version_banner_seen": b"LINKSTACK v",
    "config_update_seen": b"Updating Configuration: Apache Base",
    "apache_launch_banner_seen": b"Running Apache",
}
# No shell expansion; fixed script only checks image-internal paths, not content.
STATIC_SCRIPT = (
    'a=0;b=0;c=0;d=0;'
    '[ -r /htdocs/version.json ] && a=1;'
    '[ -w /etc/php83/conf.d/40-custom.ini ] && b=1;'
    '[ -w /htdocs ] && c=1;'
    '[ -x /usr/sbin/httpd ] && d=1;'
    'printf \'{"version_readable":%s,"php_ini_writable":%s,'
    '"htdocs_writable":%s,"apache_executable":%s}\\n\' "$a" "$b" "$c" "$d"'
)
STATIC_FIELDS = ("version_readable", "php_ini_writable",
                 "htdocs_writable", "apache_executable")


class StopProbe(Exception):
    def __init__(self, phase):
        self.phase = phase


def run(args, timeout=20):
    try:
        result = subprocess.run(args, stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=timeout, check=False)
        if len(result.stdout) > MAX_CAPTURE or len(result.stderr) > MAX_CAPTURE:
            return -1, b"", b""
        return result.returncode, result.stdout, result.stderr
    except (OSError, subprocess.TimeoutExpired):
        return -1, b"", b""


def from_json(blob):
    try:
        return json.loads(blob)
    except (TypeError, ValueError, UnicodeError):
        return None


def classification(log):
    if not isinstance(log, bytes) or len(log) > MAX_CAPTURE:
        return {"error_categories": ["unavailable"], **{k: False for k in STAGES}}
    text = log.decode("utf-8", "replace").lower()
    categories = sorted(k for k, patterns in ERROR_PATTERNS.items()
                        if any(re.search(p, text) for p in patterns))
    return {
        "error_categories": categories or ["unclassified"],
        **{key: needle.lower() in log.lower() for key, needle in STAGES.items()},
    }


def verify_image():
    rc, out, _ = run(["podman", "image", "inspect", IMAGE])
    found = from_json(out)
    if rc or not isinstance(found, list) or len(found) != 1:
        return None
    item = found[0]
    if (not isinstance(item, dict) or item.get("Id") != IMAGE_ID
            or item.get("Architecture") != "arm64" or item.get("Os") != "linux"):
        return None
    config = item.get("Config", {})
    if not isinstance(config, dict):
        config = {}
    command = config.get("Cmd")
    user = config.get("User")
    workdir = config.get("WorkingDir")
    return {"pinned_image_identity": True,
            "image_user_apache": user in ("apache", "apache:apache", "100", "100:101"),
            "image_cmd_entrypoint_script": isinstance(command, list)
                and any(isinstance(c, str) and "docker-entrypoint.sh" in c for c in command),
            "image_workdir_htdocs": workdir == "/htdocs"}


def static_prerequisites():
    args = ["podman", "run", "--rm", "--network", "none",
            "--pull", "never", "--entrypoint", "/bin/sh",
            IMAGE, "-c", STATIC_SCRIPT]
    rc, out, _ = run(args)
    vals = from_json(out)
    if rc or not isinstance(vals, dict) or set(vals) != set(STATIC_FIELDS):
        return {"status": "unavailable"}
    if any(type(vals[key]) is not int or vals[key] not in (0, 1) for key in STATIC_FIELDS):
        return {"status": "unavailable"}
    return {"status": "observed",
            **{name: bool(vals[name]) for name in STATIC_FIELDS}}


def apache_syntax():
    env = ["--env", "SERVER_ADMIN=you@example.com",
           "--env", "HTTP_SERVER_NAME=localhost",
           "--env", "HTTPS_SERVER_NAME=localhost",
           "--env", "LOG_LEVEL=info"]
    args = ["podman", "run", "--rm", "--network", "none",
            "--pull", "never", *env, "--entrypoint", "/usr/sbin/httpd",
            IMAGE, "-t"]
    rc, out, err = run(args)
    if rc < 0:
        return {"status": "unavailable"}
    return {"status": "observed", "syntax_valid": rc == 0,
            "diagnostics": classification(out + err)["error_categories"]}


def available(kind, name):
    rc, _, _ = run(["podman", kind, "exists", name])
    return rc == 1


def one_case(name, network, restrict):
    args = ["podman", "run", "--detach", "--name", name,
            "--network", network, "--pull", "never"]
    if restrict:
        args += ["--security-opt", "no-new-privileges"]
    args += ["--env", "HTTP_SERVER_NAME=localhost", IMAGE]
    code, _, raw_error = run(args, timeout=35)
    if code:
        return {"status": "start_command_failed", "running": None,
                "exit_code": None, "oom_killed": None, "http_status": None,
                "log": classification(raw_error)}
    time.sleep(2)
    rc, out, _ = run(["podman", "container", "inspect",
                       "--format", "{{json .State}}", name])
    state = from_json(out)
    if rc or not isinstance(state, dict):
        return {"status": "state_unavailable", "running": None,
                "exit_code": None, "oom_killed": None, "http_status": None,
                "log": {"error_categories": ["unavailable"]}}
    running = state.get("Running")
    exitcode = state.get("ExitCode")
    oom = state.get("OOMKilled")
    if not isinstance(running, bool):
        running = None
    if type(exitcode) is not int or not 0 <= exitcode <= 255:
        exitcode = None
    if not isinstance(oom, bool):
        oom = None
    http = None
    if running:
        code, val, _ = run(["podman", "exec", name, "curl",
                            "--silent", "--output", "/dev/null",
                            "--max-time", "5", "--write-out", "%{http_code}",
                            "--header", "Host: dir.nexus.sanctum",
                            "http://127.0.0.1/"], timeout=10)
        status = val.decode("ascii", "ignore").strip()
        if not code and re.fullmatch(r"[1-5][0-9]{2}", status):
            http = int(status)
    logs_rc, logs, _ = run(["podman", "logs", "--tail", "100", name])
    log = classification(logs) if logs_rc == 0 else classification(None)
    return {"status": "observed", "running": running,
            "exit_code": exitcode, "oom_killed": oom,
            "http_status": http, "log": log}


def compare(cases):
    a, b = cases.get("restricted"), cases.get("podman_default")
    if not isinstance(a, dict) or not isinstance(b, dict):
        return "incomplete"
    if a.get("status") != "observed" or b.get("status") != "observed":
        return "incomplete"
    if a["running"] is False and b["running"] is True:
        return "only_no_new_privileges_variant_exits"
    if a["running"] is True and b["running"] is False:
        return "only_default_podman_variant_exits"
    if a["running"] is True and b["running"] is True:
        return "both_running"
    if a["running"] is False and b["running"] is False:
        return "both_exit_common_image_startup"
    return "unknown_running_state"


def collect(host, account):
    if host != HOST or account != ACCOUNT:
        return {"status": "refused", "reason": "wrong_host_or_account"}
    result = {
        "schema": "sanctum-linkstack-image-runtime-diagnostic/v1",
        "observer": host, "image_source_unchanged": True,
        "original_saved_volumes_unchanged": True,
        "kvar_and_production_untouched": True,
        "raw_logs_or_credentials_returned": False,
        "application_recovery_accepted": False, "status": "partial",
        "image": None, "static_prerequisites": None, "apache_syntax": None,
        "cases": {},
        "cleanup": {"restricted_container_removed": False,
                    "default_container_removed": False,
                    "internal_network_removed": False}}
    flags = {"network": False, "restricted": False, "podman_default": False}
    try:
        result["image"] = verify_image()
        if result["image"] is None:
            raise StopProbe("pinned_image_identity")
        result["static_prerequisites"] = static_prerequisites()
        result["apache_syntax"] = apache_syntax()
        if any(not available("container", name) for name in NAMES.values()):
            raise StopProbe("reserved_container_identity_occupied")
        if not available("network", NETWORK):
            raise StopProbe("reserved_network_identity_occupied")
        rc, _, _ = run(["podman", "network", "create", "--driver", "bridge",
                         "--internal", "--disable-dns", NETWORK])
        if rc:
            raise StopProbe("internal_network_create")
        flags["network"] = True
        rc, raw, _ = run(["podman", "network", "inspect", NETWORK])
        nets = from_json(raw)
        if (rc or not isinstance(nets, list) or len(nets) != 1
                or not isinstance(nets[0], dict)
                or nets[0].get("name") != NETWORK
                or nets[0].get("driver") != "bridge"
                or nets[0].get("internal") is not True
                or nets[0].get("dns_enabled") is not False):
            raise StopProbe("isolated_network_contract")
        for case, container in NAMES.items():
            result["cases"][case] = one_case(
                container, NETWORK, restrict=(case == "restricted"))
            rc, _, _ = run(["podman", "container", "exists", container])
            flags[case] = rc == 0
        result["status"] = "observed"
    except StopProbe as ex:
        result["failure_phase"] = ex.phase
    except Exception:
        result["failure_phase"] = "unexpected_internal_error"
    finally:
        for case in ("podman_default", "restricted"):
            container = NAMES[case]
            code, _, _ = run(["podman", "container", "exists", container])
            if flags[case] or code == 0:
                rc, _, _ = run(["podman", "rm", "--force", container])
                result["cleanup"][case + "_container_removed"
                                  if case == "restricted"
                                  else "default_container_removed"] = rc == 0
            else:
                result["cleanup"]["restricted_container_removed"
                                  if case == "restricted"
                                  else "default_container_removed"] = True
        rc, _, _ = run(["podman", "network", "exists", NETWORK])
        if flags["network"] or rc == 0:
            rc, _, _ = run(["podman", "network", "rm", NETWORK])
            result["cleanup"]["internal_network_removed"] = rc == 0
        else:
            result["cleanup"]["internal_network_removed"] = True
    if not all(result["cleanup"].values()):
        result["status"] = "cleanup_incomplete"
    result["comparison"] = compare(result["cases"])
    return result


def main():
    report = collect(socket.getfqdn(), pwd.getpwuid(__import__("os").geteuid()).pw_name)
    print(json.dumps(report, sort_keys=True))
    if report["status"] == "refused":
        sys.exit(2)


if __name__ == "__main__":
    main()
