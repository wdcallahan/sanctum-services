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
| YXORP / Nginx | Was fixed SHA without `AutoUpdate`; source changed to `nginx:stable-alpine` + `AutoUpdate=registry` for source-managed production/stage | Previous 7-route Nginx acceptance; **new source not applied to Kvin and no rootful auto-update timer acceptance** | Source correction **pending CI + eventual native activation**; no automatic updates proven live |
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

## Actual next steps

1. Finish current YXORP source CI and later run a reviewed, bounded native
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
