# GimmeSomeSlack 0.1.1 — in-game acceptance, visit 1

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE_RUN_TWO, game b on Archmagi
(`D:\ClaudeWork\rimmandrake\instances\b\game`). Started 2026-11-20 9:33 PM PST.

## Progress
- 9:33 PM precondition `in_game 0.1.1` [measured]; item claimed by this unit; bridge archmagi.b taken by BENCH; skeleton written.
- 9:35-9:41 PM GSS on game b in sync (362 files; DLL sha256 7157d9f1 = its .srchash over the 0.1.1 source 934b35e053);
  JawaBench companion FRESH; tier gimmesomeslack (12 mods, all 5 DLC) applied; game b launched (34 s). Game b's Saves
  backed up to D:\ClaudeWork\rimmandrake\backups\saves_b_gss_011_visit1_20261120; RM_TestSite_calm_v3 and
  GSS_OWNER_LOOK_20261116 copied in from game a's Saves (md5 checked; game a's copies untouched).
- 9:42 PM offline gate (proof_all --offline-gate): 0 red [measured].
- 9:43 PM PIPELINE DEFECT: the unit carried RM_GAME_INSTANCE=b with an empty WSLENV, so python.exe never saw it and the first
  batch drove game a (port 5174): it loaded RM_TestSite_calm_v3 there 10 s after a FlowWorks judge run took game a's bridge,
  then stopped at its preflight (18 mods, GSS absent). No save written, nothing deployed. That run was told at once.
  Filed and fixed test first: RIMMANDRAKE_CARRY_WSLENV_INTO_B_RUNS_PROOF_HIT_A (selftest_detached_game_env.py 6 FAIL on
  9708ac4b5e, 10 PASS after), published 08b3ba8881, closed. Measured on the way: WSLENV=NAME/u does not reach python.exe.
  From here every command runs with game_instance.env("b") (Transient/gss_env_b.sh); game b answers on 5175.
- 9:50-9:53 PM runA matrix,core on game b: 81/81 PASS [measured].
- 9:57-10:03 PM runB aerial,style,save_load,d4_save,statics: 64/64 PASS (P_R3b_sway_looks_each_draw among them);
  runC matrix,core,scenes: 108 PASS + 2 UNMEASURED that need FlowWorks loaded (SC_shock_reach_deck_cord_per_value,
  SC_under_liquid_pit; their tier is gimmesomeslack_flowworks) [measured].
- 10:03 PM the four 0.1.1 scenes: sc_pole_icons_loaded PASS, sc_switch_off_ends PASS, sc_no_roof_over_pole FAIL on one row
  (SC_forced_roof_still_cuts_spans: read 3 ticks after the forced roof; the mod cuts in its roof sweep, once per 250 ticks):
  class HARNESS, repaired test-first in the sitting (wait 260 ticks, read the roof back), published a2b606e05f; planted
  (roof gone before the sweep) FAIL, real PASS. sc_pole_south_of_tree: draw layer PASS, its capture waits a read.
