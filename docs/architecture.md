# Sanctum Services — Architecture

**Status:** Dated Nextcloud architecture with updated **November 8, 2026** shared-service decisions. Nextcloud's Calendar integration is operating and accepted; full recovery and YXORP route/TLS qualification remain open. Some deployment observations below are historical rather than today's live runtime. For current decisions see the [estate register](SERVICE-ESTATE.md) and [roadmap](ROADMAP.md).

## Automation and operating boundary — November 8, 2026

**So let it be written, so let it be run.** Normal management is declarative Ansible and version-controlled data, with changes documented and independently reproducible; a manual fix is reconciled into declared state. This implements the preexisting [cross-project completion standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md). Any current running container, NPM web UI, or local file is evidence, not independently sufficient reconstruction authority.

**Service privilege is functional, not ideological.** Rootless Podman Quadlets remain the right fit for Nextcloud and other unprivileged application containers. **Rootful Podman is accepted for YXORP** because the selected listener publishes host ports 80 and 443; don't change global privileged-port thresholds or add forwarding tricks merely to label it rootless. Native services like SSH need not be moved into containers. Leave host security, routing and firewall policy with their existing owners; do not confuse application deployment with assuming network-security ownership.

**YXORP design:** replace currently running Kvar Nginx Proxy Manager with **plain Nginx**, configured solely from Git-managed route data and Ansible templates. NPM's management UI, users, access lists and configuration database need not be reconstructed if they are not part of actual service requirements. Reproduce the actual HTTP upstream, proxy headers, WebSocket, and client routing semantics; safely validate generated Nginx configuration before reload. Build and qualify independently on Kvin before switching names or retiring Kvar. Existing NPM can remain running untouched during qualification. Source: [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2).

**Private HTTPS gap and settled naming intent:** `.sanctum` is a deliberately chosen, stable, private network namespace. Nova owns numerous public domains and previously operated a public/private hybrid domain internally, but deliberately abandoned that arrangement after a costly migration to `.sanctum`. **Do not propose migrating `.sanctum` services to a public domain or creating a hybrid public/private namespace as the default TLS solution.** Public CAs cannot issue certificates valid for private `.sanctum` names; DNS-01 validation of a different owned domain would not make its certificate valid for `.sanctum`. The leading technical direction to investigate is **internal PKI that preserves the existing names**, with automated certificate issuance/renewal and maintainable distribution of the CA's public trust anchor across managed operating systems, browsers, applications and VPN-connected clients. Trust delivery for unmanaged/family/mobile devices and apps using independent trust stores remains a substantial open problem. Signing keys must remain protected. TLS policy is not yet selected or deployed; document feasibility/operating costs before adoption, and do not claim HTTPS acceptance during the current proxy migration.

## Why this architecture?

The work has two equally real outputs: a useful self-hosted service and hands-on knowledge its owner can use to teach and maintain the technology independently. A turnkey installation, opaque wrapper, or running container that cannot be understood and removed is not success.

We use existing Sanctum components rather than giving each application its own database server, DNS service, proxy, or controller.

## Intended request and data paths

```text
User's browser/client
        |
        | stable Nextcloud service name (to be chosen)
        v
      YXORP (reverse proxy; managed by its owner)
        |
        | target host/port can change without changing client URL
        v
    Kvin:8085 (proposed initial published port)
        |
        | Podman forwards to port 80 inside the application
        v
   rootless Nextcloud Apache container
        |                          |
        | files/config             | named PostgreSQL connection
        v                          v
   Kvin persistent storage      existing Sanctum PostgreSQL
        |                          |
        +--------- consistent, recoverable backup --------+
                               |
                               v
                         Peanut (backup)
```

Kvin has approximately 870 GB available and Peanut 434 GB at the October 17 observations. **50 GiB** is a soft live-data budget, not a newly created partition. **Void** is the planned later durable-storage home. That change will require a planned migration and independent restoration check.

