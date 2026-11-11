#!/usr/bin/env bash
# Set (or correct before bootstrap) the Kuma password in the existing Vault.
# The user chooses the password. Kuma applies its own policy at account setup.
set -euo pipefail
set +x
umask 077

vault_dir="$HOME/.config/sanctum-services/secrets"
key="$vault_dir/vault.key"
target="$vault_dir/kuma-admin.vault.yml"

if [[ ! -r "$key" ]]; then
  echo "Existing Sanctum Vault key not readable" >&2
  exit 1
fi
if [[ -L "$target" || ( -e "$target" && ! -f "$target" ) ]]; then
  echo "Unexpected Kuma Vault file type; no change made" >&2
  exit 1
fi

read -rsp 'Kuma password: ' password
printf '\n'
read -rsp 'Confirm Kuma password: ' confirmation
printf '\n'

if [[ "$password" != "$confirmation" ]]; then
  echo "Passwords did not match; encrypted credential unchanged" >&2
  exit 1
fi
if [[ -z "$password" ]]; then
  echo "Password cannot be empty; encrypted credential unchanged" >&2
  exit 1
fi
echo "Passwords matched."

staging_dir="$(mktemp -d "$vault_dir/.kuma-vault.XXXXXXXX")"
cleanup() {
  unset password confirmation
  rm -f -- "$staging_dir/kuma-admin.vault.yml"
  rmdir -- "$staging_dir"
}
trap cleanup EXIT

printf '%s' "$password" |
  "$HOME/.local/bin/ansible-navigator" exec \
    --eev "$key:$key:ro,Z" \
    --exec-shell false -- \
    ansible-vault encrypt_string \
      --vault-password-file "$key" \
      --stdin-name vault_kuma_admin_password \
      > "$staging_dir/kuma-admin.vault.yml"

grep -q '^vault_kuma_admin_password: !vault |' "$staging_dir/kuma-admin.vault.yml" || {
  echo "Vault output was not valid; encrypted credential unchanged" >&2
  exit 1
}
chmod 600 "$staging_dir/kuma-admin.vault.yml"
mv -f -- "$staging_dir/kuma-admin.vault.yml" "$target"
echo "Kuma encrypted password saved. Application account unchanged."
