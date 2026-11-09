# Sanctum service estate — ownership, disposition, and reconstruction

**Decision register and reconstruction inventory · 2026-11-08.** This document is the Services-owned reference for the intended service estate, including externally owned containers and retired definitions. It is not a live deployment authorization or a claim that reconstruction has passed. Maintain it alongside [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2) and the [roadmap](ROADMAP.md).

## Settled operating intentions (Nova, November 8)

- **Kvin's longstanding role:** Kvin was acquired years ago to take over Kvar's service-host duties. Moving the intended survivors is fulfillment of that existing design, not a new destination decision. The actual migration remains subject to evidence, restore testing, and independent operator authorization.
- **Pi-hole: RETAIN for ad blocking.** It is **not** the general/authoritative Sanctum DNS service or the DHCP-advertised network resolver. It still serves ad filtering, including whatever DNS-filtering interface its clients use. Record current clients and the future host; do **not** reinterpret absence of general DNS duties as permission to retire Pi-hole. Peanut provides the verified general DHCP DNS path per Maintenance's current observations.
- **OpenWebUI: RETIRED in favor of Prism.** **Endlessh: RETIRED.** Its former SSH-tarpit role was relevant when a host had a public-facing SSH entry point; that rationale no longer applies. Neither is in the intended reconstruction set. Some containers may still be running on Kvar: a retirement decision is **not** evidence they have been shut down and is **not** blanket authorization to remove data or services.
- **Access policy:** No intended publicly exposed inbound service ports. Tailscale is the current **stopgap** for private remote access. A properly integrated Sanctum VPN is a future **Services** project, coordinated with Bunny Factory/network routing, Maintenance/firewall/host work, DNS, and clients. Protocol, placement, trust policy, migration and client behavior have **not** yet been selected. Do not disable working Tailscale until a qualified replacement exists.
- **Planned applications:** **Luanti** and **Home Assistant** are explicit future Services projects, alongside further applications Nova may nominate. Neither is implied to be currently deployed or ready for implementation.
- **Cross-project inventory:** Include containers not installed by Services, prominently **Prism**, which is **owned by Project Joule**. A whole-estate rebuild inventory cannot exclude an application simply because its own project is the installer.

## Intended / observed services

Status below combines the November 8 Maintenance [Kvar inventory](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-11-08-kvar-retirement-inventory.md) with November 8 operator decisions and available tracked source. **Observed running** and **approved to retain** are separate concepts. Installer presence is a source audit only, not clean-host recovery proof.

