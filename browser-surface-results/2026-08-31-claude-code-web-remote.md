# Browser surface test: Claude Code on the web (remote container) — no browser surface exposed

- Date and local time: 2026-08-31 11:46 UTC (container TZ = UTC)
- Product, app and version: Claude Code 2.1.251, `origin: web_claude_ai`, environment kind `anthropic_cloud`, environment `env_019kvNdUFTaAbmz1F44nmPSN`
- Model: `claude-opus-5` (`session_context.model` = claude-opus-5; `external_metadata.last_served_model` = claude-opus-5)
- Operating system: Ubuntu 24.04.4 LTS, Linux 6.18.44-fc-v22 x86_64 (ephemeral container)
- Requested surface: not named at invocation. Per the prompt's Claude Code rule, the target was Claude in Chrome.
- Actual backend or surface: **none exposed.** No browser-control tool namespace exists in this conversation. Identified by tool-schema enumeration (`ToolSearch`) plus MCP/plugin config inspection — method recorded in §1.
- Browser and version, if visible: no agent-controllable browser. A Playwright-managed Chromium binary exists on disk (`/opt/pw-browsers/chromium` -> `chromium-1194`, Playwright CLI 1.56.1) but is a shell asset, not an agent browser surface.
- Working directory: `/home/user/experiments` (git repo `alejoacelas/experiments`, branch `main`)
- Result file: `browser-surface-results/2026-08-31-claude-code-web-remote.md`
- Overall result: SURFACE UNAVAILABLE

## Run identity

| Field | Value | How observed |
|---|---|---|
| Session origin | `web_claude_ai`, `environment_kind: anthropic_cloud` | `get_session` (claude-code-remote MCP), `session_id` omitted |
| Container CC version | 2.1.251 | `get_session` -> `external_metadata.container_cc_version`; matches `claude --version` in shell |
| Model | configured `claude-opus-5`; last served `claude-opus-5` | `get_session` -> `session_context.model`, `external_metadata.last_served_model` |
| Permission mode | `auto` | `get_session` -> `permission_mode` |
| OS | Ubuntu 24.04.4 LTS, kernel 6.18.44-fc-v22 x86_64 | `cat /etc/os-release; uname -srm` |
| Egress | agent proxy at `127.0.0.1:43055`, `selective: false`, `toolScoped: false` | `curl -sS "$HTTPS_PROXY/__agentproxy/status"` |
| Clock / TZ | 2026-08-31T11:45:23+00:00, TZ=UTC | `date -Is; date +%Z` |

## Executive result

**Overall: SURFACE UNAVAILABLE.**

Two independent blockers were established empirically, and they sit at different layers. Neither
was inferred from documentation; documentation was not consulted before testing.

1. **No agent browser surface exists in this conversation.** No browser-control tool namespace is
   exposed — not Claude in Chrome, not a Cowork built-in browser, not a Playwright/CDP MCP server,
   not a computer-use primitive. Tool-schema enumeration returned zero browser-control tools, and
   the MCP server list for this workspace is empty. Limiting layer: **routing or provisioning**
   (no browser backend was provisioned to this remote session), compounded by **agent tool
   wrapper** (no wrapper exists to expose one).
2. **Every named public test page is unreachable from this container.** The environment's network
   policy allowlists only `*.80000hours.org` (plus proxy-injected `*.googleapis.com` Drive paths).
   All four test hosts fail at the CONNECT stage. Limiting layer: **product policy** (admin-set
   network allowlist on the remote environment).

Because blocker 1 alone makes §2–§12 impossible, and blocker 2 would independently prevent them
even if a browser surface were attached, no browser action was ever dispatched. Per the evidence
rules, nothing here is marked PASS, and no shell/HTTP substitute was used to manufacture a pass.

A **non-surface engine probe** (explicitly not a substitute test, and reported separately)
confirms the layering: a real Chromium 141.0.7390.37 launches successfully inside the container
via Playwright 1.56.1, and then fails to load `https://example.com/` with
`net::ERR_TUNNEL_CONNECTION_FAILED`. So the missing piece at layer 1 is the agent-facing surface,
not a browser engine; and layer 2 blocks the engine that does exist.

Elapsed, §1 surface identification: **72 s** (11:45:23Z first inspection -> 11:46:35Z identity
capture complete). Engine probe: **2.703 s** wall clock (reported by the probe itself).

## Live capability inventory

Tool schemas in this session **are** inspectable: the harness lists deferred tools by name and
`ToolSearch` returns full JSONSchema for any match. This is what makes the negative result solid
rather than an assumption — the capability list was read, not guessed.

Full set of tool namespaces visible: core harness tools (Bash, Read, Write, Edit, Glob, Grep,
Agent, Artifact, ToolSearch, Task*, Skill, Monitor, WebFetch, WebSearch, …) and MCP servers
`github`, `Gmail`, `Gdoc_connector_v1`, `Google_Calendar`, `Google_Drive`, `Vercel`,
`Wispr_Flow`, `Claude_Code_Remote`. None of these is a browser-control surface.

