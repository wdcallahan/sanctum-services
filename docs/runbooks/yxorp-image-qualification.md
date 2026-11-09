# YXORP — candidate image qualification

**Native qualification ACCEPTED on Kvin — November 9, 2026.**

Nova executed `ansible/yxorp-qualify-image.yml` via the normal Navigator
execution environment on Kvin. The play succeeded with `ok=11 changed=4
unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`:

- Exact digest pulled into Kvin's rootful Podman image cache (`changed`).
- Podman inspect reported Linux/ARM64; that architecture assertion passed.
- Nginx `-t` succeeded in a disposable container with networking disabled.
- Temporary directory created, config rendered and directory removed
  (three remaining expected `changed` tasks).
- The receipt expressly reported no persistent service started and no
  DNS or firewall change. No new listener or Kvar mutation.

This is a **qualified image** and configuration parser, not qualification of
Kvin bridge-network reachability, live proxy forwarding, TLS/client behavior,
or production cutover. The exact digest has now been promoted into
`ansible/group_vars/yxorp.yml`, while **`yxorp_stage_approved: false`**
continues to block lasting installation until a separate operator decision.

The [registry metadata CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42690400649)
located Linux ARM64-specific Nginx stable-alpine and Uptime Kuma 2.5.9
image digests, preserved in
[`data/container-image-candidates.yml`](../../data/container-image-candidates.yml).
The Nginx candidate has since passed native Kvin qualification; Kuma's
candidate remains registry-only. Neither authorizes deployment.

The completed image-only test was performed with:

```bash
cd ~/src/sanctum-services
git pull
~/.local/bin/ansible-navigator run ansible/yxorp-qualify-image.yml
```

This qualified the image and would populate Kvin's rootful Podman cache
if the exact digest were missing; the initial run did pull it. It asserts Kvin's
identity and AArch64 platform, inspects the downloaded image's architecture,
renders a disposable Nginx configuration, and runs `nginx -t` inside an
ephemeral container with **network disabled** and a synthetic Yarn hosts
entry. The temporary configuration is cleaned up. No rootful Quadlet is
installed, no lasting service started, no ports opened, no firewall or
DNS changes, and Kvar's NPM is not contacted.

This does not qualify actual proxy forwarding, networking or browser
access on Kvin. The image test did not itself change deployment source;
the exact digest was subsequently promoted in Git. The stage still requires
`yxorp_stage_approved: true`, selected explicitly by the operator. Its proposed loopback bind remains `127.0.0.1:18080`.
Kuma's candidate is recorded but is not pulled or qualified here.
