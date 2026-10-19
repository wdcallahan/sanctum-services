# Engineering Log — Sanctum Services

A short chronological record of significant observations, decisions, experiments and evidence. **Not** an installation guide, requirements authority, or raw chat/command transcript. For the current plan and accepted state, see the [roadmap](../ROADMAP.md).

## 2026-10-17 — Repository created and scope bounded

- Nova and Pixel created `wdcallahan/sanctum-services` on public `main`, with GNU GPLv3 license and an initial README.
- Scope: reproducible self-hosted application deployment via Ansible and Podman Quadlets. Nextcloud selected as the first service.
- A short `PROJECT_LEAD_INTRODUCTION.md` was committed for session continuity. No service was deployed.

## 2026-10-17 — Host, port, and storage observations

- On Kvin, Nova observed `kvin.outer.sanctum`, `aarch64`, Podman 5.4.2, and approximately **870 GB available** on NVMe.
- `podman ps` confirmed rootless EyesOnly/SearXNG using host **8083 → 8080** and Joule Prism using **8084 → 8000**; PostgreSQL was publishing **192.168.1.192:5432 → 5432**. The PostgreSQL bind-address correction is an already-tracked separate ticket.
- An `ss -ltn` query showed no listener on **8085**, so it became Nextcloud's selected initial host-port candidate. Nextcloud Apache itself listens on container **TCP 80**.
- Kvar-to-Kvin migration plans include Dashy, Uptime Kuma, LinkStack, Nginx Proxy Manager and Pi-hole. Nova clarified that historical rootless port numbers are not binding reservations; Nginx Proxy Manager has rootful port requirements, and DNS port 53 belongs to BIND rather than Pi-hole.
- On Peanut, Nova observed **434 GB free**. The agreed pilot plan is approximately **50 GiB soft live-data budget on Kvin**, separate recoverable copies on Peanut, and eventual storage on Void. Backup mechanism and retention are **not yet implemented**.

## 2026-10-17 — First Ansible candidate and syntax-only test

- Pixel committed a Nextcloud Ansible role, rootless Quadlet template, local-connection inventory, and a project-specific `ansible-core==2.19.14` venv recipe.
- On Kvin, Nova cloned/pulled the new repository, installed the declared controller dependency in `.venv`, and ran `--syntax-check` successfully: output `playbook: ansible/site.yml`.
- **Limit of evidence:** this established parsing only; no EE-based execution, deployment, database provisioning, proxy routing, backup, restore, or uninstall was demonstrated.

## 2026-10-17 — Original educational objective restored

- Nova identified a significant mismatch: years of requests to practice real **Ansible Navigator + Execution Environment** operations had been displaced by venv/direct-Ansible instructions. Professional learning and independent maintenance are central deliverables, not post-install options.
- The initial `ansible/README.md` was changed to **withdraw** the direct-via-venv apply instructions. The lead handoff now records the wrong runtime selection and blocks deployment until corrected.
- Additional review identified that the candidate `ansible_connection: local` would target an EE container rather than Kvin after the runtime switch. The inventory and connection approach remain **unaccepted**.
- Nova restated four nonnegotiable requirements: **documented, repeatable, understandable, uninstallable**. There is no initial value in a running but unmaintainable service. Work on the operator documentation, architecture explanation, roadmap, and this log began in response.

## 2026-10-17 — Human documentation and roadmap separated

- Replaced the repository landing page with a newcomer-readable README, explicit unqualified status, and navigation.
- Published a [roadmap](../ROADMAP.md) with bounded stages and acceptance tests and an [architecture explanation](../architecture.md) distinguishing the planned EE/controller/host path from runtime evidence.
- Kept this engineering log separate from operating instructions; reduced `PROJECT_LEAD_INTRODUCTION.md` to a short pointer-based handoff. Validated runbooks will be published only when their operations have been exercised.
- **No application deployment or EE qualification occurred as part of this documentation work.** The shared engineering-standards amendment remains a proposed separate operation.

## 2026-10-17 — Standard managed-host connection chosen

