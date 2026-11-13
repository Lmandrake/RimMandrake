#!/usr/bin/env python3
# selftest-timeout: 30
"""Every GSS proof row cites a leaf of the Designer's tree, and every leaf has a row (owner, by card 2026-11-13,
OWNER:1794594173709591776: "Re-key proof rows to the tree's leaf ids and restore his 2026-11-07 'no sharp turn' bar to the
tree"). The map is northstar/proof_leaves.py; the tree is design/concepts/GimmeSomeSlack/tree.json.

Oracles, each independent of the map's own key list:
  LIVE_RUN: the 157 row ids proof_all --live printed in J20261113T075443Z-3da526 (SteveDesktop, 35aaf354ea; the log names
            S12d twice and 156 rows in its JSON). Each must cite a leaf or be a preflight SITE row.
  the code's own row lists, read by ast (no import, no game): validation.OFFLINE_IDS, validation.ROW_SHOWS and ROW_TOGGLES
            keys, scene_rows.ROWS, gravship_scene.ROW_IDS.
  the tree: every leaf has a row, or is in proof_leaves.OWED under a live item; every cited id is a leaf; every north-star id a row shows (validation.ROW_SHOWS) is a root
            of a leaf that row cites; the no-sharp-turn leaf exists, roots in never_taut_straight_cord, carries his words on
            the sheet (OWNER:1794107260790205247) and is cited by M2c_no_sharp_bends.
Planted faults, each must go red by name: a row stripped of its leaves, a row citing a non-leaf, a leaf added with no row,
a shows id outside the row's leaf roots, an OWED leaf whose item is not live, an OWED leaf a row already cites, and the
base tree (no no_unforced_sharp_turn leaf).
--tree PATH runs the real checks against another tree (the base: `git show HEAD~:design/concepts/GimmeSomeSlack/tree.json`).
Exit 0 green, 1 red, 2 a planted fault was not caught.
"""
import ast
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proof_leaves as PL  # noqa: E402

MOD = os.path.dirname(HERE)
SHEET = os.path.join(PL.REPO, "design", "concepts", "GimmeSomeSlack", "sheet.md")
SHARP = "no_unforced_sharp_turn"
HIS = "OWNER:1794107260790205247"

