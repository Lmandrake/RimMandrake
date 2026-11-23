# GimmeSomeSlack 0.1.1 — in-game acceptance, visit 3

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_THREE_RUN_TWO, game b on Archmagi
(`D:\ClaudeWork\rimmandrake\instances\b\game`). Started 2026-11-21 7:13 PM PST. 142 checks to run again (rerun_relation.py:
the switch-light C# since visit 1 touches them); 61 keep their PASS.

## Progress
- 7:13 PM precondition `in_game 0.1.1` [measured]; item claimed; bridge archmagi.b taken by BENCH (gen 26); skeleton written.
- 7:15-7:25 PM GSS on game b in sync (362 files; deployed folder sha256:e9c2b80d6890, the build visit 2 walked on game a);
  game b found on tier gimmesomeslack_flowworks (13 mods). Offline gate (proof_all --offline-gate): 0 red [measured].
- 7:26-7:33 PM runE matrix,core,scenes (flowworks tier): 107 PASS + Z_log_budget FAIL, class SITE (FlowWorks
  RM_PitAccess.cs:277 ThingsOfDef(MinifiedThing); no GSS frame; open item RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR).
- 7:34-7:37 PM runF aerial,style,save_load,d4_save,statics (flowworks tier): 62/62 PASS (Z_log_budget PASS).
- 7:37-7:46 PM game b relaunched on tier gimmesomeslack (12 mods): runC matrix,core,scenes 102 PASS + 2 UNMEASURED that need
  FlowWorks (SC_shock_reach_deck_cord_per_value, SC_under_liquid_pit: left out of this run's rows; PASS in runE);
  runB aerial,style,save_load,d4_save,statics 62/62 PASS [measured].
- 7:46-7:51 PM gravship_scene.py on PASS, off PASS. 7:51-7:53 PM tier bridge (10 mods): removal check on runB's proof save PASS.
- 7:55-8:10 PM two pipeline defects found, filed and fixed test first, published, closed (see "Pipeline defects").
- 8:19-8:23 PM game b back on tier gimmesomeslack; game b's Saves backed up (83 files,
  D:\ClaudeWork\rimmandrake\backups\saves_b_gss_011_visit3_20261121); review map built (human_review.py --build --fresh-map:
  31 stations, 62 labels, 31 sign books, 58.7 s) and saved as GSS_011_VISIT3_WALK_20261121.rws (Saves diff: one new
  file, none changed).
- 8:23-8:26 PM all 31 stations captured with the game's render (screenshots/sheet0-7.jpg) and looked at; 2 follow-up
  captures (station 5's steam cloud, station 9's cord). Walk save copied into game a's Saves (manifest backed up first to
  D:\ClaudeWork\rimmandrake\backups\saves_a_gss_011_visit3_20261121; diff: one new file, none changed; md5 5e8eea3d5848 on both).

## What ran
- Game b on Archmagi (`D:\ClaudeWork\rimmandrake\instances\b\game`), RimWorld 1.6.4871 rev590. GSS deployed folder
  sha256:e9c2b80d6890 on every row (deploy dry run in sync, 362 files; DLL from source d0b6483f04, the same build visit 2
  walked on game a). No mod change in the sitting, so one build throughout.
- Tiers: gimmesomeslack_flowworks (13 mods) for runE and runF and the four scenes the table puts there; gimmesomeslack (12)
  for runC, runB, gravship and the walk save; bridge (10, no GSS) for the removal check. All 5 DLC on each. Each row carries
  `build_match.py identity` for its tier (evidence/identity_tier_*.json).
- The flowworks tier ran first because game b was already on it; so the gimmesomeslack scene rows written at runC read some
  aerial rows from runF (flowworks tier). runB then re-ran those rows on the gimmesomeslack tier with the same results, so
  no scene verdict changed (visit_rows.py writes a scene row only when its verdict or detail changes).

