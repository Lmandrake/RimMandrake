#!/usr/bin/env python3
"""Draw AerialSelfTest.DumpFallen's JSON at about play zoom, so a fallen wire's shape can be judged without the game."""
import json, sys
from PIL import Image, ImageDraw
rows = json.load(open(sys.argv[1]))
PX, W, H = 26, 30, 22
if len(sys.argv) > 3:   # only these aims
    keep = {int(a) for a in sys.argv[3].split(",")}
    rows = [r for r in rows if r["aim"] in keep]
aims = sorted({r["aim"] for r in rows})
seeds = sorted({r["seed"] for r in rows})
im = Image.new("RGB", (len(aims) * W * PX, len(seeds) * H * PX), (122, 92, 66))
d = ImageDraw.Draw(im)
for r in rows:
    ox = aims.index(r["aim"]) * W * PX + 12 * PX
    oy = seeds.index(r["seed"]) * H * PX + (H // 2) * PX
    for x, z in r.get("blocked") or []:
        d.rectangle([ox + x * PX, oy - (z + 1) * PX, ox + (x + 1) * PX - 1, oy - z * PX - 1], fill=(70, 66, 62))
for r in rows:
    ox = aims.index(r["aim"]) * W * PX + 12 * PX
    oy = seeds.index(r["seed"]) * H * PX + (H // 2) * PX
    p = [(ox + x * PX, oy - z * PX) for x, z in r["pts"]]
    d.line(p, fill=(20, 20, 20), width=3)
    d.ellipse([p[-1][0] - 4, p[-1][1] - 4, p[-1][0] + 4, p[-1][1] + 4], fill=(255, 170, 40))
for i in aims:
    for j in range(len(seeds)):
        ox, oy = aims.index(i) * W * PX + 12 * PX, j * H * PX + (H // 2) * PX
        d.line([(ox, oy), (ox, oy - 3.3 * PX)], fill=(200, 200, 200), width=4)
im.save(sys.argv[2])
