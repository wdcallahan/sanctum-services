# Sanctum Services — Roadmap

**Status:** Initial Nextcloud source exists; deployment paused for runtime-design correction.  
**Updated:** 2026-10-17.  
**Scope:** Reproducible operation of self-hosted application services, beginning with Nextcloud.  
**Current waypoint: Stage 1 — choose and demonstrate the Ansible Navigator + EE operating model.**

## Destination

An independently maintainable service, **not just a running container**. Nova should be able to install, inspect, modify, update, back up, restore, move, and uninstall the service using understandable, documented procedures and the owning automation. The build itself is hands-on education relevant to his Red Hat instruction, professional experience, and CV.

Four requirements must be true **from the start**, not promised at the end:

1. **Documented:** The public-facing explanation and operations guide make sense without chat history or project-lead notes.
2. **Repeatable:** Automation plus declared durable inputs reconstruct the service; unchanged reruns converge.
3. **Understandable:** Nova knows why each component exists and can independently operate and troubleshoot it. The technologies selected for professional learning are exercised for real.
4. **Uninstallable:** Application-owned runtime objects can be cleanly removed. Data retention or intentional destruction is an explicit separate choice, with verified scope.

A healthy service, passing syntax test, or documented procedure alone does not meet these conditions.

## Decisions already established

- First service: **Nextcloud**, using the Apache container variant and existing PostgreSQL.
- Initial application host: **Kvin** (`aarch64`, rootless Podman); host TCP **8085 → container TCP 80**. Port was observed unoccupied on October 17; confirm at deployment.
- Users reach a **stable service name via YXORP**. The actual public hostname and scheme remain to be chosen. Moving hosts or host ports changes the proxy upstream, not the user's service identity.
- Initial live file storage: **Kvin's NVMe**, with an approximate **50 GiB soft planning budget**. **Peanut** is the separate backup destination (434 GB free on October 17). **Void** is the eventual intended persistent-storage host, not a dependency for the initial pilot.
- **Podman Quadlets, not Docker Compose**. The long-lived Ansible experience should use **Ansible Navigator with an EE**. Do not reproduce per-project venvs as a default merely because they are easy to create.
- Secrets and nonreconstructible data are managed outside public plaintext Git. Existing PostgreSQL, proxy, network registry, and controller infrastructure each retain their own ownership boundaries.
- Source-control workflow: direct linear `main`, no default branch/PR ceremony; GNU GPL version 3 or later for our original work.

## Work sequence

These are *acceptance gates*, not calendar estimates. An unchecked gate has no acceptance evidence yet. Complete each active stage before relying on it in the next one; nondependent documentation can evolve alongside implementation.

### Stage 0 — Establish the correct objective

- [x] Give the service deployment its own repository.
- [x] Record host/storage/port observations and the separation from adjacent projects.
- [x] Correct the false claim that an installation or syntax test establishes a completed service.
- [x] Withdraw the direct-via-venv deployment instructions pending EE design.
- [x] Preserve Nova's practical-learning, independent-operation and **teach when a real operation needs it** requirements in the existing cross-project [Nova–Pixel interface standard](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md). Preserve his choice of plain `git pull` in the existing [Git standard](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md).
- [ ] Separately review whether the [Operational Project Completion Standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md) needs an explicit four-part exit test. This normative document has **not** been amended; avoid creating another overlapping policy.

**Evidence:** Repository source and operator terminal observations, recorded separately in the [engineering log](history/engineering-log.md). The four requirements above are Nova's explicit objective for this project whether or not the shared standards amendment is approved yet.

### Stage 1 — Controller workflow: learn the mechanism before hiding it

