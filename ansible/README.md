# Nextcloud installation — initial Ansible source

The first target is Kvin, with **rootless Podman Quadlets** and
an external existing PostgreSQL service. The application listens on **80/tcp
inside its container**; the host mapping starts at **8085/tcp**, behind YXORP.
The host, port, storage path, image digest, and stable application DNS name
are configuration inputs rather than part of Nextcloud's identity.

This is an **unqualified initial source candidate**, not a published claim
that a working Nextcloud or reliable backups have been deployed.

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

## Inputs required before the first apply

1. Choose the stable Nextcloud service hostname and public scheme in
   `ansible/group_vars/nextcloud.yml`, plus the authoritative named
   PostgreSQL endpoint (never hard-code an IP address).
2. Resolve and select a Nextcloud **Apache image by digest** that supports
   the host architecture; do not treat a floating tag as immutable.
3. Have the PostgreSQL owning operation provision the dedicated `nextcloud`
   role and database with its own credential. This deployment does not
   modify the shared database's service, network binding, roles, or HBA.
4. Supply `vault_nextcloud_postgres_password` and
   `vault_nextcloud_admin_password` in encrypted
   `ansible/group_vars/nextcloud/vault.yml`. For example create it with
   the approved encrypted-variables workflow. Keep the Vault unlock secret
   outside Git.
5. Verify the desired user systemd manager is reachable and lingering is
   correctly managed for persistent rootless services. Confirm no other
   service is bound to the configured host port.

**No apply command is approved yet.** After the EE-based operator path
has been chosen, tested, and documented, qualify the installation and
unchanged repeat. Verify Nextcloud login through YXORP, not just a
running process or HTTP status.

Also implement and exercise distinct operator procedures for start/stop,
inspection, upgrades, backup, restore, and **uninstall**. Uninstall must
remove only application-owned resources while clearly offering *retain*
versus explicit *purge* handling for user data, configuration and secrets.
None of these lifecycle promises is presently accepted.

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
