# Pyrelands 0.1.0: test-and-stage table

Generated 2026-11-16T21:27:29-08:00 from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Same columns as Explosive Knockback's table.

## Counts (measured)

- bars: 43
- with at least one test runnable today (a built offline test that ran green, or an in-game scene whose entry exists in validation.py): 43
- with every deciding test runnable today: 43
- with an offline deciding test, all green today: 16
- decided offline only (no game needed): 6, of which every decider is built: 6
- scenes.json scenes: 29, entry exists 28, absent 1
- offline tests: 21 built (ran today: 21 green for this mod), 0 specified for Stage 3

## Bars

| bar | from | proves at | decides | supports | runnable today |
|---|---|---|---|---|---|
| `burn_line_walks` | tree | 6 | sc_burn_line_walks | T_FUZZ, T_BURN_ECOLOGY, T_BURN_LANES, LOOK_STAGE8 | all |
| `ash_ground_and_blowing_ash` | tree | 6 | sc_fire_dusts_ash | T_LINT, T_FUZZ, T_TRACKS, P_ambient_ash_drift | all |
| `ash_fertile_when_watered` | tree | 6 | sc_ash_watered | T_FUZZ | all |
| `fresh_burn_compounds_with_black_rain` | tree | 6 | sc_burn_compounds | T_FUZZ, T_ASH_PROBE_OFFLINE | all |
| `grass_carpets_and_regreens` | tree | 6 | sc_grass_regreens | T_LINT, T_BURN_ECOLOGY, P_grass_cover, LOOK_STAGE8 | all |
| `scorchfruit_born_of_fire` | tree | 6 | sc_scorchfruit | T_SETTINGS_SWEEP_OFFLINE, T_FRUIT_CLEAR, T_BURN_COST, P_scorchfruit_produces, P_scorchfruit_spoils, LOOK_STAGE8 | all |
| `populations_are_the_biomes_own` | tree | 6 | sc_populations, T_ALLOWLIST | T_LINT, T_SITE, P_animal_census, P_mapgen_log | all |
| `ruins_stand_blackened` | tree | 6 | sc_ruins | - | all |
| `firehawk_lights_ahead` | tree | 6 | sc_firehawk | T_FUZZ | all |
| `furnacebeast_warms` | tree | 6 | sc_furnace, T_FURNACE_WARMTH | T_FUZZ, T_DEFS_OFFLINE, P_furnace_room | all |
| `ashwallow_dives_unharmed` | tree | 6 | sc_ashwallow, sc_heat_dome | T_BURN_COST | all |
| `ullai_graze_old_burns` | tree | 6 | sc_ullai | T_LINT | all |
| `three_skies` | tree | 6 | sc_three_skies | T_BURN_ECOLOGY, P_ashfall_weather_accumulation, P_ashfall_drifts, P_blackrain | all |
| `no_ordinary_rain` | tree | 6 | T_DEFS_OFFLINE, sc_no_rain | - | all |
| `ash_fertility_probe` | tree | 4-5 | T_ASH_PROBE_OFFLINE | T_FUZZ, sc_burn_compounds | all |
| `walk_season_on_the_pyre` | tree | 6 | sc_reload_keeps_the_burn, sc_fire_sense | T_WALK_SMALL, T_FUZZ, sc_burn_line_walks, sc_scorchfruit, sc_burn_compounds, sc_ash_watered, sc_furnace, LOOK_STAGE8 | all |
| `firefoam_sprayer_reaches_the_fruit` | tree | 6 | sc_firefoam_sprayer | T_FIREFOAM_SCENE, P_firefoam_aim | all |
| `sand_shovel_yields_glass_sand` | tree | 6 | sc_sand_shovel | T_DEFS_OFFLINE | all |
| `fire_rite_hook_silent_alone` | tree | 6 | sc_rite_hook_alone | - | all |
| `biome_text_says_engineered` | tree | 4-5 | T_DEFS_OFFLINE | - | all |
| `flamefang_bite_carries_venom` | tree | 6 | sc_flamefang_venom | T_DEFS_OFFLINE | all |
| `inv_biome_self_contained` | record | 6 | T_LINT, sc_populations | T_SITE, P_startup_and_def_wiring, P_mapgen_log, T_SELF_CONTAINED_OFFLINE | all |
| `inv_plant_roster` | record | 6 | sc_populations, T_ALLOWLIST, T_LINT | P_grass_cover | all |
| `inv_embergrass_regrow` | record | 6 | sc_grass_regreens | T_LINT | all |
| `inv_animal_roster` | record | 6 | sc_populations | P_animal_census, sc_flamefang_venom, T_DEFS_OFFLINE | all |
| `inv_ash_field` | record | 6 | sc_ash_watered, sc_burn_compounds | T_FUZZ, T_LINT, T_TRACKS, sc_fire_dusts_ash, P_ambient_ash_drift | all |
| `inv_burn_line_fire_clock` | record | 6 | sc_burn_line_walks, T_FUZZ | T_BURN_ECOLOGY, sc_fire_dusts_ash, T_BURN_COST | all |
| `inv_scorchfruit` | record | 6 | sc_scorchfruit | T_FRUIT_CLEAR, P_scorchfruit_produces, P_scorchfruit_spoils | all |
| `inv_ruins_scorched` | record | 6 | sc_ruins | - | all |
| `inv_firehawk_ember` | record | 6 | sc_firehawk | T_FUZZ | all |
| `inv_furnacebeast` | record | 6 | sc_furnace, T_FURNACE_WARMTH | T_FUZZ, T_DEFS_OFFLINE, P_furnace_room | all |
| `inv_burrowers_heat_dome` | record | 6 | sc_ashwallow, sc_heat_dome | T_BURN_COST | all |
| `inv_ullai_herd_giant` | record | 6 | sc_ullai | T_CUT_STAYS_CUT, T_ULLAI_HERD_MIGRATES | all |
| `inv_weather` | record | 6 | sc_three_skies, sc_no_rain, T_DEFS_OFFLINE | P_ashfall_weather_accumulation, P_ashfall_drifts, P_blackrain | all |
| `inv_firebreak_firefoam` | record | 4-5 | T_CUT_STAYS_CUT | - | all |
| `inv_firefoam_sprayer` | record | 6 | sc_firefoam_sprayer | T_FIREFOAM_SCENE, P_firefoam_aim | all |
| `inv_sand_shovel` | record | 6 | sc_sand_shovel | T_DEFS_OFFLINE | all |
| `inv_lightning_breaker` | record | 4-5 | T_CUT_STAYS_CUT | - | all |
| `inv_fire_rite_hook` | record | 6 | sc_rite_hook_alone | - | all |
| `inv_settings_gate` | record | 4-5 | T_SETTINGS_SWEEP_OFFLINE, T_SETTINGS_SCREENS, T_SITE | sc_fire_sense, P_gate, T_SELF_CONTAINED_OFFLINE | all |
| `inv_art_and_text` | record | 4-5 | RECORD_ART_SHEET, T_DEFS_OFFLINE | sc_three_skies, T_BARBSLINGER, T_TRACKS, T_REVIEW_MAP | all |
| `inv_firehawk_hunt_rewards` | record | 6 | T_FH_LETTER, T_FH_CRESTFEATHER, firehawk_first_sighting_letter, firehawk_crestfeather_yield | T_FUZZ, LOOK_STAGE8 | all |
| `ullai_cross_the_map_as_vanilla_herds` | tree | 6 | T_ULLAI_HERD_MIGRATES, sc_foreign_arrivals, T_CUT_STAYS_CUT | - | all |