The published port **8085** is a configurable host-side choice, not a Nextcloud application requirement. Nextcloud Apache listens on **TCP 80** inside the container. It connects *outbound* to the shared PostgreSQL listener at **TCP 5432**. Optional Redis would be an independently managed service, not a second published Nextcloud port. All these locations must be configurable so the client-facing URL survives infrastructure changes.

## Intended automation path

```text
Kvin or Peanut: centrally managed ansible-navigator
                     |
                     | starts pinned, reusable EE image with Podman
                     v
             Execution Environment
             (Ansible + collections + dependencies)
                     |
                     | Ansible default smart/SSH to target host
                     v
              Kvin as managed host
                     |
                     | applies owning Ansible role/Quadlet
                     v
            rootless Nextcloud application
```

**Do not confuse the EE container with the managed machine.** The original inventory used `ansible_connection: local`, which would have executed tasks **inside the EE container**, not on Kvin. On October 17 we removed that override and chose Ansible's ordinary **smart connection**, which uses SSH for this Linux host. This is intentional even when the controller is Kvin: **Navigator/EE on Kvin → SSH to Kvin as `wdc2` → rootless Quadlet operations**. Peanut can manage the same target later without rewriting the role. The configuration change is committed, but actual SSH authentication and user-systemd behavior **remain unverified**. A separate project venv running `ansible-playbook` is **not** the accepted intended runtime.

## Where the EE comes from

Navigator does **not** create the EE by reading its `ansible-navigator.yml`.
That config tells Navigator **which image to use**. There are two normal paths:

1. **Pull a prebuilt EE** from an image registry, as in Nova's classroom:
   the provided image reference resolves to a finished container image.
2. **Build an EE locally** with `ansible-builder`, using a
   version-controlled `execution-environment.yml` plus collection, Python,
   and system-package requirements. Builder creates a Containerfile and
   invokes Podman to produce the image, which Navigator can use directly
   from the local image store or after publication.

