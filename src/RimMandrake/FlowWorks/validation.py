"""validation.py -- modcheck suite for RimMandrake FlowWorks (mandrake.rm.flowworks): the WIRING, not the checks.

Densified 2026-10-05 (owner: "simplify and compress the northstar validation script for flow works ... separate the
extension tests"; lessons: design/RimMandrake/northstar_densification_lessons.md). Three layers, three files:

  CORE proof   northstar/validation_v2.py   one live session on one fresh quicktest map (python.exe, --live
               --fresh-map), every mechanism row once, one log budget, one result JSON recorded with
               `modcheck record FlowWorks --result <json> --tier flowworks`. Offline tier O + --mock first.
  EXTENSIONS   northstar/extensions.py      the visual-trial plots (golden site, judge screenshots) and the
               optional-feature toggle chains; run on request (northstar/extension_proof.py), never by the core.
  THIS FILE    which core row is evidence for which north-star bar (`shows=`) and Mod Settings toggle
               (`toggle=`), so `modcheck floor --all` reads coverage off the rows that actually run; plus the
               extension chains, registered unchanged so their own claims and a situational re-run still count.

Chains:
  core_offline       v2's offline tier (O1-O10, O-NEG, O-LIVE-NEG) as rows, 0 ticks, no bridge.
  core_live_rows     v2's live rows. On a live `modcheck run` they report the newest v2 result made AT the current
                     mod hash (the same contract `modcheck record` enforces); with none, each row is UNMEASURED and
                     names the command -- never PASS from a stale or missing result.
  <extension chains> northstar/extensions.py, registered as-is.

Every bar named in ROW_SHOWS is a row that already exists in v2; no check was added or relaxed to claim a bar.
Bars with NO core row (only an extension chain claims them) are listed in EXTENSION_ONLY_BARS: proven by nothing
that runs by default -- that list is the owed promotion work, not a coverage hole to hide.
"""
import glob
import json
import os
import sys

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.join(HERE, "northstar")
if NS not in sys.path:
    sys.path.insert(0, NS)
import extensions as EXT  # noqa: E402

suite = Suite("FlowWorks")
suite.toggles = list(EXT.suite.toggles)

# v2's live rows (selftest_extensions asserts this equals a clean --mock run's row ids, in order)
CORE_LIVE_IDS = [
    "L1_fresh_map", "L2_tier_live", "L3_defs_live", "E1a_cadence_shipped", "L4_site_ready",
    "S1_dig_ladder", "S1n_superdeep_is_max", "S1p_pit_is_grid_only", "S2_fill_clamp", "S3_classification",
    "S4_sink_band", "S5_sticky_limitless", "S6_digToDepth_gate",
    "A0_instrument", "E2_twins_identical", "E2_channels_fill_every_direction", "E2_dry_ring", "E3b_recession_shipped",
    "E5_sink_drains", "E5_inner_holds", "E2s_shared_source_both_fill", "E3_budget_exhaustion",
    "E3n_budget_off_supplies", "E5n_sinks_off", "E5_sinks_back_on", "E2_rerun_determinism", "G_every_cell_vs_oracle",
    "J_workgiver_selection", "J_orders_accepted", "E4_engine_off", "E1b_pulse_clamp", "E1c_cadence_real_scheduler",
    "E4_engine_on_scheduled", "E6n_rain_toggle_off", "E7a_fillin_displaces", "E7b_overflow_sanctioned",
    "E8_player_dig", "E6_roof_readback", "E6_rain_fills_unroofed",
    "P1_width_matrix", "P2_fillin_releases_large", "P3_walk_in_held", "P3f_forced_entry_falls", "P4_ladder_frees", "P4f_ladder_frees_forced",
    "P4b_ladder_raised_strands",
    "P5n_own_faction_carveout",
    "X1_pawn_height_ladder", "X2_pawn_lowers_walking_in", "X3_pawn_rises_walking_out", "X4_pit_wall_over_head",
    "X5_slime_occupant_below_surface", "X7_tar_front_lags_water", "X6_two_fluids_distinct", "X7n_viscosity_off",
    "X8_cover_hides_pit", "X9_cover_deck_uniform", "X8b_cover_occupant_stays_below", "X8c_lid_walker_drawn_at_ground", "X10_canal_fire", "T0n_fluid_switch_refused", "E9_log_budget", "Z_settings_restored",
]

# core row -> the north-star bars (design/validation_walks/RimMandrake/FlowWorks.md `## north star`) whose
# mechanism it proves. The LOOK of each bar is the human review sheet's (human_review.py) and the visual trial's.
ROW_SHOWS = {
    "S1_dig_ladder": ["canal_reads_as_dug_channel", "never_gravel_path", "pit_depth_ladder_legible",
                      "depth_and_fill_jointly_legible"],
    "E8_player_dig": ["canal_reads_as_dug_channel"],
    "L3_defs_live": ["canal_dry_reads_as_obstacle", "filled_excavation_reads_as_obstacle"],
    "S2_fill_clamp": ["fill_tier_legible", "canal_partial_fill_distinct", "depth_and_fill_jointly_legible"],
    "E2_channels_fill_every_direction": ["canal_fill_spreads_along_itself", "canal_fill_front_watchable"],
    "G_every_cell_vs_oracle": ["canal_fill_front_watchable", "canal_partial_fill_distinct"],
    "E2_dry_ring": ["canal_holds_only_the_channel", "never_liquid_on_open_ground"],
    "X7_tar_front_lags_water": ["tar_fill_front_lags_water", "slime_reads_as_viscous_not_water"],
    "X6_two_fluids_distinct": ["fill_fluid_distinct", "canal_reads_as_same_liquid_as_reservoir"],
    "T0n_fluid_switch_refused": ["canal_reads_as_same_liquid_as_reservoir"],
    "E3_budget_exhaustion": ["reservoir_fill_visibly_drops", "never_full_reservoir_after_heavy_draw",
                             "empty_reservoir_stops_flow"],
    "E3b_recession_shipped": ["reservoir_shoreline_recedes"],
    "X5_slime_occupant_below_surface": ["slime_occupant_below_surface"],
    "X1_pawn_height_ladder": ["pawn_height_ladder_legible"],
    "X2_pawn_lowers_walking_in": ["pawn_lowers_on_deeper_cell", "pit_occupant_below_floor", "never_snared_standing"],
    "X3_pawn_rises_walking_out": ["pawn_rises_on_shallower_cell"],
    "X4_pit_wall_over_head": ["pit_walls_have_visible_depth", "pit_trapped_reads_as_trapped", "pit_occupant_below_floor"],
    "S1p_pit_is_grid_only": ["pit_reads_as_hole", "pit_not_vanilla_trap", "never_reads_as_building"],
    "P1_width_matrix": ["pit_reads_at_size"],
    "P3_walk_in_held": ["pit_occupied_distinguishable", "pit_trapped_reads_as_trapped", "never_snared_standing"],
    "X8_cover_hides_pit": ["pit_covered_invisible"],
    "X9_cover_deck_uniform": ["pit_covered_seam_at_max_zoom"],
    "P4_ladder_frees": ["ladder_state_legible"],
    "P4b_ladder_raised_strands": ["ladder_state_legible"],
    "X10_canal_fire": ["canal_burning_reads_as_burning_liquid", "canal_fire_persists", "canal_spent_after_burn"],
}
# bars only an extension chain claims (selftest_extensions asserts this list is exactly the difference)
EXTENSION_ONLY_BARS = ["canal_fire_reaches_reservoir", "reservoir_recharge_progress_visible", "sluice_gate_state_legible",
                       "spikes_read_distinct", "still_water_one_surface_height",
                       # of the 16 bars accepted at the 2026-10-20 sitting, 5 now rest on driver rows (DRIVER_BAR_ROWS); these 11
                       # are claimed by UNMEASURED live components only: no existing driver row measures them
                       "climbing_gear_reads_as_kit", "deep_water_pawn_swims",
                       "geared_pawn_scales_built_wall", "half_metre_water_reads_as_silt",
                       "pipe_meets_building_centre",
                       "pit_cover_unlike_bridge", "portable_ladder_leans_on_its_wall", "pump_hose_joins_at_side_port",
                       "raiders_never_shelter_in_a_cage", "suspension_bridge_reads_hung",
                       "wall_ladder_rides_on_rails"]

# core row -> the Mod Settings toggle it flips (both sides proven in the same row or its pair)
ROW_TOGGLES = {
    "S5_sticky_limitless": "stickyLimitlessEnabled", "S6_digToDepth_gate": "digToDepthEnabled",
    "E3_budget_exhaustion": "sourceBudgetEnabled", "E3n_budget_off_supplies": "sourceBudgetEnabled",
    "E5_sink_drains": "edgeSinksEnabled", "E5n_sinks_off": "edgeSinksEnabled", "E5_sinks_back_on": "edgeSinksEnabled",
    "E4_engine_off": "depthEngineEnabled", "E4_engine_on_scheduled": "depthEngineEnabled",
    "E6_rain_fills_unroofed": "rainFillsExcavationsEnabled", "E6n_rain_toggle_off": "rainFillsExcavationsEnabled",
    "P4b_ladder_raised_strands": "superdeepCapturesOwnFaction", "P5n_own_faction_carveout": "superdeepCapturesOwnFaction",
    "X7_tar_front_lags_water": "viscosityEnabled", "X7n_viscosity_off": "viscosityEnabled",
}
NOT_MEASURED = ("UNMEASURED", "UNBUILT", "UNCOVERED")


def _shows(rid):
    return ROW_SHOWS.get(rid) or HOSE_ROW_SHOWS.get(rid)


def _report_rows(t, rows, declare=()):
    """One component per row, same id. FAIL raises (-> FAIL + finding); UNMEASURED/UNBUILT/UNCOVERED record
    UNMEASURED with the status in the detail. The rows are already-measured, independent results, so a FAIL row
    does not blank the rows after it. Under the declaration probe (no game) `declare` lists the ids to declare,
    so toggle and bar coverage is answerable offline. (Same shape as GimmeSomeSlack/validation.py.)"""
    if not t._guard() and not rows:
        for rid in declare:
            with t.component(rid, toggle=ROW_TOGGLES.get(rid), shows=_shows(rid)):
                pass
        return
    for r in rows:
        st = r["status"]
        with t.component(r["id"], toggle=ROW_TOGGLES.get(r["id"]), shows=_shows(r["id"])):
            if t._guard() and st == "FAIL":
                raise ExpectationFailed("[%s] %s" % (r.get("cls"), str(r.get("detail"))[:600]))
        c = t.components[-1]
        c.evidence.append({"call": "row %s" % r["id"], "result": r})
        if c.verdict == "FAIL":
            t.upstream_failed = False        # this row only; it touched nothing
        elif c.verdict == "PASS":
            # P12 (hose port step 0): a SKIP row never certifies -- it is UNMEASURED, same as an unknown status.
            if st in NOT_MEASURED or st not in ("PASS", "FAIL"):
                c.verdict, c.detail = "UNMEASURED", "%s: %s" % (st, str(r.get("detail"))[:400])
            else:
                c.detail = str(r.get("detail"))[:400]


def _v2():
    import validation_v2 as V2  # noqa: E402 - northstar/ is on sys.path
    return V2


def offline_rows():
    """v2's offline tier as rows; a repeated check id would get a #n suffix (none repeats today: see OFFLINE_IDS)."""
    V2 = _v2()
    checks = V2.run_offline() + [V2.selftest_live_mock()]
    rows, seen = [], {}
    for c in checks:
        seen[c.cid] = seen.get(c.cid, 0) + 1
        rid = "v2_%s" % c.cid if seen[c.cid] == 1 else "v2_%s#%d" % (c.cid, seen[c.cid])
        rows.append({"id": rid, "status": "PASS" if c.ok else "FAIL", "cls": "" if c.ok else "MOD", "detail": c.detail})
    return rows


# exactly offline_rows()' ids, in order (northstar/selftest_extensions.py asserts it): the declaration probe declares these
OFFLINE_IDS = ["v2_O1", "v2_O2", "v2_O3", "v2_O4", "v2_O5", "v2_O6", "v2_O7", "v2_O8", "v2_O9", "v2_O10", "v2_O11", "v2_O-NEG",
               "v2_O-LIVE-NEG"]


