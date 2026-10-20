#!/usr/bin/env python3
"""shoot_lineup_facings.py -- after stage_xenotype_grid.py, shoot the same line-up in every facing, close up.

stage_xenotype_grid.py frames the whole grid and faces everyone south. A HEAD review needs the
camera close and all four facings (owner, 2026-10-20: "I REALLY want to see a screenshot of aliens
with these head types installed"). This turns every pawn in the rect to each facing in turn
(rotation-locked, drafted pawns keep it), zooms in to the camera's minimum, frames the rect, clears
the UI and shoots one PNG per facing.

RUN WITH python.exe (the bridge binds Windows loopback).

usage: python.exe shoot_lineup_facings.py --rect x,z,w,h --shot NAME [--facings south,east,north,west]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as rc  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def call(b, tool, params=None):
    try:
        return b.call(tool, params or {}, check=False)
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "message": "%s: %s" % (type(exc).__name__, exc)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rect", required=True, help="x,z,w,h of the line-up (cells)")
    ap.add_argument("--shot", required=True)
    ap.add_argument("--facings", default="south,east,north,west")
    ap.add_argument("--zoom", type=float, default=0,
                    help="camera rootSize; 0 = frame_cell_rect (MEASURED 2026-10-20: it zooms IN past a 21-cell rect, use --zoom)")
    a = ap.parse_args()
    x, z, w, h = (int(v) for v in a.rect.split(","))
    host, port, token = rc.resolve_endpoint()
    with rc.RimBridge(host=host, port=port, token=token) as b:
        pawns = call(b, "jawa/list_pawns").get("pawns") or []
        ids = [str(p["id"]) for p in pawns if not p.get("dead") and p.get("x") is not None
               and x <= p["x"] < x + w and z <= p["z"] < z + h]
        print("subjects in rect: %d" % len(ids))
        if not ids:
            return 2
        call(b, "rimworld/jump_camera_to_cell", {"x": x + w // 2, "z": z + h // 2})
        if a.zoom:
            call(b, "rimworld/set_camera_zoom", {"rootSize": a.zoom})
        out = []
        for f in a.facings.split(","):
            r = call(b, "jawa/set_pawn_rotation", {"pawnId": ",".join(ids), "dir": f, "lockRotation": True})
            if not a.zoom:
                call(b, "rimworld/frame_cell_rect", {"x": x - 1, "z": z - 1, "width": w + 2,
                                                     "height": h + 2, "paddingCells": 0})
            call(b, "jawa/clear_ui")
            time.sleep(0.8)
            s = call(b, "jawa/take_screenshot", {"fileName": "%s_%s" % (a.shot, f)})
            out.append((f, r.get("success"), s.get("filePath") or s.get("message")))
            print("%-5s rotate=%s shot=%s" % (f, r.get("success"), json.dumps(out[-1][2])))
        cam = call(b, "rimworld/get_camera_state")
        print("camera map=%s zoom=%s" % (cam.get("mapId"), cam.get("zoom") or cam.get("rootSize")))
        print("The PNGs are a cache, not an observation. LOOK at them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
