# YXORP — plain Nginx on a rootful Podman Quadlet

**Current source state, November 9, 2026:** Peanut is the explicitly selected
full-port, full-LAN trial host. Kvin remains the intended production host.
Kvar's incumbent Nginx Proxy Manager (NPM) remains online until a separate
accepted cutover. Peanut is **Kvin's intended service peer and standby**:
once YXORP is accepted and its persistent standby publication is deliberately
commissioned, Peanut can assume the reverse-proxy role if Kvin fails.
This ad hoc test is not yet that failover mechanism. Source CI is not a
native Peanut deployment receipt.

## Same service architecture in trial and production

| | Peanut trial | Kvin after cutover |
| --- | --- | --- |
| Scope | `yxorp_test` | `yxorp` |
| Container | Rootful Podman Quadlet | Rootful Podman Quadlet |
| Listener | `0.0.0.0:80` | `0.0.0.0:80` |
| HTTP | Plain internal HTTP | Plain internal HTTP |
| Image input | `docker.io/library/nginx:stable-alpine` | ARM64 qualified image digest, until update policy promoted |
| Service name | `sanctum-yxorp-peanut-test.service` | `sanctum-yxorp.service` |
| Existing traffic | Unchanged; test via Peanut hostname + Host header | Separate reviewed DNS cutover required |

There is **no localhost-only or high-port workaround**. The trial really
binds TCP/80 on Peanut. Nova explicitly approved an **ad hoc runtime-only**
firewall exception for this test after the native preflight observed
firewalld running in `public`, no listener on 80, and both service/port
admission disabled. The trial adds only `80/tcp` in zone `public`, with
a **four-hour expiration**; the permanent Maintenance-owned firewall
configuration is unchanged. The test-removal playbook takes down that
exception and checks the result. Firewall reload, daemon restart or reboot
also discards the temporary runtime permission. Test and production
target groups are separate, so running the Peanut playbook cannot target
Kvin.

The checked-in route list [`data/yxorp-routes.yml`](../../data/yxorp-routes.yml)
currently enables only the newly proposed
`yarn.nexus.sanctum` → `http://yarn.inner.sanctum:80` route.
The other observed NPM routes remain declared but disabled until their
applications and consumer behavior are accepted. The NPM administrative
UI itself is retired rather than reproduced.

## First trial: Kvin controller, Peanut target

From `~/src/sanctum-services` on Kvin:

```bash
git pull
~/.local/bin/ansible-navigator run ansible/yxorp-peanut.yml
```

The **first imported play** is
`ansible/yxorp-peanut-trial-firewall.yml`: it verifies the exact Peanut
identity, checks port ownership and current firewalld zone, records a
root-only cleanup marker in `/run`, and adds a **runtime-only**
`public` zone TCP/80 exception using `--timeout=4h` **only if not
already admitted**. Nothing is added to the permanent firewall policy.
The original **read-only preflight** runs next and must confirm that
Peanut is ready, followed by the ordinary rootful deployment role.
A wrong zone, listener or unexpectedly changed marker aborts the
operation without relaxing the firewall. If preflight or deployment
fails after the exception was opened, run the bounded remover below;
the temporary rule also expires independently.

Once the preflight passes, the ordinary Services YXORP role:

1. validates the selected host and route inputs,
2. renders the version-controlled Nginx configuration,
3. checks/pulls the selected container image and validates the candidate
   using Nginx in a disposable Podman **bridge** container,
4. installs only the trial's own Nginx configuration and system Quadlet,
5. starts its generated systemd service and checks the local health path.

Quadlet's `[Install] WantedBy=multi-user.target` manages boot startup;
the transient generated service must not be explicitly enabled via
`systemctl enable`. No NPM, DNS, Kvar, Kvin service or host firewall
is modified by the trial installer.

**Actual network-client smoke**, from Kvin:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-probe.yml
```

This queries `http://peanut.arcane.sanctum/__yxorp_health` and the
Yarn route through Peanut over HTTP/80 using
`Host: yarn.nexus.sanctum`. It runs on Kvin as a *different host*, not
inside the Nginx container. A successful probe confirms bounded HTTP
routing from that vantage point, **not** complete app/browser acceptance.
Once available, test with a real browser/client from the intended segments
before claiming availability to everyone. The original DNS entry still
points to Kvar; direct client testing should send the desired Host header
or use a temporary per-request URL-to-address override, not reconfigure
authoritative DNS.

