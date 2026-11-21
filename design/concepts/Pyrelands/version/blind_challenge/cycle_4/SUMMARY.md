# Pyrelands 0.1.0 blind challenge, cycle 4

## Start time
2026-11-21T00:36:15Z (2026-11-20 4:36 PM PST), before any input was opened.

## Changed files to bars
`git diff --name-only 26c6f53375 origin/main` over the brief's paths, `/blind_challenge/` dropped: 56 files [measured].
Locked files, by id on the changed lines [measured, structural diff of the JSON at both shas]:
- `tree.json`: leaves ash_fertile_when_watered, burn_line_walks, fire_walks_with_wind (new), firehawk_hunt_rewards (coverage of
  inv_firehawk_hunt_rewards), fresh_burn_compounds_with_black_rain, furnacebeast_warms, grass_carpets_and_regreens,
  sand_shovel_yields_glass_sand, scorchfruit_born_of_fire; plus `coverage` and `root_hash`.
- `scenes.json`: sc_ash_watered, sc_burn_compounds, sc_burn_line_walks, sc_fire_walks_with_wind, sc_firehawk_rewards, sc_furnace_giant,
  sc_furnace_hide_bank, sc_grass_regreens, sc_sand_shovel, sc_scorchfruit; `coverage_rest`.
- `record.json`: inv_burn_line_fire_clock; `decisions`. `sheet.md` and `version/bars.md`: the same leaves' sentences (re-pins).
Code and data, by what each file feeds:
- `Source/FireEcologyHook.cs`, `Source/Kernel/RM_BurnKernel.cs`, `Source/MapComponent_BurnLine.cs`, `Source/PyrelandsFireFront.cs`,
  `pyre_burn_sim.py`, `pyre_save_burn_grid.py`, `wind_burn_live.py`, `testdata/pyre_walk_visit1.npz`, `Assemblies/FireEcologyHook.dll(.srchash)`:
  burn_line_walks, fire_walks_with_wind, inv_burn_line_fire_clock, grass_carpets_and_regreens, scorchfruit_born_of_fire, three_skies
  (black-rain dousing), inv_settings_gate (the new wind switch).
- `Source/PyrelandsTuning.cs`, `Source/RM_PyrelandsMod.cs`, `Languages/English/Keyed/Pyrelands.xml`, `preflight_pyrelands.py`: inv_settings_gate,
  inv_art_and_text (text).
- `About/About.xml`: inv_art_and_text, biome_text_says_engineered (the mod's own description).
- Tests and harness (`selftest_pyrelands_ash_probe.py`, `_defs_offline.py`, `_settings_sweep.py`, `_site.py`, `_burn_ecology.py`,
  `_wind_burn_rows.py`, `_round6_*`, `validation.py`, `Source/SelfTest/Fuzz/PyrelandsFuzz.cs`): the bars their rows decide
  (ash_fertility_probe, biome_text_says_engineered, inv_settings_gate, burn_line_walks, fire_walks_with_wind).
- Records (`coverage_*`, `exam*`, `journal.md`, `result.*`, `stage.json`, `version/evidence/*`, `version/in_game/unrun.jsonl`,
  `version/locked_bars.json`, `version/next_version/README.md`, `version/run_spend.jsonl`, `version/stage_record.json`,
  `version/test_table.*`, `pilot_throwaway/make_test_table.py`): no bar input; they record stages.
Lane-1 scope: the 6 offline bars, all; and of the stage-6 bars, those with a kernel: fire_walks_with_wind, burn_line_walks,
fresh_burn_compounds_with_black_rain, ash_fertile_when_watered, furnacebeast_warms, inv_firehawk_hunt_rewards.

## Lane 1
Written from the bars (tree.json, sheet.md, plan.md, record.json rows, bars.md), the shipped settings and the named kernels only.
Command: `python3 design/concepts/Pyrelands/version/blind_challenge/cycle_4/lane1/run_lane1.py` (C# `BlindLane1.cs` against
RM_FireEcoKernel, RM_BurnKernel, RM_FireHawkRewardsKernel, FurnaceWarmthMath; Python `BlindLane1.py` over Defs, Patches, Languages,
About and RM_PyrelandsMod.cs).
Result: 68 rows: **25 PASS, 0 FAIL, 5 INFO, 38 UNSETTLED** [measured]. Every UNSETTLED row is `not_kernel` on a stage-6 bar
(32 bars with no kernel, 6 with a kernel half and a game-side half); no offline bar has an UNSETTLED row.
Every offline bar has PASS rows: ash_fertility_probe 4 (+ 4 shared), biome_text_says_engineered 2, inv_firebreak_firefoam 1,
inv_lightning_breaker 1, inv_settings_gate 7, inv_art_and_text 1 (+ 3 INFO).
Two of my own rows were wrong on their first run and were fixed before this record (harness, not mod): the culture check counted
the comma inside the refusal sentence, and the description-overwrite pattern matched a patch that only adds an extension to the
BiomeDef (RM_AcousticPayload_Pyrelands.xml).
INFO worth reading: the slider sweep (compound_slider_sweep) finds the compound ordering fails only at player tunings (watered 2.0
hits the cap 2.0; watered at or below dry); the Pristine Firehawk Crestfeather is drawn with vanilla's ThrumboHorn texture
(art_texture_paths_resolve); 44 settings fields against the record row's "about 47".

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
