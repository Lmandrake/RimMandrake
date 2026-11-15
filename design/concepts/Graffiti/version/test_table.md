# Graffiti 0.1.0 test table (read view of test_table.json)

Made by `pilot_throwaway/make_test_table.py`, 2026-11-15T23:28:31Z. A bar passes when every deciding test passes.

## Counts

- bars: 47 (locked: 47)
- tests: 46 (12 built offline, 1 new offline, 32 live, 1 look)
- scene entries present: 18, absent: 12
- built offline green today: 11, red: 1
- bars with every decider runnable today: 30
- known red: P_A9 = RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL

## Bars

| bar | proves at | decides | supports | held | runnable today |
|---|---|---|---|---|---|
| inv_mark_on_wall | 6 | sc_wall_closeup, P_A9 | sc_spree_corridor, T_FUZZ | - | no |
| inv_mark_art_set | 6 | sc_gallery, sc_spree_variety | T_LINT, T_SHIP_CHECK, sc_beauty_pair | - | no |
| inv_beauty_and_craft | 6 | sc_beauty_pair, sc_art_skill | sc_spree_corridor, LOOK_STAGE8 | 5 | no |
| inv_ideo_sigils | 6 | sc_sigil, T_SIGIL_COVERAGE | T_LINT, T_FUZZ | - | yes |
| inv_spree | 6 | sc_spree_wall | sc_spree_corridor, T_SPREE_SURPRISE | - | yes |
| inv_joy_and_idle_tag | 6 | sc_own_fun | - | - | yes |
| inv_player_orders | 6 | sc_player_orders | - | - | yes |
| inv_viewer_mood | 6 | sc_rereads, sc_hostile_thought | sc_beauty_pair, T_LINT | - | yes |
| inv_social_layer | 6 | sc_mockery, sc_answer_wall, sc_tribute_memorial, sc_fights | T_FUZZ, T_MSG_COUNTERS_RESET | - | no |
| inv_visitors | 6 | sc_visitors | - | - | no |
| inv_raid_marks | 6 | sc_raid_exit, sc_going_over, sc_raid_retaken, T_RAID_TAG_BUILT_WALL_ONLY | - | 2 | yes |
| inv_breach_bias | 6 | sc_breach_bias_raid, sc_breach_toggle | T_FUZZ | - | yes |
| inv_scrub_protection | 6 | sc_scrub_protection | T_FUZZ | - | yes |
| inv_temperament | 6 | sc_temperament | - | - | yes |
| inv_wall_loss | 6 | sc_wall_loss | - | - | no |
| inv_settings | 6 | sc_settings, T_SETTINGS_SCREENS | T_LINT, T_SHIP_CHECK, sc_breach_toggle | - | yes |
| inv_standalone | 6 | sc_settings, H1_IDEO_RELOAD | T_SHIP_CHECK | 1 | yes |
| inv_raider_future_marks | 6 | sc_raider_pressure | - | - | yes |
| inv_weathering | 6 | sc_weathered_raid_mark, T_WEATHER_OFFLINE | - | - | yes |
| mark_appears | 6 | sc_spree_wall | sc_spree_corridor, T_FRESH_QT, T_SPREE_SURPRISE, T_FUZZ | - | yes |
| reads_at_play_zoom | 6 | sc_gallery | T_PLAY_ZOOM, LOOK_STAGE8 | - | yes |
| sits_on_wall | 6 | sc_wall_closeup, P_A9 | T_FUZZ | - | no |
| marks_various | 6 | sc_spree_variety | sc_spree_corridor, T_FUZZ | - | no |
| ideo_sigil | 6 | sc_sigil | T_FUZZ, T_SIGIL_COVERAGE | - | yes |
| punk_register | 6 | sc_gallery | LOOK_STAGE8 | - | yes |
| no_english | 6 | sc_gallery | T_LINT, LOOK_STAGE8 | - | yes |
| not_dirt | 6 | sc_gallery | LOOK_STAGE8 | - | yes |
| ugliness_visible | 6 | sc_beauty_pair | sc_spree_corridor, sc_walk, LOOK_STAGE8 | 5 | yes |
| art_skill | 6 | sc_art_skill | sc_spree_corridor, T_FUZZ | - | no |
| own_fun | 6 | sc_own_fun | - | - | yes |
| rereads_daily | 6 | sc_rereads | sc_lived_in_soak | - | yes |
| mockery | 6 | sc_mockery | T_FUZZ, sc_lived_in_soak | 3 | no |
| tribute_memorial | 6 | sc_tribute_memorial | T_FUZZ | - | no |
| answer_wall | 6 | sc_answer_wall | - | - | no |
| scrub_protection | 6 | sc_scrub_protection | T_FUZZ | - | yes |
| player_orders | 6 | sc_player_orders | - | - | yes |
| raid_mark_troubles | 6 | sc_raid_exit, sc_hostile_thought, sc_raid_retaken, sc_weathered_raid_mark, T_RAID_TAG_BUILT_WALL_ONLY | T_FUZZ | 2 | yes |
| going_over | 6 | sc_going_over | - | - | yes |
| raider_pressure | 6 | sc_raider_pressure | - | - | yes |
| visitors | 6 | sc_visitors | - | - | no |
| fights_reasons | 6 | sc_fights | - | - | no |
| temperament | 6 | sc_temperament | - | - | yes |
| stands_alone_settings | 6 | sc_settings, sc_breach_toggle, sc_breach_bias_raid | H1_IDEO_RELOAD, T_SETTINGS_SCREENS | 1 | yes |
| stories_not_tax | 6 | sc_lived_in_soak | sc_rereads, T_MSG_COUNTERS_RESET | 3, 4, 6 | no |
| paint_dies_with_wall | 6 | sc_wall_loss | - | - | no |
| weathering_bounds_marks | 6 | T_WEATHER_OFFLINE, sc_weathered_raid_mark | - | - | yes |
| walk_lived_in | 6 | sc_walk | LOOK_STAGE8, T_FULL_LIST_MODE | - | no |

