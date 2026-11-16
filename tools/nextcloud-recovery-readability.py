#!/usr/bin/env python3
"""Non-mutating, content-redacted readability check for the exact backup inputs.

Run as the same rootless user namespace that will assemble the bundle. No
file bytes or paths are reported. A passing scan is NOT a consistent snapshot.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import stat
import sys

# Only fixed categories may cross the diagnostic boundary. Real OSError
# messages often contain private filenames, so never show their raw text.
SAFE_SOURCE_REASONS = {
    "unsafe_source_member",
    "unsafe_source_link",
    "non_directory_or_linked_source",
    "nonregular_or_linked_source",
    "empty_required_file",
    "unsupported_html_source_member",
}


class SourceAccessRefused(ValueError):
    def __init__(self, stage, reason):
        self.stage = stage
        self.reason = reason
        super().__init__(reason)


def safe_reason(error):
    if isinstance(error, PermissionError):
        return "permission_denied"
    if isinstance(error, FileNotFoundError):
        return "missing_source"
    if isinstance(error, IsADirectoryError):
        return "expected_regular_file"
    if isinstance(error, NotADirectoryError):
        return "expected_directory"
    if isinstance(error, ValueError):
        value = str(error)
        return value if value in SAFE_SOURCE_REASONS else "invalid_source"
    return "filesystem_error"


def at_stage(stage, operation):
    try:
        return operation()
    except (OSError, ValueError) as error:
        raise SourceAccessRefused(stage, safe_reason(error)) from None


ASSEMBLER = Path(__file__).with_name("nextcloud-recovery-assemble.py")
spec = importlib.util.spec_from_file_location("nextcloud_recovery_assemble", ASSEMBLER)
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


def check(html, private):
    html = Path(html)
    private = Path(private)
    def check_required():
        producer.require_directory(html)
        producer.require_directory(private)
        for name in producer.REQUIRED_HTML:
            required = html / name
            if name == "config/config.php":
                producer.require_regular(required)
            else:
                producer.require_directory(required)

    at_stage("required_inputs", check_required)

    counts = {
        "html_regular_files": 0,
        "html_directories": 0,
        "html_relative_internal_symlinks": 0,
        "html_file_bytes": 0,
    }

    def inspect_html_tree():
        for item in producer.sorted_tree(html):
            mode = item.lstat().st_mode
            if stat.S_ISLNK(mode):
                # Producer has already refused escaping/dangling/cyclic links.
                # Do not follow link targets during this readability probe.
                counts["html_relative_internal_symlinks"] += 1
            elif stat.S_ISREG(mode):
                # A stat alone can succeed when an actual open would fail.
                # Read one byte but never echo any content or source paths.
                with item.open("rb") as stream:
                    stream.read(1)
                    counts["html_file_bytes"] += item.stat().st_size
                counts["html_regular_files"] += 1
            elif stat.S_ISDIR(mode):
                counts["html_directories"] += 1
            else:
                raise ValueError("unsupported_html_source_member")

    at_stage("html_tree", inspect_html_tree)

    def inspect_private():
        for name in producer.REQUIRED_PRIVATE:
            item = private / name
            producer.require_regular(item)
            with item.open("rb") as stream:
                stream.read(1)

    at_stage("private_inputs", inspect_private)
    return {
        "scope": "nextcloud_existing_html_and_four_private_inputs",
        **counts,
        "private_required_files_readable": len(producer.REQUIRED_PRIVATE),
        "unaccepted_special_members_observed": 0,
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
    except SourceAccessRefused as error:
        # The stage/reason are fixed safe labels, never user-controlled paths.
        print(json.dumps({
            "status": "refused",
            "stage": error.stage,
            "reason": error.reason,
            "file_paths_or_contents_returned": False,
            "application_interrupted": False,
            "backup_created": False,
        }, sort_keys=True), file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, ImportError):
        print(json.dumps({
            "status": "refused",
            "stage": "startup",
            "reason": "unexpected_local_error",
            "file_paths_or_contents_returned": False,
            "application_interrupted": False,
            "backup_created": False,
        }, sort_keys=True), file=sys.stderr)
        sys.exit(1)
