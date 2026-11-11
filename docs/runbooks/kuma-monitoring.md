# Uptime Kuma — retained monitors and source-managed recovery

## November 11 — Actual Kvin admin no-op and first Wicket monitor created

Native Kvin provided two exact acceptance outputs:
- The repeated Vault-backed admin bootstrap:
  **`ok=12 changed=0 failed=0`**. No account
  creation/replacement or password rotation.
- The separately approved first Wicket monitor
  reconcile: **`ok=11 changed=1 failed=0`**,
  `action:created`, `monitor_id:1`,
  `configuration_persisted_and_verified:true`,
  `notifications_attached:false`. Its
  desired URL is
  `http://wicket.arcane.sanctum:11435/healthz`,
  HTTP GET every 60 seconds, expected HTTP
  200–299. The report says
  `actual_up_accepted:false` because **no
  heartbeat was measured**, not because an
  actual Down result was observed. The
  existing Kvar service/proxy is unchanged.

### Next Kvin acceptance — actual heartbeat plus monitor no-change repeat

An update to `tools/kuma-reconcile-monitors.js`
uses tagged Uptime Kuma 2.5.9's own read-only
authenticated Socket.IO `getMonitorBeats`
event, specifically **monitor ID 1**,
after the source-owned monitor config
has been independently re-read.
The updated `ansible/kuma-monitors.yml`
reports Kuma's actual most recent status,
number of beats seen in the last hour and
age of the latest heartbeat. It marks
`actual_up_accepted:true` only when the
latest beat is Up and recent (within 180
seconds). This is not a controller-side curl,
not a fabricated Up result, and not a
server configuration mutation. Passwords
and tokens remain private.

From Kvin, after confirming the latest
source CI pass:

```bash
cd ~/src/sanctum-services &&
git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
~/.local/bin/ansible-navigator run ansible/kuma-monitors.yml \
  --eev "$vault_dir/vault.key:$vault_dir/vault.key:ro,Z" \
  --eev "$vault_dir/kuma-admin.vault.yml:$vault_dir/kuma-admin.vault.yml:ro,Z" \
  --senv "ANSIBLE_VAULT_PASSWORD_FILE=$vault_dir/vault.key" \
  --pae false \
  -e kuma_monitors_approved=true
```

Expected monitor repeat: `changed=0`
with `action:unchanged`, no duplicate
monitor or attached notification, and
bounded `latest_status_in_kuma`,
`heartbeat_age_seconds`,
`actual_up_accepted`. Return only
the `PLAY RECAP` and
`Report bounded Wicket monitor configuration acceptance`
`msg` (or a failed task).
A successful repeat plus current Up
will close the initial live monitoring
gate, **not** backup/restore, restart,
update, named client or production.

## November 11 — Wicket monitor reconciliation source green; native test next

Native Kuma administrator creation and Vault-backed login
are accepted (`ok=12 changed=1 failed=0`,
`administrator_created_this_run:true`,
`administrator_login_verified:true`). The separate
unchanged admin repeat has not yet been run.

