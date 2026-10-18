# Sanctum Services — Continuation Entry Point

This is a **short orientation and recovery note**, not a Golden Book, a second configuration authority, or a demand that every successor reread every engineering standard.

## Purpose and ownership

Sanctum Services owns the **repeatable deployment and recovery of self-hosted applications** through Ansible and rootless Podman Quadlets. The first intended application is Nextcloud; Home Assistant is a possible later addition, not part of the current deployment.

Nova chooses consequential architecture and operational changes. Pixel works with Nova **in an ordinary ChatGPT conversation**, with Nova operating the native terminal when required; do not assume Work mode, subagents, unattended continuation, or live SSH access. A new assistant is appointed to continue this project by Nova's actual direction, not merely by reading this file.

Preserve project boundaries:
- This repo owns application deployment configuration, its orchestration, verification, and documented recovery dependencies.
- The Sanctum registry owns authoritative host/network facts. Sanctum Maintenance owns OS/fleet maintenance. Joule owns its own application stack.
- Existing PostgreSQL and YXORP/nginx integrations are dependencies; their configurations belong to their respective owners. Do not silently modify adjacent projects.

The published Ansible playbooks, roles, variables, and Quadlets will be the **evolving executable desired state**. This document records the current goal and evidence, but never overrides actual source or observed behavior.

## Working rules

- Follow the applicable current [Git](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md), [Ansible](https://github.com/wdcallahan/engineering-standards/blob/main/Ansible-Project-Engineering-Standard.md), [Operational Completion](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md), and [Nova–Pixel Interface](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md) standards **for the active operation**, without treating them as a mandatory full rereading exercise on every chat turn. Some links are access-controlled.
- Work directly on `main`; no branches or pull requests unless Nova specifically authorizes them. Preserve and inspect unknown local work.
- Use Podman Quadlets, **not Docker Compose**. Prefer simple, declarative Ansible and verify rerun idempotence.
- Default to GNU GPL version 3 or later for original project code and documents, subject to applicable third-party licenses.
- Public Git must not contain passwords, tokens, backup secrets, or other sensitive material. Declare and manage secret inputs separately.
- Treat proposed architecture, committed source, tests, actual deployment, and observed operation as different levels of evidence. No implied completion.

## Active boundary — 2026-10-17

**Goal:** Install a useful Nextcloud service, via repeatable automation, using the existing PostgreSQL infrastructure and existing reverse proxy. No project deployment has yet been demonstrated.

**Candidate host:** `kvin.outer.sanctum`, not yet an irrevocable placement decision. Nova's native-terminal observations:

- `hostname -f`: `kvin.outer.sanctum`; `uname -m`: `aarch64`.
- `df -h ~`: root filesystem 917G total, 11G used, **870G available** at observation time. Filesystem capacity does not establish a backup strategy.
- Rootless Podman storage: `/home/wdc2/.local/share/containers/storage`.
- `podman ps` / `ss -ltnp` confirm **8083 is the EyesOnly/SearXNG `search` container** (container port 8080), and **8084 is the `joule-prism` container** (container port 8000, via rootless `pasta`). Both are occupied and must be preserved.
- `sanctum-postgresql` currently publishes **`192.168.1.192:5432` to container 5432**. Nova confirms that binding is an existing, separately tracked ticket and is intended to become `0.0.0.0:5432` when the responsible work is done. This is not a Sanctum Services fix; do not modify it. Database port 5432 is not a Nextcloud inbound port.
- Two running Joule PostgreSQL restore containers, `joule-presence-restore-mhleutvr` and `joule-attachments-restore-9hk2s3ag`, show container-only port 5432 with no published host binding. Do not disturb them.
- Kvin already has a documented rootless Podman Quadlet precedent in the [EyesOnly SearXNG repo](https://github.com/wdcallahan/eyesonly-searxng).
- **Planned Kvar-to-Kvin migrations:** Dashy, Uptime Kuma, LinkStack, Nginx Proxy Manager and Pi-hole. Nova clarified that their old Kvar host-port mappings are **not constraints on the new rootless services**: select convenient conflict-free Kvin ports. Nginx Proxy Manager is rootful and needs its real host-facing web ports; DNS port 53 belongs to BIND, **not Pi-hole**, which no longer provides DNS. The migration is owned separately from Nextcloud; do not prescribe port mappings for it.

**Nextcloud network intent:** The standard Apache image listens on **TCP 80 inside the container**. Nova's `ss -ltn '( sport = :8085 )'` on Kvin returned no listeners on October 17, so **host TCP 8085 → container TCP 80** is the selected initial mapping (check again when deploying). Rootless applications can be remapped and do not need their former Kvar host ports. YXORP is intended to reach Nextcloud through its host endpoint and user-facing name; proxy naming/configuration is still to be agreed. An application container's connection to PostgreSQL (TCP 5432) is *outbound*, not an additional Nextcloud published port. Redis is optional and would be a separate internal service if chosen. Do not change production proxy routing until Nextcloud itself is verified.

**Runtime observation:** Kvin reports Podman 5.4.2. `ansible-playbook` is absent from the ordinary PATH, but Nova verified executable `~/src/sanctum-maintenance/.venv/bin/ansible-playbook` and `ansible-navigator` at the corresponding path. These belong to the maintenance project's virtual environment; availability is proven, but using that project-owned environment as Sanctum Services' **reconstruction authority** is not justified. Define the new project's own reproducible dependencies.

**Storage direction agreed with Nova:** For the initial learning period, Nextcloud's live persistent files may reside on **Kvin's NVMe**, with recoverable backup copies on **Peanut**; the intended eventual durable storage host is **Void**. The application's filesystem location, host and port must be configurable inputs to Ansible rather than embedded identity. **Provisional capacity budget: 50 GiB** of live file data on Kvin and at least a corresponding backup-copy allowance on Peanut; this is a planning budget, not a requirement to create a fixed-size partition or Podman volume. Peanut's free space and backup retention need verification. Treat live files, Nextcloud config, credentials, and consistent PostgreSQL backups as a restorable set, rather than assuming a copy of only the files is a backup. Preserve the user-facing Nextcloud URL through YXORP when moving from Kvin to Void; Nextcloud's trusted domain/proxy settings still have to match the intended endpoint.

**Important unresolved choices:** the exact Kvin/Peanut storage paths, recoverable backup mechanism and retention, where associated database/secret backups are held, and the intended proxy hostname/settings. Kvin's live NVMe is accepted for this initial phase, not as a permanent storage decision. No commitment to expose Nextcloud directly to the public internet has been made.

## Resume and next small step

1. Confirm Nova's current request and inspect the present `main` source and this note; check any newer documented decisions. Do not infer that this dated observation is still true.
2. Reconcile only the **active Nextcloud** boundary with relevant current standards, actual local/host evidence, and any in-flight changes. Avoid rebuilding an exhaustive project history.
3. **Next action:** check Peanut's free storage before committing to a backup retention budget. Agree on the initial bind-mount/storage paths and intended Nextcloud public hostname, then define the new project's independent Ansible runtime and application role. The host-port candidate and path to existing Ansible executables were checked; do not repeatedly rediscover them.
4. Implement the smallest complete Ansible/Quadlet path; verify clean second-run convergence and real browser access through the intended proxy. Record database/volume backup and restore requirements before claiming reconstructibility.
5. Update this handoff when the frontier changes meaningfully: what's proven, what remains open, and the next safe operator or Pixel action. A successor must never execute this note's next step without comparing it to current evidence.

**Current frontier:** repository created; minimal README and GPL license present; deployment planning underway; no Nextcloud service acceptance or recovery test yet.
