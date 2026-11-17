#!/usr/bin/env python3
"""Prepare ONE isolated Nextcloud config overlay for an owner-retained trial DB.

Run through rootless "podman unshare python3 -c <this source>..." on Peanut.
This only writes to a previously extracted /nextcloud-restore-trials/<id>/html
tree, never a production config. The existing private Maintenance handoff
remains the sole authority for the isolated PostgreSQL password.

Do not log/print the password or existing PHP configuration.
"""
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys

HOST = "peanut.arcane.sanctum"
ROOT = Path("/home/wdc2/.local/share/sanctum-services/nextcloud-restore-trials")
RECOVERY = re.compile(r"nextcloud-[0-9]{8}t[0-9]{6}\Z")
CID = re.compile(r"[a-f0-9]{64}\Z")
NAME = "zzzz-sanctum-isolated.config.php"


class Refusal(Exception):
    pass


def private_regular(path):
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode) != 0o600:
        raise Refusal("requires_owner_private_regular_file")
    return path


def load_receipt(receipt_path, password_file):
    private_regular(receipt_path)
    data = json.loads(receipt_path.read_text(encoding="ascii"))
    cid = data.get("container_id", "")
    if (data.get("status") != "isolated_database_ready_for_application"
            or not isinstance(cid, str) or not CID.fullmatch(cid)
            or data.get("password_file") != str(password_file)
            or data.get("database") != "nextcloud_restore"
            or data.get("username") != "nextcloud_restore"
            or data.get("host") != "127.0.0.1"
            or data.get("port") != 5432
            or data.get("network") != "container:" + cid
            or data.get("application_started") is not False
            or data.get("production_database_contacted") is not False
            or type(data.get("restored_application_tables")) is not int
            or data["restored_application_tables"] < 1):
        raise Refusal("unexpected_maintenance_owner_handoff")
    return cid, data["restored_application_tables"]


def php_overlay(password):
    if not CID.fullmatch(password):
        raise Refusal("unexpected_password_shape")
    # This file is in an isolated restored copy; Nextcloud's documented
    # multiple config system merges these values after config.php.
    return ("<?php\n"
            "$CONFIG = [\n"
            "  'dbtype' => 'pgsql',\n"
            "  'dbhost' => '127.0.0.1',\n"
            "  'dbname' => 'nextcloud_restore',\n"
            "  'dbuser' => 'nextcloud_restore',\n"
            f"  'dbpassword' => '{password}',\n"
            "  'maintenance' => false,\n"
            "  'trusted_domains' => ['127.0.0.1', 'localhost'],\n"
            "  'overwrite.cli.url' => 'http://127.0.0.1',\n"
            "  'overwritehost' => '127.0.0.1',\n"
            "  'overwriteprotocol' => 'http',\n"
            "];\n")


def prepare(recovery_id, html_dir, password_file):
    if socket.getfqdn() != HOST or os.geteuid() != 0:
        raise Refusal("requires_peanut_rootless_unshare")
    if not RECOVERY.fullmatch(recovery_id):
        raise Refusal("invalid_recovery_id")
    expected = ROOT / recovery_id
    if html_dir != expected / "html":
        raise Refusal("unexpected_isolated_html_path")
    expected_handoff = expected / "postgresql-trial"
    if password_file != expected_handoff / "postgresql-trial-password":
        raise Refusal("unexpected_maintenance_password_path")
    for path in (ROOT, expected, html_dir, html_dir / "config", expected_handoff):
        s = path.lstat()
        if not stat.S_ISDIR(s.st_mode):
            raise Refusal("requires_unlinked_restored_directory")
    if stat.S_IMODE(expected.lstat().st_mode) != 0o700:
        raise Refusal("requires_private_restore_directory")
    installed_config = (html_dir / "config" / "config.php").lstat()
    if not stat.S_ISREG(installed_config.st_mode):
        raise Refusal("missing_or_linked_restored_nextcloud_config")
    receipt = expected_handoff / "postgresql-trial.json"
    cid, tables = load_receipt(receipt, password_file)
    private_regular(password_file)
    password = password_file.read_text(encoding="ascii").strip()
    output = html_dir / "config" / NAME
    # Never permit a later ordered config override to redirect DB back to
    # production. Also refuse overwriting an existing isolated trial.
    for path in (html_dir / "config").glob("*.config.php"):
        if path.name >= NAME:
            raise Refusal("unexpected_existing_or_later_config_override")
    source = php_overlay(password)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="ascii") as target:
            target.write(source)
            target.flush()
            os.fchown(target.fileno(), 33, 33)
            os.fchmod(target.fileno(), 0o600)
            os.fsync(target.fileno())
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"status": "isolated_nextcloud_config_ready",
            "recovery_id": recovery_id, "db_container_id": cid,
            "restored_application_tables": tables,
            "isolated_only": True, "production_database_contacted": False,
            "original_restored_config_unchanged": True,
            "password_written_only_into_private_isolated_override": True,
            "override_filename": NAME}


def main(argv):
    if len(argv) != 4:
        print("Usage: nextcloud-isolated-config.py RECOVERY_ID RESTORED_HTML_DIR OWNER_PASSWORD_FILE",
              file=sys.stderr)
        return 2
    try:
        result = prepare(argv[1], Path(argv[2]), Path(argv[3]))
    except (Refusal, OSError, ValueError, KeyError, UnicodeError, json.JSONDecodeError):
        result = {"status": "refused", "reason": "invalid_or_missing_private_trial_input"}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "isolated_nextcloud_config_ready" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
