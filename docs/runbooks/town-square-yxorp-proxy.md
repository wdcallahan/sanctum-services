# Town Square — YXORP reverse-proxy route

**Status (October 19, 2026):** Nextcloud's Kvin listener returned HTTP 200
from Kvin at 192.168.1.192:8085 (installed=false), and the accepted Services
playbook repeated unchanged. NPM's newly configured HTTP proxy host reached
OpenResty but returned 502. Kvar's native curl to Kvin:8085 returned
"connection refused". Kvin's live public firewalld zone lacked 8085;
existing source-restricted Joule 8084 rule already permits 192.168.1.7/32.
Nova explicitly rejected an analogous source-restricted Nextcloud rule.
The Services role no longer mutates firewalld. Maintenance owns the
ordinary open TCP 8085 port in Kvin's active and permanent public zone; the
Services role now fails **before touching application state** if the live
interface zone or either port query fails. The Maintenance change has **not
yet been applied or accepted**.

**Current TLS decision:** NPM has no appropriate certificate. The initial
proxy route is HTTP only, and the application scheme is temporarily HTTP to
match it. This is a conscious staging choice, not proof that HTTP logins
are safe: administrator passwords, sessions and content may be intercepted
on the LAN. Prefer trusted HTTPS for actual user login/sensitive data,
or obtain Nova's explicit acceptance of the pilot HTTP risk. No Force SSL.
When adding a certificate, restore the declared https scheme in Services.

**Next acceptance:** After Nova approves Maintenance's separately previewed
firewall correction, Maintenance converges its ordinary Kvin service ports and
removes the exact obsolete rich rules, and Services verifies its runtime +
permanent 8085 prerequisite. Then confirm Kvar ->
192.168.1.192:8085 -> HTTP 200 and the NPM host's URL -> HTTP 200.
Kvar's native SSH is **port 10022**; port 22 intentionally reaches a tarpit.

## Host-firewall ownership and reconstruction order

The firewall is **not** part of Nextcloud's rootless Quadlet deployment.
[Sanctum Maintenance's Kvin service firewall](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/kvin-service-firewall.md)
owns ordinary `8084/tcp`, `5432/tcp`, and `8085/tcp` publication through
`playbooks/configure-kvin-firewall.yml`; see
[Maintenance issue 18](https://github.com/wdcallahan/sanctum-maintenance/issues/18).
Services never opens a host port and never adds/removes rich rules.

**Fresh host:** independently establish Kvin's platform/network/firewalld
foundations with the owning baseline procedure, then apply Maintenance's
reviewed published-service firewall policy, then deploy the Nextcloud
application via `ansible/site.yml`, then qualify direct HTTP and the YXORP
route. Baseline-after-service reconciliation must preserve Maintenance's
published service ports; do not use a whole-zone baseline overwrite. See
[Maintenance's reconstruction runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/kvin-firewall-acceptance.md).

**Existing Kvin (current incident):** no full baseline or old PostgreSQL
deployment is necessary. Nova reviews the independent Maintenance source and
preview and **separately authorizes the live firewall correction**. Only after
Maintenance converges runtime/permanent policy should Services' Nextcloud
playbook be run. Services' early, read-only `firewall-cmd` checks require
`eth0` in `public` and `8085/tcp` permitted by **both** runtime and
permanent firewalld. Missing prerequisite fails without changing the host
firewall or creating/updating Nextcloud files or services; the error points
back to Maintenance's runbook. An application-only later converge uses the
same prerequisite and cannot silently compensate for a missing host policy.

The host firewall proof is separate from application availability: it does
**not** imply Nextcloud is listening, PostgreSQL authentication works, the
installer is complete, or `square.nexus.sanctum` is reachable. Independent
peer `/status.php` and browser acceptance follow application availability.
Never interpret this source handoff as permission to apply live firewall changes.

## Existing owner and request path

Existing **Nginx Proxy Manager** (NPM) on YXORP is the currently installed
rootful Podman reverse proxy on Kvar (`kvar.outer.sanctum`,
`192.168.1.7`), with an admin GUI historically published at
`http://192.168.1.7:81`. **Confirm the live management UI before changes.**
Wildcard service DNS already targets YXORP; it does **not** create
individual proxy hosts.

Desired path:

```text
browser -> http://square.nexus.sanctum (YXORP:80; HTTP pilot)
        -> NPM proxy host for square.nexus.sanctum
        -> http://kvin.outer.sanctum:8085
        -> Kvin's rootless sanctum-nextcloud container :80
        -> db.nexus.sanctum:5432 (PostgreSQL, already accepted)
```

Services defines the intended application name, host and port.
YXORP's existing owner operates the actual NPM proxy. This runbook is the
application's **requested route contract and UI procedure**, not an
authorization for this repository to mutate the proxy host's underlying
service or database directly.

## Add NPM Proxy Host (new `square` entry; don't edit Joule's route)

From the NPM GUI, **Hosts → Proxy Hosts → Add Proxy Host**:

| NPM field | Intended value |
| --- | --- |
| Domain Names | `square.nexus.sanctum` |
| Scheme (upstream) | `http` |
| Forward Hostname / IP | `kvin.outer.sanctum` |
| Forward Port | `8085` |
| Websockets Support | Enabled |
| Cache Assets | Disabled |
| Access List | Publicly Accessible (no proxy authentication; access still governed by private network and Nextcloud's own login) |

Retain other defaults on initial bring-up unless an established shared
proxy policy requires otherwise. This is **not** a request to publish the
service to the Internet or to modify the wildcard DNS.

### HTTP-only staging and later TLS

For the present pilot, NPM's SSL certificate is **None** and Force SSL
is **off**, with no HSTS. Public scheme is temporarily `http`.
A certificate is not required for HTTP routing, but using administrator
credentials over HTTP risks LAN interception. Revisit trusted private
TLS before sensitive use. Future HTTPS will require a suitable certificate,
NPM host SSL configuration and a matching `https` scheme in Services.

## Acceptance

1. After Maintenance's normal 8085/tcp opening is approved and applied, and Services' read-only dual-store preflight passes, verify from Kvar
   using `ssh -p 10022 kvar.outer.sanctum 'curl -i --max-time 10 http://192.168.1.192:8085/status.php'`.
   Expect HTTP 200, not connection refused. Then verify from the browser
   or Kvin `curl -i --max-time 10 http://square.nexus.sanctum/status.php`
   and expect Nextcloud JSON instead of NPM's 502.
2. Confirm Nextcloud's web installer uses the existing PostgreSQL _FILE
   credential contract. Administrator is created by Nova in the browser
   and stored in Bitwarden, not generated by this playbook. Make an
   explicit decision about HTTP login risk before entering credentials.
3. After setup verify PostgreSQL schema, login, upload/download and proxy
   headers/trusted proxies with the actual source observed, not a guess.
4. Preserve an exportable/reconstructible NPM proxy definition and
   documented removal. HTTPS is a later separately accepted step.

**Non-goal:** This runbook does not claim existing automated proxy host
reconciliation or disaster restore. The lasting route must eventually be
owned, exportable/reconstructible, and safely removable through the accepted
YXORP management mechanism; the one-time NPM UI entry is the initial
operator procedure, not completion of that automation work.
