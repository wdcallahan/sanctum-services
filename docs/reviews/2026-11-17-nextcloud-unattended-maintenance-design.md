# Nextcloud on Kvin — unattended maintenance update design (source proposal)

**Date:** 2026-11-17  
**Owner:** Sanctum Services (Nextcloud app); Sanctum Maintenance (PostgreSQL/host facilities)  
**Status:** DESIGN ONLY, not a deployed updater, running automation, approved image change or proof of restore.  
**Issues:** [Services #5](https://github.com/wdcallahan/sanctum-services/issues/5), [Services #6](https://github.com/wdcallahan/sanctum-services/issues/6), [Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17).

## Why update cadence matters (Nova, November 17)

Nova explicitly requires **reasonably frequent unattended maintenance updates**, including timely review of supported major upgrades: staying frozen for months increases the eventual upgrade distance, compatibility exposure and operational cost. Do not reinterpret a protected backup prerequisite as permission to postpone all updates indefinitely. Maintain a functioning, repeatable patch/update cadence, and plan major version hops proactively while each supported migration path remains manageable. For Nextcloud, automatic **within-34** release progression and a separate planned **34→35** upgrade are distinct paths, not a reason to choose `:latest` or skip PostgreSQL consistency. A verified backup lowers risk; an actual restore rehearsal must remain a finite concurrent objective rather than a perpetual theoretical veto. The initial production promotion remains gated by the expressly accepted restore contract until it can be safely qualified.

### Newly implemented source-only candidate gate

`ansible/nextcloud-qualify-maintenance-image.yml` now preflights the exact running Kvin Nextcloud, confirms it still has the frozen original image, pulls **only** the official `34.0-apache` image into Kvin's rootless image cache, checks actual ARM64 metadata and uses a short **networkless, read-only, ephemeral** PHP container to read the shipped Nextcloud version. It verifies that the candidate stays in major 34, minor 0 and doesn't regress below the actual running patch. It does **not** touch the live Quadlet, app, database, proxy, ports, timer, or backup. It is source-only until Nova runs it; its registry/cache/image probe is distinct from the already accepted read-only production baseline.

## Accepted actual baseline — do not repeat observation

Nova executed `ansible/nextcloud-update-readiness.yml` on Kvin on Nov17. Exact TASK `Report actual Nextcloud update baseline without starting an upgrade`; `PLAY RECAP: ok=8 changed=0 failed=0 unreachable=0 skipped=0`. Nextcloud installed **34.0.5** (internal **34.0.5.1**), maintenance=false, needsDbUpgrade=false. Installed rootless Quadlet, running image and Git agree on immutable `nextcloud@sha256:bcf8db2ebb4c5365f8ac8ca89d3857efecd88df68147353fbfe019b6dc888145`; no `AutoUpdate=registry`. This was a read-only observation; nothing was upgraded.

Accepted separate recovery evidence, **not to be regenerated to prove this baseline:** consistent source backup `nextcloud-20261116t233618`, independent full four-file Peanut SHA/archive retention, and isolated application/private file extraction on Peanut. **Not yet demonstrated:** an isolated Nextcloud-only PostgreSQL restore supporting a running independent Nextcloud and actual login/file/Calendar acceptance. Maintenance owns the database restore interface.

## Upstream documented channel and risk

- [Nextcloud Docker official tag guide](https://github.com/nextcloud/docker/wiki): use **`docker.io/library/nextcloud:34.0-apache`** as the candidate rolling **within-34.0.x maintenance** channel. Avoid `:latest`, `:apache`, `:stable` and any channel that silently changes major. Verify real ARM64 image and candidate version before any live apply. Unlike an immutable digest, an advancing tag is **necessary but not sufficient** for unattended updates.
- [Current official release schedule](https://github.com/nextcloud/server/wiki/Maintenance-and-Release-Schedule): 34.0.6 was released Nov12 2026; 34 is maintained through Jun2027. Do not jump to 35 for an ordinary 34 security patch.
- [Official Docker upgrade instructions](https://github.com/nextcloud/docker/blob/master/README.md#update-to-a-newer-version): on new image/container startup Nextcloud compares the image with the version in persistent `/var/www/html`, and may automatically upgrade application data. A rollback of the image alone **does not undo schema/data mutations**. Preserve exactly the existing HTML bind, four private inputs, database, rootless namespace mapping, ports, user service and Calendar app.

## Required ordering for a source-managed automatic cycle

1. **Scope, lock and release check.** Only Kvin's original rootless Nextcloud; protect against overlapping manual/automated operations or existing maintenance mode. Check official `34.0-apache` ARM64 version/digest against the currently running image and within-major rule. If unchanged, perform no disruptive operation. Do not infer image freshness solely from the version string: base-image security rebuilds can change the digest.
2. **Backup gate before a changed image starts.** Reuse the existing Services consistent-backup playbook, which asks Maintenance's *Nextcloud-only* PostgreSQL export helper and captures the matching HTML/data/config under a brief maintenance window. Then reuse the existing Peanut retention and independent artifact validation. Require a positive, uniquely identifiable complete recovery point **and** validated off-host custody before allowing the update stage. Do not invent a new PostgreSQL dumper or re-export other databases. A preexisting one-time November16 backup is not a substitute for backing up the *current* state before a later scheduled update.
3. **Guarded candidate and activation.** Use source-owned automation, not ad-hoc `podman pull && systemctl restart`. Refuse major-version drift and missing/failed backup. Preserve stable settings; apply the qualified new 34.0 Apache image to the existing rootless Nextcloud Quadlet. Stop/restart only the Nextcloud unit. Allow a normal brief overnight interruption and normal client retry, not an unsupported promise of zero downtime.
4. **Observe success/failure.** Check container identity/version, installed=true, maintenance=false, needsDbUpgrade=false, status HTTP200, and Calendar's declared/installed compatibility. A supported representative file/login/Calendar client acceptance is required at the initial live promotion; regular unattended checks should be appropriately bounded and not gratuitously re-run full user tests after every no-op cycle. Record actual old/new image identity, recovery point, timings, result and failure without exposing environment/credentials.
5. **Recovery and failure policy.** Do not treat an old image or restored Quadlet alone as a reliable downgrade after startup migrations. If failure occurs, stop automatic retries and report the recovery point and actual diagnostic. Recovery is the consistent **application files + private inputs + scoped database** restore path, once fully qualified; preserve any changed user data and require explicit approval for a destructive production restore. Document safe refusal when a dependency is down rather than advancing without a backup.

## Scheduling and source architecture

**Do not attach `AutoUpdate=registry` to the production Nextcloud Quadlet and leave the existing shared user `podman-auto-update.timer` free to restart Nextcloud.** That independent timer cannot be relied on to first execute the coordinated application+PostgreSQL backup and offhost acceptance. Other source-qualified services using that timer should remain unaffected.

Prefer a **separate source-managed scheduled workflow** (possibly a rootless user systemd timer invoking the already-established Services Ansible control path) that determines candidate freshness, executes the existing backup/Peanut custody, applies only this service, and performs post-update checks. Select exact timer cadence, log/notification semantics and retention after testing against actual Kvin/Peanut controller/runtime constraints, and preserve the user's learning goal of transparent Navigator/EE/Ansible, not an opaque private updater framework. No new permission to deploy a timer is inferred from this design.

A separate recurring backup schedule must also exist independently of whether upstream published new images. Select bounded retention and explicit protection for the known recovery point before automatic pruning.

## Next engineering work / acceptance sequence

1. Complete the Maintenance-owned isolated PostgreSQL restore and a persistent **isolated test DB** for a running restored Nextcloud; qualify matching restored app, actual login, file and Calendar 6.6.2 behavior on Peanut. (This is a separate owner dependency, not an instruction to re-run already accepted source backup and file extraction.)
2. Develop source-only nextcloud update controller, tests and operator runbook, using existing Services owned backup and retention playbooks; prove no-op, update available, refused backup, offsite failure, version drift and recovery/failure handling in controlled/synthetic checks.
3. Apply only after full source CI, informed operator authorization and meaningful isolated rehearsal; accept live Nextcloud 34 maintenance update, consistent user/data/calendar operation and unchanged repeat. Then enable and observe the intended unattended schedule.
4. Handle major 34→35 as a different reviewed, explicit upgrade when needed. No permanent freeze on 34 beyond its support lifetime.

**Operator interface:** Whenever a command is eventually required, identify the exact host and terminal, give one pasteable command, and request output by exact `TASK [Full task name]` and `PLAY RECAP`; never just say “the named report.”
