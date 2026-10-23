"""zoomshot.py X Z ROOTSIZE NAME -- full-screen screenshot at a root size, prints image size and px/cell"""
import sys, json, time, shutil, os
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
x, z, rs, name = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
H,P,T = resolve_endpoint()
with RimBridge(H,P,T) as B:
    B.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    B.call("rimworld/set_camera_zoom", {"rootSize": rs}); time.sleep(1.0)
    cs = B.call("rimworld/get_camera_state", {})
    B.call("jawa/clear_ui", {}); time.sleep(0.5)
    r = B.call("rimworld/take_screenshot", {"fileName": name, "includeTargets": False})
    p = r.get("path") or r.get("screenshotPath"); time.sleep(1.5)
    dst = os.path.join(r"Transient\live_batch_20261023\r2", name + ".png")
    shutil.copy(p, dst)
    from PIL import Image
    w, h = Image.open(dst).size
    print(json.dumps({"rootSize": cs.get("rootSize"), "viewRect": cs.get("viewRect"), "img": [w, h], "pxPerCell_h": h / (2.0 * float(cs.get("rootSize"))), "out": dst}))
