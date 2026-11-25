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
- **Stage now:** Stage 7, the walk brief, since 2026-11-25 12:00 PM PST (`version/stage_record.json`).
- **Bars:** 55 = 28 inventory rows of `record.json` + 27 leaves of `tree.json` (`coverage_judge.required_ids()`); 59 at the
  lock, his card of 2026-11-14 added `inv_geyser_tub` and `inv_liquid_coating` (61), and his card of 2026-11-14 ~9:43 PM
  PST moved the four wetting bars to 0.2.0 (57), and his word of 2026-11-23 ~11:05 PM PST moved the raid proof to 0.2.0
  (55; interventions below; `version/next_version/README.md`). No 0.1.0 scene stages a raid.
- **Judge corrections open:** none. FlowWorks has no `coverage_verdict.json` and no `coverage_fixes.json`; the Arbiter
  signed the 59-row checklist covered on 2026-11-05 (`tree.json` coverage). So the pilot's "six corrections" step is
  empty here.
- **Held look statements for this mod:** 103 rows in five files of `design/RimMandrake/validation_holding/` (2026-11-12:
  56 rows; 2026-11-13 morning: 18; 2026-11-13 dig interface: 2; 2026-11-13 evening: 5; 2026-11-14: 22); 83 are placed
  in `version/test_table.json`, all 103 placed. [measured, preflight C8, 2:40 PM PST]
- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 12:00 PM PST).

### The vision (his root paragraph, approved 2026-11-04, OWNER:1793794915205594887; eight lines in `version/vision.md`)

1. Dig canals, pits, moats and trenches; the liquids already on the map (water, tar, fuel, slime) flow in and settle at one level.
2. Every liquid comes from a real supply: the pond drops and refills slowly; a body at the map edge is endless.
3. Its main job is deadly earthworks: moats, covered pit traps, sluices and drawbridges you fill, drain and set alight when you choose.
4. Judged first on one raid: raiders swim a deep moat under a raised drawbridge and tire, a sluice drains it, the drained
   hole holds them as prisoners, and chemfuel pumped in from above is lit by a colonist tossing a flame from the rim.
   (0.1.0 is judged on it with ordered and placed pawns; the raid itself is 0.2.0's proof, OWNER:1795504867390195471.)
5. A pit reads as a hole with deep walls; ladders, climbing gear and jumps are the only ways in and out; raiders make a
   ladder to fetch comrades who fell in (built; its proof is 0.2.0).
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

1. **Three bar vocabularies.** The 55 checklist rows are the bars of 0.1.0. The sheet's `[floor:…]` lines (mod_settings,
   tick_cost, worldgen, multiplayer) and the 22 lines of `floor.json` are floor lines every mod meets, not among the 59.
   The older north-star bars in `northstar/` and the walk doc are a third list, not reconciled with the 55.
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
- CONDUCTOR INTERVENED (stage 6, 2026-11-23 11:30 PM PST, kind decision): deferral by his word: bars `moat_raid_sequence`, `raiders_fetch_their_fallen` and `inv_raider_fetch_fallen` left 0.1.0 for 0.2.0, with the raider clauses of `trench_gives_cover`, `inv_trench_cover` (now `raiders_shelter_only_where_they_can_climb_out`) and `island_bridges_trap_and_fail` (now `raiders_break_a_winch_and_escape`), scenes `sc_moat_raid`, `sc_trench_cover`, `sc_islands`, `sc_pit_trap_raid`, `sc_fetch_fallen` and showcase `pit_trap`; bar `moat_drains_and_burns`, the part of the moat bar that needs no raider, takes its place (57 to 55 bars). Objects kept in `version/next_version/raid_from_0.1.0.json`. lost: FlowWorks 0.1.0 passes with no real raid ever assaulting a moat, trench, island or pit; the walker scenes show that pawns path, cross and climb, not that raider AI chooses to. undo: move the listed bars and scenes back from next_version into the 0.1.0 locked bars and test table and re-pin. Source: owner, typed 2026-11-23 ~11:05 PM PST (OWNER:1795504867390195471).
- CONDUCTOR INTERVENED (stage 6, 2026-11-23 11:30 PM PST, kind re-pin): `version/bars.md` and `version/locked_bars.json` re-pinned for tree.json, sheet.md, scenes.json, record.json and plan.md after the raid move; tree hash now `c5d360b8c9`, sheet hash `6d0efc4bb0`. The Arbiter's coverage signature still names the lock's hashes, so `concept_tree.py gate` refuses on hash, and on north-star line `raiders_never_shelter_in_a_cage`, whose leaf is 0.2.0 now; nothing in Stage 6 reads that gate. Source: this journal's raid deferral line above.
- CONDUCTOR INTERVENED (stage 6, 2026-11-19 8:41 PM PST, kind decision): route b on RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT: no fifth blind cycle. Source: maturation.py advance by CONDUCTOR, cycle 3.
- CONDUCTOR INTERVENED (stage 6, 2026-11-21 6:32 PM PST, kind decision): In-game checks that count from a build older than the C# they exercise must run again BEFORE his walk, so that his walk is not the first reader of those bars. Sending FlowWorks back to the in-game stage for exactly those checks is decided: do it. Source: maturation.py advance by BENCH, cycle 3.

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

