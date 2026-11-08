#!/usr/bin/env python3
"""Before/after of lab lays at named rects, side by side, one row per rect. Runs here, no game.
    python3 ralph/live/lab_ba.py LOOK BEFORE_DIR AFTER_DIR OUT.png x,z,w,h [x,z,w,h ...] [--ppc 56]
"""
import argparse, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser()
ap.add_argument("look"); ap.add_argument("before"); ap.add_argument("after"); ap.add_argument("out"); ap.add_argument("rects", nargs="+")
ap.add_argument("--ppc", type=int, default=56)
a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
world = "Transient/lab/ba/worlds/ba_%s.json" % a.look
rows = []
with tempfile.TemporaryDirectory() as td:
    for i, r in enumerate(a.rects):
        pair = []
        for j, d in enumerate((a.before, a.after)):
            o = os.path.join(td, "%d_%d.png" % (i, j))
            subprocess.run([sys.executable, os.path.join(here, "lab_render.py"), world, os.path.join(d, "ba_%s.out.json" % a.look), o, r, "--ppc", str(a.ppc)], check=True, capture_output=True)
            im = Image.open(o).convert("RGB")
            ImageDraw.Draw(im).text((4, 4), "%s %s %s" % (("BEFORE", "AFTER")[j], a.look, r), fill=(255, 255, 0))
            pair.append(im)
        rows.append(pair)
W = max(p[0].width + p[1].width + 8 for p in rows); H = sum(p[0].height + 8 for p in rows)
sheet = Image.new("RGB", (W, H), (0, 0, 0)); y = 0
for p in rows:
    sheet.paste(p[0], (0, y)); sheet.paste(p[1], (p[0].width + 8, y)); y += p[0].height + 8
sheet.save(a.out); print(a.out, sheet.size)
