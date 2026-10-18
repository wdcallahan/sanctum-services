# Sanctum Services — Architecture

**Status:** Proposed Nextcloud arrangement, **not yet deployed or qualified** (2026-10-17). This page explains the intended pieces and who owns them. For acceptance gates, see the [roadmap](ROADMAP.md).

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
                     | explicit connection to target host
                     v
              Kvin as managed host
                     |
                     | applies owning Ansible role/Quadlet
                     v
            rootless Nextcloud application
```

**Do not confuse the EE container with the managed machine.** The initial candidate inventory says `ansible_connection: local`; with Ansible running inside an EE, that would execute tasks **in the EE container**, not on Kvin. The role and connection model must be corrected and tested before deployment. A separate project venv running `ansible-playbook` is **not** the accepted intended runtime.

The shared controller tools and EE need a declared owning project. This application repository should consume their supported interface, not accidentally become the automation platform owner.

## Ownership and migration boundaries

| Component | Intended owner / contract |
| --- | --- |
| Nextcloud Quadlet, application persistent paths and configuration | `sanctum-services` |
| Host operating-system maintenance | `sanctum-maintenance` |
| Network/host facts | `sanctum` registry |
| YXORP route and proxy | Existing reverse-proxy owner |
| Shared PostgreSQL service, database provisioning and DB backup interface | Existing PostgreSQL owner |
| Shared Navigator installation and reusable EE | **Owner to be agreed before implementation** |
| Nextcloud backup integration and documented restore | `sanctum-services` coordinated with database owner |
| Later move to Void | Explicit future migration |

Do not put credentials in public plaintext Git. Use declared encrypted inputs; restore must include everything that cannot be regenerated from source. Uninstall removes only the application-owned resources specified by a qualified procedure; erasing user data or a shared database is a separate explicit operation.

## Further reading

The [roadmap](ROADMAP.md) separates accepted facts from pending work. The [engineering log](history/engineering-log.md) records how the work evolved. The current [Ansible source candidate](../ansible/README.md) is **not an approved deployment procedure**. When installation, operation, and uninstall are actually tested, human-facing runbooks will be published under `docs/runbooks/`.
