# Town Square: reproducible third-party Nextcloud applications

**Status: Calendar 6.6.2 native installation, unchanged repeat and
bidirectional desktop/browser access accepted (2026-10-21).** On Kvin, the first
application-only play reported `ok=22 changed=7 unreachable=0 failed=0`, and
the unchanged repeat reported `ok=14 changed=0 unreachable=0 failed=0 skipped=9`.
The role asserted the pinned version, enabled state and local Nextcloud
responsiveness. Nova saw an existing example event in both Nextcloud and GNOME
Calendar and subsequently explicitly confirmed that **Calendar access is
bidirectional**. This is accepted operator-observed functionality; exact
event-writing/reload steps were not separately supplied. Fresh-instance
reconstruction, full service recovery, and the browser route/TLS transport
remain separately unqualified.

## Scope and ownership

Sanctum Services owns the application manifest, its Ansible role, and the
rootless Nextcloud Quadlet. The shared PostgreSQL service, YXORP, host firewall
and platform baseline remain with their established owners.

The approved list is [`ansible/nextcloud-apps.yml`](../../ansible/nextcloud-apps.yml).
It currently pins **Calendar 6.6.2**, its official release URL, and the SHA-256 from the publisher's GitHub release metadata; this is the first live-qualification candidate. Apps not listed there are left alone: no surprising
uninstalls, no upgrades, and no bulk disabling of shipped Nextcloud components.

## Approve an app

Research the publisher, release activity, adoption, Nextcloud compatibility,
and operational dependencies. Record one exact release in the manifest:

```yaml
nextcloud_extra_apps:
  - id: calendar
    version: "6.6.2"
    state: enabled
    url: "https://example.invalid/replace-with-reviewed-release.tar.gz"
    sha256: "REPLACE_WITH_64_LOWERCASE_HEX_CHARACTERS"
```

The example URL and hash are **placeholders**, not a usable release. The URL must
point to the reviewed HTTPS release archive (normally a `.tar.gz` with one
top-level app-ID folder) and the SHA-256 must be calculated from **that exact**
archive. Archive retrieval with a checksum detects silent changes. Retain a
recoverable copy if the upstream archive might disappear.

An app with `state: disabled` is present but not active. No automatic removal
is implemented. Deliberate removal requires a separate review because apps
may create tables and persistent data.

## How it works

After Nextcloud's web installer finishes, the role reads `occ app:list
--output=json` from the rootless Podman container, validates the entire manifest
and rejects mismatched **already-installed** versions *before* making changes.
For missing apps it downloads the pinned archive to a private Kvin cache, checks
SHA-256, rejects unsafe archive members, reads `appinfo/info.xml` to validate
ID/version/server-major compatibility, places it under the already persistent
`/var/www/html/custom_apps`, and uses `occ app:enable` when requested.
It verifies exact version, enabled state, and local HTTP status after each app.

There is no `--force`, no automatic app update/downgrade, and no removal of
unlisted apps. App installation can still execute PHP/database migrations
and may fail or segfault; **this is not a transactional package manager**.
After a failed install, preserve logs before any restart or manual disable.

The existing base `ansible/site.yml` calls the app role only when the manifest
is nonempty and the base Nextcloud instance is installed. On the *first* fresh
host setup, complete the web installer, then reconcile apps on the next run.

A separate `ansible/apps.yml` handles app-only reconciliation without
reapplying the container role.

## Qualification sequence before first live apply

1. On Kvin, pull the current `main` and inspect the intended diff (Calendar 6.6.2 is now pinned).
2. Run `python3 -m unittest discover -s tests` in the repository.
3. Run `ansible-navigator run ansible/apps.yml --syntax-check` through the
   **approved project EE/controller context**, with its inventory and Vault
   conventions. Don't assume the existing Maintenance EE is generally approved.
4. Use the pinned **Calendar 6.6.2** entry and the app-only playbook first,
   recording the actual launch command, target, and the output.
5. Confirm web UI, local `/status.php`, `occ app:list`, and Apache logs.
   If workers segfault, preserve evidence. Test service restart before
   changing the app state, so causality isn't lost.
6. Repeat unchanged and demand zero modifications. Also demonstrate an app
   reconstruction in a disposable fresh application instance before calling
   the role production-qualified.

**No current-user data preservation requirement:** this is an exploratory
installation, per Nova on October 20. That does not authorize deleting
unrelated PostgreSQL or other shared Sanctum data.

## Recovery and reproducibility boundaries

The manifest reconstructs **app software and enabled state**, not application
database content, user files, shares, settings or secrets. Complete disaster
recovery later requires the Nextcloud persisted directory, a consistent
PostgreSQL snapshot, and private credentials. Reconstructing a bare installation
and restoring a previous installation are **different** workflows.

Nextcloud source: https://docs.nextcloud.com/server/34/admin_manual/occ_apps.html
Nextcloud app management: https://docs.nextcloud.com/server/34/admin_manual/apps_management.html