## Results [measured]
142 checks to run: 142 PASS, 0 FAIL, 0 UNMEASURED.
- 141 ran here, each with a PASS last row in rows.jsonl.
- sc_walk did not run here. Its visit 2 row is PASS on his full list (315 mods), on game a, on the same deployed hash
  sha256:e9c2b80d6890 (visit_2/rows.jsonl). The only change since that row's commit d0b6483f04 is three review/ documents
  (KEYSHEET.md, README.md, keysheet.html) that GSS's .hashignore lists as never shipped. rerun_relation.py counted them
  against a whole-mod check; that was a pipeline defect, fixed in this run (below). With the fix, the relation reads all 203
  checks untouched. The brief asked for an UNMEASURED sc_walk row ("game b: tier list only beside game a"). This run wrote
  none, because such a row would replace a valid PASS with a reading of a run that did not happen.
- P_Z_log_budget: FAIL on runE (flowworks tier), class SITE: FlowWorks' RM_PitAccess.cs:277 calls
  ThingsOfDef(MinifiedThing), with no GSS frame (open item RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR).
  PASS on runF, runC and runB (its last row: runB, tier gimmesomeslack, tap lost 0).
- SC_shock_reach_deck_cord_per_value and SC_under_liquid_pit read UNMEASURED on runC, because they need FlowWorks loaded.
  They were left out of runC's rows (--only), and their rows are runE's PASS on the flowworks tier.
- No mod fix made. No check repaired or removed. No item filed against the mod.

## Pipeline defects fixed in this run
- RIMMANDRAKE_SKIP_HASHIGNORED_FILES_IN_WHOLE_MOD_RERUN_DOCS_SENT_WALK_BACK, 83fb77dd87: rerun_relation.py counted
  files a mod's .hashignore lists (they never ship, and the mod hash leaves them out) against whole-mod and full-list
  checks. So three review/ docs sent GSS's full-list walk back on an unchanged mod hash. selftest_rerun_relation.py: red
  1 of 19 on c8ef19b610, green 0 of 19. The boundary page gains the promise whole-mod-check-skips-hashignored. Closed.
- RIMMANDRAKE_CLEAR_CALLER_GAME_IN_LOCK_SELFTEST_B_HELPERS_REFUSED, 780285d06a: selftest_game_lock.py inherited the
  caller's RM_GAME_INSTANCE=b, so ./publish refused this game-b helper twice. With RM_GAME_INSTANCE=b: red, 3 failed on
  83fb77dd87; green, 0 failed. The fix was published from that environment. Closed.

## Owed cases from the blind challenge (cycle 1)
- PF_G_TAPS_DOUBLE_CLAIM_SURPLUS (listed twice): would NOT have been seen by sc_tap_theft or sc_statics_new_game [read,
  not run; guess ~85%]. Every tap row stages one tap per victim net, and there the fault changes nothing. Both checks PASS
  here (runC scene read; runB/runF aerial rows). Visit 1's UNMEASURED row for the plant stands, with its polish line.
- PF_G_LINK_RANGE_DOUBLED: would have been seen [read, not run; guess ~90%]. M13d asks m1->m3 at 24 cells with a 20-cell
  range for OutOfRange. Doubled to 40, it links, so M13d and sc_spans FAIL. This visit read M13d `'m1->m3 (24 cells)':
  'OutOfRange'` on runF and runB [measured].
- PF_P_SWITCH_NOT_STYLEABLE (listed twice): an equivalent mutant (planted_faults.json: the loaded defs do not change), so
  no check can see it. sc_four_looks PASS here; sc_switch_off_ends keeps its visit 2 PASS (untouched).
- The 34 lane-1 not_kernel rows: each named check of the 142 has a PASS last row here. sc_walk's is visit 2's (above).
  sc_owner_change, sc_fuel_ignition, sc_stub_joins, sc_switch_off_ends, sc_pole_icons_loaded and sc_pole_south_of_tree are
  among the 61 untouched checks; they keep their earlier PASS rows. sc_owner_change and sc_fuel_ignition also got
  PASS rows here.