- [ ] Diagram the normal path: **Kvin/Peanut host → ansible-navigator → selected EE container → playbook → managed host**. Explain where Ansible, collections, Python, Podman, SSH, and the project files actually run.
**Existing learning example:** Sanctum Maintenance already has a `localhost/sanctum-maintenance-ee:2026.07` image and `ansible-navigator` tooling established on both Debian ARM64 controllers; see its [Navigator configuration](https://github.com/wdcallahan/sanctum-maintenance/blob/main/ansible-navigator.yml) and [controller pair runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/controller-pair-readiness.md). The Maintenance EE is **qualified for that project only** and must not be silently promoted to a generic shared runtime. Its existing Navigator installation is a valid, read-only object lesson before deciding how to install a centrally managed toolchain for other projects.

- [ ] Identify the correct owner for a **shared controller-tool installation and reusable EE image**. Decide with Nova whether the existing controller infrastructure should own it or whether a bounded separate owner is justified. Do **not** give Nextcloud accidental ownership of both controllers.
- [ ] Decide and document how Navigator/Builder are installed on both Debian controllers: supported native packages if available; otherwise a separately justified and centrally managed host-tool installation. An EE does not require a project-local Python venv.
- [ ] Define a minimal, version-controlled EE with the required Ansible/collection/system dependencies; pin the selected content and document rebuilding and reobtaining the exact accepted image. Qualify it on **ARM64** and establish usable availability on both controllers.
- [ ] Use Navigator to inspect the EE contents and run a small harmless read-only playbook. Nova practices the steps and understands the output.
- [x] Remove the **wrong inventory override** `ansible_connection: local`. The inventory now uses Ansible's default **smart** connection (SSH for Kvin) and names `wdc2` as the managed user. **Source correction only; no EE/SSH acceptance test yet.**
- [ ] Qualify SSH from the EE to Kvin, including **Kvin → SSH → Kvin** and **Peanut → SSH → Kvin**. Confirm access to the intended `wdc2` rootless user-systemd manager without mounting arbitrary host control sockets into the EE.

**Exit test:** Starting in a normal shell on either controller, Nova can identify the configured EE, launch Navigator, inspect its Ansible and collections, and run a read-only task against the intended *host* (not the EE container). Both controllers can reconstruct the tooling from its owning source and durable image inputs.

**YOU ARE HERE.** No Nextcloud application deployment until this model is working and understood.

### Stage 2 — Build a complete first-deployment path

- [ ] Review the existing `ansible/` candidate against the approved execution model; revise or replace mistaken assumptions at source instead of layering workarounds.
- [ ] Configure a stable user-facing Nextcloud hostname/scheme and confirm YXORP's intended route.
- [ ] Confirm a stable **named** endpoint and the PostgreSQL owner's supported way to provision Nextcloud's dedicated database and role. Do not embed a transient IP or change shared database ownership from this repo.
- [ ] Choose and verify a platform-compatible **digest-pinned Nextcloud Apache image**.
- [ ] Define persistent directories, appropriate rootless ownership, private secrets, Quadlet, startup/lingering, and a bounded host port through Ansible.
- [ ] Define **installation and removal** procedures together, so each managed object has a clear owner and safe removal behavior.
- [ ] Run static checks (syntax and relevant lint/tests) **in the intended EE**, then deploy from Kvin through Navigator.
- [ ] Run the same playbook again and require truthful **zero-change convergence**.

**Exit test:** A new application host can be configured from source and declared secrets; the Nextcloud service starts, survives the supported restart sequence, and a second unchanged deployment reports no changes.

### Stage 3 — Demonstrate real Nextcloud use

- [ ] Establish and verify PostgreSQL connectivity and initial application setup.
- [ ] Verify the service through YXORP at its stable name; confirm trusted domains/proxy headers, expected scheme, and absence of undesired direct public exposure.
- [ ] Log in as a real test user; upload, download, edit, and delete a representative file; demonstrate the intended client behavior.
- [ ] Define and verify appropriate background-job scheduling, error visibility, and a practical inspection/troubleshooting procedure.
- [ ] Explain the path of an actual request and file write, from user-facing name to container, filesystem, and database.

**Exit test:** Nova can use and diagnose the application without guessing which host, port, volume, or database it uses.

### Stage 4 — Backup, restore, and replaceability

- [ ] Implement automated, recoverable copies on **Peanut**, including retention and an observable last-success status. A mirror that propagates accidental deletion is **not** sufficient.
- [ ] Define an application-consistent backup set: Nextcloud files/config, database snapshot through its owner, and required secrets/recovery inputs; include correct ownership restoration.
- [ ] Perform a **real restore exercise** into a separate qualifying location from the retained backup artifacts; verify files and application operation independently.
- [ ] Document how to replace Kvin's Nextcloud role without requiring ChatGPT, remembered commands, or the surviving source container.
- [ ] Recheck capacity and retention against the 50 GiB soft budget; raise the budget if actual use requires it.

**Exit test:** An observed backup can restore a working Nextcloud instance and its representative files without relying on unstated local residue.

### Stage 5 — Normal operation, upgrades, and uninstall

- [ ] Write and exercise readable operator runbooks for deploy, check status, stop/start, update, troubleshooting, and recovery.
- [ ] Demonstrate a controlled image/configuration update through source-controlled desired state; identify rollback limits, including database/schema compatibility.
- [ ] Exercise **uninstall with data retained**: remove only owned services/configuration as intended and leave a recoverable data set.
- [ ] Exercise **explicit purge** only with deliberately disposable test data; do not silently delete shared PostgreSQL state or valuable files. Document the owner and authorization for database deletion.
- [ ] Have Nova follow the published procedures, explain the major mechanisms, and independently perform representative operations without relying on new ad hoc instructions.
- [ ] Review the README and runbooks as a new human administrator would. Remove stale guidance and ensure links, commands, status claims, and dependency owners are clear.

**Exit test — first project complete:** The four requirements are demonstrated with meaningful evidence: documented, repeatable, understandable, **and** uninstallable. A fresh operator can navigate the repository and Nova can administer the service himself.

### Stage 6 — Later, explicitly separate work

- [ ] Move persistent file storage toward **Void** when its storage service is ready; use the stable YXORP name, controlled data migration, rollback, and restoration checks. Do not make this a hidden condition for the Kvin pilot.
- [ ] Consider **Home Assistant** as a separate application module, subject to its own actual storage/database requirements.
- [ ] Reuse the same established operator and documentation patterns without copying an unnecessary new EE or implementation for each service.

These items are **future work**, not reasons to keep the completed Nextcloud pilot perpetually unfinished.

The normal managed-host connection is **smart/SSH**, including when the controller and managed host happen to be the same physical machine. This makes controller location an operational choice rather than changing playbook semantics.

## Important work boundaries

- `sanctum-services` owns application deployment, its lifecycle contract, and its operator documentation.
- A shared Navigator/EE controller toolchain must have a clearly agreed owning infrastructure project before it is installed as a reusable platform service.
- PostgreSQL provisioning/backups, proxy upstream management, DNS/network registration, and fleet OS maintenance are coordinated with their owners, not silently absorbed.
- The broader review of other Sanctum projects against this educational/maintainability objective is a separate cross-project effort. This roadmap does not authorize mass refactoring.

## Evidence and documentation policy

- **README:** purpose, current status, and navigation; newcomer-friendly.
- **Architecture:** actual supported mechanisms, ownership, data flows, and key reasons.
- **Runbooks:** proven end-user commands/procedures, preconditions, expected results, troubleshooting, and recovery.
- **This roadmap:** destination, checkpoints, acceptance tests, and the active frontier; change the tick boxes only when evidence supports them.
- **[Engineering log](history/engineering-log.md):** dated experiments, changes, failures and evidence links. Not a second manual and not a transcript archive.
- **[Lead handoff](../PROJECT_LEAD_INTRODUCTION.md):** concise continuity for another assistant; not a prerequisite for human operators.

When the implementation changes, update the relevant explanation and operational procedure **with the same change**. Do not promise to document it after deployment. Record substantial outcomes separately in the engineering log.
