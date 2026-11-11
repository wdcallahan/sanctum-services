# Uptime Kuma — retained monitors and source-managed recovery

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