def latest_core_result(mod_hash):
    """Newest v2 result JSON made AT `mod_hash` (None if there is none): the only live evidence this suite trusts."""
    best = None
    for p in sorted(glob.glob(os.path.join(NS, "validation_v2_result_*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if d.get("mode") == "live" and d.get("mod_hash") == mod_hash:
            best = (p, d)
    return best


@suite.chain("core_offline")
def core_offline(t):
    """v2 offline tier: defs, shipped settings, UNBUILT register, geometry, pulse oracle (+ selftest), scene
    predictions, schema lint, shared source, pit width, every offline check mutated red, and the --mock live tier
    green with every MockBridge fault turning its row red. 0 ticks."""
    rows = []
    with t.component("offline_tier_ran"):
        if t._guard():
            rows = offline_rows()
    if t.components and t.components[-1].verdict == "PASS":
        _report_rows(t, rows, declare=OFFLINE_IDS)


def core_rows_from(found):
    """Rows for every CORE_LIVE_IDS id, in order, from one v2 result (p, d): an id the run never emitted (an aborted run
    stops early) is UNMEASURED "not emitted by <file>", never silently absent; rows outside CORE_LIVE_IDS (the ABORT row)
    are kept after them."""
    p, d = found
    got = {r["id"]: r for r in d.get("rows") or []}
    why = "not emitted by %s%s" % (os.path.basename(p), " (run aborted: %s)" % str(d["aborted"])[:200] if d.get("aborted") else "")
    rows = [got[rid] if rid in got else {"id": rid, "status": "UNMEASURED", "cls": "HARNESS", "detail": why}
            for rid in CORE_LIVE_IDS]
    return rows + [r for rid, r in got.items() if rid not in set(CORE_LIVE_IDS)]


@suite.chain("core_live_rows")
def core_live_rows(t):
    """v2's live rows, read from the newest v2 result made at the current mod hash. 0 ticks."""
    rows = []
    if t._guard():
        from modcheck import status as _st  # noqa: E402
        found = latest_core_result(_st.mod_hash(HERE))
        if found:
            rows = core_rows_from(found)
        else:
            rows = [{"id": rid, "status": "UNMEASURED", "cls": "HARNESS",
                     "detail": "no v2 live result at the current mod hash: run `python.exe "
                               "src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map`, then "
                               "`modcheck record FlowWorks --result <json> --tier flowworks`"} for rid in CORE_LIVE_IDS]
    _report_rows(t, rows, declare=CORE_LIVE_IDS)


# ============================================================================ the flexible hose (hose port, 2026-10-11)
# Moved from Gimme Some Slack's validation.py with the hose. Offline: FlowWorks/validation_hose_offline.py (HO5-HO8, the hose
# halves of GSS's O5/O6/O7). Live: the hose block rows (validation_hose.py H/M/P/RL/CR, validation_style_hose.py R, the nine
# hose matrix scenes MX_H0*), which only the hose live driver measures (northstar/proof_hose.py, hose port step 8). The newest
# certifiable proof_hose result at the current mod hash is read WHOLE: the HOSE_LIVE_IDS (the rows a bar shows) first, then
# every other row it holds, so a FAIL anywhere in the proof reaches modcheck (hose_rows_from); with no result each
# HOSE_LIVE_IDS row is UNMEASURED naming that driver (hose_live_rows below). Their north-star bars moved to FlowWorks.md.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import validation_hose_offline as HOFF  # noqa: E402

HOSE_ROW_SHOWS = {
    "HO6_hose_fittings": ["hose_joiner_reads_brass_screwed_together"],
    "H2_hose_laid_as_hose_cord": ["hose_thicker_stiffer_than_cord"],
    "MX_H01_Flat_corner_L14": ["hose_thicker_stiffer_than_cord"],
    "H9_stiffness_setting": ["hose_thicker_stiffer_than_cord"],
    "MX_H00_Flat_straight_L6": ["hose_plump_when_flowing_flat_when_not"],
    "MX_H03_Plump_straight_L14": ["hose_plump_when_flowing_flat_when_not"],
    "H6_plump_within_transition": ["hose_plump_when_flowing_flat_when_not"],
    "H8_collapse_after_release": ["hose_plump_when_flowing_flat_when_not"],
    "MX_H04_Plump_corner_L24": ["hose_joiner_reads_brass_screwed_together"],
    "MX_H02_Flat_water_L24": ["never_hose_across_impassable"],
    "R3_laid_out_per_look": ["reel_laid_and_wound_look_differ", "reel_hose_leaves_brass_outlet_nozzle"],
    "R5_reeled_in_per_look": ["reel_laid_and_wound_look_differ"],
    "CR6_retract_stored": ["reel_laid_and_wound_look_differ"],
    "RL3_hose_onto_relay_B": ["relay_chain_reads_connected"],
    "RL4_relay_B_onward_to_C": ["relay_chain_reads_connected"],
    "RL8_chain_beyond_one_hose": ["relay_chain_reads_connected"],
    "RL9_overhead_drawn_over_hose": ["hose_drawn_under_overhead_span"],
    "R2_built_reels_stored_art": ["four_reel_looks_distinguishable"],
    "CR7_no_instant_gizmos_without_devmode": ["reel_offers_choose_style"],
}
# the real-flow bars (hose port step 6, measured by proof_hose.py's realflow block, FINAL §3.6)
HOSE_ROW_SHOWS.update({
    "NS_hose_plumps_only_from_powered_pump": ["hose_plumps_only_from_powered_pump"],
    "NS_hose_carries_real_units": ["hose_carries_real_units"],
    "NS_hose_tint_is_carried_liquid": ["hose_tint_is_carried_liquid"],
    "NS_hose_dropped_carries_nothing": ["hose_dropped_carries_nothing"],
    "NS_hose_port_removed_discovered": ["hose_follows_port_changes"],
    "NS_hose_port_removed_moves": ["hose_follows_port_changes"],
    "NS_hose_far_end_pump": ["hose_far_end_pump_reaches_reel_tank"],
    "NS_relay_chain_carries": ["relay_chain_carries_liquid"],
    "NS_pipe_and_hose_one_net": ["pipe_and_hose_one_net"],
    "NS_tank_does_not_bridge_pipe_runs": ["never_tank_bridges_pipe_runs"],
    "NS_external_pipe_is_visual_only": ["never_external_pipe_carries"],
    "NS_tank_feeds_hose": ["tank_feeds_hose_without_pump"],
})
HOSE_LIVE_IDS = [r for r in HOSE_ROW_SHOWS if r not in HOFF.OFFLINE_IDS]


@suite.chain("hose_offline")
def hose_offline(t):
    """The hose's offline art/source rows (HO5-HO8). 0 ticks."""
    rows = []
    with t.component("hose_offline_ran"):
        if t._guard():
            import io
            import contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                rows = [dict(r, cls=r.get("class")) for r in HOFF.run_offline()]
    if t.components and t.components[-1].verdict == "PASS":
        _report_rows(t, rows, declare=HOFF.OFFLINE_IDS)


def latest_hose_result(mod_hash):
    """Newest proof_hose result JSON made AT `mod_hash`, live and certifiable (None if there is none)."""
    best = None
    for p in sorted(glob.glob(os.path.join(NS, "proof_hose_*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if d.get("mode") == "live" and d.get("certifiable") and d.get("mod_hash") == mod_hash:
            best = (p, d)
    return best


def hose_rows_from(found):
    """Rows for every HOSE_LIVE_IDS id, in order, then EVERY other row of the result: `certifiable` does not require the
    rows to PASS (proof_hose: live, not aborted, nothing raised), so reading only HOSE_LIVE_IDS hid a FAIL in the other
    rows (36 of 66 on 2026-10-11, MX_H05..MX_H08 among them) while the suite read green."""
    p, d = found
    got = {r["id"]: r for r in d.get("rows") or []}
    rows = [dict(got[rid], cls=got[rid].get("class")) if rid in got else
            {"id": rid, "status": "UNMEASURED", "cls": "HARNESS", "detail": "not emitted by %s" % os.path.basename(p)}
            for rid in HOSE_LIVE_IDS]
    return rows + [dict(r, cls=r.get("class")) for rid, r in got.items() if rid not in set(HOSE_LIVE_IDS)]


@suite.chain("hose_live_rows")
def hose_live_rows(t):
    """The hose block rows the hose live driver measures (northstar/proof_hose.py), read from its newest certifiable result
    made AT the current mod hash -- the same contract as core_live_rows; with none, each row is UNMEASURED and names the
    command, never PASS from a stale or missing result. 0 ticks."""
    rows = []
    if t._guard():
        from modcheck import status as _st  # noqa: E402
        found = latest_hose_result(_st.mod_hash(HERE))
        if found:
            rows = hose_rows_from(found)
        else:
            rows = [{"id": rid, "status": "UNMEASURED", "cls": "HARNESS",
                     "detail": "no proof_hose result at the current mod hash: run `python.exe src/RimMandrake/FlowWorks/northstar/"
                               "proof_hose.py --live`, then `modcheck record FlowWorks --result <json>`"} for rid in HOSE_LIVE_IDS]
    _report_rows(t, rows, declare=HOSE_LIVE_IDS)


# RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED: offline switch-flip proofs for the Rivers toggles no live component claims.
# Each is one Case in the C# SelfTest (Source/SelfTest/RiverSwitchFlipChecks.cs, `RiverSwitchFlip_<toggle>`): the
# setting is flipped through its Verse-free RM_RiverMath gate, the outcome must change, and the production call site
# must pass the setting into that gate. Offline proof only -- what a live map decides (a flood spawning, a pawn
# routing, a bruise landing) is still owed to a live row.
RIVER_FLIP_TOGGLES = ["riverWorksEnabled", "scaleWithRiverSize", "floodSurgeEnabled", "countSeasonalFloods",
                      "countTorrentialRainFloods", "carryAnimals", "carryStrangers", "carryItems",
                      "crossingHazardsEnabled", "pathfinderAvoidsCurrents", "weirCatchesDrift"]


_SELFTEST_CASES = {}


def _selftest_cases():
    """Run the FlowWorks C# SelfTest once per process; {case name: "ok"|"FAIL"}, or raise UNMEASURED when it could not run.
    Memoised (review 2026-10-17): ten chains read it and each run is ~80 s; the source cannot change within one suite run.
    A failed run is not memoised, so each chain still reports its own UNMEASURED."""
    if _SELFTEST_CASES:
        return dict(_SELFTEST_CASES)
    import subprocess
    runner = os.path.join(os.path.dirname(os.path.dirname(HERE)), "RimMandrake", "Utils", "selftest_flowworks_stock.py")
    r = subprocess.run([sys.executable, runner], capture_output=True, text=True, timeout=1200)
    cases = {}
    for ln in r.stdout.splitlines():
        if ln.startswith("ok    ") or ln.startswith("FAIL  "):
            cases[ln[6:].strip()] = ln[:4].strip()
    if not cases:
        raise ExpectationFailed("UNMEASURED: the FlowWorks SelfTest did not run (rc=%s): %s"
                                % (r.returncode, (r.stderr or r.stdout)[-300:]))
    _SELFTEST_CASES.update(cases)
    return dict(cases)


@suite.chain("rivers_switch_flips")
def rivers_switch_flips(t):
    """Offline: each Rivers toggle flipped through its RM_RiverMath gate, plus its call site. 0 ticks, no bridge."""
    cases = {}
    with t.component("rivers_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for tg in RIVER_FLIP_TOGGLES:
        with t.component("flip_" + tg, toggle=tg):
            if t._guard():
                got = cases.get("RiverSwitchFlip_" + tg)
                if got != "ok":
                    raise ExpectationFailed("RiverSwitchFlip_%s: %s" % (tg, got or "case missing from the SelfTest output"))


# SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR (owner 2026-10-16): a sluice or grate on a dug canal cell turns so its leaf spans
# between the banks, as a door spans between walls (RM_Patch_FlowDoorFacing on DoorUtility.DoorRotationAt). Offline proof
# of the verdict on small grids and the call site (Source/SelfTest/FlowDoorFacingChecks.cs). OWED live: a sluice and a grate
# placed in a N-S and an E-W canal (one superdeep), blueprint and finished door both drawn across the channel.
FLOW_DOOR_FACING_CASES = ["FlowDoorFacing_spans_between_the_banks", "FlowDoorFacing_superdeep_channel_is_not_a_wall",
                          "FlowDoorFacing_ends_bends_and_mouths", "FlowDoorFacing_gates_side_by_side_form_one_barrier",
                          "FlowDoorFacing_walls_still_win_and_dry_ground_is_vanilla",
                          "FlowDoorFacing_call_site_is_vanilla_door_rotation"]


@suite.chain("flow_door_facing")
def flow_door_facing(t):
    """Offline: sluices and grates turn across their canal (RM_FlowDoorFacingMath + call site). 0 ticks, no bridge."""
    cases = {}
    with t.component("flow_door_facing_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in FLOW_DOOR_FACING_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    with t.component("flow_door_facing_live"):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- sluice and grate drawn across a N-S, an E-W and a "
                                    "superdeep canal, blueprint and finished door (SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR)")


# still_water_one_surface_height (owner R9, 2026-10-17, OWNER.jsonl tsn 1792258162801304562): every square of a connected
# still body at one surface height within 1 cm, read from game state. Measuring script: northstar/level_surface_bar.py, which
# reads RM_NorthstarProofs.ProofLevelSurface (WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES); UNMEASURED on a DLL without it.
@suite.chain("water_level_surface")
def water_level_surface(t):
    """Live state read: the worst surface gap inside any connected still body is under 1 cm (run on a settled site)."""
    with t.component("level_surface_within_1cm", shows=["still_water_one_surface_height"]):
        if t._guard():
            import level_surface_bar
            level_surface_bar.measure(t)


# PIT_LADDER_REDRAW_HUNG_ON_THE_WALL (owner 2026-10-16: "installed along a side of the pit, like a door to a room"): the
# ladder stands on the pit square hung on ONE wall (its rotation; auto-turned to the biggest drop), joins only that wall,
# and slid up holds everyone below. Offline proof of the wall verdict, the state->climb rule and the call sites
# (Source/SelfTest/LadderWallChecks.cs). OWED live: review map stations hold_ladder / hold_ladder_raised -- a ladder on each
# of N, S, W, E drawn against its wall; a colonist climbs out by a slid-down one and not by a slid-up one; a colonist in a
# corner square does not climb out over the wall the ladder does NOT hang on; per-wall art once installed.
LADDER_WALL_CASES = ["LadderWall_placed_rotation_stands_on_a_wall", "LadderWall_auto_turns_to_the_biggest_drop",
                     "LadderWall_no_wall_refused", "LadderWall_joins_only_the_wall_it_hangs_on",
                     "LadderWall_slid_up_holds_everyone_slid_down_is_the_prison_door", "LadderWall_call_sites"]


@suite.chain("ladder_hung_on_wall")
def ladder_hung_on_wall(t):
    """Offline: the pit ladder hangs on one wall (RM_LadderWallMath + call sites). 0 ticks, no bridge."""
    cases = {}
    with t.component("ladder_wall_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in LADDER_WALL_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    with t.component("ladder_wall_live"):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- ladders on N/S/E/W walls drawn against their wall, "
                                    "slid down climbed and slid up not, no climb over a wall it does not hang on "
                                    "(PIT_LADDER_REDRAW_HUNG_ON_THE_WALL; review map hold_ladder / hold_ladder_raised)")


# North-star bars that rest on rows an existing live driver ALREADY measures (K3, 2026-10-21): bar -> [(driver result row ids that
# must ALL be PASS at the current mod hash and deployed DLL, why those rows are the bar)]. Read by _bar_chain(rows=...) through
# driver_rows_at; no row at the current hash = UNMEASURED naming the driver, never PASS. Each id must exist in its driver (the
# selftest greps the driver source). Look halves of a bar stay the human review sheet's; the rest of the 21 former extension-only
# bars have NO measuring row in any driver yet (EXTENSION_ONLY_BARS says which).
DRIVER_BAR_ROWS = {
    "pawn_walks_under_deck": (("UND_floor_path_walks_under", "UND_both_arrive"), "suspension_bridge_proof.py",
                              "a colonist on a trench floor walks to the far side of an RM_SuspensionBridge deck (production under-path found, "
                              "position read from jawa/order_pawn)"),
    "geared_pawn_climbs_out": (("B4_access_gear_climbs_sheer_4m", "B4_access_no_gear_stays_in"), "live_session.py",
                               "a colonist wearing RM_ClimbingGear leaves a sheer 4 m pit, the gearless control stays in (depth read from game state)"),
    "jump_into_pit_lands_unhurt": (("B4_access_jump_pack_in_no_fall",), "live_session.py",
                                   "a jump-packed colonist lands in a pit with no fall hediff (the flyer/floater halves are the "
                                   "offline PitTravel cases)"),
    "limitless_body_marked": (("B2_readout_sea_never_dry", "B2_readout_drainable_not_endless"), "live_session.py",
                              "an edge-touching painted sea reads 'Endless', a dug square, canal and pond do not"),
    "trench_wall_cover_shown": (("TRENCH_square_on_hit_falls", "TRENCH_one_back_third"), "trench_cover_proof.py",
                                "the hit-chance report of a shot at a colonist in a 1 m trench falls by the trench block (HitReportFor "
                                "with the setting on vs off), square-on and one back from the lip"),
}


def _driver_bar_component(t, live_id, bar):
    """One component `live_id` claiming `bar`, verdict from the driver rows DRIVER_BAR_ROWS names (see above)."""
    ids, drv, what = DRIVER_BAR_ROWS[bar]
    got = None
    if t._guard():
        from modcheck import status as _st  # noqa: E402
        got = driver_rows_at(_st.mod_hash(HERE), dll_sha=repo_dll_sha256())
    with t.component(live_id, shows=[bar]):
        if t._guard():
            miss = [i for i in ids if i not in got]
            if miss:
                raise ExpectationFailed("UNMEASURED: live check owed -- no %s result at the current mod hash and deployed DLL carries %s: "
                                        "run `python.exe src/RimMandrake/FlowWorks/northstar/%s` (%s)" % (drv, ", ".join(miss), drv, what))
            bad = [(i, got[i]) for i in ids if got[i][0].get("status") == "FAIL"]
            if bad:
                raise ExpectationFailed("[%s] %s: %s" % (bad[0][1][0].get("class"), bad[0][1][1], str(bad[0][1][0].get("detail"))[:600]))
            unm = [(i, got[i]) for i in ids if got[i][0].get("status") != "PASS"]
            if unm:
                raise ExpectationFailed("UNMEASURED: %s %s [%s]: %s" % (unm[0][1][1], unm[0][1][0].get("status"), unm[0][1][0].get("class"),
                                                                         str(unm[0][1][0].get("detail"))[:400]))
    if got is not None:
        c = t.components[-1]
        for i in ids:
            if i in got:
                c.evidence.append({"call": "row %s (%s)" % (i, got[i][1]), "result": got[i][0]})
        if c.verdict == "PASS":
            c.detail = "; ".join("%s %s" % (got[i][1], i) for i in ids)[:380]


def _bar_chain(t, ran_id, cases, live_id, bar, owed):
    """The 2026-10-20 bar-fix chains: the C# SelfTest cases that prove the mechanism offline, then ONE live component
    that claims the bar (shows=) and reports UNMEASURED naming the live check until a bridge session runs it (owed)."""
    got = {}
    with t.component(ran_id):
        if t._guard():
            got = _selftest_cases()
    for name in cases:
        with t.component(name):
            if t._guard():
                if got.get(name) != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got.get(name) or "case missing from the SelfTest output"))
    t.upstream_failed = False   # the live row only names what is owed: an offline FAIL above must not blank it
    if bar in DRIVER_BAR_ROWS:  # a driver already measures this bar: read its rows (UNMEASURED until one ran at this hash)
        _driver_bar_component(t, live_id, bar)
        t.upstream_failed = False
        return
    with t.component(live_id, shows=[bar]):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- " + owed)


# FLOWWORKS_ENDLESS_LABEL_WIRE_READOUT_PLAINLY (bar limitless_body_marked; he typed 2026-10-20: "it should simply say
# Endless, for simplicity"). Offline: the mark, the drainable readouts and the call site (Source/SelfTest/RewireChecks.cs).
ENDLESS_CASES = ["Readout_limitless_says_Endless", "Readout_two_numbers_and_the_limitless_mark"]


@suite.chain("limitless_endless")
def limitless_endless(t):
    """Offline: never-drying water reads "Endless", drainable water never does. 0 ticks, no bridge."""
    _bar_chain(t, "endless_selftest_ran", ENDLESS_CASES, "endless_live", "limitless_body_marked",
               "northstar/live_session.py block B2 (rows B2_readout_sea_never_dry + B2_readout_drainable_not_endless): "
               "an edge-touching painted sea reads 'Endless', the dug dry square, canal and pond beside it do not; plus a "
               "river square by mouseover (FLOWWORKS_ENDLESS_LABEL_WIRE_READOUT_PLAINLY)")


# FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE (bar wall_ladder_rides_on_rails; he typed 2026-10-20: "It can be raised from
# either below or above. But it can only be lowered from above."). Offline: the rule and the gizmo / work giver / job call
# sites (Source/SelfTest/LadderWallChecks.cs). The rails ART half of the bar is the art ledger's, judged by eye.
LADDER_RAIL_CASES = ["LadderRails_raise_either_side_lower_only_from_above", "LadderRails_gizmo_job_and_ai_ask_the_rule"]


@suite.chain("ladder_rails_raise_lower")
def ladder_rails_raise_lower(t):
    """Offline: a wall ladder is raised from above or below, lowered only from above. 0 ticks, no bridge."""
    _bar_chain(t, "ladder_rails_selftest_ran", LADDER_RAIL_CASES, "ladder_rails_live", "wall_ladder_rides_on_rails",
               "a lowered wall ladder in a 3 m pit (RM_PromotionProofs.ProofLadder x,z,order_raise / order_lower / read): "
               "(1) ordered up with the only colonist in the pit -> he walks to the ladder square and it reads raised; "
               "(2) ordered down with him still in the pit -> no job, it stays raised (want=False ordered=True); "
               "(3) a second colonist on the rim -> walks to top= and it reads lowered; (4) ordered up from the rim -> "
               "raised; the rails drawn on each of N/S/E/W walls by eye (FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE)")


# FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT (bar jump_into_pit_lands_unhurt; he typed 2026-10-20: "plus flying creatures can
# simply fly in/out, jumping creatures jump in or out, floating creatures float in/out"). Offline: the free-traveller rule,
# the fall rule and every trap / mask / reach / fall call site (Source/SelfTest/PitAccessChecks.cs). The jump-pack and skip
# halves were built by PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS (PitAccess_jumps_and_skips_land_safely). Flight is NEVER
# live-watched (owner 2026-09-25): the live row is a STATE read (RM_PromotionProofs.ProofPitTravel), the look waits for him.
PIT_TRAVEL_CASES = ["PitTravel_fly_jump_float_cross_freely_and_never_fall", "PitTravel_every_trap_mask_reach_and_fall_read_asks_it",
                    "PitAccess_jumps_and_skips_land_safely"]


@suite.chain("pit_travel_fly_jump_float")
def pit_travel_fly_jump_float(t):
    """Offline: jump packs, skips, flyers, jumpers and floaters arrive in a pit unhurt and are never held. 0 ticks."""
    _bar_chain(t, "pit_travel_selftest_ran", PIT_TRAVEL_CASES, "pit_travel_live", "jump_into_pit_lands_unhurt",
               "state reads only, no flight watched: a colonist jump-packed (extensions.py jump landing) and one skipped into "
               "a 3 m pit read health unchanged and descents +0; a MaxFlightTime animal and a race marked RM_PitTravelExtension "
               "(jumps / floats) placed on a pit floor read ProofPitTravel free=True held=False, and a thrown one "
               "(ProofForcedFlyer) takes no fall damage (FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT)")


# FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE (bar pump_hose_joins_at_side_port; he typed 2026-10-20: "No. a HOSE must connect
# at one of the four sides. A solid pipe must only be adjacent and is then drawn undernead to the center of the object as
# ruled previously."). Offline: the port rule, hose couplings gated, pipes unchanged (Source/SelfTest/PumpChecks.cs). The
# drawn port and coupling art is the look half, judged by eye.
PUMP_PORT_CASES = ["PumpPorts_hose_at_a_side_port", "PumpPorts_pipes_join_adjacent_hoses_at_ports",
                   "PipeStub_corner_adjacent_runs_under_to_centre", "PipeStub_tank_corner_joins_and_runs_under"]


@suite.chain("pump_ports_one_per_side")
def pump_ports_one_per_side(t):
    """Offline: a hose joins a pump only at one of its four side ports, one to a port; pipes join wherever adjacent. 0 ticks."""
    _bar_chain(t, "pump_ports_selftest_ran", PUMP_PORT_CASES, "pump_ports_live", "pump_hose_joins_at_side_port",
               "a powered RM_LiquidPump with a reel on its north port and a hose end laid at its east port (hose net probe reads "
               "both linked); a second reel at the north port and a hose end at a corner read uncoupled; a pipe at a corner "
               "and one on a side are both on its net and drawn under to its centre; one port drawn per side by eye "
               "(FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE)")


# The rest of the 16 bars accepted at the 2026-10-20 sitting (commit 70f488619; SELFTEST_SWEEP_FIX_FOUR_REDS_REMAIN): each
# is claimed by ONE live component that reports UNMEASURED naming its live check, after the C# SelfTest cases that already
# prove its mechanism offline. Nothing here is a PASS: every bar below stays owed live work (EXTENSION_ONLY_BARS).
# Look bars ("reads as") are judged by eye on a staged frame; mechanism bars by a state read through the bridge.
WATER_LADDER_CASES = ["P14_one_ladder_maps_metres_to_def_for_every_rung"]


@suite.chain("water_ladder_silt")
def water_ladder_silt(t):
    """Offline: 0.5 m of water maps to RM_WaterThin (the silt rung), 1 m to WaterShallow. 0 ticks, no bridge."""
    _bar_chain(t, "water_ladder_selftest_ran", WATER_LADDER_CASES, "water_silt_live", "half_metre_water_reads_as_silt",
               "a dug channel filled to 0.5 m beside one filled to 1 m on a review map: the 0.5 m squares read grey-brown "
               "silt (terrain RM_WaterThin), the 1 m squares the first blue (WaterShallow), judged by eye "
               "(POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD)")


SWIM_CASES = ["Swim_pawn_dropped_in_deep_water", "Swim_swimmer_vs_nonswimmer_in_2m_8m_and_lake_water",
              "Swim_who_swims_by_race_gene_and_load", "Swim_wired_at_call_sites"]


@suite.chain("deep_water_swims")
def deep_water_swims(t):
    """Offline: a swimmer in water 2 m or deeper swims, a non-swimmer never enters it. 0 ticks, no bridge."""
    _bar_chain(t, "swim_selftest_ran", SWIM_CASES, "swim_live", "deep_water_pawn_swims",
               "a colonist ordered into a 3 m dug pool: drawn at the surface, head and shoulders above it, never on the floor "
               "nor standing on top of it, judged by eye on a staged frame; RM_Swim reads him swimming (DEEP_WATER_BUILD_SWIM_OR_SINK)")


def _trench_cover_selftest():
    """The trench-cover C# SelfTest (SelfTestTrench, net8.0); raise UNMEASURED when it could not run, FAIL when it failed."""
    import subprocess
    runner = os.path.join(os.path.dirname(os.path.dirname(HERE)), "RimMandrake", "Utils", "selftest_flowworks_trench_cover.py")
    r = subprocess.run([sys.executable, runner], capture_output=True, text=True, timeout=1200)
    out = (r.stderr or "") + (r.stdout or "")
    if "UNMEASURED" in out and r.returncode != 0:
        raise ExpectationFailed("UNMEASURED: the trench-cover SelfTest did not run: %s" % out[-300:])
    if r.returncode != 0:
        raise ExpectationFailed("trench-cover SelfTest failed (rc=%s): %s" % (r.returncode, out[-300:]))


@suite.chain("trench_cover_and_raiders")
def trench_cover_and_raiders(t):
    """Offline: the trench-wall cover table (SelfTestTrench). No bridge."""
    with t.component("trench_cover_selftest_ran"):
        if t._guard():
            _trench_cover_selftest()
    t.upstream_failed = False
    # trench_cover_proof.py's square-on and one-back hit-report rows (DRIVER_BAR_ROWS); the chest-deep 1.5 m hole and the
    # breakdown's drawn text line are still the look half (human review sheet)
    _driver_bar_component(t, "trench_cover_live", "trench_wall_cover_shown")
    t.upstream_failed = False
    # the cage guard (RM_TrenchCover.IsCageFor, setting trenchAiAvoidsCages) has NO offline case yet: the live read is all of it
    with t.component("trench_cage_live", shows=["raiders_never_shelter_in_a_cage"]):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- a raid on a map with a climbable trench and a sheer 4 m "
                                    "pocket beside it: every raider that takes cover in the dug ground stands on a square "
                                    "with a way out, none in the pocket; the TRENCH hit-report line reads cage=False for each "
                                    "(RM_TrenchCover.IsCageFor; TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT Q5)")


PIT_GEAR_CASES = ["PitAccess_climbing_gear_climbs_every_step", "PitAccess_gear_is_slow_only_past_the_natural_limit",
                  "PitAccess_portable_ladder_reach", "PitAccess_defs_and_settings_shipped", "PitAccess_call_sites_wired"]


@suite.chain("pit_access_gear_ladders")
def pit_access_gear_ladders(t):
    """Offline: climbing gear climbs out of a sheer pit, a portable ladder reaches only so deep. 0 ticks, no bridge."""
    _bar_chain(t, "pit_access_selftest_ran", PIT_GEAR_CASES, "climb_out_live", "geared_pawn_climbs_out",
               "a colonist wearing RM_ClimbingGear dropped on the floor of a sheer 4 m pit with no ladder: BEFORE frame on the "
               "floor, AFTER frame on the ground beside it, position read from game state (PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS)")
    t.upstream_failed = False
    with t.component("portable_ladder_live", shows=["portable_ladder_leans_on_its_wall"]):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- RM_LadderPortable set in a 2 m pit leans diagonally against "
                                    "the wall it serves and a colonist climbs out by it; one set against a wall too tall for it "
                                    "lies flat and gives no way out, judged by eye and read from game state")
    with t.component("climbing_gear_look", shows=["climbing_gear_reads_as_kit"]):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: look owed -- RM_ClimbingGear on the ground and worn reads as one belt-or-"
                                    "backpack kit of ropes, small grappling hooks and climbing claws, judged by eye on a "
                                    "staged frame (art ledger)")


WALL_CLIMB_CASES = ["WallClimb_unroofed_on_both_sides_and_the_wall", "WallClimb_gear_required_raiders_by_setting",
                    "WallClimb_is_slow_x20", "WallClimb_routes_only_when_shorter", "WallClimb_wiring"]


@suite.chain("wall_scaling_gear")
def wall_scaling_gear(t):
    """Offline: a pawn with climbing gear scales an unroofed built wall, slowly; one without cannot. 0 ticks, no bridge."""
    _bar_chain(t, "wall_climb_selftest_ran", WALL_CLIMB_CASES, "wall_climb_live", "geared_pawn_scales_built_wall",
               "two colonists on one side of an unroofed doorless built wall, one wearing RM_ClimbingGear, both ordered to a "
               "cell on the far side: BEFORE/AFTER frames show the geared one across and the other not, read from game state "
               "(WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS)")


SUSPENSION_CASES = ["Suspension_spans_supports_and_swing_order", "Suspension_deck_built_over_the_hole_floor",
                    "Underpass_band_step_clearance_and_sunken_height", "Underpass_wiring_masks_sites_not_tunnels",
                    "SpanBase_cover_is_the_trap_tier_of_the_base", "SpanBase_cover_read_is_decked_surface_no_underpass"]


@suite.chain("suspension_bridges_and_covers")
def suspension_bridges_and_covers(t):
    """Offline: a suspension deck hangs between end supports over a hole, pawns pass beneath, a cover is the trap tier."""
    _bar_chain(t, "suspension_selftest_ran", SUSPENSION_CASES, "under_deck_live", "pawn_walks_under_deck",
               "a colonist on the floor of a 2 m trench crossed by an RM_SuspensionBridge deck, ordered to the far side: "
               "BEFORE frame on one side of the deck, AFTER on the other, having walked beneath it, position read from game "
               "state (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD; UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL)")
    t.upstream_failed = False
    with t.component("suspension_look", shows=["suspension_bridge_reads_hung"]):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: look owed -- an RM_SuspensionBridge over a dug hole reads as a deck hung "
                                    "between anchors at its two ends, not a floor tile or the game's own bridge, judged by eye "
                                    "(SUSPENSION_ART_RESKIN_HE_SEES_FIRST)")
    with t.component("cover_vs_bridge_look", shows=["pit_cover_unlike_bridge"]):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: look owed -- a pit cover and a suspension bridge side by side: the cover "
                                    "passes for ground, the bridge reads as a built crossing, judged by eye")


