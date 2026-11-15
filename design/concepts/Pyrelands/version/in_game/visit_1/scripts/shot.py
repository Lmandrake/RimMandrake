"""shot.py name x z w h [name x z w h ...] -> zoomed captures, copied to Transient/pv1/shots/"""
import sys, os, shutil, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
a = sys.argv[1:]
os.makedirs(r"Transient\pv1\shots", exist_ok=True)
with RimBridge(h,p,tk) as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    for i in range(0, len(a), 5):
        name, x, z, w, hh = a[i], *map(int, a[i+1:i+5])
        try: rb.call("jawa/clear_ui", {})
        except Exception as e: print("clear_ui", e)
        rb.call("rimworld/jump_camera_to_cell", {"x": x + w//2, "z": z + hh//2})
        rb.call("rimworld/frame_cell_rect", {"x": x, "z": z, "width": w, "height": hh, "paddingCells": 2})
        time.sleep(0.5)
        r = rb.call("rimworld/take_screenshot", {"fileName": name})
        path = r.get("path") or r.get("filePath") or str(r)
        print(name, path)
        try:
            dst = os.path.join(r"Transient\pv1\shots", os.path.basename(path))
            shutil.copy(path, dst); print("  ->", dst)
        except Exception as e: print("  copy failed", e)