| Capability | Advertised by live runtime? | Primitive or tool | Evidence |
|---|---|---|---|
| Browser navigation (open/goto) | No | none | `ToolSearch "+chrome"` -> `No matching deferred tools found`; `ToolSearch "+browser"` -> only `WebFetch` (matched on description text, it is an HTTP fetcher) |
| Tab listing / switching / close | No | none | same enumeration; no tab primitive in any namespace |
| DOM snapshot / query | No | none | same enumeration |
| Accessibility tree | No | none | same enumeration |
| Screenshot | No | none | `ToolSearch "browser chrome tab navigate page screenshot"` -> returned only Google Docs tab tools, WebFetch, GitHub tools |
| Coordinate / pixel input | No | none | same enumeration; no computer-use tool present |
| JavaScript evaluation in page | No | none | same enumeration |
| Console log read | No | none | same enumeration |
| Network log / HAR | No | none | same enumeration |
| Raw CDP / devtools protocol | No | none as an agent primitive | no CDP tool; no CDP listener found (`ss -ltnp` returned no listening sockets) |
| Viewport / emulation control | No | none | same enumeration |
| Browser downloads | No | none | same enumeration |
| File chooser / upload into page | No | none | same enumeration |
| Clipboard access | No | none | same enumeration |
| Browser history / bookmarks / tab groups | No | none | same enumeration |
| Authentication assistance / passkey handoff | No | none | same enumeration |
| Browser management (launch/claim/release) | No | none | same enumeration |
| HTTP fetch (not a browser action) | Yes | `WebFetch`, `WebSearch`, `curl` via Bash | present, but the prompt's evidence rules bar these as substitutes; not used as such |
| Browser **engine** on disk (not an agent surface) | Yes, as a shell asset | `/opt/pw-browsers/chromium`, Playwright 1.56.1 | `ls -la /opt/pw-browsers`; `playwright --version` -> `Version 1.56.1`; probe launched Chromium 141.0.7390.37 |

Which capabilities are always present vs. requested at runtime: all tool schemas are either listed
up front or fetchable on demand via `ToolSearch`. No browser capability appeared in either tier,
so there is no "request it at runtime" path — the absence is not a discovery gap.

Method used to acquire/claim/connect to a target browser: **none available to attempt.** There is
no claim, connect, attach or acquire primitive. No CDP endpoint was listening to connect to.

## Test results

### 1. Surface identification

Status: **UNAVAILABLE** — no browser backend exposed.

Exact steps and arguments:

- `ToolSearch(query="browser chrome tab navigate page screenshot", max_results=15)` -> returned
  `mcp__Gdoc_connector_v1__add_tab`, `mcp__Gdoc_connector_v1__list_tabs`,
  `mcp__Gdoc_connector_v1__table_of_contents`, `WebFetch`, plus Gdoc/GitHub/Drive tools. The
  "tab" matches are Google Docs document tabs, not browser tabs.
- `ToolSearch(query="+chrome", max_results=10)` -> `No matching deferred tools found`
- `ToolSearch(query="+browser", max_results=10)` -> `WebFetch` only.
- `python3` inspection of `/root/.claude.json` -> `/projects//home/user/experiments/mcpServers -> []`
  (no workspace MCP servers configured).
- `ls ~/.claude/plugins/synced/...` -> single plugin `google-drive`. No browser plugin.
- `ss -ltnp` -> no listening TCP sockets, so no pre-existing CDP endpoint to attach to.
- No `chromium`/`google-chrome`/`chrome` on `PATH` (`command -v` for each -> not found); the only
  binary is the Playwright-managed one under `/opt/pw-browsers`.

**Tab inventory:** not applicable and not attempted — tab listing is UNAVAILABLE, so the profile
inheritance test could not begin. Zero pre-existing tabs were observed because no tab primitive
exists to observe them. No pre-existing or private tab was navigated or inspected.

Seconds: 72.

### 2. Common read baseline

Status: **UNAVAILABLE** (no navigation or read primitive). Independently **BLOCKED** at the
network layer.

`https://example.com/` was never opened in a browser. The site's reachability from this container
was probed only to characterize the environment, never as a page-read substitute:

```
$ curl -sS -o /dev/null -w "code=%{http_code}\n" --max-time 20 https://example.com/
curl: (56) CONNECT tunnel failed, response 403
code=000
```

Control, proving the network path itself works and the block is host-scoped policy:

```
$ curl -sS -o /dev/null -w "80000hours.org -> HTTP %{http_code}\n" --max-time 25 https://80000hours.org/
80000hours.org -> HTTP 200
```

Requested URL: `https://example.com/`. Final URL: not reached. Title: not read. First heading: not
read. No screenshot artifact exists — no screenshot primitive. No primitive-vs-primitive title
comparison was possible, since zero read primitives exist.

