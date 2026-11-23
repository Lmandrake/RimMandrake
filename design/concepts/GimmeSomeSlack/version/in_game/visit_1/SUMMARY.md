# GimmeSomeSlack 0.2.0 — in-game acceptance, visit 1

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE_RUN_THREE, game ArchBig on Archmagi.
Started 2026-11-23 1:14 PM PST.

## Progress
- 1:14 PM precondition in_game 0.2.0 [measured]; item claimed; bridge ArchBig taken by BENCH; skeleton written.
- 1:15 PM ArchBig found cold-loading his full list (315 mods, started 1:11 PM, bridge free). GSS deploy dry run: in sync
  (378 files; DLL sha256 fe67c9ef = its .srchash). Saves backed up (661 .rws, 8.2 GB) to
  D:\ClaudeWork\rimmandrake\backups\saves_a_gss_020_visit1_20261123, with MANIFEST_before.txt.
- 1:22-1:31 PM offline gate: red O6_review_round1. Class HARNESS: its 'fire hose' sweep reads selftest_gss_no_hose.py's
  planted text (added 650bdab37b). O6 decides sc_spans and sc_four_looks, so it was repaired: the sweep skips selftest_*
  files. Planted (a def description with 'fire hose') FAIL; real PASS (evidence/o6_check.py).
- 1:32 PM ArchBig at the main menu. build_match identity --full: 314 of 315 listed mods present, mod_sha cf5a867a53, mod_hash
  sha256:a9e908d1ed3e, game 1.6.4871 rev590 (evidence/identity_full.json). Offline gate rerun after the O6 repair: red []
  (evidence/offline_gate.json).
- 1:33-1:37 PM review map built on a full-list quicktest (31 stations, 62 labels, 31 sign books, 5 non-colonists swept), plus
  two 0.2.0 stands by the scenes' own verbs (stand_020.py: 32 one line with every piece, 33 wall lamps); saved as
  GSS_020_VISIT1_WALK_20261123.rws (one new file, none changed).
- 1:38-1:40 PM sc_walk PASS on his full list (cords, soak 8 blasts, ui 24/24, save_reload_b 7/7).
- 1:41-1:43 PM walk save reloaded: master off reads vanilla conduit and lamp art with no cord layer, on reads both back
  (evidence/full_master_off_on.json); stations captured and looked at.
- 1:44 PM relaunched on tier gimmesomeslack (12 mods, all 5 DLC), bridge up 25 s; runC and runB started.
- 1:45-1:54 PM first pass on the tier (build a9e908d1ed3e): runC 108 PASS + 2 UNMEASURED (FlowWorks), runB 64/64, seven
  one-off scenes: 6 as they should, sc_restyle_whole_line FAIL on SC_restyle_cut_span_ends_line. Class SITE: the first pole
  auto-linked to the bracket too, so cutting the poles' span left the line whole. Repaired (that wire is taken down, read
  back); the fake game now auto-links as the mod does, and reads the old scene FAIL and the repaired one PASS.
- 1:42-2:06 PM MOD fault found by looking at stand 33 (wall lamps): the device plug of a lamp on the far side of a wall was
  drawn on the wall plate, and the cord left the wall plug 39-48 degrees off its slope (visible in Modern). Two causes in
  CordBuilder.cs: EndDecor's tie picked the dive end as the machine's end; FitEnds and UnkinkPiece skipped dive ends. Test
  first (StubJoinChecks.FarWallLamps, 240 scenes): red on the parent (240 of 240 plugs away from their lamp, 6 joins off),
  green after (0, 0). Full SelfTest 5803/5803. Every check runs again on the fixed build.
- 2:07-2:13 PM fix and repairs published (01c8191ac9), deployed to ArchBig (mod_hash sha256:18fde3975f10), ArchBig relaunched
  on tier gimmesomeslack. All rows below are on this build.
- 2:14-2:22 PM runC 108 PASS + 2 UNMEASURED that need FlowWorks (left out of its rows); runB 62/62; scenes switch_off_ends,
  pole_icons_loaded, no_roof_over_pole, switch_light, restyle_whole_line PASS; look_menu_icons, wall_lamp_looks,
  pole_south_of_tree PASS on their program rows with captures read. joins on the wall lamp scene: 29 taken, 0 off, 0 bare.
