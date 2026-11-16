# LeaningScrub 0.1.0 test table (read view of test_table.json)

Made by `pilot_throwaway/make_test_table.py`, 2026-11-16T17:10:34Z. A bar passes when every deciding test passes. Every bar-to-test pair is read from the locked files (coverage_verdict.json checklist parts; scenes.json requirement, exercises, coverage_rest, showcases); none is hand-written.

## Counts

- bars: 123 (locked: 123)
- tests: 94 (11 built offline, 82 scene tests, 1 look)
- scene entries present: 1, absent (Stage 3 work): 81
- built offline green today: 10, red: 1
- bars with every decider runnable today: 0
- bars with no deciding test: 0

## Bars

| bar | scope | proves at | decides | supports | held | runnable today |
|---|---|---|---|---|---|---|
| biome_cast | not_opened | 6 | sc_native_cast | LOOK_STAGE8 | 26 | no |
| weather_calendar | not_opened | 6 | sc_wind_plain | sc_gale_drawing, sc_wind_audio, sc_gale_exposure, sc_scent | - | no |
| wind_sound | not_opened | 6 | sc_wind_audio | sc_wind_plain, sc_gale_drawing, sc_gale_exposure, sc_scent | - | no |
| lean_heading | not_opened | 6 | sc_wind_plain | sc_gale_drawing, sc_wind_audio, sc_gale_exposure, sc_scent | - | no |
| plant_lean | not_opened | 6 | sc_wind_plain | sc_gale_drawing, sc_wind_audio, sc_gale_exposure, sc_scent | - | no |
| gale_dust | not_opened | 6 | sc_gale_drawing | sc_wind_plain, sc_wind_audio, sc_gale_exposure, sc_scent | - | no |
| stall_freeze | not_opened | 6 | sc_stall_wait | sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| gale_exposure | live_minimal | 6 | sc_gale_exposure | sc_wind_plain, sc_gale_drawing, sc_wind_audio, sc_scent | - | no |
| gale_turbines | not_opened | 6 | sc_working_wind | sc_home_routes, sc_ordered_travel, ix_route_growth | - | no |
| gale_raid_weight | not_opened | 6 | sc_raid_weight | - | - | no |
| upwind_scent | not_opened | 6 | sc_scent | sc_wind_plain, sc_gale_drawing, sc_wind_audio, sc_gale_exposure | - | no |
| downwind_fire | not_opened | 6 | sc_fire_bias, ix_fire_accountability | sc_stamping, sc_maker | - | no |
| ripple | not_opened | 6 | sc_concealment | sc_stall_wait, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places, T_SELFTEST, T_FAUNA_BEHAVIOURS | - | no |
| windbreak_lee | not_opened | 6 | sc_lee_reveal | sc_stall_wait, sc_concealment, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| stall_hunter | not_opened | 6 | sc_stall_predation, ix_conceal_hunt | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| vine_islands | not_opened | 6 | sc_island_land | sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| vine_creep | not_opened | 6 | sc_creep, ix_route_growth | sc_working_wind, sc_home_routes, sc_ordered_travel | - | no |
| vine_growth_exemption | not_opened | 6 | sc_creep | - | - | no |
| vine_hazard | not_opened | 6 | sc_vine_contact | sc_island_land, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| dripping_harvest | not_opened | 6 | sc_dripping | sc_island_land, sc_vine_contact, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| twitcher | live_minimal | 6 | sc_twitcher, floor_visual | sc_island_land, sc_vine_contact, sc_dripping, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| hollow_passage | not_opened | 6 | sc_hollow | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| crown_mob | not_opened | 6 | sc_crown | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| rearing | live_minimal | 6 | sc_rearing, floor_visual | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| walking | live_minimal | 6 | sc_walking, ix_route_growth | sc_working_wind, sc_home_routes, sc_ordered_travel, T_FUZZ | - | no |
| hoard | live_minimal | 6 | sc_hoard | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure, T_GPT_FIXES, T_FUZZ | - | no |
| quench | live_minimal | 6 | sc_quench, floor_visual | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure, T_FUZZ | - | no |
| sworn | live_minimal | 6 | sc_sworn | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_shedding, sc_strangler, sc_weeper, sc_sleeper, sc_lure, T_GPT_FIXES | - | no |
| shedding | live_minimal | 6 | sc_shedding | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_strangler, sc_weeper, sc_sleeper, sc_lure | - | no |
| strangler | live_minimal | 6 | sc_strangler | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_weeper, sc_sleeper, sc_lure | - | no |
| weeper | live_minimal | 6 | sc_weeper | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_sleeper, sc_lure | - | no |
| sleeper | live_minimal | 6 | sc_sleeper, floor_visual | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_lure | - | no |
| lure | live_minimal | 6 | sc_lure | sc_island_land, sc_vine_contact, sc_dripping, sc_twitcher, sc_hollow, sc_crown, sc_rearing, sc_hoard, sc_quench, sc_sworn, sc_shedding, sc_strangler, sc_weeper, sc_sleeper | - | no |
| smother_craft | not_opened | 6 | sc_smother_claim, sc_cane_fuel | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, ix_materials | - | no |
| dead_cane_fuel | not_opened | 6 | sc_cane_fuel | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, ix_materials | - | no |
| sweetline_landmark | not_opened | 6 | sc_tree_landmark | sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| sweetline_canopy | not_opened | 6 | sc_tree_landmark | sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| sweetline_shed | not_opened | 6 | sc_tree_shed | sc_tree_landmark, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| sweetline_scratching | not_opened | 6 | sc_tree_scratch | sc_tree_landmark, sc_tree_shed, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| sweetline_felt_bank | not_opened | 6 | sc_tree_bank | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_felt_comfort, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| felt_comfort | live_minimal | 6 | sc_felt_comfort | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| sweetline_visits | not_opened | 6 | sc_tree_traces | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| runway_bloom | not_opened | 6 | sc_bloom | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| vissler_arm_food | not_opened | 6 | sc_arm_food | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| thornhold_quills | not_opened | 6 | sc_thornhold_quill | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| thornhold_den_stand | not_opened | 6 | sc_thornhold_den | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| surrik_crustswim | not_opened | 6 | sc_surrik | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| ribbonwhip_wind_concealment | not_opened | 6 | sc_concealment, sc_bloom | sc_stall_wait, sc_lee_reveal, sc_stall_predation, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| shirrel_glide | not_opened | 6 | sc_shirrel_flight | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_rollbug, ix_ecology_places | - | no |
| shirrel_flight_art | not_opened | 6 | sc_shirrel_flight | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_rollbug, ix_ecology_places | - | no |
| rollbug_carrion | not_opened | 6 | sc_rollbug | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, ix_ecology_places | - | no |
| ruin_injections | later | 6 | sc_ruins | - | - | no |
| wind_vaporator | later | 6 | sc_vaporator | - | - | no |
| scavenger_camps | later | 6 | sc_camps | - | - | no |
| fire_stamping | not_opened | 6 | sc_stamping, ix_fire_accountability | sc_fire_bias, sc_maker | - | no |
| calling_pyre | later | 6 | sc_pyre_beliefs, sc_pyre_ritual | - | - | no |
| save_aliases | out | 6 | sc_removed_save_preservation | - | - | no |
| acoustic_payload | live_minimal | 6 | sc_acoustic_payload | - | - | no |
| proximity_hatch | live_minimal | 6 | sc_proximity_hatch | - | - | no |
| settings | not_opened | 6 | sc_settings | T_SELFTEST, T_FAUNA_BEHAVIOURS, T_SHIRREL_GLIDE, T_WILDLIFE_ZERO_PATHS | - | no |
| dependable_home_routes | approved | 6 | sc_home_routes, ix_route_growth | sc_working_wind, sc_ordered_travel | - | no |
| ordered_crossing_policy | approved | 6 | sc_ordered_travel, ix_route_growth | sc_working_wind, sc_home_routes | - | no |
| fire_maker_witness_trail | approved | 6 | sc_maker, ix_fire_accountability | sc_fire_bias, sc_stamping | - | no |
| premium_dead_cane | approved | 6 | sc_cane_fuel | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_healing, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, ix_materials | - | no |
| shokka_ambush | approved | 6 | sc_shokka | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| fuzzviper_ambush | approved | 6 | sc_fuzzviper | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| ribbonwhip_canopy_route | approved | 6 | sc_ribbon_route | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| pillowmoss_wet_spot | approved | 6 | sc_pillowmoss | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| tanglefuzz_den_ecology | approved | 6 | sc_tanglefuzz | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| cruststar_grazing_ecology | approved | 6 | sc_cruststar | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_regrowth, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| vissler_finite_arm_regrowth | approved | 6 | sc_arm_regrowth | sc_stall_wait, sc_concealment, sc_lee_reveal, sc_stall_predation, sc_bloom, sc_arm_food, sc_thornhold_quill, sc_thornhold_den, sc_surrik, sc_shokka, sc_fuzzviper, sc_ribbon_route, sc_pillowmoss, sc_tanglefuzz, sc_cruststar, sc_shirrel_flight, sc_rollbug, ix_ecology_places | - | no |
| bark_wardens_removed | out | 6 | sc_cuts | - | - | no |
| farmer_camps_removed | out | 6 | sc_cuts | - | - | no |
| sweetline_scratching_healing | approved | 6 | sc_tree_healing | sc_tree_landmark, sc_tree_shed, sc_tree_scratch, sc_tree_bank, sc_felt_comfort, sc_tree_traces, sc_smother_claim, sc_cane_fuel, ix_materials | - | no |
| route_observer | offline | 4-5 | sc_route_observer | - | - | no |
| witness_observer | offline | 4-5 | sc_witness_observer | - | - | no |
| economy_observer | offline | 4-5 | sc_economy_observer | - | - | no |
| wind_plain | live_minimal | 6 | sc_wind_plain, floor_visual | - | - | no |
| gale_drawing | live_minimal | 6 | sc_gale_drawing, floor_visual | - | - | no |
| wind_audio | live_minimal | 6 | sc_wind_audio | - | - | no |
| working_wind | live_minimal | 6 | sc_working_wind | - | - | no |
| raid_weight | quicktest | 6 | sc_raid_weight | - | - | no |
| scent | live_minimal | 6 | sc_scent | T_FUZZ | - | no |
| fire_bias | live_minimal | 6 | sc_fire_bias | - | - | no |
| stall_wait | live_minimal | 6 | sc_stall_wait | - | - | no |
| concealment | live_minimal | 6 | sc_concealment | - | - | no |
| lee_reveal | live_minimal | 6 | sc_lee_reveal | - | - | no |
| stall_predation | live_minimal | 6 | sc_stall_predation | - | - | no |
| island_land | live_minimal | 6 | sc_island_land | - | - | no |
| creep | live_minimal | 6 | sc_creep | T_SELFTEST | - | no |
| home_routes | live_minimal | 6 | sc_home_routes | - | - | no |
| ordered_travel | live_minimal | 6 | sc_ordered_travel | - | - | no |
| vine_contact | live_minimal | 6 | sc_vine_contact | - | - | no |
| dripping | live_minimal | 6 | sc_dripping | T_SELFTEST, T_SITE | - | no |
| hollow | live_minimal | 6 | sc_hollow | - | - | no |
| crown | live_minimal | 6 | sc_crown | T_SELFTEST, T_GPT_FIXES | - | no |
| smother_claim | live_minimal | 6 | sc_smother_claim | - | - | no |
| cane_fuel | live_minimal | 6 | sc_cane_fuel | - | - | no |
| tree_landmark | live_minimal | 6 | sc_tree_landmark, floor_visual | - | - | no |
| tree_shed | live_minimal | 6 | sc_tree_shed | - | - | no |
| tree_scratch | live_minimal | 6 | sc_tree_scratch | - | - | no |
| tree_healing | live_minimal | 6 | sc_tree_healing | - | - | no |
| tree_bank | live_minimal | 6 | sc_tree_bank | - | - | no |
| tree_traces | live_minimal | 6 | sc_tree_traces | - | - | no |
| native_cast | live_minimal | 6 | sc_native_cast, floor_payload | - | - | no |
| bloom | live_minimal | 6 | sc_bloom | T_SELFTEST, T_FAUNA_BEHAVIOURS, T_FUZZ | - | no |
| arm_regrowth | live_minimal | 6 | sc_arm_regrowth | - | - | no |
| arm_food | live_minimal | 6 | sc_arm_food | - | - | no |
| thornhold_quill | live_minimal | 6 | sc_thornhold_quill | - | - | no |
| thornhold_den | live_minimal | 6 | sc_thornhold_den | - | - | no |
| surrik | live_minimal | 6 | sc_surrik | T_FAUNA_BEHAVIOURS | - | no |
| shokka | live_minimal | 6 | sc_shokka | - | - | no |
| fuzzviper | live_minimal | 6 | sc_fuzzviper | - | - | no |
| ribbon_route | live_minimal | 6 | sc_ribbon_route | - | - | no |
| pillowmoss | live_minimal | 6 | sc_pillowmoss | - | - | no |
| tanglefuzz | live_minimal | 6 | sc_tanglefuzz | - | - | no |
| cruststar | live_minimal | 6 | sc_cruststar | - | - | no |
| shirrel_flight | live_minimal | 6 | sc_shirrel_flight | - | - | no |
| rollbug | live_minimal | 6 | sc_rollbug | T_SELFTEST, T_FAUNA_BEHAVIOURS | - | no |
| stamping | live_minimal | 6 | sc_stamping | - | - | no |
| maker | live_minimal | 6 | sc_maker | - | - | no |
| cuts | live_minimal | 6 | sc_cuts, sc_removed_save_preservation, floor_payload, floor_recovery | - | - | no |
| colony_walk | live_minimal | 6 | sc_colony_walk, floor_runtime, sc_settings, floor_persistence | - | - | no |

