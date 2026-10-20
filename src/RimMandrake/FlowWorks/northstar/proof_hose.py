"""proof_hose.py -- FlowWorks flexible hoses: the ONE live proof (hose port step 8,
design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md §3.6, §3.9-3.10, §4 step 8).

The hose blocks moved out of Gimme Some Slack's proof_all.py (hose, maze, relay, carry, style_hose, the nine hose matrix scenes,
the hose half of the one save/load) plus the real-flow bars of step 6, on ONE fresh quicktest map of the flowworks tier, in ONE
bridge session:

    python3    src/RimMandrake/FlowWorks/northstar/proof_hose.py --offline-gate        # WSL: the offline tier only (seconds)
    python.exe src/RimMandrake/FlowWorks/northstar/proof_hose.py --live [--no-fresh-map] [--only realflow,save_load]
    python.exe src/RimMandrake/FlowWorks/northstar/proof_hose.py --live --preport-save NAME_CARRY,NAME_RETRACT   # PP1/PP2

Run python.exe from the repo root (bridge calls only work under python.exe; pipe through tr -d '\\r').

ORDER: offline gate (WSL) -> preflight (HP1 tier + startup log, HP2 probes + site pinned) -> matrix_hose (the nine H0* scenes,
CROSS-MOD: they draw cords too, so they run only when Gimme Some Slack is active and its matrix modules are on disk; else
UNMEASURED) -> hose -> maze -> relay -> carry -> style_hose -> realflow (NS_* bars) -> the ONE save + load (SL1-SL4) ->
preport (PP1/PP2, only with --preport-save: saves made BEFORE the port, one with a colonist mid-carry and one mid-retract; they
fail on "Cleaning up invalid job state" or a could-not-find-class line, G5.9) -> Z one log budget (errors naming any hose
namespace, old or new, are ours: G5.7).

Output: ONE result JSON northstar/proof_hose_<stamp>.json (mode "live" for a full run; "partial" with --only), read by
FlowWorks/validation.py's hose_live_rows at the current mod hash (`modcheck record FlowWorks --result <json>`).
The manifest the FlowWorks walk names is northstar/manifest.py: v2's rows UNION declared_rows() below.

Its control flow is proven offline by northstar/selftest_proof_hose.py against a fake bridge; it has run live since the port
(e.g. the 2026-10-19 pass-2 realflow run, Transient/live_session/pass2_20261019T014313/proof_hose_20261019T021252.json).
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import collections
import json
import os
import sys
import time

OUT_DIR = os.path.dirname(os.path.abspath(__file__))     # .../FlowWorks/northstar
MOD = os.path.dirname(OUT_DIR)                             # .../FlowWorks
RM = os.path.dirname(MOD)                                  # .../src/RimMandrake
UTILS = os.path.join(RM, "Utils")
GSS_MATRIX = os.path.join(RM, "GimmeSomeSlack", "northstar_matrix")
for _p in (MOD, UTILS, OUT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import validation_core as V  # noqa: E402
import validation_hose as VH  # noqa: E402
import validation_style_hose as VSH  # noqa: E402

PKG = "mandrake.rm.flowworks"
TIER = "flowworks"
BLOCKS = ["matrix_hose", "hose", "maze", "relay", "carry", "style_hose", "realflow", "save_load", "preport"]
LIQUID_WATER = "RM_Liquid_FreshWater"
OURS = ("RimMandrake.FlowWorks.Hose", "RimMandrake.GimmeSomeSlack.Hose", "RimMandrake.MessyConduit.Hose", "FlowWorks")

# The row ids a full live run emits, per block (the walk's manifest, northstar/manifest.py, unions these with v2's). Seeded
# from Gimme Some Slack's proof_all DECLARED_ROWS of 2026-10-05 (RL6 split, G5.6) plus the real-flow bars (§3.6).
DECLARED_ROWS = {
    "preflight": ["HP1_tier_running_startup_log_clean", "HP2_probes_site_pinned"],
    "hose": ["H1b_install_validity", "H2_hose_laid_as_hose_cord", "H6_plump_within_transition",
             "H7_no_flicker_fast_toggle", "H8_collapse_after_release", "H9_stiffness_setting"],
    "maze": ["M1_open_maze_short_route", "M2_gap_walled_reroutes", "M3_length_cap_install",
             "M3b_laid_hose_over_cap_retracts", "M4_unreachable_retracts", "M5_walls_removed_recovers",
             "P1_reel_couples_to_tank", "P2_lone_reel_not_coupled"],
    "relay": ["RL2_one_hose_cannot_reach", "RL3_hose_onto_relay_B", "RL4_relay_B_onward_to_C", "RL5_ring_refused",
              "RL6_debug_flow_propagates", "RL7_no_latch", "RL8_chain_beyond_one_hose", "RL9_overhead_drawn_over_hose"],
    "carry": ["CR1_deploy_carrying", "CR2_trail_follows_walk", "CR3_draft_drops_end", "CR5_resume_laid_at_target",
              "CR5b_laid_hose_plumps", "CR5c_end_kind", "CR6_retract_stored", "CR7_no_instant_gizmos_without_devmode"],
    "style_hose": ["R1_pick_reaches_reel", "R2_built_reels_stored_art", "R3_laid_out_per_look", "R5_reeled_in_per_look",
                   "R6_reinstall_keeps_look", "R7_legacy_reel_default_look"],
    "realflow": ["NS_hose_carries_real_units", "NS_hose_plumps_only_from_powered_pump", "NS_hose_tint_is_carried_liquid",
                 "NS_hose_dropped_carries_nothing", "NS_hose_port_removed_discovered", "NS_hose_port_removed_moves",
                 "NS_hose_far_end_pump", "NS_relay_chain_carries", "NS_pipe_and_hose_one_net",
                 "NS_tank_does_not_bridge_pipe_runs", "NS_external_pipe_is_visual_only", "NS_tank_feeds_hose"],
    "save_load": ["SL1_save_landed_new_file_only", "SL2_save_names_no_class_of_ours", "SL3_hoses_and_reel_styles_survive",
                  "SL4_carry_states_survive"],
    "preport": ["PP1_preport_midcarry_save_loads", "PP2_preport_midretract_save_loads"],
    "session": ["Z_log_budget"],
}


# The design catalog is built by design_spec.py, which needs numpy: WSL python3 has it, the bridge side (python.exe) does
# not, so run_live's `import design_spec` leaves D None there and load_catalog("design") raised on the first live run
# (2026-10-11, MATRIX_HOSE_block "'NoneType' object has no attribute 'build_spec'"). Same split as GSS proof_all: the offline
# gate (WSL) writes the catalog JSON here and the live side reads it.
SPEC_WIN = rm_win("scratch", "fw_hose_proof", "scenes_design.json")
SPEC_POSIX = rm_str("scratch", "fw_hose_proof", "scenes_design.json")


def _posix(p):
    import re
    m = re.match(r"^\\\\wsl(?:\.localhost|\$)\\[^\\]+\\(.*)$", p)
    return "/" + m.group(1).replace("\\", "/") if m else p


def hose_catalog():
    """run_live's catalog argument: "design" where design_spec imports (WSL), else the gate's JSON (python.exe), else None."""
    if not os.path.isdir(GSS_MATRIX):
        return None
    if GSS_MATRIX not in sys.path:
        sys.path.insert(0, GSS_MATRIX)
    import run_live as RL  # noqa: E402
    if getattr(RL, "D", True) is not None:     # a stub run_live (selftest) without D counts as importable
        return "design"
    return SPEC_WIN if os.path.exists(SPEC_WIN) else None


def hose_matrix_spec():
    """The nine hose scenes (GSS's design catalog, reduced.hose_spec), or None when Gimme Some Slack's matrix (or, on the
    python.exe side, the offline gate's catalog JSON) is not on disk."""
    cat = hose_catalog()
    if cat is None:
        return None
    import run_live as RL  # noqa: E402
    import reduced as RD  # noqa: E402
    with open(os.devnull, "w") as dn:
        so, sys.stdout = sys.stdout, dn
        try:
            return RD.hose_spec(RL.load_catalog(cat))
        finally:
            sys.stdout = so


def declared_rows():
    """Every row id a full `--live` run emits (offline, no bridge): DECLARED_ROWS plus "MX_<scene>" for the nine hose scenes.
    PP1/PP2 are declared too: a run without --preport-save reports them UNMEASURED, never silently absent."""
    out = []
    for ids in DECLARED_ROWS.values():
        out += [i for i in ids if i not in out]
    spec = hose_matrix_spec()
    if spec:
        out += ["MX_" + s["id"] for s in spec["scenes"]]
    return out


# ============================================================================ the bridge
class PB(VH.H):
    """call / hp (the hose probe) / ticks / probe_of on one socket."""


def _tank(B, cell):
    r = B.hp("tank:%d,%d" % tuple(cell))
    return r if r.get("success") else {}


def _hose(B, reel):
    for h in B.hp("census").get("hoses") or []:
        if tuple(h.get("reel") or ()) == tuple(reel):
            return h
    return {}


# ============================================================================ real-flow scenes (§3.6)
# One scene per plot, plots 26 x 14 in the north-east (clear of validation_hose's sites, x < 150). Layout in plot coords:
# a 3-cell water channel at (2..4, 6) dug 2 and filled 2; the pump at (3, 7) on its north bank; a battery at (6, 6);
# the reel 2x2 at (3, 8) north of the pump (it couples to it: Machine kind); the hose laid east to (16, 9); a tank 2x2 at
# (17, 9) whose west edge the hose end touches. The reel's nozzle faces west: (0..2, 8..11) is kept clear for the lead-out.
RF_X0, RF_Z0, RF_PW, RF_PH = 158, 150, 26, 14
# LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: probe "units" are raw tank units = decilitres. One level = 1,000 L = 10,000 units
# (was 5 drums); the old per-cycle bar 5 (and window 5..15) is x2000.
UNITS_PER_LEVEL = 10000
# HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK: a tank job moves RM_HoseSettings.tankLitresPerCycle (default 2,000 L = 20,000
# units) per settle; the old 5 x 2000 was the drum-era half-of-per-cycle bar converted, not the per-cycle amount.
PER_CYCLE_CAP = 2000 * 10
FILL_UNITS = 120000          # filltank staging: 12 kL of a 16 kL 2x2 tank (the old 100 exceeded the old 80 capacity)
RF_WEST = 6
# FINAL §3.6 / G6.4 contract: a new link is discovered <= 60 ticks after it is made (the reel's free-end cache), and liquid
# moves by the NEXT pump cycle (250 ticks, at the pump's own hash phase) after that. A flat 260-tick window from the lay is
# shorter than that bound (60 + 250), so it failed a mod meeting the contract whenever the pump's phase fell inside the
# discovery gap (first live run 2026-10-11: scene 0 read 0 units at +260 and plumped at +350). The bars below read the
# discovery tick and then the transfer within one cycle of it -- the contract itself, each half separately.
RF_DISCOVER, RF_CYCLE = 60, 250


def rf_plot(i):
    return (RF_X0 + (i % 3) * (RF_PW + 2), RF_Z0 + (i // 3) * (RF_PH + 2))


class Scene(object):
    def __init__(self, B, i):
        self.B = B
        self.bad = []       # build_batch replies that built less than asked: a row that FAILs over one is the staging, not the mod
        self.o = rf_plot(i)
        ox, oz = self.o
        self.channel = [(ox + 2 + k, oz + 6) for k in range(3)]
        self.pump = (ox + 3, oz + 7)
        self.battery = (ox + 6, oz + 6)
        self.reel = (ox + 3, oz + 8)
        self.end = (ox + 16, oz + 9)
        self.tank = (ox + 17, oz + 9)

    def P(self, dx, dz):
        return (self.o[0] + dx, self.o[1] + dz)

    def site(self, rows, rid):
        # 2026-10-11 (first live run, full list): the plot's reel sits 3 cells from the plot's west edge, but an un-fed reel's
        # hose leaves the west nozzle straight for OutletLead (~4.4) and turns there, i.e. onto the 2-cell gap between plots
        # that nobody prepared -- NS_relay_chain_carries' reel A was refused "no room for the straight lead-out" on whatever
        # the random map had there. Prepare RF_WEST cells west of the plot too (the previous plot's columns 22-25 are unused).
        return V.prepare_site(self.B, (self.o[0] - RF_WEST, self.o[1], RF_PW + RF_WEST, RF_PH), rows, rid)

    def water(self):
        for x, z in self.channel:
            self.B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=2, setFill=-1)
            self.B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=0, setFill=2)

    def build(self, *ops):
        asked = [o for o in ops if o]
        r = self.B.call("jawa/build_batch", ops=";".join(asked), faction="player", wipeExisting=False) or {}
        short = r.get("success") is False or (r.get("survived") is not None and r.get("survived") < len(asked))
        if short:
            self.bad.append({"ops": asked, "success": r.get("success"), "survived": r.get("survived"), "failed": r.get("failed")})
        return r

    def charge(self):
        lt = self.B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % self.battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            self.B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)

    def pump_scene(self, reel=True, tank=True):
        self.water()
        self.build("RM_LiquidPump:%d,%d" % self.pump, "Battery:%d,%d" % self.battery,
                   "RM_HoseReel:%d,%d" % self.reel if reel else None, "RM_LiquidTank:%d,%d" % self.tank if tank else None)
        self.B.ticks(2)
        self.charge()
        self.powered = _powered(self.B, self.pump)


    def lay(self, to=None):
        return self.B.hp("lay:%d,%d,%d,%d" % (self.reel + (to or self.end)))


def _powered(B, pump, bound=400, step=10):
    """Ticks until the pump reads powered. 2026-10-11 (full list, measured): a freshly built pump beside a just-charged battery
    read powered=false for ~100-130 ticks (vanilla's power net switches a new consumer on later, not at spawn), and a pump
    cycle in that gap moves nothing -- so a transfer window timed from the lay measured vanilla's power-up, not the hose. The
    real-flow bars start their clock once the pump is powered; an unpowered pump after `bound` is reported in the row."""
    v, w = _poll(B, lambda: B.hp("pump:%d,%d" % tuple(pump)).get("powered"), bound, step=step)
    return w if v else None


def _poll(B, fn, max_ticks, step=10):
    """Tick in steps until fn() is truthy; returns (value, ticks waited)."""
    waited = 0
    v = fn()
    while not v and waited < max_ticks:
        B.ticks(step)
        waited += step
        v = fn()
    return v, waited


def _discover(B, reel, bound=RF_DISCOVER, step=5):
    """Ticks until reel's hose reports a netLink (<= bound), stepped exactly; (link, ticks)."""
    return _poll(B, lambda: _hose(B, reel).get("netLink"), bound, step=step)


def _held(B, reels):
    """Units (decilitres) held IN the hoses of `reels` (CompHoseReel.heldUnits). Hoses hold liquid (rev 2 §3.7 L8,
    RM_LiquidNet.FillFrom): the first level a hose carries fills it from the destination tank, so that tank gains a level
    MINUS the hose's room (live 2026-10-19: 8,899 of 10,000 over a 13-cell hose). The level is conserved in tank + hoses."""
    tot = 0
    for reel in reels:
        hid = _hose(B, reel).get("id")
        if hid is None:
            continue
        v = ((B.call("jawa/comp_read", thing="RM_HoseReel%d" % hid, comp="CompHoseReel", members="heldUnits") or {})
             .get("values") or {}).get("heldUnits")
        try:
            tot += int(v or 0)
        except (TypeError, ValueError):
            pass
    return tot


def _moved(B, tank, u0, reels=(), h0=0, bound=RF_CYCLE + 10, step=10):
    """Ticks until one level (UNITS_PER_LEVEL) arrived over u0 at the tank at `tank`, counting what the route's hoses
    (`reels`, holding h0 at the start) took to fill (<= bound); (units now, ticks). The tank itself must gain."""
    def arrived():
        g = (_tank(B, tank).get("units") or 0) - u0
        return g > 0 and g + (_held(B, reels) - h0) >= UNITS_PER_LEVEL
    v, w = _poll(B, arrived, bound, step=step)
    return _tank(B, tank).get("units") or 0, w


def _set_tank_job(B, cell, job, max_clicks=4):
    """Cycle the tank's "Job:" gizmo to `job` (owner ruling #9: a tank feeds a hose screwed into it by one click on the tank,
    RM_LiquidNet.SettleTick moves only Fill/Empty tanks; Store, the default, moves nothing). Same route as liquid_checks."""
    out = {"clicks": 0, "ok": False, "want": "Job: " + job}
    B.call("rimworld/set_god_mode", enabled=True)
    try:
        B.call("rimworld/clear_selection")
        B.call("rimworld/click_cell", x=cell[0], z=cell[1])
        for _ in range(max_clicks + 1):
            gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
            g = next((q for q in gz if str(q.get("label") or "").startswith("Job:")), None)
            if g is None:
                out["labels"] = [q.get("label") for q in gz][:20]
                return out
            out["label"] = g.get("label")
            if g.get("label") == out["want"]:
                out["ok"] = True
                return out
            r = B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
            out["clicks"] += 1
            if r.get("success") is False:
                out["error"] = r
                return out
        return out
    finally:
        B.call("rimworld/set_god_mode", enabled=False)
        B.call("rimworld/clear_selection")


def realflow(B, rows):
    """The real-flow bars of hose port step 6 (FINAL §3.6). Each reads the FAR tank's units (G3.11), never the pump's neighbour."""
    def row(rid, ok, detail, cls="MOD", unmeasured=None, bad=None):
        if not ok and not unmeasured and bad:
            unmeasured = "the scene's buildings were not all built (build_batch survived < asked): %s" % json.dumps(bad, default=str)[:300]
        V.row(rows, rid, "UNMEASURED" if unmeasured else ("PASS" if ok else "FAIL"), "SITE" if unmeasured else cls,
              dict(detail, why=unmeasured) if unmeasured else detail)

    B.hp("defaults")
    # ---- scene 0: pump -> reel -> hose -> far tank
    s = Scene(B, 0)
    if not s.site(rows, "RF_site0_ready"):
        return
    s.pump_scene()
    lay = s.lay()
    t0 = _tank(B, s.tank)
    h0 = _held(B, [s.reel])
    link, dt = _discover(B, s.reel)
    u1, mt = _moved(B, s.tank, t0.get("units") or 0, [s.reel], h0)
    t1 = _tank(B, s.tank)
    h = _hose(B, s.reel)
    gained = (t1.get("units") or 0) - (t0.get("units") or 0)
    hose_took = _held(B, [s.reel]) - h0
    row("NS_hose_carries_real_units", lay.get("success") and link and dt <= RF_DISCOVER and gained > 0
        and gained + hose_took >= UNITS_PER_LEVEL and mt <= RF_CYCLE + 10 and (h.get("credits") or 0) > 0 and h.get("netLink"),
        {"lay": lay, "before": t0, "after": t1, "gained": gained, "hoseTook": hose_took, "discoveredAfterTicks": dt, "movedTicksAfterDiscovery": mt,
         "bound": [RF_DISCOVER, RF_CYCLE], "pumpPoweredAfterTicks": s.powered, "credits": h.get("credits"), "netLink": h.get("netLink")}, bad=s.bad)
    plump, waited = _poll(B, lambda: _hose(B, s.reel).get("state") == "Plump", 300)
    tint = _hose(B, s.reel).get("tintLiquid")
    row("NS_hose_tint_is_carried_liquid", tint == LIQUID_WATER, {"tintLiquid": tint, "want": LIQUID_WATER,
        "tarHalf": "UNMEASURED here: a tar channel needs a fresh map's active fluid (water ran first)"}, bad=s.bad)
    # power cut: destroy the battery -> no transfer -> flat no later than 1.5 x 250 + releaseTicks + transitionTicks = 905
    plumped_at = B.hp("census").get("tick")
    B.call("jawa/destroy_batch", rects="%d,%d,1,2" % s.battery, categories="Building")
    cut_tick = B.hp("census").get("tick")
    flat, w2 = _poll(B, lambda: _hose(B, s.reel).get("state") == "Flat", 1000)
    u_after = _tank(B, s.tank).get("units")
    B.ticks(300)
    u_later = _tank(B, s.tank).get("units")
    row("NS_hose_plumps_only_from_powered_pump", plump and flat and w2 <= 905 + 10 and u_later == u_after,
        {"plumpedAfterTicks": waited, "flatAfterCut": w2, "bound": 905, "plumpedAtTick": plumped_at, "cutTick": cut_tick,
         "tankStillAfterCut": [u_after, u_later]}, bad=s.bad)
    # ---- scene 1: a dropped hose carries nothing
    s1 = Scene(B, 1)
    if s1.site(rows, "RF_site1_ready"):
        s1.pump_scene()
        trail = ";".join("%d,%d" % c for c in [s1.reel] + [(s1.reel[0] + k, s1.reel[1] + 1) for k in range(1, 13)] + [s1.end])
        st = B.hp("settrail:%d,%d=dropped;%s" % (s1.reel + (trail,)))
        a0 = _tank(B, s1.tank).get("units")
        B.ticks(520)
        a1 = _tank(B, s1.tank).get("units")
        h1 = _hose(B, s1.reel)
        # can-fail (code review 2026-10-19): "the tank did not change" is vacuous when nothing could have moved -- an unbuilt tank
        # (units None) or an unpowered pump -- so the row first needs a live tank and a powered pump to mean anything
        if a0 is None or s1.powered is None or s1.bad:
            row("NS_hose_dropped_carries_nothing", False, {"staged": st, "units": [a0, a1], "pumpPoweredAfterTicks": s1.powered, "bad": s1.bad},
                unmeasured="the dropped-hose scene could not move liquid anyway (tank unread %s, pump powered %s, unbuilt %s)" % (a0 is None, s1.powered is not None, bool(s1.bad)))
        else:
            row("NS_hose_dropped_carries_nothing", st.get("carry") == "Dropped" and a0 == a1 and not h1.get("netLink"),
                {"staged": st, "units": [a0, a1], "netLink": h1.get("netLink"), "pumpPoweredAfterTicks": s1.powered})
    # ---- scene 2: the far tank removed mid-flow, then rebuilt (G6.4: discovery read at an exact tick, transfer by next cycle)
    s2 = Scene(B, 2)
    if s2.site(rows, "RF_site2_ready"):
        s2.pump_scene()
        s2.lay()
        B.ticks(260)
        B.call("jawa/destroy_batch", rects="%d,%d,2,2" % s2.tank, categories="Building")
        B.ticks(61)
        gone = _hose(B, s2.reel).get("netLink")
        s2.build("RM_LiquidTank:%d,%d" % s2.tank)
        B.ticks(61)                            # the reel's free-end cache re-reads within 60 ticks; the index rebuilds per tick
        found = _hose(B, s2.reel).get("netLink")
        row("NS_hose_port_removed_discovered", gone is None and found is not None, {"afterRemove": gone, "afterRebuild61": found}, bad=s2.bad)
        b0 = _tank(B, s2.tank).get("units") or 0
        B.ticks(260)
        b1 = _tank(B, s2.tank).get("units") or 0
        row("NS_hose_port_removed_moves", b1 - b0 >= UNITS_PER_LEVEL, {"units": [b0, b1]}, bad=s2.bad)
    # ---- scene 3: the pump at the FAR end, the tank beside the reel (M2); bars below were ">= 5" (one level) in the drum era
    s3 = Scene(B, 3)
    if s3.site(rows, "RF_site3_ready"):
        ox, oz = s3.o
        tank_at_reel = (ox + 3, oz + 10)                       # north of the reel: the reel's port is the tank
        far_pump, far_ch, far_bat = (ox + 17, oz + 9), [(ox + 18 + k, oz + 9) for k in range(3)], (ox + 17, oz + 11)
        for x, z in far_ch:
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=2, setFill=-1)
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=0, setFill=2)
        s3.build("RM_HoseReel:%d,%d" % s3.reel, "RM_LiquidTank:%d,%d" % tank_at_reel, "RM_LiquidPump:%d,%d" % far_pump,
                 "Battery:%d,%d" % far_bat)
        B.ticks(2)
        s3.battery = far_bat
        s3.charge()
        s3.powered = _powered(B, far_pump)
        lay3 = s3.lay((ox + 16, oz + 9))
        c0 = _tank(B, tank_at_reel).get("units") or 0
        g0 = _held(B, [s3.reel])
        link, dt = _discover(B, s3.reel)
        c1, mt = _moved(B, tank_at_reel, c0, [s3.reel], g0)
        took3 = _held(B, [s3.reel]) - g0
        row("NS_hose_far_end_pump", link and dt <= RF_DISCOVER and c1 - c0 > 0 and c1 - c0 + took3 >= UNITS_PER_LEVEL and mt <= RF_CYCLE + 10,
            {"lay": lay3, "units": [c0, c1], "hoseTook": took3, "pumpPoweredAfterTicks": s3.powered, "discoveredAfterTicks": dt, "movedTicksAfterDiscovery": mt, "netLink": link,
             "net": B.hp("net:%d,%d" % far_pump)}, bad=s3.bad)
    # ---- scene 4: relay chain pump -> reel A -> reel B -> tank (both hoses credited)
    s4 = Scene(B, 4)
    if s4.site(rows, "RF_site4_ready"):
        ox, oz = s4.o
        relay_b, tank_b = (ox + 13, oz + 8), (ox + 23, oz + 9)
        s4.pump_scene(tank=False)
        s4.build("RM_HoseReel:%d,%d" % relay_b, "RM_LiquidTank:%d,%d" % tank_b)
        B.ticks(2)
        # A is aimed ONTO B's own south-west footprint cell, the way a relay is made (validation_hose RL3: the hose ends on
        # B's intake, relayTo = B); 2026-10-11 the first live run aimed it at the cell WEST of B, which is a free end, not a relay
        la = B.hp("lay:%d,%d,%d,%d" % (s4.reel + relay_b))
        lb = B.hp("lay:%d,%d,%d,%d" % (relay_b + (tank_b[0] - 1, tank_b[1])))
        d0 = _tank(B, tank_b).get("units") or 0
        k0 = _held(B, [s4.reel, relay_b])
        lkb, dtb = _discover(B, relay_b)
        d1, mt = _moved(B, tank_b, d0, [s4.reel, relay_b], k0)
        took4 = _held(B, [s4.reel, relay_b]) - k0
        ha, hb = _hose(B, s4.reel), _hose(B, relay_b)
        row("NS_relay_chain_carries", d1 - d0 > 0 and d1 - d0 + took4 >= UNITS_PER_LEVEL and lkb and dtb <= RF_DISCOVER and mt <= RF_CYCLE + 10
            and (ha.get("credits") or 0) > 0 and (hb.get("credits") or 0) > 0,
            {"layA": la, "layB": lb, "relayTo": ha.get("relayTo"), "pumpPoweredAfterTicks": s4.powered, "units": [d0, d1], "hoseTook": took4, "discoveredAfterTicks(B)": dtb,
             "movedTicksAfterDiscovery": mt, "creditsA": ha.get("credits"), "creditsB": hb.get("credits")}, bad=s4.bad)
    # ---- scene 5: pump -> universal pipe run -> reel -> hose -> tank; and two pipe runs never merge through a tank
    s5 = Scene(B, 5)
    if s5.site(rows, "RF_site5_ready"):
        ox, oz = s5.o
        s5.water()
        pipe = [(ox + 3, oz + 8 + k) for k in range(3)]          # north from the pump
        reel5 = (ox + 4, oz + 10)                               # the reel beside the pipe's last cell (west edge on (ox+3, oz+10))
        tank5 = (ox + 17, oz + 10)
        s5.build("RM_LiquidPump:%d,%d" % s5.pump, "Battery:%d,%d" % s5.battery, *["RM_UniversalPipe:%d,%d" % c for c in pipe])
        s5.build("RM_HoseReel:%d,%d" % reel5, "RM_LiquidTank:%d,%d" % tank5)
        B.ticks(2)
        s5.charge()
        s5.powered = _powered(B, s5.pump)
        lp = B.hp("lay:%d,%d,%d,%d" % (reel5 + (tank5[0] - 1, tank5[1])))
        e0 = _tank(B, tank5).get("units") or 0
        k5 = _held(B, [reel5])
        B.ticks(300)
        e1 = _tank(B, tank5).get("units") or 0
        # pass 2 (2026-10-19, HARNESS): the hose's first fill comes out of the level (see _held): 8,950 + the hose's room
        # was read as a FAIL against a bare 10,000 bar -- the same fault f93867b198 fixed in scenes 1-4 and 6
        took5 = _held(B, [reel5]) - k5
        row("NS_pipe_and_hose_one_net", e1 - e0 > 0 and e1 - e0 + took5 >= UNITS_PER_LEVEL,
            {"lay": lp, "units": [e0, e1], "hoseTook": took5, "net": B.hp("net:%d,%d" % s5.pump)}, bad=s5.bad)
        # a second pipe run touching a mid tank (and a tank V on it) must stay out of the pump's net
        # A 2x2 tank at (x,z) occupies x..x+1, z..z+1. Live run 6 (2026-10-19) put V at (ox+1, oz+13): its z+1 row is oz+14, one row
        # past the prepared plot (RF_PH=14 -> oz..oz+13), so V was never built (SITE). V now sits WEST of the pipe run, inside the
        # RF_WEST-prepared strip (since 2026-10-20 at oz+8..oz+9, see below), touching run 2's pipe cells from the other side than mid.
        # Code review 2026-10-20: mid at (ox+1, oz+11) met run 1's last pipe (ox+3, oz+10) only corner to corner, so it touched
        # ONE run and the row could not fail. It now sits WEST of run 1 at (ox+1, oz+8): ox+1..ox+2, oz+8..oz+9, edge to edge with
        # pipes (ox+3, oz+8/9), clear of the channel (oz+6), the pump (ox+3, oz+7) and reel5's west lead-out (row oz+10). Run 2
        # is (ox, oz+8/9) on mid's west edge, and V (ox-2..ox-1, oz+8..oz+9) on run 2's west: a real bridge for the mod to refuse.
        mid, v = (ox + 1, oz + 8), (ox - 2, oz + 8)
        bb = s5.build("RM_LiquidTank:%d,%d" % mid, "RM_UniversalPipe:%d,%d" % (ox + 0, oz + 8), "RM_UniversalPipe:%d,%d" % (ox + 0, oz + 9),
                      "RM_LiquidTank:%d,%d" % v)
        B.ticks(300)
        net = B.hp("net:%d,%d" % s5.pump)
        reached = [tuple(t.get("tank") or ()) for t in net.get("tanks") or []]
        # can-fail on an empty probe (code review 2026-10-11): an empty or failed net read used to PASS ("v not in []"). The probe
        # must first see the pump's own hose-fed tank (tank5), and V must really stand, before "V is absent" means anything.
        saw_own, v_built = tuple(tank5) in reached, bool(_tank(B, v))
        mid_built = bool(_tank(B, mid))
        if not (mid_built and v_built):
            # a tank that was not built measures the staging, not the mod: UNMEASURED SITE, with the build_batch reply for the cause
            row("NS_tank_does_not_bridge_pipe_runs", False, {"reached": reached, "secondRunTank": v, "midTankBuilt": mid_built,
                "secondRunTankBuilt": v_built, "build": bb}, unmeasured="the second pipe run's tanks were not both built (mid %s, V %s)" % (mid_built, v_built))
        else:
            row("NS_tank_does_not_bridge_pipe_runs", saw_own and tuple(v) not in reached,
                {"reached": reached, "secondRunTank": v, "probeSawPumpTank": saw_own, "secondRunTankBuilt": v_built})
    # ---- an external (VE PipeSystem) pipe: visual only. Needs a VE pipe def on the list.
    ve = B.call("jawa/get_defs", defs="ThingDef/VPE_PipeChemfuel") or {}
    row("NS_external_pipe_is_visual_only", False, {"probe": ve.get("foundCount")},
        unmeasured=("no VE PipeSystem pipe on the flowworks tier" if not ve.get("foundCount") else
                    "a VE pipe def is loaded but no live scene is written for it") +
                   ": the offline kernel row (HoseNetChecks) is the evidence")
    # ---- scene 6: owner Q7 -- a tank feeds a hose screwed into it, no pump
    s6 = Scene(B, 6)
    if s6.site(rows, "RF_site6_ready"):
        ox, oz = s6.o
        src = (ox + 3, oz + 10)
        s6.build("RM_HoseReel:%d,%d" % s6.reel, "RM_LiquidTank:%d,%d" % src, "RM_LiquidTank:%d,%d" % s6.tank)
        B.ticks(2)
        fill = B.hp("filltank:%d,%d=%s,%d" % (src + (LIQUID_WATER, FILL_UNITS)))
        s6.lay()
        # the source tank's job must be Empty: a Store tank (the default) never sends (RM_LiquidNet.SettleTick); live run 6
        # left it Store and read 0 moved, which measured the harness, not the mod
        job = _set_tank_job(B, src, "Empty")
        if not job.get("ok"):
            row("NS_tank_feeds_hose", False, {"job": job, "fill": fill},
                unmeasured="could not set the source tank's job to Empty (no Job: gizmo or it would not cycle)")
        else:
            s0 = _tank(B, src).get("units") or 0
            f0 = _tank(B, s6.tank).get("units") or 0
            q0 = _held(B, [s6.reel])
            B.ticks(520)
            f1 = _tank(B, s6.tank).get("units") or 0
            s1u = _tank(B, src).get("units") or 0
            took6 = _held(B, [s6.reel]) - q0
            h6 = _hose(B, s6.reel)
            # 520 ticks hold 2 or 3 settles (phase); each sends PER_CYCLE_CAP; the hose's first fill is part of what left src
            row("NS_tank_feeds_hose", f1 - f0 > 0 and PER_CYCLE_CAP <= f1 - f0 + took6 <= 3 * PER_CYCLE_CAP and s0 - s1u >= f1 - f0 + took6
                and (h6.get("credits") or 0) > 0,
                {"units": [f0, f1], "source": [s0, s1u], "hoseTook": took6, "perCycleCap": PER_CYCLE_CAP, "job": job, "fill": fill,
                 "credits": h6.get("credits"), "netLink": h6.get("netLink")}, bad=s6.bad)


