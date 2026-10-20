# Sanctum Services — Session Continuation

This is a **short handoff for the next assistant**, not a second design authority, an automatic project-lead appointment, or required reading for human operators. Nova's actual request appoints the scope of each session.

## Active handoff — October 20 firewall ownership transfer

[Services issue 1](https://github.com/wdcallahan/sanctum-services/issues/1)
is the current bounded task. Maintenance's native **read-only** Kvin firewall
preview and separate Pi-baseline no-change preview passed. Maintenance owns
ordinary 8084/5432/8085 service-port publication on Kvin; its live correction
has **not** been approved or applied. Services' Nextcloud role has now removed
its application-owned firewalld port-opening mutation and added an early,
**read-only** preflight checking `eth0`/`public` and **both runtime and
permanent 8085/tcp**. A missing prerequisite fails before Nextcloud file,
credential or service mutation and points to Maintenance's
[owner runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/kvin-service-firewall.md).
The cross-project installation/reconstruction sequence is documented in
[Services' Ansible README](ansible/README.md) and
[Town Square proxy runbook](docs/runbooks/town-square-yxorp-proxy.md).

No live firewall or Nextcloud deployment action is authorized by this source
transfer. Nextcloud **does** already run locally with `status.php` HTTP 200,
`installed=false`; previous "not installed" notes below are historical.
Next: source-qualify and post Services issue 1 implementation; Maintenance
reviews it and obtains Nova's separate approval before any live host change.
Do not run the old PostgreSQL deploy play or the full platform baseline.
The new general-purpose EE co-build with Nova remains a separate learning
goal, not a missing source-handoff approval.

## What this project is for

`sanctum-services` owns reproducible self-hosted application deployment, lifecycle operations, and recovery, beginning with Nextcloud. **The learning is a deliverable**: Nova wants real Ansible Navigator/EE practice, professional skill, and independent ability to understand and maintain the system. He does *not* want an opaque turnkey result.

**Joule tool-model correction (October 18):** Pixel mistakenly suggested Runner would need to enforce Joule permissions. No: Joule's established tool menu accepts a selected tool, inventory limit and supported arguments; the tool processes the **actual attempted action** and either runs it or returns denial/escalation instructions. Joule is scored on justified tool calls/arguments regardless of outcome, so even an inevitably denied attempt must be sent to the real tool; **no dry-run surrogate**. Runner may provide structured results **behind Ansible-backed tools**, not replace the existing tool boundary or grading. The first file-based Runner demo returned `failed` / `rc=250`, with diagnostics suppressed; cause undetermined. See [engineering log](docs/history/engineering-log.md), and do not treat that run as accepted success.

**Runner rabbit hole closed October 18:** After three unsuccessful
assistant-designed demonstrations, diagnostic output identified an
`awx_display` callback-loading exception caused by a likely nested Runner
initialization through Navigator. Nova verified that Navigator exports
`ANSIBLE_STDOUT_CALLBACK=awx_display`. He already understands Runner's value
as a job/results adapter for possible Joule Ansible-backed tools and questioned
the diminishing returns of repairing a disposable demonstration. **We agreed
to stop here; no further Runner demo or workaround is a prerequisite to the
base EE.** Runner itself and the qualified Maintenance EE have not been
established to be broken. Return to designing and building the minimal base
EE **with Nova participating**. The Ansible Core-first learning requirement
remains in force.

**Learning guardrail October 18:** Nova teaches **ordinary Ansible Core**, not Ansible Runner. He is not opposed to Runner being inside an EE, but is concerned that using Runner's interface in everyday project automation would erode the transferability of his practice to teaching. Keep Ansible inventories, roles, playbooks and usual CLI behavior as the **portable project contract**. Using Navigator to execute the same Ansible code in an EE is fine; writing project-specific Runner API/CLI/artifact dependencies is **not the default**. Runner's presence serves the EE/tooling layer, not a new coding model. This is a design constraint, not a request to delete Runner.

**Important correction on October 18:** Pixel said "We built our own!" about the Maintenance EE. Nova pointed out **he did not get to participate in creating it and wanted that experience**. Observing Navigator, running an ad hoc command, or merely pasting a Builder invocation is not equivalent to understanding and co-building the EE. Stage 1 now requires Nova to help design the new EE, inspect Builder-generated output, build it with Podman, and learn how to maintain, reproduce and uninstall it. Don't run ahead and produce a finished EE for him. The current [Maintenance recipe](https://github.com/wdcallahan/sanctum-maintenance/blob/main/execution-environment.yml) is useful as a reference, but its qualified image must stay intact.

**Four nonnegotiable properties from the start: documented, repeatable, understandable, uninstallable.** An application that merely runs has no initial value if it fails these. Explain nontrivial mechanisms before introducing them. Maintain human-facing explanations and validated procedures alongside code.

**Cross-session learning correction (2026-10-17):** Nova wants *situated teaching*: use the **simplest command needed now**, introduce a new flag or concept **only when a real operation makes it useful**, and explain its purpose at that moment. When he questions a switch, answer why **this task** needs it, not merely what the switch means. His willingness to continue copying commands is not proof of consent or comprehension. If he says he no longer understands the mechanism, revisit the architecture. These rules are now written into the [cross-project interface standard](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md), which requires that important corrections be saved DURING each working session. **For everyday Git sync, Nova explicitly chose ordinary `git pull` without `--ff-only` and without hidden equivalent config**; see the updated [Git standard](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md).

## Read only what you need

1. [README](README.md): newcomer introduction, honest state, and navigation.
2. [Roadmap](docs/ROADMAP.md): destination, decisions, current **YOU ARE HERE** milestone, acceptance tests, and next actions.
3. [Architecture](docs/architecture.md): intended data path, automation path, and ownership boundaries.
4. [Ansible source README](ansible/README.md): important warning that existing code is an **unaccepted candidate**, not approved instructions.
5. [Engineering log](docs/history/engineering-log.md): dated evidence and mistakes; consult selectively, never as a mandatory transcript.

When needed for the *active decision*, consult the current cross-project [Git](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md), [Ansible](https://github.com/wdcallahan/engineering-standards/blob/main/Ansible-Project-Engineering-Standard.md), [Operational Completion](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md), and [Nova–Pixel Interface](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md) standards. They are authoritative over this handoff; do not recreate a mandatory full-reading chain.

## Frontier through October 18, 2026

- Kvin and Peanut are the designated Ansible controllers. Kvin is the initial Nextcloud application host; Peanut is the proposed backup destination; Void is the eventual file-storage destination. Kvin's first host-port mapping is **8085 → Nextcloud Apache 80**; YXORP will provide the stable client-facing service name.
- Source: Ansible role and Quadlet candidate on `main`; **no application deployment**. Nova installed `ansible-core==2.19.14` into a project venv and passed **direct-Ansible syntax-check** on Kvin. That is syntax evidence only.
- **Mistake to repair:** per-project venv/direct-Ansible was not the requested Navigator/EE learning workflow. The original inventory used `ansible_connection: local`, which would target an **EE container, not Kvin**. Nova chose ordinary **Ansible smart/SSH**, explicitly allowing Kvin's controller to SSH back into Kvin; the inventory override was **removed on main**. **Actual Kvin→EE→SSH→Kvin ad hoc ping passed October 18 using Maintenance's existing EE**. Rootless user-systemd control for the Nextcloud role is **not** tested. The remaining runtime design still needs review and correction, not a concealing wrapper.
- Existing application code has **no qualified deployment, backup/restore, normal operation or clean uninstall**. The original application README's deploy commands were withdrawn. The exact dates/observations are in the engineering log.
- The current active milestone is **Roadmap Stage 1**: explain and establish a supported shared Navigator/EE/controller workflow, including the infrastructure owner and an explicit managed-host connection. No deployment until proven and understood.

## Working contract

- Stay in this project's ownership boundary. Existing PostgreSQL, YXORP, network registry, OS maintenance, and shared controller runtime belong to their actual owning projects. Don't treat integrations as permission to change them.
- **Active-session checkout boundary — Nova correction October 18:** Even when we tentatively agree that another project (e.g. `sanctum-maintenance`) is the long-term **owner** of an artifact, that does **not** authorize this session to create files, do Builder experiments, or edit GitHub planning documents in that project's active working tree/repository. We instructed Nova to create `ee/base` inside his Maintenance checkout, producing unexpected `?? ee/` during Maintenance's own `git status`; Nova deleted those untracked experiment folders because they interfered with its working session. Earlier direct edits to Maintenance's roadmap were likewise uncoordinated. **Do not touch Maintenance's working tree or remotely mutate its GitHub repo again without the active Maintenance session's permission**; do not autonomously revert the earlier docs. Keep exploratory EE building in an explicitly agreed *isolated* workspace outside all actively managed checkouts; when ready, hand off the proposal/artifact to the authorized project owner. Ownership, implementation location and permission to change active state are separate questions.

- Work directly on linear `main`, without default branches or PRs. Preserve unfamiliar local work, and distinguish source, syntax check, actual live run, and accepted operating result.
- Use **Podman Quadlets**, not Docker Compose. Seek Nova's decision before consequential changes to shared infrastructure, data, or exposure. Never store credentials in public plaintext Git.
- Treat supported host-side Navigator tooling and the EE as distinct: the EE has Ansible and collections; Navigator launches it. Shared tooling should not be duplicated into each service without reason.
- Keep this handoff short. The **roadmap** owns milestones, **architecture/runbooks** own explanation and operation, and **engineering log** owns events. Update each at the same time as meaningful code/decisions.
- This is chat-based work with Nova operating Kvin/Peanut terminals as needed. There is no automatic background continuation.

**Architecture decision October 18:** Nova agreed provisionally to let [Sanctum Maintenance's controller-infrastructure workstream](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md) own the shared host-side Navigator/Builder tools and a **new, separately named general-purpose EE** for applications. This is a coherent ownership default, not proof that there are no alternatives or approval to rebuild Maintenance's qualified EE. The existing Maintenance EE stays untouched. Nova **must participate** in designing and building the new EE; do not do that work for him.

**EE composition ACCEPTED October 18:** After a full architecture comparison, Nova answered **yes, fully understood** to the layered model: (1) centrally owned minimal Ansible EE foundation, (2) unchanged, digest-pinned reuse when adequate, and (3) project-specific derivative only when extra dependencies warrant one, separately pinned and tested. This is **not** a single giant universal EE or one needless image copy per project. Red Hat's ee-minimal/custom-EE guidance supports the approach. Builder derivative details (notably avoiding duplicate Core/Runner installation when the base is already populated) still require inspection. The agreed design does **not** mean any new tooling or images are yet deployed. **Do not ask for architectural approval again.** [Owning controller design](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md); [application roadmap](docs/ROADMAP.md).

## Smallest next step

Ownership of the shared controller tools and EE foundation is provisionally Sanctum Maintenance, and the layered base/derived EE architecture is **explicitly accepted**; **do not ask Nova to decide either again**. Next co-design the base's minimum required contents and the first consumer's dependencies with Nova, explaining Builder inputs during the real build. The Maintenance EE's read-only **smart/SSH to Kvin** ping succeeded already, so **do not repeat it**. Nova already teaches ad hoc Ansible and only needs the *new* Navigator-specific `exec -- ansible …` relationship explained. Investigate the supported host-side Navigator/Builder installation options and the appropriate owner for a reusable shared toolchain before creating or installing anything; then qualify its own EE and remote connection. Record design before repairing the initial application candidate. The roadmap is the authoritative current progress map; verify newer source and live evidence before acting.

**End condition for a useful handoff:** Nova can tell what is accepted, what failed or is still proposed, and who has the next action, without searching chat history.
