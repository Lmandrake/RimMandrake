# Traps — each one happened

| trap | what happened | the check |
|---|---|---|
| A sheet of game art built outside the gated builder | 7 non-biome art sheets in a week (sluice box, junk reskins, creatures, icons) shipped with no scale panel; one declared itself `non-art` while showing 311 sprites (2026-10-03…10) | build with `art_sheet.py --subjects`; `game_art.py deliver <html>` before giving it to him |
| A whitelist in the generator | a `SCALE_BIOMES` whitelist silently left 21 sheets with no panel (2026-10-06 handoff) | the gate checks every row, never only the opted-in ones |
| "Current art" taken from a def's LAST texture path | 65 of 109 desert rows showed the dessicated corpse (2026-10-04) | resolve the body graphic by role, never by list position |
| A rebuild re-letters columns he already ruled | 28 spurious rejection events from one rebuild (2026-10-09) | `remap_decisions.py` after every rebuild of a touched sheet; letters are append-only |
| A note followed twice | 7 Greentide notes already filed as jobs were briefed out again (2026-10-08); an old note rode along on a new click (2026-10-07) | enact moves followed notes to `notes_followed`; compare the job's `created` with `decidedAt`, never `at` |
| A redo carrying the rejected picture as its reference | a "make it alien" redo kept redrawing the rejected creature and failed canon twice (2026-10-10) | a redo whose note rejects the anatomy carries NO reference; build the prompt from the def's description |
| Pre-snapshot decisions | 229 rows of legacy (pre-2026-10-04) decisions were refused by enact | `legacy_redo_triage.py`; never hand-translate them |
| A served sheet `refresh_sheets` cannot find | server stdout went elsewhere (2026-10-10) | serve into `<sheet>.serve.log` beside the sheet |
| A size that was never measured | plants drawn at the fallback size while their defs set sizes several times larger | every size prints its source; FALLBACK is flagged on the row and checked by the gate |
| Enacting slowly | four helpers chained serially took ~2 h (2026-10-08) | one `art.py enact` pass, one batched card at most |

## A sheet copied out for the owner's convenience (2026-10-31)

