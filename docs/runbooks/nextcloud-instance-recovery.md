# Town Square / Nextcloud — complete-instance recovery boundary

## November 21 late evening — complete native Nextcloud disaster recovery ACCEPTED; live update next

Real independent Peanut HTTP/DAV recovery passed: **ok=25 changed=2 failed=0 unreachable=0**, existing recovered account authenticated, pre-existing user file read, Calendar collection queried and **2 event objects** recovered, temporary Apache removed. Browser login not explicitly exercised. [Actual native acceptance](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7074839767) completes the earlier [137-table PostgreSQL restore](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7073940132) and [OCC/Calendar test](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7074239528). Production remained untouched. Do not repeat these tests. The retained owner's temporary DB remains for separate cleanup using its staged Maintenance helper; no deletion of backup artifacts is authorized.

The source recovery gate is now accepted, not merely source-tested. The protected update cycle will refresh the supported moving 34.0-apache image, make a NEW consistent pre-update snapshot if an update is available, verify independent Peanut custody, then activate the source-managed Quadlet. Next operator action is the actual update cycle from the existing Kvin terminal, with the same flock lock as the installed weekly backup. Pixel verifies full CI first. After actual live acceptance, install the daily patch timer; no automatic pruning or unrelated PostgreSQL upgrade. If already at same image, no new snapshot/restart. Do not treat a historical candidate version as a perpetual pin.

**Nova warning correction:** native Ansible reported deprecated dict-to-bool conversion in HTTP host port check. Corrected to explicit collection length (normalizing null/undefined). Every reported deprecation/FutureWarning is an actionable compatibility defect even with failed=0. Correct it in source, add targeted regression and track any outstanding cases rather than suppressing warnings or asking Nova to repeat an accepted native run just to validate cosmetic output. Current scan of Nextcloud maintenance/restore entrypoints found the one exact collection coercion. This is NOT a claim that the entire Sanctum fleet is warning-free.

Run from the existing Kvin Services checkout after Pixel confirms source validation:

```bash
git pull &&
flock -n ~/.local/share/sanctum-services/backups/nextcloud/.nextcloud-cycle.lock \
  ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/nextcloud-maintenance-cycle.yml \
  -e nextcloud_maintenance_cycle_approved=true \
  -e nextcloud_maintenance_activation_approved=true
```

Expect a protected update and temporary Nextcloud maintenance window only if a new image exists. Return the update report and PLAY RECAP, or the failure and warnings. Do not blindly rerun a failed migration. The scheduler installation is separate after native live update acceptance.

## November 21 — restored Nextcloud CLI and Calendar NATIVE ACCEPTED

Nova's actual corrected CLI result: **Peanut ok=28 changed=1 unreachable=0 failed=0 skipped=3 rescued=0 ignored=0**. Recovered Nextcloud **34.0.5.1** and Calendar **6.6.2** against the independently recovered 137-table DB, official moving same-series runtime shipped 34.0.6.2. [Receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7074239528). Document-root correction confirmed. Do NOT rerun prior backups, filesystem, DB or OCC acceptance.

Next: `ansible/nextcloud-isolated-http-trial-on-peanut.yml` uses the same retained DB namespace, app code and verified private overlay. Starts temporary Apache with its initialization entrypoint bypassed, no external network or published host port. Prompts for an existing username/password (or app password present in the Nov16 backup) at Nova's terminal; password is hidden and passed via stdin to a disposable local HTTP client, never in arguments, Git or conversation. Authenticated OCS identity, WebDAV existing file listing plus nonempty file read, CalDAV collection listing and calendar query are measured; only codes/counts/status are reported. Browser login not claimed. Stops the Apache container in always; preserves the owner DB for later cleanup. If account lacks a file/calendar, report incomplete, not fabricated success. Production gate stays closed until native functional evidence is accepted. Pixel checks source CI before asking Nova to run.

From the existing Kvin Services checkout after Pixel confirms CI:

```bash
git pull &&
ansible-playbook -i ansible/inventory/hosts.yml \\
  ansible/nextcloud-isolated-http-trial-on-peanut.yml \\
  -e nextcloud_isolated_recovery_id=nextcloud-20261116t233618 \\
  -e nextcloud_isolated_http_trial_approved=true
```

Return the bounded HTTP/DAV report and final TASK/PLAY RECAP; never paste passwords or private raw output.

## November 21 — Peanut PostgreSQL restore NATIVE ACCEPTED; next recovered application

Nova ran `ansible/nextcloud-isolated-db-trial-on-peanut.yml` successfully: **Peanut ok=30 changed=5 failed=0 unreachable=0 skipped=1**. Restored **137 application tables** from `nextcloud-20261116t233618`, with retained owner-labelled networkless DB, private handoff, already restored HTML/private files untouched, production Kvin not contacted and shared PostgreSQL unchanged. [Exact native receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7073940132); [Maintenance owner acceptance handoff](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-7073941735). Retained owner helper revision `7a5f3185`, staged at the trial's `maintenance-helper/restore-nextcloud-postgresql` (not the scheduled checkout). The accepted DB must NOT be recreated; use its existing private receipt.

Services next rehearses the **restored 34.0.5 application code** from the extracted HTML tree using a native same-series PHP runtime from `docker.io/library/nextcloud:34.0-apache` (cache if absent), not a new old pinned-image download. The runtime's shipped version must be 34.0.x; bypass the normal image entrypoint using PHP and mount restored HTML, so no image-driven app sync/upgrade. Validate `occ status` (installed, not maintenance, no DB upgrade, restored code version 34.0.5.x) and enabled Calendar 6.6.2, in the existing networkless owner DB namespace. No public listener or production access. Real authenticated user, files and Calendar functional checks remain after CLI. Production update gate stays closed.

