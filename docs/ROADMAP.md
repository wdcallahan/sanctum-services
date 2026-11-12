# Sanctum Services — Roadmap

## November 12 — LinkStack real production browser and administrator login ACCEPTED

**Native operator report:** Nova ran the approved production `ansible/yxorp.yml` route change from the CI-qualified [source commit](https://github.com/wdcallahan/sanctum-services/commit/7e7ab7992244a3df957c44b946bca374352c37de). Kvin play recap **`ok=31 changed=3 failed=1 unreachable=0 skipped=1`**: the existing YXORP role applied the production configuration and service reconciliation, then the **unrelated pre-existing Yarn HTTP post-task timed out** (`Verify production proxy still reaches original Yarn service`). Because that Yarn failure occurred before the new LinkStack post-task, the Ansible play itself did not reach LinkStack final check. **Do not interpret nonzero play exit as a rolled-back route.**

**Decisive actual production acceptance from Nova:** In normal Firefox, `http://dir.nexus.sanctum/` loaded the recovered directory and the **administrator sign-in worked**. This accepts the **actual named production route's public directory and authentication**, not speculative localhost or tunnel browser access. No request for further anonymous probes, isolated Firefox profiles, or SSH tunneling. Do **not** run rollback or rerun this play merely to make its unrelated Yarn check green. Keep Kvar's LinkStack running and its old data intact for easy fallback; later retirement is separate ordinary housekeeping, not a prerequisite for accepting the migrated service. New Kvin edits will not synchronize back to the original Kvar copy.

**Source + disposition:** Existing production YXORP source selects Kvin `127.0.0.1:18081` for `dir` and preserves Kvar `:8081` as an explicitly selectable fallback. The CI [run #43314459926](https://github.com/wdcallahan/sanctum-services/actions/runs/43314459926) passed. The old Yarn postcheck is a **separately known defect in reporting/reconciliation**, not an unresolved LinkStack migration gate; treat it as routine source maintenance when YXORP playbook reliability is next worked on, not as a demand for further migration testing. **No immediate operator action required.**


## November 12 — Nova authorizes direct production LinkStack route switch; source ready for CI and operator apply

**Decision replaces the isolated Firefox/SSH-tunnel plan.** Existing Peanut authoritative DNS already sends `dir.nexus.sanctum` to Kvin's LIVE, host-networked production YXORP; only YXORP's `dir` backend still targets Kvar `:8081`. Kvin's recovered original-image LinkStack is **already running** on `127.0.0.1:18081`, and anonymous directory/assets and login path HTTP passed natively. No further tunnels, isolated browser profiles, additional cloned volumes, or nonproduction login simulation are required. The final acceptance is Nova's normal Firefox visit to `http://dir.nexus.sanctum/` and private `/login` authentication through production YXORP.

**Source change pending live apply:** `ansible/yxorp.yml` now defaults `yxorp_production_linkstack_backend=kvin`, projecting the `dir.nexus.sanctum` backend to `http://127.0.0.1:18081`, while retaining exact eight routes, original Kvar stage manifest, existing Kuma `127.0.0.1:13001` retarget, and every other upstream unchanged. Its existing role validates then remounts/restarts only the owned production YXORP service if config changes; no DNS/firewall changes, no Kvar service stop, no app/data migration. One direct HTTP 200 upstream precheck and one YXORP route HTTP 200 postcheck accompany the change. The Kvar rootless LinkStack remains running for rollback. Existing fixture covers both Kvin target and `-e yxorp_production_linkstack_backend=kvar` rollback; source CI must pass before host command.

**NEXT single operator action (Kvin, after source CI green):** follow [production LinkStack cutover runbook](runbooks/linkstack-browser-acceptance.md) to pull `main`, run `~/.local/bin/ansible-navigator run ansible/yxorp.yml -e yxorp_production_cutover_approved=true` and then open the real `dir.nexus.sanctum` in ordinary Firefox and privately sign in. On an actual issue, rerun the SAME play with `-e yxorp_production_linkstack_backend=kvar` to restore Kvar LinkStack's backend without disturbing the other seven routes. Production LinkStack admin remains unaccepted until Nova reports it. New writes to Kvin after the switch do not copy back to Kvar. Kvar retirement/stop follows acceptance, not this route change.


## November 12 — LinkStack anonymous administrator-login and HTTP proxy-form gate NATIVE ACCEPTED; isolated browser remains

**Native Kvin operator receipt (subsequent to the public-directory parity already accepted):** Nova ran `ansible/linkstack-anonymous-login-proxy-probe.yml` with separate approval. Kvin recap **`ok=9 changed=0 unreachable=0 failed=0 skipped=0`**. All exact-rootless-user, ARM64 pinned-image, qualified restored volume, running-state and `127.0.0.1:18081` loopback-only port assertions passed. The four bounded anonymous `GET /login` cases — Kvar direct `:8081`, Kvar NPM `:80`, Kvin direct loopback, and Kvin **absolute-form** `GET http://dir.nexus.sanctum/login` to the SAME loopback port — all returned **HTTP 200**, HTML, bounded-complete bodies. All four showed **no redirects**, `Set-Cookie` present, `HttpOnly` present, `SameSite=Lax`, no `Secure` attribute and no explicit cookie `Domain`. The native report recorded **`candidate_proxy_request_compatible=true`**, **`login_status_equal_to_kvar_direct=true`**, **`login_status_equal_to_kvar_npm=true`**. This is **accepted anonymous login-path and proxy-form compatibility**, not actual Firefox or authenticated admin acceptance. No password, form, cookie, CSRF token or private HTML was submitted or printed; no app/service, DNS, proxy, firewall, data-volume or routing changes. Ordinary anonymous GET may allocate an anonymous server session.

**NEXT operator boundary — DESKTOP, not a Kvin Ansible rerun:** use the independently documented [isolated Firefox acceptance procedure](runbooks/linkstack-browser-acceptance.md) (from the project root). First establish an SSH local forward to **Kvin** and a **fresh Firefox profile** with both HTTP and HTTPS proxies explicitly set to the tunnel, no direct fallback or bypass. Verify `http://dir.nexus.sanctum/login` loads, and **fail-closed behavior** (with tunnel stopped, a new uncached request must fail rather than visit Kvar) **before entering credentials**. Restore tunnel, then have Nova privately authenticate and verify recovered admin data. Do not disclose any password/cookie/CSRF/private screenshots. The normal `dir.nexus.sanctum` browser route still ends at Kvar by design; Kvar is not malfunctioning or obstructing anything. The isolated browser test is needed so recovered Kvin, not the live incumbent, is actually exercised. No production cutover or Kvar retirement until separate explicit approval and named-client/rollback qualification. Rootful Pi-hole consistent backup remains separately gated, prepared but not executed.


## November 12 — recovered LinkStack anonymous public-directory parity ACCEPTED; administrator browser route separately gated

**Native Kvin receipt:** Nova ran `ansible/linkstack-recovered-public-surface.yml`. **Kvin `ok=9 changed=0 unreachable=0 failed=0 skipped=0`**; persistent rootless Kvin candidate `sanctum-linkstack-kvin-candidate`, original pinned image, owned recovered volume `sanctum-linkstack-qualified-20261112t105926`, and **only `127.0.0.1:18081`** published port reverified. Anonymous `GET /` from **direct Kvar :8081**, **Kvar NPM :80**, and **Kvin recovered loopback :18081** returned **HTTP 200, HTML**, complete within 512 KiB bounds. Direct Kvar vs recovered exact HTML **`body_equal:true`**; Kvar NPM vs recovered exact HTML **`body_equal:true`**, and old NPM vs Kvar origin also exact. **23 public anchors on both**, **4 CSS asset references on each side with 4 in common**, **2 JS references on each with 2 in common**. Exactly **one shared CSS and one shared JS** anonymously fetched across all three origins; statuses HTTP 200, MIME class, and COMPLETE BODY bytes **identical**. The other 3 CSS and 1 JS resources were discovered but **not individually requested**, and no real browser rendering was performed. **Anonymous public-directory parity is ACCEPTED**; authenticated login/admin and browser session remain unaccepted. `login_surface.status=not_discovered_on_both` means **no matching recognized login link in public home-page markup**, not failure of login. Every task was read-only; Kvar survivors, NPM, Kvin live proxy, DNS, firewall and accepted recovery volumes unchanged. **Do not rerun the one-time LinkStack Kvin stage play** now that its Quadlet is installed.

**Official admin path:** LinkStack's own [FAQ](https://docs.linkstack.org/faq/) says administrator sign-in is at `/login`, whether or not the public directory links there. New read-only source `tools/observe-linkstack-login-proxy-form.py`, `ansible/linkstack-anonymous-login-proxy-probe.yml`, `tests/test_linkstack_anonymous_login_proxy_probe.py` passed full Services source/tests/Ansible syntax [CI #43307103402](https://github.com/wdcallahan/sanctum-services/actions/runs/43307103402). The probe confirms exact Kvin image, owned volume and loopback-only port, and compares **anonymous GET /login** between Kvar direct, Kvar NPM, Kvin direct and Kvin **absolute-form HTTP proxy request** (`GET http://dir.nexus.sanctum/login`) to the **same Kvin loopback backend**. It discloses only fixed response statuses, media classes, redirect host/scheme classes, cookie attribute flags and request-form compatibility; not HTML, redirects, cookies, CSRF or credentials. No auth submitted, no proxy/tunnel created, no production change. Like any login GET, may allocate an anonymous application session. **Probe has NOT yet run natively.**

**NEXT SINGLE OPERATOR ACTION (Kvin only, read-only HTTP requests):**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-anonymous-login-proxy-probe.yml \
  -e sanctum_linkstack_anonymous_login_probe_approved=true
```
Full output welcome. Look for `Report bounded anonymous LinkStack login parity and HTTP proxy compatibility` plus Kvin recap, or failed task. This determines whether a dedicated Firefox profile can use an **SSH `-L` localhost forward as an HTTP proxy**, preserving browser origin `dir.nexus.sanctum` while all requests go only to Kvin, not Kvar. A redirect to HTTPS or unrelated host, incompatible HTTP proxy-form, or a required Secure cookie may block that approach; **do not send credentials before assessing**. Browser conditional procedure is documented in [docs/runbooks/linkstack-browser-acceptance.md](docs/runbooks/linkstack-browser-acceptance.md). After native login compatibility, arrange controlled Firefox session with original credentials privately; explicit user acceptance before any production YXORP upstream transition. Rootful Pi-hole consistent backup remains prepared but unexecuted without separate DNS downtime approval.

**Source/Ansible qualification now GREEN for the next native public-surface observation:** [Services CI #43305239757 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43305239757) at the exact observer+tests source commit `f0b7d34fb080554c23de6dda271986bf85cbee52`. Nothing in this observer has been run on Kvin yet. **Next single Kvin operator command** (bounded anonymous HTTP GET only, no app re-deploy or production routing):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-recovered-public-surface.yml \
  -e sanctum_linkstack_anonymous_surface_observe_approved=true
```
Full output is welcome; expect task `Report sanitized recovered LinkStack directory assets and anonymous login parity` and Kvin recap, or first failure. Compare candidate to current Kvar direct and original NPM on public directory and common static resources with no printed content, credentials, login path, or raw Location. A dynamic body mismatch is **not** proof of data loss. A clean anonymous comparison still does **not** authorize/admin-accept authenticated browser login or retarget current YXORP `dir.nexus.sanctum`. Separately stage a desktop SSH-forward browser path after observing redirect behavior, with actual user login confirmation and explicit cutover later.

## CURRENT — November 12: recovered LinkStack *persistent Kvin loopback Quadlet* native accepted; anonymous page/asset comparison source under CI

**Native operator receipt:** Nova ran `ansible/linkstack-kvin-loopback-stage.yml` on Kvin with the separately approved persistent candidate flag. **`kvin.outer.sanctum ok=29 changed=2 unreachable=0 failed=0 skipped=0`**. Exact owned restored `sanctum-linkstack-qualified-20261112t105926` and original preserved restore-test volume both confirmed; SQLite integrity `ok`, image digest content ID and native ARM64 reconfirmed. Rootless `wdc2` Quadlet **`/home/wdc2/.config/containers/systemd/sanctum-linkstack-kvin-candidate.container`** installed and persistent user systemd service **`sanctum-linkstack-kvin-candidate.service`** started. Container **`sanctum-linkstack-kvin-candidate`** running from exact Kvar image; mounts only corrected recovered candidate volume; actual Podman published port **`127.0.0.1:18081:80/tcp`** verified; Kvin local `GET /` with `Host: dir.nexus.sanctum` returned **HTTP 200**. Two changes are the source Quadlet file and starting the user service. Source archive, unmodified Kvin original restore, live Kvar LinkStack/Pi-hole/NPM, production Kvin proxy, Peanut DNS, host firewall/sysctl unchanged. **Persistent restored-service installation + localhost HTTP are now genuinely ACCEPTED.** Do not repeat the one-shot stage playbook: it intentionally refuses an already installed candidate Quadlet or active service. **Directory content, assets, login/admin UI, live client semantics and production YXORP backend have NOT been accepted.**

**New autonomous source work after this receipt:** `tools/observe-linkstack-recovered-browser-surface.py`, `ansible/linkstack-recovered-public-surface.yml`, and `tests/test_linkstack_recovered_public_surface.py` developed to compare **anonymous GET /** from direct incumbent `kvar.outer.sanctum:8081`, original Kvar NPM HTTP:80 and recovered Kvin **loopback** `127.0.0.1:18081` with identical `Host: dir.nexus.sanctum` and safe forward headers. It privately buffers at most 512 KiB per response, compares status, MIME class, complete bounded body equality, and redirect equality without exposing content or URLs. If both direct Kvar and recovered HTML parse, it counts public links and samples at most one exact **common same-origin, query-free CSS and JS** resource per category across all three endpoints, and optionally anonymous GET of a login link **only if discovered on BOTH public pages**. Never follows redirects, sends credentials, or prints response bodies, titles, path names, login target, cookies, raw Location values or content hashes. All output is boolean/numeric or fixed classes, with dynamic page differences explicitly not conflated with a failed restore. The read-only observer play requires rootless exact Kvin, actual running restored candidate image+volume+loopback binding, separate `sanctum_linkstack_anonymous_surface_observe_approved=true`; no production service, DNS, firewall, proxy or application-data mutation. CI source qualification must pass before host execution; **this new observer has not run on Kvin**.

**Browser gate after anonymous comparison:** Actual named-user browser directory and admin login must be tested without sending passwords/cookies in chat. The retained candidate is loopback-only; **do not** open the public `dir.nexus.sanctum` route or assume clicking links under a tunnel stays on candidate if LinkStack uses absolute URLs. Observe redirects first. A desktop-to-Kvin SSH local forward is a possible independently approved browser path, not an already-accepted admin session. Only after browser behavior is accepted should YXORP `dir.nexus.sanctum` backend be changed in a separate explicit source-reviewed operation with Kvar rollback still intact. Rootful Pi-hole snapshot remains source-qualified but **unexecuted** without separate DNS downtime opt-in.

## November 12 — retained recovered LinkStack volume SUCCESS and loopback Quadlet stage source GREEN

**New native Kvin recovery acceptance:** Nova ran `ansible/linkstack-owned-restored-candidate.yml` with both explicit approvals. **Kvin `ok=26 changed=6 unreachable=0 failed=0 skipped=0`**. Verified original Kvin private LinkStack tar SHA-256 `a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa` and original preserved volume; verified pinned original Kvar ARM64 image; created only new rootless **retained** `sanctum-linkstack-qualified-20261112t105926` volume and imported state. Pre-change SQLite integrity **ok**; a disposable app container with **`sanctum-linkstack-qualified-20261112t105926:/htdocs:U,Z`** and per-container `net.ipv4.ip_unprivileged_port_start=80` remained running and returned **HTTP 200**. It was cleaned up together with its internal/no-DNS network, deliberately **leaving the converted candidate volume available**. Kvar source app, Pi-hole/NPM, original Kvar and Kvin private archives, original unmodified Kvin `sanctum-linkstack-restore-test-20261112t105926` volume, Kvin production apps, host sysctl, proxy/DNS/firewall were unchanged. **Retained, ownership-corrected restored data and genuine isolated HTTP app boot ACCEPTED. Real browser pages/admin, named LAN route, source-managed service, production proxy switch and independent disaster recovery are still NOT accepted.**

**Operator UI correction:** Nova asked what `:U` meant because no `:U` option appeared in the Ansible output. The previous assistant explained Podman option syntax without saying the `podman run --volume ...:/htdocs:U,Z` command sat **inside a task with `no_log: true`**, so Ansible only displayed the `TASK [Start disposable candidate with only its own volume relabeled and chowned]` success, not its arguments. `:U` recursively adjusts mounted volume file UID/GID, `:Z` relabels for private SELinux access; these are Podman *mount option suffixes*, not Ansible task names. Always link explanations to the command that was actually hidden.

**Autonomous source work after this host result:** New `ansible/files/sanctum-linkstack-kvin-candidate.container`, `ansible/linkstack-kvin-loopback-stage.yml`, and `tests/test_linkstack_kvin_loopback_stage.py`; **full Services source and Ansible syntax CI [#43301771698 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43301771698)**. The fixed rootless Quadlet targets **only Kvin `wdc2`**, original pinned image `docker.io/linkstackorg/linkstack@sha256:b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1`, **already corrected** retained named candidate volume `sanctum-linkstack-qualified-20261112t105926:/htdocs:Z` (DO NOT re-run `:U` against preserved unmodified restore volume), namespace-local `Sysctl=net.ipv4.ip_unprivileged_port_start=80`, `NoNewPrivileges=true`, and only **`PublishPort=127.0.0.1:18081:80/tcp`**. No client LAN exposure or production YXORP route replacement. No credentials in Quadlet; recovered config is kept only in named persistent volume. The default-off **one-time** stage playbook requires `sanctum_linkstack_loopback_candidate_stage_approved=true`, verifies image content identity and candidate SQLite/config before installation, checks presence of both preserved volumes, refuses pre-existing Quadlet/unit/container and occupied port 18081, installs only its source-managed rootless candidate Quadlet, reloads/starts the user service, verifies actual running pinned image + exact volume, actual loopback-only Podman port mapping, and local HTTP **200 with Host dir.nexus.sanctum**. No Kvar NPM/Pi-hole, DNS, production proxy, firewall or host sysctl changes. **A successful operation starts a retained, persistent candidate service; this is NOT a throwaway trial.**

**NEXT exactly one Kvin host operator action** (new separate approval to create a persistent loopback-only recovered app; no public route):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-kvin-loopback-stage.yml \
  -e sanctum_linkstack_loopback_candidate_stage_approved=true
```
Full output welcome. Expected final task `Report bounded Kvin loopback restored LinkStack candidate acceptance` and Kvin recap or first failed task. Native run has **not yet occurred**, so do not claim Quadlet service/browser acceptance. If stage succeeds, inspect directory page assets and admin in a separate browser/controlled route without sending credentials in chat; then separately approve YXORP `dir.nexus` backend transition, keep Kvar fallback. Rootful Pi-hole backup remains source-qualified but **not yet executed** without separate DNS downtime approval.
**Source and Ansible syntax now GREEN:** Full [Services CI #43299880000 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43299880000) with the retained candidate one-shot and guard tests. **No native run of the retained owned candidate has occurred.** Next one Kvin operator boundary (explicitly authorizes a NEW retained candidate and recursive `:U,Z` ownership/relabel of only that new volume; NO source archive, preserved accepted restore volume, Kvar service, DNS, host sysctl, production proxy or Pi-hole modification):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-owned-restored-candidate.yml \
  -e sanctum_linkstack_owned_candidate_restore_approved=true \
  -e sanctum_linkstack_candidate_private_relabel_chown_approved=true
```
Send full native output including `Report bounded owned LinkStack candidate recovered HTTP acceptance` and Kvin recap or the first failed task. The new volume remains after the test as `sanctum-linkstack-qualified-20261112t105926`, even if HTTP fails, rather than touching the already accepted original test volume. Success accepts only isolated restored HTTP 200 on this candidate; next build/verify source-managed Kvin service and recognizable real browser/admin state before proxy cutover. The separate Pi-hole backup is still unexecuted.

## CURRENT — November 12: restored LinkStack :U,Z candidate HTTP 200 PROVEN on disposable clone; new retained candidate source

**Native Kvin evidence:** Nova ran `ansible/linkstack-volume-mount-diagnose.yml`, recap **`kvin.outer.sanctum ok=6 changed=1 unreachable=0 failed=0 skipped=0`**. Exact pinned ARM64 LinkStack image with per-container `net.ipv4.ip_unprivileged_port_start=80` and no persistent volume: **Running=true, HTTP 200**. Freshly imported **disposable clone** from Kvin's original checksum-verified archive attached normally: **exits 1**, stderr categories `permission_denied`, entrypoint begins but fails before Apache launch banner. Same disposable clone with private SELinux-only `:Z`: **also exits 1**, same category. Same clone with `:U,Z` (recursive UID/GID adjustment plus private SELinux relabel): **Running=true, HTTP 200**. Thus `comparison=ownership_repair_after_relabel_restores_http`; owner/mapping is an actual missing mount prerequisite, while `:Z` alone was insufficient. **No specific individual file is yet identified as the cause.** Prior to adjustment, the fixed sample `.env`, `version.json`, `database`, `database/database.sqlite` was host-owned `100099:100100` with ordinary `0644`/ `0755`; imported volume root `1000:1000`. These subordinate IDs may be valid user namespace mappings and do not themselves prove which other paths required chown. The diagnostic did not return post-`:U` per-file ownership. Every one of **four temporary containers**, the cloned volume, and the temporary internal/no-DNS network was cleaned. Original accepted rootless Kvin restore volume `sanctum-linkstack-restore-test-20261112t105926`, private source archive on Kvar and hash-matched private Kvin copy remain unchanged, as do all Kvar apps/NPM/Pi-hole, Kvin production services, host sysctl and DNS/YXORP. **This is a positive application HTTP 200 against a temporarily *corrected clone*, not yet the retained Kvin application candidate nor a real browser/admin acceptance.**

**Podman semantics:** Official Podman `podman-run` documentation https://docs.podman.io/en/stable/markdown/podman-run.1.html states `:U` recursively changes source owner/group using the container user-to-host UID/GID mapping. `:Z` privately relabels for SELinux. Both modify metadata, and `:U` can be costly on thousands of entries. Neither should be used to mutate the original accepted restore volume in an exploratory test.

**New autonomous source:** `ansible/linkstack-owned-restored-candidate.yml` and `tests/test_linkstack_owned_restored_candidate.py` prepare a separately approved **new retained Kvin rootless candidate volume `sanctum-linkstack-qualified-20261112t105926`**, imported from only the verified original **93,845,504-byte** SHA-256 `a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa` archive. The playbook refuses colliding volume/container/network names, preserves original accepted restore, verifies pinned image content ID and pre-adjustment candidate SQLite, then applies `:U,Z` **only to the new candidate volume** in a throwaway network-internal no-host-port container with proven container-only low-port sysctl; accepts only real HTTP 200, removes container/network in `always`, and **retains the newly owned candidate volume** for later source-managed Kvin service staging and browser/admin acceptance. It never modifies production, off-Kvar originals, an existing restore volume, host sysctl or proxy. Separate explicit default-off affirmative approvals for candidate creation and clone-only recursive relabel/chown. **Source CI still needs green before host instruction.** Old original LinkStack trial must not be repeated or amended with `:U` on the preserved accepted restore volume.

## CURRENT — November 12: restored LinkStack exits even with proven port-80 sysctl; disposable clone differential CI GREEN, next host gate

**New native receipt:** Nova reran `ansible/linkstack-qualify-isolated-application.yml` on Kvin after the image-only A/B proved that the rootless Apache startup required a **container-only** `--sysctl net.ipv4.ip_unprivileged_port_start=80`. The restored-volume application trial **still exited before HTTP**, failing exact task `Refuse HTTP acceptance if restored app has already exited`. Kvin recap **`ok=23 changed=4 unreachable=0 failed=1 skipped=1`**. Ansible `always` removed **both** the uniquely named disposable app container and temporary internal/no-DNS network. No live Kvar LinkStack/NPM/Pi-hole interruption, no Kvin production service/host-sysctl/proxy/DNS modification; accepted source archive, verified Kvin private copy and original Kvin isolated restore volume `sanctum-linkstack-restore-test-20261112t105926` remain intact. This is evidence that **port 80 was ONE genuine blocker**, not that it was the only blocker. The volume-specific root cause is not yet accepted; no app-startup or browser/admin acceptance.

**Completed autonomous recovery diagnostic:** `tools/diagnose-linkstack-volume-mount.py`, `ansible/linkstack-volume-mount-diagnose.yml`, and `tests/test_linkstack_volume_mount_diagnose.py`; **[full Services CI #43294979453 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43294979453)** including Python safety/negative tests and Ansible syntax. Exact Kvin rootless `wdc2` host, verified *immutable* ARM64 source image ID, exact Kvin-local private tar **93,845,504 bytes SHA-256 a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa**, and existing accepted restored volume are preflight gates. It makes a **new disposable rootless volume** by importing that exact tar, never mounts or changes the accepted restore volume. All trials use only an ephemeral `--internal --disable-dns` bridge with **no published ports**, the proved **per-container** port-80 sysctl and existing `no-new-privileges`. Compare: (1) image-only control; (2) freshly cloned volume unmodified at `/htdocs`; (3) same disposable clone with private `:Z` SELinux relabel; (4) only if earlier stages fail, same clone with `:U,Z` recursive ownership repair. **`:Z` and `:U` can modify filesystem metadata**, but only the *disposable cloned volume*; the new play has a **separate affirmative** `sanctum_linkstack_disposable_relabel_chown_approved=true` gate in addition to `sanctum_linkstack_clone_mount_diagnostic_approved=true`. It skips remaining stages as soon as an earlier mount serves HTTP 200. Reports finite process exit/OOM/HTTP and categories from privately captured stdout+stderr, plus metadata-only safe modes/owner IDs of fixed known markers `.env`, `version.json`, `database/database.sqlite`—**no file contents, raw error text or secrets**. Attempts exact-name cleanup of every created temporary container, cloned volume and internal bridge in finally; negative tests reject preexisting resource identities without deletion. The clone may incur ownership relabel cost on approximately 10,523 files. This diagnostic does **not** itself qualify production app startup, persistent LinkStack candidate, named browser content/admin, Kvar retirement, or independent disaster recovery.

**NEXT operator boundary, Kvin only**: user must accept temporary clone-only SELinux relabel/recursive chown operations; no original preserved volume mutation. Run:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-volume-mount-diagnose.yml \
  -e sanctum_linkstack_clone_mount_diagnostic_approved=true \
  -e sanctum_linkstack_disposable_relabel_chown_approved=true
```
**Entire output welcome** (no manual report extraction): `Report sanitized LinkStack restored-volume mount and labeling differential` plus Kvin PLAY RECAP or failed task. If `comparison=private_selinux_relabel_restores_http`, source-gate appropriate relabel on a *separately cloned test* before changing accepted volumes. If `ownership_repair_after_relabel_restores_http`, qualify mapping/UID plan, again do not chown original restored or live data on hypothesis alone. If all cases fail, use the captured finite error classes to narrow the application-data startup cause. Retain all earlier accepted archive and volume work; do not repeat Kvar backup or SCP transfer.

## CURRENT — Thursday, November 12: LinkStack Apache port-80 namespace cause PROVEN; restored-app trial corrected, pending native

**Native Kvin receipt:** Nova ran the source-owned default-off `ansible/linkstack-port80-bind-diagnose.yml`; **`kvin.outer.sanctum ok=6 changed=1 unreachable=0 failed=0 skipped=0`**. The rootless Linux ARM64 pinned image (original Kvar immutable content ID `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65`) was exercised in two otherwise identical *image-only*, disconnected containers on a new internal/no-DNS bridge, with **no saved LinkStack volume mounted**. **Baseline** exited code **1**, `running:false`, `http_status:null`, error classes `apache_listen_socket`, `apache_log_open`, **`listen_permission_denied`**. **Container network-namespace-only** `--sysctl net.ipv4.ip_unprivileged_port_start=80` variant **ran**, `exit_code:0` (while running), and responded **HTTP 200** internally; its log had no recognized error classes. `comparison:namespaced_low_port_policy_enables_startup`; **this confirms insufficient unprivileged port-80 permission as the startup cause for the standalone image**, not SQLite corruption, a broken immutable image, or added `no-new-privileges`. The report explicitly accepted that the **host sysctl was unchanged**, all three disposable resources removed, original restored data and Kvar/production untouched. **Do not claim actual restored-application boot yet**; prior original restored-app trial exited before HTTP and has not been repeated with the proven setting.

**Services source correction:** In `ansible/linkstack-qualify-isolated-application.yml`, add **`--sysctl net.ipv4.ip_unprivileged_port_start=80` to only the disposable restored-app `podman run`**; retain the same extra `no-new-privileges`, isolated internal/no-DNS bridge, no published ports, exact immutable ARM64 image gate, prior imported and SQLite-verified dedicated Kvin rootless volume `sanctum-linkstack-restore-test-20261112t105926`, bounded internal HTTP and guaranteed container/network cleanup. No host `sysctl -w` or host port 80 exemption. Add regression asserting exactly one isolated `--sysctl` and no host-level configuration write, and honest report flags `container_network_namespace_low_port_override_used:true`, `host_low_port_sysctl_unchanged:true`. Source edits are on main with CI needed before operator run. Previous accepted source tar on Kvar, SHA-verbatim Kvin private tar and Kvin imported distinct rootless volume remain; **do not** rerun backups/SCP/import.

**Source qualification:** Full Services source/negative tests and Ansible syntax **[CI #43290872566 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43290872566)** at corrected restored-app source commit `10ef129fd5898be193670b053346d71bc167f7e3`. The native restored-volume app test with container-only port-80 sysctl has **not yet run**. This is the current operator action; no separate Kvar backup/SCP/import is needed.

**Next host action, source CI green** (on Kvin, new operator execution approval):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-qualify-isolated-application.yml \
  -e sanctum_linkstack_image_qualification_approved=true \
  -e sanctum_linkstack_offline_application_trial_approved=true
```
**Entire output welcome**. Report `Report bounded LinkStack ARM64 image and offline restored-application acceptance` and Kvin recap, or failed task. A positive result means **HTTP app startup with imported restored data**, not named live browser directory/admin content acceptance, production YXORP backend routing or independent disaster recovery. Kvar LinkStack/NPM, Pi-hole and Peanut DNS remain untouched. Separately source-green Pi-hole backup remains **not executed** without approval of an intentional DNS service interruption.

**CI ACCEPTED and next native operator boundary — November 12:** Full [Services source and Ansible syntax CI #43285610612 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43285610612). The current default-off diagnostic is `ansible/linkstack-port80-bind-diagnose.yml`, **NOT** the old image runtime or restored-app test. It tests only the exact already-cached ARM64 image, on a new internal/no-DNS bridge in two throwaway **image-only** rootless containers, one ordinary and one with **only container-network-namespace** `net.ipv4.ip_unprivileged_port_start=80`. No host sysctl, service, published port, original volume, Kvar app, database, DNS, firewall, YXORP or Pi-hole change. Both temp containers and network are cleaned in finally with pre-existing name collision refusal. This tests the actual low-port bind permission hypothesis; does not assert Kvin restored app works.

**Run on Kvin only after explicit opt-in:**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-port80-bind-diagnose.yml \
  -e sanctum_linkstack_namespaced_port80_diagnostic_approved=true
```
Send **entire output** (no need to trim); one report `Report sanitized LinkStack namespaced port-80 bind comparison` and Kvin recap, or failed task. If `comparison=namespaced_low_port_policy_enables_startup`, implement the same isolated per-container network permission in a *separately guarded restored-app test*, not a global sysctl. If it fails, inspect its `start_command_failed` vs exit categories and do not misclassify a Podman unsupported namespaced sysctl as proof of a different Apache cause.

## CURRENT — November 12: native LinkStack Apache stderr confirms port-80 bind denied; namespace-only differential CI pending

**Native receipt:** Nova reran `ansible/linkstack-image-runtime-diagnose.yml` after the stdout/stderr diagnostic fix. Kvin `ok=6 changed=1 unreachable=0 failed=0 skipped=0`, all temporary image-only containers and internal/no-DNS bridge successfully removed. Both ordinary rootless Podman and the additional `no-new-privileges` case report `Running:false, ExitCode:1, OOMKilled:false, http_status:null`. Both passed static image prerequisites and Apache `httpd -t`; entrypoint banners reached `Running Apache` before exit. **Captured stderr error classes for BOTH**: `apache_bind`, `apache_listen_socket`, `apache_log_open`, `permission_denied`. This is positive evidence Apache's socket binding was denied, not failure of the verified archive or imported SQLite. Apache's secondary `AH00015` log-open message can result from a failed bind; do not assume it requires an independent logging fix.

**Grounded cause hypothesis:** The actual upstream `LinkStackOrg/linkstack-docker/configs/apache2/httpd.conf` declares **`Listen 80`**, and its Dockerfile declares **`USER apache:apache`**; Kvin rootless's container network namespace may enforce privileged-port threshold 1024. Official Podman troubleshooting documents rootless port-80 permission failures and the `net.ipv4.ip_unprivileged_port_start` knob. References: https://github.com/LinkStackOrg/linkstack-docker/blob/main/configs/apache2/httpd.conf and https://github.com/LinkStackOrg/linkstack-docker/blob/main/Dockerfile ; https://github.com/containers/podman/blob/main/troubleshooting.md#48-pasta-fails-with-listen-failed-or-rootless-podman-fails-with-bind-permission-denied. **Do not change global Kvin sysctl** or assume the namespaced option works until native proof; actual upstream source may differ from cached historical digest but its running errors support this hypothesis.

**Independent source work:** `tools/diagnose-linkstack-port80-bind.py`, `ansible/linkstack-port80-bind-diagnose.yml`, `tests/test_linkstack_port80_bind_diagnose.py` prepared. It is **default-off**, targeted only to rootless `wdc2` on Kvin `aarch64`, using one disposable Podman `--internal --disable-dns` bridge with no published host ports and **no mounted volumes**. It compares a baseline pinned-image startup to one using **`--sysctl net.ipv4.ip_unprivileged_port_start=80`**, which Podman documents as a **per-network-namespace runtime sysctl**, not a host/global change. Reports only bounded exit/running/OOM/HTTP, error classes from both private stdout/stderr, no raw logs or secrets. Refuses preexisting exact temp names and deletes only created temp objects; no Kvar, no live LinkStack/Pi-hole, no YXORP, no backup/restore mutations. The separate flag is `sanctum_linkstack_namespaced_port80_diagnostic_approved=true`. Source CI is running; do NOT ask the operator to run until the full Services source/Ansible tests pass.

## CURRENT — November 12: independent Pi-hole consistent backup source GREEN; still not run

While the **LinkStack image-only stderr diagnostic remains the current Kvin host boundary** (see immediately below; do not repeat Kvar→Kvin backup/transfer/import), Services independently prepared a **default-off rootful Pi-hole same-stop two-volume backup**. `ansible/pihole-consistent-backup.yml` + `tools/pihole-archive-verify.py` + tests passed **[full Services CI #43283325769](https://github.com/wdcallahan/sanctum-services/actions/runs/43283325769)** including syntax/negative archive checks. It requires **separate explicit approvals** to temporarily interrupt Pi-hole DNS/web service; stops only `pihole.service` on Kvar, exports both named `/etc/pihole` and empty `/etc/dnsmasq.d` volumes in the same stopped window, uses `always` original restart, and validates full private archive tar/SQLite integrity before no-clobber promotion. Preflight refuses changed Pi-hole image identity `64c81b3c8132f3e7ae56925a1668d2cfa5a53c509c43b4c1cc71591e0f42c3d8` or runtime mounts/ports, so automatic updates cannot silently change the qualified input. No Pi-hole backup has **executed**, been copied to Kvin, or been restored. **Do not auto-run the Pi-hole source**; if Nova opts into the DNS interruption, use the separate exact command recorded in [docs/runbooks/kvar-survivor-consistent-backup-plan.md](docs/runbooks/kvar-survivor-consistent-backup-plan.md). Pi-hole cutover, general DNS ownership and LAN client adoption remain closed.

## CURRENT — November 12: LinkStack native runtime diagnosis reaches Apache but both exit 1; fix discarded stderr, CI GREEN

**Native accepted diagnostic:** Nova ran `ansible/linkstack-image-runtime-diagnose.yml` on Kvin, recap `ok=6 changed=1 unreachable=0 failed=0`. Pinned running Kvar image ID was matched in cached Kvin ARM64 image, declared image user `apache`, `docker-entrypoint.sh` command and `/htdocs` workdir recognized. Image-only static preflight confirms `version.json` readable, `php83` configuration writable, `/htdocs` writable, and Apache executable. Apache `httpd -t` passed. Both disconnected, **no-mounted-volume** test containers (one added `--security-opt no-new-privileges`, one normal rootless default) reached `version_banner_seen`, `config_update_seen`, and `apache_launch_banner_seen`, then **exited 1**, neither OOM-killed, neither serving HTTP. `comparison:both_exit_common_image_startup`; **the additional security flag is ruled out as the distinguishing cause**. All temporary containers and temporary internal/no-DNS network removed; no Kvar or Kvin production changes, restored backup/data untouched.

**Diagnostic loss discovered in source:** `tools/diagnose-linkstack-image-runtime.py` used `logs_rc, logs, _ = run(["podman","logs",...])` and applied `classification(logs)` to only the subprocess **stdout**, throwing away **stderr**. Upstream LinkStack Apache `httpd.conf` explicitly has `ErrorLog /dev/stderr`, so the repeated `unclassified` classifications may have concealed the actual Apache cause. This is an observability defect in *our tool*, not evidence of a malformed SQLite backup, bad image, SELinux failure, or privileged-port conflict. We must not guess a concrete Apache error before collecting the missing stream.

**Corrected autonomous source:** The same bounded diagnostic now privately captures **both stdout and stderr** from only the two unique temporary image-only trials, verifies combined bounded size, emits only allowlisted error classes and safe startup milestones, plus booleans `stdout_available`/`stderr_available` and **`stderr_error_categories`**. New safe Apache classes include `apache_log_open` (`AH00015`), `apache_startup_config_failed` (`AH00016`), `apache_runtime_directory` and `apache_listen_socket`. The regression test puts a secret sentinel and **only** an AH00015 error in stderr and proves it is recognized without disclosing raw text. Full [Services source, Python tests and Ansible syntax CI #43281797940 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43281797940). No live Apache changes, no image update, no database mount or transfer.

**NEXT Kvin operator boundary:** rerun only the now-instrumented source-owned image-only diagnostic to see the previously omitted stderr categories; do **not** repeat Kvar backup, Kvar→Kvin SCP/import or restored app trial. On Kvin:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-image-runtime-diagnose.yml \
  -e sanctum_linkstack_image_runtime_diagnostic_approved=true
```
The whole output is welcome; specifically `Report sanitized LinkStack image runtime and startup variant comparison` and PLAY RECAP. If stderr yields a bounded Apache error, correct that *specific* source/runtime condition; if not, add a different diagnostic rather than inventing a root cause. Exact pinned image and original restored volume remain intact. Keep Kvar LinkStack/NPM/Pi-hole and Kvin YXORP running; no route cutover yet.

## CURRENT — November 12: LinkStack BOTH image-only and restored-copy startups EXIT 1; focused image runtime diagnosis source GREEN

**Native receipt:** Nova approved and ran `ansible/linkstack-offline-startup-diagnose.yml` on Kvin: `ok=6 changed=1 unreachable=0 failed=0 skipped=0`. Both **image-only** and **cloned restored data** disposable LinkStack instances exited **code 1**, `running:false`, `oom_killed:false`, `http_status:null`. Both emitted logs categorized **`unclassified`**. `reason_comparison:both_exit_startup_independent_of_restored_data_possible`, **NOT evidence of a corrupt database** or proven root cause. All four temporary resources (two containers, cloned volume, private internal bridge) were removed; existing Kvin restored volume and tar and original Kvar app remain untouched. No application startup acceptance, DNS/proxy change, production interference or Pi-hole change.

**Upstream source consulted** (do not claim identical contents of exact cached digest until native inspection): `LinkStackOrg/linkstack-docker/Dockerfile` sets `USER apache:apache` and `CMD ["docker-entrypoint.sh"]`. The shell entrypoint reads `/htdocs/version.json`, appends to `/etc/php83/conf.d/40-custom.ini`, removes `/htdocs/httpd.pid`, then launches Apache `httpd -D FOREGROUND`. This directs the next non-secret probe to image-internal file access and Apache configuration, rather than repeating backup/copy/import or generic application HTTP tests. Upstream: https://github.com/LinkStackOrg/linkstack-docker/blob/main/Dockerfile and https://github.com/LinkStackOrg/linkstack-docker/blob/main/docker-entrypoint.sh.

**Completed autonomous engineering:** `tools/diagnose-linkstack-image-runtime.py`, `ansible/linkstack-image-runtime-diagnose.yml` and `tests/test_linkstack_image_runtime_diagnose.py` added. Full Services source and native Ansible syntax **[CI #43280197789 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43280197789)**. The one Kvin-only rootless read-only/image-only diagnosis re-verifies exact cached image digest, architecture and Kvar image ID, then tests static `/htdocs/version.json` readability, PHP INI writability, `/htdocs` writability, Apache executable and `httpd -t` syntax in temporary unmounted containers. On one disposable internal/no-DNS bridge it compares image-only startups with the previous additional `--security-opt no-new-privileges` option **versus normal rootless Podman confinement**, recording only running/exit/OOM/HTTP numeric status and *finite* known-error/entrypoint-stage categories (no raw stdout, logs, private files, image environment or credentials). It mounts **no saved LinkStack data**, has no published ports or external network, and cleans up only its two exact new containers and one temporary internal network. Negative tests forbid deletion of pre-existing named resources. **Not a production restore or evidence that removing the security flag fixes anything**; only a native comparison can establish that.

**NEXT SINGLE OPERATOR ACTION on Kvin**, explicit opt-in to two disposable *image-only* internal startup trials; no existing volumes/application data or Kvar interaction:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-image-runtime-diagnose.yml \
  -e sanctum_linkstack_image_runtime_diagnostic_approved=true
```
Entire output is welcome. The single report `Report sanitized LinkStack image runtime and startup variant comparison` and Kvin recap (or failed task) determine whether the extra security option changes startup and whether entrypoint file/Apache syntax prerequisites exist. Do not retry old copied-data container or source archive transfer. Once native cause is known, correct only that startup contract and rerun a separate gated isolated restored-app acceptance. Keep Kvar, NPM, Pi-hole and live YXORP untouched.

## CURRENT — November 12: differential LinkStack test proves *both* startup paths exit 1; startup/runtime discrepancy, not proven data corruption

**Native Kvin differential diagnostic:** Nova ran `ansible/linkstack-offline-startup-diagnose.yml` with approval. `kvin.outer.sanctum: ok=6 changed=1 unreachable=0 failed=0`; report `status:observed`. **Both the image-only container and independent cloned-restored-volume container exited with `ExitCode=1`, `Running=false`, `OOMKilled=false`, `http_status=null`**. Both log outputs classified **`unclassified`**, not empty/safe or proof of good Apache startup. `reason_comparison=both_exit_startup_independent_of_restored_data_possible`. The tool confirmed **all four disposable resources removed** (both containers, copied volume, temporary internal/no-DNS network), unchanged accepted restored volume and source archive, no Kvar touch or production network/service changes. Earlier archive SQLite integrity, image digest and ARM64 checks remain accepted, but **a recovered LinkStack app has not been proven to start**.

**Upstream startup source inspected:** LinkStackOrg/linkstack-docker `Dockerfile` specifies `USER apache:apache`, `CMD ["docker-entrypoint.sh"]`, `WORKDIR /htdocs`. The entrypoint reads `/htdocs/version.json`, writes to `/etc/php83/conf.d/40-custom.ini`, removes `/htdocs/httpd.pid`, then `exec`-like foreground Apache `httpd -D FOREGROUND` (actual shell command). This is general upstream source, not yet confirmation of the exact pinned image's file state. Tests must distinguish startup prerequisites and Podman runtime restrictions. This test's `unclassified` log categories are an **instrumentation gap**; do not broaden logging to disclose real `.env` values or raw container logs.

**Next engineering direction:** Build one bounded image-only, Kvin-rootless differential: compare the formerly added `--security-opt no-new-privileges` trial to ordinary rootless Podman's existing default confinement, under the same temporary `--internal --disable-dns` network, without mounting any LinkStack data; inspect pre-start exact cached image, user/command classification, static `/htdocs/version.json` readability, `/etc/php83/conf.d/40-custom.ini` write access and Apache syntax, collect only fixed startup milestone boolean flags, exit code and a finite known-error taxonomy (never free text), then clean up both container names and internal network. If default mode works, identify a restrictive flag regression; if both exit, compare other host/Quadlet runtime prerequisites. **No previous backup, transfer or restore repeat; no production interruption.**

**Qualification result / current operator gate:** Full Services source and Ansible syntax CI **[#43277394735 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43277394735)**, including host/account refusals, raw-log redaction, two-case process comparisons, archive identity guards, no host ports/external network, and mandatory four-resource cleanup. This is **source only**; no differential diagnostic has yet run natively on Kvin. Next operator action **on Kvin**, with explicit consent to create two temporary rootless containers, one internal/no-DNS network and one disposable cloned volume (original accepted restored volume untouched):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-offline-startup-diagnose.yml \
  -e sanctum_linkstack_startup_diagnostic_approved=true
```
**Entire output welcome**; the single task `Report sanitized image-only versus restored-copy startup comparison` and Kvin recap (or a failed task) are sufficient. Its output distinguishes image-only startup from failure caused by data/mount/permissions without exposing logs. It **does not** start production, retarget the proxy, interrupt Kvar, or qualify the application as working. Never rerun the old full LinkStack HTTP trial as the diagnostic.

## November 12 — corrected LinkStack internal-network trial confirms application EXIT before HTTP; differential diagnostic source pending native

Nova reran `ansible/linkstack-qualify-isolated-application.yml` with the disposable internal/no-DNS bridge. **Kvin `ok=23 changed=4 unreachable=0 failed=1 skipped=1`**. The actual task `Refuse HTTP acceptance if restored app has already exited` failed because `(linkstack_trial_running.stdout | trim) == 'true'` evaluated **false**. The disposable container **exited before an HTTP request could be made**. Both the *specifically named disposable container* and *its internal bridge* were successfully removed in the `always` block. Image identity/ARM64 and PHP 8.3 from prior native run were accepted; restored volume SQLite integrity was rechecked earlier in this run. Original Kvar LinkStack and Pi-hole, Kvar NPM, live Kvin apps, published DNS and YXORP unchanged. Original Kvar tar, verified Kvin tar, and original separately imported Kvin rootless LinkStack test volume remain intact. **Do NOT claim HTTP app boot, nor infer exact cause from exited state alone.**

**New diagnostic engineering:** `tools/diagnose-linkstack-offline-startup.py` with `ansible/linkstack-offline-startup-diagnose.yml` performs a **differential bounded two-case test** on Kvin only: (1) original pinned image with its own image-seeded `/htdocs`, (2) same image using a **new disposable rootless volume freshly imported** from the already checksum-validated **Kvin-local** tar. It never remounts or modifies the *accepted separately imported restore-test volume* or any incumbent volume. It creates one temporary **internal/no-DNS** rootless bridge, has no published ports/external route, and checks both containers' bounded `Running`, `ExitCode`, `OOMKilled`, HTTP status where running, and **allowlisted log classifications only** (`permission_denied`, `read_only`, `missing_path`, `apache_config`, `apache_bind`, `sqlite_error`, `php_error`, `pid_file`), never showing raw logs, paths, .env content or credentials. An unconditional finally block removes both uniquely named containers, new temporary volume and new network, and reports any cleanup failure. Host/user, exact archive SHA256/mode/size and exact pinned ARM64 image identity are hard gates. A positive `sanctum_linkstack_startup_diagnostic_approved=true` is required. Source tests and full Ansible syntax CI must be green first.

**Interpretation:** If image-only runs but restored-data copy exits, focus on imported volume ownership/SELinux/entrypoint data state. If both exit, focus on common image startup. A missing recognized log category is not evidence of success; next narrower non-secret probe may be needed. Do **not** repeat the original 15 HTTP retries or Kvar backup/SCP/import to diagnose.

## November 12 — first LinkStack offline boot HTTP test FAILED SAFELY; corrected internal-only network CI GREEN

Nova ran the original `ansible/linkstack-qualify-isolated-application.yml` on Kvin. Actual native recap **`ok=18 changed=3 unreachable=0 failed=1`**. **Passed**: exact rootless Kvin target, previously imported separate volume, restored SQLite integrity, free disposable name, rootless pull of the pinned exact ARM64 LinkStack image, image architecture and exact original Kvar content ID, and offline PHP 8.3 execution. Temporary restored-app container started. All **15** `podman exec ... curl http://127.0.0.1/` probes failed (`rc != 0`); the HTTP status acceptance assertion failed. The Ansible `always` handler **removed the disposable container successfully**. No production route/service or Kvar image/volume was changed; the previously copied tar, original source tar, and separately imported Kvin volume remain. **Do not claim restored LinkStack application boot or HTTP acceptance.**

**Design defect identified:** The original trial used `podman run --network none` then tried TCP 127.0.0.1 inside that unconfigured network namespace. Podman's own [run documentation](https://docs.podman.io/en/latest/markdown/podman-run.1.html) states `none` creates a namespace **without configuring network interfaces**; therefore localhost HTTP cannot be reliably tested through that mode. The native failure does **not** establish whether Apache itself was healthy or exited later; that remains an evidence gap, not proof of an invalid backup. The original run's successful guaranteed container cleanup is independently observed.

**Source correction:** Rebuilt the playbook from a known-good revision after rejecting an intermediate malformed YAML edit in CI. It now checks a unique temporary rootless network name, creates **only** a new `--driver bridge --internal --disable-dns` Podman network, requires its observed `driver=bridge`, `internal=true`, and `dns_enabled=false`, then runs the temporary LinkStack container on *that network* with **no published ports, no external route, and no host networking**. It checks the container is actually running before attempting HTTP from inside the namespace. Its `always` tasks remove both the disposable container and the single temporary network; it refuses declaring success unless both cleanups pass. No new image pull expected because original exact digest is already cached; the image and restored data are reverified without repeating Kvar backup, SCP transfer or import. Test source now explicitly prevents using `--network none` in the application HTTP trial and verifies internal/no-DNS network, cleanup and failure behavior.

**Full Services source+syntax CI [#43275657216 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43275657216)**, including Ansible syntax after rebuilding the YAML and all isolated-app/negative tests. **No native rerun of corrected playbook yet**.

**Next exact Kvin operator action (same permissions as previously granted, but creates a disposable internal bridge):**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-qualify-isolated-application.yml \
  -e sanctum_linkstack_image_qualification_approved=true \
  -e sanctum_linkstack_offline_application_trial_approved=true
```
Full output welcome. This requires explicit operator opt-in for the new short-lived internal network; it **does not** touch Kvar, existing apps, production host ports, DNS, proxy or firewall. If this still fails, classify the next actual failure (network creation, container running state or HTTP) from native evidence; do not infer apache health or launch live LinkStack until proved.

## CURRENT — November 12: Kvar→Kvin LinkStack isolated data restore ACCEPTED; pinned ARM64 offline app trial CI GREEN, native operator gate next

**New native operator evidence:** Nova ran default-off `ansible/linkstack-transfer-isolated-data-restore.yml` successfully from Kvin. Kvar `ok=4 changed=0 failed=0`; Kvin `ok=22 changed=6 failed=0`; `unreachable=0` both. Kvar archived original private `linkstack-20261112t105926.tar` was confirmed 93,845,504 bytes / SHA-256 `a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa`; authenticated strict-host-key port 10022 SCP copied exact bytes to Kvin. Recipient private tar and archive SQLite validation passed; new rootless Kvin isolated volume **`sanctum-linkstack-restore-test-20261112t105926`** imported and verified `.env` present, SQLite integrity `ok`. **Archive off Kvar and isolated data import accepted**, but **live restored application boot and named directory browser/admin NOT accepted**. Independent disaster recovery across both host failures remains unproven. Original Kvar LinkStack/Pi-hole, NPM, Kvin production services and YXORP/DNS were untouched.

**Autonomous work:** Docker Hub `linkstackorg/linkstack:latest` Linux/ARM64 platform digest **`b1a16980ad4964aac81e484e1b5c870d37a4d040892607d963b443c2be1f8df1`** matches one of the exact running Kvar image's previously observed `RepoDigests` (running image ID `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65`). Official upstream LinkStack Docker supports `linux/arm64`, Apache and PHP 8.3 with `/htdocs` persistent state. Added a **registry-only candidate**, *not yet Kvin-qualified*, to `data/container-image-candidates.yml`. Implemented `ansible/linkstack-qualify-isolated-application.yml` and `tests/test_linkstack_qualify_isolated_application.py`; **full Services CI [#43272156993 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43272156993)**. This strictly default-off Kvin aarch64 rootless operation requires two approvals, exact previously imported volume pre-verified SQLite integrity and unoccupied temporary container, pulls only a pinned digest if absent, checks actual native architecture **and equal original source image ID**, executes PHP 8.3 offline, then tests LinkStack HTTP within a **disposable `--network none` container without published ports** using only the isolated data volume. An `always` task removes the created disposable container. No Kvar touch, live app, production volume, DNS/proxy/firewall change or browser admin acceptance. Original restored volume retained.

**NEXT EXACT HOST OPERATOR GATE: one Kvin-only opt-in** (immutable image pull into rootless cache + isolated offline app trial; no production route or service change):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-qualify-isolated-application.yml \
  -e sanctum_linkstack_image_qualification_approved=true \
  -e sanctum_linkstack_offline_application_trial_approved=true
```
**Full output welcome;** one bounded final task `Report bounded LinkStack ARM64 image and offline restored-application acceptance` and Kvin PLAY RECAP, or failed task. [Runbook](docs/runbooks/kvar-survivor-consistent-backup-plan.md) updated. After native acceptance, source-manage a separate Kvin rootless candidate behind loopback port, verify user-recognizable directory and admin, then separately retarget `dir.nexus` YXORP upstream. Kvar remains fallback. **Do not repeat already accepted transfer/import.**

## CURRENT — November 12: LinkStack quiesced Kvar snapshot ACCEPTED; new transfer/import source CI GREEN

**Native accepted original backup:** Nova ran `ansible/linkstack-consistent-backup.yml` from Kvin against Kvar rootless LinkStack with explicit interruption approval. Recap **`ok=30 changed=6 unreachable=0 failed=0 skipped=0`**. Original LinkStack was briefly stopped and always restarted; image ID/mount/port were unchanged after restart, HTTP returned **200**. **Kvar-local private tar** `/home/wdc2/.local/share/sanctum-services/backups/linkstack/linkstack-20261112t105926.tar` is **93,845,504 bytes**; SHA-256 **`a1110a717d11ee1723c02f8b66557a1c122ac64137f5fa793488428b7a398eaa`**. Safe archive validation passed; `.env` present and SQLite `integrity_check=ok`. `linkstack_consistent_snapshot_accepted:true`. **`archive_copied_off_kvar:false`, `isolated_kvin_restore_accepted:false`** until native downstream result. Kvar remains running with its NPM; Pi-hole and DNS/proxy were not changed.

**Operator feedback repaired:** The backup was using deprecated `ansible_date_time` injected top-level fact; source now uses `ansible_facts['date_time']['iso8601_basic_short']` and source regression forbids old syntax. Do not suppress warning instead of correcting it.

**Autonomous implementation:** `ansible/linkstack-transfer-isolated-data-restore.yml` and accompanying tests extend `tools/linkstack-archive-verify.py` to validate an imported offline rootless volume. Separate default-off `sanctum_linkstack_offhost_transfer_approved=true` and `sanctum_linkstack_isolated_volume_restore_approved=true`. First Kvar play checks the exact SHA, size, owner and private mode; second Kvin play uses strict-batch OpenSSH `scp` over Kvar's actual management port **10022**, validates exact received tar checksum & SQLite, no-clobber publishes Kvin private tar, creates **only** isolated `sanctum-linkstack-restore-test-20261112t105926`, imports it via Podman volume import, and checks restored `.env` and SQLite integrity. No live applications, image pulls, DNS, firewall or proxy changes; rootless Kvar original remains untouched. **Full source tests and Ansible syntax CI [#43268592944 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43268592944)**. Only *source* and safe application-data import are qualified, not the actual native transfer or LinkStack running on Kvin. [Authoritative runbook](docs/runbooks/kvar-survivor-consistent-backup-plan.md).

**NEXT ONE NATIVE OPERATOR ACTION**, on Kvin with opt-in to copy a credential-bearing tar by SSH and create an isolated rootless restore test volume (no service interruption):
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-transfer-isolated-data-restore.yml \
  -e sanctum_linkstack_offhost_transfer_approved=true \
  -e sanctum_linkstack_isolated_volume_restore_approved=true
```
**Full output is welcome**, not only selected reports. In success report exact task `Report bounded Kvar-to-Kvin LinkStack archive transfer and isolated data restoration` plus Kvar/Kvin PLAY RECAP. Any failed task is enough. If Kvin's direct SSH trust to `kvar.outer.sanctum:10022` is unavailable, fail without trying other paths or leaking content; do not disable host-key verification. After native copy+isolated volume integrity, qualify a pinned aarch64 LinkStack image, actual restored app content and admin, and separately gated YXORP backend cutover. Independently durable recovery backup still missing.

## CURRENT — November 12: backup readiness PASSED; LinkStack consistent snapshot source CI GREEN; LIVE LinkStack interruption requires operator

**New native operator evidence:** `ansible/kvar-survivor-backup-readiness.yml` completed read-only. `kvar.outer.sanctum: ok=8 changed=0 failed=0`, `kvin.outer.sanctum: ok=4 changed=0 failed=0`. Both Kvar reports `status:observed`; source volume filesystem available bytes LinkStack **441302228992**, Pi-hole **441302208512**. Kvin home staging **916098523136** and rootful store **916098523136** free bytes; `home_staging_headroom_established:true`, `recovery_destination_independence_accepted:false`. Both Podman auto-update timers loaded/enabled/active. LinkStack Quadlet `AutoUpdate=registry`; Pi-hole direct policy unspecified but an additional auto-update label is present. Pi-hole's earlier image-ID change may be related, **causation still unproven**. No app interrupted, source data exported, backups created, or production altered. The three task titles were confusing to Nova; **full play output is accepted**, do not request trimmed or reformatted output.

**Autonomous implementation:** Services now has `tools/linkstack-archive-verify.py`, `ansible/linkstack-consistent-backup.yml`, and `tests/test_linkstack_consistent_backup.py`, qualified by [full Services CI #43263995752 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43263995752). This is a **one-service-at-a-time, default-off real backup**, not a read-only probe: on Kvar rootless `wdc2`, require explicit approval and exact running LinkStack image ID `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65`, rootless Quadlet, single `linkstack:/htdocs` volume and TCP8081 mapping, then reserve a new 0600 private file and briefly stop only `linkstack.service` in a block with guaranteed `always` restart. It checks original active state, image ID/mount/port continuity and HTTP after restart, validates the private archive's safe paths and SQLite integrity, then no-clobber-promotes the retained Kvar-local tar. **No off-host copy, isolated restore, Kvin app install, Pi-hole/NPM, proxy or DNS changes are performed.** Retain partial on failure, preserve old Kvar for rollback.

**NEXT SINGLE OPERATOR ACTION on Kvin**, only if Nova accepts a temporary LinkStack interruption:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-consistent-backup.yml \
  -e sanctum_linkstack_consistent_backup_approved=true
```
Return **one** task's `msg`: `Report bounded consistent LinkStack source-backup acceptance`, and the Kvar `PLAY RECAP`, or the failed task. Full output is fine, no secrets. [Source-controlled transaction runbook](docs/runbooks/kvar-survivor-consistent-backup-plan.md). This is the actual host/approval blocker; do not claim archive exists before native result. After success continue private archive transfer to Kvin and hash verification, isolated restore into **new** volume and real LinkStack browser acceptance. Pi-hole backup with both volumes is a later separately approved transaction. Kvar NPM must stay active throughout.

## CURRENT — November 12: native three-volume preflight accepted; source-qualified backup readiness next

**Native Kvar result:** Nova supplied the full four-report execution of `ansible/kvar-survivors-source.yml`: `kvar.outer.sanctum ok=14 changed=0 unreachable=0 failed=0 skipped=0`. LinkStack rootless volume `linkstack:/htdocs`: 10,523 regular files / 1,827 dirs / **84,805,553 bytes**, known `.env` and `database/database.sqlite` markers. Pi-hole rootful volume `systemd-pihole_etc-pihole:/etc/pihole`: 56 files / six dirs / **1,310,387,005 bytes**, `pihole.toml`, `gravity.db`, `pihole-FTL.db` markers. Pi-hole second `systemd-pihole_etc-dnsmasq:/etc/dnsmasq.d` volume empty but still mounted. No symlinks or special files found; no contents read. Total regular bytes **1,395,192,558** (~1.30 GiB), not backup size or tested consistency. All volume scans **observed**, **no backup/restore accepted**.

**Image result:** Local image-list fallback matched the exact running image ID in both privilege namespaces and returned two repository digest strings per service; `pullable_digest_known:true` means the source lists digests, *not* validated registry access/ARM64. Both image reports `status:partial` because platform was unverified. Original `podman image inspect` attempts returned `command_unavailable` by ID and tag. Root cause likely source Go template typo: `IMAGE_FORMAT` used `.Id`, but Podman's documented field is `.ID`; repaired and CI regression added. New native proof is pending, no speculative image pin.

**Potential drift:** Pi-hole image changed from old `edb7f703649f4b6ab8b14f28d12f15e8cbe1c50a2092458e9b640bd6bc6fe59e` to currently observed `64c81b3c8132f3e7ae56925a1668d2cfa5a53c509c43b4c1cc71591e0f42c3d8`. Cause of container image change **not established**; do not claim Podman auto-update or other cause until read-only update-owner evidence. LinkStack ID remained `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65`.

**Autonomous work completed:** Services `tools/observe-survivor-backup-readiness.py` and `ansible/kvar-survivor-backup-readiness.yml` are a new distinct **read-only** probe of Kvar's two Quadlet `AutoUpdate`/`Pull` policies and `podman-auto-update.timer` states, exact named-volume filesystem headroom, and Kvin home/archive plus rootful-store free-space. The installed Quadlet may contain secrets, so raw content is read privately but **never emitted**. Statuses may be `partial`/unknown. No duplicate volume tree scan, stop, app data export, image pull, DNS/firewall/route changes. Full [Services source CI #43248203417 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43248203417), including proper documented image-inspect `.ID` regression, source/negative tests, and Ansible syntax. Detailed staged plan: [docs/runbooks/kvar-survivor-consistent-backup-plan.md](docs/runbooks/kvar-survivor-consistent-backup-plan.md). Previous three-volume inventory remains accepted and must not be re-run.

**NEXT ONE NATIVE OPERATOR ACTION on Kvin:**
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kvar-survivor-backup-readiness.yml
```
Return the **three bounded report `msg` dictionaries** titled `Report Kvar rootless LinkStack backup readiness`, `Report Kvar rootful Pi-hole backup readiness`, and `Report Kvin backup receiver and restore space`, plus the Kvar and Kvin PLAY RECAP rows (or failed task). Then Services qualifies actual source-controlled quiesced volume exports and Kvin isolated restores behind a *new separate explicit approval*. Kvar NPM and both live applications stay operating. This command is the current host-access blocker; no operation should be invented on the host by chat.

## November 11 — second native image probe receipt, and bounded volume preflight prepared

Nova reran `ansible/kvar-survivors-source.yml` from Kvin on Kvar: **`ok=8 changed=0 unreachable=0 failed=0`**. Both original services remain running; their image IDs, port maps, Quadlet sources and named persistent volumes match the first observation. Image inspection by **running image ID AND local `latest` name** failed for **both rootless LinkStack and rootful Pi-hole**, returning `image_probe.attempts[0/1].status: command_unavailable`. `pullable_digest_known:false` for both. This categorization means the subprocess returned nonzero or an unavailable result; it **does not prove either image is absent from the local store**. Do not select an image by the mutable `latest` name or guess a digest.

**Follow-up source (no host mutation yet):** The Services tool first retains the safe exact-ID image-inspect attempts. When those cannot establish the image, it separately queries only the local `podman images --no-trunc --format json` listing, selecting **solely the exact immutable image ID of the running container**. It never emits other images or repository labels; a manifest digest from a listing is only a *candidate*, not proof of a Kvin-pullable registry reference. The observer remains `partial` unless sufficient platform + pullable repo digest metadata exists.

The same single Kvar read-only play now includes `tools/observe-kvar-survivor-volumes.py`: it inspects the three named volumes in their correct Podman privilege namespaces, **without reading any volume file contents**. It reports bounded file counts, regular file bytes, symlink counts and mere existence of known file markers: LinkStack `.env` and `database/database.sqlite`, Pi-hole `pihole.toml`, `gravity.db`, `pihole-FTL.db`. Paths and secret contents are not returned. Both observations remain metadata-only; neither exports files, interrupts the apps nor creates a backup.

**Why those markers:** LinkStack's [official container persistence documentation](https://github.com/LinkStackOrg/linkstack-docker#persistent-storage) identifies `/htdocs` as its critical persistent state, including SQLite database and settings. Pi-hole's [container documentation](https://docs.pi-hole.net/docker/) preserves `/etc/pihole`; `/etc/dnsmasq.d` remains a separately mounted legacy volume on this exact Kvar instance. Pi-hole version and configuration semantics must be qualified, not inferred from `latest`.

**Next after CI accepts the new tests:** Run **the same single** `ansible/kvar-survivors-source.yml` from Kvin. This time it produces **four** bounded reports (two image/backing and two volume preflight) plus one Kvar PLAY RECAP. Then plan an explicitly authorized, short quiescence and consistent complete-volume export with off-host retention and isolated restore; do not confuse metadata presence with a backup. Keep Kvar and its NPM fallback intact.

## CURRENT — November 11: Mace Firefox Kuma WebSocket upgrade 101 ACCEPTED; Kuma initial production client gate CLOSED

**Actual Mace Firefox evidence:** Nova supplied the Firefox DevTools Network **WS** screenshot for `kuma.nexus.sanctum`, showing `GET /socket.io/?EIO=4&transport=websocket&sid=...` with **HTTP 101 Switching Protocols**. This is the actual browser's successful Engine.IO/Socket.IO WebSocket upgrade through Kvin production YXORP. Earlier on the same production named route, Mace resolver returned `192.168.0.192`, the existing `sanctum-admin` application login succeeded, and the `Wicket Ollama` dashboard monitor visibly reported **Up / 100% uptime**.

**Acceptance:** Kuma **initial named-client production browser/login/meaningful monitor/WebSocket upgrade** gate is accepted. The 101 directly proves protocol upgrade, not indefinite session stability or every Socket.IO message; no gratuitous further probe necessary to accept this bounded gate. Continue later with other Nexus application name/session checks, full application estate recovery, and Maintenance-main reconciliation of source DNS aliases (old broad-renumber source still assumes Kvar). **Do not retire Kvar NPM.** Existing separately prepared DNS rollback candidate remains available for separately gated use if genuine regression appears. Do not copy a screenshot's Socket.IO session-id/query data into issue notes.

## CURRENT — November 11: Mace Kuma dashboard monitor UP at 100%; live browser Socket.IO still to verify

**New user-visible browser acceptance:** From the normal Mace Firefox session already authenticated through Kvin YXORP at `http://kuma.nexus.sanctum`, Nova confirms the **`Wicket Ollama` monitor is visible and reports Up with 100% uptime**. Combined with Mace name resolution to `192.168.0.192` and the successful `sanctum-admin` login, this accepts **named-client DNS, real proxy/browser authentication, and meaningful monitor state being displayed**. The 100% displayed figure is the app's uptime metric, **not proof that the Socket.IO WebSocket upgrade occurred or stays connected**; require an observed client-side WebSocket exchange for that specific remaining gate. Preserve Kvar NPM as rollback; no source or live infrastructure mutation requested by this browser observation.

**Next one browser-only observation:** In Mace Firefox DevTools Network, inspect WebSocket requests during a Kuma page reload for `socket.io` traffic/101 Switching Protocols and continuing frames (without sharing tokens, frames, or credentials). If Socket.IO remains polling or no 101 appears, classify separately rather than assuming Nginx failure. Then independently check other named application routes and reconcile Maintenance main with the successful DNS promotion.

## Active execution plan — Wednesday, November 11, 2026

## CURRENT — November 11: Kvar survivor image probe classified; corrected Services CI GREEN, native rerun required

**Read-only first Kvar observation accepted** (both active Quadlets, persistent volumes, exposed ports, and exact running image IDs), recap `ok=8 changed=0 failed=0`. Both original `status:partial` results were specific to unproven image-platform and registry digests, not container availability.

**Correction tested:** Services `tools/observe-kvar-survivors.py` now reports `image_probe.attempts` with bounded status categories instead of ambiguous missing fields. It first tries the immutable running image ID in the correct Podman user namespace, optionally queries the existing local name/tag **only if the exact image ID matches** (rejects unexpected local `latest` drift), and reports `pullable_digest_known` separately. Missing digest remains `partial`, without guessing an immutable image reference or requesting a pull. The full Services source and recovery workflow [#43128132860 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43128132860) including new negative tests. No app, data, NPM, firewall or DNS changes.

**Single next host gate, on Kvin** after `git pull`:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kvar-survivors-source.yml
```
Ask for the two `Report bounded ... backing discovery` `msg` dictionaries and aggregate Kvar `PLAY RECAP`. Prefer `image_probe`, `repo_digests`, `image_platform`, and `status` to decide the next actual image qualification step. The previous first-run volume and port evidence need not be disputed or repeated in the report. Keep all survivors running; Kvar NPM intact.

## November 11 native Kvar receipt — both live survivors, image identity metadata incomplete

Nova ran `ansible/kvar-survivors-source.yml` on Kvin against Kvar, **`ok=8 changed=0 failed=0 unreachable=0`**. Each named service was confirmed **running**, Quadlet `loaded/active/generated`, with source files on Kvar. No application state, passwords or volume contents were read and no host/app configuration was changed.

| Service / account | Running container image reference and observed image ID | Writable volumes | Kvar published ports |
|---|---|---|---|
| Rootless `linkstack`, `wdc2` | `docker.io/linkstackorg/linkstack:latest`; `53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65` | `linkstack` → `/htdocs` | TCP 8081 → 80 |
| Rootful `pihole`, `root` | `docker.io/pihole/pihole:latest`; `edb7f703649f4b6ab8b14f28d12f15e8cbe1c50a2092458e9b640bd6bc6fe59e` | `systemd-pihole_etc-pihole` → `/etc/pihole`, `systemd-pihole_etc-dnsmasq` → `/etc/dnsmasq.d` | TCP/UDP 53 → 53 and TCP 82 → 80 |

Both bounded results had `status: partial`, although `service_unit.status: observed`. The reason is the **additional local image inspection did not yield accepted `image_platform` and `repo_digests`**, not that either container is unavailable. `latest` is mutable and the displayed container image ID is **not** proof of a Kvin-pullable immutable reference. No image pull, service restart, backup, data movement, DNS or proxy change is authorized by this observation.

**Follow-up source correction:** `tools/observe-kvar-survivors.py` now explicitly reports only sanitized image-inspection outcome categories. It first queries the exact observed container image ID; if unavailable, it tries the existing local image tag, **accepting that result only if its image ID equals the running container's ID**. A newer local `latest` tag must not be used to reconstruct the wrong image. A missing repository digest remains `partial`. The updated source tests cover all of these failure modes. Once CI is green, the next read-only native rerun can report a specific image-probe result rather than an unexplained `partial`. Do not re-run any broad retirement inventory.

## CURRENT — November 11: Kvar LinkStack + Pi-hole read-only recovery-source observer CI GREEN; native inputs next

**Next single Kvin operator action:** The existing Maintenance inventory already established rootless Kvar LinkStack's persistent `linkstack` volume at `/htdocs` and rootful Pi-hole's two config volumes. No need to repeat broad inventory. Services source now provides `ansible/kvar-survivors-source.yml` and `tools/observe-kvar-survivors.py` to inspect **only** the two wanted services in the proper distinct privilege namespaces on old Kvar. It reports bounded selected image reference/id/digest, ports, mount destination/volume names and safe service/Quadlet source status, suppressing raw inspection, environment, content and credentials. Both plays are read-only and have no rollout, backup, data access or app mutation. Source tests and full Services CI [#43126902608 **PASSED**](https://github.com/wdcallahan/sanctum-services/actions/runs/43126902608); **no native Kvar observation yet**.

One command **on Kvin**, using the current Services inventory and logged-in Navigator:
```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/kvar-survivors-source.yml
```
Return the single aggregate Kvar **PLAY RECAP** row and bounded `Report bounded LinkStack image and backing discovery` and `Report bounded Pi-hole image and backing discovery` `msg` dictionaries (or failed task). `partial` means input unknown, not failure to report. Read [docs/runbooks/kvar-survivor-recovery-inputs.md](docs/runbooks/kvar-survivor-recovery-inputs.md). This is a **real host evidence boundary**; do not choose images or design a live restore from speculation. Kvar NPM and all apps remain running. After native evidence, prepare owned consistent backups, isolated Kvin restores and actual client acceptance separately.

## CURRENT — November 11: Mace named Kuma authentication accepted; browser monitor/Socket.IO next

Nova confirmed from Mace that `kuma.nexus.sanctum` resolves to **`192.168.0.192`**, Firefox loaded its live login, and the existing **`sanctum-admin`** user successfully authenticated through Kvin YXORP. Mark actual Mace client resolution and browser login accepted. The visible monitor state, sustained browser Socket.IO/WebSocket updates, and other apps' named-client behavior are **not yet evidenced**. Keep Kvar fallback. The previous instructions omitted the browser username and blurred the distinction between the saved Kuma login password and unrelated Vault unlock key; corrected operational docs, no account rotation needed.

## CURRENT — November 11: live guarded Peanut six-Nexus DNS publication ACCEPTED; named client acceptance NEXT

**New native operator receipt (23:32Z):** Nova ran the previously accepted exact Maintenance release packet `artifacts/yxorp-dns-release-0858020` with `sanctum_publish_dns_zones=true`, `sanctum_yxorp_dns_publish_approved=true`, target `peanut.arcane.sanctum`, **without `--check`**. Report `Report bounded proxy DNS candidate scope and publication gate` returned **`check_mode:false`**, **`published_change_accepted:true`**, `candidate_serial:2026111101`, prior served forward/reverse SOA `2026101904`, both zone-file changes true, six proxy aliases directed to Kvin **`192.168.0.192`**, `old_npm_administration_address_retained:true`, `db_and_nonproxy_addresses_retained:true`, `reverse_ptr_records_unchanged_in_source:true`, `production_proxy_or_app_changed:false`, `real_named_client_sessions_and_websocket_accepted:false`. Actual play **`ok=18 changed=3 unreachable=0 failed=0 skipped=0`**, Navigator exit0, run completed. Private logged transcript: `artifacts/transcripts/publish-yxorp-nexus-dns-2026-11-11T23-32-01Z.log` and matching `.json`.

**Publication is ACCEPTED** on authoritative Peanut, based on the full play and publisher's guarded real authoritative postchecks; do not claim browser, login/session or Socket.IO from it. Kvar NPM remains running, old admin DNS preserved for rollback. The separate Maintenance rollback source candidate at `f7461ee84d13439e92e07037858b6828840a94d6` / `yxorp-dns-rollback-20261111`, desired SOA `2026111102`, has passing source CI but has NOT been natively previewed or executed.

**Next operational gate:** verify normal client resolver answers for relevant named Nexus routes, real browser login/session (particularly Kuma), and Kuma Socket.IO/WebSocket behavior. If client acceptance fails, classify DNS cache/client route/application issue; keep Kvar NPM intact and use separately previewed/authorized higher-serial rollback only if required. After client acceptance, reconcile the scoped DNS change with Maintenance main's older, incompatible broad renumber assumptions. Do not treat old YAML main source as safe to republish yet.

**Commissioned outcome, SS-ROOT (in progress):** Replace Kvar's wanted
services with reproducible, usable, recoverable services on Kvin, backed
by an owned plain-Nginx YXORP and correct named client access; preserve
Kvar production until separate acceptance and approved cutover. Peanut's
future standby/failover is a related recovery outcome, not an excuse
to call a single Kvin proxy install complete. The operational
[completion standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md)
applies: mechanism, state, repeatability, client consumption, backup/restore,
operations, reversal and discovery all need appropriate evidence.

**Planning doctrine from Nova, November 10:** NO arbitrary task time limits.
Work continues until the required outcome is correctly evidenced, or
there is a *specific* genuine blocker, safety/permission boundary or a
more valuable independent assignment. A short positive probe never
magically proves full application acceptance. Conversely, no extra
diagnostics simply because more could be collected. Every investigation
must identify the concrete decision/repair its result enables.
Pixel owns source, tests, CI, issue/roadmap reconciliation and
technical choices within authorized scope. Nova participates in
meaningful learning and executes exact native commands when source
tests cannot substitute for actual Kvin/Kvar observations. Do not
make Nova relay trivial, sequential probes or repeatedly redo
already accepted tests. Do not hide private-network IPs when they
are useful operational evidence; keep passwords, tokens, cookies and
unnecessary raw content private.

### SS-YX — Finish a faithful and operable YXORP

**Earlier November 11 — dedicated Maintenance DNS native preview ACCEPTED:**
Exact scoped `yxorp-dns-release-20261111`
candidate commit
`0858020065777070bf6e9a36b0d0f3056f7f5334`
previewed on Peanut with owner logged Navigator,
`--check --diff`, `ok=10 changed=1 failed=0 skipped=8`.
Actual served forward and reverse SOA
both **`2026101904`**;
candidate `2026111101` is newer.
Both forward and reverse zone files
would change, with source-aligned
six proxy aliases to
`192.168.0.192`, source PTR,
Kvar old-NPM admin, DB and nonproxy
records unchanged. No live DNS
mutation. The full installed-file
diff is retained in the private
logged preview; bounded message
alone cannot prove there were no
other installed-file differences.
**Next:** same exact Maintenance
candidate packet, explicit LIVE
`sanctum_yxorp_dns_publish_approved=true`
(without check mode), then real
named-client DNS answers and
authenticated browser/Socket.IO
acceptance. Kvar NPM retained
for fallback. After native acceptance,
repair Maintenance main and the
older core-renumber alias projection
to preserve the live migration.

**November 11 — Peanut independent Kvin HTTP80 ACCEPTED; six-name Nexus DNS release source candidate ready:**
Native Peanut `ansible/yxorp-kvin-peer-http.yml`
`ok=5 changed=0 failed=0`:
Kvin `192.168.0.192:80` returned
Kuma HTTP302 and Yarn HTTP200.
The alternate `192.168.1.192:80`
returned only `transport_error` for
both. Peanut really resolves
`kvin.outer.sanctum` to
`192.168.0.192`. This closes
independent peer HTTP route and selects
the observed DNS target, **not**
named Nexus/browser/Socket.IO acceptance.

Maintenance owns a **separate source
branch**, `yxorp-dns-release-20261111`,
exact commit `0858020065777070bf6e9a36b0d0f3056f7f5334`,
rather than editing currently active
main controller/core-renumber candidate.
It changes exactly the five explicit
`dir/joule/kuma/pihole/search.nexus`
records and `*.nexus` to Kvin
`192.168.0.192`, proposes new
SOA `2026111101`, preserves
`yxorp.nexus` old Kvar NPM, DB,
all other A and PTR. Uses original
Maintenance BIND validated/backup/
serial-protected zone publisher with
separately gated preview/live modes.
[Dedicated source CI #43115349084
PASSED](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43115349084).
Native owner **preview**, LIVE publication,
real named client and merge to
Maintenance main are **not yet accepted**.
Do not conflate this with broad old
core-renumber candidate assumptions.

**November 11 — owner Kvin TCP80 policy repeat has EMPTY runtime/permanent diff:**
Nova's supplied safe task report
`check_mode:false` and
`would_change:false`,
`public`/`eth0`, with no
runtime or permanent add_ports or
remove_rich_rules. The separate
full PLAY RECAP from this repeat
wasn't supplied; don't invent one.
Native initial live TCP80 apply was
already `ok=28 changed=1 failed=0`
with full PostgreSQL/fwall preservation.

**Next source-owned LAN observer:**
A new read-only Services playbook
`ansible/yxorp-kvin-peer-http.yml`
targets **Peanut**, not Kvin; queries
production Kvin via both
`192.168.0.192` and
`192.168.1.192`, with Kuma and
Yarn Host headers, and reports actual
Kvin FQDN DNS answer on Peanut.
The two address contracts conflict:
Maintenance zone maps `kvin.outer`
to `192.168.0.192`, but Peanut
health checks expect
`192.168.1.192`. Do not change
the six Nexus DNS aliases to an
assumed address. Confirm actual
Peanut reachability and use owner
serial/zone publication afterward.
No native Peer test or DNS
publication accepted yet.

**November 11 — live owner TCP80 Kvin firewall APPLY ACCEPTED:**
Maintenance's reviewed revision
`3ba9523befe229af2262194a615c3bc35da5aa01`
from the unchanged staged source packet
completed native `ok=28 changed=1 failed=0`,
`check_mode:false`, navigator exit0.
Runtime and permanent `public`/`eth0`
both planned only `add_ports:['80/tcp']`,
with `remove_rich_rules:[]`. Post-state
firewall and PostgreSQL boundary checks
passed. This is the genuine mutation,
not the preceding check-mode prediction.
Next: **one unchanged repeat** of the
same pinned owner play, then independent
LAN Kvin TCP80 reachability before
Maintenance authoritative Nexus DNS
publication (six names/wildcard and new
served serial). Kvar NPM remains live.
No DNS or named browser/session/WebSocket
cutover acceptance yet.

**November 11 — production listener native ACCEPTED unchanged:**
The operator's repeat of only
`ansible/yxorp.yml` after a transient
first-run Yarn timeout returned
**`ok=31 changed=0 failed=0 skipped=1`**.
Bounded report confirmed 8 enabled
production routes through
`sanctum-yxorp.service`,
Kuma proxy HTTP302 to
Kvin `127.0.0.1:13001`,
Yarn proxy HTTP200,
`local_production_listener_accepted:true`;
Kvar NPM, DNS and firewall unchanged.
**Local production listener gate closed.**
Stage and Yarn probes do not need repetition.
**Next:** Maintenance's exact source
`3ba9523befe229af2262194a615c3bc35da5aa01`
with dedicated CI #43100611079 green
must run native `--check --diff`
for TCP80 on Kvin via its established
staged-source logged runner; then
approved apply/repeat and peer HTTP.
Only then modify six named Nexus
DNS entries and wildcard under
Maintenance DNS owner with fresh serial.
No live DNS change yet; client/session/
WebSocket gates still open.

**November 11 — production Yarn timeout NOT REPRODUCED, now responds correctly:**
The native read-only diagnostic
`ansible/yxorp-production-yarn-diagnose.yml`
completed **`ok=7 changed=0 failed=0`**,
classification
`current_production_yarn_proxy_http_path_answers`.
At this new observation, direct
`192.168.1.110` for both Yarn Hosts,
named `yarn.inner.sanctum` origin,
production `127.0.0.1:80` for
both `yarn.nexus` and `yarn.inner`
all returned **HTTP200**. Original
Yarn DNS = `192.168.1.110` and
production Kuma control = **302**.
No config, Kvar, DNS or firewall mutation.
The first production play's post-task
timeout remains a historical transient
failure; don't “fix” route/source without
evidence. Repeat **only** production
`ansible/yxorp.yml` once for a full
zero-change local listener acceptance.
No new staging operation necessary.
Maintenance's firewall CI is green;
neither TCP80 nor DNS changes are
live yet. Kvar remains production.

**November 11 — first Kvin production native attempt FAILED on Yarn:**
The approved stage removal plus
production deployment chain progressed
into the new production post-tasks.
`ansible/yxorp.yml` native
`ok=29 changed=5 failed=1 skipped=1`;
the Kvin Kuma frontend check passed
but the next test for
`Host: yarn.nexus.sanctum` at
`http://127.0.0.1:80/` timed out
(status -1). **Do not claim production
accepted or move DNS.** Kvar NPM
still serves normal names and is
available for rollback. The earlier
eight-route **stage** acceptance remains
valid *for that vantage point and time*;
the new production Yarn behavior needs
fresh explanation. Source now contains
a specifically read-only production
Yarn origin-by-IP/name and both-new/
old-proxy-Host comparison. Run once
after targeted CI passes, then select
a concrete correction. No firewall,
DNS or Kvar source changed.

**Longstanding hairpin/Kuma rule reaffirmed:**
Old rootless Podman/pasta Kuma couldn't
monitor own-host published containers,
even while other-host monitoring
worked; `Network=host` was an
explicit workaround, not an upstream
bugfix. Two independent bears
cross-monitoring each other is the
established design; eventual independent
peers are Kvin and Peanut (Maintenance
`kuma_peer`), not permanently Kvar.

**November 11 — Production promotion SOURCE QUALIFIED, awaiting native owner acceptance:**
Nova permits an immediate pragmatic Kvar->Kvin
proxy cutover, accepting even substantial
proxy downtime. All 8 approved local stage
hostnames remain accounted for.
`ansible/yxorp.yml` promotes eight source
routes, retargeting only Kuma to Kvin's
`127.0.0.1:13001`, and proves local
Yarn+Kuma forwarding after stage removal.
`ansible/yxorp-production-remove.yml`
provides scoped reversal. **[Full Services
CI #43098976225 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43098976225).**
No native production promotion yet.
Maintenance's supported Kvin firewall
source now adds TCP80 (commit
`873c9c6`) and [its own full source CI
#43100611079 PASSED](https://github.com/wdcallahan/sanctum-maintenance/actions/runs/43100611079);
no live firewall apply yet.
The separate Maintenance cutover-candidate
CI currently reports an unrelated prior
Kvin DNS baseline mismatch, which must
not be disguised as a TCP80 policy failure.
The owner-managed DNS source still
points the five explicit relevant Nexus
aliases plus wildcard at Kvar.
[One supported release/rollback
sequence](runbooks/yxorp-production-cutover.md)
stages the firewall, removes old
Kvin YXORP staging, installs proper
production Quadlet, then publishes
DNS and tests real clients. Kvar NPM
stays for rollback.

- **SS-YX-1 — [accepted, limited] Seven Kvin stage virtual hosts.**
  `yarn.nexus`, `square.nexus`, `joule.nexus`,
  `search.nexus`, `dir.nexus`, `kuma.nexus`, and
  `pihole.nexus` have each passed the initial **anonymous local HTTP**
  checks. Their exact approvals were used to reconcile the **rootful
  Podman/Quadlet Nginx** on Kvin HTTP:80; the last Pi-hole
  native reconcile was `ok=46 changed=3 failed=0`, and its
  raw-wire `/` and `/admin/` probe was
  `ok=4 changed=0 failed=0`. The old Kuma redirect
  mismatch was **an Ansible URI normalization artifact**, not
  a real Location difference. This evidence is banked: do
  NOT re-run seven individual canaries merely for reassurance.
  It does **not** qualify browser sessions, WebSockets,
  app state, LAN firewall reachability, production or cutover.

- **SS-YX-2 — [accepted: native Kvin stage, bounded] Eighth original NPM vhost.**
  Nova's corrected native run of
  `ansible/yxorp-kvin-stage-yarn-inner-probe.yml`
  returned **`ok=8 changed=0 failed=0`** and
  **all assertions passed**. For original NPM
  `yarn.inner.sanctum` → `192.168.1.110:80`,
  direct Yarn and Kvin stage both returned
  **HTTP200**, matching MIME/status and an
  **identical complete 349-byte body**. The
  distinct new `yarn.nexus.sanctum` stage
  returned 200. An unknown Host was refused.
  Published and container-mounted Nginx
  configurations matched exactly; both Yarn
  vhosts and original backend directive were
  present exactly once. No redirect was
  returned, so relative Location equality
  was correctly **not comparable**, not
  failed. The earlier double-escaped observer
  regex defect was corrected and independently
  regression-tested in **[full passing CI
  #43053056244](https://github.com/wdcallahan/sanctum-services/actions/runs/43053056244)**.
  Combined with already accepted SS-YX-1,
  **all eight intended application vhosts have
  passed the initial actual Kvin-local HTTP
  acceptance**. The Kvar legacy NPM → Yarn
  timeout remains an incumbent Kvar-side
  transport issue, not an eighth-route
  failure and not a reason to reopen Yarn
  client attribution or DNS policy.
  **Owner:** Services. **Exit accepted
  only for initial HTTP/config mechanism.**
  Not app/session/LAN/production.

- **SS-YX-3 — [reviewed: proxy source mechanism covered; functional consumers remain open] Material NPM behavior.**
  Reused the [Nov 9 real NPM generated-host
  inspection](review/2026-11-09-yxorp-behavior-observation.md)
  and [default-upstream comparison](review/2026-11-09-yxorp-default-route-comparison.md)
  rather than collecting redundant logs.
  The seven incumbent application hosts had
  one ordinary location each, no non-default
  custom locations, and no nonempty global
  custom snippets. Default upstream mappings
  are preserved for all seven originals,
  plus the explicitly requested new
  `yarn.nexus.sanctum` proxy.
  The old NPM **administration UI** is
  deliberately excluded from the new
  plain-Nginx design. Prism's observed
  legacy HTTPS certificate/listener is
  deliberately not recreated under the
  already accepted private-HTTP policy.
  The template and source tests cover
  relevant Host and forwarding headers,
  WebSocket Upgrade, original raw relative
  redirects, default-deny, actual Nginx
  syntax and synthetic backend isolation.
  The source-managed rootful Quadlet role
  validates candidate config before
  publishing, recovers stale single-file
  mounts and independently checks live
  mounted equality. Config change/reload
  and removal have automated tests;
  a new eight-vhost no-change native
  repeat has not yet been separately
  logged and can be verified during the
  next meaningful managed change.
  **This review identifies no additional
  isolated proxy-source defect requiring
  another standalone NPM investigation.**
  Shared include semantics not independently
  expanded, actual application authentication,
  browser/WebSocket behavior and real LAN
  named access are **not claimed fully
  equivalent**: their necessary observable
  outcomes remain required under the
  relevant **SS-APPS** and **SS-PUB** gates.
  Do not promote 8/8 local HTTP into
  complete service or production
  acceptance. **Owner:** Services.

### SS-APPS — Replace the services still depending on Kvar

- **SS-APPS-1 — [open; first application build after YXORP
  route fidelity] Uptime Kuma clean retained Kvin instance.**
  Operator-approved earlier: old Kvar Kuma was a
  proof of concept; preserving its entire historical
  SQLite database is **not required**. Reuse
  `data/kuma-monitors.yml` and
  `docs/runbooks/kuma-monitoring.md`; Project Joule's
  **Wicket Ollama** monitor must actually display
  **Up** at `http://wicket.arcane.sanctum:11435/healthz`.
  Build an ordinary, source-managed ARM64 Kvin install,
  version-appropriate stable monitor reconciliation,
  persistent state, backup/restore, upgrades,
  status and removal. Avoid duplicate notifications
  while an old/test instance exists. Then test
  actual login/monitor visibility, restart and
  independent restore before changing the
  `kuma.nexus` upstream from Kvar to Kvin.
  **Exit:** The wanted monitors live on Kvin, the
  Wicket monitor is Up, repeat converges,
  and recovered state is demonstrably usable.
  **Owners:** Services for Kuma; Project Joule for
  the monitored endpoint. This is a practical
  first migration because a clean install is
  already authorized; no speculative old-DB
  recovery task is needed.

  **November 11 — Kuma consistent backup/isolated restore ACCEPTED:**
  Native explicit one-shot recovery play
  `ok=49 changed=11 failed=0`.
  Kvin original user service restarted and
  HTTP/Vault auth verified; disposable
  network-none Kuma restored from private tar,
  SQLite integrity checked, and existing
  Vault login plus Wicket monitor verified.
  The test instance/volume were deleted
  without touching original data. Artifact:
  `sanctum-kuma-20261111t144137.tar`,
  290816 bytes, SHA-256
  `97f7fae21ed845f6e719352025166a155c6ede9489525f701dbaedaed6273648`.
  **Local backup+application restore accepted.**
  **Off-host archive and master Vault key recovery not accepted.**

  **November 11 — new proxy cutover authorized with downtime tolerance:**
  Nova says it is fine to switch YXORP live
  without waiting for an after-hours window,
  even if the proxy is down all day; his
  teaching does not depend on its uptime.
  Engineering still owns correct eight-route
  production promotion, stage TCP80 handoff,
  Maintenance-managed Kvin firewall & DNS,
  and retained Kvar fallback. Do not claim
  those components deployed until native
  acceptance. Wants two Kuma bears on
  Kvar/Kvin to monitor one another; no
  cross-Kuma monitor was configured yet.

  **Historical accepted actual monitoring:**
  Nova's native `ansible/kuma-monitors.yml` repeat
  completed **`ok=13 changed=0 failed=0`**,
  `action:unchanged`, `monitor_id:1`, persisted
  configuration and no subscriptions. Kuma's
  own last-hour heartbeat records contained **12
  beats**, most recent **Up** and **17 seconds
  old**; `actual_up_accepted:true`. Wicket is
  genuinely monitored by retained Kvin Kuma.
  No more isolated health probes needed.

  Next source-provisioned trial is a guarded
  **consistent volume backup**, brief Kuma stop
  with guaranteed restart, then an **isolated,
  offline restored Kuma** proving saved Vault
  authentication and Wicket monitor configuration.
  This is `ansible/kuma-backup-restore-trial.yml`
  documented at [Kuma recovery](runbooks/kuma-recovery.md),
  not yet natively executed. A private backup
  on Kvin is not independent recovery: off-host
  artifact and existing Vault key backups are
  still a required follow-up. No production
  proxy, DNS or firewall change is authorized.

  **Historical native initial monitor creation:**
  Nova's approved admin bootstrap repeat completed
  `ok=12 changed=0 failed=0`; idempotent
  login/account reconciliation is now banked.
  First native source-managed Wicket monitor
  reconcile completed `ok=11 changed=1 failed=0`,
  `action:created`, `monitor_id:1`,
  `configuration_persisted_and_verified:true`,
  `notifications_attached:false`. The monitor
  itself has been created and persisted on
  Kvin via Kuma 2.5.9 native Socket.IO.
  `actual_up_accepted:false` still means
  **not observed**, not Down. No Kvar,
  YXORP/DNS/firewall or production changes.

  Source now adds a read-only, authenticated
  `getMonitorBeats` observation to the same
  monitor playbook; after full CI, run it
  once more for no-op configuration and an
  actual recent heartbeat Up/Down/Pending
  report. Independent restore, lifecycle
  and named client acceptance remain open.

  **Historical source CI-qualified monitor reconciler:**
  Added `ansible/kuma-monitors.yml` and
  `tools/kuma-reconcile-monitors.js` after reviewing
  the exact upstream 2.5.9 Socket.IO monitor APIs.
  Explicit `kuma_monitors_approved=true` and
  exact Kvin, image, rootless user Quadlet and
  Vault guards limit writes to `data/kuma-monitors.yml`'s
  single wanted `Wicket Ollama` HTTP monitor.
  Reconcile by stable name; refuse duplicate names
  or preexisting attached notifications; verify
  persistence and report nonsecret metadata. Synthetic
  Socket.IO integration tests cover first create,
  no-op repeat, config edit and guarded failures.
  [Full CI #43082780801 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43082780801).
  **No native monitor operation, actual Up, or
  monitor-level repeat has happened.**
  Next operate the approved admin no-change repeat
  followed by first monitor reconcile using the
  one Kvin chain in [Kuma runbook](runbooks/kuma-monitoring.md).
  Production unchanged; remaining actual Up and
  independent restore gates are open.

  **Historical first native administrator acceptance:**
  Nova's native approved bootstrap finished **`ok=12 changed=1
  failed=0`**, with `administrator_created_this_run:true`
  and `administrator_login_verified:true`. The
  user-selected, existing Vault credential was loaded
  without generating or modifying a password,
  writing a separate secret to the host, or
  touching Kvar, YXORP, DNS or firewall.
  **The administrator first-run acceptance is closed.**
  A second unchanged bootstrap run must still
  prove `changed=0` with the same account login.
  Then source-manage the wanted `Wicket Ollama`
  2.5.9 Socket.IO monitor, prove actual Up,
  no duplicates/alerts, browser usage, restart
  and independent recovery. Do not prematurely
  retarget Kvar's live `kuma.nexus` route.

  **Historical approved Vault design and preparation:**
  Nova selected a single established Ansible Vault
  password file as the unlock authority for independently
  encrypted, per-service credentials, including Kuma.
  Existing `/home/wdc2/.config/sanctum-services/secrets/vault.key`
  and the already documented Nextcloud PostgreSQL
  encrypted file remain intact; never regenerate the key.
  Replaced random Kuma admin password generation
  and Kvin-local JSON with a protected, external
  `kuma-admin.vault.yml` defining
  `vault_kuma_admin_password`. The explicit
  one-time bootstrap keeps native Kuma 2.5.9
  Socket.IO setup/login and fails closed for
  unknown existing users.

  The EE is scoped to two explicitly mounted
  private files for secret-consuming runs; global
  vault defaults broke unrelated CI and were
  rejected. CI #43076965704 passed full
  nonsecret source checks. Administrator is
  **not natively created**; first operator
  action is the one-time nonclobbering
  [private Vault file creation](runbooks/vault-credentials.md),
  then the guarded admin bootstrap and a no-change
  repeat. Changing an encrypted variable alone
  is not sufficient for password rotation; explicit
  authenticated rotation remains separate work.
  No Kvar, YXORP, DNS or firewall change.

  **Historical SQLite and first administrator planning:**
  Nova's Kvin SQLite reconciliation finished `ok=9 changed=2
  failed=0`; the immediately repeated guarded Kuma run
  finished **`ok=9 changed=0 failed=0`**. The actual
  browser reached Kuma's `/setup-database` and
  `/setup` pages via SSH tunnel. These are verified
  application bootstrap-screen observations, not
  completed admin authentication or a useful monitor.

  User feedback correctly rejected hand-created admin
  state as the default automation strategy. Exact
  upstream Kuma **2.5.9** sources confirm first-user
  `needSetup`, `setup` and `login` Socket.IO events.
  Created separately opt-in
  `ansible/kuma-admin-bootstrap.yml`, guarded by
  `kuma_admin_bootstrap_approved=true`, with a
  0700 Kvin-local directory, random private 0600
  admin credential, native Socket.IO initialization,
  no-log processing and login verification. Repeat
  verifies the same account; an existing unauthorized
  user is not overwritten. [Source and Node protocol
  tests in CI #43072165068 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43072165068).
  **Admin bootstrap not yet run natively.**
  Next run the one approved bootstrap+repeat command
  in the [Kuma runbook](runbooks/kuma-monitoring.md).
  Plan an off-host backup of both the volume and
  private credential before claiming recovery.
  No Kvar or YXORP cutover.

  **Historical initial stage (accepted):**
  Nova's first approved `ansible/kuma.yml`
  completed `ok=10 changed=3 failed=0 skipped=1`
  and returned HTTP 302 at
  `http://127.0.0.1:13001/` with named
  `sanctum-kuma-data` volume and managed user
  Quadlet. This is accepted application-startup
  evidence, not administrator, actual monitor,
  restore or LAN/prod evidence. The incumbent
  Kvar Kuma and shared proxy/routes are unchanged.

  Immediately afterward, Services pinned the
  official Kuma v2 SQLite setting
  `UPTIME_KUMA_DB_TYPE=sqlite` in the Quadlet
  through `kuma_db_type`, with source contract
  and [CI #43065990976 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43065990976).
  That SQLite reconciliation and actual browser
  access have subsequently been observed, as
  recorded above. Administrator provisioning is
  now a separately authorized automated gate,
  not a manual browser instruction. Authenticated
  Wicket monitor reconciliation still requires
  actual Kuma 2.5.9-compatible testing.

  **Historical stage preparation (now accepted):**
  Nova's corrected Kvin run passed `ok=8 changed=0 failed=0
  skipped=1`, with actual Linux/ARM64 image inspection and
  disposable offline Node execution. No application or volume
  exists because of that image-only step. The tested 2.5.9
  digest is now pinned in `ansible/group_vars/kuma.yml`;
  staging still requires separate `kuma_stage_approved=true`
  authorization. The rootless Quadlet role uses its generator
  `[Install]` (not unsupported `systemctl enable`), and a new
  default-off, volume-preserving candidate reversal is source-owned.
  [Installation source CI #43064138846 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064138846);
  [reversal source CI #43064602595 passed](https://github.com/wdcallahan/sanctum-services/actions/runs/43064602595).
  That initial native app stage has now passed
  `ok=10 changed=3 failed=0` as noted above.
  Preserve useful evidence; do not repeat the
  image-only qualification or initial stage
  merely to retake its acceptance. Continue
  from the SQLite source reconciliation and
  actual administrator/monitor state.

  **Historical image qualification preparation (now superseded):**
  Existing `data/container-image-candidates.yml`
  records an explicit Linux/ARM64 Uptime Kuma
  2.5.9 digest marked **registry_only**.
  New `ansible/kuma-qualify-image.yml`
  requires exact Kvin aarch64, rootless
  execution, explicit image qualification
  opt-in and *no app-stage approval*. It
  checks/pulls the exact digest into the
  rootless image cache, validates actual
  image metadata and runs Node offline
  in a disposable read-only container.
  It creates **no service or volume**.
  [Source CI #43055414958 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43055414958).
  **November 11 native checkpoint:** Nova's first
  Kvin run pulled the exact image (`ok=5 changed=1 failed=1`)
  but stopped before disposable Node execution:
  the image `Id` assertion incorrectly required
  `sha256:`; Podman reports a bare 64-hex `Id`
  (the prefixed value is `Digest`). Linux/ARM64
  and singleton inspect predicates had passed.
  Corrected the playbook and added real-Ansible
  positive/negative metadata regression tests;
  [CI #43059304269 PASSED](https://github.com/wdcallahan/sanctum-services/actions/runs/43059304269).
  The corrected Kvin retry subsequently **passed**
  native ARM64 and Node runtime qualification as
  recorded above. That evidence is retained for
  chronology, not an instruction to rerun qualification.

- **SS-APPS-2 — [open] LinkStack with actual directory
  data.** The existing rootless Kvar
  `linkstack` volume is mounted at `/htdocs`.
  Preserve the *live* rootless instance; do
  not adopt the historical failed rootful
  duplicate. Define a durable, verified
  backup of its actual pages, configuration,
  assets and secrets, implement ordinary
  Kvin rootless Quadlet/Ansible setup,
  restore into Kvin and test named links,
  page assets, login/editing as applicable,
  repeat convergence and an independent
  recovery procedure. Only then point
  `dir.nexus` at the accepted Kvin app.
  **Exit:** User-recognizable directory content
  works through the intended named route
  and can be restored after a host loss.
  **Owner:** Services.

- **SS-APPS-3 — [open; independent opt-in service] Pi-hole
  for ad blocking, not the LAN's general DNS.**
  Kvar Pi-hole has two known writable
  volumes (Pi-hole and dnsmasq config).
  Maintenance's Nov 8/9 evidence plus
  Nova's confirmation already established
  that **no current client is intentionally
  using Pi-hole** after the DHCP DNS swap.
  Do not spend another session finding
  dormant clients, nor hijack the Peanut
  authoritative resolver or DHCP.
  Build a restorable Kvin instance,
  coordinate local port53/owner constraints
  with Maintenance, test filtering from
  **one deliberately opted-in client**,
  restore the wanted configuration,
  and test update/recovery before
  changing `pihole.nexus` upstream.
  **Exit:** Working opt-in filtering,
  backed-up/recoverable state, correct
  UI, no changes to general Sanctum
  DNS or unselected clients.
  **Owners:** Services for Pi-hole;
  Maintenance for host DNS/firewall
  and client publication dependencies.

- **SS-APPS-4 — [open; separate ownership and recovery
  gates] Already-on-Kvin services.** Nextcloud's
  October 21 bidirectional Calendar ↔ GNOME
  Calendar interaction is accepted; do not
  repeat it merely to fill a checklist.
  Its full backup/restore and broad
  application lifecycle still remain.
  Search/SearXNG has a separate
  EyesOnly owner and known divergent
  old/new settings/theme: do not
  blindly overwrite the intended Kvin
  instance. Prism belongs to Project
  Joule, not Services; qualify the
  integration route and consume its
  owner's restore proof. PostgreSQL
  host service belongs to Maintenance.
  **Exit:** Each required consumer and
  restore dependency is accepted by
  its actual owning project, not
  silently reimplemented by Services.

### SS-PUB — Deliver real named client use and a reversible handoff

- **SS-PUB-1 — [blocked on SS-YX and relevant SS-APPS
  acceptance] Independent client acceptance.**
  Existing Kvin stage is locally
  reachable on HTTP:80; it is **not**
  a LAN published service yet.
  Maintenance owns Kvin HTTP:80
  firewalld admission. Agree the
  exact rule with that owner, then
  exercise actual trusted Outer
  and Inner clients with the selected
  route Host headers while existing
  Kvar NPM and wildcard DNS remain
  production. Test useful browser
  operation, authentication where
  needed, websocket/long-lived
  connections for relevant apps,
  data and monitor/filtering outcomes,
  and explicit rollback.
  **Exit:** Intended real clients
  complete their tasks on Kvin
  independently of same-host curl,
  with verified revert and no
  public inbound exposure.
  **Owners:** Services client/application
  tests; Maintenance firewall/DNS;
  Bunny Factory inner/outer routing.

- **SS-PUB-2 — [held for explicit live authorization]
  Production migration and Kvar retirement.**
  A reviewed cutover must preserve
  authoritative DNS, source-managed
  Nginx, named access, retained app
  data, functional clients and
  revertability. Change Kvar-facing
  app upstreams to accepted Kvin
  backends through the owning
  source, not hand edits. Reconcile
  wildcard/explicit DNS with
  Maintenance only after test
  and operator approval. Then
  independently qualify service
  restart/repeat, backup restoration,
  failback paths and eventually
  Peanut standby/failover as the
  separately recorded resilience
  outcome. **Only after every wanted
  service and recovery path is accepted**
  may Kvar be taken offline and
  reformatted under Maintenance's
  **separate destructive approval**.
  No permission for this exists
  in an overnight planning document.
  **Exit:** Kvin takes over user
  service duties without data or
  naming regressions; Kvar is
  redundant and safe for the
  separately authorized retirement.

### Immediate next work and reporting contract

**Tonight:** No native actions. This is a committed source
plan, not an asynchronous promise or a hidden host mutation.

**Tomorrow's order:** First implement and source-test
SS-YX-2, give Nova the *one* guarded native Kvin
eighth-route trial after CI, interpret its bounded
result and record the exact acceptance. Then finish
SS-YX-3's **material** routing gaps using existing
evidence as much as possible. Begin SS-APPS-1
Kuma's actual reproducible install/monitor
recovery implementation once the proxy
mechanism is source-qualified; move through
SS-APPS-2, SS-APPS-3 and the other
known restore gates by their real dependencies,
not by arbitrary clock or a daily checkbox quota.

**Every handoff:** State (1) the capability gained,
(2) proof level — source test, native local,
real client, or restored recovery, (3) what
remains to achieve its parent outcome,
(4) one concrete next executable task or
specific blocker. Nova gets **only**
the native action that cannot be
completed through connected source/CI
tools; keep ordinary follow-up output
requests narrow and meaningful. If
a task fails, fix the bounded cause
or report the genuine dependency;
do not launch a self-perpetuating
diagnostic chain. Do not promise a
given number of tasks will fit into
a day. Done means done right.

---

## Nova's available-week priority — November 1–8, 2026

Nova has no class until **November 9**. His intended push before then is the
planned **physical Inner/Outer network cutover** and beginning **Fedora 45
migration on every eligible computer**, once the release is available and the
host is ready. His expectation of release in a few days is not release evidence.
These are existing roadmap outcomes, now prioritized for his available week.

Each lead must give Nova its readiness assessment, concrete concerns and proposed
dependency order **before the corresponding cutover or upgrade proceeds**. Nova
will give each session a turn to weigh in. This prioritizes preparation; it does
not grant blanket cutover/upgrade/reboot approval or pause independent authorized
work. Services owns application, storage and database/address-consumer readiness and acceptance during the topology change; coordinate host/network prerequisites with Maintenance and Bunny.

[Cross-project directive and coordination](https://github.com/wdcallahan/sanctum-maintenance/issues/20#issuecomment-6561435565).


**Status:** Native Calendar 6.6.2 install and unchanged application-only repeat passed on Kvin (October 21). Nextcloud Calendar opens in the browser; Nova observed an existing event in GNOME Calendar and explicitly confirmed **bidirectional Calendar access** between desktop and Nextcloud. The exact event-write/reload steps were not separately reported. Protected reverse-proxy login, full service recovery and fresh-instance reconstruction remain separate; the general-purpose EE/controller co-build is still open. Some lower sections retain dated infrastructure observations requiring separate verification.  
**Updated:** 2026-10-21.  
**Scope:** Reproducible operation of self-hosted application services, beginning with Nextcloud.  
**Current waypoint:** Calendar installation, idempotence and operator-confirmed bidirectional client access accepted → separately qualify protected service access, recoverability and the hands-on shared Navigator/EE milestone.

## YXORP current gate — November 9, 2026 (Peanut trial corrected)

Nova rejected localhost-only/high-port staging: test the **actual rootful
HTTP:80, all-interface proxy on Peanut**, leaving **Kvin** as the production
destination and **Kvar** NPM untouched. The source now defines an independent
`yxorp_test` inventory group for `peanut.arcane.sanctum`,
`ansible/yxorp-peanut.yml` with read-only port-80/firewall preflight,
a real HTTP-client probe from Kvin, and a scoped Peanut-only remover.
Kvin's declared listener is likewise normal `0.0.0.0:80`, but its
production cutover gate remains false. There is **no** DNS or firewall
mutation inside Services. Peanut's active firewalld is Maintenance-owned,
so a missing port-80 policy requires cross-project coordination.

**Native result:** Nova ran Peanut's read-only preflight from Kvin:
`ok=11 changed=0 failed=1`. Exact Peanut and free port-80 assertions
passed; firewalld `public` refused both `http` and `80/tcp`.
Nova explicitly authorized an **ad hoc runtime-only trial exception**
with cleanup. Source now records and applies a four-hour expiring port-80
exception before repeating the original preflight and trial; the matching
trial removal play revokes only that runtime exception. No permanent
firewall or DNS change, no Kvar or Kvin production change.
**Next terminal step** is the updated Peanut test play on Kvin; this is
a meaningful retry after changing the originally blocked policy condition. [Trial and rollback runbook](runbooks/yxorp-reconstruction.md).
The Peanut test tag follows a maintained Nginx channel but automatic
updates/rollback remain a separately measured lifecycle decision.

## Peanut YXORP HTTP:80 trial — native DNS boundary, November 9

The first actual Peanut port-80 preflight found the firewall closed;
Nova authorized a four-hour temporary runtime exception and cleanup.
The subsequent selected trial advanced: permission/preflight passed,
Peanut trial config directory/candidate rendered, official maintained
Nginx Alpine image pulled. It then **failed before persistent install**
because `nginx -t` in Podman's rootful bridge container could not
resolve `yarn.inner.sanctum`. This is **not** an Nginx syntax or
application failure. [Bounded DNS comparison playbook](../ansible/yxorp-peanut-dns-observe.yml)
is the next native operator step from Kvin; compare the host and bridge
queries (default, Peanut DNS, Kvin DNS) before changing resolver or
upstream config. Do not repeat the unchanged failing deployment blindly.
Temporary HTTP admission still expires; remove test artifacts and
revoke the exception with `ansible/yxorp-peanut-remove.yml` when done.

## YXORP bridge DNS resolved in design — November 9

Nova's read-only Peanut DNS observation passed `ok=8 changed=0`.
Host `getent` resolves Yarn `192.168.1.110`; default/Peanut-DNS
Podman bridge probes report BIND `REFUSED`; Kvin-DNS bridge times out.
The Maintenance BIND ACL source permits only loopback and
`192.168.0.0/16` clients. Rather than altering the active DNS owner
solely for an isolated proxy, Services now uses **host networking**
for both rootful Quadlets on Peanut/Kvin, normal TCP/80 with no
`PublishPort`. Nginx syntax validation also uses host networking.
Next operator run is the changed `ansible/yxorp-peanut.yml`, followed
by `ansible/yxorp-peanut-probe.yml` from Kvin if it succeeds. The
revised test remover validates host networking and still cleans
the temporary runtime firewall permission. No production cutover.

## Estate-wide reconstruction and future services — decisions November 8, 2026

[Service estate / owner and disposition register](SERVICE-ESTATE.md) is the authoritative Services inventory across projects, including Project Joule's Prism and Maintenance's PostgreSQL rather than omitting containers not owned by this repository. Kvin was purchased years ago for the service-host role previously served by Kvar; the host transition is not a new strategic choice. Installation, data restore, proxy adoption, client acceptance and Kvar retirement still need actual qualification.

Decisions: **retain Pi-hole for ad blocking, not general/authoritative LAN DNS**; **retire OpenWebUI (replaced by Prism) and Endlessh**; preserve **no intended public inbound port exposure**. **Tailscale is a temporary VPN arrangement**, not the destination. A proper network VPN, **Luanti** and **Home Assistant** are explicitly planned Services work, with network and host boundaries coordinated and implementations yet to be selected. Retired Kvar containers do **not** each need uninstalling: once every wanted service has been restored and verified on Kvin and the actual handoff is approved, Kvar will be taken offline and reformatted. No partial migration, historical source observation or this plan authorizes early formatting. The active recovery and YXORP route reconciliation work is [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2).

## Declarative operations and service privilege — November 8, 2026

**"So let it be written, so let it be run."** All intended recurring service configuration and maintenance should be expressed through version-controlled Ansible/source and declared nonsecret configuration, then independently repeatable and restorable. This implements the existing [canonical Operational Project Completion Standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md). Manual UI or host changes are temporary responses to reconcile into the owning source; a running service without an installer and declared recovery inputs fails the objective.

**Rootless is a choice, not a requirement.** Use native privileged services where required (including normal host SSH); use rootless Podman for suitable app workloads and **rootful Podman Quadlet for the chosen YXORP listener on host ports 80/443**. Do not invent low-port tricks merely to avoid root. Services deploys workloads; existing network/firewall owners retain their responsibilities. The design selected for [Services issue #2](https://github.com/wdcallahan/sanctum-services/issues/2) is **plain Nginx managed through Ansible-rendered configuration**, replacing Kvar Nginx Proxy Manager's UI and database—not automating the old admin interface.

**HTTPS/private CA decision is deferred, not an open delivery workstream.** Ordinary HTTP was consciously accepted for trusted internal `.sanctum` use by October 20, and Project Joule selected the HTTP browser origin on October 16. Plaintext credentials/tokens are a known risk; a universal private CA would impose certificate/key lifecycle, enrollment and potentially impossible trust-store changes for the worst clients (e.g., restricted Android apps). **Do not reopen PKI merely by defaulting to HTTPS.** Reassess only when a particular app/function or concrete changed threat model makes TLS worth the full operational cost. `.sanctum` naming is settled; public/private hybrid naming was deliberately retired. [Decision record #3](https://github.com/wdcallahan/sanctum-services/issues/3) is closed/not planned. YXORP plain Nginx must work over HTTP without certificates.

## Destination

An independently maintainable service, **not just a running container**. Nova should be able to install, inspect, modify, update, back up, restore, move, and uninstall the service using understandable, documented procedures and the owning automation. The build itself is hands-on education relevant to his Red Hat instruction, professional experience, and CV.

Four requirements must be true **from the start**, not promised at the end:

1. **Documented:** The public-facing explanation and operations guide make sense without chat history or project-lead notes.
2. **Repeatable:** Automation plus declared durable inputs reconstruct the service; unchanged reruns converge.
3. **Understandable:** Nova knows why each component exists and can independently operate and troubleshoot it. The technologies selected for professional learning are exercised for real.
4. **Uninstallable:** Application-owned runtime objects can be cleanly removed. Data retention or intentional destruction is an explicit separate choice, with verified scope.

A healthy service, passing syntax test, or documented procedure alone does not meet these conditions.

## Decisions already established

- First service: **Nextcloud**, using the Apache container variant and existing PostgreSQL.
- Initial application host: **Kvin** (`aarch64`, rootless Podman); host TCP **8085 → container TCP 80**. The listener returned HTTP 200 locally October 19. The missing **host firewall** publication is a distinct Maintenance-owned prerequisite, not a reason for Services to mutate firewalld.
- The initial HTTP-only Town Square route is `http://square.nexus.sanctum` through YXORP, with no matching internal certificate; the current 502 remains unaccepted. Moving hosts/ports changes the proxy upstream, not the stable service name. Later trusted TLS is a separate decision.
- Initial live file storage: **Kvin's NVMe**, with an approximate **50 GiB soft planning budget**. **Peanut** is the separate backup destination (434 GB free on October 17). **Void** is the eventual intended persistent-storage host, not a dependency for the initial pilot.
- **Podman Quadlets, not Docker Compose**. The long-lived Ansible experience should use **Ansible Navigator with an EE**. Do not reproduce per-project venvs as a default merely because they are easy to create.
- Secrets and nonreconstructible data are managed outside public plaintext Git. Existing PostgreSQL, proxy, network registry, and controller infrastructure each retain their own ownership boundaries.
- Source-control workflow: direct linear `main`, no default branch/PR ceremony; GNU GPL version 3 or later for our original work.

## Work sequence

These are *acceptance gates*, not calendar estimates. An unchecked gate has no acceptance evidence yet. Complete each active stage before relying on it in the next one; nondependent documentation can evolve alongside implementation.

### Stage 0 — Establish the correct objective

- [x] Give the service deployment its own repository.
- [x] Record host/storage/port observations and the separation from adjacent projects.
- [x] Correct the false claim that an installation or syntax test establishes a completed service.
- [x] Withdraw the direct-via-venv deployment instructions pending EE design.
- [x] Preserve Nova's practical-learning, independent-operation and **teach when a real operation needs it** requirements in the existing cross-project [Nova–Pixel interface standard](https://github.com/wdcallahan/engineering-standards/blob/main/Nova-Pixel-Project-Interface-Standard.md). Preserve his choice of plain `git pull` in the existing [Git standard](https://github.com/wdcallahan/engineering-standards/blob/main/Git-Project-Engineering-Standard.md).
- [ ] Separately review whether the [Operational Project Completion Standard](https://github.com/wdcallahan/engineering-standards/blob/main/Operational-Project-Completion-Standard.md) needs an explicit four-part exit test. This normative document has **not** been amended; avoid creating another overlapping policy.

**Evidence:** Repository source and operator terminal observations, recorded separately in the [engineering log](history/engineering-log.md). The four requirements above are Nova's explicit objective for this project whether or not the shared standards amendment is approved yet.

### Stage 1 — Controller workflow: learn the mechanism before hiding it

- [ ] Diagram the normal path: **Kvin/Peanut host → ansible-navigator → selected EE container → playbook → managed host**. Explain where Ansible, collections, Python, Podman, SSH, and the project files actually run.
**Existing learning example:** Sanctum Maintenance already has a `localhost/sanctum-maintenance-ee:2026.07` image and `ansible-navigator` tooling established on both Debian ARM64 controllers; see its [Navigator configuration](https://github.com/wdcallahan/sanctum-maintenance/blob/main/ansible-navigator.yml) and [controller pair runbook](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/runbooks/controller-pair-readiness.md). The Maintenance EE is **qualified for that project only** and must not be silently promoted to a generic shared runtime. Its existing Navigator installation is a valid, read-only object lesson before deciding how to install a centrally managed toolchain for other projects.

- [x] **Ownership chosen provisionally by Nova on October 18:** the existing [Sanctum Maintenance controller-infrastructure workstream](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md) will own centrally maintained Navigator/Builder tooling and a **separate, new, general-purpose EE** for applications. This is for coherence, not because no other design is possible. Revisit a dedicated controller-platform repository if this boundary grows too large. The current qualified Maintenance EE remains unchanged. **Decision recorded, not implemented.**
- [ ] Decide and document how Navigator/Builder are installed on both Debian controllers: supported native packages if available; otherwise a separately justified and centrally managed host-tool installation. An EE does not require a project-local Python venv.
- [ ] **Keep this automation ordinary-Ansible-first:** Nextcloud's roles, inventories, variables, playbooks and operator workflow must remain meaningful with plain `ansible-playbook` given equivalent dependencies. Navigator is the selected EE delivery/launch interface; Runner may be present *within* the EE for that interface, but do **not** make application scripts call Runner's CLI/Python API or parse Runner-specific artifacts just because it is installed. Preserve the classroom-portable Ansible learning objective; separate infrastructure-specific execution from ordinary Ansible content.
- [ ] **Build the new shared EE together with Nova, not merely for him.** First decide the image's purpose and dependencies; then have Nova participate in authoring/reviewing its `execution-environment.yml` and inputs, generating and inspecting Builder's Containerfile, performing the Podman build, inspecting the resulting image, running it with Navigator, and practicing a rebuild and clean removal. Explain what is unfamiliar at each real step. This is a required hands-on professional learning experience, **not** a delegated one-command image delivery.
- [x] **EE architecture accepted by Nova with a fully understood yes on October 18:** one minimal, versioned, centrally owned EE foundation; consume its exact pinned image when sufficient; otherwise build a project-specific EE derived from the pinned foundation with only genuinely needed collections/packages, separate acceptance and digest. Avoid duplicate equivalent images; retain separately qualified/incompatible runtimes. **Design accepted, not installed or built.**
- [ ] Define the accepted common EE's actual minimal runtime and rebuild/retrieval path; pin and qualify the image on **ARM64** and make it available to both controllers. Before deriving from an existing EE with Builder, inspect its generated Containerfile for redundant Core/Runner installation. **Do not rebuild or overwrite the existing qualified Maintenance image** as a teaching shortcut.
- [ ] Use Navigator to inspect the EE contents and run a small harmless read-only playbook. Nova practices the steps and understands the output.
- [x] Remove the **wrong inventory override** `ansible_connection: local`. The inventory now uses Ansible's default **smart** connection (SSH for Kvin) and names `wdc2` as the managed user. **Source correction only; no EE/SSH acceptance test yet.**
- [x] From Kvin, launch the existing Maintenance EE with Navigator and confirm an **ad hoc `ansible.builtin.ping` over smart/SSH back to Kvin** returned `SUCCESS` and `pong` (October 18); this qualifies **that existing EE-to-Kvin path only**.
- [ ] Confirm the intended `wdc2` rootless user-systemd path from an approved EE and the applicable controller/SSH permissions; establish **Peanut → SSH → Kvin** through the selected runtime as part of shared-controller acceptance. Existing Maintenance peer evidence is relevant but does not automatically qualify the new Nextcloud setup.

**Exit test:** Starting in a normal shell on either controller, Nova can identify the configured EE, launch Navigator, inspect its Ansible and collections, and run a read-only task against the intended *host* (not the EE container). Both controllers can reconstruct the tooling from its owning source and durable image inputs.

**Learning stage still open.** The initial container was deployed through the existing Maintenance Navigator/EE as a bounded deployment; Nova's hands-on new shared-EE build remains a separate, unfinished deliverable.

### Stage 2 — Build a complete first-deployment path

**Host firewall owner boundary (October 20):**
- [x] Transfer the **Services source** from opening its own host port to only checking Kvin's `eth0`/`public` zone and `8085/tcp` in both runtime/permanent firewalld before changing Nextcloud resources. See [Services issue 1](https://github.com/wdcallahan/sanctum-services/issues/1). This is **source-only** pending native controller qualification.
- [x] Maintenance's Kvin ordinary published-service port correction was **authorized and applied October 20**; independent peers qualified 5432/8084/8085 and Maintenance's preservation/repeat evidence passed. See [final owner receipt](https://github.com/wdcallahan/sanctum-maintenance/blob/24ea37e9c432841cc994381503736e84bceca637/docs/qualification/2026-10-20-kvin-firewall-complete.md). This does not discharge Services' separate Nextcloud application/proxy/restore tests.
- [ ] Verify the Services role's prereq on the actual managed Kvin, then perform independent direct Nextcloud `/status.php` and proxy/browser acceptance. Host firewall convergence is not proof of a working Nextcloud login.

- [ ] Review the existing `ansible/` candidate against the approved execution model; revise or replace mistaken assumptions at source instead of layering workarounds.
- [ ] Configure a stable user-facing Nextcloud hostname/scheme and confirm YXORP's intended route.
- [x] Confirm the stable **named** PostgreSQL endpoint `db.nexus.sanctum:5432` and the PostgreSQL owner's supported dedicated `nextcloud` database/login provisioner. **Production creation and unchanged repeat accepted by Maintenance October 19.** Actual authentication from the Nextcloud container and application schema creation remain untested.
- [x] Pull/inspect the ARM64 Nextcloud Apache image on Kvin and pin its observed image manifest digest. **No successful container launch or app-specific image test yet.**
- [ ] Define persistent directories, appropriate rootless ownership, private secrets, Quadlet, startup/lingering, and a bounded host port through Ansible.
- [ ] Define **installation and removal** procedures together, so each managed object has a clear owner and safe removal behavior.
- [ ] Run static checks (syntax and relevant lint/tests) **in the intended EE**, then deploy from Kvin through Navigator.
- [ ] Run the same playbook again and require truthful **zero-change convergence**.

**Exit test:** A new application host can be configured from source and declared secrets; the Nextcloud service starts, survives the supported restart sequence, and a second unchanged deployment reports no changes.

### Stage 3 — Demonstrate real Nextcloud use

- [x] **First third-party app milestone (October 21):** Calendar 6.6.2 installed and enabled through Ansible; unchanged repeat `changed=0`; Nova opened Calendar successfully and saw an existing example event both there and in GNOME Calendar.
- [x] **Operator confirmation (October 21):** Calendar access works bidirectionally between Nextcloud and desktop GNOME Calendar. Exact event-writing/reload steps were not logged individually; no further bidirectional-access confirmation is requested simply to repeat the accepted result.

- [ ] Establish and verify PostgreSQL connectivity and initial application setup.
- [ ] Verify the service through YXORP at its stable name; confirm trusted domains/proxy headers, expected scheme, and absence of undesired direct public exposure.
- [ ] Log in as a real test user; upload, download, edit, and delete a representative file; demonstrate the intended client behavior.
- [ ] Define and verify appropriate background-job scheduling, error visibility, and a practical inspection/troubleshooting procedure.
- [ ] Explain the path of an actual request and file write, from user-facing name to container, filesystem, and database.

**Exit test:** Nova can use and diagnose the application without guessing which host, port, volume, or database it uses.

### Planned next user feature — first-class Joule collaboration (clarified October 19)

**Nova's specific requirement is Google-Sheets-style *live* coediting**, not creating a replacement .ods/.xlsx on disk and re-uploading it. Give Joule her own ordinary Nextcloud user identity, subject to the server's sharing/group access controls: Nova can share read-only, editable, or create-capable workspaces with her; Joule can own/create her own files and share them back to Nova. Joule is a family member with her own account, subject to the same ordinary privacy and sharing boundaries as every other family member; membership never implies global file or administration rights. Folder sharing permissions are available in core; the optional Group folders app may provide more granular ACL policy.

Provide a Nextcloud-compatible browser-based office editor (Collabora Online/CODE or another qualified office backend) where both Nova and Joule participate as **distinct authenticated editors in the same live document**, with visible concurrent changes and normal session conflict handling. Joule's **independent agent/tool integration** should perform authorized live edit actions in **Joule's identity**, regardless of whether Nova interacts with her through Prism or another client. The implementation location is an open design choice; **do not couple Nextcloud editing to Prism by assumption**. An app account alone does *not* provide a machine-usable concurrent editing API; verify the office backend's supported edit/session/auth interface, operation controls, and feasibility first. **WebDAV whole-workbook fetch/modify/re-upload is not an acceptable substitute** for this user goal. Current Collabora releases have evolving integration interfaces and in-editor AI features; neither establishes that Joule already has session-authorized editing. No untested implementation promise. Coordinate any Joule agent/tool changes with that project's owner; this project owns Nextcloud/office service plumbing, not Joule's runtime or client source.

**Naming candidate from Nova:** **Town Square**, with initial proposed address `square.nexus.sanctum`. It is a family/community workspace, not a claim of unrestricted public access. Confirm the name and external/internal routing before filling `nextcloud_public_hostname`; no DNS/proxy change is approved by this note. Continue basic Nextcloud installation without making future live Joule integration a hard prerequisite for initial Files login.

### Stage 4 — Backup, restore, and replaceability

- [ ] Implement automated, recoverable copies on **Peanut**, including retention and an observable last-success status. A mirror that propagates accidental deletion is **not** sufficient.
- [ ] Define an application-consistent backup set: Nextcloud files/config, database snapshot through its owner, and required secrets/recovery inputs; include correct ownership restoration.
- [ ] Perform a **real restore exercise** into a separate qualifying location from the retained backup artifacts; verify files and application operation independently.
- [ ] Document how to replace Kvin's Nextcloud role without requiring ChatGPT, remembered commands, or the surviving source container.
- [ ] Recheck capacity and retention against the 50 GiB soft budget; raise the budget if actual use requires it.

**Exit test:** An observed backup can restore a working Nextcloud instance and its representative files without relying on unstated local residue.

### Stage 5 — Normal operation, upgrades, and uninstall

- [ ] Write and exercise readable operator runbooks for deploy, check status, stop/start, update, troubleshooting, and recovery.
- [ ] Demonstrate a controlled image/configuration update through source-controlled desired state; identify rollback limits, including database/schema compatibility.
- [ ] Exercise **uninstall with data retained**: remove only owned services/configuration as intended and leave a recoverable data set.
- [ ] Exercise **explicit purge** only with deliberately disposable test data; do not silently delete shared PostgreSQL state or valuable files. Document the owner and authorization for database deletion.
- [ ] Have Nova follow the published procedures, explain the major mechanisms, and independently perform representative operations without relying on new ad hoc instructions.
- [ ] Review the README and runbooks as a new human administrator would. Remove stale guidance and ensure links, commands, status claims, and dependency owners are clear.

**Exit test — first project complete:** The four requirements are demonstrated with meaningful evidence: documented, repeatable, understandable, **and** uninstallable. A fresh operator can navigate the repository and Nova can administer the service himself.

### Stage 6 — Later, explicitly separate work

- [ ] Move persistent file storage toward **Void** when its storage service is ready; use the stable YXORP name, controlled data migration, rollback, and restoration checks. Do not make this a hidden condition for the Kvin pilot.
- [ ] Deliver **Home Assistant** as a planned application, scoped and qualified separately with its storage, devices and security integrations.
- [ ] Deliver **Luanti** as a planned Services application, with its server, data, update, backup and recovery contracts.
- [ ] Plan and qualify a **proper Sanctum VPN** to replace temporary Tailscale, without opening unreviewed public ingress or interrupting clients. Coordinate topology, authentication, firewall, DNS and host responsibilities with owning projects.
- [x] **Do not require blanket HTTPS / a private CA.** Existing October HTTP decisions and the worst-client trust burden are recorded in [closed issue #3](https://github.com/wdcallahan/sanctum-services/issues/3). A future specific application or material new security requirement can initiate a new explicit TLS design; it is not a migration or completion prerequisite.
- [ ] Reuse the same established operator and documentation patterns without copying an unnecessary new EE or implementation for each service.

These items are **future work**, not reasons to keep the completed Nextcloud pilot perpetually unfinished.

The normal managed-host connection is **smart/SSH**, including when the controller and managed host happen to be the same physical machine. This makes controller location an operational choice rather than changing playbook semantics.

## Important work boundaries

- `sanctum-services` owns application deployment, its lifecycle contract, and its operator documentation.
- The **shared** Navigator/Builder toolchain and future application EE belong to [Sanctum Maintenance's controller-infrastructure workstream](https://github.com/wdcallahan/sanctum-maintenance/blob/main/docs/maintenance-roadmap.md), provisionally agreed October 18. This application project consumes that qualified interface, not its private `.venv` or its existing Maintenance-qualified EE.
- PostgreSQL provisioning/backups, DNS/network registration, and fleet OS maintenance are coordinated with their owners, not silently absorbed. **Services issue #2** establishes Services' proposed YXORP installation and desired-route reconciliation ownership; coordinate takeover of the currently operated proxy before live modification. Prism remains Project Joule-owned and must still appear in estate-wide reconstruction planning.
- The broader review of other Sanctum projects against this educational/maintainability objective is a separate cross-project effort. This roadmap does not authorize mass refactoring.

## Evidence and documentation policy

- **README:** purpose, current status, and navigation; newcomer-friendly.
- **Architecture:** actual supported mechanisms, ownership, data flows, and key reasons.
- **Runbooks:** proven end-user commands/procedures, preconditions, expected results, troubleshooting, and recovery.
- **This roadmap:** destination, checkpoints, acceptance tests, and the active frontier; change the tick boxes only when evidence supports them.
- **[Engineering log](history/engineering-log.md):** dated experiments, changes, failures and evidence links. Not a second manual and not a transcript archive.
- **[Lead handoff](../PROJECT_LEAD_INTRODUCTION.md):** concise continuity for another assistant; not a prerequisite for human operators.

When the implementation changes, update the relevant explanation and operational procedure **with the same change**. Do not promise to document it after deployment. Record substantial outcomes separately in the engineering log.

### Source checkpoint — November 8 (unqualified, no live changes)

- [x] Record Project Joule's required Wicket Ollama Kuma probe as
  [desired monitor source](../data/kuma-monitors.yml) with
  [retained-instance acceptance issue #4](https://github.com/wdcallahan/sanctum-services/issues/4).
  **Monitor installation and Up acceptance remain unchecked.**
- [x] Add initial plain Nginx [route manifest](../data/yxorp-routes.yml),
  [rootful Quadlet/Ansible role](../ansible/yxorp.yml),
  [local preview](../ansible/yxorp-preview.yml), and
  [rebuild runbook](runbooks/yxorp-reconstruction.md). Draft routes are
  **not** a verified full extraction from Kvar NPM.
- [x] Source-only CI passed for YXORP and retained Kuma: route/monitor contracts, Ansible syntax, isolated controller render, read-only NPM report comparison tests and actual Nginx `-t` parser runs (minimal and all proposed routes, synthetic CI DNS). [Accepted run](https://github.com/wdcallahan/sanctum-services/actions/runs/42562957639). No native Kvin or application acceptance is implied.
- [ ] Select and natively qualify immutable ARM64 Nginx and Kuma image digests; only then authorize any isolated service staging.
- [ ] Qualify a native loopback-only YXORP stage on Kvin, actual routes and
  WebSocket client behavior; only then consider separately authorized DNS
  and listener cutover. Existing Kvar NPM is untouched.

### November 9 — current YXORP native evidence gate

- [x] Nova ran the accepted November 8 generated-upstream report comparison:
  **8** NPM hosts, **5** matching originally proposed current names with zero
  upstream discrepancies; Pi-hole UI and legacy Yarn routes are now recorded.
  See [the review](review/2026-11-09-yxorp-default-route-comparison.md).
- [x] Source-only NPM behavior inspector added and [passed CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42677320762):
  generated proxy-host metadata, extra location counts, headers/directive
  names, access/redirect/TLS indicators, custom file presence and hashes.
  Never print raw config/credentials. SSH uses Kvar TCP 10022; no live
  changes. [Runbook](runbooks/yxorp-reconstruction.md).
- [ ] **Current operator-dependent read-only step:** from the pulled Services
  checkout, run `~/.local/bin/ansible-navigator run ansible/yxorp-inspect-npm.yml`;
  inspect the actual Kvar report and decide whether any route behavior needs
  further migration. This does not authorize the eventual cutover.

### November 9 — NPM behavior inspection received (read-only)

- [x] Kvar rootful NPM generated-host metadata examined using the accepted
  value-redacting observer: **eight** host files, one location per host,
  no non-default locations, no nonempty global custom files, no extra
  redirect/stream host files. Explicit WebSocket headers on Nextcloud and
  Prism; historical Prism config contains TLS certificate directives.
  All files had two unclassified lines and one custom-include reference:
  **no automatic assertion of per-host customization or full parity**.
  [Behavior evidence record](review/2026-11-09-yxorp-behavior-observation.md).
- [ ] Validate actual reverse proxy forwarding/Upgrade/host isolation with
  synthetic Nginx endpoints in isolated CI (no real Sanctum services).
- [ ] Qualify the final generated shared-include semantics, real app client
  access and later Kvin native rootful staging, subject to selected image.

### November 9 — NPM behavior adoption and native image gate

- [x] Operator supplied read-only Kvar generated-host inspection:
  eight hosts; one default location each; no extra generated redirect/stream
  hosts or nonempty global custom snippets. Explicit Upgrade headers on
  Square and Prism only; legacy Prism TLS certificate directives present.
  The repeated custom include and `https` marker resemble NPM's public
  generated template (optional include and HSTS map), **not proof of eight
  special route configurations**. Preserve private HTTP decision.
  [Review](review/2026-11-09-yxorp-behavior-observation.md).
- [x] Source-only Nginx CI now proves actual HTTP routing, forwarded headers,
  WebSocket 101, unknown-host denial, route change and explicitly selected
  removal on loopback with synthetic backends. It also parses both draft
  Yarn-only and all-proposed configurations. [Passing CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42690046860).
- [x] Registry metadata identified published **ARM64-specific image digest
  candidates** (official Nginx and Uptime Kuma 2.5.9). Source-only
  [image lookup CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42690400649)
  passed; no images downloaded onto Kvin.
- [x] Prepared native [image-only qualification](../ansible/yxorp-qualify-image.yml)
  and [runbook](runbooks/yxorp-image-qualification.md), source-validated in
  [CI](https://github.com/wdcallahan/sanctum-services/actions/runs/42691039448).
  It never enables a proxy, opens a port or changes Kvar/DNS/firewall; an
  operator-selected run can fill Kvin's rootful image cache.
- [x] Nova ran `ansible/yxorp-qualify-image.yml` on native Kvin:
  **ok=11 changed=4 failed=0**. Pinned official Nginx image pulled into rootful
  Podman cache, Linux ARM64 architecture confirmed, ephemeral offline
  `nginx -t` accepted the generated Yarn-only configuration; temporary
  config removed. No listener, service, Kvar, firewall or DNS modification.
- [x] The exact natively qualified digest is now the `yxorp_image` source
  value. Added `yxorp_stage_approved: false` as a deliberate hold before
  the rootful Quadlet deployment; source change is not staging approval.
- [x] Promoted the native-tested Nginx digest to the YXORP deployment vars
  and enforced a pre-mutation `yxorp_stage_approved: false` gate; source
  checks guard the gate and exact digest.
- [ ] **Current operator-dependent gate:** authorize or decline installation
  of the separate **loopback-only** Kvin YXORP stage. Even if authorized,
  that is not production publication, DNS cutover, or application acceptance.
- [ ] After image qualification, independently authorize a loopback-only
  YXORP stage and real client routing acceptance; only later consider the
  separate production cutover. Kvar NPM must remain untouched until then.