Seconds: action never dispatched; 1 s spent establishing the network block.

### 3. Navigation and tabs

Status: **UNAVAILABLE**. No navigate, back, forward, reload, tab-list, tab-switch or tab-close
primitive exists. `https://the-internet.herokuapp.com/` is additionally BLOCKED:

```
$ curl -sS -o /dev/null -w "code=%{http_code}\n" --max-time 20 https://the-internet.herokuapp.com/
curl: (56) CONNECT tunnel failed, response 403
code=000
```

No tab was created, so foreground/background/hidden visibility could not be characterized, and no
ownership/claim/release/handoff semantics were exposed to exercise.

Seconds: action never dispatched.

### 4. Semantic and visual actions

Status: **UNAVAILABLE**. No click primitive of any kind — neither semantic (role/label/DOM
locator) nor coordinate-based. `/add_remove_elements/` is on the BLOCKED host above. Before/after
`Delete` button counts: not observed.

Seconds: action never dispatched.

### 5. Difficult page structures

Status: **UNAVAILABLE** for all six sub-tests; host additionally BLOCKED.

| Sub-test | Page | Status | Note |
|---|---|---|---|
| Dynamic content | `/dynamic_loading/2` | UNAVAILABLE | no wait/condition primitive exists |
| JavaScript dialog | `/javascript_alerts` | UNAVAILABLE | no dialog handling primitive |
| Iframe | `/iframe` | UNAVAILABLE | no frame primitive; nothing typed anywhere |
| Nested frames | `/nested_frames` | UNAVAILABLE | no frame primitive |
| Shadow DOM | `/shadowdom` | UNAVAILABLE | no DOM/JS primitive |
| Pop-up / new target | `/windows` | UNAVAILABLE | no target-discovery primitive |

Seconds: action never dispatched.

### 6. Developer and diagnostic primitives

Status: **UNAVAILABLE** for every item.

- `document.title` / `window.location.href` evaluation: no JS-evaluation primitive.
- DOM snapshot: no primitive.
- Accessibility role and name of the Example Domain link: no accessibility primitive.
- HTTP 500 via network log (`/status_codes/500`): no network-log primitive; host also BLOCKED.
- Console log read + `browser-surface-probe-console` emission: no console primitive, and no JS
  evaluation to emit with. The probe string was never emitted.
- Request/response headers and bodies: no primitive. No cookie/authorization header was read.
- DOM/CSS inspection (tag name, bounding box, computed font size): no primitive.
- Trace / HAR / GIF / video replay artifact: no primitive.
- Raw CDP: no CDP tool, and `ss -ltnp` showed no listening socket, so no protocol surface to
  enumerate. Reporting zero exposed CDP domains — not inferred from a single command's absence,
  but from the absence of any connect path.

Limiting layer for all of the above: **routing or provisioning** / **agent tool wrapper** — no
browser backend was attached to this session, so none of these could be gated by the browser,
the profile, or user permission. The evidence distinguishes this cleanly: the container *has* a
browser engine, so the limitation is not "the browser cannot".

### 7. Viewport and emulation

Status: **UNAVAILABLE**. No viewport primitive is exposed. Per the instruction, **no workaround
was attempted** — nothing was resized, and no emulation (device, touch, color-scheme,
geolocation, locale, time-zone, CPU, network) primitive exists to list or exercise. No
`window.innerWidth` / `innerHeight` / `devicePixelRatio` values were read, and no screenshot with
pixel dimensions exists.

Seconds: action never dispatched.

### 8. Downloads and uploads

Status: **UNAVAILABLE** for the browser-boundary questions; the local-file half was performed.

The disposable probe file **was** created, since that step is a filesystem action rather than a
browser action:

```
$ printf 'browser-surface-probe-2026' > <scratch>/browser-surface-probe.txt
```

Path (home prefix redacted): `<home>/../scratchpad/browser-surface-probe.txt` under the session
scratchpad. Tool used: `Bash` heredoc/printf. Content verified by `cat` as exactly
`browser-surface-probe-2026` (26 bytes, no trailing newline).

- Download from `/download`: **UNAVAILABLE** — no download primitive; host also BLOCKED. No file
  was created, and page navigation to a file URL was correctly not counted as a download.
- File selection on `https://www.selenium.dev/selenium/web/web-form.html`: **UNAVAILABLE** — no
  file-chooser primitive. The host is additionally BLOCKED:
  `curl: (56) CONNECT tunnel failed, response 403`. The form was not submitted and the probe file
  was never published anywhere.

Distinguishing the five upload layers: only the first is answerable from evidence — there is **no
page-level file chooser primitive** (agent tool wrapper / provisioning). Local filesystem access
**is** present and demonstrated. A product allowlist, a native OS dialog and an anti-automation
upload policy were never reached, so they are `INCONCLUSIVE` rather than absent.

Cleanup of the probe file is recorded in §14.

