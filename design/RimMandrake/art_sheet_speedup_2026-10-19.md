# Art review sheets: why a sheet takes hours, and the options to make it take minutes (2026-10-19)

Owner, 2026-10-19: *"The art sheet has taken 1 hour 38 minutes so far. This is abysmal. … Make it faster, make it more
reliable. Evaluate the options I typically click on and remove ones that don't get used. … Use Python as much as
possible and eliminate LLM delays in the process. Go get GPT's help and give me the rundown on options as option cards."*

This is a read-only analysis. No tool code was changed. Evidence (committed beside this file): `design/RimMandrake/art_sheet_speedup_2026-10-19_evidence/` —
`usage_census.txt`, `sitting_times.txt`, `notes_classes.txt`, `gate_stack_dump.txt`, `gpt_brief.md`, `gpt_answer.md`
and the miner scripts.

## 1. Where the time goes: today's sheet, stage by stage

| stage | wall clock | how it was measured |
|---|---|---|
| request → agent starts work | ~04:26 (back-dated from his "1 h 38 min" at 06:04) | owner |
| agent rebuilds ~20 stale sheets **one after another** (the 04:07 hourly install of 116 donor renders made them stale, and `serve_gated.py` refuses a stale sheet) | **04:32 → 05:25, 53 min**, including one 28-minute gap that is UNMEASURED | html/snapshot file times |
| agent works out the 178 subjects by hand (corpses, Alpha plants, icons, Braskeen/Ismerrow) and writes the command | UNMEASURED (the LLM part; transcript not read) | — |
| `art_sheet.py` builds the 178-row sheet | 05:53:22 → 05:54:57, **95 s** | file times |
| **gate requirement 13: headless Edge render** | **more than 600 s, then killed.** A stack dump shows it waiting in `gate_browser.browser_render`. Its timeout is 600 s with one retry, so the worst case is 20 min | timed; `faulthandler` |
| agent gives up on one sheet, splits it into three (48 / 12 / 118 rows) | built and gated in 93 s / 55 s / 114 s; served at 06:17–06:22 | file times |
| **total from request to page** | **about 1 h 55 min, of which about 4 min was real building** | — |

**Root cause of the gate hang (I checked this in the code).** `gate_browser.browser_render` starts a throwaway sidecar
with `stdout=PIPE, stderr=STDOUT`. It reads that pipe only until it sees the URL, then never reads it again. The sidecar
logs every HTTP request to stderr (`log_message`, because `--quiet` is not passed). Every image on the scratch copy
returns 404 and adds a log line. Once about 64 KB of log lines pile up, the pipe is full. The sidecar then blocks
mid-request, Edge waits for it until the timeout, and the gate retries the whole thing. A sheet with many pictures will
always hit this; a sheet with few pictures never does. That explains why 1-row and 47-row sheets gate in 8–12 s while
the 178-row sheet never finished. GPT spotted the mechanism as "plausible"; I read the code and confirmed it. The fix is
one line (pass `--quiet`, or send the sidecar's output to DEVNULL once the URL is known). It is not applied here.

**Past sheets (MEASURED from 49 decisions files and git):**

| stage | typical | range |
|---|---|---|
| rebuilding one sheet | 23–39 s for 1 row; 1–5 min for 35–47 rows | most of that is the gate plus scale-panel misses (about 1 panel/s); import plus index load is 0.5 s |
| his time per row | **median 28 s** (p75 61 s, p90 113 s; n = 630 click gaps) | — |
| his active time on a 46–93-row biome sheet | 22–52 min | — |
| last click → enact commit (agent-driven) | 2–25 min | git log |
| servers | 13+ per-sheet servers alive for 1–4 days; logs of 1.4–26 MB, mostly `BrokenPipe` tracebacks | ps, ls |

**Conclusion:** his judging (about 30 s a row) is not the bottleneck. Three things are: (1) agents composing the
request and enacting notes by hand; (2) the whole-sheet freshness refusal combined with the hourly installer, which
forces serial rebuilds of unrelated sheets; (3) the Edge gate, which hangs on any large sheet.

## 2. What he actually clicks (MEASURED)

Scope: 107 live decisions files with 3,637 rows. Of those, the 67 sheets built by `art_sheet.py` since 2026-10-04 hold
1,547 rows, and 698 of those rows carry his `decidedAt`.

| control | his rows using it (of 698) | all files | verdict |
|---|---|---|---|
| click a picture = use this | 467 | 671 | **core** |
| notes box (open or already followed) | 398 (57%) | 736 notes (~368 typed by him, the rest agent-written blanket rulings) | **core, primary** |
| per-picture purge ✕ | 252 | 331 | used |
| "redraw this slot" | 165 | 189 | used; overlaps with notes |
| note with no slot action at all | 88 | — | the note *is* the decision |
| "this is:" select on renders found by name | 122 | 198: 185 = the one slot, 13 = "not needed" | a three-way select that is really a checkbox (his complaint confirmed) |
| retire a live picture | 34 | 56 | rare |
| random pool add / leave | 23 (3%) | 43 | rare |
| per-row size-tier question | 20 | 39 | one sheet type only |
| accept unchanged | 3 | 4 | essentially never |
| "✕ not for this slot" | 1 | 1 | never |
| **Requests panel** (rename · description · N more like X · missing facings · size · move biome / tier · cut) | **0** | **0**; no `asks` key in any file, although it has existed since 2026-10-10 and he has decided 148 rows since, 57 of them with notes | **never used**; he types these requests into the note |

What his notes say (736 notes, regex-classified; median 62 characters): keep/fine 146, more variants 76, rename 76,
colour/style 45, description 40, redraw 36, cut 25, canon 23, move biome/tier 15, size 11, facing 4. Every category in
the Requests panel shows up here as free text instead.

**Why "random pool" comes and goes.** `generate_biome` offers the pool verbs only when the def's texture path is a
**folder** (Graphic_Random / Graphic_Collection, via `random_folder_variants`) or the def has `alternateGraphics`. He
never sees the texture class, so to him it looks random. It is offered on 347 of 1,765 snapshot rows (20%). In **143
of those 347** the folder holds a single picture ("random variant X (1 of 1)"), so a pool is offered where nothing
visibly varies.

## 3. GPT's proposals, and my verdict on each

GPT's answer is in `design/RimMandrake/art_sheet_speedup_2026-10-19_evidence/gpt_answer.md` (model via `gpt_consult.py`, effort high, 21
attached files).

