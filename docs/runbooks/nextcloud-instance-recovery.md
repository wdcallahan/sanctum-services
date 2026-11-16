# Town Square / Nextcloud — complete-instance recovery boundary

**Status:** The existing Kvin Nextcloud installation and Calendar 6.6.2
bidirectional use are accepted. The installation/app-manifest roles are
source-managed, but **full-instance backup, independent storage, and an
isolated recovery have not been accepted**. This document authorizes no
application downtime or database change.

## Recovery contents and ownership

- Include the **actual** Nextcloud data directory, configuration,
  installed/custom app files, and user content. The source role mounts
  `~/srv/sanctum-services/nextcloud/html` at `/var/www/html` and a native `occ` query on November 16 **confirmed**
  `/var/www/html/data` as the configured data directory.
- Include a consistent application-specific PostgreSQL database snapshot.
  Sanctum Maintenance owns the shared PostgreSQL service, connection and
  host lifecycle; Services owns Nextcloud application recovery. Never
  restore the whole shared database cluster to recover one application.
- Recover secret files privately via the established Vault and custody
  mechanisms. No passwords, config.php contents or bearer credentials
  belong in Git or operator transcripts. The administrator password
  is not supplied by the Services Ansible role.
- Preserve the pinned application image and Calendar 6.6.2 declaration,
  along with the Quadlet, YXORP/DNS dependencies and restore order.
  Reinstalling an app does not restore calendar entries or user accounts.

## First observation — read-only, no changes

`ansible/nextcloud-recovery-inputs.yml` runs **only against current Kvin**.
It checks the presence (not content) of required files and directories,
the user service state, and local `/status.php`. It does not dump a
database, export files, modify a service, read passwords or establish that
a backup exists. The input observer only checked presence, but the separate accepted
native `occ` query has since confirmed `/var/www/html/data`.

After source CI and Ansible syntax qualification, run from the existing
Services checkout on Kvin:

```console
~/.local/bin/ansible-navigator run ansible/nextcloud-recovery-inputs.yml
```

Return only `Report only bounded recovery-input availability` and the
play recap. No passwords or raw application configuration.

## Next implementation after native observation

1. Use the **confirmed** `/var/www/html/data` path and select an appropriate
   **off-Kvin** protected backup destination with capacity, integrity
   verification and retention; another path on Kvin alone is not disaster recovery.
2. Create a bounded maintenance-mode operation that prevents application
   writes, takes a coordinated Nextcloud-only PostgreSQL snapshot and
   archives the required files/private configuration as **one named recovery
   point**. Restore the existing application's prior service state on failure.
3. Restore to an **isolated** service and separate database without changing
   Kvin's live Nextcloud, shared PostgreSQL state, production DNS or YXORP.
   Apply the existing protected credentials via their supported owner.
4. Verify representative user files, settings, login, a known Calendar
   entry, and repeat-converged source reconciliation. Document update,
   rollback and deliberate removal with data-retention choice.
5. Only then consider production replacement via a separately approved
   operator decision.

Kvar is already **powered off**; there is no reason to turn it on for this
work. Project Joule owns Prism and Bunny Factory owns the VyOS routers.

## November 16 — effective data path and recovery-bundle integrity

Nova's **native read-only** command on running Kvin returned exactly
`/var/www/html/data` from `podman exec -u www-data sanctum-nextcloud php
occ config:system:get datadirectory`. This is a confirmed configured path,
not an inference from directory presence. The existing Quadlet's bind
`~/srv/sanctum-services/nextcloud/html:/var/www/html` includes that data
directory, `config/config.php`, and `custom_apps`.

**Do not repeat** the accepted six-task native input play or this OCC query.

The source-only `tools/nextcloud-recovery-bundle.py` verifies one
privately staged recovery bundle, with three exact artifacts: a full HTML-tree
tar archive, a private configuration/credential tar archive, and a
**Nextcloud-database-only** PostgreSQL custom-format dump. Its
`manifest.json` must name the exact host, data directory, and database;
each artifact needs a byte count and SHA-256. The verifier rejects unexpected
filenames, symlinks, group/world readable payloads, malformed paths,
special archive members, missing required state, and a missing PGDMP
header. It never extracts the archives or prints contents or credentials.