### 9. Cookies and session persistence

Status: **UNAVAILABLE** (no browser to hold a cookie jar); `httpbin.org` additionally **BLOCKED**:

```
$ curl -sS -o /dev/null -w "code=%{http_code}\n" --max-time 20 https://httpbin.org/
curl: (56) CONNECT tunnel failed, response 403
code=000
```

No synthetic cookie was set, because setting one via `curl` would not be a browser action and
would produce a value no browser ever held. The raw cookie store was not inspected — there is no
store and no primitive. Tab-sharing, tab-close persistence and reload persistence: not observable
without tabs. App-restart persistence: **NOT TESTED** (restarting would lose this run).

The The Internet login with the public credentials `tomsmith` / `SuperSecretPassword!` was **not
performed**: the host is blocked and no browser exists to submit a form. No credential was entered
anywhere, no `/secure` URL was reached, and consequently no logout was required.

### 10. Regular-profile reuse

Status: **UNAVAILABLE** across the board — and this is the cleanest structural finding of the run.

This session is a fresh ephemeral cloud container with a repository cloned at start. There is no
user browser attached to it, no browser profile, and no extension host. Concretely:

- Pre-existing regular-browser tabs visible to the surface: **none observable** — no tab
  primitive. Counts and domains: not applicable. No pre-existing tab was opened or inspected.
- Signed-in state on a pre-existing tab: not observable. No account name was recorded and no
  private content was inspected.
- Ordinary browser extensions active on a test page: **UNAVAILABLE** — no page and no extension
  host. No extension data or configuration was enumerated.
- Browser history / bookmarks / tab groups as agent primitives: **UNAVAILABLE**. No such tool
  exists in any namespace; no contents were read. Required permission: not applicable, since no
  permission would attach a capability that does not exist here.
- Password manager / passkey handoff: **UNAVAILABLE**. No vault was opened, no password
  retrieved, no passkey created.
- Cookie or profile import into a built-in browser: **NOT TESTED** — this product surface offers
  no importer at all, so `httpbin.org` could not be offered as a selectable source and the
  site-level isolation precondition could not be met. The import was correctly not broadened.
- Import synchronization follow-up (change source cookie, reload destination): **NOT TESTED**,
  since no import occurred. Nothing here generalizes to passkeys or OAuth refresh tokens.

The distinction the section is designed to draw — "extension using the user's browser" vs.
"separate browser profile" — resolves to a third case here: **neither.** There is no browser
profile of any kind in this execution surface.

### 11. Sessions and subagents

Status: browser concurrency **UNAVAILABLE**; subagent dispatch **PASS**; subagent browser access
**UNAVAILABLE** (a separate, independently established result).

**Parent concurrency.** Could not be tested: no tab primitive, so two test tabs
(`?owner=parent-a`, `?owner=parent-b`) could never be opened, no titles could be read, and no
backend/context identifier exists to decide between "two tabs in one profile", "two isolated
contexts" and "two browser sessions". No second browser session or context was created, because
the live API exposes no such operation. Deliberately not called "two sessions" — there were zero.

**Subagents.** This product does expose subagents (`Agent` tool, `subagent_type` values including
`general-purpose`, `Explore`, `Plan`). Two were dispatched concurrently with the exact tasks
specified. Both completed and returned structured evidence; neither wrote this report.

| | Subagent A | Subagent B |
|---|---|---|
| Task | open `example.com/?owner=subagent-a`, read title + heading | open `/add_remove_elements/?owner=subagent-b`, add/verify/remove |
| `BROWSER_TOOL_NAMES` | none | none |
| `BACKEND_OR_SESSION_IDENTIFIERS` | none exposed | none exposed |
| `FINAL_URL` | not reached | not reached |
| Observed values | title not read, heading not read | Delete counts: not observed (before/after-add/after-remove) |
| `STATUS` | UNAVAILABLE | UNAVAILABLE |
| `EXACT_ERROR_TEXT` | `No matching deferred tools found` | `No matching deferred tools found`; `ls: cannot access '/root/.cache/ms-playwright': No such file or directory` |
| Duration | 45.588 s, 8 tool uses | 42.489 s, 8 tool uses |

Both independently reproduced the parent's enumeration result via `ToolSearch "+browser"` (returns
only `WebFetch`) and `ToolSearch "+chrome"` (returns `No matching deferred tools found`), and both
declined to substitute `WebFetch` for a browser action. So: **subagents can be created, and they
receive no browser tools** — the two distinct UNAVAILABLE results the section asks to separate.

