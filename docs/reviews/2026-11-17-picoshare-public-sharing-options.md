# Candidate review — occasional externally reachable file shares

## November 17 — NOVA RECALLED `buny.us`'s ORIGINAL PURPOSE: YOURLS URL SHORTENER

Nova registered `buny.us` specifically to host **YOURLS** (Your
Own URL Shortener). The project retains the **YOURLS** name in
November 2026, currently maintained at
https://github.com/YOURLS/YOURLS (release 1.10.6), with owner-only
link creation, custom keywords and API integration.
This is a user-owned, historical goal worth recovering, **not**
a new invented service. Nova now proposes:

- **`https://buny.us/<typeable-short-code>`** — the original apex
  YOURLS redirect service, publicly following links but
  **owner-only creation/admin**. Also useful for nonfile shortened
  links, independent of the future file-sharing service.
- **`https://share.buny.us/<strong-one-time-token>`** — home-hosted,
  sharply isolated public file download service (maybe fdrop modified,
  maybe a minimal own download handler); actual file transfer, token
  lifetime, in-flight claim and success/expiry logic LIVE HERE.
- **`vpn.buny.us`** — proposed new dedicated hostname for eventual
  WireGuard/Sanctum private remote-access endpoint, replacing the
  historical `buny.us` bare VPN hostname from the Nov12 register.
  VPN remains separately owned; no router/firewall/DNS approved.
- TWO ISP static public IPs are reportedly available. Multiple
  hostnames/web services can share one IP using HTTPS/SNI; the VPN
  can share an IP with TCP/443 web via its distinct UDP WireGuard port,
  or use the other address. True DMZ/segment firewall isolation
  matters; **second IP is not itself isolation**. Determine actual
  ISP routing/assignment with Bunny Factory before changing network.
  The shortener should be isolated from the private network as well,
  not simply connected to trusted Sanctum PostgreSQL services.

**Key security property: short code is now the PUBLIC BEARER TOKEN.**
A strong 128-bit file token hidden behind a public five-character
alias does **NOT** impart 128-bit unguessability to the public link:
an attacker only has to guess the shorter code.
Normal YOURLS sequential/default keywords are inappropriate for
sensitive file links. Use unambiguous, cryptographically random,
human-typeable codes with a separately chosen minimum length,
for example 12 chars from a 34-character alphabet
(~61 bits before rate limiting, limited lifetime),
or 14 chars (~71 bits); hyphen grouping is a UI option.
Shorter non-sensitive redirects may use different alias rules.
Time-based expiry, 404-throttle, and prompt alias disable/revoke
after successful transfer are necessary practical controls.

**Redirect behavior:** avoid permanent cached YOURLS `301`
redirects for one-time files; use **`302`/temporary** and
`Cache-Control: no-store` for their alias route, no logs that
reveal hidden share tokens or URLs. Public YOURLS may otherwise
create stable redirects; deleting the public alias later is not
sufficient if a browser caches a permanent redirect. Expiry/
completion **must be enforced at download target regardless of
YOURLS redirect state**, and the alias should expire/revoke too.
Ordinary link previews may request the short alias, but the actual
download service must distinguish non-consuming HEAD/prefetch from
real transfer and prevent overlapping once-only GETs.

**Integration:** owner-side upload from phone creates share's long
token and file data; owner-only service-to-service YOURLS API
shortens it and returns the short link + local QR display. Recipient
just types/scans and downloads in browser—zero extra clicks,
passwords, guest accounts or software. After full practical
server-side transfer completion, target invalidates its token;
disable/delete the redirect alias too, but retain owner-private
file bytes ~24h so Nova can issue a new link without reupload.
YOURLS's default PHP/DB stack should not be installed on existing
production Kvin alongside shared Nextcloud data if a public
DMZ/service boundary is chosen.

**Source status:** this is a design refinement / feasibility
decision, NOT public ingress approval or request to install
YOURLS and file gateway now. Review/qualify before deployment.
Earlier tentative external VPS or mandatory passphrase
suggestions are REJECTED by user.


## November 17 later — short enough to TYPE in remote Firefox is a hard usability requirement

Nova additionally requires a full link **short enough to type by hand**
on a cloud-hosted remote virtual system where he opens Firefox, in
addition to tapping/copying or presenting a QR code. A 128-character
opaque query string is **not** acceptable. Recipient must still have
a single ordinary browser action with no app/account/passphrase.