## Tests

| test | kind | stage | file::entry | today | item |
|---|---|---|---|---|---|
| T_SELFTEST | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_leaningscrub.py | PASS | - |
| T_FAUNA_BEHAVIOURS | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_leaningscrub_fauna_behaviours.py | PASS | - |
| T_GPT_FIXES | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_leaningscrub_gpt_fixes.py | PASS | - |
| T_SHIRREL_GLIDE | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_leaningscrub_shirrel_glide.py | PASS | - |
| T_SITE | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_leaningscrub_site.py | PASS | - |
| T_SOUNDSCAPE | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_scrub_soundscape.py | PASS | - |
| T_WILDLIFE_ZERO_PATHS | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_scrub_wildlife_zero_paths.py | FAIL | - |
| T_WIND | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_scrub_wind.py | PASS | - |
| T_SHED_PROBE | offline | 4-5 | src/RimMandrake/LeaningScrub/selftest_sweetline_shed_probe.py | PASS | - |
| T_FUZZ | offline | 4-5 | src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py | PASS | - |
| T_LINT_DEFS | offline | 4-5 | src/RimMandrake/Utils/lint_leaningscrub_defs.py | PASS | - |
| look_existing_home | live_minimal | 6 | src/RimMandrake/LeaningScrub/northstar/venomvine_islands_live.py::stage | entry present | SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY |
| sc_wind_plain | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_wind_plain | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_gale_drawing | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_gale_drawing | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_wind_audio | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_wind_audio | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_working_wind | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_working_wind | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_gale_exposure | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_gale_exposure | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_raid_weight | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_raid_weight | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_scent | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_scent | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_fire_bias | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_fire_bias | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_stall_wait | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_stall_wait | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_concealment | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_concealment | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_lee_reveal | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_lee_reveal | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_stall_predation | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_stall_predation | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_island_land | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_island_land | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_creep | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_creep | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_home_routes | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_home_routes | entry absent | SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY |
| sc_ordered_travel | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ordered_travel | entry absent | SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY |
| sc_vine_contact | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_vine_contact | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_dripping | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_dripping | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_twitcher | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_twitcher | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_hollow | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_hollow | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_crown | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_crown | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_rearing | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_rearing | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_walking | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_walking | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_hoard | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_hoard | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_quench | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_quench | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_sworn | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_sworn | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_shedding | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_shedding | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_strangler | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_strangler | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_weeper | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_weeper | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_sleeper | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_sleeper | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_lure | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_lure | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_smother_claim | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_smother_claim | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_cane_fuel | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_cane_fuel | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_tree_landmark | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tree_landmark | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_tree_shed | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tree_shed | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_tree_scratch | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tree_scratch | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_tree_healing | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tree_healing | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_tree_bank | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tree_bank | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_felt_comfort | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_felt_comfort | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_tree_traces | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tree_traces | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_native_cast | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_native_cast | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_bloom | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_bloom | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_arm_regrowth | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_arm_regrowth | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_arm_food | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_arm_food | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_thornhold_quill | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_thornhold_quill | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_thornhold_den | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_thornhold_den | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_surrik | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_surrik | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_shokka | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_shokka | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_fuzzviper | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_fuzzviper | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_ribbon_route | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ribbon_route | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_pillowmoss | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_pillowmoss | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_tanglefuzz | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_tanglefuzz | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_cruststar | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_cruststar | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_shirrel_flight | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_shirrel_flight | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_rollbug | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_rollbug | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| sc_ruins | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ruins | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_vaporator | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_vaporator | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_camps | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_camps | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_stamping | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_stamping | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_maker | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_maker | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_pyre_beliefs | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_pyre_beliefs | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_pyre_ritual | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_pyre_ritual | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_settings | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_settings | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_cuts | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_cuts | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_route_observer | offline | 4-5 | src/RimMandrake/LeaningScrub/validation.py::scene_route_observer | entry absent | SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY |
| sc_witness_observer | offline | 4-5 | src/RimMandrake/LeaningScrub/validation.py::scene_witness_observer | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| sc_economy_observer | offline | 4-5 | src/RimMandrake/LeaningScrub/validation.py::scene_economy_observer | entry absent | SCRUB_PROVE_VINE_FORMS_AND_CRAFT |
| sc_colony_walk | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_colony_walk | entry absent | SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY |
| sc_removed_save_preservation | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_removed_save_preservation | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_acoustic_payload | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_acoustic_payload | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| sc_proximity_hatch | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_proximity_hatch | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| ix_route_growth | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ix_route_growth | entry absent | SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY |
| ix_conceal_hunt | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ix_conceal_hunt | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| ix_materials | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ix_materials | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| ix_fire_accountability | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ix_fire_accountability | entry absent | SCRUB_PROVE_WIND_FIRE_AND_RITUAL |
| ix_ecology_places | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_ix_ecology_places | entry absent | SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS |
| floor_runtime | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_floor_runtime | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| floor_persistence | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_floor_persistence | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| floor_payload | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_floor_payload | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| floor_visual | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_floor_visual | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| floor_recovery | live_minimal | 6 | src/RimMandrake/LeaningScrub/validation.py::scene_floor_recovery | entry absent | SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY |
| LOOK_STAGE8 | look | 8 | - | Stage 8: the owner's own walk | - |

## Held statements placed

| source row | bars | tests | note |
|---|---|---|---|
| design/RimMandrake/validation_holding/owner_look_defects_2026-11-12.md row 26 | biome_cast | sc_native_cast, LOOK_STAGE8 | a question, not a defect: the dinosaur he saw in big pit BP3 is RM_Segnosaurus, LeaningScrub's absorbed fauna (RM_Absorbed_Segnosaurus.xml); the pit-site wildlife clear landed a09040a09e; the cast's presence and natural generation are what sc_native_cast decides, and he judges whether it belongs at the walk |