**Operator interface:** Pixel checks the complete CI result before offering an executable command, not Nova. Nova need not open Actions, watch a color, or independently check CI. Do not send a conditional command and leave Nova to monitor CI. Current playbook checks [source CI](https://github.com/wdcallahan/sanctum-services/actions/runs/44983309352). After verified completion, provide the next operator command from Kvin. No repeated DB restore, backups, extraction or timer installation.

### Next native application CLI rehearsal

From the ordinary `wdc2@kvin` Services checkout, **after Pixel confirms full CI success**:

```bash
cd ~/src/sanctum-services &&
git pull &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/nextcloud-isolated-app-cli-trial-on-peanut.yml \
  -e nextcloud_isolated_recovery_id=nextcloud-20261116t233618 \
  -e nextcloud_isolated_app_trial_approved=true
```

This authorizes moving-series image cache acquisition only if missing and the isolated restored-copy configuration overlay and CLI checks on Peanut. Report `TASK [Report actual networkless Nextcloud recovered application CLI and Calendar trial]` and `PLAY RECAP`, or the failed task. Do not rerun blindly if the copied config overlay has already been written.

## November 21 — Maintenance #17 source dependency resolved; Services restore integration prepared

Maintenance [owner handoff](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-7073128840) and [#17 correction](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-7073141882) confirm reviewed owner revision `7a5f3185`: the helper exports `docker.io/library/postgres:18`, resolves the cached local image once for server and peer, and checks the running PostgreSQL major before restoring. Seven local owner tests, syntax/target selection and Services' runpy contract passed. Native retained restore remains to be proven.

Services' `ansible/nextcloud-isolated-db-trial-on-peanut.yml` now reads only the two owner helper files from that reviewed Git revision on the Kvin controller (obtaining missing Git objects without switching or advancing either Maintenance checkout), stages them in the existing Peanut trial's private `maintenance-helper` directory, and checks the actual staged channel before any image pull or DB restore. The old fixed-digest download remains withdrawn. Source revision records the owner's tested code, NOT an image pin. The retained original November 16 bundle and filesystem staging are the inputs. Do not repeat prior backup, retention, extraction, or timer installation.

**Next operator step, after source CI is green:** run the isolated Peanut DB restore from the normal Kvin Services checkout, then return the final TASK and PLAY RECAP or exact failed task. The command and scope are in the command below. This starts a separate rootless networkless DB on Peanut and retains its private handoff for the restored app; it does not start the app, promote an image in production, or change shared PostgreSQL. Until actual result, neither full restore nor unattended patch promotion is accepted.

From the ordinary `wdc2@kvin` shell:

```bash
cd ~/src/sanctum-services &&
git pull &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/nextcloud-isolated-db-trial-on-peanut.yml \
  -e nextcloud_isolated_recovery_id=nextcloud-20261116t233618 \
  -e nextcloud_isolated_db_trial_approved=true \
  -e nextcloud_maintenance_restore_contract_approved=true \
  -e nextcloud_isolated_db_image_cache_approved=true
```

Only after [current integration CI](https://github.com/wdcallahan/sanctum-services/actions) is green. The three existing approval inputs authorize one isolated restore, the Maintenance-owned interface, and a cache pull of the corresponding moving major channel if absent. The controller stages the reviewed files from Git objects, not from the installed Peanut checkout. On success report `TASK [Report actual independent Nextcloud-only PostgreSQL trial ready for isolated application]` and `PLAY RECAP`. On failure report the exact failed task and preserve the trial; do not blindly rerun. The retained helper can later perform its owner-defined cleanup with `--cleanup PRIVATE_PASSWORD_FILE` after the restored application has stopped. No new backup or production change is part of this command.

## November 17 — NOV16 WHOLE-SANCTUM AUDIT OVERRIDES OLD PINNED IMAGE COMMAND

**WITHDRAWN:** The below older example directing an explicit cache pull of
Maintenance's legacy SHA-pinned PostgreSQL image is no longer actionable.
Nova objected after recognizing it violates the intent of the [Nov16
whole-Sanctum policy audit #38](https://github.com/wdcallahan/sanctum-maintenance/issues/38).
Do NOT run the previous `nextcloud-isolated-db-trial-on-peanut.yml`
command until the owner restore-helper image policy is reconciled,
reviewed and source CI green. Historical immutable image IDs remain
permitted for accepted snapshots and bounded fixtures, but must not be
silently imposed as an endless installed service policy or blindly copied
into a new download/update workflow.

**Confirmed source mismatch:** Maintenance's *real production backup
dump path* accepts compatible PostgreSQL 18 patch images, while
`tools/restore-nextcloud-postgresql` imports an obsolete digest
constant from its backup helper for all rootless trial container runs.
The Services playbook now specifies **`docker.io/library/postgres:18`**
(a moving major-version channel), but fails **before any Podman pull,
private handoff or database creation** if the installed owner helper
does not itself select that channel. No Services-owned PostgreSQL SQL
implementation or unchecked image fallback was introduced.
[Owner repair request](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6961470716).

**Current valid acceptance:** weekly backup user timer enabled, one
supervised **installed user service** backup native accepted with
recovery `nextcloud-20261117t134454` independently verified on Peanut;
the Nov16 restored HTML/private trial remains staged. The isolated
full PostgreSQL+app recovery, authenticated login/files/Calendar and
first live 34.0.6 update still await proper owner reconciliation.
Do not rerun any banked backup or cache-qualifier procedure.

## November 17 — Real installed backup-service run accepted; isolated full recovery staged in source

**NATIVE FIRST SYSTEMD ONE-SHOT PASSED:** Nova ran the supervised
`ansible/nextcloud-backup-service-first-run.yml` with exact
**`kvin.outer.sanctum ok=20 changed=1 unreachable=0 failed=0`**.
The **already enabled** weekly user service executed and returned
systemd `Result=success`, creating **NEW recovery point
`nextcloud-20261117t134454`**, identical SHA256 manifests and
independently full-bundle-verified Kvin + Peanut copies. Nextcloud
returned to normal and the weekly timer remains enabled.
No update or automatic prune; natural Sunday timer firing has NOT
been observed. [Native receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6960759294).
**Do not repeat** the installer or first worker execution.

**New database restore path under owner Maintenance #17:** The current
`/home/wdc2/src/sanctum-maintenance/tools/restore-nextcloud-postgresql`
supports optional durable isolated owner handoff (the helper is the
ONLY SQL implementation). Given Nov16 Peanut bundle
`nextcloud-20261116t233618` and its **already extracted HTML/private
Peanut trial**, Services source
`ansible/nextcloud-isolated-db-trial-on-peanut.yml` will validate the
real retained dump against its manifest and use ONLY that Maintenance
helper to produce a new networkless PostgreSQL18 trial with private
password/receipt handoff at:
```text
/home/wdc2/.local/share/sanctum-services/nextcloud-restore-trials/nextcloud-20261116t233618/postgresql-trial/
```
No shared DB, DNS, proxy or live Kvin changes. The play demands separate
explicit isolated DB/owner contract approval. If the exact
Maintenance-pinned image is not already cached, an **additional
explicit cache-only approval** allows fetching that exact digest
into Peanut's rootless Podman cache, checking CPU architecture and
PostgreSQL server major 18 before any DB container starts. A
successful owner handoff intentionally leaves the isolated test
database running for the subsequent Services app trial. It must later
be removed through the Maintenance owner cleanup contract.

**Follow-up restored app CLI source:** `tools/nextcloud-isolated-config.py`
writes a one-time private `zzzz-sanctum-isolated.config.php` ONLY inside
the extracted trial HTML/config. It reads Maintenance's private
password, restricts DB host/role/database to `127.0.0.1` and
`nextcloud_restore`, preserves the original copied `config.php`,
and makes the override owner `www-data` mode 0600 using
`podman unshare`. Nextcloud documents
[additional configuration files](https://docs.nextcloud.com/server/stable/admin_manual/configuration_server/config_sample_php_parameters.html).
`ansible/nextcloud-isolated-app-cli-trial-on-peanut.yml` requires
original immutable **34.0.5** image cached on Peanut and runs
`occ status` + Calendar `occ app:list` in exactly the separate
database's `--network=none` namespace, without a public HTTP port.
Even bad copied settings cannot connect to production. This CLI
result DOES NOT prove authenticated HTTP login/user-file or calendar
client functionality, nor does it authorize the live 34.0.6 patch;
that full-application acceptance is a later separate stage.

**Next operator action is blocked on Maintenance-owned source reconciliation.**
The formerly proposed pinned-digest download-and-restore command has been
withdrawn. Services checks Maintenance's actual restore-helper image
contract **before any pull**; at current source it still selects the
obsolete SHA. Do not attempt a native DB trial or repeatedly probe
previously accepted Kvin/Peanut backup stages until Maintenance updates
its owner helper to the supported `docker.io/library/postgres:18`
channel and the Services source tests remain green.

## November 17 — Weekly user backup timer installed; first one-shot qualification

Nova completed the actual Kvin schedule installer:
**`kvin.outer.sanctum ok=13 changed=3 failed=0 unreachable=0`**,
exact **`TASK [Report source-owned weekly Nextcloud backup schedule without claiming first occurrence]`**:
`installed_and_enabled=true`, Sunday 03:30 local,
`immediate_backup_not_triggered=true`,
`current_nextcloud_not_restarted=true`,
`scheduled_first_run_not_yet_observed=true`. Native receipt
[Services #2](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6958782891).
**Do not rerun installation to confirm it.**

**New supervised first-job source qualification:**
`ansible/nextcloud-backup-service-first-run.yml` requires separately
approved live snapshot execution and exactly Kvin/`wdc2`. It starts
the **ALREADY INSTALLED** rootless systemd
`sanctum-nextcloud-backup.service` once and awaits actual completion,
verifies successful systemd one-shot result, identifies exactly one
newly created private recovery directory not present beforehand,
checks the expected same manifest SHA256 and complete archive/DB
headers independently on Kvin and Peanut, and verifies Nextcloud
returned to normal mode. No updater, timer modification, deletion,
shared PostgreSQL service change or software restart. This first
run uses the existing Maintenance-only export and may briefly put
Nextcloud into maintenance mode, write a new data/DB bundle and
transfer it to Peanut, so a new distinct user approval is required.
**A supervised service start is NOT proof that a later natural Sunday
timer triggering was observed.** That remains a future acceptance
item.

**Upon full CI green, the exact operator command** for a supervised
first-run test, in the normal `wdc2` shell on Kvin (no sudo), is:
```bash
cd ~/src/sanctum-services &&
git pull --ff-only &&
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/nextcloud-backup-service-first-run.yml \
  -e nextcloud_first_backup_run_approved=true
```
Request the exact
**`TASK [Report actual installed weekly Nextcloud backup service execution and Peanut recovery acceptance]`**
and **`PLAY RECAP`**, or the full failed task and error. A fresh verified
backup is intentionally made as part of this new test; no repetition of
the already accepted Nov16 manual snapshot is needed. On failure,
retain all candidate bytes for diagnosis; do not assume the scheduled
worker succeeded just because the timer is enabled.

## November 17 — Native 34.0.6 image ready; updater and weekly backup SOURCE, not live

**Native qualified image-only observation ACCEPTED:** On Kvin, Nova ran
`ansible/nextcloud-qualify-maintenance-image.yml`, recap
`ok=13 changed=1 failed=0`; task
**`Report actual independent Nextcloud 34 maintenance image qualification`**
proves actual 34.0.5.1 running on original image ID
`dcdf0b20ac50bce33cb2585c96fc92968e7c2d7378aef185547f735c9058f7b2`,
official Linux ARM64 34.0.6 cached as
`docker.io/library/nextcloud:34.0-apache` at image ID
`e72f1a9e448447bc170f7fb3993033ff21d233906542852afd10c1cc5ec37d60`.
**Live version and user data are unchanged**; only the rootless image cache
changed. Do not rerun the one-time image stage.

**Coordinated maintenance update SOURCE:** 
`ansible/nextcloud-maintenance-cycle.yml` orders its imported plays:

1. `nextcloud-maintenance-preflight.yml`: check actual old/new image
   identities and 34.0.x shipped version; if unchanged, no backup or restart.
2. `nextcloud-consistent-backup.yml`: allocate a **NEW, same-run** recovery
   point, quiesce only Nextcloud briefly, call Maintenance's Nextcloud-only
   PostgreSQL exporter and archive the HTML/private state, then leave
   maintenance mode.
3. `nextcloud-retain-on-peanut.yml`: transfer and independently verify
   the exact four-file current recovery point on Peanut.
4. `nextcloud-maintenance-activate.yml`: refuse unless both same-run source
   and Peanut proofs, explicitly accepted **complete isolated Nextcloud +
   PostgreSQL restore**, and separate activation approval are all present.
   Only then install the source-managed 34.0 tag Quadlet and restart
   *only* Nextcloud; verify 34.0 version, app mode, original mounts,
   HTTP200 and Calendar 6.6.2. No automatic image-only downgrade
   (a new image can mutate the HTML bind and database).

**Source reconciliation:** `ansible/group_vars/nextcloud.yml` now declares
the desired moving **34.0-apache** channel, retaining the former digest only
as historical migration identity. The ordinary `ansible/site.yml` role now
**refuses** to change the installed old Quadlet's image behind the
coordinated backup gate. Both managed and canonical Quadlet templates
represent the same approved future state and deliberately **omit
`AutoUpdate=registry`**, because the shared Podman timer would bypass
the essential application+database backup. `Pull=never` means only the
Services update preflight advances the local tag. **This source change does
not imply native deployment; Kvin still runs 34.0.5.1.** The shared
restore gate `nextcloud_complete_restore_qualified_in_source=false`
remains closed. Finish actual Maintenance-owned isolated database restore,
then start restored Nextcloud and accept login/files/Calendar before
authorizing live 34.0.6.

**Independent weekly backup SOURCE:** `ansible/nextcloud-scheduled-backup.yml`
allocates a fresh unique identity and runs the already accepted Kvin
snapshot and Peanut retention playbooks in sequence. The proposed
rootless user `sanctum-nextcloud-backup.timer` schedules this every
**Sunday at 03:30 Kvin local clock**, avoids an unscheduled daytime
catch-up (`Persistent=false`), and uses a single-instance `flock`
lock with private `UMask=0077`. It does not depend on an upstream release,
does not upgrade Nextcloud, and **does not delete previous recovery points**;
bounded retention and disk-capacity monitoring remain planned before
indefinite operation. `ansible/nextcloud-backup-schedule-install.yml`
only installs/enables the timer with explicit approval; it does not run
a snapshot immediately. **Source existence is not installed timer acceptance,
nor proof that a scheduled run completed.**

**Operator outputs are always named exactly.** For a future timer-install
acceptance, ask for
**`TASK [Report source-owned weekly Nextcloud backup schedule without claiming first occurrence]`**
and **`PLAY RECAP`** (or the failed task/error). For an actual separate
backup run, ask for
**`TASK [Report one locally assembled recovery point without disaster-recovery overclaim]`**,
**`TASK [Report actual off-host retention without claiming application restore]`**
and **`PLAY RECAP`**. Do not ask Nova to repeat the already accepted
November 16 backup and isolated file extraction just to fill report fields.

**Progress does not stop here:** Initial application-data restore is still an
independent [Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17)
dependency; scheduled backup installation and first live update remain
separate operator-authorized actions. Keep automatic maintenance releases
timely; do not let the qualified backup requirement turn into indefinite
version freezing.

## November 16 final native recovery acceptance — isolated files STAGED on Peanut

Nova ran `ansible/nextcloud-isolated-files-restore.yml` from Kvin,
targeting the **real retained recovery point**
`nextcloud-20261116t233618` on Peanut, and returned
**`ok=14 changed=5 unreachable=0 failed=0 skipped=0 rescued=0`**.

Actual report: `isolated_application_tree_staged=true`,
`isolated_private_inputs_staged=true`,
`source_bundle_integrity_checked=true`,
`database_dump_not_imported=true`,
`nextcloud_container_not_started=true`,
`live_nextcloud_untouched=true`,
`postgres_cluster_untouched=true`, and
`restore_application_accepted=false` (correct).

**Private source retained bundle on Peanut (do not modify):**
`/home/wdc2/.local/share/sanctum-services/backups/nextcloud/nextcloud-20261116t233618`.

**Peanut-only restored target:**
`/home/wdc2/.local/share/sanctum-services/nextcloud-restore-trials/nextcloud-20261116t233618`,
with `html/` and `private/`. Production Kvin was untouched.

**Now actual accepted:** Kvin consistent snapshot, independent Peanut
copy with SHA/archive checks, and Peanut application-file extraction.
**Still open:** isolate and restore the actual Nextcloud-only PostgreSQL
dump via owner [Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6940147324);
then start a fully **isolated** Nextcloud against an independently
available Nextcloud-only trial DB and accept real login, Calendar,
file and sync-client behavior.

Maintenance's existing `tools/restore-nextcloud-postgresql` is a
networkless **disposable** database-restore rehearsal and **removes its
restored DB/container** after validating tables. It cannot itself be
the still-running DB server for an application test. Agree on a
separately owned longer-lived isolated test-DB interface, **never**
modifying the production shared PostgreSQL service. Do not overclaim
full instance recovery until user-level application checks pass.
[Services issue #2 native file-stage receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6940151074).

## November 16, late — NATIVE first complete off-Kvin backup ACCEPTED

**This section supersedes historical below statements that no real backup
or Peanut copy exists.** Nova completed the two actual Services playbooks
from Kvin, without any runtime or database service restarts.

1. `ansible/nextcloud-consistent-backup.yml`:
   Kvin `ok=29 changed=9 unreachable=0 failed=0`. Nextcloud
   entered maintenance mode, Maintenance's scoped PostgreSQL exporter
   returned the accepted `nextcloud` database custom-format receipt,
   full actual HTML/data tree and four private inputs were included in
   the authenticated bundle, manifest/hash/archive checks passed,
   Nextcloud **left maintenance mode** and passed HTTP readiness.
   It returned `bundle_hashes_match_manifest=true` and
   `original_nextcloud_maintenance_state_restored=true`.
2. `ansible/nextcloud-retain-on-peanut.yml`:
   Peanut `ok=14 changed=3 unreachable=0 failed=0`.
   Exactly the four expected files (`manifest.json`,
   `nextcloud-html.tar`, `nextcloud-private.tar`,
   `nextcloud-postgresql.dump`) transferred over ordinary Ansible
   SSH to a **new private directory** on Peanut. Peanut directly
   verified their SHA256 and archive structure;
   `hashes_and_archive_structures_verified_on_peanut=true`.
   **No database or service was modified on Peanut**.

**Authoritative recovery ID:** `nextcloud-20261116t233618`.

**Same private directory on both hosts:**
`/home/wdc2/.local/share/sanctum-services/backups/nextcloud/nextcloud-20261116t233618`.

**Status:** An actual **application-consistent, off-Kvin, integrity-verified
recovery point** exists. An isolated **database restore**, isolated
**application file extraction**, and a **running isolated Nextcloud**
with real account/Calendar/file checks have NOT yet been accepted.
Do not confuse backup validity with completed disaster recovery.

Services sent the exact retained path and native acceptance to
[Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6940073248)
for owner-led disposable networkless PostgreSQL Nextcloud-only restore
on Peanut, using its existing `tools/restore-nextcloud-postgresql`.
Services' next independent native operation is the source-qualified
`ansible/nextcloud-isolated-files-restore.yml` on Peanut with
`nextcloud_isolated_recovery_id=nextcloud-20261116t233618`,
`nextcloud_retained_bundle` as above and explicit
`nextcloud_isolated_file_restore_approved=true`.
This extracts only fresh isolated HTML and private data; no database is
imported, no Nextcloud container is started, and neither Kvin nor its
live service is changed. Only after both halves pass should Services and
Maintenance integrate a genuinely usable isolated application startup.

**Operator policy:** Treat these successful native tasks as completed;
don't request more SSD size checks, repeat backing scans, rerun the
backup or recopy the snapshot merely to "confirm" it. No need to
reinstate blanket `no_log` on ordinary four-file transfers.

**Status:** The existing Kvin Nextcloud installation and Calendar 6.6.2
bidirectional use are accepted. The installation/app-manifest roles are
source-managed, but **full-instance backup, independent storage, and an
isolated recovery have not been accepted**. This document authorizes no
application downtime or database change.

## November 16, late — Maintenance export handoff resolved in source

Maintenance has **published** its supported bounded
[Nextcloud-only PostgreSQL exporter](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/nextcloud-postgresql-backup.md)
(`/home/wdc2/src/sanctum-maintenance/tools/backup-nextcloud-postgresql` on Kvin).
[Maintenance's CI 43974977911](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43974977911)
accepted its source contract and **disposable PostgreSQL export/restore**.
This is **not** a native backup of Nova's actual Nextcloud database.

Services' source-only `ansible/nextcloud-consistent-backup.yml` now declares
the **exact** source-owned helper call
`/usr/bin/python3 <maintenance-helper> <new-private-nextcloud-postgresql.dump>`,
checks existence and ownership before changing Nextcloud mode, and requires
a successful helper receipt naming **only database `nextcloud`**, a
readable `pg_restore --list` catalog and the expected fixed dump basename.
The helper exports with local peer authentication, not arbitrary admin
credentials or a broad PostgreSQL installer. Both the application quiesce and
the owner-specific database export remain under **two false-by-default
execution approval switches**; no live snapshot was created, and no
automatic Nextcloud updates were enabled by this source integration.

**Maintenance helper correction:** After rereading the current exporter,
the actual runtime check matches the supported PostgreSQL repository's
image-digest **family**, then verifies server major 18; it does **not**
compare to its unused old `IMAGE` constant. The assertion that this
helper would reject any valid new PostgreSQL 18 patch image was **wrong**;
it was [explicitly corrected with Maintenance](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6939054034).
The installed PostgreSQL 18.4 Quadlet is still pinned, an unrelated
Maintenance-owned unattended-update defect.

**Next real native qualification** after Services CI: one read-only Kvin
version/runtime/help-path and timer inventory, private backup directory
capacity checked earlier, then approved short maintenance-mode capture,
independent off-Kvin custody, and isolated restoration. A first backup
still needs explicit owner/operator coordination; this paragraph is not
live permission.

## November 16 — Services next native recovery milestone is now unblocked

Maintenance confirmed that **Services should run the coordinated backup
playbook in an agreed short overnight Nextcloud maintenance window**,
without a preceding separate Maintenance command. The source integration
has [CI pass 44001769569](https://github.com/wdcallahan/sanctum-services/actions/runs/44001769569).
The first actual backup has **not been run yet**.

The follow-on source-only
`ansible/nextcloud-retain-on-peanut.yml` takes the completed named private
four-file bundle from Kvin, verifies it locally, copies precisely those
four files with Ansible-managed SSH to a **fresh owner-only directory** on
Peanut, then checks archive structure and hashes **on Peanut**. This
supplies independent retention, not database or full application restore.
Its source, regression and Ansible syntax tests **passed [CI run 44021986569](https://github.com/wdcallahan/sanctum-services/actions/runs/44021986569)**; native use remains a separately operator-approved operation. Later an isolated application
and owner PostgreSQL restore rehearsal can qualify the retained point.
Avoid asking Nova to run duplicate source/SSD/Nextcloud login probes.

The **first backup** will briefly put Nextcloud into maintenance mode,
export only the Nextcloud DB, capture its persistent HTML tree and private
inputs, verify the manifest, and **turn maintenance mode off even on a
normal task failure**. Production user data, calendar, PostgreSQL's other
databases and the system services are not otherwise altered. If Ansible
is killed while the remote task is between mode-on and mode-off, the
operator must explicitly check and restore normal Nextcloud mode; an
`always` block cannot guarantee recovery after an interrupted controller.

## Consistency model — not atomically synchronized at every instant

Nextcloud's file tree and PostgreSQL are **two distinct stores**; they do
**not** have to match at the same hypothetical instant during ordinary
operation. Do not describe a Planck-time matching requirement to Nova.
PostgreSQL `pg_dump` produces an internally consistent database export
even while other sessions use the database
([PostgreSQL 18 documentation](https://www.postgresql.org/docs/18/app-pgdump.html)).
The purpose of putting **Nextcloud** into maintenance mode for a recovery
point is to **limit cross-store application changes while the two backups
are taken**. It does **not** stop the shared PostgreSQL server, and it
doesn't require simultaneous physical filesystem/DB snapshots.

**Failure/rollback semantics:** If an old DB is restored while newer files
remain, some files may no longer have the corresponding indexed metadata,
while some database records may refer to missing/old content. Filesystem
rescan and client reconciliation can address *some* mismatches, but cannot
reconstruct arbitrary application-only records such as calendar entries
that were written after the recovered database state. Conversely,
restoring an older file tree against a newer DB can also produce
temporarily inaccessible records. Nextcloud's
[official restore guide](https://docs.nextcloud.com/server/stable/admin_manual/maintenance/restore.html#synchronising-with-clients-after-data-recovery)
specifically discusses outdated backups and provides
`maintenance:data-fingerprint` and `files:scan` as **situational** recovery
tools; it warns that the former can produce conflicts and is **not**
routine after every recovery. Preserve newer state before reconciliation
and test against an isolated restore rather than rewriting live Kvin.

**Operational consequence:** Aim for an application-quiesced window and
paired files+DB recovery point as the safest, simplest *backup* approach,
**not** because Nextcloud is incapable of surviving a mismatch. The
objective is predictable recovery with minimal missing metadata and
minimal lost edits. This does not imply a PostgreSQL cluster restart,
shared-server downtime, or zero-length capture window.

## Accepted operating policy — brief maintenance window, two recovery modes

**Nova's November 16 decision:** This is a low-traffic personal Nextcloud.
Short scheduled overnight maintenance-mode backup windows and the possibility
that an active client must retry an interrupted transfer are acceptable.
We do not need a zero-downtime backup architecture. Do not promise an exact
few-minute duration: the currently observed HTML tree alone has 5.77 GB
of ordinary file data; measure real end-to-end tar + dump + verification
before selecting a frequency/window. Maintenance mode is a lockout/status
screen, not a guaranteed advance user notification or graceful resumable
upload mechanism. Existing users may need to refresh/reconnect.

**Separate supported recovery intents (both need isolated rehearsal):**

- **Complete snapshot recovery:** Restore the matching HTML/config/private
  files and Nextcloud-only database dump from one protected recovery point.
  This is the simplest deterministic path after a lost server or filesystem.
- **Database-only rollback with the *current* filesystem preserved:** Use a
  selected older Nextcloud database backup **without silently replacing the
  current data tree**. Before touching production, preserve *today's*
  database and file tree as a new immutable recovery point, then rehearse the
  older database with a **copy** of the current file tree in an isolated
  instance and isolated database. Reconcile filecache/index discrepancies
  with the supported `occ files:scan` tools when appropriate, and evaluate
  `maintenance:data-fingerprint` and sync-client behavior for this specific
  outdated-backup scenario. Verify current user files, deleted/moved/renamed
  files, sharing, calendar entries, and working login. Do not treat these
  `occ` commands as a magic reconstruction of database-only Calendar data
  written after the rollback point. Confirm Nextcloud application version
  and DB schema compatibility; rollback across an application/schema
  upgrade is not assumed safe. Only then approve a production database-only
  rollback.

These are the **same Ansible recovery workflow with explicit modes**, not
two unrelated projects. A passed tar verifier is not evidence that the
DB-only rollback mode works; it requires a separate real isolated trial.
No production rollback is authorized yet.

Nextcloud's official [backup](https://docs.nextcloud.com/server/stable/admin_manual/maintenance/backup.html)
and [restore/reconciliation](https://docs.nextcloud.com/server/stable/admin_manual/maintenance/restore.html#synchronising-with-clients-after-data-recovery)
guides describe maintenance mode, client recency, data fingerprint and
file scans. The reconciliation advice needs to be tested on the *deployed*
Nextcloud version before claiming this mode accepted.

## Operator model — two Ansible jobs and one protected recovery point

**What Nova should picture:** This is a straightforward Ansible-managed backup
and restore of one running Nextcloud instance, not a new security architecture.
Nextcloud's application and user files are in the **bind-mounted host directory**
`/home/wdc2/srv/sanctum-services/nextcloud/html` (mounted at
`/var/www/html` inside the container), **not** a separately named Podman
volume. Nextcloud's records and Calendar entries also depend on its **own**
database in the Maintenance-owned PostgreSQL service. The user-specific
private config inputs live separately under
`/home/wdc2/.config/sanctum-services/nextcloud`.

**Backup playbook, eventual result:**

1. Confirm destination and sufficient available space; obtain the exact
   app-scoped PostgreSQL export interface from Maintenance. No whole-cluster
   backup or PostgreSQL reconfiguration is involved.
2. Put Nextcloud in maintenance mode while recording one consistent
   recovery point: tar the persisted HTML tree **including links and file
   metadata**, export **only** its PostgreSQL database, and package the
   private inputs. Always turn maintenance mode off even if capture fails.
3. Place one named `nextcloud-YYYYMMDDTHHMMSS/` snapshot **off Kvin**
   (Peanut is a possible destination, not yet capacity-accepted).
   The protected directory contains these **exact four files**:

   ```text
   nextcloud-YYYYMMDDTHHMMSS/
     nextcloud-html.tar
     nextcloud-postgresql.dump
     nextcloud-private.tar
     manifest.json
   ```

   The manifest contains file sizes and checksums. The data plus config
   archives contain real private material; keep the **snapshot private**.
   There is no reason to conceal ordinary symlink filenames or fixed
   application paths from Nova. Tar entry types and safe restore paths
   should be validated, but our own live source isn't inherently hostile.

**Restore playbook, eventual result:** On a different, isolated host, verify
the retained recovery point, stage the file tree with preserved ownership
and links under an isolated rootless Podman namespace, stage its private
inputs, have Maintenance restore **only** the Nextcloud database into an
isolated database/role, start the pinned Nextcloud image and Quadlet against
that database, and check that login, user files, a known Calendar entry,
and normal application operations work. Existing Kvin production, other
PostgreSQL databases, YXORP, DNS and its users stay untouched. An actual
production cutover would be a **third, separately approved action**, not
a side effect of a restore trial.

**What already exists versus what doesn't:** The source-only guarded
`ansible/nextcloud-consistent-backup.yml` candidate, the bundle
producer/verifier, and their synthetic tests exist. Kvin's actual source tree
was successfully checked read-only (28,955 regular files, 3,877 directories,
118 safe contained links and 4 private inputs; 5,769,576,446 bytes of file
content by metadata). **No real application backup, PostgreSQL dump,
off-host retained snapshot, or completed restore playbook has been
accepted yet.** The Maintenance owner export contract, destination capacity,
native backup approval and isolated restore qualification remain open.

**Why any guardrails at all?** Permission checks govern what the backup
process can read; care is also needed not to dereference symlinks outside
the intended source or write archive members outside the new destination
when restoring. Those are implementation-level precautions, not a reason
to obscure ordinary file names, lecture the operator about filesystem basics,
or require a dozen diagnostic turns. Actual passwords, private config
contents and credential-bearing snapshots are the information to protect.

## Source-only isolated restore staging candidate

`ansible/nextcloud-isolated-files-restore.yml` now expresses the **simple
filesystem half** of the restore job. Its only managed host is the
**separate Peanut trial** (`peanut.arcane.sanctum`), not Kvin. It requires
an explicitly supplied recovery-point directory *already retained on Peanut*,
a fresh named destination and explicit approval; it first verifies the four
expected bundle members and manifest, then uses `podman unshare tar` to
extract `nextcloud-html.tar` and `nextcloud-private.tar` into separate
**new, isolated** directories. GNU tar and the user namespace preserve
the archive's numeric ownership, modes and links; production Kvin stays
unchanged. Its output deliberately says **database not imported; no container
started; restore not accepted**. On failure, partial isolated staging remains
available for review, never silently treated as usable restoration.

This is a **source candidate only** until CI and native qualification.
No retained source bundle exists yet, destination capacity is not accepted,
and the playbook is **not** an instruction to execute it today. The actual
database restore, isolated database creation, Quadlet start and user Calendar
acceptance are separate remaining stages of the same eventual Ansible
restore workflow, not extra service migrations. If Peanut is later rejected
as the independent recovery host, revise the target explicitly rather than
silently redirect to production Kvin.

## Recovery contents and ownership

- Include the **actual** Nextcloud data directory, configuration,
  installed/custom app files, and user content. The source role mounts
  `~/srv/sanctum-services/nextcloud/html` at `/var/www/html` and a native `occ` query on November 16 **confirmed**
  `/var/www/html/data` as the configured data directory.
- Include a consistent application-specific PostgreSQL database snapshot.
  Sanctum Maintenance owns the shared PostgreSQL service, connection and
  host lifecycle; Services owns Nextcloud application recovery. Never
  restore the whole shared database cluster to recover one application.
- Recover secret files privately via the established Vault and custody
  mechanisms. No passwords, config.php contents or bearer credentials
  belong in Git or operator transcripts. The administrator password
  is not supplied by the Services Ansible role.
- Preserve the pinned application image and Calendar 6.6.2 declaration,
  along with the Quadlet, YXORP/DNS dependencies and restore order.
  Reinstalling an app does not restore calendar entries or user accounts.

## First observation — read-only, no changes

`ansible/nextcloud-recovery-inputs.yml` runs **only against current Kvin**.
It checks the presence (not content) of required files and directories,
the user service state, and local `/status.php`. It does not dump a
database, export files, modify a service, read passwords or establish that
a backup exists. The input observer only checked presence, but the separate accepted
native `occ` query has since confirmed `/var/www/html/data`.

After source CI and Ansible syntax qualification, run from the existing
Services checkout on Kvin:

```console
~/.local/bin/ansible-navigator run ansible/nextcloud-recovery-inputs.yml
```

Return only `Report only bounded recovery-input availability` and the
play recap. No passwords or raw application configuration.

## Next implementation after native observation

1. Use the **confirmed** `/var/www/html/data` path and select an appropriate
   **off-Kvin** protected backup destination with capacity, integrity
   verification and retention; another path on Kvin alone is not disaster recovery.
2. Create a bounded maintenance-mode operation that prevents application
   writes, takes a coordinated Nextcloud-only PostgreSQL snapshot and
   archives the required files/private configuration as **one named recovery
   point**. Restore the existing application's prior service state on failure.
3. Restore to an **isolated** service and separate database without changing
   Kvin's live Nextcloud, shared PostgreSQL state, production DNS or YXORP.
   Apply the existing protected credentials via their supported owner.
4. Verify representative user files, settings, login, a known Calendar
   entry, and repeat-converged source reconciliation. Document update,
   rollback and deliberate removal with data-retention choice.
5. Only then consider production replacement via a separately approved
   operator decision.

Kvar is already **powered off**; there is no reason to turn it on for this
work. Project Joule owns Prism and Bunny Factory owns the VyOS routers.

## November 16 — effective data path and recovery-bundle integrity

Nova's **native read-only** command on running Kvin returned exactly
`/var/www/html/data` from `podman exec -u www-data sanctum-nextcloud php
occ config:system:get datadirectory`. This is a confirmed configured path,
not an inference from directory presence. The existing Quadlet's bind
`~/srv/sanctum-services/nextcloud/html:/var/www/html` includes that data
directory, `config/config.php`, and `custom_apps`.

**Do not repeat** the accepted six-task native input play or this OCC query.

The source-only `tools/nextcloud-recovery-bundle.py` verifies one
privately staged recovery bundle, with three exact artifacts: a full HTML-tree
tar archive, a private configuration/credential tar archive, and a
**Nextcloud-database-only** PostgreSQL custom-format dump. Its
`manifest.json` must name the exact host, data directory, and database;
each artifact needs a byte count and SHA-256. The verifier rejects unexpected
filenames, symlinks, group/world readable payloads, malformed paths,
special archive members, missing required state, and a missing PGDMP
header. It never extracts the archives or prints contents or credentials.

Example **manifest structure** (fake digests; not a usable backup):
```json
{
  "schema": "sanctum-nextcloud-recovery-bundle/v1",
  "source_host": "kvin.outer.sanctum",
  "data_directory": "/var/www/html/data",
  "database": "nextcloud",
  "artifacts": {
    "application": {"filename": "nextcloud-html.tar", "bytes": 123, "sha256": "REPLACE"},
    "credentials": {"filename": "nextcloud-private.tar", "bytes": 123, "sha256": "REPLACE"},
    "database": {"filename": "nextcloud-postgresql.dump", "bytes": 123, "sha256": "REPLACE"}
  }
}
```
The validator can run offline as
`python3 tools/nextcloud-recovery-bundle.py /private/recovery-point`
**after** the application+database snapshot operation has been designed and
approved. It is not a command to run on live Kvin today; no recovery bundle
exists yet.

Passing manifest/hash/header checks proves **byte integrity only against
that manifest**; they do not establish snapshot consistency, authenticity of
the manifest, off-host custody, a valid SQL restore or working Nextcloud.
The actual coordinated backup procedure, authenticated retention and isolated
restore are still pending. Never pass private archive contents or generated
secrets through issue comments. Maintenance owns the shared PostgreSQL
service and the narrow Nextcloud database dump interface; the Services owner
has requested that interface on Maintenance issue #17. No production
Nextcloud maintenance-mode change, file snapshot or DB dump has been run.


## November 16 — private bundle producer (source only, no native backup)

`tools/nextcloud-recovery-assemble.py` now provides the missing **file-level
bundle assembly** counterpart to the earlier read-only verifier. It reads
an **already-quiesced, accessible** Nextcloud HTML source tree, the exact four
private credential/configuration inputs and an already-produced
**Nextcloud-only PostgreSQL custom-format dump**. It writes three protected
payloads and a manifest into a **new** 0700 directory (0600 files), then calls
the existing integrity verifier. It refuses missing files, linked or special
members, wrong dump header, pre-existing output names and output nested inside
its own input trees. Its output deliberately continues to report
`consistent_snapshot_proven=false`, `database_restore_tested=false` and
`independent_off_host_retention_proven=false`.

**No Kvin invocation is approved yet.** This tool neither selects a snapshot
time nor enters/exits Nextcloud maintenance mode. It does not invoke pg_dump,
restore PostgreSQL or copy data to Peanut. A malformed or interrupted attempt
may leave a private **incomplete** output directory; it is never evidence
of a successful recovery bundle. Before native use, explicitly qualify the
existing rootless user-namespace/host-file read permissions for all Nextcloud
data, including UID 33-owned paths. Do not work around permission errors by
changing live ownership or broadening permissions.

The source-only tests exercise complete fixture assembly, private output modes,
missing inputs, symlinks, collision protection, unsafe destinations and invalid
dump signatures. Production still needs the **Maintenance-owned scoped database
export contract**, a guarded Services coordinator that confirms and restores
Nextcloud's maintenance state, one consistent write-freeze window, protection
and verification of an off-Kvin copy, and a real isolated restore. No current
operator action is implied by source CI success.

**Planned operator sequence (not yet an executable runbook):** review approved
authorization and destination -> confirm correct running source and writable
quiescence control -> enter Nextcloud maintenance mode -> Maintenance-scoped
database export while writes remain quiesced -> assemble matching application,
private and database bytes under the same freeze -> validate -> **always**
restore the original maintenance state and verify service health -> transfer
privately to an independent host and verify -> isolated restore and consumer
acceptance. A failed database export must never silently publish the source
bundle as a valid recovery point.

## November 16 — guarded coordinator candidate and rootless-readability gate

`ansible/nextcloud-consistent-backup.yml` is now a **source-only guarded
candidate**, not an approved operating playbook. It requires an exact Kvin
target, separate explicit live/write-quiescence authorization, and an
approved **complete owner-supplied argv list** for a synchronous scoped
PostgreSQL dump whose output path matches its privately staged destination.
It refuses an uninstalled or already-maintained instance, enables
maintenance mode, confirms that status, invokes the owner export, assembles
files while writes are quiesced, and has an Ansible `always` sequence to
return Nextcloud to its prior **nonmaintenance** state. That source and its
unit/syntax checks do **not** prove a successful live run, full maintenance
consistency (including independent writers), the owner interface, archive
read permissions, off-host retention, or restore. **Never paste this
playbook's approval variables or invoke it until these prerequisites are
settled.** The resulting files, if ever produced, are only a local Kvin
bundle until independently protected on another host.

Before using this coordinator, the new
`tools/nextcloud-recovery-readability.py` can traverse the entire
current HTML bind and four private credential/config inputs **read-only**
within the same `podman unshare` rootless user namespace planned for the
producer. It attempts a one-byte read from every regular file and rejects
symlinks/special members and unreadable subtrees. It returns *only aggregate
counts and boolean status*, not paths or contents. This is a distinct
necessary gate from the already accepted ten-path presence observer.
A pass establishes source readability at that instant, **not** a snapshot,
absence of concurrent writers, owner dump interface, or recovery.

**Single Kvin-only read-only operator check after CI accepts this source**:

```bash
cd ~/src/sanctum-services &&
git pull &&
podman unshare python3 tools/nextcloud-recovery-readability.py \
  --html-root /home/wdc2/srv/sanctum-services/nextcloud/html \
  --private-root /home/wdc2/.config/sanctum-services/nextcloud
```

This performs no Nextcloud service change, no DB operation, no backup creation
and prints no user files. Return the single sanitized JSON record (or the
exact failure); report `git pull` errors if it stops before the scan.
**Do not** send archive contents or credentials.

## November 16 — first native readability refusal and diagnostic correction

Nova ran the **read-only** Kvin `podman unshare` source traversal and received
`Nextcloud bundle source traversal refused (private details withheld)`.
This confirms the gate **refused**, not why; no private files were reported,
no backup was created, and no application/database mutation was requested.
**Do not infer a permission failure, symlink, or missing input from the
generic denial. Do not alter filesystem permissions to make it pass.**

The original diagnostic suppressed all cause information. Source now reports
a fixed, private-safe JSON error containing only `status=refused`,
`stage` (`required_inputs`, `html_tree`, `private_inputs` or `startup`),
and `reason` (a bounded error category), with no real filenames, file
contents, or passwords. CI tests verify redaction, failure-stage mapping
and the previously accepted read-only success contract.

**Next Kvin action once diagnostic source CI is green:** repeat the same
nonmutating command from the immediately preceding section after normal
`git pull`. Return the **one JSON record on stdout or stderr**, not raw
paths or private data. This is a targeted attempt to identify the *cause*
of the first refusal and is not reopening the earlier successful
ten-path/occ inspections. If the gate still refuses, fix only the
identified producer/namespace/permissions issue with review before an
actual live backup operation.

## November 16 — actual HTML-tree special-entry gate (no permission changes)

Nova ran the source-qualified Kvin full-tree scan again. It returned exactly
`{"application_interrupted": false, "backup_created": false,
"file_paths_or_contents_returned": false, "reason": "unsafe_source_member",
"stage": "html_tree", "status": "refused"}`. This establishes that the
source contains at least one unsupported entry type **within the existing
HTML tree**. It is not evidence of a general file-read permission failure.
The producer currently supports only ordinary files and directories and
the integrity validator likewise rejects symlinks and special archive
members. **Do not strip links, silently skip the entry, chmod/chown the
tree, or relax archive extraction safety just to make this pass.**

A new standalone, read-only `tools/nextcloud-recovery-specials.py`
classifies **all** HTML-tree entry types, aggregates unusual members by
fixed broad component groups (`config`, `data`, `custom_apps`,
top-level or other), and classifies links as absolute/relative,
resolved inside/outside the source or dangling. It returns counts and
known safe labels **only**; no individual names, link targets or file
contents. It does not follow symbolic links or create an archive.

**Next single Kvin-only operator action after CI passes:**

```bash
cd ~/src/sanctum-services &&
git pull &&
podman unshare python3 tools/nextcloud-recovery-specials.py \
  --html-root /home/wdc2/srv/sanctum-services/nextcloud/html
```

Return the complete JSON result, or the exact command failure. This is a
**new classification** of the accepted refusal, not another meaningless
repeat of the existing readiness observer. If links are internal, assess a
safe self-contained archive/restore policy and tests; if external, identify
their real data owner and reconstructible backing *without assuming their
targets are included*. If the offending entries are sockets, FIFOs, or
devices, determine whether they are transient and how a consistent backup
procedure should exclude or reconstruct them **before** modifying the
producer and validator. No native backup, interruption or database dump is
authorized by this scan.

## November 16 — internal-link discovery and source-policy correction

Nova ran the Kvin metadata-only classifier and returned this **native,
nonmutating source topology receipt**:

| Source class | Count |
| --- | ---: |
| Ordinary directories | 3,877 |
| Ordinary files | 28,955 |
| Symbolic links | **118** |
| Other special entries (FIFO, device, socket, unknown) | **0** |
| Absolute or externally resolving links | **0** |
| Dangling or unresolved links | **0** |

All 118 links are **relative**, resolve **inside the same HTML tree**, and
occur under the classifier's broad `other` region (neither `data`,
`config`, nor `custom_apps`). Total entries reported: 32,950.
**Do not rerun the classifier without a specific new reason.**

**Revised Services source policy (source-only until CI + native gate):**

- Preserve a relative link *as a link*, rather than copy its target data,
  silently omit it or follow it out of the persistent tree.
- Producer `tools/nextcloud-recovery-assemble.py` permits a link only if
  relative, lexically confined to the HTML source and strictly resolvable
  inside that same source. Missing, cyclic, absolute and external targets
  are rejected. The file walk never descends through a link. Private
  credentials remain ordinary file-only inputs.
- Independent `tools/nextcloud-recovery-bundle.py` archive verification
  requires every application link to be relative, archive-confined,
  resolvable through any finite internal link chain to a member **actually
  present in the archive**. Reject linked parents with archive entries
  underneath them, duplicate paths, dangling/cyclic/escaping links,
  hardlinks and special file types. Private credential tar links are still
  forbidden. Verifier performs **zero archive extraction**.
- `tools/nextcloud-recovery-readability.py` now checks the complete real
  source tree, verifies link eligibility without dereferencing linked file
  contents, and returns sanitized counts (including
  `html_relative_internal_symlinks`). Source tests simulate both allowed
  links and malicious archive metadata.
- This acceptance is for archive **construction and verification**, **not**
  direct unsafe extraction. The *future isolated restore* must implement
  and test a separate extraction strategy that does not follow preexisting
  or archived symlinks outside its new private staging root.

**Next native test after all modified code passes CI:**

```bash
cd ~/src/sanctum-services &&
git pull &&
podman unshare python3 tools/nextcloud-recovery-readability.py \
  --html-root /home/wdc2/srv/sanctum-services/nextcloud/html \
  --private-root /home/wdc2/.config/sanctum-services/nextcloud
```

This is **not a retry of an unchanged diagnostic**: it qualifies the
source-selected preservation policy against the actual **118 already
identified** links. Expect one sanitized JSON record; do not send user
content or any credentials. No production service or database mutation,
no backup creation. The separate Maintenance-owned Nextcloud-only PG dump
interface and approval for an eventual write-quiescing operation remain
outstanding.

## November 16 — complete rootless source-readability gate accepted

Nova ran the **updated** rootless private+HTML scan on Kvin. Native evidence:

```json
{
  "source_tree_readable_for_assembler_at_scan_time": true,
  "html_regular_files": 28955,
  "html_directories": 3877,
  "html_relative_internal_symlinks": 118,
  "html_file_bytes": 5769576446,
  "private_required_files_readable": 4,
  "unaccepted_special_members_observed": 0,
  "application_interrupted": false,
  "database_exported": false,
  "recovery_bundle_created": false,
  "consistent_snapshot_proven": false,
  "off_host_backup_proven": false
}
```

The native output was sanitized; this is a summary of selected fields, not an
assertion that *every byte was read*. The scan opens each regular file for a
one-byte readability test, checks all private inputs, and validates all 118
relative contained links against the updated producer contract. Source file
sizes sum to **5,769,576,446 bytes** (5.77 decimal GB) before archive overhead,
an application database dump, working space, and an independent retained copy.
**Do not rerun this already accepted scan or prior ten-path and data-dir
observations.** No real backup or restoration has yet taken place.

### What the links are (and are not)

The previous producer refused **all** symbolic links so that a backup could not
silently follow a pointer to outside or secret host data. The revised source
preserves only relative, fully contained links **as links**, with the independent
archive validator checking that their targets are actually included and safe
inside the archive. This changed **future backup software policy**, not the
live Nextcloud installation or its links. The classifier counted the links but
redacted their specific names/targets; therefore their individual identity,
purpose, and specific Nextcloud subdirectory are **not yet known**. Do not
claim they are a specific vendor package or module without inspecting their
names.

If Nova wants to inspect examples for understanding, this **read-only Kvin
metadata-only** command shows the first 25 relative source link names and their
relative targets (no file contents). It is not a prerequisite for backup
qualification; it serves the operator's understanding and may expose
filenames, not secrets. It does not need a conspicuous operational warning.

```bash
podman unshare find /home/wdc2/srv/sanctum-services/nextcloud/html -type l \
  -printf '%P -> %l\n' | sort | sed -n '1,25p'
```

**Next planned engineering work:** approve off-Kvin storage with enough free
space for one 5.77 GB plus-dump snapshot and extra working headroom; preserve
metadata/UID mappings needed for an isolated file restore; prove independent
archive extraction safety; and integrate the Maintenance-owned Nextcloud-only
database dump when its contract is available. A real maintenance-mode
interruption is separately approval-gated.

## November 16 — apparent 5.77 GB, disk inventory and Kvin/Peanut role correction

Nova has **not moved normal user files into Nextcloud yet**. The accepted
one-byte readability scan summed the *apparent lengths of ordinary files in
the whole bind-mounted HTML tree*, not `du` filesystem blocks and **not**
the size of user uploads. Nextcloud's official container layout places
the shipped `apps`, application code and dependencies under
`/var/www/html` alongside `data` (actual user files) and `config`.
The ordinary observed `apps/.../*.js.map.license` symbolic links are
application build products. The reason for the observed large total is
**still unknown** until the directory breakdown is measured; do not
assume uploads, runaway logs, or cache without evidence. Source:
[official Nextcloud container layout](https://github.com/nextcloud/docker/blob/master/README.md#persistent-data).

**Hardware/HA design intent from Nova:** Kvin and Peanut should be analogous
hosts and eventually have matching SSDs; one is currently approximately
0.5 TB and the other approximately 1 TB, with **which host has which size
not yet verified**. They are meant to provide primary/secondary database
service with an up-to-date peer, with redundant/hot-spare behavior for some
workloads and possible backup custody for others. This is an operator
**goal**, not evidence PostgreSQL replication/failover is active. A replica
copies bad transactions too, so it is not a substitute for a retained
historical point-in-time snapshot; and a PostgreSQL replica alone does not
replicate Nextcloud's HTML/data files. Maintenance #17 owns the actual
PostgreSQL topology and owner-supported scoped dump/isolated restore. The
[latest Services-to-Maintenance contract](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6932965316)
spells out the short application lock, database-only rollback and expected
Kvin/Peanut authority, with **no live changes approved**.

**One read-only operator discovery command** from Kvin as `wdc2` should
show two-level HTML `du` distribution, Kvin's underlying mount and disks,
and Peanut's filesystem free space and block device sizes via noninteractive
SSH. Clearly tell Nova before pasting that the last part **queries Peanut
remotely**. These are measurements for capacity and role planning only:
no config, databases, containers or storage are changed. Choose destination
and retention only once both actual capacities are known.


## November 16 — Native HTML allocation and controller SSD sizes resolved

Nova ran the approved **read-only Kvin rootless `du`** and
noninteractive Peanut SSH device check. The actual allocated directory
breakdown from `du -h` was:

| Kvin Nextcloud HTML component | Approximate disk allocation |
| --- | ---: |
| Entire persisted HTML mount | **5.5 GiB** |
| `data` | **4.6 GiB** |
| `data/wdc2` | **4.4 GiB** |
| `data/appdata_oc0fmherf6qh` | **112 MiB** |
| `apps` (shipped Nextcloud apps) | **523 MiB** |
| `core` | 158 MiB |
| `custom_apps` (Calendar etc.) | 97 MiB |
| `dist` | 75 MiB |
| `3rdparty` | 53 MiB |

Thus **the unexpected majority is the single Nextcloud user account
directory `data/wdc2`**, not Nextcloud shipped code. Nova states
he has not yet meaningfully migrated his data. **We don't yet know what
inside `data/wdc2` accounts for 4.4 GiB**; do not guess default
skeleton, orphaned uploads, test files, versions or trash without
checking the next level. Preserve all user files, hidden folders,
shares/versions/trash and database metadata; **no cleanup/delete** is
authorized. Next operator step is a read-only `du` within
`data/wdc2` and optionally an actual largest-file-name list (names,
not file contents), if Nova is comfortable reporting those file names.
Do not rerun already accepted full-tree readability, link scans, or
host-capacity test.

**Actual Kvin/Peanut device identity and capacity (read-only):**

- Kvin `/dev/nvme0n1`: **931.5 GiB** Crucial CT1000P3SSD8;
  root `/dev/nvme0n1p2`, ext4 **917 GiB** capacity,
  **32 GiB used, 849 GiB free**.
- Peanut `/dev/nvme0n1`: **465.8 GiB** Kingston SNV2S500G;
  root `/dev/nvme0n1p2`, ext4 **459 GiB** capacity,
  **8.0 GiB used, 432 GiB free**.
- Nova wants both originally symmetric; **Peanut** is the half-sized
  drive to replace eventually. There is ample present disk space
  for capacity investigation. This does not establish any live
  PostgreSQL replication, and the backup design must not equate
  replication with historical independent recovery.

The Services→Maintenance owner-interface request and intended
primary/secondary reconciliation remain at
[Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-6932965316).
No live host/database mutation is required by this observation.
