# FlowWorks: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

FlowWorks is **not the pilot**: it advances beside Explosive Knockback, offline only (owner by card 2026-11-14, "All four
now, offline only"). Its table matches the pilot's columns (`design/concepts/ExplosiveKnockback/version/test_table.json`).

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`: "Yes, lock the other four mods").
  Code exists and is large: `src/RimMandrake/FlowWorks/` (C# mod, a 325+ case C# SelfTest, about 168 Python selftests,
  a northstar proof harness).
- **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 9:07 AM PST (`version/stage_record.json`).
- **Bars:** 57 = 29 inventory rows of `record.json` + 28 leaves of `tree.json` (`coverage_judge.required_ids()`); 59 at the
  lock, his card of 2026-11-14 added `inv_geyser_tub` and `inv_liquid_coating` (61), and his card of 2026-11-14 ~9:43 PM
  PST moved the four wetting bars to 0.2.0 (interventions below; `version/next_version/README.md`).
- **Judge corrections open:** none. FlowWorks has no `coverage_verdict.json` and no `coverage_fixes.json`; the Arbiter
  signed the 59-row checklist covered on 2026-11-05 (`tree.json` coverage). So the pilot's "six corrections" step is
  empty here.
- **Held look statements for this mod:** 103 rows in five files of `design/RimMandrake/validation_holding/` (2026-11-12:
  56 rows; 2026-11-13 morning: 18; 2026-11-13 dig interface: 2; 2026-11-13 evening: 5; 2026-11-14: 22); 83 are placed
  in `version/test_table.json`, all 103 placed. [measured, preflight C8, 2:40 PM PST]
- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 9:07 AM PST).

### The vision (his root paragraph, approved 2026-11-04, OWNER:1793794915205594887; eight lines in `version/vision.md`)

1. Dig canals, pits, moats and trenches; the liquids already on the map (water, tar, fuel, slime) flow in and settle at one level.
2. Every liquid comes from a real supply: the pond drops and refills slowly; a body at the map edge is endless.
3. Its main job is deadly earthworks: moats, covered pit traps, sluices and drawbridges you fill, drain and set alight when you choose.
4. Judged first on one raid: raiders swim a deep moat under a raised drawbridge and tire, a sluice drains it, the drained
   hole holds them as prisoners, and chemfuel pumped in from above is lit by a colonist tossing a flame from the rim.
5. A pit reads as a hole with deep walls; ladders, climbing gear and jumps are the only ways in and out; raiders make a
   ladder to fetch comrades who fell in.
6. (Moved: canal-side wetting left 0.1.0 for 0.2.0 by his card 2026-11-14, OWNER:1794721673433243094.)
7. Pipes, pumps, tanks and hoses are one network moving the same real litres from the same supply.
8. Every feature has superb Mod Settings; no worldgen, no multiplayer.

### His words on this mod (verbatim; ledger ids in `record.json` decisions and `sheet.md` "his words")

- 2026-11-04, the flagship (OWNER:1793794915205594887): "Filled water moat has raiders swimming across it (getting tired
  swimming in deep water), then water drains and they become Prisoners in a prisoner pit for awhile (prisoner mechanic),
  then chemfuel gets pumped in from above and the burning moat mechanic. All with a drawbridge on top that's raised."
- 2026-11-04, wetting (OWNER:1793794389686592719): "Two squares away from the canal should become "wetted" … This isn't the
  same as flood water … Wetted ground means the plants have access to water."
- 2026-11-04, three raid scenes (OWNER:1793794392567351532): the moat; the covered pit trap onto spikes and the makeshift
  ladder under arrows; the island bridges whose winch is destroyed ("Not today").
- 2026-11-04 (OWNER:1793796507483890758): concept budgets are advisory.
- 2026-11-05, by card: "(b) you click 'capture' from the rim as now, but a drained moat (or pit) counts as a prison without
  a bed." · "a new order where a colonist walks to the rim and tosses a flame onto the square the player picks."
- 2026-11-12 and 11-13, live looks at under-liquid pits: 81 held rows (above), e.g. "Tar is not nearly dark enough (fix)",
  "It's as though each case is independently set in these variables, badly (major fix)", "please ensure they can only be
  placed where there are two sides adjacent to solid ground, to avoid "covered pit bridges" being built."
- 2026-11-13 09:55 PST, on Explosive Knockback: "Melee shove is a great idea, but it belongs in FlowWorks, not here."
  (FlowWorks 0.2.0, Divergent, `version/next_version/README.md`; his card 2026-11-14: "Next FlowWorks version")
- 2026-11-13 ~9:45 PM PST: "The vast grid of options when I selected Digging was... daunting and not how the game usually
  is." (RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION; FlowWorks 0.2.0, Divergent, his card 2026-11-13 10:12 PM PST: "All in the next version")

### Oddities (things a reader would otherwise get wrong)

1. **Three bar vocabularies.** The 57 checklist rows are the bars of 0.1.0. The sheet's `[floor:…]` lines (mod_settings,
   tick_cost, worldgen, multiplayer) and the 22 lines of `floor.json` are floor lines every mod meets, not among the 59.
   The older north-star bars in `northstar/` and the walk doc are a third list, not reconciled with the 57.
2. **The inventory's `proof` field reads `stale` (20), `missing` (7) or `exercised_unrecorded` (1)**: it records
   proof-run freshness on 2026-11-05, not whether a test exists.
3. **Three inventory rows are `impl: absent`** at the lock: `inv_prison_no_bed`, `inv_toss_flame`,
   `inv_raider_fetch_fallen`. Their leaves (`drained_hole_is_a_prison`, `toss_flame_from_rim`,
   `raiders_fetch_their_fallen`) are owed code, not owed tests. (`inv_irrigation`, `unknown` at the lock, left for 0.2.0.)
4. **`stage.json` is the only locked file that moved since the lock** (blob `3af342069` → `34f93a515`; state, not a bar).
   The seven bar files are byte-identical to `version/bars.md`. `stage.json` reads `locked` since 2026-11-14 (it read
   an OWNER HOLD pending the lock until then; intervention of 2:28 PM PST). [measured 2026-11-14]
5. **Every live scene's tier says "quicktest"**, but the `tier_reason` of 25 of 31 leaves is one boiler-plate sentence ("an
   on-screen look and a live state change: needs a running map"). Whether a faster test decides each is the Stage 4
   challenger's question; the reason is written, not shown true.
6. **The C# SelfTest is one console app holding most of the offline checks** (325+ cases); a Python wrapper
   `src/RimMandrake/Utils/selftest_flowworks_stock.py` builds it with Windows `dotnet.exe`. One run covers many bars.
7. **The Stage 3 offline checks of five bars are source laws, not behaviour runs** (`selftest_stage3_owed.py`): the
   code is Verse-bound. They decide "the code that would make the bar true exists and has this shape"; whether it
   works is the scene's question at Stage 6.

## History (dated, added to only)

### Conductor interventions (one line each, added to only; the form is in the spec §5, "The steward and the journal")

- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind hold): Stage 3 is held while the look-fix builder (item `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE`, run since 11:53 PST) edits FlowWorks water code; the other three mods' Stage 3 runs started at 12:15 without it. Source: the Conductor's brief for the Maturation page (12:20 PST) and the detached-run records.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 2:05 PM PST, kind bar-added): bar `inv_geyser_tub` added to 0.1.0: "A pit dug on a geyser keeps the geyser at its bottom; once water or another harmless liquid covers the vent it bubbles there as real bubbling water, the pit reads Hot Tub on mouse-over, and pawns nearby bathe in it for vanilla's small hot-spring bonus, while a geyser beside the water rather than under it heats nothing." Checked at Stage 4-5 by `T_GEYSER_TUB` (C# `GeyserTub_*`, 11 cases green) and `PY_FLOWWORKS_GEYSER_TUB` (green); at Stage 6 by scene `sc_geyser_tub` (entry absent, owed Stage 3, UNRUN); looked at Stage 8. Its 11 held rows now name it; `record.json` re-pinned in `version/bars.md`. Source: owner by card 2026-11-14 (OWNER:1794693278631337978).
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 2:05 PM PST, kind bar-added): bar `inv_liquid_coating` added to 0.1.0: "A pawn who comes out of oil, tar, blood or another staining liquid carries it as a named condition with a clean, not crude, look, and walking into normal water plainly washes it off." Checked at Stage 4-5 by `T_LIQUID_COATING_OFFLINE` and at Stage 6 by scene `sc_coating_wash`, both owed Stage 3 (no coating condition exists in the code; item `RIMMANDRAKE_DESIGN_LIQUID_DIRT_AS_CONDITION_NOT_GRAPHICS`), the scene UNRUN; looked at Stage 8. Its 3 held rows now name it; `record.json` re-pinned in `version/bars.md`. Source: owner by card 2026-11-14 (OWNER:1794693278631337978).
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 2:16 PM PST, kind release): the 12:15 hold on Stage 3 is released; the look-fix builder in FlowWorks water code ended 12:54 PM PST with six fixes on origin/main, so Stage 3 "reconcile" starts now on detached run RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT. Source: ledger notes on RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE (2026-11-14T20:53Z, 20:54Z) and the Conductor's Stage 3 brief.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 2:28 PM PST, kind decision): `stage.json` and `VERSION.json` made to agree with the truth, by the steward's standing decision in the Stage 3 brief. What was wrong: `stage.json` still read status `blocked` on the 2026-11-13 OWNER HOLD "pending the lock", a day after the lock landed on his word; `VERSION.json` said 59 bars and carried a caveat about the older CONCEPT_LOCK block, while the table and the lock record hold 61 since his card of 2026-11-14. Now `stage.json` reads `locked` (as Explosive Knockback's), and `VERSION.json` reads 61 bars, 59 of them met by the Arbiter's 2026-11-05 signing and the 2 added bars never judged. No bar file changed, so nothing re-pinned. Source: detached run RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT, batch 2.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 10:05 PM PST, kind decision): deferral by his card: bars `inv_irrigation`, `canal_wets_two_squares`, `wetting_is_not_flood` and `wetness_probe` left 0.1.0 for 0.2.0 (61 to 57 bars), with test `T_WETTING_OFFLINE`, `T_WETNESS_PROBE_OFFLINE` and scene `sc_wetting`; `sc_garden` lost its wetting feature, rows and control clause; build items `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP` and `FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST` aimed at 0.2.0. Objects kept in `version/next_version/wetting_from_0.1.0.json`. Source: owner by card 2026-11-14 ~9:43 PM PST (OWNER:1794721673433243094).
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 10:05 PM PST, kind re-pin): check X4 in `validation_v2.py` rewritten to follow the pit sink of 0.05 per half metre (drawn 4 x 0.05 down at D=4, the wall ratio agreeing with it), a new mock fault `wall_ratio_off` seen turning it red; the C# case `PitDraw_sink_is_monotonic_in_depth_and_follows_the_pit_sink` and `RM_PitDrawMath.DefaultSinkPerLevel` (0.3 to 0.05) follow too; the retired wall-height number is deleted from the north star (`pit_trapped_reads_as_trapped`, re-validated by his card), the pit item, `human_review.py` J04 and seven design docs. Source: owner by card 2026-11-14 ~9:43 PM PST (OWNER:1794721678572743709).
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 10:05 PM PST, kind re-pin): `version/bars.md` re-pinned for tree.json, sheet.md, scenes.json, record.json and plan.md after the wetting move; tree hash now `5b90f4e381`, sheet hash `16533ac4f2`. The Arbiter's coverage signature names the lock's hashes, so `concept_tree.py gate` refuses on hash; nothing in Stage 3 reads that gate. Source: this journal's deferral line above.

### 2026-11-14 11:24 PST, advance begins (rm-builder, detached, offline only)

Brief from the Conductor: rows 1 to 3 of the pilot table by hand (journal, finish Stage 1, Stage 2), throwaway scripts
only, stop before Stage 3; FlowWorks advances beside the pilot, so its counts are its own. Owner, 2026-11-14: "We need to
get this going."

### 2026-11-14 11:28 PST, row 1 done: journal started

- **Cost:** about $1.9 of model spend (the harness budget line; tokens not separately measured), about 5 minutes wall.
  Nearly all of it reading: the spec, the pilot's journal and draft table, the version folder, `record.json`,
  `tree.json`, `scenes.json`, `sheet.md`, the four held-statement files.
- **Boring enough to automate:** "his words" (already in `record.json` decisions and `sheet.md` with ledger ids); the
  post-lock drift check (one `git hash-object` per pinned file against `bars.md`); counting held rows per mod; the
  `proof`/`impl` census of the inventory.
- **Needed judgment:** which oddities would trip a cold reader (three bar vocabularies, `proof: stale` is not "no test",
  absent rows owe code not tests); seeing that the pilot's correction step is empty for this mod.

### 2026-11-14 11:50 PST, row 2 done: Stage 1 finished by hand

The table: `version/test_table.json` (read view `version/test_table.md`), same columns as Explosive Knockback's. Made by
`version/advance_scripts/make_table.py` and `held_place.py` (throwaway; kept only as provenance for the Stage 2 program).

- **Runnable tests, measured by running every one today** (offline only; the game was never touched):
  - C# SelfTest, one full run: **1,337 cases ok, 0 failed, 531 s**. Two cases are defined in source but never reached
    (`Sheet_runs_back_into_the_canal_when_it_is_drawn_down_relief_…`, `LadderClimb_slow_only_on_the_art_D…`).
  - Python selftests under `src/RimMandrake/FlowWorks` (169 incl. the kernel oracle): **159 pass, 10 red, ~1,360 s**.
    Red and deciding a bar: `northstar/selftest_flowworks_northstar.py` (settings classes missing from
    `site_spec.SETTINGS_SOURCES`), `Tools/selftest_liquid_looks.py`, `selftest_natives_drink_own_water.py` (RM_TheChill:
    RM_PropaneDeep → RM_Liquid_Propane blocked), `validation_v2.py --offline` (O2: `digLabourMultiplier` C# default
    None, table 4.0; O8; O-LIVE-NEG X4_pit_wall_over_head). Red but not mapped to a bar (harness or look tests):
    `selftest_extensions.py`, `selftest_lines_proof.py`, `selftest_flowworks_call_sites.py` (55/56),
    `selftest_flowworks_looks_round.py` (tar tint), `selftest_flowworks_readout_proof_parity.py`, `selftest_hose_port.py`,
    `selftest_review_map.py`. Another helper is editing water code: some reds may be that work.
- **Counts (measured, `test_table.md`):** 59 bars. **51 already had at least one runnable test** (an offline test that
  ran, or an in-game scene whose entry function exists). **49 have a built offline deciding test; 44 of them all green
  today.** 25 have every deciding test runnable today. 2 have no offline decider at all (`moat_raid_sequence`,
  `walk_moat_season`: the game alone decides them). In-game scenes: 29, entry exists 14, absent 15.
  Offline tests: 78 built (74 green, 4 red), 6 specified for Stage 3 (wetting, wetness probe, toss flame, fetch fallen,
  bedless prison care, dig-time arithmetic).
- **Judge corrections:** none to apply (no verdict file; Arbiter signed 2026-11-05).
- **Held statements:** all 81 rows placed (`held_statements` in the table): 58 on a bar and a test; 10 are harness,
  process, rule or answered-question rows with no bar; **13 have no 0.1.0 bar** (the geyser hot tub and its bubbles, 9 rows; liquid coating on pawns and washing it
  off, 3; the dig-interface consolidation, 1): questions for him, below.
- **Settings sweep moved offline:** FlowWorks' in-game "sweep" is `validation_v2.py`'s live L2 `settings_default` read.
  Every default it compares is decidable offline: `T_SETTINGS_SWEEP_OFFLINE` = C# `SettingsReset/MachinerySettings/
  Settings` cases + `selftest_settings_registry.py` + `selftest_settings_search.py` + the northstar selftest's registry
  rows + `validation_v2.py --offline` O2. The game keeps only `sc_walk`'s master switch off and on mid-game; L2 stays a
  harness precondition, not a bar. No bar text edited. **It is red today** (O2 and the northstar registry rows).
- **Cost:** about $4.0 (harness budget $1.9 → $5.9), 22 minutes wall, of which ~9 min C# suite and ~20 min Python sweep
  ran in the background in parallel with the mapping.
- **Boring enough to automate:** running every selftest and recording rc and seconds; per-case C# results by prefix;
  checking each scene's entry function exists; row counts of held files; rendering the md view.
- **Needed judgment:** which C# case families and which Python selftests decide which bar (the regex groups in
  `make_table.py`; a judge should challenge them); telling mod tests from harness tests; placing 81 held rows (which bar,
  or "no bar"); recognising that FlowWorks' "settings sweep" is the L2 live read and that O2 already decides it offline.

### 2026-11-14 11:52 PST, row 3 done: Stage 2 by a throwaway program

`version/advance_scripts/preflight_fw.py` (no model) checked the table against the repo, a copy of the def dump
(`game_paths.DEF_DUMP`, captured 2026-11-12) and the ledger; record `version/preflight.json`. Fifteen checks, the pilot's
C1–C12 and its items check plus "every scene proves a leaf" and "tiers consistent". **Run time 0.24 s** (plus about a
minute to copy the 541 MB dump from the Windows drive). **Verdict: refuse, 37 refusals in three checks.**

- **C6 built tests run (22):** 4 red offline deciders (`selftest_flowworks_northstar.py`, `selftest_liquid_looks.py`,
  `selftest_natives_drink_own_water.py`, `validation_v2.py --offline`); 5 offline tests specified, not built (wetting,
  wetness probe, toss flame, fetch fallen, bedless prison care); 13 in-game scenes whose entry function does not exist
  (all in `northstar/concept_scenes.py`: fill front, one surface, source pays, pawn height, hose look, trench cover, ice,
  moat raid, toss flame, wetting, fetch fallen, islands, the season walk). Route: Stage 3.
- **C8 held statements (13):** every row is placed, but 13 have no 0.1.0 bar (geyser hot tub 9, liquid coating 3, dig
  interface 1). Route: his call, Problem (a new bar now) or Divergent (`next_version`).
- **C13 scenes prove a leaf (2):** `sc_pit_trap_raid` and `sc_garden` name no requirement; they are showcase scenes whose
  inventory rows are named only in `showcases`. Test text, not bar meaning: a neutral fixer could add their leaves.
- **Passed:** bars complete (59/59), every bar has a deciding test, every test has a stage, files and reads real (273
  reads), game reasons written (29 in-game tests), defs real (12 RM_ names), locked files unchanged (7 pinned files
  byte-identical; stage.json exempt as state), owed items real, tiers consistent. **C10 (mods) and C11 (settings fields)
  pass vacuously:** the scenes name no packageId and no settings field (probed by grep), so they decide nothing here.
- **The checker was watched failing:** planted faults (a dropped bar, an undefined test, an empty decides list, a missing
  file, a blank game reason, an unplaced held row, an invented RM_ name, a red result) each turned their check red (C1,
  C2, C4, C6, C7, C8, C9). C12 was not mutated.
- One of my own table errors was caught on the way: the wetting test named an item I had not filed; it now points at the
  existing `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP`.
- **Cost:** about $0.5 (harness $5.9 → $6.4 incl. the publish), 3 minutes wall.
- **Boring enough to automate:** all fifteen checks; this script is the seed of the Stage 2 program (spec §9 build order 3).
- **Needed judgment:** whether a bar-less held row is a refusal or a placement (taken as a refusal routed to him);
  reading C10/C11's zeros as blind rather than green.

### 2026-11-14 from 2:16 PM PST, Stage 3 "reconcile" (rm-builder, detached, offline only)

Batch 1, the four red offline deciders (preflight 48 → 45 refusals):

- `PY_FLOWWORKS_NORTHSTAR`, **the test's table was wrong**: `site_spec.SETTINGS` lacked today's `pitEdgeStraddleRefusedEnabled`
  and the whole `RM_GeyserPitSettings` class (14 bools, 4 numbers); the toggle count was pinned at 244 while e2fffa4f50 had
  already made it 246. Table caught up, count 261. Bar meaning unchanged. Green.
- `PY_LIQUID_LOOKS`, **the generator's table was wrong**: 441c321a20 (his look of 2026-11-12, "It should be dark indeed.")
  and 9a7b10befc edited the generated XML by hand (dark tar, fresh water see-through 0.45, coolant labels), so the
  byte-compare failed. The table in `Tools/generate_liquid_suite.py` now holds those values; the regenerated XML differs
  only by two comments that moved into the generator. The tint assertion in `selftest_liquid_looks.py` and
  `selftest_flowworks_looks_round.py` now names his newer word. Green.
- `PY_NATIVES_DRINK_OWN_WATER`, **the mod was wrong**: three home waters were undrinkable to their natives against his
  ruling of 2026-11-01 (Miasma's brackish band, both depths; The Chill's `RM_PropaneDeep`). Marked `nativeWater` (generator
  flag for brackish, a patch for deep propane, like the shallows). Green, 0 blocked of 41 water rows.
- `PY_VALIDATION_V2_OFFLINE`, two test faults fixed and one left for him. O2 compared a number (`digLabourMultiplier` 4.0)
  through the bool census and read None: numbers in that table now compare with `site_spec`. O8 allowed one non-literal
  bridge call and the file has two pure pass-throughs: both are named now. Each was watched failing on a planted fault.
  **Left red, his call:** the negative control's X4 row held an older wall-height number that disagreed with the
  `pitSinkPerLevel` 0.05 he confirmed 2026-11-13 ~9:50 PM PST (0.2 cells down at 4 levels). Making X4 pass meant
  loosening a check, which is his; he answered by card 2026-11-14 (question 6, history below).

Batch 2, table work (preflight 45 → 23 refusals):

- **The 20 held rows of 2026-11-14 are placed** (`version/advance_scripts/held_place_1114.py`): 6 on a bar with a test that
  exists (rows 1, 3, 7b, 12 on the look-fix builder's C# `PitLook1114_*` cases, now table test `T_PIT_LOOK_1114`, and its
  live script `PIT_LOOK_1114_LIVE`, UNRUN; rows 7 and 10d kept approvals), 2 on a bar with a specified test (5 loose-ground
  dig refusal, 11 sluice square level), 6 next-version (8, 10, 10c, 10f, 12b per his own words or the 10f ruling), 4
  harness or dev tooling (6, 9, 9b, 10b), 1 another mod's (2), 1 answered question (10e). Row 4, the swale rebuilt as a
  soaking floor, has no 0.1.0 bar: his call (question below).
- `dig_interface#2` is placed as next-version work (his card 2026-11-13 10:12 PM PST, recorded in 261f053e64).
- **Two preflight check corrections**, meaning unchanged: C8 now accepts "next version" and "other mod" as placements (its
  own would-pass named a next-version entry); C13 reads a scene's `features` as well as `requirement` (the two showcase
  scenes named their leaves under `features`) and now refuses a named leaf that is not in `tree.json`. Both watched
  failing on planted faults (an invented leaf, a scene with neither field: 2 refusals).
