# Nextcloud installation — initial Ansible source

The first target is Kvin, with **rootless Podman Quadlets** and
an external existing PostgreSQL service. The application listens on **80/tcp
inside its container**; the host mapping starts at **8085/tcp**, behind YXORP.
The host, port, storage path, image digest, and stable application DNS name
are configuration inputs rather than part of Nextcloud's identity.

**Current evidence, October 20:** The Nextcloud rootless service on Kvin
responded locally with HTTP 200 at `192.168.1.192:8085/status.php`, with
`installed=false`; the unchanged Services deployment repeat passed. The
database-only Nextcloud client authentication was independently qualified by
Maintenance. The YXORP HTTP proxy still returned 502 because Kvin's
published-service firewall is missing ordinary 8085 admission. **The browser
installer, accounts, application-data acceptance, backup and recovery are not
complete.** Do not confuse a running container with a finished application.

## Kvin firewall owner and required install order

[Sanctum Maintenance's firewall owner](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/kvin-service-firewall.md)
manages Kvin's `8084/tcp`, `5432/tcp`, and `8085/tcp` in firewalld.
[Maintenance issue 18](https://github.com/wdcallahan/sanctum-maintenance/issues/18)
contains the reviewed source and preview. **Services' Nextcloud role does
not change the host firewall.** Before any Nextcloud storage, secret file,
Quadlet, or service operation, its read-only `firewall-cmd` queries require:
Kvin's `eth0` in `public`, and `8085/tcp` permitted in **both runtime
and permanent** `public` state. Missing permission fails with a diagnostic
that directs the operator to the Maintenance runbook; no compensating
application-owned firewall command is permitted. The two read-only
`firewall-cmd --query-port` tasks use task-scoped `become: true`: firewalld
may return `NOT_AUTHORIZED` (253) for an unprivileged query, which is not proof
that a port is closed. There is no Services-owned firewall mutation, and
other Nextcloud tasks continue as the unprivileged deployment user.

**Reconstruction order on a fresh Kvin:**
1. Complete the platform owner's host/network/firewalld foundations; apply
   only the bounded baseline, not the full old baseline over active services.
2. Apply the reviewed Maintenance service-firewall policy through its
   `playbooks/configure-kvin-firewall.yml` (using the independently
   authorized procedure). The
   [Maintenance reconstruction runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/kvin-firewall-acceptance.md)
   documents the baseline → service-policy composition.
3. Deploy/reconcile Nextcloud using this repository's `ansible/site.yml`,
   with its existing encrypted database-only input and the approved Navigator
   execution environment; the firewall preflight must pass first.
4. Qualify direct Kvin `/status.php` from an independent peer, YXORP route,
   installer/login and recovery. A firewall-pass is not an application-pass.

**Existing Kvin correction:** The bounded Maintenance baseline preview
returned `ok=12 changed=0 failed=0`, with no live changes. Maintenance has
separately previewed its ordinary ports and exact old-rich-rule removal.
Nova must explicitly approve that **live** correction; it has not happened
merely because Services source was updated. Do not rerun the retired old
PostgreSQL deployment playbook or full host baseline for this correction.
Once Maintenance has converged both firewall stores, the next Services
playbook run may proceed; if not, its preflight stops before mutation.



## Operator learning and execution model (not yet implemented)

Nova's project objective includes hands-on, independent operating experience
with **ansible-navigator and a containerized Ansible Execution Environment
(EE)**. The previous application deployment used an existing qualified
Maintenance EE; independently co-building a general-purpose EE is still a
separate learning milestone.
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

The initial deployment used the existing qualified Maintenance Navigator/EE
path. Design and native qualification of a new reusable EE are separately
owned and are not prerequisites to this firewall ownership source transfer.

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

- The current pilot public name is `http://square.nexus.sanctum` without a
  trusted internal TLS certificate. Its YXORP HTTP route returned 502 and
  remains unaccepted; do not enter browser administrator credentials until
  the chosen transport's risks are considered.
- ARM64 Nextcloud Apache 34.0.5 is running from a pinned image digest via
  the rootless Quadlet; local `status.php` returned HTTP 200 with
  `installed=false`. Direct peer and browser acceptance are pending.
- The supported PostgreSQL endpoint is `db.nexus.sanctum:5432`, with database
  and login `nextcloud`. Maintenance qualified the container's DNS and
  authenticated SCRAM path. Nextcloud's installation/schema remain pending.
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
  This mechanism was exercised on Kvin; complete installer and recovery
  acceptance remain outstanding.
- Verify Maintenance's runtime **and** permanent 8085 admission before any
  application converge. Independent peer HTTP access and browser login remain
  separate acceptance gates. No new certificates or TLS policy are selected
  by the firewall handoff.

**No live firewall change is approved by this source transfer.** Existing
container startup and database authentication passed their bounded tests.
The next Services application run must wait for Maintenance-owned runtime and
permanent firewall policy, and real browser setup/login and recovery remain
unfinished. Plain HTTP or a successful `status.php` response is not sufficient
acceptance.

The service is deployed but **not accepted for real data** until browser
setup and operational qualification pass. We also need actual backup,
restore, upgrade and application-only uninstall procedures;
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


## Declarative third-party applications (source candidate, October 20)

The [pinned app manifest](nextcloud-apps.yml) and separate
[`apps.yml` reconciliation playbook](apps.yml) are now source-controlled.
The normal `site.yml` includes this role **after** the container is running
and web installation has completed. The manifest is initially empty, so no
third-party apps are changed by default. See the
[operator guide](../docs/runbooks/nextcloud-apps.md) for the review, validation,
verification and repeat requirements. Source is not native-accepted yet.