@suite.chain("pipes_meet_centre")
def pipes_meet_centre(t):
    """Offline: a pipe or hose beside a tank or machine is drawn on beneath it to its centre. 0 ticks, no bridge."""
    _bar_chain(t, "pipe_centre_selftest_ran", ["PipeStub_1x1_runs_edge_to_centre",
                                               "PipeStub_multicell_enters_at_edge_then_turns_to_centre",
                                               "PipeStub_wiring_shipped"], "pipe_centre_live", "pipe_meets_building_centre",
               "a pipe and a hose each meeting a tank, a pump, a tap and a sprinkler: each drawn running on beneath it to its "
               "centre, seen through its see-through margins and hidden by its solid body, never stopping at its edge, "
               "judged by eye at play zoom (PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE)")


# FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS (owner 2026-10-16): dev-placed flow source and flow sink (Source/MapControls/).
# Offline proof of the rate math, a source and a sink driven through the production kernel with its ledger balanced every
# pulse, and the wiring incl. the mapControlsEnabled master switch gating the pulse (Source/SelfTest/MapControlChecks.cs).
# OWED live: place both on a dug channel (RM_MapControls.PlaceSource / PlaceSink via jawa/static_call), watch the level
# rise and fall, read the L0 ledger (flowSources= / flowSinks=) and see no conservation warning; save and reload.
MAP_CONTROL_CASES = ["MapControl_rate_to_levels", "MapControl_rate_clamps", "MapControl_blocked_source_never_banks",
                     "MapControl_pick_targets", "MapControl_source_and_sink_conserve_through_the_kernel"]
