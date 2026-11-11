#!/usr/bin/env python3
"""Create a Kvin-local Uptime Kuma admin secret with exclusive file creation.

The account is subsequently initialized by Kuma's own authenticated Socket.IO
flow; never edit its SQLite tables. This file must join recoverable backups.
"""
import json
import os
from pathlib import Path
import secrets
import sys

TARGET = Path("/home/wdc2/.config/sanctum-services/secrets/kuma-admin.json")


def main():
    if len(sys.argv) != 2 or Path(sys.argv[1]) != TARGET:
        raise SystemExit("Refusing to write outside the one owned Kvin secret path")
    if TARGET.is_symlink() or TARGET.parent.is_symlink():
        raise SystemExit("Refusing symlinked secret path")
    if not TARGET.parent.is_dir():
        raise SystemExit("Private secret directory must exist first")

    secret = {
        "username": "sanctum-admin",
        "password": secrets.token_urlsafe(48),
    }
    fd = os.open(TARGET, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        json.dump(secret, out)
        out.write("\n")

    print("Created owned private Kuma administrator secret (value withheld)")


if __name__ == "__main__":
    main()
