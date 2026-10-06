# BENCH_REBOOT_HANDOFF_202610060904 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610060555`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The scoreboard is blind, not the mods.** `required_checks_report.py` read "proven 0 of 1543" while FlowWorks ran 59/59 PASS and GSS 143/144 live: it reads only `Transient/modcheck/live_queue/*_summary.json`, so 108 of 148 manifest mods (1,783 required checks) have no readable record. It now names them (NOT IN THE TOTAL). Never cite a proven-count without that line beside it; the join is `NORTHSTAR_RESULTS_JOIN_1`.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Northstar review he asked for: `design/RimMandrake/northstar_review_2026-10-06.md` (GPT answer in `Transient/northstar_review_2026-10-06/`). Top action: one result contract so checkouts reach the scoreboard.
- Tint ruling ready: `Transient/tint_review_2026-10-06/tint_before_after.png` (56 defs, painted vs in game); `strip_tints.py` verified, NOT applied; skips 3 reskins over shared art (RSW_VentStalker, RSW_WraidAlpha, RSW_ShadeWhale) whose tint is all that tells them apart.
- `RM_Ulkhoss` built from his kept bluedesert_Vapaad_v2 render into RM_TheChill (0.08): name and stats are BENCH's guesses for his correction.
- Open card questions: does a giant/predator sea creature owe a fishTypes catch (Twilight giants RM_GrippingTerror, RSW_SandoAquaMonster; RM_Ulkhoss); deploy now that the biomes compose works again (Contagion's duplicate Shambles retired on his words).
- Sheets ready to sit (gate PASS, not yet sat): Grey Sea (half-ruled), The Chill, Twilight Sea, Webwork, The Scald. Failing: Cauldron, Feverwood (Chakroot row), Flooded Canyon, Greentide, Miasma, The Forge, The Rot, Wasteland, Weeping Stones (Ambrosia: he purged its only render), Long Shade, Leaning Scrub.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NORTHSTAR_RESULTS_JOIN_1` — report names unread mods; no join yet; NEXT: add a `checkout:` walk header naming proof_all.py and teach required_checks.py + the report to read its rows.
- `GREYSEA_FLOOR_PASS_1` — `grey_floor_is_a_place` chain + `world_tile_map_generate layer=/biome=` written, compiled, never run; NEXT: after the composed biomes deploy and a companion DLL build.py deploy at the next restart, run the DivingInteraction suite's grey chain live.
- `TINT_ON_COLOUR_ART_1` — sheet + script ready; NEXT: put strip-all-but-reskins to him on a card, then `python3 Transient/tint_review_2026-10-06/strip_tints.py --apply` per his answer.
- `SHEET_DONOR_COLUMN_FALSE_PASS_1` — req 4 passes on our copy of donor art; NEXT: export `ours`, count an owner-purged donor original as shown-and-rejected, and rebuild Abyss/TheRot/Feverwood/WeepingStones.
- `TWILIGHT_GIANT_CATCHES_1` — waits on his answer; NEXT: ask whether a leviathan/predator owes a catch, then build or close.
- `PROPANE_LAKE_HYDROCARBON_TENTACLER_1` — RM_Ulkhoss built, not deployed; NEXT: confirm name/stats at the Chill sheet, then close.
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — 362 art jobs pending at ~33/h; NEXT: rerun `scaled_review_gate.py all` once the queue drains and list PASS sheets for him.
- `FLYER_FLIPBOOK_ART_1` — sheet shows flip-books (8ca553815); 48 Pyrelands frames still pending; NEXT: when they land, rebuild the Pyrelands sheet and take his flight pick.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A Windows exe launched from WSL survives a subprocess timeout; the gate leaked 915 msedge.exe (filed: lessons).
- `art_sheet.py --biome` without `--date` builds a NEW dated sheet, and skips rebuilds whose inputs look unchanged, so a stale file reads as the new result (see: this handoff).
- Exporting a column flag can change another check's meaning: `ours` was set but never exported, and req 4 relied on that (see: SHEET_DONOR_COLUMN_FALSE_PASS_1).
- `proof_all.py` writes its JSON only after P.run() returns and reads a missing `success` as success (see: PROOF_ALL_DURABLE_RESULTS_1).

## Closed since the last handoff (2)

- `ART_RULING_RENAME_CARRY_1` — a38ce0b3dfec
- `ARTPIPE_REQUEUE_AUTOMATION_1` — 6de6f9515

## Filed and still open (4) — the next seat's queue

- `NORTHSTAR_RESULTS_JOIN_1` — Lead metric can't read proof_all / validation_v2 results; FlowWorks+GSS invisible, 108 mods unrecorded
- `PROOF_ALL_DURABLE_RESULTS_1` — proof_all.py: crash loses all rows, missing success reads as success, --only skips preflight
- `FLOWWORKS_CHECKOUT_SCOPE_1` — FlowWorks: ordinary features only in the on-request extension proof; walk lines lack coverage arrows
- `SHEET_DONOR_COLUMN_FALSE_PASS_1` — Sheet gate req 4 counts our own copy as the donor column (false pass)

## Commits

```
7af27ef7b Sheets: 'our render' relabel keeps its own flag; file SHEET_DONOR_COLUMN_FALSE_PASS_1 (req 4 has passed on our copies of donor art)
ca569a0e7 Sheets: an IN GAME column whose bytes our mod ships reads as OUR art, not donor (The Rot's rot_*_v2 renders failed gate req 3 as 'donor art only')
278983687 FlowWorks extensions harness: earlier chains' pawns vanish when the next chain starts; rivers chains run first; river_site spawns drafted colonists off the plot grid on tropical-mild tiles
128067cb1 LivingBolt wall flit: three options measured against the 1.6 path grid, A recommended
bb9642e0e Overnight sheet refresh state: renders landed, sheets and snapshots rebuilt
3c9bca142 Verified apply+revert: 58 <color> removals in 24 files, XML parses, nothing else changes. Not applied.
89c59dfb2 debug-testing skill: full-list cold load is ~15 min (measured 2026-09-07), not 23-30; two windows, not five seats
e74081e27 lesson: Windows exes launched from WSL survive a subprocess timeout
a9f49b9dc check_sheet now reads a staged prefill (decisions were written only after the gate passed). Each Edge render gets its own profile marker and is stopped after, timeout or not: 915 msedge.exe had piled up and every render timed out.
90982b79c Northstar review: finding 7 confirmed
6c2045f42 File FLOWWORKS_CHECKOUT_SCOPE_1
6617a0474 Validation spec: four passages still enforced the open-line gate the owner removed 2026-09-16 ('Let a model YES green a line.')
c67260094 Human-review docs: the key sheet is built in Transient and filed into the mod's review/ (two docs each told half)
db049199e river_site: mild tiles only (12-24 C mean, |lat| <= 25)
5e7375011 FlowWorks rivers suite live 16/16 PASS (current, swept, works) on a river_site map; river_site retries until the mod's grid shows a fast lane
a3e48e637 Notes: tentacler built, Grey floor checkout ready
2e835f0be Owner 2026-10-04: 'keep Option B in the Propane Lakes'. Invented RM_ name; stats are a first guess for his sheet. Roster 0.08; art installed on his keep ruling.
5701c3b37 Tint review contact sheet: 56 tinted defs, painted vs in-game (TINT_ON_COLOUR_ART_1)
e6ae63376 FlowWorks rivers suite: river_site.py founds a mild river map; ProofShove args ';'-separated; weir proof site kept off the map edge
0785ee241 Generates the Grey floor map straight on RM_SeabedLayer (no landing, no painted tile needed) and censuses pillars, crystals, ruled flora, cast. Compiles; DLL deploys at next restart. NEVER RUN LIVE.
... 15 more: git log --oneline 111802360..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: held by FOUNDRY for "GimmeSomeSlack review map for owner walk" (its hold, not BENCH's)

Uncommitted: only `conversations/` (hook-written session transcripts, deliberately untracked, not BENCH work). Sheet state committed at e9625c987.