Example **manifest structure** (fake digests; not a usable backup):
```json
{
  "schema": "sanctum-nextcloud-recovery-bundle/v1",
  "source_host": "kvin.outer.sanctum",
  "data_directory": "/var/www/html/data",
  "database": "nextcloud",
  "artifacts": {
    "application": {"filename": "nextcloud-html.tar", "bytes": 123, "sha256": "REPLACE"},
    "credentials": {"filename": "nextcloud-private.tar", "bytes": 123, "sha256": "REPLACE"},
    "database": {"filename": "nextcloud-postgresql.dump", "bytes": 123, "sha256": "REPLACE"}
  }
}
```
The validator can run offline as
`python3 tools/nextcloud-recovery-bundle.py /private/recovery-point`
**after** the application+database snapshot operation has been designed and
approved. It is not a command to run on live Kvin today; no recovery bundle
exists yet.

Passing manifest/hash/header checks proves **byte integrity only against
that manifest**; they do not establish snapshot consistency, authenticity of
the manifest, off-host custody, a valid SQL restore or working Nextcloud.
The actual coordinated backup procedure, authenticated retention and isolated
restore are still pending. Never pass private archive contents or generated
secrets through issue comments. Maintenance owns the shared PostgreSQL
service and the narrow Nextcloud database dump interface; the Services owner
has requested that interface on Maintenance issue #17. No production
Nextcloud maintenance-mode change, file snapshot or DB dump has been run.


## November 16 — private bundle producer (source only, no native backup)

`tools/nextcloud-recovery-assemble.py` now provides the missing **file-level
bundle assembly** counterpart to the earlier read-only verifier. It reads
an **already-quiesced, accessible** Nextcloud HTML source tree, the exact four
private credential/configuration inputs and an already-produced
**Nextcloud-only PostgreSQL custom-format dump**. It writes three protected
payloads and a manifest into a **new** 0700 directory (0600 files), then calls
the existing integrity verifier. It refuses missing files, linked or special
members, wrong dump header, pre-existing output names and output nested inside
its own input trees. Its output deliberately continues to report
`consistent_snapshot_proven=false`, `database_restore_tested=false` and
`independent_off_host_retention_proven=false`.

**No Kvin invocation is approved yet.** This tool neither selects a snapshot
time nor enters/exits Nextcloud maintenance mode. It does not invoke pg_dump,
restore PostgreSQL or copy data to Peanut. A malformed or interrupted attempt
may leave a private **incomplete** output directory; it is never evidence
of a successful recovery bundle. Before native use, explicitly qualify the
existing rootless user-namespace/host-file read permissions for all Nextcloud
data, including UID 33-owned paths. Do not work around permission errors by
changing live ownership or broadening permissions.

The source-only tests exercise complete fixture assembly, private output modes,
missing inputs, symlinks, collision protection, unsafe destinations and invalid
dump signatures. Production still needs the **Maintenance-owned scoped database
export contract**, a guarded Services coordinator that confirms and restores
Nextcloud's maintenance state, one consistent write-freeze window, protection
and verification of an off-Kvin copy, and a real isolated restore. No current
operator action is implied by source CI success.

**Planned operator sequence (not yet an executable runbook):** review approved
authorization and destination -> confirm correct running source and writable
quiescence control -> enter Nextcloud maintenance mode -> Maintenance-scoped
database export while writes remain quiesced -> assemble matching application,
private and database bytes under the same freeze -> validate -> **always**
restore the original maintenance state and verify service health -> transfer
privately to an independent host and verify -> isolated restore and consumer
acceptance. A failed database export must never silently publish the source
bundle as a valid recovery point.

## November 16 — guarded coordinator candidate and rootless-readability gate

