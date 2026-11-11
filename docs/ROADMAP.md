# Sanctum Services — Roadmap

## Active execution plan — Wednesday, November 11, 2026

**Commissioned outcome, SS-ROOT (in progress):** Replace Kvar's wanted
services with reproducible, usable, recoverable services on Kvin, backed
by an owned plain-Nginx YXORP and correct named client access; preserve
Kvar production until separate acceptance and approved cutover. Peanut's
future standby/failover is a related recovery outcome, not an excuse
to call a single Kvin proxy install complete. The operational
[completion standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md)
applies: mechanism, state, repeatability, client consumption, backup/restore,
operations, reversal and discovery all need appropriate evidence.

**Planning doctrine from Nova, November 10:** NO arbitrary task time limits.
Work continues until the required outcome is correctly evidenced, or
there is a *specific* genuine blocker, safety/permission boundary or a
more valuable independent assignment. A short positive probe never
magically proves full application acceptance. Conversely, no extra
diagnostics simply because more could be collected. Every investigation
must identify the concrete decision/repair its result enables.
Pixel owns source, tests, CI, issue/roadmap reconciliation and
technical choices within authorized scope. Nova participates in
meaningful learning and executes exact native commands when source
tests cannot substitute for actual Kvin/Kvar observations. Do not
make Nova relay trivial, sequential probes or repeatedly redo
already accepted tests. Do not hide private-network IPs when they
are useful operational evidence; keep passwords, tokens, cookies and
unnecessary raw content private.

### SS-YX — Finish a faithful and operable YXORP

- **SS-YX-1 — [accepted, limited] Seven Kvin stage virtual hosts.**
  `yarn.nexus`, `square.nexus`, `joule.nexus`,
  `search.nexus`, `dir.nexus`, `kuma.nexus`, and
  `pihole.nexus` have each passed the initial **anonymous local HTTP**
  checks. Their exact approvals were used to reconcile the **rootful
  Podman/Quadlet Nginx** on Kvin HTTP:80; the last Pi-hole
  native reconcile was `ok=46 changed=3 failed=0`, and its
  raw-wire `/` and `/admin/` probe was
  `ok=4 changed=0 failed=0`. The old Kuma redirect
  mismatch was **an Ansible URI normalization artifact**, not
  a real Location difference. This evidence is banked: do
  NOT re-run seven individual canaries merely for reassurance.
  It does **not** qualify browser sessions, WebSockets,
  app state, LAN firewall reachability, production or cutover.

