# YXORP comparison — 2026-11-09, Maintenance NPM report

**Scope:** read-only comparison of the existing Kvar Nginx Proxy Manager
generated proxy-host default upstreams with proposed YXORP routes on Kvin.
Operator executed `tools/review-yxorp-publication.py` on Kvin using
`sanctum-maintenance/artifacts/maintenance-discovery.njEtjLMN/reports/cutover-service-publications.json`.
The report contains eight projected hosts, none marked partial or unsupported,
and five of the six initial YXORP proposals matched their observed default
upstreams exactly. This establishes **default-upstream agreement only**,
not header, WebSocket, custom-location, redirect or client equivalence.

## Observed NPM default upstreams

| NPM name | Default upstream | Generated source | Disposition |
| --- | --- | --- | --- |
| `dir.nexus.sanctum` | `http://kvar.outer.sanctum:8081` | `5.conf` | Retain; later move LinkStack to Kvin |
| `joule.nexus.sanctum` | `http://kvin.outer.sanctum:8084` | `9.conf` | Retain Prism; Project Joule owns app |
| `kuma.nexus.sanctum` | `http://kvar.outer.sanctum:3001` | `4.conf` | Retain; later point to accepted Kvin Kuma |
| `pihole.nexus.sanctum` | `http://kvar.outer.sanctum:82` | `7.conf` | Retain Pi-hole; qualify UI after Kvin restore |
| `search.nexus.sanctum` | `http://kvin.outer.sanctum:8083` | `8.conf` | Retain existing Kvin Search |
| `square.nexus.sanctum` | `http://kvin.outer.sanctum:8085` | `10.conf` | Retain Nextcloud |
| `yarn.inner.sanctum` | `http://192.168.1.110:80` | `11.conf` | Existing route; preserve pending client review |
| `yxorp.nexus.sanctum` | `http://kvar.outer.sanctum:81` | `6.conf` | Obsolete NPM administration UI; not rebuilt |

## Proposed addition, not in NPM

`yarn.nexus.sanctum` → `http://yarn.inner.sanctum:80` is the
explicit new Git-declared route. It must not be confused with the existing
`yarn.inner.sanctum` proxy host. Maintenance independently published DNS
for `yarn.inner.sanctum` and qualified its then-current address. No removal
of the older route is authorized by this report.

## Reconciliation performed

[The proposed route manifest](../../data/yxorp-routes.yml) now contains
the eight migration-relevant desired or observed names **except** the old
NPM admin UI, which is explicitly excluded. Of the eight entries in the
manifest, seven represent existing NPM proxy routes and one is the new
`yarn.nexus.sanctum` route. All existing NPM records remain disabled
in the initial staged renderer; only the deliberately new Yarn route is
enabled. `pihole.nexus.sanctum` is no longer treated as an unknown-port
upstream, but its **application-specific path semantics remain unqualified**.

The source comparison may still show one observed-only name
(`yxorp.nexus.sanctum`) and one proposed-only name
(`yarn.nexus.sanctum`). Both are **explicitly intended differences**,
not an uninvestigated missing proxy host. Do not change DNS or clients
based on this report alone.

## Still unknown

NPM custom locations, additional request/response headers, redirects,
WebSocket behavior, non-default proxy behavior, and actual app acceptance
were not part of Maintenance's read-only projection. A separate,
appropriately scoped observation is needed before replacing the active NPM
proxy. Kvar and Kvin networking remain untouched by this review.
