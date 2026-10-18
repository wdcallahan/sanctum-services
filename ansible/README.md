# Nextcloud installation — initial Ansible source

The first target is Kvin, with **rootless Podman Quadlets** and
an external existing PostgreSQL service. The application listens on **80/tcp
inside its container**; the host mapping starts at **8085/tcp**, behind YXORP.
The host, port, storage path, image digest, and stable application DNS name
are configuration inputs rather than part of Nextcloud's identity.

This is an **unqualified initial source candidate**, not a published claim
that a working Nextcloud or reliable backups have been deployed.

## Independent controller runtime

On Kvin, from the root of this checkout:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r ansible/requirements-controller.txt
.venv/bin/ansible-playbook --syntax-check ansible/site.yml
```

The controller dependency is pinned separately from Sanctum Maintenance.
A complete transitive dependency lock and native execution qualification
remain open; do not describe this venv recipe as byte-for-byte reproducible.

## Inputs required before the first apply

1. Choose the stable Nextcloud service hostname and public scheme in
   `ansible/group_vars/nextcloud.yml`, plus the authoritative named
   PostgreSQL endpoint (never hard-code an IP address).
2. Resolve and select a Nextcloud **Apache image by digest** that supports
   the host architecture; do not treat a floating tag as immutable.
3. Have the PostgreSQL owning operation provision the dedicated `nextcloud`
   role and database with its own credential. This deployment does not
   modify the shared database's service, network binding, roles, or HBA.
4. Supply `vault_nextcloud_postgres_password` and
   `vault_nextcloud_admin_password` in encrypted
   `ansible/group_vars/nextcloud/vault.yml`. For example create it with
   `.venv/bin/ansible-vault create ansible/group_vars/nextcloud/vault.yml`.
   Keep the Vault unlock secret outside Git.
5. Verify the desired user systemd manager is reachable and lingering is
   correctly managed for persistent rootless services. Confirm no other
   service is bound to the configured host port.

Then, from Kvin and only when these inputs and dependencies exist:

```sh
.venv/bin/ansible-playbook ansible/site.yml --ask-vault-pass
```

Repeat that same command unchanged and require a no-change run. Verify
Nextcloud login through YXORP, not only an HTTP status or running process.

## Persistent state, backups, and migration

The default Kvin live data directory is
`~/srv/sanctum-services/nextcloud/html` (bind-mounted as
`/var/www/html`), so its contents can later move to Void. The learning
period's **50 GiB** is a soft capacity budget, not a quota. Peanut is the
intended separate backup destination; as of October 17 it had 434 GB free.

**No backup job is installed by this initial playbook.** Before storing
valuable files, define and verify a consistent restore set: uploaded files,
Nextcloud configuration, PostgreSQL database, necessary credentials, and
recovery of rootless user-namespace ownership. A mirror with propagated
deletions is not a substitute for recoverable backup history.

The first pass uses Nextcloud's default AJAX background-job method. Add
a qualified scheduler for the recommended cron mode before asserting normal
unattended operations are complete.

The initial host/port can change without changing the stable service URL
if YXORP is updated to point at the new backend. Never silently replace
the shared proxy or database ownership contracts.