LIVE_RUN = """
    P1_fresh_map P2_tier_running_startup_log_clean P3_probes_site_pinned_region_empty MX_D00_n1_S0 MX_F00_T0_S0 
    MX_F04_T1_S0 MX_F11_T2_S3 MX_D05_n10_S1 MX_F13_T3_S1 MX_F18_T4_S2 MX_F21_T5_S1 MX_F25_T6_S1 MX_F30_T7_S2 MX_F33_T8_S1 
    MX_D15_n1000_S3 MX_F39_T9_S3 MX_D10_n100_S2 MX_F42_T10_S2 MX_F47_T11_S3 MX_F51_T12_S3 MX_F54_T13_S2 MX_F56_T14_S0 
    MX_F60_T15_S0 MX_A04_N3_R12_fallen MX_A05_N3_R19_up MX_A06_N5_R6_fallen MX_A07_N5_R12_up MX_A08_N5_R19_cut 
    MX_A09_N2_R6_cut MX_A10_N2_R12_fallen MX_A11_N2_R19_up MX_A12_N3_R6_fallen MX_C00_empty M1_conduit_transparent 
    M1_cords_exist M1_node_census M1c_end_pieces M2b_no_vertex_unwalkable M2c_no_sharp_bends M6_overlay_lines_intact 
    M5_local_invalidation M8_break_two_ends_live_dead M2_cords_only_within_net B1_rope_settle B6_tangle_lit_strips 
    B3c_spark_rides_whip B3_whip_live_ends SW3_break_readout_off_no_glow_no_whip SW4_sparks_only_overlay_shut_no_glow 
    B4_downed_wire_bursts B4b_sparks_thrown_ticking B4c_spark_intensity_scales_downed 
    B4d_spark_budget_shared_visible_first M1e_machine_on_inwall_run_draws_a_cord M1f_machine_on_hidden_conduit_draws_none 
    B7_sway_cpu_two_frame B7b_sway_shader_path B7c_floor_ripple B5_selection_highlight SW1_highlight_off_draws_no_ring 
    SW2_lod_off_far_zoom_draws_full B8_lod_far_zoom B9_cutscene_guard_idle B6b_strips_dark_when_dead 
    M10_tangle_threshold_setting M11_dive_through_setting M12a_slide_under_off_plug_on_cell_centre 
    M12b_slide_under_on_plug_off_centre B13_hidden_conduit_hookup_not_drawn SW5_hide_hookup_off_leaves_vanilla_wire 
    SW6_needless_loops_off_reaches_builder B12_shader_sway_far_zoom_drawn_once P1B_perf_rebuild 
    A8_same_frame_dirty_not_dropped ST1_styles_textures_load ST2_switch_changes_textures ST3_extcord_colour_modes 
    ST4_settings_roundtrip ST5_restore_default_and_master M8c_source_off_reads_dead_250 M7_off_restores_vanilla 
    M7b_on_again_invisible M13a_linked_one_net_across_gap M13b_far_consumer_powered M13c_unlink_two_nets_relink_one 
    M13d_refusals M13e_hostile_mast_not_autolinked R1_span_altitude_above_pawns_below_blueprints R2_spans_and_heads_drawn 
    M14_gap_control_without_fix M14a_remove_middle_both_ends_resolve M14b_dead_pole_drops_live_and_dead_cords 
    M14c_live_tip_glows M15_explosion_cuts_span M15a_wire_down_alert_lists_cut M15b_restring_rejoins 
    M15c_wire_down_alert_clears_on_restring M15e_restring_is_a_colonist_job M15f_restring_joined_run_one_look 
    M15d_diagonal_cut_halves_meet_on_line R3_sway_proxy M19_tap_drains_one_way M19n_taps_off_control 
    M19m_tap_mixed_net_connects_own_conduit M17_owner_change_cuts_cross_owner_wires M20a_fallen_wire_shock_flip 
    M20b_fallen_wire_knockback_flip M20c_fallen_wire_ignites_flip M20e_shock_cells_die_with_wire 
    M20d_keep_wires_setting_roundtrip M21a_cut_wires_on_owner_change_off_keeps_link 
    M21b_cut_wires_on_owner_change_on_cuts_link M21c_drip_loops_off_plain_curve M21d_drip_loops_on_loop_samples 
    M22a_kinetic_sway_on_swings_never_cuts M22b_kinetic_sway_off_does_nothing 
    M21e_keep_wires_on_gravship_off_setting_state M21f_keep_wires_on_gravship_on_setting_state S1_pick_reaches_blueprint 
    S2_blueprint_frame_building S3_god_mode S4_copy_carries_look S5_reinstall_keeps_look S8_legacy_unstyled_draws_default 
    S8b_legacy_joined_to_styled_stores_look S6_spans_in_pole_look S9a_two_runs_two_styles S9b_bridge_largest_wins 
    S9c_split_keeps_styles S9d_restyle_and_materials S10_legacy_default_materials S11_lamp_master_off_vanilla 
    S12a_D1_legacy_run_one_look S12b_D7_bulk_spawn_cost S12c_D5_multilink_one_frame S12e_batched_links_merge 
    S12d_D4_pending_queue_save SC_cords_all_slack SC_no_two_cords_alike SC_doorway_run_is_one_cord 
    SC_cut_never_powered_both_dead SC_cut_battery_each_side_both_live SC_bend_draws_no_joint_tee_draws_one 
    SC_sparse_room_no_tangle SC_restring_drafted_no_job SC_restring_work_scheduler_takes_it 
    SC_splicer_spared_bystander_shocked SC_dead_wire_shocks_nobody SC_dead_wire_lights_no_fuel D1_zero_tick_rereads_same 
    D2_fresh_builder_same SL1_save_landed_new_file_only SL2_save_names_no_class_of_ours SL3_after_load_census_equal 
    S7_save_load_styles Z_log_budget SC_statics_clear_between_games
""".split()