| # | GPT proposal | GPT estimate | my verdict |
|---|---|---|---|
| 1 | Drop the per-build Edge gate. Python renders the first row HTML; validate row models and every row/asset; keep browser tests only for template releases | 1–2 days; saves 8–12 s normally and 10–20+ min on a hang | **Agree, and do it first.** The deadlock above makes the Edge gate actively harmful. It also proves little: it counts `<img` strings on a page whose images all 404, and passes at half the expected count. A cheaper interim step is to fix the pipe and pass `--quiet`. |
| 2 | Replace the whole-sheet "stale = refused" rule with per-row freshness: a stale row is labelled stale and its current-state actions are disabled; only affected rows rebuild | 3–5 days | **Agree on the goal; the design is over-engineered.** Leases and acknowledgement handshakes are heavy. A simpler version keeps the guarantee: the server re-measures freshness per row on page load (it already does, per sheet), marks stale rows, and blocks only their pick buttons. **Needs his ruling:** he removed the stale-sheet escape hatch by card on 2026-10-14. |
| 3 | Persistent row-model cache keyed on input hashes; incremental assembly; panel cache extended | 3–5 days | **Agree, but third priority.** Building was 95 s today, not the problem. Worth doing once 1, 2 and 5 are in. |
| 4 | One supervised daemon for all sheets, with a registry endpoint instead of scraping `.serve.log` | 2–3 days | **Agree.** It also fixes the BrokenPipe log flood and servers running for days on stale code. RimPulse has to switch to the registry. |
| 5 | `art review <query>` (awaiting-pick, jobs:, defs:, biome:) with a Python queue definition | 1–2 days | **Agree; biggest win per day.** It removes the agent from step 1, which is where most of today's unmeasured time went. Split pages automatically by kind (creatures / plants / icons), as the agent ended up doing by hand. |
| 6 | Notes grammar parsed by Python (`use C`, `redraw: …`, `2 more like C: …`, `rename "X"`, `describe: "…"`, `size draw x2`, `move RM_X`, `pool B C`, `cut`), with the parse shown live beside the note; enact consumes the stored operations | 7–12 days | **Agree, with GPT's own caveat.** "Improve description" or "rename" with no name cannot be done deterministically; those stay as marked unresolved items for an agent or a card. His real notes are mostly that kind ("Rename, improve description, make two other improved variants…"). So the grammar handles the routine part and the LLM part shrinks; it does not go away. |
| 7 | Delete the Requests panel, reject, accept-unchanged and pool-add-all. Collapse "this is:" into the pick click when there is one compatible slot. Show pool verbs only for a real pool of two or more pictures, with a plain reason. Move legacy ticks to a one-time migration queue. Add keyboard shortcuts (j/k, letters, n, r, Enter, u) | 1–2 days | **Agree.** The usage table supports every one of these deletions. |
| 8 | Migration to schema 3 alongside the legacy fields: backups, shadow-run old against new enact plans, no followed note re-fired | 3–5 days | **Agree.** Required by option 4 below; options 1–2 need only a one-time migration of the legacy ticks. |
| 9a | Bug: `remap_decisions.apply_map` rewrites only `decision`, `picks`, `variants`, not schema-2 `slots`, pool, assign or purge letters | — | **Confirmed in the code.** The risk is lower than GPT implies, because `slots` also store `set_id`. Still worth fixing. |
| 9b | Bug: `--mark-done` writes ledger events on a dry run | — | **Confirmed, but deliberate** (the code comment says so). Not a defect. |
| 9c | Bug: `refresh_sheets.py` does not restart servers by default, which contradicts `references/lifecycle.md` | — | **Confirmed.** The skill text is wrong (it says refresh "restarts a dead server itself") and should be corrected. |
| 9d | Bugs: `clear_followed` lost-update race; installs judged by `live_anywhere`; writing the snapshot before the HTML is not atomic | — | Plausible; not verified here. File them as items before building on them. |
| — | Against localStorage or a static page as the save path | — | **Agree.** `decisions.json` stays the record. A static page would bring back the decisions-lost-in-chat failure. |

