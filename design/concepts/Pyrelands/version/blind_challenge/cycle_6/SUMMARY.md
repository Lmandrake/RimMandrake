# Pyrelands 0.1.0 blind challenge, cycle 6

## Start time
2026-11-23 22:25 UTC (2:25 PM PST). Precondition: stage blind_challenge, cycles {visit 1, total 6}. Parent: 54a809a0f0.

## Changed files to bars
1181 changed files [measured]; 1120 are in_game records or stage evidence (no bar's input). The rest map so:

| changed | bars |
|---|---|
| Kernel/RM_BurnKernel.cs, MapComponent_BurnLine.cs, FireEcologyHook.cs, pyre_burn_sim.py, burn selftests | burn_line_walks, fire_walks_with_wind, inv_burn_line_fire_clock, ullai_graze_old_burns (history probe) |
| Kernel/RM_FoamPathKernel.cs, PyrelandsFoamPath.cs, FoamPathFuzz.cs | firefoam_sprayer_reaches_the_fruit, inv_firefoam_sprayer |
| PyrelandsAshField.cs (BurnTickAt) | ash_fertility_probe, fresh_burn_compounds_with_black_rain |
| PyrelandsFireSense.cs | walk_season_on_the_pyre (steps away from fire) |
| RM_PyrelandsMod.cs, scenes.json settings_map, settings sweep and screens selftests | inv_settings_gate |
| About/About.xml | inv_art_and_text, inv_firebreak_firefoam, inv_lightning_breaker (absence), biome_text_says_engineered |
| Defs: RM_FlamefangVenomBite.xml, RM_FlamefangVenom.xml | flamefang_bite_carries_venom |
| Defs: RM_PyrelandsFauna.xml (furnace-beast spares roofs) | furnacebeast_warms, inv_furnacebeast |
| Textures Ullai, FireHawk flying frames (east) | inv_art_and_text, inv_ullai_herd_giant |
| validation.py, play.py, northstar_site.py, venom_dose.py, other selftests | their scenes' bars (harness only) |
| test_table.json/.md, make_test_table.py, polish.md, journal.md, stage_record.json | records |

## Lane 1
Recorded blind at 22:32 UTC, before anything else was opened: 39 rows, see lane1/lane1_rows.jsonl. 32 PASS, 2 FAIL, 1 INFO, 4 UNSETTLED (not_kernel, game-side, Stage 6). [measured]
FAIL: `settings_master_tooltip_names_what_it_leaves_on` and `settings_wind_tooltip_matches_kernel` (both inv_settings_gate: a Mod Settings tooltip states a thing the mod no longer does).
One more FAIL on the first run was my own parser (it read default 40 as 4.0), repaired before recording.

## Lane 2 reruns
27 of 27 reruns match (every offline and record test; the 7 deciders of the 6 offline bars among them) [measured, lane2/reruns.jsonl]; timings are masked in the compare. After the fixes, the 13 tests rerun_relation names for the fix's parent ran again: 13 of 13 PASS [measured, lane2/reruns_after_fix.jsonl]. sc_walk is also named; it is live, Stage 6.
Lane 1 after the fixes: 34 PASS, 0 FAIL, 1 INFO, 4 UNSETTLED [measured, lane2/lane1_rows_after_fix.jsonl].

## Planted
40 faults planted; 28 caught on the first run, 29 after the two check repairs [measured, lane2/planted_results.jsonl, baseline first, tree_clean_after true]. Each fault ran only the suites it names; T_BURN_LANES and T_BURN_ECOLOGY were not run on survivors (the survivors are game-side C# those two do not read [measured by grep]).
Survivors: foam_any_faction, foam_path_not_read, firesense_cancels_aim, ash_burn_tick_off_by_one, firesense_fights_firefighter, carry_marks_nothing, carry_anchor_blind, carry_vanilla_spread_too, burnline_carried_at_unset, burnline_ago_wrong_lag, beast_spare_gone. Each is a game-side caller whose bar is decided live at Stage 6 (sc_fire_walks_with_wind, sc_burn_line_walks, sc_firefoam_sprayer, sc_fire_sense, sc_ullai, P_furnace_room); none names an offline bar. beast_spare_gone is already on polish.md.
Not planted: validation.py, play.py, northstar_site.py and the scene selftests that changed (harness; their checks are live).

## Faults
4 Problems, all FIXED (1 miss_of 5: the picture check), 1 Polish [measured, lane2/faults.json]:
- MOD: the wind tooltip and the fire-front letter said a fire lights one cell, never sideways, and a line is as wide as it was lit. The kernel heals gaps and opens flanks; a lone fire fans out.
- MOD: the "Mod enabled" tooltip did not name the sprayer carrier's foam, which it does not stop.
- HARNESS: T_SETTINGS_SWEEP_OFFLINE stayed green on a sprayer that foams with its switch off.
- HARNESS: T_DEFS_OFFLINE stayed green on a def naming a picture the mod does not ship.

## Fixes
- 956fb0c600: the two check repairs (own_switch_stops, pictures_shipped), each red on its plant and green on the real build; red_seen recorded for both deciders.
- 454764adbe: the mod text (RM_PyrelandsMod.cs, Keyed Pyrelands.xml, the DLL), with wind_tooltip, master_tooltip and fire_text_true red on the parent and green on the fix.
Owed on 454764adbe: one fresh reader (lane2/fix_reviews.jsonl), not this run.

## Steward's decisions enacted
None were written for this cycle.

## Tests edited
selftest_pyrelands_settings_sweep.py and selftest_pyrelands_defs_offline.py: checks and mutants added, nothing removed (tests_edited.json).

## Unsettled
The 4 not_kernel rows of lane 1 (populations_are_the_biomes_own, three_skies, walk_season_on_the_pyre, furnacebeast_warms): their Stage 6 scenes settle them.

## Exit
offline_bars: {ash_fertility_probe: green, biome_text_says_engineered: green, inv_firebreak_firefoam: green, inv_lightning_breaker: green, inv_settings_gate: green, inv_art_and_text: green}
problems_open: 0
exit_met: true

## Owed
One fresh reader of the mod fix 454764adbe (the steward's run).
