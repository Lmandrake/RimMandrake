#!/usr/bin/env python3
"""Live scene (kind A): a suspension bridge spans a pit that holds the wreck of a fallen bridge, and marks the wreck for clearing.

RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP (owner walk 2026-11-20: "Would not place over a pit that had the
scrap of a ruined bridge in it, even though it likely still should."). Offline: SelfTest/SuspensionBridgeChecks.cs
(Suspension_span_over_a_wreck_marks_it_for_clearing, RM_SuspensionMath.EdificeBlocksSpan).

Contract.
- claim: a steel suspension bridge dragged landing to landing over a 1 m trench whose middle square holds RM_SuspensionWreck is
  placed, and the wreck then carries a Deconstruct designation; the same drag over a trench holding another building (sandbags)
  is still refused.
- entry point: Designator_SuspensionBridge.TryDesignate, the path DesignateMultiCell takes (RM_SuspensionProofs.ProofBuild).
- valid opportunity: the trench digs and the wreck (or the sandbags) stands on its middle square before the drag.
- success: the wreck drag reads ok=True and a Deconstruct designation lies on the wreck's square; the sandbag drag reads ok=False.
- forbidden effects: the wreck destroyed outside god mode; a bridge placed over the sandbags.
- end: rows written; the site reset in finally.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_bridge_over_wreck.py <out.json> [--fresh-map] [--origin X,Z]
Exit 0 PASS, 1 FAIL, 2 UNMEASURED.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

PROOFS = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="40,70")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402
    B = PH.PB()
    rows = []
    res = {"script": "live_bridge_over_wreck.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}

    def save():
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def call(tool, **kw):
        try:
            return B.call(tool, **kw) or {}
        except Exception as ex:  # noqa: BLE001
            return {"success": False, "error": str(ex)}

    def build(x1, x2, z):
        r = call("jawa/static_call", type=PROOFS, method="ProofBuild", args="%d,%d;%d,%d;steel" % (x1, z, x2, z))
        return str(r.get("result") or r.get("error") or r.get("message") or r)

    if a.fresh_map:
        call("rimworld/go_to_main_menu")
        call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    import validation_core as V    # noqa: E402
    if not V._wait_playing(B, leave_s=0)[0]:
        row("WR_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    ox, oz = (int(v) for v in a.origin.split(","))
    rect = (ox - 2, oz - 2, 12, 9)
    reset = lambda: call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                         args="%d;%d;%d;%d" % rect)

    def at(x, z, dn):
        return [t for t in (call("jawa/list_things", defName=dn, rect="%d,%d,1,1" % (x, z), limit=5).get("things") or [])
                if t.get("def") == dn]

    def marked(x, z):
        r = call("jawa/designate_batch", action="query", limit=1000)
        return [d for d in r.get("designations") or [] if d.get("x") == x and d.get("z") == z
                and "deconstruct" in json.dumps(d).lower()]

    try:
        reset()
        res["open_sky"] = V.open_sky_site(B, rect).get("ok")
        call("jawa/destroy_batch", rects="%d,%d,%d,%d" % rect, categories="All")
        call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % rect)
        call("rimworld/pause_game")
        # two trenches, ox+1..ox+5, 1 m deep: the wreck's at oz, the sandbags' at oz+4; landings at ox and ox+6
        for z in (oz, oz + 4):
            digs = [call("jawa/flowworks_excavation_drive", x=ox + i, z=z, deepenLevels=2, setBodyWaterM=-1, fillInLevels=0).get("success")
                    for i in range(1, 6)]
            if not all(digs):
                row("WR_site", "UNMEASURED", {"why": "a trench did not dig", "z": z, "digs": digs})
                return 2
        call("jawa/spawn_batch", ops="RM_SuspensionWreck:%d,%d" % (ox + 3, oz))
        call("jawa/spawn_batch", ops="Sandbags:%d,%d" % (ox + 3, oz + 4))
        wreck, bags = at(ox + 3, oz, "RM_SuspensionWreck"), at(ox + 3, oz + 4, "Sandbags")
        res["staged"] = {"wreck": len(wreck), "sandbags": len(bags)}
        if not wreck:
            row("WR_site", "UNMEASURED", {"why": "the wreck did not spawn in the trench"})
            return 2
        got = build(ox, ox + 6, oz)
        placed = "ok=True" in got
        row("WR_bridge_spans_the_wreck", "PASS" if placed else "FAIL", {"got": got})
        still, mark = at(ox + 3, oz, "RM_SuspensionWreck"), marked(ox + 3, oz)
        row("WR_wreck_marked_for_clearing", "PASS" if placed and still and mark else ("FAIL" if placed else "UNMEASURED"),
            {"wreck_still_there": len(still), "designations": mark[:2],
             "why": None if placed else "the bridge did not place, so no mark can be read"})
        if bags:
            other = build(ox, ox + 6, oz + 4)
            row("WR_other_building_still_blocks", "PASS" if "ok=False" in other else "FAIL", {"got": other})
        else:
            row("WR_other_building_still_blocks", "UNMEASURED", {"why": "the sandbags did not spawn in the trench"})
        return 1 if any(r["status"] == "FAIL" for r in rows) else (2 if any(r["status"] == "UNMEASURED" for r in rows) else 0)
    finally:
        reset()
        save()


if __name__ == "__main__":
    sys.exit(main())