## Tests

| test | kind | stage | file::entry | today | new item |
|---|---|---|---|---|---|
| T_FUZZ | offline | 4-5 | src/RimMandrake/Utils/selftest_graffiti_fuzz.py | PASS | - |
| T_LINT | offline | 4-5 | src/RimMandrake/Utils/selftest_graffiti_lint.py | PASS | - |
| T_SIGIL_COVERAGE | offline | 4-5 | src/RimMandrake/Graffiti/sigil_coverage.py | PASS | - |
| T_SETTINGS_SCREENS | offline | 4-5 | src/RimMandrake/Utils/selftest_settings_screens.py | PASS | - |
| T_SHIP_CHECK | offline | 4-5 | src/RimMandrake/Graffiti/ship_check.py | FAIL | - |
| T_FULL_LIST_MODE | offline | 4-5 | src/RimMandrake/Graffiti/selftest_full_list_mode.py | PASS | - |
| T_FRESH_QT | offline | 4-5 | src/RimMandrake/Graffiti/selftest_graffiti_fresh_quicktest.py | PASS | - |
| T_PLAY_ZOOM | offline | 4-5 | src/RimMandrake/Graffiti/selftest_graffiti_play_zoom.py | PASS | - |
| T_SPREE_SURPRISE | offline | 4-5 | src/RimMandrake/Graffiti/selftest_graffiti_spree_surprise.py | PASS | - |
| T_V1_LIVE_VERDICTS | offline | 4-5 | src/RimMandrake/Graffiti/selftest_graffiti_v1_live.py | PASS | - |
| T_WEATHER_OFFLINE | offline | 4-5 | src/RimMandrake/Utils/selftest_graffiti_weather.py | PASS | - |
| T_RAID_TAG_BUILT_WALL_ONLY | offline | 4-5 | src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py | PASS | - |
| T_MSG_COUNTERS_RESET | offline | 4-5 | src/RimMandrake/Utils/selftest_graffiti_message_counters.py | not written yet: Stage 3 work (RIMMANDRAKE_RESET_GRAFFITI_MESSAGE_COUNTERS_EACH_GAME) | RIMMANDRAKE_RESET_GRAFFITI_MESSAGE_COUNTERS_EACH_GAME |
| sc_spree_corridor | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_spree_corridor | entry absent | - |
| sc_spree_wall | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::spree_wall | entry present | - |
| sc_spree_variety | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::spree_variety | entry absent | - |
| sc_wall_closeup | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::wall_closeup | entry absent | - |
| sc_gallery | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::gallery | entry present | - |
| sc_beauty_pair | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::beauty_pair | entry present | - |
| sc_art_skill | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_art_skill | entry absent | - |
| sc_own_fun | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_own_fun | entry present | - |
| sc_rereads | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_rereads | entry present | - |
| sc_mockery | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_mockery | entry absent | - |
| sc_tribute_memorial | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_tribute_memorial | entry absent | - |
| sc_answer_wall | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_answer_wall | entry absent | - |
| sc_scrub_protection | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A6 | entry present | - |
| sc_sigil | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A3 | entry present | - |
| sc_player_orders | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A7 | entry present | - |
| sc_raid_exit | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A2 | entry present | - |
| sc_hostile_thought | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A5 | entry present | - |
| sc_raid_retaken | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_raid_retaken | entry present | - |
| sc_going_over | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A4 | entry present | - |
| sc_raider_pressure | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_raider_pressure | entry present | - |
| sc_visitors | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_visitors | entry absent | - |
| sc_fights | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_fights | entry absent | - |
| sc_temperament | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_temperament | entry present | - |
| sc_settings | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_settings_each_switch | entry present | - |
| sc_breach_toggle | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::breach_bias_toggle_flips | entry present | - |
| sc_wall_loss | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_wall_loss | entry absent | - |
| sc_lived_in_soak | live_full | 6 | src/RimMandrake/Graffiti/validation.py::scene_lived_in_soak | entry absent | - |
| sc_walk | live_full | 6 | src/RimMandrake/Graffiti/validation.py::scene_walk_lived_in | entry absent | - |
| sc_weathered_raid_mark | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_weathered_raid_mark | entry present | - |
| sc_breach_bias_raid | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_breach_bias_raid | entry present | - |
| P_A9 | live_minimal | 6 | src/RimMandrake/Graffiti/graffiti_v1_live_proof.py::A9 | entry present (known red) | - |
| H1_IDEO_RELOAD | live_minimal | 6 | src/RimMandrake/Graffiti/validation.py::scene_ideo_removed_save_reload | entry present | RIMMANDRAKE_PROVE_GRAFFITI_MARKS_RELOAD_AFTER_IDEO_LOST |
| LOOK_STAGE8 | look | 8 | - | Stage 8: the owner's own walk | - |

## Held statements placed

| row | bars | tests | note |
|---|---|---|---|
| 1 | inv_standalone, stands_alone_settings | H1_IDEO_RELOAD | - |
| 2 | raid_mark_troubles, inv_raid_marks | T_RAID_TAG_BUILT_WALL_ONLY, sc_raid_exit | - |
| 3 | stories_not_tax, mockery | sc_lived_in_soak, sc_mockery | may be by design: the owner's call at the Stage 8 walk; the soak measures it |
| 4 | stories_not_tax | sc_lived_in_soak | the owner's call; the soak measures the slope over weeks |
| 5 | ugliness_visible, inv_beauty_and_craft | sc_beauty_pair, sc_walk, LOOK_STAGE8 | look only: text and picture agree is judged by eye; decided at sc_beauty_pair and the walk |
| 6 | stories_not_tax | T_MSG_COUNTERS_RESET | harness defect; its fix makes sc_lived_in_soak's message count an honest instrument |
