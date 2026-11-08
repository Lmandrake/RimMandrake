#!/usr/bin/env python3
"""The blind judge's spots, cropped from several shoots side by side, one row per spot. Runs here on the shots folder.
    python3 ralph/live/judge_spots.py OUT.png TAG [TAG ...] [--spots Look_tile:x,y:label;...] [--w 360 --h 260]
"""
import argparse, os
from PIL import Image, ImageDraw
SHOTS = "/mnt/d/ClaudeWork/rimmandrake/ralph_gss/shots"
SPOTS = [("Industrial_t21", 241, 135, "1 mast box lead over the wires"), ("Scrapper_t21", 225, 330, "1b mast pair"),
         ("Modern_t31", 890, 358, "2 spur ring over strip"), ("Scrapper_t31", 900, 360, "3 spur ring under box"),
         ("Futuristic_t11", 232, 159, "4 figure-8"), ("Futuristic_t31", 920, 389, "5 ring under box"),
         ("Scrapper_t01", 621, 271, "6 lamp plug hooked tip"), ("Modern_t11", 1064, 216, "7 socket X"),
         ("Modern_t11", 350, 150, "lamp post in at foot out at top"), ("Futuristic_t10", 654, 347, "hump on box-plate hop"),
         ("Scrapper_t20", 436, 386, "circle into solar panel")]
ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("tags", nargs="+")
ap.add_argument("--w", type=int, default=360); ap.add_argument("--h", type=int, default=260)
a = ap.parse_args()
rows = []
for frame, x, y, label in SPOTS:
    cells = []
    for t in a.tags:
        p = os.path.join(SHOTS, "%s_%s.png" % (t, frame))
        if not os.path.exists(p):
            cells.append(Image.new("RGB", (a.w, a.h), (40, 0, 0))); continue
        im = Image.open(p).convert("RGB")
        x0 = max(0, min(im.width - a.w, x - a.w // 2)); y0 = max(0, min(im.height - a.h, y - a.h // 2))
        c = im.crop((x0, y0, x0 + a.w, y0 + a.h))
        ImageDraw.Draw(c).text((4, 4), t, fill=(255, 255, 0))
        cells.append(c)
    row = Image.new("RGB", (len(cells) * (a.w + 6), a.h + 18), (0, 0, 0))
    ImageDraw.Draw(row).text((4, 2), "%s (%d,%d) %s" % (frame, x, y, label), fill=(255, 160, 160))
    for i, c in enumerate(cells): row.paste(c, (i * (a.w + 6), 18))
    rows.append(row)
H = sum(r.height + 4 for r in rows); W = max(r.width for r in rows)
s = Image.new("RGB", (W, H)); y = 0
for r in rows: s.paste(r, (0, y)); y += r.height + 4
s.save(a.out); print(a.out, s.size)