**Promising existing candidate found:** [fdrop](https://github.com/polimo-dev/fdrop),
a small open-source Go project published Aug 2026, explicitly written
for human-typed single-download URLs. Its example is
`https://f.example.com/a3k9m`; actual candidate config uses
`FDROP_ID_LENGTH` (5 default; up to 20), cryptographically
generated readable lowercase letters and digits 2–9, time expiry,
one-download cap, HTTP direct download with no confirmation, handling
of `HEAD`/recognized prefetch requests, and partial-transfer retry.
Its image supports ARM64; HTTPS requires a reverse proxy.
No deployment or security audit has been done.

**Candidate not safe to install as-is for Nova's STRONG public security:**
- Its **5-character default** offers ~25 bits and is guessable at scale.
  Use a short hostname and a **14–16-character human-typeable code**
  (~71–81 bits for a uniform 34-character alphabet), with brute-force
  throttling and short expiry, and consider groups separated by hyphens
  for humans. These lengths are a proposed design, not user's selected
  settings or a live link. Example domain must be owner controlled.
- Inspected [download handler](https://github.com/polimo-dev/fdrop/blob/main/internal/server/download.go)
  opens/checks the token, then serves the entire file via `io.Copy`
  and **only then** calls `store.Consume`. The SQL update prevents
  double *counting* but **not two overlapping transfers** from both
  successfully fetching a one-shot file. Fix via **atomic in-flight
  claim** before streaming and release on failed/aborted transfer,
  with recovery from abandoned claims after a controlled timeout.
- Current implementation purges the SQLite row **and blob** immediately
  when download cap is reached or expiry hits. User wants a spent/expired
  **token invalid immediately** but file **retained privately about
  24 hours** to reissue a *fresh* share code without reuploading.
  Separate public-token lifecycle from private blob-retention lifecycle.
  Ensure expired/orphan cleanup never deletes other services' data.
- Need convenient **QR code display**, not just visible short URL; add
  in the owner UI if missing. Admin/upload paths should be available
  only from a protected internal management channel, while only the
  direct-download path is publicly permitted by the ingress proxy.
- `io.Copy` finishing without error and the full file length being
  submitted to the HTTP response gives a practical, server-observable
  completion point, **NOT proof the browser saved the file**. TCP
  acknowledgments reflect network-stack receipt (potentially by a
  proxy), not the final application save, and server writes may be
  buffered. Disable reverse-proxy response buffering/caching for
  direct downloads; treat network aborts as retryable. HEAD/prefetch
  must not consume. Existing files are preserved as owner-only blobs.
- New tiny low-adoption repository (Aug 2026, limited public uptake),
  deserving a focused source security review before exposing ANY
  port to the Internet; existing docs/tests alone are not certification.

**Important:** This is a better functional candidate than modifying
PicoShare for one-shot link semantics. It is still just a feasibility
discovery and **not** authorization for installation, offsite hosting,
public ingress or additional unfinished Services scope.


## November 17 operator correction — HOME ONLY; ZERO RECIPIENT FRICTION

**This supersedes the external VPS/object-storage and multi-secret
recommendations below.** Nova explicitly rejected offsite hosting:
if files cannot be served from *his own network*, this service is not
worth installing. Also rejected any added recipient application,
registration, passphrase, second channel, manual decryption or other
procedure. The wanted experience is:

1. Nova selects/uploads a file from his own computer/phone.
2. Service immediately produces a share URL and a QR code for that URL.
3. Recipient taps URL or scans QR with a normal phone/browser and
   immediately downloads the file **without further questions or apps**.
4. After that ONE download the link becomes unusable (plus configurable
   expiry/revocation for files not collected). No broad public browsing
   of old shared files.
5. Network is publicly reachable over trusted HTTPS via ISP-provided
   STATIC address, but host/service has **no reachability into Sanctum
   internal management/LAN networks**. All additional protection is
   server-side; ordinary LAN services retain sensible low-friction access.

**Implementation observation from current upstream PicoShare source:**
[handlers/download.go](https://github.com/mtlynch/picoshare/blob/master/handlers/download.go)
calls `http.ServeContent` and only then `recordDownload` as a
historical download log; it does NOT atomically consume or revoke the
entry after serving. Its [metadata model](https://github.com/mtlynch/picoshare/blob/master/picoshare/picoshare.go)
has a download count but not an owner-configurable maximum downloads
per file. **PicoShare cannot be claimed to meet "exactly one GET and
invalidate" out-of-the-box.** Its built-in expiry is time-based and
the Nov16 v1.5.5 optional passphrase is an unwanted recipient step here.
We should assess either a **small isolated one-shot download gateway**
with atomic token redemption, or a narrowly scoped patch to PicoShare;
only build either if selected by Nova. A policy promise based merely
on reading a download count is subject to races and is insufficient.

**Operational nuance:** Safe handling of `HEAD`, range/resume requests,
preview/unfurl bots and retries must be designed and tested.
An unconditional first-GET consumption can allow an antivirus/link
scanner to burn a file before the real recipient clicks, or prevent
recovering a dropped mobile download. Determine whether the practical
meaning is "one started transfer" or "one completed transfer", because
they cannot always be distinguished perfectly over unreliable networks
without adding a recipient acknowledgement. No need to ask Nova to
install anything or impose a second interaction.

**Only on-premises network choices:** use a physically or logically
separate public DMZ host/segment with default-deny initiation into the
interior network, isolated storage containing only explicitly
uploaded/shareable files, no Kvin/Peanut/Wicket data mounts, private
administration/upload channel, and incoming 443 only. The existing
second static IP could be used **if** Bunny Factory establishes
real routed/address ownership; static address alone is not isolation.
The home public endpoint remains a service that can be scanned/attacked,
so keep software updated, restrict exposed HTTP routes and rate-limit
abuse. Public certificate/hostname is a server-owned convenience,
not a recipient step. Do not expose existing production Nginx/Kvin as
the default just to avoid one additional isolated container/host.

**Status:** User has specified product goals, **not approved a
deployment**; don't purchase, route/NAT, open ports or install
anything before choosing an on-premises implementation. It's still an
uncommitted future candidate, not a new blocking task for current
Kuma/LinkStack/Nextcloud commitments.

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