- 2:22-2:27 PM gravship on PASS, off PASS. 2:30 PM sc_look_menu_icons capture repaired (b4a2b18daf). 2:33 PM sc_stub_joins on
  GSS_OWNER_LOOK_20261116 (md5 a1c76e27c41e before and after): PASS, 398 taken, 0 off line, 0 off slope.
- 2:42-2:59 PM tier gimmesomeslack_flowworks (13 mods): runE 110/110, runF 62/62, P_Z_log_budget PASS on both.
- 3:00 PM tier bridge (10 mods, no GSS): removal check on RM_gss_proof_20261123142054 PASS (0 errors naming the mod).
- 3:02-3:06 PM planted GC_LAMP_MASTER_OFF_KEEPS_LOOK (faulted DLL built and deployed): sc_wall_lamp_looks FAIL
  (SC_wall_lamp_master_off_vanilla: 8 wall lamps keep their look). Real DLL put back, hash read back as 18fde3975f10.
- 3:10 PM red-seen recorded: T_STUB_JOINS (fault_far_lamp_plug_on_plate.patch), T_LOOK_SCENES_FAKE_GAME
  (fault_look_scenes_leaves_autolink.patch). Offline gate rerun on the fixed source: red [] (offline_gate_fixed.json).
- 3:23-3:30 PM his full list (315 listed, 314 present): review map and stands built, sc_walk PASS on the fixed build.
- 3:30-3:34 PM master off/on on the full list reads vanilla art and no cord layer, then both back. The first walk save (arid
  map) loaded and looked at on the fixed build; the second map rolled a giant-fungus tile, so it is not the walk save.
- 3:35 PM bridge ArchBig released.

## What ran
- ArchBig (Steam's install on Archmagi), RimWorld 1.6.4871 rev590. GSS deployed folder sha256:18fde3975f10 (source
  01c8191ac9) on every last row. One mod fix in the sitting, so every check ran again on the fixed build; the rows of the
  first build (a9e908d1ed3e) stay as history and count for nothing.
- Lists: gimmesomeslack (12 mods), gimmesomeslack_flowworks (13; the 4 scenes the table puts there), bridge (10, no GSS),
  his full list (315 listed, koth.isid not installed). All 5 DLC on each. Each row carries build_match.py identity.

## Results [measured]
206 stage-6 checks: 206 PASS on their last row, 0 FAIL, 0 UNMEASURED.
- Mod wrong, fixed in the sitting (class MOD): RIMMANDRAKE_SEAT_SLACK_FAR_LAMP_PLUG_DREW_ON_WALL_PLATE, 01c8191ac9. A wall lamp
  on the far side of a wall drew its plug on the wall plate its cord comes through by, and dive ends lost the wall fitting's
  slope (39-48 degrees in Modern). Bars cords_join_stubs_on_position_and_slope and wall_lamp_takes_looks. It was found by
  looking at stand 33 and at the picture of sc_wall_lamp_looks, whose program rows had passed; that read is the FAIL row (MOD). Before/after test: StubJoinChecks.FarWallLamps (selftest_gimmesomeslack.py
  --joins-only), red on the parent (240 of 240 plugs, 6 joins), green 11/11. Screenshots modern_wall_plug_BEFORE_fix.jpg and
  modern_wall_plug_AFTER_fix.jpg. It OWES its one fresh reader (fix_reviews.jsonl), the steward run that reads this visit;
  the block says exit_met true for the driver's part, and maturation.py next reads it not met for that one reason until the reader writes `sound`.
- Scene wrong, repaired (class SITE): sc_restyle_whole_line, 01c8191ac9. Known-bad state FAIL, real build PASS.
- Checks wrong, repaired (class HARNESS): O6_review_round1, an input of sc_spans and sc_four_looks, 4c5fa9da13 (planted FAIL,
  real PASS); the capture of sc_look_menu_icons, b4a2b18daf.
- sc_look_menu_icons, limit of the read: the look menu itself was not held open on screen. The program read the picture of each
  of its 150 entries (PASS); the four pictures were read off the Restyle button in the game.
- Reads by eye (sc_look_menu_icons, sc_wall_lamp_looks, sc_pole_south_of_tree) are this run's. This run made the plug fix, not
  the looks, the icons or the pole order.
