"""POND_RETURN_LEG_BUILD_WATER_GOES_HOME A3 (night FlowWorks short checks, 2026-10-13, BENCH): dig a dry bed square of a
limited pond, fill it back in: it is Mud (not water), the pond capacity returns to its value, and the square re-wets on
refill. The bed is dried by a pump draw (the pond_probe scene); refill at the slider max, bounded to 3000 governed ticks.

  python.exe dugbed_probe.py <out.json> [--origin X,Z] [--fresh-map]
"""
import argparse
import json
import os
import sys
import time

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH  # noqa: E402

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--origin", default="150,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--refill-rate", type=float, default=5.0,
                    help="refillRateMultiplier for the re-wet leg; above the slider max (5) is a COMPRESSED clock "
                         "(owner 2026-10-13: shorten the timing constant, observe, restore); restored in finally")
    a = ap.parse_args()
    V = PH.V
    B = PH.PB()
    res = {"script": "dugbed_probe.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": []}

    def save():
        with open(a.out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(a.out + ".tmp", a.out)

    def row(rid, st, det):
        res["rows"].append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:700]), flush=True)
        save()

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def terr(c):
        return ((B.call("rimworld/get_cell_info", x=c[0], z=c[1]) or {}).get("cell") or {}).get("terrainDefName")

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    pond = [P(x, z) for z in (5, 6) for x in (2, 3, 4)]
    pump, battery, tank = P(3, 7), P(6, 6), P(3, 10)

    def body():
        r = B.call("jawa/flowworks_body_report", x=P(3, 6)[0], z=P(3, 6)[1], classify=False) or {}
        return r.get("body") or {}

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    FIELDS = ("refillEnabled", "refillRateMultiplier", "liquidPumpEnabled", "dugBedLeavesPondEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        if not ok or not V.prepare_site(B, (ox, oz, 16, 14), res["rows"], "SITE_ready"):
            row("SITE", "UNMEASURED", {"why": "site not ready"})
            return 2
        sset("refillEnabled", False)
        sset("liquidPumpEnabled", True)
        B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % P(2, 5))
        cls = B.call("jawa/flowworks_body_report", x=P(3, 6)[0], z=P(3, 6)[1], classify=True) or {}
        cap0 = (cls.get("body") or {}).get("capacity")
        B.call("jawa/build_batch", ops="RM_LiquidPump:%d,%d;Battery:%d,%d;RM_UniversalPipe:%d,%d;RM_UniversalPipe:%d,%d;"
               "RM_LiquidTank:%d,%d" % (pump + battery + P(3, 8) + P(3, 9) + tank), faction="player", wipeExisting=False)
        B.ticks(2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        for _ in range(12):
            B.ticks(250)
        sset("liquidPumpEnabled", False)
        B.ticks(260)
        dry = [c for c in pond if terr(c) != "WaterShallow"]
        res["dry_bed"] = dry
        if not dry:
            row("A3_dug_bed", "UNMEASURED", {"why": "no dry bed square after the draw"})
            return 2
        sq = P(2, 5) if P(2, 5) in dry else dry[0]
        b1 = body()
        dig = B.call("jawa/flowworks_excavation_drive", x=sq[0], z=sq[1], deepenLevels=1, setFill=-1)
        B.ticks(2)
        b2 = body()
        fill = B.call("jawa/flowworks_excavation_drive", x=sq[0], z=sq[1], deepenLevels=0, setFill=-1, fillInLevels=1)
        B.ticks(2)
        b3 = body()
        t3 = terr(sq)
        ex3 = B.call("jawa/flowworks_excavation_report", x=sq[0], z=sq[1]) or {}
        det = {"square": sq, "capFresh": cap0, "capDry": b1.get("capacity"), "capDug": b2.get("capacity"),
               "cellsDug": b2.get("cellCount"), "capFilledIn": b3.get("capacity"), "cellsFilledIn": b3.get("cellCount"),
               "terrainFilledIn": t3, "depthAfterFillIn": ex3.get("depth"), "dig": dig.get("success"), "fillIn": fill.get("success")}
        okA = b2.get("capacity") is not None and b2["capacity"] < b1["capacity"] and \
            abs((b3.get("capacity") or -1) - b1["capacity"]) < 1e-3 and t3 == "Mud" and not (ex3.get("depth") or 0)
        row("A3_dig_and_fill_in_capacity_returns_mud", "PASS" if okA else "FAIL", det)
        sset("refillRateMultiplier", a.refill_rate)
        sset("refillEnabled", True)
        tr = []
        for _ in range(12):
            B.ticks(250)
            bd = body()
            tr.append({"stock": bd.get("stock"), "receded": bd.get("recededCount"), "sq": terr(sq)})
            if tr[-1]["sq"] == "WaterShallow":
                break
        row("A3_square_rewets_on_refill", "PASS" if tr and tr[-1]["sq"] == "WaterShallow" else "UNMEASURED",
            {"trace": tr, "ticks": len(tr) * 250, "refillRateMultiplier": a.refill_rate, "why": None if tr and tr[-1]["sq"] == "WaterShallow"
             else "refill did not reach the square within 3000 ticks (bounded wait)"})
        return 0
    finally:
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", a.out)


if __name__ == "__main__":
    sys.exit(main())