- `version/advance_scripts/render_table.py` recomputes each bar's derived fields and rewrites `test_table.md`.

Batch 3, the owed tests (preflight 23 → 7 refusals):

- **17 in-game scene entries written** in `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` (the 13 of the first
  preflight, the two showcase scenes, and `scene_geyser_tub` and `scene_coating_wash` for his two new bars), on one shared
  stage helper: stage, act, read, the control case where the scene names one, restore settings and the scene-begin save.
  Each is UNRUN, listed with its command (`python.exe ...concept_scenes.py --scene <name> --out <json>`). Checked: imports,
  every bridge call literal and in the tool schema (54 calls; the lint watched failing on two planted bad calls), a smoke
  run of all 17 on a fake bridge (0 Python errors), and `selftest_hole_prison.py` still green on the extended file.
  **Not checked:** the argument shapes of a few tools and proof verbs (named in the file's header) and every coordinate;
  Stage 6 owns those on its prepared map. Controls not written: the islands' indestructible winches, the hose's unpowered
  pump, the garden's unpowered pump, the walk's pre-fill reload.
- **6 offline tests built** in `src/RimMandrake/FlowWorks/selftest_stage3_owed.py`, one `--only` section each, as source
  laws over the shipping code (the code is Verse-bound; the C# SelfTest cannot run it). `T_PRISON_CARE_OFFLINE` is green,
  and its five undo mutants each turn it red. **Red as intended, the behaviour is absent:** `T_WETTING_OFFLINE`,
  `T_WETNESS_PROBE_OFFLINE`, `T_TOSS_FLAME_OFFLINE`, `T_FETCH_FALLEN_OFFLINE` (the ladder half exists, the fetch does not),
  `T_LIQUID_COATING_OFFLINE`.
- `T_PIT_LOOK_1114` ran: the look-fix builder's 7 C# cases and the 11 geyser-tub cases, 18 of 18 ok, 232 s.

Stage change, Stage 3 "reconcile" (2:14 to 2:47 PM PST, rm-builder, detached):

- **Cost:** about $9.5 of model spend (the harness budget line, $0 → about $9.5 of the $15 bound; tokens not separately
  measured); about 33 minutes wall, of which about 4 minutes were one C# SelfTest run and 1 minute the v2 offline tier;
  none of his minutes.
- **Boring enough to automate:** re-running a named test and writing its result into the table (`rerun_tests.py`);
  recomputing each bar's derived fields and the md view (`render_table.py`); the preflight itself; linting a scene file
  against the tool schema and smoke-running it on a fake bridge; finding which commit hand-edited a generated file.
- **Needed judgment:** whether a red test was the mod or the test (two tables behind the mod, one mod against his
  ruling, one check against his newer word, left to him); which bar each of 20 held rows sits on, and which are next
  version, harness or another mod's; that a checker refusing named leaves was blind, not the scenes wrong; what a
  scene's rows and controls are when the mod has no hook yet; stopping short of building behaviour that his thin-film
  ruling or a design item may change.

### What Stage 3 ("reconcile") must build, not begun here

1. Make the 4 red offline deciders green (settings registry / O2 `digLabourMultiplier`, liquid looks, natives' propane
   drink, the v2 offline tier): small, a fixer each, unless the concurrent water work explains them.
2. Build the 5 specified offline tests failing first, and their code where it is absent: wetting and the probe (code
   absent: large), toss flame (absent: medium), raiders fetch their fallen (partly present in `RM_PitAccessMath`:
   medium-large), bedless prison care (code present in `RM_PitPrisonCare.cs`: small test).
3. Write the 13 missing scene entries in `concept_scenes.py` (live tests, built and listed UNRUN with their commands per
   his 2026-11-13 ruling): large in total, about one hour of builder time each for the simple ones, more for the three raids.
4. Reach or delete the 2 never-reached C# cases; add leaves to `sc_pit_trap_raid` and `sc_garden` (neutral fixer).
5. The specified held checks (GodLiquid naming and never-"No room", the deep-opacity and blue-with-depth parity rows, the
   drafted-move release ring): small each.
6. The two bars his card added on 2026-11-14: the coating condition, its washing and `T_LIQUID_COATING_OFFLINE` (code
   absent: medium), and the scene entries `scene_geyser_tub` and `scene_coating_wash`.
7. Place the 20 held rows of 2026-11-14 that are not yet in the table (preflight C8).

### What remains after Stage 3 "reconcile" (2:45 PM PST)

1. **Four behaviours to build**, each item now carrying its acceptance test (ledger notes 2:41 PM PST):
   FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP (wetting and its probe; see question 5 first),
   FLOWWORKS_FLAME_BUILD_TOSS_FROM_THE_RIM, FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN,
   RIMMANDRAKE_DESIGN_LIQUID_DIRT_AS_CONDITION_NOT_GRAPHICS (a design item: the coating's look wants a ruling first).
2. **X4 in `validation_v2.py`**: his call (question 6).
3. **Row 4 of 2026-11-14, the swale**: his call (question 7).
4. **Stage 6 owns** the first run of the 17 written scenes and `pit_look_1114_live.py`, their coordinates, the unverified
   argument shapes named in `concept_scenes.py`'s header, and the four controls not yet written.
5. Not done here: the 2 never-reached C# cases and the specified held checks (items 4 and 5 of the list above); the
   code review (`code_review_status.py`) of the files this stage touched, all DIRTY.

- 2026-11-14 9:25 PM PST, Stage 3 offline build (detached, RIMMANDRAKE_AUTOBUILD_FLOWWORKS_SEVEN_BARS_LEFT): built the Stage 6 look `LOOK_BLIND_READER` as `src/RimMandrake/FlowWorks/northstar/blind_reader.py` (18 closed questions, a foil per bar from scenes.json, a fresh sandboxed `claude -p` reader; UNRUN until the Stage 6 captures) with `selftest_blind_reader.py` (6 mutants red; a fresh Opus review's 8 defects fixed); test table remade, bars not runnable 7 -> 0.

- 2026-11-14 ~9:43 to 9:47 PM PST, his answers by card to questions 5, 6 and 7 (ledger notes on
  RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT):
  - 5, wetting: *"Move wetting to 0.2.0: the wetting bars leave 0.1.0 by his word and arrive in 0.2.0 with the thin
    film"* (OWNER:1794721673433243094). Four bars moved; interventions above; `version/next_version/README.md`.
  - 6, pit sink: *"Keep 0.05, retire the 20% rule; the old check (X4 in validation_v2.py) is rewritten to follow 0.05"*
    (OWNER:1794721678572743709). X4 rewritten and green; the old number deleted where it stood (interventions above).
  - 7, swale: *"Next version, 0.2.0; 0.1.0's bars do not move"* (OWNER:1794721683744408896). Divergent, entry in
    `version/next_version/README.md` pointing at RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE.
  Enacted by detached run RIMMANDRAKE_ENACT_FLOWWORKS_THREE_CARDS_WETTING_SINK_SWALE (offline only).

### Questions for him (none blocks Stage 3)

None open; question 3 (the dig speed) is answered in the history entry of 2026-11-15 11:45 AM PST.

### 2026-11-14 11:49 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by CONDUCTOR)

- Why: Every Stage 3 exit test passes after his three cards were enacted (39753a53ff)
- Checks passed: order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle.
- Blind cycle 1 of this visit (1 in all).
- Was, "Stage now": - **Stage now:** Stage 3 "reconcile" done as far as offline work can take it, 2026-11-14 2:45 PM PST: every bar has a check that runs (offline) or exists (in-game, UNRUN); five bars' offline checks are red because their behaviour is not built, one is red on his call (history, Stage 3). Stage 1 by hand 11:50 PST; Stage 2 by a throwaway program.
- Was, "Waiting on": - **Waiting on:** builds for three absent behaviours (the toss-flame order, raiders fetching their fallen, the liquid coating), each now with its acceptance test on its item. Wetting and its probe are 0.2.0 work since his card of 2026-11-14. Open question for him: dig speed (end), which waits on the 0.2.0 dig-interface design. Preflight: refuse, 7 refusals (`version/preflight.json`, 2026-11-14 2:40 PM PST; 48 when Stage 3 began).
- Record: `version/stage_record.json`.

### 2026-11-15 3:42 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by CONDUCTOR)

- Why: Blind challenge cycle 1 exit met by the program's reading after a neutral reconcile (18b41519f3) and the sprinkler exact-fit fix (4b37a37db9); night order of 2026-11-15
- Checks passed: order, version, hold, steward_confirms.
- Steward confirms: Read the judge's report, the neutral fixer's and the sprinkler fixer's: 5 offline bars green (8 deciders rerun PASS), all 6 Problems fixed and shown red on the parent and green on the fix by the fixer's own runs, the one remaining lane-1 FAIL (sprinkler one cell short on an exact fit) was fixed instead of moved to Polish (lane 1 now 43 PASS, 0 FAIL), the judge's two loosened blind tests were both right, the pit-cover check now reads the compiled signature. Owed to Stage 6: 7 UNSETTLED game-side rows, the three planted faults no offline test caught, the overflow sheet shipped off until live acceptance.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-14 11:49 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-14 11:49 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 11:45 AM PST, question 3 answered (by BENCH)

- This answers question 3 (the dig speed), delegated under his Evidence-for-Ask ruling
  (RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME): Divergent, 0.2.0. His card of 2026-11-13 10:12 PM PST put
  the whole dig-interface redesign in the next version, *"All in the next version"* (OWNER:1794636834064875208), and
  `version/next_version/README.md` names the speed target as a question inside that design
  (RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION). No 0.1.0 decider waits on it: T_DIG_TIME_ARITHMETIC only
  supports canal_reads_as_dug and inv_dig_depth. Held row `2026-11-13_dig_interface#1` in `version/test_table.json` and
  `.md` now reads 0.2.0 Divergent instead of "his open call"; 0.1.0's bars do not move.

### 2026-11-15 2:51 PM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: delegated: steward road back: visit 1 exit not met (16 PASS, 3 FAIL, 12 UNMEASURED of 31, two earlier FAIL rows); two failures are unbuilt mod behaviour (toss-flame order, coating condition), so the road is offline_build, not blind_challenge; 16 items filed caused by RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_ONE_FAILURES_BACK
- Checks passed: order, by, version, hold.
- Steward confirms: read design/concepts/FlowWorks/version/in_game/visit_1/SUMMARY.md and rows.jsonl (72 rows): exit_met false, verdict NOT met; FAIL sc_toss_flame, sc_coating_wash (MOD, real miss), sc_moat_raid (MOD dep + harness); UNMEASURED 10 scenes (harness/site real misses), OL_OWNER_LOOK_READS (criterion-flaw candidate), PIT_LOOK_1114_LIVE (bridge Int64 instrument gap); sc_fill_front/sc_fill_tiers earlier FAIL are record gaps (harness fixes at mod sha 8caccd561c, no red-before test); the driver's three test edits are stricter, none weakened
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: steward road back: visit 1 exit not met (16 PASS, 3 FAIL, 12 UNMEASURED of 31, two earlier FAIL rows); two failures are unbuilt mod behaviour (toss-flame order, coating condition), so the road is offline_build, not blind_challenge; 16 items filed caused by RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_ONE_FAILURES_BACK
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-15 3:42 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 3:42 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 4:14 AM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: steward advance: every Stage 3 exit test passes (order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate); certificate OK (55 bars, red_seen unproven warn only); gate open; opens blind cycle 2 (visit total 1 so far)
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: Read maturation next/show/certificate/gate (all pass, no not-met reasons to sort) and cycle_1 tests_edited.json: the only judge-loosened test, lane1 BlindLane1.cs d8f6162->17d2a9d, widens conv budget tolerance to the kernel's own floor(accrued/inU+1e-4) slack (RM_ConversionMath.cs:34) and counts a held part-batch as not lost; both rows still FAIL on the old kernel and PASS on the fix per SUMMARY: CRITERION FLAW repaired, meaning kept, not a REAL MISS. Verdict: advance.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: steward advance: every Stage 3 exit test passes (order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate); certificate OK (55 bars, red_seen unproven warn only); gate open; opens blind cycle 2 (visit total 1 so far)
- Blind cycle 1 of this visit (2 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-15 2:51 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 2:51 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 9:07 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: steward road back: blind cycle 2 FIXED all 5 Problems at 4b33b22f00 (problems_open 0, 5 offline bars green), so a new blind judge is owed to judge the fixes; judge-the-judge: the 11 certificate refusals were all RECORD GAP (ran_on_this_build stale after the fixes changed the tests), redone for real by certificate --run, now OK on 55 bars; tests_edited.json diffs only add or tighten (3 replaced lines are stricter supersets); no CRITERION FLAW, no REAL MISS
- Checks passed: order, by, version, hold, fourth_cycle, judge_certificate.
- Steward confirms: read cycle_2/SUMMARY.md, faults.json, tests_edited.json and the 5 test diffs a395d97a12..4b33b22f00; 5 Problems FIXED and closed, 4 Polish filed (Polish list); certificate --run OK; verdict: new blind judge owed, cycle 3
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: steward road back: blind cycle 2 FIXED all 5 Problems at 4b33b22f00 (problems_open 0, 5 offline bars green), so a new blind judge is owed to judge the fixes; judge-the-judge: the 11 certificate refusals were all RECORD GAP (ran_on_this_build stale after the fixes changed the tests), redone for real by certificate --run, now OK on 55 bars; tests_edited.json diffs only add or tighten (3 replaced lines are stricter supersets); no CRITERION FLAW, no REAL MISS
- Blind cycle 2 of this visit (3 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 4:14 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 4:14 AM PST).
- Record: `version/stage_record.json`.
