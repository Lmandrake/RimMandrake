# Pyrelands 0.1.0 — blind challenge, cycle 3 (visit 2)

Judge: detached BENCH helper, item RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_THREE_TESTS_FIRST. New blind judge; no earlier cycle read.

## Start time
2026-11-17 14:31 UTC (06:31 PST), before any input was opened.

## Changed files to bars
Mechanical: `git diff --name-only 4d926284c8 origin/main -- <brief's paths> | grep -v /blind_challenge/` lists 30 files [measured]. Mapped by file role (no commit message after `4d926284c8` read):

| changed file | bars whose inputs it touches |
|---|---|
| `tree.json` (leaf `burn_line_walks`: experience, scenario, oracle), `sheet.md` (its line), `scenes.json` (`sc_burn_line_walks`, `settings_map` + `windCarriesFireEnabled`) | `burn_line_walks`; `inv_settings_gate` (a new setting in the map) |
| `Source/Kernel/RM_BurnKernel.cs` (wind carry: `WindProbes`, `WindCarryDue`, `VanillaSpreadRuns`, `AcrossWind`, `Downwind`, `CarriedStillBurning`) | `burn_line_walks`, `inv_burn_line_fire_clock`; `inv_settings_gate` (the wind switch) |
| `Source/MapComponent_BurnLine.cs`, `Source/PyrelandsFireFront.cs`, `Source/FireEcologyHook.cs` (callers of the wind carry) | `burn_line_walks`, `inv_burn_line_fire_clock`, `ullai_graze_old_burns` (burn centre), `inv_settings_gate` |
| `Source/PyrelandsTuning.cs` (`FireFrontWidthCells` 9 -> 24) | `burn_line_walks`, `inv_burn_line_fire_clock` |
| `Source/RM_PyrelandsMod.cs`, `Languages/English/Keyed/Pyrelands.xml` (the new `windCarriesFireEnabled` switch and its text) | `inv_settings_gate`, `inv_art_and_text` |
| `Assemblies/FireEcologyHook.dll` + `.srchash` | every bar its source feeds (rebuild of the above) |
| `Source/SelfTest/Fuzz/PyrelandsFuzz.cs`, `selftest_pyrelands_settings_sweep.py`, `preflight_pyrelands.py` | `inv_settings_gate` (deciders / preflight) |
| `selftest_pyrelands_defs_offline.py` | `biome_text_says_engineered` (its decider) |
| `pyre_burn_sim.py`, `selftest_pyrelands_burn_ecology.py`, `selftest_pyrelands_wind_burn_rows.py`, `wind_burn_live.py`, `pyre_save_burn_grid.py`, `testdata/pyre_walk_visit1.npz` | `burn_line_walks`, `grass_carpets_and_regreens` (tests and models of the burn) |
| `version/bars.md`, `version/stage_record.json`, `version/run_spend.jsonl`, `version/next_version/README.md`, `version/pilot_throwaway/make_test_table.py`, `version/test_table.*`, `journal.md` | records; no bar input (test_table and journal read only in lane 2) |

Lane-1 scope therefore: the six offline bars (all once), plus `burn_line_walks`, `inv_burn_line_fire_clock` and the new switch in `inv_settings_gate` (changed). `record.json` was read for the four offline `inv_*` rows' words (their bar text lives there).

