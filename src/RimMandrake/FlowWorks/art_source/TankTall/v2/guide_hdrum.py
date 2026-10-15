"""TANK_TALL_BUILD_TWICE_THE_DRINK v3: camera guide for a SHORT tank - a drum lying east-west on a skid - at the measured
building camera (orthographic ~35 deg; design/RimMandrake/building_camera_perspective_2026-10-14.md).
For an E-W drum of radius r seen from 35 deg: the silhouette stays 2r tall, the world-top line sits 0.18r below the
silhouette top (r(1-cos35)), the south-facing line 0.57r below centre, and a hatch on top is an ellipse 0.57 tall for
its width. The skid shows its TOP face (lit) in front of the drum, then a thin front face.
usage: guide_hdrum.py <out.png> <W> <H> <x0> <x1> <top_y> <r> <bottom_y>"""
import sys
from PIL import Image, ImageDraw
out, W, H, x0, x1, top, r, bot = sys.argv[1], *map(int, sys.argv[2:9])
S, C = 0.57, 0.82
im = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
cy = top + r
# skid: top face (depth band) then a front face, spanning most of the drum length
sk_top = cy + int(0.55 * r); sk_front = bot - int(0.10 * (bot - top))
d.rectangle([x0 + 40, sk_top, x1 - 40, sk_front], fill=(170, 140, 100), outline=(50, 40, 30), width=4)        # top face, lit
d.rectangle([x0 + 40, sk_front, x1 - 40, bot], fill=(100, 80, 58), outline=(50, 40, 30), width=4)            # front face
for sx in (x0 + 0.25 * (x1 - x0), x1 - 0.25 * (x1 - x0)):                                                     # saddles
    d.rectangle([sx - 30, cy + int(0.4 * r), sx + 30, sk_top + 30], fill=(90, 90, 90), outline=(40, 40, 40), width=3)
# drum body: shade by the surface normal's facing (lit from overhead-front: brightest near the world-top line)
er = int(0.45 * r)                                  # dished-head rounding at each end
for y in range(top, top + 2 * r + 1):
    t = (y - top) / (2 * r)                         # 0 at silhouette top, 1 at bottom
    v = int(235 - 140 * abs(t - 0.09) ** 1.2)
    dy = abs(y - cy) - (r - er)
    ins = er - (max(0.0, er * er - dy * dy)) ** 0.5 if dy > 0 else 0
    d.line([x0 + ins, y, x1 - ins, y], fill=(v, v, v))
d.rounded_rectangle([x0, top, x1, top + 2 * r], radius=er, outline=(60, 60, 60), width=5)
# hatch lying on the world-top line: an ellipse 0.57 tall for its width
hx, hy, hw = (x0 + x1) / 2, top + (1 - C) * r, 0.13 * (x1 - x0)
d.ellipse([hx - hw, hy - hw * S, hx + hw, hy + hw * S], fill=(205, 205, 205), outline=(60, 60, 60), width=4)
d.line([x0 + er, top + int((1 - C) * r), x1 - er, top + int((1 - C) * r)], fill=(250, 250, 250), width=2)   # top line highlight
im.save(out); print(out, dict(r=r, top_line=round(top + (1 - C) * r), hatch_w=round(2 * hw), hatch_h=round(2 * hw * S)))
