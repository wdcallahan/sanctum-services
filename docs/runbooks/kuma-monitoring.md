# Uptime Kuma — retained monitors and source-managed recovery

## November 11 — Linux ARM64 image qualified; loopback staging source ready

**Accepted native evidence:** Kvin's corrected image-only
qualification finished `ok=8 changed=0 failed=0 skipped=1`.
The rootless cached Uptime Kuma **2.5.9 Linux ARM64** digest
passed actual Podman inspect and a disposable offline,
read-only `node --version` execution. No application,
service, data volume or network change was made by
qualification.

The exact qualified digest is pinned in
`ansible/group_vars/kuma.yml`, not a mutable `:2` tag.
[Staging source CI #43064138846 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064138846).
The rootless Quadlet will use a local `sanctum-kuma-data`
volume mounted at `/app/data`; it is local persistent storage,
not a remote share without reliable SQLite locking.
It publishes only `127.0.0.1:13001` to the host from
container port `3001`. The user-systemd generated service
is started via the ordinary manager, with boot linkage
handled by Quadlet's own `[Install] WantedBy=default.target`.
No Kvar, YXORP, DNS, firewall or client publication is changed.

**Next operator command, from Kvin.** This is the **first
actual application installation**, which creates a retained
named volume, a rootless Quadlet and running candidate.
It requires explicit stage approval supplied only on this
command (default remains off):

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma.yml \
  -e kuma_stage_approved=true
```

Return only the Kvin `PLAY RECAP` and the `msg` dictionary
from **Report bounded loopback Kuma candidate staging
acceptance**, or failed task/error. HTTP 200/302 on the
Kvin loopback endpoint means basic application startup,
not administrator/session, monitor, persistence, recovery
or named client acceptance. The old Kvar proof-of-concept
database need not be migrated, but the NEW retained volume
is valuable state once configured.

**Source-managed reversal, separately approved only when needed:**
`ansible/kuma-stage-remove.yml` has explicit
`kuma_stage_remove_approved=true` protection, validates
the exact owned user Quadlet, stops/removes the candidate
service and generator input, and **does not delete the
persistent data volume or image cache**. Its [source
CI #43064602595 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064602595);
native reversal has not yet been exercised. It is not
a production cutover or a data-purge procedure. When
explicitly authorized to reverse a candidate, run:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kuma-stage-remove.yml \
  -e kuma_stage_remove_approved=true
```

**Next application acceptance after staging:** version-qualified
authenticated monitor reconciliation, an actual UI/login,
`Wicket Ollama` genuinely Up as observed in the retained
Kuma, repeat without duplicate monitors/alerts, restart,
independent backup and restore, update/reversal workflow.
Only then retarget `kuma.nexus.sanctum` away from Kvar and
qualify real clients with the proper infrastructure owners.
The old Kvar installation and production route stay untouched.

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
