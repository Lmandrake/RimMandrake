"""Visit 8: tight cell-rect captures of each walk-save station on the staged map (read-only: no write, no tick), so every
station is looked at zoomed in before the save reaches him. Stations from evidence/walk_save.json's windows (the first
four) and the densest charred-wall cluster (as walk_save.py finds it). Prints each capture path."""
import json, os, sys, time
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
W = json.load(open(os.path.join(ROOT, "design/concepts/Pyrelands/version/in_game/visit_9/evidence/walk_save.json")))
(fx, fz), (cx, cz), (sx, sz), (rx, rz) = [tuple(w) for w in W["windows"][:4]]
rects = [("burn_front", (fx - 2, fz, 24, 16)), ("creatures", (cx, cz, 20, 16)), ("scorchfruit", (sx + 4, sz + 2, 12, 12)),
         ("roof_wither", (rx, rz, 20, 16))]
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    def call(name, **kw):
        return clockgate._unwrap(raw.call(name, kw))
    ex = call("jawa/export_things", rect="0,0,250,250", includePawns=False, includeItems=False, limit=100000) or {}
    pts = [(int(w.get("x", 0)), int(w.get("z", 0))) for w in ex.get("things") or []
           if "Wall" in str(w.get("def")) and w.get("paint") == "RM_FE_Charred"]
    if len(pts) >= 4:
        r = max(pts, key=lambda a: sum(abs(a[0] - b[0]) <= 8 and abs(a[1] - b[1]) <= 8 for b in pts))
        rects.append(("charred_ruin", (r[0] - 8, r[1] - 6, 16, 12)))
    call("jawa/clear_ui")
    call("jawa/safe_advance", ticks=60)   # his list draws a flame on the ticks after the camera reaches it
    for name, (x, z, w, h) in rects:
        call("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + h // 2)
        call("jawa/safe_advance", ticks=30)
        res = call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1, rootSize=14, fileName="pv9_walk_closeup_%s" % name) or {}
        print("SHOT", name, (x, z, w, h), res.get("path"))
        time.sleep(1.2)   # the capture is named by the second: two in one second overwrite each other
