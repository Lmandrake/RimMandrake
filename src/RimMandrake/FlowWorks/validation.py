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
    "P1_width_matrix", "P2_fillin_releases_large", "P3_walk_in_held", "P4_ladder_frees", "P4b_ladder_raised_strands",
    "P5n_own_faction_carveout",
    "X1_pawn_height_ladder", "X2_pawn_lowers_walking_in", "X3_pawn_rises_walking_out", "X4_pit_wall_over_head",
    "X5_slime_occupant_below_surface", "X7_tar_front_lags_water", "X6_two_fluids_distinct", "X7n_viscosity_off",
    "X8_cover_hides_pit", "X9_cover_deck_uniform", "T0n_fluid_switch_refused", "E9_log_budget", "Z_settings_restored",
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
}
# bars only an extension chain claims (selftest_extensions asserts this list is exactly the difference)
EXTENSION_ONLY_BARS = ["canal_burning_reads_as_burning_liquid", "canal_fire_persists", "canal_fire_reaches_reservoir",
                       "canal_spent_after_burn", "reservoir_recharge_progress_visible", "sluice_gate_state_legible",
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


def _report_rows(t, rows, declare=()):
    """One component per row, same id. FAIL raises (-> FAIL + finding); UNMEASURED/UNBUILT/UNCOVERED record
    UNMEASURED with the status in the detail. The rows are already-measured, independent results, so a FAIL row
    does not blank the rows after it. Under the declaration probe (no game) `declare` lists the ids to declare,
    so toggle and bar coverage is answerable offline. (Same shape as GimmeSomeSlack/validation.py.)"""
    if not t._guard() and not rows:
        for rid in declare:
            with t.component(rid, toggle=ROW_TOGGLES.get(rid), shows=ROW_SHOWS.get(rid)):
                pass
        return
    for r in rows:
        st = r["status"]
        with t.component(r["id"], toggle=ROW_TOGGLES.get(r["id"]), shows=ROW_SHOWS.get(r["id"])):
            if t._guard() and st == "FAIL":
                raise ExpectationFailed("[%s] %s" % (r.get("cls"), str(r.get("detail"))[:600]))
        c = t.components[-1]
        c.evidence.append({"call": "row %s" % r["id"], "result": r})
        if c.verdict == "FAIL":
            t.upstream_failed = False        # this row only; it touched nothing
        elif c.verdict == "PASS":
            if st in NOT_MEASURED or st not in ("PASS", "FAIL", "SKIP"):
                c.verdict, c.detail = "UNMEASURED", "%s: %s" % (st, str(r.get("detail"))[:400])
            else:
                c.detail = str(r.get("detail"))[:400]


def _v2():
    import validation_v2 as V2  # noqa: E402 - northstar/ is on sys.path
    return V2


def offline_rows():
    """v2's offline tier as rows; a repeated check id (O1 twice, O8 thrice) gets a #n suffix."""
    V2 = _v2()
    checks = V2.run_offline() + [V2.selftest_live_mock()]
    rows, seen = [], {}
    for c in checks:
        seen[c.cid] = seen.get(c.cid, 0) + 1
        rid = "v2_%s" % c.cid if seen[c.cid] == 1 else "v2_%s#%d" % (c.cid, seen[c.cid])
        rows.append({"id": rid, "status": "PASS" if c.ok else "FAIL", "cls": "" if c.ok else "MOD", "detail": c.detail})
    return rows


OFFLINE_IDS = ["v2_O1", "v2_O1#2", "v2_O2", "v2_O3", "v2_O4", "v2_O5", "v2_O6", "v2_O7", "v2_O9", "v2_O8", "v2_O8#2",
               "v2_O8#3", "v2_O10", "v2_O-NEG", "v2_O-LIVE-NEG"]


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


@suite.chain("core_live_rows")
def core_live_rows(t):
    """v2's live rows, read from the newest v2 result made at the current mod hash. 0 ticks."""
    rows = []
    if t._guard():
        from modcheck import status as _st  # noqa: E402
        found = latest_core_result(_st.mod_hash(HERE))
        if found:
            rows = found[1]["rows"]
        else:
            rows = [{"id": rid, "status": "UNMEASURED", "cls": "HARNESS",
                     "detail": "no v2 live result at the current mod hash: run `python.exe "
                               "src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map`, then "
                               "`modcheck record FlowWorks --result <json> --tier flowworks`"} for rid in CORE_LIVE_IDS]
    _report_rows(t, rows, declare=CORE_LIVE_IDS)


# the extension suite, registered unchanged (its chains carry their own toggle=/shows= claims)
for _name, _fn in EXT.suite.chains:
    suite.chains.append((_name, _fn))
    if _name in EXT.suite.chain_caps:
        suite.chain_caps[_name] = EXT.suite.chain_caps[_name]
