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

**Transport decision:** Ordinary HTTP is a deliberate, accepted choice for the trusted private `.sanctum` network and may remain so; a universal HTTPS/private-CA initiative is **not commissioned**. The risk of unencrypted passwords, tokens and content on that HTTP path is understood, but any certificate and per-client trust overhead must be justified by a concrete application requirement or threat. Modern mobile apps and sealed devices may not support a user-installed private CA at all. The `.sanctum` namespace is deliberately chosen and not to be renamed for certificates. [The deferred HTTPS decision, including the worst-client test](https://github.com/wdcallahan/sanctum-services/issues/3) records the prior tradeoff rather than an active dependency.

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

## YXORP reconstruction and Kvin staging (November 10, 2026)

- [YXORP replacement runbook](docs/runbooks/yxorp-reconstruction.md), [declarative routes](data/yxorp-routes.yml) and [Nginx role](ansible/roles/yxorp/tasks/main.yml): rootful Nginx with host networking and normal HTTP `0.0.0.0:80`. The **Peanut-only trial passed** a Kvin same-client, same-Host **349-byte byte-identical HTTP200** Yarn content check, then was **removed** by its scoped Ansible cleanup. Peanut is an intended *future* standby, not a commissioned permanent proxy. Other routes and full user/session/WebSocket behavior remain unaccepted.
- **Kvin's rootful HTTP80 YXORP stage is installed and locally accepted for Yarn.** The stage deployed `ok=22 changed=5 failed=0`, and its independent native four-path diagnosis returned `ok=6 changed=0 failed=0`: local health 200, staged Yarn 200, direct Yarn hostname/IP 200 and exact response-body equality on both comparisons. The earlier origin timeout did not recur, cause unknown. Kvar NPM and wildcard DNS remain production. The stage code lives in [the Kvin playbook](ansible/yxorp-kvin-stage.yml), [independent route tests](ansible/yxorp-kvin-yarn-transport-diagnose.yml), and [reversal](ansible/yxorp-kvin-stage-remove.yml); the stage is not production and should remain for further acceptance.
- **Kvin's separate rootful YXORP stage has accepted four of eight routes for initial anonymous HTTP behavior:** Yarn HTTP200/response-body parity, Square HTTP302/incumbent Location and MIME parity, Prism HTTP200/status and MIME parity, and Search HTTP200/status and MIME parity from direct backend, Kvar NPM and Kvin stage. A [default-off fifth-route LinkStack stage canary](ansible/vars/yxorp-kvin-stage.yml) and [bounded observer](ansible/yxorp-kvin-stage-dir-probe.yml) compare only interim proxy routing to the **existing Kvar LinkStack backend :8081**; the retained application, data, credentials and eventual Kvin restore are **not** migrated by enabling this route. Kuma and Pi-hole also still have Kvar backends. No new Kvar, DNS, firewall or production authority is opened; Kvar NPM remains live, and the initial route manifest remains Yarn-only. Actual sessions/WebSockets/Calendar, Search results, remote clients, service restore and production cutover remain separate acceptance gates.
- The prior **Kvar NPM legacy Yarn timeout** was reproduced from both Kvar host and its NPM container, while Kvin reached the direct backend. A native Kvar/Kvin selected-route comparison showed the **same gateway `192.168.0.1`** for Yarn and Arcane control destinations, not a route-table divergence. Additional diagnosis of this obsolete Kvar-origin path is deferred unless an active consumer requires it; `yarn.inner.sanctum` remains recorded for explicit retirement review. See [Services #2](https://github.com/wdcallahan/sanctum-services/issues/2).
- **Mace → Arcane/Peanut direct access** has a separate A/B/A-verified Bunny Inner invalid-forward-drop rule issue ([Maintenance #36](https://github.com/wdcallahan/sanctum-maintenance/issues/36)). Router source repair belongs to Bunny Factory/Maintenance; Services must not add per-client static routes or conflate it with Kvar's Yarn timeout.
- [Declared Kuma monitors](data/kuma-monitors.yml) and [Kuma monitoring runbook](docs/runbooks/kuma-monitoring.md) preserve Project Joule's **Wicket Ollama** `http://wicket.arcane.sanctum:11435/healthz` requirement ([issue #4](https://github.com/wdcallahan/sanctum-services/issues/4)). Monitor reconciliation on the retained Kvin Kuma has not yet been natively accepted.

The [source CI](.github/workflows/yxorp-source-check.yml) checks Ansible syntax, authorization and desired-state contracts, generated Nginx syntax, and synthetic HTTP behavior. **CI is not live service or disaster-recovery acceptance.**
