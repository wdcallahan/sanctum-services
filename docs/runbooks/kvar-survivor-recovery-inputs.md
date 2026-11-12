# Kvar survivor recovery inputs — LinkStack and Pi-hole

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
Share these two **`msg`** dictionaries and both `PLAY RECAP` rows.
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
