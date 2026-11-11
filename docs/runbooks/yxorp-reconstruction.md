# YXORP — plain Nginx on a rootful Podman Quadlet

## Native source-class result: 3 Kvin, 3 other old Yarn log requests; exact addresses next (November 10)

**Kvar NPM old Yarn source-category probe completed**
`ok=5 changed=0 failed=0`.
Six records in one readable
proxy-host 11 access log,
all from the last 30 days,
none lost to a truncated tail:
three from the known Kvin
observer address, zero from
known Kvar host or loopback,
**three from other IP
addresses**, none unclassified.
A log source is not necessarily
a distinct client; NAT or
proxy forwarding may be present.
Exact other addresses remain
**unobserved**, so do not guess
which device or person made
those requests.

Nova asked why addresses
had been redacted. For his
own LAN, an IP address is
a useful operational identifier,
not a password or credential.
A new narrowly scoped **read-only
exact-address** diagnostic
returns IPs and request counts,
while still suppressing
request paths, query strings,
tokens, cookies, and raw log
lines. No NPM config, DNS,
firewall or host is modified.

**Next exact operator command from Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvar-legacy-yarn-source-addresses.yml
```

This play targets only the
existing Kvar NPM, checks
the legacy Yarn route remains
disabled, reads a bounded
tail of only the fixed current
and first plain rotated
`proxy-host-11_access.log`,
and emits precise source
IP/count pairs and log-coverage
metadata. It never exposes
HTTP request lines or credentials.
**Return only** the one-line
Kvar `PLAY RECAP` and `msg`
from **“Report only old Yarn
NPM logged source addresses
and counts”**, or failed task
and error. No full logs.

**Current policy remains**
7/8 Kvin anonymous local HTTP
routes qualified. The eighth
old `yarn.inner.sanctum`
name is **disabled**, not
accepted or retired.
Kvin can reach the origin,
but Kvar host and Kvar
NPM container could not
reach it in prior native
tests. Its actual consumers
and alias need remain a
deliberate operator decision.
Kvar NPM/wildcard DNS still
production; cutover,
firewall and Kvar retirement
are not approved.

## Native Kvar NPM old Yarn access count — six recent entries; classify fixed source buckets next (November 10)

**Completed native privacy-preserving log
check** `ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml`
returned Kvar `ok=5 changed=0 failed=0`.
The old NPM generated host 11 config
exists and explicitly declares the
fixed access log. One plain current
file was found and fully sampled.
Six entries, all six timestamps
parseable, were recorded within
the last 7 and 30 days, newest
less than a day old. No selected
tail truncation or additional
rotation was observed. The
6 entries **could all be our own
test requests**; they could also
contain an actual client. The
report did not expose source
addresses, requests or client
identities. Neither real consumer
use nor safety to retire the
old hostname has been proven.

The old `yarn.inner.sanctum`
Kvar NPM route **still timed
out** through the last independent
Kvin observation. Kvin reaches
the origin directly by hostname
and IP and forwards successfully
under the accepted new
`yarn.nexus.sanctum` stage.
Earlier direct **Kvar-host
and Kvar-NPM-container**
origin requests also failed,
so NPM-only misconfiguration
is not demonstrated. The
old path remains deliberately
**disabled on Kvin** pending
a consumer/retirement decision.
No Kvar-specific network repair
is approved from these counts.

**One last bounded consumer signal:**
`ansible/yxorp-kvar-legacy-yarn-source-classes.yml`
runs only on the existing Kvar
NPM container; it reads at most
1MiB each from the fixed current
and plain-rotated proxy-host-11
logs. It counts 30-day entries
by the explicit NPM `[Client IPv4]`
field, using predefined buckets:
known Kvin test-host source,
known Kvar source, known Kvar
loopback, other, or
unclassified log syntax.
It **does not print IPs or any
raw log data**, and does
not claim a source is a
particular person or a
genuine user rather than
another internal test. A
missing or unparseable source
remains **unknown** rather
than inferred, and even
all entries matching our
test hosts cannot justify
automatic hostname removal.
No route, NPM configuration,
file, DNS, firewall or
service is modified.

**Next exact command from Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvar-legacy-yarn-source-classes.yml
```
Ask only **Kvar's one-line
`PLAY RECAP`** and the
`msg` dictionary from
**“Report only old Yarn NPM
client-source classes and sample
coverage”**. On failure only
failed task/error. No raw logs.
After this review, leave the
legacy hostname explicitly
held for Nova's client-use/
retirement decision, not an
eighth Kvin activation. The
seven accepted new Kvin
local HTTP routes and Kvar
production proxy are unchanged.
App state migration and
client cutover are still
separate work.

## Legacy Yarn old name: healthy from Kvin, Kvar transport broken; usage evidence next (November 10)

**Native Kvin-only observation complete:**
`ansible/yxorp-kvin-legacy-yarn-observe.yml`
returned `ok=4 changed=0 failed=0`.
Direct old Yarn backend by literal
`192.168.1.110:80` and by DNS
`yarn.inner.sanctum` both gave
HTTP200 to the legacy Host header.
The old origin IP also answered
HTTP200 with the newer
`yarn.nexus.sanctum` Host, and
the already accepted Kvin stage's
new Yarn name returned HTTP200.
All observed media types present,
no redirects. But Kvar NPM's
existing frontend for
`yarn.inner.sanctum` **timed out**
from Kvin (HTTP status unavailable).
This test left the old eighth
route disabled and made no changes.

**Previously established Kvar transport
failure must not be overlooked:**
The earlier Services native Kvar
diagnosis separately tested origin
`192.168.1.110:80` from Kvar
HOST and Kvar NPM's own rootful
container namespace; **both failed
to receive HTTP**, including a
container Node request classified
as **timeout**. Thus the shared
failure is Kvar's path/source/
return behavior, not demonstrated
to be an NPM configuration problem.
Later `ip route get` succeeded
on Kvar and Kvin, showing the
same selected gateway with
different source IPs and no
explanation of packet delivery.
The decision was to **defer
repair of this obsolete Kvar
transport path unless an actual
client needs it**. [Native
Kvar finding](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6777002547)
and [route comparison/deferral](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6777997059).

**Current count: seven Kvin names
initially accepted of eight
manifest entries**. The last old
`yarn.inner.sanctum` is neither
accepted nor activated on Kvin.
Do not enable or retire it merely
to get 8/8. Need client usage
and route policy decision. The
new `yarn.nexus.sanctum` route
is independently accepted.

**Next privacy-preserving evidence:**
`ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml`
targets only Kvar's known
`npm_proxy_legacy` and uses
the existing `nginx-proxman`
container's Node runtime to
examine at most 1MiB each from
current and one rotated old
`proxy-host-11_access.log`.
No live NPM config, DNS, backend,
routing, firewall or container
state is changed. The result
reports the existence of
generated config/logging, file
coverage, whether rotations/truncation
make the sample incomplete,
parsed timestamp count and
aggregate samples in the last
7/30 days. The play suppresses
raw config/log content, requests,
host IPs, query strings,
cookies, errors and credentials.

**Do not overinterpret a count:**
our repeated operator requests
may appear in those access logs;
the current log may be absent or
disabled, rotated samples incomplete,
and direct clients bypass NPM.
Even 0 records cannot prove
the old name is unused. The
script always reports
`current_client_use_proven=false`
and `safe_to_retire_proven=false`.