## Leaves that are coverage of a bar (not bars)

- `firehawk_hunt_rewards` covers bar `inv_firehawk_hunt_rewards`

## Tests

| test | kind | stage | file | runs today |
|---|---|---|---|---|
| `T_FUZZ` | offline | 4-5 | `src/RimMandrake/Utils/selftest_pyrelands_fuzz.py` | PASS 14.5s |
| `T_BURN_ECOLOGY` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_burn_ecology.py` | PASS 100.1s |
| `T_BURN_LANES` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_burn_front_lanes.py` | PASS 137.0s |
| `T_LINT` | offline | 4-5 | `src/RimMandrake/Utils/selftest_pyrelands_lint.py` | PASS 76.2s |
| `T_ALLOWLIST` | offline | 4-5 | `src/RimMandrake/Utils/selftest_pyrelands_allowlist_postfix.py` | PASS 1.7s |
| `T_BURN_COST` | offline | 4-5 | `src/RimMandrake/Utils/selftest_pyrelands_burn_cost.py` | PASS 0.1s |
| `T_TRACKS` | offline | 4-5 | `src/RimMandrake/Utils/selftest_pyrelands_track_contrast.py` | PASS 0.3s |
| `T_FURNACE_WARMTH` | offline | 4-5 | `src/RimMandrake/Utils/selftest_furnace_warmth.py` | PASS 2.2s |
| `T_SITE` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_site.py` | PASS 4.7s |
| `T_FRUIT_CLEAR` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_fruit_clear.py` | PASS 0.0s |
| `T_FIREFOAM_SCENE` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_firefoam_scene.py` | PASS 0.3s |
| `T_SETTINGS_SCREENS` | offline | 4-5 | `src/RimMandrake/Utils/selftest_settings_screens.py --mod Pyrelands` | PASS 2.4s |
| `T_BARBSLINGER` | offline | 4-5 | `src/RimMandrake/Utils/selftest_barbslinger_two_tails.py` | PASS 0.0s |
| `T_REVIEW_MAP` | offline | 4-5 | `src/RimMandrake/Pyrelands/review/selftest_pyre_review_map.py` | PASS 0.2s |
| `T_FH_LETTER` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_firehawk_letter.py` | PASS 0.0s |
| `T_FH_CRESTFEATHER` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_firehawk_crestfeather.py` | PASS 0.0s |
| `T_SETTINGS_SWEEP_OFFLINE` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py` | PASS 2.6s |
| `T_DEFS_OFFLINE` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_defs_offline.py` | PASS 55.1s |
| `T_CUT_STAYS_CUT` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_cut_stays_cut.py` | PASS 0.8s |
| `T_ULLAI_HERD_MIGRATES` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_ullai_herd_migration.py` | PASS 7.5s |
| `T_ASH_PROBE_OFFLINE` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_ash_probe.py` | PASS 1.9s |
| `sc_burn_line_walks` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: burn_line | live: this run is offline only; entry exists in validation.py |
| `sc_ash_watered` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: ash_fertility_watered | live: this run is offline only; entry exists in validation.py |
| `sc_burn_compounds` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: fresh_burn_bonus | live: this run is offline only; entry exists in validation.py |
| `sc_grass_regreens` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: embergrass_regrow | live: this run is offline only; entry exists in validation.py |
| `sc_scorchfruit` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: scorchfruit_fire_born | live: this run is offline only; entry exists in validation.py |
| `sc_populations` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: plant_census | live: this run is offline only; entry exists in validation.py |
| `sc_ruins` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: ruins | live: this run is offline only; entry exists in validation.py |
| `sc_firehawk` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: firehawk | live: this run is offline only; entry exists in validation.py |
| `sc_furnace` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: furnace_warmth | live: this run is offline only; entry exists in validation.py |
| `sc_ashwallow` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: burrowers | live: this run is offline only; entry exists in validation.py |
| `sc_ullai` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: herd_follows_drive | live: this run is offline only; entry exists in validation.py |
| `sc_three_skies` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: cinderfall | live: this run is offline only; entry exists in validation.py |
| `sc_no_rain` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: no_ordinary_rain | live: this run is offline only; entry exists in validation.py |
| `sc_reload_keeps_the_burn` | live_minimal | 6 | `src/RimMandrake/Pyrelands/walk_small_live.py` :: reload_keeps_the_burn | UNRUN |
| `sc_fire_sense` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: fire_sense | UNRUN on this build |
| `sc_firefoam_sprayer` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: firefoam_sprayer | live: this run is offline only; entry exists in validation.py |
| `sc_sand_shovel` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: sand_shovel | live: this run is offline only; entry exists in validation.py |
| `sc_rite_hook_alone` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: rite_hook_alone | live: this run is offline only; entry exists in validation.py |
| `sc_heat_dome` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: heat_dome | live: this run is offline only; entry exists in validation.py |
| `sc_fire_dusts_ash` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: fire_tick_effects | live: this run is offline only; entry exists in validation.py |
| `sc_flamefang_venom` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: flamefang_venom | live: this run is offline only; entry exists in validation.py |
| `sc_foreign_arrivals` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: foreign_arrivals | live: this run is offline only; entry exists in validation.py |
| `sc_firehawk_rewards` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: firehawk_first_sighting_letter | live: this run is offline only; entry ABSENT in validation.py |
| `P_startup_and_def_wiring` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: startup_and_def_wiring | live: this run is offline only; entry exists in validation.py |
| `P_mapgen_log` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: mapgen_log | live: this run is offline only; entry exists in validation.py |
| `P_grass_cover` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: grass_cover | live: this run is offline only; entry exists in validation.py |
| `P_animal_census` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: animal_census | live: this run is offline only; entry exists in validation.py |
| `P_ambient_ash_drift` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: ambient_ash_drift | live: this run is offline only; entry exists in validation.py |
| `P_scorchfruit_produces` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: scorchfruit_produces | live: this run is offline only; entry exists in validation.py |
| `P_scorchfruit_spoils` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: scorchfruit_spoils | live: this run is offline only; entry exists in validation.py |
| `P_furnace_room` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: furnace_room | live: this run is offline only; entry exists in validation.py |
| `P_ashfall_weather_accumulation` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: ashfall_weather_accumulation | live: this run is offline only; entry exists in validation.py |
| `P_ashfall_drifts` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: ashfall_drifts | live: this run is offline only; entry exists in validation.py |
| `P_blackrain` | live_minimal | 6 | `src/RimMandrake/Pyrelands/validation.py` :: blackrain | live: this run is offline only; entry exists in validation.py |
| `P_firefoam_aim` | live_minimal | 6 | `src/RimMandrake/Pyrelands/firefoam_aim_live_proof.py` | live: this run is offline only; entry exists in firefoam_aim_live_proof.py |
| `P_gate` | live_minimal | 6 | `src/RimMandrake/Pyrelands/gate_live_proof.py` | live: this run is offline only; entry exists in gate_live_proof.py |
| `firehawk_first_sighting_letter` | live_minimal | 6 | `src/RimMandrake/Pyrelands/firehawk_rewards_live.py` :: firehawk_first_sighting_letter | live: this run is offline only; entry exists in firehawk_rewards_live.py |
| `firehawk_crestfeather_yield` | live_minimal | 6 | `src/RimMandrake/Pyrelands/firehawk_rewards_live.py` :: firehawk_crestfeather_yield | live: this run is offline only; entry exists in firehawk_rewards_live.py |
| `RECORD_ART_SHEET` | record | 2 | `infrastructure/state/ledger/events/` | PASS |
| `LOOK_STAGE8` | look | 8 | `(his walk)` | Stage 8 |
| `T_SELF_CONTAINED_OFFLINE` | offline | 4-5 | `src/RimMandrake/Pyrelands/selftest_pyrelands_self_contained.py` | PASS 0.7s |
| `T_ROUND6_GAPS` | offline | 3 | `src/RimMandrake/Pyrelands/selftest_pyrelands_round6_gaps.py` | PASS 2.6s |

