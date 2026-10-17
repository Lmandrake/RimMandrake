# BENCH_REBOOT_HANDOFF_202610170103 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610161821`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The FlowWorks level solve (2732aa5faa + body fix 50da06da8b, DLL 31f335066b, deployed, L7 PASS live at bc86a9fd8f) replaced the one-level pairwise swap that made canals 1,0,1,0. If water ever looks striped again, the first suspect is how wet cells join into one body (a single dry dug cell between two wet ones must bridge them), not the kernel. And: a plain `load_game` over a live game KILLS the game — go through `go_to_main_menu` (loadwalk.py); the `jawa/static_call` test-profile grant expires and needs renewing (companion_profile.json).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Walk save for his return: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_FW_walk_20261016b.rws` (rebuilt after the layout moved inward; game paused on it at station 1, bridge FREE). Stations still owed his eyes: 1, 2 (verdict after the level fix), 3 tar, 11 'runs' look, 12 slime, 45, 51.
- Explosive growth: 5 rounds of rulings in design/RimMandrake/explosive_growth_rulings_2026-10-16.md; the ruled spec design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md has 17 open card lines (OQ-1..17; top: does a dry native live or die after fruit+sprouts; does a wild plant's cycle use up water; how long ground stays wet after rain). Spec finding: vanilla rests plants by clock for 45% of the day, which breaks 'always lit = always growing' on the locked world (OQ-7).
- Pond depth design design/RimMandrake/pond_depth_design_2026-10-16.md: cards D1–D4.
- Venomvine's 4 card questions still wait (previous handoff).
- ModsConfig is the ratchet_pilot tier (21 mods); his full list (minus retired AshkarrFlora) is backed up at Transient/bench_live_20261016b/ModsConfig.OWNER_LIST_no_ashkarrflora.xml — restore with modset_builder --restore when he wants his list back.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS` — rulings rounds 1–5 + ruled spec landed (634991cea0); NEXT: put the spec's OQ-1..OQ-17 to the owner as question cards, 4 per round, starting OQ-6, OQ-8, OQ-9, OQ-7.
- `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` — level solve live PASS (L7, bc86a9fd8f), owner-held; NEXT: walk stations 1 and 2 on RM_FW_walk_20261016b with the owner and record his verdict with rimflow verify --owner-said.
- `FLOWWORKS_REVIEW_WALK` (no item; Transient/flowworks_closeout_2026-10-16.md bucket C) — state passes for 1, 8, 11, 12 in Transient/bench_live_20261016b/fw_afk_batch.md; NEXT: with the owner, walk 1, 2, 3, 11, 12, 45, 51 on RM_FW_walk_20261016b and close each item his look passes.
- `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` — design done (e22508d49c); NEXT: put cards D1–D4 to the owner, then spawn the build (opus).
- `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` — filed from his ruling; NEXT: spawn an opus design pass (own bottles + thirst need, DBH Lite interop, no dependency).
- `SPRINKLERS_DESIGN_PIPES_THEN_PANACHE` — filed; NEXT: spawn an opus design pass for native pipe sprinklers and the VFE adaptation.
- `ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL` — batch RUNNING (140 installed, 72 needs_eyes, 35 pending at 01:03Z; auto-installs/commits per 20); NEXT: when `facing_regen_batch.py status` shows pending 0, build the needs_eyes sheet for the owner with `facing_regen_batch.py montage`.
- `LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK` — bill round trip PASS live (747999af5b); NEXT: state-read the right-click menu and unpowered reason on the review map, then close.

- `SELF_MATCHING_WAITS` (no ledger item; Machinist) — carried from 202610161821 unchanged; NEXT: when knowledge/wait_loop_census/<laptop>-*.json appears in Machinist, check the hook's macOS pgrep assumption against it.
- `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` — biomes/UtinniPatches/SWBestiary deployed, AshkarrFlora moved to D:\Luke\dev\_rmbuild\retired_mods and off his list; ratchet_pilot startup had no unresolved RM_/RSW_/RUT_ refs; NEXT: on his next full-list load grep Player.log for missing plant defs, then close.
- `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` — unchanged; NEXT: put its 4 card questions to the owner after the growth OQ cards.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `load_game` over a running game kills it; go through go_to_main_menu (see: Transient/bench_live_20261016b/fw_afk_batch.md)
- liquid_checks L5 counted filth things, but vanilla thickens an existing filth instead of spawning another — count thickness (filed: lessons)
- review stations inside the 10-cell map-edge sink strip drain off-map silently; review_map.py --plan now refuses them (filed: lessons)
- Windows save names are case-insensitive: RM_FW_walk overwrote RM_fw_walk; check before --save (see: Transient/bench_live_20261016b/walk_prep.md)

## Closed since the last handoff (2)

- `REVIEW_MAP_LABELS_FIX_ORPHANS_ADOPTED` — 45ee83717
- `SPILL_FILTH_FIX_SOIL_SAYS_NO` — b20c1b890a

## Filed and still open (5) — the next seat's queue

- `SPRINKLERS_DESIGN_PIPES_THEN_PANACHE` — Design sprinklers before any water-rule hook: FlowWorks native = rudimentary sprinkler heads on pipes; VFE sprinkler = bold automation and enhancement
- `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE` — Renormalize plant growth and yields planet-wide under the water rule (x0.1 dry, x10 wet+lit, wet natives x4, wood at tree rate, full harvest consumes 
- `REVIEW_MAP_FILL_FOUR_SETTINGS_NO_STAGE` — selftest_review_map.py fails: four FlowWorks settings have no review-map station (pre-existing; found 2026-10-16 while fixing b9ef8959ad). Add station
- `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` — FlowWorks gets its own drinking bottles and its own thirst need (design first); when Dubs Bad Hygiene Lite (+Thirst) is loaded, interoperate without c
- `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` — Natural water cells (ponds, marsh, vanilla water terrain) get partial depth like dug cells: a drying pond shallows all over, then mud, then dry — not 

## Commits

```
3141de8858 FW walk map rebuilt after layout move: RM_FW_walk_20261016b
16e2cc14d3 Facings stand tall batch: 19 creatures' redrawn S/N installed via art ledger (owner's words)
e22508d49c Design: ponds shallow out before mud (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD)
ba5df19d35 FlowWorks review map: gallery grid inside the edge-sink strip; --plan refuses edge-strip cells
b35e6fe427 FlowWorks CHANGELOG: name the 2026-10-16 packaged DLL hash (level solve 31f335066b)
457ce9f479 Ledger: FlowWorks AFK batch verify events
efb7293efd Ledger: FlowWorks AFK batch verify events
747999af5b FlowWorks AFK live batch: stations 11/8/1/12, L5, map controls, door facing, lacquer bill
2e8e684b35 FlowWorks: rescue 6 game-only textures (Doors icons/movers, RM_WallFace_*) into the repo
99f12e07e2 Facings stand tall batch: 19 creatures' redrawn S/N installed via art ledger (owner's words)
7ca3a5b9c0 FlowWorks review: 10 Keyed/Defs XML files CLEAN (batch 5)
3cb879735b FlowWorks review: GptFixesAChecks + RM_LiquidNet CLEAN (batch 4)
efdfa74dfe FlowWorks review: 7 more .cs files CLEAN (batch 3)
85e0fbeba2 FlowWorks selftest: drop a vacuous '|| true' assertion in MapControl_timer_schedule (zero-period call kept, must not throw)
861e701749 FlowWorks review: 11 more .cs files CLEAN (batch 2)
89a3fc7648 FlowWorks review: 11 more .cs files CLEAN (batch 1)
04c6c578c9 Facings stand tall batch: 19 creatures' redrawn S/N installed via art ledger (owner's words)
bc86a9fd8f Level solve live fix 2: L7 both rows PASS (0 stripes, 0 steps)
31f335066b FlowWorks DLL built from 50da06da8b (clean export)
50da06da8b FlowWorks level solve: a one-square dry gap joins wet squares, so 1,0,1,0 water loaded from a save gathers
... 34 more: git log --oneline 2d8aff2bb6..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-17T01:03:24Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/census.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/census.md   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/scale_ground_measured.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/facing_regen_batch_2026-10-16/events.jsonl   facing regen batch runner (running; it commits its own state)
 M Transient/facing_regen_batch_2026-10-16/state.json   facing regen batch runner (running; it commits its own state)
 M Transient/fw_review_map_verify.json   derived: review_map.py regenerates
 M Transient/mc_human_review/KEYSHEET.md   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/mc_human_review/keysheet.html   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours / pre-existing or another agent's derived output: left untouched
 M conversations/2026-10-12-1403-b0ee9afc.md   conversation records: the hourly sweep commits them
 M conversations/2026-10-13-0007-b342a8ee.md   conversation records: the hourly sweep commits them
 M deployed/config/ModsConfig.before-tier-bridge.xml   not ours / pre-existing or another agent's derived output: left untouched
 M infrastructure/state/ledger/events/BENCH.jsonl   not ours / pre-existing or another agent's derived output: left untouched
 M infrastructure/state/ledger/events/OWNER.jsonl   not ours / pre-existing or another agent's derived output: left untouched
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