**Next native command from Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvar-legacy-yarn-consumer-signal.yml
```
Return just **Kvar's one-line
`PLAY RECAP`** and `msg` from
**“Report only old Yarn NPM
access-log coverage and aggregate
counts.”** If a task fails,
only its failed task/error.
No long logs. No old Kvar network
repair or eighth route activation.

## Latest native Pi-hole check accepted (7/8); old Yarn alias remains disabled — November 10

**Seven of eight YXORP route names have passed
the first bounded local HTTP check on Kvin.**
Pi-hole is the new seventh result:
`ansible/yxorp-kvin-stage.yml`
completed `ok=46 changed=3 failed=0
skipped=1` while selecting exactly
Yarn, Square, Prism, Search,
LinkStack, Kuma and Pi-hole.
`ansible/yxorp-kvin-stage-pihole-probe.yml`
completed `ok=4 changed=0 failed=0`.

For Pi-hole `Host: pihole.nexus.sanctum`,
the direct Kvar UI backend `:82`,
incumbent NPM `:80` and new local
Kvin stage `:80` matched:
- Anonymous GET `/`: all returned
  **HTTP404** with the same candidate/
  incumbent media type; no redirects
  were sent; no redirect comparison
  is relevant.
- Anonymous GET `/admin/`: all
  returned **HTTP302**, the same
  candidate/incumbent media type,
  and **exact equal original
  relative Location headers**.
This accepts initial Pi-hole UI
proxy compatibility, **not**
ad blocking/resolver behavior,
login, persisted data,
dashboard scripts or actual
Pi-hole application restore
onto Kvin. The Pi-hole backend
still resides on Kvar.

**Final unqualified route name:**
the old `yarn.inner.sanctum`
frontend to IP `192.168.1.110:80`
is *distinct* from the accepted
new `yarn.nexus.sanctum`.
Kvar NPM's legacy path previously
timed out. Do not enable it merely
to reach 8/8: first establish
whether its backend and the
existing NPM route are reachable
and what consumes the old name.
Replacement/retirement needs a
separate deliberate decision.

**Next bounded read-only task:**
`ansible/yxorp-kvin-legacy-yarn-observe.yml`,
which *asserts the legacy route
is disabled* and performs anonymous
HTTP GET / via five paths:
direct old IP/old Host,
direct DNS name/old Host,
incumbent Kvar NPM/old Host,
Kvin accepted new-name stage
as a control, and old IP/new Host.
`tools/observe-yxorp-legacy-yarn.py`
uses raw HTTP from Kvin with
six-second per-request timeout
and reports only safe outcome/status,
redirect kind and media-type
presence. It never reveals bodies,
raw redirects, cookie/session
values or error messages. This
does not establish historical
client usage or warrant legacy
route activation.

**Next exact command on Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-legacy-yarn-observe.yml -e yxorp_kvin_stage_approved=true
```
**Output:** Only the single
`PLAY RECAP` line and `msg`
dictionary from **“Report only
old Yarn alias HTTP transport
classifications.”** If a task fails,
provide that failed task and
error only. Do not request
complete Ansible output.
No configuration, active
route selection, DNS, Kvar NPM,
firewall or cutover changes occur.
Kvar NPM and wildcard DNS
remain production; Maintenance
owns Kvin firewall. Restoring
Kuma, Pi-hole and LinkStack
and their application state
on Kvin remains separate
from these proxy compatibility
checks.

## Current Kvin stage — Kuma raw redirect parity confirmed; Pi-hole seventh canary next (November 10)

**Root cause of the earlier Kuma "mismatch" was the
observer, not the HTTP proxy.** Nova's
latest actual read-only wire probe completed
`ok=7 changed=0 failed=0`; it confirmed
the Kvin-mounted config equals the
host-published one and contains the
temporary Kuma-only redirect rule.
More importantly, the exact **wire
Location** from three independent
`Host: kuma.nexus.sanctum` GET /
requests through direct Kvar Kuma
:3001, incumbent Kvar NPM and
new Kvin stage was **relative in
all three**, with full header equality
true through all paths and HTTP302
statuses. Direct Kuma with proxy-style
forwarded headers emitted the same
relative Location. The earlier
Ansible `uri.location` compared
*absolute representations* resolved
against each different request
address, so its hostname/port
comparison gave a false negative.
The active Kvin stage's anonymous
Kuma root routing is **accepted**
based on the independent actual
HTTP header comparison, not the
previous normalized `uri` field.

**Status: 6/8 route names tested,
6 passed their first limited local
HTTP check**: Yarn, Square,
Joule/Prism, Search, interim
LinkStack and interim Kuma.
Pi-hole and the old Yarn inner
name remain untested. Real Kuma
login, monitor history, notification
delivery and WebSockets still
unaccepted. Kuma, LinkStack
and Pi-hole apps and persistence
remain on Kvar, not migrated
to Kvin.

**Remove mistaken Kuma workaround:**
The source manifest no longer
declares `redirect_strip_upstream_port`
and the shared Nginx template no
longer emits the Kuma-only
`proxy_redirect`. This unnecessary
rule was synthetic-tested only
for an *absolute* Location, but
actual Kuma root redirects were
**relative**. The old stage will
still contain the rule until
the next approved native
reconciliation. The source CI
now tests preserved relative
Location behavior with a real
Nginx synthetic backend. The
checked-in manifest remains
Yarn-only.

**Next seventh route: interim Pi-hole
UI proxy compatibility.** Its
disabled source route targets
`pihole.nexus.sanctum` →
`http://kvar.outer.sanctum:82`,
the *current* Kvar Pi-hole UI,
not a restored app on Kvin.
Default-off `yxorp_stage_pihole_approved`
requires the six previously
authorized Kvin stage flags.
The stage checks the exact
seven-route selection before
the existing validated
service remount/restart;
old `yarn.inner.sanctum`
remains disabled. Kvar NPM
and wildcard DNS are production;
Maintenance owns Kvin LAN port80.

**Test both GET / and GET /admin/.**
Pi-hole's upstream root historically
returned HTTP404, which does not
mean its UI is down.
`ansible/yxorp-kvin-stage-pihole-probe.yml`
executes a Python `http.client`
raw-header observer through all
three paths from Kvin, no
redirect following, with five-second
per-request bounds. Its sanitized
output reports HTTP status
and content-type equality,
presence/kind of redirect
and exact **original raw wire**
Location equality. No actual
URL values, credentials,
bodies, query values or cookies
are printed. This does **not**
accept Pi-hole DNS blocking,
ad lists, persistent databases,
login or user clients, real
LAN access or cutover.

**Next native action on Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true -e yxorp_stage_pihole_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-pihole-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true -e yxorp_stage_pihole_approved=true
```

**Reply contract:** Two short `PLAY RECAP`
lines and the `msg` object from
`Report only Pi-hole root and admin
HTTP parity metadata` only. If
anything fails, paste just the
failed task/error. No complete
Ansible logs and no rerun of
Kuma or other earlier checks.
A clean nonfatal probe recap
alone does not accept Pi-hole;
evaluate explicit statuses and
wire header equality.

## Latest Kvin Kuma stage: explicit redirect fix did NOT achieve parity — November 10

The user has **already applied** the first narrowly
scoped Kuma-only `proxy_redirect` source change
using the usual six-route Kvin stage play and
rerun the three-path Kuma parity test:
- Stage: `ok=44 changed=3 failed=0 skipped=1`.
- Read-only comparison: `ok=4 changed=0 failed=0`.
- All three direct Kvar Kuma, incumbent
  Kvar NPM and Kvin stage routes returned
  **HTTP302**, with candidate/incumbent
  status, MIME, redirect scheme/path equal.
- **Full redirect equality still false**;
  candidate and incumbent redirect host
  still differ. Candidate port remains
  an explicit non-backend-port, while
  NPM redirect has no explicit port.

**Kuma still not accepted** despite passing
synthetic real-Nginx CI. The prior native
authority diagnosis identified candidate
`loopback:80` versus incumbent Kvar
host without an explicit port and direct
backend Kvar:3001; the post-fix source's
output did not re-classify the new host.
The original generated Kuma-specific
`proxy_redirect http://kvar.outer.sanctum:3001/ http://kvar.outer.sanctum/;`
is still source-controlled and stage
preflight requires it, but there
is insufficient evidence yet to
assert that the live raw HTTP
response is rewritten as intended.
**Do not blindly repeat deployment
or install a second speculative fix.**

The next source-managed **read-only**
`ansible/yxorp-kvin-stage-kuma-wire-observe.yml`
checks host-published and container-mounted
exact Nginx config (privately) and
reports only whether they match and whether
the expected Kuma-specific `proxy_redirect`
line is present and how many times.
It separately executes
`tools/observe-yxorp-kuma-wire.py`
from Kvin with exactly scoped
direct Kvar :3001, incumbent Kvar NPM :80,
and local Kvin stage :80 HTTP root
requests. It uses Python's
`http.client` to read the **raw
Location header** before any
Ansible URI-module transformation
and sends a fourth request directly
to Kuma with proxy-style forwarded
headers to test whether Kuma changes
its redirect under those inputs.
No unrecognized hostname, raw
redirect, query value, cookies,
app body, error strings, config
contents or credentials are printed.
No Nginx/service/host edits occur.