suite.toggles += [t for t in ["mapControlsEnabled"] if t not in suite.toggles]


@suite.chain("flow_map_controls")
def flow_map_controls(t):
    """Offline: flow source / sink math, kernel conservation and wiring (RM_MapControlMath + call sites). 0 ticks, no bridge."""
    cases = {}
    with t.component("map_controls_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in MAP_CONTROL_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    with t.component("MapControl_wiring_and_master_switch", toggle="mapControlsEnabled"):
        if t._guard():
            got = cases.get("MapControl_wiring_and_master_switch")
            if got != "ok":
                raise ExpectationFailed("MapControl_wiring_and_master_switch: %s" % (got or "case missing from the SelfTest output"))
    with t.component("flow_map_controls_live"):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- a flow source and sink on a dug channel move liquid, "
                                    "the L0 ledger shows them and no conservation warning fires; survives save/reload "
                                    "(FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS)")


# FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16): six further dev-placed map controls (Source/MapControls/), all
# small stones: flow meter, level holder, timer switch, map-edge setter, current painter, liquid thermostat. Offline: their
# math (setpoint, schedule, edge rules, thermostat energy), a level holder driven through the production kernel with the
# ledger balanced every pulse, and the wiring into IsSinkCell / the kernel gate / body classification / liquid heat /
# river current, all behind mapControlsEnabled (Source/SelfTest/MapControlChecks.cs).
# OWED live (RM_MapControls static_calls): PlaceMeter/ReadMeter on a dug channel; PlaceLevelHolder holds a channel and a
# limited pond at 50%; PlaceTimer + PulseTimer flips a source and holds a sluice open; PlaceEdgeSetter "ssss" makes an
# edge-touching lake LIMITED and "dddd" drains a dug edge band with edge sinks off (EdgeSinkReport); PlacePainter on a
# hand-dug water channel carries a pawn (CurrentAt); PlaceThermostat + HeatNow moves a roofed room's temperature.
MAP_CONTROL_SIX_CASES = ["MapControl_level_holder_need", "MapControl_level_holder_conserves_through_the_kernel",
                         "MapControl_timer_schedule", "MapControl_edge_rules", "MapControl_thermostat_energy"]


@suite.chain("flow_map_controls_six")
def flow_map_controls_six(t):
    """Offline: meter, level holder, timer, map-edge setter, current painter, thermostat (math, kernel conservation, wiring)."""
    cases = {}
    with t.component("map_controls_six_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in MAP_CONTROL_SIX_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    with t.component("MapControl_six_wiring", toggle="mapControlsEnabled"):
        if t._guard():
            got = cases.get("MapControl_six_wiring")
            if got != "ok":
                raise ExpectationFailed("MapControl_six_wiring: %s" % (got or "case missing from the SelfTest output"))
    for ctl in ["flow_meter", "level_holder", "timer_switch", "map_edge_setter", "current_painter", "liquid_thermostat"]:
        with t.component(ctl + "_live"):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: live check owed -- %s placed by RM_MapControls static_call does its job, "
                                        "the L0 ledger shows no conservation warning, survives save/reload "
                                        "(FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES)" % ctl)


