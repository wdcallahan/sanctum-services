# Sanctum Services

**Repeatable self-hosted applications, built to be understood and maintained.**

Sanctum Services is the application-deployment project for the Sanctum home lab. Its intended, still-being-qualified workflow uses **Ansible Navigator, containerized Ansible execution environments, and Podman Quadlets (rootless or rootful according to each service's actual needs)** to make services reproducible and operable without relying on a particular assistant or undocumented shell history.

The first application is **Nextcloud**. The estate also includes the planned reconstruction of YXORP, LinkStack, Uptime Kuma and Pi-hole, and the future Sanctum VPN, Luanti and Home Assistant work. We build these systems for two outcomes: useful services **and** real hands-on engineering experience.

> **Current status — 2026-11-08:** Nextcloud's Calendar 6.6.2 is installed with accepted bidirectional GNOME Calendar access. Maintenance's Kvin TCP 8085 firewall correction was authorized, applied and independently verified October 20; any older pre-approval statements are historical. Nextcloud's complete backup/restore and lifecycle and protected proxy access remain to be qualified. [The authoritative service estate and settled keep/retire decisions](docs/SERVICE-ESTATE.md) cover both Services-owned containers and other project owners. [Services #2](https://github.com/wdcallahan/sanctum-services/issues/2) tracks reconstructible YXORP and the full container audit.

## Start here

| If you want to… | Read… |
| --- | --- |
| Understand our destination and current milestone | [Project roadmap](docs/ROADMAP.md) |
| See all intended, retired, externally owned and planned services | [Service estate / decision register](docs/SERVICE-ESTATE.md) |
| Understand hosts, data paths, EEs, and component ownership | [Architecture](docs/architecture.md) |
| Understand application automation and host-firewall prerequisites | [Ansible deployment and owner order](ansible/README.md) |
| Review what changed and what actually happened | [Engineering log](docs/history/engineering-log.md) |
| Resume an interrupted assistant-led engineering session | [Short lead handoff](PROJECT_LEAD_INTRODUCTION.md) |

As operations are developed and tested, the supported **installation, everyday operation, backup/restore, update, and uninstall runbooks** will be published under `docs/runbooks/`. No untested command should be represented as a supported operating procedure.

## Sanctum's operating rule

**So let it be written, so let it be run.** Source control and owning Ansible automation define repeatable configuration changes; manual UI/host edits are temporary interventions to reconcile into the durable declared source, not the normal administrative method. Fresh-host reconstruction must work from owning automation and declared persistent data/secrets, including across application and infrastructure owners. This project follows the [cross-project Operational Project Completion Standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md), rather than creating another standard.

**Right tool and privilege for the job.** Rootless containers are useful for unprivileged application workloads; rootful services are accepted when appropriate, including a reverse proxy binding host ports 80/443. SSH is a native host service and need not be containerized. Services is not taking over network/firewall policy; it coordinates with its owners rather than layering arbitrary proxy authentication or rootless workarounds onto the design.

**Trusted HTTPS is unresolved, not optional forever.** Public certificate authorities will not issue for the private `.sanctum` names. An internal CA is possible but requires trust distribution to all relevant devices, including VPN users, and ongoing key/certificate lifecycle. A publicly trusted domain with private DNS/routing is another design avenue if naming changes are acceptable. Do not select a trust strategy, enable TLS, or alter client trust as a side effect of replacing YXORP; [track the HTTPS decision in issue #3](https://github.com/wdcallahan/sanctum-services/issues/3) separately.

## Our definition of useful software

A service has no initial value merely because it starts. It must be:

- **Documented:** understandable instructions aimed at a human administrator.
- **Repeatable:** reproducible from its owning automation and declared durable inputs.
- **Understandable:** its owner can explain, run, change, and diagnose it, and practices the technologies the project was intended to teach.
- **Uninstallable:** application-owned resources can be removed cleanly, with user data either deliberately retained or explicitly purged under a separate, safe procedure.

We measure progress through demonstrated operating outcomes, not source-code volume or passing tests alone.

## Initial Nextcloud pilot — container running, installer pending

- **Compute:** Kvin (ARM64), rootless Podman; host port 8085 is the chosen initial mapping to Nextcloud Apache port 80.
- **User-facing name:** `square.nexus.sanctum`; initial pilot route is HTTP via YXORP, not yet accepted; TLS requires a separate later decision.
- **Database:** existing Sanctum PostgreSQL, with Nextcloud's own role/database provisioned by its owner and a qualified client SCRAM path.
- **Files:** Kvin NVMe, about **50 GiB soft budget** for the learning period; separately restorable copies planned on Peanut. Void is the intended later long-term file-storage location.
- **Automation runtime:** centrally managed Navigator/EE workflow on the Kvin and Peanut controllers; actual runtime ownership and qualified image to be selected.

Those facts and decisions may evolve. The [roadmap](docs/ROADMAP.md) identifies open choices and acceptance tests; the [architecture page](docs/architecture.md) distinguishes intended flow from deployed state.

## Project boundaries

This repo owns applications and their supported lifecycle. The Sanctum registry owns canonical network facts; Sanctum Maintenance owns host/OS maintenance; Maintenance and the other infrastructure projects own PostgreSQL and shared controller facilities; Services now tracks reproducible YXORP installation and desired routes under [issue #2](https://github.com/wdcallahan/sanctum-services/issues/2), with any incumbent proxy operations coordinated before mutation. We consume their supported interfaces instead of silently replacing them.

The source is developed on linear `main`, with no default branch/PR workflow. The original project material is licensed under the **GNU General Public License, version 3 or later**; see [LICENSE](LICENSE).

## Approved third-party applications

[Application manifest](ansible/nextcloud-apps.yml) ·
[App-only playbook](ansible/apps.yml) ·
[App management and reconstruction runbook](docs/runbooks/nextcloud-apps.md)

The October 20 app management source is **not yet natively qualified**. Its
manifest now pins Calendar 6.6.2 (reviewed release archive and SHA-256); no
third-party app has been deployed through it yet. The normal site playbook
reconciles approved apps only after the web installer completes. Unlisted apps
are preserved, not silently uninstalled. No current test uploads are treated
as irreplaceable data; eventual data recovery is a separate qualification.
