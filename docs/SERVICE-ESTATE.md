# Sanctum service estate — ownership, disposition, and reconstruction

## November 12 — Production YXORP projection updated to omit retired Pi-hole

**Source only, not yet native:** The existing production `ansible/yxorp.yml` historically asserted, projected and health-checked eight routes including Pi-hole. It now uses seven wanted application routes; it preserves the old disabled Pi-hole route only in staging provenance. This removes the accidentally required runtime dependency on the retired Pi-hole and lets a fresh YXORP rebuild run without Pi-hole. Host application and proxy configuration unchanged until the separately approved production play is applied; other seven routes remain unchanged by the intended projection. Once the normal YXORP role has reconciled, Kvin's old Pi-hole Quadlet remains optional leftover cleanup, not a required service or a Kvar exit gate. Real next survivor is Search / EyesOnly on Kvin.

## Current November 12 decision — Pi-hole RETIRED from Sanctum's wanted services

**Nova explicitly removed Pi-hole from the future service estate.** Peanut/BIND now supplies Sanctum client DNS, and the already accepted November 9 post-swap audit closed Pi-hole client discovery. Pi-hole does not provide ad blocking without being part of the DNS request path. **No replacement ad-blocking service or DNS policy is commissioned by this decision.** No Pi-hole migration, DNS-filter testing, client-discovery rerun, replica, monitoring, or ongoing backup-refresh tasks remain on the Services roadmap. If desired in the future, Pi-hole can be installed again as a newly requested service.

**Project-state boundary:** The successful restore and November 12 Kvin rootful Quadlet/service and `pihole.nexus.sanctum` production YXORP route are historical *deployed* state, **not desired retention**. They have not been stopped, removed, or modified by this source decision. Kvar's original Pi-hole remains untouched pending whole-host retirement; the Kvin instance and proxy vhost can be retired through ordinary targeted application cleanup, separate from the rest of the Kvar migration. Do not schedule a Pi-hole-only migration/retirement project or make stopping its legacy containers a condition for completing unrelated Services tasks. Earlier "RETAIN Pi-hole" plans and pending filtering qualification elsewhere in this file are superseded by this section.


## November 12 — Pi-hole client-discovery was already CLOSED November 9; do not reopen it

**Verified prior accepted Maintenance evidence, not a future task:** The [November 8–9 Kvar retirement handoff](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-11-08-kvar-retirement-inventory.md) records the native `pihole-postswap` run, source `eed2bbee9143`, **`Kvar ok=3 changed=0`**, with **zero recorded Pi-hole queries and client source addresses** between the November 7 22:25:07 UTC DHCP transition preview and the November 9 02:07 UTC observation. Nova explicitly stated that no device should still use Pi-hole and **declined discovery or preservation of stale dormant-client pins**. The Maintenance handoff says **"This closes the Pi-hole client-discovery gate; do not repeat the query or make dormant-client continuity a retirement prerequisite."** The verified post-swap core DHCPv4 scopes advertise **Peanut `192.168.3.3`** as the only managed BIND resolver. Old Kvar Pi-hole at `192.168.1.7` is not an intended active resolver.

**Lead correction:** The Services suggestion to "identify anything still relying on Pi-hole" after that acceptance was a **regression**, not diligence. It incorrectly reopened an already completed migration requirement and contradicted Nova's explicit decision. If a genuine stale Pi-hole dependency is independently discovered in normal operations, classify it as a DNS cutover defect; do not assume hidden consumers exist and invent a new survey. Do not block Pi-hole retirement on dormant-client speculation. Whether to maintain **any** network-wide ad blocking now depends only on Nova's current behavior goals; the previous assistant promises that Pi-hole would filter outside the DNS path were incorrect. No further Pi-hole client audit is authorized by this note, and no live Pi-hole service is stopped by it.


## November 12 — Correct planning error about Pi-hole and advertisement goals

**Assistant/project lead correction (not an operator error):** Sanctum spent a long time planning to migrate its *actual client DNS service* from Pi-hole to Peanut/BIND and completed the cutover roughly a week and a half before November 12. During planning, cutover, and subsequent work, the assistant repeatedly claimed Pi-hole would continue blocking ads as an independent service once Peanut became the clients' resolver. That was **technically incorrect**. Pi-hole's blocking is DNS-answer filtering: unless clients or a forwarding DNS server continue asking Pi-hole, moving client DNS to Peanut **removes Pi-hole from their filtering path**. This design consequence should have been identified before the cutover and before investing effort in restoring the Pi-hole application. Do not frame this as Nova misunderstanding what was promised.