**Correction to subagent-reported evidence.** Both subagents additionally asserted that no
Playwright browser engines are installed, citing the absence of `~/.cache/ms-playwright`. That
conclusion is wrong and is not carried into this report: they missed
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`. The parent verified directly that
`/opt/pw-browsers/chromium` exists and launches (Chromium 141.0.7390.37). Their core finding — no
browser tool namespace — is confirmed and consistent with the parent's.

**Concurrency actually observed:** agent-level concurrency is real. The two subagents ran in
parallel (overlapping 45.6 s and 42.5 s runs) while the parent continued writing this report.
Browser access was never serialized or contended, because there was no browser lock to contend
for. No subagent displaced, renamed, navigated, closed or blocked any tab — there were no tabs.
No subagent tabs persisted or required handoff. Nothing needed closing in cleanup.

**Parent tab list after subagents:** not applicable; no tab primitive. The parent could not see
subagent tabs, and no backend/browser/session/context/tab identifiers exist on either side to
compare.

### 12. Reliability sequence

Status: **UNAVAILABLE** — the ten-step sequence was never started, because step 1 (navigate)
has no primitive and the target host is blocked. No step was retried.

| Step | Action | Tool response | Independently observed state |
|---|---|---|---|
| 1 | navigate `/add_remove_elements/` | no tool to call | — |
| 2 | add one element | no tool to call | — |
| 3 | add a second element | no tool to call | — |
| 4 | remove one element | no tool to call | — |
| 5 | reload, verify zero | no tool to call | — |
| 6 | navigate `/status_codes/200` | no tool to call | — |
| 7 | go back | no tool to call | — |
| 8 | open new tab on Example Domain | no tool to call | — |
| 9 | close that tab | no tool to call | — |
| 10 | return to original tab, read URL | no tool to call | — |

Counts: verified actions **0**; tool errors **0**; claimed successes without the expected state
change **0**; unexpected confirmations **0**; backend changes or disconnects **0**; actions
requiring manual recovery **0**.

The zeros in rows 3–6 are not a clean bill of health — they are the arithmetic consequence of
zero dispatched actions. This run produced no evidence about the surface's false-success rate.

### 13. Policy and human handoffs

| Product behaviour | Observed? | Evidence |
|---|---|---|
| Asked user to choose/approve a site, credential, file, download or sensitive action | No | permission mode `auto`; no approval prompt fired during the run |
| Required the user to take control of the browser | No | no browser exists to hand over |
| Blocked a site despite the browser being technically able to display it | **Yes** | Chromium launched and could render, but `example.com` and the other three hosts fail with `net::ERR_TUNNEL_CONNECTION_FAILED` / `curl: (56) CONNECT tunnel failed, response 403`, while `80000hours.org` returns HTTP 200. This is an admin network allowlist on the remote environment, not a browser limitation. |
| Hid secret values from the model while still completing authentication | Partially, unrelated to browsing | `env` shows `GITHUB_TOKEN=proxy-injected`, `AWS_SECRET_ACCESS_KEY=proxy-injected` — credentials are injected at the proxy and never exposed to the model. No browser authentication was involved. |
| Refused to inspect cookies, storage, browser internals or another tab | No refusal observed | Nothing refused the request; the primitives simply do not exist. Distinguishing a refusal from an absence: absence, on the enumeration evidence. |
| Routed the task to a different tool or browser | No, and no silent fallback was taken | The only web-reaching tools are `WebFetch`, `WebSearch` and `curl`. Per the evidence rules none was used as a browser substitute. |

Separation of policy from missing primitives:

- **Product policy** (clear): the host allowlist blocking all four test sites.
- **Routing or provisioning** (clear): no browser backend attached to this cloud session.
- **Agent tool wrapper** (clear): no wrapper exposes browser control to parent or subagents.
- **User permission** vs. product policy for browser access specifically: **INCONCLUSIVE** — no
  prompt or permission gate was ever reached, so the run cannot tell whether a permission exists
  that would attach a browser if granted.

### 14. Cleanup

- The Internet public test session: **no logout needed** — never logged in (host blocked, no
  browser).
- Tabs created by this run: **none**; nothing to close. No pre-existing tab was touched, closed or
  modified.
- Disposable local files removed: the probe file and the engine-probe script (both created by this
  run). Commands and verification recorded below.
- Not done, as instructed: no browser profile, history, Downloads folder or cookie store was
  cleared. None exists here in any case.
- Report and artifacts preserved.

**Turn-end tab behaviour:** not observable — no agent tabs exist. Recorded as such rather than
delaying the report to discover it.

### Consolidated per-test table

Seconds are wall-clock for the work actually performed in that section. Where no browser action
could be dispatched, the figure is the time spent establishing that fact, and is marked `est.`
only where it was not separately timed.

| Test | Status | Tool or primitive | Before | Action | After | Human intervention | Seconds | Artifact |
|---|---|---|---|---|---|---|---:|---|
| 1. Surface identification | UNAVAILABLE | `ToolSearch` x3, `Bash` (config/PATH/socket inspection) | unknown tool surface | enumerate all tool schemas + MCP + plugins + listeners | zero browser-control tools; `mcpServers: []` | none | 72 | this report |
| 2. Common read baseline | UNAVAILABLE | none exists | no tab | none dispatched | no page opened; host 403 | none | 1 | curl transcript in §2 |
| 3. Navigation and tabs | UNAVAILABLE | none exists | no tab | none dispatched | no tab created | none | 1 | curl transcript in §3 |
| 4. Semantic and visual actions | UNAVAILABLE | none exists | counts not observable | none dispatched | counts not observable | none | 0 | — |
| 5. Difficult page structures | UNAVAILABLE | none exists | n/a | none dispatched | n/a | none | 0 | — |
| 6. Developer and diagnostic primitives | UNAVAILABLE | none exists; no CDP listener | n/a | `ss -ltnp` for CDP endpoint | no listening socket | none | 2 | §6 |
| 7. Viewport and emulation | UNAVAILABLE | none exists | n/a | none dispatched (no workaround attempted) | n/a | none | 0 | — |
| 8. Downloads and uploads | UNAVAILABLE (browser half); local file created | `Bash` `printf` | no probe file | create + verify probe file | 26-byte file, content `browser-surface-probe-2026` | none | 3 | probe file (since deleted) |
| 9. Cookies and session persistence | UNAVAILABLE | none exists | no cookie jar | none dispatched; no credential entered | httpbin 403 | none | 1 | curl transcript in §9 |
| 10. Regular-profile reuse | UNAVAILABLE | none exists | no profile | none dispatched | no browser profile in this surface | none | 0 | — |
| 11. Sessions and subagents | subagents PASS; their browser access UNAVAILABLE | `Agent` (`general-purpose`) x2 | no subagents | dispatch 2 concurrent subagents with fixed tasks | both returned `STATUS: UNAVAILABLE`, `BROWSER_TOOL_NAMES: none` | none | 46 | subagent structured reports, §11 |
| 12. Reliability sequence | UNAVAILABLE | none exists | n/a | sequence never started | 0 of 10 steps dispatched | none | 0 | §12 |
| 13. Policy and human handoffs | PASS (observation complete) | `Bash` env/proxy inspection | unknown policy | read proxy status + allowlist behaviour | host allowlist confirmed as the blocking policy | none | 4 | §13, proxy status JSON |
| 14. Cleanup | PASS | `Bash` `rm` | 2 disposable files | delete probe + engine-probe script | both absent; nothing else touched | none | 2 | §14 |

## Capability matrix

| Capability | Status | Live evidence | Limiting layer | Confidence |
|---|---|---|---|---|
| Browser surface attached to session | UNAVAILABLE | `ToolSearch "+chrome"` -> `No matching deferred tools found`; `"+browser"` -> only `WebFetch`; workspace `mcpServers: []` | routing or provisioning | High |
| Navigate to URL | UNAVAILABLE | no navigation primitive in any namespace | agent tool wrapper | High |
| Read page title | UNAVAILABLE | no read primitive | agent tool wrapper | High |
| Read first heading | UNAVAILABLE | no read primitive | agent tool wrapper | High |
| DOM snapshot / query | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Accessibility tree | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Screenshot | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Coordinate / pixel input | UNAVAILABLE | no computer-use primitive | agent tool wrapper | High |
| JavaScript evaluation | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Console log read | UNAVAILABLE | no primitive; probe string never emitted | agent tool wrapper | High |
| Network log / HTTP status capture | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Request/response headers and bodies | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Raw CDP / devtools protocol | UNAVAILABLE | no CDP tool; `ss -ltnp` shows no listening socket to attach to | agent tool wrapper | High |
| Tab list / switch / close | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Wait-for-condition primitive | UNAVAILABLE | no primitive | agent tool wrapper | High |
| JS dialog handling | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Iframe / nested frame access | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Shadow DOM access | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Viewport control | UNAVAILABLE | no primitive; no workaround attempted per instruction | agent tool wrapper | High |
| Device / touch / color-scheme emulation | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Geolocation / locale / timezone / CPU / network emulation | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Browser download to filesystem | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Page file chooser / upload | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Local filesystem read/write | PASS | probe file created and verified: 26 bytes, `browser-surface-probe-2026` | none observed | High |
| Clipboard access | UNAVAILABLE | no primitive | agent tool wrapper | High |
| Cookie set/read via page | UNAVAILABLE | no browser; httpbin blocked | agent tool wrapper | High |
| Session persistence across tabs | UNAVAILABLE | no tabs exist | agent tool wrapper | High |
| Session persistence across app restart | NOT TESTED | restart would lose this run | unknown | High |
| Form login with public test credentials | UNAVAILABLE | no browser; host blocked; no credential entered | agent tool wrapper | High |
| Pre-existing user tab visibility | UNAVAILABLE | no tab primitive; ephemeral cloud container has no user browser | routing or provisioning | High |
| Browser extensions active on page | UNAVAILABLE | no browser profile / extension host | browser profile | High |
| Browser history / bookmarks / tab groups | UNAVAILABLE | no primitive; contents not read | agent tool wrapper | High |
| Password manager / passkey handoff | UNAVAILABLE | no primitive; no vault opened | agent tool wrapper | High |
| Cookie or profile import | NOT TESTED | no importer exists, so httpbin could not be offered as an isolatable source | agent tool wrapper | High |
| Subagent creation | PASS | 2 `Agent` calls completed, 45.588 s / 42.489 s, structured reports returned | none observed | High |
| Subagent browser access | UNAVAILABLE | both returned `BROWSER_TOOL_NAMES: none`, `STATUS: UNAVAILABLE` | agent tool wrapper | High |
| Concurrent browser sessions/contexts | UNAVAILABLE | no session/context creation operation exposed | agent tool wrapper | High |
| Reach `example.com` | BLOCKED | `curl: (56) CONNECT tunnel failed, response 403`; Chromium: `net::ERR_TUNNEL_CONNECTION_FAILED` | product policy | High |
| Reach `the-internet.herokuapp.com` | BLOCKED | same 403 / `ERR_TUNNEL_CONNECTION_FAILED` | product policy | High |
| Reach `httpbin.org` | BLOCKED | `curl: (56) CONNECT tunnel failed, response 403` | product policy | High |
| Reach `selenium.dev` web-form | BLOCKED | `curl: (56) CONNECT tunnel failed, response 403` | product policy | High |
| Browser engine present in container (not a surface) | PASS | Chromium 141.0.7390.37 launched via Playwright 1.56.1 from `/opt/pw-browsers/chromium` | none observed | High |

## Credential and profile model

Only what this run demonstrated:

- **Existing session reuse:** none possible. The surface is an ephemeral Anthropic-managed cloud
  container with no attached user browser and no browser profile. There is no signed-in state to
  inherit, and no pre-existing tab was visible or inspected.
- **New login state:** not established. No login was attempted; the public The Internet
  credentials were never entered anywhere.
- **Synthetic cookie sharing between tabs:** not observable. No cookie was set, no tab exists.
- **Cookie or profile import:** no import mechanism exists on this surface.
- **Password-manager / passkey handoff:** no mechanism exists. No vault, password or passkey was
  touched.
- **Persistence boundaries:** the one persistence fact this run does establish is at the container
  level, not the browser level — the container filesystem persists within the session and is
  reclaimed after inactivity, so any browser state would be session-scoped at best.
- **Credential handling observed (non-browser):** the agent proxy injects credentials for
  allowlisted hosts and the model never sees them (`GITHUB_TOKEN=proxy-injected`,
  `AWS_SECRET_ACCESS_KEY=proxy-injected`, `CLOUDSDK_AUTH_ACCESS_TOKEN=proxy-injected`). No secret
  value was read or recorded.

## Browser topology

Identifiers below are only those actually returned by tools. Nothing is invented.

```
claude.ai/code  (origin: web_claude_ai)
      |
      v
