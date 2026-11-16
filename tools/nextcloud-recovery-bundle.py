#!/usr/bin/env python3
"""Read-only integrity check for a staged, private Nextcloud recovery bundle.

A matching checksum proves only that the files match the *supplied* manifest.
It does not prove snapshot consistency, independent retention, or restorability.
Never extract archives or print application content.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tarfile

SCHEMA = "sanctum-nextcloud-recovery-bundle/v1"
ARTIFACTS = {
    "application": ("nextcloud-html.tar", {"config/config.php", "data", "custom_apps"}),
    "credentials": ("nextcloud-private.tar", {
        "postgresql-password", "postgresql-database",
        "postgresql-username", "nextcloud.env",
    }),
    "database": ("nextcloud-postgresql.dump", None),
}
MAX_MANIFEST = 16384
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
MAX_MEMBERS = 1_000_000


def private_regular(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing_or_linked_payload")
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ValueError("payload_permissions")
    return path.stat().st_size


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_tar(path, markers):
    found = set()
    count = 0
    with tarfile.open(path, mode="r:*") as archive:
        for entry in archive:
            count += 1
            if count > MAX_MEMBERS:
                raise ValueError("excessive_archive_entries")
            raw = entry.name
            if not raw or raw.startswith("/") or "\\" in raw or "\x00" in raw:
                raise ValueError("unsafe_archive_path")
            parts = [part for part in raw.split("/") if part not in ("", ".")]
            if ".." in parts:
                raise ValueError("unsafe_archive_path")
            if not (entry.isfile() or entry.isdir()):
                # No links, devices, FIFOs, or other special restore entries.
                raise ValueError("unsafe_archive_member")
            canonical = "/".join(parts)
            if canonical in markers:
                if canonical == "config/config.php" or canonical in {
                    "postgresql-password", "postgresql-database",
                    "postgresql-username", "nextcloud.env",
                }:
                    if not entry.isfile() or entry.size == 0:
                        raise ValueError("invalid_required_file")
                found.add(canonical)
            for marker in markers:
                if canonical.startswith(marker + "/"):
                    found.add(marker)
    if not markers <= found:
        raise ValueError("missing_archive_state")


def verify(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("invalid_bundle_directory")
    if stat.S_IMODE(root.stat().st_mode) & 0o077:
        raise ValueError("bundle_permissions")
    manifest_path = root / "manifest.json"
    length = private_regular(manifest_path)
    if length == 0 or length > MAX_MANIFEST:
        raise ValueError("invalid_manifest_size")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema", "source_host", "data_directory", "database", "artifacts",
    }:
        raise ValueError("invalid_manifest_fields")
    if (manifest["schema"] != SCHEMA
            or manifest["source_host"] != "kvin.outer.sanctum"
            or manifest["data_directory"] != "/var/www/html/data"
            or manifest["database"] != "nextcloud"):
        raise ValueError("unexpected_instance_identity")
    entries = manifest["artifacts"]
    if not isinstance(entries, dict) or set(entries) != set(ARTIFACTS):
        raise ValueError("invalid_artifact_set")
    for kind, (filename, markers) in ARTIFACTS.items():
        entry = entries[kind]
        if (not isinstance(entry, dict) or set(entry) != {"filename", "bytes", "sha256"}
                or entry["filename"] != filename
                or type(entry["bytes"]) is not int or entry["bytes"] <= 0
                or not isinstance(entry["sha256"], str)
                or not SHA256.fullmatch(entry["sha256"])):
            raise ValueError("invalid_artifact_metadata")
        file = root / filename
        actual_bytes = private_regular(file)
        if actual_bytes != entry["bytes"] or checksum(file) != entry["sha256"]:
            raise ValueError("payload_checksum_mismatch")
        if kind == "database":
            with file.open("rb") as source:
                if source.read(5) != b"PGDMP":
                    raise ValueError("unrecognized_pg_dump_header")
        else:
            verify_tar(file, markers)
    return {
        "schema": SCHEMA,
        "source_host": "kvin.outer.sanctum",
        "archive_and_dump_hashes_match_manifest": True,
        "nextcloud_required_paths_present_in_archive": True,
        "postgresql_custom_dump_header_recognized": True,
        "application_or_secret_bytes_returned": False,
        "consistent_snapshot_proven": False,
        "independent_off_host_retention_proven": False,
        "database_restore_tested": False,
        "application_restore_accepted": False,
    }


def main():
    if len(sys.argv) != 2:
        raise ValueError("one_private_bundle_directory_required")
    print(json.dumps(verify(sys.argv[1]), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError,
            tarfile.TarError, OverflowError, EOFError):
        print("Nextcloud recovery bundle validation refused (private details withheld)",
              file=sys.stderr)
        sys.exit(1)
