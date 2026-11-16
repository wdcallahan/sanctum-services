# Town Square / Nextcloud — complete-instance recovery boundary

**Status:** The existing Kvin Nextcloud installation and Calendar 6.6.2
bidirectional use are accepted. The installation/app-manifest roles are
source-managed, but **full-instance backup, independent storage, and an
isolated recovery have not been accepted**. This document authorizes no
application downtime or database change.

## Recovery contents and ownership

- Include the **actual** Nextcloud data directory, configuration,
  installed/custom app files, and user content. The source role mounts
  `~/srv/sanctum-services/nextcloud/html` at `/var/www/html` but that
  does **not** prove `html/data` is the configured data directory.
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
a backup exists. The default data-path presence report is **not** proof
of the effective configured data directory.

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