def literal(path, name):
    """The literal value of the first top-level `name = ...` in `path`."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError("%s not found in %s" % (name, path))


def code_rows():
    v = os.path.join(MOD, "validation.py")
    shows = literal(v, "ROW_SHOWS")
    ids = list(literal(v, "OFFLINE_IDS")) + list(shows) + list(literal(v, "ROW_TOGGLES"))
    ids += literal(os.path.join(HERE, "scene_rows.py"), "ROWS")
    ids += list(literal(os.path.join(HERE, "gravship_scene.py"), "ROW_IDS").values())
    return list(dict.fromkeys(ids)), shows


def check(leaves, row_leaves, shows, rows, owed=None):
    errs = PL.problems(rows, leaves, row_leaves, shows, owed)
    errs += ["map row %s is in no proof line (stale key)" % r for r in row_leaves if r not in rows]
    sharp = leaves.get(SHARP)
    if not sharp:
        errs.append("the tree has no %s leaf (his 2026-11-07 bar)" % SHARP)
    else:
        if "never_taut_straight_cord" not in (sharp.get("root") or ()):
            errs.append("%s does not root in never_taut_straight_cord" % SHARP)
        if SHARP not in (row_leaves.get("M2c_no_sharp_bends") or ()):
            errs.append("M2c_no_sharp_bends does not cite %s" % SHARP)
    return errs


def main(argv):
    tree_path = argv[argv.index("--tree") + 1] if "--tree" in argv else PL.TREE
    leaves = PL.leaves_of(tree_path)
    crow, shows = code_rows()
    rows = list(dict.fromkeys(LIVE_RUN + crow + ["selftest_gss_no_hose"]))
    errs = check(leaves, PL.ROW_LEAVES, shows, rows)
    sheet = open(SHEET, encoding="utf-8").read()
    if tree_path == PL.TREE and not any(l.startswith("- [leaf:%s]" % SHARP) and HIS in l for l in sheet.splitlines()):
        errs.append("sheet.md has no `does` line for %s with his words %s" % (SHARP, HIS))
    cited = {x for r in rows for x in PL.ROW_LEAVES.get(r) or ()}
    print("rows %d (live run %d), leaves %d, cited %d, site rows %d" % (len(rows), len(LIVE_RUN), len(leaves),
          len(cited & set(leaves)), len(PL.SITE_ROWS)))
    for e in errs:
        print("RED  " + e)
    if "--tree" in argv:
        return 1 if errs else 0

    base = copy.deepcopy(PL.ROW_LEAVES)
    mutants = [
        ("row stripped of its leaves", leaves, dict(base, B1_rope_settle=[]), shows, "row B1_rope_settle cites no leaf"),
        ("row cites a non-leaf", leaves, dict(base, B1_rope_settle=["cord_lies_slack_in_loops"]), shows,
         "cites cord_lies_slack_in_loops, not a leaf"),
        ("leaf with no row", dict(leaves, planted_leaf={"id": "planted_leaf", "root": []}), base, shows, "leaf planted_leaf has no row"),
        ("shows outside its leaf roots", leaves, base, dict(shows, M1_conduit_transparent=["one_run_one_style"]),
         "row M1_conduit_transparent shows one_run_one_style"),
        ("owed leaf whose item is not live", leaves, base, shows, "owed by GSS_NO_SUCH_ITEM_PLANTED_HERE, which is not a live item",
         {k: "GSS_NO_SUCH_ITEM_PLANTED_HERE" for k in PL.OWED}),
        ("owed leaf a row already cites", leaves, dict(base, B1_rope_settle=["cords_lie_slack"] + list(PL.OWED)[:1]), shows,
         "which a row already cites"),
        ("tree without the sharp-turn leaf", {k: v for k, v in leaves.items() if k != SHARP}, base, shows,
         "the tree has no %s leaf" % SHARP),
    ]
    mutants = [m if len(m) == 6 else m + (None,) for m in mutants if PL.OWED or not m[0].startswith("owed ")]
    missed = []
    for name, lv, rl, sh, want, ow in mutants:
        got = check(lv, rl, sh, rows, ow)
        hit = any(want in e for e in got)
        print("%-6s planted: %s" % ("caught" if hit else "MISSED", name))
        if not hit:
            missed.append(name)
    if missed:
        return 2
    print("RED: %d" % len(errs) if errs else "GREEN: every row cites a leaf, every leaf has a row or a live item owing it (%d owed)" % len(PL.OWED))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
