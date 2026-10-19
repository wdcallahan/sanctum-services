# Nextcloud installation — initial Ansible source

The first target is Kvin, with **rootless Podman Quadlets** and
an external existing PostgreSQL service. The application listens on **80/tcp
inside its container**; the host mapping starts at **8085/tcp**, behind YXORP.
The host, port, storage path, image digest, and stable application DNS name
are configuration inputs rather than part of Nextcloud's identity.

This is an **unqualified initial source candidate**, not a published claim
that a working Nextcloud or reliable backups have been deployed.

**October 19 progress:** Maintenance created production `nextcloud` database and
least-privilege `nextcloud` login, verified unchanged repeat and preserved Joule
readiness. The supported endpoint is `db.nexus.sanctum:5432`. Nextcloud has
**not** yet authenticated from its application container, initialized its
schema, or started its web service. See the [Maintenance handoff](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-10-19-nextcloud-postgresql-contract.md).


## Operator learning and execution model (not yet implemented)

**This candidate is paused before first deployment.** Nova's actual project
objective includes acquiring hands-on, independent operating experience with
**ansible-navigator and a containerized Ansible Execution Environment (EE)**.
The deployment is not a successful deliverable merely because it runs: it
must be documented, repeatable, understandable to its owner, and cleanly
uninstallable.

The initial repository mistakenly selected a project-local Python `venv`
and direct host-side `ansible-playbook`. On October 17, Nova installed
`ansible-core==2.19.14` into that venv and successfully ran the syntax
check (`playbook: ansible/site.yml`). That is historical syntax evidence,
**not approval of the runtime architecture**, and no Nextcloud deployment
was made. Do not repeat those venv commands as the standard procedure.

Next establish and explain the actual
**Navigator → selected EE → project playbook → Kvin container** path,
including how Kvin and Peanut reconstruct the chosen controller tooling.
Keep the runtime simple and shared where it makes sense; do not introduce
an additional wrapper that hides the mechanism Nova wants to practice.
The existing Sanctum Maintenance qualified runtime is separately owned
and must not be repurposed without verifying its contract.

An EE setup and tested Navigator invocation will replace this section
when they have been selected and qualified.

## Managed-host connection

The inventory deliberately omits `ansible_connection` and accepts Ansible's
standard `smart` connection selection: SSH to `kvin.outer.sanctum`
as `wdc2` on this Linux host. This remains correct when Navigator and
the EE run on Kvin itself: **the EE connects by SSH back to Kvin**.
From Peanut, the same inventory points to the same managed host.
This is a *source design*, not an SSH authentication or runtime acceptance result.
The EE must provide a supported, explicit SSH credential path and the
connection must allow control of `wdc2`'s user systemd manager.


## First-boot contract and remaining qualifications (October 19)

- The intended public name is `https://square.nexus.sanctum`, but DNS/HTTPS
  and the YXORP route have **not** been qualified by this project.
- ARM64 Nextcloud Apache 34.0.5 was pulled onto Kvin and its image digest
  pinned in source; the rootless Quadlet startup remains untested.
- The supported PostgreSQL endpoint is `db.nexus.sanctum:5432`, with database
  and login `nextcloud`. The real container must still prove DNS, authenticated
  SCRAM connection, and the application's actual schema creation.
- Nova prepared the **database-only encrypted** credential file at
  `/home/wdc2/.config/sanctum-services/secrets/nextcloud-postgresql.vault.yml`
  and the separate local Vault key at
  `/home/wdc2/.config/sanctum-services/secrets/vault.key`.
  Use those existing inputs through an explicitly qualified Vault/EE path;
  **do not regenerate passwords, paste them into chat, or put them in Git**.
- The first run intentionally **does not** supply
  `NEXTCLOUD_ADMIN_USER` or `NEXTCLOUD_ADMIN_PASSWORD` because Nova will create
  his own login in the **browser** and save it in Bitwarden. A fresh uninstalled
  `status.php` response with `installed=false` is expected and **not** a
  failing health check before the web wizard completes.
- The source places the database credential in a file inside a mode-0700
  host-only configuration directory. The individual file is mode 0644
  (accessible to the unprivileged web process within its read-only bind mount),
  but cannot be traversed by other normal host users through its private
  parent. The container environment holds only the secret-file **path**.
  This mechanism still needs actual user-namespace and Nextcloud image tests.
- Qualify rootless Podman storage ownership, the `wdc2` user systemd manager
  and lingering, and port 8085 availability. Arrange the authorized YXORP
  route and HTTPS access before entering the human admin password.

**No production apply command is approved yet.** We first test container DNS,
then authenticate from the actual Nextcloud image/network without displaying
secrets, and qualify first startup through the chosen Ansible/EE controller.
After browser setup, verify a real login and unchanged repeat. Plain HTTP or a
successful `status.php` response is not sufficient acceptance.

The source is a **candidate** until those native observations occur. We also
need actual backup, restore, upgrade and application-only uninstall procedures;
none are silently waived by first startup.

## Persistent state, backups, and migration

The default Kvin live data directory is
`~/srv/sanctum-services/nextcloud/html` (bind-mounted as
`/var/www/html`), so its contents can later move to Void. The learning
period's **50 GiB** is a soft capacity budget, not a quota. Peanut is the
intended separate backup destination; as of October 17 it had 434 GB free.

**No backup job is installed by this initial playbook.** Before storing
valuable files, define and verify a consistent restore set: uploaded files,
Nextcloud configuration, PostgreSQL database, necessary credentials, and
recovery of rootless user-namespace ownership. A mirror with propagated
deletions is not a substitute for recoverable backup history.

The first pass uses Nextcloud's default AJAX background-job method. Add
a qualified scheduler for the recommended cron mode before asserting normal
unattended operations are complete.

The initial host/port can change without changing the stable service URL
if YXORP is updated to point at the new backend. Never silently replace
the shared proxy or database ownership contracts.
