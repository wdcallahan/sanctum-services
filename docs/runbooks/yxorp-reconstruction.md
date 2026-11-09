# YXORP — source-owned plain Nginx reconstruction

**Source status: preliminary, November 8, 2026.** This is a rootful Podman
Quadlet and Ansible candidate for **Kvin**, not a completed proxy cutover,
NPM-route parity finding or native install receipt. Kvar's Nginx Proxy
Manager remains the active production proxy. No live networking has been
changed by writing these files.

## Why and what is already known

Yxorp keeps the established `*.nexus.sanctum` service names while replacing
NPM's UI/SQLite-managed configuration with ordinary Nginx generated from
`data/yxorp-routes.yml`. The operator selected HTTP on the private network;
neither a new CA nor HTTPS is required by this work.

Maintenance's [Kvar evidence](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/handoffs/2026-11-08-kvar-retirement-inventory.md)
and Services' [Town Square runbook](town-square-yxorp-proxy.md) establish
documented upstreams for Yarn, Square, Prism, Search, LinkStack and Kuma.
The routes file intentionally includes **disabled proposed entries**; it is
*not* a claim of current NPM parity. The Pi-hole UI default upstream has since been observed as
`http://kvar.outer.sanctum:82`; custom NPM locations/headers remain
unqualified, and the old NPM admin UI is intentionally excluded. The legacy
`yarn.inner.sanctum` route and the requested `yarn.nexus.sanctum` route
are different, even though their intended upstream may coincide.

## Read-only / source-only preview

From the Services checkout with a configured Ansible controller:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-preview.yml
```

This renders a candidate at `/tmp/sanctum-yxorp-proposed.conf` on the
controller, without contacting Kvin or Kvar. Review the generated Nginx
server blocks; only the explicitly `enabled: true` Yarn route is selected
initially. The other route records document intended behavior pending
real NPM comparison. Preview is **not** an Nginx parser test.

## Native isolated staging — not yet approved or performed

1. Obtain the **real linux/arm64 tested Nginx image manifest digest** using
   the host's trusted container supply path, then set `yxorp_image` in
   `ansible/group_vars/yxorp.yml`. An empty digest intentionally blocks
   deployment. Do not substitute a mutable `:latest` tag.
2. Reconcile all intended NPM proxy hostnames and upstreams against the
   maintained production report. Include nondefault paths, redirects,
   custom headers, WebSockets and current accepted client URLs.
3. Confirm Kvin is otherwise ready to run a system-level Quadlet. An
   independent host/Podman prerequisite remains Maintenance-owned; this role
   does not bootstrap a replacement computer.
4. With Kvar's production listener untouched, separately select the isolated
   stage run:

   ```bash
   ~/.local/bin/ansible-navigator run ansible/yxorp.yml
   ```

   It is deliberately constrained to Kvin `127.0.0.1:18080`. The role
   validates all route tokens, renders a *candidate* config, runs Nginx
   `-t` in a disposable Podman container, publishes only a valid config,
   then installs/reconciles the rootful Quadlet. No DNS, host firewall or
   Kvar mutation occurs. A later configuration-only change triggers Nginx
   reload; a Quadlet change restarts its service.
5. Verify on Kvin from a native shell:

   ```bash
   curl --noproxy '*' -fsS http://127.0.0.1:18080/__yxorp_health
   curl --noproxy '*' -i -H 'Host: yarn.nexus.sanctum' http://127.0.0.1:18080/
   ```

   The first tests only local Nginx readiness. The second tests whether the
   selected upstream works through the proposed hostname. Real app sessions,
   login redirects, Nextcloud CalDAV and Prism WebSockets must be tested
   with their specific active routes, not inferred from these probes.

## Production change is separate and explicit

Source defaults refuse `0.0.0.0:80` without
`yxorp_production_cutover_approved: true` **and** matching deliberate bind
and port changes. This variable is a technical guard, not an authorization
on its own. Maintenance owns firewall and DNS publication changes, including
`*.nexus.sanctum`. An owner-approved cutover must qualify those routes and
allow rollback to Kvar before repointing names. Keep old NPM and its persistent
data until Kvin's wanted applications and their client access are accepted.

The stage container uses ordinary rootful Podman bridge networking; actual
reachability of same-host Kvin upstreams through the bridge must be verified
natively (hairpin/routing and DNS resolution), not assumed. The candidate
config's static hostnames resolve at Nginx start/reload time. A change in
upstream address requires a verified reload or deploy.

## Rebuild and operations

- **Rootful manager:** `systemctl status sanctum-yxorp.service`,
  `journalctl -u sanctum-yxorp.service`, `podman ps`.
- **Config source:** `data/yxorp-routes.yml`, not a manually maintained
  `/etc/nginx` file or web UI.
- **No application database:** Nginx routing is text configuration; it has
  no stateful YXORP database to migrate or back up. Desired state plus the
  selected image digest and underlying host platform rebuild the proxy.
- **Removal:** use systemd to stop/disable the rootful service, then remove
  the source-owned Quadlet and configuration only after a separately approved
  change. Do **not** remove unrelated Podman volumes, host networking or
  app-owned databases.
- **Evidence still missing:** actual NPM route parity, ARM64 pinned image,
  client-by-client acceptance, idempotent native repeat, approved rollback
  and production cutover. None is implied by this source commit.

Follow [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2)
for the remaining reconstruction/qualification.

## Comparing the real NPM publication report with proposed routes

Maintenance already has a read-only observer:
[`playbooks/inspect-cutover-service-publication.yml`](https://github.com/wdcallahan/sanctum-maintenance/blob/main/playbooks/inspect-cutover-service-publication.yml).
It creates a private controller-side report,
`reports/cutover-service-publications.json`, containing the selected
Kvar rootful generated NPM default-upstream projection. The report has
previously been run, but its **actual JSON content is not in Git**.
Do not pretend that the notes are a full observed inventory.

When that authentic report is available, compare without editing either
repository:

```bash
python3 tools/review-yxorp-publication.py \
  --report /path/to/sanctum-maintenance/reports/cutover-service-publications.json \
  --declared data/yxorp-routes.yml