An explicit, default-off monitor playbook now exists:
`ansible/kuma-monitors.yml`, backed by
`tools/kuma-reconcile-monitors.js`. It uses the
actual tagged **Kuma 2.5.9** authenticated
Socket.IO methods to create, read or update only
the `Wicket Ollama` monitor already declared in
`data/kuma-monitors.yml`; it refuses duplicates
and preexisting attached notifications. No
new alert subscriptions, SQLite direct changes,
proxy routing, firewall or Kvar changes are part
of this playbook. It reports the verified saved
configuration, not a fabricated Up status.
[Full source CI #43082780801 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43082780801).
The monitor has **not** been natively created.

### Next Kvin operator action — admin repeat + first Wicket reconcile

From Kvin, use this one Bash chain. It reads
the **same existing** Vault key and encrypted
Kuma credential file without exposing secrets.
The first play should finish unchanged and
verify login; the second explicitly authorizes
only the wanted Wicket monitor.

```bash
cd ~/src/sanctum-services &&
git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
nav="$HOME/.local/bin/ansible-navigator" &&
options=(
  --eev "$vault_dir/vault.key:$vault_dir/vault.key:ro,Z"
  --eev "$vault_dir/kuma-admin.vault.yml:$vault_dir/kuma-admin.vault.yml:ro,Z"
  --senv "ANSIBLE_VAULT_PASSWORD_FILE=$vault_dir/vault.key"
  --pae false
) &&
"$nav" run ansible/kuma-admin-bootstrap.yml "${options[@]}" \
  -e kuma_admin_bootstrap_approved=true &&
"$nav" run ansible/kuma-monitors.yml "${options[@]}" \
  -e kuma_monitors_approved=true
```

Return **both PLAY RECAP lines** and the
`msg` dictionary from **Report bounded
Wicket monitor configuration acceptance**,
or failed task/error, not secret logs.

Expected results: first play `changed=0`,
login verified and no account created; second
play may create the monitor, then re-read
its persisted config. The monitor's actual
**Up** status is separately accepted after
running inside retained Kuma. A later monitor
repeat must have `changed=0` with no
duplicate or attached notifications.

Independent backup/restore of the Kuma volume
and Vault data, restart/update lifecycle and
real named client/proxy reachability remain
unaccepted. Kvar NPM/Kuma and production
routes must not change as side effects.

## November 11 — native Vault-backed administrator creation accepted

Nova's first approved `ansible/kuma-admin-bootstrap.yml`
run returned **`ok=12 changed=1 failed=0 skipped=0`**.
The bounded report independently proved that Kuma
**created `sanctum-admin` and verified actual login**
using the already encrypted private Vault value:
`administrator_created_this_run:true`,
`administrator_login_verified:true`,
`encrypted_credentials_loaded:true`. It
generated or modified no credential and
did not change proxy, Kvar or production.
The earlier intentionally bad password
test is historical; a real user-chosen
Vault password succeeded. **Do not run
the setup wizard or reset the account.**

**Next: no-change administrator bootstrap repeat.**
Use the exact command in
[the Vault credential runbook](vault-credentials.md)
one more time. It should return
`changed=0`, `administrator_created_this_run:false`,
`administrator_login_verified:true`.
This verifies existing-account authentication
without account recreation or Vault mutation.

After that, build and prove the wanted
`Wicket Ollama` monitor through Kuma 2.5.9's
authenticated Socket.IO `getMonitorList`, `add`
and `editMonitor` interfaces; source declarations
exist at `data/kuma-monitors.yml`. Exact Up status,
restart, no duplicate notifications, off-host
Vault + data backup/restore and actual named
client access are still open. No live cutover.

## November 11 — native Kuma startup and SQLite repeat accepted, Vault administrator next

**Banked Kvin results:** Qualified Linux/ARM64 Uptime Kuma
2.5.9; first guarded rootless app stage passed
`ok=10 changed=3 failed=0` with HTTP 302 at
`127.0.0.1:13001` and named `sanctum-kuma-data`
mounted at `/app/data`. SQLite configuration
converged `ok=9 changed=2 failed=0` followed
by an unchanged repeat `ok=9 changed=0 failed=0`.
A real SSH-tunneled Firefox browser reached the
live database setup and admin setup screens.
Administrator creation, actual monitors, backup,
restore, LAN and production use remain unproven.
Kvar and YXORP are unchanged.

### Administrator credentials — existing Vault authority

Do **not** complete the administrator wizard or run
the old random-secret bootstrap; user feedback
rightly requires reconstructible source-managed
credential authority. Kvin already has an
established Ansible Vault password file at
`/home/wdc2/.config/sanctum-services/secrets/vault.key`
from the earlier Nextcloud PostgreSQL work. It
must be **reused, not reset**. The service-specific
Kuma password belongs in an independently encrypted
file `kuma-admin.vault.yml` outside the Git checkout.

Read the exact [Sanctum Vault credentials
runbook](vault-credentials.md). Its first
operator command creates the encrypted Kuma
variable with your chosen password privately,
without placing the value in history or output
and without overwriting existing credentials.
Run it from Kvin and report only its success
marker or nonsecret failure.

Once the encrypted file exists, the same runbook
contains the separate explicitly approved
`ansible/kuma-admin-bootstrap.yml` native
command using **two read-only, file-only
Navigator mounts**, a run-local Vault password
source, and disabled playbook artifacts.
Kuma's official 2.5.9 Socket.IO events perform
first-user setup and login verification, with
all authentication content under `no_log`.
A repeat must verify existing login with
`changed=0`; preexisting unknown admin is
not reset. The password is neither generated
nor persisted separately by the playbook.

[Full source CI #43076965704 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43076965704).
**Native Vault-aware administrator initialization has
not yet been performed.** An external Vault file
and its key also require independent, access-controlled
off-host recovery copies. A Git checkout cannot
recreate private credential material.

### Next application qualifications

After the first account is genuinely created,
verify browser login via the existing loopback
SSH tunnel, then implement source-managed,
idempotent, authenticated monitor reconciliation
for `Wicket Ollama` using Kuma 2.5.9's
actual Socket.IO behavior. Verify actual Up,
repeat/no duplicates, restart and independent
backup/restore before considering moving
`kuma.nexus.sanctum` from Kvar to Kvin.

**Password rotation is not yet implemented.**
Changing `vault_kuma_admin_password` in the
encrypted file does not make Kuma automatically
change an established password. That requires a
separate, safely authenticated and explicitly
approved application mutation. Existing account
mismatch fails closed; do not directly edit SQLite.

Kuma's separately approved candidate reversal is
source-owned as `ansible/kuma-stage-remove.yml`;
it preserves the named data volume and cached
image and has only source, not native, reversal
acceptance. Kvar production remains unchanged.

## Project Joule request

The [Wicket Ollama monitor request](https://github.com/wdcallahan/sanctum-services/issues/4)
is captured as a stable entry in `data/kuma-monitors.yml`:

- Name: `Wicket Ollama`
- HTTP URL: `http://wicket.arcane.sanctum:11435/healthz`
- Expected response: 200–299; actual Kuma UI state must show **Up**
- Probe location: the **retained** Uptime Kuma instance after its Kvin
  deployment/restore and networking have been accepted.

This is Project Joule's service health contract. Services owns only Kuma.

## Adoption conditions

The Kvar Kuma instance was a proof of concept; the operator allows a clean
retained Kvin instance instead of requiring migration of the old monitor
database. Do not change abandoned test installations or accidentally send
duplicate alerts. Preserve wanted state in code and verify persistent
monitor state after disaster restore.

Uptime Kuma's documented REST surface is not a universal monitor-write API.
Monitor creation/editing commonly uses authenticated Socket.IO and may vary
between Kuma versions. Select an actual version-qualified, testable
reconciliation interface before coding monitor mutations. Avoid direct SQLite
editing and do not put credentials into Git.

When Kuma is managed properly, load these declarations, reconcile by stable
monitor identity (not an unconditional add), and verify both a second
unchanged run and an actual **Up** observation in the retained instance.
A successful curl from the controller alone does not meet that acceptance.
