#!/usr/bin/env python3
"""Live scene (kind A): a built suspension bridge offers Choose style, and the pick restyles every part of that bridge.

RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES (owner walk 2026-11-20: "For the bridges, they have Styles like Industrial
but no UI button to select it."). Offline: SelfTest/SuspensionBridgeChecks.cs (Suspension_built_bridge_offers_choose_style).

Contract.
- claim: a steel suspension bridge built over a 1 m trench shows a "Choose style" button when its deck is selected; picking a look
  in its menu gives every part on the bridge's squares (deck, anchors, railings) that look, and the bridge keeps it.
- entry point: the player's route: rimworld/click_cell on a deck square, rimworld/list_selected_gizmos, rimworld/execute_gizmo,
  the menu's look row through rimworld/execute_context_menu_option. Read back with RM_SuspensionProofs.ProofBridgeLook (read only).
- valid opportunity: the trench digs and the bridge is built (god mode build through the drag designator).
- success: the button is there; after picking Industrial, then Modern, every styled part reads that look and the record too.
- forbidden effects: a part of the bridge left in the old look; anything off the bridge restyled.
- end: rows written; the site reset in finally.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_bridge_choose_style.py <out.json> [--fresh-map] [--origin X,Z]
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
    ap.add_argument("--origin", default="40,80")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402
    B = PH.PB()
    rows = []
    res = {"script": "live_bridge_choose_style.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}

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
        r = call("jawa/static_call", type=PROOFS, method="ProofBuild", args="%d,%d;%d,%d;steel;god" % (x1, z, x2, z))
        return str(r.get("result") or r.get("error") or r.get("message") or r)

    if a.fresh_map:
        call("rimworld/go_to_main_menu")
        call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    import validation_core as V    # noqa: E402
    if not V._wait_playing(B, leave_s=0)[0]:
        row("CS_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    ox, oz = (int(v) for v in a.origin.split(","))
    rect = (ox - 2, oz - 2, 12, 5)
    reset = lambda: call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                         args="%d;%d;%d;%d" % rect)

    def read():
        r = call("jawa/static_call", type=PROOFS, method="ProofBridgeLook", args="%d,%d" % (ox + 3, oz))
        return str(r.get("result") or r.get("error") or r.get("message") or r)

    def parts(got):
        tail_ = got.split(" parts=", 1)[1] if " parts=" in got else ""
        return [p.rsplit(":", 1) for p in tail_.split(",") if ":" in p]

    def pick(look):
        call("rimworld/clear_selection")
        call("rimworld/click_cell", x=ox + 3, z=oz)
        gz = (call("rimworld/list_selected_gizmos").get("gizmos")) or []
        g = next((q for q in gz if str(q.get("label") or "").startswith("Choose style")), None)
        if g is None:
            return False, [q.get("label") for q in gz][:8]
        call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
        opts = (call("rimworld/get_context_menu_options").get("options")) or []
        hit = [q for q in opts if str(q.get("label") or "").split(" ")[0] == look]
        if not hit:
            call("rimworld/close_context_menu")
            return True, "no %s row in %s" % (look, [q.get("label") for q in opts])
        call("rimworld/execute_context_menu_option", optionIndex=hit[0].get("index"))
        call("rimworld/clear_selection")
        return True, None

    try:
        reset()
        res["open_sky"] = V.open_sky_site(B, rect).get("ok")
        call("jawa/destroy_batch", rects="%d,%d,%d,%d" % rect, categories="All")
        call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % rect)
        call("rimworld/pause_game")
        digs = [call("jawa/flowworks_excavation_drive", x=ox + i, z=oz, deepenLevels=2, setBodyWaterM=-1, fillInLevels=0).get("success")
                for i in range(1, 6)]
        built = build(ox, ox + 6, oz)
        res["built"] = built
        if not all(digs) or "ok=True" not in built or "decks=0" in built:
            row("CS_site", "UNMEASURED", {"why": "the trench or the bridge did not build", "digs": digs, "built": built})
            return 2
        res["before"] = read()
        for i, look in enumerate(("Industrial", "Modern")):
            has, why = pick(look)
            if i == 0:
                row("CS_built_bridge_has_choose_style", "PASS" if has else "FAIL", {"gizmos": why if not has else "Choose style"})
            if not has:
                break
            got = read()
            ps = parts(got)
            wrong = [p for p in ps if p[1] != look]
            ok = why is None and len(ps) >= 3 and not wrong and ("record=" + look) in got
            row("CS_pick_%s_restyles_whole_bridge" % look, "PASS" if ok else "FAIL",
                {"got": got[:400], "menu": why, "parts": len(ps), "wrong": wrong[:5]})
        return 1 if any(r["status"] == "FAIL" for r in rows) else (2 if any(r["status"] == "UNMEASURED" for r in rows) else 0)
    finally:
        call("rimworld/clear_selection")
        reset()
        save()


if __name__ == "__main__":
    sys.exit(main())
