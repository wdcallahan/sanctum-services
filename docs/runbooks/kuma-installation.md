# Uptime Kuma — retained Kvin deployment and recovery proposal

**Status: source prepared, not deployed or natively qualified.**

Sanctum Services will keep Uptime Kuma on Kvin, replacing the Kvar
proof-of-concept rather than requiring migration of its old history.
The former proof-of-concept remains untouched while the intended replacement
is built. The [Wicket Ollama request](https://github.com/wdcallahan/sanctum-services/issues/4)
is separately declared in [`data/kuma-monitors.yml`](../../data/kuma-monitors.yml).
Declaring a monitor is not adding it to Kuma.

## Supported upstream base

The [Uptime Kuma 2 installation guide](https://github.com/louislam/uptime-kuma/wiki/%F0%9F%94%A7-How-to-Install)
identifies container port **3001** and persistent storage **`/app/data`**.
Its SQLite database requires reliable POSIX locking; do **not** place this
data volume on NFS or a filesystem whose locks are not dependable.

The proposed host uses a **rootless Podman named volume**
`sanctum-kuma-data` backed by Kvin's local NVMe, and the rootless user
systemd Quadlet at
`~/.config/containers/systemd/sanctum-kuma.container`. Source is under
`ansible/roles/kuma` and `ansible/kuma.yml`.

The initial listener is **`127.0.0.1:13001`** on Kvin, separate from
Kvar's existing 3001/tcp and independent of YXORP's production DNS. The
rootless `slirp4netns` selection follows the existing Kvin Nextcloud
networking decision; actual routed access to Wicket must be tested from
**inside the Kuma service**, not presumed.

## Stage prerequisites and intended command

- Choose and qualify an actual Linux ARM64 Uptime Kuma 2 **manifest
  digest** in `ansible/group_vars/kuma.yml`. The default empty value
  deliberately prevents deployment.
- Confirm a clean new instance and new local named volume are desired;
  do not overwrite old monitoring data or import the Kvar proof-of-concept.
- After the operator explicitly authorizes isolated staging, set
  `kuma_stage_approved: true` in the reviewed vars, then run:

  ```bash
  ~/.local/bin/ansible-navigator run ansible/kuma.yml
  ```

The role asserts the exact Kvin FQDN, pinned image, and staged loopback
binding, creates the Podman volume only if missing, and enables/reconciles
the user Quadlet. No DNS or firewalld commands appear in the role.
Port 3001 inside the container is not exposed to other LAN clients by
this candidate. It checks only that the local HTTP service responds.

## Initial configuration and real acceptance

A first-run admin account is created/retained using normal operator
credential management. Neither the username nor password belongs in Git.

Once the instance is selected as **the retained Kuma**, qualify the local
named volume's backup and restore, repeat runs, upgrades, systemd service
lifecycle, application login and long-term notification policy. Compose a
safe backup that stops/quiesces Kuma before copying SQLite database files;
a casual live copy is **not** evidence of recoverability. Test restore on
a separate disposable candidate without corrupting the selected instance.
Choose the image update and rollback sequence, including data schema
compatibility, before first production update.

The `kuma.nexus.sanctum` YXORP route remains disabled in the draft
until the retained endpoint and actual WebSocket/session behavior are
qualified. Maintenance owns eventual DNS/firewall cutover.

Monitor reconciliation is a separate step: monitor creation/editing in
Uptime Kuma 2 uses a version-dependent authenticated Socket.IO interface
rather than an established stable general REST write API. Choose and
qualify that client after the retained version is known. Reconcile the
declared Wicket monitor **without duplicates** and accept actual
**Up** from within Kuma. Do not issue duplicate notifications while
the legacy proof of concept remains accessible.

No source step authorizes Kvar removal, data deletion, or production
traffic cutover.
