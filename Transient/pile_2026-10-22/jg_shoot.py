"""WSL: python3 Transient/pile_2026-10-22/jg_shoot.py NAME CX CZ ROOT X0 Z0 W H  -> joints/NAME.png (cropped to cells X0..X0+W, Z0..Z0+H)"""
import json, subprocess, sys, os, time
from PIL import Image
name, cx, cz, root = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
x0, z0, w, h = (float(v) for v in sys.argv[5:9])
out = subprocess.run(["python.exe", "Transient/pile_2026-10-22/joints_gallery.py", "shoot", name, cx, cz, root],
                     capture_output=True, text=True, timeout=120).stdout.replace("\r", "")
j = json.loads([l for l in out.splitlines() if l.startswith("{")][-1])
vr = j["cam"]["viewRect"]
src = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots/%s.png" % name
for _ in range(40):
    if os.path.exists(src) and os.path.getsize(src) > 0: break
    time.sleep(0.25)
im = Image.open(src).convert("RGB")
W, H = im.size
# viewRect is integer cells; the camera centre is cx+0.5,cz+0.5 and the visible span is H px tall
pxc = H / (vr["height"] - 1.0)          # approx px per cell (viewRect pads one cell)
ccx, ccz = float(cx) + 0.5, float(cz) + 0.5
def px(x, z):
    return (W / 2 + (x - ccx) * pxc, H / 2 - (z - ccz) * pxc)
l, t = px(x0, z0 + h); r, b = px(x0 + w, z0)
box = tuple(int(round(v)) for v in (max(0, l), max(0, t), min(W, r), min(H, b)))
c = im.crop(box)
dst = "Transient/pile_2026-10-22/joints/%s.png" % name
c.save(dst)
print(json.dumps({"out": dst, "pxPerCell": round(pxc, 1), "viewRect": vr, "crop": box, "size": c.size}))