`ansible/nextcloud-consistent-backup.yml` is now a **source-only guarded
candidate**, not an approved operating playbook. It requires an exact Kvin
target, separate explicit live/write-quiescence authorization, and an
approved **complete owner-supplied argv list** for a synchronous scoped
PostgreSQL dump whose output path matches its privately staged destination.
It refuses an uninstalled or already-maintained instance, enables
maintenance mode, confirms that status, invokes the owner export, assembles
files while writes are quiesced, and has an Ansible `always` sequence to
return Nextcloud to its prior **nonmaintenance** state. That source and its
unit/syntax checks do **not** prove a successful live run, full maintenance
consistency (including independent writers), the owner interface, archive
read permissions, off-host retention, or restore. **Never paste this
playbook's approval variables or invoke it until these prerequisites are
settled.** The resulting files, if ever produced, are only a local Kvin
bundle until independently protected on another host.

Before using this coordinator, the new
`tools/nextcloud-recovery-readability.py` can traverse the entire
current HTML bind and four private credential/config inputs **read-only**
within the same `podman unshare` rootless user namespace planned for the
producer. It attempts a one-byte read from every regular file and rejects
symlinks/special members and unreadable subtrees. It returns *only aggregate
counts and boolean status*, not paths or contents. This is a distinct
necessary gate from the already accepted ten-path presence observer.
A pass establishes source readability at that instant, **not** a snapshot,
absence of concurrent writers, owner dump interface, or recovery.

**Single Kvin-only read-only operator check after CI accepts this source**:

```bash
cd ~/src/sanctum-services &&
git pull &&
podman unshare python3 tools/nextcloud-recovery-readability.py \
  --html-root /home/wdc2/srv/sanctum-services/nextcloud/html \
  --private-root /home/wdc2/.config/sanctum-services/nextcloud
```

This performs no Nextcloud service change, no DB operation, no backup creation
and prints no user files. Return the single sanitized JSON record (or the
exact failure); report `git pull` errors if it stops before the scan.
**Do not** send archive contents or credentials.

## November 16 — first native readability refusal and diagnostic correction

Nova ran the **read-only** Kvin `podman unshare` source traversal and received
`Nextcloud bundle source traversal refused (private details withheld)`.
This confirms the gate **refused**, not why; no private files were reported,
no backup was created, and no application/database mutation was requested.
**Do not infer a permission failure, symlink, or missing input from the
generic denial. Do not alter filesystem permissions to make it pass.**

The original diagnostic suppressed all cause information. Source now reports
a fixed, private-safe JSON error containing only `status=refused`,
`stage` (`required_inputs`, `html_tree`, `private_inputs` or `startup`),
and `reason` (a bounded error category), with no real filenames, file
contents, or passwords. CI tests verify redaction, failure-stage mapping
and the previously accepted read-only success contract.

**Next Kvin action once diagnostic source CI is green:** repeat the same
nonmutating command from the immediately preceding section after normal
`git pull`. Return the **one JSON record on stdout or stderr**, not raw
paths or private data. This is a targeted attempt to identify the *cause*
of the first refusal and is not reopening the earlier successful
ten-path/occ inspections. If the gate still refuses, fix only the
identified producer/namespace/permissions issue with review before an
actual live backup operation.

## November 16 — actual HTML-tree special-entry gate (no permission changes)

Nova ran the source-qualified Kvin full-tree scan again. It returned exactly
`{"application_interrupted": false, "backup_created": false,
"file_paths_or_contents_returned": false, "reason": "unsafe_source_member",
"stage": "html_tree", "status": "refused"}`. This establishes that the
source contains at least one unsupported entry type **within the existing
HTML tree**. It is not evidence of a general file-read permission failure.
The producer currently supports only ordinary files and directories and
the integrity validator likewise rejects symlinks and special archive
members. **Do not strip links, silently skip the entry, chmod/chown the
tree, or relax archive extraction safety just to make this pass.**

