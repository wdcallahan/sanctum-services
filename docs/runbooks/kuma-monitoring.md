# Uptime Kuma — declared monitors and future reconciliation

## November 11 — next native action: image qualification only

The commissioned proxy rebuild has passed initial native Kvin-local
HTTP acceptance for **all eight routes**. The first actual Kvar-hosted
application migration is a clean retained **Kuma 2** on Kvin.

The repository already declares a version-specific, registry-discovered
**Linux ARM64 Uptime Kuma 2.5.9** digest in
`data/container-image-candidates.yml`:
`docker.io/louislam/uptime-kuma@sha256:302aceeca2db79617f195a7549f7c8dfb05375a274b1092c59d81c1fb61a9ab9`.
That entry is **not native accepted** or an authorization to
install the application. The source-managed
`ansible/kuma-qualify-image.yml` requires exact Kvin/aarch64,
explicit `kuma_image_qualification_approved=true`,
the declared digest/tag and `kuma_stage_approved=false`.
It looks for the image in **wdc2's rootless Podman store**,
pulls the exact digest if absent, inspects Linux/arm64
metadata, and runs only `node --version` in a disposable
rootless, read-only, network-disabled container.
No Kuma app, volume, port, Quadlet, monitor, DNS, firewall,
YXORP route or Kvar service is touched. A successful
image qualification proves image and runtime only.

**November 11 native checkpoint:** First Kvin run:
`ok=5 changed=1 failed=1` — the exact image was downloaded,
and the single-image, Linux and ARM64 checks passed.
The playbook then incorrectly required `sha256:` on Podman's
bare hexadecimal `Id` (distinct from its prefixed `Digest`).
The runtime check did not execute, so this is NOT yet
native image acceptance. The assertion has been corrected,
and a new real-Ansible metadata regression checks both valid and
deliberately invalid inspect data. [Corrected full source
CI #43059304269 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43059304269).
No application, volume, service, network or Kvar changes occurred.

To resume the image-only qualification on Kvin, the same
playbook will reuse the cached image if present:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma-qualify-image.yml \
  -e kuma_image_qualification_approved=true
```

Return ONLY the single Kvin `PLAY RECAP` line and
`msg` from **“Report bounded image-only qualification metadata”**,
or the failed task/error. Don't share the full pull log.

After **native** acceptance, pin the tested digest in
`ansible/group_vars/kuma.yml` and explicitly stage the
existing source-owned **rootless loopback-only** Kuma
candidate at `127.0.0.1:13001`; do not retarget
`kuma.nexus.sanctum` yet. Select a version-qualified
Socket.IO monitor-reconciliation mechanism, verify
actual Up for `Wicket Ollama`, persistence, no-op
repeat and recovery before Kvar upstream migration.
Kvar PoC database migration remains unnecessary,
but retained Kuma state still requires recoverable backup.

**Status:** Desired monitor declarations only. No service creation, monitor
mutation, login or live endpoint verification has been performed.

## Project Joule request

The [Wicket Ollama monitor request](https://github.com/wdcallahan/sanctum-services/issues/4)
is captured as a stable entry in `data/kuma-monitors.yml`:

- Name: `Wicket Ollama`
- HTTP URL: `http://wicket.arcane.sanctum:11435/healthz`
- Expected response: 200–299; actual Kuma UI state must show **Up**
- Probe location: the **retained** Uptime Kuma instance after its Kvin
  deployment/restore and networking have been accepted.

This is Project Joule's service health contract. Services owns only Kuma.

## Adoption conditions

The Kvar Kuma instance was a proof of concept; the operator allows a clean
retained Kvin instance instead of requiring migration of the old monitor
database. Do not change abandoned test installations or accidentally send
duplicate alerts. Preserve wanted state in code and verify persistent
monitor state after disaster restore.

Uptime Kuma's documented REST surface is not a universal monitor-write API.
Monitor creation/editing commonly uses authenticated Socket.IO and may vary
between Kuma versions. Select an actual version-qualified, testable
reconciliation interface before coding monitor mutations. Avoid direct SQLite
editing and do not put credentials into Git.

When Kuma is managed properly, load these declarations, reconcile by stable
monitor identity (not an unconditional add), and verify both a second
unchanged run and an actual **Up** observation in the retained instance.
A successful curl from the controller alone does not meet that acceptance.