# Hose port review S2/S3 (2026-10-11), liquid networks L4: the tank-jobs switch tankModesEnabled (default on; was tanksFeedHoses). One C#
# SelfTest case flips it through RM_LiquidNetKernel.SettlePlan (jobs vs all-Store) and reads the production call site
# (Source/SelfTest/HoseSwitchFlipChecks.cs, `HoseSwitchFlip_<toggle>`). Offline proof only -- a tank actually draining
# between tanks with jobs on a live map is still owed to a live row (proof_hose).
HOSE_FLIP_TOGGLES = ["tankModesEnabled", "freeEndRolesEnabled", "hoseHoldsLiquid", "liquidTheftEnabled"]   # liquidTheftEnabled lives in RM_MachinerySettings   # liquid networks L4: tanksFeedHoses became tank jobs (rev 2 §3.11)
suite.toggles += [t for t in HOSE_FLIP_TOGGLES if t not in suite.toggles]


@suite.chain("hose_switch_flips")
def hose_switch_flips(t):
    """Offline: each claimed hose toggle flipped through its RM_LiquidNetKernel gate, plus its call site. 0 ticks, no bridge."""
    cases = {}
    with t.component("hose_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for tg in HOSE_FLIP_TOGGLES:
        with t.component("flip_" + tg, toggle=tg):
            if t._guard():
                got = cases.get("HoseSwitchFlip_" + tg)
                if got != "ok":
                    raise ExpectationFailed("HoseSwitchFlip_%s: %s" % (tg, got or "case missing from the SelfTest output"))
    with t.component("tank_feed_refused_add_puts_back"):
        if t._guard():
            got = cases.get("HoseTankFeed_refused_add_puts_back")
            if got != "ok":
                raise ExpectationFailed("HoseTankFeed_refused_add_puts_back: %s" % (got or "case missing from the SelfTest output"))


# RIGID_PIPE_BUILD_WIRE_STYLE_PICKER + FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES (owner rulings 2026-10-11 #1, #4, #6, #8):
# the rigid pipe's four looks through the shared style picker, the build-menu placement, and "pitch stays pitch". Offline
# halves only (Source/SelfTest/PipeStyleChecks.cs); the menu, the look surviving blueprint -> frame -> save and the atlas
# joining up on a map are owed to a live row.
PIPE_LOOK_CASES = ["PipeStyles_looks_are_the_wires_looks", "PipeStyles_resolve_rule", "PipeStyles_shipped_style_defs",
                   "PipeStyles_pipe_is_styleable", "BuildMenu_pipes_and_tanks_in_the_pipe_networks_tab",
                   "Pitch_never_solidifies_in_bulk",
                   # TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH (owner 2026-10-16): the four tanks' looks and their Choose style gizmo
                   "TankStyles_four_looks_per_tank", "TankStyles_choose_style_gizmo"]


@suite.chain("pipe_looks")
def pipe_looks(t):
    """Offline: rigid pipe looks, build-menu placement, no bulk solidification. 0 ticks, no bridge."""
    cases = {}
    with t.component("selftest_cases"):
        if t._guard():
            cases = _selftest_cases()
            bad = {c: cases.get(c) for c in PIPE_LOOK_CASES if cases.get(c) != "ok"}
            if bad:
                raise ExpectationFailed("pipe look cases not ok: %s" % bad)
    with t.component("owned_art_installed"):
        if t._guard():
            looks = ("Scrapper", "Industrial", "Modern", "Futuristic")
            want = [os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Pipe", l, n + ".png")
                    for l in looks for n in ("UniversalPipe_Atlas", "UniversalPipe_MenuIcon")]
            missing = [w for w in want if not os.path.isfile(w)]
            if missing:
                raise ExpectationFailed("pipe art missing: %s" % missing)
    with t.component("tank_art_installed"):
        if t._guard():
            want = [os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Tank", l, d + ".png")
                    for l in ("Scrapper", "Industrial", "Modern", "Futuristic")
                    for d in ("RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall")]
            missing = [w for w in want if not os.path.isfile(w)]
            if missing:
                raise ExpectationFailed("tank art missing: %s" % missing)
    with t.component("tank_choose_style_live"):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- select a built tank, Choose style -> Modern: the art "
                                    "changes in place, survives save/reload; multi-select restyles every selected tank "
                                    "(TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH; review map station tank_styles)")


# LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (owner 2026-10-16: "They too should have the four styles of art."; sheet approved
# 100%; by card: material colour on the TRIM only, body keeps its painted style, liquid in the masked window). Offline: the
# style rules, the shipped style defs / ItemBases / Dubs Bad Hygiene bottles / generated filled defs, and the call sites
# (Source/SelfTest/ContainerStyleChecks.cs); the 24 installed PNGs (12 sprites + 12 masks). OWED live: review map station
# containers_styles -- each look drawn, the window in the liquid's colour, the trim in steel, the body untinted; a bill's
# Style button -> Modern makes Modern bottles; fill/drink/wash keeps the look; two looks never merge on one cell.
CONTAINER_STYLE_CASES = ["ContainerStyle_looks_and_names", "ContainerStyle_tech_default",
                         "ContainerStyle_stacks_keep_looks_apart", "ContainerStyle_window_colours",
                         "ContainerStyle_shipped_style_defs", "ContainerStyle_item_bases_wired",
                         "ContainerStyle_dbh_bottles_masked", "ContainerStyle_call_sites"]