- sc_dense_tangle and sc_four_looks PASS on their scripted reads; no judge agent ran (this helper starts none).
- No check removed.

## Owed cases from the blind challenge (cycle 1)
- RIMMANDRAKE_STEADY_SLACK_REBUILD_TAIL_BOUND_UNDER_LOAD: sc_rewire_cost PASS in the game (P1B_perf_rebuild and A8 PASS on both
  tiers). The item's change is in the SelfTest's timing rows; the game has no such rows.
- GC_LAMP_MASTER_OFF_KEEPS_LOOK: sc_wall_lamp_looks SEES it [measured, planted build: FAIL]. sc_settings was not run on the
  planted build; it reads standing lamps' vanilla art through S11_lamp_master_off_vanilla (guess ~80% it would see it too).
- GAME_SIDE_BARS: each named scene has a PASS last row: sc_conduit_invisible, sc_restring, sc_statics_new_game,
  sc_removal_consequence, sc_floor_end_shock, sc_fuel_ignition, sc_shock_reach, sc_cords_under_items, sc_switch_off_ends,
  sc_pole_icons_loaded, sc_pole_south_of_tree, sc_no_roof_over_pole, sc_switch_light, sc_look_menu_icons, sc_wall_lamp_looks, sc_walk.
- FLOOR_CORD_SHAPE_BARS: sc_cords_slack, sc_junction_strips, sc_dense_tangle, sc_stub_joins, sc_no_sharp_turn, sc_no_repeat,
  sc_true_to_grid, sc_cords_under_items, sc_cut_ends: PASS. Note the mod fault above is in one of these bars, outside sc_stub_joins' map.

## Owed from the road back (unrun.jsonl)
- RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES -> sc_walk: PASS on his full list (live == fresh at every step).
- RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE -> P_M8_break_two_ends_live_dead: PASS (runC and runE).
- RIMMANDRAKE_FINISH_SLACK_ICON_LAMP_CHECKS_CAPPED_AT_HALF -> sc_restyle_whole_line, sc_look_menu_icons, sc_wall_lamp_looks: PASS.

## The pipeline's reading of this record (maturation.py next GimmeSomeSlack, 3:38 PM PST)
One reason stays, of substance: sc_wall_lamp_looks' mod fix 01c8191ac9 owes its fresh reader (fix_reviews.jsonl). Form reasons:
none. build_match.py check: 206 cases read, 206 count, 0 to run.