| Service | Last source/observation | Lifecycle owner and source | Desired disposition / missing proof |
| --- | --- | --- | --- |
| **YXORP / Nginx Proxy Manager** | Kvar rootful; HTTP/HTTPS/admin ports 80/443/81; writable data and Let's Encrypt volumes | **Sanctum Services** takes responsibility for reproducible install/restore and Git-reconciled proxy routes under issue #2; no current installer was found in the checked service repositories | **Keep; reconstruct on Kvin** under the longstanding host plan. Preserve existing routes, TLS material, data, secrets and UI changes; adopt without duplicates; prove restore, idempotence and client access before cutover |
| **LinkStack** | Kvar rootless, port 8081; named `linkstack` volume | **Services** rebuild owner; no tracked installer located in the checked repositories | **Keep; move to Kvin**. Restore directory data/config/secrets and qualify `dir.nexus.sanctum` |
| **Uptime Kuma** | Kvar rootless, port 3001; `uptime-kuma-data` volume | **Services** rebuild owner; no tracked installer located in the checked repositories | **Keep; move to Kvin**. Restore monitors, history, credentials, notifications without duplicate notifications during tests |
| **Pi-hole** | Kvar rootful; Pi-hole and dnsmasq config volumes | **Services** owns application reconstruction, coordinated with Maintenance's DNS/client evidence | **Keep specifically for ad blocking**; **not** general LAN DNS. Determine actual ad-filtering clients and qualified Kvin restoration. No DHCP/general-DNS role inferred |
| **Search / EyesOnly SearXNG** | Rootless Search observed on both Kvar and Kvin; images matched but persistent backing differed | [EyesOnly SearXNG](https://github.com/wdcallahan/eyesonly-searxng/blob/main/ansible/site.yml) has an Ansible deploy role; coordinate its project ownership | **Keep Kvin instance**. Validate effective configuration/theme, data/backup and named client route; no duplicate deployment or presumed equivalent contents |
| **Nextcloud / Town Square** | Kvin rootless; Calendar 6.6.2 installed and bidirectional GNOME Calendar access accepted October 21 | [Sanctum Services application play](../ansible/site.yml) | **Keep**. Full recovery, protected proxy access, uninstallation and complete operational lifecycle still need qualification |
| **Prism** | Kvin-facing Joule browser service | **Project Joule owns Prism's container, application deployment and recovery.** Its [Kvin deployment source](https://github.com/wdcallahan/joule/tree/main/deploy/kvin) is separate. Services owns only its shared proxy route and estate dependency accounting | **Keep.** Must appear in whole-estate inventory even though Services must not duplicate or override the Joule installer. Obtain Joule's own restore acceptance |
| **PostgreSQL (shared)** | Existing Kvin rootless service and named endpoint | **Sanctum Maintenance** owns PostgreSQL service lifecycle; service clients own their respective database/application data | **Keep.** Restore sequence and credentials/data coordination are prerequisites to app recovery; Services must not recreate conflicting PostgreSQL ownership |
| **Joule host-side services** | Wicket and any Project Joule standby components; not comprehensively inventoried in this pass | **Project Joule**, with its own deployment and recovery contracts | **Include in eventual estate-wide audit by owner handoff**, not as a claim that Services operates them |

## Explicitly excluded from intended rebuild

| Container | Decision | Safety boundary |
| --- | --- | --- |
| **OpenWebUI** | **Retired**, superseded by Prism | Existing Kvar presence/backing is historical/residual evidence, not a reason to recreate it. No live deletion authorized by this document |
| **Endlessh** | **Retired**, former SSH tarpit no longer required | No reconstruction. Distinguish abandoned tarpit port from legitimate host management SSH; do not alter exposure/firewall without approved owner change |
| **Obsolete LinkStack rootful duplicate, AWX, Dashy, Wiki.js, Homarr** | Historical/failed/removed candidates according to Maintenance inventory; **not** inferred intended services | Reconcile evidence before treating any unknown current component as disposable |

## Future Services backlog (not deployed by this register)

- **Proper Sanctum VPN:** replace the temporary Tailscale arrangement only after a private-access topology, authentication, routing, firewall, DNS, recovery and client migration are designed and qualified with owning projects. Preserve no-public-inbound-ports intent.
- **Luanti:** new managed application, requiring ordinary Services install/backup/restore/update/uninstall contract.
- **Home Assistant:** new managed application, requiring the same contract and explicit hardware/network integration design.
- **Other future applications:** add to this register and roadmap as Nova selects them; no implicit approvals.

## What a reconstructible service requires

For every intended service, record: real owner; current and intended host; playbook/role/Quadlet; image selection and dependencies; network/ports/routes; persistent mounts; secret/certificate custody; backup and restore inputs; rebuild entry point; idempotent repeat; client acceptance; uninstall/retain-data behavior. Mark source-known, natively deployed, repeat-converged, restored and safely uninstallable **separately**. Unknown must remain unknown.

**Configuration discipline:** A manual UI or host change is not the finished desired state. Reconcile that change into the owning Git-managed configuration or a defined durable/restorable state in the same operational workflow, as with Maintenance's `data/dns.yml`. Snapshots of proxy database state alone do not replace an installer, desired route list, or restore proof.

**Immediate active work:** [Services #2](https://github.com/wdcallahan/sanctum-services/issues/2) owns YXORP reproducible deployment, route-list reconciliation (including `yarn.nexus.sanctum`), and the comprehensive audit. Maintenance's [Kvar inventory](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-11-08-kvar-retirement-inventory.md) is evidence of existing containers and mounts; its older unresolved Pi-hole/OpenWebUI/Endlessh wording is superseded by the operator decisions recorded here. Maintenance owns edits to that document; Services sends the correction through the board.

No changes to live hosts, routers, firewall, DNS, client VPN, containers, credentials, or persistent data are authorized by this record.
