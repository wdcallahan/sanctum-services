# Sanctum Services — Session Continuation

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