## Savegame for his walk
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_020_VISIT1_WALK_20261123.rws`
(md5 1d835b0e741c, sign sidecar beside it): the 31-station labelled review map on his full list, plus stand 32 (one line, every
piece) and stand 33 (wall lamps in the four looks). Made on the first build, loaded and looked at on the fixed build (the save
holds no class of the mod's). Saves diff against MANIFEST_before.txt: new files only, none changed. His keepers are untouched.

## Game and bridge at the end
ArchBig left running, healthy and paused, his full list, the walk save loaded. Bridge released.

## Exit
```
ingame_rows: {P_A8_same_frame_dirty_not_dropped: pass, P_B13_hidden_conduit_hookup_not_drawn: pass, P_B1_rope_settle: pass, P_B3_whip_live_ends: pass, P_B3c_spark_rides_whip: pass, P_B4b_sparks_thrown_ticking: pass, P_B4c_spark_intensity_scales_downed: pass, P_B4d_spark_budget_shared_visible_first: pass, P_B5_selection_highlight: pass, P_B6_tangle_lit_strips: pass, P_B6b_strips_dark_when_dead: pass, P_B7_ground_cords_never_sway: pass, P_B8_lod_far_zoom: pass, P_B9_cutscene_guard_idle: pass, P_D1_zero_tick_rereads_same: pass, P_D2_fresh_builder_same: pass, P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down: pass, P_GS1_keep_wires_on_gravship_on_aboard_span_flies: pass, P_M10_tangle_threshold_setting: pass, P_M11_dive_through_setting: pass, P_M12a_slide_under_off_plug_on_cell_centre: pass, P_M12b_slide_under_on_plug_off_centre: pass, P_M13a_linked_one_net_across_gap: pass, P_M13b_far_consumer_powered: pass, P_M13c_unlink_two_nets_relink_one: pass, P_M13d_refusals: pass, P_M13e_hostile_mast_not_autolinked: pass, P_M14_gap_control_without_fix: pass, P_M14a_remove_middle_both_ends_resolve: pass, P_M14b_dead_pole_drops_live_and_dead_cords: pass, P_M14c_live_tip_glows: pass, P_M15_explosion_cuts_span: pass, P_M15a_wire_down_alert_lists_cut: pass, P_M15b_restring_rejoins: pass, P_M15c_wire_down_alert_clears_on_restring: pass, P_M15d_diagonal_cut_halves_meet_on_line: pass, P_M15e_restring_is_a_colonist_job: pass, P_M15f_restring_joined_run_one_look: pass, P_M17_owner_change_cuts_cross_owner_wires: pass, P_M19_tap_drains_one_way: pass, P_M19m_tap_mixed_net_connects_own_conduit: pass, P_M19n_taps_off_control: pass, P_M1_conduit_transparent: pass, P_M1_cords_exist: pass, P_M1_node_census: pass, P_M1c_end_pieces: pass, P_M1e_machine_on_inwall_run_draws_a_cord: pass, P_M1f_machine_on_hidden_conduit_draws_none: pass, P_M20a_fallen_wire_shock_flip: pass, P_M20b_fallen_wire_knockback_flip: pass, P_M20c_fallen_wire_ignites_flip: pass, P_M20d_keep_wires_setting_roundtrip: pass, P_M20e_shock_cells_die_with_wire: pass, P_M21a_cut_wires_on_owner_change_off_keeps_link: pass, P_M21b_cut_wires_on_owner_change_on_cuts_link: pass, P_M21c_drip_loops_off_plain_curve: pass, P_M21d_drip_loops_on_loop_samples: pass, P_M21e_keep_wires_on_gravship_off_setting_state: pass, P_M21f_keep_wires_on_gravship_on_setting_state: pass, P_M22a_kinetic_sway_on_swings_never_cuts: pass, P_M22b_kinetic_sway_off_does_nothing: pass, P_M2_cords_only_within_net: pass, P_M2b_no_vertex_unwalkable: pass, P_M2c_no_sharp_bends: pass, P_M5_local_invalidation: pass, P_M6_overlay_lines_intact: pass, P_M7_off_restores_vanilla: pass, P_M7b_on_again_invisible: pass, P_M8_break_two_ends_live_dead: pass, P_M8c_source_off_reads_dead_250: pass, P_MX_A04_N3_R12_fallen: pass, P_MX_A05_N3_R19_up: pass, P_MX_A06_N5_R6_fallen: pass, P_MX_A07_N5_R12_up: pass, P_MX_A08_N5_R19_cut: pass, P_MX_A09_N2_R6_cut: pass, P_MX_A10_N2_R12_fallen: pass, P_MX_A11_N2_R19_up: pass, P_MX_A12_N3_R6_fallen: pass, P_MX_C00_empty: pass, P_MX_D00_n1_S0: pass, P_MX_D05_n10_S1: pass, P_MX_D10_n100_S2: pass, P_MX_D15_n1000_S3: pass, P_MX_F00_T0_S0: pass, P_MX_F04_T1_S0: pass, P_MX_F11_T2_S3: pass, P_MX_F13_T3_S1: pass, P_MX_F18_T4_S2: pass, P_MX_F21_T5_S1: pass, P_MX_F25_T6_S1: pass, P_MX_F30_T7_S2: pass, P_MX_F33_T8_S1: pass, P_MX_F39_T9_S3: pass, P_MX_F42_T10_S2: pass, P_MX_F47_T11_S3: pass, P_MX_F51_T12_S3: pass, P_MX_F54_T13_S2: pass, P_MX_F56_T14_S0: pass, P_MX_F60_T15_S0: pass, P_P1B_perf_rebuild: pass, P_R1_span_altitude_above_pawns_below_blueprints: pass, P_R2_spans_and_heads_drawn: pass, P_R3_sway_proxy: pass, P_R3b_sway_looks_each_draw: pass, P_S10_legacy_default_materials: pass, P_S11_lamp_master_off_vanilla: pass, P_S12a_D1_legacy_run_one_look: pass, P_S12b_D7_bulk_spawn_cost: pass, P_S12c_D5_multilink_one_frame: pass, P_S12d_D4_pending_queue_save: pass, P_S12e_batched_links_merge: pass, P_S1_pick_reaches_blueprint: pass, P_S2_blueprint_frame_building: pass, P_S3_god_mode: pass, P_S4_copy_carries_look: pass, P_S5_reinstall_keeps_look: pass, P_S6_spans_in_pole_look: pass, P_S7_save_load_styles: pass, P_S8_legacy_unstyled_draws_default: pass, P_S8b_legacy_joined_to_styled_stores_look: pass, P_S9a_two_runs_two_styles: pass, P_S9b_bridge_largest_wins: pass, P_S9c_split_keeps_styles: pass, P_S9d_restyle_and_materials: pass, P_SC_bend_draws_no_joint_tee_draws_one: pass, P_SC_box_stub_slope: pass, P_SC_cord_end_one_kind: pass, P_SC_cords_all_slack: pass, P_SC_cut_battery_each_side_both_live: pass, P_SC_cut_never_powered_both_dead: pass, P_SC_dead_wire_lights_no_fuel: pass, P_SC_dead_wire_shocks_nobody: pass, P_SC_doorway_run_is_one_cord: pass, P_SC_floor_end_bites_aerial_master_off: pass, P_SC_floor_end_cord_behind_spares: pass, P_SC_floor_end_dead_spares: pass, P_SC_floor_end_every_end_over_spark_budget: pass, P_SC_floor_end_fixer_spared_other_builder_shocked: pass, P_SC_floor_end_live_shocks: pass, P_SC_floor_end_unfinished_run_bites: pass, P_SC_no_two_cords_alike: pass, P_SC_restring_drafted_no_job: pass, P_SC_restring_work_scheduler_takes_it: pass, P_SC_shock_reach_deck_cord_per_value: pass, P_SC_shock_reach_default_all: pass, P_SC_shock_reach_three_values: pass, P_SC_sparse_room_no_tangle: pass, P_SC_splicer_spared_bystander_shocked: pass, P_SC_statics_clear_between_games: pass, P_SC_under_battery_dry: pass, P_SC_under_furniture_dry: pass, P_SC_under_item_stack_dry: pass, P_SC_under_junction_piece_dry: pass, P_SC_under_liquid_pit: pass, P_SL1_save_landed_new_file_only: pass, P_SL2_save_names_no_class_of_ours: pass, P_SL3_after_load_census_equal: pass, P_ST1_styles_textures_load: pass, P_ST2_switch_changes_textures: pass, P_ST3_extcord_colour_modes: pass, P_ST4_settings_roundtrip: pass, P_ST5_restore_default_and_master: pass, P_SW1_highlight_off_draws_no_ring: pass, P_SW2_lod_off_far_zoom_draws_full: pass, P_SW3_break_readout_off_no_glow_no_whip: pass, P_SW4_sparks_only_overlay_shut_no_glow: pass, P_SW5_hide_hookup_off_leaves_vanilla_wire: pass, P_SW6_needless_loops_off_reaches_builder: pass, P_Z_log_budget: pass, sc_conduit_invisible: pass, sc_cords_slack: pass, sc_cords_under_items: pass, sc_cut_ends: pass, sc_dense_tangle: pass, sc_fallen_span: pass, sc_floor_end_shock: pass, sc_four_looks: pass, sc_fuel_ignition: pass, sc_gravship: pass, sc_junction_strips: pass, sc_look_menu_icons: pass, sc_no_repeat: pass, sc_no_roof_over_pole: pass, sc_no_sharp_turn: pass, sc_owner_change: pass, sc_pole_icons_loaded: pass, sc_pole_south_of_tree: pass, sc_removal_consequence: pass, sc_restring: pass, sc_restyle_whole_line: pass, sc_rewire_cost: pass, sc_settings: pass, sc_shock: pass, sc_shock_reach: pass, sc_shock_restring: pass, sc_spans: pass, sc_statics_new_game: pass, sc_stub_joins: pass, sc_switch_light: pass, sc_switch_off_ends: pass, sc_tap_theft: pass, sc_true_to_grid: pass, sc_walk: pass, sc_wall_lamp_looks: pass, sc_walls: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_020_VISIT1_WALK_20261123.rws
exit_met: true
```