@suite.chain("container_styles")
def container_styles(t):
    """Offline: bottles, buckets and barrels in the four looks (RM_ContainerStyleMath, shipped XML, call sites). 0 ticks."""
    cases = {}
    with t.component("container_style_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in CONTAINER_STYLE_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    with t.component("container_art_installed"):
        if t._guard():
            want = [os.path.join(HERE, "Textures", "Things", "Item", "Resource", "FlowWorks", look, "RM_%s%s.png" % (size, m))
                    for look in ("Scrapper", "Industrial", "Modern", "Futuristic")
                    for size in ("Bottle", "Bucket", "Barrel") for m in ("", "_m")]
            missing = [os.path.relpath(w, HERE) for w in want if not os.path.isfile(w)]
            if missing:
                raise ExpectationFailed("container art missing (%d of 24): %s" % (len(missing), missing[:6]))
    with t.component("container_styles_live"):
        if t._guard():
            raise ExpectationFailed("UNMEASURED: live check owed -- review map station containers_styles: each look drawn, "
                                    "window = liquid colour, trim = steel, body untinted; bill Style button -> Modern makes "
                                    "Modern bottles; fill/drink/wash keeps the look; two looks never merge on one cell "
                                    "(LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS)")


# The two standalone live drivers written on the 2026-10-17 review walk (northstar/thirst_live.py, northstar/sprinkler_live.py)
# each run a SUBSET of rows (--only) and write {script, mode, mod, mod_hash, env.running, env.assembly_sha256, rows}
# (northstar/driver_stamp.py) to northstar/<script>_result_<stamp>.json (their default out; a result written elsewhere is not
# read). A result counts only if its mod_hash is the repo's now AND the game ran the repo's DLL (a run before the deploy of a
# fix must not certify it). The THIRST_LIVE / SPRINKLER_LIVE rows below read
# them: across every result made AT the current mod hash, the newest row per id wins (a later FAIL overrides an earlier PASS);
# a row no such result carries is UNMEASURED naming the driver. T21 / T22 are thirst rows the sprinkler driver measures, so
# both chains read one pool. Same contract as core_live_rows: never PASS from a stale or missing result.
DRIVER_RESULTS = ("thirst_live_result_*.json", "sprinkler_live_result_*.json", "drawbridge_result_*.json", "lines_result_*.json",
                  "suspension_bridge_result_*.json", "trench_cover_proof_result_*.json", "live_session_result_*.json")
DRIVER_OF = {"T21_drinking_reserve": "sprinkler_live.py", "T22_no_brine_spray": "sprinkler_live.py"}


def repo_dll_sha256():
    """sha256 of the committed FlowWorks assembly (None if unreadable)."""
    import hashlib
    try:
        with open(os.path.join(HERE, "Assemblies", "RimMandrakeFlowWorks.dll"), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def driver_rows_at(mod_hash, ns=None, dll_sha=None):
    """{row id: (row, result file basename)} from every live driver result made at `mod_hash` whose game ran the repo's
    DLL (env.assembly_sha256 == `dll_sha`; a result without it is not read), newest per id. Pure but for the reads."""
    found = []
    for g in DRIVER_RESULTS:
        for p in glob.glob(os.path.join(ns or NS, g)):
            try:
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError):
                continue
            if d.get("mode") == "live" and mod_hash and d.get("mod_hash") == mod_hash and dll_sha \
                    and str((d.get("env") or {}).get("assembly_sha256") or "").lower() == dll_sha.lower():
                found.append((str(d.get("started") or ""), os.path.basename(p), d))
    found.sort(key=lambda x: (x[0], x[1]))
    got = {}
    for _, name, d in found:
        for r in d.get("rows") or []:
            if r.get("id"):
                got[r["id"]] = (r, name)
    return got


def _driver_live_report(t, spec, default_driver, item):
    """One component per (id, toggle, bar) of `spec`, its verdict read from driver_rows_at (see above). Each row is an
    independent result, so a FAIL or UNMEASURED row does not blank the rows after it."""
    got = None
    if t._guard():
        from modcheck import status as _st  # noqa: E402
        got = driver_rows_at(_st.mod_hash(HERE), dll_sha=repo_dll_sha256())
    for rid, toggle, bar in spec:
        found = got.get(rid) if got is not None else None
        drv = DRIVER_OF.get(rid, default_driver)
        with t.component(rid, toggle=toggle):
            if t._guard():
                if found is None:
                    raise ExpectationFailed("UNMEASURED: live check owed (%s) -- no %s result at the current mod hash carries "
                                            "this row: run `python.exe src/RimMandrake/FlowWorks/northstar/%s --only ...` on "
                                            "the calm site; bar: %s" % (item, drv, drv, bar))
                r, name = found
                st = r.get("status")
                if st == "FAIL":
                    raise ExpectationFailed("[%s] %s: %s" % (r.get("class"), name, str(r.get("detail"))[:600]))
                if st != "PASS":
                    raise ExpectationFailed("UNMEASURED: %s %s [%s]: %s" % (name, st, r.get("class"), str(r.get("detail"))[:400]))
        if got is not None:
            c = t.components[-1]
            if found is not None:
                c.evidence.append({"call": "row %s (%s)" % (rid, found[1]), "result": found[0]})
                if c.verdict == "PASS":
                    c.detail = "%s: %s" % (found[1], str(found[0].get("detail"))[:380])
            t.upstream_failed = False        # this row only; it touched nothing


# THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (design/RimMandrake/thirst_bottles_design_2026-10-16.md §9; OQ-1..OQ-5 ruled by the
# owner by card 2026-10-16). The design's T-rows: the offline halves run here off the C# SelfTest (Source/SelfTest/
# ThirstChecks.cs: the production RM_ThirstMath, the shipped XML, the DBH patch, the Harmony target and call sites); every
# live row is written and reports UNMEASURED with its call and pass bar until a bridge session runs it (owed).
# Informative false theory to record if met (design §9): "the pawn has no thirst" when T1 says Dbh may mean DBH's own
# thirst setting is off, not our bug.
THIRST_OFFLINE = [("T0_provider_rule", "Thirst_provider_rule"), ("T3o_fall_rate", "Thirst_fall_rate_ruled"),
                  ("T3h_heat_cap", "Thirst_heat_cap_ruled"), ("T4o_bottle_and_quality", "Thirst_bottle_and_quality"),
                  ("T6o_dehydration", "Thirst_dehydration_ruled"), ("T8_coloured_bottles_without_dbh", "Thirst_bottles_generated"),
                  ("Td_defs_shipped", "Thirst_defs_shipped"), ("Tb_dbh_bridge_patch", "Thirst_dbh_bridge_patch"),
                  ("Th_harmony_target", "Thirst_harmony_target_and_call_sites"),
                  # THIRST_RULES_BUILD_SALT_OFF_THE_MENU (04-merged.md §8): the use-class gate and the auto-fill fix
                  ("Tu_use_class_gate", "Thirst_use_class_gate_ruled"),
                  ("Ta_autofill_potable_only", "Thirst_autofill_potable_only_in_source"),
                  ("Ts_slime_last_resort", "Thirst_slime_last_resort_ruled"),
                  ("Tb_salt_break", "Thirst_salt_break_ruled"),
                  ("Tk_awkward_access", "Thirst_awkward_access_ruled"),
                  ("Tr_reserve_orders_sprinklers", "Thirst_reserve_orders_sprinklers_ruled"),
                  ("Tq_q12_defaults", "Thirst_q12_defaults_ruled"),
                  ("Tt_bottle_stock_batches", "Thirst_bottle_stock_batches_ruled")]
THIRST_LIVE = [
    ("T1_provider_line", None, "Player.log grep 'thirst provider:' + parsed ModsConfig on three lists: no DBH -> Own; "
     "Lite+Thirst -> Dbh; Lite without Thirst -> Own (and DBHThirst absent or inert)"),
    ("T2_one_thirst_need", "thirstEnabled", "bridge pawn needs read on every free colonist: count(RM_Thirst)+count(DBHThirst) "
     "== 1 (== 0 with thirstEnabled off in Own mode)"),
    ("T3_need_falls", "thirstHeatScaling", "read RM_Thirst, advance 0.25 day at 20 C: drop 0.2 +/- 0.03 x thirstRateMultiplier"),
    ("T4_bottle_satisfies", None, "set need 0.2, give RM_Bottle_FreshWater, order Ingest: level rises >= 0.45 (Own) / DBH "
     "need rises (Dbh); a dirty bottle appears"),
    ("T5_salt_water_quality", "waterQualityEffects", "ORDERED drink of RM_Bottle_SaltWater x4 on test pawns: hydrate x0.7; "
     "RM_SaltPoisoning +0.25 each and RM_Thought_SaltRelief (no FoodPoisoning since THIRST_RULES_BUILD_SALT_OFF_THE_MENU)"),
    ("T6_dehydration_readable", None, "need held at 0, advance 1 day: RM_Dehydration 0.30 +/- 0.03 on the health tab"),
    ("T7_no_dbh_clean_log", None, "Player.log first exception since load names none of DubsBadHygiene, RM_Thirst, RM_Bottle_"),
    ("T9_animals_drink", "animalsGetThirst", "RM_Thirst on a wild and a tame animal (Own); advance until < 0.3 beside fresh "
     "water: each reaches RM_DrinkFromTerrain, level rises, no bottle touched"),
    ("T10_terrain_drink", "drinkFromTerrain", "colonist at 0.2, no bottles, pond 10 cells away: RM_DrinkFromTerrain job, "
     "+0.5 after ~300 ticks; with drinkFromTerrain off: no job"),
    # THIRST_RULES_BUILD_SALT_OFF_THE_MENU. Informative false theory if T11 fails: "the fill giver ignored the rule" when
    # the empty container was FORCED by a float-menu order (forced fills take any liquid, by ruling).
    ("T11_autofill_skips_salt", None, "empty RM_BottleEmpty x3 beside salt water, fresh pond 20 cells away, colonist on "
     "hauling: every RM_FillBottleJob targets a fresh-water cell; no RM_Bottle_SaltWater is made"),
    ("T12_no_routine_salt", None, "colonist at 0.2 standing on a salt shore, no potable water anywhere: no drink job "
     "for 2000 ticks (need falls); a fresh bottle dropped 30 cells away is then fetched"),
    ("T13_desperate_toxic_last", "lastResortDrinking", "colonist at 0.05 beside toxic water only: no job; set 0: "
     "RM_DrinkFromTerrain on toxic water and ToxicBuildup rises; with a fresh bottle on the map: the bottle wins"),
    ("T15_slime_effects", "waterQualityEffects", "four colonists at need 0, each beside one slime colour only: each drinks "
     "(RM_DrinkFromTerrain), gains RM_Thought_DrankSlime and RM_SlimePurge; red adds RM_ContagionTouched 1.0, green "
     "RM_Slimification >= 0.3, white RM_SporeFlesh, yellow RM_SlimeNausea; a fifth at 0.05 does not drink"),
    ("T16_living_slime", "lastResortDrinking", "Gelatinous Slime map, colonist at 0 beside RM_Slime_Liquid only: drinks it, "
     "RM_Slimification rises; with lastResortDrinking off: no job"),
    ("T17_salt_break", "saltBreakEnabled", "colonist at 0.05, mood forced below the Major threshold, only salt water in reach: "
     "dev 'Mental break' list offers RM_Break_DrinkBrine; started: drinks salt until >= 0.9, RM_Thought_SaltRelief, "
     "RM_SaltPoisoning 0.25 per drink, state ends; offered again only after the poisoning is gone; with a fresh bottle on "
     "the map it is not offered. Informative false theory if it never fires: 'the worker is wrong' when mood was above the "
     "Major threshold (the mood half is vanilla's)"),
    ("T18_dubs_last_resort", "lastResortDrinking", "Dubs mode (Lite + Thirst add-on), DBHThirst forced to 0, only slime in "
     "reach: JobGiver_RM_Drink drinks it and Dubs' bar rises; at DBHThirst 0.2 ours does nothing"),
    ("T19_awkward_access", "roughDrinkPenalty", "home map: colonist drinks a bottle and a tank: no RM_Thought_DrankRough; "
     "only a filled RM_Bucket_FreshWater in reach: RM_DrinkFromContainer, -3 thought, the bucket reads 'Partly drunk: 1.5 L' "
     "and no longer stacks; an Ascetic and a tribal pawn drinking the same: no thought; a pond: no thought"),
    ("T20_bucket_drunk_dry", None, "a 15 L bucket drunk 10 times becomes RM_BucketDirty (or Empty with the dirty stage off); "
     "emptying a part-drunk bucket into a tank adds only what is left"),
    ("T21_drinking_reserve", None, "net: one fresh tank at 300 L, a sprinkler over crops, reserve 200 L: the "
     "head sprays until 200 L, then reads Dry; a colonist still drinks at the tank; a salt tank on a still drains to 0"),
    ("T22_no_brine_spray", None, "a sprinkler net holding only brine: head reads 'No liquid'; brine + a little fresh: sprays fresh"),
    ("T23_fill_tank_is_the_order", None, "a Fill-mode tank holding brine with room, empty buckets, brine shore: pawns fill "
     "buckets with brine unforced and pour them in; set the tank to Store: the brine fills stop"),
    ("T24_bucket_douses_fire", "bucketFirefighting", "home-area fire 3x3, a filled RM_Bucket_FreshWater 8 cells from a "
     "firefighter: RM_DouseFireWithBucket, fires within 1.5 cells out at once, an empty bucket left; no bucket: vanilla BeatFire"),
    ("T25_snow_to_water", "snowGathering", "snowy map, no liquid water in 40 cells, an empty bucket: RM_GatherSnow, snow depth "
     "drops 0.4, RM_BucketSnow made; at 5 C it becomes RM_Bucket_FreshWater after ~5000 ticks; with a pond near: no snow job"),
    ("T26_ice_block_bill", None, "campfire bill RM_MeltBlueIceIntoBucket with 5 RM_BlueIce + a wooden empty bucket: a wooden "
     "RM_Bucket_FreshWater appears, no error in Player.log"),
    ("T27_water_items", None, "thirsty colonist, only RM_BlueIceMeltwaterCan on the map: RM_DrinkWaterItem, +0.67 need, the "
     "distilled thought"),
    ("T28_sanguophage_blood", "sanguophageBloodQuenches", "sanguophage at thirst 0.2 ingests a HemogenPack: thirst +0.5 and "
     "hemogen up; a baseliner given the same pack: no thirst change"),
    ("T29_bottle_stock_and_batches", None, "2 colonists, target 3, 20 empty bottles beside a pond: one hauler fills them in "
     "trips of up to 10 and stops at 6 filled (packed ones counted); 15 dirty bottles washed in two trips"),
    ("T14_native_animal_terrible_water", "animalsGetThirst", "on a salt/brine biome map, a roster-native animal at 0.2 "
     "drinks the brine (no FoodPoisoning); a non-native animal beside the same brine does not"),
]


@suite.chain("thirst")
def thirst(t):
    """Offline: FlowWorks thirst + bottles (ThirstChecks.cs cases), 0 ticks, no bridge. Live T-rows: read from the newest
    thirst_live / sprinkler_live results at the current mod hash (driver_rows_at), else UNMEASURED naming the driver."""
    cases = {}
    with t.component("thirst_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for rid, name in THIRST_OFFLINE:
        with t.component(rid):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    t.upstream_failed = False   # the live rows only read result files: an offline FAIL above must not blank them
    _driver_live_report(t, THIRST_LIVE, "thirst_live.py", "THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY")


# SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design/RimMandrake/sprinklers_design_2026-10-16.md §6, §8; OQ-S1..S7 ruled by the owner
# by card 2026-10-16). Offline halves run off the C# SelfTest (Source/SelfTest/SprinklerChecks.cs: the production
# RM_SprinklerKernel, the shipped defs, the VFE FindMod patch, the draw call sites); every live row is written and reports
# UNMEASURED with its call and pass bar until a bridge session runs it (owed). Staging for every live row: a quicktest map,
# spawn a RM_LiquidTank + 3 RM_UniversalPipe + RM_SprinklerHead on the last pipe + a Building_LiquidPump on the run (powered),
# fill the tank through the probe's filltank verb, advance 2,600 ticks, read the head's inspect line and the tank's units.
SPRINKLER_OFFLINE = [("S0_ruled_cost", "Sprinkler_ruled_cost"), ("S1o_all_or_nothing", "Sprinkler_pulse_all_or_nothing"),
                     ("S2o_needs_a_pump", "Sprinkler_needs_a_pump"), ("S3o_thick_clogs", "Sprinkler_thick_liquid_clogs"),
                     ("S4o_expiry", "Sprinkler_expiry_one_pulse_plus_grace"), ("S5o_spend", "Sprinkler_spend_dries_until_next_pulse"),
                     ("S6o_liquid_key", "Sprinkler_liquid_key_per_cell"), ("S7o_sealed", "Sprinkler_sealed_cells_never_charged"),
                     ("S8o_valve", "Sprinkler_valve_budget_and_reserve"), ("S9o_conserves", "Sprinkler_conserves_litres"),
                     ("S10o_walls_effects", "Sprinkler_walls_and_effects_wired"), ("S11o_defs", "Sprinkler_shipped_defs"),
                     ("S12o_vfe_patch", "Sprinkler_vfe_patch_findmod")]
SPRINKLER_LIVE = [
    ("sprinkler.draws_and_wets", None, "1 kL water tank, pump on: after one pulse the tank lost cells x 5 units (145 for 29 "
     "cells) and the head reads 'Spraying water'; ExplosiveGrowth's wet read says 'sprinkled' on a covered cell"),
    ("sprinkler.dries_when_starved", None, "empty the tank: the head reads 'Dry' and covered cells read dry within 2,750 ticks"),
    ("sprinkler.no_pressure", None, "despawn the pump: next pulse reads 'No pressure: no pump on this network', tank unchanged; "
     "respawn it: the next pulse sprays (design §8 item 1)"),
    ("sprinkler.thick_clogs", None, "a tar tank: the head reads 'Clogged: tar too thick to spray' and the tank is unchanged"),
    ("sprinkler.liquid_key", None, "a slime tank: covered cells' liquid key = that slime's FluidDef (probe RM_MapComponent_Sprinklers.WetAt)"),
    ("sprinkler.acid_hurts_fuel_puddles", "sprinklerNonWaterEffects", "an acid tank with a colonist in the spray: one contact "
     "hit per pulse; a chemfuel tank: its spill filth on covered cells; setting off: neither"),
    ("sprinkler.walls_stop_spray", None, "a wall between the head and a cell: that cell never reads sprinkled"),
    ("sprinkler_switch_flips.flip_sprinklersEnabled", "sprinklersEnabled", "setting off: the head draws nothing and reads "
     "'Sprinklers are off in Mod Settings'"),
    ("sprinkler.vfe_boost_skipped", "vfeSprinklerAdapterEnabled", "VFE Farming list, our biome: RM_SprinklerVFE.BoostsSkipped "
     "rises at hour 7 and a plant's Growth is not +0.04; a vanilla biome: BoostsPassed rises"),
    ("sprinkler.vfe_valve", "vfeThirstValve", "VFE head on a pump net, powered, half its cells bare: inspect 'Thirst valve: "
     "watering N of M cells' with N < M; daily budget 100 L stops it after ~100 L"),
]


@suite.chain("sprinklers")
def sprinklers(t):
    """Offline: FlowWorks sprinklers (SprinklerChecks.cs cases), 0 ticks, no bridge. Live rows: read from the newest
    sprinkler_live results at the current mod hash (driver_rows_at), else UNMEASURED naming the driver."""
    cases = {}
    with t.component("sprinkler_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for rid, name in SPRINKLER_OFFLINE:
        with t.component(rid):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    t.upstream_failed = False   # the live rows only read result files: an offline FAIL above must not blank them
    _driver_live_report(t, SPRINKLER_LIVE, "sprinkler_live.py", "SPRINKLER_HEADS_BUILD_PUMP_REQUIRED")


# DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md §Ruled design R1-R13 and
# §Owner's follow-up answers). Offline: the C# SelfTest cases of phases 1-6 (Source/SelfTest/DrawbridgeChecks.cs). Live: the
# eleven R13 rows of northstar/drawbridge_proof.py (phase 6b), read from its newest result at the current mod hash and deployed
# DLL (driver_rows_at), else UNMEASURED naming the driver. The driver calls the C# class RM_DrawbridgeProofs (contracts:
# drawbridge_proof.OWED_PROOFS); against a deployed FlowWorks without it, a live run writes every row UNMEASURED/HARNESS.
DRAWBRIDGE_CASES = [
    "Drawbridge_P1_materials_timber_and_steel_only", "Drawbridge_P1_split_one_leaf_or_two_each_hinged_on_its_own_bank",
    "Drawbridge_P1_leaf_is_rigid_off_its_seat_and_reversible", "Drawbridge_P1_decked_reads_raised_and_only_drawbridge_decks_raise",
    "Drawbridge_P1_structure_reads_see_a_raised_leaf", "Drawbridge_P1_toggle_forces_pocket_rebuild_and_repath",
    "Drawbridge_P1_raise_never_collapses", "Drawbridge_P1_leaf_record_saves_per_leaf_versioned",
    "Drawbridge_P2_tip_order_nearest_hinge_then_cell", "Drawbridge_P2_six_riders_one_free_square_one_lands_five_fall",
    "Drawbridge_P2_landings_never_through_a_wall_and_within_reach",
    "Drawbridge_P2_tip_wiring_once_per_raise_band_aware_overflow_falls", "Drawbridge_P3_sides_raise_either_lower_winch_only",
    "Drawbridge_P3_drive_timber_hands_steel_power_freezes", "Drawbridge_P3_winch_lost_crashes_down_and_hits",
    "Drawbridge_P3_winch_gone_any_way_crashes_and_unlinks", "Drawbridge_P1_tower_mid_span_refused",
    "Drawbridge_P3_one_winch_per_leaf_on_its_own_bank", "Drawbridge_P3_peace_auto_lowers_free_hostiles_lock",
    "Drawbridge_P4_raid_plank_fits_and_commits_once", "Drawbridge_P4_raiders_trench_hand_off_and_winch",
    "Drawbridge_P5_hoses_on_a_leaf_cut_while_raised_rejoin_lowered", "Drawbridge_P5_gravship_edge_bridge_collapses_at_launch",
    "Drawbridge_P5_length_by_material_from_settings", "Drawbridge_P6_gate_never_open_on_a_raised_leaf_locked_only_by_order",
    "Drawbridge_P6_real_build_buttons", "Drawbridge_P6_art_contract_paths_with_stand_ins",
    "Drawbridge_Looks_paths_look_first_then_material", "Drawbridge_Looks_raid_plank_pieces",
    "Drawbridge_Looks_wired_at_the_draw_sites"]
DRAWBRIDGE_LIVE = [
    ("RAISE_PATH", None, "a colonist holding a path over a lowered steel leaf; raised: the production path no longer crosses "
     "it, ToggleCount and RepathCount rise within 10 ticks"),
    ("RAISE_TIPS_RIDERS", None, "six hostile riders on a 3-wide leaf, one free hinge-bank square: one lands on the bank, "
     "five fall into the hole, all still hostile"),
    ("RAISE_SPARES_UNDERPASS", None, "a colonist under the deck keeps its cell and health; the rider on it tips"),
    ("LOWER_ONLY_FROM_WINCH", None, "the WorkGiver gives a far-bank colonist a raise job but no lower job; the winch-bank "
     "colonist gets the lower job"),
    ("TWO_LEAF_TIPS_OWN_HINGE", None, "an 8-square timber bridge is two leaves; each rider tips to its own leaf's hinge bank"),
    ("HOSTILE_LOCKS", None, "a raid cancels a pending auto-lower (target back to raised); a hostile trapped in a pit does "
     "not lock (FreeHostileCount 0)"),
    ("STEEL_UNPOWERED_FREEZES", None, "a steel leaf part-way up stays put while its winch is unpowered; moves on when powered"),
    ("WINCH_LOST_CRASHES", None, "a destroyed winch house crashes its raised leaf down at once and hurts the pawn under it"),
    ("WINCH_DESPAWN_CRASHES", None, "a winch house despawned without being destroyed (a gravship launch's WillReplace) "
     "unlinks and crashes its raised leaf, hurting the pawn under it"),
    ("RAID_UP", None, "raised leaf, winch inside, decoy outside: raiders make legal progress (winch jobs, planks, trench, "
     "decoy) and no job loop"),
    ("RAID_PLANK", None, "an interrupted plank carrier makes no duplicate crossing: exactly one plank crossing laid"),
    ("SAVE_MIDRAISE", None, "saved and loaded mid-raise: progress kept, the tip not replayed, the raise completes"),
]


@suite.chain("drawbridges")
def drawbridges(t):
    """Offline: drawbridge phases 1-6 (DrawbridgeChecks.cs cases), 0 ticks, no bridge. Live R13 rows: read from the newest
    drawbridge_proof results at the current mod hash (driver_rows_at), else UNMEASURED naming the driver."""
    cases = {}
    with t.component("drawbridge_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in DRAWBRIDGE_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    t.upstream_failed = False   # the live rows only read result files: an offline FAIL above must not blank them
    _driver_live_report(t, DRAWBRIDGE_LIVE, "drawbridge_proof.py", "DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS")


# PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §Ruled design P1-P9)
# and POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS. Offline: the C# SelfTest cases of phases 1-7 and the cord (the files in
# LINES_CASE_FILES; selftest_lines_proof checks the list against them). Live: the nine rows of northstar/lines_proof.py, read
# from its newest result at the current mod hash and deployed DLL (driver_rows_at), else UNMEASURED naming the driver. The
# driver calls the C# class RM_LineProofs (contracts: lines_proof.OWED_PROOFS); against a deployed FlowWorks without it, a
# live run writes every row UNMEASURED/HARNESS.
LINES_CASE_FILES = ("LineCrossingChecks.cs", "LineDigBreakChecks.cs", "DeckCollapseLinesChecks.cs", "PipePoleChecks.cs", "PipeSpanNetChecks.cs", "HoseBandChecks.cs", "LineReadoutChecks.cs", "PowerCordChecks.cs", "ReelRiserShadowChecks.cs", "CoverFloorSurveyChecks.cs")
LINES_CASES = [
    "LineCrossing_P2_table_every_kind_by_every_surface",
    "LineCrossing_P2_rigid_only_on_solid_ground_cover_carries_nothing",
    "LineCrossing_P2_surface_deck_wins_over_the_hole_under_it",
    "LineCrossing_P2_every_refusal_has_a_reason_every_allow_none",
    "LineCrossing_P1_style_change_does_not_change_permission",
    "LineCrossing_P2_gates_at_placement_rebuild_and_frame_completion",
    "LineDigBreak_cancelled_or_refused_dig_breaks_nothing", "LineDigBreak_commit_breaks_rigid_and_cords_once_never_hose",
    "LineDigBreak_repeat_commit_is_idempotent", "LineDigBreak_liquid_net_splits_where_the_pipe_broke",
    "DeckCollapse_cord_drops_one_live_fallen_wire_and_the_net_splits_once", "DeckCollapse_repeat_teardown_is_idempotent",
    "DeckCollapse_unpowered_or_disconnected_cord_shocks_nobody", "DeckCollapse_hose_across_a_collapsed_deck_is_reeled_in",
    "DeckCollapse_every_collapse_path_clears_through_ClearDeckTop", "DeckCollapse_GSS_shock_seam_is_soft_and_load_safe",
    "PipePole_P3_support_on_solid_ground_only_refused_on_deck_cover_dug", "PipePole_P3_span_length_cap_follows_the_slider",
    "PipePole_P3_sag_at_the_slider_extremes", "PipePole_P3_span_is_not_walkable_and_not_in_pawn_topology",
    "PipePole_P4_dig_kills_the_pole_so_its_spans_fall", "PipePole_P3_settings_and_the_gss_seam_line_up",
    "PipePole_D5_ground_pipe_reaches_the_pole_and_the_span_is_the_looks_pipe",
    "PipeSpan_P3_edge_joins_two_60pct_components_cap_after_join_refused",
    "PipeSpan_P3_edge_joins_two_40pct_components_accepted_as_one",
    "PipeSpan_P3_one_logical_edge_no_duplicate_cardinal_or_reverse_span",
    "PipeSpan_P3_ring_of_two_pole_routes_cut_in_turn", "PipeSpan_P3_cut_span_splits_the_net_once",
    "PipeSpan_P3_production_wiring_adapter_callback_join_order", "HoseBand_P5_refuses_a_dug_square_without_ramp_or_ladder",
    "HoseBand_P5_routes_lip_ramp_floor", "HoseBand_P5_routes_lip_ladder_floor_and_raised_ladder_leaves_it_hanging",
    "HoseBand_P5_endpoint_reach_respects_band", "HoseBand_P5_newly_dug_square_replans_or_retracts_once",
    "HoseBand_P2_pit_cover_carries_no_hose", "HoseBand_P5_no_bands_leaves_gss_signatures_unchanged",
    "HoseBand_swim_split_pool_stays_one_floor", "Scenario_C4_C10_hoses_lay_offline",
    "LineReadout_P9_four_cases_read_apart", "LineReadout_P9_counts_and_dry_pole",
    "LineReadout_P9_adapters_print_the_lines", "PipePoleGravship_P8_aboard_span_rekeys_on_landing",
    "PipePoleGravship_P8_edge_span_coils_and_no_support_loss", "PowerCord_def_is_a_FlexCord_power_transmitter_of_its_own",
    "PowerCord_placeable_on_rope_timber_steel_decks_and_leaf_refused_dug_and_cover",
    "PowerCord_restyled_conduit_still_refused_on_decks", "PowerCord_dig_break_catches_the_cord_def",
    "PowerCord_leaf_raise_disconnects_lower_rejoins_the_power_net",
    "PowerCord_deck_collapse_destroys_it_and_records_the_fallen_wire_first",
    # owner cards 2026-10-22: REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST, PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID, HOSE_GIRTH_TUNE_MUCH_THINNER
    "ReelFacing_outlet_nozzle_and_picture_turn_with_the_reel", "ReelFacing_target_on_the_outlet_side_lays_with_no_U_loop",
    "ReelFacing_relay_inlet_turns_with_the_relay", "ReelFacing_def_rotatable_west_default_preview_and_legacy_saves",
    "PipeTankRiser_ends_on_the_hose_flange_not_under_the_skid", "PipeTankRiser_wiring_link_stops_layer_prints_flange_follows",
    "HoseShadow_empty_is_darker_and_wider_full_unchanged",
    # owner cards 2026-10-22: PIT_COVER_WIDEN_PLANKS_BEAR_BOOTS, DRILL_PLACEMENT_ENFORCE_NO_DRY_HOLES
    "CoverFloor_planked_squares_are_ground_open_squares_the_pit", "CoverFloor_laying_or_lifting_a_lid_invalidates_path_and_reach",
    "DrillSurvey_empty_survey_refuses_unsurveyed_allows", "DrillSurvey_placeworker_wired_on_drill_and_bleed_well"]
LINES_LIVE = [
    ("ROPE_DECK_RIGID_REFUSED_FLEX_OK", None, "on a rope deck square the placement gate refuses a pipe and a conduit and accepts "
     "a power cord; a hose to the far bank is laid over >= 3 deck squares"),
    ("COVER_CARRIES_NO_HOSE", None, "an intact pit cover reads hoseClosed and a hose to the far bank lies on no cover square"),
    ("POLE_SPAN_CARRIES_LIQUID", None, "two tanks joined only by a strung pipe-pole span share one liquid net (tank B in tank A's "
     "store); destroying a pole splits it"),
    ("DIG_UNDER_PIPE_SPLITS_NET", None, "a square dug under a pipe destroys that pipe once and splits the net; a second dig "
     "breaks nothing"),
    ("CORD_DECK_LAMP_LIT", None, "a cord across a timber deck powers a lamp on the far bank; the deck cord reads 'Lying on a "
     "bridge deck.'"),
    ("LEAF_RAISED_LAMP_DARK", None, "a raised drawbridge leaf cuts its cord (lamp dark, 'Disconnected:' readout); lowered, the "
     "lamp lights again"),
    ("COLLAPSE_CORD_SHOCKS_ONCE", None, "a collapsing deck drops its powered cord as a live fallen wire: the net split exactly "
     "once, a colonist on a fallen square shocked"),
    ("LADDER_HOSE_DRAINS_RAISED_STAYS", None, "a hose down a ladder with an Intake end drains the pit into the tank; raising the "
     "ladder leaves the hose laid, unmoved"),
    ("DIG_REROUTES_LAID_HOSE", None, "a pit dug under a laid hose: within one corridor check it re-routes round the pit, "
     "still laid"),
    ("COVER_BREAK_DROPS_RIDER", None, "a pit cover destroyed by damage under a colonist drops him into the pit (one descent, "
     "held)"),
    ("PITFALL_SAVED_ARRIVAL_FALLS", None, "a forced arrival into a pit saved before the detector judged it still falls after "
     "the load (lastCell scribed)"),
]


@suite.chain("lines")
def lines(t):
    """Offline: pipe-pole phases 1-7 and the power cord (LINES_CASES), 0 ticks, no bridge. Live rows: read from the newest
    lines_proof results at the current mod hash (driver_rows_at), else UNMEASURED naming the driver."""
    cases = {}
    with t.component("lines_selftest_ran"):
        if t._guard():
            cases = _selftest_cases()
    for name in LINES_CASES:
        with t.component(name):
            if t._guard():
                got = cases.get(name)
                if got != "ok":
                    raise ExpectationFailed("%s: %s" % (name, got or "case missing from the SelfTest output"))
    t.upstream_failed = False   # the live rows only read result files: an offline FAIL above must not blank them
    import lines_proof as _LP  # noqa: E402  (pure python: the row to item map)
    for item in ("PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE", "POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS"):
        _driver_live_report(t, [r for r in LINES_LIVE if _LP.ROW_ITEM[r[0]] == item], "lines_proof.py", item)


# the extension suites, registered unchanged (their chains carry their own toggle=/shows= claims): the main
# extensions and, since the River Works merge (409d1f57c), the rivers suite
import extensions_rivers as RIV  # noqa: E402
# Rivers toggles no component claims. Named so the hole is visible and fixed-size: selftest_extensions fails if it grows
# OR shrinks without this list changing. rivers_switch_flips (above) claims eleven offline; these two had components
# that could not fail (review 2026-10-11: forced refill ignores the setting; the trace read held for any bool).
RIVER_TOGGLES_OWED = ["placerFloodRefill", "takenByLandTraceEnabled"]
suite.toggles += [t for t in RIV.suite.toggles if t not in suite.toggles]
# hose port (2026-10-11): the flexible hose's player-facing switches join the toggle floor. No row flips them yet (the hose
# live rows flip minBendRadius / maxLength, numbers), so they are owed, named and fixed-size like the rivers' list.
HOSE_TOGGLES_OWED = ["autoResumeDroppedHose", "enabled", "fillWobble", "tintByContents"]
suite.toggles += [t for t in HOSE_TOGGLES_OWED if t not in suite.toggles]
suite.toggles += [t for t in ["thirstEnabled", "thirstHeatScaling", "waterQualityEffects", "animalsGetThirst",
                                 "drinkFromTerrain", "lastResortDrinking", "saltBreakEnabled", "roughDrinkPenalty", "bucketFirefighting",
                                 "snowGathering", "sanguophageBloodQuenches"] if t not in suite.toggles]
suite.toggles += [t for t in ["sprinklersEnabled", "sprinklerNonWaterEffects", "vfeSprinklerAdapterEnabled", "vfeThirstValve"]
                  if t not in suite.toggles]
# extension toggles whose every component is an `_owed` placeholder (northstar/extensions.py; it waited and recorded PASS
# until 2026-10-11): on the floor, claimed by no component, named and fixed-size like the lists above.
# 2026-10-11 re-review: liquidIgnition (water fill + vanilla Fire could not tell ON from OFF), riverSteam (setting
# read-back only) and the three machinery rows that were UNMEASURED by construction joined it. riverSteamEnabled and
# bottleDirtyStageEnabled left it 2026-10-15 (toggle_river_steam, toggle_bottle_dirty claim both sides).
EXTENSION_TOGGLES_OWED = ["fallDamageEnabled", "liquidCorrosionEnabled",
                          "liquidDrillingEnabled", "liquidIgnitionEnabled", "liquidWorksRuinStockEnabled",
                          "liquidWorksRuinsEnabled", "pipeAdaptersEnabled",
                          "superdeepShootingRuleEnabled", "typedLiquidShoresEnabled",
                          "machineDigEnabled"]   # DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: needs a staged colony mech (design §8)
# Every bool switch the C# settings sections expose (northstar/settings_registry.py) is either on the toggle floor above
# or named here. These were never on it (a gap older than the hose port, listed so it cannot grow unseen).
TOGGLES_NOT_ON_FLOOR = ["blastsBreakPitCovers", "pitStuckAlertEnabled", "fallDeathEnabled", "pitGuardrailEnabled", "excavationLoadRepairEnabled", "excavationWallMaterialEnabled",
                        "ladderRaiseLowerEnabled", "legacyFillFallbackEnabled", "legacyFloodViaEngineEnabled",
                        "liquidBubblesEnabled", "liquidLooksEnabled", "liquidSeeThroughEnabled", "liquidSurfaceMotionEnabled",
                        "liquidWakesEnabled", "networkSeamsMoveEnabled", "pitHidesShadowEnabled", "pitLipOcclusionEnabled",
                        "pitLipOccupantCutEnabled", "pitOutlineEnabled", "pitScorchEnabled", "pitSinkClampEnabled",
                        "pitWalkNormalEnabled", "pumpFedSpreadEnabled", "recedeKeepsLastCell", "recedeSparesOutflow",
                        "thickCreepEnabled", "waterFrontCreepEnabled", "levelBySurfaceEnabled", "levelSetEnabled", "levelExactEnabled", "wetnessCutoffEnabled",
                        # POND_RETURN_LEG_BUILD_WATER_GOES_HOME (2026-10-13): their live rows (L3 return leg, L6 refill
                        # over things) are owed on the item, not yet a toggle chain
                        "dugBedLeavesPondEnabled", "pondReturnLegEnabled", "refillWaitsForOccupants",
                        # PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP (2026-10-13): its live rows are the climb proof owed on
                        # the item (design §8.6), not yet a toggle chain
                        "pitRelativeClimbEnabled",
                        # PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL (2026-10-20): its live rows (two ponds level; pond and oil
                        # pit do not) are owed on the item, not yet a toggle chain
                        "gravityLevellingEnabled",
                        # POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (2026-10-16): its live row is liquid_checks.pond_depth_verdict (L8, run
                        # with the bridge, selftested offline), not yet a toggle chain
                        "pondDepthEnabled", "pondHeadRuleEnabled",
                        # POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2 (2026-10-14): its live rows (A1 hollow, A2 LIFO refill)
                        # are owed on the item, not yet a toggle chain
                        "pondBedHollowEnabled",
                        # POND_ELEVATION_BUILD_LAKES_RUN_DEEP (2026-10-15): its live rows are northstar/deep_lake_proof.py (run on
                        # request with the bridge), not yet a toggle chain
                        "deepBedsEnabled",
                        # PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS (2026-10-14): its live rows are owed on the item, not yet a
                        # toggle chain
                        "pitRampsEnabled",
                        # DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT (2026-10-17): the dig cost curve; offline in SelfTest
                        # DeepDig_cost_curve_numbers_measured, its live row is the P10 walk's dig (FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG)
                        "digCostRisesWithDepth",
                        # DIG_ROCK_TUNE_STONE_FIGHTS_BACK (2026-10-16): digging rock takes longer and drops chunks; no live
                        # toggle chain yet (the rows are owed on the item)
                        "digRockGroundEnabled", "digRockChunksEnabled",
                        # LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (2026-10-16; absorbed into LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD): the cell readout's depth/litres line is UI text
                        # read by eye (review map station pond_bed); no live toggle chain yet
                        "mouseoverDepthEnabled",
                        # the liquid-kit section, registered in site_spec 2026-10-15 (they were scribed
                        # all along but missing from the registry): no live row flips them yet
                        "fluidResidueEnabled", "hotLiquidEnabled", "liquidBathRecipesEnabled", "liquidReactionsEnabled",
                        # HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY / FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW (site_spec 2026-10-16):
                        # art/diagnostic switches, no live row flips them yet
                        "pipeLinksIntoMachines", "joinFittings", "waterBodyTypeFlipFixEnabled",
                        # RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW (2026-10-16): the planet-map river gradient; what it
                        # paints is read by eye on the world map (the old mod's script had no live row for it either)
                        "riverColorsEnabled",
                        # THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (2026-10-16): restart-only (read while patches apply), so a
                        # live row flipping it needs two loads with Dubs Bad Hygiene; owed
                        "dbhBottleBridge",
                        # TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT / PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS /
                        # PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (built 2026-10-18, registered in site_spec by the F2 settings
                        # audit): their live rows are owed on the items (A1-A5), not yet a toggle chain
                        "trenchCoverEnabled", "trenchAiAvoidsCages", "portableLadderEnabled", "climbingGearEnabled",
                        "pitJumpLandsSafe", "pitTeleportLandsSafe", "pitFreeTravelEnabled", "reachSeesWallsAndCliffs", "pitRescueLadderEnabled", "pipesUnderToCentre",
                        # registered 2026-10-19 (settings audit catch-up): wall climb, raider trench, swim, water mend. Live
                        # rows are owed on their items; not yet a toggle chain
                        "wallClimbEnabled", "raidersMayClimbWalls", "wallClimbAutoRoute", "raidersCarryClimbingGear",
                        "raiderTrenchEnabled", "raiderJumpsEnabled", "raiderLaddersEnabled", "raiderFillEnabled",
                        "deepSwimEnabled", "swimOpenWaterEnabled", "humanlikesSwim", "mechanoidsSink", "animalsAvoidDeepWater",
                        "tiredSwimmersHeadForShore", "deepSwimJoyEnabled", "shallowWaterDrowningEnabled",
                        "waterBodyMendsEnabled", "fishRollOnGrowth", "fishReturnOnRefill", "fishingZoneReturnOnRefill",
                        "waterBodySplitEnabled", "waterPlantGraceEnabled", "freezeCountMendEnabled",
                        # RM_SuspensionSettings registered 2026-10-19 (SETTINGS_REGISTRY_FILL_FOUR_SECTIONS_UNSEEN): the suspension
                        # items' live rows are owed on them (B4); not yet a toggle chain
                        "suspensionBridgesBuildable", "suspensionWeightCollapse", "suspensionAnchorLossFalls",
                        "vanillaBridgeRefusedOverDug", "suspensionOwnPeopleFall", "grateFirePasses", "grateDrainsSpills",
                        "suspensionWalkUnder", "sunkenBridges", "suspensionOverWater", "suspensionOverSea",
                        "floodsDamageLightBridges",
                        # RM_DrawbridgeSettings registered 2026-10-20 (DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS): its live rows are
                        # northstar/drawbridge_proof.py (owed to its first live run), not yet a toggle chain
                        "drawbridgesEnabled", "raidsBringPlanks",
                        # PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 1 (2026-10-21): live rows owed on the item (L2), not yet a
                        # toggle chain
                        "lineCrossingRulesEnabled",
                        # PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 (2026-10-21): pipe poles need GSS; live rows owed (L2)
                        "pipePolesEnabled"]
for _src in (EXT.suite, RIV.suite):
    for _name, _fn in _src.chains:
        suite.chains.append((_name, _fn))
        if _name in _src.chain_caps:
            suite.chain_caps[_name] = _src.chain_caps[_name]