**Next Kvin command (single read-only play):**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-wire-observe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```

**Output contract:** Return only one
short `PLAY RECAP` and `msg`
from **“Report only Kuma wire classes and
mounted Nginx rule presence”**.
On failure only the failed task
and sanitized error.
Do **not** rerun the already failed
Kuma reconciliation, dump the raw
`Location` or whole Nginx config,
or paste long Ansible logs.

**Project accounting remains 6/8
attempted; only five initially
HTTP-accepted:** Yarn, Square,
Prism, Search and interim LinkStack.
Kuma blocked on parity, Pi-hole
and old Yarn inner route untested.
No Kvar, wildcard DNS, Kvin
Maintenance-owned firewall or
production cutover change. Kuma,
Pi-hole and LinkStack application
restore on Kvin is a later
independent migration gate.

## Kuma redirect root cause and source-only correction — November 10

**Native diagnostic complete; staged correction NOT yet applied.**
Nova's safe read-only Kuma authority classification completed
`ok=4 changed=0 failed=0`. All three anonymous Kuma root
requests returned HTTP302. The old backend returns Location
authority **Kvar:3001**; incumbent Kvar NPM emits **Kvar
without an explicit port**, while new Kvin YXORP stage
emits **loopback:80**. Candidate/incumbent redirect path,
query and fragment all match. This specifically identifies
Nginx's default upstream `proxy_redirect` translation of
the existing Kvar location into the loopback test request
authority. Kuma itself is still answering normally.

**Narrow source-managed fix:** Only the disabled Kuma entry
in `data/yxorp-routes.yml` now declares
`redirect_strip_upstream_port: true`.
The Nginx Jinja template uses this opt-in to emit
a specific `proxy_redirect` mapping from the
declared `http://kvar.outer.sanctum:3001/` to
`http://kvar.outer.sanctum/`.
It intentionally does **not** emit this for the
other seven routes, avoiding an unreviewed global
redirect policy. The exact Kuma Kvar backend and
selected policy are protected by the existing
Kvin stage play preflight. When Kuma's stateful
service migrates to Kvin, the route's backend
and redirect policy need independent review.
Current production manifest remains Yarn-only.

