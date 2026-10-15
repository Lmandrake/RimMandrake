"""TANK_TALL_BUILD_TWICE_THE_DRINK v2: draw the camera guide (grey blockout) an edit is anchored to.
The convention (design/RimMandrake/building_camera_perspective_2026-10-14.md): orthographic, upright cylinder seen
from ~34 deg above horizontal => top ellipse minor/major = 0.56, vertical sides parallel, bottom arc the same ellipse.
usage: guide.py <out.png> <W> <H> <cx> <a> <top_y> <bottom_y> [ratio]   (all px at generation scale)"""
import sys
from PIL import Image, ImageDraw
out, W, H, cx, a, top, bot = sys.argv[1], *map(int, sys.argv[2:8])
k = float(sys.argv[8]) if len(sys.argv) > 8 else 0.56
b = a * k
skid = int(0.10 * (bot - top))                      # base skid height
cyt, cyb = top + b, bot - skid - b                   # ellipse centres: top rim, bottom rim
im = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
# skid base (a low rectangular frame under the drum, inside the footprint)
d.rectangle([cx - a * 0.92, cyb + b * 0.2, cx + a * 0.92, bot], fill=(95, 80, 62), outline=(40, 34, 28), width=4)
# body: horizontal shading, lit centre-left (overhead-frontal light)
for x in range(int(cx - a), int(cx + a) + 1):
    u = (x - cx) / a
    v = int(150 + 70 * max(0, 1 - abs(u + 0.25) * 1.3))
    d.line([x, cyt, x, cyb], fill=(v, v, v))
d.chord([cx - a, cyb - b, cx + a, cyb + b], 0, 180, fill=(140, 140, 140))   # lower half of bottom rim
for x in range(int(cx - a), int(cx + a) + 1):                                 # reshade the lower arc to match body
    u = (x - cx) / a
    v = int(150 + 70 * max(0, 1 - abs(u + 0.25) * 1.3)) - 20
    yb = cyb + b * (1 - u * u) ** 0.5
    d.line([x, cyb, x, yb], fill=(v, v, v))
d.ellipse([cx - a, cyt - b, cx + a, cyt + b], fill=(232, 232, 232), outline=(60, 60, 60), width=5)   # top face
la = a * 0.36; d.ellipse([cx - la, cyt - la * k, cx + la, cyt + la * k], fill=(200, 200, 200), outline=(70, 70, 70), width=4)  # manway lid
d.line([cx - a, cyt, cx - a, cyb], fill=(60, 60, 60), width=5); d.line([cx + a, cyt, cx + a, cyb], fill=(60, 60, 60), width=5)
d.arc([cx - a, cyb - b, cx + a, cyb + b], 0, 180, fill=(60, 60, 60), width=5)
im.save(out); print(out, dict(a=a, b=round(b), top_rim_centre=round(cyt), bottom_rim_centre=round(cyb), body_px=round(cyb - cyt)))
