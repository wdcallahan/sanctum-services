#!/usr/bin/env python3
"""Assemble private Nextcloud recovery artifacts from a *previously quiesced* input set.

This creates bytes, not a consistent database/application snapshot. The caller
must establish maintenance-mode, database dump timing, and off-host retention.
Do not run on production until the owner orchestration is qualified.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import posixpath
from pathlib import Path
import shutil
import stat
import sys
import tarfile

REQUIRED_PRIVATE = (
    "postgresql-password",
    "postgresql-database",
    "postgresql-username",
    "nextcloud.env",
)
REQUIRED_HTML = ("config/config.php", "data", "custom_apps")
NAMES = {
    "application": "nextcloud-html.tar",
    "credentials": "nextcloud-private.tar",
    "database": "nextcloud-postgresql.dump",
}


def require_regular(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("nonregular_or_linked_source")
    if path.stat().st_size == 0:
        raise ValueError("empty_required_file")


def require_directory(path):
    if path.is_symlink() or not path.is_dir():
        raise ValueError("non_directory_or_linked_source")


def new_private_file(path):
    return os.fdopen(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb")


def raise_walk_error(error):
    # os.walk otherwise silently skips unreadable directories: that could
    # publish an incomplete backup as if all application data were included.
    raise error


def validate_internal_link(root, link):
    """Require one relative, non-dangling link entirely contained in HTML root.

    Preserve link identity instead of dereferencing it. The archive validator
    independently checks all link targets *inside the archive*, rather than
    trusting the producer's inspection of the live source filesystem.
    """
    target = os.readlink(link)
    if not target or os.path.isabs(target) or chr(0) in target or chr(92) in target:
        raise ValueError("unsafe_source_link")
    relative_name = link.relative_to(root).as_posix()
    effective = posixpath.normpath(posixpath.join(
        posixpath.dirname(relative_name), target))
    if effective == ".." or effective.startswith("../"):
        raise ValueError("unsafe_source_link")
    try:
        resolved = link.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ValueError("unsafe_source_link") from None
    if not resolved.is_relative_to(root.resolve(strict=True)):
        raise ValueError("unsafe_source_link")
    return target


def sorted_tree(root):
    # Symlinks are preserved only when relative and resolved entirely inside
    # this source. os.walk must not descend through a linked directory.
    # Devices, sockets, FIFOs, dangling/external links are never archived.
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=raise_walk_error):
        dirs.sort()
        files.sort()
        for name in dirs + files:
            candidate = Path(directory) / name
            mode = candidate.lstat().st_mode
            if stat.S_ISLNK(mode):
                validate_internal_link(root, candidate)
            elif not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError("unsafe_source_member")
            yield candidate


def archive_tree(root, destination):
    with new_private_file(destination) as stream:
        with tarfile.open(fileobj=stream, mode="w:") as archive:
            for item in sorted_tree(root):
                archive.add(item, arcname=item.relative_to(root).as_posix(), recursive=False)


def archive_private(root, destination):
    with new_private_file(destination) as stream:
        with tarfile.open(fileobj=stream, mode="w:") as archive:
            for name in REQUIRED_PRIVATE:
                archive.add(root / name, arcname=name, recursive=False)


def copy_dump(source, destination):
    with source.open("rb") as input_file:
        if input_file.read(5) != b"PGDMP":
            raise ValueError("database_dump_not_custom_format")
        input_file.seek(0)
        with new_private_file(destination) as output:
            shutil.copyfileobj(input_file, output, length=1024 * 1024)


def fingerprint(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return {"filename": path.name, "bytes": path.stat().st_size, "sha256": h.hexdigest()}


def assemble(html_root, private_root, database_dump, output):
    html_root = Path(html_root)
    private_root = Path(private_root)
    database_dump = Path(database_dump)
    output = Path(output)

    require_directory(html_root)
    require_directory(private_root)
    require_regular(database_dump)
    for marker in REQUIRED_HTML:
        candidate = html_root / marker
        if marker == "config/config.php":
            require_regular(candidate)
        else:
            require_directory(candidate)
    for name in REQUIRED_PRIVATE:
        require_regular(private_root / name)

    # Do not recursively archive our own destination or place private payloads
    # in either source tree. A fresh output path is mandatory; no overwrites.
    output_abs = output.resolve()
    for source_root in (html_root, private_root):
        if output_abs.is_relative_to(source_root.resolve()):
            raise ValueError("output_inside_source")
    if output.exists() or output.is_symlink():
        raise ValueError("output_already_exists")
    output.mkdir(mode=0o700)  # a fresh directory, no implicit parent creation

    archive_tree(html_root, output / NAMES["application"])
    archive_private(private_root, output / NAMES["credentials"])
    copy_dump(database_dump, output / NAMES["database"])
    manifest = {
        "schema": "sanctum-nextcloud-recovery-bundle/v1",
        "source_host": "kvin.outer.sanctum",
        "data_directory": "/var/www/html/data",
        "database": "nextcloud",
        "artifacts": {kind: fingerprint(output / filename) for kind, filename in NAMES.items()},
    }
    with new_private_file(output / "manifest.json") as target:
        target.write((json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8"))

    verifier_path = Path(__file__).with_name("nextcloud-recovery-bundle.py")
    spec = importlib.util.spec_from_file_location("nextcloud_bundle_verifier", verifier_path)
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    return verifier.verify(output)


def main():
    parser = argparse.ArgumentParser(description="Assemble a private, offline Nextcloud bundle")
    parser.add_argument("--html-root", required=True)
    parser.add_argument("--private-root", required=True)
    parser.add_argument("--database-dump", required=True)
    parser.add_argument("--output", required=True, help="fresh private directory, no overwriting")
    options = parser.parse_args()
    # Inherit no accidentally permissive creation defaults.
    os.umask(0o077)
    print(json.dumps(assemble(options.html_root, options.private_root,
                              options.database_dump, options.output), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, tarfile.TarError, ImportError, AttributeError):
        print("Nextcloud private bundle assembly refused; incomplete output, if any, is not a backup",
              file=sys.stderr)
        sys.exit(1)
