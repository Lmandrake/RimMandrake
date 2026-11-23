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

## Planted

## Faults

## Fixes

## Steward's decisions enacted

## Tests edited

## Unsettled

## Exit
offline_bars: {ash_fertility_probe: red, biome_text_says_engineered: red, inv_firebreak_firefoam: red, inv_lightning_breaker: red, inv_settings_gate: red, inv_art_and_text: red}
problems_open: 0
exit_met: false

## Owed
Everything (skeleton).
