#!/usr/bin/env python3
"""Stream the two already-verified Kvar Pi-hole archives to Kvin, without slurp.

Runs only as wdc2 on Kvin. Exact original root-owned files are read over the
existing SSH path using noninteractive sudo; temporary local bytes remain 0600.
No content is printed, no local backup is overwritten, no host service changed.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

DEST = Path("/home/wdc2/.local/share/sanctum-services/backups/pihole")
SRC = Path("/var/lib/sanctum-services/backups/pihole")
ITEMS = {
    "etc-pihole": {
        "name": "pihole-etc-20261112t161524.tar",
        "bytes": 1305682432,
        "sha256": "4731ee1765d33a14ef1a01dabbac23e43effaca941695281b3f74cdb5f72e3da",
    },
    "etc-dnsmasq": {
        "name": "pihole-dnsmasq-20261112t161524.tar",
        "bytes": 1024,
        "sha256": "5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef",
    },
}

def _hash_existing(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for data in iter(lambda: source.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

def stream_one(kind):
    if kind not in ITEMS or os.geteuid() == 0 or os.getuid() != os.geteuid():
        raise ValueError("invalid_scope_or_archive")
    spec = ITEMS[kind]
    if DEST.is_symlink():
        raise ValueError("invalid_destination")
    DEST.mkdir(parents=True, mode=0o700, exist_ok=True)
    dest = DEST / spec["name"]
    partial = DEST / (spec["name"] + ".partial")
    if dest.exists() or dest.is_symlink():
        meta = dest.lstat()
        if (not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.getuid()
                or stat.S_IMODE(meta.st_mode) != 0o600
                or meta.st_size != spec["bytes"]
                or _hash_existing(dest) != spec["sha256"]):
            raise ValueError("previous_archive_mismatch")
        return {"archive":kind,"copied":False,"verified":True,"bytes":meta.st_size}
    if partial.exists() or partial.is_symlink():
        raise ValueError("prior_partial_requires_manual_cleanup")
    remote = str(SRC / spec["name"])
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
           "-o", "ConnectTimeout=12", "-o", "ServerAliveInterval=20",
           "-o", "ServerAliveCountMax=5", "-p", "10022",
           "wdc2@kvar.outer.sanctum", "sudo", "-n", "cat", "--", remote]
    fd = os.open(partial, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    proc = None
    size = 0
    digest = hashlib.sha256()
    try:
        with os.fdopen(fd, "wb") as out:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL)
            with proc.stdout:
                while True:
                    data = proc.stdout.read(1024 * 1024)
                    if not data:
                        break
                    size += len(data)
                    if size > spec["bytes"]:
                        raise ValueError("archive_size_exceeded")
                    digest.update(data)
                    out.write(data)
        if proc.wait() or size != spec["bytes"] or digest.hexdigest() != spec["sha256"]:
            raise ValueError("ssh_sudo_or_archive_verification_failed")
        os.rename(partial, dest)
    except BaseException:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        partial.unlink(missing_ok=True)
        raise
    return {"archive":kind,"copied":True,"verified":True,"bytes":size}

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("expected_one_archive")
        print(json.dumps(stream_one(sys.argv[1]),sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError):
        print("Pi-hole transfer refused: existing Kvar SSH access, passwordless sudo, or archive checksum unavailable",file=sys.stderr)
        sys.exit(1)
