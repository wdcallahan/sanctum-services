# YXORP — plain Nginx on a rootful Podman Quadlet

**Current state, November 10, 2026:** **Kvar Nginx Proxy Manager
remains the production proxy**; the authoritative wildcard DNS and
existing client routes have not been switched. Plain Nginx on Kvin
is the intended rootful Podman host-network HTTP:80 replacement;
Peanut is the intended future peer/standby, not currently serving
permanent standby traffic.

The **Peanut-only rootful trial is complete**: Kvin got a same-client,
same-Host **349-byte byte-identical HTTP200** Yarn response via Peanut
and directly from the origin. Nova then ran the scoped removal play
on Peanut successfully (`ok=26 changed=5 failed=0`).
Do not repeat this trial, client test or cleanup. The prior Peanut
local health check and cross-host HTTP200 have been superseded by
the stronger content comparison and completed removal.

The **independent Kvin stage source** is now implemented:
`ansible/yxorp-kvin-stage.yml`, its same-Host/remote-client
`ansible/yxorp-kvin-stage-probe.yml`, and the verified
`ansible/yxorp-kvin-stage-remove.yml`. CI includes executed
real-Ansible checks of the exact stage permission expression.
The stage is a separate `sanctum-yxorp-kvin-stage` unit/Quadlet and
config tree, sharing **only the intended host port80** with
future production; it cannot coexist with another port80 listener.
**Neither Kvin stage nor production has been deployed**.
The stage approval and removal approval default false, and the
separate production cutover approval remains false.

**Blockers to native Kvin staging:** Maintenance owns the absent
runtime and permanent `eth0/public` HTTP:80 admission on Kvin
([Maintenance #20](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-6775538017));
actual firewall policy application and actual stage deployment
each require Nova's separate approval. Stage/production and wildcard
DNS are distinct authorization boundaries. See the new **Independent
Kvin stage** section below for precise source and future commands.

Kvar's broken old `yarn.inner.sanctum` NPM path is deferred, not
repaired, after a Kvar/Kvin native route comparison showed the same
gateway for Yarn and Arcane destinations. The new
`yarn.nexus.sanctum` route was accepted in the Peanut trial, and
the old name remains tracked for explicit eventual consumer
review/retirement. No arbitrary route, firewall, private CA or
Kvar NPM rewrite is warranted by those results.

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


## Kvin HTTP:80 stage — install locally before network publication

**Status, November 10:** The operator has authorized deploying the
**separately named YXORP stage on Kvin now**, while Kvar NPM continues
serving production and wildcard DNS remains unchanged. This authorizes
the Kvin stage, **not** publication, production cutover, DNS mutation
or a Maintenance firewall change. The stage has not yet been natively
installed; until the first successful Kvin run it is still source-only.
The earlier rootful Peanut trial is accepted and removed.

**Why Kvin can be staged immediately:** The actual Kvin readiness
check found no host TCP80 listener or existing YXORP Quadlet, and the
qualified rootful ARM64 Nginx image is cached. The host firewall
blocks **inbound LAN** TCP80 but does not prevent a local rootful
Nginx process binding normal `0.0.0.0:80` or Kvin sending its own
HTTP requests to `127.0.0.1:80`. Therefore firewalld admission
is deliberately **not** an installation or local-test prerequisite.
Maintenance retains full ownership of the host firewall.

**Install the approved Kvin stage and then test locally** from Kvin
using its existing Services checkout:

```bash
cd ~/src/sanctum-services
git pull
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage.yml -e yxorp_kvin_stage_approved=true
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-probe.yml -e yxorp_kvin_stage_approved=true
```

The first play validates exact Kvin identity, explicitly supplied
stage approval and closed production cutover, inspects existing
stage/production Quadlets, checks for an unrelated TCP80 listener,
and refuses unknown files before using the standard YXORP role.
It deploys **rootful host-network Nginx on real port 80** with the
previously qualified digest, but uses separate test-owned
`sanctum-yxorp-kvin-stage` Quadlet, service and configuration path.
It does not modify any firewall, DNS, Kvar or application service,
and does not authorize production. Kvar is untouched throughout.

The local probe queries Kvin's own `127.0.0.1:80` health endpoint
and compares the direct Yarn backend with the **local staged
proxy** using identical public Host headers, requiring HTTP status,
content type and actual response body equality. Raw HTTP contents
are suppressed. All seven legacy routes stay disabled in the
candidate manifest; only `yarn.nexus.sanctum` is enabled. These
tests establish **local Kvin application forwarding**, not
reachability from another machine or consumer/browser readiness.

**Later independent network acceptance** after Maintenance's
source-managed Kvin HTTP80 runtime admission is approved/applied:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-peer-probe.yml -e yxorp_kvin_stage_approved=true
```

This separate read-only play first checks that Kvin's stage unit
is running and `eth0/public` **runtime** firewalld admits HTTP80,
then probes the actual listener and Yarn route **from Peanut**
without changing DNS. For longer-term service publication,
Maintenance also owns desired **permanent** HTTP80 policy.
The owner handoff remains [Maintenance #20](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-6775538017).
Do not rerun the old Peanut trial merely to test Kvin.

**Removal when the stage is no longer wanted or must be rolled
back:** `ansible/yxorp-kvin-stage-remove.yml` requires explicit
`-e yxorp_kvin_stage_remove_approved=true`. It validates the
exact owned stage Quadlet and only the two known files in its
configuration tree (including hidden entries), then stops/removes
only stage resources and verifies inactivity. It does not remove
images or application data, change firewalld, DNS, incumbent
NPM, or production Quadlet/configuration. **Do not remove
the new stage automatically after its local test**; it can
remain available for the separately gated remote acceptance.

When the staged service works locally and from an external
client, qualify the intended disabled routes and actual
sessions/WebSockets—particularly Nextcloud and Prism—before
authorizing a DNS cutover or a permanent production-service
transition. Kvin stage approval does **not** authorize that
future cutover.

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
