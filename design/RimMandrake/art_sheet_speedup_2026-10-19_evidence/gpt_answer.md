**The pipeline needs fewer stages, not faster agents.** Remove browser startup from sheet builds, stop rebuilding unrelated sheets before opening the requested review, and cache reusable rows. Those changes address the measured delays directly.

I reviewed only the supplied source. The excerpts lack original line numbers, so references below name functions and the exact statements or branches supporting each finding. Speed estimates are forecasts, not benchmarks.

**1. Ranked redesign**

Savings overlap; do not add them together.

| Priority | Change | Expected saving per sitting | Risk | Build cost |
|---|---|---|---|---|
| 1 | Delete per-build Edge gate; render initial rows in Python | Normal: 8–12 seconds/build. Hung case: removes 10–20+ minutes per gate invocation | Medium: replace its useful protection first | 1–2 agent-days |
| 2 | Delete “refresh every stale sheet before opening this review” | Avoids the reported 53-minute prerequisite window; 28 minutes remain unexplained | Medium–high: freshness coordination | 3–5 days |
| 3 | Persistent row and asset cache; incremental assembly | Collective: plausibly saves 60–90 of the measured 95 build seconds when warm | Medium: incomplete cache dependencies | 3–5 days |
| 4 | One shared Python daemon; registry instead of log scraping | Seconds on startup; larger reliability/resource benefit | Medium: shared failure domain | 2–3 days |
| 5 | `art review <query>` plus indexed review queue | Removes subject-list composition; minutes saved currently unmeasured | Low–medium: query semantics | 1–2 days |
| 6 | Notes parser and Python enact handlers | Removes routine agent interpretation; targets much of the measured 2–25-minute post-review interval | High for existing prose and def edits | 7–12 days |
| 7 | Delete unused controls; keyboard-first review | Setup saving negligible; owner-time saving unmeasured | Low | 1–2 days |

Migration and regression fixtures: another **3–5 days**. Ship priorities 1–3 first; do not make a complete UI rewrite their prerequisite.

**2. Replace the Edge gate, preserve the protection**

`scaled_review_gate.check_browser()` retries when the problem contains `"Timeout"`. `gate_browser.browser_render(timeout=600)` therefore permits **1,200 seconds of Edge waiting**, plus startup and cleanup.

Worse, `browser_render()` deliberately serves a scratch copy without images, then counts `"<img"` in dumped markup. It does not prove images load. `check_browser()` accepts roughly half the expected scale-panel count. This is expensive, weak coverage.

Recommended replacement:

- **Python renders the initial row HTML.** JavaScript enhances an already usable page.
- Validate normalized row models: required arrays, nullable fields, unique IDs, valid slot/set references, valid decisions and snapshot relationships.
- Parse generated HTML and verify **every expected row**, required control, scale panel and referenced asset.
- Catch a row-render exception as a build failure naming that row. Never publish an error placeholder as a successful row.
- Gate scale assets against their render manifest, including measurement, human reference and renderer version.
- Retain browser interaction tests for **template releases**, using bounded native execution, not WSL-to-Windows Edge on every sheet.

A JSON schema alone cannot catch renderer exceptions. jsdom/QuickJS can catch some JavaScript errors but cannot prove browser layout or image decoding. Python-rendered initial content removes the original “one null blanks the entire sheet” failure path most directly.

Keep the substantive checks for scale, identity, provenance, purges, donor context and freshness. Delete browser launch, string-presence pseudo-checks, and duplicate validation passes. For example, `refresh_sheets.main()` runs `check_sheet.py` again after `generate_biome()` already gated the build.

**3. Cache rows, not whole-sheet accidents**

Split `generate_biome()` into:

`resolve inputs → build reusable row model → bind sheet letters/decisions → render HTML`

Its supplied implementation currently resolves resources, gathers candidates, assigns letters, reads thumbnails, resolves canon and renders scale panels inside whole-sheet loops.

Maintain a persistent Python index/cache with:

- Def/slot identity and resolved graphics.
- Installed **path → facing → SHA**, including load-order winner.
- Candidate sets, jobs, purges, rulings, canon and measured sizes.
- Dependency hashes and reverse dependency → affected-def mappings.

A row key must include source XML/patch inputs, relevant dump data, texture membership/content, load order, jobs, ledger state, canon, terrain, human assets and resolver/render versions. **Do not key it on repository HEAD**, which invalidates everything for unrelated changes.

Keep reusable models independent of sheet letters. Bind letters using that sheet’s permanent snapshot memory; apply notes and picks afterward.

`_panel_for()` already caches panels, but its key uses the row key, truncated picture hash and selected size fields. Extend it to complete render inputs and human/renderer dependencies. Reuse panels across sheets and compatible defs. Precompute new candidate panels when renders arrive; use bounded worker processes for misses.

