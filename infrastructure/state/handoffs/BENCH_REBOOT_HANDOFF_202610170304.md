# BENCH_REBOOT_HANDOFF_202610170304 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610170103`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
RiverWorks AND now RiverColors live inside FlowWorks (01600a60e5/0e472b3fc2, built, NOT deployed); the old standalone folders were moved out of the game Mods dir to D:\Luke\dev\_rmbuild\retired_mods. The FlowWorks DLL in the repo is ahead of the game's — deploy FlowWorks the next time the game is down, or river colours vanish (the standalone is gone).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Card questions waiting, all with recommendations in their docs: thirst/bottles (5) design/RimMandrake/thirst_bottles_design_2026-10-16.md; sprinklers (7) design/RimMandrake/sprinklers_design_2026-10-16.md; growth OQ-1..17; pond D1-D4; Venomvine 4.
- Art review (Codex, two passes): Transient/river_hose_art_review_2026-10-16/REVIEW.md + overview.png — 10 ranked candidate fixes (weir reads as a fish trap; hose/tank/pump/reel ports; pump 2x1 vs 1x1 split). Ford stones: RM_FordStones.xml uses vanilla Terrain/Surfaces/Flagstone, our RM_FordStones.png is unused — one-line fix but cosmetic, needs his yes.
- Facings sheet: Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.html (38 rows/47 pictures; served http://localhost:41715/?t=lX1YllI0yt3x6BbxdTnQWw while the server lives). Batch final: installed 176, needs_eyes 74.
- Walk save + stations still owed his eyes (unchanged from previous handoff): RM_FW_walk_20261016b, stations 1, 2, 3, 11, 12, 45, 51 and map R (rivers).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW` — merged + built, not deployed; NEXT: when the game is down, deploy_custom_mods.py --mod FlowWorks --apply and confirm river colours on the planet map, then close.
- `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` — review landed b5ae71e2a4; NEXT: put its top fixes to the owner as question cards (weir redraw, ford texturePath, pump footprint).
- `ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL` — sheet built (5fa6870aa7), 12 rows refused by art_sheet.py freshness gate (req 15) + MastiffPhalone; NEXT: fix art_sheet.py's req-15 gap and add the 12 rows (list in Transient/facing_regen_batch_2026-10-16/infra_followups.md).
- `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` — design 5b9028bafc; NEXT: put its 5 card questions to the owner, then spawn the build (opus).
- `LIQUID_BOTTLE_LOOP_1` — fill bug already fixed (cf1e75d26), BLOCKED reason stale (BENCH may not re-block FOUNDRY's item; noted); NEXT: FOUNDRY re-runs extension_proof --chains toggle_bottle_loop,toggle_bottle_dirty,bottle_revert + tank chain and updates the block.
- `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS` — unchanged; NEXT: put OQ-6, OQ-8, OQ-9, OQ-7 to the owner as cards.
- `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` — unchanged; NEXT: walk stations 1 and 2 with the owner and rimflow verify --owner-said.
- `FLOWWORKS_REVIEW_WALK` (no item) — unchanged; NEXT: with the owner walk 1, 2, 3, 11, 12, 45, 51 and map R on RM_FW_walk_20261016b.
- `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` — unchanged; NEXT: put cards D1-D4 to the owner.
- `LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK` — unchanged (needs bridge); NEXT: state-read the right-click menu and unpowered reason on the review map, then close.
- `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` — unchanged; NEXT: on his next full-list load grep Player.log for missing plant defs, then close.
- `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` — unchanged; NEXT: put its 4 card questions after the growth cards.
- `SELF_MATCHING_WAITS` (no item; Machinist) — unchanged; NEXT: when knowledge/wait_loop_census/<laptop>-*.json appears, check the hook's macOS pgrep assumption.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- rimflow `block` refuses BENCH on FOUNDRY's item even to correct a stale reason; use `note` (see: LIQUID_BOTTLE_LOOP_1 history)
- facing_regen slug() collided on shared basenames (Jewelbug, Smogapillar); fixed 998c05a8a8 with selftest (see: selftest_facing_regen_slug.py)
- `facing_regen_batch.py requeue <substring>` matches broadly — it also reset GizkaW when asked for Gizka; use a full texPath (see: 998c05a8a8)

## Closed since the last handoff (2)

- `REVIEW_MAP_FILL_FOUR_SETTINGS_NO_STAGE` — e648e99dd7
- `SPRINKLERS_DESIGN_PIPES_THEN_PANACHE` — 86b27742d0aa

## Filed and still open (2) — the next seat's queue

- `RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW` — Merge RiverColors (mandrake.rut.rivercolors) into FlowWorks as part of adding liquids to the world; retire the standalone mod
- `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` — Zoom in on river-works art (weir, stakes, silt trap, ferry, fords) and hose connections (tank, pump, reel side by side); get Codex critique: what it l

## Commits

```
2292bb14f8 Facings stand tall batch: 3 creatures' redrawn S/N installed via art ledger (owner's words)
998c05a8a8 facing_regen: unique slug for colour variants (Gembug, Smogapillar) + batch requeue verb
5fa6870aa7 Facing regen: needs-eyes review sheet (candidates beside installed, true scale) + infra follow-ups
9ef4111c99 ledger sync: CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK implemented
77a51692d4 Contagion suite runs on the saved (already-sick) site: off-retile for the stock-map arm, START biome restored
b5ae71e2a4 River works and hose joins art review: Codex critique, composites, overview Offline composites for river works (no live capture exists); live crops for hose/pump/tank. Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
f95ab27b1f merge River Colors into FlowWorks: retire mandrake.rut.rivercolors and fix every inbound reference
01600a60e5 FlowWorks River colours: move River Colors' gradient and settings into FlowWorks (merge step a)
b557290bc7 Biome sprint round: cauldron, leaningscrub, contagion test sites built; calm reload read back Cauldron census: only Suush alive (Vexxiss/Zisska/Eskith 0). LeaningScrub first try had 0 natives (fresh-map variance); 2nd try clean.
789c2ece06 Facings stand tall batch: 13 creatures' redrawn S/N installed via art ledger (owner's words)
6a555ac5d4 FlowWorks canal fix live-proved: calm 61/0/0, river 20/0/1; CHANGELOG DLL hash
fb5e5bfd35 ledger sync: CANAL_INLET_DIAGNOSE_FIRST_CELL_ONLY note
f11976b498 FlowWorks level solve: a source's mouth never keeps its unit for being wet, so a fed D=1 canal fills (was 1,0,0,0 for ever)
27fb17e11a FlowWorks DLL rebuilt from fead0c39b9cd (clean export)
fead0c39b9 code review log: review_map.py clean mark
492dfe00fd FlowWorks ratchet sign-off: settings window L1 pass, validation_v2 calm 56/5 (canal fills stall), river ext 20/0/1
3b96ba41e8 code review log: FlowWorks python batch g6 clean marks
e6c315c5e7 FlowWorks review sheet: drop row ids the densified run no longer emits; stop saying a pond feeds '5 canal tiles' and a tank holds 5 (yardstick unified)
9435a8b22b FlowWorks conservation selftest: header still said a level is 5 tank units
219e04285c FlowWorks proof_hose: far-end-pump and relay bars still asked for 5 units (= one level in the drum era), now one level in decilitres
... 18 more: git log --oneline 12fd48fbec..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     biome sprint round

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/census.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/census.md   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/scale_ground_measured.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/facing_regen_batch_2026-10-16/events.jsonl   facing regen batch runner state (it commits its own installs)
 M Transient/fw_review_map_verify.json   derived: review_map.py regenerates
 M Transient/mc_human_review/KEYSHEET.md   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/mc_human_review/keysheet.html   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours / pre-existing or another agent's derived output: left untouched
 M conversations/2026-10-12-1403-b0ee9afc.md   conversation records: the hourly sweep commits them
 M conversations/2026-10-13-0007-b342a8ee.md   conversation records: the hourly sweep commits them
 M deployed/config/ModsConfig.before-tier-bridge.xml   not ours / pre-existing or another agent's derived output: left untouched
 M infrastructure/state/ledger/events/BENCH.jsonl   mine: committed in 4dcc51237c
 M infrastructure/state/ledger/events/OWNER.jsonl   owner-seat ledger shard: pre-existing, left untouched
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   derived: review_map.py regenerates
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   derived: review_map.py regenerates
 M src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs   not ours / pre-existing or another agent's derived output: left untouched
