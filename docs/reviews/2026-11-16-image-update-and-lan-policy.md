# November 16, 2026 — Sanctum services unattended updates and LAN access policy

**Owner:** Sanctum Services for its application Quadlets and proxy; Maintenance
for host firewalls, host platform and shared PostgreSQL; Joule for Wicket and
Prism; EyesOnly for Search. **No host was changed by this source review.**

## Operator correction, not a new request

Nova expected **unattended updates for wanted services**. An immutable image
digest committed forever as the active Quadlet image, without any automatic
process advancing the deployed image, violates this requirement. Restart
policy is not update policy. No application should be fenced behind a
source-IP-only firewall rule without a specific approved reason; ordinary
intended internal clients must reach the published service using its supported
authentication. This does not mean bypass application authentication,
blindly expose the public Internet, or confuse a loopback upstream hop
with a firewall allowlist.

Historic immutable image **receipts**, synthetic test fixtures, and
images advanced by a working unattended release pipeline are distinct
from silently frozen deployed images. Do not use those distinctions
to excuse an unmaintained production service.

## Services-owned source inventory

| Service | November 16 observed source | Runtime/updating evidence | Status |
| --- | --- | --- | --- |
| Nextcloud | `group_vars/nextcloud.yml` fixed 34.0.5 image digest; Quadlet lacks `AutoUpdate` | User authenticated and saw notice for 35.0.2; **actual running version not yet rechecked** | **Open** [#5](https://github.com/wdcallahan/sanctum-services/issues/5): complete app+DB recovery first, then moving-image and unattended maintenance path |
| Uptime Kuma | `group_vars/kuma.yml` fixed 2.5.9 image digest; Quadlet lacks `AutoUpdate` | Normal Kvin usage previously accepted; **actual running image/timer not inspected here** | **Open** [#6](https://github.com/wdcallahan/sanctum-services/issues/6): protect SQLite and restore before upgrade |
| YXORP / Nginx | Was fixed SHA without `AutoUpdate`; source changed to `nginx:stable-alpine` + `AutoUpdate=registry` for source-managed production/stage | Previous 7-route Nginx acceptance; **new source not applied to Kvin and no rootful auto-update timer acceptance** | **Source CI PASSED**, eventual native activation pending; no automatic updates proven live |
| LinkStack | Recovered candidate Quadlet fixes old Kvar image digest and `Pull=never` | Restored content and current directory UI accepted; **which installed live source owns the update cadence is not verified** | **Open**: distinguish fixed-identity recovery candidate from production lifecycle; retain user data |
| Pi-hole | Old Kvin restore template fixed original digest and `Pull=never` | Nova explicitly retired it from wanted services | Exclude from update work; do not resurrect |
| EyesOnly Search (adjacent owner) | `ghcr.io/searxng/searxng:latest` + `AutoUpdate=registry` in owner Quadlet | Browser/search accepted, **timer/update history not checked by this audit** | Correct *declared* image policy; monitor owner runtime separately |

The additional `data/container-image-candidates.yml` includes tested/historic
digest identities; those are **not themselves deployed Quadlet policy**.

## Cross-owner findings

- Maintenance's owner [Quadlet inventory issue #5](https://github.com/wdcallahan/sanctum-maintenance/issues/5#issuecomment-6935782334)
  has the request for actual host/service image, mutable channel, system/user
  `podman-auto-update.timer` state and a finite active/retired classification.
  Shared PostgreSQL 18 still has exact image identity in old deployment
  source **and in new Nextcloud-only backup helper**; the backup helper
  must not become unusable after a valid future PostgreSQL patch refresh.
- Joule [network issue #9](https://github.com/wdcallahan/joule/issues/9#issuecomment-6935786809)
  has the **known obsolete** source-only Wicket Host 18096 single-Kvin
  `192.168.1.192/32` rich-rule helper, and the current Ollama Quadlet
  template `PublishPort=127.0.0.1:11434` / `Pull=never`.
  **Neither proves live restriction today**. Maintenance's Nov2 Wicket
  native proof showed **no live Host 18096 firewall restriction** and
  Kvin+Mace connected. The old helpers require source retirement.
- Maintenance Kvin host firewall #18 already accepted ordinary LAN
  8084/5432/8085 admission and removal of earlier narrow rich rules;
  do not rerun it. Postgres HBA's `192.168.0.0/16` is a full regional
  address range, **not** a single-client IP restriction.

## Native Kvin evidence after source correction (November 16, evening)

Nova ran the exact read-only inventory and reported:

- `occ status --output=json`: **Nextcloud installed 34.0.5.1 / versionstring 34.0.5**, maintenance **false**, `needsDbUpgrade=false`. This confirms the **running** app still needs its neglected update pipeline; user has successfully logged in after password reset.
- `podman ps` as **wdc2/rootless**: `sanctum-nextcloud`, `sanctum-postgresql`, `sanctum-kuma`, `sanctum-linkstack-kvin-candidate` all run fixed digests; `joule-prism` uses a local release identity; `search` runs `ghcr.io/searxng/searxng:latest`.
- User `podman-auto-update.timer` is **enabled and active**. System **rootful** `podman-auto-update.timer` is **disabled and inactive**. Only the inspected Search Quadlet has `AutoUpdate=registry`. **Not all active user services are current just because the user timer works.**
- The **actual installed system** YXORP Quadlet still specifies the historic frozen Nginx digest and lacks `AutoUpdate`. Services **source** correction to `nginx:stable-alpine` + `AutoUpdate=registry` **passed [CI 44001338860](https://github.com/wdcallahan/sanctum-services/actions/runs/44001338860)**; not applied. A future source deploy also needs enabling/qualifying the **rootful** timer, not just installing the revised Quadlet.
- The Pi-hole **rootful Quadlet file** still exists under `/etc/containers/systemd/sanctum-pihole-kvin.container`, despite Nova's retirement decision. The supplied `podman ps` enumerates **rootless** containers only: it does **not** show whether rootful Pi-hole is running, enabled at boot or gone. **Do not list Pi-hole as a wanted service;** inspect system unit safely before scoped cleanup. An old `joule-presence-restore-...` user Quadlet also remains on disk, not listed among currently running rootless containers. No cleanup has happened.
- The existing PostgreSQL user Quadlet declares `PublishPort=192.168.0.192:5432:5432/tcp`; prior native topology evidence describes Kvin as `192.168.1.192`. This is a **candidate fixed-destination-address drift**, **not** proof of an unreachable actual DB port. Maintenance owns confirming actual current host IP/interface and live `podman port` before modifying desired networking; source-address firewalls are a distinct question.

**Additional owner audit:** [Sanctum-wide exception issue #38](https://github.com/wdcallahan/sanctum-maintenance/issues/38) now tracks broader categories beyond SHA pins and /32 rules. [Joule #16](https://github.com/wdcallahan/joule/issues/16) conspicuously tracks the **rejected historical** Wicket 18096 single-client firewall helper. Actual November 2 Wicket Host restriction absence was already accepted, not contradicted.

## Further YXORP source correction — the missing SYSTEM timer

The accepted Kvin inventory showed the user's Podman updater active but the
**system/rootful** updater disabled/inactive. Simply adding
`AutoUpdate=registry` to a **rootful** YXORP Quadlet would not itself
provide unattended updates. Services has now extended the production-only
YXORP role to enable/start the **system**
`podman-auto-update.timer` **after** the proxy is deployed and checked
healthy, without touching the updater on staging/Peanut trials. Its
contract test checks rootful/system scope and that stage play does not
enable the timer. **Full source+Ansible CI passed**
[run 44005725062](https://github.com/wdcallahan/sanctum-services/actions/runs/44005725062)
at commit `3de917e6`. This is **source-only**, not a native apply; Kvin's
currently installed Nginx Quadlet and disabled system timer are **still
unchanged** as far as accepted native evidence establishes.

### Retired Pi-hole and ordinary client-file operations

Nova explicitly confirmed he **unplugged old Kvar**, chose **not to migrate
Pi-hole as a wanted service**, and does not want historical Pi-hole backup
retention as a recovery obligation. The remaining rootful Kvin Quadlet file
is stale/undesired residue to classify and retire, **not** an update target.
A rootless `podman ps` report is insufficient to prove whether that
system service is currently enabled/running; do not present it as live
without an appropriate bounded rootful observation. See supersession at
the start of [SERVICE-ESTATE.md](../SERVICE-ESTATE.md).

Nova's Nextcloud music WAV files were uploaded using his ordinary share/
application interface and may be removed through **that same
Nextcloud-managed client mechanism**. Do not propose raw backend Samba/NFS
paths without evidence or issue broad warnings against standard file
manager operations. Exact protocol has not been inspected; no deletion was
performed by this audit.

### Extended whole-fleet scope

A cross-project [priority register in Maintenance #38](https://github.com/wdcallahan/sanctum-maintenance/issues/38#issuecomment-6936521235)
now includes more than image pins and single-source firewall rules:
Kvin's inactive **system** updater, old test/boot Quadlets, actual vs
declared PG destination address, Mace scheduled update not yet installed
as documented in owner inventory, Wicket Image Mode update policy
undecided, Dragon's last-recorded unsupported Fedora 42, Kvin/Peanut HA
not yet deployed, Nextcloud missing off-host recovery and historically
rejected Wicket FPC-7 helper. Source records are **not** live confirmation.

## Actual next steps

1. YXORP source CI [PASSED at 86702ff](https://github.com/wdcallahan/sanctum-services/actions/runs/44001338860); later run a reviewed, bounded native
   rootful Quadlet/timer activation; never claim installed just from a commit.
2. One read-only Kvin actual-container/Quadlet/timer census; enumerate rootless
   and rootful update timers and source image fields without exposing secrets.
   Verify running Nextcloud via `occ status --output=json`, not notification age.
3. Finish paired Nextcloud filesystem+Maintenance owner-scoped PG dump backup,
   independently retain and restore it. Then implement user-requested
   unattended Nextcloud updates **without a frozen digest**, respecting
   snapshot and schema/Calendar preservation.
4. Bring Kuma and production LinkStack into the same unattended update policy
   with native backup/restore receipts. Remove obsolete source checks that
   explicitly demand hardcoded digests.
5. Trust real firewall/remote-API acceptance where already obtained; correct
   source that could recreate single-source rules, but **do not broadly
   flush firewalls or invent current outages from dormant code**.
