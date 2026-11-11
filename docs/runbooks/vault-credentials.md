# Private Sanctum Vault credentials

## One existing Vault unlock secret

Sanctum Services already used the external Vault password file
`/home/wdc2/.config/sanctum-services/secrets/vault.key` for a private
Nextcloud PostgreSQL variable file. **Do not generate a second Vault master
password or replace this existing key.** It is plaintext by design,
owner-readable only (0600); its separate encrypted files each contain
different per-service passwords. Ansible Vault is encryption at rest, not
a defense against a compromised controller that can also read the key.

The project `ansible.cfg` points at the existing key. The
`ansible-navigator.yml` execution environment deliberately does
**not** mount this private directory for every unrelated playbook:
the real controller on Kvin and the EE are different filesystems.
For **Vault-aware commands only**, pass `--eev` with a
scoped explicit mount of that private directory. The directory
must already exist on the host. Podman on SELinux-enforcing Fedora
may require a relabel (`:Z`), which changes SELinux context
on the files beneath that directory. Do not apply `:Z` to an
arbitrary home directory or a broadly shared secret store.
The separate Kvin-only secret directory is intentionally small.

## One-time operator action: create the encrypted Kuma password variable

From Kvin, choose a strong **service-specific** password privately.
Only the *Vault unlock key* is reused from the existing service.
The `ansible-vault encrypt_string --stdin-name` command reads
the password on stdin, not as a command-line argument.
`umask 077` makes the new encrypted file owner-only.
The command below uses the already installed Navigator and EE.
Run it from the project directory:

```bash
cd ~/src/sanctum-services
umask 077
vault_dir="$HOME/.config/sanctum-services/secrets"
test -r "$vault_dir/vault.key" || { echo "Existing Vault key missing" >&2; false; }
read -rsp 'Choose Kuma admin password: ' kuma_password
printf '\n'
printf %s "$kuma_password" |
  ~/.local/bin/ansible-navigator exec \
    --eev "$vault_dir:$vault_dir:ro,Z" \
    --exec-shell false -- \
    ansible-vault encrypt_string \
      --vault-password-file "$vault_dir/vault.key" \
      --stdin-name vault_kuma_admin_password > "$vault_dir/kuma-admin.vault.yml"
unset kuma_password
chmod 600 "$vault_dir/kuma-admin.vault.yml"
```

Check the output file format **without decrypting or printing its
contents**: its first line should be
`vault_kuma_admin_password: !vault |`.
If the command failed, **do not execute the bootstrap**;
report the nonsecret failure. The generated encrypted file
contains one variable named `vault_kuma_admin_password`,
used exclusively by `ansible/kuma-admin-bootstrap.yml`.
No plaintext local secret file is generated, and nothing
is checked into Git.

To rotate a credential **after** installation, editing
`vault_kuma_admin_password` is not enough to authenticate
to an account using the old credential. Rotation requires
a separate source-managed, explicitly authorized operation
that can authenticate with the current password and apply
the proposed new one. Until that operation is implemented
and tested, the bootstrap refuses a mismatch rather than
silently resetting an account. Keep a retrievable previous
password when planning rotations.

## Native Kvin bootstrap (after encrypted file exists)

The Ansible Navigator command mounts the existing secret
directory read-only into the selected EE and uses
`ansible.cfg`'s Vault password file:

```bash
cd ~/src/sanctum-services &&
git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
~/.local/bin/ansible-navigator run ansible/kuma-admin-bootstrap.yml \
  --eev "$vault_dir:$vault_dir:ro,Z" \
  -e kuma_admin_bootstrap_approved=true
```

For a second run (no change), repeat the same native command.
The playbook loads the out-of-repository encrypted
`kuma-admin.vault.yml` from the controller, checks exact Kvin
and the source-owned Kuma 2.5.9 Quadlet, invokes the existing
upstream Socket.IO first-user `setup` only if needed, then
independently verifies login with `no_log`. It does not
create local JSON secrets, mutate DNS, edit SQLite directly,
install monitors, or change Kvar.

**Recovery:** Preserve encrypted variable files and the
Vault password file as independent, access-controlled,
off-host backups. A restored server must have the encrypted
files *and* the correct vault.key available to its Ansible
controller; a Git checkout alone is insufficient. An
independent restore is not yet accepted.