**Actual existing Sanctum example:** [Maintenance's EE recipe](https://github.com/wdcallahan/sanctum-maintenance/blob/main/execution-environment.yml)
starts from `quay.io/fedora/fedora:44`, declares `ansible-core==2.21.2`
and `ansible-runner==2.4.3`, and draws dependencies from
`requirements.yml`, `requirements-ee.txt`, and `bindep.txt`.
### Ansible Core vs Runner in an EE

**Ansible Core** runs playbooks and modules. **Ansible Runner** is the
Python library and CLI that provides a stable *programmatic execution and
results interface* around Ansible: it starts an operation, gathers stdout,
status/return code, individual task events and artifacts. Other tools and
automation platforms can use that interface instead of implementing their
own invocation and event capture. Runner is not a separate always-running
service, second control node, or replacement for Ansible Core.

**Important qualification:** Runner is not a dependency of Ansible Core:
ordinary `ansible` and `ansible-playbook` work without it. For an EE intended
for Navigator and automation-platform execution, however, it belongs in the
supported runtime contract. Ansible Builder 3.1.1 checks for both Core and
Runner at the end of an image build by default (`skip_ansible_check: false`).
If Runner is absent from the image, that check fails, unless deliberately
skipped; skipping does not qualify Runner-dependent execution. An explicit
`ansible-navigator exec -- ansible ...` invocation can execute the Core CLI
without requiring that the invoked command use Runner's API.


Builder's definition deliberately has separate `dependencies.ansible_core`
and `dependencies.ansible_runner` entries; its normal final-image check
expects both, because the EE is intended for automation-tool execution as
well as direct CLI operation. See the official [Runner overview](https://docs.ansible.com/projects/runner/en/latest/)
and [Builder definition](https://docs.ansible.com/projects/builder/en/latest/definition/).
Our prior Maintenance EE explicitly installed `ansible-runner==2.4.3`
alongside `ansible-core==2.21.2`. Whether these exact versions are
appropriate for the **new foundation** is still subject to compatibility
review during its participatory build.

Its [Navigator settings](https://github.com/wdcallahan/sanctum-maintenance/blob/main/ansible-navigator.yml)
select the locally tagged `localhost/sanctum-maintenance-ee:2026.07` and
set image pull policy to `never`. The image was qualified for **Maintenance**,
not automatically for Nextcloud. It was copied to the peer controller; the
Maintenance project documents an independent durable image-publication gap.
A tag or a rebuild from mutable upstream inputs does **not** guarantee the
same image bytes as the already accepted one.

On October 18 Nova queried Kvin's APT metadata: neither
`ansible-navigator` nor `ansible-builder` was found under those package
names in its configured repositories. That is a **host-tool installation**
question, not an EE dependency or evidence that every application requires
a Python venv. On October 23 Maintenance installed normal-user Navigator on
both Debian controllers through its master playbook. Services now consumes
`~/.local/bin/ansible-navigator` and explicitly selects the existing EE;
the read-only `ansible/qualify-controller.yml` is the native migration check.
That consumer check passed before and after old Maintenance environment removal
on October 23; both controller environments are retired. No application reconciliation is part of this cleanup.

Nova provisionally selected **Sanctum Maintenance's existing controller-infrastructure workstream** to own shared Navigator/Builder tooling and a new general-purpose application EE. The decision can be revisited if it becomes a separate platform in its own right; this application repository will only consume its supported interface, not own controllers or their tooling. The accepted Maintenance EE must not be silently replaced or mutated.

### Accepted EE composition (October 18; implementation pending)

The word **shared** can mean *shared image identity* or *shared foundation*;
these are not the same choice. The proposed model combines both:

```text
Sanctum Maintenance controller infrastructure
  |-- centrally managed Navigator + Builder (Kvin and Peanut)
  |-- minimal, published base EE -- exact digest retained
         |-- Nextcloud: use the base as-is, if sufficient
         |-- Other service: use the base as-is, if sufficient
         |-- Specialized project EE: derive from pinned base
                    + only that project's required dependencies

The existing qualified sanctum-maintenance-ee stays separate.
```

A project that needs no extra dependencies can consume the same pinned
EE, with no needless duplicate image. A project needing incompatible
collections or Python/system packages owns an independently qualified
derivative. If incompatible core/Python or operational restrictions make
even the base unsuitable, use an independently built EE as a justified
exception. Builder accepts an image as its `base_image`, but before
deriving from an **already-populated EE**, examine Builder's generated
Containerfile to confirm its base-stage Ansible Core/Runner installation
does not conflict or create pointless duplication.

**Nova explicitly accepted this layering plan with a fully understood yes.**
The architecture is accepted; no new images have been built or changed for
it. The [controller-infrastructure owner](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md)
has the corresponding proposed architecture.

## Ownership and migration boundaries

| Component | Intended owner / contract |
| --- | --- |
| Nextcloud Quadlet, application persistent paths and configuration | `sanctum-services` |
| Host operating-system maintenance | `sanctum-maintenance` |
| Network/host facts | `sanctum` registry |
| YXORP application, plain Nginx Quadlet and declared route configuration | `sanctum-services` under [issue #2](https://github.com/wdcallahan/sanctum-services/issues/2); coordinate actual live proxy handoff before touching NPM or its routes |
| Shared PostgreSQL service, database provisioning and DB backup interface | Existing PostgreSQL owner |
| Shared Navigator/Builder toolchain and future general-purpose application EE | [Sanctum Maintenance — controller infrastructure](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md); normal-user tools and Services consumer accepted October 23; old Maintenance environments retired. New foundation EE co-building remains separate. |
| Nextcloud backup integration and documented restore | `sanctum-services` coordinated with database owner |
| Later move to Void | Explicit future migration |

Do not put credentials in public plaintext Git. Use declared encrypted inputs; restore must include everything that cannot be regenerated from source. Uninstall removes only the application-owned resources specified by a qualified procedure; erasing user data or a shared database is a separate explicit operation.

## Further reading

The [roadmap](ROADMAP.md) separates accepted facts from pending work. The [engineering log](history/engineering-log.md) records how the work evolved. The current [Ansible source candidate](../ansible/README.md) is **not an approved deployment procedure**. When installation, operation, and uninstall are actually tested, human-facing runbooks will be published under `docs/runbooks/`.
