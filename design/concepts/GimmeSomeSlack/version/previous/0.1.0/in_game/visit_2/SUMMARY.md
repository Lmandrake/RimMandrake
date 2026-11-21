# GimmeSomeSlack 0.1.0 — in-game acceptance, visit 2

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_ACCEPTANCE_VISIT_TWO, game a, Archmagi. Started 2026-11-19 18:59 PST.

## Progress
- 18:59 precondition `in_game 0.1.0` [measured]; bridge taken by BENCH; skeleton written.
- 19:04 deploy dry run: in sync (362 files); committed DLL a00e4619… MATCHes its .srchash (dll_source_stamp). Tier gimmesomeslack (12 mods, all 5 DLC); game a launched through Steam.
- 19:09 offline gate green (0 red, ~300 s).
- 19:10–19:26 proof_all --live, four runs: run 1 matrix+core (80 PASS, 1 FAIL: M8), run 2 aerial+style+scenes, run 3 core+save+statics (M8 PASS; SL3/S12d read without the style block staged, a split of mine: excluded), run 4 the whole proof in one session: 168 PASS, 0 FAIL, 2 UNMEASURED (the two FlowWorks-tier rows).
- 19:28–19:45 M8 diagnosis: six core-only repeats all FAIL (shots on or off); a probe run re-reads the census after the FAIL: the dead end is listed at once, with no tick between. Filed RIMMANDRAKE_SETTLE_SLACK_M8_CENSUS_READS_ONE_POLL_EARLY.
- 19:47–19:53 gravship on PASS; off: staging refused once and the script wrote no row (fixed test-first, closed: RIMMANDRAKE_GUARD_SLACK_GRAVSHIP_SCENE_EXIT_WRITES_NO_ROW, 774d8f068b); rerun PASS.
- 19:56 sc_stub_joins on his review save GSS_OWNER_LOOK_20261116 (loaded, never saved over): PASS, 375 stubs, 0 off line or slope, worst 7.1°.
- 19:58–20:02 all 31 review stations captured with the game's render and looked at (screenshots/sheet0-3.jpg).
- 20:04 tier gimmesomeslack_flowworks (13 mods): SC_under_liquid_pit and SC_shock_reach_deck_cord_per_value PASS; the tier's log budget caught an untraced error (filed RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR).
- 20:10 tier bridge (10 mods, no GSS): removal check on the run-4 proof save: PASS.
- 20:12–20:27 owner's full list (316 mods, Camera+ for zoom, all 5 DLC) loaded on game a. His review save would not load on it (it records SimpleCameraSetting, which his list replaces with Camera+), so 20:32–20:45 a fresh labelled review map was built on the full list (`human_review.py --build`, 31 stations, 62 labels, 31 sign books) and saved as GSS_VISIT2_WALK_20261119.rws (Saves stat-diff: one new file; his four GSS saves byte-identical; backup D:\ClaudeWork\rimmandrake\backups\saves_gss_visit2_20261119).
- 20:45 sc_walk (gss_playtest_runner --recipe full) on that map: FAIL. 20:46–20:57 diagnosis (below). Filed RIMMANDRAKE_SPLIT_SLACK_WALK_FAILS_ONLY_BESIDE_REVIEW_STATIONS.



## What ran
- Game a on Archmagi, RimWorld 1.6.4871 rev590. The GSS deployed folder hash is sha256:9db9f693… (DLL a00e4619…, source 85f388636e). It did not change during the visit (no redeploy). Every row carries `build_match.py identity` (mod_hash, game_build, active_mods, tier or full_list, unit).
- Tiers: gimmesomeslack (12 mods) for the proof runs, gravship and stub joins; gimmesomeslack_flowworks (13) for SC_under_liquid_pit and SC_shock_reach_deck_cord_per_value; bridge (10, no GSS) for the removal check; the owner's full list (316) for sc_walk and the walk save. Every list holds all five DLC.
- The deployed FlowWorks DLL was older than origin/main (game copy of 2026-11-16 02:26). It was not redeployed, because it is not this visit's mod. This is noted on RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR.

