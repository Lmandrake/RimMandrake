"""Night FlowWorks short checks, 2026-10-13 (BENCH): a flood release into a dug D4 channel, governed ticks only.

DEBIT  FLOOD_DEBIT_MEND_DEEP_CELL_ONE_LEVEL A2: the release spends 4 x volumePerTile per D4 cell it fills
       (spent = sum of channel levels added + one per flooded non-channel cell, all x volumePerTile = 1 for water).
DRIVER FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 A1: the channel holds engine fill (FillAt>0) with no flood temp terrain,
       still so after the release's expiry tick.
SWITCH FLOOD_SWITCH_RACE_MEND_ENGINE_OFF A2: legacyFloodViaEngineEnabled off, a release next to a dug channel leaves the
       channel's terrain and fill unchanged (read past the release's expiry).

  python.exe flood_probe.py <out.json> [--origin X,Z] [--fresh-map] [--volume V]
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
FLUID, TRACE = "RM_Fluid_Water", "RM_Fill_Water_Trace"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--origin", default="150,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--volume", type=float, default=12.0)
    a = ap.parse_args()
    V = PH.V
    B = PH.PB()
    res = {"script": "flood_probe.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": [], "args": vars(a)}

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

    def cell(c):
        r = B.call("jawa/canal_cell_report", x=c[0], z=c[1]) or {}
        e = B.call("jawa/flowworks_excavation_report", x=c[0], z=c[1]) or {}
        fl = [t.get("flood") for t in (r.get("things") or []) if t.get("flood")]
        return {"terrain": r.get("terrain"), "temp": r.get("tempTerrain"), "under": r.get("underneath"),
                "D": e.get("depth", e.get("D")), "F": e.get("fill", e.get("F")), "flood": fl[0] if fl else None}

    def area(x0, z0, w, h):
        r = B.call("jawa/flowworks_excavation_rect", x=x0, z=z0, w=w, h=h, onlyNonZero=False, includeTerrain=True) or {}
        return r

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    rect = (ox, oz, 30, 22)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    FIELDS = ("legacyFloodViaEngineEnabled", "depthEngineEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    chA = [P(4 + i, 6) for i in range(6)]
    chB = [P(4 + i, 15) for i in range(6)]
    try:
        if not ok or not V.prepare_site(B, rect, res["rows"], "SITE_ready"):
            row("SITE", "UNMEASURED", {"why": "site not ready / not playing"})
            return 2
        for c in chA + chB:
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setFill=-1)
        B.ticks(2)
        res["chA_dug"] = [cell(c) for c in chA]
        res["chB_dug"] = [cell(c) for c in chB]
        res["probe_shape"] = B.call("jawa/flowworks_excavation_report", x=chA[0][0], z=chA[0][1])
        # ---------------- A: engine path on
        sset("legacyFloodViaEngineEnabled", True)
        sp = B.call("jawa/flowworks_spawn_flood", x=chA[0][0], z=chA[0][1], fluidDefName=FLUID, volume=a.volume) or {}
        res["spawnA"] = sp
        f0 = cell(chA[0])
        res["floodA_at_spawn"] = f0
        exp = (f0.get("flood") or {}).get("expiresAtTick")
        trace, last_flood = [], f0.get("flood")
        for k in range(36):
            B.ticks(15 if k < 20 else 250)
            c0 = cell(chA[0])
            if c0.get("flood"):
                last_flood = c0["flood"]
            elif last_flood is not None and k < 20:
                last_flood = dict(last_flood, gone=True)
            trace.append({"tick": tg(), "flood": c0.get("flood"), "F0": c0.get("F")})
            if exp is not None and trace[-1]["tick"] is not None and trace[-1]["tick"] > exp + 20 and not c0.get("flood"):
                break
        res["traceA"] = trace
        chan = [cell(c) for c in chA]
        ar = area(*rect)
        res["areaA"] = ar
        rows_ = ar.get("cells") or ar.get("rows") or []
        chA_set = {"%d,%d" % c for c in chA}
        soil = []
        for r_ in rows_:
            k = "%s,%s" % (r_.get("x"), r_.get("z"))
            if k in chA_set:
                continue
            if r_.get("terrain") == TRACE and 0 <= (r_.get("z") - oz) < 11:
                soil.append(k)
        levels = sum((c.get("F") or 0) for c in chan)
        # a release that spent its whole volume destroys itself: last seen with volume, then gone -> 0 left
        remaining = 0.0 if (last_flood or {}).get("gone") else (last_flood or {}).get("remainingVolume")
        det_trace = [(t["tick"], (t["flood"] or {}).get("remainingVolume"), (t["flood"] or {}).get("floodedTileCount"))
                     for t in trace[:20]]
        spent = a.volume - remaining if remaining is not None else None
        full = [c for c in chan if c.get("F") == 4]
        det = {"volume": a.volume, "remainingLastSeen": remaining, "spent": spent, "channelLevels": levels,
               "soilTraceCells": len(soil), "channel": [{k: c.get(k) for k in ("D", "F", "temp")} for c in chan],
               "fullD4Cells": len(full), "remainingByTick": det_trace}
        if spent is None or not chan or chan[0].get("F") is None:
            row("DEBIT_four_levels_per_D4_cell", "UNMEASURED", det)
        else:
            # the engine redistributes fill after placement, so the cell pattern is not the debit; conservation is:
            # every level in the channel + every flooded soil cell was paid for, nothing more (old bug: 1 per D4 cell)
            okd = abs(spent - (levels + len(soil))) < 1e-3
            row("DEBIT_four_levels_per_D4_cell", "PASS" if okd else "FAIL", det)
        filled = [c for c in chan if (c.get("F") or 0) > 0]
        # the engine draws its own fill as RM_Fill_<fluid>_<depth> temp terrain; the FLOOD's overlay is the Trace terrain
        okr = filled and all(c.get("temp") != TRACE for c in filled)
        row("DRIVER_engine_fill_no_temp_terrain_after_expiry", "PASS" if okr else ("FAIL" if filled else "UNMEASURED"),
            {"filled": len(filled), "expiresAtTick": exp, "readTick": tg(),
             "temps": [c.get("temp") for c in chan], "fills": [c.get("F") for c in chan]})
        # ---------------- B: switch off
        sset("legacyFloodViaEngineEnabled", False)
        b0 = [cell(c) for c in chB]
        seed = chB[0]   # a release ON the dug channel: every channel cell is HandsOff when the switch is off
        sp = B.call("jawa/flowworks_spawn_flood", x=seed[0], z=seed[1], fluidDefName=FLUID, volume=a.volume) or {}
        res["spawnB"] = sp
        fb = cell(seed)
        expb = (fb.get("flood") or {}).get("expiresAtTick")
        traceB = []
        for _ in range(16):
            B.ticks(250)
            cs = cell(seed)
            traceB.append({"tick": tg(), "flood": cs.get("flood"), "chB0": cell(chB[0])})
            if expb is not None and traceB[-1]["tick"] > expb + 20 and not cs.get("flood"):
                break
        res["traceB"] = traceB
        b1 = [cell(c) for c in chB]
        strip = lambda L: [{k: c.get(k) for k in ("terrain", "temp", "D", "F")} for c in L]   # noqa: E731
        spread = bool(sp.get("success")) and expb is not None and traceB and traceB[-1]["tick"] > expb
        oks = strip(b0) == strip(b1)
        row("SWITCH_off_channel_unchanged_past_expiry", ("PASS" if oks else "FAIL") if spread else "UNMEASURED",
            {"before": strip(b0), "after": strip(b1), "releaseSpreadNearChannel": spread, "expiresAtTick": expb,
             "readTick": tg()})
        return 0
    finally:
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", a.out)


if __name__ == "__main__":
    sys.exit(main())
