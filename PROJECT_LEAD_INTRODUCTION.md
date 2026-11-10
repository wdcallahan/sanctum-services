# Sanctum Services — Session Continuation

## Latest native acceptance — Peanut YXORP cross-host HTTP 200, Nov 9 ~19:10 CST

**Supersedes the "client probe pending" and "next run host-network deployment"
instructions below.** Nova actually ran `ansible/yxorp-peanut-probe.yml`
from Kvin. Native recap: **Kvin ok=4 changed=0 failed=0**.
Kvin contacted the *actual network listener* on
`http://peanut.arcane.sanctum:80`, confirmed the YXORP health response,
then sent `Host: yarn.nexus.sanctum` through Peanut and received
**HTTP 200**. The rootful host-network Peanut Quadlet is installed and
working to this level, and Kvar NPM and DNS were not cut over.
[Accepted runtime evidence](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6755992476).

**Next test only if worthwhile before cleanup:** confirm actual Yarn
page content from a normal client (Mace) via a request-only DNS
override, without editing authoritative DNS:
`curl --noproxy '*' --resolve yarn.nexus.sanctum:80:192.168.3.3 -i http://yarn.nexus.sanctum/`.
Do not claim full app/browser, all VLANs, login, Prism WebSocket or
failover acceptance from the 200 alone. No needless repeat of the
already accepted Kvin/Peanut HTTP probe.

**Next cleanup after trial checks:** run
`~/.local/bin/ansible-navigator run ansible/yxorp-peanut-remove.yml`
from the Services checkout on Kvin. It targets only the temporary
Peanut Quadlet/config and the marked runtime firewall exception; the
latter also expires four hours after the **original** add, not
the time of the most recent playbook. Persistent standby and eventual
Kvin production are separate pending lifecycle decisions. No Kvar or
authoritative DNS changes are authorized.


## Most recent accepted native result — Peanut YXORP running, Nov 9 18:59 CST

**THIS OVERRIDES HISTORICAL STAGING/PERMISSION/DNS-BLOCKER NOTES BELOW.**
Nova successfully ran the normal `ansible/yxorp-peanut.yml` from Kvin.
Full recap: **Peanut ok=40 changed=3 unreachable=0 failed=0
skipped=5**. The trial's temporary HTTP/80 permission was still active
(`public` zone), and was **not re-added/refreshed** in this run.
Disposable rootful Nginx config validation in host networking passed;
the validated config was published, the dedicated rootful Quadlet was
installed, systemd started its generated service, and local
`http://127.0.0.1:80/__yxorp_health` returned successful readiness.
**Peanut has a running YXORP test service on real LAN HTTP/80.**

**Next operator step:** Kvin network-client acceptance, using
`~/.local/bin/ansible-navigator run ansible/yxorp-peanut-probe.yml`
from the usual `~/src/sanctum-services` checkout. This actually
requests Peanut's health route and Yarn with the correct HTTP Host header
from Kvin; it has **not yet been executed**. Browser/app acceptance and
all legacy proxy routes remain separate. There is no DNS cutover, Kvar
NPM change, or Kvin production deployment authorization.

**Test cleanup:** `ansible/yxorp-peanut-remove.yml` stops/removes
the exact trial, validates ownership and cleans any remaining owned
runtime-only firewalld port exception. That permission expires **four
hours after its original addition** even if the container persists;
do not misdiagnose expired firewall admission as application failure.
Kvin and Peanut are actual service-host twins with intended redundancy;
this limited trial is not yet working reverse-proxy failover.

