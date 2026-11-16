#!/usr/bin/env python3
"""Read-only integrity check for a staged, private Nextcloud recovery bundle.

A matching checksum proves only that the files match the *supplied* manifest.
It does not prove snapshot consistency, independent retention, or restorability.
Never extract archives or print application content.
"""
import hashlib
import json
import os
import posixpath
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


def archive_relative_target(link_path, target):
    """Interpret one archive symlink without following host filesystem paths."""
    if (not target or target.startswith("/") or chr(0) in target
            or chr(92) in target or len(target) > 4096):
        raise ValueError("unsafe_archive_member")
    candidate = posixpath.normpath(posixpath.join(
        posixpath.dirname(link_path), target))
    if candidate == ".." or candidate.startswith("../"):
        raise ValueError("unsafe_archive_member")
    return candidate


def verify_internal_links(entries, links):
    """Require contained, present, non-cyclic targets entirely inside this tar.

    Expansion is archive-metadata-only and never extracts or touches live
    target paths. Reject archives that try to put any member beneath a
    symlink, regardless of tar entry order. Only relative symbolic links
    in the *application* archive are permitted.
    """
    names = set(entries)
    for name in names:
        parts = name.split("/")
        for i in range(1, len(parts)):
            if "/".join(parts[:i]) in links:
                raise ValueError("archive_path_descends_through_link")

    for name, link_target in links.items():
        target = archive_relative_target(name, link_target)
        for _ in range(41):
            # A directory link to the root of the archive is valid.
            if target == ".":
                break
            parts = target.split("/")
            redirected = False
            for i in range(1, len(parts) + 1):
                prefix = "/".join(parts[:i])
                if prefix in links:
                    remaining = "/".join(parts[i:])
                    resolved_prefix = archive_relative_target(prefix, links[prefix])
                    target = posixpath.normpath(posixpath.join(
                        resolved_prefix, remaining)) if remaining else resolved_prefix
                    if target == ".." or target.startswith("../"):
                        raise ValueError("unsafe_archive_member")
                    redirected = True
                    break
                if i < len(parts) and prefix in entries and entries[prefix] == "file":
                    raise ValueError("archive_link_target_not_directory")
            if redirected:
                continue
            # Explicit member, or an implicit directory formed by an
            # archive member's path. No dangling link targets are accepted.
            if target not in names and not any(
                    member.startswith(target + "/") for member in names):
                raise ValueError("missing_internal_link_target")
            break
        else:
            raise ValueError("cyclic_or_excessive_archive_links")


def verify_tar(path, markers, allow_internal_links=False):
    found = set()
    entries = {}
    links = {}
    count = 0
    with tarfile.open(path, mode="r:*") as archive:
        for entry in archive:
            count += 1
            if count > MAX_MEMBERS:
                raise ValueError("excessive_archive_entries")
            raw = entry.name
            if not raw or raw.startswith("/") or chr(92) in raw or chr(0) in raw:
                raise ValueError("unsafe_archive_path")
            parts = [part for part in raw.split("/") if part not in ("", ".")]
            if not parts or ".." in parts:
                raise ValueError("unsafe_archive_path")
            canonical = "/".join(parts)
            if canonical in entries:
                raise ValueError("duplicate_archive_member")
            if entry.isfile():
                entries[canonical] = "file"
            elif entry.isdir():
                entries[canonical] = "directory"
            elif allow_internal_links and entry.issym():
                entries[canonical] = "symlink"
                links[canonical] = entry.linkname
            else:
                # Never admit hardlinks, sockets, devices or FIFOs.
                # Private credential/config archive rejects ALL links.
                raise ValueError("unsafe_archive_member")
            if canonical in markers:
                if canonical == "config/config.php" or canonical in {
                    "postgresql-password", "postgresql-database",
                    "postgresql-username", "nextcloud.env",
                }:
                    if not entry.isfile() or entry.size == 0:
                        raise ValueError("invalid_required_file")
                else:
                    if not entry.isdir():
                        raise ValueError("invalid_required_directory")
                found.add(canonical)
            for marker in markers:
                if canonical.startswith(marker + "/"):
                    found.add(marker)
    if not markers <= found:
        raise ValueError("missing_archive_state")
    if links:
        verify_internal_links(entries, links)
    return len(links)


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
    verified_internal_links = 0
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
            verified_internal_links += verify_tar(
                file, markers, allow_internal_links=(kind == "application"))
    return {
        "schema": SCHEMA,
        "source_host": "kvin.outer.sanctum",
        "archive_and_dump_hashes_match_manifest": True,
        "nextcloud_required_paths_present_in_archive": True,
        "internal_relative_symlinks_verified": verified_internal_links,
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
