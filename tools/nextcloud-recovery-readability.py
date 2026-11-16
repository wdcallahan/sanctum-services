#!/usr/bin/env python3
"""Non-mutating, content-redacted readability check for the exact backup inputs.

Run as the same rootless user namespace that will assemble the bundle. No
file bytes or paths are reported. A passing scan is NOT a consistent snapshot.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ASSEMBLER = Path(__file__).with_name("nextcloud-recovery-assemble.py")
spec = importlib.util.spec_from_file_location("nextcloud_recovery_assemble", ASSEMBLER)
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


def check(html, private):
    html = Path(html)
    private = Path(private)
    producer.require_directory(html)
    producer.require_directory(private)
    for name in producer.REQUIRED_HTML:
        required = html / name
        if name == "config/config.php":
            producer.require_regular(required)
        else:
            producer.require_directory(required)

    counts = {"html_regular_files": 0, "html_directories": 0, "html_file_bytes": 0}
    for item in producer.sorted_tree(html):
        if item.is_file():
            # Metadata access alone can succeed when opening a file would fail.
            # Read one byte, not the user's data, and never echo file contents.
            with item.open("rb") as stream:
                stream.read(1)
                counts["html_file_bytes"] += item.stat().st_size
            counts["html_regular_files"] += 1
        elif item.is_dir():
            counts["html_directories"] += 1
        else:
            raise ValueError("unsupported_html_source_member")
    for name in producer.REQUIRED_PRIVATE:
        item = private / name
        producer.require_regular(item)
        with item.open("rb") as stream:
            stream.read(1)
    return {
        "scope": "nextcloud_existing_html_and_four_private_inputs",
        **counts,
        "private_required_files_readable": len(producer.REQUIRED_PRIVATE),
        "symlinks_special_members_observed": 0,
        "source_tree_readable_for_assembler_at_scan_time": True,
        "contents_or_secret_paths_returned": False,
        "application_interrupted": False,
        "database_exported": False,
        "recovery_bundle_created": False,
        "consistent_snapshot_proven": False,
        "off_host_backup_proven": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Read-only Nextcloud bundle input traversal")
    parser.add_argument("--html-root", required=True)
    parser.add_argument("--private-root", required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.html_root, args.private_root), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, ImportError):
        print("Nextcloud bundle source traversal refused (private details withheld)",
              file=sys.stderr)
        sys.exit(1)
