"""Night FlowWorks short checks, 2026-10-13 (BENCH). One quicktest map, governed ticks only (jawa/safe_advance).

V  POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK A2: fresh RM_LiquidTank 2x2 capacity 80, RM_UniversalCargoTank 160;
   a freshly classified deep pond of N cells capacity 4N, shallow 2N (levels), via jawa/flowworks_body_report.
R  POND_RETURN_LEG_BUILD_WATER_GOES_HOME A1 (short form): a limited shallow pond drained by a pump into a tank, then the
   pump set to Pour toward the pond; the pond's wet set equals the fresh snapshot and the L0 ledger total (the
   "Report water ledger (L0)" dev action, FlowWorksDebugActions.ReportLedger) is unchanged within 1e-3.

  python.exe pond_probe.py <out.json> [--origin X,Z] [--fresh-map] [--max-cycles N]
Run from a git-archive root (needs src/RimMandrake/FlowWorks/northstar on the path).
"""
import argparse
import json
import os
import re
import sys
import time

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH  # noqa: E402

LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
EPS = 1e-3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--origin", default="150,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--max-cycles", type=int, default=16)
    a = ap.parse_args()
    V = PH.V
    B = PH.PB()
    res = {"script": "pond_probe.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": []}

    def save():
        with open(a.out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(a.out + ".tmp", a.out)

    def row(rid, st, det):
        res["rows"].append({"id": rid, "status": st, "detail": det})
        print("%-40s %-10s %s" % (rid, st, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def ledger():
        r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.FlowWorksDebugActions", method="ReportLedger", args="")
        time.sleep(1.0)
        with open(LOG, "r", encoding="utf-8", errors="replace") as f:
            lines = [l for l in f.read().splitlines() if "L0 ledger (tank units)" in l]
        line = lines[-1] if lines else ""
        m = re.search(r"total=([0-9.\-]+)", line)
        return {"call": r.get("success"), "line": line, "total": float(m.group(1)) if m else None, "n": len(lines)}

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    rect = (ox, oz, 24, 24)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    FIELDS = ("refillEnabled", "recessionEnabled", "liquidPumpEnabled", "depthEngineEnabled", "tankCapacityMultiplier",
              "sourceBudgetMultiplier")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        if not ok or not V.prepare_site(B, rect, res["rows"], "SITE_ready"):
            row("SITE", "UNMEASURED", {"why": "site not ready / not playing"})
            return 2
        sset("refillEnabled", False)
        sset("liquidPumpEnabled", True)
        # ---------------- V: tanks
        bb = B.call("jawa/build_batch", ops="RM_LiquidTank:%d,%d;RM_UniversalCargoTank:%d,%d" % (P(18, 2) + P(18, 6)),
                    faction="player", wipeExisting=False)
        res["build_tanks"] = {k: bb.get(k) for k in ("success", "built", "failed")}
        B.ticks(2)
        t1, t2 = B.hp("tank:%d,%d" % P(18, 2)), B.hp("tank:%d,%d" % P(18, 6))
        ok_t = t1.get("capacity") == 80 and t2.get("capacity") == 160
        row("V_tank_capacity_80_160", "PASS" if ok_t else ("FAIL" if t1.get("success") and t2.get("success") else "UNMEASURED"),
            {"RM_LiquidTank": t1, "RM_UniversalCargoTank": t2, "tankCapacityMultiplier": before.get("tankCapacityMultiplier")})
        # ---------------- V: deep pond 3x3 (N=9) and shallow pond 3x2 (N=6)
        B.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,3,3" % P(2, 16))
        deep = B.call("jawa/flowworks_body_report", x=P(3, 17)[0], z=P(3, 17)[1], classify=True) or {}
        db = deep.get("body") or {}
        B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % P(2, 5))
        sh = B.call("jawa/flowworks_body_report", x=P(3, 6)[0], z=P(3, 6)[1], classify=True) or {}
        sb = sh.get("body") or {}
        res["classify"] = {"deep": deep, "shallow": sh}
        okd = db.get("cellCount") == 9 and not db.get("limitless") and abs((db.get("capacity") or -1) - 36) <= EPS
        oks = sb.get("cellCount") == 6 and not sb.get("limitless") and abs((sb.get("capacity") or -1) - 12) <= EPS
        row("V_deep_pond_capacity_4N", "PASS" if okd else ("FAIL" if db else "UNMEASURED"),
            {"N": db.get("cellCount"), "capacity": db.get("capacity"), "expect": 36, "limitless": db.get("limitless"),
             "sourceBudgetMultiplier": before.get("sourceBudgetMultiplier")})
        row("V_shallow_pond_capacity_2N", "PASS" if oks else ("FAIL" if sb else "UNMEASURED"),
            {"N": sb.get("cellCount"), "capacity": sb.get("capacity"), "expect": 12, "limitless": sb.get("limitless")})
        # ---------------- R: shallow pond -> tank -> pond
        pond = [P(x, z) for z in (5, 6) for x in (2, 3, 4)]
        pump, battery, tank = P(3, 7), P(6, 6), P(3, 10)

        def terr():
            o = {}
            for c in pond:
                ci = B.call("rimworld/get_cell_info", x=c[0], z=c[1]) or {}
                o["%d,%d" % c] = (ci.get("cell") or {}).get("terrainDefName")
            return o

        def body():
            r = B.call("jawa/flowworks_body_report", x=pond[4][0], z=pond[4][1], classify=False) or {}
            return r.get("body") or {}

        def units():
            r = B.hp("tank:%d,%d" % tank)
            return r.get("units") if r.get("success") else None

        snap = terr()
        res["wet_snapshot"] = snap
        bb = B.call("jawa/build_batch", ops="RM_LiquidPump:%d,%d;Battery:%d,%d;RM_UniversalPipe:%d,%d;RM_UniversalPipe:%d,%d;"
                    "RM_LiquidTank:%d,%d" % (pump + battery + P(3, 8) + P(3, 9) + tank), faction="player", wipeExisting=False)
        res["build_pump"] = {k: bb.get(k) for k in ("success", "built", "failed")}
        B.ticks(2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        L0 = ledger()
        b0 = body()
        trace = [{"phase": "start", "tick": tg(), "units": units(), "stock": b0.get("stock"), "receded": b0.get("recededCount"),
                  "ledger": L0.get("total")}]
        print("L0 start:", L0["line"], flush=True)
        for i in range(a.max_cycles):
            B.ticks(250)
            bd = body()
            trace.append({"phase": "draw", "tick": tg(), "units": units(), "stock": bd.get("stock"),
                          "receded": bd.get("recededCount"), "pump": B.hp("pump:%d,%d" % pump)})
            if len(trace) > 3 and trace[-1]["units"] == trace[-2]["units"] == trace[-3]["units"]:
                break
        L1 = ledger()
        terr_drawn = terr()
        trace.append({"phase": "drawn", "ledger": L1.get("total"), "terrain": terr_drawn})
        print("L0 drawn:", L1["line"], flush=True)
        drew = (trace[-2].get("units") or 0) - (trace[0].get("units") or 0)
        row("R_draw_moves_water_conserved", "PASS" if drew > 0 and L0["total"] is not None and L1["total"] is not None
            and abs(L1["total"] - L0["total"]) <= EPS else ("UNMEASURED" if drew <= 0 or L1["total"] is None else "FAIL"),
            {"tankGained": drew, "ledger0": L0["total"], "ledger1": L1["total"], "drawnTerrain": terr_drawn})
        pr = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump",
                    args="%d,%d;pour" % pump)
        # pour drains DUMP tanks only; with tank jobs off (a Mod Setting) it drains any tank (Building_LiquidPump.TryPour)
        res["pour_switch"] = pr
        res["tankModesOff"] = B.hp("set:tankModesEnabled=False")
        for i in range(a.max_cycles * 2):
            B.ticks(250)
            bd = body()
            trace.append({"phase": "pour", "tick": tg(), "units": units(), "stock": bd.get("stock"),
                          "receded": bd.get("recededCount"), "pump": B.hp("pump:%d,%d" % pump)})
            if trace[-1]["units"] == 0 or (len(trace) > 3 and trace[-1].get("units") == trace[-2].get("units") == trace[-3].get("units")):
                break
        B.ticks(260)
        L2 = ledger()
        after = terr()
        b2 = body()
        print("L0 after:", L2["line"], flush=True)
        res["trace"] = trace
        same = after == snap
        cons = L0["total"] is not None and L2["total"] is not None and abs(L2["total"] - L0["total"]) <= EPS
        row("R_round_trip_wet_set_and_ledger", "PASS" if same and cons and drew > 0 else "FAIL",
            {"wetSetEqualsSnapshot": same, "snapshot": snap, "after": after, "ledger0": L0["total"], "ledger2": L2["total"],
             "tankEnd": units(), "bodyEnd": {k: b2.get(k) for k in ("stock", "capacity", "recededCount", "cellCount")},
             "ledgerLines": [L0["line"], L1["line"], L2["line"]]})
        return 0
    finally:
        res["hose_defaults_restored"] = B.hp("defaults")
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", a.out)


if __name__ == "__main__":
    sys.exit(main())
