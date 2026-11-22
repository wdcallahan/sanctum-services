# Sanctum Services

**Repeatable self-hosted applications, built to be understood and maintained.**

Sanctum Services is the application-deployment project for the Sanctum home lab. Its intended, still-being-qualified workflow uses **Ansible Navigator, containerized Ansible execution environments, and Podman Quadlets (rootless or rootful according to each service's actual needs)** to make services reproducible and operable without relying on a particular assistant or undocumented shell history.

**For a new Pixel session:** start with [AGENTS.md](AGENTS.md) and the
[lead handoff](PROJECT_LEAD_INTRODUCTION.md) before changing source or
proposing an operator command. The active
[whole-Sanctum audit (Maintenance #38)](https://github.com/wdcallahan/sanctum-maintenance/issues/38)
records established decisions that a new session must not reverse.

The first application is **Nextcloud**. The active estate also includes **YXORP, LinkStack, Uptime Kuma and EyesOnly** (Search is owned by its own project); **Pi-hole is retired**. The [future-services section of the estate register](docs/SERVICE-ESTATE.md#future-services-backlog-not-deployed-by-this-register) records three explicit plans—**Sanctum VPN, Luanti and Home Assistant**—and keeps earlier brainstorming candidates clearly marked **uncommitted** rather than manufacturing installation tasks. We build for useful services **and** real hands-on engineering experience.

> **Current status — November 17, 2026:** Kvar remains unplugged;
> seven-route Kvin YXORP, Kuma, LinkStack, EyesOnly Search and Nextcloud
> with Calendar 6.6.2 are usable; Pi-hole, OpenWebUI and Endlessh remain
> retired from desired state. YXORP, Kuma and LinkStack have native
> accepted moving-image update policies. **Nextcloud now has a real
> enabled weekly user timer (Sunday 03:30) AND a natively accepted
> successful execution of its installed backup one-shot.** That
> supervised service run created a **new `nextcloud-20261117t134454`
> consistent Kvin recovery point** and independently verified its
> complete four-member recovery copy + matching manifest on Peanut.
> Nextcloud returned to normal. **Natural Sunday timer firing not yet
> observed**; backups not auto-pruned.
>
> **November 21:** [Full independent Nextcloud recovery ACCEPTED](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7074839767):
> filesystem, 137 restored database tables, Nextcloud 34.0.5.1 and Calendar
> 6.6.2 CLI, recovered account authentication, actual file read, and two calendar
> events. Production untouched; old pinned-image command is withdrawn.
> Production remains 34.0.5.1 until protected live update acceptance.
> Next run the backup-gated moving-channel maintenance cycle, then enable
> the daily updater. No repeat of the accepted recovery stages.
>
> See the [lead handoff](PROJECT_LEAD_INTRODUCTION.md),
> [roadmap](docs/ROADMAP.md) and
> [Nextcloud recovery runbook](docs/runbooks/nextcloud-instance-recovery.md).
> Later dated sections preserve history, not new tasks.

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

## Original Nextcloud pilot — historical deployment design

- **Compute:** Kvin (ARM64), rootless Podman; host port 8085 is the chosen initial mapping to Nextcloud Apache port 80.
- **User-facing name:** `square.nexus.sanctum` over deliberately accepted private-network HTTP; current production YXORP is on Kvin. No blanket HTTPS/CA project is required.
- **Database:** existing Maintenance-owned shared Sanctum PostgreSQL with Nextcloud's own database and working authenticated application connection. A supported **Nextcloud-only backup/export interface** is still pending.
- **Files:** Kvin NVMe, about **50 GiB soft budget** for the learning period; separately restorable copies planned on Peanut. Void is the intended later long-term file-storage location.
- **Automation runtime:** Maintenance's shared Navigator/EE on Kvin/Peanut is in use and its Services consumer was accepted October 23; a separately built general-purpose EE remains a distinct workstream.

Those facts and decisions may evolve. The [roadmap](docs/ROADMAP.md) identifies open choices and acceptance tests; the [architecture page](docs/architecture.md) distinguishes intended flow from deployed state.

## Project boundaries

This repo owns applications and their supported lifecycle. The Sanctum registry owns canonical network facts; Sanctum Maintenance owns host/OS maintenance; Maintenance and the other infrastructure projects own PostgreSQL and shared controller facilities; Services now tracks reproducible YXORP installation and desired routes under [issue #2](https://github.com/wdcallahan/sanctum-services/issues/2), with any incumbent proxy operations coordinated before mutation. We consume their supported interfaces instead of silently replacing them.

The source is developed on linear `main`, with no default branch/PR workflow. The original project material is licensed under the **GNU General Public License, version 3 or later**; see [LICENSE](LICENSE).

## Approved third-party applications

[Application manifest](ansible/nextcloud-apps.yml) ·
[App-only playbook](ansible/apps.yml) ·
[App management and reconstruction runbook](docs/runbooks/nextcloud-apps.md)

**Calendar 6.6.2 was installed and accepted in normal bidirectional GNOME Calendar use on October 21**, with the repeat application reconciliation accepted. Its version is pinned in the application manifest. Unlisted apps are preserved, not silently uninstalled. The dated October 20 exploratory-data statement is **not current permission to discard user data**. Full instance backup and restore remain the active recovery milestone.

## YXORP reconstruction and Kvin staging (historical November 10 evidence)

- [YXORP replacement runbook](docs/runbooks/yxorp-reconstruction.md), [declarative routes](data/yxorp-routes.yml) and [Nginx role](ansible/roles/yxorp/tasks/main.yml): rootful Nginx with host networking and normal HTTP `0.0.0.0:80`. The **Peanut-only trial passed** a Kvin same-client, same-Host **349-byte byte-identical HTTP200** Yarn content check, then was **removed** by its scoped Ansible cleanup. Peanut is an intended *future* standby, not a commissioned permanent proxy. Other routes and full user/session/WebSocket behavior remain unaccepted.
- **Kvin's rootful HTTP80 YXORP stage is installed and locally accepted for Yarn.** The stage deployed `ok=22 changed=5 failed=0`, and its independent native four-path diagnosis returned `ok=6 changed=0 failed=0`: local health 200, staged Yarn 200, direct Yarn hostname/IP 200 and exact response-body equality on both comparisons. The earlier origin timeout did not recur, cause unknown. Kvar NPM and wildcard DNS remain production. The stage code lives in [the Kvin playbook](ansible/yxorp-kvin-stage.yml), [independent route tests](ansible/yxorp-kvin-yarn-transport-diagnose.yml), and [reversal](ansible/yxorp-kvin-stage-remove.yml); the stage is not production and should remain for further acceptance.
- **Kvin's isolated YXORP stage has seven of eight app-route names locally HTTP-qualified.** The goal is to reproduce the existing **application** proxy hosts from Kvar NPM as plain Nginx on Kvin, plus the separately requested new `yarn.nexus.sanctum` name; only the replaced NPM management UI is intentionally excluded. The eighth `yarn.inner.sanctum` is **an existing NPM proxy-host that remains in the target migration inventory** and is currently disabled in Kvin *staging only pending its own test*. Earlier consideration of dropping that vhost because Maintenance DNS already points the hostname at Yarn was an error: DNS and incumbent proxy configuration are distinct. Kvar NPM host 11 logged six recent requests, three from Kvin `192.168.0.192` and three from Inner NAT egress `192.168.0.104` (`hop.inner.sanctum`); behind the latter may be any Inner clients, not identifiable from a PTR lookup. Identifying original clients requires retained Inner session/NAT data at the logged request times, if available. The old Kvar host and NPM container transport to Yarn timed out, whereas direct/new-stage Kvin reached it; this is migration evidence, not proof the configured old proxy host is unwanted. [YXORP runbook](docs/runbooks/yxorp-reconstruction.md) and [route inventory](data/yxorp-routes.yml) preserve the migration baseline. Kvar NPM, DNS, firewalld and production cutover remain unchanged; Kvar LinkStack/Kuma/Pi-hole app and retained data must still migrate to Kvin.
- The prior **Kvar NPM legacy Yarn timeout** was reproduced from both Kvar host and its NPM container, while Kvin reached the direct backend. A native Kvar/Kvin selected-route comparison showed the **same gateway `192.168.0.1`** for Yarn and Arcane control destinations, not a route-table divergence. Additional diagnosis of this obsolete Kvar-origin path is deferred unless an active consumer requires it; `yarn.inner.sanctum` remains recorded for explicit retirement review. See [Services #2](https://github.com/wdcallahan/sanctum-services/issues/2).
- **Mace → Arcane/Peanut direct access** has a separate A/B/A-verified Bunny Inner invalid-forward-drop rule issue ([Maintenance #36](https://github.com/wdcallahan/sanctum-maintenance/issues/36)). Router source repair belongs to Bunny Factory/Maintenance; Services must not add per-client static routes or conflate it with Kvar's Yarn timeout.
- [Declared Kuma monitors](data/kuma-monitors.yml) and [Kuma monitoring runbook](docs/runbooks/kuma-monitoring.md) now have **native accepted** Kvin `Wicket Ollama` actual **Up**, an unchanged monitor repeat and a successful isolated offline restored-application trial. The Kvar legacy Kuma remains a migration fallback. The intended long-term two-bear monitoring peers are **Kvin and Peanut**; Peanut's Kuma is not yet deployed. [Production YXORP release](docs/runbooks/yxorp-production-cutover.md) is source CI-qualified but not live; Maintenance's firewall/DNS work remains pending.

The [source CI](.github/workflows/yxorp-source-check.yml) checks Ansible syntax, authorization and desired-state contracts, generated Nginx syntax, and synthetic HTTP behavior. **CI is not live service or disaster-recovery acceptance.**
