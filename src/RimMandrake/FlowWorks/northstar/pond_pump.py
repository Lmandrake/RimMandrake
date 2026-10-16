"""POND_PUMP live row (owner asked 2026-10-11): a basic pump on Draw lifts water out of a LIMITED natural pond into a tank,
and the pond's stock falls by exactly what the tank gained; then refill brings the stock back and re-wets receded cells.

  python.exe src/RimMandrake/FlowWorks/northstar/pond_pump.py [out.json] [--origin X,Z] [--fresh-map] [--cycles N]
                                                              [--refill-days D]

Run from the repo (or a git-archive export) root with python.exe; the bridge must be held. Exit 0 = both rows PASS.

Scene (plot coords from --origin, default 180,40; the plot is 14 x 14 and is cleared + read back by validation_core.prepare_site):
  a 3x2 natural WaterShallow pond at (2..4, 5..6) -- 6 cells, far below minLimitlessBodyCells, so LIMITED (the regression
  probe fw_pond_outflow_regression.py measured cap 30); the basic RM_LiquidPump at (3,7) on its north bank (reach = the 8
  touching cells, so it draws pond cells (2..4,6)); a Battery at (6,6); two RM_UniversalPipe at (3,8),(3,9); an RM_LiquidTank
  (2x2) at (3,10) on that pipe net. Same layout as fw_live_checks L2b, with a natural pond where L2b had a dug channel.

Phase A (draw), refill OFF: read the tank units u0 and the body stock s0 at one tick, run --cycles pump cycles (250 ticks
each), read u1 / s1 at one tick.  Unit bridge: one world level = RM_PumpMath.TankUnitsPerLevel = 10,000 tank units (decilitres; was 5
drums before LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS), and a level
debits volumePerTile = 1 stock unit. So the bar is
    (s0 - s1) * 10000 == (u1 - u0)  exactly (|diff| <= 1e-3),  u1 > u0,
and the raw floats are recorded so a reader who expects stock and tank units to be the SAME unit sees the 1:10000 directly.
Phase B (refill), pump switched off (liquidPumpEnabled false), refillEnabled on, refillRateMultiplier 5 (the slider max),
weather locked Clear: tick up to --refill-days in-game days; the bar is stock rises AND recededCount falls below its
post-draw value (a receded cell re-wets). Settings are restored to their values before the run.

Rows: POND_PUMP_draw_conserves, POND_PUMP_refill_rewets (+ site/precondition rows). "Could not ask" is UNMEASURED.

ANTI-GUESSING NOTES
- body_report(classify=True) FORMS the body and makes it sticky; it is called once on the fresh pond, before any pump runs.
- Refill and recession only happen on depth-engine pulses (RM_LiquidStock pulse); the engine must be enabled. The row
  records flowworks_engine_state before and after.
- Recession order is outside-in; a 3x2 pond keeps the pump-side middle cell (3,6) longest, so the pump keeps a source.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

UNITS_PER_LEVEL = 10000      # RM_PumpMath.TankUnitsPerLevel = LitresPerLevel x UnitsPerLitre (was 5)
STOCK_PER_LEVEL = 1.0        # FluidDef.volumePerTile of fresh water (FlowWorks_Fluids.xml)
EPS = 1e-3


# ============================================================================ verdicts (pure; selftest_pond_pump.py)
def draw_verdict(u0, u1, s0, s1):
    """(status, detail) for phase A. None anywhere = could not ask."""
    if None in (u0, u1, s0, s1):
        return "UNMEASURED", {"why": "a read returned nothing", "u0": u0, "u1": u1, "s0": s0, "s1": s1}
    gained = u1 - u0
    fell = s0 - s1
    expect = fell * UNITS_PER_LEVEL / STOCK_PER_LEVEL
    d = {"tankGained": gained, "stockFell": fell, "stockFellInTankUnits": expect, "diff": gained - expect,
         "rawEqual": abs(gained - fell) <= EPS}
    if gained <= 0:
        return "FAIL", dict(d, why="the tank gained nothing")
    return ("PASS" if abs(gained - expect) <= EPS else "FAIL"), d


def refill_verdict(trace, s_after_draw, receded_after_draw):
    """trace: [{stock, receded}] during phase B. PASS = stock rose and some receded cell re-wet."""
    pts = [t for t in trace if t.get("stock") is not None and t.get("receded") is not None]
    if not pts or s_after_draw is None or receded_after_draw is None:
        return "UNMEASURED", {"why": "no body reads in the refill window"}
    if receded_after_draw == 0:
        return "UNMEASURED", {"why": "the draw receded no cell, so re-wetting cannot be observed",
                              "stockAfterDraw": s_after_draw}
    s_max = max(t["stock"] for t in pts)
    r_min = min(t["receded"] for t in pts)
    d = {"stockAfterDraw": s_after_draw, "stockMax": s_max, "recededAfterDraw": receded_after_draw, "recededMin": r_min}
    return ("PASS" if (s_max > s_after_draw + EPS and r_min < receded_after_draw) else "FAIL"), d


# ============================================================================ live
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="180,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--cycles", type=int, default=8)
    ap.add_argument("--refill-days", type=float, default=2.0)
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
    B = PH.PB()
    out = a.out or os.path.join(HERE, "pond_pump_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "pond_pump.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-34s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    raw_ticks = B.ticks

    def ticks(n):
        t0 = tg()
        left = n
        while left > 0:
            k = min(1500, left)
            raw_ticks(k)
            left -= k
        t1 = tg()
        if t0 is not None and t1 is not None and t1 - t0 < n:
            raw_ticks(n - (t1 - t0))
    B.ticks = ticks

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    pond = [P(x, z) for z in (5, 6) for x in (2, 3, 4)]
    pump, battery, tank = P(3, 7), P(6, 6), P(3, 10)
    rect = (ox, oz, 14, 14)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
    res["running"] = len(rm.get("packageIds") or [])
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    FIELDS = ("refillEnabled", "refillRateMultiplier", "recessionEnabled", "liquidPumpEnabled", "depthEngineEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before

    def body():
        r = B.call("jawa/flowworks_body_report", x=pond[4][0], z=pond[4][1], classify=False) or {}
        return r.get("body") or {}

    def units():
        r = B.hp("tank:%d,%d" % tank)
        return r.get("units") if r.get("success") else None

    def terrain():
        out_t = {}
        for c in pond:
            ci = B.call("rimworld/get_cell_info", x=c[0], z=c[1]) or {}
            # rimworld/get_cell_info answers {"cell": {"terrainDefName": ...}}; the old top-level read was always None
            out_t["%d,%d" % c] = (ci.get("cell") or {}).get("terrainDefName")
        return out_t

    try:
        if not ok or not V.prepare_site(B, rect, rows, "POND_PUMP_site_ready"):
            row("POND_PUMP_draw_conserves", "UNMEASURED", "SITE", {"why": "site not ready / not playing"})
            return 2
        B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % P(2, 5))
        cls = B.call("jawa/flowworks_body_report", x=pond[4][0], z=pond[4][1], classify=True) or {}
        b0 = cls.get("body") or {}
        res["classify"] = cls
        res["engine_before"] = B.call("jawa/flowworks_engine_state")
        res["terrain_fresh"] = terrain()
        if not b0 or b0.get("limitless") or b0.get("cellCount") != 6:
            row("POND_PUMP_pond_limited", "UNMEASURED", "SITE", {"body": b0})
            return 2
        row("POND_PUMP_pond_limited", "PASS", "SITE", {"body": b0})
        sset("refillEnabled", False)
        sset("liquidPumpEnabled", True)
        bb = B.call("jawa/build_batch", ops="RM_LiquidPump:%d,%d;Battery:%d,%d;RM_UniversalPipe:%d,%d;RM_UniversalPipe:%d,%d;"
                    "RM_LiquidTank:%d,%d" % (pump + battery + P(3, 8) + P(3, 9) + tank), faction="player", wipeExisting=False)
        res["build"] = {k: bb.get(k) for k in ("success", "built", "failed")}
        B.ticks(2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        pw = PH._powered(B, pump)
        res["pumpPoweredAfterTicks"] = pw
        u0, s0b = units(), body()
        s0 = s0b.get("stock")
        trace = [{"tick": tg(), "units": u0, "stock": s0, "receded": s0b.get("recededCount")}]
        for _ in range(a.cycles):
            B.ticks(250)
            bd = body()
            trace.append({"tick": tg(), "units": units(), "stock": bd.get("stock"), "receded": bd.get("recededCount"),
                          "pump": B.hp("pump:%d,%d" % pump).get("status")})
        u1, s1 = trace[-1]["units"], trace[-1]["stock"]
        st, det = draw_verdict(u0, u1, s0, s1)
        if pw is None and st != "PASS":
            st, det = "UNMEASURED", dict(det, why="the pump never read powered")
        row("POND_PUMP_draw_conserves", st, "MOD", dict(det, u0=u0, u1=u1, s0=s0, s1=s1, trace=trace,
                                                         capacity=b0.get("capacity"), pumpPoweredAfterTicks=pw))
        res["terrain_after_draw"] = terrain()
        # ---- phase B
        sset("liquidPumpEnabled", False)
        B.ticks(260)
        bd = body()
        s_ad, r_ad = bd.get("stock"), bd.get("recededCount")
        sset("refillRateMultiplier", 5.0)
        sset("refillEnabled", True)
        tb = []
        left = int(a.refill_days * 60000)
        while left > 0:
            B.ticks(min(5000, left))
            left -= 5000
            bd = body()
            tb.append({"tick": tg(), "stock": bd.get("stock"), "receded": bd.get("recededCount")})
            if r_ad and bd.get("recededCount") is not None and bd["recededCount"] < r_ad:
                break
        st, det = refill_verdict(tb, s_ad, r_ad)
        row("POND_PUMP_refill_rewets", st, "MOD", dict(det, trace=tb, tankAfter=units(), terrainAfter=terrain(),
                                                        engine=B.call("jawa/flowworks_engine_state")))
        return 0 if all(r["status"] == "PASS" for r in rows if r["id"] in ("POND_PUMP_draw_conserves",
                                                                         "POND_PUMP_refill_rewets")) else 1
    finally:
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", out)


if __name__ == "__main__":
    sys.exit(main())
