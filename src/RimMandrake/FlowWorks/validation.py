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
    "X8_cover_hides_pit", "X9_cover_deck_uniform", "X10_canal_fire", "T0n_fluid_switch_refused", "E9_log_budget", "Z_settings_restored",
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
                       "spikes_read_distinct"]

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


def _selftest_cases():
    """Run the FlowWorks C# SelfTest once; {case name: "ok"|"FAIL"}, or raise UNMEASURED when it could not run."""
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
    return cases


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
                  ("Th_harmony_target", "Thirst_harmony_target_and_call_sites")]
THIRST_LIVE = [
    ("T1_provider_line", None, "Player.log grep 'thirst provider:' + parsed ModsConfig on three lists: no DBH -> Own; "
     "Lite+Thirst -> Dbh; Lite without Thirst -> Own (and DBHThirst absent or inert)"),
    ("T2_one_thirst_need", "thirstEnabled", "bridge pawn needs read on every free colonist: count(RM_Thirst)+count(DBHThirst) "
     "== 1 (== 0 with thirstEnabled off in Own mode)"),
    ("T3_need_falls", "thirstHeatScaling", "read RM_Thirst, advance 0.25 day at 20 C: drop 0.2 +/- 0.03 x thirstRateMultiplier"),
    ("T4_bottle_satisfies", None, "set need 0.2, give RM_Bottle_FreshWater, order Ingest: level rises >= 0.45 (Own) / DBH "
     "need rises (Dbh); a dirty bottle appears"),
    ("T5_salt_water_quality", "waterQualityEffects", "drink RM_Bottle_SaltWater x10 on test pawns: hydrate x0.7; "
     "FoodPoisoning in 1-4 of 10"),
    ("T6_dehydration_readable", None, "need held at 0, advance 1 day: RM_Dehydration 0.30 +/- 0.03 on the health tab"),
    ("T7_no_dbh_clean_log", None, "Player.log first exception since load names none of DubsBadHygiene, RM_Thirst, RM_Bottle_"),
    ("T9_animals_drink", "animalsGetThirst", "RM_Thirst on a wild and a tame animal (Own); advance until < 0.3 beside fresh "
     "water: each reaches RM_DrinkFromTerrain, level rises, no bottle touched"),
    ("T10_terrain_drink", "drinkFromTerrain", "colonist at 0.2, no bottles, pond 10 cells away: RM_DrinkFromTerrain job, "
     "+0.5 after ~300 ticks; with drinkFromTerrain off: no job"),
]


@suite.chain("thirst")
def thirst(t):
    """Offline: FlowWorks thirst + bottles (ThirstChecks.cs cases), 0 ticks, no bridge. Live T-rows: UNMEASURED, owed."""
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
    for rid, toggle, bar in THIRST_LIVE:
        with t.component(rid, toggle=toggle):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: live check owed (THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY) -- " + bar)


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
    """Offline: FlowWorks sprinklers (SprinklerChecks.cs cases), 0 ticks, no bridge. Live rows: UNMEASURED, owed."""
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
    for rid, toggle, bar in SPRINKLER_LIVE:
        with t.component(rid, toggle=toggle):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: live check owed (SPRINKLER_HEADS_BUILD_PUMP_REQUIRED) -- " + bar)


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
                                 "drinkFromTerrain"] if t not in suite.toggles]
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
                          "superdeepShootingRuleEnabled", "typedLiquidShoresEnabled"]
# Every bool switch the C# settings sections expose (northstar/settings_registry.py) is either on the toggle floor above
# or named here. These were never on it (a gap older than the hose port, listed so it cannot grow unseen).
TOGGLES_NOT_ON_FLOOR = ["blastsBreakPitCovers", "excavationLoadRepairEnabled", "excavationWallMaterialEnabled",
                        "ladderRaiseLowerEnabled", "legacyFillFallbackEnabled", "legacyFloodViaEngineEnabled",
                        "liquidBubblesEnabled", "liquidLooksEnabled", "liquidSeeThroughEnabled", "liquidSurfaceMotionEnabled",
                        "liquidWakesEnabled", "networkSeamsMoveEnabled", "pitHidesShadowEnabled", "pitLipOcclusionEnabled",
                        "pitLipOccupantCutEnabled", "pitOutlineEnabled", "pitScorchEnabled", "pitSinkClampEnabled",
                        "pitWalkNormalEnabled", "pumpFedSpreadEnabled", "recedeKeepsLastCell", "recedeSparesOutflow",
                        "thickCreepEnabled", "waterFrontCreepEnabled", "levelBySurfaceEnabled", "levelSetEnabled",
                        # POND_RETURN_LEG_BUILD_WATER_GOES_HOME (2026-10-13): their live rows (L3 return leg, L6 refill
                        # over things) are owed on the item, not yet a toggle chain
                        "dugBedLeavesPondEnabled", "pondReturnLegEnabled", "refillWaitsForOccupants",
                        # PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP (2026-10-13): its live rows are the climb proof owed on
                        # the item (design §8.6), not yet a toggle chain
                        "pitRelativeClimbEnabled",
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
                        # DIG_ROCK_TUNE_STONE_FIGHTS_BACK (2026-10-16): digging rock takes longer and drops chunks; no live
                        # toggle chain yet (the rows are owed on the item)
                        "digRockGroundEnabled", "digRockChunksEnabled",
                        # LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (2026-10-16): the cell readout's depth/litres line is UI text
                        # read by eye (review map station pond_bed); no live toggle chain yet
                        "mouseoverDepthEnabled",
                        # the liquid-kit and sluice-gate sections, registered in site_spec 2026-10-15 (they were scribed
                        # all along but missing from the registry): no live row flips them yet
                        "fluidResidueEnabled", "hotLiquidEnabled", "liquidBathRecipesEnabled", "liquidReactionsEnabled",
                        "sluiceGatesEnabled",
                        # HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY / FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW (site_spec 2026-10-16):
                        # art/diagnostic switches, no live row flips them yet
                        "pipeLinksIntoMachines", "joinFittings", "waterBodyTypeFlipFixEnabled",
                        # RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW (2026-10-16): the planet-map river gradient; what it
                        # paints is read by eye on the world map (the old mod's script had no live row for it either)
                        "riverColorsEnabled",
                        # THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (2026-10-16): restart-only (read while patches apply), so a
                        # live row flipping it needs two loads with Dubs Bad Hygiene; owed
                        "dbhBottleBridge"]
for _src in (EXT.suite, RIV.suite):
    for _name, _fn in _src.chains:
        suite.chains.append((_name, _fn))
        if _name in _src.chain_caps:
            suite.chain_caps[_name] = _src.chain_caps[_name]