### 2026-11-16 1:17 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: steward road back after blind cycle 3: its 4 Problems were FIXED by the judge (96941bfa43) and the 5th (pit census pin) by the steward (d0d33973116a), so a judge who did not make the fixes must judge them; certificate rerun OK on 55 bars
- Checks passed: order, by, version, hold, fourth_cycle, judge_certificate.
- Steward confirms: read cycle_3/SUMMARY.md, faults.json, tests_edited.json and the 96941bfa43 diff (135 lines added, 0 removed: no weakened assertion). Sort: 4 FIXED Problems -> new judge owed; census Problem REAL MISS (stale pin after GSS b560ff91e8 removed ripple) re-pinned as a stronger ABSENT law, closed at d0d33973116a; certificate refusals RECORD GAP (stale ran_on_this_build), redone by certificate --run (7 reruns, OK on 55 bars); no CRITERION FLAW. Verdict: exit not met, open cycle 4 (visit 2's third).
- Blind cycle 3 of this visit (4 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 9:07 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 9:07 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-19 8:41 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by CONDUCTOR)

- Why: FlowWorks 0.1.0 to in-game visit 2 by the game-only road; the judgement is built into the pipeline by RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT (d9870b13c6)
- Checks passed: order, game_only, by, version, hold, steward_confirms, exit_met, judge_certificate.
- Steward confirms: cycle 4 read: 4 Problems FIXED red then green, 0 open; SHEET, THIRST, DRILL rows carried by game-only items
- Conductor decision: route b on RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT: no fifth blind cycle
- Game only: RIMMANDRAKE_PROVE_FLOWWORKS_SHEET_DROWNS_CROPS_LIVE, RIMMANDRAKE_PROVE_FLOWWORKS_BOTTLE_JOBS_MOVE_EXACT_LITRES, RIMMANDRAKE_PROVE_FLOWWORKS_DRILL_SURVEY_ROLLS_PER_BIOME_LIVE, RIMMANDRAKE_RETEST_FLOWWORKS_TOSS_FLAME_SINCE_JOBDEF_BUILT, RIMMANDRAKE_PASS_FLOWWORKS_COATING_WASH_SCENE_NEVER_PASSED
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 1:17 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 1:17 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-19 11:54 PM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: visit 2 exit not met: 8 FAIL, 5 UNMEASURED of 31, each filed as a named item caused by RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK; 3 offline (source_pays row re-pin, geyser check command, big-pit reset class + OL absent-goods reader), 10 game-only (Stage 6 work, no run at offline_build)
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_2/SUMMARY.md and rows.jsonl (18 PASS, 8 FAIL, 5 UNMEASURED of 31, build_match 31 of 31): verdict not met stands; sc_source_pays is a CRITERION FLAW (row against his ponds-pump-to-last-dL ruling), geyser a RECORD GAP (table runs the draft scene), OL a harness REAL MISS (reset called on the wrong class), PIT_LOOK a CRITERION FLAW (a look row the script can never decide), the rest REAL MISS or staging gaps needing live experiments; no test assertion weakened in the visit (only f24f71dba4 exit-code split)
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-19 8:41 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-19 8:41 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-20 9:40 PM PST, stage change: Offline build (Stage 3) to In-game acceptance (Stage 6) (by DISPATCH)

- Why: every open road-back item (RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE, RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_MOUND_RELIEF_OR_KERNEL, RIMMANDRAKE_READ_FLOWWORKS_PAWN_HEIGHT_CONTROL_SINK_NONE, RIMMANDRAKE_STAGE_FLOWWORKS_ICE_CUT_SHOVEL_KEEP_FROZEN, RIMMANDRAKE_STAGE_FLOWWORKS_PIT_TRAP_RAID_NONE_FELL, RIMMANDRAKE_STAGE_FLOWWORKS_TRENCH_RAID_NEVER_CAME_CLOSE, RIMMANDRAKE_TRACE_FLOWWORKS_FALLEN_RAIDER_WAITS_FOR_NO_LADDER, RIMMANDRAKE_TRACE_FLOWWORKS_HELD_WINCH_FELL_IN_THE_CONTROL, RIMMANDRAKE_TRACE_FLOWWORKS_ISLAND_RESTORE_OUT_OF_BANK_REACH, RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL) is a fault only the game can show, and the version's offline Problems are closed: the Maturation tick takes the game-only exit back to Stage 6 (RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS)
- Checks passed: order, game_only, by, version, hold.
- Game only: RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE, RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_MOUND_RELIEF_OR_KERNEL, RIMMANDRAKE_READ_FLOWWORKS_PAWN_HEIGHT_CONTROL_SINK_NONE, RIMMANDRAKE_STAGE_FLOWWORKS_ICE_CUT_SHOVEL_KEEP_FROZEN, RIMMANDRAKE_STAGE_FLOWWORKS_PIT_TRAP_RAID_NONE_FELL, RIMMANDRAKE_STAGE_FLOWWORKS_TRENCH_RAID_NEVER_CAME_CLOSE, RIMMANDRAKE_TRACE_FLOWWORKS_FALLEN_RAIDER_WAITS_FOR_NO_LADDER, RIMMANDRAKE_TRACE_FLOWWORKS_HELD_WINCH_FELL_IN_THE_CONTROL, RIMMANDRAKE_TRACE_FLOWWORKS_ISLAND_RESTORE_OUT_OF_BANK_REACH, RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-19 11:54 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-19 11:54 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 10:41 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: visit 3 not met. MOD lines not fixed in the sitting: sc_ice (RIMMANDRAKE_FIX_FLOWWORKS_FROZEN_POND_CUT_LEAVES_NO_CRUSHED_ICE, offline) and sc_source_pays (RIMMANDRAKE_FIX_FLOWWORKS_SINK_STOPS_ON_LAST_DECILITRE_FILM, offline). Undecided bar island_bridges_trap_and_fail: sc_islands scene presumed wrong, unrepaired (RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF, game-up). sc_garden one MOD-presumed FAIL then PASS (RIMMANDRAKE_TRACE_FLOWWORKS_FILTER_SLOWS_ONE_RUN_IN_TWO, game-up). OL_OWNER_LOOK_READS needless, kept (held_statements name it). Judge the judge: every reason a REAL MISS; the driver's repairs a07d2f8ea8 and 6fbf4d8c3b weaken no assertion.
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_3/SUMMARY.md, rows.jsonl and maturation.py next lines; 2 MOD lines filed offline, 1 undecided bar and 1 flake filed game-up; no mod fix in the sitting, so no fix reader owed
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-20 9:40 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-20 9:40 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 12:16 PM PST, stage change: Offline build (Stage 3) to In-game acceptance (Stage 6) (by DISPATCH)

- Why: every open road-back item (RIMMANDRAKE_MEASURE_FLOWWORKS_DIG_CALL_QUARTER_SECOND_ON_SITTING_MAP, RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF, RIMMANDRAKE_TRACE_FLOWWORKS_FILTER_SLOWS_ONE_RUN_IN_TWO, RIMMANDRAKE_WIRE_FLOWWORKS_OL_TO_READERS_LANDED_EIGHT_DAYS_AGO) is a fault only the game can show, and the version's offline Problems are closed: the Maturation tick takes the game-only exit back to Stage 6 (RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS)
- Checks passed: order, game_only, by, version, hold.
- Game only: RIMMANDRAKE_MEASURE_FLOWWORKS_DIG_CALL_QUARTER_SECOND_ON_SITTING_MAP, RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF, RIMMANDRAKE_TRACE_FLOWWORKS_FILTER_SLOWS_ONE_RUN_IN_TWO, RIMMANDRAKE_WIRE_FLOWWORKS_OL_TO_READERS_LANDED_EIGHT_DAYS_AGO
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-21 10:41 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 10:41 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 5:59 PM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: steward run RIMMANDRAKE_CONFIRM_FLOWWORKS_VISIT_FOUR_EXIT_MET: visit 4 exit met, read and confirmed
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match.
- Steward confirms: Read visit_4/SUMMARY.md, rows.jsonl (8 rows, one mod hash sha256:33f817434c71), strange.jsonl (7, all explained or filed) and maturation.py next (fix_readers_owed [], undecided_bars [], only refusal steward_confirms). Verdict: exit met. 30/31 PASS; sc_source_pays HARNESS repair 9da1303401 shown both ways on the row (mutant LIMITLESS_BODY_RUNS_DOWN FAIL 11790->11784.415, real PASS 11790->11790), diff adds a reading and weakens nothing; OL_OWNER_LOOK_READS UNMEASURED (1629 PASS, 1 BLOCKED: shadow-queue reader is mod C#), HARNESS, decides no bar, owned by RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER. No mod code changed in the visit, so no fix reader owed. Judge-the-judge: no not-met reason to sort; exit-reader change 1c65a6e664 keeps a held-statement check rather than removing it, a stricter reading, not a loosening. Walk save FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws present (13.6 MB, 5:29 PM).
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-21 12:16 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 12:16 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 6:14 PM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_1 written
- Checks passed: order, by, version, hold, walk_brief.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-21 5:59 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 5:59 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 6:32 PM PST, stage change: His live walk (Stage 8) to In-game acceptance (Stage 6) (by BENCH)

- Why: RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN: with each check's exercises declared (92c459ca74), build_match names 22 of 31 in-game checks to rerun (rows made before C# they exercise changed: the pit redraw e2288f4c84, the water look b80104f7a7, the sink film 2083f92acb and others). No mod fault: a declaration gap in the change relation. Back to Stage 6 for exactly those 22; 9 still count.
- Checks passed: order, by, version, hold.
- Conductor decision: In-game checks that count from a build older than the C# they exercise must run again BEFORE his walk, so that his walk is not the first reader of those bars. Sending FlowWorks back to the in-game stage for exactly those checks is decided: do it.
- Was, "Stage now": - **Stage now:** Stage 8, his live walk, since 2026-11-21 6:14 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 6:14 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 8:31 PM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: visit 5 exit not met on two game-only MOD lines: sc_hung_bridge (grate 5 vs solid 13; RIMMANDRAKE_GATE_INFERNO_DECK_CHANCE_SOLID_OUTBURNS_GRATE, supersedes GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO) and sc_hole_prison's earlier FAIL (RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO); both Verse-bound or cause-unknown, so the next visit, not offline_build
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_5 SUMMARY.md, rows.jsonl and maturation.py next: sc_hung_bridge REAL MISS (MOD, inferno in-cell chance 0.9 for solid and grated riders contradicts flowworks_bridges_design §4.1); sc_hole_prison REAL MISS (an earlier FAIL, cause unknown, a later PASS does not hide it); OL_OWNER_LOOK_READS not counted, HARNESS, carries his held look statements, owned by RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER; no tests_edited.json, no fix readers owed, no undecided bar
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-21 6:32 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 6:32 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-22 12:29 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: visit 6 road back: sc_hung_bridge has two MOD lines, both filed by the driver, neither fixed in the sitting. RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN is needs offline: the solid-deck chance saturates in one burn, and the steward took the design call (delegated, evidence-for-ask). RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE is needs game-up: the fill job stalls, cause unknown until a live experiment, so it gets no Stage 3 run. sc_walk is UNMEASURED: it was not run, it is owed on game a, it is not a failure, and it does not send the mod back. OL_OWNER_LOOK_READS is HARNESS, unrepaired, decides no bar, owner RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER. No fix readers owed.
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_6 SUMMARY.md and maturation.py next lines: sc_hung_bridge count=mod (2 MOD lines filed, verdict not met); all other rows pass or carry; fix_readers_owed []; verdict: back to offline_build for the offline line
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-21 8:31 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** RIMMANDRAKE_GATE_INFERNO_DECK_CHANCE_SOLID_OUTBURNS_GRATE and RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO (both game-only), then visit 6
- Record: `version/stage_record.json`.

### 2026-11-22 1:05 AM PST, stage change: Offline build (Stage 3) to In-game acceptance (Stage 6) (by DISPATCH)

- Why: every open road-back item (RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE) is a fault only the game can show, and the version's offline Problems are closed: the Maturation tick takes the game-only exit back to Stage 6 (RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS)
- Checks passed: order, game_only, by, version, hold.
- Game only: RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-22 12:29 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 12:29 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-22 3:29 AM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: steward: visit 7 exit met, read and confirmed (RIMMANDRAKE_CONFIRM_FLOWWORKS_VISIT_SEVEN_EXIT_MET)
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match.
- Steward confirms: read design/concepts/FlowWorks/version/in_game/visit_7/SUMMARY.md, rows.jsonl (13 rows, one mod hash), evidence/crush_planted.json, unarmed_planted.json, crush_parent_rule.txt and the diffs of 581e6f4baf and b1cc65afe2: 30 of 31 checks PASS on the walk build (sc_hung_bridge last 3 PASS on b1cc65afe2, sc_walk PASS on his full list); the 3 non-PASS sc_hung_bridge lines are HARNESS/SITE/SITE, repaired and shown both ways, no assertion weakened, selftests green at HEAD; OL_OWNER_LOOK_READS decides no bar, owner RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER; undecided bars none; fix readers owed none; strange 2 of 2 explained. Verdict: exit met.
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-22 1:05 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 1:05 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-22 3:42 AM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_2 written
- Checks passed: order, by, version, hold, walk_brief.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-22 3:29 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 3:29 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-22 3:48 PM PST, stage change: His live walk (Stage 8) to In-game acceptance (Stage 6) (by BENCH)

- Why: walk 2 not passed: every finding is a fault only the game showed, in Verse-bound draw, pathing or UI code (precedent: visit 5 road back, in_game to in_game); at Stage 6 the tick gives each open item one fixer run before visit 8, and visit 8 reruns only the checks the fixes touch
- Checks passed: order, by, version, hold.
- Owner said: OWNER:1795388411626379281
- Walk result: design/concepts/FlowWorks/version/walk_brief/walk_2_result.json
- Was, "Stage now": - **Stage now:** Stage 8, his live walk, since 2026-11-22 3:42 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 3:42 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 6:00 AM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: visit 8 road back: the only line that sends the mod back is sc_moat_raid (MOD, not fixed in the sitting: 2 capture FAILs and 1 bridge-down swimmer in 9 counted runs on 6b52871479); both causes are known only from a live read, so both items are game-only and the mod goes to the next visit, never to Stage 3. OL_OWNER_LOOK_READS is HARNESS, decides no bar, its blind sub-row already on polish.md: no item. undecided_bars [] and fix_readers_owed [] per maturation.py next.
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_8/SUMMARY.md and rows.jsonl (sc_moat_raid 10 rows: 3 MOD FAIL, 1 HARNESS void, 6 PASS with no mod_fix; OL not counted, HARNESS, no bar); verdict: exit not met stands, a REAL MISS on moat_raid_sequence, game-only
- Game only: RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS, RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMER_PAST_LOWERED_LEAF_AGAIN
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-22 3:48 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 3:48 PM PST).
- Record: `version/stage_record.json`.
- RE-PIN (stage 6, 2026-11-23 8:05 AM PST, kind re-pin): `version/bars.md` re-pinned for scenes.json (`90e671a405a0`): the start and action text of `sc_moat_raid` only (D4 = 4 m, four squares wide, water a metre below the rim, the sluice opens while the raiders swim). No bar, expect line or control changed; tree.json untouched. Why: `version/moat_geometry/DECISION.md` (RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX).

### 2026-11-23 11:28 PM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: visit 9 road back: no mod-wrong line sends it back. sc_moat_raid (the one MOD FAIL) is PAUSED (raid tests paused, 661658cd6b, after the visit) and makes no line; its fault stays on RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT (game-only, raid paused). What is left is a run, not a fault: sc_trench_cover_pawns, sc_moat_walkers and sc_islands_walker were written after the visit and never ran; sc_walk was not run (ArchBig's full list) and leaves inv_settings and walk_moat_season undecided; 15 passing checks and PIT_LOOK_1114_LIVE re-run because the scene files and the drawbridge and hose C# changed since f4971d58fa.
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_9/SUMMARY.md, rows.jsonl (64 rows), strange.jsonl, maturation.py next --json: fix_readers_owed [], shortfalls [], undecided_bars inv_settings and walk_moat_season (sc_walk only, COULD NOT LOOK), strange_open 0; verdict: exit not met stands, every line is a check only to run in the next visit
- Game only: RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 6:00 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 6:00 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 9:27 AM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: visit 10 road back: no mod-wrong line sends it back. sc_hung_bridge has one UNRESOLVED run (row 55, T064839) that the evidence on disk cannot class; its cause is readable only in a game, so RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS (filed by the driver, now needs game-up) is worked at Stage 6. sc_walk was not run (his full list, ArchBig) and alone leaves inv_settings and walk_moat_season undecided: it runs in the next visit. The other 27 checks count.
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_10/SUMMARY.md, rows.jsonl, strange.jsonl, both sc_hung_bridge evidence files, the diff and planted reading of the sc_moat_walkers repair 8eab92b6c2 (sound, not weakened), the visit's one edit of suspension_bridge_proof.py (verdict unchanged), maturation.py next --json: fix_readers_owed [], shortfalls [], paused_raids {}, undecided_bars inv_settings and walk_moat_season; verdict: exit not met stands, no item added, nothing classed without evidence
- Game only: RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 11:28 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 11:28 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 8:21 PM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: visit 11 steward: 29 of 30 lines count; sc_ways_out spoiled twice on ArchBig (ENVIRONMENT FAULT, Cherry Picker refuses Apparel_PackJump), a check only to re-run on the walk build, game-only; filed by the driver as RIMMANDRAKE_RUN_FLOWWORKS_WAYS_OUT_WHERE_CHERRY_PICKER_KEEPS_JUMP_PACK (run on ArchSmall); mod bug RIMMANDRAKE_FIX_FLOWWORKS_LINE_LOOK_CAST_THROWS_WHEN_TANK_TOUCHES_PIPE is game-up, filed; strange-thing reasons were a reader fault of form, fixed 6e1a770f1e
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_11 SUMMARY.md, rows.jsonl, strange.jsonl and maturation.py next: 0 FAIL, 0 undecided bars, 0 fix readers owed, sc_ways_out spoiled (game-only rerun), driver test edit 00a965aa56 a repair not a weakening; verdict: next visit
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-24 9:27 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** a live run of RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS on any free game (it classes visit 10's one UNRESOLVED `sc_hung_bridge` run), and `sc_walk` on ArchBig with his full list in visit 11 (it alone decides `inv_settings` and `walk_moat_season`).
- Record: `version/stage_record.json`.

### 2026-11-25 12:15 AM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by CONDUCTOR)

- Why: in-game visit 12 exit met: 30 of 30 in-game checks PASS on build e32272585f; hand act folds into RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match, unrun_run.
- Steward confirms: I read design/concepts/FlowWorks/version/in_game/visit_12/SUMMARY.md. The stage exit is met. Three owed cases of blind challenge cycle 4 (film never drowns crops, sheet settings units, drill reads its setting) are UNMEASURED in game; their offline cases stand and decide their bars, so no bar is left undecided. Material-word doubling goes to the Polish list.
- Owner said: per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS: in-game visit 12 exit met: 30 of 30 in-game checks PASS on build e32272585f; hand act folds into RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-24 8:21 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 8:21 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-25 1:01 AM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_3 written
- Checks passed: order, by, version, hold, walk_checks_stand, walk_brief, walk_items_closed.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-25 12:15 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 12:15 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-25 2:17 AM PST, stage change: His live walk (Stage 8) to In-game acceptance (Stage 6) (by DISPATCH)

- Why: in-game checks are owed before he walks (OL_OWNER_LOOK_READS, sc_canal_fire, sc_coating_wash, sc_covered_pit, sc_dig_and_read, sc_dig_finds, sc_fill_front, sc_fill_tiers, sc_geyser_tub, sc_hole_prison, sc_hose_look, sc_hung_bridge, sc_ice, sc_islands_walker, sc_moat_walkers, sc_one_network, sc_one_surface, sc_pawn_height, sc_pit_crowd, sc_pit_reads, sc_slime, sc_sluice, sc_toss_flame, sc_trench_cover_pawns, sc_ways_out): the Maturation tick opens the next visit for only these (RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED)
- Checks passed: order, by, version, hold.
- Was, "Stage now": - **Stage now:** Stage 8, his live walk, since 2026-11-25 1:01 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 1:01 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-25 12:00 PM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: steward: in-game visit 13 exit met; the driver's exit_met false was only for 033392ed2d's fresh reader, read sound at 6470bcda9d (reader fix 32df3b51c5)
- Checks passed: order, by, version, hold, road_back_items, steward_confirms, exit_met, build_match, unrun_run.
- Steward confirms: read visit_13/SUMMARY.md and rows: 22 of 22 run checks PASS (10 Steve2, 12 ArchBig), 13 carried PASS counted by build_match (35/35), strange_open 0, no FAIL or UNMEASURED line, no mod change in the sitting, no check repaired; the only not-met reason was the owed fresh reader of 033392ed2d, a RECORD GAP: rm-detached-bench-rimmandrake-read-flowworks-height-fix-on-1795631843 landed it sound at 6470bcda9d; this run independently saw selftest_flowworks_humanlike_height.py rc=1 (5 FAIL) at 033392ed2d^, PASS at the fix and HEAD, --mutate 4 RED + real GREEN; sc_pawn_height re-passed on 6b07457e86, which holds the fix. Verdict: exit met
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-25 2:17 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 2:17 AM PST).
- Record: `version/stage_record.json`.