**Operator's actual content policy:** Nova does *not* aim to block all legitimate or clearly labeled advertisements (including an ordinary video commercial). The unwanted behavior is intrusive, deceptive, misleadingly search-result-like, or content-obstructing advertising—e.g. overlays or fake content/download links. DNS filtering with Pi-hole or native BIND RPZ operates on hostnames, **not** the presentation or ethics of a given advertisement. Neither can distinguish acceptable and unacceptable advertising on the same origin. Some click-through advertising/tracking hosts can be blocked by DNS, but that is incidental to the domain and not a contextual judgment. A browser-level content blocker can make more selective request/page-element decisions, but common default lists will block legitimate ads too; evaluate opt-ins/rules according to this preference, not assume blanket blocking.

**Change to previous recommendation:** The prior "BIND RPZ plus endpoint filtering" proposal was **premature** given the objective. Do **not** start a network-wide RPZ deployment automatically, and do not declare Pi-hole retirement completed or disable either instance based solely on this conversation. The completed November 9 Maintenance audit already closed Pi-hole client discovery: no further legacy DNS-client check is needed. Keep the successful Kvin Pi-hole recovery/backup as working evidence while the *need for any domain-wide blocking* is decided. Maintenance owns any later changes to Peanut's BIND. Treat selective browser behavior as a distinct possible solution and avoid adding interception/proxy complexity. Project remains open for its other service recovery and Kvar retirement work.


## November 12 — Pi-hole retention reconsidered; use existing Peanut DNS for blocking

**New operator direction:** Nova says Sanctum will **not return to advertising Pi-hole as a client DNS server** and questions whether its original "retain for ad blocking" decision still serves a purpose. Actual Pi-hole behavior: this is a DNS filtering resolver, **not** a transparent network filter. Without direct clients or a resolver forwarding queries to it, it provides **no network ad filtering**. The completed restored Kvin service and named admin UI are functional, but the desktop direct-`dig` checks only establish reachability; they did not demonstrate any blocking. **Pi-hole is therefore a retirement candidate**, not an accepted permanent service requirement. Do not disable, remove, or reimage either host based on this analysis alone; retain the working Kvin service and backups until the replacement decision is made.

