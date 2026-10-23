"""crop.py NAME CX CZ RS OUT [X0 Z0 W H] -- copy the game screenshot NAME (shot centred on cell CX,CZ at rootSize RS) to
hose_audit/OUT.png, optionally cropped to the cell rect, with a 1-cell grid tick + cell labels on the border. WSL python3."""
import sys, os, time
from PIL import Image, ImageDraw
SS = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots/%s.png"
name, cx, cz, rs, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), max(8.0, float(sys.argv[4])), sys.argv[5]
src = SS % name
for _ in range(40):
    if os.path.exists(src) and os.path.getsize(src) > 0: break
    time.sleep(0.25)
im = Image.open(src).convert("RGB"); W, H = im.size
pxc = H / (2 * rs)
def px(x, z): return (W / 2 + (x - cx - 0.5) * pxc, H / 2 - (z - cz - 0.5) * pxc)
if len(sys.argv) > 9:
    x0, z0, w, h = (float(v) for v in sys.argv[6:10])
else:
    x0, z0 = cx + 0.5 - W / 2 / pxc, cz + 0.5 - H / 2 / pxc; w, h = W / pxc, H / pxc
l, t = px(x0, z0 + h); r, b = px(x0 + w, z0)
box = tuple(int(round(v)) for v in (max(0, l), max(0, t), min(W, r), min(H, b)))
c = im.crop(box)
d = ImageDraw.Draw(c)
import math
for gx in range(math.ceil(x0), int(x0 + w) + 1):
    X = px(gx, 0)[0] - box[0]
    d.line([(X, 0), (X, 8)], fill=(255, 255, 0), width=2)
    if gx % 2 == 0: d.text((X + 2, 9), str(gx), fill=(255, 255, 0))
for gz in range(math.ceil(z0), int(z0 + h) + 1):
    Y = px(0, gz)[1] - box[1]
    d.line([(0, Y), (8, Y)], fill=(255, 255, 0), width=2)
    if gz % 2 == 0: d.text((10, Y - 12), str(gz), fill=(255, 255, 0))
if c.size[0] > 1600:
    c = c.resize((1600, int(c.size[1] * 1600 / c.size[0])), Image.LANCZOS)
dst = os.path.join("Transient/pile_2026-10-22/hose_audit", out + ".png")
c.save(dst); print(dst, c.size, "px/cell %.0f" % pxc)
