#!/usr/bin/env python3
"""Classify unusual Nextcloud HTML-tree entries without disclosing any path.

Read-only: metadata, symlink destination classification and existence only.
No file contents, host changes, database calls, application control or backups.
Run with the same rootless user namespace as the proposed archive producer.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import stat
import sys

KINDS = ("symbolic_link", "fifo", "socket", "character_device", "block_device", "unknown")
AREAS = ("root", "config", "data", "custom_apps", "other")
LINKS = ("absolute", "relative", "inside_root", "outside_root", "unresolved", "dangling")
MAX_ENTRIES = 1_000_000


def kind(mode):
    if stat.S_ISLNK(mode):
        return "symbolic_link"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISCHR(mode):
        return "character_device"
    if stat.S_ISBLK(mode):
        return "block_device"
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    return "unknown"


def area(root, item):
    parts = item.relative_to(root).parts
    if len(parts) == 1:
        return "root"
    return parts[0] if parts[0] in ("config", "data", "custom_apps") else "other"


def record_link(root, link, counts):
    target = os.readlink(link)
    counts["absolute" if os.path.isabs(target) else "relative"] += 1

    # Resolve only filesystem metadata. Never print link or target paths.
    # A missing target is a recovery-design question, not a permission fix.
    try:
        resolved = link.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError):
        counts["dangling"] += 1
    except (RuntimeError, OSError):
        counts["unresolved"] += 1
    else:
        if resolved.is_relative_to(root.resolve(strict=True)):
            counts["inside_root"] += 1
        else:
            counts["outside_root"] += 1


def classify(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("invalid_source_root")

    special = Counter()
    by_area = {name: Counter() for name in AREAS}
    links = Counter()
    totals = Counter()
    entries = 0

    def on_walk_error(error):
        raise error

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=on_walk_error):
        dirs.sort()
        files.sort()
        for name in dirs + files:
            entries += 1
            if entries > MAX_ENTRIES:
                raise ValueError("too_many_entries")
            item = Path(directory) / name
            observed = kind(item.lstat().st_mode)
            totals[observed] += 1
            if observed not in ("regular", "directory"):
                special[observed] += 1
                by_area[area(root, item)][observed] += 1
                if observed == "symbolic_link":
                    record_link(root, item, links)

    return {
        "status": "classified",
        "scope": "nextcloud_html_tree_entry_types_only",
        "total_entries_observed": entries,
        "ordinary_file_count": totals["regular"],
        "ordinary_directory_count": totals["directory"],
        "special_entry_count": sum(special.values()),
        "special_entry_types": {key: special[key] for key in KINDS},
        "special_entry_areas": {
            name: {key: by_area[name][key] for key in KINDS} for name in AREAS
        },
        "symbolic_link_classification": {key: links[key] for key in LINKS},
        "paths_targets_contents_or_secrets_returned": False,
        "application_or_database_changed": False,
        "backup_created": False,
        "backup_accepted": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Classify only Nextcloud HTML source entry types")
    parser.add_argument("--html-root", required=True)
    args = parser.parse_args()
    print(json.dumps(classify(args.html_root), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError):
        print(json.dumps({
            "status": "refused",
            "reason": "read_only_special_entry_scan_failed",
            "paths_targets_contents_or_secrets_returned": False,
            "application_or_database_changed": False,
            "backup_created": False,
        }, sort_keys=True), file=sys.stderr)
        sys.exit(1)