## Lane 1
Run: `python3 lane1/run_lane1.py` (C# `lane1/BlindLane1.cs` against the Verse-free kernels, staged under `/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_lane1/`, plus `lane1/blind_lane1_files.py` over the mod's files). Recorded blind, before any lane-2 input was opened.

- **63 rows: 29 PASS, 1 FAIL, 3 INFO, 30 UNSETTLED** [measured]. The 30 UNSETTLED are `not_kernel` rows, one per game-side bar (stage 6 or later by their words; checked against `proves_at` in lane 2).
- Offline bars: `ash_fertility_probe` 4 PASS + 1 INFO (parts per cell, the base-for-every-cell false pass caught, refusal with reason, 20 000 random cases where the parts add up); `biome_text_says_engineered` PASS; `inv_firebreak_firefoam` PASS (absent); `inv_lightning_breaker` PASS (absent); `inv_settings_gate` 6 PASS (gate truth table, 27 switch-off paths, weight conservation, 44 settings Scribed with their shipped default, 17 defaults inside slider ranges, every setting drawn and in its section's reset); `inv_art_and_text` 2 PASS + **1 FAIL**.
- **FAIL `text_fixed_about_does_not_promise_worldgen_that_ships_off`** (`inv_art_and_text`): `About/About.xml` says the mod "places itself on newly generated worlds with no other mod required", but `biomeGenerationEnabled` ships `false`, labelled unsupported (sheet floor:worldgen, his card 2026-11-13). Would pass: the About text says new-world placement is an unsupported switch, off by default.
- Changed bar `burn_line_walks` (kernel half): carry probes downwind only at any bearing (20 000 cases), a 24-cell line abreast of the wind, carried once at 1 200 ticks; a whole-front model on 300x300 grass: no fire makes two, every burnt cell a lit fire, the front advances about 57-59 cells a day and 0 of 40 fronts went out in 4 days (full and 70% grass). INFO: vector-mean heading leans up to 5.3 degrees to the diagonals.
- INFO rows: the probe's `bonusDaysLeft` keeps counting with the bonus switched off; the watered slider (0.4..2) can sit below dry (0..1). Both Polish at most.
- Oracle correction before recording: the compound sweep's first form asked "wet fresh >= dry fresh" at every slider pair, which a player who sets watered below dry breaks by choice; it was replaced (before the first commit) by the bar's real claim, the bonus survives the rain whole, and the gap kept as an INFO row.

## Lane 2 reruns
`lane2/rerun_offline.py` reran every `kind` offline or record test of `test_table.json` with its recorded command: **22 of 22 match** their recorded verdict (`lane2/reruns.jsonl`) [measured], the six offline bars' 7 deciders among them, all PASS. After the fixes (three deciders and About.xml changed), the 8 tests that read them were rerun: **8 of 8 PASS** (`lane2/reruns_after_fix.jsonl`) [measured].

## Planted
46 faults (`lane2/planted_faults.json`, built by `lane2/make_planted_faults.py`), run by `lane2/plant_faults.py` with `WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_mut/`; suites per fault: the offline deciders and supports of its bars, every offline test whose `reads` covers the file, and lane 1. Caught = a new failing row. **31 of 46 caught** [measured]; `planted_results.jsonl` ends `tree_clean_after: true`. Three runs were cut by the 535 s command timeout; the signal restore held and the tree was clean each time (checked with `git diff --quiet`).

Coverage: 8 in the probe's kernel and caller, 6 in the biome text, the heat-immunity patch and RM_TerrainDig, 4 absence faults (firebreak, breaker, fulgurite), 10 in the settings gate, the screen and preflight, 3 in art and text, 15 in the changed burn kernel, its callers and the burn model. Records that are not code (journal, run_spend, stage_record, npz, the DLL) carry no planted fault.

Survivors:
- **Offline bars, decider gaps (Problems, fixed):** `probecell_bonus_dropped` (ash_fertility_probe); `gate_shellon_always`, `heat_immunity_gate_ignored`, `wind_ignores_gate`, `wind_checkbox_wrong_field` (inv_settings_gate); `about_promises_worldgen_more` (inv_art_and_text, already a lane-1 FAIL, so no new row). `desc_millennia_dropped` was caught by lane 1 only, not by its decider T_DEFS_OFFLINE: also fixed.
- **Stage-6 bars (Polish, live decides):** 7 burn-line faults (`carry_lights_every_probe`, `spread_prefix_always_vanilla`, `carry_forgets_carried`, `markcarried_noop`, `front_line_along_wind_caller`, `scar_wind_not_set`, `downwind_cone_wide`); `dig_leaves_no_gravel` (sand_shovel_yields_glass_sand, stage 6).
- **Equivalent:** `dig_default_count_one`: the def sets `<count>5</count>`, so the code default is never read.

## Faults
`lane2/faults.json`, each filed as a rimflow item [measured: 7 file events in BENCH.jsonl]:

| id | class | bar | status | miss_of |
|---|---|---|---|---|
| `RIMMANDRAKE_FIX_PYRE_ABOUT_PROMISES_WORLDGEN_SHIPPED_OFF` | Problem | inv_art_and_text | FIXED 4a7c450d6b | 2 |
| `RIMMANDRAKE_GUARD_PYRE_GATE_SHELL_TOGGLE_AND_WIND_ENTRY` | Problem | inv_settings_gate | FIXED 4a7c450d6b | 2 |
| `RIMMANDRAKE_GUARD_PYRE_WIND_CHECKBOX_BOUND_TO_BURN_LINE` | Problem | inv_settings_gate | FIXED 4a7c450d6b | - |
| `RIMMANDRAKE_GUARD_PYRE_PROBE_BONUS_PART_HANDED_ZERO` | Problem | ash_fertility_probe | FIXED 4a7c450d6b | 2 |
| `RIMMANDRAKE_GUARD_PYRE_DESCRIPTION_MILLENNIA_HALF_UNCHECKED` | Problem | biome_text_says_engineered | FIXED 4a7c450d6b | 2 |
| `RIMMANDRAKE_NOTE_PYRE_WIND_CALLERS_PROVE_ONLY_LIVE` | Polish | burn_line_walks | PENDING | - |
| `RIMMANDRAKE_CORRECT_PYRE_TEST_TABLE_SAYS_BODY_SIZE_SIX` | Polish | furnacebeast_warms (a record) | FIXED 4a7c450d6b | - |

5 Problems (4 of them `miss_of: 2`), 2 Polish. The lane-1 INFO rows (the probe's `bonusDaysLeft` with the bonus off; the watered slider below dry) are noted here and not filed: Polish at most.

## Fixes
One commit, `4a7c450d6b` (parent `912c1ee157`). Red first: every command was run on `912c1ee157` before any edit, then on `4a7c450d6b` (`lane2/fixes.jsonl`, 5 rows, 8 red runs, 8 green runs) [measured]. Each catching run is `lane2/catch.py <fault> <TEST>` (rc 0 when the test goes red on the planted fault); the About fault also carries `lane1/blind_lane1_files.py` (rc 1 then 0).
- `src/RimMandrake/Pyrelands/About/About.xml`: "...ship here, with no other mod required. Placing the Pyrelands on newly generated worlds is an unsupported switch in Mod Settings, off by default."
- deciders extended (below). The fix to T_DEFS_OFFLINE's catching runs ends with its copy check ("the unchanged copy is not green") because the planted fault sits in the live tree it copies; the verdict is the new fact's (at the parent the same run printed PASS).
- `code_review_status.py check`: the three test files read DIRTY (never marked clean, before this cycle too); not marked clean here (no full-file review done).

## Steward's decisions enacted
The 2026-11-16 9:57 PM PST release (the Fable rescue landed 49e11870b4; the 8:36 PM hold on stage 4+5 lifted) is the decision this cycle ran under; recorded as a note with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (OWNER.jsonl, published in `4a7c450d6b`). The 8:36 PM hold itself needed no act (it had been released).

## Tests edited
`tests_edited.json` (before/after sha256). All additions; nothing removed, skipped or loosened:
- `src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py` (T_SETTINGS_SWEEP_OFFLINE): ShellOn wiring; Patch_FurnaceBeastHeatImmunity.Prefix and the WindCarries predicate in `entry_gated`; new fact `checkboxes`; 5 mutants (21 of 21 red).
- `src/RimMandrake/Pyrelands/selftest_pyrelands_ash_probe.py` (T_ASH_PROBE_OFFLINE): ProbeCell must pass the cell's own parts.
- `src/RimMandrake/Pyrelands/selftest_pyrelands_defs_offline.py` (T_DEFS_OFFLINE): facts `biome_text_burned_for_millennia`, `about_no_worldgen_promise_while_off`; 2 mutants (20 of 20 red); its copy now includes About.xml.
- Not a test: `test_table.json` and `make_test_table.py` prose "body size 6" -> 9.
`run_selftests.py --only` on the three plus T_CUT_STAYS_CUT and T_SELF_CONTAINED_OFFLINE: GREEN 5/5 [measured].

## Unsettled
- 30 `not_kernel` rows, one per game-side bar; every one proves at stage 6 (`proves_at` 6, checked in lane 2), so none blocks this exit.
- The wind carry's game-side callers have no offline guard (Polish item above); the live scene `sc_burn_line_walks` decides. Whether a carried grass fire survives its 1 200 ticks before its plant burns out (else the line thins) is a live question: the lane-1 model assumes every lit fire lives to carry [guess ~70% that it holds live, since the builder's live walk measured 43 cells a day].
- `runs_today` in test_table.json is stale for the three edited deciders (the judge certificate reads it): the next recorded run refreshes it.

## Exit
offline_bars: {ash_fertility_probe: green, biome_text_says_engineered: green, inv_firebreak_firefoam: green, inv_lightning_breaker: green, inv_settings_gate: green, inv_art_and_text: green}
problems_open: 0
exit_met: false

Every offline bar's deciders PASS on the rerun after the fix and no Problem is open, but this cycle FIXED 5 Problems, so by the brief its own fixes cannot pass its exit: a new blind judge is owed.

## Owed
- A new blind judge (cycle 4 would be a fourth cycle in total; the Conductor decides after three, spec "After three cycles").
- `maturation.py next Pyrelands` reports the Conductor's hold of 2026-11-17 6:52 AM PST (journal: no advance past Stages 4 and 5 and no blind cycle 4 until the owner's card of 6:33 AM PST lands in tree.json), written after this cycle began; this cycle judged the tree as it stood at 14:31 UTC. It also reports a judge certificate refused on stale `runs_today`. Both are the steward's; nothing changed here.
- Polish item `RIMMANDRAKE_NOTE_PYRE_WIND_CALLERS_PROVE_ONLY_LIVE` (optional offline guard for the wind-carry callers).