## Results [measured]
197 stage-6 checks: 194 PASS, 3 FAIL, 0 UNMEASURED (the last row of each).
- FAIL P_M8_break_two_ends_live_dead and sc_cut_ends: the first census after a one-cell cut lists only the live end. FAIL in 7 of 9 core runs, PASS in 2 (runs 3 and 4). Experiment: the next census, with no tick between, lists the dead end. The dead end stays listed at +30, +250 and +1000 ticks and after a fresh probe (evidence/m8_probe.json). So the end is never lost; the first read comes before the rebuild is published. This is the symptom of visit 1's RIMMANDRAKE_MEND_SLACK_DEAD_CUT_END_MISSING_FROM_ENDS (closed 2026-11-17). Filed RIMMANDRAKE_SETTLE_SLACK_M8_CENSUS_READS_ONE_POLL_EARLY.
- FAIL sc_walk (full list): on the labelled review map, cords and soak read "live cords != fresh build" (67 edges, all on review stations 5 MODERN: EVERY COLOUR ENTRY and 31 STYLED BLUEPRINTS); ui fails 1 of 24 (conduit look pick Industrial->Industrial); save_reload_b lost 1 of 7 lines. Experiments: the batch and speed tick modes fail the same way (so not frame timing). On a plain full-list quicktest, the same build passes cords, soak and save_reload (ui INVALID there: no clean site). Filed RIMMANDRAKE_SPLIT_SLACK_WALK_FAILS_ONLY_BESIDE_REVIEW_STATIONS.
- Every other check PASS. That includes every check that visit 1 left UNMEASURED: sc_walls, sc_rewire_cost, sc_cords_under_items (the pit row, on the FlowWorks tier), sc_floor_end_shock, and sc_shock_reach (the deck-cord row, on the FlowWorks tier). It also includes visit 1's FAILs sc_true_to_grid / P_D2 and sc_stub_joins (375 stubs, 0 off line or slope).
- No fix to the mod was made in the sitting.

## Pipeline defects fixed in this run
- RIMMANDRAKE_GUARD_SLACK_GRAVSHIP_SCENE_EXIT_WRITES_NO_ROW: gravship_scene.py wrote no row when prove_gravship's staging refused (SystemExit got past `except Exception`). The test came first (selftest_gravship_scene_exit.py, red, then green). Published 774d8f068b and closed.
- This visit's visit_rows.py: at 19:19, a row excluded as a harness split (run 3's SL3, read without the style block staged) still fed a scene read and wrote one sc_true_to_grid FAIL row. The slim now keeps only the --only rows. That one row was removed: it recorded no run of the scene, and SL3 PASSed in run 4's whole session.

## Record notes
- Build match (`build_match.py check --mod GimmeSomeSlack --visit 2`): 197 cases, 194 count, 3 to re-run. The 3 are sc_true_to_grid, sc_cords_under_items and sc_shock_reach: their last scene rows read an input that can ask only on tier gimmesomeslack_flowworks, and the table names tier gimmesomeslack for the scene. Filed RIMMANDRAKE_MATCH_SLACK_TWO_TIER_SCENE_ROWS_NEVER_COUNT (a design choice, for the Conductor). The P15 row names no check in the table (read, not counted).
- Rows not recorded as runs (my harness splits, not mod readings): the FlowWorks-tier rows of runs 2 and 4 on tier gimmesomeslack (FlowWorks absent); run 2's S12d (it needs the d4_save block); run 3's SL1-3, S12d and S7 (a save without the style block staged). Each was run again where it can ask.
- The earlier UNMEASURED rows of sc_cords_under_items and sc_shock_reach (run 2, FlowWorks absent) stay as history before their PASS rows.
- `held` names what proof_all locks (weather Clear, incidents cleared). Gravship, stub joins, the removal check and the walk lock nothing.

