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

1. Identify the effective configured data path and an appropriate **off-Kvin**
   protected backup destination with capacity, integrity verification and
   retention; another path on Kvin alone is not disaster recovery.
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
\`/var/www/html/data\` from \`podman exec -u www-data sanctum-nextcloud php
occ config:system:get datadirectory\`. This is a confirmed configured path,
not an inference from directory presence. The existing Quadlet's bind
\`~/srv/sanctum-services/nextcloud/html:/var/www/html\` includes that data
directory, \`config/config.php\`, and \`custom_apps\`.

**Do not repeat** the accepted six-task native input play or this OCC query.

The source-only \`tools/nextcloud-recovery-bundle.py\` verifies one
privately staged recovery bundle, with three exact artifacts: a full HTML-tree
tar archive, a private configuration/credential tar archive, and a
**Nextcloud-database-only** PostgreSQL custom-format dump. Its
\`manifest.json\` must name the exact host, data directory, and database;
each artifact needs a byte count and SHA-256. The verifier rejects unexpected
filenames, symlinks, group/world readable payloads, malformed paths,
special archive members, missing required state, and a missing PGDMP
header. It never extracts the archives or prints contents or credentials.

Example **manifest structure** (fake digests; not a usable backup):
\`\`\`json
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
\`\`\`
The validator can run offline as
\`python3 tools/nextcloud-recovery-bundle.py /private/recovery-point\`
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

