#!/usr/bin/env python3
"""Inspect a quiesced Kuma volume archive or imported isolated volume.

Read-only; never extracts arbitrary tar members, edits SQLite, or prints
credential material. The stopped-service archive can carry SQLite WAL files.
"""
import json
import os
from pathlib import Path
import sqlite3
import sys
import tarfile
import tempfile


def check_db(path):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=8)
    try:
        if conn.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise ValueError("sqlite_integrity_failed")
        users = conn.execute(
            "SELECT COUNT(*) FROM user WHERE username = ?",
            ("sanctum-admin",)
        ).fetchone()[0]
        row = conn.execute(
            "SELECT id, type, method, url, interval, active, "
            "accepted_statuscodes_json FROM monitor WHERE name = ?",
            ("Wicket Ollama",)
        ).fetchall()
        expected_url = "http://wicket.arcane.sanctum:11435/healthz"
        valid_monitor = (len(row) == 1
                         and row[0][:6] ==
                         (1, "http", "GET", expected_url, 60, 1)
                         and json.loads(row[0][6]) == ["200-299"])
        alerts = conn.execute(
            "SELECT COUNT(*) FROM monitor_notification WHERE monitor_id = ?",
            (1,)
        ).fetchone()[0]
        if users != 1 or not valid_monitor or alerts:
            raise ValueError("restored_kuma_contract_mismatch")
        return {
            "sqlite_integrity": "ok",
            "administrator_record_present": True,
            "wicket_monitor_persisted": True,
            "notification_subscriptions_absent": True,
        }
    finally:
        conn.close()


def check_archive(archive):
    with tempfile.TemporaryDirectory(prefix="sanctum-kuma-archive-") as tmp:
        with tarfile.open(archive, mode="r:*") as tf:
            matched = {}
            for member in tf:
                raw = member.name
                parts = raw.split("/")
                if raw.startswith("/") or ".." in parts:
                    raise ValueError("unsafe_archive_member")
                path = raw.lstrip("./")
                if path in ("kuma.db", "kuma.db-wal", "kuma.db-shm"):
                    if not member.isfile() or path in matched:
                        raise ValueError("invalid_database_archive_member")
                    matched[path] = member
            if "kuma.db" not in matched:
                raise ValueError("archive_missing_database")
            for name, member in matched.items():
                source = tf.extractfile(member)
                if source is None:
                    raise ValueError("archive_member_unreadable")
                with source, open(Path(tmp) / name, "xb") as target:
                    while True:
                        data = source.read(1024 * 1024)
                        if not data:
                            break
                        target.write(data)
        return check_db(Path(tmp) / "kuma.db")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("archive", "restored"):
        raise ValueError("invalid_inspection_mode")
    input_path = Path(sys.argv[2])
    if sys.argv[1] == "archive":
        if not input_path.is_file() or input_path.is_symlink():
            raise ValueError("archive_missing_or_symlinked")
        result = check_archive(input_path)
    else:
        if not input_path.is_dir() or input_path.is_symlink():
            raise ValueError("restored_volume_missing")
        result = check_db(input_path / "kuma.db")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, sqlite3.Error, tarfile.TarError, json.JSONDecodeError):
        print("Kuma snapshot validation failed (private details withheld)", file=sys.stderr)
        sys.exit(1)