Anthropic-managed cloud VM   environment_id = env_019kvNdUFTaAbmz1F44nmPSN
  session_id = session_015u7X6kALbrjEspgNULByNK
  Claude Code 2.1.251 | model claude-opus-5 | Ubuntu 24.04.4
  cwd /home/user/experiments  (repo alejoacelas/experiments @ main)
      |
      +-- Parent agent
      |     |-- browser backend: (none)          <-- no tool namespace, no session id, no context id
      |     |-- tabs: (none)
      |     '-- egress: agent proxy 127.0.0.1:43055
      |            allow: *.80000hours.org -> HTTP 200
      |            deny : example.com / the-internet.herokuapp.com /
      |                   httpbin.org / selenium.dev -> CONNECT 403
      |
      +-- Subagent A (general-purpose)           browser backend: (none)   tabs: (none)
      |
      +-- Subagent B (general-purpose)           browser backend: (none)   tabs: (none)
      |
      '-- [shell-only, NOT an agent surface]
            Playwright 1.56.1 -> /opt/pw-browsers/chromium
            Chromium 141.0.7390.37 launches OK
            then blocked: net::ERR_TUNNEL_CONNECTION_FAILED
```

No browser session, context, target or tab identifier exists anywhere in this topology, in the
parent or in either subagent.

## Failures and exact errors

Verbatim, none truncated (all under 500 characters):

1. Tool enumeration, parent and both subagents:
   `No matching deferred tools found`
2. All four named test hosts, via `curl -sS --max-time 20`:
   `curl: (56) CONNECT tunnel failed, response 403`
   with `code=000` from the write-out format.
3. Browser engine probe via Playwright:
   `GOTO https://example.com/: FAILED: Error: page.goto: net::ERR_TUNNEL_CONNECTION_FAILED at https://example.com/`
   `GOTO https://the-internet.herokuapp.com/: FAILED: Error: page.goto: net::ERR_TUNNEL_CONNECTION_FAILED at https://the-internet.herokuapp.com/`