## Owed from the road back (unrun.jsonl)
- RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES -> sc_walk: PASS in visit 2 on his full list, on this deployed
  hash. Not rerun here; see Results.
- RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE -> P_M8_break_two_ends_live_dead: PASS on runE and runC
  (proof_all --only matrix,core,scenes; the owed command's core block).

## Beyond the checks
All 31 stations of the walk save were captured with the game's render and looked at (screenshots/sheet0-7.jpg; PNGs in
D:\ClaudeWork\scratch\gss_011_v3\shots). Strange things: 7 in strange.jsonl, 3 filed (two fixed here, one already open),
4 explained, 0 open. Two polish lines (polish.md).

## Savegame for his walk
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT2_WALK_20261121.rws`
(md5 f97d61ca4935, unchanged since 3:42 AM). This is visit 2's 31-station labelled review map on his full list (315 mods),
on the same deployed build sha256:e9c2b80d6890. His walk is on his full list, and game b cannot hold that list beside game
a, so this visit names that save. The build match reads 203 of 203 count against it [measured].
This visit's own build of the same map is on tier gimmesomeslack, and every station was looked at:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT3_WALK_20261121.rws`
(md5 5e8eea3d5848; also in game b's Saves). The first name in the exit block was this tier save. build_match refused it
for sc_walk ("a full-list test whose list is not his walk's", 12 mods against 315), so it was replaced. His keepers
(GSS_OWNER_LOOK_20261116*) are untouched.

## Game and bridge at the end
Game b is left running on tier gimmesomeslack with the walk map loaded (healthy, paused). The list is not restored (owner,
2026-10-24). Bridge archmagi.b released by BENCH.

## The pipeline's reading of this record (maturation.py next GimmeSomeSlack, 2026-11-21 ~8:40 PM PST)
Three form reasons were repaired, and no verdict changed. (1) The block left out checks that have rows here (sc_spans,
sc_fallen_span, sc_owner_change and others among the 61 untouched); it now lists every check with a row in this visit, plus
sc_walk. (2) Three strange rows carried prose in `filed`; they now carry the bare item id, with the prose in `note`. (3) The
first savegame named was this visit's tier save; build_match refused it for the full-list sc_walk, so the block names visit
2's full-list walk save of the same build. Last lines:

> exit tests passing: order, version, hold, exit_met, build_match
> in-game visit 3: 203 stage-6 checks (0 with a testq block); exit met: 203 of 203 in-game checks PASS on checked sites;
> strange things all explained or filed; savegame C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_011_VISIT2_WALK_20261121.rws

`build_match.py check --mod GimmeSomeSlack`: 203 cases read, 203 count, 0 to run.

## Rerun on the build he walked (2026-11-22 11:00 PM to 2026-11-23 12:15 AM PST)
His walk of 2026-11-22 (the short look at the four changes, `OWNER:1795413364353487264`, "GSS walk full pass. Looks
great!") was on ArchBig, his full list (314 mods), save `RM_GSS_011_FOUR_CHANGES_LOOK_20261122.rws`, build 244ae76cdf
(deployed sha256:9fab75a79000). The four changes since 86d5dae1bc (kink rounding in CordShape/CordBuilder, the halved
switch light, Gust sway default, the Restyle reach menu) touch all 203 checks, so all 203 ran again here, on that build
(run: detached helper on RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS, ArchBig taken idle-ok).
- Offline gate (proof_all --offline-gate): first run red on O3, one timing row: "slice: an all-keys-changed re-lay held
  one Build 32.1 ms" (bound 30 ms), load average 5 to 8. Class: the check (a single timed attempt; the cold-build row
  beside it takes the best of 3). Re-runs: 25.5 ms and 23.4 ms with the Unkink step, 17.7 ms without it; the gate
  again: red [] [measured]. Not repaired: its source is in Source/SelfTest, which the checks read, so an edit would send
  all 203 back. One polish line.
- Tier gimmesomeslack (12 mods): runC matrix,core,scenes 108 PASS + 2 UNMEASURED that need FlowWorks (left out of its
  rows); runB aerial,style,save_load,d4_save,statics 64/64 PASS; gravship on PASS, off PASS; validation.py --scene for
  switch_off_ends, pole_icons_loaded, no_roof_over_pole, switch_light PASS; pole_south_of_tree: layer row PASS and the
  shot read PASS (south mast in front of the tree north of it, the tree south of the other mast drawn over it;
  screenshots/rerun_244ae76cdf_pole_south_of_tree.png); live_stub_joins.py --load PASS (398 taken, 0 off line, 0 off
  slope, 0 live unlaid).
- Tier gimmesomeslack_flowworks (13): runE matrix,core,scenes 110/110 PASS (P_Z_log_budget PASS this time); runF 64/64.
- Tier bridge (10): removal check on runB's proof save RM_gss_proof_20261122231359 PASS (0 errors naming the mod).
- His walk list (314, written from his walk save into ModsConfig, cold load 12 min): his walk save loaded from the main
  menu (314/314 compatible); gss_playtest_runner.py --recipe full PASS (cords, soak 8 blasts, ui 24/24, save_reload_b
  7/7 lines). Saves diff: one new file (the runner's JBPT_gsspt_20261123T081050_s1.rws), none changed.
- Every row carries `build_match.py identity` (mod_sha 244ae76cdf) for its tier or the full list. Scene rows were read
  only after every proof row they read had run on this build (checked; one sc_gravship row read the old gravship rows
  and was removed and re-read).
- Pipeline defect fixed here: visit_rows.py wrote no scene row when the verdict and detail were unchanged, even on a new
  build, so the build match kept reading the old build's scene row. It now writes the row when the mod hash differs.
- Results: 203 of 203 PASS on 244ae76cdf [measured]. No mod fault. No check repaired or removed.
- The exit block's savegame now names the save he walked (it named visit 2's walk save, 315 mods, which he did not walk
  this time).

## Exit
```
ingame_rows: {P_A8_same_frame_dirty_not_dropped: pass, P_B13_hidden_conduit_hookup_not_drawn: pass, P_B1_rope_settle: pass, P_B3_whip_live_ends: pass, P_B3c_spark_rides_whip: pass, P_B4b_sparks_thrown_ticking: pass, P_B4c_spark_intensity_scales_downed: pass, P_B4d_spark_budget_shared_visible_first: pass, P_B5_selection_highlight: pass, P_B6_tangle_lit_strips: pass, P_B6b_strips_dark_when_dead: pass, P_B7_ground_cords_never_sway: pass, P_B8_lod_far_zoom: pass, P_B9_cutscene_guard_idle: pass, P_D1_zero_tick_rereads_same: pass, P_D2_fresh_builder_same: pass, P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down: pass, P_GS1_keep_wires_on_gravship_on_aboard_span_flies: pass, P_M10_tangle_threshold_setting: pass, P_M11_dive_through_setting: pass, P_M12a_slide_under_off_plug_on_cell_centre: pass, P_M12b_slide_under_on_plug_off_centre: pass, P_M13a_linked_one_net_across_gap: pass, P_M13b_far_consumer_powered: pass, P_M13c_unlink_two_nets_relink_one: pass, P_M13d_refusals: pass, P_M13e_hostile_mast_not_autolinked: pass, P_M14_gap_control_without_fix: pass, P_M14a_remove_middle_both_ends_resolve: pass, P_M14b_dead_pole_drops_live_and_dead_cords: pass, P_M14c_live_tip_glows: pass, P_M15_explosion_cuts_span: pass, P_M15a_wire_down_alert_lists_cut: pass, P_M15b_restring_rejoins: pass, P_M15c_wire_down_alert_clears_on_restring: pass, P_M15d_diagonal_cut_halves_meet_on_line: pass, P_M15e_restring_is_a_colonist_job: pass, P_M15f_restring_joined_run_one_look: pass, P_M17_owner_change_cuts_cross_owner_wires: pass, P_M19_tap_drains_one_way: pass, P_M19m_tap_mixed_net_connects_own_conduit: pass, P_M19n_taps_off_control: pass, P_M1_conduit_transparent: pass, P_M1_cords_exist: pass, P_M1_node_census: pass, P_M1c_end_pieces: pass, P_M1e_machine_on_inwall_run_draws_a_cord: pass, P_M1f_machine_on_hidden_conduit_draws_none: pass, P_M20a_fallen_wire_shock_flip: pass, P_M20b_fallen_wire_knockback_flip: pass, P_M20c_fallen_wire_ignites_flip: pass, P_M20d_keep_wires_setting_roundtrip: pass, P_M20e_shock_cells_die_with_wire: pass, P_M21a_cut_wires_on_owner_change_off_keeps_link: pass, P_M21b_cut_wires_on_owner_change_on_cuts_link: pass, P_M21c_drip_loops_off_plain_curve: pass, P_M21d_drip_loops_on_loop_samples: pass, P_M21e_keep_wires_on_gravship_off_setting_state: pass, P_M21f_keep_wires_on_gravship_on_setting_state: pass, P_M22a_kinetic_sway_on_swings_never_cuts: pass, P_M22b_kinetic_sway_off_does_nothing: pass, P_M2_cords_only_within_net: pass, P_M2b_no_vertex_unwalkable: pass, P_M2c_no_sharp_bends: pass, P_M5_local_invalidation: pass, P_M6_overlay_lines_intact: pass, P_M7_off_restores_vanilla: pass, P_M7b_on_again_invisible: pass, P_M8_break_two_ends_live_dead: pass, P_M8c_source_off_reads_dead_250: pass, P_MX_A04_N3_R12_fallen: pass, P_MX_A05_N3_R19_up: pass, P_MX_A06_N5_R6_fallen: pass, P_MX_A07_N5_R12_up: pass, P_MX_A08_N5_R19_cut: pass, P_MX_A09_N2_R6_cut: pass, P_MX_A10_N2_R12_fallen: pass, P_MX_A11_N2_R19_up: pass, P_MX_A12_N3_R6_fallen: pass, P_MX_C00_empty: pass, P_MX_D00_n1_S0: pass, P_MX_D05_n10_S1: pass, P_MX_D10_n100_S2: pass, P_MX_D15_n1000_S3: pass, P_MX_F00_T0_S0: pass, P_MX_F04_T1_S0: pass, P_MX_F11_T2_S3: pass, P_MX_F13_T3_S1: pass, P_MX_F18_T4_S2: pass, P_MX_F21_T5_S1: pass, P_MX_F25_T6_S1: pass, P_MX_F30_T7_S2: pass, P_MX_F33_T8_S1: pass, P_MX_F39_T9_S3: pass, P_MX_F42_T10_S2: pass, P_MX_F47_T11_S3: pass, P_MX_F51_T12_S3: pass, P_MX_F54_T13_S2: pass, P_MX_F56_T14_S0: pass, P_MX_F60_T15_S0: pass, P_P1B_perf_rebuild: pass, P_R1_span_altitude_above_pawns_below_blueprints: pass, P_R2_spans_and_heads_drawn: pass, P_R3_sway_proxy: pass, P_R3b_sway_looks_each_draw: pass, P_S10_legacy_default_materials: pass, P_S11_lamp_master_off_vanilla: pass, P_S12a_D1_legacy_run_one_look: pass, P_S12b_D7_bulk_spawn_cost: pass, P_S12c_D5_multilink_one_frame: pass, P_S12d_D4_pending_queue_save: pass, P_S12e_batched_links_merge: pass, P_S1_pick_reaches_blueprint: pass, P_S2_blueprint_frame_building: pass, P_S3_god_mode: pass, P_S4_copy_carries_look: pass, P_S5_reinstall_keeps_look: pass, P_S6_spans_in_pole_look: pass, P_S7_save_load_styles: pass, P_S8_legacy_unstyled_draws_default: pass, P_S8b_legacy_joined_to_styled_stores_look: pass, P_S9a_two_runs_two_styles: pass, P_S9b_bridge_largest_wins: pass, P_S9c_split_keeps_styles: pass, P_S9d_restyle_and_materials: pass, P_SC_bend_draws_no_joint_tee_draws_one: pass, P_SC_box_stub_slope: pass, P_SC_cord_end_one_kind: pass, P_SC_cords_all_slack: pass, P_SC_cut_battery_each_side_both_live: pass, P_SC_cut_never_powered_both_dead: pass, P_SC_dead_wire_lights_no_fuel: pass, P_SC_dead_wire_shocks_nobody: pass, P_SC_doorway_run_is_one_cord: pass, P_SC_floor_end_bites_aerial_master_off: pass, P_SC_floor_end_cord_behind_spares: pass, P_SC_floor_end_dead_spares: pass, P_SC_floor_end_every_end_over_spark_budget: pass, P_SC_floor_end_fixer_spared_other_builder_shocked: pass, P_SC_floor_end_live_shocks: pass, P_SC_floor_end_unfinished_run_bites: pass, P_SC_no_two_cords_alike: pass, P_SC_restring_drafted_no_job: pass, P_SC_restring_work_scheduler_takes_it: pass, P_SC_shock_reach_deck_cord_per_value: pass, P_SC_shock_reach_default_all: pass, P_SC_shock_reach_three_values: pass, P_SC_sparse_room_no_tangle: pass, P_SC_splicer_spared_bystander_shocked: pass, P_SC_statics_clear_between_games: pass, P_SC_under_battery_dry: pass, P_SC_under_furniture_dry: pass, P_SC_under_item_stack_dry: pass, P_SC_under_junction_piece_dry: pass, P_SC_under_liquid_pit: pass, P_SL1_save_landed_new_file_only: pass, P_SL2_save_names_no_class_of_ours: pass, P_SL3_after_load_census_equal: pass, P_ST1_styles_textures_load: pass, P_ST2_switch_changes_textures: pass, P_ST3_extcord_colour_modes: pass, P_ST4_settings_roundtrip: pass, P_ST5_restore_default_and_master: pass, P_SW1_highlight_off_draws_no_ring: pass, P_SW2_lod_off_far_zoom_draws_full: pass, P_SW3_break_readout_off_no_glow_no_whip: pass, P_SW4_sparks_only_overlay_shut_no_glow: pass, P_SW5_hide_hookup_off_leaves_vanilla_wire: pass, P_SW6_needless_loops_off_reaches_builder: pass, P_Z_log_budget: pass, sc_conduit_invisible: pass, sc_cords_slack: pass, sc_cords_under_items: pass, sc_cut_ends: pass, sc_dense_tangle: pass, sc_fallen_span: pass, sc_floor_end_shock: pass, sc_four_looks: pass, sc_fuel_ignition: pass, sc_gravship: pass, sc_junction_strips: pass, sc_no_repeat: pass, sc_no_sharp_turn: pass, sc_owner_change: pass, sc_removal_consequence: pass, sc_restring: pass, sc_rewire_cost: pass, sc_settings: pass, sc_shock: pass, sc_shock_reach: pass, sc_shock_restring: pass, sc_spans: pass, sc_statics_new_game: pass, sc_tap_theft: pass, sc_true_to_grid: pass, sc_walk: pass, sc_walls: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_GSS_011_FOUR_CHANGES_LOOK_20261122.rws
exit_met: true
```