```

The tool reads both files and emits a bounded JSON comparison: actual
observed name/HTTP scheme/upstream host/port, missing proposed and extra
observed names, conflicting upstreams, and partial/unparseable NPM files.
It refuses the wrong rootful host and never writes files or changes routers.
Importantly, it **does not** claim to inspect custom NPM locations, headers,
redirection, access lists or actual client behavior. These still require
additional review before declaring route parity.

## November 9 default-upstream reconciliation

The Kvin operator compared Maintenance's **actual retained** read-only
report against the declared route manifest. All five previously observed proposed
upstreams matched NPM, and the report gave exact Pi-hole and legacy Yarn
upstreams. These have been added as **disabled** entries. The obsolete NPM
administration UI remains excluded; `yarn.nexus.sanctum` remains a new
requested route. The [bounded comparison review](../review/2026-11-09-yxorp-default-route-comparison.md)
records the complete eight-name result and the remaining behavioral gaps.

## Next observation — effective NPM behavior flags (read-only)

The accepted generated-default-upstream comparison cannot say whether NPM
configured extra locations, proxy headers, authentication, redirects,
WebSockets, TLS or global custom snippets. NPM's public upstream templates
include possible advanced config and custom includes in generated proxy hosts.
A complementary **value-redacting** observer now exists:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-inspect-npm.yml
```

Run from the Services checkout on Kvin **only when an operator is available
to review it**. It targets only the existing `kvar.outer.sanctum` management
SSH entry on port **10022** and uses privileged read-only access to the
rootful NPM generated config. It does not access the NPM API/database,
modify files, reload a service, or change DNS or firewall.

The observer emits bounded generated file names and SHA256 fingerprints,
directive/header **names** (not values), location counts (without printing their values),
a count of unsupported paths/conditional lines, markers for access control,
WebSockets/redirects/TLS, and only the name/checksum of nonempty custom
snippet files. The literal bodies of NPM config, URL values, passwords,
tokens, Authorization header contents and advanced custom includes are
**not printed**. Its output is for migration review, not a claim of full
effective NPM `nginx -T` parity. Any unexpected structure remains
`unknown`; do not auto-enable a route that requires manual investigation.

The [source and syntax CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42677320762) passed. The check has **not been executed on Kvar**.
If it fails due to the legacy SSH/privilege setup, do not quietly change
router or server auth to make this inspector work.
