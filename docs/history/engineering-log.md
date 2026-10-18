# Engineering Log — Sanctum Services

A short chronological record of significant observations, decisions, experiments and evidence. **Not** an installation guide, requirements authority, or raw chat/command transcript. For the current plan and accepted state, see the [roadmap](../ROADMAP.md).

## 2026-10-17 — Repository created and scope bounded

- Nova and Pixel created `wdcallahan/sanctum-services` on public `main`, with GNU GPLv3 license and an initial README.
- Scope: reproducible self-hosted application deployment via Ansible and Podman Quadlets. Nextcloud selected as the first service.
- A short `PROJECT_LEAD_INTRODUCTION.md` was committed for session continuity. No service was deployed.

## 2026-10-17 — Host, port, and storage observations

- On Kvin, Nova observed `kvin.outer.sanctum`, `aarch64`, Podman 5.4.2, and approximately **870 GB available** on NVMe.
- `podman ps` confirmed rootless EyesOnly/SearXNG using host **8083 → 8080** and Joule Prism using **8084 → 8000**; PostgreSQL was publishing **192.168.1.192:5432 → 5432**. The PostgreSQL bind-address correction is an already-tracked separate ticket.
- An `ss -ltn` query showed no listener on **8085**, so it became Nextcloud's selected initial host-port candidate. Nextcloud Apache itself listens on container **TCP 80**.
- Kvar-to-Kvin migration plans include Dashy, Uptime Kuma, LinkStack, Nginx Proxy Manager and Pi-hole. Nova clarified that historical rootless port numbers are not binding reservations; Nginx Proxy Manager has rootful port requirements, and DNS port 53 belongs to BIND rather than Pi-hole.
- On Peanut, Nova observed **434 GB free**. The agreed pilot plan is approximately **50 GiB soft live-data budget on Kvin**, separate recoverable copies on Peanut, and eventual storage on Void. Backup mechanism and retention are **not yet implemented**.

## 2026-10-17 — First Ansible candidate and syntax-only test

- Pixel committed a Nextcloud Ansible role, rootless Quadlet template, local-connection inventory, and a project-specific `ansible-core==2.19.14` venv recipe.
- On Kvin, Nova cloned/pulled the new repository, installed the declared controller dependency in `.venv`, and ran `--syntax-check` successfully: output `playbook: ansible/site.yml`.
- **Limit of evidence:** this established parsing only; no EE-based execution, deployment, database provisioning, proxy routing, backup, restore, or uninstall was demonstrated.

## 2026-10-17 — Original educational objective restored

- Nova identified a significant mismatch: years of requests to practice real **Ansible Navigator + Execution Environment** operations had been displaced by venv/direct-Ansible instructions. Professional learning and independent maintenance are central deliverables, not post-install options.
- The initial `ansible/README.md` was changed to **withdraw** the direct-via-venv apply instructions. The lead handoff now records the wrong runtime selection and blocks deployment until corrected.
- Additional review identified that the candidate `ansible_connection: local` would target an EE container rather than Kvin after the runtime switch. The inventory and connection approach remain **unaccepted**.
- Nova restated four nonnegotiable requirements: **documented, repeatable, understandable, uninstallable**. There is no initial value in a running but unmaintainable service. Work on the operator documentation, architecture explanation, roadmap, and this log began in response.

## 2026-10-17 — Human documentation and roadmap separated

- Replaced the repository landing page with a newcomer-readable README, explicit unqualified status, and navigation.
- Published a [roadmap](../ROADMAP.md) with bounded stages and acceptance tests and an [architecture explanation](../architecture.md) distinguishing the planned EE/controller/host path from runtime evidence.
- Kept this engineering log separate from operating instructions; reduced `PROJECT_LEAD_INTRODUCTION.md` to a short pointer-based handoff. Validated runbooks will be published only when their operations have been exercised.
- **No application deployment or EE qualification occurred as part of this documentation work.** The shared engineering-standards amendment remains a proposed separate operation.

## 2026-10-17 — Standard managed-host connection chosen

- Nova explicitly chose Ansible's normal **smart/SSH** model, including SSH from a Kvin-based EE back into Kvin itself. This preserves the ability to run the same playbook from Peanut or against a replacement application host.
- Removed `ansible_connection: local` from `ansible/inventory/hosts.yml` on `main`. The SSH credential and rootless user-systemd execution paths still require a live EE-based test.
- Clarified the unrelated Python-version question: tests of **Python 3.12 and 3.14** came from Project Joule's separately documented application compatibility/CI matrix, not an Ansible requirement to install two interpreters globally on Kvin and Peanut. Joule's owning [ADR-0002](https://github.com/wdcallahan/joule/blob/main/docs/adr/0002-python-and-dependency-workflow.md) records that decision; it is not authority to introduce a project-local Ansible venv here.

## 2026-10-17 — Learning and continuity requirements made cross-project

- Nova reaffirmed that practical experience is gained by **using commands when they are actually needed**, not by memorizing unexplained switches inserted for hypothetical cases. Using `git -C` from the current repository is unnecessary; it is useful when invoking Git for a *different* directory. A repeated explanation of what a flag means does not answer why that flag was needed in the actual task.
- Nova explicitly chose ordinary `git pull` in his usual sequential workflow, accepting that genuine divergence, if it ever arises, will be diagnosed as a real learning event. The shared [Git standard](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md) was amended; no hidden `pull.ff only` configuration is authorized.
- The shared [Nova–Pixel interface standard](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md) was updated to preserve learning as a deliverable and require **in-session durable recording** of meaningful corrections to purpose, architecture, operator independence, and instructional practice. This project handoff now points to those rules.
- These are GitHub source/documentation updates only, not evidence of successful EE deployment, system changes, or user comprehension.

## 2026-10-18 — Navigator inspection, first live learning checkpoint

- On Kvin, Nova invoked the already-installed Sanctum Maintenance `ansible-navigator images --mode interactive`, without installing or creating another environment.
- The interactive Podman image list identified `sanctum-maintenance-ee:2026.07` as **Execution environment: True**, image size **468 MB**. Other local images (including Prism and SearXNG) were marked `False`, confirming Navigator lists ordinary container images alongside recognized EEs.
- This is **read-only discovery of an existing project-qualified EE**, not Nextcloud runtime acceptance or approval to reuse the Maintenance EE as a generic shared runtime.
- Nova is already familiar with Navigator's **stdout mode** for playbook execution. Interactive image inspection was selected specifically to explore an EE's contents; the next useful teaching step is inspecting the image details before choosing new tooling.

## How to extend this log

Add an entry only for a meaningful changed design, verified run, discovery, accepted decision or failed experiment. Include what was observed, what conclusion is justified, and links to commits/tests/receipts where useful. Keep everyday instructions in runbooks, plans in the roadmap, and transient command output in appropriate private evidence artifacts. Never make new users read this log before operating the system.
