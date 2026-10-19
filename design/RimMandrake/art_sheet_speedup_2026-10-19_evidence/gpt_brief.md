# Review: make the RimMandrake art-review-sheet procedure MUCH faster and more reliable

You are reviewing a working but slow pipeline. The attached files are its real source (excerpts where a file is huge;
the excerpt file names say which lines). Read them; cite function names and line-level behaviour when you claim
something about the code. Where you are guessing, say so.

## The owner's complaint (verbatim, 2026-10-19)

"The art sheet has taken 1 hour 38 minutes so far. This is abysmal. I would like you to send the ENTIRE art sheet
procedure to GPT for a review of how we can make this MUCH faster. This was an enormous expenditure of time and tokens
just to take a look at some art. Make it faster, make it more reliable. Evaluate the options I typically click on and
remove ones that don't get used. For example: random pool is sometimes offered and sometimes not for reasons I never
know. There's a drop-down that offers 'where will this art be used' that always has only undecided, (some random word
that means use), and (don't need anymore). Useless, that's basically a checkbox for 'use this.' There's an entire
dialog I can open to give detailed clickable options, but I just type free text in the notes box as much more
efficient instead. Use Python as much as possible and eliminate LLM delays in the process."

## Goal

- "Owner wants to look at N pieces of art" -> a page in front of him in MINUTES (target: < 2 min for 200 rows on a
  warm cache; < 10 s for an incremental rebuild of one row), not hours.
- Pure Python for building, gating, serving and enacting. No LLM/agent in the loop for any of those steps. (Image
  GENERATION of redraws by artpipe stays an LLM/image model; that is not in scope.)
- The notes free-text box is his PRIMARY input. Picking a picture (click) is the other. Everything else is suspect.
- Remove controls he does not use; make the ones that stay predictable (no control that appears or disappears for
  reasons he cannot see).
- Deterministic, reliable, keyboard-first.
- Keep the owner's hard rulings (these are NOT negotiable): (1) every picture with an in-game size is shown at TRUE
  SCALE beside a vanilla human (a scale panel per row; enforced in code at serve/commit/phone); (2) decisions are data
  in a `<sheet>.decisions.json`, never chat; (3) a note he wrote is followed once and then moved to `notes_followed`
  (never re-fired); (4) letters he picked keep naming the same pictures after a rebuild (snapshot + remap); (5) nothing
  installs until he says the sheet is done; (6) a stale sheet (a row no longer shows what is installed) is not shown as
  current. You MAY propose a cheaper mechanism that keeps the same guarantee.
- Migration must not lose any existing decisions.json data (107 live files, 3,637 rows, 1,602 touched by him).

## The pipeline as it is (mapped from the code and the skills)

1. **Intent -> subject list.** He asks to see some art ("everything waiting on my picks"). An AGENT (LLM) works out
   which defs/jobs belong on the sheet by reading the ledger, artpipe state and other sheets, then composes an
   `art_sheet.py --subjects <defs...> --jobs <job ids...> --name x --label "..." --lead "<html>"` command. There is no
   Python query for "everything awaiting a pick". (Today: 178 rows, four groups.)
2. **Freshness.** `serve_gated.py` + `sheet_freshness.py` REFUSE a sheet any row of which no longer shows what is
   installed, re-checked on every page load, with no override (owner card 2026-10-14). An hourly timer
   (`rm-donor-regen-install`) installs finished donor-replacement renders (116 at 04:07 today). Every install makes
   every sheet containing that def stale -> every open sheet must be rebuilt (`refresh_sheets.py`, serial).
3. **Build** (`art_sheet.py`, 3,523 lines, 239 KB, one process per sheet): census (`subjects_census` /
   biome census) -> `generate_biome` (743 lines): resolve each def's graphics by role, gather candidate columns
   (in-game, shadowed copies, artpipe renders, git history, donor), dHash near-duplicates, assign append-only letters
   from the snapshot memory, prefill, scale panels via `scale_panel.py` (PNG per candidate set, cached by hash under
   `Transient/biome_ffar/img/`: 21,990 files, 1.5 GB), write HTML (embedded JS UI, ~1.5 MB for 178 rows) + snapshot.
4. **Gate** (`scaled_review_gate.py`, 14+ requirements): builds to `<sheet>.gate.tmp.html`, checks, stamps, moves into
   place. Requirement 13 (`check_browser` -> `gate_browser.browser_render`) starts a throwaway sidecar server and runs
   **Windows headless Edge through WSL interop** with `--dump-dom`, `timeout=600`, plus ONE RETRY on timeout, then a
   PowerShell sweep to kill the Edge tree. Also `check_sheet.py` (general skill) runs.
5. **Serve** (`serve_gated.py` -> exec `serve_sheet.py` sidecar, one long-lived Python HTTP server per sheet, log to
   `<sheet>.serve.log`, which RimPulse scrapes for the URL). Many servers live for days.
6. **Owner sitting** in the browser: click a picture to use it; per-picture verbs; the notes box; a "Requests" panel;
   a "this is:" select for renders found by name; random-pool toggles; legacy-variant keep/drop; per-picture purge ✕.
   The sidecar writes every click to `decisions.json`.
7. **Remap** after any rebuild of a touched sheet (`remap_decisions.py`).
8. **Enact** (`art.py enact` -> `enact.py` `build_plan`/`enact`): ingest rulings, install picks, queue redraws with his
   note verbatim as `owner_note`, purge ✕, cut rows, deploy touched mods. Notes that ask for def changes (rename,
   description, size, move biome) become "def halves" that an AGENT carries out by hand, then `--mark-done`.
   Several recent enacts were hand-written scripts by an agent ("dry-run enact script", "converted from Single per his
   notes").
9. **Audit** by an agent (fresh reads of ledger/artpipe), then commit/push.

## Timings (MEASURED unless marked)

| stage | measured | source |
|---|---|---|
| today's collective sheet, wall clock to "still not shown" | 1 h 38 min (owner) at 06:04; still not served at 06:10 | owner; file mtimes |
| agent rebuilding ~20 stale sheets serially before composing the collective (after the 04:07 hourly install of 116 renders) | 04:32 -> 05:25 = 53 min, incl. one unexplained 28-min gap | html/snapshot mtimes |
| per-sheet rebuild, 1-row sheet | 23–39 s | mtime deltas |
| per-sheet rebuild, 35–47 rows | 59–315 s | mtime deltas |
| art_sheet import + art Index load | 0.5 s | timed |
| scale panel renders (cache misses) | ~1 per second (589 in 10 min) | img/ mtimes |
| collective subjects.json written -> gate.tmp written | 05:53:22 -> 05:54:57 (95 s build) | mtimes |
| **gate check of the 178-row collective sheet** | **> 600 s, killed by my timeout; stack dump shows it waiting in `gate_browser.browser_render` (headless Edge)** | timed, faulthandler |
| gate check, 1-row sheet / 47-row sheet | 8.2 s / 11.8 s | timed |
| the agent then started over (`art_sheet.py --jobs ...`) | 06:08 | ps |
| owner per-row decision time (gap between his clicks, gaps < 10 min, n=630) | median 28 s, p75 61 s, p90 113 s | decidedAt in decisions.json |
| owner active time on a 46–93-row biome sheet | 22–52 min | decidedAt |
| sheet built -> his first click | 0.1 h to 128 h (median ~8 h; sheets wait for him to be free) | git add time vs decidedAt |
| his last click -> enact commit | 2–25 min (agent-driven) | git log |
| serve logs | 1.4–26 MB each, mostly BrokenPipe tracebacks; 13+ servers alive for 1–4 days | ls, ps |
| agent (LLM) time composing subject lists, reading notes, writing enact scripts | UNMEASURED (transcripts not read) | — |

So the owner's own judging is ~30 s/row and is NOT the bottleneck. The time goes to: agents composing the request, the
serial rebuild cascade forced by freshness + hourly installs, and the Edge render gate, with the 600 s subagent
watchdog killing long builds so they restart.

## What he actually uses (MEASURED over 107 live decisions files, 3,637 rows; the 67 sheets built by art_sheet.py since 2026-10-04: 1,547 rows, 698 touched by him)

| control | art_sheet.py-era touched rows using it (of 698) | all files | verdict input |
|---|---|---|---|
| click a picture = "use this" (slot state `pick`) | 467 | 671 | core |
| notes free text (open or already followed) | 398 (57%) | 736 notes; ~368 typed by him, rest agent-written blanket rulings | core, primary |
| "redraw this slot" button (slot state `redraw`) | 165 | 189 | used; overlaps with notes |
| per-picture purge ✕ (deletes from art store) | 252 | 331 | used |
| "this is:" select on by-name renders (options: — choose — / <the slot, usually one> / not needed) | 122 | 198 (185 = the slot, 13 = not needed) | a 3-way select that is really a checkbox |
| legacy variant keep/drop (pre-2026-10-10 ticks) | present on 223 | 312 | migration debt |
| retire a live picture | 34 | 56 | rare |
| random pool add/leave | 23 (3%) | 43 | rare; offered on 347 of 1,765 snapshot rows (20%) |
| per-row `--question` (size tier) | 20 | 39 | only on one sheet type |
| "accept unchanged" | 3 | 4 | ~never |
| "✕ not for this slot" (reject) | 1 | 1 | never |
| "Requests" panel (rename / description / make N more based on X / missing facings / size / move biome / tier / cut) | **0** | **0** (no `asks` key in any file) | never used — he types these in the note |
| note with no slot action at all | 88 | — | note carries the whole decision |

Note text (all 736 notes, regex-classified, median 62 chars, p90 93): keep/accept 146, more variants 76, rename 76,
colour/style 45, description 40, redraw/new art 36, cut/remove 25, canon 23, move biome/tier 15, size 11, facing 4.
I.e. every Requests-panel category appears in free text instead. Sample notes: "Rename, improve description, make two
other improved variants that are more realistic"; "duplicate, remove"; "Tint it darker stone"; "add variants";
"Canon shows something more like C. We need a high quality version of that."; "This is just a bird. More alien
please, and much more colorful. Perhaps a pale blue?"

**Why "random pool" is intermittent:** `generate_biome` sets `g["pool"]` only when the def's texPath is a FOLDER
(Graphic_Random / Graphic_Collection: `random_folder_variants`) or the def has `alternateGraphics`. That is invisible
to him. 143 of the 347 pool rows have a folder holding ONE picture ("random variant X (1 of 1)"), so a pool is offered
where nothing is visibly random.

## What I want from you

1. A concrete REDESIGN, ranked by speed-up and risk. Cover at least:
   - what to DELETE (controls, gate requirements, server-per-sheet, freshness-refusal behaviour, etc.) and what to MERGE;
   - the Edge render gate (req 13): replace with a pure-Python/Node DOM check, a jsdom/QuickJS smoke test, a JSON-schema
     check of the embedded data, or drop it — what preserves "a null field once blanked a whole sheet" protection?;
   - PRECOMPUTE and CACHE: a persistent per-def "row model" cache keyed by input hashes so a 200-row sheet is assembled
     from cached rows in seconds; incremental rebuild of only changed rows; scale panels already cached by hash;
   - the freshness cascade: how to keep "never show a stale row as current" without rebuilding whole sheets serially
     (e.g. client-side freshness overlay, per-row staleness badges from a small JSON the server recomputes, or pausing
     the hourly installer while a sheet is open);
   - a single command: e.g. `art review <query>` where the query is pure Python ("awaiting-pick", "jobs:<glob>",
     "defs:<list>", "biome:<X>") so no agent composes subject lists;
   - "review now": a STATIC single-HTML (or a single long-lived server for all sheets) so there is no per-sheet server
     start; how decisions get saved without a per-sheet sidecar (e.g. one shared server, or localStorage + export,
     or a POST endpoint on one daemon);
   - a FREE-TEXT NOTES GRAMMAR parsed deterministically by Python into decisions (e.g. "use C", "cut", "redraw: more
     alien, pale blue", "rename Foo", "describe", "2 more like C: darker", "size x2", "move RM_Greentide", "pool B C"),
     with everything unparsed kept verbatim as the redraw/owner_note; show the parse back to him live, next to the
     note, so he sees what will happen; how enact consumes it with no agent;
   - keyboard-first UI: e.g. j/k rows, A..Z picks, n focuses notes, r redraw, x cut, Enter next undecided;
   - what to do about the "this is:" select (make it a checkbox? auto-assign when the row has one slot?), the random
     pool (show only when there is a real >1-picture pool, and say why), legacy-variant answers (one-time migration),
     the Requests panel (delete; grammar replaces it), the per-row question (keep as an option only when a sheet asks).
2. A MIGRATION PLAN that does not lose existing decisions.json data (schema versions, `notes_followed`, slots, pool,
   assign, purge, legacy variants), and keeps letters stable.
3. For each proposal: expected speed-up (minutes saved per sitting, with your reasoning from the timings above), risk,
   and build cost in agent-days. Flag anything in my measurements you think is wrong or misread.
4. Point out reliability bugs you can see in the code (e.g. the 600 s Edge timeout + retry = 20 min worst case; serve
   logs filling with BrokenPipe tracebacks; servers living for days on code that has since changed).

Be concrete and blunt; prefer deletion over new machinery. Answer in Markdown, under ~2,500 words.
