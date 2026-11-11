# Uptime Kuma — retained monitors and source-managed recovery

## November 11 — rootless Kuma and SQLite converged; native administrator bootstrap next

**Native acceptance:** The Kvin-only, source-owned
Uptime Kuma 2.5.9 image was independently accepted
as Linux/ARM64 with offline Node runtime.
Its rootless Kuma Quadlet uses the exact pinned
digest, a named `sanctum-kuma-data` volume mounted
at `/app/data`, `127.0.0.1:13001` host binding,
and `Environment=UPTIME_KUMA_DB_TYPE=sqlite`.
Native application stage succeeded with `ok=10
changed=3 failed=0`; SQLite source reconciliation
then succeeded `ok=9 changed=2 failed=0`,
followed immediately by **`ok=9 changed=0 failed=0`**.
An SSH-tunneled Firefox browser reached both
the actual database-selection and create-admin
screens. These are bounded startup/real UI
observations; no account has been confirmed
created, no monitor Up, no restart/recovery
acceptance and no Kvar/DNS/firewall/YXORP changes.

### Administrator creation is source-managed, not a manual wizard

Nova asked why creating the administrator had
been left to browser interaction. It should
not have been. **Kuma 2.5.9** exposes
`needSetup`, `setup(username,password,ack)`,
and `login` over Socket.IO, confirmed directly
in the tagged upstream server implementation
and Vue admin setup page. Kuma refuses
the first-user setup event after a user exists.

The separately guarded `ansible/kuma-admin-bootstrap.yml`
uses these exact events via the `socket.io-client`
dependency included in the pinned image.
It runs a temporary Node process **inside**
the running rootless Kuma container, connecting
only to container-local `127.0.0.1:3001`.
It first checks `needSetup`; for an uninitialized
instance only, creates a random credential and
uses Kuma's own setup API, then independently
calls login. On repeat, it verifies that same
account and makes no changes. If Kuma was
manually initialized without the owned secret,
it refuses to override or reset an unknown user.

The private credential:
- Fixed nonsecret username `sanctum-admin`
- A random password generated with Python's `secrets`
  library, in `/home/wdc2/.config/sanctum-services/secrets/kuma-admin.json`
- Secret directory `0700`, file `0600`, created
  exclusively, never overwritten
- Sent to a container-local socket process via
  stdin, not in command arguments, public YAML,
  CI fixtures, Ansible output or this conversation
- Must later be backed up **off Kvin**, alongside
  a proven and independently restorable Kuma
  `sanctum-kuma-data` volume

Source contract, real-Node simulated protocol
and full [CI #43072165068 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43072165068).
**No native admin operation has yet been run.**

**Next one operator command from Kvin:** explicitly
authorize admin initialization and immediately
verify an unchanged repeat, without displaying
any password or authentication token.

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma-admin-bootstrap.yml \
  -e kuma_admin_bootstrap_approved=true &&
~/.local/bin/ansible-navigator run ansible/kuma-admin-bootstrap.yml \
  -e kuma_admin_bootstrap_approved=true
```

Return only the **two PLAY RECAP** rows and
the final `msg` dictionary from
**Report only safe administrator bootstrap acceptance**,
or a failed task and error. Do not paste
private task output, secret JSON, cookies or tokens.
The first run may create the credential and account;
the second should be `changed=0` and report
`administrator_login_verified:true`.

After native success, the browser's existing SSH
forward can be used to log in. To retrieve the
generated credentials **only on Kvin in a private
terminal**, without embedding the password in
shell history:

```bash
python3 - <<'PY'
import json
from pathlib import Path
secret = json.loads(
    (Path.home() / ".config/sanctum-services/secrets/kuma-admin.json").read_text()
)
print("Username:", secret["username"])
print("Password:", secret["password"])
PY
```

Move them to your own password manager and
arrange an off-host encrypted backup.
The password will be displayed in that local
terminal deliberately; **never paste it into
a chat or Git issue**. Access the existing
SSH tunnel at `http://127.0.0.1:13001/`
and verify login/dashboard. Do not create
the wanted monitors manually.

### Subsequent useful service gates

`data/kuma-monitors.yml` already declares
`Wicket Ollama`. Select a source-owned
idempotent Socket.IO monitor reconciler
against actual Kuma **2.5.9**, including
the correct admin auth and monitor payload.
A community wrapper (`uptime-kuma-api2`)
is a candidate, but its published tests
stop at 2.5.0; check real 2.5.9 behavior
before accepting monitor mutations.
Test the displayed Up state, unchanged
repeat, no duplicate notifications,
restart, off-host backup/independent restore,
version updates and candidate reversal.
Only after application and proper named
client acceptance should the incumbent
Kvar route be retargeted and independently
accepted. No production cutover yet.

The source-managed Kuma candidate-only reversal
is `ansible/kuma-stage-remove.yml`, separately
default-off and validated to preserve the data
volume and image; its source CI passed but native
reversal has not yet been exercised.

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