4. Subagent B, checking the default Playwright cache path:
   `ls: cannot access '/root/.cache/ms-playwright': No such file or directory`
   — this one is a **misleading** error. It reflects looking in the wrong directory, not an absent
   engine; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` holds the engines. Recorded here so the
   discrepancy is visible rather than silently reconciled.

Control result proving the block is host-scoped rather than a dead network:
`80000hours.org -> HTTP 200`

## Artifacts

| Artifact | Location | Retained? |
|---|---|---|
| This report | `browser-surface-results/2026-08-31-claude-code-web-remote.md` | Yes |
| Proxy status JSON | quoted inline in §Run identity / §13 | Yes (inline) |
| Engine probe script | `<scratch>/engine-probe.js` | No — deleted in cleanup |
| Probe file | `<scratch>/browser-surface-probe.txt` | No — deleted in cleanup |
| Screenshots | none | No screenshot primitive exists |
| Trace / HAR / video | none | No such primitive exists |
| Subagent structured reports | quoted in §11 | Yes (inline) |

## Remaining unknowns

Each with the exact next experiment that would settle it.

1. **Would Claude in Chrome attach if this task were run from the Claude Code CLI on a desktop
   with the Chrome extension installed?** Unknown — this run only shows it is absent from a cloud
   session. Next experiment: run this identical prompt from a local `claude` CLI on a machine with
   Claude in Chrome connected, and re-run §1 enumeration.
2. **Is browser access withheld from cloud sessions by product design, or merely not provisioned
   to this environment?** The evidence cannot distinguish these. Next experiment: create a second
   cloud environment with a different network access level and check whether any browser tool
   namespace appears in `ToolSearch "+browser"`.
3. **Would the four test hosts become reachable under a more permissive environment access
   level?** Next experiment: set the cloud environment's network access to a level that allowlists
   `example.com`, `the-internet.herokuapp.com`, `httpbin.org` and `selenium.dev`, then re-run the
   `curl` reachability probe and the Chromium engine probe.
4. **Every capability in §2–§12** — the surface's real behaviour on dynamic content, dialogs,
   iframes, shadow DOM, viewport, downloads, uploads, cookies and false-success rate. Next
   experiment: re-run this prompt unchanged on a surface that passes §1, so the sequence actually
   dispatches.
5. **Restart persistence (§9).** Next experiment: on a surface with a browser, set the synthetic
   cookie, restart the app, and re-open `/cookies` in a run whose report is already saved.
6. **Whether a user-permission gate exists that would attach a browser.** Next experiment: attempt
   a browser action on a surface where the tool exists but is ungranted, and record whether a
   permission prompt appears rather than a missing tool.

## Documentation appendix

Consulted **after** all testing was complete. Nothing below is used as evidence that a test passed,
and no observed failure was revised to match it.

Source: [Use Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web),
fetched via `WebFetch`.

- `documented`: "Claude Code on the web runs tasks on Anthropic-managed cloud infrastructure at
  claude.ai/code" in an "isolated, Anthropic-managed VM". **Agrees** with the observed result: an
  isolated cloud VM has no user browser to inherit, which is exactly what §10 found.
- `documented`: "Network access controls: in Anthropic-hosted environments, network access is
  limited by default and can be disabled." **Agrees** with the observed 403 CONNECT failures on all
  four test hosts alongside HTTP 200 on the admin-allowlisted host, and supports classifying the
  limiting layer as product policy rather than a browser limitation.
- `documented`: "Every cloud session runs in a cloud environment, the saved configuration that
  controls network access, environment variables, and setup scripts." **Agrees**; identifies the
  configuration surface that would settle unknown 3 above.
- `documented`: "Subagents work the same way they do locally. Claude can spawn them with the Agent
  tool." **Agrees** with §11: subagents spawned successfully. The docs do not claim subagents
  receive browser tools, and none did.
- `documented`: the page's feature list, command tables and Limitations section make **no mention
  of a browser-control surface, a built-in browser, or Claude in Chrome** for cloud sessions.
  **Agrees** with the observed absence. Note this is an argument from silence in the docs; the
  observed result stands on the enumeration evidence in §1, not on this.
- **No disagreement** between documentation and observation was found in this run.

### Cleanup verification

```
$ rm -f <scratch>/browser-surface-probe.txt <scratch>/engine-probe.js
$ ls <scratch>/browser-surface-probe.txt
ls: cannot access '.../browser-surface-probe.txt': No such file or directory
$ ls <scratch>/engine-probe.js
ls: cannot access '.../engine-probe.js': No such file or directory
$ pgrep -af 'pw-browsers|chrome-linux|headless_shell' | grep -v 'bash -c'
(no output - no Chromium process remaining; the probe closed its browser)
$ ps -eo comm | grep -iE '^chrome|^chromium|^headless'
(no output)
```

Only the two files this run created were removed. No browser profile, history, Downloads folder
or cookie store was cleared, and no pre-existing file or tab was touched.

**Final overall result: SURFACE UNAVAILABLE.**