?? conversations/2026-10-02-1217-54206aec.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-02-1952-4b4a687b.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-02-2332-d58606e4.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-03-1458-7ed5ddfd.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-04-2105-400ef7dc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-04-2219-962263b0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-05-1426-fab8a134.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-06-0601-5ab77072.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-06-1305-ecebcb6f.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0058-b305fb53.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0059-c857706d.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0120-033b16fc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0547-d6861da6.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-1520-6a6f7a30.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0001-cc216258.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0158-8aeef5fc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0215-c4ae9260.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0217-3acaea39.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1348-bac7589f.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1411-2294fe53.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1411-3ffd55d0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1413-52caf5c0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1413-658e0588.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1414-b4b8553c.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1428-de9591de.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-09-0450-85e0a0f9.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-09-1308-818639f9.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0040-5e2fd376.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0049-58eabd09.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0440-c71b568d.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-1341-91d07ad1.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-2102-71d8c9eb.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-0052-2f152d1c.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-1934-f086ce1a.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-1953-24347684.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-2000-edefebc8.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-12-0625-88710e84.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-13-1146-7444c21a.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-15-1939-5e86e9cb.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-16-0628-abd280e4.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-16-1824-05355635.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-17-0128-782256d7.md   conversation records: the hourly sweep commits them
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-flowworks.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.swap-active.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T125537.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T130318.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T144034.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T161200.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T162747.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261016T125532.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GSS   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230218.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230455.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230639.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231027.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231203.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   not ours / pre-existing or another agent's derived output: left untouched
```

