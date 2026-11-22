# Sanctum Services — durable instructions for a new Pixel session

**Reading this file does not appoint you project lead or authorize host
mutations.** Work within the scope Nova assigned. Source is the current
`main` branch of this repository; old chat text and dated example
commands are not newer authority.

## Before designing, editing or giving an operator command

1. Read the current [lead handoff](PROJECT_LEAD_INTRODUCTION.md) **from
   the top**, then relevant active [Services issues](https://github.com/wdcallahan/sanctum-services/issues)
   and [roadmap](docs/ROADMAP.md). Bank real native acceptance before
   asking for tests; never redo a previously accepted operation merely
   because it is convenient or idempotent.
2. Follow the canonical [Git](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md),
   [Ansible](https://github.com/wdcallahan/engineering-standards/blob/main/Ansible-Project-Engineering-Standard.md),
   [Operational Completion](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md)
   and [Nova–Pixel Interface](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md)
   standards on their own current `main`. In particular read Interface
   section **8.3 fresh-session regression gate** and section **4.5
   resume orientation**.
3. **Mandatory Sanctum policy look-up when relevant:** the November 16
   [whole-Sanctum exception audit, Maintenance #38](https://github.com/wdcallahan/sanctum-maintenance/issues/38)
   and its latest findings. This covers lifecycle/update channels,
   reachability/auth, source/live drift, unwanted retired services,
   backup/recovery, PostgreSQL availability, obsolete source rules,
   and observability. The applicable current owning issue/contract
   also matters. Never treat a stale owner helper or historical test
   artifact as newer user authorization.

## Do not reintroduce rejected operational restrictions

- **Wanted production services must have an actual advancing unattended
  update path.** Frozen SHA-only runtime images with no renewal mechanism
  are a known regression. Choose a supported moving channel or genuinely
  automatic, qualified promotion path; stateful schema-major upgrades
  require recoverable sequencing. A digest recording a historic backup,
  a specifically justified test fixture, or an advancing build artifact
  is NOT the same thing as an indefinitely frozen live service.
- **Ordinary intended LAN clients must not be arbitrarily denied.**
  A single-client source-IP firewall exception, forced proxy path,
  or accidental loopback-only publication is not a default security
  policy. Respect existing authentication and justified isolation.
  Do not confuse destination binding, test namespace isolation, and
  directed-broadcast /32 routes with a single permitted client source.
- **Retired services stay retired.** Do not resurrect Pi-hole,
  OpenWebUI, Endlessh, or Wiki.js to make older automation green.
  Kvar is unplugged; recovery work should not assume it is serving.
- **Cross-owner interfaces are authoritative for what they implement,
  not for superseding Nova's policy.** Before using Maintenance-owned
  PostgreSQL restore code, compare its actual image/version/credential
  contract to the November audit. If it is inconsistent, fail **before
  pulling an image or modifying a database**, document an owner handoff
  and do not invent Services-side SQL or silently override the owner.
- **No unnecessary accepted-test repeats.** Separate source CI,
  native Kvin/Peanut evidence, live production acceptance, and
  genuine recovery exercise. A green test is not a running service.

## Nextcloud recovery frontier (recorded November 17; refresh from owner issues)

- Kvin's rootless **Sunday 03:30 weekly backup timer is installed and
  enabled**. The *installed user service* successfully executed a
  supervised new consistent snapshot
  `nextcloud-20261117t134454` and verified an identical complete
  bundle on Peanut (native `ok=20 changed=1 failed=0`,
  [Services #2 receipt](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-6960759294)).
  The natural Sunday timer firing has NOT been observed. Do not rerun
  timer install, first service test, earlier manual dump or Peanut
  retention merely for reassurance.
- Nextcloud **34.0.5.1** is running; official **34.0.6** was
  independently qualified in Kvin's cache, NOT deployed.
  The daily updater and production patch are gated on real full app
  and database disaster recovery, [Services #5](https://github.com/wdcallahan/sanctum-services/issues/5).
- The older `nextcloud-20261116t233618` recovery bundle's HTML/private
  files are ALREADY restored in a separate tree on Peanut. A full
  database restoration and isolated functioning Nextcloud login,
  files and Calendar are NOT yet accepted.
- **WITHDRAWN command:** The old fixed PostgreSQL image download is
  still prohibited. November 21 [Maintenance #17 owner correction](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-7073141882)
  resolves the source mismatch. Services stages only two reviewed
  helper files inside the existing Peanut trial; no Maintenance
  checkout advance. The actual native DB and app restore still await
  acceptance. Read the current [lead handoff](PROJECT_LEAD_INTRODUCTION.md)
  and recovery runbook before issuing the next command. Do not repeat
  accepted recovery stages or reuse the withdrawn digest download.

## Human handoff after interruption

At the start of a post-sleep / cold-session recap: say **what works,
what remains, why the immediately preceding turn had no command,
which owner moves next**, and the smallest genuinely new safe step if
one exists. Do not keep Nova at a terminal waiting on an owner source
dependency or claim you are running background work.

A project turn ends with an explicit **NOVA ACTION REQUIRED**,
**NOVA DECISION REQUIRED**, **EXTERNAL OWNER DEPENDENCY**,
**PIXEL CONTINUATION REQUIRED** (only a true tool/session boundary),
or **REQUEST COMPLETE** under the Interface standard. If no command
is justified, say *why*, including the named owner and missing
deliverable. Do useful independent source work until an actual boundary;
do not create an unnecessary operator probe merely to produce a
command.

Generated-by: Pixel (OpenAI GPT-6)
