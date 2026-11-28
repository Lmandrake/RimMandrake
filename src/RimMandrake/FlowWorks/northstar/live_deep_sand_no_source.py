#!/usr/bin/env python3
"""Live scene (kind A): deep sand is ground to FlowWorks, never a natural water source.

DEEP_SAND_FIX_READS_AS_FRESHWATER, source half (RIMMANDRAKE_MEND_FLOWWORKS_LIQUID_RULES_FIVE_OLD_DEFECTS). RM_DeepSand keeps
vanilla's Water tag for fishing; before the fix FlowWorks' IsNaturalLiquid read that tag alone, so deep sand was a source cell,
a SUPERDEEP lake square, and a pit dug beside it filled with free fresh water. The fix: the RM_NotLiquidExtension marker on
RM_DeepSand, honoured by IsNaturalLiquid. Offline: SelfTest/DeepSandSourceChecks.cs ("deep sand holds no liquid*").

Contract.
- claim: on a live map, painted RM_DeepSand reads isSourceCell=False and is not SUPERDEEP (depth 4), and a 1 m pit dug beside it
  holds no water after the wait; the same scene on painted WaterShallow (the control, run first) reads isSourceCell=True, depth 4.
- entry point: RM_MapComponent_Excavation.IsSourceCell / DepthAt (read by jawa/flowworks_excavation_report) and the mod's own
  flow pulses during the wait (the scene calls nothing in them).
- valid opportunity: the control reads its water squares as sources (the instrument can see a source); the deep sand paint
  landed (the report's cell answers and the control and sand plots are apart).
- success: every deep sand square isSourceCell=False with depth != 4, and the pit beside the sand reads waterDl 0 after WAIT.
  The pit beside the control water is read too: when it holds water, the dry sand pit row is decided; when it does not,
  that row is UNMEASURED (the pit-fill route did not run), and the source row still decides.
- forbidden effects: an exception from the report; water in the sand pit.
- end: rows written to the out file; both plots reset (ProofResetRect) in finally.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_deep_sand_no_source.py <out.json> [--fresh-map] [--origin X,Z]
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (could not look; the reason is in the row).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

SUPERDEEP = 4     # RM_ExcavationDepth.Superdeep: natural liquid reads through as this
WAIT = 2500       # ticks: ten flow pulses at the shipped 250-tick pulse


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="110,110")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402  (bridge-side import on a live run only)
    B = PH.PB()
    rows = []
    res = {"script": "live_deep_sand_no_source.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}

    def save():
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-40s %-10s %s" % (rid, st, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def call(tool, **kw):
        return B.call(tool, **kw) or {}

    def report(c):
        r = call("jawa/flowworks_excavation_report", x=c[0], z=c[1])
        return {"cell": c, "ok": bool(r.get("success")), "src": r.get("isSourceCell"), "depth": r.get("depth"),
                "waterDl": r.get("waterDl"), "dug": r.get("isExcavated")}

    if a.fresh_map:
        call("rimworld/go_to_main_menu")
        call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    import validation_core as V    # noqa: E402
    if not V._wait_playing(B, leave_s=0)[0]:
        row("DS_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    ox, oz = (int(v) for v in a.origin.split(","))
    plots = {"water": (ox, oz, "WaterShallow"), "sand": (ox + 12, oz, "RM_DeepSand")}
    try:
        for x0, z0, _t in plots.values():
            call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                 args="%d;%d;%d;%d" % (x0 - 2, z0 - 2, 8, 8))
        reads = {}
        for k, (x0, z0, terr) in plots.items():
            p = call("jawa/set_terrain_batch", ops="%s:%d,%d,3,3" % (terr, x0, z0))
            pit = (x0 + 3, z0 + 1)   # east of the 3x3 pool's middle row, touching it
            d = call("jawa/flowworks_excavation_drive", x=pit[0], z=pit[1], deepenLevels=2, setBodyWaterM=-1)
            reads[k] = {"paint": {kk: p.get(kk) for kk in ("success", "opsApplied", "cellsChanged", "error")},
                        "pool": [report((x0 + dx, z0 + dz)) for dx in range(3) for dz in range(3)],
                        "pit": pit, "dig": {kk: d.get(kk) for kk in ("success", "depth", "error")}}
        w, s = reads["water"], reads["sand"]
        if not all(r["ok"] for r in w["pool"] + s["pool"]):
            row("DS_site", "UNMEASURED", {"why": "the excavation report did not answer on every square", "reads": reads})
            return 2
        ctrl_src = all(r["src"] for r in w["pool"]) and all(r["depth"] == SUPERDEEP for r in w["pool"])
        row("DS_control_water_is_a_source", "PASS" if ctrl_src else "UNMEASURED",
            {"water": w["pool"][:3], "paint": w["paint"],
             "why": "painted WaterShallow reads as a natural source, SUPERDEEP" if ctrl_src
             else "the control water did not read as a source: the instrument cannot see one here"})
        if not ctrl_src:
            return 2
        sand_src = [r for r in s["pool"] if r["src"] or r["depth"] == SUPERDEEP]
        row("DS_deep_sand_is_no_source", "FAIL" if sand_src else "PASS",
            {"wrong": sand_src, "sample": s["pool"][:3], "paint": s["paint"],
             "why": "deep sand reads as natural liquid" if sand_src else "every deep sand square: isSourceCell False, not SUPERDEEP"})
        call("rimworld/step_game_ticks", ticks=WAIT, pauseFirst=True, timeoutMs=180000)
        wp, sp = report(w["pit"]), report(s["pit"])
        if not (wp["dug"] and sp["dug"]):
            row("DS_pit_beside_sand_stays_dry", "UNMEASURED", {"why": "a pit did not dig", "waterPit": wp, "sandPit": sp,
                                                                "digs": [w["dig"], s["dig"]]})
        elif not (wp["waterDl"] or 0) > 0:
            row("DS_pit_beside_sand_stays_dry", "UNMEASURED" if not (sp["waterDl"] or 0) else "FAIL",
                {"why": "the control pit beside water took no water in %d ticks: the pit-fill route did not run" % WAIT
                 if not (sp["waterDl"] or 0) else "the sand pit holds water", "waterPit": wp, "sandPit": sp})
        else:
            dry = (sp["waterDl"] or 0) == 0
            row("DS_pit_beside_sand_stays_dry", "PASS" if dry else "FAIL",
                {"waterPit": wp, "sandPit": sp, "why": "the pit beside water filled, the pit beside deep sand stayed dry" if dry
                 else "the pit beside deep sand took water"})
        bad = [r for r in rows if r["status"] == "FAIL"]
        if bad:
            return 1
        return 0 if not sand_src else 1
    finally:
        for x0, z0, _t in plots.values():
            call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                 args="%d;%d;%d;%d" % (x0 - 2, z0 - 2, 8, 8))
        save()


if __name__ == "__main__":
    sys.exit(main())