**Unrelated user request recorded:** all eligible machines should have
the `fortune` command via the normal Maintenance software baseline;
[Maintenance issue #21 comment](https://github.com/wdcallahan/sanctum-maintenance/issues/21#issuecomment-6755832483).
Kvin was installed manually by Nova; fleet-wide deployment is not yet done.


## November 9 current checkpoint — next actual operator decision

- Kvar Nginx Proxy Manager default-upstream and redacted behavior reports
  were run and accepted; **do not ask Nova to repeat them**.
- The official Nginx ARM64 digest is native-qualified on Kvin, and synthetic
  Nginx forwarding/WebSocket tests passed in CI. The exact known-good digest
  is still the selected image for **the first loopback-only stage**, not a
  sanctioned permanent image freeze.
- Source-only work fixed the Quadlet generated-systemd startup error (do
  **not** enable a generated transient service), prepared a read-only
  Kvin `ansible/yxorp-stage-probe.yml` for real Yarn forwarding and an
  explicit, guarded `ansible/yxorp-remove-stage.yml` removal path for
  the local stage. Kvar, DNS, firewall and production traffic untouched.
- **Pending Nova:** choose whether to authorize a *new persistent test*
  YXORP container on **Kvin 127.0.0.1:18080**. Approval is not production
  cutover or automatic updates. Source guard
  `yxorp_stage_approved: false` must remain until this decision.
- Image lifecycle requires the established two-sided cost calculation:
  compare a moving Nginx stable tag with Podman registry auto-update,
  readiness/actual client verification, rollback and observability against
  manually promoting pinned digests. The image channel and update cadence
  are not selected yet. Avoid pinning forever merely for reproducibility;
  avoid auto-updating merely because Podman makes it easy.
- The **full removal** of any production service eventually means
  dependency reconciliation (Maintenance DNS, proxy routes, client
  consumers, monitors, data retention) beyond removing a Quadlet.

**November 9 firewall gate resolved for the test only:** Nova executed the
native Peanut read-only port/firewall preflight on Kvin: `ok=11 changed=0
failed=1`, with exact target and free port80 verified, active firewalld
zone `public` but `http` service and TCP/80 denied. Nova authorized
**an ad hoc runtime-only exception** so the test needn't wait for
Maintenance's normal work to resume; he requires restoration afterward.
New `ansible/yxorp-peanut-trial-firewall.yml` adds only
`public:80/tcp` with `--timeout=4h` (no `--permanent`), records a
cleanup marker in `/run`, and is imported **before** the original
read-only preflight in `ansible/yxorp-peanut.yml`. The matching
`ansible/yxorp-peanut-remove.yml` removes the trial and its verified
runtime-only exception, and leaves Maintenance's permanent policy,
Kvar and DNS untouched. Peanut is Kvin's intended peer/future proxy
standby, not a disposable clone. The standby promotion/failover workflow
is later regular maintenance work, distinct from this test. The real
next operator action is running the updated `yxorp-peanut.yml` on Kvin
and returning the result; do not ask Nova to rerun the **old, unmodified**
read-only preflight for its own sake.

## Updated YXORP Peanut native frontier — host networking selected

Nova's rootful Podman bridge DNS observation passed unchanged:
host `getent` → `192.168.1.110`, bridge-to-Peanut BIND → `REFUSED`,
bridge-to-Kvin DNS → timeout. The authoritative BIND client ACL
is declared by Maintenance in `data/dns.yml` as loopback and
`192.168.0.0/16` only, with the same ACL applied to ordinary
queries/recursion/cache. Do **not** attempt `DNS=192.168.3.3`
alone; the attempted explicit bridge server already returned REFUSED.

Chosen minimal operational correction: both twin YXORP Quadlets
use `Network=host`, no unsupported `PublishPort`; disposable
`nginx -t` validation also uses `--network host`. This avoids
reconfiguring or restarting authoritative DNS and preserves
ordinary rootful HTTP port80 exposure. It does reduce the container's
network namespace isolation; revisit if specific needs justify
a dedicated bridged-network DNS allowance.

**Next operator:** on Kvin's Services checkout, `git pull` and
run `~/.local/bin/ansible-navigator run ansible/yxorp-peanut.yml`.
A temporary runtime port-80 firewall exception remains time-limited
and managed by the wrapper. Return the native test result. If the
trial succeeds, run `ansible/yxorp-peanut-probe.yml` from Kvin as
an independent HTTP client. No Kvin/Kvar cutover permitted.

## Latest native boundary — rootful Podman DNS, November 9

Peanut and Kvin are deliberately matched service-host twins, intended
for redundant DNS, backups, service mirrors and potential hot takeover.
Their incidental storage-size difference is not an architectural reason
to partition roles. Peanut is the proper real HTTP:80 YXORP trial host
and eventual Kvin proxy standby, not an unrelated spare.

Nova's retry passed the temporary firewalld port-80 admission and
Peanut preflight, created only the trial configuration directory,
rendered its candidate and pulled the official Alpine Nginx tag.
It failed **at the disposable rootful Podman bridge nginx -t**,
`host not found in upstream "yarn.inner.sanctum"`. **No Quadlet
was installed and no persistent proxy started.** The runtime-only
Peanut firewall opening expires automatically after four hours
(or via the scoped trial cleanup).

**Next actual native action:** run
`ansible/yxorp-peanut-dns-observe.yml` from the existing Kvin Services
checkout. This read-only scoped check compares Peanut's host getent
and the unchanged Podman bridge resolver with bridge queries explicitly
using both canonical DNS peers, `192.168.3.3` and `192.168.1.192`.
Do not assume this is an Nginx template bug or rush into hardcoded
Yarn addresses, host networking or new firewall rules. After actual
output, choose the minimal correct DNS fix and continue the same
Peanut port-80 trial.

## Current decision — Peanut is the realistic HTTP:80 YXORP trial (Nov 9)

Nova explicitly rejected the repeated localhost/18080 workaround. **The
commissioned Kvin production YXORP is rootful Podman, HTTP over
`0.0.0.0:80`, LAN-accessible via normal DNS after an approved cutover.**
The non-production test goes to **Peanut**, with the **same rootful,
all-interface port-80 architecture**, not an approximation on Kvin.
This direction supersedes older notes asking permission to stage on
Kvin loopback. No Kvar changes, DNS switch or production approval.

Services source now includes a dedicated `yxorp_test` group targeting
`peanut.arcane.sanctum`, `ansible/yxorp-peanut.yml` (first a read-only
socket/firewall check then deployment), `ansible/yxorp-peanut-probe.yml`
(actual Kvin network-client HTTP), and
`ansible/yxorp-peanut-remove.yml` (scoped test rollback). Peanut's
firewall is owned by Maintenance; the last accepted policy from
October 22 did not establish port-80 admission. Do not touch Maintenance
firewall policy from Services. The first **native** operator move after
source CI is to run the Peanut test play from Kvin; a preflight denial
must not be bypassed by weakening the firewall. See
[the revised runbook](docs/runbooks/yxorp-reconstruction.md).

The first Peanut trial uses multi-architecture Nginx
`docker.io/library/nginx:stable-alpine` (normal maintained tag) and
keeps Kvin's previously tested ARM64 digest as a known-good reference.
Automatic updates, consumer-side acceptance and actual app rollback
are not yet proven; never claim completion from `nginx -t` alone.

## Latest operator decisions — November 8, 2026

**Binding prior security decision: no blanket HTTPS requirement.** By October 20, Nova had explicitly accepted ordinary HTTP for private `.sanctum` applications, potentially permanently. Project Joule independently implemented Nova's selected HTTP Prism browser origin on October 16; see [its accepted HTTP transition](https://github.com/wdcallahan/joule/blob/main/docs/runbooks/prism-http-transition-2026-10-16.md). The assistant has repeatedly reopened HTTPS/CA as a new idea despite this decision. It is **not** an active project or prerequisite to YXORP, Kvin or VPN. Threats of plaintext secrets/sessions remain understood; a private CA's worst-case client enrollment may be impossible for Android apps with system-only trust or hard pinning. New PKI work requires a concrete functional/security need outweighing full trust-distribution cost, not vague conventional best practice. `.sanctum` is an intentionally settled private namespace; Nova deliberately abandoned a hybrid public/private scheme despite owning many domains. [Issue #3](https://github.com/wdcallahan/sanctum-services/issues/3) is closed/not planned to prevent re-litigation by default.

**Current source checkpoint (Nov 8):** Source-only [YXORP rootful Ansible/Quadlet](ansible/yxorp.yml), [declared proposed routes](data/yxorp-routes.yml), [Kuma rootless staged installer](ansible/kuma.yml), [Project Joule Wicket Ollama desired monitor](data/kuma-monitors.yml), and [read-only NPM report comparison](tools/review-yxorp-publication.py) are committed. [CI source validation with real Nginx parser passed](https://github.com/wdcallahan/sanctum-services/actions/runs/42562957639); this is **not** native staging, retained Kuma acceptance or Kvar cutover. Both image digests are intentionally blank; Kuma stage additionally requires explicit approval. Only Yarn is enabled in the draft proxy routes, which are not full NPM parity. Wicket monitor `http://wicket.arcane.sanctum:11435/healthz` must be installed and verified **Up** on accepted retained Kuma, not an old proof-of-concept. See [YXORP #2](https://github.com/wdcallahan/sanctum-services/issues/2) and [Kuma #4](https://github.com/wdcallahan/sanctum-services/issues/4).

**Next native Services blocker:** Kvar NPM's generated **behavioral** configuration remains unexamined beyond default upstreams. The new [read-only metadata observer](ansible/yxorp-inspect-npm.yml) passed [isolated CI tests](https://github.com/wdcallahan/sanctum-services/actions/runs/42677320762), including confidentiality tests and Ansible syntax. It targets Kvar's existing SSH management port **10022** and checks headers/directive names, custom snippets, extra locations, authentication/redirect indicators without outputting raw config values. Its run **has not occurred**; ask Nova to use `git pull --ff-only && ~/.local/bin/ansible-navigator run ansible/yxorp-inspect-npm.yml` from `~/src/sanctum-services`. Do not repeat the already completed default-upstream comparison. Then review real output; no production change is authorized.

**November 9 followup:** Nova successfully ran the Kvar read-only NPM behavior observer. Its eight observed generated proxy hosts showed no non-default locations and no nonempty global custom snippets, with explicit WebSocket headers on Nextcloud/Prism and TLS directives on old Prism. NPM's published templates explain the repeated optional custom include and `https` HSTS-map entry; the exact Kvar image has not been reverse-mapped, so real client parity remains open. [Evidence record](docs/review/2026-11-09-yxorp-behavior-observation.md).

**Current stage gate (November 9, after native qualification):** Nova executed `ansible/yxorp-qualify-image.yml` on Kvin; **ok=11 changed=4 failed=0**, exact official Nginx ARM64 digest pulled/cached, Podman image architecture and offline generated-config Nginx parser accepted, temporary file cleaned. No lasting service, Kvar, DNS or firewall change. Promoted this tested digest into `ansible/group_vars/yxorp.yml`, but added `yxorp_stage_approved: false` and made the install role assert it before any host mutation. A separate operator decision must precede starting a rootful Kvin proxy even on loopback port 18080; production cutover remains unapproved. Project Joule/Prism and old OpenWebUI WebSocket history is consistent with the explicit Upgrade headers found for Prism (OpenWebUI retired). Do not request a repeat qualifier to demonstrate idempotence. See [native receipt](docs/runbooks/yxorp-image-qualification.md).

**Additional Services operating doctrine:** "So let it be written, so let it be run." Treat automation and declared durable inputs—not manual web interfaces or remembered commands—as the reconstruction authority, consistent with the [canonical shared completion standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md). Rootless is not mandatory: **rootful Nginx/Quadlet for host ports 80/443** is the intended YXORP replacement, not an occasion to adjust global low-port privileges; SSH remains a native root-operated host service. Network security/firewall policy belongs to other owners. **HTTP remains explicitly accepted for internal services; no certificate infrastructure may be made a default dependency**. Existing NPM admin UI/db need not be migrated as features; actual routing and application semantics must be. See [architecture](docs/architecture.md) and [estate register](docs/SERVICE-ESTATE.md).

**Start with the [Services service-estate/decision register](docs/SERVICE-ESTATE.md) and [issue #2](https://github.com/wdcallahan/sanctum-services/issues/2)** for active reconstructibility work; older Kvar/Pi-hole/Endlessh descriptions below and in Maintenance snapshots are historical. Kvin's Kvar-replacement role was the original reason for its purchase years ago, not a newly chosen destination. **Pi-hole stays for ad blocking** but is not the general/authoritative DNS infrastructure. **OpenWebUI is retired in favor of Project Joule's Prism; Endlessh is retired** because its old public-SSH tarpit purpose no longer exists. **Prism belongs in the all-containers inventory but its install/recovery owner is Project Joule.** Tailscale is temporary; a proper VPN is **future Sanctum Services scope**, as are **Luanti** and **Home Assistant**. No intended WAN/publicly exposed inbound service ports. **Kvar retirement method:** no need to uninstall old OpenWebUI, Endlessh or each retired Kvar container; once every wanted service has been restored and independently accepted on Kvin, take Kvar offline and format/reimage it under Maintenance's host-retirement ownership and Nova's separate approval. Do not format it prematurely. None of these decisions authorizes immediate live deletion, migration, VPN cutover or router/firewall changes. Services maintains the canonical inventory and sends maintenance-only document corrections to Maintenance via the inter-Pixel board at [Maintenance issue #20](https://github.com/wdcallahan/sanctum-maintenance/issues/20).


## October 23 — controller cleanup ownership correction

Nova authorized the Maintenance session to handle this bounded Services tooling
command migration and qualification. The “3 Explore Nextcloud Together” chat is
for exploring and learning the application; it is not an active GitHub project
lead waiting on the message board. Do not invent an owner dependency on that tab.
Services now documents the normal-user Navigator and selects its existing EE in
project settings. The old Core2.19.14 environment recipe was unused and removed.
Read-only `ansible/qualify-controller.yml` is the native consumer check. It
passed before and after Maintenance's environment
removal on October 23. Both controllers completed retirement successfully; see
[the native receipt](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/qualification/2026-10-23-controller-venv-retirement-native.md). This does not deploy or reconcile Nextcloud, and Joule's
independent controller is outside this migration.

This is a **short handoff for the next assistant**, not a second design authority, an automatic project-lead appointment, or required reading for human operators. Nova's actual request appoints the scope of each session.

## Active handoff — October 20 firewall ownership transfer

[Services issue 1](https://github.com/wdcallahan/sanctum-services/issues/1)
is the current bounded task. Maintenance's native **read-only** Kvin firewall
preview and separate Pi-baseline no-change preview passed. Maintenance owns
ordinary 8084/5432/8085 service-port publication on Kvin; its live correction
has **not** been approved or applied. Services' Nextcloud role has now removed
its application-owned firewalld port-opening mutation and added an early,
**read-only** preflight checking `eth0`/`public` and **both runtime and
permanent 8085/tcp**. A missing prerequisite fails before Nextcloud file,
credential or service mutation and points to Maintenance's
[owner runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/kvin-service-firewall.md).
The cross-project installation/reconstruction sequence is documented in
[Services' Ansible README](ansible/README.md) and
[Town Square proxy runbook](docs/runbooks/town-square-yxorp-proxy.md).

No live firewall or Nextcloud deployment action is authorized by this source
transfer. Nextcloud **does** already run locally with `status.php` HTTP 200,
`installed=false`; previous "not installed" notes below are historical.
Next: source-qualify and post Services issue 1 implementation; Maintenance
reviews it and obtains Nova's separate approval before any live host change.
Do not run the old PostgreSQL deploy play or the full platform baseline.
The new general-purpose EE co-build with Nova remains a separate learning
goal, not a missing source-handoff approval.

## What this project is for

`sanctum-services` owns reproducible self-hosted application deployment, lifecycle operations, and recovery, beginning with Nextcloud. **The learning is a deliverable**: Nova wants real Ansible Navigator/EE practice, professional skill, and independent ability to understand and maintain the system. He does *not* want an opaque turnkey result.

**Joule tool-model correction (October 18):** Pixel mistakenly suggested Runner would need to enforce Joule permissions. No: Joule's established tool menu accepts a selected tool, inventory limit and supported arguments; the tool processes the **actual attempted action** and either runs it or returns denial/escalation instructions. Joule is scored on justified tool calls/arguments regardless of outcome, so even an inevitably denied attempt must be sent to the real tool; **no dry-run surrogate**. Runner may provide structured results **behind Ansible-backed tools**, not replace the existing tool boundary or grading. The first file-based Runner demo returned `failed` / `rc=250`, with diagnostics suppressed; cause undetermined. See [engineering log](docs/history/engineering-log.md), and do not treat that run as accepted success.

**Runner rabbit hole closed October 18:** After three unsuccessful
assistant-designed demonstrations, diagnostic output identified an
`awx_display` callback-loading exception caused by a likely nested Runner
initialization through Navigator. Nova verified that Navigator exports
`ANSIBLE_STDOUT_CALLBACK=awx_display`. He already understands Runner's value
as a job/results adapter for possible Joule Ansible-backed tools and questioned
the diminishing returns of repairing a disposable demonstration. **We agreed
to stop here; no further Runner demo or workaround is a prerequisite to the
base EE.** Runner itself and the qualified Maintenance EE have not been
established to be broken. Return to designing and building the minimal base
EE **with Nova participating**. The Ansible Core-first learning requirement
remains in force.

**Learning guardrail October 18:** Nova teaches **ordinary Ansible Core**, not Ansible Runner. He is not opposed to Runner being inside an EE, but is concerned that using Runner's interface in everyday project automation would erode the transferability of his practice to teaching. Keep Ansible inventories, roles, playbooks and usual CLI behavior as the **portable project contract**. Using Navigator to execute the same Ansible code in an EE is fine; writing project-specific Runner API/CLI/artifact dependencies is **not the default**. Runner's presence serves the EE/tooling layer, not a new coding model. This is a design constraint, not a request to delete Runner.

**Important correction on October 18:** Pixel said "We built our own!" about the Maintenance EE. Nova pointed out **he did not get to participate in creating it and wanted that experience**. Observing Navigator, running an ad hoc command, or merely pasting a Builder invocation is not equivalent to understanding and co-building the EE. Stage 1 now requires Nova to help design the new EE, inspect Builder-generated output, build it with Podman, and learn how to maintain, reproduce and uninstall it. Don't run ahead and produce a finished EE for him. The current [Maintenance recipe](https://github.com/wdcallahan/sanctum-maintenance/blob/main/execution-environment.yml) is useful as a reference, but its qualified image must stay intact.

**Four nonnegotiable properties from the start: documented, repeatable, understandable, uninstallable.** An application that merely runs has no initial value if it fails these. Explain nontrivial mechanisms before introducing them. Maintain human-facing explanations and validated procedures alongside code.

**Cross-session learning correction (2026-10-17):** Nova wants *situated teaching*: use the **simplest command needed now**, introduce a new flag or concept **only when a real operation makes it useful**, and explain its purpose at that moment. When he questions a switch, answer why **this task** needs it, not merely what the switch means. His willingness to continue copying commands is not proof of consent or comprehension. If he says he no longer understands the mechanism, revisit the architecture. These rules are now written into the [cross-project interface standard](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md), which requires that important corrections be saved DURING each working session. **For everyday Git sync, Nova explicitly chose ordinary `git pull` without `--ff-only` and without hidden equivalent config**; see the updated [Git standard](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md).

## Read only what you need

1. [README](README.md): newcomer introduction, honest state, and navigation.
2. [Roadmap](docs/ROADMAP.md): destination, decisions, current **YOU ARE HERE** milestone, acceptance tests, and next actions.
3. [Architecture](docs/architecture.md): intended data path, automation path, and ownership boundaries.
4. [Ansible source README](ansible/README.md): important warning that existing code is an **unaccepted candidate**, not approved instructions.
5. [Engineering log](docs/history/engineering-log.md): dated evidence and mistakes; consult selectively, never as a mandatory transcript.

When needed for the *active decision*, consult the current cross-project [Git](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md), [Ansible](https://github.com/wdcallahan/engineering-standards/blob/main/Ansible-Project-Engineering-Standard.md), [Operational Completion](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md), and [Nova–Pixel Interface](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md) standards. They are authoritative over this handoff; do not recreate a mandatory full-reading chain.

## Frontier through October 18, 2026

- Kvin and Peanut are the designated Ansible controllers. Kvin is the initial Nextcloud application host; Peanut is the proposed backup destination; Void is the eventual file-storage destination. Kvin's first host-port mapping is **8085 → Nextcloud Apache 80**; YXORP will provide the stable client-facing service name.
- Source: Ansible role and Quadlet candidate on `main`; **no application deployment**. Nova installed `ansible-core==2.19.14` into a project venv and passed **direct-Ansible syntax-check** on Kvin. That is syntax evidence only.
- **Mistake to repair:** per-project venv/direct-Ansible was not the requested Navigator/EE learning workflow. The original inventory used `ansible_connection: local`, which would target an **EE container, not Kvin**. Nova chose ordinary **Ansible smart/SSH**, explicitly allowing Kvin's controller to SSH back into Kvin; the inventory override was **removed on main**. **Actual Kvin→EE→SSH→Kvin ad hoc ping passed October 18 using Maintenance's existing EE**. Rootless user-systemd control for the Nextcloud role is **not** tested. The remaining runtime design still needs review and correction, not a concealing wrapper.
- Existing application code has **no qualified deployment, backup/restore, normal operation or clean uninstall**. The original application README's deploy commands were withdrawn. The exact dates/observations are in the engineering log.
- The current active milestone is **Roadmap Stage 1**: explain and establish a supported shared Navigator/EE/controller workflow, including the infrastructure owner and an explicit managed-host connection. No deployment until proven and understood.

## Working contract

- Stay in this project's ownership boundary. Existing PostgreSQL, YXORP, network registry, OS maintenance, and shared controller runtime belong to their actual owning projects. Don't treat integrations as permission to change them.
- **Active-session checkout boundary — Nova correction October 18:** Even when we tentatively agree that another project (e.g. `sanctum-maintenance`) is the long-term **owner** of an artifact, that does **not** authorize this session to create files, do Builder experiments, or edit GitHub planning documents in that project's active working tree/repository. We instructed Nova to create `ee/base` inside his Maintenance checkout, producing unexpected `?? ee/` during Maintenance's own `git status`; Nova deleted those untracked experiment folders because they interfered with its working session. Earlier direct edits to Maintenance's roadmap were likewise uncoordinated. **Do not touch Maintenance's working tree or remotely mutate its GitHub repo again without the active Maintenance session's permission**; do not autonomously revert the earlier docs. Keep exploratory EE building in an explicitly agreed *isolated* workspace outside all actively managed checkouts; when ready, hand off the proposal/artifact to the authorized project owner. Ownership, implementation location and permission to change active state are separate questions.

- Work directly on linear `main`, without default branches or PRs. Preserve unfamiliar local work, and distinguish source, syntax check, actual live run, and accepted operating result.
- Use **Podman Quadlets**, not Docker Compose. Seek Nova's decision before consequential changes to shared infrastructure, data, or exposure. Never store credentials in public plaintext Git.
- Treat supported host-side Navigator tooling and the EE as distinct: the EE has Ansible and collections; Navigator launches it. Shared tooling should not be duplicated into each service without reason.
- Keep this handoff short. The **roadmap** owns milestones, **architecture/runbooks** own explanation and operation, and **engineering log** owns events. Update each at the same time as meaningful code/decisions.
- This is chat-based work with Nova operating Kvin/Peanut terminals as needed. There is no automatic background continuation.

**Architecture decision October 18:** Nova agreed provisionally to let [Sanctum Maintenance's controller-infrastructure workstream](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md) own the shared host-side Navigator/Builder tools and a **new, separately named general-purpose EE** for applications. This is a coherent ownership default, not proof that there are no alternatives or approval to rebuild Maintenance's qualified EE. The existing Maintenance EE stays untouched. Nova **must participate** in designing and building the new EE; do not do that work for him.

**EE composition ACCEPTED October 18:** After a full architecture comparison, Nova answered **yes, fully understood** to the layered model: (1) centrally owned minimal Ansible EE foundation, (2) unchanged, digest-pinned reuse when adequate, and (3) project-specific derivative only when extra dependencies warrant one, separately pinned and tested. This is **not** a single giant universal EE or one needless image copy per project. Red Hat's ee-minimal/custom-EE guidance supports the approach. Builder derivative details (notably avoiding duplicate Core/Runner installation when the base is already populated) still require inspection. The agreed design does **not** mean any new tooling or images are yet deployed. **Do not ask for architectural approval again.** [Owning controller design](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md); [application roadmap](docs/ROADMAP.md).

## Smallest next step

Ownership of the shared controller tools and EE foundation is provisionally Sanctum Maintenance, and the layered base/derived EE architecture is **explicitly accepted**; **do not ask Nova to decide either again**. Next co-design the base's minimum required contents and the first consumer's dependencies with Nova, explaining Builder inputs during the real build. The Maintenance EE's read-only **smart/SSH to Kvin** ping succeeded already, so **do not repeat it**. Nova already teaches ad hoc Ansible and only needs the *new* Navigator-specific `exec -- ansible …` relationship explained. Investigate the supported host-side Navigator/Builder installation options and the appropriate owner for a reusable shared toolchain before creating or installing anything; then qualify its own EE and remote connection. Record design before repairing the initial application candidate. The roadmap is the authoritative current progress map; verify newer source and live evidence before acting.

**End condition for a useful handoff:** Nova can tell what is accepted, what failed or is still proposed, and who has the next action, without searching chat history.