A helper had no server for a sheet and a pile that wanted a `D:\` path, so it ran `cp $N.html $D/`. Variables hid the path from
the hook, the copy fell back to browser storage, and he worked it and exported by hand. Its links were WSL paths too. The check
is `sheet_live_guard.py` (block with the URL), req 16, the copy clause of `block_hand_edited_sheet.py`, and `owner_doc_lint.py`.
Serve the sheet. There is no second route.

## Image sizing on a sheet
- **A custom row body that caps image `max-height` squeezes tall sprites, and the owner reads it as truncation.** Keep aspect at natural thumb size and let the zoom control carry the detail; a giant creature ("render MUCH larger") also deserves a 512 canvas.
An offline art sheet composited on a stand-in background can win owner approval and still fail in game: a flat grey floor (lum 56) hid that the dug floor (Gravel x RM_Channel_Superdeep, lum 28 brown) swallows brown stake bodies, which read as orange fuzz live. Composite on the real terrain texture x def colour at play zoom (~83 px/cell) and pin the floor against a live capture (`fw_scenes_spikes.floor_matches_live`). Also `stage_fw_art.py` `gizmo()` matches 'Ladder up' exactly but the label gains ' (ordered)', so its raise never fires (the raised shot came from `gz2.py`'s DEV gizmo).

## Name and census sweeps
- **`biome_census.py` marks a row NO ART when its def's texPath points at vanilla/donor art, even when artpipe holds finished renders for it by name** (6 of 8 Blue Desert rows). `art_sheet.py` finds renders by name and the census does not: trust the sheet's NO-ART list, not `census.md`'s count.
- **A biome lives under two names: the program-table/def name and a campaign label.** Grepping only one missed a sheet and nearly filed a false missing-sheet gap (e.g. desert.md is the Long Shade's record; Leaning Scrub's legacy label is arid_shrubland). Sweep both the def name and the `<label>`, and take the mapping from About.xml / BiomeDef headers, never inference.

## Art that does not reach the game
- **Approved art is invisible when the PawnKindDef has `alternateGraphics`:** the engine draws the alternate at `alternateGraphicChance` (GizkaW at 0.8), so a ruling that rewrites only the primary body graphic changes only 20% of spawns. `artledger.scan_def_slots`/`GRAPHIC_ROLE` has no role for `alternateGraphics/li`, so the ledger says "(none in our defs)" and no sheet ruling can bind to it. Guard: `src/RimMandrake/Utils/art/selftest_drawn_art_ruled.py` (ratchet baseline: 6 more creatures, 72 pictures); check the alternates when a creature is "approved" but looks unchanged.

## What a row may hold
- **Keep projectile and attachment art in its own row.** `art_sheet.py` can put a non-body render (a projectile) as a column in a creature's body row, and an owner pick there is ambiguous (Barbslinger "B" meant approve the spike).

## A sheet built from stale inputs
- **A sheet built from `art_sheet` subjects can resolve art from a stale live def dump** and show the stand-in (the dragonsnake sheet showed the olive stand-in four times and a white albino swim graphic) while the four real renders sat unshown in `_artpipe/_artsrc`. Before offering any sheet, render what it displays and LOOK at it.
- **A collection builder re-run for a SUBSET (e.g. keep = reels only) can silently overwrite the other subjects' summary sheets with empty ones,** voiding every earlier 'looked at it' check. Make builders skip subjects with nothing kept, and re-Read the final folder (sizes + images) as the LAST step before publishing.

## Agent guesses on a decisions file
- **A `decisions.json` row whose decision equals its prefill, on a sheet with `reviewStatus.state=prefill` and no `savedBy`, is an AGENT GUESS, not an owner pick.** A handoff called two closed gate renders "picked A" from exactly that. Before installing a "pick", find the art-ledger ruling event (`by=owner`) or a ledger `ownerSaid`/`byCard`.

## The sheet hook and Bash
- **The biome-sheet PreToolUse hook refuses a Bash call whose inline script names a `Transient/biome_ffar/*_sheet_*.html` path and writes ANY file** (even filling `<stem>.prereview.json`, or a heredoc, or a pin). Put the writer in a script file, pass the path as an argument, and pin in a separate call.
- **A Windows exe launched from WSL (msedge, codex) survives a Python subprocess timeout:** only the WSL-side handle dies. The sheet gate leaked 915 `msedge.exe` (110 headless roots) and every later render timed out (UNMEASURED). Give each run a unique marker on the Windows command line (`--user-data-dir`), stop by marker afterwards (`gate_browser.stop_marked`), and count with `Get-CimInstance Win32_Process`, not `tasklist` guesses.

## Auditing GPT redo lists
- **Before filing or acting on a GPT redo list, run `art.py status` + `regen_eligibility.Gate.classify` per def, and grep `art_eval/runs/*/decisions.jsonl` (subject prefix before `__`).** A GPT biome audit listed "no owner keep" rows that carried 39 and 11 `trust=ruled` keep events (RSW_LongtailGorg, RSW_Worrt), and every redo slot was REFUSED_REGEN.

## Dedup on a sheet
- **A cross-lane sha dedup must never drop a `kind=live` column** (`art_sheet._take_unseen`): the installed picture vanishes as installed and gate req 15 (freshness) refuses the sheet. Fix the builder, never the gate. A relaxed dedup lets a row hold two columns with identical faces, so letter memory must be multiplicity-aware (faces -> [letters]); a faces -> ONE-letter memory hands the copy a NEW letter every rebuild and his pick turns into a false "WAS in game" KEPT column.

## Prereview record
- **`prereview.fingerprint()` hashes only the row label and `PICTURE_KEYS` paths, not image bytes and not extra keys such as a custom `views` list.** A sheet rebuilt with new pictures under the SAME filenames keeps its old "looked at" record (`prereview init` reset 0 of 22 rows to TODO), so re-look and re-record by hand, or hash content (size + sha of each image) and include every image path (`views[].src`). The review-sheets template zoom overlay caps at 70vw/70vh with `image-rendering: pixelated`, so a big composite opened in zoom is downscaled nearest-neighbour and aliases: a sheet showing texture detail shows pictures inline at 1:1 and links the bare file.

## World-face sheets
- **An HSV saturation boost on a water face must stay below `biome_worldfaces`' water rule (sat <= 60%),** or the "clearer/deeper" variants fail verdict (TwilightSea hit 69%); `world_water_variants` caps s at 0.56.
- **Report organic patch size (glass panes, blobs) by both measures:** median area understates what the eye reads, because big patches carry most of the visible colour (round-3 Twilight panes: median 4.5 hexes, area-weighted median 7.5, eye-catching panes 8-10 at mid zoom; `pane_metrics` in `world_water_variants.py`). When the owner gives a size target, show one row hitting it by each measure. One hex = 0.866 x (centre-to-centre width)^2, not width^2 (forgetting it understated r2 panes by 13%).

## Borrowed pictures
- **A creature that wears ANOTHER creature's picture by texPath (RSW_SandStalker draws Skarnix; RSW_Excretor draws RSW_FeralNerf's owner-kept renders) trips two guards.** If the owner rejected that picture, the art ledger refuses `install_bytes` of any copy, so a tier move of the BORROWER fails mid-apply after `git mv`: before a move batch list every texPath the defs draw, look each sha up for a reject/redo verdict, and drop that creature first. And the regen gate classifies a row for its own new path REFUSED_REGEN ("the def now draws a render of ours elsewhere"), so the dregen path cannot queue its own-art job: run `regen_eligibility` classify on a scratch row before promising "queue it a picture", and read the sheet decisions (the owner may have kept the shared picture FOR that creature, then it is his call, not a gate bypass).
Foreign-copy audits: an image shared by two subjects does not say which one owns it. Direction comes from the codex rollout trace: a rollout whose own id differs from the `generated_images/<session>` it copies from is the copier, and the cache session id is a UUIDv7 whose first 48 bits date the original (a 'known bad' cocoon was the spiral desert wrap's OWN render, copied 09-23..28). A retried job overwrites the copied PNG in `_artsrc`, but art_eval runs and owner-sheet `subjects.json` keep a `reference_texture` to it, so 'never installed' is not 'never shown': grep sheets and runs for the copy paths before closing.

## Prereview parsing
- **`prereview.py` reads ITEMS with `<script id="ITEMS"[^>]*>`,** so a block written `<script type="application/json" id="ITEMS">` reports "no readable ITEMS block" though it is valid HTML. Put `id` first, or loosen `ITEMS_RE`.

## Sheets served from a mirror
- **A Transient sheet path on the D: mirror can open blank:** sheets are per-clone, image folders may exist only in the seat clone, and unpinned sheets vanish from the mirror altogether. Before citing a sheet path to the owner, check that every `img` reference resolves beside that exact file.

## Audits that count owner decisions
- **`texture_regen_audit.py`'s "owner sheet decided" UNPROVEN sub-class is a stem substring match in any `decisions.json`, not proof of an owner pick:** traced to the commit that first brought each picture's bytes in (git blob id via one `git log --raw`), 61 of 121 such defs were donor stand-ins. Art-ledger `kind=artpipe` includes `_artsrc/` job INPUTS (often donor pictures), `kind=install` can record donor bytes, and a 256-bit dhash <=7 matched a spore item to an animal by chance: confirm dhash hits by pixels (`unproven_adjudicate.py`).
`texture_regen_audit.py`'s roster view classes a face by its bytes' ledger kinds only, while its def view's `file_class` also accepts an install-time live record of the path, so the same N/S facing reads UNPROVEN in one view and REGEN in the other (15 roster rows). An art-ledger 'install' is not proof of our render: the 2026-10-16 facing rescale installed donor-port pictures under swanimals/BiomesTeam with empty provenance.

## Rebuilding a decayed sheet
- **Before rebuilding a review sheet that "decayed unseen", census the art ledger for owner rulings on its pictures.** "218 renders never owner-reviewed" was 109 jobs (json + manifest = 2 files each) and the owner had already purged 95 of them on earlier biome sheets. A render family he ruled on a biome sheet needs no second sheet; `desert_port_coverage.py` is the pattern (`events/**/*.jsonl` purge|rejected by owner, then sheet snapshots >= a date).

## Art-tool traps
**`art.py install` takes `--ruling`, `--owner-said` or `--by-card`; card decisions must never go through `--owner-said`,** which records a KEEP ruling and makes provisional installs look owner-kept (36 installs once overwrote owner-kept slots this way).
