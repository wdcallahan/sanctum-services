# Sanctum service estate — ownership, disposition, and reconstruction

## November 10 correction — preserve existing Yarn NPM proxy host in the reconstruction baseline

The existing Kvar NPM `yarn.inner.sanctum` proxy-host 11 is
**part of the incumbent application's proxy inventory**.
Services must rebuild the incumbent application routes
under plain Nginx on Kvin, not invent a keep-or-retire
decision about the corresponding ordinary DNS hostname.
The earlier suggestion to omit NPM virtual host 11 because
Maintenance DNS directly resolves `yarn.inner.sanctum`
to the Yarn origin was an **unsupported recommendation,
now withdrawn**. DNS naming and proxy vhost migration are
independent concerns.

The original NPM review observed eight proxy-host
configurations: seven application routes plus the NPM
management UI `yxorp.nexus.sanctum`. The management UI
is intentionally not reproduced because the replacement
is plain Nginx. The new requested `yarn.nexus.sanctum`
is separately added, so the Services manifest has eight
app-route entries. The old `yarn.inner.sanctum` entry
stays present and default-off in Kvin **staging only**
until an explicit bounded test; this flag is not a
retirement signal.

Kvar NPM's recent old-Yarn access log had six
records from two source addresses:
Kvin `192.168.0.192` (three)
and Inner NAT egress `192.168.0.104` (three).
Nova confirmed the latter is `hop.inner.sanctum`
and could represent requests from any client behind
Inner. Retrospective identification needs request
timestamps correlated with retained Inner NAT/session
records and may be impossible if those were not
logged. The recorded Kvar-to-Yarn transport failure,
despite Kvin reaching the same origin, needs
no new deprecation decision.

No DNS, Kvar NPM, Kvin proxy stage, firewalld
or cutover changed under this correction.
Seven initial local HTTP stage routes remain
accepted; eighth pending qualification. Kvar
app/data restores and Kvar eventual retirement
remain separately gated.

## Settled operating intentions (Nova, November 8)

- **Kvin and Peanut are deliberately matched Pi 5 service-host twins:** Same
  processor and substantially the same capabilities; their storage size
  difference was incidental, not a functional split. Peanut is Kvin's
  second host for redundant services (such as DNS1/DNS2), backups,
  failover and hot spares. The eventual YXORP network proxy on Kvin
  should have a Peanut counterpart capable of assuming reverse-proxy
  service if Kvin is lost. **Failover publication/control and verified
  automatic or manual promotion are not currently implemented.** Peanut's
  2026-11-09 rootful HTTP:80 trial tests the real candidate and must
  remain distinguished from permanent failover readiness.
