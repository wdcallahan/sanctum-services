# Kvar survivors: consistent backup and isolated recovery design

## CURRENT — November 12: differential LinkStack test proves *both* startup paths exit 1; startup/runtime discrepancy, not proven data corruption

**Native Kvin differential diagnostic:** Nova ran `ansible/linkstack-offline-startup-diagnose.yml` with approval. `kvin.outer.sanctum: ok=6 changed=1 unreachable=0 failed=0`; report `status:observed`. **Both the image-only container and independent cloned-restored-volume container exited with `ExitCode=1`, `Running=false`, `OOMKilled=false`, `http_status=null`**. Both log outputs classified **`unclassified`**, not empty/safe or proof of good Apache startup. `reason_comparison=both_exit_startup_independent_of_restored_data_possible`. The tool confirmed **all four disposable resources removed** (both containers, copied volume, temporary internal/no-DNS network), unchanged accepted restored volume and source archive, no Kvar touch or production network/service changes. Earlier archive SQLite integrity, image digest and ARM64 checks remain accepted, but **a recovered LinkStack app has not been proven to start**.

**Upstream startup source inspected:** LinkStackOrg/linkstack-docker `Dockerfile` specifies `USER apache:apache`, `CMD ["docker-entrypoint.sh"]`, `WORKDIR /htdocs`. The entrypoint reads `/htdocs/version.json`, writes to `/etc/php83/conf.d/40-custom.ini`, removes `/htdocs/httpd.pid`, then `exec`-like foreground Apache `httpd -D FOREGROUND` (actual shell command). This is general upstream source, not yet confirmation of the exact pinned image's file state. Tests must distinguish startup prerequisites and Podman runtime restrictions. This test's `unclassified` log categories are an **instrumentation gap**; do not broaden logging to disclose real `.env` values or raw container logs.

**Next engineering direction:** Build one bounded image-only, Kvin-rootless differential: compare the formerly added `--security-opt no-new-privileges` trial to ordinary rootless Podman's existing default confinement, under the same temporary `--internal --disable-dns` network, without mounting any LinkStack data; inspect pre-start exact cached image, user/command classification, static `/htdocs/version.json` readability, `/etc/php83/conf.d/40-custom.ini` write access and Apache syntax, collect only fixed startup milestone boolean flags, exit code and a finite known-error taxonomy (never free text), then clean up both container names and internal network. If default mode works, identify a restrictive flag regression; if both exit, compare other host/Quadlet runtime prerequisites. **No previous backup, transfer or restore repeat; no production interruption.**

