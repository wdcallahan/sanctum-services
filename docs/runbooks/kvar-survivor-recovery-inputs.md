# Kvar survivor recovery inputs — LinkStack and Pi-hole

## November 11 native Kvar receipt — both live survivors, image identity metadata incomplete

Nova ran `ansible/kvar-survivors-source.yml` on Kvin against Kvar, **`ok=8 changed=0 failed=0 unreachable=0`**. Each named service was confirmed **running**, Quadlet `loaded/active/generated`, with source files on Kvar. No application state, passwords or volume contents were read and no host/app configuration was changed.

| Service / account | Running container image reference and observed image ID | Writable volumes | Kvar published ports |
|---|---|---|---|
| Rootless `linkstack`, `wdc2` | `docker.io/linkstackorg/linkstack:latest`; `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65` | `linkstack` → `/htdocs` | TCP 8081 → 80 |
| Rootful `pihole`, `root` | `docker.io/pihole/pihole:latest`; `edb7f703649f4b6ab8b14f28d12f15e8cbe1c50a2092458e9b640bd6bc6fe59e` | `systemd-pihole_etc-pihole` → `/etc/pihole`, `systemd-pihole_etc-dnsmasq` → `/etc/dnsmasq.d` | TCP/UDP 53 → 53 and TCP 82 → 80 |

Both bounded results had `status: partial`, although `service_unit.status: observed`. The reason is the **additional local image inspection did not yield accepted `image_platform` and `repo_digests`**, not that either container is unavailable. `latest` is mutable and the displayed container image ID is **not** proof of a Kvin-pullable immutable reference. No image pull, service restart, backup, data movement, DNS or proxy change is authorized by this observation.

**Follow-up source correction:** `tools/observe-kvar-survivors.py` now explicitly reports only sanitized image-inspection outcome categories. It first queries the exact observed container image ID; if unavailable, it tries the existing local image tag, **accepting that result only if its image ID equals the running container's ID**. A newer local `latest` tag must not be used to reconstruct the wrong image. A missing repository digest remains `partial`. The updated source tests cover all of these failure modes. Once CI is green, the next read-only native rerun can report a specific image-probe result rather than an unexplained `partial`. Do not re-run any broad retirement inventory.

## Why this one read-only observation exists

Sanctum Services [issue #2](https://github.com/wdcallahan/sanctum-services/issues/2)
retains the actual Kvar **LinkStack directory** and **Pi-hole ad blocker**.
Both are to be reconstructed on Kvin with their wanted data and recoverable
configuration. The previously accepted Maintenance inventory already
identified Kvar's LinkStack rootless named volume `linkstack` mounted at
`/htdocs`, and rootful Pi-hole configuration volumes. **Do not rerun that
broad inventory.**

The remaining source input gap is the *currently effective image reference,
immutable image identity, selected port and mount declarations, and service
unit / Quadlet source* for each survivor. A previous backing report knew
image IDs but not a documented, operator-reconstructible application
lifecycle. This step collects only the missing implementation inputs.
No automatic restore, replacement image selection or data migration is
authorized merely because a container appears present.

## Supported command (run on Kvin, after Services CI passes)

This single Ansible Navigator playbook uses the current Services inventory's
existing Kvar SSH management port (10022). The first play inspects only
the named `linkstack` container as connection user `wdc2`; the second
inspects only the named `pihole` container with root privileges. No
application file contents, SQLite, environment variables, password values,
logs, proxy configuration or tokens are queried. Every subprocess is a
fixed bounded `podman container/image inspect` or fixed `systemctl show`
query. Raw observation output is suppressed until strict bounded
metadata parsing succeeds.

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kvar-survivors-source.yml
```

Expected: both plays finish `failed=0 changed=0` and report exactly
`Report bounded LinkStack image and backing discovery` and
`Report bounded Pi-hole image and backing discovery`.
Share these two **`msg`** dictionaries and the single aggregate `PLAY RECAP` row for Kvar.
Do not share full Podman inspect output or application secrets.

The bounded report includes the observed container state, image
reference/ID, any repository digests, selected mount destinations and
volume names (not bind source paths), selected host port mappings,
and safe unit status / recognized Quadlet source path.
A `partial` status is useful evidence of an unresolved assumption;
do not make up unknown values or install an image on that basis.
If either play fails, report the failed task instead of attempting
ad-hoc container changes.

## What this does NOT do

It is an observation, not a backup. The service remains running;
neither volume is exported, copied, mounted or modified. The resulting
image ID is useful identity evidence but **not** automatically a
qualified pullable immutable image. Registry manifest, architecture,
version, persistence and service lifecycle must be qualified together
before source-owned replacement is written.

LinkStack backup must quiesce or otherwise prove consistency of the
actual `/htdocs` state, keep the Kvar instance intact, restore to an
isolated Kvin volume and verify recognizable directory pages/assets
and editing when applicable. Pi-hole must keep its actual configuration
volumes, avoid claiming general LAN DNS ownership, and prove opt-in
filtering from a deliberately selected client. No current household
client is intentionally using Pi-hole per the accepted November DHCP
transition; do not reopen dormant-client discovery.

Both native application migrations, recovery rehearsals, live YXORP
backend changes and Kvar retirement remain separately authorized.
The already accepted Kuma named browser/WebSocket cutover does not
establish LinkStack or Pi-hole readiness.