- Nova explicitly chose Ansible's normal **smart/SSH** model, including SSH from a Kvin-based EE back into Kvin itself. This preserves the ability to run the same playbook from Peanut or against a replacement application host.
- Removed `ansible_connection: local` from `ansible/inventory/hosts.yml` on `main`. The SSH credential and rootless user-systemd execution paths still require a live EE-based test.
- Clarified the unrelated Python-version question: tests of **Python 3.12 and 3.14** came from Project Joule's separately documented application compatibility/CI matrix, not an Ansible requirement to install two interpreters globally on Kvin and Peanut. Joule's owning [ADR-0002](https://github.com/wdcallahan/joule/blob/main/docs/adr/0002-python-and-dependency-workflow.md) records that decision; it is not authority to introduce a project-local Ansible venv here.

## 2026-10-17 — Learning and continuity requirements made cross-project

- Nova reaffirmed that practical experience is gained by **using commands when they are actually needed**, not by memorizing unexplained switches inserted for hypothetical cases. Using `git -C` from the current repository is unnecessary; it is useful when invoking Git for a *different* directory. A repeated explanation of what a flag means does not answer why that flag was needed in the actual task.
- Nova explicitly chose ordinary `git pull` in his usual sequential workflow, accepting that genuine divergence, if it ever arises, will be diagnosed as a real learning event. The shared [Git standard](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md) was amended; no hidden `pull.ff only` configuration is authorized.
- The shared [Nova–Pixel interface standard](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md) was updated to preserve learning as a deliverable and require **in-session durable recording** of meaningful corrections to purpose, architecture, operator independence, and instructional practice. This project handoff now points to those rules.
- These are GitHub source/documentation updates only, not evidence of successful EE deployment, system changes, or user comprehension.

## 2026-10-18 — Navigator inspection, first live learning checkpoint

- On Kvin, Nova invoked the already-installed Sanctum Maintenance `ansible-navigator images --mode interactive`, without installing or creating another environment.
- The interactive Podman image list identified `sanctum-maintenance-ee:2026.07` as **Execution environment: True**, image size **468 MB**. Other local images (including Prism and SearXNG) were marked `False`, confirming Navigator lists ordinary container images alongside recognized EEs.
- This is **read-only discovery of an existing project-qualified EE**, not Nextcloud runtime acceptance or approval to reuse the Maintenance EE as a generic shared runtime.
- Nova is already familiar with Navigator's **stdout mode** for playbook execution. Interactive image inspection was selected specifically to explore an EE's contents; the next useful teaching step is inspecting the image details before choosing new tooling.

## 2026-10-18 — Maintenance EE inspected; stdout mode preferred

- Nova selected image 14 (`sanctum-maintenance-ee:2026.07`) in Navigator's interactive image browser, then chose **Ansible version and collections**. Inspection showed **ansible-core 2.21.2**, with `ansible.netcommon 8.6.0`, `ansible.posix 2.2.2`, `ansible.utils 6.0.3`, `community.general 13.2.0`, `community.library_inventory_filtering_v1 1.1.5`, `community.openwrt 1.5.0`, `containers.podman 1.20.1`, and `vyos.vyos 6.0.0`.
- These are **observed contents of Maintenance's existing EE**, not a qualification of a reusable EE for Nextcloud. The difference between the EE's core 2.21.2 and Nextcloud's earlier venv core 2.19.14 illustrates independent Python/Ansible environments.
- Nova pointed out that the interactive Navigator interface renders its menu numbers in very dark gray against black and is hard to read. **He normally uses stdout mode and prefers it for ordinary operation.** Interactive inspection was a one-off learning exercise, not a new operating requirement. Avoid imposing inaccessible navigation or troubleshooting his terminal theme without a real need.

## 2026-10-18 — Navigator executed Ansible inside the Maintenance EE

- On Kvin, from `~/src/sanctum-maintenance`, Nova ran `./.venv/bin/ansible-navigator exec -- ansible --version`. The output reported **Ansible Core 2.21.2**, **Python 3.14.6**, executable `/usr/local/bin/ansible`, and Ansible module directory `/usr/local/lib/python3.14/site-packages/ansible`.
- The EE process loaded `/home/wdc2/src/sanctum-maintenance/ansible.cfg`. This demonstrates the distinction between the project configuration mounted or made available from Kvin, the host-side Navigator executable (presently installed in Maintenance's `.venv`), and the **Ansible runtime inside the EE**. No venv activation was necessary.
- **Acceptance limit:** `ansible --version` proves the launched runtime, **not** an SSH connection from the EE to the native Kvin managed host. A subsequent read-only module test must establish that separate boundary before treating the EE as usable for this project's remote host operations.
- The existing Maintenance [inventory](https://github.com/wdcallahan/sanctum-maintenance/blob/main/inventories/production/hosts.yml) contains `kvin.outer.sanctum` as a Debian/controller host. Its [ansible.cfg](https://github.com/wdcallahan/sanctum-maintenance/blob/main/ansible.cfg) supplies the inventory and requires host-key checking. Prefer the actual existing EE/connection for a read-only test rather than installing other controller tooling prematurely.

## 2026-10-18 — EE-to-Kvin ad hoc SSH accepted

- From Kvin's regular terminal, in `~/src/sanctum-maintenance`, Nova ran `./.venv/bin/ansible-navigator exec -- ansible kvin.outer.sanctum -m ansible.builtin.ping`. **Actual output:** `kvin.outer.sanctum | SUCCESS => {"changed": false, "ping": "pong"}`. This verifies the existing Maintenance EE executed an Ansible ad hoc module **over its configured connection to native Kvin**, rather than merely reporting container runtime metadata.
- **Limit:** Maintenance's qualified EE and host connection were exercised, but a reusable new EE, shared host-side Navigator installation, and Nextcloud's rootless user-systemd apply path have **not** been accepted. Do not mark the whole controller architecture complete.
- Nova already teaches Ansible ad hoc commands and `ansible.builtin.ping`; he does **not** need introductory Ansible explanations. His new learning here is `ansible-navigator exec -- ansible …` as a way to run familiar ad hoc commands **inside an EE**, versus the classroom's direct `ansible` executable on PATH. Keep future guidance at his actual experience level, distinguish host Python from EE Python, and explain only the genuinely unfamiliar Navigator/EE mechanics.

## 2026-10-18 — EE origin explained; Debian APT tools absent

- Nova compared `podman images` / `ansible-navigator images` and `podman exec` / `ansible-navigator exec`. He **already understands this connection** and normally teaches ad hoc Ansible; his actual unanswered EE question was **where the container image comes from**. Do not repeat introductory Ansible modules or laboriously reteach image-list navigation.
- Two EE supply paths were identified: **pull a registry-published image** (classroom model) or **build it using Ansible Builder**, which generates a Containerfile from `execution-environment.yml` and uses Podman. Existing [Sanctum Maintenance builder input](https://github.com/wdcallahan/sanctum-maintenance/blob/main/execution-environment.yml) and [Navigator selected image](https://github.com/wdcallahan/sanctum-maintenance/blob/main/ansible-navigator.yml) provide a concrete local example; Maintenance uses a locally tagged, qualified EE, not a new EE built by Navigator.
- On Kvin, Nova's `apt-cache policy ansible-navigator ansible-builder` returned `Unable to locate package` for each. This rules out those package names from **currently configured local APT metadata**, not every possible distro/package source. Host-side controller tooling installation is still undecided; do not jump to another per-project venv by default.
- [Architecture](../architecture.md) now explains EE origins and their separation from host-side Navigator/Builder installation. Nextcloud is still not deployed.

## 2026-10-18 — Nova must participate in the first new EE build

- Pixel excitedly told Nova "We built our own!" about Sanctum Maintenance's EE. Nova corrected the statement: **he had not participated in creating that EE**, and doing so would have been an especially valuable practical learning opportunity. Treat this as a missed educational deliverable, not as completed hands-on experience.
- Reviewed actual Maintenance builder inputs: Fedora 44 base, Python 3, `ansible-core==2.21.2`, `ansible-runner==2.4.3`; `requirements.yml` lists the seven directly required collections; `requirements-ee.txt` lists `ansible-pylibssh==1.4.0`; `bindep.txt` lists RPM `openssh-clients` and `sshpass`. These Python packages are installed **inside the EE**, not by changing Debian's system Python.
- Added a concrete Stage 1 hands-on deliverable: design a *new* reusable EE with Nova, examine the generated Containerfile, run the build, inspect the image in Navigator, and practice rebuild and removal. Existing Maintenance EE is only a reference; avoid altering or rebuilding its qualified image. No new EE has been built as a result of this conversation.

## 2026-10-18 — Shared EE ownership selected (planning)

- Nova said he would accept Sanctum Maintenance's existing controller infrastructure owning a general-purpose EE, with the higher objective that Sanctum's systems become **coherent**. The decision is **provisional and reversible**, not proof that a separate controller-platform owner was impossible.
- Maintenance's [roadmap](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md) now records responsibility for the host-side Navigator/Builder toolchain and a **new general-purpose application EE**, separate from the existing qualified `sanctum-maintenance-ee:2026.07`. Sanctum Services remains the owner of application playbooks, Quadlets, and lifecycle.
- **No packages, EEs, playbooks or running services changed.** Nova and Pixel will design and build the new EE **together**, beginning with a review of the necessary contents, rather than having an assistant create a completed image without teaching the build process.

## 2026-10-18 — Overall EE image strategy questioned before first build

- Nova said the ownership decision was not a high-level execution-environment plan. In his classroom, projects may each have their own EE, including images built or copied from a common source. He asked for best practice and suggested a **base EE with project-specific modifications**.
- Research against [Red Hat's custom EE guidance](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.7/administer-define__create__and_build_execution_environments) and [Ansible Builder's definition schema](https://docs.ansible.com/projects/builder/en/latest/definition/) supports a minimal EE foundation with extra dependencies only where required. Proposed choice: centrally publish one minimal pinned foundation; reuse it unchanged where enough; derive and independently qualify specialized EEs where needed. Do not blindly reinstall Ansible Core/Runner when deriving from an already populated EE—inspect the generated Containerfile first.
- The existing qualified Maintenance EE remains separate. **This composition is proposed pending Nova's agreement**, not an accepted runtime or executed image build. The controller ownership decision itself remains the previously agreed provisional Maintenance workstream.

## 2026-10-18 — Nova fully understands and accepts the layered EE architecture

- After reviewing one universal EE, per-project independent copies, and a centrally maintained minimal EE with optional project-specific derivatives, **Nova explicitly accepted the layered model** and emphasized that this was a **fully understood yes**, not just assent to move forward.
- **Accepted architecture:** one published, pinned minimal Ansible EE foundation maintained by the Sanctum Maintenance controller-infrastructure workstream. A project can use the identical pinned image directly if sufficient; otherwise it can create, test, and pin a derivative with additional required dependencies. Specialized preexisting Maintenance EE stays independently qualified. This acceptance does not establish specific base image or dependency versions.
- The acceptance was recorded in the [owning controller roadmap](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md), [Services roadmap](../ROADMAP.md), [architecture](../architecture.md), and [lead handoff](../../PROJECT_LEAD_INTRODUCTION.md). **No tool installation or EE build yet occurred.** Next is collaborative recipe design and first build with Nova participating in the work.

## 2026-10-18 — Builder installed; Ansible Runner explained at point of use

- On Kvin, Nova ran `./.venv/bin/ansible-builder --version`, which returned **3.1.1**. That is the *existing Maintenance-installed Builder* invoked without activating its venv; it is not yet a centralized host-tool installation and no image build occurred.
- Before authoring the new base EE, Nova asked what **Ansible Runner** is. It is a Python library/CLI for stable invocation of Ansible and structured output/event/artifact collection, **not** Ansible Core itself, a new management daemon, or a separate controller. Builder has distinct `ansible_core` and `ansible_runner` dependencies and normally verifies both in a completed EE. Explanation is now maintained in the [architecture guide](../architecture.md).
- Nova's question is a useful stop point: do not proceed through unfamiliar recipe ingredients without explaining *why each is present*, despite his deep general Ansible experience.

## 2026-10-18 — Runner experiment attempted; Navigator multiline command failed before Runner

- Nova correctly recognized Runner's structured execution/events as a potentially valuable **execution adapter for Joule's permissioned Ansible-backed tools**. This is a future integration possibility, not a general grant of access to control hosts. A tool layer must allowlist operations, validate inputs, and restrict mutations; Runner is not an authorization mechanism. Runner is relevant to Ansible-backed tools, not literally every Joule capability.
- The first attempted demo passed a multiline Python `-c` program through `ansible-navigator exec -- python3 -c '...'`. Native output showed `Argument expected for the -c option`, then Bash `import: command not found` and a shell syntax error on `with TemporaryDirectory`. **The Python program and Runner never ran.** Do not count this as evidence of Runner success/failure. Navigator's shell-command treatment can disrupt quoting/newline arguments; use a short file inside the project directory (which Navigator mounts) rather than a multiline `-c` argument.
- The correction is to run an isolated Runner API example from a temporary Python file through `ansible-navigator exec -- python3 FILENAME`, inspect `status`, `rc`, and `runner_on_ok` event data, then remove the temporary file. In the example, `ansible_connection=local` is **deliberately scoped to the throwaway EE-local demonstration**, not the production managed-host inventory. Only advance to an absence test after successful Runner behavior is observed.
- Nova said the explanation now makes much more sense, even though the demonstration failed. Do not conflate conceptual understanding of potential value with empirical qualification of this installed Runner.

## 2026-10-18 — Joule's actual tool contract and Runner rc=250

- Nova corrected Pixel's speculative concern about Runner enforcing Joule permissions. Joule already has a **defined menu of tools**. She selects a tool, an inventory-limited target and permitted options, and **submits an actual tool invocation**. The tool boundary can execute or return an authorization denial plus instructions to escalate to Nova. There is **no dry-run substitute** for an attempted tool call: the attempt itself is the observable behavior scored.
- Joule is graded for **whether her chosen tool and arguments were justified**, not for whether external conditions or authorization allowed successful completion; a denied request may still be a justified tool choice. Pixel must not silently replace this with success-based scoring or require Runner to supply authorization. For Ansible-backed tools, Runner could be a useful structured execution/events adapter behind the existing tool contract; it neither chooses nor authorizes tools. This correction is Nova's description of Joule's model, not independent audit of implementation.
- Runner's second demonstration **did execute Python and return a Runner object**. It printed `JOB STATUS: failed` and `RETURN CODE: 250`, with **no `runner_on_ok` event**. This **does not qualify the demonstrated Ansible job**. The demo used `quiet=True` and discarded its temporary artifact directory before capturing stdout/error diagnostics; the underlying error is unknown. Exit 250 can indicate an unexpected Ansible exception, but the precise cause has not been inspected.
- The next read-only experiment should **repeat the same isolated Runner job with captured stdout and diagnostic events shown before the temporary directory closes**. Do not speculate that permissions, lack of Runner, or a specific version incompatibility caused rc=250. Leave the qualified Maintenance image unchanged.

## 2026-10-18 — Source-level diagnosis after failed Runner demo

- A third Runner demonstration displayed the actual stored stdout. It failed before executing the requested Ansible module: `module 'ansible.plugins.callback.awx_display' has no attribute 'CallbackModule'`, while loading `/runner/artifacts/<id>/callback/awx_display.py`, around its `callback_loader.get(default_stdout_callback, class_only=True)` call. The prior `rc=250` is now known to come from an exception during **callback initialization**, not from a host connection/ping result.
- Reviewed upstream [Runner environment preparation](https://github.com/ansible/ansible-runner/blob/devel/src/ansible_runner/config/_base.py) and [awx_display callback source](https://docs.ansible.com/projects/runner/en/latest/_modules/ansible_runner/display_callback/callback/awx_display/). Runner captures an inherited `ANSIBLE_STDOUT_CALLBACK` as `ORIGINAL_STDOUT_CALLBACK`, then sets its own callback to `awx_display`. The callback loads the named original as its base class. **Leading hypothesis:** our attempt to launch Runner **inside an already Navigator-managed EE invocation** inherited `ANSIBLE_STDOUT_CALLBACK=awx_display`, which would cause `awx_display` to try to inherit itself before `CallbackModule` exists. This is a mechanism supported by source and observed traceback, but the **actual inherited environment remains uninspected**. See also [upstream issue 1390](https://github.com/ansible/ansible-runner/issues/1390).
- **Next step is a single read-only environment inspection**, not another unverified script or image rebuild: from the existing Kvin Maintenance shell, `./.venv/bin/ansible-navigator exec -- printenv ANSIBLE_STDOUT_CALLBACK`. If it reports `awx_display`, the inheritance hypothesis is strongly confirmed. If empty/not set, revisit before proposing any fix. Keep the qualified EE unchanged.
- Nova correctly objected that Pixel had supplied multiple unverified or unresearched experiments. Future experiments require checking actual upstream behavior first and reducing the next operator action to one falsifiable test rather than adding complexity or changing packages by guess.

## How to extend this log

Add an entry only for a meaningful changed design, verified run, discovery, accepted decision or failed experiment. Include what was observed, what conclusion is justified, and links to commits/tests/receipts where useful. Keep everyday instructions in runbooks, plans in the roadmap, and transient command output in appropriate private evidence artifacts. Never make new users read this log before operating the system.
