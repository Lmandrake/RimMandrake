# GimmeSomeSlack 0.2.0: the live scenes sorted into kind A, B or C (proposal)

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`, 2026-11-23. The rule:
`design/RimMandrake/standing_rulings.md` §Live tests have three kinds. The Conductor decides; no test table was changed.

- Read: `version/test_table.json` (the record behind `test_table.md`) and every recorded row of the in-game visits of 0.1.0 and 0.1.1; version 0.2.0 has no row yet.
- A scene with no record of a spoiled run (a run that something outside the tested behaviour spoiled) is kind A. Where a
  reason below is only a count of rows, I read the row's own fields (cut at 430 characters) and the visit summaries, not every evidence file.
- Count of 206 scenes: A 206, B 0, C 0 scenes.

## Scenes

| scene | proposed kind | reason |
|---|---|---|
| `sc_conduit_invisible` | A | 6 recorded rows, all PASS. |
| `sc_cords_slack` | A | 6 recorded rows, all PASS. |
| `sc_no_sharp_turn` | A | 6 recorded rows, all PASS. |
| `sc_walls` | A | 2 of 7 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_junction_strips` | A | 6 recorded rows, all PASS. |
| `sc_dense_tangle` | A | 6 recorded rows, all PASS. |
| `sc_no_repeat` | A | 6 recorded rows, all PASS. |
| `sc_true_to_grid` | A | 4 of 9 rows not PASS (no class 4); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_cords_under_items` | A | 2 of 7 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_cut_ends` | A | 4 of 9 rows not PASS (no class 4); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_rewire_cost` | A | 2 of 7 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_spans` | A | 6 recorded rows, all PASS. |
| `sc_fallen_span` | A | 6 recorded rows, all PASS. |
| `sc_shock` | A | 6 recorded rows, all PASS. |
| `sc_floor_end_shock` | A | 1 of 6 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_shock_reach` | A | 2 of 7 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_restring` | A | 6 recorded rows, all PASS. |
| `sc_tap_theft` | A | 6 recorded rows, all PASS. |
| `sc_four_looks` | A | 1 of 7 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_settings` | A | 6 recorded rows, all PASS. |
| `sc_gravship` | A | 6 recorded rows, all PASS. |
| `sc_walk` | A | Non-PASS rows are the mod's, the script's, or COULD NOT LOOK (ArchSmall cannot hold his full list). |
| `sc_shock_restring` | A | 6 recorded rows, all PASS. |
| `sc_owner_change` | A | 6 recorded rows, all PASS. |
| `sc_fuel_ignition` | A | 6 recorded rows, all PASS. |
| `sc_statics_new_game` | A | 6 recorded rows, all PASS. |
| `sc_removal_consequence` | A | 6 recorded rows, all PASS. |
| `sc_stub_joins` | A | 1 of 6 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_switch_off_ends` | A | 3 recorded rows, all PASS. |
| `sc_pole_icons_loaded` | A | 2 recorded rows, all PASS. |
| `sc_pole_south_of_tree` | A | 1 of 3 rows not PASS (LOOK 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_no_roof_over_pole` | A | 1 of 4 rows not PASS (HARNESS 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_switch_light` | A | 2 recorded rows, all PASS. |
| `sc_restyle_whole_line` | A | no run on record; nothing shows a spoiled run. |
| `sc_look_menu_icons` | A | no run on record; nothing shows a spoiled run. |
| `sc_wall_lamp_looks` | A | no run on record; nothing shows a spoiled run. |
| `P_MX_D00_n1_S0` | A | 13 recorded rows, all PASS. |
| `P_MX_D05_n10_S1` | A | 13 recorded rows, all PASS. |
| `P_MX_D10_n100_S2` | A | 13 recorded rows, all PASS. |
| `P_MX_D15_n1000_S3` | A | 13 recorded rows, all PASS. |
| `P_MX_C00_empty` | A | 13 recorded rows, all PASS. |
| `P_MX_F00_T0_S0` | A | 13 recorded rows, all PASS. |
| `P_MX_F04_T1_S0` | A | 13 recorded rows, all PASS. |
| `P_MX_F11_T2_S3` | A | 13 recorded rows, all PASS. |
| `P_MX_F13_T3_S1` | A | 13 recorded rows, all PASS. |
| `P_MX_F18_T4_S2` | A | 13 recorded rows, all PASS. |
| `P_MX_F21_T5_S1` | A | 13 recorded rows, all PASS. |
| `P_MX_F25_T6_S1` | A | 13 recorded rows, all PASS. |
| `P_MX_F30_T7_S2` | A | 13 recorded rows, all PASS. |
| `P_MX_F33_T8_S1` | A | 13 recorded rows, all PASS. |
| `P_MX_F39_T9_S3` | A | 13 recorded rows, all PASS. |
| `P_MX_F42_T10_S2` | A | 13 recorded rows, all PASS. |
| `P_MX_F47_T11_S3` | A | 13 recorded rows, all PASS. |
| `P_MX_F51_T12_S3` | A | 13 recorded rows, all PASS. |
| `P_MX_F54_T13_S2` | A | 13 recorded rows, all PASS. |
| `P_MX_F56_T14_S0` | A | 13 recorded rows, all PASS. |
| `P_MX_F60_T15_S0` | A | 13 recorded rows, all PASS. |
| `P_MX_A04_N3_R12_fallen` | A | 13 recorded rows, all PASS. |
| `P_MX_A05_N3_R19_up` | A | 13 recorded rows, all PASS. |
| `P_MX_A06_N5_R6_fallen` | A | 13 recorded rows, all PASS. |
| `P_MX_A07_N5_R12_up` | A | 13 recorded rows, all PASS. |
| `P_MX_A08_N5_R19_cut` | A | 13 recorded rows, all PASS. |
| `P_MX_A09_N2_R6_cut` | A | 13 recorded rows, all PASS. |
| `P_MX_A10_N2_R12_fallen` | A | 13 recorded rows, all PASS. |
| `P_MX_A11_N2_R19_up` | A | 13 recorded rows, all PASS. |
| `P_MX_A12_N3_R6_fallen` | A | 13 recorded rows, all PASS. |
| `P_M1_conduit_transparent` | A | 15 recorded rows, all PASS. |
| `P_M1_cords_exist` | A | 15 recorded rows, all PASS. |
| `P_M1_node_census` | A | 2 of 15 rows not PASS (MOD 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_M1c_end_pieces` | A | 15 recorded rows, all PASS. |
| `P_M2b_no_vertex_unwalkable` | A | 15 recorded rows, all PASS. |
| `P_M2c_no_sharp_bends` | A | 15 recorded rows, all PASS. |
| `P_M6_overlay_lines_intact` | A | 15 recorded rows, all PASS. |
| `P_M5_local_invalidation` | A | 15 recorded rows, all PASS. |
| `P_M8_break_two_ends_live_dead` | A | 10 of 23 rows not PASS (MOD 10); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_M2_cords_only_within_net` | A | 15 recorded rows, all PASS. |
| `P_B1_rope_settle` | A | 15 recorded rows, all PASS. |
| `P_B6_tangle_lit_strips` | A | 15 recorded rows, all PASS. |
| `P_B3c_spark_rides_whip` | A | 15 recorded rows, all PASS. |
| `P_B3_whip_live_ends` | A | 15 recorded rows, all PASS. |
| `P_SW3_break_readout_off_no_glow_no_whip` | A | 15 recorded rows, all PASS. |
| `P_SW4_sparks_only_overlay_shut_no_glow` | A | 15 recorded rows, all PASS. |
| `P_B4b_sparks_thrown_ticking` | A | 15 recorded rows, all PASS. |
| `P_B4c_spark_intensity_scales_downed` | A | 15 recorded rows, all PASS. |
| `P_B4d_spark_budget_shared_visible_first` | A | 2 of 15 rows not PASS (MOD 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_M1e_machine_on_inwall_run_draws_a_cord` | A | 15 recorded rows, all PASS. |
| `P_M1f_machine_on_hidden_conduit_draws_none` | A | 15 recorded rows, all PASS. |
| `P_B7_ground_cords_never_sway` | A | 15 recorded rows, all PASS. |
| `P_B5_selection_highlight` | A | 15 recorded rows, all PASS. |
| `P_SW1_highlight_off_draws_no_ring` | A | 15 recorded rows, all PASS. |
| `P_SW2_lod_off_far_zoom_draws_full` | A | 15 recorded rows, all PASS. |
| `P_B8_lod_far_zoom` | A | 15 recorded rows, all PASS. |
| `P_B9_cutscene_guard_idle` | A | 15 recorded rows, all PASS. |
| `P_B6b_strips_dark_when_dead` | A | 15 recorded rows, all PASS. |
| `P_M10_tangle_threshold_setting` | A | 15 recorded rows, all PASS. |
| `P_M11_dive_through_setting` | A | 15 recorded rows, all PASS. |
| `P_M12a_slide_under_off_plug_on_cell_centre` | A | 15 recorded rows, all PASS. |
| `P_M12b_slide_under_on_plug_off_centre` | A | 15 recorded rows, all PASS. |
| `P_B13_hidden_conduit_hookup_not_drawn` | A | 15 recorded rows, all PASS. |
| `P_SW5_hide_hookup_off_leaves_vanilla_wire` | A | 15 recorded rows, all PASS. |
| `P_SW6_needless_loops_off_reaches_builder` | A | 15 recorded rows, all PASS. |
| `P_P1B_perf_rebuild` | A | 15 recorded rows, all PASS. |
| `P_A8_same_frame_dirty_not_dropped` | A | 15 recorded rows, all PASS. |
| `P_ST1_styles_textures_load` | A | 15 recorded rows, all PASS. |
| `P_ST2_switch_changes_textures` | A | 15 recorded rows, all PASS. |
| `P_ST3_extcord_colour_modes` | A | 15 recorded rows, all PASS. |
| `P_ST4_settings_roundtrip` | A | 15 recorded rows, all PASS. |
| `P_ST5_restore_default_and_master` | A | 15 recorded rows, all PASS. |
| `P_M8c_source_off_reads_dead_250` | A | 15 recorded rows, all PASS. |
| `P_M7_off_restores_vanilla` | A | 15 recorded rows, all PASS. |
| `P_M7b_on_again_invisible` | A | 15 recorded rows, all PASS. |
| `P_M13a_linked_one_net_across_gap` | A | 12 recorded rows, all PASS. |
| `P_M13b_far_consumer_powered` | A | 12 recorded rows, all PASS. |
| `P_M13c_unlink_two_nets_relink_one` | A | 12 recorded rows, all PASS. |
| `P_M13d_refusals` | A | 12 recorded rows, all PASS. |
| `P_M13e_hostile_mast_not_autolinked` | A | 12 recorded rows, all PASS. |
| `P_R1_span_altitude_above_pawns_below_blueprints` | A | 12 recorded rows, all PASS. |
| `P_R2_spans_and_heads_drawn` | A | 12 recorded rows, all PASS. |
| `P_M14_gap_control_without_fix` | A | 12 recorded rows, all PASS. |
| `P_M14a_remove_middle_both_ends_resolve` | A | 12 recorded rows, all PASS. |
| `P_M14b_dead_pole_drops_live_and_dead_cords` | A | 12 recorded rows, all PASS. |
| `P_M14c_live_tip_glows` | A | 12 recorded rows, all PASS. |
| `P_M15_explosion_cuts_span` | A | 12 recorded rows, all PASS. |
| `P_M15a_wire_down_alert_lists_cut` | A | 12 recorded rows, all PASS. |
| `P_M15b_restring_rejoins` | A | 12 recorded rows, all PASS. |
| `P_M15c_wire_down_alert_clears_on_restring` | A | 12 recorded rows, all PASS. |
| `P_M15e_restring_is_a_colonist_job` | A | 12 recorded rows, all PASS. |
| `P_M15f_restring_joined_run_one_look` | A | 12 recorded rows, all PASS. |
| `P_M15d_diagonal_cut_halves_meet_on_line` | A | 12 recorded rows, all PASS. |
| `P_R3_sway_proxy` | A | 12 recorded rows, all PASS. |
| `P_R3b_sway_looks_each_draw` | A | 6 recorded rows, all PASS. |
| `P_M19_tap_drains_one_way` | A | 12 recorded rows, all PASS. |
| `P_M19n_taps_off_control` | A | 12 recorded rows, all PASS. |
| `P_M19m_tap_mixed_net_connects_own_conduit` | A | 12 recorded rows, all PASS. |
| `P_M17_owner_change_cuts_cross_owner_wires` | A | 12 recorded rows, all PASS. |
| `P_M20a_fallen_wire_shock_flip` | A | 12 recorded rows, all PASS. |
| `P_M20b_fallen_wire_knockback_flip` | A | 12 recorded rows, all PASS. |
| `P_M20c_fallen_wire_ignites_flip` | A | 12 recorded rows, all PASS. |
| `P_M20e_shock_cells_die_with_wire` | A | 12 recorded rows, all PASS. |
| `P_M20d_keep_wires_setting_roundtrip` | A | 12 recorded rows, all PASS. |
| `P_M21a_cut_wires_on_owner_change_off_keeps_link` | A | 12 recorded rows, all PASS. |
| `P_M21b_cut_wires_on_owner_change_on_cuts_link` | A | 12 recorded rows, all PASS. |
| `P_M21c_drip_loops_off_plain_curve` | A | 12 recorded rows, all PASS. |
| `P_M21d_drip_loops_on_loop_samples` | A | 12 recorded rows, all PASS. |
| `P_M22a_kinetic_sway_on_swings_never_cuts` | A | 12 recorded rows, all PASS. |
| `P_M22b_kinetic_sway_off_does_nothing` | A | 12 recorded rows, all PASS. |
| `P_M21e_keep_wires_on_gravship_off_setting_state` | A | 12 recorded rows, all PASS. |
| `P_M21f_keep_wires_on_gravship_on_setting_state` | A | 12 recorded rows, all PASS. |
| `P_S1_pick_reaches_blueprint` | A | 12 recorded rows, all PASS. |
| `P_S2_blueprint_frame_building` | A | 12 recorded rows, all PASS. |
| `P_S3_god_mode` | A | 12 recorded rows, all PASS. |
| `P_S4_copy_carries_look` | A | 12 recorded rows, all PASS. |
| `P_S5_reinstall_keeps_look` | A | 12 recorded rows, all PASS. |
| `P_S8_legacy_unstyled_draws_default` | A | 12 recorded rows, all PASS. |
| `P_S8b_legacy_joined_to_styled_stores_look` | A | 12 recorded rows, all PASS. |
| `P_S6_spans_in_pole_look` | A | 12 recorded rows, all PASS. |
| `P_S9a_two_runs_two_styles` | A | 12 recorded rows, all PASS. |
| `P_S9b_bridge_largest_wins` | A | 12 recorded rows, all PASS. |
| `P_S9c_split_keeps_styles` | A | 12 recorded rows, all PASS. |
| `P_S9d_restyle_and_materials` | A | 12 recorded rows, all PASS. |
| `P_S10_legacy_default_materials` | A | 12 recorded rows, all PASS. |
| `P_S11_lamp_master_off_vanilla` | A | 12 recorded rows, all PASS. |
| `P_S12a_D1_legacy_run_one_look` | A | 12 recorded rows, all PASS. |
| `P_S12b_D7_bulk_spawn_cost` | A | 12 recorded rows, all PASS. |
| `P_S12c_D5_multilink_one_frame` | A | 12 recorded rows, all PASS. |
| `P_S12e_batched_links_merge` | A | 12 recorded rows, all PASS. |
| `P_S7_save_load_styles` | A | 10 recorded rows, all PASS. |
| `P_S12d_D4_pending_queue_save` | A | 1 of 11 rows not PASS (HARNESS 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_SC_doorway_run_is_one_cord` | A | 12 recorded rows, all PASS. |
| `P_SC_cut_never_powered_both_dead` | A | 12 recorded rows, all PASS. |
| `P_SC_cut_battery_each_side_both_live` | A | 12 recorded rows, all PASS. |
| `P_SC_bend_draws_no_joint_tee_draws_one` | A | 12 recorded rows, all PASS. |
| `P_SC_sparse_room_no_tangle` | A | 12 recorded rows, all PASS. |
| `P_SC_cords_all_slack` | A | 11 recorded rows, all PASS. |
| `P_SC_no_two_cords_alike` | A | 11 recorded rows, all PASS. |
| `P_SC_restring_drafted_no_job` | A | 12 recorded rows, all PASS. |
| `P_SC_restring_work_scheduler_takes_it` | A | 12 recorded rows, all PASS. |
| `P_SC_splicer_spared_bystander_shocked` | A | 12 recorded rows, all PASS. |
| `P_SC_dead_wire_shocks_nobody` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_live_shocks` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_dead_spares` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_cord_behind_spares` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_unfinished_run_bites` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_bites_aerial_master_off` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_every_end_over_spark_budget` | A | 12 recorded rows, all PASS. |
| `P_SC_floor_end_fixer_spared_other_builder_shocked` | A | 1 of 12 rows not PASS (HARNESS 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_SC_shock_reach_default_all` | A | 12 recorded rows, all PASS. |
| `P_SC_shock_reach_three_values` | A | 12 recorded rows, all PASS. |
| `P_SC_shock_reach_deck_cord_per_value` | A | UNMEASURED twice because FlowWorks was not loaded (staging). Runs on tier gimmesomeslack_flowworks. |
| `P_SC_dead_wire_lights_no_fuel` | A | 12 recorded rows, all PASS. |
| `P_SC_under_battery_dry` | A | 12 recorded rows, all PASS. |
| `P_SC_under_item_stack_dry` | A | 1 of 12 rows not PASS (MOD 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_SC_under_furniture_dry` | A | 1 of 12 rows not PASS (MOD 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_SC_under_junction_piece_dry` | A | 1 of 12 rows not PASS (MOD 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_SC_under_liquid_pit` | A | UNMEASURED because FlowWorks was not loaded (staging). Runs on tier gimmesomeslack_flowworks. |
| `P_SC_cord_end_one_kind` | A | 12 recorded rows, all PASS. |
| `P_SC_box_stub_slope` | A | 12 recorded rows, all PASS. |
| `P_D1_zero_tick_rereads_same` | A | 13 recorded rows, all PASS. |
| `P_D2_fresh_builder_same` | A | 1 of 13 rows not PASS (MOD 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_SL1_save_landed_new_file_only` | A | 10 recorded rows, all PASS. |
| `P_SL2_save_names_no_class_of_ours` | A | 10 recorded rows, all PASS. |
| `P_SL3_after_load_census_equal` | A | 10 recorded rows, all PASS. |
| `P_Z_log_budget` | A | FAILs of 0.1.0 and 0.1.1 are one error of another mod (FlowWorks RM_PitAccess.cs:277, open item RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR). The control is a tier with no FlowWorks or the named fix. |
| `P_SC_statics_clear_between_games` | A | 11 recorded rows, all PASS. |
| `P_GS1_keep_wires_on_gravship_on_aboard_span_flies` | A | 6 recorded rows, all PASS. |
| `P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down` | A | 6 recorded rows, all PASS. |

## Hunt candidates (kind C, never a table scene)

- None. No unexplained failure is on record for 0.2.0, which has no visit record yet (its first visit is running).
