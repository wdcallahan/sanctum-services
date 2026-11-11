# Uptime Kuma — retained monitors and source-managed recovery

## November 11 — Kvin loopback startup accepted, initial administrator pending

**Accepted native state:** Kvin's rootless Podman Quadlet
deployment `ansible/kuma.yml -e kuma_stage_approved=true`
completed `ok=10 changed=3 unreachable=0 failed=0 skipped=1`.
Uptime Kuma 2.5.9 Linux ARM64 is installed as a
managed service, responds with HTTP **302** at
`http://127.0.0.1:13001/`, and uses named
`sanctum-kuma-data` storage at `/app/data`.
This is a successful initial HTTP startup, but
**administrator setup, actual monitor state,
reboot, backup/restore and LAN access are unproven**.
Kvar remains production; YXORP, DNS and firewalld unchanged.

The image was already separately natively qualified
(`ok=8 changed=0 failed=0 skipped=1`), with
actual Podman linux/arm64 inspection and disposable
offline Node execution. The exact digest is pinned
in `ansible/group_vars/kuma.yml`.

**SQLite is declared in source.** The Quadlet now
includes `Environment=UPTIME_KUMA_DB_TYPE=sqlite`,
supported by the
[official Kuma v2 environment documentation](https://github.com/louislam/uptime-kuma/wiki/Environment-Variables).
This eliminates an ambiguous database choice on
fresh reconstruction while retaining the local named
volume. [Source CI #43065990976 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43065990976).
The initial native install was before this setting:
**it has not yet been applied on Kvin**.

### Next: source reconciliation and true no-op repeat

On Kvin, run this single `&&` chain. The first
playbook call is expected to reconcile/restart the
user Quadlet to declare SQLite. The second
call must be **unchanged** for idempotence:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma.yml -e kuma_stage_approved=true &&
~/.local/bin/ansible-navigator run ansible/kuma.yml -e kuma_stage_approved=true
```

Return only the **two PLAY RECAP rows** and the
`msg` from the final
**Report bounded loopback Kuma candidate staging
acceptance**, or the first failed task/error.
Do not post raw application/credential logs.

### Then: administrator bootstrap from your browser

Kuma's initial administrator is a one-time
application credential setup, not a secret to
publish in the Services repo or relay in chat.
On the desktop where you will use the browser
(e.g., Mace, **not** a second shell inside Kvin),
open an SSH forwarding session to Kvin:

```bash
ssh -o ExitOnForwardFailure=yes -N \
  -L 127.0.0.1:13001:127.0.0.1:13001 \
  wdc2@kvin.outer.sanctum
```

Leave that SSH session open and navigate in the
**same desktop** browser to
`http://127.0.0.1:13001/`.
The source-pinned SQLite backend should avoid
an arbitrary remote database choice; if the
database selector still appears, choose **SQLite**,
not an unconfigured MariaDB backend. Complete the
administrator creation flow and verify login/
the actual dashboard. Keep the chosen credentials
in an operator-controlled private secret store.
**Do not manually create the Wicket monitor** in
the UI: it is already declared in
`data/kuma-monitors.yml` and belongs in
idempotent authenticated reconciliation.

A browser login is a separate acceptance gate
from localhost HTTP 302; please report only
whether the setup/login and empty dashboard
worked, and unexpected nonsecret messages
if they did not. Never share a password,
session cookie, or authentication token.

### Remaining durable application work

Next select and test a stable, version-compatible
authenticated Socket.IO interface to create/update
the declared `Wicket Ollama` monitor. The maintained
[uptime-kuma-api2](https://github.com/pbarone/uptime-kuma-api2)
wrapper supports Kuma 2 in principle, but its
published compatibility matrix is tested through
**2.5.0**, not our exact **2.5.9**. No monitor
write or direct SQLite mutation is authorized
solely by that library's existence. Reconcile by
stable identity and ensure a second run creates
no duplicates/notifications. Verify `Wicket Ollama`
genuinely **Up** in the retained Kuma UI.

Source-managed candidate-only reversal
`ansible/kuma-stage-remove.yml` is separately
default-off (`-e kuma_stage_remove_approved=true`);
it verifies the owned Quadlet, removes its
running user service and generator input, but
**preserves `sanctum-kuma-data` and the cached image**.
[Reversal CI #43064602595 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064602595).
Native reversal has not yet been exercised.
No Kvar retirement is authorized by this procedure.

Once administrator and desired monitors actually
work, independently prove restart/idempotence,
backup/restore, update/recovery and eventually
real named clients before moving the existing
`kuma.nexus.sanctum` proxy upstream from Kvar.
Avoid premature proxy diagnostics or production cutover.

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
