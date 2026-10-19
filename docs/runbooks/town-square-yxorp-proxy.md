# Town Square — YXORP reverse-proxy route

**Status (October 19, 2026):** Nextcloud application on Kvin is **running** using
Ansible-managed rootless Podman; native first deployment passed and unchanged
repeat passed `ok=15 changed=0`. The public-facing YXORP proxy host has
**not yet been created or accepted**. A `curl -i --max-time 10
https://square.nexus.sanctum/status.php` probe returned an OpenSSL
`tlsv1 unrecognized name` alert before an HTTP response; this is consistent
with the HTTPS proxy not recognizing that SNI name. It is not evidence of
an application failure.

## Existing owner and request path

Existing **Nginx Proxy Manager** (NPM) on YXORP is the currently installed
rootful Podman reverse proxy on Kvar (`kvar.outer.sanctum`,
`192.168.1.7`), with an admin GUI historically published at
`http://192.168.1.7:81`. **Confirm the live management UI before changes.**
Wildcard service DNS already targets YXORP; it does **not** create
individual proxy hosts.

Desired path:

```text
browser -> square.nexus.sanctum (YXORP:443; trusted HTTPS)
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

### Certificate / SSL tab

- Check whether NPM already holds an appropriate **trusted** certificate
  covering `square.nexus.sanctum` or the wildcard `*.nexus.sanctum`.
  If one exists, select it and enable **Force SSL**.
- If none exists, **do not assign an unrelated host certificate**, do not
  pretend a public ACME issuer can validate a private `.sanctum` name,
  and **do not enter administrator credentials over plain HTTP**.
  A bare HTTP proxy entry can be used for credential-free reachability
  checks only. Provision/trust the appropriate private CA certificate through
  YXORP's owning procedure before administrator setup.
- HSTS is not a prerequisite to first bring-up. Use it only after a
  trusted HTTPS route is proven. A certificate existing in the UI is
  not itself proof that the client trusts its chain.

## Acceptance

1. From a real intended user/client, `curl -i --max-time 10
   https://square.nexus.sanctum/status.php` must complete **trusted TLS**
   without `-k`, reach Nextcloud and report HTTP 200 with
   `"installed":false` until first setup (then `true`). Never use
   `curl -k` to treat an untrusted certificate as accepted.
2. Open the **HTTPS** page in a real browser. Nova creates the initial
   administrator account interactively and manages the website login in
   Bitwarden; Services automation must not generate/store that account's
   password. Confirm Nextcloud's browser installer chooses the existing
   PostgreSQL database from its private `_FILE` inputs.
3. After install verify application schema, login, and basic file operations
   from the actual URL. Configure/check forwarded headers and trusted proxies
   against real NPM source addresses; do not hardcode inferred proxies.
4. Record the validated proxy host + certificate association and intended
   removal operation. Subsequent normal operation, backup, restore and
   application-only uninstall remain separate project acceptance gates.

**Non-goal:** This runbook does not claim existing automated proxy host
reconciliation or disaster restore. The lasting route must eventually be
owned, exportable/reconstructible, and safely removable through the accepted
YXORP management mechanism; the one-time NPM UI entry is the initial
operator procedure, not completion of that automation work.
