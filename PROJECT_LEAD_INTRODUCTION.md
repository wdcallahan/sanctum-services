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
- **Planned services migrating from Kvar to Kvin:** Dashy, Uptime Kuma, LinkStack, Nginx Proxy Manager, and Pi-hole. These services may reserve host ports or storage despite not appearing in the observed running-container list.
- Historical **Kvar host-port allocations** from prior Nova/operator discussions (not confirmed as final Kvin reservations): Dashy **8082→8080**, Uptime Kuma **3001→3001**, LinkStack **8081→80**, Nginx Proxy Manager **80, 81, 443**, Pi-hole **53 TCP/UDP and 82→80**. The migration is a separate workstream; later redesigns may change these ports. Confirm before relying on them.

**Nextcloud network intent:** The standard Apache image listens on **TCP 80 inside the container**. The selected host-side port is **undecided** and must be checked before binding; neither 8083 nor 8084 is free in the observed snapshot. No host port has been committed as Nextcloud desired state yet. Based on the historical Kvar assignments and Kvin's observed listeners, **8085/TCP is a reasonable candidate**; verify no newer migration reservation and actual availability before setting it. YXORP will connect to the selected Kvin host endpoint and provide the user-facing name. An application container's connection to PostgreSQL (TCP 5432) is *outbound*, not an additional Nextcloud published port. Redis is optional and would be a separate internal service if chosen. Do not change production proxy routing until Nextcloud itself is verified.

**Runtime observation:** Kvin reports Podman 5.4.2, and `command -v ansible-playbook` returned no path in Nova's login shell. Sanctum Maintenance has a separately qualified containerized Ansible runtime; do not assume it is a supported application-deployment runtime without checking its contract.

**Important unresolved choices:** Which host-side HTTP port given pending migrations; whether Kvin is the long-term storage host; where Nextcloud files, database state, secrets, and **restorable backups** live; and what proxy hostname/settings Nova wants. No commitment to expose Nextcloud directly to the public internet has been made.

## Resume and next small step

1. Confirm Nova's current request and inspect the present `main` source and this note; check any newer documented decisions. Do not infer that this dated observation is still true.
2. Reconcile only the **active Nextcloud** boundary with relevant current standards, actual local/host evidence, and any in-flight changes. Avoid rebuilding an exhaustive project history.
3. **Next operator observation on Kvin:** reconcile the five historically assigned Kvar ports against the current migration plan and verify whether Nextcloud can reserve **8085/TCP**; do not change those other applications. Then select the application deployment runtime and settle Nextcloud's persistent-data location and proxy name with Nova. Inspect the existing Ansible execution interface and then settle the Nextcloud persistent-data location and reverse-proxy name with Nova. No deployment or database provisioning has been authorized solely by this handoff.
4. Implement the smallest complete Ansible/Quadlet path; verify clean second-run convergence and real browser access through the intended proxy. Record database/volume backup and restore requirements before claiming reconstructibility.
5. Update this handoff when the frontier changes meaningfully: what's proven, what remains open, and the next safe operator or Pixel action. A successor must never execute this note's next step without comparing it to current evidence.

**Current frontier:** repository created; minimal README and GPL license present; deployment planning underway; no Nextcloud service acceptance or recovery test yet.