Target budget, to verify with instrumentation:

- Warm 200-row review: query/index 2 s, cache assembly 5 s, validation/publication 5 s, initial display 5 s.
- One changed row: under 10 s **with cached panels or a bounded number of misses**.

At approximately one second per panel miss, arbitrary rows containing dozens of new candidates cannot honestly receive an unconditional ten-second guarantee.

**4. Replace whole-sheet freshness refusal with per-row fail-closed freshness**

Delete the rebuild cascade. Opening review A must never require rebuilding reviews B–T.

Use one shared current-state index and per-def revisions. When installed art changes:

1. Invalidate affected row revisions.
2. Rebuild only affected reusable models.
3. Refresh those rows in interested sheets.
4. Preserve notes, decisions, focus and letter identities.

A stale row may remain visible as **historical review content**, with an unmistakable stale label and disabled current-dependent actions. Remove its “IN GAME/current” claims until validated. Other rows remain usable.

**Polling alone does not preserve the hard guarantee.** It creates a stale-but-labelled-current interval. All installation paths must participate in per-def coordination: invalidate active views before replacement, acknowledge invalidation or wait for short freshness leases to expire, then write. Disconnected/reconnecting clients default to stale. Serve, commit, enact and phone publication validate the same revision contract.

If coordinated invalidation is unavailable, use short installation locks while validating/delivering rows and display historical status afterward. Do not claim an unconditional freshness guarantee from a watcher.

Reject “pause hourly installation while any sheet is open” as the default: sheets wait hours or days. A short critical-section pause is reasonable.

**5. One command, one daemon, one saving protocol**

Examples:

```text
art review awaiting-pick
art review jobs:donor_*
art review defs:RM_Foo,RSW_Bar
art review biome:RM_Greentide
```

Define `awaiting-pick` explicitly: completed eligible candidate sets not covered by a verified owner disposition, including new sets after an earlier ruling; exclude withdrawn work and followed requests. Explain inclusion on each row. Resolve aliases through `subject.py`; use stable ordering. Preserve biome-specific views rather than silently merging biome rosters.

`subjects_census()` currently requires supplied defs/jobs and writes their census; it does not discover this queue.

Use **one supervised Python daemon** with routes for sheets, row models, decisions, parse previews and status. Keep `<sheet>.decisions.json` authoritative. A registry endpoint replaces RimPulse’s dependence on `.serve.log`.

Retain durable writes, tokens, freeze enforcement and visible save acknowledgements. Add row revisions and field-level operations. `DecisionsFile.write_ops()` currently preserves other rows and unknown top-level fields, but replaces each submitted row wholesale.

Do not make localStorage/export the normal persistence path. It adds recovery work and weakens the decisions-file guarantee.

**6. Notes become the primary command surface**

Keep the exact raw note. Parse commands in Python after a short debounce; return the interpretation beside the note. Persist parser version, resolved targets and operation IDs with the decision.

A deliberately small grammar:

| Input | Explicit effect |
|---|---|
| `use C` | Pick C for the sole eligible slot |
| `adult: use C` | Pick C for a named slot |
| `redraw: more alien, pale blue` | Queue redraw carrying the complete note verbatim |
| `2 more like C: darker` | Queue two candidates using C |
| `rename "Dunejelly"` | Set the displayed label; preserve defName |
| `describe: "Exact replacement text"` | Replace description literally |
| `size draw x2` | Change draw size; record old and target values |
| `move RM_Greentide` / `tier RM` | Explicit roster/tier operation |
| `pool B C` | Add B/C to an eligible pool; preview existing members retained |
| `cut` | Cut from the stated biome, showing the deletion scope |

Allow newline-separated commands. Preview conflicts instead of applying precedence silently. Resolve letters to immutable sets when saving.

**Do not promise deterministic understanding of arbitrary prose.** “Improve description”, “rename”, “see above” and “redundant?” lack executable parameters. Python cannot invent satisfactory names or descriptions. Offer explicit wording or declared templates; otherwise retain an unresolved instruction that prevents claiming the row fully enacted.

Unparsed text stays verbatim. With a redraw/more action, pass the entire note as `owner_note`; without one, show “preserved, unresolved”—do not turn “Good!” into a redraw.

Enact must consume persisted operations directly, with Python handlers for supported def edits. Remove hand-written enact scripts and routine `--mark-done` bookkeeping. Each operation gets a durable idempotency key; restart resumes incomplete effects. Move the note to `notes_followed` only when **all its operations** have durable outcomes. Retries continue the same operation.

Nothing installs until an explicit **Done** action freezes the acknowledged decisions and authorizes their displayed plan.

**7. Delete and merge controls**