- 10:10-10:15 PM gravship on PASS, off PASS.
- 10:16-10:22 PM sc_stub_joins on his review save (a copy in game b's Saves; md5 a1c76e27c41e before and after): PASS.
  All 31 stations captured (screenshots/sheet0-7.jpg) and looked at. Walk save built (human_review.py --build --fresh-map,
  31 stations, 62 labels, 31 sign books) and saved as GSS_011_VISIT1_WALK_20261120.rws. save_keeper read game a's Saves:
  filed and fixed test first (RIMMANDRAKE_POINT_REVIEWMAP_AT_GAME_B_SAVES_KEEPER_BLIND, 4ee4209d57).
- 10:30-10:55 PM sc_pole_south_of_tree: a planted control (fault_mast_on_building_layer.patch deployed, cold load): layer
  row FAIL and the south mast drawn behind the oak; real build redeployed (hash back to b9ae8819): layer row PASS and the
  south mast drawn in front (evidence/pole_south_look_read.json). Filed RIMMANDRAKE_RESTORE_SLACK_LOOK_FILE_AFTER_PROOF_LEFT_EXTCORD
  (the proof leaves the GSS settings file on ExtensionCord).
- 10:58-11:10 PM tier gimmesomeslack_flowworks (13 mods; game b's FlowWorks DLL brought level with the repo first):
  runE matrix,core,scenes 109 PASS + Z_log_budget FAIL (class SITE: FlowWorks' RM_PitAccess.cs:277 error, as in visit 3,
  its item still open); runF aerial,style,save_load,d4_save,statics 64/64 PASS (Z_log_budget PASS).
- 11:12-11:15 PM tier bridge (10 mods, no GSS): removal check on runB's proof save PASS.
- 11:20 PM walk save copied into game a's Saves (one new file, none changed: manifest diff) with its sign sidecar.

## What ran
- Game b on Archmagi (`D:\ClaudeWork\rimmandrake\instances\b\game`), RimWorld 1.6.4871 rev590. GSS deployed folder
  sha256:b9ae88196d35 (DLL from the 0.1.1 source 934b35e053, its .srchash matching). The planted-def deploy for the draw-order
  control (10:30-10:40 PM) was reverted and the hash read back as b9ae88196d35 before any further row; every row names it.
- Tiers: gimmesomeslack (12 mods, all 5 DLC) for runs A-C, the four 0.1.1 scenes, gravship, stub joins and the walk save;
  gimmesomeslack_flowworks (13) for runs E-F and the four scenes the table puts there; bridge (10, no GSS) for the removal
  check. Each row carries `build_match.py identity` for its tier (evidence/identity_tier_*.json).
- sc_walk did not run: it needs his full list, which game b cannot hold beside game a; game a was another run's all visit.

## Results [measured]
202 stage-6 checks: 201 PASS on their last row, 0 FAIL, 1 UNMEASURED (sc_walk: game b: tier list only beside game a).
- sc_no_roof_over_pole: first run FAIL on SC_forced_roof_still_cuts_spans, class HARNESS (read 3 ticks after the forced roof;
  the mod cuts in its roof sweep, once per 250 ticks). Repaired in the sitting (wait 260 ticks; the roof read back, else
  UNMEASURED SITE), published a2b606e05f. Planted (the roof removed again before the sweep): FAIL. Real: PASS (both span
  ends Cut). red-seen does not apply: no offline decider's file is scene_rows.py.
- sc_pole_south_of_tree: the scene leaves its capture for a reader. Read here, with a control: real build PASS (south mast in
  front of the oak north of it, north mast behind the oak south of it); planted fault_mast_on_building_layer.patch FAIL (south
  mast behind; its layer row FAIL too). 27544 pixels differ, all at the south mast (evidence/pole_south_look_read.json;
  screenshots/pole_rect_REAL_bot_layer.jpg, pole_rect_PLANTED_building_layer.jpg). The reader is this visit run, which did not
  make the mod or the fix; the steward may re-read the two captures.
- P_Z_log_budget: FAIL on runE (tier gimmesomeslack_flowworks, class SITE, FlowWorks' error); PASS on runA-C and runF.
- No fix to the mod was made in the sitting. No check was removed.

## Pipeline defects fixed in this run
- RIMMANDRAKE_CARRY_WSLENV_INTO_B_RUNS_PROOF_HIT_A, 08b3ba8881: a detached run for game b carried RM_GAME_INSTANCE=b with no
  WSLENV, so python.exe drove game a. The first batch loaded its calm site on game a while a FlowWorks judge held it (told at
  once; no save, no deploy). selftest_detached_game_env.py 6 FAIL on base, 10 PASS after. Closed.
- RIMMANDRAKE_POINT_REVIEWMAP_AT_GAME_B_SAVES_KEEPER_BLIND, 4ee4209d57: reviewmap watched game a's Saves whatever game was
  named. selftest_reviewmap_game_saves.py 2 FAIL on base, all PASS after. Closed.
- sc_no_roof_over_pole's read (HARNESS repair above), a2b606e05f.
- Filed, not fixed: RIMMANDRAKE_RESTORE_SLACK_LOOK_FILE_AFTER_PROOF_LEFT_EXTCORD (the proof leaves the GSS settings file on
  ExtensionCord; game a's file too, since 0.1.0 visit 3). The writer is in the mod's DLL; a fix here would void every row.

## Owed cases from the blind challenge (cycle 1)
- PF_G_TAPS_DOUBLE_CLAIM_SURPLUS: would NOT have been seen [read, not run; guess ~85%]: every tap row stages one tap per
  victim net, where the fault changes nothing. A row of its own (UNMEASURED); one polish.md line.
- PF_G_LINK_RANGE_DOUBLED: would have been seen [read, not run; guess ~90%]: the range is 20 cells, doubled 40; M13d asks
  m1->m3 at 24 cells for OutOfRange, which would link instead: M13d and sc_spans FAIL.
- PF_P_SWITCH_NOT_STYLEABLE: an equivalent mutant (planted_faults.json: the loaded defs do not change); no check can see it.
- The 34 lane-1 not_kernel rows: each named check has a PASS last row (sc_conduit_invisible, sc_cords_slack, sc_no_sharp_turn,
  sc_walls, sc_junction_strips, sc_dense_tangle, sc_no_repeat, sc_true_to_grid, sc_cords_under_items, sc_cut_ends,
  sc_rewire_cost, sc_restring, sc_four_looks, sc_owner_change, sc_statics_new_game, sc_removal_consequence,
  sc_floor_end_shock, sc_shock_reach, sc_fuel_ignition, sc_stub_joins, sc_switch_off_ends, sc_pole_icons_loaded,
  sc_pole_south_of_tree), except not_kernel_walk_scavenger_base: sc_walk UNMEASURED (game b). sc_dense_tangle and
  sc_four_looks PASS on their scripted reads; no judge agent ran (this helper starts none).

## Owed from the road back (unrun.jsonl)
- RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE -> P_M8_break_two_ends_live_dead: PASS in all 3 runs with the core
  block (runA, runC, runE).
- RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES -> sc_walk: UNMEASURED, not run (full list; game a only).

## Beyond the checks
All 31 stations of his review save captured with the game's render and looked at (screenshots/sheet0-7.jpg; PNGs in
D:\ClaudeWork\scratch\gss_011_v1\shots). Experiments on the pole draw order: four looks placed by the Architect and
batch-built linked masts all drew in front of an oak north of them (screenshots/look_experiment*.jpg). Strange things: 7 in
strange.jsonl, 3 filed, 4 explained, 0 open.

## Savegame for his walk
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT1_WALK_20261120.rws`
(md5 1cd9974f5111, sign sidecar beside it): the 31-station labelled review map built on game b, tier gimmesomeslack, on the
deployed build b9ae88196d35. The same file is in game b's Saves. Game a's Saves: GSS keepers and a stat manifest backed up
to D:\ClaudeWork\rimmandrake\backups\saves_a_gss_011_visit1_20261120 first; the diff shows one new file, none changed.

## The pipeline's reading of this record (maturation.py next GimmeSomeSlack, 2026-11-20 ~10:55 PM PST)
Two FORM reasons were repaired: sc_walk's not-run row now says `unrepaired` and `owner`; 174 rows named the clone's HEAD
a2b606e05f as mod_sha and now name 934b35e053 (the trees differ only in northstar/scene_rows.py, which does not ship; the
deployed hash is b9ae88196d35 on every row; each changed row carries `mod_sha_note`). What stays is substance:

> refused exit_met: in-game visit 1 exit not_met: the driver's block says exit_met false; bar walk_scavenger_base is undecided: its in-game check(s) sc_walk are not counted (unrepaired: not run, nothing to repair: game b: tier list only beside game a. The check needs his full list, which game b cannot hold beside game a (memory); game a was held by another run's FlowWorks work all visit.; owner game a, at the next GSS visit or steward run that holds it (unrun.jsonl: RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES -> sc_walk)) and no other in-game check of it counts: repair one in the sit

`build_match.py check --mod GimmeSomeSlack`: 202 cases read, 202 count, 0 to re-run.

## Exit
```
ingame_rows: {P_A8_same_frame_dirty_not_dropped: pass, P_B13_hidden_conduit_hookup_not_drawn: pass, P_B1_rope_settle: pass, P_B3_whip_live_ends: pass, P_B3c_spark_rides_whip: pass, P_B4b_sparks_thrown_ticking: pass, P_B4c_spark_intensity_scales_downed: pass, P_B4d_spark_budget_shared_visible_first: pass, P_B5_selection_highlight: pass, P_B6_tangle_lit_strips: pass, P_B6b_strips_dark_when_dead: pass, P_B7_ground_cords_never_sway: pass, P_B8_lod_far_zoom: pass, P_B9_cutscene_guard_idle: pass, P_D1_zero_tick_rereads_same: pass, P_D2_fresh_builder_same: pass, P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down: pass, P_GS1_keep_wires_on_gravship_on_aboard_span_flies: pass, P_M10_tangle_threshold_setting: pass, P_M11_dive_through_setting: pass, P_M12a_slide_under_off_plug_on_cell_centre: pass, P_M12b_slide_under_on_plug_off_centre: pass, P_M13a_linked_one_net_across_gap: pass, P_M13b_far_consumer_powered: pass, P_M13c_unlink_two_nets_relink_one: pass, P_M13d_refusals: pass, P_M13e_hostile_mast_not_autolinked: pass, P_M14_gap_control_without_fix: pass, P_M14a_remove_middle_both_ends_resolve: pass, P_M14b_dead_pole_drops_live_and_dead_cords: pass, P_M14c_live_tip_glows: pass, P_M15_explosion_cuts_span: pass, P_M15a_wire_down_alert_lists_cut: pass, P_M15b_restring_rejoins: pass, P_M15c_wire_down_alert_clears_on_restring: pass, P_M15d_diagonal_cut_halves_meet_on_line: pass, P_M15e_restring_is_a_colonist_job: pass, P_M15f_restring_joined_run_one_look: pass, P_M17_owner_change_cuts_cross_owner_wires: pass, P_M19_tap_drains_one_way: pass, P_M19m_tap_mixed_net_connects_own_conduit: pass, P_M19n_taps_off_control: pass, P_M1_conduit_transparent: pass, P_M1_cords_exist: pass, P_M1_node_census: pass, P_M1c_end_pieces: pass, P_M1e_machine_on_inwall_run_draws_a_cord: pass, P_M1f_machine_on_hidden_conduit_draws_none: pass, P_M20a_fallen_wire_shock_flip: pass, P_M20b_fallen_wire_knockback_flip: pass, P_M20c_fallen_wire_ignites_flip: pass, P_M20d_keep_wires_setting_roundtrip: pass, P_M20e_shock_cells_die_with_wire: pass, P_M21a_cut_wires_on_owner_change_off_keeps_link: pass, P_M21b_cut_wires_on_owner_change_on_cuts_link: pass, P_M21c_drip_loops_off_plain_curve: pass, P_M21d_drip_loops_on_loop_samples: pass, P_M21e_keep_wires_on_gravship_off_setting_state: pass, P_M21f_keep_wires_on_gravship_on_setting_state: pass, P_M22a_kinetic_sway_on_swings_never_cuts: pass, P_M22b_kinetic_sway_off_does_nothing: pass, P_M2_cords_only_within_net: pass, P_M2b_no_vertex_unwalkable: pass, P_M2c_no_sharp_bends: pass, P_M5_local_invalidation: pass, P_M6_overlay_lines_intact: pass, P_M7_off_restores_vanilla: pass, P_M7b_on_again_invisible: pass, P_M8_break_two_ends_live_dead: pass, P_M8c_source_off_reads_dead_250: pass, P_MX_A04_N3_R12_fallen: pass, P_MX_A05_N3_R19_up: pass, P_MX_A06_N5_R6_fallen: pass, P_MX_A07_N5_R12_up: pass, P_MX_A08_N5_R19_cut: pass, P_MX_A09_N2_R6_cut: pass, P_MX_A10_N2_R12_fallen: pass, P_MX_A11_N2_R19_up: pass, P_MX_A12_N3_R6_fallen: pass, P_MX_C00_empty: pass, P_MX_D00_n1_S0: pass, P_MX_D05_n10_S1: pass, P_MX_D10_n100_S2: pass, P_MX_D15_n1000_S3: pass, P_MX_F00_T0_S0: pass, P_MX_F04_T1_S0: pass, P_MX_F11_T2_S3: pass, P_MX_F13_T3_S1: pass, P_MX_F18_T4_S2: pass, P_MX_F21_T5_S1: pass, P_MX_F25_T6_S1: pass, P_MX_F30_T7_S2: pass, P_MX_F33_T8_S1: pass, P_MX_F39_T9_S3: pass, P_MX_F42_T10_S2: pass, P_MX_F47_T11_S3: pass, P_MX_F51_T12_S3: pass, P_MX_F54_T13_S2: pass, P_MX_F56_T14_S0: pass, P_MX_F60_T15_S0: pass, P_P1B_perf_rebuild: pass, P_R1_span_altitude_above_pawns_below_blueprints: pass, P_R2_spans_and_heads_drawn: pass, P_R3_sway_proxy: pass, P_R3b_sway_looks_each_draw: pass, P_S10_legacy_default_materials: pass, P_S11_lamp_master_off_vanilla: pass, P_S12a_D1_legacy_run_one_look: pass, P_S12b_D7_bulk_spawn_cost: pass, P_S12c_D5_multilink_one_frame: pass, P_S12d_D4_pending_queue_save: pass, P_S12e_batched_links_merge: pass, P_S1_pick_reaches_blueprint: pass, P_S2_blueprint_frame_building: pass, P_S3_god_mode: pass, P_S4_copy_carries_look: pass, P_S5_reinstall_keeps_look: pass, P_S6_spans_in_pole_look: pass, P_S7_save_load_styles: pass, P_S8_legacy_unstyled_draws_default: pass, P_S8b_legacy_joined_to_styled_stores_look: pass, P_S9a_two_runs_two_styles: pass, P_S9b_bridge_largest_wins: pass, P_S9c_split_keeps_styles: pass, P_S9d_restyle_and_materials: pass, P_SC_bend_draws_no_joint_tee_draws_one: pass, P_SC_box_stub_slope: pass, P_SC_cord_end_one_kind: pass, P_SC_cords_all_slack: pass, P_SC_cut_battery_each_side_both_live: pass, P_SC_cut_never_powered_both_dead: pass, P_SC_dead_wire_lights_no_fuel: pass, P_SC_dead_wire_shocks_nobody: pass, P_SC_doorway_run_is_one_cord: pass, P_SC_floor_end_bites_aerial_master_off: pass, P_SC_floor_end_cord_behind_spares: pass, P_SC_floor_end_dead_spares: pass, P_SC_floor_end_every_end_over_spark_budget: pass, P_SC_floor_end_fixer_spared_other_builder_shocked: pass, P_SC_floor_end_live_shocks: pass, P_SC_floor_end_unfinished_run_bites: pass, P_SC_no_two_cords_alike: pass, P_SC_restring_drafted_no_job: pass, P_SC_restring_work_scheduler_takes_it: pass, P_SC_shock_reach_deck_cord_per_value: pass, P_SC_shock_reach_default_all: pass, P_SC_shock_reach_three_values: pass, P_SC_sparse_room_no_tangle: pass, P_SC_splicer_spared_bystander_shocked: pass, P_SC_statics_clear_between_games: pass, P_SC_under_battery_dry: pass, P_SC_under_furniture_dry: pass, P_SC_under_item_stack_dry: pass, P_SC_under_junction_piece_dry: pass, P_SC_under_liquid_pit: pass, P_SL1_save_landed_new_file_only: pass, P_SL2_save_names_no_class_of_ours: pass, P_SL3_after_load_census_equal: pass, P_ST1_styles_textures_load: pass, P_ST2_switch_changes_textures: pass, P_ST3_extcord_colour_modes: pass, P_ST4_settings_roundtrip: pass, P_ST5_restore_default_and_master: pass, P_SW1_highlight_off_draws_no_ring: pass, P_SW2_lod_off_far_zoom_draws_full: pass, P_SW3_break_readout_off_no_glow_no_whip: pass, P_SW4_sparks_only_overlay_shut_no_glow: pass, P_SW5_hide_hookup_off_leaves_vanilla_wire: pass, P_SW6_needless_loops_off_reaches_builder: pass, P_Z_log_budget: pass, sc_conduit_invisible: pass, sc_cords_slack: pass, sc_cords_under_items: pass, sc_cut_ends: pass, sc_dense_tangle: pass, sc_fallen_span: pass, sc_floor_end_shock: pass, sc_four_looks: pass, sc_fuel_ignition: pass, sc_gravship: pass, sc_junction_strips: pass, sc_no_repeat: pass, sc_no_roof_over_pole: pass, sc_no_sharp_turn: pass, sc_owner_change: pass, sc_pole_icons_loaded: pass, sc_pole_south_of_tree: pass, sc_removal_consequence: pass, sc_restring: pass, sc_rewire_cost: pass, sc_settings: pass, sc_shock: pass, sc_shock_reach: pass, sc_shock_restring: pass, sc_spans: pass, sc_statics_new_game: pass, sc_stub_joins: pass, sc_switch_off_ends: pass, sc_tap_theft: pass, sc_true_to_grid: pass, sc_walk: unmeasured, sc_walls: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT1_WALK_20261120.rws
exit_met: false
```
