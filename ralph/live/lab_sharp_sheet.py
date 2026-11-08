#!/usr/bin/env python3
"""Contact sheet of the bends lab_sharp.py found: one 4x4-cell crop per bend, lab_render style. Runs here, no game.

    python3 ralph/live/lab_sharp_sheet.py WORLD.json LAID.json SHARP.json OUT.png [--only unforced|all] [--skip-tangle] [--max 30]
"""
import argparse, json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser()
ap.add_argument("world"); ap.add_argument("laid"); ap.add_argument("sharp"); ap.add_argument("out")
ap.add_argument("--max", type=int, default=30); ap.add_argument("--skip-tangle", action="store_true"); ap.add_argument("--tangle-only", action="store_true")
ap.add_argument("--cells", type=int, default=4); ap.add_argument("--ppc", type=int, default=48)
a = ap.parse_args()
rows = [r for r in json.load(open(a.sharp)) if not r["forced"]]
if a.skip_tangle: rows = [r for r in rows if not r["piece"].startswith("tangle")]
if a.tangle_only: rows = [r for r in rows if r["piece"].startswith("tangle")]
rows = rows[:a.max]
here = os.path.dirname(os.path.abspath(__file__))
tiles = []
with tempfile.TemporaryDirectory() as td:
    one = os.path.join(td, "one.json")
    for i, r in enumerate(rows):
        json.dump([r], open(one, "w"))
        x0, z0 = int(r["apex"][0] - a.cells / 2), int(r["apex"][1] - a.cells / 2)
        o = os.path.join(td, "t%d.png" % i)
        subprocess.run([sys.executable, os.path.join(here, "lab_render.py"), a.world, a.laid, o, "%d,%d,%d,%d" % (x0, z0, a.cells, a.cells), "--ppc", str(a.ppc), "--sharp", one], check=True, capture_output=True)
        im = Image.open(o).convert("RGB")
        ImageDraw.Draw(im).text((3, 3), "%d %s %s t%.0f" % (i, r["cls"], r["piece"][:28], r["turn"]), fill=(255, 255, 255))
        tiles.append(im)
cols = 6
W = a.cells * a.ppc
sheet = Image.new("RGB", (cols * (W + 4), ((len(tiles) + cols - 1) // cols) * (W + 4)), (0, 0, 0))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * (W + 4), (i // cols) * (W + 4)))
sheet.save(a.out)
print(a.out, len(tiles))
