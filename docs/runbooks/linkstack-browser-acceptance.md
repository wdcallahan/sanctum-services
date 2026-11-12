# LinkStack production route transition (Kvar to Kvin)

## CURRENT — November 12: production LinkStack browser and admin login ACCEPTED

Nova ran the source-managed production YXORP update: Kvin recap **`ok=31 changed=3 failed=1 skipped=1`**. The existing role applied changed Nginx configuration before the post-task **old Yarn HTTP timed out**; the later new LinkStack post-task was not reached. This failure **does not mean** the already-applied `dir` route was reverted. Nova then confirmed from ordinary Firefox that **`http://dir.nexus.sanctum/` displayed the directory and administrator sign-in worked**. The production LinkStack public directory and admin-authentication acceptance gates are therefore **closed** based on the real browser, despite the unrelated Yarn smoke-test failure. No extra LinkStack test or rerun of the failing playbook is requested.

Desired route: normal client DNS → existing Kvin production YXORP port 80 → Kvin LinkStack `127.0.0.1:18081`. Kvar rootless LinkStack and its original volume remain **running, unchanged**, solely as a usable fallback. Do not invoke the rollback command unless a **real** problem with LinkStack occurs. The historical rollout and fallback instructions below are retained for maintenance; they are **not pending operator actions**.


## Accepted native state

- Kvin's restored LinkStack is already running on `127.0.0.1:18081` with recovered application data. Public directory, sampled assets and anonymous `/login` HTTP have passed.
- The ordinary `dir.nexus.sanctum` name already resolves to production Kvin YXORP. The existing route forwards to Kvar LinkStack `:8081` until this update is applied.
- The isolated Firefox and SSH-tunnel proposal is **withdrawn**. Use the real production browser path. No DNS, firewall, or special client configuration is needed.

## Switch one existing production upstream

Once the updated Services source CI has passed, run on **Kvin as `wdc2`**:

```bash
cd ~/src/sanctum-services && git pull &&
~/.local/bin/ansible-navigator run ansible/yxorp.yml \
  -e yxorp_production_cutover_approved=true
```

This uses the **existing** production YXORP deployment play and role. The only intended change to the live Nginx upstream configuration is `dir.nexus.sanctum` from `kvar.outer.sanctum:8081` to **`127.0.0.1:18081` on Kvin**. Its shared production Nginx service may restart briefly to load the new source-managed config. The play verifies the Kvin LinkStack listener first and the resulting production `dir` HTTP response afterward. Other seven routes, including Kuma, stay as they are. Do **not** stop Kvar LinkStack yet.

In your ordinary Firefox profile, load **`http://dir.nexus.sanctum/`**, check that the directory and links work, then visit **`http://dir.nexus.sanctum/login`** and privately sign in to check the dashboard and recognizable original data. Do not send passwords, cookies or session tokens to chat. If it works, report acceptance; retiring/stopping the old Kvar service is a later, ordinary housekeeping action.

## Roll back if the real service fails

Keep the old Kvar LinkStack running and its data untouched until acceptance. On **Kvin**, rerun the same source-owned production play with just one backend override:

```bash
cd ~/src/sanctum-services &&
~/.local/bin/ansible-navigator run ansible/yxorp.yml \
  -e yxorp_production_cutover_approved=true \
  -e yxorp_production_linkstack_backend=kvar
```

This restores **only** the LinkStack `dir` origin to `kvar.outer.sanctum:8081` while preserving the other seven YXORP routes. Then retest the normal URL. If this rollback is used as the ongoing desired configuration, reconcile that selected state into Git rather than allowing a later default run to switch back unintentionally.

LinkStack is stateful: new edits made against Kvin **after** the switch are not automatically synchronized back to Kvar. If you make new edits before rollback, decide whether they need copying. There is no reason to delay this trial over a speculative failure.

The earlier isolated-browser validation plan was superseded by Nova's explicit direct production test decision on November 12. Historical read-only qualification receipts are retained in `PROJECT_LEAD_INTRODUCTION.md` and issue #2.
