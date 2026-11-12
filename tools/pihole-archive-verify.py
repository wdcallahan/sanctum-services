#!/usr/bin/env python3
"""Private, bounded Pi-hole volume export verification; no application mutation.

Checks two separate tar files from a stopped original Pi-hole service.
No arbitrary tar extraction. Known SQLite databases are copied exclusively
to an owner-private temporary directory for SQLite integrity_check and then
removed. Only fixed metadata, file counts, SHA-256 and booleans are returned.
"""
import hashlib
import json
import os
from pathlib import Path
import posixpath
import sqlite3
import stat
import sys
import tarfile
import tempfile

MAX_ARCHIVE_BYTES = 12 * 1024**3
MAX_REGULAR_BYTES = 10 * 1024**3
MAX_ENTRIES = 100000
MARKERS = {"pihole.toml", "gravity.db", "pihole-FTL.db"}
SQLITE_NAMES = {"gravity.db", "pihole-FTL.db"}
SQLITE_JOURNALS = {p + extra for p in SQLITE_NAMES
                   for extra in ("-wal", "-shm", "-journal")}
SUPPORTED = {"etc-pihole", "etc-dnsmasq"}


def safe_name(name):
    if (not isinstance(name, str) or not name or len(name) > 512
            or "\x00" in name or "\\" in name or name.startswith("/")):
        raise ValueError("unsafe_tar_path")
    if any(seg == ".." for seg in name.split("/")):
        raise ValueError("unsafe_tar_path")
    result = posixpath.normpath(name)
    if result == "." and name in (".", "./"):
        return None
    if result in (".", "..") or result.startswith("../"):
        raise ValueError("unsafe_tar_path")
    return result


def hash_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def check_sqlite(db):
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=8)
    try:
        results = conn.execute("PRAGMA integrity_check").fetchall()
        if results != [("ok",)]:
            raise ValueError("private_database_integrity_check_failed")
    finally:
        conn.close()


def inspect(kind, filename):
    if kind not in SUPPORTED:
        raise ValueError("unsupported_volume_identity")
    path = Path(filename)
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size == 0 or info.st_size > MAX_ARCHIVE_BYTES
            or info.st_uid != os.geteuid()):
        raise ValueError("unsafe_or_unavailable_private_archive")
    total = 0
    regular = 0
    directory_count = 0
    seen = set()
    markers = set()
    with tempfile.TemporaryDirectory(prefix="sanctum-pihole-check-") as tmp:
        root = Path(tmp)
        with tarfile.open(path, "r:") as tar:
            for index, member in enumerate(tar):
                if index >= MAX_ENTRIES:
                    raise ValueError("archive_entry_limit_exceeded")
                name = safe_name(member.name)
                if name is None:
                    if not member.isdir():
                        raise ValueError("archive_root_not_directory")
                    continue
                if name in seen:
                    raise ValueError("duplicate_archive_path")
                seen.add(name)
                if member.isdir():
                    directory_count += 1
                    continue
                if not member.isfile() or member.size < 0:
                    raise ValueError("unsupported_tar_member_type")
                regular += 1
                total += member.size
                if total > MAX_REGULAR_BYTES:
                    raise ValueError("archive_file_bytes_limit")
                if kind == "etc-pihole" and name in MARKERS:
                    markers.add(name)
                if kind == "etc-pihole" and name in SQLITE_NAMES | SQLITE_JOURNALS:
                    reader = tar.extractfile(member)
                    if reader is None:
                        raise ValueError("database_unreadable")
                    target = root / name
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with reader, os.fdopen(fd, "wb") as output:
                        while True:
                            piece = reader.read(1024 * 1024)
                            if not piece:
                                break
                            output.write(piece)
        if kind == "etc-pihole":
            if markers != MARKERS:
                raise ValueError("missing_required_pihole_state")
            for db in sorted(SQLITE_NAMES):
                if (root / db).stat().st_size < 100:
                    raise ValueError("invalid_sqlite_size")
                check_sqlite(root / db)
        else:
            # Previously inventoried empty volume. Preserve exactly, even if
            # it has directory-only tar metadata, but refuse unexpected data.
            if regular != 0:
                raise ValueError("dnsmasq_volume_no_longer_empty")
    return {
        "schema": "sanctum-pihole-volume-archive/v1",
        "volume_role": kind,
        "archive_verified": True,
        "archive_size_bytes": info.st_size,
        "archive_sha256": hash_file(path),
        "regular_file_count": regular,
        "regular_file_bytes": total,
        "directory_count": directory_count,
        "required_state_present": kind == "etc-pihole",
        "sqlite_integrity": "ok" if kind == "etc-pihole" else "not_applicable",
        "archive_contents_returned": False,
        "restored_application_accepted": False,
        "off_host_copy_accepted": False,
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in SUPPORTED:
        raise ValueError("unsupported_operation")
    print(json.dumps(inspect(sys.argv[1], sys.argv[2]), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, sqlite3.Error, tarfile.TarError,
            OverflowError, EOFError):
        print("Pi-hole archive validation refused; private details withheld",
              file=sys.stderr)
        raise SystemExit(1)
