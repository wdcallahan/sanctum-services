#!/usr/bin/env python3
"""Read-only vetting of a pinned Nextcloud third-party app tar.gz archive.

Reject unsafe paths and archive links, require the expected app identity and
version, and check declared Nextcloud major-version compatibility. This is not
a code-security audit; vet the upstream publisher separately.
"""
import pathlib
import sys
import tarfile
import xml.etree.ElementTree as ET


def validate(archive_path: str, app_id: str, version: str, server_major: int) -> None:
    prefix = app_id + "/"
    info_path = prefix + "appinfo/info.xml"
    names = set()
    metadata = None
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            raw = member.name
            path = pathlib.PurePosixPath(raw)
            parts = path.parts
            if (
                not raw or raw.startswith("/") or "\\" in raw
                or ".." in parts or "." in parts
                or not (raw == app_id or raw.startswith(prefix))
                or not (member.isfile() or member.isdir())
            ):
                raise ValueError(f"unsafe or unexpected archive member: {raw!r}")
            if raw in names:
                raise ValueError(f"duplicate archive member: {raw!r}")
            names.add(raw)
            if raw == info_path:
                if not member.isfile():
                    raise ValueError("appinfo/info.xml is not a regular file")
                if member.size > 512 * 1024:
                    raise ValueError("appinfo/info.xml exceeds 512 KiB")
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError("cannot read app metadata")
                metadata = stream.read()
    if metadata is None:
        raise ValueError("archive is missing appinfo/info.xml")
    root = ET.fromstring(metadata)
    if root.tag != "info":
        raise ValueError("unexpected info.xml root element")
    if root.findtext("id") != app_id:
        raise ValueError(f"app id mismatch (expected {app_id})")
    if root.findtext("version") != version:
        raise ValueError(f"app version mismatch (expected {version})")
    requirement = root.find("dependencies/nextcloud")
    if requirement is None:
        raise ValueError("app does not declare a Nextcloud dependency range")
    low, high = requirement.get("min-version"), requirement.get("max-version")
    if low and server_major < int(low.split(".")[0]):
        raise ValueError(f"Nextcloud {server_major} is below app minimum {low}")
    if high and server_major > int(high.split(".")[0]):
        raise ValueError(f"Nextcloud {server_major} exceeds app maximum {high}")
    if not low and not high:
        raise ValueError("no usable Nextcloud compatibility bounds")


if __name__ == "__main__":
    try:
        validate(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
    except (IndexError, ValueError, OSError, tarfile.TarError, ET.ParseError) as exc:
        print(f"APP ARCHIVE REJECTED: {exc}", file=sys.stderr)
        sys.exit(1)
    print("APP ARCHIVE ACCEPTED: identity, version, paths, and version range")
