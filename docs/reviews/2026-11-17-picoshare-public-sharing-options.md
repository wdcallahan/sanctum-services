# Candidate review — occasional externally reachable file shares
## November 17, 2026 — NOT an approved installation or WAN change

Nova is exploring using **PicoShare** for an occasional public link handed
to a particular outside recipient, and explicitly wants **exceptionally
strong isolation** for *this* Internet-facing service. This does not
supersede his general preference against needless internal single-IP
firewalls or militarized LAN administration. The ISP now provides
static public addresses, but none has been assigned by this document to
a service, firewall, interface, NAT rule or DNS record.

**History:** PicoShare was discussed as a candidate in January 2025 and
March 2026. In October 2026, an earlier assistant noted that Nextcloud
already has public links and File Drop, and proposed dropping PicoShare
unless a compelling distinct standalone-sharing need appeared. Nova's
November request for an **isolated public sharing surface** is a valid
reason to reassess, but **does not authorize deployment**.

## Findings from upstream source on November 17

- Official archive: https://github.com/mtlynch/picoshare
  (its repository now indicates a move to
  https://codefloe.com/mtlynch/picoshare; verify current upstream supply
  chain before building or deploying).
- **Actual GitHub latest release v1.5.5 dated November 16, 2026**:
  https://github.com/mtlynch/picoshare/releases/tag/v1.5.5
  New *download passphrase protection*, two guest-upload security fixes
  (client-disconnect handling and bypass of guest-link limits), plus an
  Alpine base image update. Version 1.5.4 is **not** the current release.
  Verify the exact supported ARM64 image/release availability and
  checksum if selecting it; a stale registry tag is not enough.
- Existing features: unguessable recipient download links, file
  expiration, owner passphrase protected upload/admin, optional guest
  upload links. **Do not assume** recipient identity proof, unlimited
  single-use token enforcement, or the existence of preauthenticated
  download-only HTTP paths without source verification.
- PicoShare stores both file payloads and metadata in a SQLite store;
  no automatic disk-space reclamation simply because a share expires.
  Owner updates/retention/restore still matter even if usage is small.

## Threat model and accepted controls to consider

**Purpose:** Allow someone on the general Internet to download *one
explicitly released file* without giving them any authority on
`.sanctum`, private services or other owner data. The recipient need
not create an account. Public inbound reachability is limited to this
one separately commissioned service, not a new global LAN policy.

**Two alternative physical trust boundaries:**

1. **Strongest locality isolation:** PicoShare or a static/signed-URL
   sharing endpoint on an external VPS/object-storage gateway. Admin
   upload only from the private owner connection; no incoming home
   firewall/NAT required and no network tunnel back to internal Sanctum.
   The ISP static IP is optional in this approach. Vendor/cloud account
   and remote storage become third-party trust considerations.
2. **Home-hosted dedicated DMZ:** distinct host/VM and router/VLAN
   policy isolated from management, Kvin, Peanut, Wicket, all RFC1918
   and ULA internal networks and other private subnets, with no internal
   data mounts. Public 443 terminates on its own isolated gateway;
   outbound access limited to necessary update/DNS/CA services.
   Admin control on separately protected VPN-only interface.
   A second static IP alone is **not** a DMZ; routing, real bidirectional
   firewall rules and segmentation must be accepted by Bunny Factory
   and Maintenance. Exposing existing production Kvin YXORP is *not*
   the default design.

**Application and link rules:** TLS (trusted public cert);
public access only to audited read-only download routes; deny admin
dashboard, authentication, upload and guest-upload endpoints via
reverse proxy, and disable guest upload features unless expressly
wanted. Owner upload/admin only via authenticated private management
path (VPN), not by publishing the admin endpoint to the Internet.
Long random token links, short configurable expiration, easy
revoke/delete; **v1.5.5 optional independent download passphrase**
sent over a separate channel. Don't claim a token or passphrase
proves the recipient's identity or stops forwarding.
Avoid URLs containing other credentials in standard access logs,
Referrer or external analytics. Set appropriate cache/referrer
controls and forced attachment where needed.

**Abuse containment:** no unnecessary host filesystem mounts,
system/private APIs or container socket; rootless or least-privileged
container service, one dedicated limited-volume storage area with
capacity and size bounds, request-rate/time/body-size controls,
resource caps, daily patch/update mechanism, log visibility and
recovery of its own SQLite data. Public reachability always entails
some DoS and unknown-vulnerability risk—network and process
isolation reduce blast radius, do not make exploitation impossible.
Guest uploads introduce a larger attack surface and need a distinct
approval. Archive/content-type and handler behavior should be
tested against current upstream; no inventing URL patterns.

## Alternatives, not invented obligations

- **PicoShare** best fits small ad-hoc administrator-created links.
  It's still a running public application; stronger isolation warranted.
- **Read-only static/signed URL file gateway** from isolated storage has
  fewer app/admin endpoints and is arguably the lower-attack-surface
  solution if recipients only need to **download**. Usability and
  private uploading remain to be evaluated.
- **Nextcloud public share links** already exist as an application
  capability but exposing the entire functioning private Nextcloud
  service to the Internet would expand the impact of compromise.
  A separate isolated Nextcloud replica would have much more state and
  maintenance than this limited use case.

**Not done/authorized:** deployment, WAN firewall, static-address route,
DDNS/domain, DNS record, certificate, container pull or new public
endpoint. This is a deliberately uncommitted candidate; owner should
choose the physical boundary and required recipient controls before
implementation is added to the roadmap.
