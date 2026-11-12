# Sanctum Services — Session Continuation

## November 11 native Kvar receipt — both live survivors, image identity metadata incomplete

Nova ran `ansible/kvar-survivors-source.yml` on Kvin against Kvar, **`ok=8 changed=0 failed=0 unreachable=0`**. Each named service was confirmed **running**, Quadlet `loaded/active/generated`, with source files on Kvar. No application state, passwords or volume contents were read and no host/app configuration was changed.

| Service / account | Running container image reference and observed image ID | Writable volumes | Kvar published ports |
|---|---|---|---|
| Rootless `linkstack`, `wdc2` | `docker.io/linkstackorg/linkstack:latest`; `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65` | `linkstack` → `/htdocs` | TCP 8081 → 80 |
| Rootful `pihole`, `root` | `docker.io/pihole/pihole:latest`; `edb7f703649f4b6ab8b14f28d12f15e8cbe1c50a2092458e9b640bd6bc6fe59e` | `systemd-pihole_etc-pihole` → `/etc/pihole`, `systemd-pihole_etc-dnsmasq` → `/etc/dnsmasq.d` | TCP/UDP 53 → 53 and TCP 82 → 80 |

Both bounded results had `status: partial`, although `service_unit.status: observed`. The reason is the **additional local image inspection did not yield accepted `image_platform` and `repo_digests`**, not that either container is unavailable. `latest` is mutable and the displayed container image ID is **not** proof of a Kvin-pullable immutable reference. No image pull, service restart, backup, data movement, DNS or proxy change is authorized by this observation.

**Follow-up source correction:** `tools/observe-kvar-survivors.py` now explicitly reports only sanitized image-inspection outcome categories. It first queries the exact observed container image ID; if unavailable, it tries the existing local image tag, **accepting that result only if its image ID equals the running container's ID**. A newer local `latest` tag must not be used to reconstruct the wrong image. A missing repository digest remains `partial`. The updated source tests cover all of these failure modes. Once CI is green, the next read-only native rerun can report a specific image-probe result rather than an unexplained `partial`. Do not re-run any broad retirement inventory.

## CURRENT — November 11: Kvar LinkStack + Pi-hole read-only recovery-source observer CI GREEN; native inputs next