## 4. Options for the owner (to become cards)

All estimates are forecasts from the measurements above, not benchmarks.

| option | what he gets | request → page | build cost | risk | controls that disappear |
|---|---|---|---|---|---|
| **A. Hotfix the gate and prune the page** | Fix the Edge pipe deadlock (or drop the per-build Edge check); serve big sheets whole; delete unused controls; pool verbs only on real ≥2-picture pools, each with a one-line reason; "this is:" becomes part of the pick click when there is one slot | today's ~2 h → ~20–40 min (the agent still composes the request; the rebuild cascade remains) | 1–2 agent-days | low | Requests panel, accept unchanged, ✕ not for this slot, pool-add-all, pool verbs on 1-picture folders, the "this is:" select on single-slot rows |
| **B. A + one command, no agent before he sees it** (recommended now) | `art review awaiting-pick` (or `jobs:` / `defs:` / `biome:`) built from a Python queue, auto-split by kind; stale rows labelled per row instead of refusing the whole sheet and forcing the other sheets to rebuild; one daemon serves every sheet | **~3–5 min** cold, about 1 min warm | 4–6 agent-days | low–medium; needs his ruling to relax the 2026-10-14 "stale sheet is refused" card to "stale rows are refused" | A's list, plus per-sheet servers and the `.serve.log` scraping |
| **C. B + notes become commands, enact without an agent** | Notes grammar (`use C`, `cut`, `redraw: …`, `2 more like C: …`, `rename "X"`, `size x2`, `move RM_X`, `pool B C`), parsed live beside the note; `art.py enact` runs the parsed operations directly; only vague asks ("improve description") go to an agent or a card | as B; last click → installed goes from 2–25 min (agent) to about 1 min for routine rows | 11–16 agent-days | medium–high (grammar mistakes act on his art; needs a shadow-run against past sheets) | B's list, plus the redraw button (it becomes `redraw` in the note) and retire (becomes a note verb) |
| **D. Full rebuild (GPT's whole plan)** | C, plus a persistent per-row cache, incremental rebuilds (one changed row in under 10 s), schema-3 decisions, freshness leases with the installers | about 1 min for 200 rows warm | 20–30 agent-days | high (rewrites a 3,500-line tool plus migration) | as C |
| **E. Leave it alone; only split big sheets and pause the hourly installer while he sits** | process rules, no code | ~30–60 min | 0.5 day | low, but nothing gets faster for good | none |

**Recommendation: B now. Then C, but only after a shadow-run of the notes grammar over the 736 existing notes shows
what fraction it parses correctly.** Do D's row cache only if B's measured warm build still exceeds 2 minutes. A's
deadlock fix is part of B and is the one-line change that would have saved most of today's gate time.

## 5. Corrections owed elsewhere (found during this analysis)

- `skills/rimworld-review-sheets/references/lifecycle.md` says `refresh_sheets.py` "restarts a dead server itself". The
  code (`--restart-servers`, default off since the 2026-10-14 OOM) does not. Fix in the next skill-curation pass.
- `SKILL.md` and `art_requirements.md` describe the gate as cheap. On large sheets requirement 13 hangs until the 600 s
  timeout, then retries, so the worst case is 20 min.