- **SS-YX-2 — [accepted: native Kvin stage, bounded] Eighth original NPM vhost.**
  Nova's corrected native run of
  `ansible/yxorp-kvin-stage-yarn-inner-probe.yml`
  returned **`ok=8 changed=0 failed=0`** and
  **all assertions passed**. For original NPM
  `yarn.inner.sanctum` → `192.168.1.110:80`,
  direct Yarn and Kvin stage both returned
  **HTTP200**, matching MIME/status and an
  **identical complete 349-byte body**. The
  distinct new `yarn.nexus.sanctum` stage
  returned 200. An unknown Host was refused.
  Published and container-mounted Nginx
  configurations matched exactly; both Yarn
  vhosts and original backend directive were
  present exactly once. No redirect was
  returned, so relative Location equality
  was correctly **not comparable**, not
  failed. The earlier double-escaped observer
  regex defect was corrected and independently
  regression-tested in **[full passing CI
  #43053056244](https://github.com/wdcallahan/sanctum-services/actions/runs/43053056244)**.
  Combined with already accepted SS-YX-1,
  **all eight intended application vhosts have
  passed the initial actual Kvin-local HTTP
  acceptance**. The Kvar legacy NPM → Yarn
  timeout remains an incumbent Kvar-side
  transport issue, not an eighth-route
  failure and not a reason to reopen Yarn
  client attribution or DNS policy.
  **Owner:** Services. **Exit accepted
  only for initial HTTP/config mechanism.**
  Not app/session/LAN/production.

- **SS-YX-3 — [reviewed: proxy source mechanism covered; functional consumers remain open] Material NPM behavior.**
  Reused the [Nov 9 real NPM generated-host
  inspection](review/2026-11-09-yxorp-behavior-observation.md)
  and [default-upstream comparison](review/2026-11-09-yxorp-default-route-comparison.md)
  rather than collecting redundant logs.
  The seven incumbent application hosts had
  one ordinary location each, no non-default
  custom locations, and no nonempty global
  custom snippets. Default upstream mappings
  are preserved for all seven originals,
  plus the explicitly requested new
  `yarn.nexus.sanctum` proxy.
  The old NPM **administration UI** is
  deliberately excluded from the new
  plain-Nginx design. Prism's observed
  legacy HTTPS certificate/listener is
  deliberately not recreated under the
  already accepted private-HTTP policy.
  The template and source tests cover
  relevant Host and forwarding headers,
  WebSocket Upgrade, original raw relative
  redirects, default-deny, actual Nginx
  syntax and synthetic backend isolation.
  The source-managed rootful Quadlet role
  validates candidate config before
  publishing, recovers stale single-file
  mounts and independently checks live
  mounted equality. Config change/reload
  and removal have automated tests;
  a new eight-vhost no-change native
  repeat has not yet been separately
  logged and can be verified during the
  next meaningful managed change.
  **This review identifies no additional
  isolated proxy-source defect requiring
  another standalone NPM investigation.**
  Shared include semantics not independently
  expanded, actual application authentication,
  browser/WebSocket behavior and real LAN
  named access are **not claimed fully
  equivalent**: their necessary observable
  outcomes remain required under the
  relevant **SS-APPS** and **SS-PUB** gates.
  Do not promote 8/8 local HTTP into
  complete service or production
  acceptance. **Owner:** Services.

### SS-APPS — Replace the services still depending on Kvar

- **SS-APPS-1 — [open; first application build after YXORP
  route fidelity] Uptime Kuma clean retained Kvin instance.**
  Operator-approved earlier: old Kvar Kuma was a
  proof of concept; preserving its entire historical
  SQLite database is **not required**. Reuse
  `data/kuma-monitors.yml` and
  `docs/runbooks/kuma-monitoring.md`; Project Joule's
  **Wicket Ollama** monitor must actually display
  **Up** at `http://wicket.arcane.sanctum:11435/healthz`.
  Build an ordinary, source-managed ARM64 Kvin install,
  version-appropriate stable monitor reconciliation,
  persistent state, backup/restore, upgrades,
  status and removal. Avoid duplicate notifications
  while an old/test instance exists. Then test
  actual login/monitor visibility, restart and
  independent restore before changing the
  `kuma.nexus` upstream from Kvar to Kvin.
  **Exit:** The wanted monitors live on Kvin, the
  Wicket monitor is Up, repeat converges,
  and recovered state is demonstrably usable.
  **Owners:** Services for Kuma; Project Joule for
  the monitored endpoint. This is a practical
  first migration because a clean install is
  already authorized; no speculative old-DB
  recovery task is needed.

  **November 11 — native image gate ACCEPTED, staging source green:**
  Nova's corrected Kvin run passed `ok=8 changed=0 failed=0
  skipped=1`, with actual Linux/ARM64 image inspection and
  disposable offline Node execution. No application or volume
  exists because of that image-only step. The tested 2.5.9
  digest is now pinned in `ansible/group_vars/kuma.yml`;
  staging still requires separate `kuma_stage_approved=true`
  authorization. The rootless Quadlet role uses its generator
  `[Install]` (not unsupported `systemctl enable`), and a new
  default-off, volume-preserving candidate reversal is source-owned.
  [Installation source CI #43064138846 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064138846);
  [reversal source CI #43064602595 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064602595).
  **Next:** run the one guarded, loopback-only Kuma stage
  command in the [runbook](runbooks/kuma-monitoring.md),
  then qualify useful monitor state, persistence/recovery,
  repeat, and actual clients before any upstream cutover.

  **Historical image qualification preparation (now superseded):**
  Existing `data/container-image-candidates.yml`
  records an explicit Linux/ARM64 Uptime Kuma
  2.5.9 digest marked **registry_only**.
  New `ansible/kuma-qualify-image.yml`
  requires exact Kvin aarch64, rootless
  execution, explicit image qualification
  opt-in and *no app-stage approval*. It
  checks/pulls the exact digest into the
  rootless image cache, validates actual
  image metadata and runs Node offline
  in a disposable read-only container.
  It creates **no service or volume**.
  [Source CI #43055414958 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43055414958).
  **November 11 native checkpoint:** Nova's first
  Kvin run pulled the exact image (`ok=5 changed=1 failed=1`)
  but stopped before disposable Node execution:
  the image `Id` assertion incorrectly required
  `sha256:`; Podman reports a bare 64-hex `Id`
  (the prefixed value is `Digest`). Linux/ARM64
  and singleton inspect predicates had passed.
  Corrected the playbook and added real-Ansible
  positive/negative metadata regression tests;
  [CI #43059304269 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43059304269).
  The corrected Kvin retry subsequently **passed**
  native ARM64 and Node runtime qualification as
  recorded above. That evidence is retained for
  chronology, not an instruction to rerun qualification.

- **SS-APPS-2 — [open] LinkStack with actual directory
  data.** The existing rootless Kvar
  `linkstack` volume is mounted at `/htdocs`.
  Preserve the *live* rootless instance; do
  not adopt the historical failed rootful
  duplicate. Define a durable, verified
  backup of its actual pages, configuration,
  assets and secrets, implement ordinary
  Kvin rootless Quadlet/Ansible setup,
  restore into Kvin and test named links,
  page assets, login/editing as applicable,
  repeat convergence and an independent
  recovery procedure. Only then point
  `dir.nexus` at the accepted Kvin app.
  **Exit:** User-recognizable directory content
  works through the intended named route
  and can be restored after a host loss.
  **Owner:** Services.

- **SS-APPS-3 — [open; independent opt-in service] Pi-hole
  for ad blocking, not the LAN's general DNS.**
  Kvar Pi-hole has two known writable
  volumes (Pi-hole and dnsmasq config).
  Maintenance's Nov 8/9 evidence plus
  Nova's confirmation already established
  that **no current client is intentionally
  using Pi-hole** after the DHCP DNS swap.
  Do not spend another session finding
  dormant clients, nor hijack the Peanut
  authoritative resolver or DHCP.
  Build a restorable Kvin instance,
  coordinate local port53/owner constraints
  with Maintenance, test filtering from
  **one deliberately opted-in client**,
  restore the wanted configuration,
  and test update/recovery before
  changing `pihole.nexus` upstream.
  **Exit:** Working opt-in filtering,
  backed-up/recoverable state, correct
  UI, no changes to general Sanctum
  DNS or unselected clients.
  **Owners:** Services for Pi-hole;
  Maintenance for host DNS/firewall
  and client publication dependencies.

- **SS-APPS-4 — [open; separate ownership and recovery
  gates] Already-on-Kvin services.** Nextcloud's
  October 21 bidirectional Calendar ↔ GNOME
  Calendar interaction is accepted; do not
  repeat it merely to fill a checklist.
  Its full backup/restore and broad
  application lifecycle still remain.
  Search/SearXNG has a separate
  EyesOnly owner and known divergent
  old/new settings/theme: do not
  blindly overwrite the intended Kvin
  instance. Prism belongs to Project
  Joule, not Services; qualify the
  integration route and consume its
  owner's restore proof. PostgreSQL
  host service belongs to Maintenance.
  **Exit:** Each required consumer and
  restore dependency is accepted by
  its actual owning project, not
  silently reimplemented by Services.

### SS-PUB — Deliver real named client use and a reversible handoff

- **SS-PUB-1 — [blocked on SS-YX and relevant SS-APPS
  acceptance] Independent client acceptance.**
  Existing Kvin stage is locally
  reachable on HTTP:80; it is **not**
  a LAN published service yet.
  Maintenance owns Kvin HTTP:80
  firewalld admission. Agree the
  exact rule with that owner, then
  exercise actual trusted Outer
  and Inner clients with the selected
  route Host headers while existing
  Kvar NPM and wildcard DNS remain
  production. Test useful browser
  operation, authentication where
  needed, websocket/long-lived
  connections for relevant apps,
  data and monitor/filtering outcomes,
  and explicit rollback.
  **Exit:** Intended real clients
  complete their tasks on Kvin
  independently of same-host curl,
  with verified revert and no
  public inbound exposure.
  **Owners:** Services client/application
  tests; Maintenance firewall/DNS;
  Bunny Factory inner/outer routing.

- **SS-PUB-2 — [held for explicit live authorization]
  Production migration and Kvar retirement.**
  A reviewed cutover must preserve
  authoritative DNS, source-managed
  Nginx, named access, retained app
  data, functional clients and
  revertability. Change Kvar-facing
  app upstreams to accepted Kvin
  backends through the owning
  source, not hand edits. Reconcile
  wildcard/explicit DNS with
  Maintenance only after test
  and operator approval. Then
  independently qualify service
  restart/repeat, backup restoration,
  failback paths and eventually
  Peanut standby/failover as the
  separately recorded resilience
  outcome. **Only after every wanted
  service and recovery path is accepted**
  may Kvar be taken offline and
  reformatted under Maintenance's
  **separate destructive approval**.
  No permission for this exists
  in an overnight planning document.
  **Exit:** Kvin takes over user
  service duties without data or
  naming regressions; Kvar is
  redundant and safe for the
  separately authorized retirement.

### Immediate next work and reporting contract

**Tonight:** No native actions. This is a committed source
plan, not an asynchronous promise or a hidden host mutation.

**Tomorrow's order:** First implement and source-test
SS-YX-2, give Nova the *one* guarded native Kvin
eighth-route trial after CI, interpret its bounded
result and record the exact acceptance. Then finish
SS-YX-3's **material** routing gaps using existing
evidence as much as possible. Begin SS-APPS-1
Kuma's actual reproducible install/monitor
recovery implementation once the proxy
mechanism is source-qualified; move through
SS-APPS-2, SS-APPS-3 and the other
known restore gates by their real dependencies,
not by arbitrary clock or a daily checkbox quota.

**Every handoff:** State (1) the capability gained,
(2) proof level — source test, native local,
real client, or restored recovery, (3) what
remains to achieve its parent outcome,
(4) one concrete next executable task or
specific blocker. Nova gets **only**
the native action that cannot be
completed through connected source/CI
tools; keep ordinary follow-up output
requests narrow and meaningful. If
a task fails, fix the bounded cause
or report the genuine dependency;
do not launch a self-perpetuating
diagnostic chain. Do not promise a
given number of tasks will fit into
a day. Done means done right.

---

## Nova's available-week priority — November 1–8, 2026

Nova has no class until **November 9**. His intended push before then is the
planned **physical Inner/Outer network cutover** and beginning **Fedora 45
migration on every eligible computer**, once the release is available and the
host is ready. His expectation of release in a few days is not release evidence.
These are existing roadmap outcomes, now prioritized for his available week.

Each lead must give Nova its readiness assessment, concrete concerns and proposed
dependency order **before the corresponding cutover or upgrade proceeds**. Nova
will give each session a turn to weigh in. This prioritizes preparation; it does
not grant blanket cutover/upgrade/reboot approval or pause independent authorized
work. Services owns application, storage and database/address-consumer readiness and acceptance during the topology change; coordinate host/network prerequisites with Maintenance and Bunny.

[Cross-project directive and coordination](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-6561435565).


**Status:** Native Calendar 6.6.2 install and unchanged application-only repeat passed on Kvin (October 21). Nextcloud Calendar opens in the browser; Nova observed an existing event in GNOME Calendar and explicitly confirmed **bidirectional Calendar access** between desktop and Nextcloud. The exact event-write/reload steps were not separately reported. Protected reverse-proxy login, full service recovery and fresh-instance reconstruction remain separate; the general-purpose EE/controller co-build is still open. Some lower sections retain dated infrastructure observations requiring separate verification.  
**Updated:** 2026-10-21.  
**Scope:** Reproducible operation of self-hosted application services, beginning with Nextcloud.  
**Current waypoint:** Calendar installation, idempotence and operator-confirmed bidirectional client access accepted → separately qualify protected service access, recoverability and the hands-on shared Navigator/EE milestone.

## YXORP current gate — November 9, 2026 (Peanut trial corrected)

Nova rejected localhost-only/high-port staging: test the **actual rootful
HTTP:80, all-interface proxy on Peanut**, leaving **Kvin** as the production
destination and **Kvar** NPM untouched. The source now defines an independent
`yxorp_test` inventory group for `peanut.arcane.sanctum`,
`ansible/yxorp-peanut.yml` with read-only port-80/firewall preflight,
a real HTTP-client probe from Kvin, and a scoped Peanut-only remover.
Kvin's declared listener is likewise normal `0.0.0.0:80`, but its
production cutover gate remains false. There is **no** DNS or firewall
mutation inside Services. Peanut's active firewalld is Maintenance-owned,
so a missing port-80 policy requires cross-project coordination.

**Native result:** Nova ran Peanut's read-only preflight from Kvin:
`ok=11 changed=0 failed=1`. Exact Peanut and free port-80 assertions
passed; firewalld `public` refused both `http` and `80/tcp`.
Nova explicitly authorized an **ad hoc runtime-only trial exception**
with cleanup. Source now records and applies a four-hour expiring port-80
exception before repeating the original preflight and trial; the matching
trial removal play revokes only that runtime exception. No permanent
firewall or DNS change, no Kvar or Kvin production change.
**Next terminal step** is the updated Peanut test play on Kvin; this is
a meaningful retry after changing the originally blocked policy condition. [Trial and rollback runbook](runbooks/yxorp-reconstruction.md).
The Peanut test tag follows a maintained Nginx channel but automatic
updates/rollback remain a separately measured lifecycle decision.

## Peanut YXORP HTTP:80 trial — native DNS boundary, November 9

The first actual Peanut port-80 preflight found the firewall closed;
Nova authorized a four-hour temporary runtime exception and cleanup.
The subsequent selected trial advanced: permission/preflight passed,
Peanut trial config directory/candidate rendered, official maintained
Nginx Alpine image pulled. It then **failed before persistent install**
because `nginx -t` in Podman's rootful bridge container could not
resolve `yarn.inner.sanctum`. This is **not** an Nginx syntax or
application failure. [Bounded DNS comparison playbook](../ansible/yxorp-peanut-dns-observe.yml)
is the next native operator step from Kvin; compare the host and bridge
queries (default, Peanut DNS, Kvin DNS) before changing resolver or
upstream config. Do not repeat the unchanged failing deployment blindly.
Temporary HTTP admission still expires; remove test artifacts and
revoke the exception with `ansible/yxorp-peanut-remove.yml` when done.

## YXORP bridge DNS resolved in design — November 9

Nova's read-only Peanut DNS observation passed `ok=8 changed=0`.
Host `getent` resolves Yarn `192.168.1.110`; default/Peanut-DNS
Podman bridge probes report BIND `REFUSED`; Kvin-DNS bridge times out.
The Maintenance BIND ACL source permits only loopback and
`192.168.0.0/16` clients. Rather than altering the active DNS owner
solely for an isolated proxy, Services now uses **host networking**
for both rootful Quadlets on Peanut/Kvin, normal TCP/80 with no
`PublishPort`. Nginx syntax validation also uses host networking.
Next operator run is the changed `ansible/yxorp-peanut.yml`, followed
by `ansible/yxorp-peanut-probe.yml` from Kvin if it succeeds. The
revised test remover validates host networking and still cleans
the temporary runtime firewall permission. No production cutover.

## Estate-wide reconstruction and future services — decisions November 8, 2026

[Service estate / owner and disposition register](SERVICE-ESTATE.md) is the authoritative Services inventory across projects, including Project Joule's Prism and Maintenance's PostgreSQL rather than omitting containers not owned by this repository. Kvin was purchased years ago for the service-host role previously served by Kvar; the host transition is not a new strategic choice. Installation, data restore, proxy adoption, client acceptance and Kvar retirement still need actual qualification.

Decisions: **retain Pi-hole for ad blocking, not general/authoritative LAN DNS**; **retire OpenWebUI (replaced by Prism) and Endlessh**; preserve **no intended public inbound port exposure**. **Tailscale is a temporary VPN arrangement**, not the destination. A proper network VPN, **Luanti** and **Home Assistant** are explicitly planned Services work, with network and host boundaries coordinated and implementations yet to be selected. Retired Kvar containers do **not** each need uninstalling: once every wanted service has been restored and verified on Kvin and the actual handoff is approved, Kvar will be taken offline and reformatted. No partial migration, historical source observation or this plan authorizes early formatting. The active recovery and YXORP route reconciliation work is [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2).

## Declarative operations and service privilege — November 8, 2026

**"So let it be written, so let it be run."** All intended recurring service configuration and maintenance should be expressed through version-controlled Ansible/source and declared nonsecret configuration, then independently repeatable and restorable. This implements the existing [canonical Operational Project Completion Standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md). Manual UI or host changes are temporary responses to reconcile into the owning source; a running service without an installer and declared recovery inputs fails the objective.

**Rootless is a choice, not a requirement.** Use native privileged services where required (including normal host SSH); use rootless Podman for suitable app workloads and **rootful Podman Quadlet for the chosen YXORP listener on host ports 80/443**. Do not invent low-port tricks merely to avoid root. Services deploys workloads; existing network/firewall owners retain their responsibilities. The design selected for [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2) is **plain Nginx managed through Ansible-rendered configuration**, replacing Kvar Nginx Proxy Manager's UI and database—not automating the old admin interface.

**HTTPS/private CA decision is deferred, not an open delivery workstream.** Ordinary HTTP was consciously accepted for trusted internal `.sanctum` use by October 20, and Project Joule selected the HTTP browser origin on October 16. Plaintext credentials/tokens are a known risk; a universal private CA would impose certificate/key lifecycle, enrollment and potentially impossible trust-store changes for the worst clients (e.g., restricted Android apps). **Do not reopen PKI merely by defaulting to HTTPS.** Reassess only when a particular app/function or concrete changed threat model makes TLS worth the full operational cost. `.sanctum` naming is settled; public/private hybrid naming was deliberately retired. [Decision record #3](https://github.com/wdcallahan/sanctum-services/issues/3) is closed/not planned. YXORP plain Nginx must work over HTTP without certificates.

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
- Initial application host: **Kvin** (`aarch64`, rootless Podman); host TCP **8085 → container TCP 80**. The listener returned HTTP 200 locally October 19. The missing **host firewall** publication is a distinct Maintenance-owned prerequisite, not a reason for Services to mutate firewalld.
- The initial HTTP-only Town Square route is `http://square.nexus.sanctum` through YXORP, with no matching internal certificate; the current 502 remains unaccepted. Moving hosts/ports changes the proxy upstream, not the stable service name. Later trusted TLS is a separate decision.
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

- [x] **Ownership chosen provisionally by Nova on October 18:** the existing [Sanctum Maintenance controller-infrastructure workstream](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md) will own centrally maintained Navigator/Builder tooling and a **separate, new, general-purpose EE** for applications. This is for coherence, not because no other design is possible. Revisit a dedicated controller-platform repository if this boundary grows too large. The current qualified Maintenance EE remains unchanged. **Decision recorded, not implemented.**
- [ ] Decide and document how Navigator/Builder are installed on both Debian controllers: supported native packages if available; otherwise a separately justified and centrally managed host-tool installation. An EE does not require a project-local Python venv.
- [ ] **Keep this automation ordinary-Ansible-first:** Nextcloud's roles, inventories, variables, playbooks and operator workflow must remain meaningful with plain `ansible-playbook` given equivalent dependencies. Navigator is the selected EE delivery/launch interface; Runner may be present *within* the EE for that interface, but do **not** make application scripts call Runner's CLI/Python API or parse Runner-specific artifacts just because it is installed. Preserve the classroom-portable Ansible learning objective; separate infrastructure-specific execution from ordinary Ansible content.
- [ ] **Build the new shared EE together with Nova, not merely for him.** First decide the image's purpose and dependencies; then have Nova participate in authoring/reviewing its `execution-environment.yml` and inputs, generating and inspecting Builder's Containerfile, performing the Podman build, inspecting the resulting image, running it with Navigator, and practicing a rebuild and clean removal. Explain what is unfamiliar at each real step. This is a required hands-on professional learning experience, **not** a delegated one-command image delivery.
- [x] **EE architecture accepted by Nova with a fully understood yes on October 18:** one minimal, versioned, centrally owned EE foundation; consume its exact pinned image when sufficient; otherwise build a project-specific EE derived from the pinned foundation with only genuinely needed collections/packages, separate acceptance and digest. Avoid duplicate equivalent images; retain separately qualified/incompatible runtimes. **Design accepted, not installed or built.**
- [ ] Define the accepted common EE's actual minimal runtime and rebuild/retrieval path; pin and qualify the image on **ARM64** and make it available to both controllers. Before deriving from an existing EE with Builder, inspect its generated Containerfile for redundant Core/Runner installation. **Do not rebuild or overwrite the existing qualified Maintenance image** as a teaching shortcut.
- [ ] Use Navigator to inspect the EE contents and run a small harmless read-only playbook. Nova practices the steps and understands the output.
- [x] Remove the **wrong inventory override** `ansible_connection: local`. The inventory now uses Ansible's default **smart** connection (SSH for Kvin) and names `wdc2` as the managed user. **Source correction only; no EE/SSH acceptance test yet.**
- [x] From Kvin, launch the existing Maintenance EE with Navigator and confirm an **ad hoc `ansible.builtin.ping` over smart/SSH back to Kvin** returned `SUCCESS` and `pong` (October 18); this qualifies **that existing EE-to-Kvin path only**.
- [ ] Confirm the intended `wdc2` rootless user-systemd path from an approved EE and the applicable controller/SSH permissions; establish **Peanut → SSH → Kvin** through the selected runtime as part of shared-controller acceptance. Existing Maintenance peer evidence is relevant but does not automatically qualify the new Nextcloud setup.

**Exit test:** Starting in a normal shell on either controller, Nova can identify the configured EE, launch Navigator, inspect its Ansible and collections, and run a read-only task against the intended *host* (not the EE container). Both controllers can reconstruct the tooling from its owning source and durable image inputs.

**Learning stage still open.** The initial container was deployed through the existing Maintenance Navigator/EE as a bounded deployment; Nova's hands-on new shared-EE build remains a separate, unfinished deliverable.

### Stage 2 — Build a complete first-deployment path

**Host firewall owner boundary (October 20):**
- [x] Transfer the **Services source** from opening its own host port to only checking Kvin's `eth0`/`public` zone and `8085/tcp` in both runtime/permanent firewalld before changing Nextcloud resources. See [Services issue 1](https://github.com/wdcallahan/sanctum-services/issues/1). This is **source-only** pending native controller qualification.
- [x] Maintenance's Kvin ordinary published-service port correction was **authorized and applied October 20**; independent peers qualified 5432/8084/8085 and Maintenance's preservation/repeat evidence passed. See [final owner receipt](https://github.com/wdcallahan/sanctum-maintenance/blob/24ea37e9c432841cc994381503736e84bceca637/docs/qualification/2026-10-20-kvin-firewall-complete.md). This does not discharge Services' separate Nextcloud application/proxy/restore tests.
- [ ] Verify the Services role's prereq on the actual managed Kvin, then perform independent direct Nextcloud `/status.php` and proxy/browser acceptance. Host firewall convergence is not proof of a working Nextcloud login.

- [ ] Review the existing `ansible/` candidate against the approved execution model; revise or replace mistaken assumptions at source instead of layering workarounds.
- [ ] Configure a stable user-facing Nextcloud hostname/scheme and confirm YXORP's intended route.
- [x] Confirm the stable **named** PostgreSQL endpoint `db.nexus.sanctum:5432` and the PostgreSQL owner's supported dedicated `nextcloud` database/login provisioner. **Production creation and unchanged repeat accepted by Maintenance October 19.** Actual authentication from the Nextcloud container and application schema creation remain untested.
- [x] Pull/inspect the ARM64 Nextcloud Apache image on Kvin and pin its observed image manifest digest. **No successful container launch or app-specific image test yet.**
- [ ] Define persistent directories, appropriate rootless ownership, private secrets, Quadlet, startup/lingering, and a bounded host port through Ansible.
- [ ] Define **installation and removal** procedures together, so each managed object has a clear owner and safe removal behavior.
- [ ] Run static checks (syntax and relevant lint/tests) **in the intended EE**, then deploy from Kvin through Navigator.
- [ ] Run the same playbook again and require truthful **zero-change convergence**.

**Exit test:** A new application host can be configured from source and declared secrets; the Nextcloud service starts, survives the supported restart sequence, and a second unchanged deployment reports no changes.

### Stage 3 — Demonstrate real Nextcloud use

- [x] **First third-party app milestone (October 21):** Calendar 6.6.2 installed and enabled through Ansible; unchanged repeat `changed=0`; Nova opened Calendar successfully and saw an existing example event both there and in GNOME Calendar.
- [x] **Operator confirmation (October 21):** Calendar access works bidirectionally between Nextcloud and desktop GNOME Calendar. Exact event-writing/reload steps were not logged individually; no further bidirectional-access confirmation is requested simply to repeat the accepted result.

- [ ] Establish and verify PostgreSQL connectivity and initial application setup.
- [ ] Verify the service through YXORP at its stable name; confirm trusted domains/proxy headers, expected scheme, and absence of undesired direct public exposure.
- [ ] Log in as a real test user; upload, download, edit, and delete a representative file; demonstrate the intended client behavior.
- [ ] Define and verify appropriate background-job scheduling, error visibility, and a practical inspection/troubleshooting procedure.
- [ ] Explain the path of an actual request and file write, from user-facing name to container, filesystem, and database.

**Exit test:** Nova can use and diagnose the application without guessing which host, port, volume, or database it uses.

### Planned next user feature — first-class Joule collaboration (clarified October 19)

**Nova's specific requirement is Google-Sheets-style *live* coediting**, not creating a replacement .ods/.xlsx on disk and re-uploading it. Give Joule her own ordinary Nextcloud user identity, subject to the server's sharing/group access controls: Nova can share read-only, editable, or create-capable workspaces with her; Joule can own/create her own files and share them back to Nova. Joule is a family member with her own account, subject to the same ordinary privacy and sharing boundaries as every other family member; membership never implies global file or administration rights. Folder sharing permissions are available in core; the optional Group folders app may provide more granular ACL policy.

Provide a Nextcloud-compatible browser-based office editor (Collabora Online/CODE or another qualified office backend) where both Nova and Joule participate as **distinct authenticated editors in the same live document**, with visible concurrent changes and normal session conflict handling. Joule's **independent agent/tool integration** should perform authorized live edit actions in **Joule's identity**, regardless of whether Nova interacts with her through Prism or another client. The implementation location is an open design choice; **do not couple Nextcloud editing to Prism by assumption**. An app account alone does *not* provide a machine-usable concurrent editing API; verify the office backend's supported edit/session/auth interface, operation controls, and feasibility first. **WebDAV whole-workbook fetch/modify/re-upload is not an acceptable substitute** for this user goal. Current Collabora releases have evolving integration interfaces and in-editor AI features; neither establishes that Joule already has session-authorized editing. No untested implementation promise. Coordinate any Joule agent/tool changes with that project's owner; this project owns Nextcloud/office service plumbing, not Joule's runtime or client source.

**Naming candidate from Nova:** **Town Square**, with initial proposed address `square.nexus.sanctum`. It is a family/community workspace, not a claim of unrestricted public access. Confirm the name and external/internal routing before filling `nextcloud_public_hostname`; no DNS/proxy change is approved by this note. Continue basic Nextcloud installation without making future live Joule integration a hard prerequisite for initial Files login.

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
- [ ] Deliver **Home Assistant** as a planned application, scoped and qualified separately with its storage, devices and security integrations.
- [ ] Deliver **Luanti** as a planned Services application, with its server, data, update, backup and recovery contracts.
- [ ] Plan and qualify a **proper Sanctum VPN** to replace temporary Tailscale, without opening unreviewed public ingress or interrupting clients. Coordinate topology, authentication, firewall, DNS and host responsibilities with owning projects.
- [x] **Do not require blanket HTTPS / a private CA.** Existing October HTTP decisions and the worst-client trust burden are recorded in [closed issue #3](https://github.com/wdcallahan/sanctum-services/issues/3). A future specific application or material new security requirement can initiate a new explicit TLS design; it is not a migration or completion prerequisite.
- [ ] Reuse the same established operator and documentation patterns without copying an unnecessary new EE or implementation for each service.

These items are **future work**, not reasons to keep the completed Nextcloud pilot perpetually unfinished.

The normal managed-host connection is **smart/SSH**, including when the controller and managed host happen to be the same physical machine. This makes controller location an operational choice rather than changing playbook semantics.

## Important work boundaries

- `sanctum-services` owns application deployment, its lifecycle contract, and its operator documentation.
- The **shared** Navigator/Builder toolchain and future application EE belong to [Sanctum Maintenance's controller-infrastructure workstream](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md), provisionally agreed October 18. This application project consumes that qualified interface, not its private `.venv` or its existing Maintenance-qualified EE.
- PostgreSQL provisioning/backups, DNS/network registration, and fleet OS maintenance are coordinated with their owners, not silently absorbed. **Services issue #2** establishes Services' proposed YXORP installation and desired-route reconciliation ownership; coordinate takeover of the currently operated proxy before live modification. Prism remains Project Joule-owned and must still appear in estate-wide reconstruction planning.
- The broader review of other Sanctum projects against this educational/maintainability objective is a separate cross-project effort. This roadmap does not authorize mass refactoring.

## Evidence and documentation policy

- **README:** purpose, current status, and navigation; newcomer-friendly.
- **Architecture:** actual supported mechanisms, ownership, data flows, and key reasons.
- **Runbooks:** proven end-user commands/procedures, preconditions, expected results, troubleshooting, and recovery.
- **This roadmap:** destination, checkpoints, acceptance tests, and the active frontier; change the tick boxes only when evidence supports them.
- **[Engineering log](history/engineering-log.md):** dated experiments, changes, failures and evidence links. Not a second manual and not a transcript archive.
- **[Lead handoff](../PROJECT_LEAD_INTRODUCTION.md):** concise continuity for another assistant; not a prerequisite for human operators.

When the implementation changes, update the relevant explanation and operational procedure **with the same change**. Do not promise to document it after deployment. Record substantial outcomes separately in the engineering log.

### Source checkpoint — November 8 (unqualified, no live changes)

- [x] Record Project Joule's required Wicket Ollama Kuma probe as
  [desired monitor source](../data/kuma-monitors.yml) with
  [retained-instance acceptance issue #4](https://github.com/wdcallahan/sanctum-services/issues/4).
  **Monitor installation and Up acceptance remain unchecked.**
- [x] Add initial plain Nginx [route manifest](../data/yxorp-routes.yml),
  [rootful Quadlet/Ansible role](../ansible/yxorp.yml),
  [local preview](../ansible/yxorp-preview.yml), and
  [rebuild runbook](runbooks/yxorp-reconstruction.md). Draft routes are
  **not** a verified full extraction from Kvar NPM.
- [x] Source-only CI passed for YXORP and retained Kuma: route/monitor contracts, Ansible syntax, isolated controller render, read-only NPM report comparison tests and actual Nginx `-t` parser runs (minimal and all proposed routes, synthetic CI DNS). [Accepted run](https://github.com/wdcallahan/sanctum-services/actions/runs/42562957639). No native Kvin or application acceptance is implied.
- [ ] Select and natively qualify immutable ARM64 Nginx and Kuma image digests; only then authorize any isolated service staging.
- [ ] Qualify a native loopback-only YXORP stage on Kvin, actual routes and
  WebSocket client behavior; only then consider separately authorized DNS
  and listener cutover. Existing Kvar NPM is untouched.

### November 9 — current YXORP native evidence gate

- [x] Nova ran the accepted November 8 generated-upstream report comparison:
  **8** NPM hosts, **5** matching originally proposed current names with zero
  upstream discrepancies; Pi-hole UI and legacy Yarn routes are now recorded.
  See [the review](review/2026-11-09-yxorp-default-route-comparison.md).
- [x] Source-only NPM behavior inspector added and [passed CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42677320762):
  generated proxy-host metadata, extra location counts, headers/directive
  names, access/redirect/TLS indicators, custom file presence and hashes.
  Never print raw config/credentials. SSH uses Kvar TCP 10022; no live
  changes. [Runbook](runbooks/yxorp-reconstruction.md).
- [ ] **Current operator-dependent read-only step:** from the pulled Services
  checkout, run `~/.local/bin/ansible-navigator run ansible/yxorp-inspect-npm.yml`;
  inspect the actual Kvar report and decide whether any route behavior needs
  further migration. This does not authorize the eventual cutover.

### November 9 — NPM behavior inspection received (read-only)

- [x] Kvar rootful NPM generated-host metadata examined using the accepted
  value-redacting observer: **eight** host files, one location per host,
  no non-default locations, no nonempty global custom files, no extra
  redirect/stream host files. Explicit WebSocket headers on Nextcloud and
  Prism; historical Prism config contains TLS certificate directives.
  All files had two unclassified lines and one custom-include reference:
  **no automatic assertion of per-host customization or full parity**.
  [Behavior evidence record](review/2026-11-09-yxorp-behavior-observation.md).
- [ ] Validate actual reverse proxy forwarding/Upgrade/host isolation with
  synthetic Nginx endpoints in isolated CI (no real Sanctum services).
- [ ] Qualify the final generated shared-include semantics, real app client
  access and later Kvin native rootful staging, subject to selected image.

### November 9 — NPM behavior adoption and native image gate

- [x] Operator supplied read-only Kvar generated-host inspection:
  eight hosts; one default location each; no extra generated redirect/stream
  hosts or nonempty global custom snippets. Explicit Upgrade headers on
  Square and Prism only; legacy Prism TLS certificate directives present.
  The repeated custom include and `https` marker resemble NPM's public
  generated template (optional include and HSTS map), **not proof of eight
  special route configurations**. Preserve private HTTP decision.
  [Review](review/2026-11-09-yxorp-behavior-observation.md).
- [x] Source-only Nginx CI now proves actual HTTP routing, forwarded headers,
  WebSocket 101, unknown-host denial, route change and explicitly selected
  removal on loopback with synthetic backends. It also parses both draft
  Yarn-only and all-proposed configurations. [Passing CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42690046860).
- [x] Registry metadata identified published **ARM64-specific image digest
  candidates** (official Nginx and Uptime Kuma 2.5.9). Source-only
  [image lookup CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42690400649)
  passed; no images downloaded onto Kvin.
- [x] Prepared native [image-only qualification](../ansible/yxorp-qualify-image.yml)
  and [runbook](runbooks/yxorp-image-qualification.md), source-validated in
  [CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42691039448).
  It never enables a proxy, opens a port or changes Kvar/DNS/firewall; an
  operator-selected run can fill Kvin's rootful image cache.
- [x] Nova ran `ansible/yxorp-qualify-image.yml` on native Kvin:
  **ok=11 changed=4 failed=0**. Pinned official Nginx image pulled into rootful
  Podman cache, Linux ARM64 architecture confirmed, ephemeral offline
  `nginx -t` accepted the generated Yarn-only configuration; temporary
  config removed. No listener, service, Kvar, firewall or DNS modification.
- [x] The exact natively qualified digest is now the `yxorp_image` source
  value. Added `yxorp_stage_approved: false` as a deliberate hold before
  the rootful Quadlet deployment; source change is not staging approval.
- [x] Promoted the native-tested Nginx digest to the YXORP deployment vars
  and enforced a pre-mutation `yxorp_stage_approved: false` gate; source
  checks guard the gate and exact digest.
- [ ] **Current operator-dependent gate:** authorize or decline installation
  of the separate **loopback-only** Kvin YXORP stage. Even if authorized,
  that is not production publication, DNS cutover, or application acceptance.
- [ ] After image qualification, independently authorize a loopback-only
  YXORP stage and real client routing acceptance; only later consider the
  separate production cutover. Kvar NPM must remain untouched until then.
