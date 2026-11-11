# Sanctum Services — Session Continuation

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

**Now execute SS-APPS-1 (first real application migration):** Kvar Kuma
was a proof of concept and a **clean retained Kvin installation is
already approved**. Source skeleton already exists at `ansible/kuma.yml`,
`ansible/group_vars/kuma.yml`,
`ansible/roles/kuma/tasks/main.yml`, and
`ansible/roles/kuma/templates/kuma.container.j2`, but
`kuma_image` is still empty (explicit guard): it has not deployed.
First establish a verifiable **ARM64 Kuma 2 image digest** and
version-compatible monitor management interface without manual
database edits. Build/qualify a new **rootless, loopback-only Kvin Kuma
candidate** using existing safe-approval gates. Persist and restore
its own volume, verify live UI and desired `Wicket Ollama` monitor
(`http://wicket.arcane.sanctum:11435/healthz`) actually **Up**,
reconcile an unchanged repeat and keep old/test alerts from duplicating.
Only after app acceptance move `kuma.nexus.sanctum` upstream off Kvar
and prove actual client use. Nova supplies native commands only when
Kvin evidence is indispensable; Pixel handles source/CI/docs itself.
No arbitrary time limits or speculative additional probes.

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