# ============================================================================ the session
class Proof(object):
    def __init__(self, args, bridge=None):
        self.args = args
        self.rows = []
        self.blocks = collections.OrderedDict()
        self.t0 = time.time()
        self.B = bridge or PB()
        self.log_base = 0
        self.res = {"mod": "FlowWorks", "script": "proof_hose.py", "tier": TIER, "mode": "live" if not args.only else "partial",
                    "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": self.rows, "blocks": self.blocks,
                    "doc": "design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md"}

    def row(self, block, rid, status, cls, detail):
        self.rows.append({"id": rid, "status": status, "class": cls, "detail": detail, "block": block})
        print("%-34s %-10s %-8s %s" % (rid, status, cls, json.dumps(detail, default=str)[:150]), flush=True)

    def want(self, name):
        return not self.args.only or name in ("preflight", "session") or name in self.args.only

    def ns(self, **kw):
        return argparse.Namespace(**dict({"save": None, "save_load": None, "removal_check": None, "fresh_map": False, "out": None}, **kw))

    def checkpoint(self, final=False):
        path = getattr(self, "out_path", None)
        if not path:
            return
        res = self.res
        res["wall_s"] = round(time.time() - self.t0, 1)
        res["site_notes"] = V.SITE_NOTES
        if not final:
            res["mode"], res["certifiable"] = "partial", False
        else:
            res["mode"] = "live" if not (self.args.only or getattr(self.args, "skip_offline", False)) else "partial"
            res["certifiable"] = res["mode"] == "live" and not res.get("aborted") and not res.get("run_raised") \
                and not any(b.get("raised") for b in self.blocks.values())
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(tmp, path)

    def block(self, name, fn):
        if not self.want(name):
            return None
        t, n0, err = time.time(), len(self.rows), None
        print("== %s" % name, flush=True)
        if name not in ("preflight", "session"):
            try:
                self.B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
                self.res.setdefault("site_calm_blocks", {})[name] = V.site_calm(self.B).get("ok")   # statics reset by any load
                # a giant plant regrown near a site re-plans trunk blockers into it (V.clear_huge_plants), re-calmed per block
                self.res.setdefault("huge_plants_cleared", {})[name] = V.clear_huge_plants(self.B)
            except Exception as ex:  # noqa: BLE001
                # a block that ran on an un-calmed map must say so (code review 2026-10-19): recorded, not swallowed
                self.res.setdefault("site_calm_errors", {})[name] = repr(ex)
        try:
            fn()
        except Exception as ex:  # noqa: BLE001
            import traceback
            err = "%r" % ex
            self.row(name, "%s_block" % name.upper(), "FAIL", "HARNESS", {"raised": err, "trace": traceback.format_exc()[-1200:]})
        if V.TAP:
            try:
                V.TAP[0].poll()
            except Exception:  # noqa: BLE001
                pass
        self.blocks[name] = {"wall_s": round(time.time() - t, 1), "rows": len(self.rows) - n0, "raised": err}
        self.checkpoint()

    def take(self, name, res):
        for r in (res or {}).get("rows") or []:
            self.rows.append(dict(r, block=name))
        if (res or {}).get("aborted"):
            self.row(name, "%s_aborted" % name.upper(), "FAIL", "HARNESS", res["aborted"])

    # ---------------------------------------------------------------- preflight
    def preflight(self):
        B = self.B
        if not self.args.no_fresh_map:
            B.call("rimworld/go_to_main_menu")
            B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, waited = V._wait_playing(B, leave_s=0)
        rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
        running = [p.lower() for p in rm.get("packageIds") or []]
        self.res["log_revive"] = V.log_revive(B)     # the log budget (Z) is blind once Verse.Log hit its 10,000 cap
        lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning") or {}
        logs0 = lg0.get("logs") or []
        self.log_base = max([x.get("Sequence", 0) for x in logs0] or [0])
        V.tap_start(B)                               # the journal is a 1,000-entry ring: keep warn+ as they pass (V.LogTap)
        pre = [x.get("Message", "")[:200] for x in logs0 if any(o in (x.get("Message", "") + x.get("StackTrace", "")) for o in OURS)
               and (x.get("Level") or "").lower() in ("error", "exception")]
        try:
            sys.path.insert(0, os.path.join(UTILS, "modcheck"))
            import status as _mc  # noqa: E402
            self.res["mod_hash"] = _mc.mod_hash(MOD)
        except Exception as ex:  # noqa: BLE001
            self.res["mod_hash"], self.res["mod_hash_error"] = None, repr(ex)
        self.gss_active = "mandrake.rm.gimmesomeslack" in running
        on = PKG in running
        self.row("preflight", "HP1_tier_running_startup_log_clean", "PASS" if ok and on and not pre else "FAIL", "MOD" if on else "SITE",
                 {"playing": ok, "flowworks": on, "gimmesomeslack": self.gss_active, "startupErrorsNamingHose": pre[:6]})
        hd = B.hp("defaults")
        B.call("jawa/weather_set", weather="Clear", lockWeather=True)
        B.call("jawa/incident_queue_clear")
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        self.res["site_calm"] = V.site_calm(B)       # static boring world: storyteller/mental/disease off, wild spawner blocked
        drafted = [p["id"] for p in (B.hp("colonists").get("pawns") or []) if B.hp("pawn:%d=draft" % p["id"]).get("success")]
        self.row("preflight", "HP2_probes_site_pinned", "PASS" if hd.get("success") else "FAIL", "HARNESS",
                 {"hoseProbe": hd.get("success"), "colonistsDrafted": drafted})
        if not hd.get("success"):
            raise RuntimeError("the hose probe is dead")

    # ---------------------------------------------------------------- matrix (cross-mod)
    def matrix_hose(self):
        spec = hose_matrix_spec()
        if spec is None or not getattr(self, "gss_active", False):
            for s in (spec or {}).get("scenes") or []:
                self.row("matrix_hose", "MX_" + s["id"], "UNMEASURED", "SITE", "the hose matrix scenes draw cords too: they need "
                         "Gimme Some Slack active and its northstar_matrix on disk")
            return
        import run_live as RL  # noqa: E402
        a = argparse.Namespace(catalog=hose_catalog(), only=["H"], max_boards=0, progress=None, verbose=False, fresh_map=False)
        res = RL.run(a, RL.LiveBridge(), mock=False)
        # review S7: GSS's old proof_all folded a PASSING H0_probe_channel (the matrix runner's own "HoseProbe defaults applied"
        # harness row) into its probe row; HP2_probes_site_pinned is that successor here (it fails on the same hp("defaults")).
        # A FAILING one is not dropped: every hose scene row it would have backed reads FAIL with its detail, so the declared
        # ids stay fixed and the matrix never passes on a dead probe channel.
        dead = [r for r in res.get("rows") or [] if r.get("id") == "H0_probe_channel" and r.get("status") != "PASS"]
        got = res.get("scenes") or {}
        # code review 2026-10-20: a declared scene the runner never returned is a row, not a silence
        for s in (spec or {}).get("scenes") or []:
            if s["id"] not in got:
                self.row("matrix_hose", "MX_" + s["id"], "UNMEASURED", "HARNESS", "the matrix runner returned no result for this scene")
        for sid, sc in got.items():
            if dead:
                self.row("matrix_hose", "MX_" + sid, "FAIL", "HARNESS", {"H0_probe_channel": dead[0].get("detail")})
                continue
            self.row("matrix_hose", "MX_" + sid, sc.get("status", "UNMEASURED"), "MOD", sc.get("detail") or sc.get("census"))

    # ---------------------------------------------------------------- the one save (hose half of GSS's old SL1-SL4)
    @staticmethod
    def _hose_by(c, reel):
        for h in c.get("hoses") or []:
            if tuple(h["reel"]) == tuple(reel):
                return h
        return {}

    def _poll_reel(self, reel, pred, max_ticks, step=30):
        B, waited, seen = self.B, 0, []
        while True:
            h = self._hose_by(B.hp("census"), reel)
            if h.get("carry") not in seen:
                seen.append(h.get("carry"))
            if pred(h) or waited >= max_ticks:
                return h, waited, seen
            B.ticks(step)
            waited += step

    # review S7: restored from GSS's proof_all (f8fee03e4, stage_carry_for_save). SL4 needs one hose DROPPED (reel 1: deploy,
    # carry, draft mid-walk) and one CARRYING (reel 2) at the moment of the save, and records both stagings (reel1_staged /
    # reel2_staged) so a half that could not be staged reads UNMEASURED, never PASS. Not yet run live after the port.
    CARRY_REEL2 = (VH.CX0 + 2, VH.CZ0 + 14)
    CARRY_TARGET2 = (VH.CX0 + 26, VH.CZ0 + 14)

    def stage_carry_for_save(self):
        """SL4 staging: reel 1 DROPPED (deploy, carry, draft mid-walk) and reel 2 CARRYING at the moment of the save."""
        B = self.B
        reel1, tgt1 = VH.CREEL, VH.CTARGET
        reel2, tgt2 = self.CARRY_REEL2, self.CARRY_TARGET2
        st = {"reel1": list(reel1), "reel2": list(reel2)}
        br = B.call("jawa/build_batch", ops="RM_HoseReel:%d,%d" % reel2, faction="player", wipeExisting=False) or {}
        reel2_built = br.get("success") is not False and (br.get("survived") is None or br.get("survived") >= 1)
        B.ticks(2)
        pawns = [p for p in B.hp("colonists").get("pawns") or [] if not p.get("downed")]
        st["colonists"] = len(pawns)
        if not pawns:
            return dict(st, error="no colonist")
        p1 = pawns[0]["id"]
        for p in pawns:
            if p.get("drafted"):
                B.hp("pawn:%d=undraft" % p["id"])
        # every colonist the staging does not use is drafted until the save/load is read (an idle one took reel 1's KEPT
        # Deploy order through the WorkGiver before the save, 2026-10-10), then released
        self.idle_drafted = [p["id"] for p in pawns[2:]]
        for p in pawns[1:]:
            B.hp("pawn:%d=draft" % p["id"])
        B.hp("pawn:%d=tp:%d,%d" % ((p1,) + VH.CSTAND))
        B.hp("order:%d,%d=deploy:%d,%d" % (reel1 + tgt1))
        B.hp("startjob:%d,%d=forced;%d" % (reel1 + (p1,)))
        h, w, seen = self._poll_reel(reel1, lambda x: x.get("carry") == "Carrying", 600, step=3)
        VH._walk_a_little(B, reel1)
        B.hp("pawn:%d=draft" % p1)
        B.ticks(35)
        h1 = self._hose_by(B.hp("census"), reel1)
        st["reel1_staged"] = {"carry": h1.get("carry"), "seen": seen, "pawn": p1}
        st["p1"] = p1
        if not reel2_built:
            st["reel2_staged"] = {"error": "reel 2 was not built (build_batch: %s)" % json.dumps(br, default=str)[:200]}
            return st
        if len(pawns) < 2:
            st["reel2_staged"] = {"error": "only one free colonist: the CARRYING half cannot be staged"}
            return st
        p2 = pawns[1]["id"]
        B.hp("pawn:%d=undraft" % p2)
        B.hp("pawn:%d=tp:%d,%d" % ((p2,) + (VH.CX0 + 5, VH.CZ0 + 14)))
        B.hp("order:%d,%d=deploy:%d,%d" % (reel2 + tgt2))
        B.hp("startjob:%d,%d=forced;%d" % (reel2 + (p2,)))
        h, w, seen = self._poll_reel(reel2, lambda x: x.get("carry") == "Carrying", 600, step=3)
        VH._walk_a_little(B, reel2)
        st["reel2_staged"] = {"carry": self._hose_by(B.hp("census"), reel2).get("carry"), "seen": seen, "pawn": p2}
        st["p2"] = p2
        return st

    def save_load(self):
        B = self.B
        carry = self.stage_carry_for_save() if self.want("carry") else {"error": "carry block not run"}
        reel1, reel2 = VH.CREEL, self.CARRY_REEL2
        c_a = B.hp("census")
        keys = ("carry", "far", "trailCount", "trailLast", "pending", "pendingAt")
        r1a = {k: VH._carry_view(self._hose_by(c_a, reel1))[k] for k in keys}
        r2a = VH._carry_view(self._hose_by(c_a, reel2))
        hose_jobs = sum(1 for p in B.hp("colonists").get("pawns") or [] if str(p.get("job") or "").startswith(("RM_CarryHoseEnd", "RM_RetractHose")))
        name = self.args.save_name or "RM_fw_hose_proof_%s" % time.strftime("%Y%m%d%H%M%S")
        before = V._saves_stat()
        if name + ".rws" in before:
            self.row("save_load", "SL1_save_landed_new_file_only", "FAIL", "HARNESS", "%s.rws exists" % name)
            return
        B.call("rimworld/save_game", saveName=name)
        V._wait_saved(name)
        after = V._saves_stat()
        new = sorted(set(after) - set(before))
        changed = sorted(n for n in before if n in after and after[n] != before[n])
        ok = new == [name + ".rws"] and not changed
        self.res["save"] = name + ".rws"
        self.row("save_load", "SL1_save_landed_new_file_only", "PASS" if ok else "FAIL", "HARNESS", {"new": new, "changed": changed})
        if not ok:
            return
        with open(os.path.join(V.SAVES, name + ".rws"), "rb") as f:
            blob = f.read()
        hits = VH.save_class_hits(blob)
        styles = {l: blob.count(("RM_HoseReel_%s" % l).encode()) for l in VSH.LOOKS}
        sl2 = not hits["offending"] and hits["rmHoseState"] >= 1 and hits["drivers"] <= max(hose_jobs, 0)
        self.row("save_load", "SL2_save_names_no_class_of_ours", "PASS" if sl2 else "FAIL", "MOD",
                 dict(hits, colonistsOnHoseJobsAtSave=hose_jobs, hoseReelStylesInSave=styles))
        B.call("rimworld/load_game", saveName=name)
        ok2, waited = V._wait_playing(B)
        if not ok2:
            self.row("save_load", "SL3_hoses_and_reel_styles_survive", "FAIL", "SITE", {"state": waited})
            return
        c_b = B.hp("census")       # hoses first, before any tick (a carried reel moves with every tick)
        r1b = {k: VH._carry_view(self._hose_by(c_b, reel1))[k] for k in keys}
        r2b = VH._carry_view(self._hose_by(c_b, reel2))
        sa, sb = VH._hose_set(c_a), VH._hose_set(c_b)
        ra, rb = VSH._snapshot(c_a), VSH._snapshot(c_b)
        self.row("save_load", "SL3_hoses_and_reel_styles_survive", "PASS" if sa == sb and ra == rb and sa else "FAIL", "MOD",
                 {"hoses": len(sa), "hosesEqual": sa == sb, "reelStylesEqual": ra == rb, "loadSeconds": waited})
        carry_a = {tuple(h["reel"]): VH._carry_view(h) for h in c_a.get("hoses") or [] if h.get("carry") in ("Carrying", "Dropped")}
        carry_b = {tuple(h["reel"]): VH._carry_view(h) for h in c_b.get("hoses") or [] if tuple(h["reel"]) in carry_a}
        st, cls, laid = sl4_verdict(carry, r1a, r1b, r2a, r2b, carry_a, carry_b), "MOD", {}
        if st == "PASS" and carry.get("p2"):
            # CR5 after load: the carried hose resumes and lands Laid at its target
            if r2b.get("carry") == "Dropped":
                B.hp("startjob:%d,%d=work;%d" % (reel2 + (carry["p2"],)))
            h, w, seen = self._poll_reel(reel2, lambda x: x.get("carry") == "Laid", 1200)
            laid = {"carry": h.get("carry"), "far": h.get("far"), "pending": h.get("pending"), "ticks": w, "seen": seen}
            if not (laid.get("carry") == "Laid" and tuple(laid.get("far") or ()) == self.CARRY_TARGET2):
                st = "FAIL"
        if st == "UNMEASURED":
            cls = "SITE"
        self.row("save_load", "SL4_carry_states_survive", st, cls,
                 {"dropped(CR4a)": {"before": r1a, "after": r1b}, "carrying(CR4b)": {"before": r2a, "after": r2b},
                  "resumedAfterLoad(CR5)": laid, "staging": carry,
                  "allCarried": {"before": {str(k): v for k, v in carry_a.items()}, "after": {str(k): v for k, v in carry_b.items()}}})
        for pid in [carry.get("p1")] + list(getattr(self, "idle_drafted", [])):
            if pid:
                B.hp("pawn:%d=undraft" % pid)

    # ---------------------------------------------------------------- pre-port saves (G5.9)
    def preport(self):
        names = [x for x in (self.args.preport_save or "").split(",") if x]
        ids = DECLARED_ROWS["preport"]
        if len(names) != 2:
            for rid in ids:
                self.row("preport", rid, "UNMEASURED", "SITE", "needs --preport-save MIDCARRY,MIDRETRACT: two saves made BEFORE the "
                         "port, one with a colonist mid-carry and one mid-retract")
            return
        B = self.B
        for rid, name in zip(ids, names):
            base = max([x.get("Sequence", 0) for x in (B.call("rimbridge/list_logs", limit=500, minimumLevel="warning") or {}).get("logs") or []] or [0])
            B.call("rimworld/load_game", saveName=name)
            ok, waited = V._wait_playing(B)
            B.ticks(60)
            new = [e for e in (B.call("rimbridge/list_logs", limit=500, minimumLevel="warning") or {}).get("logs") or [] if (e.get("Sequence") or 0) > base]
            text = [str(e.get("Message", "")) for e in new]
            bad = [t[:200] for t in text if "Cleaning up invalid job state" in t or (("Could not find" in t or "Could not resolve" in t) and VH.names_hose_class(t))]
            jobs = [p.get("job") for p in B.hp("colonists").get("pawns") or []]
            if not ok:
                # a load that never reached Playing measured the site, not the mod (as SL3 rules it) -- review 2026-10-20
                self.row("preport", rid, "UNMEASURED", "SITE", {"save": name, "loaded": ok, "loadSeconds": waited, "badLines": bad[:4]})
                continue
            self.row("preport", rid, "PASS" if not bad and any(str(j).startswith(("RM_CarryHoseEnd", "RM_RetractHose")) for j in jobs) else "FAIL",
                     "MOD", {"save": name, "loaded": ok, "loadSeconds": waited, "badLines": bad[:4], "jobs": jobs})

    # ---------------------------------------------------------------- Z
    def log_budget(self):
        tap = V.TAP[0] if V.TAP else None
        if tap is not None:
            new = tap.since(self.log_base)
        else:
            lg = self.B.call("rimbridge/list_logs", limit=1000, minimumLevel="warning") or {}
            new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > self.log_base]
        errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
        ours = [e for e in errs if any(o in str(e.get("Message", "")) + str(e.get("StackTrace", "")) for o in OURS)]
        site = [e for e in errs if "non-destroyable" in str(e.get("Message", ""))]
        alive = V.log_alive(self.B, "Z")
        if tap is not None and tap.lost:
            self.row("session", "Z_log_budget", "UNMEASURED", "HARNESS", {"why": "%d journal entries scrolled out of RimBridge's "
                     "1,000-entry ring between two polls: the budget did not see the whole run" % tap.lost, "polls": tap.polls, "gaps": tap.gaps,
                     "errorsSeen": len(errs), "ours": [str(e.get("Message", ""))[:200] for e in ours[:6]]})
            return
        if not alive["alive"]:
            self.row("session", "Z_log_budget", "UNMEASURED", "HARNESS", {"why": "logging is dead (Verse.Log message cap?): the "
                     "sentinel warning never reached the journal, so 0 errors here is not evidence", "sentinel": alive,
                     "revive": self.res.get("log_revive"), "errorsSeen": len(errs)})
            return
        self.row("session", "Z_log_budget", "PASS" if not ours else "FAIL", "MOD",
                 {"errorsNamingHoseOrFlowWorks": [str(e.get("Message", ""))[:240] for e in ours[:10]], "otherErrors": len(errs) - len(ours),
                  "tap": {"polls": tap.polls, "lost": tap.lost, "kept": len(tap.entries)} if tap else None,
                  "siteClearErrors": len(site), "newWarnings": len(new)})

    def run(self):
        V.SHARED = True
        self.block("preflight", self.preflight)
        if any(r["status"] != "PASS" for r in self.rows if r.get("block") == "preflight"):
            self.res["aborted"] = "preflight not green"
            return
        self.block("matrix_hose", self.matrix_hose)
        self.block("hose", lambda: self.take("hose", VH.run_live(self.ns())))
        self.block("maze", lambda: self.take("maze", VH.run_maze(self.ns())))
        self.block("relay", lambda: self.take("relay", VH.run_relay(self.ns())))
        self.block("carry", lambda: self.take("carry", VH.run_carry(self.ns())))
        self.block("style_hose", lambda: self.take("style_hose", VSH.run_live(self.ns())))
        self.block("realflow", lambda: self.take("realflow", _rf(self.B)))
        self.block("save_load", self.save_load)
        self.block("preport", self.preport)
        self.block("session", self.log_budget)


