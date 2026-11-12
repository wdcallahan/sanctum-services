# Kvar survivors: consistent backup and isolated recovery design

**Owner:** Sanctum Services (LinkStack and Pi-hole application data, Quadlets, and restores). Maintenance owns Kvin/Kvar host storage, firewalld, DNS and any general network changes. This document is a transaction design, **not a live backup authorization**.

## Accepted native state, November 12, 2026

The read-only Kvar service discovery returned `ok=14 changed=0 failed=0`, with three complete metadata-only volume scans. The following are **uncompressed sums of regular-file sizes**, not archive sizes or verified consistency:

| Surviving namespace | Volume and container mount | Files | Source regular bytes |
|---|---|---:|---:|
| `wdc2` rootless LinkStack | `linkstack:/htdocs` | 10,523 | 84,805,553 |
| rootful Pi-hole | `systemd-pihole_etc-pihole:/etc/pihole` | 56 | 1,310,387,005 |
| rootful Pi-hole | `systemd-pihole_etc-dnsmasq:/etc/dnsmasq.d` | 0 | 0 |

The total source regular-file bytes are **1,395,192,558 (~1.30 GiB)**. The empty dnsmasq volume is nevertheless part of Kvar's exact running configuration. LinkStack has a real `.env` and `database/database.sqlite`; Pi-hole has `gravity.db`, `pihole-FTL.db`, and `pihole.toml`. Presence alone does not establish a good database or recoverable service.

The running LinkStack image ID was unchanged across the reports. Pi-hole's running image ID **changed**, from `edb7f703649f4b6ab8b14f28d12f15e8cbe1c50a2092458e9b640bd6bc6fe59e` to `64c81b3c8132f3e7ae56925a1668d2cfa5a53c509c43b4c1cc71591e0f42c3d8`. Its cause is unknown; no update or credential-affecting mutation was authorized by these observations. Both containers use mutable `:latest` tags. Each has multiple local repository-digest records. Platform and a Kvin-pullable ARM64 manifest **have not been qualified**.

## One combined read-only prerequisite

`ansible/kvar-survivor-backup-readiness.yml` reports only:

- On Kvar rootless LinkStack, its declared Quadlet image, `AutoUpdate` and `Pull` policy classification, its Podman auto-update timer state, and free bytes on the exact named volume's filesystem.
- On Kvar rootful Pi-hole, the same facts in the **rootful** namespace, without exposing the Quadlet's possible secret environment values.
- On Kvin, home-directory staging capacity and separately visible rootful container-store capacity; the fixed source byte total is used only as a headroom estimate.

The tool must return no application file contents, secret values, mount source paths, arbitrary systemd output, other containers, or arbitrary registry data. `partial` preserves unknowns rather than inventing an absence. A responsive timer or `AutoUpdate=registry` is **not proof** that it caused the observed Pi-hole image change; only a relevant service journal or known operator update would establish that causal history.

### Pre-transaction gates (future, not yet accepted)

1. Confirm the currently running container's exact identity and expected Quadlet policy again **at transaction time**. Do not derive a Kvin image from the mutable tag or equate two different `RepoDigests` values. Qualify the intended **linux/arm64** immutable image on Kvin independently.
2. Verify adequate capacity in the source filesystem for private partial archives if the chosen transfer/export mechanism stages them there, plus Kvin receiver space and separate *restore-volume* space. A spare ~3.9 GB on Kvin home is an initial staging check, not an engineering promise that 1.3 GB of Pi-hole SQLite plus an image and volume can be restored.
3. Select and approve **one named service at a time** for brief, bounded quiescence. Require working rootless `systemctl --user` for LinkStack and rootful `systemctl` for Pi-hole; never stop both to simplify a backup. Before stopping, confirm backups will stay private (0700 directories, 0600 archives) and unique filenames will not overwrite previous snapshots.
4. Stop only the approved source service long enough to obtain a consistent named-volume export. For Pi-hole, **both** exact rootful volumes must be captured in the same stopped interval, even when one is empty. LinkStack SQLite and its `.env` must be captured together while its application is stopped. Use Ansible's `always` recovery block to start the original service even if export/validation fails. Stop on failed restart or failed health checks, with unmodified original volumes retained.
5. Validate archive integrity, expected paths, file markers, and persisted database integrity without disclosing the data. Treat an archive as containing secrets regardless of whether its stdout looks harmless. Name/retain a SHA-256 of the validated archive(s). Transfer over an authenticated encrypted channel to independent host storage with restricted permissions, and verify hashes again. **Kvin alone is a migration receiver, not an independent disaster-recovery backup**; full loss of Kvin must not destroy the only retained backup.
6. Restore into **new, isolated** Kvin volumes and prove application behavior before considering the live proxy routes. LinkStack: retained directory pages, images, login/admin editing and SQLite integrity without altering old Kvar. Pi-hole: intended configuration/gravity databases and one intentionally opted-in filtering client, without taking over Peanut's authoritative BIND, DHCP, or general client DNS.
7. Only after actual application restoration, source-owned Quadlet repeat and independent client acceptance should Services retarget the YXORP backend for `dir.nexus` or `pihole.nexus`. Maintenance's already published six DNS aliases continue targeting Kvin **the proxy**, but that does **not** mean every backend has moved. Kvar NPM remains available for fallback and Kvar's old application volumes are preserved until independent retirement.

## Pi-hole v6 special case

Pi-hole's current official Docker documentation identifies `/etc/pihole` as persistent configuration and databases. `/etc/dnsmasq.d` is usually optional in **new** v6 installs, but is needed when preserving older custom configuration, and requires the corresponding `FTLCONF_misc_etc_dnsmasq_d` setting. An **empty** observed Kvar dnsmasq volume does not authorize removing the declared mount or guessing the complete previous version/upgrade history. Source: https://docs.pi-hole.net/docker/ and https://docs.pi-hole.net/docker/upgrading/v5-v6/.

## Safe stopping points and authority

The present state is **metadata-only evidence**. No actual backup, verified archive, isolated restore, service restart, image pull, rootful port 53 use on Kvin, DNS migration, proxy reconfiguration, or Kvar decommissioning has occurred. Every later operator command must be source-checked, explicitly bounded, and reported as partial unless its actual acceptance evidence passed.

The longer-term owner goal is a routine updateable and reversible restore process, not a one-time filesystem copy.
