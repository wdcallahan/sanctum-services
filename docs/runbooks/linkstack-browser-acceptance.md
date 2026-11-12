# LinkStack recovered candidate: controlled browser acceptance (Kvin)

## Native state, November 12, 2026

- Kvin rootless service `sanctum-linkstack-kvin-candidate.service` is **running** from the pinned original Kvar ARM64 image, using ownership-adjusted retained volume `sanctum-linkstack-qualified-20261112t105926`.
- Its only host listener is **`127.0.0.1:18081` on Kvin**; ordinary LAN clients cannot connect directly. Candidate internal root HTTP is **200**.
- Kvin's restored public HTML body is **byte-identical** to both direct Kvar origin `kvar.outer.sanctum:8081` and Kvar NPM; all three roots return **HTTP 200**, `text/html`; both public pages have **23** anchors, **4** stylesheet references, **2** JavaScript references, with one common CSS and one common JS response sampled and identical end-to-end. The observer did **not** examine every asset, authenticated session or actual rendered page.
- Exact live `dir.nexus.sanctum` YXORP backend remains **Kvar**. No source data deletion or retirement of old services permitted. Older Kvin accepted unmodified restore volume and both private archives preserved.
- The public home page did not contain a **matching discoverable login link**. LinkStack's official [FAQ](https://docs.linkstack.org/faq/) says administrator sign-in begins at **`/login`**; absence of an anchor on the public home page is expected and is not a login failure.

## Current source-owned, read-only gate

Run on Kvin **only with separate approval**:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/linkstack-anonymous-login-proxy-probe.yml \
  -e sanctum_linkstack_anonymous_login_probe_approved=true
```

This play verifies the exact active rootless candidate image, persisted recovered volume and loopback-only port, then performs **anonymous GET `/login`** from direct Kvar, Kvar NPM and Kvin loopback. On Kvin it additionally sends an HTTP **absolute-form** request target (`GET http://dir.nexus.sanctum/login`) to the same loopback backend, simulating the request that an SSH-forwarded Firefox **HTTP proxy** would send. It never follows redirects or submits a form, password, authorization or session cookie. Output consists only of status, MIME class, finite redirect host/scheme categories, cookie-attribute flags and whether both candidate request forms behave comparably; it does not expose HTML, `Location`, cookies or CSRF values. Like any anonymous login-page GET, it may cause the application to allocate an anonymous session; there are no intended configuration writes.

**Native result not yet obtained.** Do **not** set up a browser session solely because this source exists. On native report, check whether the absolute proxy request is compatible with the ordinary request, any redirect goes to a different host or to HTTPS, and any `Secure` cookie implies HTTPS is required. If proxy-form differs or redirects require HTTPS, stop and design a separately guarded path; do not put credentials into a browser that can silently reach Kvar.

## Conditional browser procedure, after compatible native result

The intended solution preserves the **browser origin `http://dir.nexus.sanctum`** while carrying requests to **Kvin**. It must not use the ordinary live Firefox profile. It must not rely on the host's real DNS answer for `dir.nexus.sanctum` or on temporary changes to DNS, /etc/hosts, YXORP or Kvar NPM.

1. From the desktop that runs Firefox, start a dedicated SSH local tunnel (ensure local port unused) to **Kvin**, not Kvar:

   ```bash
   ssh -N -o ExitOnForwardFailure=yes \
     -L 127.0.0.1:18081:127.0.0.1:18081 \
     wdc2@kvin.outer.sanctum
   ```

   Keep the terminal open while testing. The source port on **Kvin** remains its existing loopback-only candidate.

2. Launch a **new isolated Firefox profile** with **manual HTTP *and* HTTPS proxy** set to **`127.0.0.1:18081`**, with no bypass exceptions and HTTPS-only upgrades disabled for this test. A manual proxy preserves the URL's Host/origin, unlike opening `http://localhost:18081`. The HTTP proxy request is carried over SSH to Apache and is supported **only if** the preceding native absolute-form test passed. Set the HTTPS proxy to the same tunnel, too: HTTPS attempts requiring CONNECT will **fail**, not connect to the live DNS route. Do not configure direct HTTPS fallback. Do not browse unrelated destinations from this test profile.

3. Visit **`http://dir.nexus.sanctum/login` in that dedicated proxy profile**, verify that the login form loads without a redirect to an unrelated/HTTPS URL, and *only then* authenticate with existing credentials privately. Do not send a password, CSRF token, cookie or screenshot of private admin pages into the conversation. Verify dashboard loads and recognizable original admin data appears, while checking that any redirects still reach the Kvin candidate (a proxy tunneled to Kvin should fail rather than silently fall back when stopped).

4. Exit the isolated Firefox instance, close the SSH forwarding session, and securely remove the disposable profile containing the browser cookies/credentials. Never claim authenticated admin or real browser acceptance until reported by the operator, and never repoint `dir.nexus.sanctum` before that acceptance.

For Mozilla's user-facing proxy settings, see [Firefox connection settings](https://support.mozilla.org/en-US/kb/connection-settings-firefox); for its isolated profile flags, see [Firefox command-line parameters](https://firefox-source-docs.mozilla.org/browser/CommandLineParameters.html).

## Post-browser gate

A successful authenticated session confirms recoverability of data and access **inside the Kvin candidate**. It is not yet an internet/LAN-reachable service nor permission to retire Kvar or to change production. A subsequent separately approved, source-managed **YXORP upstream** transition must retain Kvar fallback and verify actual named-client, assets/admin session and rollback.
