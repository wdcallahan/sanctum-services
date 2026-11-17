#!/usr/bin/env bash
# Permanently retire the separately restored rootful Pi-hole on Kvin.
# Operator-authorized November 16, 2026. No Kvar access; no DNS/proxy edits.
# This intentionally deletes Pi-hole's local durable rootful volumes and
# retained local Pi-hole archive directory. It cannot be undone without
# reinstalling Pi-hole from scratch, as Nova selected.
set -Eeuo pipefail

fail() { printf 'REFUSED: %s\n' "$*" >&2; exit 1; }

[[ "$(hostname -f)" == "kvin.outer.sanctum" ]] ||
  fail "This is exclusively for Kvin (kvin.outer.sanctum)."
[[ "$(id -u)" == "0" && "${SUDO_USER:-}" == "wdc2" ]] ||
  fail "Run this once on Kvin as wdc2 via sudo; never on another host."

unit="sanctum-pihole-kvin.service"
quadlet="/etc/containers/systemd/sanctum-pihole-kvin.container"
container="sanctum-pihole-kvin"
volume_etc="sanctum-pihole-etc-20261112t161524"
volume_dns="sanctum-pihole-dnsmasq-20261112t161524"
archive_dir="/home/wdc2/.local/share/sanctum-services/backups/pihole"

# Match the exact standalone old Pi-hole declaration before stopping anything.
# If this file changed to describe a different application, fail safely.
if [[ -e "$quadlet" || -L "$quadlet" ]]; then
  [[ -f "$quadlet" && ! -L "$quadlet" ]] ||
    fail "Unexpected Quadlet file type; no changes made."
  grep -Fxq "ContainerName=$container" "$quadlet" ||
    fail "Quadlet no longer declares the expected Pi-hole container."
  grep -Fxq "Volume=$volume_etc:/etc/pihole:Z" "$quadlet" ||
    fail "Quadlet no longer declares the known Pi-hole config volume."
  grep -Fxq "Volume=$volume_dns:/etc/dnsmasq.d:Z" "$quadlet" ||
    fail "Quadlet no longer declares the known Pi-hole dnsmasq volume."
fi

printf 'Retiring rootful %s on Kvin...\n' "$unit"

# Generated Quadlet units have no persistent disable flag. Stopping the service,
# removing its generator input, then reloading systemd prevents boot revival.
if [[ "$(systemctl show "$unit" --property=LoadState --value)" == "loaded" ]]; then
  systemctl stop "$unit"
fi
rm -f -- "$quadlet"
systemctl daemon-reload

# Do not force-remove anything with a different container or volume name.
if podman container exists "$container"; then
  podman container rm --force "$container"
fi
for volume in "$volume_etc" "$volume_dns"; do
  if podman volume exists "$volume"; then
    podman volume rm "$volume"
  fi
done

# Nova explicitly chose to discard retained Pi-hole backups. This dedicated
# directory is never used for any other application recovery point.
if [[ -e "$archive_dir" || -L "$archive_dir" ]]; then
  [[ ! -L "$archive_dir" ]] ||
    fail "Archive path is an unexpected symlink; manual review required."
  [[ -d "$archive_dir" ]] ||
    fail "Archive path is not a directory; manual review required."
  rm -rf -- "$archive_dir"
fi

printf 'Pi-hole rootful service, Quadlet, named container, volumes and local archive directory retired.\n'
printf 'Unit state: '
systemctl show "$unit" --property=LoadState,ActiveState --no-pager |
  tr '\n' ' '
printf '\n'
printf 'Other service Quadlets, DNS, network rules and PostgreSQL were not changed.\n'
