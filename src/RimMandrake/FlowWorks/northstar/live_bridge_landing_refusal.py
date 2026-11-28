#!/usr/bin/env python3
"""Live scene (kind A): a suspension bridge drag begun on the span says to start on the landing.

RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING (owner walk 2026-11-20: "Selector tool worked to place it, but it
should tell you that you start on the landing, not the span, in order to work."). Offline: SelfTest/SuspensionBridgeChecks.cs
(Suspension_drag_validator_ends_middle_length_width, RM_SuspensionMath.LandingRefusal).

Contract.
- claim: a steel suspension bridge drag that begins on a square of the dug hole (dragged east to the far landing, or west to
  the near one) is refused with words that name the landing and the span; a drag from landing to landing is placed.
- entry point: Designator_SuspensionBridge.TryDesignate, the path DesignateMultiCell takes (RM_SuspensionProofs.ProofBuild).
- valid opportunity: the trench digs, and the control drag (landing to landing) is placed (the instrument can place a bridge).
- success: both span drags read a refusal holding "landing" and "not on the span"; the control reads ok=True.
- forbidden effects: a span drag that places anything.
- end: rows written; the site reset in finally.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_bridge_landing_refusal.py <out.json> [--fresh-map] [--origin X,Z]
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
    ap.add_argument("--origin", default="40,60")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402
    B = PH.PB()
    rows = []
    res = {"script": "live_bridge_landing_refusal.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}

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
        row("BL_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    ox, oz = (int(v) for v in a.origin.split(","))
    rect = (ox - 2, oz - 2, 12, 5)
    reset = lambda: call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                         args="%d;%d;%d;%d" % rect)
    try:
        reset()
        res["open_sky"] = V.open_sky_site(B, rect).get("ok")
        call("jawa/destroy_batch", rects="%d,%d,%d,%d" % rect, categories="All")
        call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % rect)
        call("rimworld/pause_game")
        # landings at ox and ox+6; the hole is ox+1..ox+5, 1 m deep
        digs = [call("jawa/flowworks_excavation_drive", x=ox + i, z=oz, deepenLevels=2, setBodyWaterM=-1, fillInLevels=0).get("success")
                for i in range(1, 6)]
        if not all(digs):
            row("BL_site", "UNMEASURED", {"why": "the trench did not dig", "digs": digs})
            return 2
        east = build(ox + 3, ox + 6, oz)    # begun on the span, dragged to the far landing
        west = build(ox, ox + 3, oz)        # begun on the span, dragged back to the near landing (the rectangle is the same either way)
        for rid, got in (("BL_span_to_far_landing_says_landing", east), ("BL_span_to_near_landing_says_landing", west)):
            placed = "ok=True" in got
            said = "landing" in got and "not on the span" in got
            row(rid, "PASS" if said and not placed else "FAIL", {"got": got, "placed": placed})
        ctrl = build(ox, ox + 6, oz)
        row("BL_control_landing_to_landing_places", "PASS" if "ok=True" in ctrl else "UNMEASURED",
            {"got": ctrl, "why": "the instrument can place a bridge here" if "ok=True" in ctrl
             else "the control did not place: the span rows above cannot be told from a site fault"})
        if "ok=True" not in ctrl:
            for r in rows:
                if r["status"] == "PASS" and r["id"] != "BL_control_landing_to_landing_places":
                    r["status"] = "UNMEASURED"
            save()
        return 1 if any(r["status"] == "FAIL" for r in rows) else (2 if any(r["status"] == "UNMEASURED" for r in rows) else 0)
    finally:
        reset()
        save()


if __name__ == "__main__":
    sys.exit(main())
