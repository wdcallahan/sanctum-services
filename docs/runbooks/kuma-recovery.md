# Kuma — consistent backup and isolated restore trial

## Native recovery trial ACCEPTED — November 11, 2026

Nova executed the actual Kvin guard-approved playbook:
**`ok=49 changed=11 failed=0 skipped=0`**.
Source-qualified outcome: original user service
restarted; local HTTP and Vault login worked;
exported SQLite data passed integrity checks;
an isolated, no-network real Kuma started from
the imported copy, authenticated the existing
Vault administrator and returned the saved
Wicket monitor through its native socket API.
The disposable restored container and test volume
were removed.

**Retained private Kvin archive:**
`/home/wdc2/.local/share/sanctum-services/backups/kuma/sanctum-kuma-20261111t144137.tar`,
290816 bytes, SHA-256
`97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648`.
No Kvar/production/proxy route change.

**Recovery still incomplete:** no independent
off-host copy, no verified independent
restoration of external `vault.key` and
`kuma-admin.vault.yml`, no permanent
recovery automation for a replacement Kvin.
This local artifact is a working backup,
not a second-machine disaster recovery.

**Status:** source prepared, not yet natively executed. This procedure
is for the retained Uptime Kuma 2.5.9 on Kvin; it does **not** touch
the incumbent Kvar proxy/monitoring service.

## Accepted prerequisites

The November 11 native results established: rootless Kvin Kuma,
Vault-managed `sanctum-admin`, unchanged second administrator
bootstrap, and an idempotent `Wicket Ollama` monitor (ID 1),
reporting actual **Up** from Kuma's own persisted heartbeats.
The most recent monitoring acceptance was `ok=13 changed=0 failed=0`,
`action:unchanged`, `actual_up_accepted:true`, 12 heartbeats in
the preceding hour, latest only 17 seconds old, no alert subscriptions.
This is now **banked evidence**; do not repeat it merely to make a backup.

## What the backup/restore trial does

`ansible/kuma-backup-restore-trial.yml` is default-off and requires
`kuma_backup_restore_trial_approved=true` on exact
`kvin.outer.sanctum` as `wdc2`. It uses the **existing**
external Ansible Vault files, never generates another password.
The operation **briefly interrupts the new Kvin Kuma service**:
it stops the rootless user unit, exports the stopped
`sanctum-kuma-data` Podman volume to a private owner-only tar,
and **always starts the original user service again**, including
after an export failure. It verifies the original HTTP response
and Vault login after restart.

An archive is not counted as recovered state without validation.
The playbook checks SQLite integrity, the administrator record,
the exact Wicket monitor and no notification subscriptions.
It creates a uniquely named **separate** rootless volume, imports
the archive into that empty volume (never into the retained
`sanctum-kuma-data`), and starts a second container from the
pinned image with **`--network none`**, **no published port**.
It verifies that the restored copy actually serves HTTP, that
the preexisting Vault credentials authenticate **without creating
a new account**, and that Kuma's own authenticated Socket.IO
read still returns the saved Wicket configuration. The
isolated container and test volume are removed afterward;
the source-owned private archive survives.

The trial intentionally does **not** enable new notifications,
change DNS/firewall/reverse proxy or touch Kvar. Expect a
short, deliberate monitoring gap during consistent export.
The test instance is network-disconnected and cannot send
notifications or poll the real endpoint.

## Single operator command, on Kvin

Review the short interruption above before running.
The command is held until source CI passes.

```bash
cd ~/src/sanctum-services &&
git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
~/.local/bin/ansible-navigator run ansible/kuma-backup-restore-trial.yml \
  --eev "$vault_dir/vault.key:$vault_dir/vault.key:ro,Z" \
  --eev "$vault_dir/kuma-admin.vault.yml:$vault_dir/kuma-admin.vault.yml:ro,Z" \
  --senv "ANSIBLE_VAULT_PASSWORD_FILE=$vault_dir/vault.key" \
  --pae false \
  -e kuma_backup_restore_trial_approved=true
```

Return the `PLAY RECAP` and bounded
**Report bounded live restart and isolated Kuma backup recovery**
`msg` (or failed task and error). The backup tar's
path, SHA-256 and byte count can be shared; no private contents,
cookies, Vault secrets, raw SQLite or password hashes.

## Backup storage and real disaster recovery

A validated private archive is written to:

`/home/wdc2/.local/share/sanctum-services/backups/kuma/`

Its filename includes the run timestamp; it is owner-only
(`0600`) inside a `0700` directory. Re-runs never
overwrite a previous archive. If a trial aborts, a
private `.partial` file may remain; that is **not**
a validated backup. The original app should have been
restarted by the `always` block; if the stop/restart
task failed, review that failure first.

**A file retained on Kvin is not disaster recovery.**
The next separate acceptance must copy the archive
off Kvin to an independently retained destination
(such as Peanut), verify its SHA-256 there, and
independently preserve the encrypted `kuma-admin.vault.yml`
and existing `vault.key` through approved access-controlled
backup. Only then can replacement-machine recovery be claimed.
No off-host copy or secret-recovery verification is currently accepted.

Official Podman references:
[volume export](https://docs.podman.io/en/stable/markdown/podman-volume-export.1.html)
and [volume import](https://docs.podman.io/en/latest/markdown/podman-volume-import.1.html).
Podman's import merges into an **existing** volume, which is
why the playbook creates a new empty isolated test volume,
rather than running import against any live data.