def sl4_verdict(carry, r1a, r1b, r2a, r2b, carry_a, carry_b):
    """SL4 before the CR5 resume read (review S7, GSS's old SL4 restored): reel 1 staged DROPPED round-trips exactly, reel 2
    staged CARRYING comes back Carrying or Dropped with its trail and its Deploy order, and every other carried hose survives.
    UNMEASURED when a half could not be staged (no colonist, one colonist, the carry block not run) -- never PASS on half."""
    if carry.get("error") or (carry.get("reel2_staged") or {}).get("error") or not carry.get("reel1_staged"):
        return "UNMEASURED"
    good1 = r1a.get("carry") == "Dropped" and r1a == r1b
    good2 = (r2a.get("carry") == "Carrying" and r2b.get("carry") in ("Carrying", "Dropped") and (r2b.get("trailCount") or 0) > 0
             and r2b.get("pending") == "Deploy")
    rest = all(carry_b.get(k, {}).get("carry") in ("Carrying", "Dropped") for k in carry_a)
    return "PASS" if good1 and good2 and rest else "FAIL"


def _rf(B):
    rows = []
    realflow(B, rows)
    return {"rows": rows}


# ============================================================================ offline gate
def offline_gate():
    """The offline tier (WSL python3): the hose's offline rows, the C# SelfTest (hose suites), the hose port gates, the
    validation_style_hose R0 row and this driver's own selftest. Any red refuses to go live."""
    import subprocess
    steps, red = {}, []
    for name, cmd in (("hose_offline", [sys.executable, os.path.join(MOD, "validation_hose_offline.py")]),
                      ("style_hose_R0", [sys.executable, os.path.join(MOD, "validation_style_hose.py"), "--offline"]),
                      ("hose_port_gates", [sys.executable, os.path.join(MOD, "selftest_hose_port.py")]),
                      ("selftest_proof_hose", [sys.executable, os.path.join(OUT_DIR, "selftest_proof_hose.py")]),
                      ("csharp_selftest", [sys.executable, os.path.join(UTILS, "selftest_flowworks_stock.py")])):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1500)
        steps[name] = {"exit": r.returncode, "tail": r.stdout.strip().splitlines()[-2:]}
        if r.returncode:
            red.append(name)
    if os.path.isdir(GSS_MATRIX):     # the hose matrix catalog for the live (python.exe) side, see SPEC_WIN
        os.makedirs(os.path.dirname(SPEC_POSIX), exist_ok=True)
        r = subprocess.run([sys.executable, os.path.join(GSS_MATRIX, "design_spec.py"), "--out", SPEC_POSIX],
                           capture_output=True, text=True, timeout=1500)
        steps["design_spec"] = {"exit": r.returncode, "tail": r.stdout.strip().splitlines()[-1:]}
        if r.returncode:
            red.append("design_spec")
    return {"red": red, "steps": steps}


