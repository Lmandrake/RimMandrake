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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