**Qualification result / current operator gate:** Full Services source and Ansible syntax CI **[#43277394735 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43277394735)**, including host/account refusals, raw-log redaction, two-case process comparisons, archive identity guards, no host ports/external network, and mandatory four-resource cleanup. This is **source only**; no differential diagnostic has yet run natively on Kvin. Next operator action **on Kvin**, with explicit consent to create two temporary rootless containers, one internal/no-DNS network and one disposable cloned volume (original accepted restored volume untouched):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-offline-startup-diagnose.yml \
  -e sanctum_linkstack_startup_diagnostic_approved=true
```
**Entire output welcome**; the single task `Report sanitized image-only versus restored-copy startup comparison` and Kvin recap (or a failed task) are sufficient. Its output distinguishes image-only startup from failure caused by data/mount/permissions without exposing logs. It **does not** start production, retarget the proxy, interrupt Kvar, or qualify the application as working. Never rerun the old full LinkStack HTTP trial as the diagnostic.

## November 12 — corrected LinkStack internal-network trial confirms application EXIT before HTTP; differential diagnostic source pending native

Nova reran `ansible/linkstack-qualify-isolated-application.yml` with the disposable internal/no-DNS bridge. **Kvin `ok=23 changed=4 unreachable=0 failed=1 skipped=1`**. The actual task `Refuse HTTP acceptance if restored app has already exited` failed because `(linkstack_trial_running.stdout | trim) == 'true'` evaluated **false**. The disposable container **exited before an HTTP request could be made**. Both the *specifically named disposable container* and *its internal bridge* were successfully removed in the `always` block. Image identity/ARM64 and PHP 8.3 from prior native run were accepted; restored volume SQLite integrity was rechecked earlier in this run. Original Kvar LinkStack and Pi-hole, Kvar NPM, live Kvin apps, published DNS and YXORP unchanged. Original Kvar tar, verified Kvin tar, and original separately imported Kvin rootless LinkStack test volume remain intact. **Do NOT claim HTTP app boot, nor infer exact cause from exited state alone.**

**New diagnostic engineering:** `tools/diagnose-linkstack-offline-startup.py` with `ansible/linkstack-offline-startup-diagnose.yml` performs a **differential bounded two-case test** on Kvin only: (1) original pinned image with its own image-seeded `/htdocs`, (2) same image using a **new disposable rootless volume freshly imported** from the already checksum-validated **Kvin-local** tar. It never remounts or modifies the *accepted separately imported restore-test volume* or any incumbent volume. It creates one temporary **internal/no-DNS** rootless bridge, has no published ports/external route, and checks both containers' bounded `Running`, `ExitCode`, `OOMKilled`, HTTP status where running, and **allowlisted log classifications only** (`permission_denied`, `read_only`, `missing_path`, `apache_config`, `apache_bind`, `sqlite_error`, `php_error`, `pid_file`), never showing raw logs, paths, .env content or credentials. An unconditional finally block removes both uniquely named containers, new temporary volume and new network, and reports any cleanup failure. Host/user, exact archive SHA256/mode/size and exact pinned ARM64 image identity are hard gates. A positive `sanctum_linkstack_startup_diagnostic_approved=true` is required. Source tests and full Ansible syntax CI must be green first.

**Interpretation:** If image-only runs but restored-data copy exits, focus on imported volume ownership/SELinux/entrypoint data state. If both exit, focus on common image startup. A missing recognized log category is not evidence of success; next narrower non-secret probe may be needed. Do **not** repeat the original 15 HTTP retries or Kvar backup/SCP/import to diagnose.

## November 12 — first LinkStack offline boot HTTP test FAILED SAFELY; corrected internal-only network CI GREEN

Nova ran the original `ansible/linkstack-qualify-isolated-application.yml` on Kvin. Actual native recap **`ok=18 changed=3 unreachable=0 failed=1`**. **Passed**: exact rootless Kvin target, previously imported separate volume, restored SQLite integrity, free disposable name, rootless pull of the pinned exact ARM64 LinkStack image, image architecture and exact original Kvar content ID, and offline PHP 8.3 execution. Temporary restored-app container started. All **15** `podman exec ... curl http://127.0.0.1/` probes failed (`rc != 0`); the HTTP status acceptance assertion failed. The Ansible `always` handler **removed the disposable container successfully**. No production route/service or Kvar image/volume was changed; the previously copied tar, original source tar, and separately imported Kvin volume remain. **Do not claim restored LinkStack application boot or HTTP acceptance.**

**Design defect identified:** The original trial used `podman run --network none` then tried TCP 127.0.0.1 inside that unconfigured network namespace. Podman's own [run documentation](https://docs.podman.io/en/latest/markdown/podman-run.1.html) states `none` creates a namespace **without configuring network interfaces**; therefore localhost HTTP cannot be reliably tested through that mode. The native failure does **not** establish whether Apache itself was healthy or exited later; that remains an evidence gap, not proof of an invalid backup. The original run's successful guaranteed container cleanup is independently observed.

**Source correction:** Rebuilt the playbook from a known-good revision after rejecting an intermediate malformed YAML edit in CI. It now checks a unique temporary rootless network name, creates **only** a new `--driver bridge --internal --disable-dns` Podman network, requires its observed `driver=bridge`, `internal=true`, and `dns_enabled=false`, then runs the temporary LinkStack container on *that network* with **no published ports, no external route, and no host networking**. It checks the container is actually running before attempting HTTP from inside the namespace. Its `always` tasks remove both the disposable container and the single temporary network; it refuses declaring success unless both cleanups pass. No new image pull expected because original exact digest is already cached; the image and restored data are reverified without repeating Kvar backup, SCP transfer or import. Test source now explicitly prevents using `--network none` in the application HTTP trial and verifies internal/no-DNS network, cleanup and failure behavior.

**Full Services source+syntax CI [#43275657216 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43275657216)**, including Ansible syntax after rebuilding the YAML and all isolated-app/negative tests. **No native rerun of corrected playbook yet**.

**Next exact Kvin operator action (same permissions as previously granted, but creates a disposable internal bridge):**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-qualify-isolated-application.yml \
  -e sanctum_linkstack_image_qualification_approved=true \
  -e sanctum_linkstack_offline_application_trial_approved=true
```
Full output welcome. This requires explicit operator opt-in for the new short-lived internal network; it **does not** touch Kvar, existing apps, production host ports, DNS, proxy or firewall. If this still fails, classify the next actual failure (network creation, container running state or HTTP) from native evidence; do not infer apache health or launch live LinkStack until proved.

## November 12 — Kvar-to-Kvin LinkStack archive transfer and isolated volume import ACCEPTED

Nova ran `ansible/linkstack-transfer-isolated-data-restore.yml` with the two independent approvals. **Kvar `ok=4 changed=0 failed=0`; Kvin `ok=22 changed=6 failed=0`; both hosts reachable.** Kvar's original private tar was confirmed to be exactly 93,845,504 bytes with SHA-256 `a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa`, a regular 0600 file owned by `wdc2`.

The archive was successfully copied over authenticated strict-host-key SSH (Kvar management port 10022) to Kvin, with matching byte size, SHA-256, restrictive ownership/mode, safe tar validation and SQLite integrity `ok`. A new, separate **rootless** Kvin volume `sanctum-linkstack-restore-test-20261112t105926` was created and imported with the saved data. The restored `.env` marker and SQLite database were positively verified. Kvar's running LinkStack, its volume, Pi-hole, DNS and production YXORP were **unchanged**. These are genuine **off-Kvar archive transfer and isolated data restoration** acceptances, not a proven restored application launch. `browser_directory_and_admin_accepted:false`, `restored_linkstack_app_boot_accepted:false`, and `independent_disaster_recovery_backup_accepted:false`.

**Next image/application qualification:** The Kvar image listing previously tied the **running** LinkStack image ID `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65` to ARM64 repository digest `docker.io/linkstackorg/linkstack@sha256:b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1`. Docker Hub's contemporaneous `latest` tag ARM64 platform listing independently matched this **digest**, rather than choosing a new arbitrary mutable `latest`. LinkStack upstream declares Linux ARM64 support, Alpine/Apache/PHP 8.3 and `/htdocs` as its full persistent data. This digest is now `linkstack_candidate` in `data/container-image-candidates.yml`, status `registry_only`; **do not claim Kvin native image qualification yet**. References: https://hub.docker.com/r/linkstackorg/linkstack/tags and https://github.com/LinkStackOrg/linkstack-docker.

The default-off `ansible/linkstack-qualify-isolated-application.yml` independently requires **both** `sanctum_linkstack_image_qualification_approved=true` and `sanctum_linkstack_offline_application_trial_approved=true`. It checks exact Kvin rootless ARM64 host, prior isolated volume and its SQLite integrity, refuses an occupied trial name, pulls only the immutable digest if absent, verifies actual image architecture **and the original Kvar image ID**, tests the PHP 8.3 runtime offline, and starts a temporary **network-none, no-published-port** container with the already isolated restored volume. Its `curl` request is made **inside** the disconnected namespace and checks an HTTP result for `dir.nexus.sanctum`. Its `always` handler removes only the just-created disposable container. It preserves the isolated volume and source archive; original Kvar LinkStack and Kvin production services are not selected. This tests startup, **not** real directory content/admin from a named LAN browser or disaster recovery across simultaneous host losses.

After full source CI passes, on **Kvin** and with approval for only an immutable image pull and offline restored-app test:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-qualify-isolated-application.yml \
  -e sanctum_linkstack_image_qualification_approved=true \
  -e sanctum_linkstack_offline_application_trial_approved=true
```

Full output is welcome. Expected one final task: `Report bounded LinkStack ARM64 image and offline restored-application acceptance`; `PLAY RECAP` only Kvin. No original service interruption, live app staging, new LAN port, DNS/proxy change, or clean-up of accepted backup artifacts.

## November 12 — Kvar LinkStack consistent archive ACCEPTED; Kvin transfer is next

Nova approved and ran `ansible/linkstack-consistent-backup.yml` from Kvin against the **original rootless LinkStack on Kvar**. Native recap: **`ok=30 changed=6 unreachable=0 failed=0`**. The original service was stopped briefly, volume `linkstack:/htdocs` exported while quiesced, and the `always` restart succeeded. Post-restart immutable image ID, mount, ports and application HTTP were accepted; original returned **HTTP 200**. The private owner-controlled source archive was promoted on Kvar only:

- Source path: `/home/wdc2/.local/share/sanctum-services/backups/linkstack/linkstack-20261112t105926.tar`
- Exact tar size: **93,845,504 bytes**
- SHA-256: **`a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa`**
- Archive verifier: safe tar paths, LinkStack `.env` present, SQLite **`PRAGMA integrity_check = ok`**
- Source report flags: `linkstack_consistent_snapshot_accepted:true`, `archive_published_private_on_kvar:true`, `archive_copied_off_kvar:false`, `isolated_kvin_restore_accepted:false`.

**Operator-discovered warning repaired:** That first run emitted Ansible's top-level injected-facts deprecation on `ansible_date_time.iso8601_basic_short`. Source was corrected to `ansible_facts['date_time']['iso8601_basic_short']` with a regression test. No warning suppression; future executions use the nested mapping.

### Next source-owned one-shot — exact SSH copy and isolated Kvin volume integrity

`ansible/linkstack-transfer-isolated-data-restore.yml` is separate from the live snapshot operation. It has **two explicit, default-off approvals**: `sanctum_linkstack_offhost_transfer_approved=true` and `sanctum_linkstack_isolated_volume_restore_approved=true`.

On Kvar, it verifies the **exact saved archive SHA, byte size, owner and mode 0600**, without restarting or accessing the live container. On Kvin, it requires aarch64, both approvals, an exact source validation fact from this run, empty distinct destination archive paths, and an absent isolated rootless volume. It reserves a 0600 partial, copies the single archive with OpenSSH `scp -B -P 10022` using **strict host-key checking** and batch mode (an existing Kvin→Kvar SSH trust path is required; the play fails safely otherwise), verifies copied SHA/size/permissions and SQLite archive integrity, then promotes the archive without overwriting another copy. Only after validation does it create `sanctum-linkstack-restore-test-20261112t105926` and import the archive into **that new volume alone**. It checks restored `.env` presence and SQLite integrity without returning data. The original Kvar `linkstack` volume and all Kvin production volumes remain untouched.

The command (run on **Kvin** only after full source CI is green and with conscious approval for copying a private archive and creating the isolated test volume):

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-transfer-isolated-data-restore.yml \
  -e sanctum_linkstack_offhost_transfer_approved=true \
  -e sanctum_linkstack_isolated_volume_restore_approved=true
```

Expected final report **`Report bounded Kvar-to-Kvin LinkStack archive transfer and isolated data restoration`**; send **the full output** and both PLAY RECAP rows. The transfer is encrypted between Kvar and Kvin over SSH; no raw archive, `.env`, database rows, login or private key should be pasted into chat. If pre-existing files, SSH trust, SHA or isolated volume checks fail, stop at that failed task rather than editing data by hand.

Passing this gate establishes **off-Kvar byte-identical snapshot and isolated data import integrity**, *not* application boot, an authenticated directory page, a public backend migration, or a backup that survives simultaneous loss of both hosts. The application container still needs a separately qualified pinned linux/arm64 image and actual offline client/app acceptance before changing the live `dir.nexus` upstream.

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

## Qualified rootless LinkStack consistent snapshot source — operator gate

The source-owned one-shot `ansible/linkstack-consistent-backup.yml` stages **only a Kvar-local, private consistent snapshot of the live rootless LinkStack data volume**. It does not move a copy to Kvin, restore an application, retarget a route, or touch Pi-hole/NPM. It must **not** run without an affirmative operator choice to interrupt LinkStack temporarily.

Source constraints:

- Require exact inventory Kvar as `wdc2`, explicit `sanctum_linkstack_consistent_backup_approved=true`, no check mode, and neither restore nor cutover approvals.
- Before interruption re-observe running `linkstack` in the rootless Podman namespace and require the original observed image ID, image name, single `linkstack:/htdocs` writable mount, port 8081→80 and existing user Quadlet. An automatic image change refuses the snapshot before downtime.
- Keep any prior archive and partial filename intact; prepare a 0700 directory and exclusively reserve one new 0600 partial file.
- Stop **only `linkstack.service`**, verify inactive, export **only `linkstack`** while stopped; the Ansible `always` handler starts the original service again even when export fails. Require the service to be active and its exact image/mount/ports unchanged, and the HTTP endpoint on Kvar to respond.
- Verify the new archive is an ordinary `wdc2`-owned 0600 file. Its separate privacy-bounded validator rejects traversal, symlinks, duplicate members, unsafe types, missing `.env`/SQLite and SQLite integrity failures. Return only an archive digest, archive size, positive SQLite integrity and boolean acceptance.
- Promote the validated private partial to a retained `.tar` only without clobbering another name; retain failed private partials for investigation and never silently overwrite existing history.
- The reported `linkstack_consistent_snapshot_accepted:true` means a **validated consistent backup on Kvar only**. `archive_copied_off_kvar:false` and `isolated_kvin_restore_accepted:false` remain explicit. Do not treat Kvar-local archives as independent disaster recovery.

The command below is a **live LinkStack service interruption**. Run only when the operator accepts that interruption and source CI is green:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-consistent-backup.yml \
  -e sanctum_linkstack_consistent_backup_approved=true
```

Return only the **`Report bounded consistent LinkStack source-backup acceptance`** task's `msg` and the single Kvar **`PLAY RECAP`**, or the failed task. There are no other report names to hunt down. No secrets, SQLite content, `.env` file or archive should be pasted into chat.

**After successful native backup:** implement and qualify a copy of this exact retained archive to Kvin (different host) with hash verification, then an isolated volume import and application-level restore using a separately qualified immutable image. The existing live Kvar instance remains the reference and fallback. No claim of independent disaster recovery until a copy survives Kvar/Kvin failure separately.

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
