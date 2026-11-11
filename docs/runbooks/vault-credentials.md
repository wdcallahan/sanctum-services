# Private Sanctum Vault credentials

## One existing Vault unlock secret

Sanctum Services already used the external Vault password file
`/home/wdc2/.config/sanctum-services/secrets/vault.key` for a private
Nextcloud PostgreSQL variable file. **Do not generate a second Vault master
password or replace this existing key.** It is plaintext by design,
owner-readable only (0600); its separate encrypted files each contain
different per-service passwords. Ansible Vault is encryption at rest, not
a defense against a compromised controller that can also read the key.

The project does **not** configure a global Vault password
source. Ordinary Services playbooks, CI and controllers that
lack the private Vault key must remain operational.
Vault-aware Navigator commands explicitly set
`ANSIBLE_VAULT_PASSWORD_FILE` inside the EE and mount
**only the two required files**, read-only, not the entire
secret directory. Podman on SELinux-enforcing Fedora may
require `:Z` relabeling: it changes the SELinux context of
the mounted file. Never apply `:Z` to an entire home
directory or unrelated credentials. No secret file is
committed to this repository.

## Choose or correct the encrypted Kuma password

Kuma is a home-lab service. Sanctum imposes **no arbitrary
16-character password rule**. Choose the service password you want;
Uptime Kuma 2.5.9's actual first-user setup decides whether it
accepts it.

The user enters the password **twice**, locally. Both prompts hide
typed characters (normal terminal password entry), but the script
confirms the values match before encrypting anything. The script
uses the **existing Vault unlock file** and writes only the encrypted
`kuma-admin.vault.yml`, outside Git. This is also safe to use when
correcting the one-entry file made by the earlier workflow,
**provided Kuma's administrator has not yet been initialized**.

From Kvin after pulling the latest Services code:

```bash
cd ~/src/sanctum-services && git pull &&
bash tools/kuma-set-vault-password.sh
```

You'll see **Kuma password:** and **Confirm Kuma password:**
followed by **Passwords matched.** and
**Kuma encrypted password saved. Application account unchanged.**

When they differ, the existing encrypted file is left untouched.
The script writes the new encryption to a private temporary file and
moves it into place only after encryption succeeds. No plaintext
password is stored in the repository, printed to the screen, passed
as a command argument or saved to the host disk.

**Changing a vaulted password after Kuma has been initialized
does not itself rotate the application password.** Do not run
this password-setting script as a rotation procedure once the
administrator exists. A separately authenticated, explicitly
approved Kuma rotation is still future work.

## Native Kvin bootstrap (after encrypted file exists)

The Ansible Navigator command mounts the existing secret
key and encrypted Kuma credential file read-only into the
selected EE, sets its Vault password source only for this
run, and disables playbook artifact generation:

```bash
cd ~/src/sanctum-services &&
git pull &&
vault_dir="$HOME/.config/sanctum-services/secrets" &&
~/.local/bin/ansible-navigator run ansible/kuma-admin-bootstrap.yml \
  --eev "$vault_dir/vault.key:$vault_dir/vault.key:ro,Z" \
  --eev "$vault_dir/kuma-admin.vault.yml:$vault_dir/kuma-admin.vault.yml:ro,Z" \
  --senv "ANSIBLE_VAULT_PASSWORD_FILE=$vault_dir/vault.key" \
  --pae false \
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
