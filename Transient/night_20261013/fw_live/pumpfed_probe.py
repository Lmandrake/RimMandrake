"""PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD A2 (night FlowWorks short checks, 2026-10-13, BENCH): a pump on Pour against a
brimming dug outlet, saved, reloaded, then the channel dug on by 4 dry cells OUTSIDE the pump's reach: the extension
must take fill (the pump re-marks its backed-up outlet as a flow input; the unsaved input set starts empty on load).
Governed ticks only; the save is a throwaway test save.

  python.exe pumpfed_probe.py <out.json> [--origin X,Z] [--fresh-map] [--save NAME]
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
    ap.add_argument("--save", default="NS_night_pumpfed_20261013")
    a = ap.parse_args()
    V = PH.V
    B = PH.PB()
    res = {"script": "pumpfed_probe.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": [], "args": vars(a)}

    def save():
        with open(a.out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(a.out + ".tmp", a.out)

    def row(rid, st, det):
        res["rows"].append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:700]), flush=True)
        save()

    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def fills(cells):
        return [(B.call("jawa/flowworks_excavation_report", x=c[0], z=c[1]) or {}).get("fill") for c in cells]

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    rect = (ox, oz, 16, 14)
    chan = [P(2 + i, 6) for i in range(4)]          # pump at (3,7) reaches x 2..4 on row 6
    ext = [P(6 + i, 6) for i in range(4)]           # outside the pump's reach
    pump, battery, tank = P(3, 7), P(1, 9), P(3, 10)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    FIELDS = ("liquidPumpEnabled", "pumpFedSpreadEnabled", "depthEngineEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        if not ok or not V.prepare_site(B, rect, res["rows"], "SITE_ready"):
            row("SITE", "UNMEASURED", {"why": "site not ready / not playing"})
            return 2
        for c in chan:
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=2, setFill=-1)
        bb = B.call("jawa/build_batch", ops="RM_LiquidPump:%d,%d;Battery:%d,%d;RM_UniversalPipe:%d,%d;RM_UniversalPipe:%d,%d;"
                    "RM_LiquidTank:%d,%d" % (pump + battery + P(3, 8) + P(3, 9) + tank), faction="player", wipeExisting=False)
        res["build"] = {k: bb.get(k) for k in ("success", "built", "failed")}
        B.ticks(2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        res["filltank"] = B.hp("filltank:%d,%d=%s,80" % (tank + (PH.LIQUID_WATER,)))
        res["tankModesOff"] = B.hp("set:tankModesEnabled=False")    # pour drains any tank, no Dump job needed
        res["pour"] = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump",
                             args="%d,%d;pour" % pump).get("result")
        tr = []
        for _ in range(16):
            B.ticks(250)
            tr.append({"tick": tg(), "chan": fills(chan), "pump": B.hp("pump:%d,%d" % pump).get("lastMovedTick")})
            if all(f == 2 for f in tr[-1]["chan"]) and len(tr) > 2 and tr[-1]["chan"] == tr[-2]["chan"]:
                break
        res["fill_trace"] = tr
        brim = all(f == 2 for f in tr[-1]["chan"])
        row("PRE_outlet_brimming_before_save", "PASS" if brim else "UNMEASURED", {"chan": tr[-1]["chan"], "ticks": len(tr) * 250})
        if not brim:
            return 2
        sv = B.call("rimworld/save_game", saveName=a.save)
        res["save"] = {k: sv.get(k) for k in ("success", "message")}
        lr = B.call("rimworld/load_game_ready", saveName=a.save)
        res["load"] = {k: lr.get("success") for k in ("success",)}
        ok2, _ = V._wait_playing(B, leave_s=0)
        time.sleep(2)
        B.hp("set:tankModesEnabled=False")
        res["after_load"] = {"chan": fills(chan), "ext": fills(ext), "tank": B.hp("tank:%d,%d" % tank),
                             "pump": B.hp("pump:%d,%d" % pump)}
        for c in ext:
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=2, setFill=-1)
        tr2 = []
        for _ in range(12):
            B.ticks(250)
            tr2.append({"tick": tg(), "chan": fills(chan), "ext": fills(ext), "pump": B.hp("pump:%d,%d" % pump)})
            if (tr2[-1]["ext"][-1] or 0) > 0:
                break
        res["ext_trace"] = tr2
        far = tr2[-1]["ext"]
        row("PUMPFED_extension_fills_after_reload", "PASS" if (far[-1] or 0) > 0 else "FAIL",
            {"ext": far, "chan": tr2[-1]["chan"], "ticksAfterDig": len(tr2) * 250, "reloaded": ok2,
             "tankAfter": B.hp("tank:%d,%d" % tank).get("units")})
        return 0
    finally:
        res["hose_defaults_restored"] = B.hp("defaults")
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", a.out)


if __name__ == "__main__":
    sys.exit(main())
