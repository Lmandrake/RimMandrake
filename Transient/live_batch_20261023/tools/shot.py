"""shot.py MAPID X Z W H NAME [PAD] -- zoomed cell-rect capture, copied into Transient/live_batch_20261023/."""
import sys, json, shutil, time, os
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
mid, x, z, w, h, name = sys.argv[1:7]
pad = int(sys.argv[7]) if len(sys.argv) > 7 else 1
h_, p_, t_ = resolve_endpoint()
with RimBridge(h_, p_, t_) as B:
    if mid != "-":
        r = B.call("jawa/set_current_map", {"mapId": int(mid)}); time.sleep(1.0)
    W, Hh = int(w) + 2 * pad, int(h) + 2 * pad
    rs = max(Hh / 2.0, W * 9.0 / 32.0) + 0.6
    B.call("rimworld/jump_camera_to_cell", {"x": int(x) + int(w) // 2, "z": int(z) + int(h) // 2})
    B.call("rimworld/set_camera_zoom", {"rootSize": float(rs)}); time.sleep(0.8)
    B.call("jawa/clear_ui", {})
    r = B.call("rimworld/screenshot_cell_rect", {"x": int(x), "z": int(z), "width": int(w), "height": int(h), "paddingCells": pad})
    p = r.get("path")
    time.sleep(1.5)
    dst = os.path.join(r"Transient\live_batch_20261023", os.environ.get("SHOTDIR", "r3a"), name + ".png")
    if p and os.path.exists(p):
        shutil.copy(p, dst); print("OK", dst)
    else:
        print("NOSHOT", json.dumps(r)[:400])
