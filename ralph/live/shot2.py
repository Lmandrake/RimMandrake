"""shot2.py name x z w h root : frame the camera, wait, jawa/take_screenshot (the H.shot route), report the path."""
import sys, time, json
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import fwb
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
n, x, z, w, h = sys.argv[1], *map(int, sys.argv[2:6])
root = float(sys.argv[6]) if len(sys.argv) > 6 else 0
B.call("jawa/clear_ui", all=True)
r0 = B.call("rimworld/frame_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1, **({"rootSize": root} if root else {}))
time.sleep(2.0)
r = B.call("jawa/take_screenshot", fileName="%s_%s" % (n, time.strftime("%H%M%S")))
print(json.dumps({"frame": {k: r0.get(k) for k in ("success", "message")}, "shot": r.get("filePath") or r}, default=str)[:800])
