#!/usr/bin/env python3
"""Verify a stopped LinkStack volume archive without exposing its contents.

Use only on private archives generated from the exact rootless linkstack
volume. Never extract arbitrary paths or print secrets or SQLite rows.
"""
import hashlib
import json
import os
from pathlib import Path
import posixpath
import sqlite3
import sys
import tarfile
import tempfile

LIMIT_ENTRIES = 50000
LIMIT_BYTES = 2 * 1024**3
DB_FILES = {"database/database.sqlite",
            "database/database.sqlite-wal",
            "database/database.sqlite-shm"}
REQUIRED = {"database/database.sqlite", ".env"}


def safe_name(name):
    if not isinstance(name, str) or not name or "\x00" in name:
        raise ValueError("unsafe_name")
    if name.startswith("/") or "\\" in name or len(name) > 512:
        raise ValueError("unsafe_name")
    parts = name.split("/")
    if any(p == ".." for p in parts):
        raise ValueError("unsafe_name")
    canonical = posixpath.normpath(name)
    if canonical in (".", "..") or canonical.startswith("../"):
        if canonical == "." and name in (".", "./"):
            return None  # Podman tar root directory only
        raise ValueError("unsafe_name")
    return canonical


def inspect(archive):
    file_path = Path(archive)
    if file_path.is_symlink() or not file_path.is_file():
        raise ValueError("unavailable_archive")
    if file_path.stat().st_size > LIMIT_BYTES + 512 * LIMIT_ENTRIES:
        raise ValueError("oversize_archive")

    total, count, files = 0, 0, 0
    seen = set()
    markers = set()
    with tempfile.TemporaryDirectory(prefix="sanctum-linkstack-verify-") as tmp:
        base = Path(tmp)
        (base / "database").mkdir(mode=0o700)
        with tarfile.open(file_path, mode="r:") as tar:
            for member in tar:
                count += 1
                if count > LIMIT_ENTRIES:
                    raise ValueError("excessive_entries")
                name = safe_name(member.name)
                if name is None:
                    if not member.isdir():
                        raise ValueError("root_not_directory")
                    continue
                if name in seen:
                    raise ValueError("duplicate_member")
                seen.add(name)
                if not (member.isfile() or member.isdir()):
                    raise ValueError("unsafe_member_type")
                if member.isdir():
                    continue
                if member.size < 0:
                    raise ValueError("invalid_size")
                files += 1
                total += member.size
                if total > LIMIT_BYTES:
                    raise ValueError("oversize_payload")
                if name in REQUIRED:
                    markers.add(name)
                if name in DB_FILES:
                    reader = tar.extractfile(member)
                    if reader is None:
                        raise ValueError("unreadable_database")
                    # Private temp directory is never exposed; fixed safe names.
                    target = base / name
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with reader, os.fdopen(fd, "wb") as output:
                        while True:
                            chunk = reader.read(1024 * 1024)
                            if not chunk:
                                break
                            output.write(chunk)
        if not REQUIRED.issubset(markers):
            raise ValueError("missing_required_state")
        db_path = base / "database" / "database.sqlite"
        # Empty SQLite files and malformed archives must fail, not count as backup.
        if db_path.stat().st_size < 100:
            raise ValueError("invalid_database")
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=8)
        try:
            integrity = conn.execute("PRAGMA integrity_check").fetchall()
            if len(integrity) != 1 or integrity[0] != ("ok",):
                raise ValueError("database_integrity_failed")
        finally:
            conn.close()
    h = hashlib.sha256()
    with file_path.open("rb") as stream:
        while True:
            piece = stream.read(1024 * 1024)
            if not piece:
                break
            h.update(piece)
    return {
        "schema": "sanctum-linkstack-archive/v1",
        "archive_verified": True,
        "sqlite_integrity": "ok",
        "configuration_file_present": True,
        "regular_file_count": files,
        "regular_file_bytes": total,
        "archive_bytes": file_path.stat().st_size,
        "archive_sha256": h.hexdigest(),
        "application_contents_returned": False,
        "recovery_proven": False,
        "off_host_copy_verified": False,
    }


def inspect_restored_volume(root):
    """Check isolated imported state only, never touch or print private data."""
    parent = Path(root)
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("missing_restored_volume")
    env = parent / ".env"
    db = parent / "database" / "database.sqlite"
    for path in (env, db):
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing_restored_marker")
    if db.stat().st_size < 100 or env.stat().st_size == 0:
        raise ValueError("invalid_restored_marker")
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=8)
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchall()
        if integrity != [("ok",)]:
            raise ValueError("restored_database_integrity_failed")
    finally:
        conn.close()
    return {
        "schema": "sanctum-linkstack-volume-restore/v1",
        "isolated_imported_volume_integrity_verified": True,
        "sqlite_integrity": "ok",
        "configuration_file_present": True,
        "application_contents_returned": False,
        "restored_application_boot_verified": False,
        "browser_content_and_admin_accepted": False,
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("archive", "restored"):
        raise ValueError("unsupported_operation")
    result = (inspect(sys.argv[2]) if sys.argv[1] == "archive"
              else inspect_restored_volume(sys.argv[2]))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, sqlite3.Error, tarfile.TarError,
            OverflowError, EOFError):
        print("LinkStack archive validation refused (private details withheld)",
              file=sys.stderr)
        sys.exit(1)
