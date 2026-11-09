# YXORP — Kvar generated NPM behavior observation (November 9, 2026)

**Scope:** Kvin operator ran `ansible/yxorp-inspect-npm.yml`, using the
Services value-redacting observer on Kvar's rootful NPM generated proxy-host
configuration. The attached terminal result ended
`kvar.outer.sanctum ok=3 changed=0 unreachable=0 failed=0`.
The observer reported `status: observed`,
`configuration_changed: false`,
`credential_values_included: false`,
and no nonempty global custom configuration files.

The metadata is **not** an export of NPM database settings or a live effective
`nginx -T` configuration and cannot prove application behavior or working
URLs. The earlier [default upstream comparison](2026-11-09-yxorp-default-route-comparison.md)
still supplies the file-to-hostname mapping.

## Per-host source findings

| NPM hostname | Generated file | Explicit Upgrade/Connection headers | TLS certificate/listen directives | Non-default locations | Extra access/redirect directives |
| --- | --- | --- | --- | --- | --- |
| `square.nexus.sanctum` | `10.conf` | Yes | None detected | 0 | None detected |
| `yarn.inner.sanctum` | `11.conf` | No | None detected | 0 | None detected |
| `kuma.nexus.sanctum` | `4.conf` | No | None detected | 0 | None detected |
| `dir.nexus.sanctum` | `5.conf` | No | None detected | 0 | None detected |
| `yxorp.nexus.sanctum` | `6.conf` | No | None detected | 0 | None detected |
| `pihole.nexus.sanctum` | `7.conf` | No | None detected | 0 | None detected |
| `search.nexus.sanctum` | `8.conf` | No | None detected | 0 | None detected |
| `joule.nexus.sanctum` | `9.conf` | Yes | **Detected: listen, ssl_certificate, ssl_certificate_key** | 0 | None detected |

Every generated proxy-host file had exactly **one** location block and **no
non-default location**. No generated redirection-host, dead-host, default-host,
or stream-host files were present (all observed counts zero). Global nonempty
`/data/nginx/custom/*.conf` snippet count was **zero**.

## Upstream NPM template cross-check (context, not live evidence)

The [public NPM proxy-host template](https://github.com/NginxProxyManager/nginx-proxy-manager/blob/develop/backend/templates/proxy_host.conf)
explicitly renders an **optional** `/data/nginx/custom/server_proxy[.]conf`
include in every generated proxy server, and includes shared generated
proxy and header handling. Its
[HSTS map template](https://github.com/NginxProxyManager/nginx-proxy-manager/blob/develop/backend/templates/_hsts_map.conf)
has `https` **map keys**, not separate mandatory HTTPS listener
directives. This provides a plausible explanation for repeated
`custom_include_count: 1`, literal `https` tokens, and unclassified
mapping lines across all eight hosts, without any user-defined custom
content. The local NPM version has not been matched by an image digest,
so this is supporting template context rather than a proven exact
file-level match.

The published NPM
[shared proxy include](https://github.com/NginxProxyManager/nginx-proxy-manager/blob/develop/docker/rootfs/etc/nginx/conf.d/include/proxy.conf)
declares `X-Forwarded-Scheme`, `X-Forwarded-Proto`,
`X-Forwarded-For`, `X-Real-IP`, and the upstream Host. The new
YXORP candidate now explicitly sets `X-Forwarded-Scheme: $scheme`
along with its already-managed forwarding headers. This avoids
regressing a common forwarded-scheme contract in Nextcloud and other
applications; actual app acceptance still controls cutover.

Every file had `include_count: 2`,
`custom_include_count: 1` and
`conditional_or_unclassified_line_count: 2`. Consequently all eight had
`needs_manual_behavior_review: true`; **do not interpret these identical
flags as proof that every host is custom-configured**. The include is a
*reference*, not proof that it resolves to a nonempty custom file; the
original observer intentionally did not expand includes. Conversely, an
empty global custom directory is not an assertion that all generated
shared includes have been qualified.

All eight hosts also showed a directive called `https`, but its literal
value/context was redacted; **do not infer a working HTTPS listener from that
name**. Only the Prism host had explicit certificate and listen indicators.
The actual historical/current client origin must be verified separately.
The established design decision remains ordinary private HTTP, without
universal private CA or mandatory HTTPS deployment.

## Implementation implications

1. The proposed `square` (Nextcloud) and `joule` (Prism) entries already
   request WebSocket-aware forwarding, consistent with explicit Upgrade and
   Connection headers in generated NPM host files.
2. The proposed `kuma` entry is marked WebSocket-capable because Uptime
   Kuma's browser client needs Socket.IO/WebSocket behavior. The **old
   generated NPM host file does not contain explicit upgrade headers**:
   don't claim parity or use that absence to remove intentionally required
   WebSocket support. Check the new retained Kuma path end to end.
3. Leave other routes' disabled status unchanged. Nothing here is evidence
   that LinkStack, Pi-hole or Kuma has been restored onto Kvin.
4. Prism's old certificate directives are real source observations, but
   are **not** permission to alter the consciously accepted private HTTP
   policy. Qualify the actual Prism browser and WebSocket behavior on the
   replacement before a cutover decision.
5. Any custom/standard proxy snippets from shared NPM includes, upstream
   headers and actual clients remain to be addressed by relevant functional
   tests; do not claim full `nginx -T` equivalence from this projection.

## Next independent work and gate

- Build source-only HTTP proxy behavior tests (Host and forwarded headers,
  WebSocket upgrade, host rejection, controlled route modification) against
  real isolated Nginx, with synthetic endpoints and without Sanctum access.
- Identify a suitable immutable Linux ARM64 Nginx image digest before
  native Kvin Quadlet staging; the current source intentionally refuses
  an unset digest.
- Native application-level acceptance and the exact Kvar generated include
  semantics remain unresolved; any future inspection must be deliberately
  bounded, not a wholesale leak of NPM configuration.

No live YXORP, Kvar service, DNS, firewall or client was changed by this
observation or documentation.