## Corrections applied (judge gaps sorted CORRECTION)

| gap | where | status |
|---|---|---|
| g1 | scenes.json sc_ash_ground, sc_ruins, sc_three_skies, sc_fire_dusts_ash; tree.json oracle/scenario of ash_ground_and_blowing_ash, ruins_stand_blackened, three_skies; record.json inv_ash_field impl_evidence | applied in the row 2 commit |
| g3 | scenes.json sc_ash_watered (expect, control), sc_burn_compounds; tree.json fresh_burn_compounds_with_black_rain oracle | applied in the row 2 commit |
| g5 | sheet.md delegated (world switch); record.json d_worldgen_outside_promise | applied in the row 2 commit (text); the judge's 'add one offline leaf' not done: a new leaf would add a bar, so T_SITE is named instead |
| g11 | scenes.json coverage_rest inv_art_and_text why | applied in the row 2 commit |
| g12 | sheet.md open (line deleted); record.json inv_ullai_herd_giant what | applied in the row 2 commit (text); absence check specified, not built |
| g13 | sheet.md delegated (showcase 3) | applied in the row 2 commit |
| g14 | exam.json | NOT applied: rerunning the Cold Reader exam is a model step, not test text; question for the Conductor |

## The settings move

inv_settings_gate was proven only by the two-week walk (coverage_rest). Its defaults, readers and gate checks are now decided offline by T_SETTINGS_SWEEP_OFFLINE (specified), T_SETTINGS_SCREENS and T_SITE (built); sc_fire_sense keeps the gate-off read live, as support (sc_walk is gone: RIMMANDRAKE_SPLIT_PYRELANDS_SEASON_WALK_TO_MINIMUM_TESTS). No bar text is edited.

## Held look statements

0 held look statements name Pyrelands (grep of design/RimMandrake/validation_holding/*.md for pyre|ember|scorch|ash, 2026-11-14; the same grep for knockback finds 7 lines).