**Next single Kvin operator action:** The existing Maintenance inventory already established rootless Kvar LinkStack's persistent `linkstack` volume at `/htdocs` and rootful Pi-hole's two config volumes. No need to repeat broad inventory. Services source now provides `ansible/kvar-survivors-source.yml` and `tools/observe-kvar-survivors.py` to inspect **only** the two wanted services in the proper distinct privilege namespaces on old Kvar. It reports bounded selected image reference/id/digest, ports, mount destination/volume names and safe service/Quadlet source status, suppressing raw inspection, environment, content and credentials. Both plays are read-only and have no rollout, backup, data access or app mutation. Source tests and full Services CI [#43126902608 **PASSED**](https://github.com/wdcallahan/sanctum-services/actions/runs/43126902608); **no native Kvar observation yet**.

One command **on Kvin**, using the current Services inventory and logged-in Navigator:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kvar-survivors-source.yml
```
Return the single aggregate Kvar **PLAY RECAP** row and bounded `Report bounded LinkStack image and backing discovery` and `Report bounded Pi-hole image and backing discovery` `msg` dictionaries (or failed task). `partial` means input unknown, not failure to report. Read [docs/runbooks/kvar-survivor-recovery-inputs.md](docs/runbooks/kvar-survivor-recovery-inputs.md). This is a **real host evidence boundary**; do not choose images or design a live restore from speculation. Kvar NPM and all apps remain running. After native evidence, prepare owned consistent backups, isolated Kvin restores and actual client acceptance separately.

## CURRENT — November 11: Mace Firefox Kuma WebSocket upgrade 101 ACCEPTED; Kuma initial production client gate CLOSED

**Actual Mace Firefox evidence:** Nova supplied the Firefox DevTools Network **WS** screenshot for `kuma.nexus.sanctum`, showing `GET /socket.io/?EIO=4&transport=websocket&sid=...` with **HTTP 101 Switching Protocols**. This is the actual browser's successful Engine.IO/Socket.IO WebSocket upgrade through Kvin production YXORP. Earlier on the same production named route, Mace resolver returned `192.168.0.192`, the existing `sanctum-admin` application login succeeded, and the `Wicket Ollama` dashboard monitor visibly reported **Up / 100% uptime**.

**Acceptance:** Kuma **initial named-client production browser/login/meaningful monitor/WebSocket upgrade** gate is accepted. The 101 directly proves protocol upgrade, not indefinite session stability or every Socket.IO message; no gratuitous further probe necessary to accept this bounded gate. Continue later with other Nexus application name/session checks, full application estate recovery, and Maintenance-main reconciliation of source DNS aliases (old broad-renumber source still assumes Kvar). **Do not retire Kvar NPM.** Existing separately prepared DNS rollback candidate remains available for separately gated use if genuine regression appears. Do not copy a screenshot's Socket.IO session-id/query data into issue notes.

## CURRENT — November 11: Mace Kuma dashboard monitor UP at 100%; live browser Socket.IO still to verify

**New user-visible browser acceptance:** From the normal Mace Firefox session already authenticated through Kvin YXORP at `http://kuma.nexus.sanctum`, Nova confirms the **`Wicket Ollama` monitor is visible and reports Up with 100% uptime**. Combined with Mace name resolution to `192.168.0.192` and the successful `sanctum-admin` login, this accepts **named-client DNS, real proxy/browser authentication, and meaningful monitor state being displayed**. The 100% displayed figure is the app's uptime metric, **not proof that the Socket.IO WebSocket upgrade occurred or stays connected**; require an observed client-side WebSocket exchange for that specific remaining gate. Preserve Kvar NPM as rollback; no source or live infrastructure mutation requested by this browser observation.

**Next one browser-only observation:** In Mace Firefox DevTools Network, inspect WebSocket requests during a Kuma page reload for `socket.io` traffic/101 Switching Protocols and continuing frames (without sharing tokens, frames, or credentials). If Socket.IO remains polling or no 101 appears, classify separately rather than assuming Nginx failure. Then independently check other named application routes and reconcile Maintenance main with the successful DNS promotion.

## CURRENT — November 11: Mace named client and Kuma browser login ACCEPTED; Socket.IO/UI monitor acceptance next

**Operator-confirmed live browser evidence:** On `mace`, `getent ahostsv4 kuma.nexus.sanctum` returned Kvin's live YXORP destination **`192.168.0.192`** (STREAM/DGRAM/RAW); ordinary Firefox reached the Uptime Kuma login and Nova **logged in successfully** using the existing application administrator. **Real Mace DNS resolution, named HTTP browser reachability and Kuma authenticated login are accepted.** User has not yet reported whether `Wicket Ollama` monitor is visible/Up in this browser or whether the UI maintains authenticated Socket.IO/WebSocket updates. Do not silently graduate browser login into WebSocket acceptance.

**Human interface correction:** The password chosen through `tools/kuma-set-vault-password.sh` is the Kuma application's `sanctum-admin` password, NOT the separate `vault.key` password. Nova was not given the account username when the first operator credential setup instructions were provided, and reasonably thought the entered password was for Vault. Corrected [Vault runbook](docs/runbooks/vault-credentials.md) and Kuma guide explicitly state **browser URL, login name, password purpose, and distinct Vault key**. Nova kept the password in Bitwarden and has authenticated. Do **not** request it in chat, create/reset the admin, or change Vault material. Next request the **visible Wicket monitor state / continuing UI behavior**, then consider further real-client WebSocket proof and non-Kuma app checks. Keep Kvar NPM for fallback.

## CURRENT — November 11: live guarded Peanut six-Nexus DNS publication ACCEPTED; named client acceptance NEXT

**New native operator receipt (23:32Z):** Nova ran the previously accepted exact Maintenance release packet `artifacts/yxorp-dns-release-0858020` with `sanctum_publish_dns_zones=true`, `sanctum_yxorp_dns_publish_approved=true`, target `peanut.arcane.sanctum`, **without `--check`**. Report `Report bounded proxy DNS candidate scope and publication gate` returned **`check_mode:false`**, **`published_change_accepted:true`**, `candidate_serial:2026111101`, prior served forward/reverse SOA `2026101904`, both zone-file changes true, six proxy aliases directed to Kvin **`192.168.0.192`**, `old_npm_administration_address_retained:true`, `db_and_nonproxy_addresses_retained:true`, `reverse_ptr_records_unchanged_in_source:true`, `production_proxy_or_app_changed:false`, `real_named_client_sessions_and_websocket_accepted:false`. Actual play **`ok=18 changed=3 unreachable=0 failed=0 skipped=0`**, Navigator exit0, run completed. Private logged transcript: `artifacts/transcripts/publish-yxorp-nexus-dns-2026-11-11T23-32-01Z.log` and matching `.json`.

**Publication is ACCEPTED** on authoritative Peanut, based on the full play and publisher's guarded real authoritative postchecks; do not claim browser, login/session or Socket.IO from it. Kvar NPM remains running, old admin DNS preserved for rollback. The separate Maintenance rollback source candidate at `f7461ee84d13439e92e07037858b6828840a94d6` / `yxorp-dns-rollback-20261111`, desired SOA `2026111102`, has passing source CI but has NOT been natively previewed or executed.

**Next operational gate:** verify normal client resolver answers for relevant named Nexus routes, real browser login/session (particularly Kuma), and Kuma Socket.IO/WebSocket behavior. If client acceptance fails, classify DNS cache/client route/application issue; keep Kvar NPM intact and use separately previewed/authorized higher-serial rollback only if required. After client acceptance, reconcile the scoped DNS change with Maintenance main's older, incompatible broad renumber assumptions. Do not treat old YAML main source as safe to republish yet.

## PREVIOUS — November 11: Peanut DNS PREVIEW accepted; live guarded six-Nexus publication next

**Native Maintenance DNS preview result ACCEPTED:**
Nova ran exact immutable Maintenance scoped DNS candidate
`0858020065777070bf6e9a36b0d0f3056f7f5334`
from the extracted `artifacts/yxorp-dns-release-0858020`
packet, existing `tools/run-ansible-logged`,
target `peanut.arcane.sanctum`, `--check --diff`,
`sanctum_publish_dns_zones=true` and
`sanctum_yxorp_dns_preview_approved=true`.
Native `ok=10 changed=1 unreachable=0 failed=0
skipped=8`; Navigator exit0; run completed.
Bounded report `check_mode:true`,
`published_change_accepted:false`,
`candidate_serial:2026111101`,
`served_forward_serial_before:2026101904`,
`served_reverse_serial_before:2026101904`,
`forward_zone_file_would_change:true`,
`reverse_zone_file_would_change:true`,
`changed_proxy_alias_count:6`,
`proxy_target_ipv4:192.168.0.192`,
`old_npm_administration_address_retained:true`,
`db_and_nonproxy_addresses_retained:true`,
`reverse_ptr_records_unchanged_in_source:true`,
`production_proxy_or_app_changed:false`,
`real_named_client_sessions_and_websocket_accepted:false`.
Private controller transcript
`artifacts/transcripts/publish-yxorp-nexus-dns-2026-11-11T22-58-41Z.log`.
No native publication or DNS mutation yet.
**Both SOAs are below proposed new serial, and
the scoped source CI #43115349084 was green.**
No unexpected diff was reported by operator,
but the bounded msg itself does not contain
the actual zone-file diff; do not invent
byte-for-byte installed zone equality.

**Next one native operator command — LIVE six-record DNS publication:**
Use the exact already extracted Maintenance packet,
NOT active main:
```bash
cd ~/src/sanctum-maintenance &&
packet=artifacts/yxorp-dns-release-0858020 &&
tools/run-ansible-logged run \
  "$packet/playbooks/publish-yxorp-nexus-dns.yml" \
  -i "$packet/inventories/production/hosts.yml" \
  --limit peanut.arcane.sanctum \
  -e sanctum_publish_dns_zones=true \
  -e sanctum_yxorp_dns_publish_approved=true
```
Do **not** add `--check`, and don't set
`sanctum_yxorp_dns_preview_approved`.
This is intentional live Peanut zone
install/reload for five explicit
`dir/joule/kuma/pihole/search.nexus`
A records and `*.nexus`, mapping
from Kvar `192.168.0.7` to peer-qualified
Kvin `192.168.0.192`.
It uses owner SOA advancement guard,
BIND `named-checkzone` validation,
preexisting-file backups,
per-zone `rndc reload` with
served-serial verification, and live
authoritative `dig` checks of all six
plus old `yxorp.nexus` on Kvar.
If failure, DO NOT assume half-applied
DNS; inspect where it stopped and
preserve fallback. Return native
PLAY RECAP, bounded `Report bounded
proxy DNS candidate scope and publication gate`
msg, or failed task. **No
live cutover acceptance until actual
named client, session/Socket.IO tests.**
Kvar NPM remains running; rollback
requires republishing six old A records
with new (strictly advancing) SOA serial,
not merely copying an older zone.

**Already accepted:** Kvin production
8-route YXORP `ok=31 changed=0`,
Kuma proxy 302, Yarn proxy 200;
Maintenance live TCP80 with no-diff
repeat; Peanut independent
`192.168.0.192` Kuma302/Yarn200
`ok=5 changed=0`.
No `192.168.1.192` Kvin proxy reachability
from Peanut; do not use it for proxy DNS.
Kvin Kuma Vault admin, Wicket Up, isolated
app restore accepted; off-host backup and
external Vault recovery remain outstanding.
Two-bear cross-monitor Kvin+Peanut is
longstanding plan. Main Maintenance branch
still has older whole-network cutover alias
assumptions; after native DNS success
reconcile carefully rather than lose
source of truth.

## CURRENT — November 11: Peanut independently reaches Kvin YXORP via 192.168.0.192; six-record DNS release preview NEXT

**Native Peer HTTP acceptance (banked):**
Nova ran Services `ansible/yxorp-kvin-peer-http.yml` on
actual Peanut: **`ok=5 changed=0 unreachable=0 failed=0`**.
`observer:peanut.arcane.sanctum`,
`proven_non_kvin_http_reachability:true`.
To `192.168.0.192:80`, real
`Host:kuma.nexus.sanctum` returned **HTTP302**
and `Host:yarn.nexus.sanctum` returned
**HTTP200**; `qualified_http:true`.
To the separately assumed `192.168.1.192`,
both returned `transport_error` (not an HTTP
response), `qualified_http:false`.
Peanut's real `kvin.outer.sanctum`
DNS resolved to **`192.168.0.192`**.
`configuration_changed:false`,
`kvar_or_dns_or_firewall_changed:false`.
The Kvin production host and TCP80 are
**independently reachable from the Arcane peer**.
The old Peanut health-check assumption about
`192.168.1.192` is stale for this use
and must not silently redirect the proxy
cutover to the unreachable address.
This does NOT qualify all client subnets,
real Nexus DNS, login or WebSockets.

**DNS release preparation owned by Maintenance:**
Maintenance's old broad core renumber candidate
still treats these proxy aliases as Kvar-owned.
To avoid modifying main or conflating this
proxy-only release with that unfinished
core-network transaction, created exact
review branch `yxorp-dns-release-20261111`
at **commit
`0858020065777070bf6e9a36b0d0f3056f7f5334`**
([source](https://github.com/wdcallahan/sanctum-maintenance/commit/0858020065777070bf6e9a36b0d0f3056f7f5334)).
This changes **only** five explicit records
`dir.nexus`, `joule.nexus`,
`kuma.nexus`, `pihole.nexus`,
`search.nexus`, plus `*.nexus`
from Kvar `192.168.0.7` to
Kvin `192.168.0.192`. Source SOA
serial is proposed **`2026111101`**;
publisher refuses if it is not
newer than BOTH real served zone serials.
`yxorp.nexus` old NPM admin remains at
Kvar; all direct DB aliases, host, Yarn,
PTR records and all other DNS authority
stay unchanged. The candidate branch
source has a separately gated
`playbooks/publish-yxorp-nexus-dns.yml`
that reuses Maintenance's original
SOA-gated, BIND-validated,
backup-preserving, zone-reload publisher.
Preview requires `--check --diff` plus
`sanctum_publish_dns_zones=true` and
`sanctum_yxorp_dns_preview_approved=true`.
A **different** `sanctum_yxorp_dns_publish_approved=true`
is required for future live publication.
**Dedicated CI #43115349084 PASSED**
(BIND `named-checkzone` on both real
rendered source variants, exact-six and
nonproxy/PTR preservation tests and
Ansible syntax).
No source/main worktree update, no
Peanut zone publication or DNS client
change yet.

**ONE next Kvin operator step:**
Fetch the exact candidate branch revision into
ignored `~/src/sanctum-maintenance/artifacts/`
without altering active Maintenance main,
then run exact staged candidate DNS
`--check --diff` preview against Peanut,
using the existing owner
`tools/run-ansible-logged`.
Full commands and acceptance in
[docs/runbooks/yxorp-production-cutover.md](docs/runbooks/yxorp-production-cutover.md).
Return only `PLAY RECAP`,
`Report bounded proxy DNS candidate scope and publication gate`
msg, and any failed task / unexpected
zone-file diff. If real served serial
is not below 2026111101 or installed
zone content differs beyond six
desired A aliases and expected SOA serial
bump, HOLD and repair the source candidate.
Do NOT run live DNS publication before
native preview passes.
After owner DNS publication: verify actual
named client answers, browser login,
WebSocket, and fallback on old Kvar NPM.
On full native success, reconcile source
candidate back to Maintenance main and
its independent core-renumber assumptions,
rather than leaving live DNS with an
unreconciled main source-of-truth.

**Already native accepted:** Kvin rootful
production YXORP 8 routes, no-change
repeat `ok=31 changed=0 failed=0`;
Maintenance TCP80 live apply and
empty runtime+permanent diff on repeat;
new Kvin Kuma Vault admin, actual Wicket
Up and isolated backup/restore. Independent
two-bear Kvin+Peanut design is not new.
Off-host Kuma data+Vault independent
recovery still open.

## CURRENT — November 11: owner Kvin TCP80 firewall repeat has EMPTY diff; independent Peanut LAN HTTP test NEXT

**Native Maintenance firewall report (subsequent LIVE-repeat):**
Nova supplied the exact bounded task
`Show the exact firewall-only preview` from the
same staged reviewed source
`3ba9523befe229af2262194a615c3bc35da5aa01`,
`check_mode:false`, `zone:public`,
`interface:eth0`, **`would_change:false`**,
with **both `runtime.add_ports:[]` and
`permanent.add_ports:[]`**, and
**both `remove_rich_rules:[]`**.
This establishes the OWNER DESIRED FIREWALL
STATE now matches both live/permanent policy.
**The overall PLAY RECAP for this repeat
was not supplied**; do not invent its
`changed` or `failed` counters.
Previous actual native TCP80 apply
`ok=28 changed=1 failed=0 skipped=1`
and its full PostgreSQL/firewall preservation
were already accepted. No firewall further
changes requested.

**Next independent LAN path:** Services source
`ansible/yxorp-kvin-peer-http.yml`
runs on actual **Peanut** via existing
`yxorp_test` inventory while dispatched
from Kvin; no role or Podman mutation.
`tools/observe-yxorp-kvin-from-peanut.py`
checks both known potential Kvin addresses
`192.168.0.192` and `192.168.1.192`
with the exact production Kuma + Yarn
HTTP Host headers, plus the Peanut-visible
resolved address for `kvin.outer.sanctum`.
It emits statuses and a strict peer
reachability boolean without raw pages,
headers or authentication secrets.
**Why both?** Maintenance's authoritative
`data/dns.yml` currently maps
`kvin.outer` / DB aliases to
`192.168.0.192`, while Peanut's
`host_vars` health check expects
Kvin on `192.168.1.192`.
This conflict predates the YXORP release
and must be resolved by REAL peer wire
evidence, not assumptions. The probe
will NOT change DNS, the firewall, Kvar
or the production Nginx. **Native acceptance
not yet run.** Verify Services source CI
#43113767966 green before invocation.

**One next operator command after CI:**
```bash
cd ~/src/sanctum-services &&
git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-peer-http.yml
```
Return the peer `PLAY RECAP` plus
`Report safe Peanut LAN reachability
and exact Kvin address candidates` msg.
If neither candidate succeeds, hold DNS
and repair actual LAN routing/firewall
based on result. If one works, use
that as a real observed candidate
for Maintenance source-owned DNS
planning; **do not immediately change
names solely on anonymous GET success**.
Kvar NPM remains intact, and
real browser/Socket.IO access is next.

**Already accepted:** Kvin rootful YXORP
8 configured routes, `ansible/yxorp.yml`
`ok=31 changed=0 failed=0`,
Kuma frontend HTTP302, Yarn HTTP200,
local listener acceptance. Kvin Kuma
actual Wicket Up, Vault admin,
and isolated application restore.
Existing two independent Kuma bears
Kvin+Peanut design unchanged.

## CURRENT — November 11: Kvin live TCP80 firewall APPLY accepted; unchanged repeat next; DNS still Kvar

**Native Maintenance owner application accepted.**
Nova applied exact reviewed `wdcallahan/sanctum-maintenance`
revision `3ba9523befe229af2262194a615c3bc35da5aa01`
from the already staged source packet
`artifacts/kvin-firewall-source-3ba9523b`
using `tools/run-ansible-logged` with explicit
`sanctum_service_firewall_apply=true` and
`--diff` (without `--check`).
`ok=28 changed=1 unreachable=0 failed=0 skipped=1`,
Navigator exit 0, log status completed.
The bounded `Show the exact firewall-only preview`
report had `check_mode:false`, `zone:public`,
`interface:eth0`, and **exactly
`80/tcp` added** in runtime and permanent
plans, `remove_rich_rules:[]` in both.
All preservation/verification tasks passed,
including the PostgreSQL identity/hashes
and full firewall boundary. The `would_change:true`
field describes the state *before* this apply,
not an unmet postcondition. Private artifact:
`.../artifacts/service-firewall/20261111T220356580373Z`;
transcript `artifacts/transcripts/configure-kvin-firewall-2026-11-11T22-03-55Z.log`.
**Live firewall TCP80 application accepted.**

**Next ONE native action:** Repeat only
the same Maintenance owner play from the same
staged packet with `--diff`,
`sanctum_service_firewall_apply=true`, exact
source revision, no `--check`. Expect
`changed=0`, `failed=0`, both store
`add_ports:[]` and `remove_rich_rules:[]`,
and the same PostgreSQL state boundary.
```bash
cd ~/src/sanctum-maintenance &&
revision=3ba9523befe229af2262194a615c3bc35da5aa01 &&
packet=artifacts/kvin-firewall-source-3ba9523b &&
tools/run-ansible-logged run "$packet/playbooks/configure-kvin-firewall.yml" \
  -i "$packet/inventories/production/hosts.yml" \
  --limit kvin.outer.sanctum --diff \
  -e "sanctum_service_firewall_source_revision=$revision" \
  -e sanctum_service_firewall_apply=true
```
Ask for PLAY RECAP and bounded
`Show the exact firewall-only preview`
and final `Report the saved boundary evidence
and remaining independent acceptance` results,
or failed task. Do not ask to repeat stage
removal, proxy deployment, prior firewall preview.
Then test real Kvin HTTP80 from independent
LAN observer (Peanut), then Maintenance-managed
six Nexus DNS aliases/wildcard update with new
SOA serial, keeping Kvar NPM intact for rollback.

**Already native accepted:** YXORP production
`sanctum-yxorp.service`, eight routes,
Kuma HTTP302, Yarn HTTP200,
`ansible/yxorp.yml` repeat
`ok=31 changed=0 failed=0`.
Kvar's effective Nexus DNS is NOT moved.
Kvin Kuma Vault admin/Wicket Up and isolated
restore accepted. Off-host copy/Vault recovery
and browser/WebSocket tests remain open.
Original two-bear independent Kvin/Peanut
monitoring plan unchanged.

## CURRENT — November 11: Maintenance exact-source Kvin TCP80 check-mode preview ACCEPTED; next LIVE owner apply

**Native Kvin latest operator receipt:** With the exact staged owner source
`sanctum-maintenance` revision
`3ba9523befe229af2262194a615c3bc35da5aa01` under
`artifacts/kvin-firewall-source-3ba9523b`, Nova ran the approved
`tools/run-ansible-logged` preview of
`playbooks/configure-kvin-firewall.yml`, production inventory and
`--limit kvin.outer.sanctum --check --diff`.
It completed `ok=28 changed=1 unreachable=0 failed=0 skipped=1`,
`ansible_navigator_exit_status=0`, `Run status: completed`.
The safe `Show the exact firewall-only preview` proves
`check_mode:true`, `zone:public`, `interface:eth0`,
**exactly `80/tcp` added** in both
`diff.runtime.add_ports` and `diff.permanent.add_ports`,
and `remove_rich_rules:[]` in both stores.
All other formerly proposed firewall ports/rich-rule removals
have already converged. `changed=1` is a check-mode
prediction; **no live firewall mutation** occurred.
Private report:
`/home/wdc2/src/sanctum-maintenance/artifacts/kvin-firewall-source-3ba9523b/artifacts/service-firewall/20261111T215350954580Z`.
The native play passed its PostgreSQL hash/state preservation checks.
Kvar NPM and live Nexus DNS remain unchanged.

**Next operator action, separately approved LIVE firewall convergence**
with the **same exact reviewed packet** (NOT a `git pull` of the
active Maintenance controller checkout):
```bash
cd ~/src/sanctum-maintenance &&
revision=3ba9523befe229af2262194a615c3bc35da5aa01 &&
packet=artifacts/kvin-firewall-source-3ba9523b &&
tools/run-ansible-logged run "$packet/playbooks/configure-kvin-firewall.yml" \
  -i "$packet/inventories/production/hosts.yml" \
  --limit kvin.outer.sanctum --diff \
  -e "sanctum_service_firewall_source_revision=$revision" \
  -e sanctum_service_firewall_apply=true
```
This intentionally changes Kvin's **public/eth0 runtime+permanent
TCP80** and should change no other firewall policy or PostgreSQL.
Stop on failure; inspect bounded `Show the exact firewall-only preview`
(now `check_mode:false`), `Report the saved boundary evidence and
remaining independent acceptance`, and PLAY RECAP. After success,
repeat same LIVE playbook unchanged and seek `changed=0`.
Only then verify TCP80 from a separate LAN vantage and move
six Maintenance-owned Nexus DNS aliases/wildcard from Kvar to Kvin
with increased served SOA serial. No DNS source edit or
publication is currently accepted.

**Already accepted:** source-managed eight-vhost Kvin
`sanctum-yxorp.service` native second run
`ok=31 changed=0 failed=0 skipped=1`,
`local_production_listener_accepted:true`,
Kuma 302, Yarn 200. Kvar NPM stays current.
Kvin Kuma Vault admin, real Wicket Up, isolated
data restore accepted; off-host archive/Vault recovery still open.
Two independent Kuma peers (Kvin and Peanut) remain preexisting design.

## CURRENT — November 11: source-owned Kvin production YXORP 8/8 listener ACCEPTED NATIVE, no DNS/firewall publication

**Native operator report, November 11:** After
the earlier initial Yarn timeout and an independent
read-only Kvin production routing diagnostic
(returning HTTP200 for both Yarn Host names and
HTTP302 for Kuma), Nova repeated **only**
`ansible/yxorp.yml` with
`yxorp_production_cutover_approved=true`.
**`ok=31 changed=0 unreachable=0 failed=0 skipped=1`.**
Bounded
`Report bounded Kvin YXORP production listener readiness`:
`local_production_listener_accepted:true`,
`production_service:sanctum-yxorp.service`,
**`produced_route_count:8`**,
`kuma_target:127.0.0.1:13001`,
**`kuma_frontend_http_response:302`**,
**`yarn_frontend_http_response:200`**,
`kvars_existing_npm_changed:false`,
`firewall_changed:false`,
`dns_changed:false`,
`real_named_lan_client_accepted:false`,
`websocket_sessions_accepted:false`.
This **accepts the real rootful Kvin production
listener and unchanged source-managed convergence**,
not yet LAN reachability or hostname switchover.
Do not rerun stage removal, stage canaries, Yarn
diagnosis or production deploy just for reassurance.
The prior Yarn first-run timeout remains a recorded
historical transient, not a source defect.

**Next dependency: Maintenance-owned TCP80 firewall.**
The exact reviewed owner source at
`wdcallahan/sanctum-maintenance` revision
**`3ba9523befe229af2262194a615c3bc35da5aa01`**
adds ordinary `80/tcp` to preexisting
`5432/8084/8085` in `eth0` / `public`
and retains the two reviewed legacy rich-rule
removals and preservation of PostgreSQL service
state. [Scoped Maintenance CI
#43100611079 PASSED](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43100611079).
**No native TCP80 preview/application with this
new revision has happened.**
Maintenance's runbook explicitly uses
a separately extracted **exact-commit source
packet** in ignored `artifacts/`, through the
active checkout's `tools/run-ansible-logged`;
do **not** blindly `git pull` the active
Maintenance scheduling controller checkout.
One next operator action: source-pinned,
`--check --diff` Kvin firewall preview,
then inspect bounded `Show the exact
firewall-only preview`, final report
and PLAY RECAP before authorizing live apply.
The packet's exact command is documented at
[production cutover runbook](docs/runbooks/yxorp-production-cutover.md).
The preview must be read-only for host policy,
although it retains private controller receipts.

**After owned firewall native acceptance:**
Prove TCP80 from a non-Kvin client
before Maintenance moves the six reviewed
Peanut authoritative DNS entries from Kvar
`192.168.0.7` to Kvin `192.168.0.192`,
with updated served SOA serial and proper
owner preview/publish. Kvar NPM remains
running for DNS rollback. Actual browser
login, Kuma Socket.IO WebSocket, named
client/access acceptance still open.
Long-term two Kuma bears Kvin+Peanut
are the preexisting independent-peer
design; old rootless Podman hairpin
workaround `Network=host` is not an
upstream fix. Kvin Kuma isolated backup/
restore is accepted; off-host snapshot
and Vault-key recovery are still open.

## CURRENT — November 11, native production Yarn timeout CLEARED on read-only re-observation; one no-change YXORP repeat next

**Native Kvin production Yarn diagnostic COMPLETED**:
Nova ran `ansible/yxorp-production-yarn-diagnose.yml`,
`ok=7 changed=0 unreachable=0 failed=0 skipped=0`.
Bounded classification
**`current_production_yarn_proxy_http_path_answers`**.
`yarn.inner.sanctum` resolved exactly to declared
`192.168.1.110` (`matches_declared_origin:true`).
All six live HTTP tests responded:
direct Yarn by IP with both old/new Host = **200**;
direct Yarn by DNS with new Host = **200**;
Kvin rootful production Nginx `127.0.0.1:80`
new `yarn.nexus` Host = **200**;
legacy `yarn.inner` Host = **200**;
production Kuma control = **302**.
Response bodies remained private/bounded,
`configuration_changed:false`,
`kvar_or_dns_or_firewall_changed:false`.
The prior `ansible/yxorp.yml` initial
`ok=29 changed=5 failed=1` Yarn timeout was
**not reproducible at this new observation**.
Do NOT alter Yarn routing, timeout or proxy
source without fresh evidence; maintain both
results in history.

**One next native operator action:** Repeat
**only** the source-owned guarded production
play (the stage was already removed in
the previously approved `&&` chain; don't
try to remove it again):
```bash
cd ~/src/sanctum-services &&
git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp.yml \
  -e yxorp_production_cutover_approved=true
```
Expectation: full `PLAY RECAP` **`failed=0`**
and preferably `changed=0` along with
bounded `Report bounded Kvin YXORP production
listener readiness` containing the already
source-owned eight routes, local Kuma HTTP
200/302 and Yarn HTTP200. This would close
local production listener convergence only,
not real LAN DNS/clients/WebSockets.

**After that:** Maintenance source-owned
TCP80 firewall policy CI
[#43100611079 PASSED](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43100611079),
but no live TCP80 admission. Preview/apply
through Maintenance's existing
`playbooks/configure-kvin-firewall.yml`
with exact source revision and reviewed
operator wrapper. Only after an external
client can reach Kvin HTTP80 should
Maintenance publish six DNS alias/wildcard
names with a new SOA serial. Kvar old
NPM unchanged for rollback; named
client/session/WebSocket gates open.
[Cutover guide](docs/runbooks/yxorp-production-cutover.md).

**No re-opening settled architecture:** On
rootless Podman/pasta, own-host published
container hairpin traffic failed (April).
`Network=host` workaround not a fix;
two independent Kuma bears on Kvin and
Peanut already planned, no invented new
operator request. Kvin Kuma's Wicket
actual Up and isolated backup/restore
native accepted. Off-host backup/Vault
recovery still outstanding.

## CURRENT — November 11, 15:17 Central: Kvin production YXORP partly installed, Yarn forwarding timed out; no DNS/firewall changes. Podman hairpin design reaffirmed

**Operator's native result:** Nova executed the guarded
stage-removal then `ansible/yxorp.yml` production
deployment chain from Kvin. Production play:
`ok=29 changed=5 unreachable=0 failed=1 skipped=1`.
Exact failed post-task:
`Verify production proxy still reaches original Yarn service`
at `ansible/yxorp.yml:128`, with `Status code was -1 ...
Connection failure: timed out` to
`http://127.0.0.1/` with
`Host: yarn.nexus.sanctum`.
The preceding `Verify production proxy actually
reaches source-owned Kvin Kuma` post-task
**passed**, accepting HTTP 200 or 302.
The playbook had already reconciled the
owned Nginx unit/mounted config before
the Yarn timeout, but **full production
acceptance FAILED**. The separate
stage-removal play must have succeeded
to reach production because the native
shell used `&&`, but do not invent an
unseen stage recap. Maintenance firewall
and DNS are unchanged; the live
`*.nexus`/selected explicit A records
continue to point to Kvar NPM. Don't rerun
the deployment or publish DNS blindly.

**Next targeted action (read-only, Kvin only):**
`ansible/yxorp-production-yarn-diagnose.yml`
and `tools/observe-yxorp-production-yarn.py`
compare DNS `yarn.inner.sanctum`,
direct Yarn `192.168.1.110` with both
Host headers, direct named origin, and
the new and legacy Yarn Host routing
through the current `127.0.0.1:80`
production Nginx. Kuma remains a
proxy control. Return safe outcome/status
classes, not raw content. Source-only
CI #43102390350 was running as last
checked; wait for green before native use.
Exact command:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp-production-yarn-diagnose.yml
```
Return `PLAY RECAP` and bounded
`Report bounded production Yarn route evidence without retrying a deployment`
`msg`, or failed task. Diagnose actual
path before any production source change.

**Correction from Nova on established network design:**
On April 23, containerized Kuma
**could monitor other hosts but not its
own host-published containers** due
to rootless Podman/pasta hairpin
restriction, yielding refused traffic.
`Network=host` was the historical
workaround, **not a Podman bugfix**;
Nova does not want that workaround
as permanent monitoring architecture.
The **two Kuma bears on distinct hosts
monitoring one another was always
the plan**, not a newly invented
suggestion. Maintenance inventory
marks **Kvin and Peanut** `kuma_peer`
for the eventual independent hosts;
Kvar is temporary incumbent only.
Monitor direct external hostnames from
independent vantage points; never claim
same-host published-port reachability
or implicit Podman fixes.
This issue is *distinct* from the current
rootful host-network YXORP -> Yarn timeout
until proved otherwise.

**Already accepted (do not redo):**
Kvin Kuma has saved Wicket Ollama actual
Up, source-managed Vault admin,
unchanged repeat, and complete local
SQLite backup + isolated network-none
Kuma restore `ok=49 changed=11 failed=0`
with original service healthy after restart.
Off-host snapshot/Vault key recovery is
still outstanding. Maintenance source
TCP80 policy CI #43100611079 PASSED
but no native firewall publication.
Services full eight-route production
source CI #43098976225 PASSED
but native Yarn acceptance now FAILED.

## CURRENT — November 11: Kuma restore accepted, eight-route YXORP production source CI GREEN; firewall source awaiting CI, DNS untouched

**Native Kuma acceptance banked:** latest user-supplied
`ansible/kuma-backup-restore-trial.yml` **`ok=49 changed=11 failed=0`**.
Original Kvin Kuma restarted and verified HTTP+Vault login;
isolated `--network none` restored application actually
started, SQLite integrity passed, existing Vault
login and saved Wicket monitor verified, disposable
volume/container removed. Local retained
`sanctum-kuma-20261111t144137.tar`
290816 bytes, SHA-256
`97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648`.
This is **genuine local backup and application restore acceptance**,
not an off-host recovery. Vault key and encrypted
per-service credentials also still require independent
off-host recovery. Historical Wicket monitor is natively
`Up` with 12 heartbeats and 17-second age,
`changed=0` repeat.

**Operator production risk tolerance:** Nova says
YXORP may cut over anytime, even if an outage lasts
the remainder of the workday; his class does not
depend on it. This authorizes practical production
promotion without a zero-downtime maintenance-window
gate. It does not authorize discarding Kvar's
reversal path or pretending DNS/firewall/source
changes have run.

**Permanent two bears:** Maintenance production inventory
explicitly marks **both Kvin and Peanut** as
`sanctum_service_roles: kuma_peer`. Kvar Kuma
is temporary migration fallback, **not**
the eventual second bear; Kvar is intended
to be emptied/reprovisioned. No Peanut Kuma
deployment or peer cross-monitor configuration
has yet been performed. HTTP monitors do
not need a privileged Podman socket; direct
container-state integration is a different
socket/permissions feature.

**Production proxy source implemented:**
`ansible/yxorp.yml` now explicitly approves only
exact Kvin rootful Nginx and builds a full eight-host
production route projection from untouched
`data/yxorp-routes.yml` stage baseline, with
**only** `kuma.nexus.sanctum` retargeted to
`127.0.0.1:13001`. It verifies stage
TCP80 Quadlet is absent, Kvin Kuma local HTTP
exists, role's Nginx parsing and live mounted
configuration pass, and both Kuma and Yarn
real frontend HTTP respond. It does not
touch DNS/firewall/Kvar. A second source-owned
`ansible/yxorp-production-remove.yml`
can remove only the exact production Quadlet
and its known Nginx files; never Kvar or
application state. Source tests execute actual
Ansible eight-route projection and verify
separate production/reversal gates.
**[FULL Services CI #43098976225 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43098976225).**
No native stage-to-production handoff has happened.

**Source CI status:** [Services #43098976225
PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43098976225);
[Maintenance scoped firewall CI #43100611079
PASSED](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43100611079).
A *separate* Maintenance candidate-cutover
workflow currently has unrelated, preexisting
Kvin DNS baseline mismatch failures;
do not modify Kvin host/DNS identity to silence
that test. The firewall's own exact source
contract and real-Ansible synthetic test passed.

**Preferred next operator step (Services only, before DNS/firewall):**
```bash
cd ~/src/sanctum-services &&
git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-remove.yml \
  -e yxorp_kvin_stage_remove_approved=true &&
~/.local/bin/ansible-navigator run ansible/yxorp.yml \
  -e yxorp_production_cutover_approved=true
```
Ask ONLY two native PLAY RECAP rows and the
safe `Report bounded Kvin YXORP production listener readiness`
msg or failure. Kvar NPM and DNS stay live.
If production succeeds, proceed with the
Maintenance firewall owner source reviewed
commit and authoritative DNS publication;
if it fails, Kvar remains effective fallback.
This ordering is safe without LAN HTTP80
being open, because external clients' Nexus
names still point to Kvar.
[Exact release and rollback guide](docs/runbooks/yxorp-production-cutover.md).

**Maintenance-owned firewall source:** Updated
`wdcallahan/sanctum-maintenance` at commit
[`873c9c6`](https://github.com/wdcallahan/sanctum-maintenance/commit/873c9c6fdb7f4ac8a7b56181a957eb03a89005a9)
to include `80/tcp` in the exact
`public`/Kvin `eth0` reviewed service
policy alongside 5432, 8084 and 8085;
retained same two old rich rules and
PG/zone preservation logic. Added new
source CI fixture workflow; **CI was
queued as last checked**. No native
firewall modification. **Maintenance DNS
`data/dns.yml` untouched**: five explicit
`dir/joule/kuma/pihole/search.nexus` A
records and `*.nexus` still point to Kvar
`192.168.0.7`; Kvin is
`192.168.0.192`. Don't change DNS
before Kvin prod is actually live and
TCP80 admitted. Preserve explicit old
`yxorp.nexus` NPM-admin Kvar and three
direct DB records (already Kvin).

**Current exact operational runbook:**
[docs/runbooks/yxorp-production-cutover.md](docs/runbooks/yxorp-production-cutover.md).
It documents Maintenance source-reviewed
TCP80 preview/apply, source-owned stage
remove -> production start as **two distinct
approved** Navigator plays, then owner
DNS zone serial/publish and real external
browser/WebSocket acceptance. Reverse
DNS first after release, retaining Kvar
NPM throughout. Do not invent native
acceptance or recommend running the
firewall command before source CI green.

## CURRENT — November 11: native Kuma offline restore ACCEPTED; operator authorizes YXORP cutover and two-bear mutual monitoring

**Native operator result (now ACCEPTED):**
`ansible/kuma-backup-restore-trial.yml` on Kvin completed
`ok=49 changed=11 unreachable=0 failed=0 skipped=0`.
The bounded receipt records private backup
`/home/wdc2/.local/share/sanctum-services/backups/kuma/sanctum-kuma-20261111t144137.tar`,
**290816 bytes**, SHA-256
`97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648`.
Kuma's original HTTP and Vault login verified after safe restart;
independently imported test volume passed SQLite integrity;
restored **network-none** Kuma actually started, accepted the
previous Vault admin and retained Wicket monitor; disposable
test container+volume removed. **Local backup and isolated live-application
recovery ACCEPTED.** No data overwritten, Kvar,
YXORP or production changed. **Off-host copy and Vault
key+encrypted-secret independent recovery remain UNACCEPTED**.

**New operator guidance:** Nova explicitly says the new reverse proxy
**may be swapped into use at any point**, even if an outage lasts
the remainder of the working day; no class dependency requires
zero downtime. This supersedes any invented availability
cutover scheduling gate, but does **not** excuse preserving
source of truth, correct eight frontend routes, application
state, existing fallback and explicit reversal.

**Two Kuma/bear design:** Kvar's existing Kuma and Kvin's
new Kuma can mutually monitor one another as separately
scoped HTTP endpoints. The current Kvin Kuma already
monitors Wicket and is Up. No Kvar Kuma credential,
monitor changes or new cross-check subscriptions
have yet been qualified; avoid assuming Kvar's old
Kuma or Podman socket is open. HTTP health monitoring
does not require Kuma direct access to another local
container's Podman socket; container-native monitor
integration does have user/socket permission boundaries.

**Proxy release facts:** Eight stage routes accepted
at Kvin HTTP80 with rootful
`sanctum-yxorp-kvin-stage.service`.
Production `ansible/yxorp.yml` is separately gated
(`yxorp_production_cutover_approved`) and uses a
distinct Quadlet `sanctum-yxorp.service`;
both cannot hold TCP80 simultaneously. The
existing checked-in `data/yxorp-routes.yml`
has only Yarn enabled; production promotion must
select all 8 approved hostnames **without
altering the historical staging manifest** and
retarget only new `kuma.nexus.sanctum` backend
to Kvin `127.0.0.1:13001`. Other
app backends continue using existing direct
Kvin/Kvar origins. The Kvar NPM proxy stays
available for rollback. Maintenance owns Kvin
firewall TCP80 and Peanut DNS `data/dns.yml`,
including explicit names plus wildcard.
The current source still points those public
names at Kvar. Do not claim production cutover
until independent LAN client DNS + session/
WebSocket and rollback are actually observed.
Prepare source, CI and safe owner coordination
before asking for a single meaningful native
operator command.

## CURRENT — November 11: Wicket Ollama actually UP in retained Kvin Kuma; consistent backup/isolated restore source next

**New native acceptance from Nova:** The unchanged second native
`ansible/kuma-monitors.yml` run reported
`ok=13 changed=0 unreachable=0 failed=0 skipped=0`.
Its bounded report: `action:unchanged`,
`monitor_id:1`, `configuration_persisted_and_verified:true`,
`notifications_attached:false`,
**`latest_status_in_kuma:Up`**,
`heartbeat_age_seconds:17`,
`heartbeat_records_last_hour:12`,
`heartbeat_recent_within_180_seconds:true`,
**`actual_up_accepted:true`**. This proves the *real Kuma*
monitoring engine saw Wicket's
`http://wicket.arcane.sanctum:11435/healthz`
healthy, not just a direct Kvin curl.
Earlier admin repeat was `ok=12 changed=0`
and native Wicket creation `ok=11 changed=1`.
**The live-monitor state/identity/idempotence gates are now closed.**
Do not repeat already accepted Wicket checks. Kvar and YXORP
have NOT been changed, and no named LAN client acceptance
or independent backup/restore has happened.

**Next gated source work:** One-shot
`ansible/kuma-backup-restore-trial.yml` uses
source-pinned Kuma 2.5.9 and existing private Vault.
It is default-off until an operator supplies
`kuma_backup_restore_trial_approved=true` and
knows it will briefly stop the **Kvin** user
service for SQLite-consistent `podman volume export`.
The playbook always starts Kuma again; verifies
original HTTP and Vault login; validates a private
`0600` local backup; imports only to a new
test volume, runs a separate restored Kuma container
with **no network or port publishing**, verifies
restored SQLite integrity and Vault login
without creating users, and checks the
saved monitor using Kuma's Socket.IO. It then
removes only the disposable restored container
and volume. Off-host backup, actual restore
on a different machine, schema upgrade and
LAN/production are NOT covered.
The source also adds a read-only `verify`
mode to `tools/kuma-admin-init.js` and
SQLite archive/volume checker
`tools/kuma-backup-verify.py`.
Use the exact command in
[docs/runbooks/kuma-recovery.md](docs/runbooks/kuma-recovery.md)
**only after CI is green**. The operator must
return PLAY RECAP and safe bounded recovery msg.
If CI fails, fix source/tests before asking Nova
to run this impactful operation.

**Beyond the local restore trial:** independent
off-host copy (Peanut candidate) + hash check,
recoverable existing Vault key+encrypted secret,
actual named client browser/WebSocket path,
restart/update/rollback, then separately approved
Kvar->Kvin `kuma.nexus` retarget. This is still
one Sanctum Services/YXORP migration project,
not a new separate scope.

## CURRENT — November 11: Native Kuma admin repeat NO-CHANGE; Wicket created and persisted; real Up observation next

**Native operator acceptance, exact Kvin:**
- Guarded Vault-backed `ansible/kuma-admin-bootstrap.yml` repeat
  **`ok=12 changed=0 unreachable=0 failed=0 skipped=0`**.
  First-user administration and second-run idempotence are ACCEPTED,
  following the earlier native `administrator_created_this_run:true`
  and `administrator_login_verified:true` result.
- Separately authorized `ansible/kuma-monitors.yml` first native
  run **`ok=11 changed=1 unreachable=0 failed=0 skipped=0`**.
  Bounded report: **`action:created`**, `monitor_id:1`,
  `monitor:Wicket Ollama`, `configuration_persisted_and_verified:true`,
  `notifications_attached:false`,
  `actual_up_accepted:false`,
  `backup_restore_accepted:false`,
  `named_client_and_production_accepted:false`.
  Source-managed target is HTTP GET
  `http://wicket.arcane.sanctum:11435/healthz`
  every 60 seconds, expected 200–299. This establishes
  native monitor creation and saved configuration,
  **not the live Up heartbeat**. Kvar, YXORP,
  DNS, firewall and production unchanged.

**Next source and planned native acceptance:**
Extended the already qualified `tools/kuma-reconcile-monitors.js`
with a strictly read-only `observe` mode that
authenticates with the same existing Vault password
and uses the exact tagged Kuma **2.5.9**
Socket.IO `getMonitor(1)` and
`getMonitorBeats(1,1)` read methods. The
same `ansible/kuma-monitors.yml` now reconciles
idempotently, then reads actual retained Kuma
heartbeat status and recency. It reports
`latest_status_in_kuma`,
`heartbeat_age_seconds`, and
`actual_up_accepted:true` only for a recent
(<=180-second-old) Up/1 record. Missing,
Down, Pending or stale records do **not**
get promoted to Up. The read uses `no_log`,
makes no app writes or notifications, and
never exposes Vault credentials. New synthetic
Node tests cover actual Up/Down/Pending/stale
and absent heartbeat. Verify full CI before
giving Nova the next command.

**One next Kvin operator action after source CI:**
```bash
cd ~/src/sanctum-services && git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
~/.local/bin/ansible-navigator run ansible/kuma-monitors.yml \
  --eev "$vault_dir/vault.key:$vault_dir/vault.key:ro,Z" \
  --eev "$vault_dir/kuma-admin.vault.yml:$vault_dir/kuma-admin.vault.yml:ro,Z" \
  --senv "ANSIBLE_VAULT_PASSWORD_FILE=$vault_dir/vault.key" \
  --pae false \
  -e kuma_monitors_approved=true
```

Request only the `PLAY RECAP` row
(`changed=0` expected) and bounded
`Report bounded Wicket monitor configuration acceptance`
`msg`. Real Kuma heartbeat Up closes the
monitor-state gate; false or Down is a
specific supported blocker to investigate.
Full independent backup/restore of `sanctum-kuma-data`
and existing Vault key + encrypted files,
restart/update, actual browser and named client
acceptance remain open. No Kvar cutover.

## CURRENT — November 11: Kuma Vault administrator CREATED + AUTHENTICATED; Wicket source reconciler CI green; next native

**Native operator evidence:** Vault-backed
`ansible/kuma-admin-bootstrap.yml` completed on Kvin
`ok=12 changed=1 unreachable=0 failed=0 skipped=0`,
with `administrator_created_this_run:true`,
`administrator_login_verified:true`,
`encrypted_credentials_loaded:true`,
no password generated/changed or separately written,
no Kvar/proxy mutation. Actual administrator setup
and authenticated login **accepted**. No source
assumption replaces this observed evidence.

**Next source advance:** After reading the exact tagged
Uptime Kuma 2.5.9 upstream Socket.IO `login`,
`getMonitorList`, `getMonitor`, `add` and
`editMonitor` code, implemented separately guarded
`ansible/kuma-monitors.yml` plus
`tools/kuma-reconcile-monitors.js`. The playbook
reads the existing external `kuma-admin.vault.yml`
through the SAME per-run two-file EE mounts.
It insists on exact Kvin/wdc2/ARM64/pinned
image, rootless SQLite/volume/loopback Quadlet,
and explicit `kuma_monitors_approved=true`.
It permits **only** `data/kuma-monitors.yml`'s
one `Wicket Ollama` HTTP GET to
`http://wicket.arcane.sanctum:11435/healthz`,
60 seconds, HTTP 200–299, by stable name.
The native handler authenticates and reads
current monitors, refuses duplicate names or
preexisting attached notifications, creates
or reconciles exactly that monitor, re-reads
its persisted state, and reports safe metadata
with no added notification providers.
Node real-code fake-Socket.IO tests cover
create/unchanged/update/duplicate/auth failures;
[full CI #43082780801 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43082780801).
**Kvin has NOT executed monitor reconciler; no
Up state or backup/recovery claimed.**

**Next operator command, from Kvin** (one shell chain,
two separate approved playbooks, one
Vault configuration):
```bash
cd ~/src/sanctum-services &&
git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
nav="$HOME/.local/bin/ansible-navigator" &&
options=(
  --eev "$vault_dir/vault.key:$vault_dir/vault.key:ro,Z"
  --eev "$vault_dir/kuma-admin.vault.yml:$vault_dir/kuma-admin.vault.yml:ro,Z"
  --senv "ANSIBLE_VAULT_PASSWORD_FILE=$vault_dir/vault.key"
  --pae false
) &&
"$nav" run ansible/kuma-admin-bootstrap.yml "${options[@]}" \
  -e kuma_admin_bootstrap_approved=true &&
"$nav" run ansible/kuma-monitors.yml "${options[@]}" \
  -e kuma_monitors_approved=true
```

Ask ONLY the two PLAY RECAP lines and
the bounded `msg` from
**Report bounded Wicket monitor configuration acceptance**,
or exact failed task and error. Admin repeat should
be `changed=0`, account created this run false,
login verified true. Monitor first run may
be `changed=1`, configuration persisted;
**no actual Up accepted yet**. Then test monitor
unchanged repeat, actual Up in retained Kuma
(browser via existing SSH tunnel if needed),
restart/recovery and off-host independent
backup of data volume and Vault materials.
No YXORP, Kvar, Maintenance DNS/firewall
or production cutover.

## CURRENT — November 11: Kuma administrator CREATED + VERIFIED on native Kvin via Vault; repeat outstanding

**Native acceptance received from Nova:** The approved
`ansible/kuma-admin-bootstrap.yml` run on exact Kvin
finished `ok=12 changed=1 unreachable=0 failed=0 skipped=0`.
The bounded `Report only safe administrator bootstrap acceptance`
confirmed **`administrator_created_this_run:true`**,
**`administrator_login_verified:true`**, username
`sanctum-admin`, **`encrypted_credentials_loaded:true`**,
`credentials_generated_or_changed:false`,
`credentials_written_to_host:false`,
`private_credentials_not_logged:true`, and
`production_or_proxy_changed:false`.
This is first real source-managed Kuma administrator
creation using Nova's chosen Vault password and
Kuma's native 2.5.9 Socket.IO setup+login, **not
merely HTTP 302 or a displayed setup wizard**.
The prior intentionally bad test password had failed
before this successful run; no need to reopen that
password-policy investigation.

**Next native acceptance:** Execute the **same separately
approved admin bootstrap a second time** with the
two exact read-only secret mounts, `--senv` for
the existing `vault.key`, and `--pae false` as
in [vault runbook](docs/runbooks/vault-credentials.md).
Expected `changed=0`,
`administrator_created_this_run:false`,
`administrator_login_verified:true`.
Use `git pull` normally. Ask only for PLAY RECAP
and safe bounded `msg`, or failed task and error;
never paste secret material. This repeat does
not create/rotate credentials, affect Kvar,
proxy, DNS or firewall.

**Next actual useful app:** `data/kuma-monitors.yml`
already declares Project Joule's **Wicket Ollama**
HTTP `GET http://wicket.arcane.sanctum:11435/healthz`
60-second interval and HTTP 200–299. Tagged Kuma
2.5.9 native source provides authenticated
`monitorList`, `getMonitorList`, `getMonitor`,
`add` and `editMonitor` Socket.IO interfaces.
Services should implement **guarded source-owned**
monitor reconciliation by stable name, verify
persisted target, then prove actual **Up** in
Kuma; no duplicates or notifications. Do not
call an untested source-only design production
or infer Up from direct curl. Other open gates
are startup/restart/recovery and independent
backup of volume + encrypted Vault files/key,
actual browser authenticated use, and named
client/LAN/production acceptance. Existing
Kvar Kuma and Kvar NPM remain authoritative
until separate cutover.

## CURRENT — November 11: Simplified Kuma Vault entry at Nova's request; no arbitrary minimum, confirmation required

Nova pointed out that the previous one-time Vault command imposed an
unannounced **16-character** minimum and accepted one hidden password
entry with **no confirmation**. This was unsuitable for his home
network and his chosen credential workflow. The first encrypted
Kuma Vault file may already exist, but **administrator bootstrap
has not been run**, so the encrypted value can still be corrected
safely without touching a live account.

Source correction committed: `tools/kuma-set-vault-password.sh`
prompts for the **user-selected** password twice, checks that the
two values match and the input is nonempty, and encrypts it with
the **existing** `/home/wdc2/.config/sanctum-services/secrets/vault.key`.
It writes an encrypted temporary file and only replaces the
existing `kuma-admin.vault.yml` after encryption succeeds.
Mismatched entries or encryption errors preserve the existing file.
The Kuma bootstrap Ansible guard and internal Node client no
longer impose a 16-character limit; **Kuma 2.5.9 itself**
determines whether it accepts the password at first-user
setup. The user's password is not in Git, process argv or output.
Tests cover shorter passwords, confirmation, preservation on
mismatch/failure and replacement.
[Full CI #43079245718 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43079245718).

**One next native Kvin operator action** (replaces the old
one-entry shell block; allows correction of already-created encrypted
file, no Kuma application change):

```bash
cd ~/src/sanctum-services && git pull &&
bash tools/kuma-set-vault-password.sh
```

Ask only whether the script printed
`Passwords matched.` and
`Kuma encrypted password saved. Application account unchanged.`
or a nonsecret failure. Then run separately authorized
Vault-aware Kuma administrator bootstrap from
`docs/runbooks/vault-credentials.md`. The existing key
is retained. Neither manual wizard setup nor password
rotation is approved or needed at this stage.

## CURRENT — November 11: Kuma native SQLite convergence accepted; shared Vault credential authority selected, admin NOT bootstrapped

**Nova's accepted native results remain unchanged.** The Kvin Kuma
2.5.9 ARM64 rootless stage passed its HTTP startup with named
`sanctum-kuma-data` and `127.0.0.1:13001`. A later SQLite
Quadlet reconciliation passed `ok=9 changed=2 failed=0` and
the immediate repeat passed `ok=9 changed=0 failed=0`.
An SSH-tunneled real browser reached the database selection
and the create-administrator wizard. **No actual administrator,
monitor, backup/restore, LAN or Kvar cutover is accepted.**
Do not repeat the already accepted stage and YXORP tests.

**Credential architecture approved by Nova:** Ansible Vault is the
authority for per-service credentials. One already existing
external plaintext unlock key belongs to the user at
`/home/wdc2/.config/sanctum-services/secrets/vault.key`,
previously documented for Nextcloud's encrypted PostgreSQL
credential at `.../nextcloud-postgresql.vault.yml`.
**Do not regenerate or replace that key, or ask Nova to
supply it to ChatGPT.** Each service may have its own encrypted
vault variable file with this same key. Ansible uses the desired
password; rebuilding a service does not create a new identity.
An unrecognized existing admin must not be reset.

**Source reworked:** `ansible/kuma-admin-bootstrap.yml` now
loads the external encrypted
`/home/wdc2/.config/sanctum-services/secrets/kuma-admin.vault.yml`
containing `vault_kuma_admin_password`.
The former random password generator and the Kvin-local
`kuma-admin.json` design have been removed. The separate
`kuma_admin_bootstrap_approved=true` guard, exact
Kvin/wdc2/ARM64/source-owned Quadlet and pinned image
checks, and upstream Kuma 2.5.9 Socket.IO `needSetup`,
`setup`, `login` protocol remain. Vault data travels
via Ansible `no_log` task stdin, never in Git,
command arguments, debug, or a second on-host secret file.
A repeat verifies login without account changes; an
unknown preexisting administrator causes failure.

**Important execution-environment boundary:** A first attempt to
configure `vault_password_file` globally in `ansible.cfg`
broke source CI and would break unrelated controller
playbooks without access to Kvin's key. This was corrected.
Only a vault-aware Navigator run explicitly mounts the
two exact secret files read-only (`--eev`), passes
`ANSIBLE_VAULT_PASSWORD_FILE` via `--senv`,
and disables its playbook artifact (`--pae false`).
Full source tests and [CI #43076965704
PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43076965704).
No native Vault/bootstrap action has been run.

**ONE NEXT OPERATOR ACTION FROM KVIN:** Choose one strong private
Kuma admin password and create its encrypted Vault variable
without ever showing the secret in chat, command history,
or Git. Follow the safe, nonclobbering one-time shell
command in [docs/runbooks/vault-credentials.md](docs/runbooks/vault-credentials.md).
The repository command uses the **existing** vault.key.
Request only “Kuma Vault variable created” or a
nonsecret error. The encrypted file and key must
eventually have separately verified off-host backups.

**After that**, run the guarded native admin bootstrap
twice with the per-run Navigator mounts and
`-e kuma_admin_bootstrap_approved=true` exactly
as documented in the same runbook; ask only for the
two PLAY RECAP lines and the safe bounded message.
Native bootstrap remains **unexecuted**; changing a
vaulted password after setup does NOT automatically
rotate an application credential. An explicit
authenticated, separately approved rotation mechanism
still needs source design and testing.
Continue later to source-owned `Wicket Ollama`
monitor reconcile and Up observation, independent
restore, update, rollback, LAN/production acceptance.
Kvar and existing YXORP remain untouched.

## CURRENT — November 11: Kuma SQLite no-op verified; administrator bootstrap now automated in source

**Fresh operator evidence:** Nova reconciled the SQLite Quadlet
on Kvin, `ok=9 changed=2 failed=0 skipped=2`, then ran the
same guarded Kuma playbook again: **`ok=9 changed=0 failed=0
skipped=2`**. Bounded report says `desired_database_backend:sqlite`,
`candidate_stage_http_status:302`, exact image, named data volume,
and `administrator_and_monitor_state_accepted:false`.
Using an SSH tunnel, Nova opened both the live Kuma database
selection and **Create your admin account** screens in Firefox.
This proves actual browser UI reachable through the tunnel,
**not** a completed admin account, database restore, monitor,
client routing or production change. Do not rerun the routine
SQLite reconciliation or 8/8 YXORP route probes.

**Architecture correction from Nova:** He challenged a proposed
manual creation of the admin account because **a reproducible
service should initialize its own application state through
source-managed automation**. Agreed. Verified the **exact
Uptime Kuma 2.5.9 upstream source**: its `needSetup`,
`setup(username,password,ack)` and `login` Socket.IO
events support first-user creation and credential verification.
We must not invent a write REST endpoint or modify SQLite
directly. The initial setup refuses reinitialization if the
user table is nonempty.

**New independently approved source-owned automation:**
`ansible/kuma-admin-bootstrap.yml` is guarded by
`kuma_admin_bootstrap_approved=true` (default off),
checks exact Kvin/wdc2/aarch64, pinned image, source-owned
Quadlet, local-only binding, named volume and SQLite.
It queries the real Kuma Socket.IO `needSetup`; if
fresh it creates one `0600` private credential JSON at
`/home/wdc2/.config/sanctum-services/secrets/kuma-admin.json`
within a `0700` directory, with fixed username
`sanctum-admin` and a cryptographically random password.
`tools/kuma-admin-init.js` then calls Kuma's native
setup API and independently authenticates. On repeat
it verifies the same credential with no creation.
If an administrator already exists without the owned
secret file, it **fails closed rather than overwriting,
resetting or adopting the account**. Secret passes over
stdin to a Node process **inside** the running Kuma
container, never argv, raw logs, git or chat; all
authentication command tasks are `no_log`.
Backup of this private file OFF Kvin must be included
in the later independent recovery plan.

Source tests plus mocked real Node protocol tests and
full [CI #43072165068 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43072165068).
**Bootstrap has NOT run natively on Kvin.** The old
browser setup path is a fallback, not the next
required action. A prior CI fake-transport timeout
was corrected in the simulator; no host mutation.

**One next native action from Kvin, explicitly approves
only the retained Kuma admin bootstrap and verifies
repeatability:**

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma-admin-bootstrap.yml \
  -e kuma_admin_bootstrap_approved=true &&
~/.local/bin/ansible-navigator run ansible/kuma-admin-bootstrap.yml \
  -e kuma_admin_bootstrap_approved=true
```

Ask only for **both Kvin PLAY RECAP** lines and the
`msg` from final `Report only safe administrator bootstrap
acceptance`, or the failed task/error. Neither output should
contain secret values. On native acceptance, use existing
browser tunnel to log in with locally retrieved private
credential; do not paste the password here. Then
develop source-owned, version-qualified authenticated
`Wicket Ollama` monitor reconciliation and independently
prove it Up, no duplicate alerts, backup/restore, update,
reversal and real named client outcome before touching Kvar.
See [Kuma runbook](docs/runbooks/kuma-monitoring.md).

## CURRENT — November 11: Kuma rootless stage NATIVELY ACCEPTED, SQLite declared; next is repeat and administrator setup

**Actual native stage receipt supplied by Nova:** From Kvin,
`~/.local/bin/ansible-navigator run ansible/kuma.yml
-e kuma_stage_approved=true` completed **`ok=10 changed=3
unreachable=0 failed=0 skipped=1`**. Reported
`candidate_stage_http_status:302`, `initial_http_only:true`,
named `sanctum-kuma-data` volume, pinned Uptime Kuma
2.5.9 Linux ARM64 image, Quadlet reconciled, rootless
`127.0.0.1:13001`. HTTP 302 was expressly an accepted
startup status, **not proof of browser UI, login, monitors,
recovery or production access**. Kvar, existing YXORP,
Maintenance DNS/firewall and all production routes remain unchanged.

**Source-only continuation after the native receipt:**
Pinned supported SQLite backend `kuma_db_type: sqlite`
and `Environment=UPTIME_KUMA_DB_TYPE=sqlite` in the
rootless user Quadlet (official Kuma v2 environment
variable). Separate administrator account creation stays in
the application; secrets never go into Git or chat.
Static source contract and full [CI #43065990976
PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43065990976).
No SQLite source change has yet been reconciled
on native Kvin. Source-only CI does not establish
whether Kuma's actual setup wizard is complete.

**Next meaningful operator step, Kvin:** Reconcile
the one source-owned SQLite Quadlet change and immediately
run an unchanged repeat, with the same explicit
isolated stage approval on each call:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma.yml -e kuma_stage_approved=true &&
~/.local/bin/ansible-navigator run ansible/kuma.yml -e kuma_stage_approved=true
```

Ask for **both Kvin PLAY RECAP rows** and the final
**Report bounded loopback Kuma candidate staging
acceptance** `msg`, or failed task/error. The first run
should reconcile/restart the Quadlet; second should have
`changed=0` if role really converges. If unsuccessful
diagnose the exact failed task before asking for more runs.

**Then administrator bootstrap through existing SSH:**
From Nova's desktop/browser machine (not within
Kvin shell), open a loopback-only SSH forwarding session:
`ssh -o ExitOnForwardFailure=yes -N -L
127.0.0.1:13001:127.0.0.1:13001
wdc2@kvin.outer.sanctum`. Visit
`http://127.0.0.1:13001/` in that desktop browser;
source chooses SQLite. Create the initial administrator
using the application's own setup UI and retain secret
credentials privately, never in a pasted diagnostic.
Do NOT manually create the Wicket monitor yet;
its `data/kuma-monitors.yml` declaration is already
owned by Services, and an idempotent, version-qualified
authenticated Socket.IO reconciler is still needed.
The community `uptime-kuma-api2` library has v2 support
but documents live-test coverage only through 2.5.0,
not this exact 2.5.9 image: source assessment is
not proof of 2.5.9 native integration. No installation
of that library or monitor mutation has been done.

**Recovery remaining:** login/actual monitor Up,
source-controlled repeat and no duplicate alerts,
backup/independent restore, restart/update and
named/LAN client proof before any Kvar upstream
retarget. Volume must be preserved; current
source-managed candidate reversal is available but
not natively exercised. See
[runbook](docs/runbooks/kuma-monitoring.md).

## CURRENT — November 11: native Kuma ARM64 image QUALIFIED; pinned loopback candidate + safe reversal CI green

**Native Kvin image-only acceptance supplied by Nova:** The corrected
`ansible/kuma-qualify-image.yml` completed **`ok=8 changed=0
unreachable=0 failed=0 skipped=1`**. Its bounded `msg` confirms
image `docker.io/louislam/uptime-kuma@sha256:302aceeca2db79617f195a7549f7c8dfb05375a274b1092c59d81c1fb61a9ab9`
(2.5.9), Linux ARM64, and real disposable offline Node execution.
The existing rootless image cache was reused; **no Kuma app,
volume, Quadlet, monitor, host/network or production changes**.
This closes the image-only qualification gate, not SS-APPS-1.

**Source prepared for the first retained Kuma app stage:** The exact
natively qualified digest is now pinned in `ansible/group_vars/kuma.yml`.
`ansible/kuma.yml` still requires **explicit
`kuma_stage_approved=true`**; the default is false, and the role
insists on Kvin/aarch64, rootless user execution, loopback
`127.0.0.1:13001`, named `sanctum-kuma-data` Podman volume,
and exact image digest. It creates/stores app state and a
user Quadlet only when separately authorized, and asserts
an HTTP 200 or 302 from localhost. Fixed an existing issue:
Quadlet-generated units are enabled by their own `[Install]`
`WantedBy`, not `systemctl enable`. [Pin and stage
CI #43064138846 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43064138846).

**Reversal ready before installation:** New
`ansible/kuma-stage-remove.yml` is explicitly default-off
(`kuma_stage_remove_approved=true`), checks exact Kvin
owner/unit/Quadlet contents, stops and removes only the
Kuma user Quadlet/service, and **preserves the named data
volume and image**. It never changes YXORP, Kvar, DNS or
firewalld. [Source CI #43064602595 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43064602595).
Reversal has NOT yet been executed on Kvin.

**One next operator action (from Kvin; explicitly authorizes
loopback application staging, NOT production):**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma.yml \
  -e kuma_stage_approved=true
```
Ask only for the native `PLAY RECAP` and bounded `msg`
from **Report bounded loopback Kuma candidate staging
acceptance**, or failed task/error. A successful stage
gains only a local Kuma HTTP endpoint and data volume:
administrator bootstrap, actual wanted `Wicket Ollama`
monitor Up, no-change repeat, backup/restore, upgrade,
removal proof, named YXORP/LAN use and production cutover
remain separate gates. Do not retarget the existing
`kuma.nexus` route or stop Kvar.

## CURRENT — November 11: Kuma image cached on Kvin; Podman Id assertion corrected, native retry next

Nova's first native `ansible/kuma-qualify-image.yml` run on Kvin
returned `ok=5 changed=1 failed=1` at the metadata assertion;
the exact image was pulled into wdc2's rootless cache. The single-image,
Linux and ARM64 checks passed. The only failed predicate mistakenly
required the `sha256:` prefix on Podman's `Id`, which is actually
a bare 64-character hexadecimal image ID; `Digest` has the prefix.
The disposable offline `node --version` check did NOT execute.
No Kuma app, volume, Quadlet, monitoring data, DNS, firewall, Kvar
service or YXORP config was changed.

The source fix now checks Podman's documented bare Id form.
`tests/test_kuma_image_qualification.py` checks the exact predicate,
and `tests/fixtures/verify-kuma-image-metadata.py` executes the
REAL production assert locally via Ansible against valid/invalid image
metadata. Full [source CI #43059304269 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43059304269).
[Repair commit](https://github.com/wdcallahan/sanctum-services/commit/919344e3b7ffac45b8de75740ce05ab874e1660f).

**Next exact operator command, on Kvin** (same command; cached digest
should skip the pull):

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma-qualify-image.yml \
  -e kuma_image_qualification_approved=true
```

Ask only for Kvin's `PLAY RECAP` and `msg` dictionary from
"Report bounded image-only qualification metadata", or failed task/error.
**Image not yet native qualified; no application stage approved.**
On native image acceptance, pin the tested digest and separately
prepare/authorize loopback Kuma installation, wanted monitor reconciliation,
persistence, no-op repeat and recovery. Do not rerun YXORP route probes
or confuse this image cache with a retained application.

## CURRENT — November 11: SS-YX-2 ACCEPTED, all eight initial Kvin HTTP hosts; Kuma next

**Latest native eighth-Yarn acceptance supplied by Nova:** Kvin ran the corrected
`ansible/yxorp-kvin-stage-yarn-inner-probe.yml`, finishing
**`ok=8 changed=0 unreachable=0 failed=0 skipped=0`**.
The exact mounted configuration equals its published source, and each
old/new Yarn `server_name` occurs once with the exact old upstream.
The original `yarn.inner.sanctum` direct backend and Kvin stage
both returned **HTTP 200**, the **complete 349-byte body was identical**,
media type/status matched, and no redirect was observed.
`yarn.nexus.sanctum` independently returned **200** with
349 body bytes; unknown-Host connections were refused.
Every acceptance assertion passed. `old_redirect_exact_wire_equals_direct`
is `not_comparable` because neither response redirected,
**not an acceptance failure**. The old Kvar NPM route remains
broken/unqualified, and has never been treated as an accepted comparison.
This native evidence **closes SS-YX-2** at the agreed bounded anonymous
HTTP/loopback and mounted-config level, not browser, login,
LAN or production. **Do not rerun eighth probe or earlier seven canaries.**

**SS-YX-3 evidence decision (source review):** Reuse existing
[Nov 9 NPM behavioral observation](docs/review/2026-11-09-yxorp-behavior-observation.md)
and [default upstream mapping](docs/review/2026-11-09-yxorp-default-route-comparison.md).
All incumbent NPM app hosts had **one ordinary location and no
non-default locations**; no nonempty global custom snippets were observed.
Synthetic real-Nginx tests cover Host isolation/default-deny, forwarded
headers, raw relative redirects, Upgrade and route change/removal.
The YXORP role validates the generated config, reconciles stale Podman
single-file mounts and verifies the live readback. Prism's observed
legacy HTTPS directives are an intentional difference under the already
accepted private HTTP policy, not a surprise new TLS workstream.
No new source-only proxy behavior blocker has been identified.
**App-specific real browser/login, WebSocket/Socket.IO, data restore,
client/LAN reachability and replay/rollback gates remain open** and
belong to SS-APPS and SS-PUB. Do not claim full NPM/runtime behavior
equivalence, current LAN publication or production cutover.

**Next executable leaf — SS-APPS-1 Kuma native image qualification:**
Existing source skeleton remains safe/default-off
(`ansible/kuma.yml`, `ansible/group_vars/kuma.yml`,
`ansible/roles/kuma/tasks/main.yml` and Quadlet),
and `kuma_image` remains **empty**, not deployed.
The existing
`data/container-image-candidates.yml` contains
one exact published linux/arm64 Uptime Kuma
**2.5.9** digest, `status: registry_only`:
`docker.io/louislam/uptime-kuma@sha256:302aceeca2db79617f195a7549f7c8dfb05375a274b1092c59d81c1fb61a9ab9`.
Pixel created `ansible/kuma-qualify-image.yml`
with exact Kvin/aarch64 and
`kuma_image_qualification_approved=true`
guards; it runs **without become** under
wdc2 rootless Podman and demands
`kuma_stage_approved=false`.
Only the image cache may change: inspect
or pull exact digest, verify Linux ARM64
metadata and run `node --version` inside
a disposable offline/read-only container;
**no app, volume, Quadlet, DNS, firewall,
Kvar or YXORP change**.
`tests/test_kuma_image_qualification.py`
and Ansible syntax are included in
**[CI #43055414958 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43055414958)**.
**One next operator command from Kvin:**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma-qualify-image.yml \
  -e kuma_image_qualification_approved=true
```
Request only Kvin's single `PLAY RECAP`
and `msg` from **“Report bounded
image-only qualification metadata”**,
or failed task/error. No pull logs.
After native success, promote the
native-qualified digest, separately
stage the rootless loopback app on
Kvin, and qualify UI + wanted monitor
`Wicket Ollama` actually Up at
`http://wicket.arcane.sanctum:11435/healthz`,
idempotence, data recovery and no
duplicate alerts. Only then retarget
`kuma.nexus` away from Kvar and test
real clients. A clean Kvin Kuma install
is accepted; preserving the abandoned
Kvar PoC monitor database is not required.
Do not invent arbitrary time limits
or unsupported data migration.

**Production still unchanged:** Kvar NPM and DNS remain authoritative,
Maintenance owns Kvin LAN firewall, no production cutover is approved,
Kvar-hosted Kuma/LinkStack/Pi-hole applications and data are not yet
migrated. 8/8 is **bounded proxy acceptance**, not project completion.
Follow the [November 11 outcome roadmap](docs/ROADMAP.md#active-execution-plan--wednesday-november-11-2026).

## CURRENT — Wednesday, November 11: eighth existing Yarn NPM stage coded, real-Nginx CI pending

**Actual work this morning:** Implemented SS-YX-2 in source:
- `ansible/vars/yxorp-kvin-stage.yml` has new
  **default-off** `yxorp_stage_yarn_inner_approved: false`.
- `ansible/yxorp-kvin-stage.yml` has one
  **Kvin-stage-only**, exact backend `192.168.1.110:80`
  and prior-seven-vhost guard, followed by
  in-memory enabling of ONLY existing NPM host
  `yarn.inner.sanctum` as the eighth vhost.
  `data/yxorp-routes.yml` desired enabled flags
  remain unchanged. Kvar NPM, DNS, firewall,
  production cutover and app state are NOT touched.
- `ansible/yxorp-kvin-stage-yarn-inner-probe.yml`
  separately asserts exact seven prior approvals,
  source manifest and Kvin scope; privately compares
  published and mounted Nginx config and checks exact
  two different Yarn vhosts plus old origin backend;
  invokes `tools/observe-yxorp-kvin-stage-yarn-inner.py`
  for bounded GET / from direct Yarn origin
  `192.168.1.110` and old Kvin virtual host,
  new `yarn.nexus` Kvin host, and unmatched Host.
  Returns statuses, MIME/body/redirect comparison
  booleans and default deny without leaking raw
  content or credentials. Accepts only genuine
  HTTP200 plus complete identical old-route body,
  new-host HTTP200, default deny and current
  mounted config. If comparison fails, sanitized
  `msg` prints before the failure.
  The Kvar NPM old route's TIMEOUT is known;
  it is NOT a required HTTP parity comparator.
- Synthetic **real Nginx** test in
  `tools/test-yxorp-http.py` now exercises
  old/new Yarn names against **different**
  synthetic backend identities, their forwarded
  Host and relative Location; unknown host denied.
  `tests/test_yxorp_kvin_stage_yarn_inner.py`
  tests the fixed scope and actual local wire
  comparator (including deliberately incorrect
  body and raw-data redaction).
  `tests/fixtures/verify-yxorp-kvin-yarn-inner-stage.py`
  tests **real Ansible** one/seven/eight route
  selection and refusal of illegal eighth-only
  approval. CI workflow includes these.

**Source CI PASSED:** [GitHub Actions run #43049835644](https://github.com/wdcallahan/sanctum-services/actions/runs/43049835644) completed successfully: full source contract tests, Ansible syntax, generated Nginx syntax, actual loopback Nginx HTTP integration and image-candidate checks. The earlier run's failure was external GitHub runner DNS resolution of Ubuntu package mirrors, not a source-test failure. The newest source commit includes
`strip_empty_ends:false` when reading container
Nginx config so the host-versus-mount byte equality
does not fail solely on a stripped trailing newline.

**Next native operator action — full CI green:** from Kvin run the standard
eight-route stage reconciliation with all seven
previous stage flags plus
`-e yxorp_stage_yarn_inner_approved=true`,
then `ansible/yxorp-kvin-stage-yarn-inner-probe.yml`
with the SAME flags in one `&&` chain. Ask for
the **two PLAY RECAP** lines and the sanitized
`msg` from `Report only eighth Yarn route
configuration and wire acceptance metadata`;
if failed, just failed task + error and the
already printed sanitized classification
(if any). Never ask for full logs, user
DNS decisions, or retesting the other seven
accepted vhosts.

**Following leaf:** SS-YX-3 scoped actual NPM
behavior/cross-route coverage, then clean retained
Kuma install/monitor recovery; consult the
[active outcome plan](docs/ROADMAP.md#active-execution-plan--wednesday-november-11-2026).
No arbitrary time limits. No native changes yet
this morning. Owner: Services.

## CURRENT — Wednesday, November 11: planned execution, no arbitrary timeboxes

**Morning source of truth:** [The active November 11 Services
outcome-driven plan](docs/ROADMAP.md#active-execution-plan--wednesday-november-11-2026)
is now the SINGLE owning execution sequence. It is committed
on November 10 before Nova went to sleep.
**No source execution or live network actions happen asynchronously**.
Do not imply we spent the night actively running after
this chat turn. User instructed **no arbitrary time limits**:
a task should take the time needed to be right.
Do not resurrect the misguided deadline-based
"limit Nova's time" framing. Instead require
correct outcome, meaningful independent evidence,
specific real blocker and high-value next action.

**First concrete engineering assignment: SS-YX-2.**
Rebuild the existing **eighth** Kvar NPM app vhost
`yarn.inner.sanctum` (NPM `11.conf` →
`192.168.1.110:80`) on *isolated Kvin stage*
as a **new default-off explicit stage opt-in**
layered atop the seven already native-accepted
stage routes. This must not edit
Maintenance DNS, Kvar NPM, firewall,
production cutover or source-manifest enabled
defaults. Write source and real Nginx synthetic
tests/Ansible selection tests, run CI,
then deliver one bounded native Kvin
stage+probe action. Test HTTP200 and stable
direct-origin content/metadata with original
`Host: yarn.inner.sanctum`, old/new vhost
distinction, default deny, and raw redirects
if applicable. Kvar incumbent old proxy
path has already timed out from both Kvar
host and NPM container, so do not manufacture
a parity requirement against absent
incumbent HTTP. Do not repeat seven accepted
route probes. Do not reopen the ridiculous
DNS keep/retire question: the existing
NPM vhost is in scope by definition.

**Next:** SS-YX-3 checks only material
remaining proxy custom-location, forwarded
headers, WebSockets and actual user behaviors;
do not confuse seven short HTTP
checks with fully equivalent NPM.
Then SS-APPS-1 builds a clean
retained **Kuma** on Kvin (old PoC
database migration NOT required),
and qualifies wanted monitor
`Wicket Ollama` actual Up +
persistence/recovery, with
notifications not duplicated.
SS-APPS-2 migrates LinkStack's
real `linkstack` volume at
`/htdocs` by backed-up restore
and actual named directory use.
SS-APPS-3 restores Pi-hole's
rootful config volumes and tests
opt-in ad filtering, not general
DNS; Maintenance's accepted
evidence already says no
current intended Pi-hole clients
after DHCP DNS change.
SS-APPS-4 accounts for on-Kvin
Nextcloud, EyesOnly Search,
Project Joule Prism and Maintenance
PostgreSQL without duplicating
their ownership. Last, SS-PUB
qualifies actual clients after
Maintenance-approved Kvin HTTP80
firewall publication, then
distinct approved DNS/Kvar
cutover and host retirement.
Peanut standby is a future
resilience gate, not a claim
that yesterday's test equals
working automatic failover.

**Proof discipline:** Our actual
current Kvin stage has seven of
eight routes accepted at **initial
anonymous localhost HTTP only**,
no production publication.
Kvar NPM/DNS remain production.
Kvar Kuma, LinkStack and Pi-hole
still run there, not migrated.
Old Yarn NPM log had three
requests from Kvin .192 and
three from Inner NAT egress .104;
the .104 address doesn't identify
an individual Inner client
without retained historical
session/NAT data. These were
diagnostics, not architecture choices.

**Operator relationship:** Pixel writes/
revises source, CI tests, GitHub docs
and boards directly; asks Nova
only for necessary native runs,
relevant informed authorization
and meaningful real-client
acceptance. No unnecessary
daily report, repeated full logs
or sequential one-off probes.
Every next action advances a
named outcome and has a
specific evidence-based exit.

**Historical notes below preserve
earlier investigation, NOT current
instructions.**

## CURRENT — November 10: three of six old Yarn log requests are NOT from Kvin's known observer source; exact addresses next

**Nova's latest native Kvar source-category report:**
`ansible/yxorp-kvar-legacy-yarn-source-classes.yml`
finished `ok=5 changed=0 failed=0`.
Current NPM proxy-host 11 log has **six**
records within last 30 days, with:
`known_kvin_observer:3`,
`other_observed_source:3`,
`known_kvar_host:0`,
`known_kvar_loopback:0`,
`unclassified_format:0`.
No log truncation; one readable
file. `all_classified_sources_known_tests=false`.
**The other three may be one
or several machines**, NAT/proxies
could affect IP identity; they
are not proof of a human user
or required old hostname.
**Do not retire or activate**
old `yarn.inner.sanctum` based
on this count alone.

**User explicitly asked why source IP
addresses were hidden and whether they
are secrets.** Correct response:
addresses from their private
network are operational identifiers,
not credentials; excessive
redaction was an obstacle to
debugging. Keep tokens, raw
queries/paths, passwords/cookies
and full log lines protected,
but source addresses and aggregate
request counts are now appropriate
to display to the operator.

**New narrow diagnostic:**
`ansible/yxorp-kvar-legacy-yarn-source-addresses.yml`
targets ONLY existing Kvar
NPM via known SSH inventory,
checks cutover false and disabled
old Yarn manifest route, and runs
`tools/observe-yxorp-kvar-yarn-source-addresses.js`
through Podman's existing NPM
Node. The helper reads at most
1MiB each from the same fixed
proxy-host 11 access log and
one plain rotation, counts only
30-day records with explicit
`[Client IPv4]` syntax, and
emits exact IP and count of each
observed source, with known
Kvin and Kvar labels. It never
emits access log lines, HTTP
paths, queries, credentials,
cookies or raw errors. It reports
coverage and truncation, and
always keeps `safe_to_retire_proven:false`.
Source contract and synthetic
test include three Kvin requests
and three other requests from
two different IPs, plus
ambiguous log format handling.
The exact other IPs are
**not yet known**; don't
invent them.

**Next Kvin command after source CI green:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvar-legacy-yarn-source-addresses.yml
```
Ask only Kvar's `PLAY RECAP`
and `msg` dictionary from
**“Report only old Yarn NPM logged
source addresses and counts”**,
or failed task/error. Once actual
addresses known, compare against
existing device inventory where
available and ask for a
deliberate alias policy;
do not keep multiplying
probes indefinitely.

**Architecture unchanged:** 7 of 8
route names qualified in Kvin's
limited local anonymous HTTP
stage. Legacy old Yarn name
disabled on Kvin; Kvar NPM and
wildcard DNS still production.
Earlier Kvar host and container
both failed to connect to old
Yarn despite Kvin direct HTTP200;
this is not isolated to NPM.
LinkStack, Kuma and Pi-hole
application state still on
Kvar and not migrated.
No Kvar network repair,
firewall, cutover or retirement
authorized. End with
concrete operator action.

## CURRENT — November 10: six old Yarn NPM access entries, real consumer still unknown; test-source categories next

**Latest exact native report:** Nova ran
`ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml`
from Kvin against the existing Kvar NPM,
with Kvar `ok=5 changed=0 failed=0`.
The generated proxy-host 11 config was
present, `exact_access_log_directive=true`.
Exactly **one** current plain access
log was found and fully read (no
tail truncation, no additional or
compressed rotations observed);
**six lines**, all six with parseable
timestamps, all within last seven
and 30 days, newest age **0 days**.
These may be requests from Services'
recent Kvin tests or from actual clients.
`current_client_use_proven=false` and
`safe_to_retire_proven=false`.
A single current log provides no
assurance older rotated data never
existed, and it cannot account for
clients not visiting the old route.

**Earlier independent evidence still valid:**
The Kvin observer can reach old Yarn
origin by IP and DNS and via new
`yarn.nexus.sanctum` stage (all
HTTP200), whereas Kvin→old Kvar NPM
times out. Even **Kvar HOST** and its
NPM container could not reach the
Yarn origin in earlier native tests.
The root cause lies in Kvar's
source/transport/return behavior,
not proven to be an NPM-specific
configuration flaw. No need to
repair Kvar's old path unless an
actual consumer needs it; don't
repeat old reachability or route
tests. Old `yarn.inner.sanctum`
remains **disabled** in the Kvin
stage and checked-in production
manifest. Kvar NPM and wildcard
DNS still production, no firewalld
or cutover changes.

**New source-only follow-up:** A
`ansible/yxorp-kvar-legacy-yarn-source-classes.yml`
read-only, Kvar-only play executes
`tools/observe-yxorp-kvar-yarn-source-classes.js`
inside existing `nginx-proxman`.
The script reads only the fixed
current and one plain rotated
`proxy-host-11_access.log`, max
1 MiB tail per file. It strictly
recognizes the NPM access log's
`[Client IPv4]` field; any other
format remains unclassified.
Each recent record falls into
one of **known Kvin test-host
source**, **known Kvar host**,
**Kvar loopback**, **other observed
source** or **unclassified format**.
It never emits a client address,
HTTP request path, log line,
timestamp, cookie, token,
exception or full URL. Counts
can include our own requests;
source labels do not prove a
human, process, or real client
dependency. Retire permission
remains **false** regardless
of counts. The source has
synthetic tests of known/other/
unrecognized sources and
sensitive-value redaction.

**Current qualification:** 7/8
initial anonymous HTTP route
names accepted on Kvin: Yarn,
Square, Prism, Search, interim
LinkStack, interim Kuma and
interim Pi-hole. Eighth legacy
`yarn.inner.sanctum` intentionally
disabled/undecided. LinkStack,
Kuma and Pi-hole application
and persistence still live on
Kvar and require stateful Kvin
restores before Kvar retirement.

**Next exact command from Kvin,
after CI passed:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvar-legacy-yarn-source-classes.yml
```
Return ONLY Kvar's one-line
`PLAY RECAP` and `msg`
from **“Report only old Yarn NPM
client-source classes and sample
coverage”**. If it fails, paste
only failed task/error. No full
logs or the individual source IPs.
This is a final bounded consumer
signal; afterward preserve the
legacy-name policy for an
explicit operator decision rather
than expanding network probes
indefinitely. Every assistant
response should end with a
concrete action.

## CURRENT — November 10: old Yarn alias reachable from Kvin, broken from Kvar; bounded consumer signal next

**Latest native response from Nova:** The Kvin-only read-only
`ansible/yxorp-kvin-legacy-yarn-observe.yml` finished
`ok=4 changed=0 failed=0`. From Kvin all these
anonymous GET / requests returned **HTTP200**
with media type present and no redirect:
old origin `192.168.1.110:80` with
`Host: yarn.inner.sanctum`, old origin by
`yarn.inner.sanctum` DNS name with old
Host, origin IP with new Host
`yarn.nexus.sanctum`, and accepted
new Kvin YXORP `yarn.nexus.sanctum`.
`legacy_through_incumbent_npm` from
Kvin to Kvar NPM **timed out** (no HTTP
status); status equality not comparable.
Old route remains **disabled** in
source and new Kvin stage. Both Yarn
host headers work at the origin,
but equal HTTP200 statuses alone do
not prove identical content or client
sessions.

**CRITICAL existing Kvar evidence already accepted,
do not repeat:** Earlier native
`ansible/yxorp-npm-path-diagnose.yml`
showed **Kvar HOST→192.168.1.110:80**
returned no HTTP response and
**Kvar NPM container→same IP:80** also
timed out. See [issue #2 comment
#6777002547](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6777002547).
Prior route observation reported
both Kvin and Kvar selecting the
same gateway for Yarn but different
source IPs; this does not establish
a packet failure cause. Thus the
failure is **not proven to be NPM's
configuration**: Kvar's own transport
or return path to Yarn is broken,
while Kvin can reach it.
[Issue #2 comment #6777997059](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6777997059)
explicitly deferred repairs to that
obsolete Kvar path unless a real
consumer needs it.

**Route status:** 7/8 manifest names
tested/initially HTTP accepted on
new Kvin YXORP (Yarn, Square,
Prism, Search, LinkStack, Kuma,
Pi-hole); old `yarn.inner.sanctum`
name is not a deployed eighth Kvin
route and requires **consumer/retirement
policy decision**. Kvar NPM and
wildcard DNS still production.
No application/data restores for
Kvar-hosted LinkStack/Kuma/Pi-hole
were accepted and no remote Kvin
firewall/cutover authority.

**Next scoped consumer signal:** New
`ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml`
runs **read-only** against the exact
`kvar.outer.sanctum` NPM inventory
host, with fixed route identity and
cutover-closed assertions. It executes
`tools/observe-yxorp-kvar-yarn-usage.js`
inside the existing `nginx-proxman`
container using Node already verified
by earlier diagnostics. It inspects
only the fixed old generated proxy-host
`11.conf`, and at most the last 1 MiB
each from current and one plain rotated
`proxy-host-11_access.log` files,
without exposing **any log line,
client IP, URL/path, cookie, token,
or exception**. Its output contains
only file coverage, observed lines,
timestamp parsing coverage and
aggregate request counts within 7
and 30 days. It explicitly marks
`safe_to_retire_proven=false` and
`current_client_use_proven=false`:
some counts may be from *our own*
diagnostics, missing/old/rotated logs
can hide clients, and absence of
records cannot authorize retirement.
The consumer status must be resolved
by a separate operator decision.

**Next action from Kvin after green CI:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml
```
Return ONLY Kvar's one-line `PLAY RECAP`
and the `msg` dictionary from
`Report only old Yarn NPM access-log
coverage and aggregate counts`,
or failed task/error. No full logs;
no repeat Kvar reachability/route
checks. If unavailable, preserve
unknown status, not retirement.
Every assistant turn ends with a
concrete operator action.

## CURRENT — November 10: Pi-hole seventh Kvin route passes; legacy Yarn alias investigation next

**Native Pi-hole Kvin HTTP acceptance:** Nova ran the
seven-route stage reconciliation with
Yarn+Square+Prism+Search+LinkStack+Kuma+Pi-hole,
obtaining `ok=46 changed=3 failed=0 skipped=1`.
The read-only `ansible/yxorp-kvin-stage-pihole-probe.yml`
returned `ok=4 changed=0 failed=0`
with the following raw-wire results for
`Host: pihole.nexus.sanctum`:
- **GET /**: direct Kvar :82, incumbent Kvar NPM :80
  and Kvin stage localhost :80 all **HTTP404**,
  all status equal, candidate/incumbent media type equal,
  and no redirect at any path. No redirect equality
  is comparable; 404 here is an expected/consistent
  result, **not** a UI availability failure.
- **GET /admin/**: direct, incumbent and stage
  **HTTP302**, all statuses equal; candidate/incumbent
  MIME type equal. All three redirect types are
  `relative`, and candidate/direct and
  candidate/incumbent **original raw Location
  headers exactly equal**.
- `application_migrated_to_kvin=false`;
  this is anonymous UI proxy behavior, **not**
  Pi-hole DNS filtering, ad lists, login, client
  settings, persisted data or app restore on Kvin.

**Current count: 7/8 named routes tested on
new Kvin YXORP stage, all 7 passed
limited initial HTTP checks**: Yarn, Square,
Prism, Search, interim LinkStack, interim
Kuma, interim Pi-hole. The only unqualified
name is legacy `yarn.inner.sanctum` →
`192.168.1.110:80`. It **must remain
disabled** until an explicit consumer/use
and route-retirement decision, not
enabled simply to make the count 8/8.
Its incumbent Kvar NPM path previously
timed out in earlier route observations.
The new `yarn.nexus.sanctum` route
is separately requested, accepted and
does not itself prove the old name can
be retired.

**Next source-managed bounded task:**
`ansible/yxorp-kvin-legacy-yarn-observe.yml`
executes **only read-only HTTP observations**
from the exact Kvin observer with the old
route checked to be disabled, cutover
approval false, no Kvar/DNS/firewall
changes. The companion
`tools/observe-yxorp-legacy-yarn.py`
checks five anonymous root GET paths:
old origin by literal IP `192.168.1.110`
with old Host, old origin by DNS name
with old Host, existing Kvar NPM `:80`
with old Host, accepted Kvin stage
with new `yarn.nexus.sanctum` Host as
control, and old origin IP with new
Host to test name/header sensitivity.
Reports only bounded HTTP status,
outcome, redirect *kind*, media-type
presence and comparable status booleans;
no raw URL, response content, redirect,
cookie, secrets or errors. Timeouts/
failure on individual paths are nonfatal
and classified without guessing.
This can establish reachability but
**cannot decide client usage or
retirement**; follow with consumer
inventory if appropriate. There is
no eighth-stage route activation.

**Next operator command on Kvin,
after source CI passes:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-legacy-yarn-observe.yml -e yxorp_kvin_stage_approved=true
```
**Request only** the one-line `PLAY RECAP`
and the `msg` object from **“Report only
old Yarn alias HTTP transport
classifications”**, or the failed task
and error. No long logs or reruns
of accepted seven routes. Kvar NPM
and wildcard DNS remain production.
Maintenance owns Kvin firewall.
Kvar-hosted LinkStack, Kuma and Pi-hole
still need separate application/state
migration before cutover or Kvar
retirement. Every assistant turn
ends with one concrete operator task.

## CURRENT — November 10: Kuma raw-wire redirect ACCEPTED; Pi-hole seventh candidate ready

**Decisive actual operator result:** The read-only
`ansible/yxorp-kvin-stage-kuma-wire-observe.yml`
completed `ok=7 changed=0 failed=0` on Kvin.
It privately inspected published and
Podman-mounted Nginx config:
`published_equals_container_mount=true`,
`mounted_config_has_kuma_virtual_host=true`,
`mounted_config_has_exact_kuma_redirect_rule=true`,
`mounted_config_exact_redirect_rule_count=1`.
Crucially, Python `http.client` on Kvin
read the **unaltered wire Location header**
from direct old Kvar Kuma :3001, Kvar NPM
:80 and local Kvin stage :80:
each was **HTTP302 with a *relative*
Location** (`absolute=false`,
`host_class=relative`),
`candidate_wire_equals_incumbent_wire=true`
and `candidate_wire_equals_direct_wire=true`.
The direct backend did not change Location
when proxy forwarded headers were present.
**Kuma therefore PASSED its bounded anonymous
GET / HTTP redirect parity as actually
observed on the wire.** The earlier
Ansible `uri.location` full URL/host/port
comparisons were **test artifacts**:
relative Location headers were
resolved against each request URL,
creating spurious loopback:80 vs
Kvar host/port differences.
Do not mistake those normalized
URI properties for a real absolute
Location header from the wire.

**Project count is now 6/8 names tested and
6/6 passed initial scoped local HTTP checks:**
Yarn, Square, Prism, Search, interim Kvar-backed
LinkStack and interim Kvar-backed Kuma.
Pi-hole and legacy Yarn inner name remain
untested on Kvin. Kuma login, monitor state,
Socket.IO/WebSockets, notifications and eventual
Kvin service restore still NOT accepted.

**Source cleanup:** The Kuma-only
`redirect_strip_upstream_port` flag
and explicit Nginx `proxy_redirect` rule
were unnecessary because the observed
redirect was relative. These have been
removed from the checked-in manifest,
Nginx template and stage guard. The
previously executed stage still contains
the obsolete rule until the next native
stage reconcile. Source regression
tests now assert the plain template
leaves relative Locations intact and
Kuma has no special policy. Historical
read-only Kuma wire observer can
still inspect mounted configuration.
The checked-in desired manifest
remains **Yarn-only**; no production
Kvar, DNS or firewall changes.

**Next native stage route (7th):**
`pihole.nexus.sanctum`, current Kvar
Pi-hole **UI** backend port82.
New default-off stage flag
`yxorp_stage_pihole_approved: false`
in `ansible/vars/yxorp-kvin-stage.yml`.
`ansible/yxorp-kvin-stage.yml`
requires the six prior Kvin stage
flags, exact disabled Pi-hole manifest,
Kvar :82 upstream and no WebSocket,
then enables only Pi-hole as seventh
in-memory vhost. Other legacy
`yarn.inner.sanctum` stays off.
The stage validation/remount/health
guards remain unchanged.

**Pi-hole observer:**
`ansible/yxorp-kvin-stage-pihole-probe.yml`
loads source-managed
`tools/observe-yxorp-pihole-wire.py`
using Python `http.client` from Kvin.
Independently compares direct old Kvar :82,
incumbent Kvar NPM :80 and local Kvin
stage :80, both anonymous GET /
and GET /admin/. Reports only HTTP
status/MIME equalities, redirect presence
and **raw Location equality** (never
Ansible's normalized URI Location),
and redirect kind (relative/absolute/
absent). No Location values,
queries, HTML, cookies, credentials
or raw exceptions. A root / 404
does NOT by itself imply Pi-hole down;
the /admin/ UI path is independently
tested. Does NOT qualify Pi-hole
DNS blocking, login, client settings,
data migration or service restore.

**Next exact Kvin command, after CI green:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true -e yxorp_stage_pihole_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-pihole-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true -e yxorp_stage_pihole_approved=true
```
**Operator output only:** two one-line
`PLAY RECAP` results and the
`msg` dictionary from **“Report only
Pi-hole root and admin HTTP parity
metadata”**; if failure only the
failed task and error. Never demand
entire Ansible logs or already
accepted Kuma rechecks. The
checked-in manifest is still
Yarn-only. Kvar NPM/wildcard DNS
remain production; Maintenance
owns Kvin LAN HTTP80 firewalld.
Kuma, LinkStack and Pi-hole app
state remain on Kvar. Do not
authorize cutover or Kvar retirement.
Each assistant turn ends in
a concrete operator action.

## CURRENT — November 10: Kuma redirect still mismatched after CI-qualified fix; raw-wire diagnosis needed

**Latest native result:** Nova reran the checked-in
Kuma-only `proxy_redirect` fix against the live
Kvin stage. Stage reconcile completed
`ok=44 changed=3 failed=0 skipped=1`;
the read-only Kuma three-path probe
`ok=4 changed=0 failed=0` again showed
**HTTP302** through direct Kvar Kuma `:3001`,
Kvar incumbent NPM `:80`, and Kvin
stage loopback `:80`. Candidate
and incumbent status, MIME type, redirect
scheme/path still match, but
`candidate_redirect_equals_incumbent=false`,
`candidate_redirect_host_equals_incumbent=false`,
`candidate_redirect_port_class=other_explicit_port`,
versus incumbent `no_explicit_port`.
**Kuma must remain unaccepted**.
Do not assume the source fix changed
the live raw wire header. Stage recap
success does not establish parity.

**Prior read-only authority classification:**
Candidate Location class `loopback`,
explicit `stage_http_port_80`; incumbent
class `kvar_backend_host` no explicit port;
direct class `kvar_backend_host` port3001.
The first correction is explicitly declared
in the disabled Kuma route and shared
Nginx template; CI's *synthetic*
Nginx test passed, but native parity
did NOT. Need separate running
config and raw header measurements;
do not try another speculative rewrite.

**New source-managed investigation:**
`ansible/yxorp-kvin-stage-kuma-wire-observe.yml`
is **read-only** on the exact already
approved Kvin stage. It privately reads
published host `nginx.conf` and the
mounted config inside only
`sanctum-yxorp-kvin-stage`, verifying
mount equality and presence/count of
`proxy_redirect http://kvar.outer.sanctum:3001/ http://kvar.outer.sanctum/;`.
It invokes `tools/observe-yxorp-kuma-wire.py`
via `python3 -c` with fixed host/port
pairs to independently read the actual
Location header from the HTTP wire,
without following redirects or using
the Ansible URI module. It compares
direct Kvar backend :3001, incumbent
Kvar NPM :80, Kvin loopback :80, and
a direct Kvar request with the same
proxy-style forwarded headers as
Nginx. The report ONLY exposes
safe hostname/port classes, statuses,
boolean Location equalities and
mount-rule presence; never raw
redirect strings, paths/query values,
cookies, error details or config text.
A synthetic local HTTP test uses
localhost servers and checks raw
header and forwarded-header handling.
This distinguishes an Ansible URI
reporting artifact, absent mounted
policy and upstream behavior.

**Next exact operator command, Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-wire-observe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```

**Return ONLY** its single `PLAY RECAP`
line and the `msg` dictionary from
`Report only Kuma wire classes and mounted
Nginx rule presence`. If the play fails,
only failed task/error; don't paste
full logs or repeat deployment/probes.
Leave Kvar, DNS, Kvin firewall and
production cutover unchanged.

**Count:** 6/8 route names attempted;
five scoped anonymous HTTP tests
accepted (Yarn, Square, Prism, Search
and interim Kvar-backed LinkStack).
Kuma pending; Pi-hole and old
`yarn.inner.sanctum` untested.
Kuma/LinkStack/Pi-hole app+data
still live on Kvar and need separate
migration before Kvar retirement.
Every assistant turn should leave
Nova a concrete next action.

## CURRENT — November 10: Kuma redirect diagnosed, targeted source fix implemented, native stage retest next

**Native Kuma redirect root cause now specifically classified.**
The user ran `ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml`
on Kvin; read-only play recap `ok=4 changed=0 failed=0`.
The three `Host: kuma.nexus.sanctum` anonymous root redirects:
- Direct Kuma on Kvar `:3001`: **HTTP302**, Location host class
  `kvar_backend_host` with explicit `kuma_backend_port_3001`.
- Incumbent Kvar NPM `:80`: **HTTP302**, same Kvar backend hostname
  with **no explicit port**.
- New Kvin staged YXORP `127.0.0.1:80`: **HTTP302**, Location host
  class **`loopback`** and port **`stage_http_port_80`**.
- All redirect path, query, fragment match incumbent, and the
  direct/incumbent hostname is equal. Candidate/incumbent host and
  full Location are different. `configuration_changed=false`.

**Root cause:** Existing template's implicit Nginx
`proxy_redirect default` rewrites the backend absolute
`Location` into the incoming Kvin loopback test authority.
Kvar NPM instead strips backend port `3001` from its
absolute Kvar-host redirect while retaining the Kvar hostname.
The current stage has NOT yet been reconciled with the fix.

**Source-managed targeted correction implemented:**
`data/yxorp-routes.yml` adds only to disabled Kuma entry
`redirect_strip_upstream_port: true`. The shared
`ansible/roles/yxorp/templates/nginx.conf.j2` renders,
ONLY when that policy is true:
`proxy_redirect http://kvar.outer.sanctum:3001/ http://kvar.outer.sanctum/;`
(generalized from declared upstream fields). This overrides
Nginx's unwanted localhost:80 rewrite **only for Kuma**.
The Kvin stage's guarded Kuma task additionally asserts that
the flag is present and the backend is the exact old Kvar :3001.
No other routes' policies or enabled states were modified;
checked-in production manifest remains **Yarn only**.
The source change must be reviewed/removed when Kuma's
application actually migrates to Kvin.

**Synthetic proof:** `tools/test-yxorp-http.py` now uses
a real local Nginx and synthetic origin which redirects
with an explicit backend port, and asserts that Kuma policy
produces exactly the backend hostname without its service
port while retaining redirect path/query/fragment. It
also asserts the other host's default behavior remains
unchanged. New `tests/test_yxorp_kuma_redirect_policy.py`
checks exact manifest scope, template rendering and
preflight. All tests are in the YXORP source workflow.
Do **not** declare the sixth route accepted until
native Kvin rerun reports actual Location parity.

**Current accounting:** 6/8 routes attempted; 5 passed first
local HTTP checks (Yarn, Square, Prism, Search and interim
LinkStack). Kuma pending; Pi-hole and legacy Yarn inner
untested. Kvar NPM and wildcard DNS still production;
Kvin LAN HTTP80 firewall owned by Maintenance.
LinkStack, Kuma and Pi-hole applications/data still
reside on Kvar, not migrated to Kvin.

**Next exact operator command on Kvin AFTER CI passed:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```
**Request only two one-line PLAY RECAP results and
the `msg` dictionary from “Report only Kuma status
and redirect authority components”**, or a failed
task/error if failure occurs. No verbose logs,
no reruns of accepted other routes.
**Acceptance requires actual
`candidate_redirect_equals_incumbent:true`**,
not just matching 302. No production changes.
Every turn ends with a concrete next action.

## CURRENT — November 10: Kuma stage HTTP302 REDIRECT MISMATCH (6 attempted, 5 accepted); read-only diagnosis next

**Exact native Kuma evidence received:** The Kvin staged
YXORP reconciliation with Yarn, Square, Prism, Search,
LinkStack and Kuma selected passed
`ok=44 changed=3 failed=0 skipped=1`. The separate
`ansible/yxorp-kvin-stage-kuma-probe.yml` passed its
read-only tasks `ok=4 changed=0 failed=0` and exposed
the intended sanitized report:
- Direct Kvar Kuma `:3001`, Kvar NPM `:80`, and
  new Kvin stage `127.0.0.1:80` all returned **302**,
  with redirect present.
- Candidate and incumbent have equal HTTP status
  and MIME, redirect **scheme and path** match.
- **NOT PARITY:** `candidate_redirect_equals_incumbent=false`,
  `candidate_redirect_host_equals_incumbent=false`,
  `candidate_redirect_port_class=other_explicit_port`,
  while incumbent is `no_explicit_port`.
  The actual candidate redirect hostname and port are
  not yet classified; do not invent them.
- Kuma still runs on **Kvar**, no application/data
  restore onto Kvin. Do not mark sixth route accepted.

**Current count: 6/8 routes attempted on Kvin,
5/6 accepted at first local HTTP behavior:**
Yarn, Square, Prism, Search and interim
LinkStack. Kuma is blocked on redirect parity.
Pi-hole and old `yarn.inner.sanctum` untested.
Kvar NPM is still live for wildcard
DNS; host firewalld and production cutover
unchanged.

**Next isolated read-only task:** New
`ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml`
(requires all earlier stage flags). This does
**not** rerun installation or change any
config. On Kvin it performs only bounded,
nonfatal, no-log anonymous GET /
requests with Kuma Host header through
direct Kvar :3001, incumbent Kvar NPM
and local Kvin stage. It classifies
redirect hostname into safe categories
(frontend / Kvar / Kvin / loopback /
relative / other), and explicit port as
(80 / 3001 / none / other), and
reports whether host, path, query and
fragment match NPM. No raw URL,
hostname outside whitelist, query,
cookie, response body or error is shown.
Source includes tests of multiple
synthetic redirect cases with actual
Ansible/Jinja expressions.

**Next command after green CI, Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```
**Ask only the single one-line `PLAY RECAP`
and `msg` from `Report only Kuma redirect
host classes and explicit port classes`.**
If it fails, request only the failed
task/error. No repeated five-route
tests, no full Ansible log. Once the
safe categories identify cause, make
a source-only, behavior-tested
targeted Nginx config fix (if required)
before another stage restart and
re-test. Never force all routes
on or touch Kvar, firewall, DNS or
production cutover. Every assistant
turn ends with an executable action.

## CURRENT — November 10: 5 of 8 Kvin initial HTTP routes accepted; Kuma sixth canary prepared

**Native LinkStack initial HTTP comparison ACCEPTED.**
Nova supplied the sanitized result from
`ansible/yxorp-kvin-stage-dir-probe.yml`:
with `Host: dir.nexus.sanctum`,
direct old Kvar LinkStack `:8081`,
incumbent Kvar NPM `:80` and new Kvin
YXORP stage `127.0.0.1:80` all
returned **HTTP200**. All-three-have-
HTTP, candidate/direct status equality,
candidate/incumbent status equality and
candidate/incumbent content-type equality
were **true**. Neither proxy redirected;
the sanitized observer correctly said
`candidate_redirect_equals_incumbent:
not_comparable` and
`application_migrated_to_kvin:false`.
The read-only probe recap was
`ok=4 changed=0 failed=0`. The
separate fifth-stage reconciliation
recap was not supplied, but the
running Kvin candidate did respond.
Do not request that missing recap
or rerun the accepted probe.

**Current YXORP stage progress:** 5 of 8
declared names have passed their first
bounded Kvin local HTTP tests: Yarn,
Square, Joule/Prism, Search and LinkStack.
Three untested on Kvin:
`kuma.nexus.sanctum`,
`pihole.nexus.sanctum`,
`yarn.inner.sanctum`.
Kvar NPM is still production; wildcard
DNS, Maintenance Kvin port80 firewall and
production cutover remain unchanged.

**Migration boundary:** LinkStack, Kuma and
Pi-hole still run on Kvar. Their
Kvin-stage proxy comparisons to Kvar's
backends are interim routing evidence,
not a successful app/persistent-state
restore on Kvin or authorization to
retire Kvar. `docs/SERVICE-ESTATE.md`
preserves Kvin destination and these
restore obligations.

**Next sixth route source:** New default-off
`yxorp_stage_kuma_approved: false`
in `ansible/vars/yxorp-kvin-stage.yml`.
If all previous Kvin stage opt-ins plus
the Kuma flag are true,
`ansible/yxorp-kvin-stage.yml` checks
that only the first five exact names
are projected and the sixth disabled
route points to `kuma.nexus.sanctum`
→ `http://kvar.outer.sanctum:3001`
with WebSocket true. It then adds only
Kuma to the in-memory Kvin stage config.
Checked-in production routes remain
Yarn-only, and the role's candidate
`nginx -t`, drift-aware Podman remount
and post-start file-equivalence checks
remain in effect.

**Special redirect rule:** Kvar NPM
previously removed explicit backend
port 3001 from Kuma's absolute 302
redirect; the direct backend includes
it. Do **not** assume full redirect
equality before observing the new
proxy. The read-only bounded
`ansible/yxorp-kvin-stage-kuma-probe.yml`
compares direct old Kvar :3001, Kvar
NPM :80 and Kvin stage :80 anonymous
GET / requests. It reports HTTP status,
candidate/incumbent content-type,
conditional redirect equality, and
**safe hostname/scheme/path equality
plus explicit port classification**
without leaking raw Location URLs
or cookies. A difference is evidence
for a later source fix, not proof
the backend is broken. Kuma
application data, monitors, sessions
and restore are not tested.

**Next exact native operator command
on Kvin, after source CI passes:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```

**User output contract:** Ask for ONLY both
one-line PLAY RECAP entries and the
`msg` dictionary from **“Report only
Kuma status and redirect authority
components”**. If any task fails,
only its failed-task/error output.
A clean nonfatal probe recap does not
prove 302 parity. Avoid full logs
to conserve context. Every Services
assistant turn ends with a concrete
next action (not merely a status
report).

## CURRENT — November 10: Search local HTTP accepted (4/8); interim LinkStack canary ready

**Native acceptance:** Nova ran `ansible/yxorp-kvin-stage.yml`
with Yarn, Square, Prism and Search selected, obtaining
**`ok=40 changed=3 failed=0 skipped=1`**. The bounded
`ansible/yxorp-kvin-stage-search-probe.yml` completed
`ok=4 changed=0 failed=0`; its **actual sanitized HTTP report**
shows `search.nexus.sanctum` anonymous GET / HTTP200
through direct `kvin.outer.sanctum:8083`, existing
Kvar NPM and new Kvin stage, with
`all_three_have_http_response=true`,
candidate/direct and candidate/incumbent status equality
true and candidate/incumbent content-type equality true.
Neither proxy redirected. **Accept anonymous root HTTP
routing for Search**, not actual search queries/results,
sessions, remote clients or production traffic.

**Route count: 4 of 8 tested on new Kvin YXORP,
4 of 4 initial local HTTP checks passed:**
Yarn, Square, Prism, Search. Four untested remain:
`dir.nexus.sanctum`, `kuma.nexus.sanctum`,
`pihole.nexus.sanctum`, `yarn.inner.sanctum`.
Kvar NPM and wildcard DNS remain production, and
Maintenance owns Kvin LAN port80 firewall admission.

**Critical migration distinction:** LinkStack, Kuma and
Pi-hole remain hosted on **Kvar**, not Kvin. Testing
Kvin's proxy to those old backends may qualify interim
HTTP compatibility only, **not app/data migration**.
Per `docs/SERVICE-ESTATE.md`, all three must eventually
have state/persistence/restoration accepted on Kvin
before Kvar can be retired. Old `yarn.inner.sanctum`
has a separately known timeout from Kvar and requires
a client-name retirement/usage decision, not blind promotion.

**Next source-managed interim LinkStack trial:** Added
default-off `yxorp_stage_dir_approved: false` to
`ansible/vars/yxorp-kvin-stage.yml`.
`ansible/yxorp-kvin-stage.yml` requires all prior
Yarn/Square/Prism/Search stage flags, checks the
exact fourth existing projection and `dir.nexus.sanctum`
→ `http://kvar.outer.sanctum:8081`,
WebSocket false, then projects only LinkStack as a
**fifth stage-only route**. Checked-in
`data/yxorp-routes.yml` remains Yarn-only.
The existing role safely validates Nginx,
detects stale mounts, restarts only the Kvin
test stage when needed and checks mounted config
equality; it does not edit Kvar, DNS, firewall
or production authority.

`ansible/yxorp-kvin-stage-dir-probe.yml`
compares three bounded private anonymous GET /
requests from Kvin with `Host: dir.nexus.sanctum`:
direct old Kvar LinkStack :8081, incumbent Kvar
NPM :80, and local Kvin stage :80. Its report
has statuses, status/MIME and conditional redirect
equality, no body/URL/cookie/credential leakage.
The report includes `application_migrated_to_kvin:false`.

**Next exact operator command, after CI passes:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-dir-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true
```
**Ask Nova ONLY for the two short `PLAY RECAP` lines
and `msg` from `Report only LinkStack HTTP status
and compatibility metadata`**. If a task fails,
request only that task and error. Never demand
full logs from a successful run; conserve context.
The nonfatal comparison's recap alone cannot
accept LinkStack. Every assistant turn must end
with a concrete next action, not merely status.

## CURRENT — November 10: Prism local HTTP accepted; Search fourth route canary prepared

**Actual native Kvin Prism:** Stage reconcile with
Yarn+Square+Prism enabled through explicit Kvin
stage flags completed `ok=38 changed=3 failed=0
skipped=1`. The follow-up anonymous GET /
three-path comparison completed `ok=4 changed=0
failed=0`; its sanitized native report showed
**HTTP200** for direct Prism backend
`kvin.outer.sanctum:8084`, incumbent
Kvar NPM `kvar.outer.sanctum:80`, and
new Kvin YXORP `127.0.0.1:80`.
All three supplied valid HTTP responses,
candidate/incumbent and candidate/direct
statuses matched, and candidate/incumbent
content types matched. Neither candidate
nor incumbent returned a redirect, so
`candidate_redirect_equals_incumbent` was
correctly `not_comparable`. **Accept
initial local anonymous Prism HTTP routing,
NOT login/streaming/WebSocket semantics.**

**Route count: 3/8 tested through new Kvin
stage; 3/3 passed bounded first HTTP checks.**
Accepted: Yarn HTTP200/body parity; Square
HTTP302 and exact incumbent redirect/MIME
parity; Prism HTTP200 status and MIME parity.
Five remaining names have not passed on
new Kvin stage.

**Next fourth route:** New default-off
`yxorp_stage_search_approved: false`
flag in `ansible/vars/yxorp-kvin-stage.yml`.
`ansible/yxorp-kvin-stage.yml` selects
only Search `search.nexus.sanctum` →
`http://kvin.outer.sanctum:8083` alongside
the existing Yarn/Square/Prism stage routes
*when all four separate scope/route flags
are supplied*. It validates the exact
eight-entry source manifest and already-
selected previous three routes before
projecting Search via a stage-only
`set_fact`. Manifest remains Yarn-only.
The shared role validates candidate
Nginx configuration, handles the Podman
single-file config remount/restart, and
verifies mounted/host equality.

`ansible/yxorp-kvin-stage-search-probe.yml`
independently compares three anonymous,
bounded, private GET / requests from Kvin
with `Host: search.nexus.sanctum`:
direct `kvin:8083`, incumbent Kvar NPM:80,
and Kvin stage `127.0.0.1:80`. Its output
is limited to HTTP status, status/MIME
equality and conditional redirect metadata;
no full URLs, queries, content, credentials,
cookies or errors are emitted. This
is only root HTTP routing, not an
actual search-results functional test.

**Next operator command on Kvin after
source CI succeeds:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-search-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true
```

**Request only**: the one-line recap from
each of the two plays and the sanitized
`msg` dictionary from
**“Report only Search HTTP status and
anonymous metadata parity”**. On failure,
ask for only the failed task and error.
Do not request verbose run output or
already accepted test results. Always
end user-facing turn with something
actionable. Kvar NPM remains authoritative
for existing wildcard DNS; Kvin LAN
firewall belongs to Maintenance and
neither DNS nor production cutover
are authorized.

## CURRENT — November 10: Yarn and Square accepted; Prism HTTP canary prepared

**Updated native Kvin progress: 2 of 8 declared routes
tested, both passing *initial local HTTP*
acceptance.** Yarn forwarded HTTP200 with
identical direct origin response bodies.
Square/Nextcloud's anonymous GET / returned
HTTP302 through direct Kvin :8085,
incumbent Kvar NPM, and new Kvin stage;
candidate status, full Location and
content type matched Kvar NPM. The
drift-aware single-file mount repair ran
successfully on Kvin `ok=36 changed=1
failed=0` with the mandatory mounted
config readback; the subsequent Square
comparison `ok=4 changed=0 failed=0`
has an explicit native sanitized report
with all status/redirect parity flags true.
**Do not request the Square report again
or re-run these accepted checks.**

**Next source work:** The stage-only
`yxorp_stage_prism_approved: false`
flag is added to
`ansible/vars/yxorp-kvin-stage.yml`.
If both Square and Prism opt-ins are
passed, `ansible/yxorp-kvin-stage.yml`
verifies the exact Yarn+Square stage
projection and the existing disabled
Prism upstream
`joule.nexus.sanctum` →
`http://kvin.outer.sanctum:8084`,
WebSocket true. It enables **only Prism
in addition to Yarn and Square for that
single stage run**, without changing
`data/yxorp-routes.yml` or production
authorization. The corrected shared
YXORP role handles safe validated
config replacement, mounted-file drift
and exact stage-only service reconciliation.

**Read-only candidate acceptance:**
`ansible/yxorp-kvin-stage-prism-probe.yml`
performs three bounded anonymous GET /
requests with `Host: joule.nexus.sanctum`
from Kvin: direct :8084, Kvar NPM:80,
and local Kvin stage :80. It returns
sanitized HTTP statuses, incumbent/stage
status and MIME equality, redirect
presence/equality when applicable;
raw bodies/URLs/errors/cookies remain
suppressed. Real Prism WebSocket/session
and browser use are **separate gates**.
The three-way check is deliberately
nonfatal and must be interpreted from
its `Report only Prism HTTP status and
response equivalence metadata` task,
not only the play recap.

**Native operator command on Kvin,
after source CI passes:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-prism-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true
```
**Ask Nova ONLY for two one-line play recaps
and the sanitized `msg` dictionary of the
Prism report task**. If an execution fails,
ask only for that task's error.
Do not request complete Ansible logs,
to conserve the conversation context.
Each response should end with a concrete
next executable step, never only a
status summary.

**Other boundaries:** Kvar NPM and
wildcard DNS remain live production;
Kvin LAN HTTP80 firewalld still
Maintenance-owned; do not alter it,
cut over production, deploy Peanut
permanent standby, accept real
Nextcloud sessions/Calendar/WebDAV
or Prism WebSocket from this GET-only
test. Six routes remain untested
on Kvin *before* Prism run.

## CURRENT — November 10: 2/8 Kvin routes tested, 1 accepted; Square bind-mount lifecycle repaired in source

**Native accepted routes:** On the Kvin rootful HTTP80
YXORP **stage**, Yarn has passed its local application forwarding
and direct-versus-proxy body parity. Square/Nextcloud has
been attempted but not yet accepted. Other six of eight
declared routes have **not** been tested through Kvin
YXORP. Kvar Nginx Proxy Manager remains live production;
no DNS/firewall or production cutover.

**Square native failure now DIAGNOSED:** Nova's
`ansible/yxorp-kvin-stage-mounted-config-observe.yml`
returned `ok=8 changed=0 failed=0`:
host active config **equals** validated candidate and
both contain the `square.nexus.sanctum` vhost;
running container's `/etc/nginx/nginx.conf` was
read successfully, contains **Yarn but not Square**,
and **does not equal the host's published file**.
Local Square `curl` returned exit52/HTTP000,
as did the intentionally unmatched host. This
confirms the stale single-file bind mount: Ansible
atomically replaced the host file, but the running
Podman container remained mounted to the older
Yarn-only file and a mere `nginx -s reload` read
the stale version. Nextcloud backend and incumbent
Kvar NPM both returned HTTP302; do not blame
Nextcloud or network routing.

**Source repair implemented and fully qualified:** The
shared `ansible/roles/yxorp/tasks/main.yml`
now compares the host's current published file
against the running Podman container's
single-file bind mount **before** choosing
its systemd action. An already-stale mount
forces a restart of **only the authorized
YXORP service**, even if a prior Ansible
run wrote the desired host file and neither
source file is marked changed. Validated
config or Quadlet changes also trigger
a restart. With **no changes and no drift**,
state `started` remains idempotent; for an
inactive service it starts the unit. The
old `podman exec ... nginx -s reload`
path is removed. After reconciliation,
the role reads both mounted and host
config and asserts SHA256 equality with
raw content hidden, *before* local
health acceptance.

**[CI #42911815868 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/42911815868)**:
source-contract tests, actual role mount-drift
expression executed under real Ansible in
**six synthetic isolated cases** (including
*unchanged host config / stale existing mount*,
aligned config, config/Quadlet changes, and
stopped service), plus syntax, Nginx parser
and synthetic proxy behavior. No remote
host or service was touched by CI.
**Native Kvin repair and Square acceptance
still require the next operator run.**

**Next exact operator command on Kvin**:
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-square-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true
```
Nova already authorized the Kvin stage; this is
reconciliation of **only the test-stage** service
and the separately read-only Square application
comparison. Existing stage files are Kvin-owned,
Kvar and DNS remain intact, and all candidate
routes outside Yarn/Square stay disabled. Request
the two native recaps and three-way Square
report. Do **not** run production `ansible/yxorp.yml`
or bypass the Maintenance-owned Kvin firewall.
After successful status/redirect parity, real
Nextcloud login/Calendar and client-network
acceptance remain separate and unproven.

## CURRENT — November 10: Square stage installed but no HTTP response; inspect file bind mount

**Actual native Square stage:** Nova ran
`ansible/yxorp-kvin-stage.yml` with
`yxorp_kvin_stage_approved=true` and
`yxorp_stage_square_approved=true`: **`ok=31 changed=3
failed=0 skipped=1`**. Exact target and candidate checks
passed, only **Yarn and Square** were enabled in the
in-memory stage manifest, candidate rendered, config
published, existing Quadlet retained, and Nginx
**reloaded** (not container restarted). Local stage
health passed. Kvin rootful port80 stage still active;
Kvar NPM and wildcard DNS remain authoritative; no
firewall change or production cutover approval.

**Actual Square comparison:** Native
`ansible/yxorp-kvin-stage-square-probe.yml` returned
`ok=4 changed=0 failed=0`, **but the HTTP checks
were intentionally nonfatal**. At `Host:
square.nexus.sanctum` GET /: direct Kvin Nextcloud
backend `kvin.outer.sanctum:8085` returned HTTP302;
incumbent Kvar NPM port80 also HTTP302; **new Kvin
stage `127.0.0.1:80` returned no HTTP response
(`candidate_status=-1`)**, so candidate status
and redirect parity FAIL. `candidate_location_present=false`.
Do NOT call this a passing Square application test.

**Strong source-based hypothesis, still unconfirmed
natively:** The role's
`ansible.builtin.copy remote_src:true` atomically
replaced `/etc/sanctum-services/yxorp-kvin-stage/nginx.conf`.
The Quadlet mounts that **single host file** read-only
at `/etc/nginx/nginx.conf` inside the running Podman
container. A Linux file bind mount can remain pinned
to the previous inode after host-file replacement;
the role then sends **`nginx -s reload` instead of
restarting the container**. If the container sees
the OLD Yarn-only config, the new Square request
matches default `return 444` and yields empty
HTTP response (`curl` exit52/HTTP000). This
fits the symptom but **must be verified**;
do not presume it is the actual cause or alter
container state to test it.

**Source-qualified read-only check**:
`ansible/yxorp-kvin-stage-mounted-config-observe.yml`
compares host active and candidate configs against
the content of `/etc/nginx/nginx.conf` *inside
the already-running rootful Podman stage*,
plus two bounded curl requests with exact Square
and deliberately unmatched Host headers. It
reports **only config equality and Square/Yarn
presence booleans, stage-active flag, numeric
curl exit and status codes**. All raw configs,
responses and errors remain under `no_log`.
No host/service/router/firewall/route/DNS writes.
Unit source contract and real-Ansible synthetic
stale/aligned mount report tests passed
[Services CI #42909739503](https://github.com/wdcallahan/sanctum-services/actions/runs/42909739503).

**Next genuine operator command on Kvin**:
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-mounted-config-observe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true
```
Return the **single sanitized report and recap**.
Do not rerun the already accepted Yarn tests or
repeat the failed three-way Square comparison.
Keep the stage running; no experimental service
restart or changes to Kvar, wildcard DNS,
firewalld or production cutover. Once the live
comparison establishes whether mount divergence
occurred, correct the durable role/update lifecycle
as appropriate and retest Square, retaining the
separate stage/production authorization boundaries.

## CURRENT — November 10: local Yarn accepted; controlled Square-only Kvin stage ready

**Native accepted state:** The rootful Kvin
`sanctum-yxorp-kvin-stage.service` is active on
normal `0.0.0.0:80`. Nova's read-only
four-target diagnostic passed `ok=6 changed=0
failed=0`: local health 200, staged Yarn 200,
direct hostname Yarn 200, direct literal
`192.168.1.110` Yarn 200, DNS single IPv4
including the literal address, both
proxy-versus-direct body equality booleans
**true**. The earlier origin timeout did not
recur and has no diagnosed cause. **Do not
repeat accepted Yarn testing**. Kvar NPM and
wildcard DNS remain live; Maintenance firewall
admission for remote Kvin HTTP80 still absent.

**Next stage source QUALIFIED:** We selected
Square/Nextcloud as the next independently
needed route, not an all-routes promotion.
The `ansible/vars/yxorp-kvin-stage.yml`
flag `yxorp_stage_square_approved` defaults
false. With **explicit per-invocation opt-in**,
the same staged `ansible/yxorp-kvin-stage.yml`
checks the eight-entry baseline manifest
(Yarn-only enabled, Square disabled; Square
backend `kvin.outer.sanctum:8085`, WebSocket)
and uses only an **in-memory Ansible set_fact**
to enable Square alongside Yarn **in this
stage run**. It does not change checked-in
`data/yxorp-routes.yml`, production vars,
Kvar NPM, wildcard DNS or host firewall.
An ordinary stage re-run without the opt-in
returns to the source-manifest Yarn-only
state without removing the stage.

`ansible/yxorp-kvin-stage-square-probe.yml`
performs three independent bounded
anonymous root GETs from Kvin, with
`Host: square.nexus.sanctum`:
(1) Nextcloud backend `kvin:8085`;
(2) incumbent Kvar NPM `kvar:80`;
(3) Kvin stage `127.0.0.1:80`.
Raw responses, redirects, bodies, cookies and
errors are suppressed; only safe statuses
and comparison booleans reported. It
does not qualify login, Calendar, WebDAV,
sessions or WebSocket behavior.

**Source CI [Actions #42903575273](https://github.com/wdcallahan/sanctum-services/actions/runs/42903575273)
PASSED**: unit contracts, actual route-selection
tasks executed under synthetic real Ansible
with isolated fixture hosts, report filters,
Nginx parser and synthetic proxy tests, and
playbook syntax. The previous CI failure
was fixture cross-play `set_fact` persistence,
fixed before any native Square action.

**Next genuine operator action on Kvin**,
using Nova's preferred conditional chaining:
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-square-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true
```
Then supply both native play recaps and
the bounded Square report. **Do not**
run the old Kvin Yarn acceptance probe
again, switch wildcard DNS, deploy the
separate production YXORP unit, open
Kvin's firewall from Services, or
remove Kvar NPM. Preserve the running
Kvin stage for remaining application
qualification. Production cutover and
Peanut permanent standby remain closed.

## CURRENT — November 10: Kvin YXORP stage Yarn content ACCEPTED (native four-way)

**Latest native operator run:** Nova executed the read-only
`ansible/yxorp-kvin-yarn-transport-diagnose.yml` from Kvin
after the earlier direct-origin timeout. **`ok=6 changed=0
unreachable=0 failed=0 skipped=0`.** The separate
rootful `sanctum-yxorp-kvin-stage.service` is **active**.
Four independent GETs returned HTTP200:
(1) local `127.0.0.1:80/__yxorp_health` with
`yxorp-ready`; (2) Kvin stage Yarn virtual host at
`127.0.0.1:80/` with `Host: yarn.nexus.sanctum`;
(3) direct `http://yarn.inner.sanctum/` with same Host;
(4) direct literal `http://192.168.1.110/` with same Host.
**Stage response body equals direct hostname body AND direct
literal-IP body**. Kvin's resolver succeeded with **one
unique IPv4 address including `192.168.1.110`**.
Every result was read-only; no service/network mutation.

**Accept local Yarn application forwarding/content parity on
Kvin's stage.** The original sequential
`yxorp-kvin-stage-probe.yml` failed on direct-origin timeout
*before proxy observation*, but this independent later probe
returned HTTP200 for every path. Treat that original failure
as an intermittent/unexplained timeout, **not a diagnosed
Nginx, DNS, filtering or return-path defect**.
Do not request another rerun of the now accepted Yarn
path tests merely for reassurance.

**Still not accepted:** LAN client HTTP80 from Peanut/Mace,
real sessions, Prism WebSockets, Nextcloud user-facing
proxy behavior, other disabled route hosts, production
cutover/DNS, standby/failover and restore/update lifecycle.
Existing Kvar NPM remains production. Kvin stage is
currently installed and should be left running for next
tests; **do not remove or replace merely because the
local Yarn acceptance passed**. Maintenance #20 owns
future Kvin runtime+permanent firewalld HTTP80
admission for external clients. All seven legacy
route entries remain disabled.

**Next project-lead work:** Record the native result
([Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2))
and prepare appropriately isolated, source-managed
stage acceptance for another needed application,
beginning with Nextcloud/Square, while preserving
production route disable flags and Kvar authority.

## CURRENT — November 10: Kvin rootful YXORP STAGE INSTALLED; direct Yarn origin timed out

**Latest actual native operator report:** Nova ran the authorized
`ansible/yxorp-kvin-stage.yml` on Kvin: **`ok=22 changed=5
unreachable=0 failed=0 skipped=8`**. This installed the separately
named rootful Nginx Quadlet/systemd **stage on Kvin real HTTP:80**.
Kvar's NPM remains the **production** reverse proxy, and
wildcard DNS, host firewall, existing application services and
production cutover gate remain untouched. **Do not tell Nova
the replacement is still only on Peanut or that Kvin has no
Nginx**; the actual Kvin stage is now installed.

The immediately subsequent local
`ansible/yxorp-kvin-stage-probe.yml` run passed its exact Kvin
and closed-cutover assertions and **returned 200 for the local
`http://127.0.0.1:80/__yxorp_health` stage health check**.
However, the very next `ansible.builtin.uri` request to
**`http://yarn.inner.sanctum/`** with
`Host: yarn.nexus.sanctum` timed out, no HTTP response
(`status=-1`), after the configured 10-second timeout.
Local probe recap **`ok=2 changed=0 failed=1`**. The
playbook stopped **before testing the proxy's Yarn route**;
it is **not** evidence the proxy route itself failed, or that
the Nginx stage broke the origin. Do not repeat the failing
serial acceptance probe before diagnosing. Earlier accepted
Kvin origin and Peanut-proxy HTTP200/349-byte parity and
Kvin-to-192.168.1.110 selected route remain historical
evidence, not proof the origin is reachable *now*.

**New source-only read-only diagnostic:**
`ansible/yxorp-kvin-yarn-transport-diagnose.yml`:
(1) validates actual stage-scope approval, closed production
cutover and exact Kvin identity; (2) observes whether the
stage unit is active, bounded 5-second
`getent ahostsv4 yarn.inner.sanctum` match against
accepted origin `192.168.1.110`; (3) independently
GETs stage local health, stage Yarn with correct Host
header on **127.0.0.1:80**, direct Yarn **hostname**,
and direct Yarn **literal IP 192.168.1.110**, all
anonymous, private, bounded 7 seconds, redirects disabled
and **nonfatal**. Raw responses/errors are `no_log`;
output includes only numeric status, outcome categories,
DNS-to-prior-IP check and body equality **only if
both HTTP200**. No DNS/firewall/service/route mutation.
Unit tests, syntax and real-Ansible synthetic result-report
fixture **PASSED** in [Actions #42901044205](https://github.com/wdcallahan/sanctum-services/actions/runs/42901044205), including the corrected DNS-address regex.

**Next exact operator command on Kvin**, now that source CI
has passed; chain the update and run with Nova's preferred
shell conditional operator:
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-yarn-transport-diagnose.yml -e yxorp_kvin_stage_approved=true
```
Ask Nova for the **single sanitized report and play recap**.
Leave Kvin stage installed; do not restart it or change
host firewalls, router rules, Kvar NPM or DNS to
explain the origin timeout. Kvin LAN HTTP80 admission
still separately belongs to Maintenance #20 and
production/DNS cutover remains unapproved.
This is a fresh observed regression on the Kvin origin
path, not a reason to reopen deferred Kvar-origin
legacy Yarn path diagnostics blindly.

## CURRENT — November 10: Kvin staging AUTHORIZED, local test can proceed before firewall change

**Operator clarification:** Nova expected YXORP already on Kvin, but
the only accepted rootful Nginx deployment so far was the **temporary
Peanut trial**, which was removed. **Current live YXORP remains
Kvar Nginx Proxy Manager; Kvin currently has no YXORP service
installed.** Peanut was a separate realistic HTTP80 test host, not
proof of an installation on Kvin. Nova explicitly authorized
installing and locally testing the Kvin stage now, because there is
no existing Kvin listener to displace. Do **not** ask for that
permission again.

**Corrected engineering gate:** Kvin's missing
Maintenance-owned `eth0/public` HTTP/80 admission controls **LAN
reachability**, not binding a rootful listener or making same-host
requests via `127.0.0.1:80`. The earlier stage play incorrectly
required both runtime and permanent firewalld HTTP80 admission
**before installing**. Corrected `ansible/yxorp-kvin-stage.yml`
retains exact identity, independent stage approval, no-conflicting-
listener, existing Quadlet/config ownership and production-cutover
guards, but has **no firewall prerequisite and no firewall mutation**.
Its separate `ansible/yxorp-kvin-stage-probe.yml` performs **only
Kvin-local** YXORP health and exact Yarn origin-versus-proxy
status/MIME/body comparison using `http://127.0.0.1:80` and the
same Host header. The previous combined Peanut peer play was
split into `ansible/yxorp-kvin-stage-peer-probe.yml`, which
checks that Maintenance has admitted HTTP80 at runtime before
testing Kvin from Peanut. This separation was source/CI
qualified in [Actions #42898369323](https://github.com/wdcallahan/sanctum-services/actions/runs/42898369323).
**No live Kvin installation or HTTP probe has been executed yet.**

**Next exact operator action on Kvin:** The stage and local
probe now need *real* execution by Nova; there is no connected
shell or Ansible controller for the assistant to run itself.
From Kvin's ordinary Services checkout:
```bash
cd ~/src/sanctum-services
git pull
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-probe.yml -e yxorp_kvin_stage_approved=true
```
The `-e` passes Nova's already-given stage approval only
to these invocations. Keep `yxorp_production_cutover_approved=false`;
do not use `ansible/yxorp.yml`. The stage has a separately owned
Quadlet/service/config and binds `0.0.0.0:80` on Kvin; Kvar NPM and
wildcard DNS continue carrying production traffic. No immediate
stage cleanup: retain for later independently owned LAN/client
qualification, or use its exact scoped remove play if needed.

**Remaining external gate:** Maintenance #20's review/application
of Kvin runtime+permanent HTTP80 firewall policy is still required
for **Peanut-to-Kvin and other LAN client acceptance** (and eventual
production). A separate read-only peer play is ready but must
not be run before that policy is actually in place.
The production/DNS cutover and persistent Peanut standby are
unapproved and no other route is enabled.

## CURRENT — November 10: independent Kvin HTTP80 stage source complete; operator/owner gate next

**Current source result:** A separate, removable Kvin rootful host-network
Nginx `0.0.0.0:80` **stage** has been committed to `main`.
It is NOT Kvin production and does not share its Quadlet or config
paths. `ansible/yxorp-kvin-stage.yml` has explicit
`yxorp_kvin_stage_approved` (default false) and pre-mutation
checks for exact Kvin identity, free/owned port 80, absent
production YXORP, no unrelated stage files, `eth0/public`
firewalld **runtime and permanent** HTTP80 admission, and
closed `yxorp_production_cutover_approved`.
The role's own first assertion separately recognizes stage scope.
`ansible/yxorp-kvin-stage-remove.yml` has independent
`yxorp_kvin_stage_remove_approved` (default false), checks
exact owned Quadlet/only two config files, stops/removes stage
only and leaves host firewalld untouched.
`ansible/yxorp-kvin-stage-probe.yml` prepares same-Kvin-client
Yarn-origin-versus-new-proxy body equality and separate Peanut
client GET/health from Kvin; no application responses leaked.
Shared manifest still enables **only new Yarn**; all seven
legacy candidates remain disabled.

**Source qualification PASSED:** [GitHub Actions #42894828289](https://github.com/wdcallahan/sanctum-services/actions/runs/42894828289)
tested source contracts, Ansible syntax, real Nginx synthetic
config/client behavior and **executed the exact role's
stage/production/Peanut authorization expression in real Ansible
against synthetic local connections**, including rejection cases.
No live Kvin deployment/probe/removal is claimed.

**Genuine next owner/operator blockers:** Kvin port80 is currently
free, correct digest cached, but last native check showed
`eth0/public` HTTP80 absent in both firewalld stores.
Maintenance #20 owns source-managed policy review after
Thursday November 12 and **Nova must authorize its actual
application**. Nova must **separately authorize** the disposable
Kvin stage before its default-false approval flag is supplied.
Do NOT deploy with `ansible/yxorp.yml` or flip the production
cutover flag to simulate a stage. Once firewall is admitted and
stage approved, run only the stage play from Kvin; then its
new read-only client probe and scoped removal. Exact future
commands/rollback and conditions are in the [YXORP runbook](docs/runbooks/yxorp-reconstruction.md).
Continue preserving Kvar NPM/live wildcard DNS; actual production
and permanent Peanut standby still uncommissioned. Do not repeat
completed Peanut work or legacy Yarn route probes.

## CURRENT — November 10: Kvin/Kvar route comparison passed; legacy Kvar Yarn transport deferred

**Latest native operator result:** Nova ran
`ansible/yxorp-yarn-route-observe.yml` from Kvin. Both Kvin and Kvar
returned `ok=5 changed=0 unreachable=0 failed=0`, and both Yarn and
Arcane control route queries succeeded on each host.

For destination **Yarn `192.168.1.110`**, Kvin's kernel selected
`eth0`, source `192.168.0.192`, gateway `192.168.0.1`;
Kvar selected `end0`, source `192.168.0.7`, the **same**
gateway `192.168.0.1`. For control destination Peanut
`192.168.3.3`, each host again selected its own same interface,
source and shared gateway. Thus there is **no observed different
gateway, missing selected IPv4 route, or route-table divergence**
accounting for the earlier asymmetric HTTP result. Device names
are host-specific and not evidence of a problem.

Earlier accepted native HTTP evidence still distinguishes the hosts:
Kvin direct GET to Yarn returned HTTP200, whereas Kvar host and its
existing NPM container did not receive an HTTP response. A route
selection is **not proof of bidirectional packet delivery**;
source-specific policy, forwarding, target filtering or return path
remain possible, but no particular cause is established.

**Services decision:** Do **not** open another round of network probes
merely to repair the obsolete Kvar NPM `yarn.inner.sanctum` route.
This is **deferred diagnosis**, not a declaration that Kvar's route
works. The legacy name remains in the migration inventory until
consumers are reviewed and its retirement is separately accepted.
The independently accepted new Yarn proxy route on the temporary
rootful Peanut Nginx trial returned byte-identical HTTP200 content
from Kvin and was removed cleanly; there is no proven Kvar-origin
transport prerequisite for Kvin's new YXORP deployment. If an active
consumer or replacement acceptance demonstrates dependence on the
old path, hand source/return-path network diagnosis to the
infrastructure owner with this evidence. Keep the Mace→Arcane
Bunny Inner rule-20 defect (Maintenance #36) distinct.

**Next Services work:** prepare and review the independently testable
Kvin real-port-80 YXORP stage and route/consumer acceptance sequence,
keeping incumbent Kvar NPM and authoritative DNS untouched. **Source
finding:** `ansible/yxorp.yml` currently uses the `kvin_production`
role scope, whose guard requires
`yxorp_production_cutover_approved=true`; do **not** flip that
production authorization merely to stage a test. Prepare an independent
Kvin-stage entry point with explicit stage-only approval, exact port-80
ownership/firewall preflight, and scoped removal/recovery before
requesting any live execution. The already accepted Peanut trial and
its cleanup show the appropriate pattern, but must not be rerun.
The
**Maintenance-owned** Kvin `eth0/public` runtime+permanent HTTP/80
allowance is still absent per the last native readiness check; the
review and explicit approval gate is tracked in Maintenance #20
for Thursday Nov 12. No live Kvin publication, cutover or permanent
Peanut standby has been commissioned. Only new Yarn is enabled in
the candidate manifest; seven legacy routes remain disabled.
Kuma/Pi-hole redirect authority differences were fully explained
as explicit backend port vs absent port and need no speculative
rewrite. No extra operator command is required from this route test.

## CURRENT — November 10: Kvar host itself cannot reach legacy Yarn; route choice to observe

**Latest actual native result:** Nova ran
`ansible/yxorp-npm-path-diagnose.yml` through Kvin. Kvin
`ok=4 changed=0 failed=0`, Kvar `ok=5 changed=0 failed=0`.
Kuma `/` and Pi-hole `/admin/` redirect differences are now
fully classified as **backend port included directly, omitted
by incumbent Kvar NPM**; HTTP302, same backend hostname, path,
query, fragment and userinfo. Do not blindly reproduce a
legacy redirect rewrite or diagnose an application outage.

The old `yarn.inner.sanctum` route through Kvar NPM timed
out. The **Kvar host itself** also failed to receive any HTTP
response from `192.168.1.110:80`, and Kvar's running rootful
NPM container's own native Node HTTP request independently
**timed out**. Kvin did receive HTTP200 directly from
that same backend earlier. The common Kvar network path,
rather than solely an NPM proxy setting, needs explanation.
This is separate from Mace→Peanut/Bunny Inner's already
A/B/A-proven policy issue; do not assert they share a cause
without new evidence.

**Next exact native operator action:** From Kvin:
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-yarn-route-observe.yml
```
Read-only comparison uses two exact existing inventory peers:
Kvin and Kvar (latter via declared SSH10022). It reports the
selected kernel IPv4 device, source, next-hop and route type
for the Yarn backend `192.168.1.110` and control destination
`192.168.3.3` at each host. It does not contact backend HTTP,
add a route, manipulate a firewall or restart anything. A
kernel route choice is **not** a packet-delivery proof. The
synthetic real-Ansible JSON parse fixture and route-source
contract passed in CI. Do not rerun the already accepted
Kvar NPM, redirect or Peanut checks.

**Separate, unchanged service release gate:** Kvin's host TCP80
is unoccupied and its qualified rootful ARM64 Nginx image is
cached, but Kvin public-zone firewalld has NO runtime or
permanent HTTP/80 admission. Maintenance #20 owns a
reviewed addition after Thursday and Nova's approval.
Maintenance #36 owns the Bunny Inner asymmetric-forwarding
fix. Kvar NPM still serves existing DNS names, seven
legacy YXORP routes remain disabled, and Kvin production/
Peanut persistent standby are NOT commissioned. No new
host route, blanket firewall rule or TLS/CA initiative
is authorized by these observations.


## CURRENT — November 10: Kvar legacy Yarn timeout isolated; host versus NPM namespace next

Nova executed `ansible/yxorp-discrepancies-observe.yml` on Kvin:
`ok=7 changed=0 failed=0`. Kuma at `/` and Pi-hole at
`/admin/` both returned 302 directly and through incumbent
Kvar NPM; Location URLs were **absolute HTTP** with the same
**declared backend hostname** and matching paths/queries, yet
whole values differed. This may be a backend-port rewrite:
the remaining authority/fragment components were not previously
measured. Do **not** assert a broken redirect from this alone.

Kvar NPM's legacy `yarn.inner.sanctum` route from Kvin
**timed out**, curl exit **28** and HTTP **000** after a bounded
seven-second request. It was not a deliberate empty reply.
Kvin's earlier direct GET of Yarn's `192.168.1.110:80` returned
200; this says nothing yet about Kvar host or NPM-container
reachability. No change to the incumbent NPM is approved.

**Current source-complete next native step:**
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-npm-path-diagnose.yml
```
Two read-only plays: (1) on Kvin, compare only port/authority,
fragment and explicit-userinfo equality for Kuma/Pi-hole
redirects without disclosing sensitive Location values;
(2) on Kvar via its already qualified inventory SSH10022,
probe the Yarn HTTP origin from the Kvar host, then
from **inside the existing rootful nginx-proxman container**
using the container's Node HTTP runtime, without new software,
stopping or editing it. Reports only safe HTTP status and
timeout/connection categories; if container Node is unavailable
do **not** infer a network failure. The Node source is
syntax-checked; the actual Ansible URL split filters are
executed with synthetic examples in CI. The two plays change
no host, container, firewall, DNS, proxy, route or application
configuration.

**Completed** Kvin source backend status, whole seven-route
NPM parity and narrow redirect/no-response inspections must
not be repeated. The separate original Peanut Yarn trial
passed byte-identical content and was cleaned up.
**Remaining owner gates:** Kvin 80/tcp in both firewalld stores
awaits Maintenance #20 source/authorization on Thursday;
Bunny Inner rule20 asymmetric return path awaits Maintenance #36.
Kvar NPM / wildcard DNS untouched, Kvin production and
Peanut standby still not commissioned. No special host routes,
new private CA, or nonstandard local proxy stage are authorized.


## CURRENT — November 10: incumbent parity measured; narrow redirect/no-response diagnosis is next

Nova ran the native Kvin read-only `ansible/yxorp-incumbent-parity.yml`:
`kvin.outer.sanctum ok=8 changed=0 failed=0`. Same-client,
same-Host anonymous **backend vs Kvar NPM** responses:
Square `302/302` same Location; Joule, Search, Directory
`200/200`; Kuma `302/302` but **different Location**;
Pi-hole `404/404` on `/`; legacy
`yarn.inner.sanctum` backend `200`, NPM **status -1 / no
HTTP response**. Pi-hole `/admin/` separately `302/302`
with **different Location**. Those discrepancies are not
established application failures. No configuration changed.
[Native evidence](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6776037327).

A standalone narrow **read-only** follow-up,
`ansible/yxorp-discrepancies-observe.yml`, has been source
validated. It samples only Kuma `/` and Pi-hole `/admin/`,
both directly and through Kvar NPM; reports whether redirects
differ in scheme, absolute/relative form, frontend/backend/other
hostname *classification*, path or query **without leaking
Location values, cookies or bodies**. A single Kvin-origin
`curl` GET to NPM's legacy Yarn hostname reports a safe numeric
exit-code fingerprint (e.g. empty_reply/timeout) instead of
unredacted errors. CI includes a synthetic **executed Ansible
urlsplit** fixture, in addition to tests/syntax/Nginx behavior.
No live migration or firewall publication is authorized by it.

**Next actual operator command on Kvin:**
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-discrepancies-observe.yml
```
Do not rerun the full seven-route comparison, the completed
Peanut trial or its cleanup. Capture the new sanitized outcomes
before deciding whether any of these differences needs a
reverse-proxy rule or is just expected legacy rewriting.

**Separate gates unchanged:** Kvin HTTP/80 is unadmitted in both
firewalld stores (Maintenance #20 owner handoff for Thursday);
Kvar NPM remains live and wildcard DNS still unchanged;
all replacement routes except the new Yarn trial route remain
disabled; Kvin production deployment/Peanut persistent standby
not commissioned. Bunny Inner asymmetric-path issue belongs to
Maintenance #36. No private HTTPS/CA initiative or Kvin high-port
workaround is a requirement.


## CURRENT — November 10: all eight YXORP backends answer; incumbent NPM parity next

Nova ran the new Kvin anonymous direct-backend inventory after the
clean Kvin TCP80 readiness report. `ansible/yxorp-upstreams-observe.yml`
returned `kvin.outer.sanctum ok=5 changed=0 failed=0` with HTTP
responses for **all eight** declared backends:

`yarn.nexus.sanctum=200`,
`square.nexus.sanctum=302`,
`joule.nexus.sanctum=200`,
`search.nexus.sanctum=200`,
`dir.nexus.sanctum=200`,
`kuma.nexus.sanctum=302`,
`pihole.nexus.sanctum=404`,
`yarn.inner.sanctum=200`.

**No backend was unreachable.** A 302 may be normal; Pi-hole returning
404 at `/` does not mean its web admin application is down.
This is not user-session/WebSocket/actual-proxy or restore acceptance.

**Next meaningful, source-prepared native operator comparison:**
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-incumbent-parity.yml
```
The tested, read-only play queries seven **existing** named proxy
hosts through current Kvar NPM and directly against their declared
backends from the same Kvin observer. It uses the same Host header,
anonymous GET /, no redirects, no raw response/log values and a
six-second bound per request. The newly proposed
`yarn.nexus.sanctum` is excluded (not an incumbent host).
It also checks `/admin/` on Pi-hole's `kvar:82` backend
versus the current Kvar NPM Pi-hole route, avoiding a false
diagnosis from root 404. Output reports statuses and *boolean*
redirect equality, not actual redirect URLs, bodies or cookies.
No changes to Kvar, firewall, DNS, Kvin or route flags.

**Outstanding cross-owner gate:** Maintenance controls Kvin's
`eth0/public` runtime+permanent HTTP/80 firewall rule. Neither
store currently admits port80, and Maintenance #20 has the future
source/approval handoff. Kvin has no listener, no YXORP Quadlet and
does have the rootful ARM64 Nginx digest. Existing Peanut-only
Yarn trial passed byte-identical 349-byte HTTP200 and was
successfully removed. Do not repeat those steps. Full Kvin
production/Peanut standby, migration of remaining app services and
wildcard DNS cutover are separately unapproved.


## CURRENT — November 10: Kvin rootful port80 ready except host firewall; direct upstream discovery next

The corrected `ansible/yxorp-kvin-readiness.yml` passed natively on Kvin:
`ok=13 changed=0 failed=0`. It found `aarch64`; no host TCP80
listener, production YXORP Quadlet or systemd unit; and the exact
qualified rootful official Nginx image already in the cache. Kvin
`firewalld` is running with `eth0` in `public`, but both runtime
and permanent `http` service and `80/tcp` allowances are absent.
Kvar NPM and wildcard DNS remain untouched. The production cutover
gate remains false. [Native evidence in Services #2](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6775524905).

**Maintenance ownership:** Kvin's ordinary published-service firewall
policy already provides accepted 8084/5432/8085 via a shared owner;
Services filed a **no-immediate-change** HTTP/80 request for Thursday
in [Maintenance #20](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-6775538017).
Do not write another firewalld policy in Services or install arbitrary
source/32 restrictions. Actual approval/implementation is not recorded.

**Prepared next read-only operator action from Kvin:**
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-upstreams-observe.yml
```
The source-driven, tested play probes each of the eight declared
direct backend URLs with its corresponding Host header. No login,
no content output, redirects not followed, six-second limit per route,
no firewall/DNS/Nginx/Quadlet changes. It returns status per backend,
including disabled routes, to separate real application availability
from missing proxy publication. [CI check](https://github.com/wdcallahan/sanctum-services/actions/runs/42874534629)
passed all contracts, syntax, render, Nginx and synthetic HTTP checks.
Native execution has **not** yet occurred; operator output is needed
before further per-application route planning.

**Completed and not to repeat:** Peanut rootful HTTP/80 trial passed
same-client Yarn page byte-for-byte from Kvin (HTTP200,
`text/html`, 349 bytes). The scoped Peanut cleanup passed
`ok=26 changed=5 failed=0`. No Nginx production service or
standby has been deployed to Kvin/Peanut by this trial. The
separately A/B/A-proven Mace→Arcane asymmetric-route firewall fault
belongs to Maintenance #36. No client host-route workaround.


## CURRENT — November 10 late morning: Peanut trial removed; Kvin preflight corrected

Nova ran the previously authorized Peanut trial removal. Native recap:
`peanut.arcane.sanctum ok=26 changed=5 failed=0`. The Yarn
origin/proxy anonymous response comparison had already passed exact
HTTP 200, `text/html`, and **349-byte body equality** from Kvin.
Do **not** repeat trial cleanup or reopen Peanut solely for this step.

The following first run of standalone read-only
`ansible/yxorp-kvin-readiness.yml` stopped at `systemctl is-active`
because `yxorp_service_name` was undefined; the task never executed
on Kvin. It also would have lacked `yxorp_quadlet_file`. Those
names are in the YXORP role defaults, but the independent preflight
doesn't execute the role. The play now explicitly loads
`vars_files: [roles/yxorp/defaults/main.yml]`, with a regression test
verifying all YXORP references are declared and no vars-precedence
collision with production group vars. Source + syntax + synthetic
Nginx CI [#42870253729](https://github.com/wdcallahan/sanctum-services/actions/runs/42870253729)
**passed** after the correction.

**Exact next operator boundary:** on Kvin, update Services checkout and
run **only** `ansible/yxorp-kvin-readiness.yml`. It is read-only and
will observe production Kvin TCP80 listeners, rootful qualified image
cache, Quadlet presence, and both runtime/permanent HTTP firewall
admission. Report results before proposing any Kvar/DNS production
cutover. See [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6775045034).

## CURRENT — November 10, 2026: YXORP Peanut Yarn route content-accepted

**This is the active restart point. All dated \"pending\" instructions below
are historical unless restated here. Do not repeat accepted tests or revisit
the rejected Kvin loopback staging proposal.**

Nova ran the native authorized four-hour Peanut trial reopening, followed
by the independent Kvin same-Host origin/proxy comparison. Result:
`peanut.arcane.sanctum ok=43 changed=1 failed=0` (only the runtime
TCP/80 exception was renewed; existing rootful Nginx parser, Quadlet,
config and local health were unchanged/healthy), then
`kvin.outer.sanctum ok=4 changed=0 failed=0`.
Both the direct `http://yarn.inner.sanctum/` and the route through
`http://peanut.arcane.sanctum/` using
`Host: yarn.nexus.sanctum` returned HTTP **200**, MIME `text/html`,
**349 bytes each**, and **`body_equal=true`**. This is real anonymous
content equality, not just an HTTP 200; browser/login/WebSocket, other
routes, Kvin production and standby promotion remain unqualified.
[Accepted issue receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6774641790).

**Next distinct live steps (operator-required):** from Kvin's current
Services checkout, `git pull --ff-only`, then
`ansible/yxorp-peanut-remove.yml` to stop/remove the **Peanut test**
Quadlet/config and its marked temporary HTTP/80 opening now that
Yarn-only trial acceptance is complete. Follow with read-only
`ansible/yxorp-kvin-readiness.yml` to inspect actual production
Kvin port-80 occupancy, rootful known-good image digest and active/
permanent firewall admission. Both are source-controlled in Services;
the former was expressly approved for trial cleanup, the latter
does not modify services. Never remove Kvar NPM, change DNS or deploy
Kvin YXORP without a separate cutover decision.

**Independent infrastructure issue:** Mace cannot normally SSH to
Arcane/Peanut because Bunny Inner's IPv4 `forward` rule 20
(`state invalid action drop`) breaks the valid asymmetric return path.
Nova's five-minute `commit-confirm` A/B/A test identified the rule
and safely restored it. [Maintenance #36](https://github.com/wdcallahan/sanctum-maintenance/issues/36)
owns the source fix when Maintenance resumes Thursday; the YXORP
route itself was independently accepted from Kvin. No client host
route, blanket router/firewall redesign or unnecessary YXORP rebuild.

**Service design remains** plain Nginx rootful host-network HTTP/80,
Kvin primary and Peanut intended future peer/standby; Git-declared
routes, with **Yarn only** enabled for trial. Production gate false;
no permanent standby or automatic updates commissioned. Record new
native evidence in Services issue #2; do not infer deployment from CI.


## Most recent blocker — Mace→Peanut transport is pre-existing Maintenance #36

**November 9 native client evidence** supersedes any following note
implying that HTTP 200 from Kvin completes whole-LAN YXORP acceptance.
Kvin→Peanut rootful host-network Nginx health and Yarn forwarding
**passed HTTP 200**. But Mace (new `192.168.1.103`) can establish
TCP with Peanut (`192.168.3.3:80`), send `GET /__yxorp_health`,
and then times out after eight seconds with **zero HTTP response
bytes**. An independent proxied Yarn request does the same. Mace's
`ssh peanut` also hung until interrupted after ~25 seconds; no
verbose SSH connection stage was recorded.

This matches the already-open **[Maintenance issue #36](https://github.com/wdcallahan/sanctum-maintenance/issues/36#issuecomment-6756207921)**,
originally opened November 8 for failed Mace→Peanut SSH while Kvin
can use Peanut. Evidence was posted there, not filed as a duplicate.
On November 6, Mace SSH to Peanut had worked from its previous
`192.168.0.103` source address; now Mace uses `192.168.1.103`.
The Inner/Outer renumber and altered return path, firewall, routing
or NAT are credible suspects **but no culprit is proven**.

**Boundary:** Services owns working YXORP configuration and cross-host
Kvin acceptance, not general routing/firewall changes between Inner and
Arcane. Maintenance/Bunny should diagnose the common transport path
under their already tracked #36, using bounded route observations and
a correlated packet capture if needed. Do not rewrite YXORP, open
additional firewall holes or rerun already accepted Kvin checks without
new evidence. Full LAN/browser and hot-standby/failover acceptance remain
pending. The Peanut port80 ad hoc runtime firewall allowance is still
subject to its four-hour expiry; remove the test with
`ansible/yxorp-peanut-remove.yml` when testing concludes.


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