## Owed cases from the blind challenge (cycle 6)
- P15_DECIDER_FORGETS_FLEXIBLE_PIPES (bars no_hose, no_hose_in_gss): a row of its own, UNMEASURED. No stage-6 in-game check reads the settings text or def labels for hose words, so the in-game checks would NOT have seen it. A read of the shipped build: the settings header const has no hose, reel or flexible pipe, and 0 deployed XML files mention "flexible pipe". An in-game reader is the Conductor's call (the bar can be decided offline).
- NK_CONDUIT_INVISIBLE / NK_INVISIBLE_CONDUIT: sc_conduit_invisible PASS.
- NK_CORDS_LIE_SLACK / NK_CORD_SLACK_LAY: sc_cords_slack PASS.
- NK_NO_UNFORCED_SHARP_TURN: sc_no_sharp_turn PASS.
- NK_CORDS_MEET_WALLS_AT_FACE: sc_walls PASS.
- NK_STRIP_AT_EVERY_JUNCTION / NK_JUNCTION_STRIPS: sc_junction_strips PASS; sc_dense_tangle PASS.
- NK_DENSE_BLOCK_TANGLE: sc_dense_tangle PASS.
- NK_CORD_SHAPE_VARIATION_PROBE / NK_CORDS_NEVER_REPEAT: sc_no_repeat PASS.
- NK_DRAWING_TRUE_TO_GRID / NK_CONNECTIVITY_TRUTH: sc_true_to_grid PASS; sc_cords_under_items PASS.
- NK_CUT_LIVE_AND_DEAD_ENDS / NK_BREAK_ENDS_LIVE_DEAD: sc_cut_ends FAIL (M8, above).
- NK_FLOOR_END_SHOCKS_CROSSERS / NK_FLOOR_END_SHOCK: sc_floor_end_shock PASS; sc_fuel_ignition PASS; sc_shock_reach PASS.
- NK_NO_STALL_ON_REWIRE / NK_REBUILD_COST: sc_rewire_cost PASS.
- NK_SPANS_ABOVE_EVERYTHING / NK_OVERHEAD_SPANS: sc_spans PASS.
- NK_FALLEN_SPAN_ON_GROUND / NK_DOWNED_SPANS: sc_fallen_span PASS.
- NK_FALLEN_WIRE_SHOCKS_CROSSERS / NK_FALLEN_WIRE_SHOCK: sc_shock PASS; sc_shock_reach PASS.
- NK_SHOCK_REACH_SETTING: sc_shock_reach PASS.
- NK_LIVE_WIRE_LIGHTS_FUEL: sc_fuel_ignition PASS.
- NK_RESTRING_CUT_SPAN / NK_RESTRING_JOB / NK_WIRE_DOWN_ALERT: sc_restring PASS.
- NK_TAP_STEALS_AND_COSTS_GOODWILL / NK_POWER_THEFT: sc_tap_theft PASS; sc_statics_new_game PASS.
- NK_FOUR_LOOKS_ONE_RUN / NK_FOUR_STYLES: sc_four_looks PASS on its scripted reads. No grayscale judge agent ran in this visit, because this helper starts no agents.
- NK_SETTINGS_SWITCH_CLEANLY / NK_MOD_SETTINGS / NK_PIPE_POLE_SWITCH: sc_settings PASS; sc_owner_change PASS; sc_gravship PASS.
- NK_GRAVSHIP_KEEPS_CONNECTIONS / NK_GRAVSHIP_CONNECTIVITY: sc_gravship PASS (on and off).
- NK_OWNER_CHANGE_COILS_WIRES / NK_OWNER_CHANGE_CUT: sc_owner_change PASS.
- NK_STATICS_CLEAR_BETWEEN_GAMES / NK_GAME_STATICS_RESET: sc_statics_new_game PASS.
- NK_UNINSTALL_CLEAN: sc_removal_consequence PASS (no error names the mod).
- NK_CORDS_DRAW_UNDER_THINGS: sc_cords_under_items PASS.
- NK_WALK_SCAVENGER_BASE: sc_walk FAIL (above).
- Unsettled "ground cords hide a 0.24-cell wall clip under the wall art": I looked at station 12 (WALL + ROCK ENTRIES). The cord stubs enter the wall and rock faces with no visible clip at the capture's zoom (screenshots/sheet1.jpg) [guess ~65%: a 0.24-cell clip would show at that scale].
- Owed from the road back (unrun.jsonl): none recorded.

## Beyond the checks
All 31 stations of his review save were captured with the game's render and looked at (screenshots/sheet0-3.jpg; the full PNGs are in D:\ClaudeWork\scratch\gss_v2\shots). Strange things: 7 in strange.jsonl, 3 filed, 4 explained, 0 open.