**Evidence from authoritative DNS owner:** [Maintenance's Peanut `named.conf.options.j2`](https://github.com/wdcallahan/sanctum-maintenance/blob/main/roles/sanctum_dns/templates/named.conf.options.j2) has `recursion yes` and `dnssec-validation auto`; [`named.conf.local.j2`](https://github.com/wdcallahan/sanctum-maintenance/blob/main/roles/sanctum_dns/templates/named.conf.local.j2) publishes Sanctum forward and reverse zones. BIND9 supports [Response Policy Zones](https://bind9.readthedocs.io/en/latest/reference.html#response-policy-zone-rpz-rewriting), which can deny selected **recursive** public-domain replies on the *existing* Peanut resolver. This is the direct, source-owned network ad-filtering approach without assigning clients a new DNS server or inserting Pi-hole as a forwarding hop. DNSSEC validation, list provenance/updates, policy scope, false-positive overrides and untouched internal authoritative results need normal Maintenance design. **DNS source owner: Sanctum Maintenance, not Services.** No RPZ has been deployed.

**Endpoint complement:** Firefox [uBlock Origin](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/) blocks actual network requests and browser page elements; DNS filters cannot selectively suppress ads served from the same origin as desired content. Neither Pi-hole nor RPZ filters applications that deliberately bypass the configured resolver (e.g. independent encrypted DNS). Whole-network HTTP(S) interception would require actual inline routing and TLS interception/trust, and is not a drop-in alternative.

**Project disposition:** The November 8 "retain Pi-hole" decision was based on the assumption it would still do ad filtering for some clients; that utility is now under reconsideration. Prefer **Peanut BIND RPZ plus endpoint blocking where needed**, subject to deciding whether network-wide policy is wanted. Do not continue Pi-hole-specific migration gates merely to prove unused ad filtering. The real Pi-hole consumer audit was already accepted and closed November 9. Once Nova selects a replacement or no network filtering, update intended estate/retirement plan accordingly without rediscovering dormant pins. Preserve Kvar until unrelated Kvar exit criteria are complete.


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
- **Pi-hole: RETIRED from the intended service estate, November 12 (Nova).** Its former resolver duty was successfully migrated to Peanut/BIND. DNS filtering is not a separate feature when no clients use Pi-hole as their resolver. **No Pi-hole rebuild, filtering test, migration, monitoring, backup-refresh, or replacement-ad-blocking deployment is required.** A future installation would be a new explicit decision. Current Kvin/Kvar containers and the existing YXORP route are merely deployed legacy state, not wanted services or a dependency that must be preserved; no live uninstall or route removal occurred with this record. The completed November 9 post-cutover audit already closed legacy client discovery.
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
| **YXORP / reverse proxy** | **Production:** Kvin rootful, source-managed plain Nginx Podman Quadlet, real port 80; Peanut authoritative DNS six Nexus aliases now direct to Kvin. Kvar NPM remains unchanged as fallback. | **Sanctum Services**: `ansible/yxorp.yml`, `ansible/roles/yxorp`, `data/yxorp-routes.yml` (source deployment projects seven wanted vhosts (Pi-hole retired); one source-only change pending native reconcile). | **Active and serving named production clients.** Kuma named authenticated browser and WebSocket 101 accepted November 11; LinkStack named directory/login accepted November 12. Other app-specific browser routes and recovery are not implicitly accepted. Existing Yarn smoke test could time out even after a successful deploy; source corrected in `eba1dfcb` so it reports degradation without aborting another route's deployment. No replacement NPM UI or blanket HTTPS needed. |
| **LinkStack** | **Live on Kvin:** rootless `sanctum-linkstack-kvin-candidate.service` with restored owned volume, internal port `127.0.0.1:18081`; served by Kvin production YXORP at `dir.nexus.sanctum`. Kvar rootless `linkstack` port 8081 and original volume still running as fallback. | **Services**: `ansible/files/sanctum-linkstack-kvin-candidate.container`, `ansible/linkstack-kvin-loopback-stage.yml`, and YXORP production `dir` upstream in `ansible/yxorp.yml`; existing recovery and snapshot scripts. | **Production public directory and admin sign-in ACCEPTED in normal Firefox November 12.** No more isolation/proxy-form tests or LinkStack deployment reruns are needed; old Kvar retained until host retirement. Live Kvin edits do not sync back to Kvar. |
| **Uptime Kuma** | Old Kvar rootless:3001 remains as fallback. New Kvin rootless:13001 has Vault-backed administrator, `Wicket Ollama` Up, tested isolated backup/restore, and named production authentication plus browser WebSocket 101. | **Services** owns source-managed Kvin deploy, state/monitor reconciliation, and its YXORP route. | **Kvin real browser route and authenticated WebSocket accepted November 11.** Independent Peanut monitoring peer and off-host recovery remain outstanding; the Kvar fallback is not the permanent second monitor. |
| **Search / EyesOnly SearXNG** | Rootless Search observed on both Kvar and Kvin; images matched but persistent backing differed | [EyesOnly SearXNG](https://github.com/wdcallahan/eyesonly-searxng/blob/main/ansible/site.yml) has an Ansible deploy role; coordinate its project ownership | **Keep Kvin instance**. Validate effective configuration/theme, data/backup and named client route; no duplicate deployment or presumed equivalent contents |
| **Nextcloud / Town Square** | Kvin rootless; Calendar 6.6.2 installed and bidirectional GNOME Calendar access accepted October 21 | [Sanctum Services application play](../ansible/site.yml) | **Keep**. Full recovery, protected proxy access, uninstallation and complete operational lifecycle still need qualification |
| **Prism** | Kvin-facing Joule browser service | **Project Joule owns Prism's container, application deployment and recovery.** Its [Kvin deployment source](https://github.com/wdcallahan/joule/tree/main/deploy/kvin) is separate. Services owns only its shared proxy route and estate dependency accounting | **Keep.** Must appear in whole-estate inventory even though Services must not duplicate or override the Joule installer. Obtain Joule's own restore acceptance |
| **PostgreSQL (shared)** | Existing Kvin rootless service and named endpoint | **Sanctum Maintenance** owns PostgreSQL service lifecycle; service clients own their respective database/application data | **Keep.** Restore sequence and credentials/data coordination are prerequisites to app recovery; Services must not recreate conflicting PostgreSQL ownership |
| **Joule host-side services** | Wicket and any Project Joule standby components; not comprehensively inventoried in this pass | **Project Joule**, with its own deployment and recovery contracts | **Include in eventual estate-wide audit by owner handoff**, not as a claim that Services operates them |

## Explicitly excluded from intended rebuild

| Container | Decision | Safety boundary |
| --- | --- | --- |
| **Pi-hole** | **Retired by Nova November 12**; Peanut/BIND took over DNS before this decision and no intended clients use Pi-hole for DNS | Remove from wanted services and Kvar-exit requirements; no further Pi-hole qualification or future reconstruction. Kvar and Kvin installations and production `pihole.nexus.sanctum` legacy UI route still exist until separately reconciled; this decision does not uninstall or stop them. Previously completed backup/restore history is retained but is no longer a project gate |
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
