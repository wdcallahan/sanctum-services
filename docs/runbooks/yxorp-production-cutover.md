# YXORP production release — staged Kvin Nginx to live Sanctum Nexus

## November 11, 15:17 Central — FIRST NATIVE PRODUCTION ATTEMPT BLOCKED BY YARN

Nova authorized stage-removal and production
Quadlet transition. Native second play
`ok=29 changed=5 failed=1 skipped=1`.
The source-owned Kuma forwarding post-test
passed (HTTP 200/302), then the next Yarn
new-name `Host: yarn.nexus.sanctum`
frontend request to `127.0.0.1:80`
timed out (HTTP status -1, 8-second
timeout). **Actual eight-route production
acceptance is NOT complete.**
Existing Kvar NPM and Maintenance DNS
were NOT changed: clients still reach
Kvar for the current Nexus names.
No native TCP80 firewall publication.

**DO NOT rerun stage removal or
production deployment just to get a
second timeout.** Run one source-owned,
read-only Kvin comparison after source CI:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp-production-yarn-diagnose.yml
```
Return `PLAY RECAP` and the bounded
`Report bounded production Yarn route
evidence without retrying a deployment`
msg or failed task. This classifies
the current named origin, direct IP
and actual production proxy on
both Yarn Host headers, using the
working Kuma route as control.
No raw response body, cookies or
other secret material is reported.
Choose the correction from the actual
result, then finish stage-to-production
and Maintenance firewall/DNS release.
The already accepted historical
8/8 Kvin *stage* probes should not
be rerun for reassurance.

**Current status: SOURCE PREPARED, NO LIVE CUTOVER.** Nova expressly
permits a practical proxy switchover during the workday, including
substantial downtime. Do not invent an after-hours or zero-downtime
gate. The current **Kvar Nginx Proxy Manager remains the live proxy**,
and its data and service must stay intact for rollback.

## Why there are separate stages

The already accepted Kvin
`sanctum-yxorp-kvin-stage.service`
is rootful Nginx on real HTTP80, with eight
qualified initial local Host routes. Its
Quadlet/config live under `yxorp-kvin-stage`
paths and do not constitute a permanent production installation.

The intended permanent
`sanctum-yxorp.service` also binds HTTP80
and cannot coexist. The original
`data/yxorp-routes.yml` intentionally keeps
only initial Yarn enabled for staged approval.
Source-owned `ansible/yxorp.yml` now
selects **exactly those eight known hostnames**,
enables all eight for production, and changes
**only one upstream from that baseline**:
`kuma.nexus.sanctum` becomes
`127.0.0.1:13001` (the source-owned,
Vault-backed, natively recovery-qualified Kvin Kuma).
It preserves the other seven direct origins,
including interim old Kvar LinkStack and Pi-hole.
The role verifies Nginx syntax and its actual
container-mounted config, while post-tasks
verify Kuma and Yarn forwarding over Kvin HTTP80.
This operation does **not** edit DNS,
Kvar NPM, firewall or application data.

**Production listener first:** It is safe to retire Kvin's staging
unit and start Kvin's real production Nginx before changing
Maintenance's firewall or DNS, because clients still reach
the incumbent Kvar. That lets us observe an actual production
listener and defer the DNS change until both remaining
owner-managed prerequisites are satisfied.

## Phase 1 — scoped stage removal and production service start

**[Full Services CI #43098976225 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43098976225).** Use this single Bash chain
from **Kvin**. It deliberately has two
different opt-ins; approval for removing
the stage does not implicitly authorize
any other uninstall. No Vault mount is
needed for these proxy playbooks.

```bash
cd ~/src/sanctum-services &&
git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp-kvin-stage-remove.yml \
  -e yxorp_kvin_stage_remove_approved=true &&
~/.local/bin/ansible-navigator run ansible/yxorp.yml \
  -e yxorp_production_cutover_approved=true
