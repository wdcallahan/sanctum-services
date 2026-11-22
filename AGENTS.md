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

## Nextcloud recovery frontier (November 21; refresh from owner issues)

- Kvin's weekly backup timer is enabled; installed service run and independent
  Peanut custody accepted. Natural timer firing is not yet observed.
- [Native PostgreSQL restore](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7073940132),
  [native OCC/Calendar](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7074239528)
  and [native authenticated file/Calendar recovery](https://github.com/wdcallahan/sanctum-services/issues/2#issuecomment-7074839767)
  complete the independent restoration rehearsal. Do not repeat them. Retained
  trial DB cleanup remains via [Maintenance #17](https://github.com/wdcallahan/sanctum-maintenance/issues/17#issuecomment-7074840405).
  **WITHDRAWN command:** old digest restore download remains prohibited.
- **November 22 LIVE:** protected Nextcloud 34.0.6 image activation already
  happened after fresh recovery point `nextcloud-20261122t164508` was verified
  independently on Peanut. The original activation play falsely failed before
  checking HTTP/Calendar because it waited for OCC rc=0, not the new version;
  the follow-up [native read-only check](https://github.com/wdcallahan/sanctum-services/issues/5#issuecomment-7087238141)
  confirms running 34.0.6.2, no maintenance/DB migration, matching image and
  Quadlet. **The .update-halted latch is active.** Do not rerun upgrade/backup
  or install timer; first run the source-qualified **post-promotion acceptance**
  play, which verifies current HTTP/Calendar/image/mounts and releases only
  that specific latch after all checks pass. Then install daily update timer.
  Check lead handoff/current Services #5, not old operator packets.
- **Warnings are engineering defects:** capture and address every reported
  deprecation/FutureWarning in source, even after a successful run, or explicitly
  track unresolved warnings. Never hide them with configuration, or rerun
  already accepted native work solely to reproduce warning output.

## Human handoff after interruption

At the start of a post-sleep / cold-session recap: say **what works,
what remains, why the immediately preceding turn had no command,
which owner moves next**, and the smallest genuinely new safe step if
one exists. Do not keep Nova at a terminal waiting on an owner source
dependency or claim you are running background work.

Pixel must check the complete CI result before passing an executable
command to Nova; Nova does not watch Actions or wait for a color.

A project turn ends with an explicit **NOVA ACTION REQUIRED**,
**NOVA DECISION REQUIRED**, **EXTERNAL OWNER DEPENDENCY**,
**PIXEL CONTINUATION REQUIRED** (only a true tool/session boundary),
or **REQUEST COMPLETE** under the Interface standard. If no command
is justified, say *why*, including the named owner and missing
deliverable. Do useful independent source work until an actual boundary;
do not create an unnecessary operator probe merely to produce a
command.

Generated-by: Pixel (OpenAI GPT-6)