- **Keep:** picture selection, prominent notes, redraw, per-picture purge, undo, progress/save state.
- **Delete:** Requests panel, reject/not-for-slot, accept-unchanged, pool-add-all and duplicate selection buttons. Preserve their existing data semantics.
- **Retire:** move to notes/advanced actions; it has actual usage.
- **“This is”:** eliminate separate assignment for a sole compatible slot; clicking binds and selects together. Retain an explicit slot choice when genuinely ambiguous. One slot alone is insufficient when the render’s role conflicts: `SLX.pick()` and `generate_biome()` currently guard flight/body/catch confusion.
- **Random pool:** show membership controls only for a genuine multi-set pool. Always show a stable capability explanation, such as “Graphic_Random; one installed set—no variation yet.” Keep an explicit route to add a second eligible set. `generate_biome()` and `sheet_slots.derive()` currently set pool capability from folder/graphic structure, not visible member count.
- **Legacy ticks:** resolve through a one-time migration queue; unanswered ticks remain protected, not silently shipped or dropped.
- **Per-row question:** retain only when explicitly requested.

Keyboard: j/k rows, letter picks, n notes, r redraw, Enter next undecided, u undo, `/` search. Reserve navigation keys consistently—use a pick prefix or numeric shortcuts where letters collide. Ignore shortcuts during text input; Esc exits notes. Picks can advance; notes never lose their caret through repaint.

**8. Migration without data loss**

1. **Inventory and preserve:** byte backups and hashes of all 107 decisions files, snapshots and required historical snapshots. Account for 3,637 rows and 1,602 touched rows; preserve unknown fields and provenance.
2. **Add schema 3 alongside legacy fields.** Preserve `notes_followed`, slots, picks, pool baselines/add/remove, assign, purge, reject/retire, questions and legacy answers. Never reinterpret old prose automatically or promote prefill to owner approval.
3. **Resolve identity once:** store full facing/SHA maps and stable slot identities. Letters remain permanent sheet aliases. Missing snapshots or ambiguous identities become explicit migration exceptions.
4. **Separate identity from revision:** immutable snapshots describe each build; append-only letter memory survives builds. Current `generate_biome()` retains `snapshotId` for column supersets, so that ID is unsuitable as a complete inventory revision.
5. **Shadow-run:** compare old/new plans across every file; require no unexplained lost actions, changed targets or newly fired followed notes. Test stale tabs, concurrent saves, interruption/restart and rebuilds.
6. **Cut over writers together:** revision-check legacy clients, share locks across server/enact/migration, retain compatibility URLs, and reject incompatible writes visibly. Keep rollback backups.

**9. Reliability defects and measurement corrections**

- **Possible gate deadlock:** `browser_render()` stops draining the sidecar’s stdout pipe after finding its URL. Subsequent image-404 logging can fill it and block handlers. This is a plausible hang contributor, not a demonstrated diagnosis.
- **Incomplete remapping:** `apply_map()` changes only `decision`, `picks`, `variants`; schema-2 slot picks, pool lists, assignment keys and other letter references remain unchanged. Writes also lack the shared lock/atomic replacement.
- **Lost-update race:** `clear_followed()` checks bytes then replaces without `writer_lock`; a save between those operations can disappear. `guard_ops()` also reads history before the underlying locked write.
- **Wrong-slot shortcut:** `build_plan()` treats `idx.live_anywhere(sha)` as already installed before checking the intended destination.
- **Mutable timestamp misuse:** job matching and newer-ruling protection use row `at`; unrelated saves advance it. Use action timestamps/IDs.
- **Publication is not transactional:** `generate_biome()` writes the snapshot before committing HTML. `_move_into_place()` ultimately overwrites HTML in place, allowing partial reads.
- **Freshness gaps:** `_SHA` caches by size/mtime despite the “nothing is a cache” claim; `verify_items()` compares flattened SHAs rather than exact path/facing mappings. `_flip:` graphics bypass its installed-byte loop.
- **Scale coverage gap:** `_scale_for()` and `check_scale()` cover primary-lane candidates, not every secondary pictured slot. Serve freshness also does not remeasure size or verify scale-panel bytes.
- **Dry-run mutates:** `enact(...mark_done=...)` deliberately writes ledger events even without `apply`.
- **Logs/lifetime:** `Handler._send()` leaves disconnected-client writes uncaught, consistent with BrokenPipe tracebacks. Catch expected disconnects, rotate logs, supervise and version the single daemon.

Finally: refresh is serial in the default loop, but supports `--only` partitioning. It already skips browser validation for unchanged sheets and **does not restart servers by default**, contrary to `lifecycle.md`. Mtime gaps do not isolate CPU time or explain the 28-minute gap; the 600-second watchdog is supplied operational evidence, absent from these files. Instrument stage durations and cache misses before claiming exact savings.