A **real Nginx synthetic HTTP test** now makes an
isolated local backend redirect to itself using
its explicit service port and asserts that the
Kuma-only policy emits the same backend host
with no explicit port and preserves URL path,
query and fragment. An unselected route keeps
its original default redirect behavior.
`tests/test_yxorp_kuma_redirect_policy.py`
checks the manifest and exact scope.
**[Source CI #42948962676 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/42948962676)**.
That is source/runtime synthetic validation, **not**
Kvin native parity proof.

**Next native Kvin action, retain all six previously
selected stage routes and recompare Kuma:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```
**Operator output contract:** Return only
the stage and comparison **one-line play recaps**
plus the `msg` dictionary from
**“Report only Kuma status and redirect authority
components”**. If a task fails, return only its
failed task and error. Do not paste full runs.
Require `candidate_redirect_equals_incumbent=true`,
candidate/incumbent status equal and content type
equal before accepting Kuma at the *initial
anonymous root HTTP* gate. Do not accept
WebSockets, sessions, monitors, app state restore,
DNS/failover or production cutover from this test.

**Current count remains 6/8 attempted, 5/8 accepted**
(Yarn, Square, Prism, Search and interim LinkStack).
Kuma is pending the native recheck;
Pi-hole and old `yarn.inner.sanctum`
remain untested through Kvin. Kvar NPM and
wildcard DNS remain production. LinkStack,
Kuma and Pi-hole apps still reside on Kvar;
Maintenance owns Kvin LAN firewall.

## Native Kuma result — redirect host and port mismatch; read-only follow-up (November 10)

**Kvin stage:** `ansible/yxorp-kvin-stage.yml`
with six separately approved stage route flags
completed `ok=44 changed=3 failed=0
skipped=1`, including configuration validation
and post-reconciliation mounted-config
equality. The subsequent read-only
`ansible/yxorp-kvin-stage-kuma-probe.yml`
completed `ok=4 changed=0 failed=0`.

The Kuma anonymous root GET yielded **HTTP302**
from direct Kvar Kuma `:3001`, incumbent Kvar
NPM `:80` and staged Kvin YXORP
`127.0.0.1:80`. Candidate/incumbent status
and MIME type match, and redirect path/scheme
match. **Full redirect parity FAILED**:
candidate and incumbent hostnames differ.
Candidate redirected with an **explicit
port other than backend 3001**, whereas
incumbent had **no explicit port**.
This is not enough to identify the
candidate host or port, and status302
alone does not qualify a browser route.

**Accounting:** 6/8 YXORP route names now
attempted on Kvin; five have passed
the scoped initial HTTP check (Yarn,
Square, Prism, Search, LinkStack).
Kuma is **pending correction/acceptance**;
Pi-hole and the legacy Yarn route are
untested. Kvar NPM and wildcard DNS still
serve production. LinkStack and Kuma
still run on Kvar, not migrated to Kvin.

**Next targeted read-only diagnosis:**
`ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml`.
Reissue just the three bounded Kuma
HTTP root requests from the same Kvin
observer and classify only their
redirect authority. It reports safe
hostname classes (frontend, Kvar,
Kvin, loopback, relative, absent,
other) and port classes (80, 3001,
none, other, absent). It compares
host, path, query, fragment and full
redirect equality with incumbent
but hides raw Location strings,
unexpected hostname values, query
contents, cookies, bodies, error
strings and credentials. All
network operations are read-only
and no route re-deployment happens.

**Next Kvin operator command:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-redirect-diagnose.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```
**Return only** one `PLAY RECAP`
line and the `msg` dictionary from
**“Report only Kuma redirect host classes
and explicit port classes”**. If a task
fails, send just that failed task and
error; do not paste full logs or
repeat earlier accepted route checks.
Keep Kvar, DNS, Maintenance firewalld
and production cutover closed.

## Current Kvin stage — LinkStack interim HTTP passed; Kuma sixth canary (November 10)

**Local anonymous Kvin HTTP stage progress: 5 of 8
routes tested, all five passed their scoped
first tests.** Yarn returned HTTP200 with
direct-origin body equality, Square/Nextcloud
HTTP302 with Kvar NPM's same redirect and
content type, Prism HTTP200 with status and
MIME equality, Search HTTP200 with status
and MIME equality, and **LinkStack**
`dir.nexus.sanctum` HTTP200 through
direct Kvar backend :8081, Kvar NPM :80
and Kvin stage `127.0.0.1:80`.
The native LinkStack sanitized report
had `all_three_have_http_response=true`
and candidate/direct/incumbent status
and candidate/incumbent MIME equality
all true; neither proxy redirected.
Probe recap `ok=4 changed=0 failed=0`.
No fifth-stage reconcile recap was
supplied, but its staged HTTP response
was observed. LinkStack still resides
on **Kvar**; this test did **not**
move its data or application to Kvin.

**Next scoped compatibility candidate:
Uptime Kuma `kuma.nexus.sanctum`.**
The checked-in route still targets the
**legacy Kvar backend `:3001`**.
`yxorp_stage_kuma_approved` defaults
false and can select only this sixth
host alongside the previously accepted
five, with all stage approval flags
explicitly true. Neither the production
manifest (Yarn-only) nor Kvar NPM,
wildcard DNS, host firewall or production
cutover are edited. The stage retains
safe Nginx validation, restart-on-drift
and post-start mounted-config equality.

Kuma's known anonymous GET / returns
**HTTP302** both directly and through
NPM, but the *direct backend* originally
included explicit port 3001 in its
absolute Location and incumbent NPM
removed it. For this reason,
`ansible/yxorp-kvin-stage-kuma-probe.yml`
checks three paths (direct Kvar :3001,
incumbent Kvar NPM :80 and candidate
Kvin stage :80), compares status and
content-type and reports conditional
redirect equality, redirect path,
hostname and scheme equality and
**port classes**, never raw URLs or
credentials. An unexpected mismatch
is a **diagnostic result**, not
automatic success or failure of
Kuma itself. Kuma's application restore,
monitors/history, login, notification
behavior and WebSockets are separate
migration gates, not proven here.

**Next exact command, on Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-kuma-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true -e yxorp_stage_kuma_approved=true
```

**Return only** two one-line
`PLAY RECAP` results and the
`msg` dictionary from **“Report only
Kuma status and redirect authority
components”**. For a failure instead
return the failed task and error.
No long Ansible logs; request accepted
tests only once. The report is
deliberately nonfatal and its
HTTP values determine routing
acceptance, not a clean play recap.

[Source CI #42923666179](https://github.com/wdcallahan/sanctum-services/actions/runs/42923666179)
**passed** the sixth-route contracts, real
Ansible staged source selection, synthetically
different/equal redirect-port cases,
syntax and Nginx checks. Native
Kuma stage has **not yet run**.

## Current Kvin stage — Search accepted; interim LinkStack next (November 10)

**Native initial local HTTP acceptance: 4/8
declared routes tested through Kvin, 4 passed.**
Yarn: HTTP200 with direct-origin body equality.
Square/Nextcloud: HTTP302 with Kvar NPM Location
and content-type equality. Joule/Prism: HTTP200
with direct/incumbent status and MIME equality.
Search: HTTP200 from direct Kvin :8083,
incumbent Kvar NPM and staged Kvin YXORP,
with equal candidate/incumbent MIME and status.
Native Search stage passed `ok=40 changed=3
failed=0 skipped=1`; read-only Search
comparison `ok=4 changed=0 failed=0`
reported all three HTTP200 and matching
metadata. Search query/results functionality
was not tested. No production DNS,
Kvar NPM, firewall or cutover change.

**Remaining four are NOT all ordinary proxy
migrations.** The current LinkStack
`dir.nexus.sanctum` backend is on Kvar
:8081; Kuma remains on Kvar :3001, Pi-hole
UI on Kvar :82. The estate's intended host
for those retained services is Kvin,
but their application data/config,
credentials, clients and restore
must be separately qualified. Passing
an interim route from Kvin's Nginx
back to Kvar does **not** qualify that
migration or authorize Kvar retirement.
The last name, `yarn.inner.sanctum`,
is a legacy alias whose Kvar NPM
upstream path previously timed out;
client review and retirement decision
are still outstanding.

**Next isolated Kvin stage-only compatibility
trial: LinkStack.** A new default-off
`yxorp_stage_dir_approved: false`
requires the four previously tested
Yarn+Square+Prism+Search route flags.
It checks the exact disabled legacy
`dir.nexus.sanctum` backend
`http://kvar.outer.sanctum:8081`
with no WebSockets, and projects **only
that fifth host** in memory. Production
manifest remains Yarn-only; the other
unaccepted legacy hosts remain disabled.
The existing validated restart-on-change
and bind-mount equality checks still
apply to the exact Kvin test stage.

`ansible/yxorp-kvin-stage-dir-probe.yml`
makes three independent bounded anonymous
GET / requests with the LinkStack
Host header from Kvin: direct Kvar
LinkStack :8081, Kvar NPM :80,
and local Kvin stage :80. It reports
only HTTP status/MIME and optional
redirect parity; raw URLs, cookies,
bodies and errors are suppressed.
It explicitly reports
`application_migrated_to_kvin:false`.

**Next command, from Kvin:**
```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-dir-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true -e yxorp_stage_dir_approved=true
```
**Operator output contract:** Return **only
two one-line play recaps** and the `msg`
dictionary from **“Report only LinkStack
HTTP status and compatibility metadata”**.
On a failure, share the failed task and
error. The probe deliberately uses
`failed_when:false`; its recap alone
cannot establish HTTP acceptance.
The stage remains installed and
Kvar production traffic unchanged.

## Current Kvin YXORP stage — Prism accepted, Search next (November 10)

**Native initial HTTP acceptance: 3 of 8 declared routes
tested on Kvin, 3 passed.** Yarn yielded HTTP200
and equal response bodies against the direct
backend; Square yielded HTTP302 with identical
Kvar NPM redirect and MIME type; Joule/Prism
yielded HTTP200 through direct Kvin :8084,
Kvar NPM, and Kvin stage, with equal
status and content type. Its native stage
reconciliation finished `ok=38 changed=3
failed=0` and anonymous comparison
`ok=4 changed=0 failed=0`, including
`all_three_have_http_response=true`.
**Prism WebSockets/streaming/chat sessions
remain untested**; Nextcloud Calendar,
browser authentication and remote client
acceptance are also separate milestones.

**Fourth local candidate: Search.** The
stage-only `yxorp_stage_search_approved`
flag defaults false. With all previous
Kvin-stage Square and Prism opt-ins,
the existing stage play validates
the exact baseline manifest and
adds **only**
`search.nexus.sanctum` →
`http://kvin.outer.sanctum:8083`
as a fourth selected virtual host.
No checked-in production route is
enabled; all other legacy routes
remain disabled. Kvar NPM still
serves production and DNS, and
Kvin firewall remains
Maintenance-owned.

`ansible/yxorp-kvin-stage-search-probe.yml`
performs three independent anonymous
GET / requests under the Search Host
from Kvin to direct backend :8083,
Kvar incumbent NPM :80 and new
Kvin local stage :80. Each has an
eight-second bound, `no_log`,
nonfatal failure classification, and
no redirect following or system proxy.
Report contains only status/MIME
and conditional redirect equality,
not URL values, HTML, searches,
credentials or error strings.
This will not test actual search
queries or engine results.

**Next exact command on Kvin:**

```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-search-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true -e yxorp_stage_search_approved=true
```

**Output contract:** Return only
the two one-line `PLAY RECAP`
results and the `msg` dictionary
from **“Report only Search HTTP status
and anonymous metadata parity”**.
If failed, provide the failed task
and its error instead. Complete
Ansible logs waste context and
are not needed for a passing run.
As with prior checks, a nonfatal
probe `failed=0` alone does not
prove HTTP parity.

Source CI can be checked in the
latest GitHub Actions YXORP workflow.
No actual Search stage run has
happened yet. Production cutover,
DNS, Kvar NPM, Maintenance-owned
Kvin HTTP80 rules and standby
failover are unchanged.

## Current Kvin stage — November 10: Yarn and Square passed; next Prism HTTP canary

**Native local HTTP route progress:** **2 of 8 routes tested
through new Kvin YXORP; 2 passed initial HTTP
acceptance**. Yarn's stage proxy returned HTTP200
with response-body equality against direct
origin. Square/Nextcloud's new staged proxy
returned **HTTP302** with incumbent Kvar NPM's
**same full redirect Location and content type**;
direct backend also returned HTTP302. The
stale single-file Podman mount was corrected
by the drift-aware shared role: native stage
reconciliation passed `ok=36 changed=1 failed=0`
and subsequent Square comparison report
had all three HTTP and equality booleans true.
This does NOT establish real browser
sessions, Nextcloud Calendar/WebDAV,
remote LAN client behavior or WebSockets.

**Next route: Joule/Prism.** Only the
**Kvin stage** can select it with the
new default-off `yxorp_stage_prism_approved`
flag, alongside the already approved
Square opt-in. The stage play first
validates that the exact baseline
`data/yxorp-routes.yml` contains Yarn
enabled and all seven legacy entries
disabled. It then projects only
Yarn+Square, checks that the intended
Prism `joule.nexus.sanctum` target
remains `http://kvin.outer.sanctum:8084`
with `websocket: true`, and enables
**only Prism as a third stage virtual
host**. The checked-in manifest remains
Yarn-only and production cutover
approval remains false. The shared
role validates candidate Nginx syntax,
reconciles only the previously approved
Kvin stage service with config drift
detection and a content match assertion.

**Next native action on Kvin**, with
the original stage authorization and
independent Square/Prism stage opt-ins:

```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-prism-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true -e yxorp_stage_prism_approved=true
```

The second play performs **three independent
nonfatal anonymous GET /**
requests with `Host: joule.nexus.sanctum`
from the Kvin observer to direct
Prism `kvin:8084`, incumbent
Kvar NPM `kvar:80`, and Kvin's
new stage `127.0.0.1:80`. Redirects
are not followed, proxy bypassed,
raw HTTP responses and errors are
hidden. **Report status/MIME and
redirect equality only**. This
may qualify anonymous root HTTP routing
but not Prism sessions, WebSocket
upgrades or chat/streaming behavior.

**Operator output contract:** To save
conversation context, report just the
**two one-line play recaps** and the
`msg` dictionary of
**“Report only Prism HTTP status and
response equivalence metadata”**.
Do NOT paste full Ansible runs
unless asked for a failed task.
The deliberately nonfatal GET tasks
mean a play's `failed=0` does
not automatically qualify the route.

Kvar NPM remains production, wildcard
DNS is unchanged, Maintenance owns
Kvin's future LAN HTTP80 firewall policy
and permanent Peanut standby remains
uncommissioned. Source CI:
[Prism canary checks #42917417401](https://github.com/wdcallahan/sanctum-services/actions/runs/42917417401)
**PASSED** including real-Ansible synthetic
stage projection and report evaluation;
native Prism trial has not run yet.

## Current native result — November 10: Square's stale bind mount found; source repair awaiting Kvin

**Route acceptance:** Of eight declared YXORP routes,
**two have been tested through the new Kvin HTTP80 stage**:
**Yarn passed** (HTTP200 and matching direct-origin
bodies); **Square/Nextcloud did not yet pass**
(direct backend and Kvar NPM HTTP302, but Kvin stage
no HTTP response). The remaining six routes have
not been qualified through the new Kvin proxy.
The checked-in manifest remains Yarn-only,
Kvar NPM and wildcard DNS remain production,
and Maintenance still owns the separate Kvin
LAN HTTP80 firewall admission.

**Confirmed diagnosis:** The read-only native
`ansible/yxorp-kvin-stage-mounted-config-observe.yml`
returned `ok=8 changed=0 failed=0`.
The host's published config **equaled its
validated candidate**, both contained the
Square virtual host. The running rootful
Podman container's mounted `/etc/nginx/nginx.conf`
was readable, contained Yarn but **not Square**,
and **differed from the host's active file**.
`curl` with the Square Host and with a deliberately
unmatched Host each returned exit52/HTTP000.
Thus the problem is an **outdated single-file bind
mount**, not Nginx's parser or a broken Nextcloud
backend. The prior role atomically replaced the
host's config and issued `nginx -s reload`, which
could still see the old inode.

**Durable repair, source-qualified:** The
shared YXORP role validates generated
Nginx syntax **before** publishing.
It now compares the host's published
config with the file visible inside
the existing Podman container prior
to systemd reconciliation. A **stale
single-file mount forces an exact
owned-service restart even if no
Ansible host-file change is reported**
(the current native Kvin situation).
A config or Quadlet change also
restarts that unit. If the mounted
config already matches and source is
unchanged, the role remains idempotent.
No old Nginx-only reload is used.
A second **post-restart SHA256 equality
check** verifies the container
actually reads the published config;
a mismatch fails deployment before
local health can be accepted, without
logging the contents.

**[GitHub Actions #42911815868 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/42911815868)**:
Ansible source contracts, six real-
Ansible synthetic cases including
host-unchanged/mount-stale drift and
already aligned state, playbook syntax,
Nginx parse and synthetic HTTP behavior.
No live Kvin remediation has run yet.

**Next native operator step, from Kvin's existing
Services checkout**, with already-granted stage
authorization and the separately enabled Square
canary for this test-stage invocation:

```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-square-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true
```

The first play will validate/publish, restart **only
`sanctum-yxorp-kvin-stage.service`** if the
configuration changes, verify mounted content
equals published content, and check local health.
The next play independently queries anonymous
Nextcloud root through direct backend, incumbent
Kvar NPM and Kvin staged virtual host; nonfatal
probe responses report only safe status/redirect
comparison booleans. HTTP302 parity would accept
**anonymous root routing only**, not login,
Calendar, WebDAV, WebSocket, other applications
or client LAN access. Do not run the production
YXORP play, reopen the old Yarn investigation
or change NPM, DNS, Kvin firewall or routings.
Leave the test stage installed afterward.

**Current verified state, November 10, 2026:** Kvar's
**Nginx Proxy Manager** is still the live production proxy
for wildcard `*.nexus.sanctum` names, and neither
DNS nor Maintenance-owned Kvin HTTP80 firewall has
changed. A separate **rootful host-network Nginx
stage is installed on Kvin's real port80**, as
`sanctum-yxorp-kvin-stage.service`. Its local
health and Yarn forwarding/content equality
are natively accepted. The temporary Peanut
rootful Nginx trial passed previously and
was removed; it is not the standby yet.

**Latest native Square result:** With only
Yarn and Square enabled on Kvin's stage in
memory (the production manifest stays Yarn-only),
Ansible `ansible/yxorp-kvin-stage.yml`
finished `ok=31 changed=3 failed=0`: host
config published and Nginx reloaded, health
passed. The follow-up read-only Square
comparison returned direct Nextcloud
`kvin:8085` HTTP302, Kvar NPM HTTP302,
but **new staged Nginx `127.0.0.1:80`
no HTTP response (`status=-1`)**.
The comparison's `failed=0` recap is
expected from `failed_when:false`; it
**does not accept Square**. All other
legacy candidate routes remain disabled,
and production cutover is unapproved.

### Current next test: why Square has no HTTP response

**Specific unconfirmed source hypothesis:**
The role mounts a **single** Nginx config file
into the running Podman container and publishes
updated host configs using Ansible
`copy remote_src:true` (normally atomic file
replacement). Its config-only path executes
`podman exec ... nginx -s reload`, not a
container restart. Linux bind mounts can
stay attached to an **old inode** after
atomic host-file replacement, leaving
the container using the prior Yarn-only
configuration even though the host file
contains Square. Nginx then could treat
Square as unmatched and issue its
intentional default `return 444`, which
closes the connection with **no HTTP
response**. This is a testable hypothesis,
**not yet an established cause**.

The **read-only bounded** play
[`ansible/yxorp-kvin-stage-mounted-config-observe.yml`](../../ansible/yxorp-kvin-stage-mounted-config-observe.yml)
compares host active/candidate config to
the exact file visible **inside** the
running rootful Kvin container and probes
the Square/unknown-host response using
curl without exposing raw configs,
headers, cookies, URLs, errors or content.
It only reports equality/presence booleans
and numeric curl results. **No restart,
reconciliation, network or firewall writes.**
Its real-Ansible synthetic stale-and-aligned
report test and playbook checks passed
[CI #42909408599](https://github.com/wdcallahan/sanctum-services/actions/runs/42909408599).

**Next command, from Kvin's existing checkout**:

```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-mounted-config-observe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true
```

Share the sanitized message and recap. Leave
Kvin's stage and Kvar NPM running; do not
rerun already accepted Yarn tests or
speculatively change role, firewall,
DNS or proxy port before inspecting actual
mount evidence. After the result, correct
the durable source-managed lifecycle if
staleness is verified, and then requalify
the Square route separately. This does
not grant production cutover authorization.

## Same service architecture in trial and production

| | Peanut trial | Kvin after cutover |
| --- | --- | --- |
| Scope | `yxorp_test` | `yxorp` |
| Container | Rootful Podman Quadlet, host network | Rootful Podman Quadlet, host network |
| Listener | `0.0.0.0:80` | `0.0.0.0:80` |
| HTTP | Plain internal HTTP | Plain internal HTTP |
| Image input | `docker.io/library/nginx:stable-alpine` | ARM64 qualified image digest, until update policy promoted |
| Service name | `sanctum-yxorp-peanut-test.service` | `sanctum-yxorp.service` |
| Existing traffic | Unchanged; test via Peanut hostname + Host header | Separate reviewed DNS cutover required |

There is **no localhost-only or high-port workaround**. The trial really
binds TCP/80 on Peanut. Nova explicitly approved an **ad hoc runtime-only**
firewall exception for this test after the native preflight observed
firewalld running in `public`, no listener on 80, and both service/port
admission disabled. The trial adds only `80/tcp` in zone `public`, with
a **four-hour expiration**; the permanent Maintenance-owned firewall
configuration is unchanged. The test-removal playbook takes down that
exception and checks the result. Firewall reload, daemon restart or reboot
also discards the temporary runtime permission. Test and production
target groups are separate, so running the Peanut playbook cannot target
Kvin.

The checked-in route list [`data/yxorp-routes.yml`](../../data/yxorp-routes.yml)
currently enables only the newly proposed
`yarn.nexus.sanctum` → `http://yarn.inner.sanctum:80` route.
The other observed NPM routes remain declared but disabled until their
applications and consumer behavior are accepted. The NPM administrative
UI itself is retired rather than reproduced.

## Historical completed trial: Kvin controller, Peanut target (do not rerun)

From `~/src/sanctum-services` on Kvin:

```bash
git pull
~/.local/bin/ansible-navigator run ansible/yxorp-peanut.yml
```

The **first imported play** is
`ansible/yxorp-peanut-trial-firewall.yml`: it verifies the exact Peanut
identity, checks port ownership and current firewalld zone, records a
root-only cleanup marker in `/run`, and adds a **runtime-only**
`public` zone TCP/80 exception using `--timeout=4h` **only if not
already admitted**. Nothing is added to the permanent firewall policy.
The original **read-only preflight** runs next and must confirm that
Peanut is ready, followed by the ordinary rootful deployment role.
A wrong zone, listener or unexpectedly changed marker aborts the
operation without relaxing the firewall. If preflight or deployment
fails after the exception was opened, run the bounded remover below;
the temporary rule also expires independently.

Once the preflight passes, the ordinary Services YXORP role:

1. validates the selected host and route inputs,
2. renders the version-controlled Nginx configuration,
3. checks/pulls the selected container image and validates the candidate
   using Nginx in a disposable Podman **host-network** container,
4. installs only the trial's own Nginx configuration and system Quadlet,
5. starts its generated systemd service and checks the local health path.

Quadlet's `[Install] WantedBy=multi-user.target` manages boot startup;
the transient generated service must not be explicitly enabled via
`systemctl enable`. No NPM, DNS, Kvar, Kvin service or host firewall
is modified by the trial installer.

**Actual network-client smoke**, from Kvin:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-probe.yml
```

This queries `http://peanut.arcane.sanctum/__yxorp_health` and the
Yarn route through Peanut over HTTP/80 using
`Host: yarn.nexus.sanctum`. It runs on Kvin as a *different host*, not
inside the Nginx container. A successful probe confirms bounded HTTP
routing from that vantage point, **not** complete app/browser acceptance.
Once available, test with a real browser/client from the intended segments
before claiming availability to everyone. The original DNS entry still
points to Kvar; direct client testing should send the desired Host header
or use a temporary per-request URL-to-address override, not reconfigure
authoritative DNS.

## Native failure, November 9 — DNS in the Podman bridge

Nova's updated `ansible/yxorp-peanut.yml` run crossed the temporary
runtime-only firewall gate and read-only preflight, created the
Peanut-specific configuration directory and rendered the candidate,
and retrieved the maintained `nginx:stable-alpine` image. It **stopped
at Nginx parser validation** before installing any system Quadlet or
starting a persistent listener.

Exact error:

```text
[emerg] host not found in upstream "yarn.inner.sanctum"
nginx: configuration file /etc/nginx/nginx.conf test failed
```

The candidate container used Podman's regular `bridge` networking.
Follow-up native observation proved **Peanut's host resolves**
`yarn.inner.sanctum` to `192.168.1.110`, while the default
bridge and explicit bridge-to-Peanut DNS requests returned `REFUSED`.
Explicit DNS to Kvin timed out; it is not a demonstrated fallback.
Maintenance's authoritative BIND template applies the same
`sanctum_clients` ACL to `allow-query`, `allow-recursion` and
`allow-query-cache`, and its declared list admits only
`127.0.0.0/8` and `192.168.0.0/16`. The precise bridge source
address was not observed, but the result strongly suggests an
unadmitted Podman bridge source.

**Chosen engineering change:** both twin proxies now use
`Network=host` and a disposable `podman run --network host`
for syntax validation. This preserves ordinary rootful
`0.0.0.0:80` behavior, lets Nginx use the proven host DNS path,
and avoids changing/restarting the authoritative BIND server solely
for this one trial. Host networking **does** remove the container's
network-namespace isolation, a real but bounded tradeoff for a
rootful LAN proxy that needs host-wide port 80 and outbound network
access. Reconsider if a concrete risk or another service needs
bridge isolation. Do not claim the changed path passes natively
until the normal deployment and independent client probe succeed.

The DNS comparison finished with `ok=8 changed=0 failed=0`;
no further repeat is requested. The next native test is the
**changed** host-network deployment play, using the ordinary
`ansible/yxorp-peanut.yml` entry above. Its initial admission task
will check/reapply only the time-limited runtime firewall exception
if needed; the original preflight remains intact. If a new failure
occurs, preserve its exact result rather than bypassing Nginx's parser.
The previous temporary permission expires four hours after addition
unless removed by `ansible/yxorp-peanut-remove.yml`.

## Read-only status after the temporary HTTP exception expires

The Peanut Nginx trial can stay running locally after firewalld's four-hour
runtime HTTP/80 exception expires. This is expected and is **not** evidence
that Nginx or its upstream has failed. The temporary permission was granted
on the original addition, not reset by a successful rerun.

From Kvin's `~/src/sanctum-services` checkout, use the source-owned
read-only status check:

```bash
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-status.yml
```

This observes the actual Peanut rootful systemd unit, port-80 listener,
Quadlet and Nginx configuration presence, local health, active firewalld
LAN zone, runtime `80/tcp` and `http` admissions, and trial ownership
marker. A second play checks the same health URL **from Kvin** as a
different-subnet network client. Both HTTP requests have five-second
timeouts; connectivity failure is reported rather than treated as a
deployment command. The marker may remain after a time-limited rule
expires; its presence is not proof that access is still admitted.

This check never opens or renews a firewall port, starts or stops a
service, commits DNS, rerenders configuration, or changes Kvar NPM. The
Peanut stage can be retired via the explicitly approved scoped removal
below. A later test requiring a renewed temporary HTTP opening must
use the existing approved trial admission/deployment procedure, not an
untracked manual firewalld mutation.

The Mace-to-Peanut client-path failure was isolated to Bunny Inner's
IPv4 forwarding policy by an A/B/A firewall-rule experiment, with the
permanent fix tracked in
[Sanctum Maintenance issue #36](https://github.com/wdcallahan/sanctum-maintenance/issues/36).
The already accepted Kvin-origin Yarn HTTP 200 remains valid. Retest Mace
only after router policy reconciliation; no extra Mace static route is
appropriate.

## Compare actual Yarn content from one client

A cross-host HTTP 200 alone proves only that some backend responded. After
Peanut's already authorized four-hour test admission is re-established, run
the read-only `ansible/yxorp-peanut-yarn-content.yml` on the existing
Kvin controller. It makes two anonymous GET requests from **the same
client**, with the exact same `Host: yarn.nexus.sanctum` header:
one directly to `http://yarn.inner.sanctum/`, and one through
`http://peanut.arcane.sanctum/`. No hostname, DNS, firewall or application
configuration is changed. Both responses are collected under `no_log`;
the report contains only HTTP status, MIME type, body length and
whether the returned bytes are equal, **not** page bodies or login cookies.

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-yarn-content.yml
```

Matching HTTP status, content type and body provide stronger evidence
that the new proxy delivers the intended Yarn application than the prior
simple HTTP 200. Non-identical dynamic content (including CSRF, cookies,
timestamps and absolute URLs) is not by itself proof of bad routing:
the comparison reports these observations rather than asserting byte
identity unconditionally. No application credentials are supplied,
and WebSocket/browser/session acceptance remains separate.

If the prior read-only status report shows that Peanut's firewall HTTP
test rule has expired, the existing trial procedure can re-apply
the already authorized **four-hour runtime-only** permission by rerunning
`ansible/yxorp-peanut.yml`. The role reconciles the existing Quadlet
and validated configuration; it must not be treated as a production
cutover or lasting standby permission. When this bounded trial
finishes, use the reviewed removal procedure below to retire it.

## Kvin production readiness without changing Kvar

Yarn's real response through Peanut is now independently content-accepted:
on November 10 Nova's Kvin origin/Peanut comparison returned HTTP 200,
`text/html`, and **349 identical response bytes** on each side. The
second application of the Peanut trial role made no Nginx/Quadlet changes;
it renewed only the approved expiring firewall exception. This does
not authorize production cutover or enable the other routes.

The next *separate* production-host prerequisite can be checked safely
while Kvar continues serving the existing proxy. On Kvin, run:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-readiness.yml
```

The play observes Kvin's current TCP/80 listeners and owner metadata,
whether its production YXORP service or Quadlet already exists,
whether the previously native-qualified Nginx ARM64 image digest is
in the **rootful** image store, and the active/permanent firewalld
admission for HTTP on `eth0`'s zone. It collects facts only: no
`podman pull`, installation, file edit, Quadlet creation, start,
firewall change, service publication or DNS mutation. A missing port-80
allowance or occupied port is a finding for the corresponding owner,
not permission to take over the listener or open policy automatically.

The **current Peanut trial** remains distinct from the intended
persistent Peanut standby. Once the authorized Yarn trial concludes,
the scoped removal below retires its temporary service/port allowance.
Permanent twin/standby publication, route and client tests, and
production cutover still require their own reviewed deployment and
recovery controls.

## Kvin actual readiness and direct backend discovery — November 10

The native read-only Kvin production inspection passed with
`ok=13 changed=0 failed=0`. It found no existing TCP/80 listener,
YXORP service or Quadlet, and the exact ARM64-qualified rootful Nginx
image was already cached. Firewalld was running with `eth0` in
`public`, but **neither runtime nor permanent HTTP service/80-tcp
admission existed**. Kvin was not modified and
`yxorp_production_cutover_approved` remains false.

This absence is an **owner prerequisite**, not an invitation for
Services to add a competing firewalld task. Maintenance already owns
Kvin's ordinary published-service port policy; the requirements for
TCP/80 have been handed off to its [work board #20](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-6775538017).
Review and apply it only when Nova approves a concrete Kvin HTTP/80
deployment. Do not open unsolicited /32 ACLs, stage on 18080, change
Kvar, or redirect wildcard DNS to a configuration containing only
Yarn while other accepted service names remain disabled.

**We can qualify backend prerequisites before any Kvin proxy deployment.**
The source-controlled read-only
`ansible/yxorp-upstreams-observe.yml` sends anonymous GET requests
from Kvin to **each** declared backend, with its proposed frontend
`Host` header. It uses no credentials and doesn't follow redirects,
sends no request through Kvar's NPM or YXORP, has a 6-second bound per
request, and suppresses raw request/response details in logs. The
report shows only hostname, target/port, desired enabled state and
HTTP response status. Authentication responses (401/403) can indicate
a healthy backend; `-1` is an observation to diagnose, not proof
that an application should be retired.

From Kvin:
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-upstreams-observe.yml
```

This does not enable any route, install a service, open a firewall port
or alter DNS. It cannot prove login/WebSocket behavior or source
equivalence; its purpose is to identify actual app/backend blockers
before designing a safe real-port Kvin acceptance sequence.

The previously authorized Peanut-only Yarn trial cleanup succeeded
`ok=26 changed=5 failed=0`. Do **not** rerun that removal or
reopen Peanut as a prerequisite to observing backend availability.

## Incumbent Kvar NPM behavior parity before enabling replacement routes — November 10

Nova's native read-only `ansible/yxorp-upstreams-observe.yml`
successfully received an anonymous HTTP response from **all eight**
declared backend URLs on Kvin, with `changed=0 failed=0`.

| Desired route | Anonymous direct backend GET / |
| --- | --- |
| `yarn.nexus.sanctum` | 200 |
| `square.nexus.sanctum` | 302 |
| `joule.nexus.sanctum` | 200 |
| `search.nexus.sanctum` | 200 |
| `dir.nexus.sanctum` | 200 |
| `kuma.nexus.sanctum` | 302 |
| `pihole.nexus.sanctum` | 404 |
| `yarn.inner.sanctum` | 200 |

An HTTP response proves a listener answered, not that the application
route is correct. **Do not call Pi-hole down because GET / returned
404.** Kuma and Nextcloud returning 302 may be normal redirects.
LinkStack, Kuma and Pi-hole are still hosted on Kvar in the proposed
backend inventory; reachability alone does not move them to Kvin.

Next read-only migration check:
```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-incumbent-parity.yml
```

This queries the seven **existing** NPM application names through
`kvar.outer.sanctum:80`, using each name's Host header, and
independently requests the corresponding direct origin from Kvin.
The new `yarn.nexus.sanctum` name is intentionally excluded because
it never belonged to the incumbent NPM. Both HTTP requests are
anonymous, stop before redirects, have six-second timeouts, and
suppress unredacted response details with `no_log`.

The visible report contains **only** HTTP statuses, whether redirect
headers are present and whether their unprinted values match. It also
compares `/admin/` on Pi-hole's declared upstream
`kvar.outer.sanctum:82` with `/admin/` via the old Kvar NPM
proxy, so its root-path 404 can be interpreted in context. Status
parity is not the same as application authentication, cookies, static
assets, content or WebSocket parity. Unexpected results should drive
a narrowly scoped app-specific follow-up, **not** blind activation of
all routes.

Kvin still lacks Maintenance-owned runtime and permanent HTTP/80
admission. Do not deploy the production service or change wildcard DNS
until the owner corrects that precondition and the actual client
migration requirements are qualified. No assumption of a new
unapproved private HTTPS initiative, alternate 18080 listener or
client-specific route workaround is needed.

## Narrow diagnosis of incumbent redirect differences — November 10

Nova ran the source-owned `ansible/yxorp-incumbent-parity.yml`
from Kvin. All seven legacy route comparisons completed without
configuration changes (`ok=8 changed=0 failed=0`). Actual incumbent
HTTP/80 and direct-backend results:

| Legacy frontend | Backend status | NPM status | Redirect value comparison |
| --- | ---: | ---: | --- |
| `square.nexus.sanctum` | 302 | 302 | Equal |
| `joule.nexus.sanctum` | 200 | 200 | Neither redirected |
| `search.nexus.sanctum` | 200 | 200 | Neither redirected |
| `dir.nexus.sanctum` | 200 | 200 | Neither redirected |
| `kuma.nexus.sanctum` | 302 | 302 | Different |
| `pihole.nexus.sanctum` | 404 | 404 | Neither redirected at / |
| `yarn.inner.sanctum` | 200 | -1 | NPM returned no HTTP status |

An additional Pi-hole **/admin/** GET returned 302 from both its
declared backend and NPM, but the redirect values differed. This
is **not** proof that Pi-hole or Kuma is broken: absolute/relative
redirects and proxy origin rewrites are plausible. The legacy Yarn
`-1` does not identify whether Kvar NPM deliberately closed the
connection, timed out, or suffered another transport error. No
sensitive HTTP responses or raw Location values were logged.

A smaller, read-only follow-up is therefore available:

```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-discrepancies-observe.yml
```

It checks **only** the Kuma root redirect and Pi-hole /admin/
redirect from Kvin, direct and through incumbent Kvar NPM. It
reports redirect *shapes* (relative/absolute, scheme,
frontend/backend/other host classification), and whether path and
query components match, without exposing raw Location, body or
cookie values. One bounded curl request to the old Yarn NPM route
returns only a sanitized exit-code category such as
`empty_reply`, `timeout` or `receive_failure`.
The checked-in synthetic fixture exercises the actual Ansible
`urlsplit` filter, rather than relying only on syntax checking.

These are migration observations only. Do not copy NPM's different
redirect merely because it is different, enable unqualified routes,
modify the host HTTP/80 policy or treat a browser session as accepted
from anonymous root-page status alone.

## Inspect redirect ports and old Yarn from Kvar's NPM namespace — November 10

Nova's follow-up `ansible/yxorp-discrepancies-observe.yml` passed
`kvin.outer.sanctum ok=7 changed=0 failed=0`. With the direct
backend and Kvar NPM requests using the same Host header:

- **Kuma `/`** and **Pi-hole `/admin/`** each returned 302 on
  both paths. Both Location values were absolute HTTP URLs, both
  identified the **declared backend hostname**, and path and query
  components were equal. The full redirect values still differed.
  That narrows the question to an authority/port, fragment or
  other URL-component difference; do not claim a broken application
  or invent a redirect rewrite from the current evidence.
- **Legacy `yarn.inner.sanctum`** through Kvar NPM timed out:
  curl exit **28**, HTTP **000**, rather than a deliberately empty
  reply (52). The declared backend itself answered 200 from Kvin.
  These are different network paths; do not infer that Kvar NPM
  reached Yarn's backend.

The next read-only boundary is:

```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-npm-path-diagnose.yml
```

The first play, on **Kvin**, classifies only the port/authority and
fragment components of Kuma/Pi-hole redirects. It never displays
raw Location URLs, query contents, unexpected hostnames or cookies.
The second play uses **Kvar's existing SSH10022 inventory path**
and established rootful NPM container name to request old Yarn's
upstream from (1) the Kvar host and (2) the NPM container network
namespace, using the container's own Node HTTP runtime. It prints
only HTTP status and a safe timeout/connect/receive/unknown
category; if Node or the container isn't accessible, that branch
is reported **not observed** rather than wrongly assumed down.
All probes are bounded by six seconds and do not edit the
container, host firewall, DNS, routes or application state.

Host reachable but container unreachable suggests an NPM
container/bridge routing or filtering problem; both reachable but
the public NPM route still timing out narrows attention to NPM's
reverse-proxy configuration or its interaction with the upstream.
Neither outcome justifies adding client-side static routes,
changing Bunny policy here, modifying NPM, or commissioning
Kvin before the separately controlled port-80 application.

## Confirm Kvar routing to legacy Yarn without changing either host — November 10

Nova ran `ansible/yxorp-npm-path-diagnose.yml` from Kvin.
Both plays passed with no changes (`Kvin ok=4`, `Kvar ok=5`).
Kuma `/` and Pi-hole `/admin/` gave HTTP302 both directly and
through Kvar NPM, using absolute HTTP redirects to the **same declared
backend hostname** with matching path, query, fragment and userinfo.
The only detected difference was their explicit authority port:
direct URLs included the backend port (3001 or 82); incumbent
NPM stripped it. This is a legacy proxy rewrite/normalization
difference, **not** a demonstrated application fault.

The former `yarn.inner.sanctum` NPM route still timed out from Kvin.
More importantly, the **Kvar host's own GET** to Yarn
`192.168.1.110:80` yielded **no HTTP status**, and a GET made
inside Kvar's existing rootful NPM container also returned
`timeout` with no HTTP status. Kvin's own prior direct GET to
that backend succeeded (200). **Do not blame NPM's proxy-host config
yet**: the shared failure involves Kvar's path to Yarn.

The next bounded route-selection test **has now been run and accepted**
on November 10. Nova executed
`ansible/yxorp-yarn-route-observe.yml` from Kvin, with
`ok=5 changed=0 unreachable=0 failed=0` on **each** Kvin and Kvar.
All four kernel route lookups returned successfully.

| Observer | Selected route to Yarn `192.168.1.110` | Selected route to control `192.168.3.3` |
| --- | --- | --- |
| Kvin | `eth0`, source `192.168.0.192`, via `192.168.0.1` | `eth0`, source `192.168.0.192`, via `192.168.0.1` |
| Kvar | `end0`, source `192.168.0.7`, via `192.168.0.1` | `end0`, source `192.168.0.7`, via `192.168.0.1` |

There is no observed divergent next-hop choice or missing selected
IPv4 route: both hosts use the same gateway for both destinations.
Different interface names and source addresses are expected on
different machines. The contrasting HTTP behavior remains real but
unexplained. Route lookup is **not** a packet capture, firewall
decision, TCP handshake or return-path test. Source-specific forwarding,
filtering or return-path differences remain possibilities, not findings.

**Disposition:** Defer any further probes of Kvar's obsolete NPM
`yarn.inner.sanctum` transport unless a currently required consumer
or replacement acceptance depends on it. Do **not** silently delete
the old hostname from the route inventory; separately review its
consumers and accept eventual retirement. Do not infer a connection
to Maintenance #36's independently proven Mace-to-Arcane fault.
No host routes, firewall rules, DNS records, incumbent proxy settings
or applications were changed during this examination.

**Proceed on the actual migration path:** Review a safely isolated,
real-`0.0.0.0:80` YXORP stage for Kvin without changing existing
Kvar NPM or the wildcard DNS. The approved design is rootful Nginx
on host networking with declarative route data. The last native
Kvin readiness inspection found HTTP/80 **not admitted** in both
runtime and permanent firewalld `eth0/public`; Maintenance
work board #20 holds the Thursday Nov 12 owner review and future
explicit approval. No Services-side firewall workaround, production
deployment, DNS cutover or Peanut standby commissioning is authorized
by these observations. Later client acceptance must cover actual
Nextcloud, Prism/WebSockets and other intended routes rather than
only anonymous HTTP status parity.


## Current Kvin YXORP stage and accepted local Yarn — November 10

**Native accepted installation:** Nova ran
`ansible/yxorp-kvin-stage.yml` from Kvin successfully,
`ok=22 changed=5 unreachable=0 failed=0 skipped=8`.
The independent rootful host-network
`sanctum-yxorp-kvin-stage.service` is now installed on
**Kvin's actual `0.0.0.0:80`**. The accepted
read-only four-target diagnostic later returned
`ok=6 changed=0 failed=0`: active stage unit, local health
HTTP200 with `yxorp-ready`, and HTTP200 for all three
Yarn paths (through local staged proxy, direct Yarn hostname,
direct literal `192.168.1.110`). Both direct-response
body comparisons were **equal** to the staged proxy
response; Kvin resolved Yarn to a single IPv4 address
including `192.168.1.110`.

The first sequential acceptance play had earlier
timed out at the *direct Yarn origin* before testing
staged forwarding. That timeout did **not** recur
on the independent four-way test and has no established
cause. **Local Yarn forwarding is accepted**; do
not rerun previously accepted checks merely to
repeat them. Historical detail and commands remain
in [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2).

**Authority preserved:** Kvar Nginx Proxy Manager
still serves all real `*.nexus.sanctum` traffic;
wildcard DNS and host firewall were not modified.
The source-only candidate manifest
[`data/yxorp-routes.yml`](../../data/yxorp-routes.yml)
continues to enable **only new Yarn**, with the
other seven entries disabled. The Kvin stage and
production service are separate Quadlets and
configuration trees; the production cutover gate
remains false. The already completed Peanut
rootful HTTP80 test was removed.

## Next local service: optional Square / Nextcloud stage-only trial

**Source prepared; native Square trial not yet run.**
Nextcloud Calendar has previously been accepted on
Kvin in its *existing application path*, not
through Kvin's new YXORP stage. The incumbent
Kvar NPM `square.nexus.sanctum` anonymous root
response had matched the direct Kvin :8085
backend (HTTP302 and identical redirect) in
the earlier parity test; real browser, authentication
and WebDAV/Calendar behavior through YXORP
are **not** established.

For the next controlled stage-only test,
`ansible/vars/yxorp-kvin-stage.yml` declares
`yxorp_stage_square_approved: false`.
With that *separate explicit opt-in* supplied,
`ansible/yxorp-kvin-stage.yml` verifies the
**exact existing eight-route manifest**: Yarn
enabled, Square disabled, all other routes
disabled, and Square targeting only
`kvin.outer.sanctum:8085` over HTTP with
WebSocket support. It then enables **only
Square alongside Yarn for this one stage run**
using an Ansible in-memory `set_fact`,
before the existing YXORP role renders and
tests Nginx's candidate. **No change is made
to the committed production route manifest**.
Subsequently re-running the ordinary
Yarn-only stage play **without**
`yxorp_stage_square_approved=true`
returns the stage configuration to
Yarn-only and reuses the existing rootful
stage service, without removing it.

Future native operator step on Kvin, after CI:

```bash
cd ~/src/sanctum-services && git pull && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true && ~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-square-probe.yml -e yxorp_kvin_stage_approved=true -e yxorp_stage_square_approved=true
```

The source-selected Nextcloud test is still
rootful standard HTTP80, not a loopback-only
listener or a port workaround. It adds one
virtual Host on the **already staged** listener;
Kvar and DNS remain unmodified. Kvin's firewall
currently blocks unsolicited LAN requests to
this stage, so local requests from Kvin
via `127.0.0.1:80` are the appropriate next
test; do not open that firewall here.

`ansible/yxorp-kvin-stage-square-probe.yml`
makes three *independent* anonymous root GETs
from Kvin, each with `Host: square.nexus.sanctum`:
direct Kvin :8085 Nextcloud, incumbent Kvar
NPM port80, and Kvin's local stage
`127.0.0.1:80`. Redirects are not followed.
All HTTP results are `no_log`, never display
raw Location, cookie or body; the final report
shows only statuses and **boolean** redirect
equality/metadata. Timeout or non-2xx on one
path does not prevent the other two from reporting.
HTTP302 and equal redirects would be **anonymous
route-shape parity**, *not* permission to switch
production or a demonstration of login, Calendar,
WebSocket, CSRF, DAV or browser trust semantics.

**Later external client gate:** Maintenance #20
owns Kvin's source-managed `eth0/public`
firewall policy admitting runtime and permanent
HTTP80. After owner approval and policy application,
the separate
`ansible/yxorp-kvin-stage-peer-probe.yml`
can test existing Yarn from Peanut without
changing DNS. Do not run remote-client tests
as local-stage acceptance or bypass firewalld
from Services. LAN/browser acceptance for
Nextcloud and Prism requires later, independent
consumer-specific tests and user sign-off.

**Stage removal and rollback:** For reversible
Square-only testing, simply re-run the existing
`ansible/yxorp-kvin-stage.yml` with
`-e yxorp_kvin_stage_approved=true`
but without Square's opt-in flag to return
to the manifest's Yarn-only state. If the
entire stage needs removal, the separate
`ansible/yxorp-kvin-stage-remove.yml` with
`-e yxorp_kvin_stage_remove_approved=true`
first verifies the stage-owned Quadlet and
known config-file allowlist before stopping
only this stage. It leaves application data,
image cache, Kvar NPM, DNS, Maintenance
firewall and the future production Quadlet
untouched. Do not remove the currently
working stage merely because a test passes.

## Historical completed reversal: remove the temporary Peanut test (do not rerun)

The separately named `ansible/yxorp-peanut-remove.yml` targets
**Peanut only**. Run it from Kvin's Services checkout when the test
concludes or if an installation step aborts:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-remove.yml
```

It checks the actual Quadlet contains exactly
`ContainerName=sanctum-yxorp-peanut-test` and
`Network=host` with **no** `PublishPort=` (not permitted in host mode),
plus its exact Nginx config mount, inventories the known configuration
files including hidden entries, then stops the trial, removes its own
Quadlet, reloads systemd and removes only its own config directory.
Unexpected files, symlinks or altered listener scope cause refusal.
It leaves the cached image, Kvar, DNS, **permanent firewall policy** and
application data intact. It checks the exact `/run` cleanup marker
and removes only the test's runtime `public:80/tcp` admission, if still
active. It verifies that the explicit runtime port allowance has gone
and deletes the marker. If the four-hour timeout or a reboot already
cleared the rule, cleanup still removes any remaining marker.

The trial's scoped remove authorization is present because Nova chose
this test. Removing **production** YXORP later is a separate operation
requiring DNS, proxy references, monitor, consumer and rollback coordination
with the actual owners. Simply deleting a production container is not
the complete reverse of having published the service.

## Native evidence and image lifecycle

Kvar's actual NPM upstream comparison is in
[2026-11-09 default-route review](../review/2026-11-09-yxorp-default-route-comparison.md).
Its separately executed bounded generated-behavior inspection is
[here](../review/2026-11-09-yxorp-behavior-observation.md).
Neither needs repeating just for demonstration.

Kvin previously qualified the *official Nginx ARM64 digest* with Podman
image inspection and an ephemeral offline `nginx -t`; see
[image qualification](yxorp-image-qualification.md).
That proves the image parser, **not** client service. The Peanut test uses
the normal maintained `stable-alpine` tag on its own architecture instead.
The role currently pulls a tagged image **when missing**; routine
flowing-image updates and rollback are still incomplete and must be
demonstrated rather than treated as delivered. Native Podman
`AutoUpdate=registry` may be a suitable future mechanism, but a systemd
restart alone does not prove that clients can use the service.
No automatic-update timer is enabled by this test.

**Production is not authorized:** the Kvin group vars retain
`yxorp_production_cutover_approved: false`. The intended deployment
is rootful, on TCP/80, available on the LAN subject to reviewed firewall
policy and DNS cutover. Kvar stays online for rollback until real
application/client behavior and the chosen lifetime update/reversal
strategy are accepted.

Follow [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2)
for current state and owner coordination.