```

First play stops and removes *only* the
owned Kvin stage Quadlet and two config
files; it does not touch Kvar. The second
requires its stage to be absent, promotes
the exact eight routes, starts the distinct
rootful production Nginx, verifies the
published and mounted config, then proves
local Kuma and Yarn forwarding. Keep
the two PLAY RECAPs and the bounded
`Report bounded Kvin YXORP production listener readiness`.
This is a production **listener** acceptance,
not yet a real user-facing DNS cutover.

A fatal failure in the second play leaves
Kvar's current DNS and NPM service untouched,
so client fallback remains possible while
the local production candidate is repaired.

## Phase 2 — publish Kvin TCP80 with Maintenance

Maintenance owns Kvin's `eth0`/`public` firewalld policy.
[Maintenance source commit
`873c9c6`](https://github.com/wdcallahan/sanctum-maintenance/commit/873c9c6fdb7f4ac8a7b56181a957eb03a89005a9)
adds ordinary `80/tcp` to the existing,
strictly reviewed `5432/8084/8085` entries.
It has **not yet been applied on Kvin**. DNS remains at Kvar while this is done.

**[Maintenance's scoped firewall CI #43100611079 passed](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43100611079).** After Kvin's production proxy listener is locally qualified, use
`~/src/sanctum-maintenance` and its
existing `tools/run-ansible-logged` workflow,
with `sanctum_service_firewall_source_revision`
set to the exact reviewed commit. First
run `playbooks/configure-kvin-firewall.yml`
in `--check --diff` to inspect the bounded
runtime/permanent policy delta. Then run
the same approved owner play with
`sanctum_service_firewall_apply=true`
and a no-change repeat. Do not bypass
this with an ad hoc firewalld command.
The existing Kvin staging Nginx may
remain active throughout.

The source firewall role protects all
unrelated zone, policy and PostgreSQL
settings. Do not apply from a stale
controller checkout or an unreviewed
revision.

## Phase 3 — owner-managed Nexus DNS change

**Do not make this change before Kvin production Nginx
is running and Kvin TCP80 is admitted for LAN clients.**

Maintenance's effective zone source
`data/dns.yml` presently maps
the following aliases to **Kvar
`192.168.0.7`**. To move the proxy
frontends, change only:

| Owner (under `.sanctum`) | Old A | New A |
| --- | --- | --- |
| `dir.nexus` | `192.168.0.7` | `192.168.0.192` |
| `joule.nexus` | `192.168.0.7` | `192.168.0.192` |
| `kuma.nexus` | `192.168.0.7` | `192.168.0.192` |
| `pihole.nexus` | `192.168.0.7` | `192.168.0.192` |
| `search.nexus` | `192.168.0.7` | `192.168.0.192` |
| `*.nexus` | `192.168.0.7` | `192.168.0.192` |

Keep `yxorp.nexus` explicitly pointing
at Kvar for the old NPM administration
UI while it remains useful.
Keep the three explicit `db.nexus`,
`db1.nexus` and
`postgresql.nexus` records
pointing directly at Kvin
(`192.168.0.192`) until their
**separately commissioned** migration.
Preserve `yarn.inner` as its distinct,
direct hostname. No route is removed.
Do not confuse the Nexus wildcard
with individual explicit A records.

Maintenance must advance the SOA serial
strictly above the *actually served*
serial, validate the candidate zones,
then use its existing
`playbooks/publish-sanctum-dns-zones.yml`
preview and native publication on active
Peanut DNS. Confirm Kvar DNS/DHCP and
other client resolver authority before
claiming every client has switched.
The published TTL is 300 seconds, and
resolver caches may take time.
Have an actual non-Kvin client request
`http://kuma.nexus.sanctum` and
`http://joule.nexus.sanctum` by name
and verify real browser sessions/
Socket.IO WebSockets, not just DNS or
anonymous GET. Do not claim this
phase accepted from source tests alone.

## Rollback, including a bad route

Until named clients have accepted the
new path, leave Kvar's NPM running.

- **Before DNS publication:** Kvar still answers
  production frontend names. If new
  Nginx is broken, use the separate
  `ansible/yxorp-production-remove.yml`
  with `-e yxorp_production_remove_approved=true`
  to remove only the source-owned
  Kvin production Quadlet/config. Never
  delete the retained Kvar NPM.
- **After DNS publication:** First restore
  the same six DNS aliases to
  `192.168.0.7` in Maintenance source,
  advance the SOA serial again, publish
  and verify from actual clients.
  Only then stop/remove Kvin production
  Nginx if desired. Existing Kvar
  application data is unchanged.
- If useful, re-stage Kvin's eight-route
  Nginx later using its independently
  approved stage playbook; that is not
  required for Kvar DNS rollback.

The firewall admission may remain until
a separately source-owned policy reversal;
do not delete unrelated open service ports.

## After live cutover

The two long-term Kuma peers should live
on **Kvin and Peanut**, as already
declared by Maintenance's
`sanctum_service_roles: kuma_peer`
for each host. Kvar's old Kuma is
a migration fallback, not a permanent
dependency for cross-monitoring.
Configure each bear to observe the
other's externally reachable HTTP service,
using the established owner-managed
credentials and avoiding notification loops.
Monitoring through HTTP needs no
privileged host Podman socket; direct
container-level Podman inspection has
separate socket/permission requirements.
Peanut's Kuma remains **unbuilt**.
