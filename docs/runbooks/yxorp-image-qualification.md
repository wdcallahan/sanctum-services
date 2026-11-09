# YXORP — candidate image qualification

**As of November 9, 2026: source prepared; native action NOT performed.**

The [registry metadata CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42690400649)
located Linux ARM64-specific Nginx stable-alpine and Uptime Kuma 2.5.9
image digests, preserved in
[`data/container-image-candidates.yml`](../../data/container-image-candidates.yml).
These are not native Kvin qualifications or permission to deploy.

The next explicitly selected test from Kvin's Services checkout is:

```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-qualify-image.yml
```

This will **pull the pinned Nginx image into the rootful Podman image
cache if missing** (the only intended persistent change). It asserts Kvin's
identity and AArch64 platform, inspects the downloaded image's architecture,
renders a disposable Nginx configuration, and runs `nginx -t` inside an
ephemeral container with **network disabled** and a synthetic Yarn hosts
entry. The temporary configuration is cleaned up. No rootful Quadlet is
installed, no lasting service started, no ports opened, no firewall or
DNS changes, and Kvar's NPM is not contacted.

This does not qualify actual proxy forwarding, networking or browser
access on Kvin, and does not change the deliberately blank
`yxorp_image` deployment variable. After accepting native image results,
a separate operator decision is needed before loopback service staging.
Kuma's candidate is recorded but is not pulled or qualified here.