## Native failure, November 9 — DNS in the Podman bridge

Nova's updated `ansible/yxorp-peanut.yml` run crossed the temporary
runtime-only firewall gate and read-only preflight, created the
Peanut-specific configuration directory and rendered the candidate,
and retrieved the maintained `nginx:stable-alpine` image. It **stopped
at Nginx parser validation** before installing any system Quadlet or
starting a persistent listener.

Exact error:

```text
[emerg] host not found in upstream "yarn.inner.sanctum"
nginx: configuration file /etc/nginx/nginx.conf test failed
```

The candidate container used Podman's regular `bridge` networking.
This result does **not** prove that Peanut's host resolver is broken:
the host and rootful container may use different resolvers, and
Peanut's authoritative BIND listens at the documented
`192.168.3.3`. Kvin's documented DNS peer address is
`192.168.1.192`. Don't hardcode Yarn's host address or switch Nginx
to host networking just to make `nginx -t` pass.

The next native observation is intentionally bounded:

```bash
cd ~/src/sanctum-services
git pull --ff-only
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-dns-observe.yml
```

This changes no firewall or service configuration. It compares
`getent ahostsv4` on Peanut with ephemeral Podman bridge DNS
queries using the current default resolver, the local Peanut DNS
peer and the Kvin DNS peer. Exact results will determine whether
an explicit Podman/Quadlet `DNS=` is the right next source change,
or whether the underlying internal Yarn DNS record/policy needs
correction. **Do not rerun the original deployment until the
resolution path is qualified.** The earlier ad hoc TCP/80 allowance
will expire four hours after firewalld added it unless removed
sooner by the trial-removal play. No permanent policy was changed.

## Reversal: remove the entire temporary Peanut service

The separately named `ansible/yxorp-peanut-remove.yml` targets
**Peanut only**. Run it from Kvin's Services checkout when the test
concludes or if an installation step aborts:

```bash
~/.local/bin/ansible-navigator run ansible/yxorp-peanut-remove.yml
```

It checks the actual Quadlet contains exactly
`ContainerName=sanctum-yxorp-peanut-test` and
`PublishPort=0.0.0.0:80:80/tcp`, inventories the known configuration
files including hidden entries, then stops the trial, removes its own
Quadlet, reloads systemd and removes only its own config directory.
Unexpected files, symlinks or altered listener scope cause refusal.
It leaves the cached image, Kvar, DNS, **permanent firewall policy** and
application data intact. It checks the exact `/run` cleanup marker
and removes only the test's runtime `public:80/tcp` admission, if still
active. It verifies that the explicit runtime port allowance has gone
and deletes the marker. If the four-hour timeout or a reboot already
cleared the rule, cleanup still removes any remaining marker.

The trial's scoped remove authorization is present because Nova chose
this test. Removing **production** YXORP later is a separate operation
requiring DNS, proxy references, monitor, consumer and rollback coordination
with the actual owners. Simply deleting a production container is not
the complete reverse of having published the service.

## Native evidence and image lifecycle

Kvar's actual NPM upstream comparison is in
[2026-11-09 default-route review](../review/2026-11-09-yxorp-default-route-comparison.md).
Its separately executed bounded generated-behavior inspection is
[here](../review/2026-11-09-yxorp-behavior-observation.md).
Neither needs repeating just for demonstration.

Kvin previously qualified the *official Nginx ARM64 digest* with Podman
image inspection and an ephemeral offline `nginx -t`; see
[image qualification](yxorp-image-qualification.md).
That proves the image parser, **not** client service. The Peanut test uses
the normal maintained `stable-alpine` tag on its own architecture instead.
The role currently pulls a tagged image **when missing**; routine
flowing-image updates and rollback are still incomplete and must be
demonstrated rather than treated as delivered. Native Podman
`AutoUpdate=registry` may be a suitable future mechanism, but a systemd
restart alone does not prove that clients can use the service.
No automatic-update timer is enabled by this test.

**Production is not authorized:** the Kvin group vars retain
`yxorp_production_cutover_approved: false`. The intended deployment
is rootful, on TCP/80, available on the LAN subject to reviewed firewall
policy and DNS cutover. Kvar stays online for rollback until real
application/client behavior and the chosen lifetime update/reversal
strategy are accepted.

Follow [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2)
for current state and owner coordination.
