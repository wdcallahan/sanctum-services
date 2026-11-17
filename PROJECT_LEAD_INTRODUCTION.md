# Sanctum Services — Project Lead Handoff

## November 17 — LinkStack updater native PASSED; next is read-only Nextcloud reality check

**LATEST USER NATIVE RESULT — LINKSTACK MOVING IMAGE COMPLETED:**
Nova ran `ansible/linkstack-kvin-auto-update.yml` on
`wdc2@kvin`: **`ok=21 changed=3 unreachable=0 failed=0
skipped=0`**, actual `running_image=docker.io/linkstackorg/linkstack:latest`,
Quadlet registry auto-update declared, existing
`sanctum-linkstack-qualified-20261112t105926` rootless
named SQLite volume and `127.0.0.1:18081` port preserved.
LinkStack restarted successfully, local HTTP200,
no YXORP/DNS/firewall or other services changed. The
Nov17 live current SQLite archive was already **natively
retained and independently SHA/SQLite checked on Peanut**:
`linkstack-kvin-20261117t105833.tar`, 93,849,600 bytes,
SHA `301ee0eeee9de17a96ec1dc0292dbeaa059bceb3b7d45eed7426523727efbe05`.
No first future scheduled registry refresh observed, and
admin login was not rechecked in *this* post-update play.
**Do not rerun LinkStack auto-update, pre-update backup,
one-time stage, or prior broad browser tests.**
[Services #6 native acceptance](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6955900732).

**NEXT ACTIVE FRONT — NEXTCLOUD #5:** current official app
image source is frozen at Oct18 `34.0.5-apache` digest,
with no `AutoUpdate=registry`; actual running version and
image-reference drift remain unknown. Existing Nov16
Nextcloud consistent Kvin multi-artifact snapshot,
independent Peanut custody and isolated file/private
extraction are accepted. **Do NOT rerun original backup
or jump to major 35; independent full DB+app restore is
not yet accepted.** New strict read-only
`ansible/nextcloud-update-readiness.yml` observes
`podman exec --user www-data ... php occ status --output=json`
on actual Kvin existing rootless `sanctum-nextcloud`,
current image identity vs Git digest, installed Quadlet
auto-update declaration, actual version/maintenance/
needsDbUpgrade, without any application, DB, route,
firewall, secret, service, config or storage change.
**FULL SOURCE+SYNTAX CI [44139307721 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/44139307721)**.
No native observation yet. Single next operator action
on `wdc2@kvin`:
```bash
cd ~/src/sanctum-services &&
git pull --ff-only &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/nextcloud-update-readiness.yml \
  -e nextcloud_update_readiness_approved=true
```
Ask for task **`Report actual Nextcloud update baseline
without starting an upgrade`** plus recap or failed task
and error. No sudo or outage. After receipt design a
safe within-major patch/automatic update mechanism and
recurring backup/offsite transfer that respects app+DB
transaction/restore dependencies and Calendar 6.6.2.
[Nextcloud #5 current source comment](https://github.com/wdcallahan/sanctum-services/issues/5#issuecomment-6955995366).


## November 17 — Kvin LinkStack offhost retention NATIVE PASSED; auto-update rollout NEXT

Nova executed `ansible/linkstack-kvin-retain-on-peanut.yml`
Kvin→Peanut. **NATIVE `peanut.arcane.sanctum ok=15 changed=2
unreachable=0 failed=0 skipped=0`.** Actual independent
SHA256 + SQLite/config verification on Peanut passed for
`linkstack-kvin-20261117t105833.tar`, **93849600 bytes**,
SHA256 `301ee0eeee9de17a96ec1dc0292dbeaa059bceb3b7d45eed7426523727efbe05`.
Original LinkStack untouched, no proxy/DNS/firewall change.
No separate full application restore from THIS new archive has
been run; do not overclaim it.

**Next real Services action/source CI GREEN:** official LinkStack
Docker uses moving `docker.io/linkstackorg/linkstack:latest`, and
Podman registry updates need a fully qualified movable tag.
New current managed Quadlet at
`ansible/files/sanctum-linkstack-kvin-managed.container` has
`AutoUpdate=registry` with identical old rootless
`sanctum-linkstack-kvin-candidate` container/service, existing
volume `sanctum-linkstack-qualified-20261112t105926` and
loopback `127.0.0.1:18081`. Source-only
`ansible/linkstack-kvin-auto-update.yml` strictly checks
old live image/container/Quadlet/volume/port before touching,
pulls moving image, validates Linux ARM64, updates only
LinkStack user Quadlet, restarts only LinkStack, confirms
HTTP200, mount, runtime image, port, with best-effort original
source/service rollback on health failure. **The old staging
file remains in source as historical fallback only.** New
tests caught two mistakenly nested `vars` in `assert`
actions before any native execution; corrected. **FULL
SOURCE+SYNTAX CI PASSED
[44137175030](https://github.com/wdcallahan/sanctum-services/actions/runs/44137175030)**.
**Native production LinkStack update has NOT run**.

**Next operator invocation on `wdc2@kvin`:**
```bash
cd ~/src/sanctum-services &&
git pull --ff-only &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/linkstack-kvin-auto-update.yml \
  -e sanctum_linkstack_kvin_auto_update_approved=true
```
**WARNING PRIOR TO PASTE:** actual production directory
restart, pull latest ARM64 image and potential in-place
application SQLite migration; short downtime possible.
Fallback Quadlet doesn't undo a migrated SQLite database.
The verified off-Kvin snapshot is the pre-upgrade recovery
point. No sudo/firewall/DNS/YXORP/other-service changes.
Request `Report actual Kvin LinkStack moving registry update
deployment` + recap or actual failed task. After native
acceptance continue already defined Nextcloud recurring
backup/Calendar-safe update and meaningful isolated
DB-dependent application restore, not new invented discovery.

[Services #6 native record and source](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6955712124).


## November 17 — REAL current Kvin LinkStack backup ACCEPTED; next Peanut copy ready

**NATIVE just completed on Kvin:** Nova ran
`ansible/linkstack-kvin-consistent-backup.yml`, actual
`ok=25 changed=5 unreachable=0 failed=0 skipped=0`.
Captured current live rootless Kvin LinkStack SQLite consistently,
`sqlite_integrity=ok`, restarted original service, HTTP200 and
DNS/YXORP unmodified. Owner-private archive:
`/home/wdc2/.local/share/sanctum-services/backups/linkstack/linkstack-kvin-20261117t105833.tar`,
size **93849600** bytes and SHA256
`301ee0eeee9de17a96ec1dc0292dbeaa059bceb3b7d45eed7426523727efbe05`.
**NOT YET copied off-host** at this handoff. No need to repeat the
LinkStack source backup.

**NEXT single operator action is READY**: new
`ansible/linkstack-kvin-retain-on-peanut.yml` (with
`tests/test_linkstack_kvin_retention_peanut.py` and full source+syntax
**[CI 44132268595 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/44132268595)**)
copies exactly that file from Kvin to independent Peanut and
independently verifies full SHA256/bytes plus tar/SQLite/config
integrity using existing safe archive validator. NO service restart,
SQLite/volume write, DNS, proxy, firewall or image update.
Run as `wdc2@kvin`:
```bash
cd ~/src/sanctum-services &&
git pull --ff-only &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/linkstack-kvin-retain-on-peanut.yml \
  -e sanctum_linkstack_kvin_retain_on_peanut_approved=true
```
Request exact `Report real LinkStack off-Kvin retention on Peanut`
and play recap or failure, not prior backup output.
The source-only passing CI is NOT proof of Peanut runtime transfer.
After native acceptance, continue LinkStack from frozen image
digest/`Pull=never` to moving upstream `linkstackorg/linkstack:latest`
and rootless `AutoUpdate=registry`, with current data preserved;
do not reopen already accepted Kuma or broad browser tests.
[Services #6 status](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6955025311).


## November 17 — next real Services operator action now source-qualified

**Kuma: native COMPLETE this round.** Latest user actual
`ansible/kuma-post-update-verify.yml` `ok=12 changed=0 failed=0`,
old vaulted admin login passed, original Wicket monitor ID 1 remains
configured and `Up` at 40-second heartbeat age, running current
`docker.io/louislam/uptime-kuma:2`, registry label in installed
Quadlet, user Podman update timer previously accepted. Stop reopening
completed Kuma source/monitor/backup tasks.

**LINKSTACK next:** current production Kvin
`sanctum-linkstack-kvin-candidate.service` serves existing
accepted `dir.nexus.sanctum`, but image still frozen at old
digest, `Pull=never`; upstream officially supplies moving
`linkstackorg/linkstack:latest`. Before changing rolling
image policy, source `ansible/linkstack-kvin-consistent-backup.yml`
has been built and **[FULL CI 44128204144 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/44128204144)**.
It requires explicit approval, briefly stops ONLY current Kvin
LinkStack SQLite writer, exports current named volume
`sanctum-linkstack-qualified-20261112t105926`, ALWAYS starts
original unit again, verifies original HTTP, archive SQLite
integrity/manifest and private sha. New unique Kvin-only recovery
artifact is created; no proxy/DNS/firewall changes or other
service changes. **Real native execution NOT YET DONE.**
Operator command on `wdc2@kvin`:
```bash
cd ~/src/sanctum-services &&
git pull --ff-only &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/linkstack-kvin-consistent-backup.yml \
  -e sanctum_linkstack_kvin_backup_approved=true
```
**WARN FIRST** that production LinkStack directory will briefly
be unavailable during SQLite export. Ask for
`Report actual consistent current Kvin LinkStack backup`
and `PLAY RECAP` or failure. Archive on Kvin is NOT yet
off-host retained. Next work after real result is an independent
Peanut copy and verified hash; then adopt supported rolling
LinkStack tag + rootless `AutoUpdate=registry`, preserve existing
data and accepted route. [Services #6 source handoff](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6954460445).

**Expiring Work quota decision:** two Senzu Beans expire
Dec 1 and Dec 12, weekly allowance resets ~Nov19/20.
Nova vacation starts Thu Nov19 evening through Nov30.
Advice: save bean NOW unless planning significant Work
before imminent automatic reset; during vacation spend earliest
expiring one **after** consuming a free allowance and no later
than Nov30, lest it expire Dec1. Previous bean redemption
restored both weekly and shorter meters to 100%.
Avoid wasting a bean immediately before reset.

**Short-links future user spec:** YOURLS did NOT rename;
Piwik became Matomo in January 2018. All aliases must be
cryptographically random **full case-sensitive base62**
including `0/O`, `1/I/l`, never sequential. YOURLS
`YOURLS_URL_CONVERT=62` enables charset but not CSPRNG;
its keyword column uses case-sensitive `utf8mb4_bin`.
Separate `buny.us` shortener (original domain intent),
`share.buny.us` home-only isolated one-download endpoint
with URL/QR and zero recipient extra actions, and proposed
`vpn.buny.us`. The public alias is the bearer secret:
suggest ~8-char ordinary and ~12-char one-time file codes,
not approved fixed parameters. Parent data retained ~24h
for new-link issue; one-time token dies after practical
completion/expiry. All public ingress remains UNAPPROVED.
[Full speculative design](docs/reviews/2026-11-17-picoshare-public-sharing-options.md).


## November 17 — Kuma post-image-upgrade native accepted; future sharing candidate

**KUMA POST-UPDATE NOW NATIVE COMPLETE:** Nova ran the corrected
`ansible/kuma-post-update-verify.yml` with its existing Vault,
`kvin.outer.sanctum ok=12 changed=0 failed=0 skipped=0`.
`original_admin_login_verified=true`,
`existing_wicket_monitor_config_verified=true`,
`monitor_id=1`, `latest_wicket_status=Up`,
`heartbeat_age_seconds=40`, `currently_up_and_recent=true`,
running image `docker.io/louislam/uptime-kuma:2`,
`installed_auto_update=registry`, `service_active=active`.
No database/service/monitor changes from the verification. This closes
Kuma's immediate moving-image migration and saved-state compatibility
acceptance. **Do NOT ask for another Kuma setup, monitor reconcile,
backup/transfer, or WebSocket screenshot.** Offhost November11
archive is accepted but predates the v2 moving-tag update; no future
timer-driven update occurrence has been measured.
[Services #6 native update acceptance](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6953841654).

**PICOS HARE / FDROP EXPLORATION (UNCOMMITTED):** User wants
on-premises-only small-sharing service, with high public ingress
isolation from Sanctum: owner selects/uploads a file on phone,
receives easy **human-typeable** short HTTPS URL and QR; external
recipient opens in ordinary browser with zero extra password/app/click;
URL invalid after one practically completed transfer or expiration,
but blob retained privately ~one day for new-link reissue without
reupload. **No offsite VPS**, no recipient decryption steps. Found
existing [fdrop](https://github.com/polimo-dev/fdrop) Aug2026 Go
project explicitly built for typed one-download direct URLs, time/count
limits, ARM64 and manageable link length. It needs source hardening:
default 5-character token is only ~25 bits; use longer 14–16
human-readable characters with rate limiting; current
`GET /{id}` checks before `io.Copy` and calls `Consume` after,
so **two concurrent GETs can both receive entire file** before
post-stream SQLite count. Need atomic in-flight token ownership.
Current immediate blob deletion after link consumption is
incompatible with wanted 24-hour owner-private blob retention;
change token vs payload lifecycle. QR UI may need adding.
TCP/HTTP server can generally detect stream completion but not
**prove recipient's browser saved to disk**; proxied buffering can
obscure detection. A focused public-facing security review and DMZ
ownership are needed **only if** user chooses to implement; the
idea remains uncommitted. Current design note is
[docs/reviews/2026-11-17-picoshare-public-sharing-options.md](docs/reviews/2026-11-17-picoshare-public-sharing-options.md).

**Work allowance:** weekly Work quota was exhausted November17
and expected to replenish ~2.5 days later (~November19/20);
Nova has expiring 'Senzu Beans' December 1 and 12, and time off
work from Thursday November19 evening through November30.
This is scheduling context, NOT a technical blocker; do not
manufacture project tasks just to use purchased credits. Current
active Services next independent work is LinkStack image lifecycle
and Nextcloud recurring backup/update/owner DB recovery, none of
which should be labeled "done" yet.


## November 17 — immediate Kuma Ansible source failure RETRIED AFTER FIX

Nova ran `ansible/kuma-post-update-verify.yml` on Kvin as `wdc2`,
with existing Vault. **NATIVE** `ok=4 changed=0 failed=1`:
the fourth task checked the Kuma Quadlet and then the `assert`
action rejected the nested `vars` argument. **THIS IS OUR
Ansible SOURCE CODING ERROR**, not an actual regression in Kuma.
There was **no state change** and neither the admin login nor monitor
read-only stage ran, so their current post-upgrade status remains
unverified. Do not suggest reinstallation or new backup.

Services moved `vars` to the **task level** on
`Require installed v2 registry update declaration and preserved volume`
and added `tests/test_kuma_post_update_verify.py` acceptance that
iterates every `assert` task and rejects invalid module argument keys;
regular Ansible syntax-check alone does not catch them. **Full CI
[44122245307 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/44122245307)**.
**NEXT EXACT OPERATOR ACTION:** from `wdc2@kvin`:
```bash
cd ~/src/sanctum-services &&
git pull --ff-only &&
ANSIBLE_VAULT_PASSWORD_FILE="$HOME/.config/sanctum-services/secrets/vault.key" \
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/kuma-post-update-verify.yml \
  -e kuma_post_update_verify_approved=true
```
This is an **identical read-only retry after correction**, with no
sudo, downtime, DB writes or monitor mutations. Return the actual
`Report bounded post-update original administrator and monitor
acceptance` and `PLAY RECAP`, or the exact failed task.
Do not conflate syntax-check source CI with native success.

**PicoShare intent fully corrected:** Nova rejected offsite
VPS/object storage, recipient-side password, app, registration, manual
decryption, separate secret or any extra download steps. The one
wanted behavior is **from own home infrastructure**, upload file from
phone, hand out easy HTTPS URL or QR, recipient downloads using
normal browser with zero extra interaction, then link invalidates
after **one download**. Wants exceptional **server-side/DMZ
network isolation** for this public service, not militarized
internal LAN access. Inspecting upstream
[download handler](https://github.com/mtlynch/picoshare/blob/master/handlers/download.go)
showed it logs successful fetch **after**
`http.ServeContent`, not atomic one-shot token invalidation.
**Do not promise PicoShare already supports one-time links**;
future feasible work is one-shot gateway/patch or alternative,
QR and server-only controls and exception handling for
prefetch/HEAD/range/resume. This is an **uncommitted future
candidate**, not permission to deploy or add a blocking issue.
See [corrected concept review](docs/reviews/2026-11-17-picoshare-public-sharing-options.md).


## November 17 — native Kuma update success, actual user-facing next step

Nova executed `ansible/kuma.yml -e kuma_stage_approved=true` on
`wdc2@kvin` after Services adopted the upstream supported moving major
version image `docker.io/louislam/uptime-kuma:2` with user Quadlet
`AutoUpdate=registry` (**not `:latest`, still v1**). **Native
`ok=10 changed=3 failed=0 skipped=1`**, retained existing
`sanctum-kuma-data` SQLite volume, HTTP302 at loopback
`127.0.0.1:13001`. This confirms applied source+HTTP, NOT
post-upgrade authenticated login or saved Wicket heartbeat. Earlier user
`podman-auto-update.timer` was active/enabled.

**CRITICAL REPORT CORRECTION:** Old source role's final report had
`administrator_and_monitor_state_accepted=false` and
`backup_restore_and_recovery_accepted=false`, and obsolete
`next_gate: qualify ... before upstream cutover`. These were
HARDCODED placeholders from original November11 staging, not measured
post-upgrade failures. Admin login, Wicket monitor Up, WebSocket and
backup+independent restore/Peanut retention were separately previously
accepted; don't reinterpret these as never accepted. Source role and
contract test now replaced with truthful "this run checked HTTP only".

**NEW NEXT OPERATOR ACTION prepared by Services:** guarded **read-only**
`ansible/kuma-post-update-verify.yml`: on exact Kvin,
uses existing vaulted administrator credentials via stdin to
run existing Kuma Socket.IO `verify` and monitor `observe`.
No account, monitor, SQLite, user service, volume or proxy writes;
prints current monitor condition without demanding it be Up
at every instant. Source admin bootstrap, monitor owner and
diagnosis entrypoints updated to supported `:2` image identity,
removing old accidental digest-enforcement source traps. Tests and
CI run [44121324665](https://github.com/wdcallahan/sanctum-services/actions/runs/44121324665)
pending at handoff update. **Only after CI green**, run on
`wdc2@kvin`:
`cd ~/src/sanctum-services && git pull --ff-only && ANSIBLE_VAULT_PASSWORD_FILE="$HOME/.config/sanctum-services/secrets/vault.key" ansible-playbook -i ansible/inventory/hosts.yml ansible/kuma-post-update-verify.yml -e kuma_post_update_verify_approved=true`.
The Vault password file and encrypted Kuma admin vars file already exist
on Kvin per earlier accepted owner actions. This is not a live service
change and requires no sudo or login UI. Request exact final report and
recap or failed task/error, no secrets.

**Do not add invented tasks.** After Kuma post-update acceptance, return
to existing LinkStack and Nextcloud update lifecycle, and real complete
Nextcloud/DB recovery when Maintenance provides supported isolated
owner interface; future services only when Nova chooses. Palo Alto-level
security for internal home tasks was explicitly rejected; Nova
**does** want high isolation only for a possible publicly reachable
PicoShare (separate uncommitted feasibility review).


## November 17 — Kuma native off-host copy and public PicoShare discussion

**User's exact actual Kvin→Peanut Kuma result is ACCEPTED:**
`ansible/kuma-retain-on-peanut.yml` on Peanut
`ok=13 changed=2 unreachable=0 failed=0 skipped=0`.
`copy_verified_on_peanut=true`; SHA256
`97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648`
for `sanctum-kuma-20261111t144137.tar`; live SQLite and
Kuma user service untouched. `encrypted_admin_vault_custody_not_verified=true`,
`complete_disaster_recovery_accepted=false`. Don't repeat transfer
or existing November 11 restored-login/monitor tests.

**Now Kuma SOURCE updated and CI PASSED:**
`ansible/group_vars/kuma.yml` now selects
`docker.io/louislam/uptime-kuma:2` (not SHA, not `:latest` for v1).
Rootless `ansible/roles/kuma/templates/kuma.container.j2` has
`AutoUpdate=registry`; role preflight and fixed-image backup trial
updated, old SHA enforcement removed from currently executable desired state
but historical qualification fixture still represents prior observation.
**[Full CI 44116110856 success](https://github.com/wdcallahan/sanctum-services/actions/runs/44116110856)**.
Kvin installed Kuma container has NOT been updated yet.
**NEXT OPERATOR STEP on `wdc2@kvin`:**
`cd ~/src/sanctum-services && git pull --ff-only && ansible-playbook -i ansible/inventory/hosts.yml ansible/kuma.yml -e kuma_stage_approved=true`.
Conspicuously warn that this is a **production Kuma restart, pulls
latest major-v2 image and may migrate the live SQLite schema**, causing
temporary monitoring outage. This uses original `sanctum-kuma-data`
volume and config, touches no DB outside Kuma/DNS/firewall.
Return actual final role report and play recap/failed task. The existing
Kvin user auto-update timer was already active. Continue after native
result, no artificial extra task.

**NEW USER CONCEPT (not yet approved for deployment):**
Nova has **real static ISP IP** and wants to send a one-off PUBLIC
file link to selected external recipients. Unusually for this project,
he explicitly wants **maximum isolation and strong public-endpoint
security**, in contrast to his dislike of milspec restrictions on
ordinary internal Sanctum services. PicoShare was an uncommitted
2025/2026 idea; prior October suggestion that Nextcloud public links
may make it redundant is **under reconsideration** due the desired
dedicated and isolated Internet-facing boundary. Official upstream
latest **v1.5.5 released 2026-11-16** adds download passphrases and two
guest-upload security fixes; do not use old v1.5.4 as latest.
[Feasibility note](docs/reviews/2026-11-17-picoshare-public-sharing-options.md)
compares isolated OUTSIDE VPS/static-gateway vs dedicated home DMZ;
public download only, private-only owner upload/admin, TLS, short-lived
unguessable tokens/password, no path into `.sanctum`, resource limits.
The most isolated choice is independent external VPS/object storage
with files pushed outward, **no home WAN ingress** even though static
IP exists; a separately routed/static-IP home DMZ is an alternative
only with true denied LAN connectivity. **No PicoShare install, NAT,
WAN port, DNS, certificate or container creation is approved yet.**
Current exploratory request does NOT create a new compulsory service
workstream.


## November 17 — current next action and future-service scope

**NATIVE YXORP unattended-update source reconciliation accepted:**
Nova ran production `ansible/yxorp.yml`: `kvin.outer.sanctum
ok=36 changed=4 unreachable=0 failed=0 skipped=0`.
Final route report: seven wanted hostnames, Kuma HTTP302,
LinkStack HTTP200, Yarn HTTP200; DNS/firewall/Kvar NPM unchanged.
Source has `nginx:stable-alpine`, Quadlet `AutoUpdate=registry` and
enables/starts **rootful** `podman-auto-update.timer`, in addition to
the preexisting **user** timer. Actual future scheduled update
execution has not yet been observed. [Services #6 accepted receipt](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6952289320).
Older `next_gate: Real EyesOnly Search browser/theme/results acceptance`
was WRONG because EyesOnly actual normal use was already accepted;
source and test were corrected so no repeated browser task is assigned.

**Future service list IS written** under
[SERVICE-ESTATE.md — Future Services backlog](docs/SERVICE-ESTATE.md#future-services-backlog-not-deployed-by-this-register),
also linked from README and Roadmap Stage 6. **Explicitly
selected:** Home Assistant, Luanti and a proper Sanctum VPN.
**Separate committed Nextcloud capability:** live collaboration
between Nova and Joule as distinct user accounts; Collabora/CODE is
only a candidate backend. Historical conversations additionally
mentioned Syncthing, NetAlertX, BookStack, Kiwix, Jellyfin/Plex,
Piwigo, qBittorrent and PicoShare. These are now labeled
**UNCOMMITTED IDEAS**, not a queue, not owner-authorized installs,
and not reason to expand project duration. Historical Dashy/AWX/
Wiki.js/Homarr are not assumed wanted. Pi-hole/OpenWebUI/Endlessh
remain retired.

**IMMEDIATE existing Services next action:** Kuma v2 deployed image
remains digest-pinned and lacks rootless `AutoUpdate=registry`.
Kvin `sanctum-kuma-data` has a **previously validated, actually
restored** SQLite backup `sanctum-kuma-20261111t144137.tar`,
290816 bytes, SHA256
`97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648`.
New Services `ansible/kuma-retain-on-peanut.yml` (not a new backup)
copies this specific existing archive to Peanut with double SHA checks
and no Kuma service pause. **Full source/Ansible CI passed
[44113781527](https://github.com/wdcallahan/sanctum-services/actions/runs/44113781527)**.
Single operator command on **wdc2@kvin**:
`cd ~/src/sanctum-services && git pull --ff-only && ansible-playbook -i ansible/inventory/hosts.yml ansible/kuma-retain-on-peanut.yml -e kuma_retain_on_peanut_approved=true`.
Archive copy **has not been executed**; do not claim Peanut has it yet.
After this, correct Kuma to upstream recommended **`:2`** tag
(**`:latest` is deprecated and refers to v1**) + source-managed
`AutoUpdate=registry`; fix stale role/unit tests and ensure data
retention/upgrade compatibility; no unsolicited major v3 update.
No need to rerun the accepted November 11 Kuma offline restore test,
and do not invent a new security stage.


## Current live recovery result — November 16, late

**Nova has completed the FIRST THREE real Nextcloud recovery stages,
not just the source checks:**

- Kvin live Nextcloud consistent backup `nextcloud-20261116t233618`,
  Ansible **ok=29 changed=9 failed=0**, application mode restored and HTTP
  healthy; owner-scoped PostgreSQL dump plus HTML and private config checks.
- Peanut off-host retained snapshot, **ok=14 changed=3 failed=0**,
  four artifacts with **independent Peanut-side verified SHA256 and tar
  structure**, original point still privately present on Kvin too.
- Peanut isolated application **filesystem extraction**, **ok=14 changed=5
  failed=0**. Actual report:
  `isolated_application_tree_staged=true`,
  `isolated_private_inputs_staged=true`,
  `source_bundle_integrity_checked=true`, `database_dump_not_imported=true`,
  `nextcloud_container_not_started=true`,
  `live_nextcloud_untouched=true`,
  `postgres_cluster_untouched=true`,
  `restore_application_accepted=false`.

**Exact retained Peanut backup:**
`/home/wdc2/.local/share/sanctum-services/backups/nextcloud/nextcloud-20261116t233618`.
**Extracted Peanut-only files:**
`/home/wdc2/.local/share/sanctum-services/nextcloud-restore-trials/nextcloud-20261116t233618/html`
and `.../private`.

**CURRENT OWNER BOUNDARY:** Services reported native success via
[Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6940151074)
and handed actual real snapshot path to
[Maintenance issue #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6940147324).
Maintenance owns `tools/restore-nextcloud-postgresql` for an isolated,
networkless, disposable **actual Nextcloud-only database restore** on Peanut
from the original retained dump. **That test deletes its restored database
after inspection**, so it does not yet make a connection target for a running
restored Nextcloud instance. A longer-lived, *isolated and separate* PostgreSQL
trial service/interface will be needed to connect to a restored Nextcloud app,
followed by real login, files and Calendar acceptance. Services owns app
startup once owner DB interface is ready, and should prepare source only
without claiming backup+file extraction is full recovery. No return to Kvin,
no rebackup, no Pi-hole probe, no bulk size/file census.


**Current: November 16, 2026.** This is the concise, authoritative entry point for a user-appointed Sanctum Services lead. The previous 4,509-line rolling handoff was preserved unchanged at [the historical handoff archive](docs/history/PROJECT_LEAD_INTRODUCTION-through-2026-11-16.md). It is historical evidence, **not** a queue of outstanding commands; numerous older "CURRENT" and "NEXT" paragraphs there are superseded. Read current `main`, [issue #2](https://github.com/wdcallahan/sanctum-services/issues/2), [the roadmap](docs/ROADMAP.md), [the estate register](docs/SERVICE-ESTATE.md), and the specific runbook for the active work. Do not mechanically replay dated instructions.

## Appointment, mission, and operating rhythm

Nova appoints **this chat as the Sanctum Services project lead**, not Bunny Factory or Sanctum Maintenance. Own repeatable, understood, reversible service installation, upkeep, backup, independent restoration, and retirement from supported automation plus recoverable durable inputs. Work directly on linear `main` without default PR/branch overhead. Keep evidence and human-friendly handoffs current; source checks, native runs, consumer acceptance and actual disaster-recovery proof are separate.

**Stay productive until a real boundary:** If independent, authorized source/research/testing/coordination work remains, do it in the current turn rather than ending after an incidental observation or asking Nova to run many tiny probes. Do not claim to perform ongoing work between turns; there is no background execution. Stop and hand off when an actual native terminal action, approval, secret, owner-provided interface, or comparable user-dependent condition blocks the next meaningful operation.

**Exact finger-work contract:** When Nova must run a command, state the **exact host and terminal** first, give **one pasteable fenced code block**, and state **after** the block precisely which output to return (all output or named section plus recap). Prefer normal `git pull` if a clean checkout needs refreshing. Explain new commands/flags at point of use. If a command deviates from routine (wrong/alternate host, restarts, downtime, write/destructive effect, authentication, interactive prompts, credential display, unusual permission/approval), put an unmistakable **⚠️ READ THIS BEFORE PASTING** warning **before** the code block with the actual consequence. Never hide a meaningful change in a routine-looking paste. Never ask for a secret in a chat transcript.

**Ownership:** Services owns Nextcloud and YXORP app/routes, its own service backup/recovery orchestration, and the VPN client/remote-access outcome. **Maintenance** owns PostgreSQL service/privileged DB interface, host firewall/OS/controller tooling; **Bunny Factory** owns VyOS edge/router implementation; **Project Joule** owns Prism app recovery; **EyesOnly** owns Search installation. Coordinate via [Maintenance Interpixel board #20](https://github.com/wdcallahan/sanctum-maintenance/issues/20) and owner issues. Do not edit another owner's active repository or machine just because it is a dependency. The approved HTTP-on-private-network decision stands; do not quietly require a new CA/HTTPS project.

## What we are actually building (operator-facing explanation)

**One backup playbook, one restore playbook, one recovery point stored off Kvin.**
Read the [operator model at the beginning of the Nextcloud recovery runbook](docs/runbooks/nextcloud-instance-recovery.md#operator-model--two-ansible-jobs-and-one-protected-recovery-point). The backup snapshot is a single private directory with `nextcloud-html.tar` (the Kvin host **bind mount**, not a named Podman volume), `nextcloud-postgresql.dump` (Nextcloud's own database only), `nextcloud-private.tar` (private inputs), and `manifest.json` (integrity). Restore via an Ansible playbook into an **isolated** application instance and independent database; accept real data/calendar/login before any production cutover. The Kvin backup, Peanut independent off-host retention, and isolated application file extraction are **now native-accepted**. The full database and application restore trial, functional login/Calendar checks and future automated backup scheduling remain open; see the current live recovery result above.

**Don't conceal ordinary filenames or link targets from Nova.** The earlier staged probes were over-redacted and made the project sound mysterious; they do not justify hiding routine source structure. User-facing information should focus on **what is done, why, and what next**, not on symbolic-link primers or adversarial hypotheticals. Protect **password contents, private configuration values and backup archives**, not innocuous names. The 25 actual link examples from Nova were ordinary `apps/.../js/*.js.map.license -> *.js.license` build artifacts. We know only those 25 by name; avoid declaring that all 118 have that pattern. The prior source scan with 118 links and 5,769,576,446 file bytes has **passed**; don't rerun it.

**Source-only restore progress (November 16):** Services added `ansible/nextcloud-isolated-files-restore.yml` for a **fresh isolated Peanut restore trial** from a preexisting privately retained, verifier-passing snapshot. It restores the HTML and private tarballs into separate new paths under `podman unshare tar`, without touching running Kvin, shared PostgreSQL, services or routes; it does **not** import a database or start Nextcloud and thus is **not yet a complete restore**. Synthetic source tests plus Ansible syntax passed [CI 43971980420](https://github.com/wdcallahan/sanctum-services/actions/runs/43971980420), commit `a484aa5`. No native trial performed; the snapshot does not exist yet. Native activation remains blocked on off-Kvin storage selection/capacity, Maintenance's scoped Nextcloud database export, and explicit approval of the short application maintenance-mode window. Details in the [recovery runbook](docs/runbooks/nextcloud-instance-recovery.md).

**November 16 operator decision — backup windows and rollback:** Nova accepts a scheduled brief overnight Nextcloud maintenance-mode interruption and potential client retry; do not design zero-downtime capture by default or promise a precise duration before measuring the real 5.77 GB application capture and scoped PG dump. Crucially the eventual Ansible restore must distinguish **full snapshot restore** from **database-only rollback while preserving newer live files**. For the second mode, preserve current files+DB first, rehearse older DB with current files in isolation, reconcile file index/client state as appropriate with `occ files:scan`/`maintenance:data-fingerprint`, and validate files, shares, Calendar and schema compatibility. Do not assert it can recover database-only Calendar events newer than the DB rollback point. [Runbook decision](docs/runbooks/nextcloud-instance-recovery.md#accepted-operating-policy--brief-maintenance-window-two-recovery-modes) accepted as design intent, **not** a completed tested restore. Prioritized straightforward Ansible backup/restore over excessive filename redaction or theoretical hardening.

**November 16 accepted size/host observations:** Nova's Kvin `podman unshare du` and Kvin→Peanut SSH `df/lsblk` **passed**. Kvin HTML occupies **5.5 GiB allocated**: `data` 4.6 GiB, of which **`data/wdc2` is 4.4 GiB**; `data/appdata_oc0fmherf6qh` 112 MiB; `apps` 523 MiB, `core` 158 MiB, `custom_apps` 97 MiB. Nova has not populated Nextcloud meaningfully, so **actual contents under `data/wdc2` remain surprising and unclassified**. Do not guess, delete, clear caches or repeat accepted source and size checks. Next ask Nova for **one Kvin read-only inspection of `data/wdc2` child directory sizes and optionally largest file names** (no contents), and explain why.

**Physical SSD discrepancy identified:** Kvin's Crucial CT1000P3SSD8 is **931.5 GiB** device, root ext4 **917 GiB/849 GiB free**; Peanut's Kingston SNV2S500G is **465.8 GiB** device, root ext4 **459 GiB/432 GiB free**. Peanut is the smaller intended partner, with ample current capacity. Nova's desired two-host database primary/secondary and possible standby roles remain planned, **not proven live PG streaming replication/failover**. Maintenance #17 has the [supported scoped export/restore/HA interface handoff](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6932965316); old firewall transfer #1 and owner #18 are already complete.

**November 16 Nextcloud browser acceptance and software-update GAP:** Nova successfully reset the `wdc2` administrator password interactively, manually saved it to Bitwarden and logged into real `http://square.nexus.sanctum/`. Background changed for readability; active UI works. His screenshot shows a ~4-week-old notification advertising version **35.0.2**. **Do not assume upgrade completed**. Real deployed version is pending one read-only `podman exec -u www-data sanctum-nextcloud php occ status --output=json` observation. Source `ansible/group_vars/nextcloud.yml` pins official Nextcloud **34.0.5 Apache by immutable digest**; Quadlet template has `Restart=always` but **no `AutoUpdate=registry`** or digest refresh/scheduled application upgrades. **Automatic Nextcloud updating was expected by Nova but is NOT configured**. Official **34.0.6 and 35.0.3** were released Nov12. This is a real Services requirement, tracked [Services issue #5](https://github.com/wdcallahan/sanctum-services/issues/5); patch/security update scheduling should be integrated with Ansible source/verified backups, while major upgrades require compatibility review and recoverable snapshot. Do not apply an unreviewed major upgrade before isolated restore is proven.

**User-data gigabytes EXPLAINED:** Nova's follow-up `du` found `data/wdc2/files/Music` **4.0 GiB**, `Videos` 288 MiB, `Photos` 78 MiB and tiny trash. Actual large files included his Pint and Dale WAV collection. In the Firefox screenshot under `Music/Pint_and_Dale`, album folders with spaces each average ~500–560 MB, while corresponding underscored album folders are ~45–48 MB. **Most likely WAV versus compressed encoded tracks**, not Nextcloud-created duplicate directories, but file extensions **in each pair** are not yet verified. One native no-change observation should report *extension counts/sizes per album*, and `occ status` + running image identity together; no passwords or file contents, no deletion, no installer or updater. Do not re-run old full-tree or disk analyses.

**November 16 operator correction — do not freeze production images or LAN access:** Nova emphatically reaffirmed that wanted applications should receive **unattended updates** and services must not be limited to **one arbitrary client source IP**. The [Services source audit](docs/reviews/2026-11-16-image-update-and-lan-policy.md) identified permanent digest-without-updater defects in Nextcloud and Kuma; YXORP/Nginx was also frozen but Services has **source-corrected it** to `docker.io/library/nginx:stable-alpine` + Quadlet `AutoUpdate=registry` (production and stage) with a regression test, **[full CI passed run 44001338860](https://github.com/wdcallahan/sanctum-services/actions/runs/44001338860)** on `86702ff`. **No native host change or actual timer acceptance!** LinkStack's recovered candidate pins an older original digest + `Pull=never`; distinguish restore fixture from desired update lifecycle. Pi-hole's old pin is retired (do not redeploy). EyesOnly is source-correct with `:latest` + `AutoUpdate=registry`, native timer unverified. [Services issue #6](https://github.com/wdcallahan/sanctum-services/issues/6) owns all application image policy and [#5](https://github.com/wdcallahan/sanctum-services/issues/5) Nextcloud update gap; owner Maintenance [#5 comment](https://github.com/wdcallahan/sanctum-maintenance/issues/5#issuecomment-6935782334) owns fleet Quadlet/timer/PG inventory. Do not enable a major Nextcloud/PG upgrade before recoverable snapshot and restore, but do not treat a dormant digest as the *permanent* update policy.

**Network correction:** Joule's obsolete Wicket FPC-7 helper contains a rejected `192.168.1.192/32` Host 18096 rich rule; Nov2 native Wicket **actually had no firewall and worked from Kvin/Mace**. This is a known **source trap**, not live firewall outage; [Joule issue #9 updated](https://github.com/wdcallahan/joule/issues/9#issuecomment-6935786809). Joule's currently checked-in Ollama Quadlet `PublishPort=127.0.0.1:11434` is an additional source regression against its already approved ordinary-LAN API intent; actual live behavior not observed in this turn. Kvin 8084/5432/8085 ordinary admission and prior narrow-rule removal were already accepted in Maintenance #18. Do not rerun accepted network tests or invent live violations from code alone.

**Maintenance DB exporter is NOW AVAILABLE:** Maintenance published `tools/backup-nextcloud-postgresql` with exact scoped synchronous output contract and passing PostgreSQL synthetic round-trip [CI run 43974977911](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43974977911); [runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/nextcloud-postgresql-backup.md). Services has **integrated** its exact scoped command into the guarded backup coordinator (Services [CI 44001769569 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/44001769569)); native backup, off-host retention and isolated restoration have **not yet been run**. Correction: the current owner helper verifies the PostgreSQL **image family** and server major 18, NOT equality to a literal old digest; earlier reporting claiming the helper would reject every patched image was mistaken and [corrected](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6939054034). The installed PostgreSQL Quadlet is independently still pinned. No fresh operator approval or live host mutation implied by source publication.

**November 16 source CI checkpoint:** Services' **source-only** fixed YXORP image channel + `AutoUpdate=registry` has [full CI success 44001338860](https://github.com/wdcallahan/sanctum-services/actions/runs/44001338860), commit `86702ff`; no live Nginx update, Quadlet installation or auto-update timer check occurred. The Maintenance scoped Nextcloud exporter source integration into `ansible/nextcloud-consistent-backup.yml` and contract tests also has [full CI success 44001769569](https://github.com/wdcallahan/sanctum-services/actions/runs/44001769569), commit `f3b8f91`. No backup was run. Cross-owner response to Maintenance #17 posted [here](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6935919643); Services issue [#6](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6935928613) and [#2](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6935929222) have durable result. **Next operator action:** one non-mutating Kvin command to read actual installed Nextcloud version and ordinary rootless container images, current user/system Quadlet image/update/pull fields and rootful/rootless `podman-auto-update.timer` state. Do not ask Nova to rerun already accepted 4.4 GB music/file-tree or SSD measurements. Do not claim update mechanism live or first snapshot accepted. Preserve owner's preference for live updates, not permanent digest freezing.

**November 16 evening — Kvin Native IMAGE/TIMER OBSERVATION ACCEPTED; NEVER repeat:** Nova returned `occ status --output=json` proving **Nextcloud 34.0.5.1 (34.0.5), installed, maintenance=false, needsDbUpgrade=false**. Rootless `podman ps` lists nextcloud/postgresql/kuma/linkstack-candidate on digests, Prism local image and search `searxng:latest`. **User `podman-auto-update.timer` enabled/active; rootful system timer disabled/inactive**. Inspected Search Quadlet declares `AutoUpdate=registry`; current installed YXORP, Nextcloud, Kuma, PG and LinkStack-candidate do not. Installed rootful YXORP Quadlet still pinned, despite Services-owned source correction. Services subsequently also **added production-only convergence of the system `podman-auto-update.timer`** under the YXORP role and test; **[full CI passed run 44005725062](https://github.com/wdcallahan/sanctum-services/actions/runs/44005725062)** at `3de917e6`. **No native apply or timer activation occurred**. Next step is an actual approved production YXORP deploy/acceptance, not another inventory. [Updated policy audit](docs/reviews/2026-11-16-image-update-and-lan-policy.md).

**Nova clarifications while audit continued:** Pi-hole is **unwanted and permanently retired**. Nova physically **unplugged the old Kvar machine** and intentionally did not preserve Pi-hole as a wanted migration or retain its backup; if he wants Pi-hole again it will be a **new installation**. Do not keep Pi-hole alive via legacy Quadlet or backup work. A leftover `/etc/containers/systemd/sanctum-pihole-kvin.container` source file still exists on Kvin and needs **scoped rootful boot-state inspection** before deletion/retirement; previous `podman ps` was rootless and does not establish rootful Pi-hole process state. Avoid disputing his intent because legacy code says "restored". Ordinary user deletion of uploaded WAV albums via **the same application-managed share/interface** that uploaded them is supported; do not invent a need for a raw Kvin NFS/SMB scenario or warn him away from normal client file management. Precise protocol is not established, and no cleanup was authorized for Services.

**Wicket Host 18096 in plain words:** This is **Joule Host's authenticated HTTP API on Wicket, consumed by Prism on Kvin and other authorized internal clients**; it is distinct from the Ollama inference API at 11434. Old FPC-6 **temporary Kvin-only test** (Sep 10) became old FPC-7 **persistent single-client firewall source** (Sep 13) without demonstrated permanent user approval. Nova rejected single-IP policy explicitly Nov 2. New Wicket has accepted real Nov 2 evidence of *no active 18096 firewall source limitation*. Dedicated conspicuous owner [Joule issue #16](https://github.com/wdcallahan/joule/issues/16) requests provenance review and executable-source retirement; [#9](https://github.com/wdcallahan/joule/issues/9#issuecomment-6936395427) links handoff. Do **not** call it an active firewall rule.

**Complete audit expanded:** Initial audit only searched two symptom classes; user explicitly wants ALL similar constraints and regressions. [Maintenance issue #38](https://github.com/wdcallahan/sanctum-maintenance/issues/38) now owns broad eight-dimension audit (update paths, network/roles, declared/runtime drift, obsolete remnants, backup/restore, HA, tests enforcing outdated policies, monitoring). [Maintenance #5](https://github.com/wdcallahan/sanctum-maintenance/issues/5#issuecomment-6936427713) holds native Kvin inventory to avoid repeats. [Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6936396767) explicitly acknowledges Services backup helper integration **CI passed** and **Maintenance no longer awaits further Services handoff** to independently qualify isolated DB restore. No automatic ability to force a different ChatGPT session to take turns; GitHub handoff is durable.

**NEXT ACTION after Maintenance response (November 16 evening):** Maintenance explicitly says **Services runs the coordinated backup playbook during the tolerated brief overnight Nextcloud write pause**, no further Maintenance command beforehand. Source-only `ansible/nextcloud-retain-on-peanut.yml` stages exact four-artifact verified backup to an independently checked owner-private folder on Peanut with no DB/service changes; **[full CI passed 44021986569](https://github.com/wdcallahan/sanctum-services/actions/runs/44021986569)**; native use pending. Do not wait for owner response or redo earlier accepted disk/link checks. Actual Kvin backup and Peanut copy have not been run; the first backup still requires one precise operator command with the explicit application maintenance-mode impact warning. If Ansible is interrupted between maintenance mode on/off, issue a direct safe `occ maintenance:mode --off` recovery instruction.

**Pi-hole retirement implementation:** Native `systemctl show sanctum-pihole-kvin.service` proved **system/rootful unit is active and running**, unlike the initially observed *user* `podman ps`. Nova explicitly orders full **decommissioning**, no more inspection, no Pi-hole backups (future installation from scratch), and Kvar physically unplugged. Services removed the live Pi-hole deploy/restore/backup source and tests and prepared `tools/retire-pihole-kvin.sh`: narrowly stop exact system service, delete its Quadlet, remove the named container, its two dedicated rootful volumes and known local Pi-hole archives. **GitHub-only source work**, not native execution; script has a strict Kvin+sudo-wdc2 guard and should be run once with an explicit destructive warning. Historical disabled YXORP route remains as provenance; stale Pi-hole opt-in is now refused at the actual Kvin stage preflight, source tests pending. All future source deploy of Pi-hole should be impossible without new intentional code. No Pi-hole host changes yet.

**NATIVE Pi-hole retirement COMPLETE, November 16 (do NOT repeat):** Nova ran `cd ~/src/sanctum-services && git pull --ff-only && sudo bash tools/retire-pihole-kvin.sh` on Kvin as `wdc2`, without any sudo password prompt. Output confirms named rootful Pi-hole volumes removed, original image untagged/deleted, dedicated archive directory removed by script, and **`Unit state: LoadState=not-found ActiveState=inactive`**. Other service Quadlets, network/DNS and PostgreSQL were not touched per script. Old Kvar remains unplugged. The source reinstall paths are removed, historical Pi-hole stage is refuse-gated. **Pi-hole task done. No further probe, reinstallation, backup work or cleanup request.** [Services #6 receipt](https://github.com/wdcallahan/sanctum-services/issues/6#issuecomment-6939372574).

**ACTIVE SERVICES NEXT (not Maintenance blocking):** Next step is a real operator-authorized Kvin Nextcloud snapshot: `ansible-playbook -i ansible/inventory/hosts.yml ansible/nextcloud-consistent-backup.yml -e nextcloud_consistent_backup_approved=true -e nextcloud_database_export_contract_approved=true` as `wdc2` on Kvin. Clearly warn **real brief Nextcloud write interruption** and new private backup files; no sudo, no production PG writes and no service restart. Play first checks the Maintenance exporter exists at `/home/wdc2/src/sanctum-maintenance/tools/backup-nextcloud-postgresql`; if missing it refuses before maintenance mode. Source contract [CI 44001769569 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/44001769569). Then parse reported actual named `bundle_private_on_kvin` path, and run the source-validated Peanut retention play with that exact `nextcloud-YYYYMMDDtHHMMSS` ID; follow with independent restored test. No backup has yet occurred. The user's approved brief window can be used at appropriate quiet time; do not claim elapsed time in advance. If controller unexpectedly killed, check `occ status` and explicitly restore maintenance off. Maintenance #17 said no separate owner action before this. [Issue #2 receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6939373678).

**NEXTCLOUD KVIN→PEANUT RECOVERY POINT NOW COMPLETED/ACCEPTED (November 16):** Nova completed native `ansible/nextcloud-consistent-backup.yml` on Kvin, **`ok=29 changed=9 failed=0`**, with scoped Maintenance PostgreSQL exporter, actual app write-quiescence and full HTML/private/dump bundle, hashes valid and **Nextcloud maintenance mode OFF + HTTP healthy**. Actual ID `nextcloud-20261116t233618`. Then completed native `ansible/nextcloud-retain-on-peanut.yml`, Peanut **`ok=14 changed=3 failed=0`**, four actual artifact files copied; **Peanut independently verified hashes/archive structure**. Exact actual owner-private directory on **Kvin AND Peanut**: `/home/wdc2/.local/share/sanctum-services/backups/nextcloud/nextcloud-20261116t233618`. No database/service changed on Peanut. This IS a valid independent off-host backup, NOT yet a passed restore. [Services #2 acceptance](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6940074791), [Maintenance #17 restore handoff](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6940073248), and [runbook supersession](docs/runbooks/nextcloud-instance-recovery.md). **Do not ask user to rerun either successful operation.** No reason to wait on more Maintenance source work.

**NEXT ONE OPERATOR STEP:** On Kvin as `wdc2`, run the already source-qualified `ansible/nextcloud-isolated-files-restore.yml` targeting **Peanut** with `-e nextcloud_isolated_recovery_id=nextcloud-20261116t233618 -e nextcloud_retained_bundle=/home/wdc2/.local/share/sanctum-services/backups/nextcloud/nextcloud-20261116t233618 -e nextcloud_isolated_file_restore_approved=true`. This extracts two archives to a fresh private isolated directory on Peanut (5+GB), starts no container and modifies NO live service or production DB. After native files stage, Maintenance owns disposable PG restore (owner helper `tools/restore-nextcloud-postgresql`), then joint isolated application startup and Calendar/files/login proof. Do not conflate staged files or isolated PG tables with a complete working Nextcloud restore.

## Accepted estate and what must NOT be reopened

- **Kvar is physically powered off** by Nova on November 16 after he saved its SSH banner. It has not been wiped or reimaged. Rebooting it requires inconvenient ladder access; **do not request Kvar power-on or redo the shutdown**. Tailscale was already removed by Nova and its other users; previous "preserve Tailscale exit node" instructions are obsolete.
- Kvin **YXORP plain Nginx** production seven-vhost reconciliation is operator accepted. Kvin **Kuma**, **LinkStack** and **EyesOnly SearXNG** normal usage are accepted. **Pi-hole, OpenWebUI and Endlessh are retired** from intended estate. Do not reinstall or re-probe them. Kvin **Nextcloud** is installed and active; **Calendar 6.6.2** bidirectional GNOME Calendar usage is already accepted. Kvar wanted application migrations are complete, but off-host disaster recovery for the wanted estate is not.
- Separate future VPN work: `buny.us` is the chosen public WireGuard hostname, DirectNIC login/DDNS credential was unavailable at last confirmation, and production New Outer routing/firewall/WireGuard termination requires Bunny ownership and explicit decisions. The ISP/public-IP question was pending as of the latest recorded status. This is **not** the active Services Nextcloud recovery slice.

## Active frontier: Nextcloud complete-instance recovery

**Latest source checkpoint:** The previous validated input/bundle-reader release was Services `c1f11c8` ([CI 43946416164](https://github.com/wdcallahan/sanctum-services/actions/runs/43946416164)). Subsequent Nov16 source includes `tools/nextcloud-recovery-assemble.py`, `ansible/nextcloud-consistent-backup.yml`, `tools/nextcloud-recovery-readability.py`, synthetic tests and docs. [CI 43959448677](https://github.com/wdcallahan/sanctum-services/actions/runs/43959448677) passed at `c51ff0e`; later documentation commits are expected. All these are **source qualification only**, with no native write or restore. Check latest `main` and issue #2 before writing.

**Native observations accepted:** `ansible/nextcloud-recovery-inputs.yml` on Kvin returned `ok=6 changed=0 failed=0`, installed/active HTTP200, all expected inputs present, **no backup or restore**. Nova separately ran `podman exec -u www-data sanctum-nextcloud php occ config:system:get datadirectory`, confirming **`/var/www/html/data`** in persistent **`/var/www/html`** host bind `~/srv/sanctum-services/nextcloud/html`. **Do not repeat** either probe.

**Services source ready:** `tools/nextcloud-recovery-bundle.py`, synthetic tests, CI and [Nextcloud instance recovery runbook](docs/runbooks/nextcloud-instance-recovery.md) validate *only* a private manifest-described bundle: complete HTML/data/custom apps tar, private config/credential tar, and custom-format **Nextcloud-only** PostgreSQL dump. They verify markers, hashes, permissions and unsafe archive members, **not** actual backup creation, consistency, custody or successful restore. None of the latter has been established.

**Actual next engineering result:** Deliver a guarded, documented, tested, coordinated Nextcloud recovery procedure:
1. Develop Services-owned source for maintenance-mode write quiescence, consistent application+private file capture, one named recovery point, cleanup/reversal, protected off-Kvin copy and retention, consuming a narrow owner-supported DB dump.
2. Maintenance must publish its **Nextcloud-only PostgreSQL export interface** (request on [Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6927299607)); at last read there was **no owner answer**. Do not impersonate that interface, manage the shared PostgreSQL cluster, dump unrelated databases or print private credentials. Advance independent Services source work while this dependency is pending.
3. Once contracts/source are qualified and a native operation is independently approved, take an actual consistent recovery point, retain it off Kvin and verify bundle integrity. Then restore **isolated** app+DB without altering production, accept user data, known Calendar state, startup, and repeat convergence. Do not claim this outcome until demonstrated.

**November 16 latest native evidence:** Nova ran `tools/nextcloud-recovery-specials.py` in Kvin's rootless namespace. The actual HTML bind contains **28,955 ordinary files, 3,877 directories and exactly 118 symbolic links**, total 32,950 members. All links are **relative, resolve inside the current HTML bind, and are neither dangling nor unresolved**; all appear in the broad `other` area, none in `data`, `config`, `custom_apps`. There are **no FIFOs, sockets, devices or other unusual entries**. Do not rerun that accepted classifier or change ownership/permissions.

**Services source now preserves rather than rejects those links.** The producer `tools/nextcloud-recovery-assemble.py` admits only relative symlinks that remain lexically and physically inside the HTML source and preserves them without dereference; the verifier `tools/nextcloud-recovery-bundle.py` independently checks they resolve inside the archive to actual included members and rejects missing, circular, escaping, hardlink, special-entry or symlink-parent tricks. The private credentials archive still forbids symlinks. The read-only `tools/nextcloud-recovery-readability.py` gate now permits and counts qualifying links. Synthetic adversarial tests and Ansible/source CI **passed** at [run 43967187394](https://github.com/wdcallahan/sanctum-services/actions/runs/43967187394), source commit `229b04a`. Full explanation and exact next command are in the [Nextcloud recovery runbook](docs/runbooks/nextcloud-instance-recovery.md).

**Native source-readability gate ACCEPTED (November 16):** Nova ran the updated Kvin `podman unshare` validator. It returned `source_tree_readable_for_assembler_at_scan_time=true`, `html_regular_files=28955`, `html_directories=3877`, `html_relative_internal_symlinks=118`, `html_file_bytes=5769576446` (~5.77 GB decimal, 5.37 GiB), `private_required_files_readable=4`, and `unaccepted_special_members_observed=0`. The full result explicitly says no app interruption, DB export, bundle creation, consistency proof, or off-host backup. **Do not request this accepted readiness scan again.**

**User understanding:** Explain the goal in ordinary terms before requiring command execution: a disaster-recovery backup includes the persistent HTML tree + Nextcloud-specific database + private credentials, copied off Kvin and actually restored in isolation. The previous archive policy rejected all links; the new source accepts only safe relative contained links as links rather than copying their targets or ignoring them. The 118 known links are in the classifier's broad `other` region; their specific names and functions **have not been inspected**, so do not pretend they are known. If Nova wants to know their real identities, a newly justified **read-only Kvin `find` sample** can show relative link names and targets without file contents. No special warning label is warranted for a routine read-only inspection; reserve the red-label warning for consequential operational differences.

**Storage planning:** source file bytes alone total 5,769,576,446, excluding tar overhead, PostgreSQL dump, temporary staging, checksums and protected off-host retention. Choose and validate the destination capacity before native backup capture, and avoid simultaneous unbounded copies on Kvin.

**Separate owner blocker:** Maintenance's Nextcloud-only PostgreSQL custom dump interface remains unanswered in issue #17. Services must not mutate the shared PostgreSQL service. The guarded backup coordinator is **not authorized for live use**. No production downtime, database dump, off-Kvin backup or isolated restoration has yet been authorized or reported.

## Human handoff and reading order

The project has **two outputs**: working software and Nova's engineering understanding. Read [README](README.md), [roadmap](docs/ROADMAP.md), [estate register](docs/SERVICE-ESTATE.md), [recovery runbook](docs/runbooks/nextcloud-instance-recovery.md), and applicable [shared completion](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md) and [project interface](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md) standards. Consult logs and the [historical handoff](docs/history/PROJECT_LEAD_INTRODUCTION-through-2026-11-16.md) only for a specific needed fact.

At meaningful checkpoints record **what new operator capability exists, what was actually verified, what remains, who owns the dependency, and the exact next action**. Don't use a whole turn for a single obvious fact when meaningful source work can be completed without Nova's fingers.