## Savegame for his walk
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_VISIT2_WALK_20261119.rws`: the 31-station labelled review map (sign books in the save, floating labels from human_review.py). It was built on his full list and the deployed build, and saved before the walk runner touched the map. Load it on his full list (Camera+ zooms).

## Exit
```
ingame_rows: {P_A8_same_frame_dirty_not_dropped: pass, P_B13_hidden_conduit_hookup_not_drawn: pass, P_B1_rope_settle: pass, P_B3_whip_live_ends: pass, P_B3c_spark_rides_whip: pass, P_B4b_sparks_thrown_ticking: pass, P_B4c_spark_intensity_scales_downed: pass, P_B4d_spark_budget_shared_visible_first: pass, P_B5_selection_highlight: pass, P_B6_tangle_lit_strips: pass, P_B6b_strips_dark_when_dead: pass, P_B7_ground_cords_never_sway: pass, P_B8_lod_far_zoom: pass, P_B9_cutscene_guard_idle: pass, P_D1_zero_tick_rereads_same: pass, P_D2_fresh_builder_same: pass, P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down: pass, P_GS1_keep_wires_on_gravship_on_aboard_span_flies: pass, P_M10_tangle_threshold_setting: pass, P_M11_dive_through_setting: pass, P_M12a_slide_under_off_plug_on_cell_centre: pass, P_M12b_slide_under_on_plug_off_centre: pass, P_M13a_linked_one_net_across_gap: pass, P_M13b_far_consumer_powered: pass, P_M13c_unlink_two_nets_relink_one: pass, P_M13d_refusals: pass, P_M13e_hostile_mast_not_autolinked: pass, P_M14_gap_control_without_fix: pass, P_M14a_remove_middle_both_ends_resolve: pass, P_M14b_dead_pole_drops_live_and_dead_cords: pass, P_M14c_live_tip_glows: pass, P_M15_explosion_cuts_span: pass, P_M15a_wire_down_alert_lists_cut: pass, P_M15b_restring_rejoins: pass, P_M15c_wire_down_alert_clears_on_restring: pass, P_M15d_diagonal_cut_halves_meet_on_line: pass, P_M15e_restring_is_a_colonist_job: pass, P_M15f_restring_joined_run_one_look: pass, P_M17_owner_change_cuts_cross_owner_wires: pass, P_M19_tap_drains_one_way: pass, P_M19m_tap_mixed_net_connects_own_conduit: pass, P_M19n_taps_off_control: pass, P_M1_conduit_transparent: pass, P_M1_cords_exist: pass, P_M1_node_census: pass, P_M1c_end_pieces: pass, P_M1e_machine_on_inwall_run_draws_a_cord: pass, P_M1f_machine_on_hidden_conduit_draws_none: pass, P_M20a_fallen_wire_shock_flip: pass, P_M20b_fallen_wire_knockback_flip: pass, P_M20c_fallen_wire_ignites_flip: pass, P_M20d_keep_wires_setting_roundtrip: pass, P_M20e_shock_cells_die_with_wire: pass, P_M21a_cut_wires_on_owner_change_off_keeps_link: pass, P_M21b_cut_wires_on_owner_change_on_cuts_link: pass, P_M21c_drip_loops_off_plain_curve: pass, P_M21d_drip_loops_on_loop_samples: pass, P_M21e_keep_wires_on_gravship_off_setting_state: pass, P_M21f_keep_wires_on_gravship_on_setting_state: pass, P_M22a_kinetic_sway_on_swings_never_cuts: pass, P_M22b_kinetic_sway_off_does_nothing: pass, P_M2_cords_only_within_net: pass, P_M2b_no_vertex_unwalkable: pass, P_M2c_no_sharp_bends: pass, P_M5_local_invalidation: pass, P_M6_overlay_lines_intact: pass, P_M7_off_restores_vanilla: pass, P_M7b_on_again_invisible: pass, P_M8_break_two_ends_live_dead: fail, P_M8c_source_off_reads_dead_250: pass, P_MX_A04_N3_R12_fallen: pass, P_MX_A05_N3_R19_up: pass, P_MX_A06_N5_R6_fallen: pass, P_MX_A07_N5_R12_up: pass, P_MX_A08_N5_R19_cut: pass, P_MX_A09_N2_R6_cut: pass, P_MX_A10_N2_R12_fallen: pass, P_MX_A11_N2_R19_up: pass, P_MX_A12_N3_R6_fallen: pass, P_MX_C00_empty: pass, P_MX_D00_n1_S0: pass, P_MX_D05_n10_S1: pass, P_MX_D10_n100_S2: pass, P_MX_D15_n1000_S3: pass, P_MX_F00_T0_S0: pass, P_MX_F04_T1_S0: pass, P_MX_F11_T2_S3: pass, P_MX_F13_T3_S1: pass, P_MX_F18_T4_S2: pass, P_MX_F21_T5_S1: pass, P_MX_F25_T6_S1: pass, P_MX_F30_T7_S2: pass, P_MX_F33_T8_S1: pass, P_MX_F39_T9_S3: pass, P_MX_F42_T10_S2: pass, P_MX_F47_T11_S3: pass, P_MX_F51_T12_S3: pass, P_MX_F54_T13_S2: pass, P_MX_F56_T14_S0: pass, P_MX_F60_T15_S0: pass, P_P1B_perf_rebuild: pass, P_R1_span_altitude_above_pawns_below_blueprints: pass, P_R2_spans_and_heads_drawn: pass, P_R3_sway_proxy: pass, P_S10_legacy_default_materials: pass, P_S11_lamp_master_off_vanilla: pass, P_S12a_D1_legacy_run_one_look: pass, P_S12b_D7_bulk_spawn_cost: pass, P_S12c_D5_multilink_one_frame: pass, P_S12d_D4_pending_queue_save: pass, P_S12e_batched_links_merge: pass, P_S1_pick_reaches_blueprint: pass, P_S2_blueprint_frame_building: pass, P_S3_god_mode: pass, P_S4_copy_carries_look: pass, P_S5_reinstall_keeps_look: pass, P_S6_spans_in_pole_look: pass, P_S7_save_load_styles: pass, P_S8_legacy_unstyled_draws_default: pass, P_S8b_legacy_joined_to_styled_stores_look: pass, P_S9a_two_runs_two_styles: pass, P_S9b_bridge_largest_wins: pass, P_S9c_split_keeps_styles: pass, P_S9d_restyle_and_materials: pass, P_SC_bend_draws_no_joint_tee_draws_one: pass, P_SC_box_stub_slope: pass, P_SC_cord_end_one_kind: pass, P_SC_cords_all_slack: pass, P_SC_cut_battery_each_side_both_live: pass, P_SC_cut_never_powered_both_dead: pass, P_SC_dead_wire_lights_no_fuel: pass, P_SC_dead_wire_shocks_nobody: pass, P_SC_doorway_run_is_one_cord: pass, P_SC_floor_end_bites_aerial_master_off: pass, P_SC_floor_end_cord_behind_spares: pass, P_SC_floor_end_dead_spares: pass, P_SC_floor_end_every_end_over_spark_budget: pass, P_SC_floor_end_fixer_spared_other_builder_shocked: pass, P_SC_floor_end_live_shocks: pass, P_SC_floor_end_unfinished_run_bites: pass, P_SC_no_two_cords_alike: pass, P_SC_restring_drafted_no_job: pass, P_SC_restring_work_scheduler_takes_it: pass, P_SC_shock_reach_deck_cord_per_value: pass, P_SC_shock_reach_default_all: pass, P_SC_shock_reach_three_values: pass, P_SC_sparse_room_no_tangle: pass, P_SC_splicer_spared_bystander_shocked: pass, P_SC_statics_clear_between_games: pass, P_SC_under_battery_dry: pass, P_SC_under_furniture_dry: pass, P_SC_under_item_stack_dry: pass, P_SC_under_junction_piece_dry: pass, P_SC_under_liquid_pit: pass, P_SL1_save_landed_new_file_only: pass, P_SL2_save_names_no_class_of_ours: pass, P_SL3_after_load_census_equal: pass, P_ST1_styles_textures_load: pass, P_ST2_switch_changes_textures: pass, P_ST3_extcord_colour_modes: pass, P_ST4_settings_roundtrip: pass, P_ST5_restore_default_and_master: pass, P_SW1_highlight_off_draws_no_ring: pass, P_SW2_lod_off_far_zoom_draws_full: pass, P_SW3_break_readout_off_no_glow_no_whip: pass, P_SW4_sparks_only_overlay_shut_no_glow: pass, P_SW5_hide_hookup_off_leaves_vanilla_wire: pass, P_SW6_needless_loops_off_reaches_builder: pass, P_Z_log_budget: pass, sc_conduit_invisible: pass, sc_cords_slack: pass, sc_cords_under_items: pass, sc_cut_ends: fail, sc_dense_tangle: pass, sc_fallen_span: pass, sc_floor_end_shock: pass, sc_four_looks: pass, sc_fuel_ignition: pass, sc_gravship: pass, sc_junction_strips: pass, sc_no_repeat: pass, sc_no_sharp_turn: pass, sc_owner_change: pass, sc_removal_consequence: pass, sc_restring: pass, sc_rewire_cost: pass, sc_settings: pass, sc_shock: pass, sc_shock_reach: pass, sc_shock_restring: pass, sc_spans: pass, sc_statics_new_game: pass, sc_stub_joins: pass, sc_tap_theft: pass, sc_true_to_grid: pass, sc_walk: fail, sc_walls: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_VISIT2_WALK_20261119.rws
exit_met: false
```
