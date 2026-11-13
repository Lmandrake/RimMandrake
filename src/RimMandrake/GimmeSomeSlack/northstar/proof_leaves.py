#!/usr/bin/env python3
"""Which leaf of the Designer's tree (design/concepts/GimmeSomeSlack/tree.json) each GSS proof row is evidence for.

Owner, by card 2026-11-13 (OWNER:1794594173709591776): "Re-key proof rows to the tree's leaf ids and restore his 2026-11-07
'no sharp turn' bar to the tree". Before this map, 0 of the tree's 23 leaves were cited by any row
(D:\\ClaudeWork\\rimmandrake\\conductor\\carryover_20261112\\gss\\tree_reconcile.md). validation.ROW_SHOWS stays: it is the
north-star wiring `modcheck floor` reads (must-show ids, a different key space); every id it names must be a root of a leaf
the same row cites here (selftest_gss_proof_leaves.py).

A row cites a leaf it is evidence FOR, not a leaf it proves whole: a leaf whose every row passes is not thereby met.
The only rows citing no leaf are SITE_ROWS, the preflight block: they check the test site the proof stands on, and a FAIL
there voids the run instead of measuring the mod.

PROOF_ROWS is the row set the proof lines produce: proof_all --live (156 rows, J20261113T075443Z-3da526 on SteveDesktop at
35aaf354ea), proof_all's offline tier (validation.OFFLINE_IDS), gravship_scene on/off and selftest_gss_no_hose. A live run
names any row of its own that cites nothing (proof_all.summary), so a new row cannot slip in uncited for long.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TREE = os.path.join(REPO, "design", "concepts", "GimmeSomeSlack", "tree.json")

SITE_ROWS = {"P1_fresh_map", "P2_tier_running_startup_log_clean", "P3_probes_site_pinned_region_empty"}

# A leaf with no row yet, each owed by a LIVE item (infrastructure/state/items/<ID>.md, not closed/): the selftest stays green only
# while that item is open, so closing it without adding the rows turns the selftest red. Nothing else may be listed here.
OWED = {
    "floor_end_shocks_crossers": "RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO",   # Designer stage 3, 2026-11-13; unbuilt
    "shock_reach_setting": "RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO",
}

_MATRIX = {
    "MX_D00_n1_S0": ["dense_block_tangle", "drawing_true_to_grid"],
    "MX_D05_n10_S1": ["dense_block_tangle", "drawing_true_to_grid"],
    "MX_D10_n100_S2": ["dense_block_tangle", "drawing_true_to_grid"],
    "MX_D15_n1000_S3": ["dense_block_tangle", "drawing_true_to_grid"],
    "MX_C00_empty": ["drawing_true_to_grid"],
}
for _f in ("F00_T0_S0", "F04_T1_S0", "F11_T2_S3", "F13_T3_S1", "F18_T4_S2", "F21_T5_S1", "F25_T6_S1", "F30_T7_S2", "F33_T8_S1",
           "F39_T9_S3", "F42_T10_S2", "F47_T11_S3", "F51_T12_S3", "F54_T13_S2", "F56_T14_S0", "F60_T15_S0"):
    _MATRIX["MX_" + _f] = ["cords_lie_slack", "drawing_true_to_grid"]
for _a in ("A04_N3_R12_fallen", "A05_N3_R19_up", "A06_N5_R6_fallen", "A07_N5_R12_up", "A08_N5_R19_cut", "A09_N2_R6_cut",
           "A10_N2_R12_fallen", "A11_N2_R19_up", "A12_N3_R6_fallen"):
    _MATRIX["MX_" + _a] = {"fallen": ["fallen_span_on_ground", "drawing_true_to_grid"],
                           "up": ["spans_above_everything", "drawing_true_to_grid"],
                           "cut": ["cut_live_and_dead_ends", "fallen_span_on_ground", "drawing_true_to_grid"]}[_a.rsplit("_", 1)[1]]

ROW_LEAVES = dict(_MATRIX, **{
    # core block (validation.live_battery)
    "M1_conduit_transparent": ["conduit_invisible"],
    "M1_cords_exist": ["conduit_invisible", "drawing_true_to_grid"],
    "M1_node_census": ["drawing_true_to_grid", "cords_meet_walls_at_face"],
    "M1c_end_pieces": ["cords_meet_walls_at_face", "strip_at_every_junction"],
    "M2b_no_vertex_unwalkable": ["cords_meet_walls_at_face"],
    "M2c_no_sharp_bends": ["no_unforced_sharp_turn"],
    "M6_overlay_lines_intact": ["conduit_invisible"],
    "M5_local_invalidation": ["no_stall_on_rewire"],
    "M8_break_two_ends_live_dead": ["cut_live_and_dead_ends"],
    "M2_cords_only_within_net": ["drawing_true_to_grid"],
    "B1_rope_settle": ["cords_lie_slack"],
    "B6_tangle_lit_strips": ["dense_block_tangle"],
    "B3c_spark_rides_whip": ["cut_live_and_dead_ends"],
    "B3_whip_live_ends": ["cut_live_and_dead_ends"],
    "SW3_break_readout_off_no_glow_no_whip": ["settings_switch_cleanly", "cut_live_and_dead_ends"],
    "SW4_sparks_only_overlay_shut_no_glow": ["settings_switch_cleanly", "cut_live_and_dead_ends"],
    "B4_downed_wire_bursts": ["cut_live_and_dead_ends"],
    "B4b_sparks_thrown_ticking": ["cut_live_and_dead_ends"],
    "B4c_spark_intensity_scales_downed": ["cut_live_and_dead_ends"],
    "B4d_spark_budget_shared_visible_first": ["cut_live_and_dead_ends", "no_stall_on_rewire"],
    "M1e_machine_on_inwall_run_draws_a_cord": ["conduit_invisible", "cords_meet_walls_at_face"],
    "M1f_machine_on_hidden_conduit_draws_none": ["conduit_invisible"],
    "B7_sway_cpu_two_frame": ["settings_switch_cleanly", "no_stall_on_rewire"],
    "B7b_sway_shader_path": ["settings_switch_cleanly"],
    "B7c_floor_ripple": ["settings_switch_cleanly"],
    "B5_selection_highlight": ["drawing_true_to_grid", "settings_switch_cleanly"],
    "SW1_highlight_off_draws_no_ring": ["settings_switch_cleanly"],
    "SW2_lod_off_far_zoom_draws_full": ["settings_switch_cleanly"],
    "B8_lod_far_zoom": ["no_stall_on_rewire", "settings_switch_cleanly"],
    "B9_cutscene_guard_idle": ["gravship_keeps_connections"],
    "B6b_strips_dark_when_dead": ["cut_live_and_dead_ends", "dense_block_tangle"],
    "M10_tangle_threshold_setting": ["settings_switch_cleanly", "dense_block_tangle"],
    "M11_dive_through_setting": ["settings_switch_cleanly", "cords_meet_walls_at_face"],
    "M12a_slide_under_off_plug_on_cell_centre": ["settings_switch_cleanly", "drawing_true_to_grid"],
    "M12b_slide_under_on_plug_off_centre": ["drawing_true_to_grid", "settings_switch_cleanly"],
    "B13_hidden_conduit_hookup_not_drawn": ["conduit_invisible"],
    "SW5_hide_hookup_off_leaves_vanilla_wire": ["settings_switch_cleanly"],
    "SW6_needless_loops_off_reaches_builder": ["settings_switch_cleanly", "cords_lie_slack"],
    "B12_shader_sway_far_zoom_drawn_once": ["no_stall_on_rewire", "settings_switch_cleanly"],
    "P1B_perf_rebuild": ["no_stall_on_rewire"],
    "A8_same_frame_dirty_not_dropped": ["no_stall_on_rewire"],
    "ST1_styles_textures_load": ["four_looks_one_run"],
    "ST2_switch_changes_textures": ["four_looks_one_run", "settings_switch_cleanly"],
    "ST3_extcord_colour_modes": ["four_looks_one_run", "settings_switch_cleanly"],
    "ST4_settings_roundtrip": ["settings_switch_cleanly"],
    "ST5_restore_default_and_master": ["settings_switch_cleanly"],
    "M8c_source_off_reads_dead_250": ["cut_live_and_dead_ends"],
    "M7_off_restores_vanilla": ["settings_switch_cleanly"],
    "M7b_on_again_invisible": ["conduit_invisible", "settings_switch_cleanly"],
    # aerial block
    "M13a_linked_one_net_across_gap": ["spans_above_everything", "drawing_true_to_grid"],
    "M13b_far_consumer_powered": ["drawing_true_to_grid"],
    "M13c_unlink_two_nets_relink_one": ["drawing_true_to_grid"],
    "M13d_refusals": ["drawing_true_to_grid"],
    "M13e_hostile_mast_not_autolinked": ["drawing_true_to_grid"],
    "R1_span_altitude_above_pawns_below_blueprints": ["spans_above_everything"],
    "R2_spans_and_heads_drawn": ["spans_above_everything"],
    "M14_gap_control_without_fix": ["fallen_span_on_ground", "drawing_true_to_grid"],
    "M14a_remove_middle_both_ends_resolve": ["fallen_span_on_ground", "cut_live_and_dead_ends"],
    "M14b_dead_pole_drops_live_and_dead_cords": ["fallen_span_on_ground"],
    "M14c_live_tip_glows": ["fallen_span_on_ground", "cut_live_and_dead_ends"],
    "M15_explosion_cuts_span": ["fallen_span_on_ground"],
    "M15a_wire_down_alert_lists_cut": ["restring_cut_span"],
    "M15b_restring_rejoins": ["restring_cut_span"],
    "M15c_wire_down_alert_clears_on_restring": ["restring_cut_span"],
    "M15e_restring_is_a_colonist_job": ["restring_cut_span"],
    "M15f_restring_joined_run_one_look": ["restring_cut_span", "four_looks_one_run"],
    "M15d_diagonal_cut_halves_meet_on_line": ["fallen_span_on_ground"],
    "R3_sway_proxy": ["settings_switch_cleanly", "spans_above_everything"],
    "M19_tap_drains_one_way": ["tap_steals_and_costs_goodwill"],
    "M19n_taps_off_control": ["tap_steals_and_costs_goodwill", "settings_switch_cleanly"],
    "M19m_tap_mixed_net_connects_own_conduit": ["tap_steals_and_costs_goodwill", "drawing_true_to_grid"],
    "M17_owner_change_cuts_cross_owner_wires": ["owner_change_coils_wires"],
    "M20a_fallen_wire_shock_flip": ["fallen_wire_shocks_crossers", "settings_switch_cleanly"],
    "M20b_fallen_wire_knockback_flip": ["fallen_wire_shocks_crossers", "settings_switch_cleanly"],
    "M20c_fallen_wire_ignites_flip": ["live_wire_lights_fuel", "settings_switch_cleanly"],
    "M20e_shock_cells_die_with_wire": ["fallen_wire_shocks_crossers"],
    "M20d_keep_wires_setting_roundtrip": ["gravship_keeps_connections", "settings_switch_cleanly"],
    "M21a_cut_wires_on_owner_change_off_keeps_link": ["owner_change_coils_wires", "settings_switch_cleanly"],
    "M21b_cut_wires_on_owner_change_on_cuts_link": ["owner_change_coils_wires", "settings_switch_cleanly"],
    "M21c_drip_loops_off_plain_curve": ["settings_switch_cleanly", "spans_above_everything"],
    "M21d_drip_loops_on_loop_samples": ["settings_switch_cleanly", "spans_above_everything"],
    "M22a_kinetic_sway_on_swings_never_cuts": ["settings_switch_cleanly", "spans_above_everything"],
    "M22b_kinetic_sway_off_does_nothing": ["settings_switch_cleanly"],
    "M21e_keep_wires_on_gravship_off_setting_state": ["gravship_keeps_connections", "settings_switch_cleanly"],
    "M21f_keep_wires_on_gravship_on_setting_state": ["gravship_keeps_connections", "settings_switch_cleanly"],
    # style block
    "S1_pick_reaches_blueprint": ["four_looks_one_run"],
    "S2_blueprint_frame_building": ["four_looks_one_run"],
    "S3_god_mode": ["four_looks_one_run"],
    "S4_copy_carries_look": ["four_looks_one_run"],
    "S5_reinstall_keeps_look": ["four_looks_one_run"],
    "S8_legacy_unstyled_draws_default": ["four_looks_one_run"],
    "S8b_legacy_joined_to_styled_stores_look": ["four_looks_one_run"],
    "S6_spans_in_pole_look": ["four_looks_one_run", "spans_above_everything"],
    "S9a_two_runs_two_styles": ["four_looks_one_run"],
    "S9b_bridge_largest_wins": ["four_looks_one_run"],
    "S9c_split_keeps_styles": ["four_looks_one_run"],
    "S9d_restyle_and_materials": ["four_looks_one_run"],
    "S10_legacy_default_materials": ["four_looks_one_run"],
    "S11_lamp_master_off_vanilla": ["settings_switch_cleanly", "four_looks_one_run"],
    "S12a_D1_legacy_run_one_look": ["four_looks_one_run"],
    "S12b_D7_bulk_spawn_cost": ["no_stall_on_rewire", "four_looks_one_run"],
    "S12c_D5_multilink_one_frame": ["four_looks_one_run", "no_stall_on_rewire"],
    "S12e_batched_links_merge": ["four_looks_one_run"],
    "S7_save_load_styles": ["four_looks_one_run", "walk_scavenger_base"],
    "S12d_D4_pending_queue_save": ["four_looks_one_run", "walk_scavenger_base"],
    # scenes block (scene_rows.ROWS)
    "SC_doorway_run_is_one_cord": ["drawing_true_to_grid"],
    "SC_cut_never_powered_both_dead": ["cut_live_and_dead_ends"],
    "SC_cut_battery_each_side_both_live": ["cut_live_and_dead_ends"],
    "SC_bend_draws_no_joint_tee_draws_one": ["strip_at_every_junction", "drawing_true_to_grid"],
    "SC_sparse_room_no_tangle": ["dense_block_tangle"],
    "SC_cords_all_slack": ["cords_lie_slack"],
    "SC_no_two_cords_alike": ["cords_never_repeat", "cord_shape_variation_probe"],
    "SC_restring_drafted_no_job": ["restring_cut_span"],
    "SC_restring_work_scheduler_takes_it": ["restring_cut_span"],
    "SC_splicer_spared_bystander_shocked": ["fallen_wire_shocks_crossers"],
    "SC_dead_wire_shocks_nobody": ["fallen_wire_shocks_crossers", "cut_live_and_dead_ends"],
    "SC_dead_wire_lights_no_fuel": ["live_wire_lights_fuel"],
    # determinism, save/load, log, statics blocks (the walk leaf's reload and log-clean reads, measured short)
    "D1_zero_tick_rereads_same": ["drawing_true_to_grid"],
    "D2_fresh_builder_same": ["drawing_true_to_grid"],
    "SL1_save_landed_new_file_only": ["walk_scavenger_base"],
    "SL2_save_names_no_class_of_ours": ["walk_scavenger_base"],
    "SL3_after_load_census_equal": ["walk_scavenger_base", "drawing_true_to_grid"],
    "Z_log_budget": ["walk_scavenger_base"],
    "SC_statics_clear_between_games": ["statics_clear_between_games"],
    # offline tier (validation.OFFLINE_IDS)
    "O1_mod_files": ["conduit_invisible", "four_looks_one_run"],
    "O2_settings_defaults": ["settings_switch_cleanly"],
    "O3_core_selftest": ["drawing_true_to_grid", "cords_lie_slack"],
    "O3n_selftest_can_fail": ["drawing_true_to_grid"],
    "O4_python_oracle": ["drawing_true_to_grid"],
    "O5_style_art_sane": ["four_looks_one_run"],
    "O6_review_round1": ["spans_above_everything", "four_looks_one_run"],
    "O7_gpt_read_fixes": ["walk_scavenger_base"],
    "O8_lamp_mast_vanilla_register": ["spans_above_everything"],
    # gravship_scene on/off (A2/A3) and the offline hose scan
    "GS1_keep_wires_on_gravship_on_aboard_span_flies": ["gravship_keeps_connections"],
    "GS1_keep_wires_on_gravship_off_aboard_span_taken_down": ["gravship_keeps_connections"],
    "selftest_gss_no_hose": ["no_hose_in_gss"],
})

PROOF_ROWS = sorted(SITE_ROWS | set(ROW_LEAVES))


def leaves_of(tree_path=TREE):
    with open(tree_path, encoding="utf-8") as f:
        return {l["id"]: l for l in json.load(f)["leaves"]}


def uncited(row_ids, row_leaves=None):
    """Row ids (in order) that cite no leaf and are not preflight site rows."""
    rl = ROW_LEAVES if row_leaves is None else row_leaves
    return [r for r in row_ids if r not in SITE_ROWS and not rl.get(r)]


def problems(row_ids, leaves, row_leaves=None, row_shows=None, owed=None):
    """Every way the map fails the card: a row citing none, a cited id that is no leaf, a leaf no row cites (unless a live
    item owes it, OWED), a north-star id
    (validation.ROW_SHOWS) a row claims that is a root of none of the leaves it cites."""
    rl = ROW_LEAVES if row_leaves is None else row_leaves
    out = ["row %s cites no leaf" % r for r in uncited(row_ids, rl)]
    out += ["row %s cites %s, not a leaf of the tree" % (r, x) for r in row_ids for x in rl.get(r) or () if x not in leaves]
    cited = {x for r in row_ids for x in rl.get(r) or ()}
    ow = OWED if owed is None else owed
    live = lambda i: os.path.isfile(os.path.join(REPO, "infrastructure", "state", "items", "%s.md" % i))  # noqa: E731
    out += ["leaf %s has no row" % lid + (" (owed by %s, which is not a live item)" % ow[lid] if lid in ow else "")
            for lid in leaves if lid not in cited and not (lid in ow and live(ow[lid]))]
    out += ["OWED names %s, which a row already cites: delete the entry" % lid for lid in ow if lid in cited]
    out += ["OWED names %s, not a leaf of the tree" % lid for lid in ow if lid not in leaves]
    for r, shows in (row_shows or {}).items():
        roots = {x for lid in rl.get(r) or () for x in (leaves.get(lid) or {}).get("root") or ()}
        out += ["row %s shows %s, a root of none of its leaves %s" % (r, s, rl.get(r)) for s in shows if s not in roots]
    return out