- **Kvin's longstanding role:** Kvin was acquired years ago to take over Kvar's service-host duties. Moving the intended survivors is fulfillment of that existing design, not a new destination decision. The actual migration remains subject to evidence, restore testing, and independent operator authorization.
- **Pi-hole: RETAIN for ad blocking.** It is **not** the general/authoritative Sanctum DNS service or the DHCP-advertised network resolver. It still serves ad filtering, including whatever DNS-filtering interface its clients use. Record current clients and the future host; do **not** reinterpret absence of general DNS duties as permission to retire Pi-hole. Peanut provides the verified general DHCP DNS path per Maintenance's current observations.
- **OpenWebUI: RETIRED in favor of Prism.** **Endlessh: RETIRED.** Its former SSH-tarpit role was relevant when a host had a public-facing SSH entry point; that rationale no longer applies. Neither is in the intended reconstruction set. There is **no requirement to uninstall each retired container from Kvar**. Kvar remains unchanged until all wanted services are restored and accepted on Kvin; then Kvar is taken offline and reformatted as a separate approved host-retirement action.
- **Access policy:** No intended publicly exposed inbound service ports. Tailscale is the current **stopgap** for private remote access. A properly integrated Sanctum VPN is a future **Services** project, coordinated with Bunny Factory/network routing, Maintenance/firewall/host work, DNS, and clients. Protocol, placement, trust policy, migration and client behavior have **not** yet been selected. Do not disable working Tailscale until a qualified replacement exists.
- **Planned applications:** **Luanti** and **Home Assistant** are explicit future Services projects, alongside further applications Nova may nominate. Neither is implied to be currently deployed or ready for implementation.
- **Cross-project inventory:** Include containers not installed by Services, prominently **Prism**, which is **owned by Project Joule**. A whole-estate rebuild inventory cannot exclude an application simply because its own project is the installer.
- **Configuration doctrine:** "So let it be written, so let it be run." Every recurring configuration change belongs in its owning Ansible/source contract. A hand-edited proxy route or BIND zone is an operational exception to reconcile into source, not a new unmanaged state. Preserve documented, reviewable and reversible changes using the [existing shared completion standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md). Rootless/rootful and container/native are selected by the service's actual requirements—not by a blanket policy. Network security belongs to its actual infrastructure owners; application-specific authentication belongs to applications.
- **HTTP/TLS security tradeoff (settled unless concrete requirements change):** **HTTP is accepted, potentially indefinitely**, for ordinary trusted private `.sanctum` applications. Plaintext credentials, tokens and content are a conscious risk, not an assertion that HTTP encrypts anything. There is **no current initiative to enforce private HTTPS or a local CA**: client trust is often costly or impossible (e.g., locked-down Android apps with no support for user CAs). The `.sanctum` private namespace is a deliberate permanent choice and is not to be renamed as a certificate workaround. [Services issue #3](https://github.com/wdcallahan/sanctum-services/issues/3) is closed/not planned to preserve this decision. Revisit only for a concrete app/feature/security need and after checking its hardest client.
- **Kvar exit criterion:** Restore and verify every wanted service, its state, name-based client access and necessary dependencies on Kvin (or the approved owning host). Once this is accepted, remove Kvar from service, **take it offline, and format/reimage it** under Maintenance's host-retirement procedure. Do not make per-container uninstallation, disabling retired services on Kvar, or historical-data housekeeping a prerequisite to this plan. Formatting is deliberate destructive work needing a separate operator-approved cutover/reimage, not authorized by this inventory.

## Intended / observed services

Status below combines the November 8 Maintenance [Kvar inventory](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-11-08-kvar-retirement-inventory.md) with November 8 operator decisions and available tracked source. **Observed running** and **approved to retain** are separate concepts. Installer presence is a source audit only, not clean-host recovery proof.

| Service | Last source/observation | Lifecycle owner and source | Desired disposition / missing proof |
| --- | --- | --- | --- |
| **YXORP / reverse proxy** | **Production:** Kvin rootful, source-managed plain Nginx Podman Quadlet, real port 80; Peanut authoritative DNS six Nexus aliases now direct to Kvin. Kvar NPM remains unchanged as fallback. | **Sanctum Services**: `ansible/yxorp.yml`, `ansible/roles/yxorp`, `data/yxorp-routes.yml` (source projection enables eight vhosts). | **Active and serving named production clients.** Kuma named authenticated browser and WebSocket 101 accepted November 11; LinkStack named directory/login accepted November 12. Other app-specific browser routes and recovery are not implicitly accepted. Existing Yarn smoke test could time out even after a successful deploy; source corrected in `eba1dfcb` so it reports degradation without aborting another route's deployment. No replacement NPM UI or blanket HTTPS needed. |
| **LinkStack** | **Live on Kvin:** rootless `sanctum-linkstack-kvin-candidate.service` with restored owned volume, internal port `127.0.0.1:18081`; served by Kvin production YXORP at `dir.nexus.sanctum`. Kvar rootless `linkstack` port 8081 and original volume still running as fallback. | **Services**: `ansible/files/sanctum-linkstack-kvin-candidate.container`, `ansible/linkstack-kvin-loopback-stage.yml`, and YXORP production `dir` upstream in `ansible/yxorp.yml`; existing recovery and snapshot scripts. | **Production public directory and admin sign-in ACCEPTED in normal Firefox November 12.** No more isolation/proxy-form tests or LinkStack deployment reruns are needed; old Kvar retained until host retirement. Live Kvin edits do not sync back to Kvar. |
| **Uptime Kuma** | Old Kvar rootless:3001 remains as fallback. New Kvin rootless:13001 has Vault-backed administrator, `Wicket Ollama` Up, tested isolated backup/restore, and named production authentication plus browser WebSocket 101. | **Services** owns source-managed Kvin deploy, state/monitor reconciliation, and its YXORP route. | **Kvin real browser route and authenticated WebSocket accepted November 11.** Independent Peanut monitoring peer and off-host recovery remain outstanding; the Kvar fallback is not the permanent second monitor. |
| **Pi-hole** | **Kvar incumbent still serving DNS53/web82.** Both its original volumes were consistently backed up, transferred and successfully **imported into two permanent rootful Kvin volumes** November 12 (`ok=10 changed=3 failed=0`). | **Services** owns `ansible/pihole-consistent-backup.yml`, `ansible/pihole-kvin-restore.yml` (both natively accepted), and new `ansible/pihole-kvin-deploy.yml` + pinned ARM64 rootful Quadlet (source only pending CI/native deployment). | **Next start Kvin Pi-hole on ordinary Kvin LAN DNS53 and web82**, then retarget its existing YXORP UI route and test actual filtering clients. Kvar Pi-hole untouched until Kvin is accepted. Pi-hole does not replace Sanctum authoritative DNS. |
| **Search / EyesOnly SearXNG** | Rootless Search observed on both Kvar and Kvin; images matched but persistent backing differed | [EyesOnly SearXNG](https://github.com/wdcallahan/eyesonly-searxng/blob/main/ansible/site.yml) has an Ansible deploy role; coordinate its project ownership | **Keep Kvin instance**. Validate effective configuration/theme, data/backup and named client route; no duplicate deployment or presumed equivalent contents |
| **Nextcloud / Town Square** | Kvin rootless; Calendar 6.6.2 installed and bidirectional GNOME Calendar access accepted October 21 | [Sanctum Services application play](../ansible/site.yml) | **Keep**. Full recovery, protected proxy access, uninstallation and complete operational lifecycle still need qualification |
| **Prism** | Kvin-facing Joule browser service | **Project Joule owns Prism's container, application deployment and recovery.** Its [Kvin deployment source](https://github.com/wdcallahan/joule/tree/main/deploy/kvin) is separate. Services owns only its shared proxy route and estate dependency accounting | **Keep.** Must appear in whole-estate inventory even though Services must not duplicate or override the Joule installer. Obtain Joule's own restore acceptance |
| **PostgreSQL (shared)** | Existing Kvin rootless service and named endpoint | **Sanctum Maintenance** owns PostgreSQL service lifecycle; service clients own their respective database/application data | **Keep.** Restore sequence and credentials/data coordination are prerequisites to app recovery; Services must not recreate conflicting PostgreSQL ownership |
| **Joule host-side services** | Wicket and any Project Joule standby components; not comprehensively inventoried in this pass | **Project Joule**, with its own deployment and recovery contracts | **Include in eventual estate-wide audit by owner handoff**, not as a claim that Services operates them |

## Explicitly excluded from intended rebuild

| Container | Decision | Safety boundary |
| --- | --- | --- |
| **OpenWebUI** | **Retired**, superseded by Prism | Leave legacy instance alone; do not rebuild it on Kvin. No per-container uninstall required before Kvar is retired and reformatted |
| **Endlessh** | **Retired**, former SSH tarpit no longer required | No reconstruction and no per-container uninstall required on Kvar. Leave legitimate Kvar management SSH intact until decommissioning |
| **Obsolete LinkStack rootful duplicate, AWX, Dashy, Wiki.js, Homarr** | Historical/failed/removed candidates according to Maintenance inventory; **not** inferred intended services | Reconcile evidence before treating any unknown current component as disposable |

## Future Services backlog (not deployed by this register)

- **Proper Sanctum VPN:** replace the temporary Tailscale arrangement only after a private-access topology, authentication, routing, firewall, DNS, recovery and client migration are designed and qualified with owning projects. Preserve no-public-inbound-ports intent.
- **Luanti:** new managed application, requiring ordinary Services install/backup/restore/update/uninstall contract.
- **Home Assistant:** new managed application, requiring the same contract and explicit hardware/network integration design.
- **Other future applications:** add to this register and roadmap as Nova selects them; no implicit approvals.

## What a reconstructible service requires

For every intended service, record: real owner; current and intended host; playbook/role/Quadlet; image selection and dependencies; network/ports/routes; persistent mounts; secret/certificate custody; backup and restore inputs; rebuild entry point; idempotent repeat; client acceptance; uninstall/retain-data behavior. Mark source-known, natively deployed, repeat-converged, restored and safely uninstallable **separately**. Unknown must remain unknown.

**Configuration discipline:** A manual UI or host change is not the finished desired state. Reconcile that change into the owning Git-managed configuration or a defined durable/restorable state in the same operational workflow, as with Maintenance's `data/dns.yml`. Snapshots of proxy database state alone do not replace an installer, desired route list, or restore proof.

**Immediate active work:** [Services #2](https://github.com/wdcallahan/sanctum-services/issues/2) owns plain-Nginx YXORP reproducible deployment, route-list reconciliation (including `yarn.nexus.sanctum`), and the comprehensive audit. Maintenance's [Kvar inventory](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-11-08-kvar-retirement-inventory.md) is evidence of existing containers and mounts; its older unresolved Pi-hole/OpenWebUI/Endlessh wording is superseded by the operator decisions recorded here. Maintenance owns edits to that document; Services sends the correction through the board.

No changes to live hosts, routers, firewall, DNS, client VPN, containers, credentials, or persistent data are authorized by this record. Kvar offline/reformat is an agreed **end state**, not a command to do so before accepted Kvin recovery and a separate cutover authorization.

## Newly received service handoff — Wicket Ollama monitoring

Project Joule requested a retained Kuma HTTP monitor named **Wicket Ollama**,
URL `http://wicket.arcane.sanctum:11435/healthz`; the accepted monitor must
show **Up** in the chosen managed Kuma instance. The exact desired record is
in [`data/kuma-monitors.yml`](../data/kuma-monitors.yml), with installation
and idempotent reconciliation held until Kvin Kuma is accepted; see
[Services #4](https://github.com/wdcallahan/sanctum-services/issues/4).

The [initial YXORP staging source](../ansible/yxorp.yml) and
[route data](../data/yxorp-routes.yml) have been committed, not deployed:
only Yarn is currently enabled in the draft. Kvar NPM remains the incumbent.
See the [YXORP reconstruction runbook](runbooks/yxorp-reconstruction.md).

## November 9 YXORP default-route observation

Nova ran the repository's read-only comparison using Maintenance's retained
November 8 report from Kvin. **Eight** NPM generated default proxy hosts were
observed; **five existing declared** YXORP hosts matched exactly, with no
upstream disagreements. The previously unqualified `pihole.nexus.sanctum`
UI default upstream is `http://kvar.outer.sanctum:82`; the already-running
`yarn.inner.sanctum` NPM route points to `http://192.168.1.110:80`.
The old NPM UI `yxorp.nexus.sanctum` points at Kvar port 81 and is
**intentionally not rebuilt**. The new `yarn.nexus.sanctum` name remains a
separately requested route not already served by NPM.

The [full bounded route review](review/2026-11-09-yxorp-default-route-comparison.md)
records these eight observed upstreams and the limitations. Generated default
routes alone **do not establish** custom headers, redirects, paths, WebSocket
behavior or client acceptance. This is a source-only report reconciliation:
no service listener, DNS or proxy was changed.

## November 9 NPM generated-host behavior inspection

Nova ran the Services read-only Kvar observer. Eight NPM proxy-host files
were read without changes. The generated config explicitly declares
WebSocket Upgrade/Connection headers for Square (Nextcloud) and Joule (Prism),
Prism alone carries TLS certificate/listen directives, and all files have
one location with no extra locations. No generated redirect/stream hosts or
nonempty global custom snippets were observed. The recurring generated
include references and unclassified lines remain unexpanded; no complete
proxy behavior equivalence or client acceptance is claimed. Details:
[2026-11-09 YXORP behavior observation](review/2026-11-09-yxorp-behavior-observation.md).
