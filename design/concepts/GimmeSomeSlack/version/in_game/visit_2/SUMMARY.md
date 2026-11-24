# GimmeSomeSlack 0.2.0 — in-game acceptance, visit 2

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_TWO_RUN_FOUR, game ArchSmall on Archmagi.
Started 2026-11-23 10:37 PM PST. 133 of 206 checks run again; 73 keep visit 1's PASS.

## Progress
- 10:37 PM precondition in_game 0.2.0 [measured]; item claimed; bridge ArchSmall taken by BENCH.
- 10:38-10:41 PM Saves of ArchSmall backed up (D:\ClaudeWork\rimmandrake\backups\saves_b_gss_020_visit2_20261123); GSS deploy dry run:
  in sync (mod_sha db7ead9f11, mod_hash sha256:c8a4aace8b18); ArchSmall relaunched on tier gimmesomeslack (12 mods, all 5 DLC);
  build_match loaded: MATCH. Offline gate red [].
- 10:49-10:55 PM runC (matrix,core,scenes): 108 PASS, 2 UNMEASURED that need FlowWorks (the next tier's rows).
- 10:55-10:59 PM runB (aerial,style,save_load,d4_save,statics): 64/64 PASS; rows written.
- 10:59-11:05 PM scenes switch_off_ends, switch_light, restyle_whole_line PASS; look_menu_icons, wall_lamp_looks PASS on program rows,
  captures read. MOD fault found by looking at sc_wall_lamp_looks close up: a near wall lamp's device plug drawn on the strip its cord
  comes from (EndDecor measured to the lamp's footprint; its cord ends in the wall cell). Test first: StubJoinChecks.NearWallLamps
  red 246 of 480, green 0 after. wall_plug_look.py (owed from the road back) repaired: it staged nothing and exited 0, and V.shot's
  crop of a reused name showed the OLD picture. Its 12 captures read: every cord leaves its wall plug straight along the stub.
- 11:06-11:23 PM full SelfTest 5811/5811, fix published 37c34e81fc, deployed to ArchSmall (mod_hash sha256:b9ab79645d45), loaded MATCH.
- 11:23-11:30 PM runC on the fixed build: 108 PASS, 2 UNMEASURED that need FlowWorks.
- 11:30-11:40 PM fixed runB 64/64; 8 scenes as they should, captures read (plug stack gone); sc_stub_joins on GSS_OWNER_LOOK_20261116
  PASS (398 taken, 0 off; md5 same before and after); gravship on PASS, off PASS.
- 11:40 PM-12:08 AM tier gimmesomeslack_flowworks; a first run was discarded: ArchSmall's FlowWorks DLL was not main's. FlowWorks deployed.
- 12:08-12:45 AM fw tier (13 mods): matrix+core 75 and scenes 31 PASS (a first scenes pass ran out of its own time limit on the 3 slow deck collapses), runF 64/64 PASS; bridge tier removal check PASS (0 errors naming the mod); T_STUB_JOINS red-seen recorded.
- 12:45-12:52 AM GSS tier again: wall_plug_look.py on the fixed build rc 0, its known-bad key rc 2; 12 captures read. Explored his
  review map (GSS_OWNER_LOOK_20261116, not saved) in 14 captures; 10 strange things, all explained or on an open ticket.

## What ran
- ArchSmall (its own install on Archmagi), RimWorld 1.6.4871. GSS deployed folder sha256:b9ab79645d45 (source 37c34e81fc) on every last row
  except sc_walk. Lists: gimmesomeslack (12 mods), gimmesomeslack_flowworks (13), bridge (10). All 5 DLC on each. Rows carry build_match.py identity.
- One mod fix in the sitting, so the first build's rows (c8a4aace8b18) are history.
- Not run: sc_walk (his full list, ArchBig's).

## Results [measured]
206 stage-6 checks: 205 PASS on their last row, 0 FAIL, 1 UNMEASURED (sc_walk: needs ArchBig and his full list). Of the 133 this visit owed: 132 PASS, 1 UNMEASURED.
- Mod wrong, fixed in the sitting (class MOD): a near wall lamp's device plug was drawn on the power strip its cord comes from (EndDecor measured to the
  lamp's footprint; its cord ends in the wall cell). Fix 37c34e81fc, bars wall_lamp_takes_looks and cords_join_stubs_on_position_and_slope. Found by
  looking at sc_wall_lamp_looks close up (program rows passed). Before/after: StubJoinChecks.NearWallLamps red 246 of 480 on db7ead9f11, 0 on the fix;
  T_STUB_JOINS red-seen recorded (fault_near_lamp_plug_on_strip.patch). It OWES its one fresh reader (fix_reviews.jsonl), the steward run that reads this visit.
- Checks wrong, repaired (class HARNESS), 37c34e81fc: wall_plug_look.py (staged no cord, exited 0) known-bad rc 2, real rc 0; V.shot (its crop of a reused name
  was the OLD picture). Both are on sc_stub_joins' row.
- No check removed.

## Owed cases from the blind challenge (cycle 1)
- RIMMANDRAKE_STEADY_SLACK_REBUILD_TAIL_BOUND_UNDER_LOAD: sc_rewire_cost PASS (P1B_perf_rebuild, A8 PASS on both tiers). The item's timing bound is in the SelfTest.
- GC_LAMP_MASTER_OFF_KEEPS_LOOK: sc_wall_lamp_looks SEES it [measured in visit 1 on a planted DLL; the check is unchanged here and reads PASS]. sc_settings would see it through S11_lamp_master_off_vanilla [guess ~80%].
- GAME_SIDE_BARS: every named scene has a PASS last row except sc_walk (UNMEASURED, ArchBig).
- FLOOR_CORD_SHAPE_BARS: sc_cords_slack, sc_junction_strips, sc_dense_tangle, sc_stub_joins, sc_no_sharp_turn, sc_no_repeat, sc_true_to_grid, sc_cords_under_items, sc_cut_ends PASS.

## Owed from the road back (unrun.jsonl)
- RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES -> sc_walk: still UNRUN (ArchBig, his full list).
- RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE -> P_M8_break_two_ends_live_dead: PASS (both tiers).
- RIMMANDRAKE_FINISH_SLACK_ICON_LAMP_CHECKS_CAPPED_AT_HALF -> sc_restyle_whole_line, sc_look_menu_icons, sc_wall_lamp_looks: PASS.
- RIMMANDRAKE_STRAIGHTEN_SLACK_CORD_WHERE_IT_LEAVES_WALL_PLUG_HE_SAW_IT_LIVE -> sc_stub_joins + wall_plug_look.py: PASS; every cord leaves its wall plug straight (12 captures).

## Savegame for his walk
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_020_VISIT1_WALK_20261123.rws` (visit 1's 31-station map and stands 32 and 33). It holds no class of the mod's, but it was not loaded on the fixed build: the full list is ArchBig's.
ArchBig's deployed GSS is still an older build (its game ran a Pyrelands visit): deploy 37c34e81fc there before sc_walk and his walk.

## The pipeline's reading of this record (maturation.py next GimmeSomeSlack, 12:54 AM PST)
Form reasons: none. Substance, unchanged: the mod fix 37c34e81fc owes its fresh reader; sc_walk is not counted (ArchBig). build_match: 206 read, 205 count, 1 to run (sc_walk).

## Game and bridge at the end
ArchSmall left running, healthy, tier gimmesomeslack, his review map loaded and not saved. Saves: only new files (14 lines), none changed. Bridge released.

## Exit
```
ingame_rows: {P_A8_same_frame_dirty_not_dropped: pass, P_B13_hidden_conduit_hookup_not_drawn: pass, P_B1_rope_settle: pass, P_B3_whip_live_ends: pass, P_B3c_spark_rides_whip: pass, P_B4b_sparks_thrown_ticking: pass, P_B4c_spark_intensity_scales_downed: pass, P_B4d_spark_budget_shared_visible_first: pass, P_B5_selection_highlight: pass, P_B6_tangle_lit_strips: pass, P_B6b_strips_dark_when_dead: pass, P_B7_ground_cords_never_sway: pass, P_B8_lod_far_zoom: pass, P_B9_cutscene_guard_idle: pass, P_D1_zero_tick_rereads_same: pass, P_D2_fresh_builder_same: pass, P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down: pass, P_GS1_keep_wires_on_gravship_on_aboard_span_flies: pass, P_M10_tangle_threshold_setting: pass, P_M11_dive_through_setting: pass, P_M12a_slide_under_off_plug_on_cell_centre: pass, P_M12b_slide_under_on_plug_off_centre: pass, P_M13a_linked_one_net_across_gap: pass, P_M13b_far_consumer_powered: pass, P_M13c_unlink_two_nets_relink_one: pass, P_M13d_refusals: pass, P_M13e_hostile_mast_not_autolinked: pass, P_M14_gap_control_without_fix: pass, P_M14a_remove_middle_both_ends_resolve: pass, P_M14b_dead_pole_drops_live_and_dead_cords: pass, P_M14c_live_tip_glows: pass, P_M15_explosion_cuts_span: pass, P_M15a_wire_down_alert_lists_cut: pass, P_M15b_restring_rejoins: pass, P_M15c_wire_down_alert_clears_on_restring: pass, P_M15d_diagonal_cut_halves_meet_on_line: pass, P_M15e_restring_is_a_colonist_job: pass, P_M15f_restring_joined_run_one_look: pass, P_M17_owner_change_cuts_cross_owner_wires: pass, P_M19_tap_drains_one_way: pass, P_M19m_tap_mixed_net_connects_own_conduit: pass, P_M19n_taps_off_control: pass, P_M1_conduit_transparent: pass, P_M1_cords_exist: pass, P_M1_node_census: pass, P_M1c_end_pieces: pass, P_M1e_machine_on_inwall_run_draws_a_cord: pass, P_M1f_machine_on_hidden_conduit_draws_none: pass, P_M20a_fallen_wire_shock_flip: pass, P_M20b_fallen_wire_knockback_flip: pass, P_M20c_fallen_wire_ignites_flip: pass, P_M20d_keep_wires_setting_roundtrip: pass, P_M20e_shock_cells_die_with_wire: pass, P_M21a_cut_wires_on_owner_change_off_keeps_link: pass, P_M21b_cut_wires_on_owner_change_on_cuts_link: pass, P_M21c_drip_loops_off_plain_curve: pass, P_M21d_drip_loops_on_loop_samples: pass, P_M21e_keep_wires_on_gravship_off_setting_state: pass, P_M21f_keep_wires_on_gravship_on_setting_state: pass, P_M22a_kinetic_sway_on_swings_never_cuts: pass, P_M22b_kinetic_sway_off_does_nothing: pass, P_M2_cords_only_within_net: pass, P_M2b_no_vertex_unwalkable: pass, P_M2c_no_sharp_bends: pass, P_M5_local_invalidation: pass, P_M6_overlay_lines_intact: pass, P_M7_off_restores_vanilla: pass, P_M7b_on_again_invisible: pass, P_M8_break_two_ends_live_dead: pass, P_M8c_source_off_reads_dead_250: pass, P_MX_A04_N3_R12_fallen: pass, P_MX_A05_N3_R19_up: pass, P_MX_A06_N5_R6_fallen: pass, P_MX_A07_N5_R12_up: pass, P_MX_A08_N5_R19_cut: pass, P_MX_A09_N2_R6_cut: pass, P_MX_A10_N2_R12_fallen: pass, P_MX_A11_N2_R19_up: pass, P_MX_A12_N3_R6_fallen: pass, P_MX_C00_empty: pass, P_MX_D00_n1_S0: pass, P_MX_D05_n10_S1: pass, P_MX_D10_n100_S2: pass, P_MX_D15_n1000_S3: pass, P_MX_F00_T0_S0: pass, P_MX_F04_T1_S0: pass, P_MX_F11_T2_S3: pass, P_MX_F13_T3_S1: pass, P_MX_F18_T4_S2: pass, P_MX_F21_T5_S1: pass, P_MX_F25_T6_S1: pass, P_MX_F30_T7_S2: pass, P_MX_F33_T8_S1: pass, P_MX_F39_T9_S3: pass, P_MX_F42_T10_S2: pass, P_MX_F47_T11_S3: pass, P_MX_F51_T12_S3: pass, P_MX_F54_T13_S2: pass, P_MX_F56_T14_S0: pass, P_MX_F60_T15_S0: pass, P_P1B_perf_rebuild: pass, P_R1_span_altitude_above_pawns_below_blueprints: pass, P_R2_spans_and_heads_drawn: pass, P_R3_sway_proxy: pass, P_R3b_sway_looks_each_draw: pass, P_S10_legacy_default_materials: pass, P_S11_lamp_master_off_vanilla: pass, P_S12a_D1_legacy_run_one_look: pass, P_S12b_D7_bulk_spawn_cost: pass, P_S12c_D5_multilink_one_frame: pass, P_S12d_D4_pending_queue_save: pass, P_S12e_batched_links_merge: pass, P_S1_pick_reaches_blueprint: pass, P_S2_blueprint_frame_building: pass, P_S3_god_mode: pass, P_S4_copy_carries_look: pass, P_S5_reinstall_keeps_look: pass, P_S6_spans_in_pole_look: pass, P_S7_save_load_styles: pass, P_S8_legacy_unstyled_draws_default: pass, P_S8b_legacy_joined_to_styled_stores_look: pass, P_S9a_two_runs_two_styles: pass, P_S9b_bridge_largest_wins: pass, P_S9c_split_keeps_styles: pass, P_S9d_restyle_and_materials: pass, P_SC_bend_draws_no_joint_tee_draws_one: pass, P_SC_box_stub_slope: pass, P_SC_cord_end_one_kind: pass, P_SC_cords_all_slack: pass, P_SC_cut_battery_each_side_both_live: pass, P_SC_cut_never_powered_both_dead: pass, P_SC_dead_wire_lights_no_fuel: pass, P_SC_dead_wire_shocks_nobody: pass, P_SC_doorway_run_is_one_cord: pass, P_SC_floor_end_bites_aerial_master_off: pass, P_SC_floor_end_cord_behind_spares: pass, P_SC_floor_end_dead_spares: pass, P_SC_floor_end_every_end_over_spark_budget: pass, P_SC_floor_end_fixer_spared_other_builder_shocked: pass, P_SC_floor_end_live_shocks: pass, P_SC_floor_end_unfinished_run_bites: pass, P_SC_no_two_cords_alike: pass, P_SC_restring_drafted_no_job: pass, P_SC_restring_work_scheduler_takes_it: pass, P_SC_shock_reach_deck_cord_per_value: pass, P_SC_shock_reach_default_all: pass, P_SC_shock_reach_three_values: pass, P_SC_sparse_room_no_tangle: pass, P_SC_splicer_spared_bystander_shocked: pass, P_SC_statics_clear_between_games: pass, P_SC_under_battery_dry: pass, P_SC_under_furniture_dry: pass, P_SC_under_item_stack_dry: pass, P_SC_under_junction_piece_dry: pass, P_SC_under_liquid_pit: pass, P_SL1_save_landed_new_file_only: pass, P_SL2_save_names_no_class_of_ours: pass, P_SL3_after_load_census_equal: pass, P_ST1_styles_textures_load: pass, P_ST2_switch_changes_textures: pass, P_ST3_extcord_colour_modes: pass, P_ST4_settings_roundtrip: pass, P_ST5_restore_default_and_master: pass, P_SW1_highlight_off_draws_no_ring: pass, P_SW2_lod_off_far_zoom_draws_full: pass, P_SW3_break_readout_off_no_glow_no_whip: pass, P_SW4_sparks_only_overlay_shut_no_glow: pass, P_SW5_hide_hookup_off_leaves_vanilla_wire: pass, P_SW6_needless_loops_off_reaches_builder: pass, P_Z_log_budget: pass, sc_conduit_invisible: pass, sc_cords_slack: pass, sc_cords_under_items: pass, sc_cut_ends: pass, sc_dense_tangle: pass, sc_fallen_span: pass, sc_floor_end_shock: pass, sc_four_looks: pass, sc_fuel_ignition: pass, sc_gravship: pass, sc_junction_strips: pass, sc_look_menu_icons: pass, sc_no_repeat: pass, sc_no_roof_over_pole: pass, sc_no_sharp_turn: pass, sc_owner_change: pass, sc_pole_icons_loaded: pass, sc_pole_south_of_tree: pass, sc_removal_consequence: pass, sc_restring: pass, sc_restyle_whole_line: pass, sc_rewire_cost: pass, sc_settings: pass, sc_shock: pass, sc_shock_reach: pass, sc_shock_restring: pass, sc_spans: pass, sc_statics_new_game: pass, sc_stub_joins: pass, sc_switch_light: pass, sc_switch_off_ends: pass, sc_tap_theft: pass, sc_true_to_grid: pass, sc_walk: unmeasured, sc_wall_lamp_looks: pass, sc_walls: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_020_VISIT1_WALK_20261123.rws
exit_met: false
```