A new standalone, read-only `tools/nextcloud-recovery-specials.py`
classifies **all** HTML-tree entry types, aggregates unusual members by
fixed broad component groups (`config`, `data`, `custom_apps`,
top-level or other), and classifies links as absolute/relative,
resolved inside/outside the source or dangling. It returns counts and
known safe labels **only**; no individual names, link targets or file
contents. It does not follow symbolic links or create an archive.

**Next single Kvin-only operator action after CI passes:**

```bash
cd ~/src/sanctum-services &&
git pull &&
podman unshare python3 tools/nextcloud-recovery-specials.py \
  --html-root /home/wdc2/srv/sanctum-services/nextcloud/html
```

Return the complete JSON result, or the exact command failure. This is a
**new classification** of the accepted refusal, not another meaningless
repeat of the existing readiness observer. If links are internal, assess a
safe self-contained archive/restore policy and tests; if external, identify
their real data owner and reconstructible backing *without assuming their
targets are included*. If the offending entries are sockets, FIFOs, or
devices, determine whether they are transient and how a consistent backup
procedure should exclude or reconstruct them **before** modifying the
producer and validator. No native backup, interruption or database dump is
authorized by this scan.

## November 16 — internal-link discovery and source-policy correction

Nova ran the Kvin metadata-only classifier and returned this **native,
nonmutating source topology receipt**:

| Source class | Count |
| --- | ---: |
| Ordinary directories | 3,877 |
| Ordinary files | 28,955 |
| Symbolic links | **118** |
| Other special entries (FIFO, device, socket, unknown) | **0** |
| Absolute or externally resolving links | **0** |
| Dangling or unresolved links | **0** |

All 118 links are **relative**, resolve **inside the same HTML tree**, and
occur under the classifier's broad `other` region (neither `data`,
`config`, nor `custom_apps`). Total entries reported: 32,950.
**Do not rerun the classifier without a specific new reason.**

**Revised Services source policy (source-only until CI + native gate):**

- Preserve a relative link *as a link*, rather than copy its target data,
  silently omit it or follow it out of the persistent tree.
- Producer `tools/nextcloud-recovery-assemble.py` permits a link only if
  relative, lexically confined to the HTML source and strictly resolvable
  inside that same source. Missing, cyclic, absolute and external targets
  are rejected. The file walk never descends through a link. Private
  credentials remain ordinary file-only inputs.
- Independent `tools/nextcloud-recovery-bundle.py` archive verification
  requires every application link to be relative, archive-confined,
  resolvable through any finite internal link chain to a member **actually
  present in the archive**. Reject linked parents with archive entries
  underneath them, duplicate paths, dangling/cyclic/escaping links,
  hardlinks and special file types. Private credential tar links are still
  forbidden. Verifier performs **zero archive extraction**.
- `tools/nextcloud-recovery-readability.py` now checks the complete real
  source tree, verifies link eligibility without dereferencing linked file
  contents, and returns sanitized counts (including
  `html_relative_internal_symlinks`). Source tests simulate both allowed
  links and malicious archive metadata.
- This acceptance is for archive **construction and verification**, **not**
  direct unsafe extraction. The *future isolated restore* must implement
  and test a separate extraction strategy that does not follow preexisting
  or archived symlinks outside its new private staging root.

**Next native test after all modified code passes CI:**

```bash
cd ~/src/sanctum-services &&
git pull &&
podman unshare python3 tools/nextcloud-recovery-readability.py \
  --html-root /home/wdc2/srv/sanctum-services/nextcloud/html \
  --private-root /home/wdc2/.config/sanctum-services/nextcloud
```

This is **not a retry of an unchanged diagnostic**: it qualifies the
source-selected preservation policy against the actual **118 already
identified** links. Expect one sanitized JSON record; do not send user
content or any credentials. No production service or database mutation,
no backup creation. The separate Maintenance-owned Nextcloud-only PG dump
interface and approval for an eventual write-quiescing operation remain
outstanding.