def offline_gate_from_windows():
    """The live side (python.exe) runs the offline gate in WSL python3, as GSS proof_all does."""
    import subprocess
    r = subprocess.run(["wsl.exe", "python3", _posix(os.path.abspath(__file__)), "--offline-gate"], capture_output=True, text=True,
                       timeout=3600)
    for ln in reversed((r.stdout or "").splitlines()):
        if ln.startswith("GATE_JSON "):
            return json.loads(ln[len("GATE_JSON "):])
    return {"red": ["gate:no GATE_JSON (exit %s): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-300:])],
            "steps": {}}


def summary(res):
    t = collections.Counter(r["status"] for r in res["rows"])
    print("\nproof_hose %s  rows %d %s  wall %ss" % (res["mode"], len(res["rows"]), dict(t), res.get("wall_s")))
    for r in [r for r in res["rows"] if r["status"] != "PASS"][:25]:
        print("  NOT PASS  %-34s %-10s %s" % (r["id"], r["status"], json.dumps(r["detail"], default=str)[:120]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline-gate", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--only", default=None, help="comma list of blocks (%s): a PARTIAL run" % ",".join(BLOCKS))
    ap.add_argument("--no-fresh-map", action="store_true")
    ap.add_argument("--skip-offline", action="store_true")
    ap.add_argument("--save-name", default=None)
    ap.add_argument("--preport-save", default=None, help="MIDCARRY,MIDRETRACT: two pre-port saves (PP1/PP2)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.offline_gate:
        g = offline_gate()
        print("GATE_JSON " + json.dumps(g, default=str))
        return 1 if g["red"] else 0
    if not a.live:
        ap.print_help()
        return 2
    a.only = [x.strip() for x in a.only.split(",")] if a.only else None
    gate = None
    if not a.skip_offline:
        t = time.time()
        gate = offline_gate_from_windows()
        gate["wall_s"] = round(time.time() - t, 1)
        print("offline gate: %d red %s (%ss)" % (len(gate["red"]), gate["red"], gate["wall_s"]), flush=True)
        if gate["red"]:
            print("REFUSED: offline red -- not going live")
            return 1
    P = Proof(a)
    P.res["offline"] = gate or {"skipped": "--skip-offline"}
    P.out_path = a.out or os.path.join(OUT_DIR, "proof_hose_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    try:
        P.run()
    except BaseException as ex:  # noqa: BLE001
        P.res["run_raised"] = repr(ex)
        raise
    finally:
        try:
            P.B.hp("defaults")
        except Exception:  # noqa: BLE001
            pass
        try:
            P.res["site_calm_restore"] = V.site_calm_restore(P.B)
        except Exception as ex:  # noqa: BLE001
            P.res["site_calm_restore"] = "RAISED %r" % ex
        P.checkpoint(final=True)
    summary(P.res)
    return 1 if any(r["status"] in ("FAIL", "UNMEASURED") for r in P.res["rows"]) or P.res.get("aborted") else 0


if __name__ == "__main__":
    sys.exit(main())
