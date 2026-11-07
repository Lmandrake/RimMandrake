#!/usr/bin/env python3
"""A contact sheet of shots with their names on, to look at many for the price of one. python3 ralph/live/sheet.py OUT.png COLS CELLW a.png b.png ..."""
import os, sys
from PIL import Image, ImageDraw
out, cols, cw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ims = [Image.open(p).convert("RGB") for p in sys.argv[4:]]
th = []
for p, i in zip(sys.argv[4:], ims):
    h = int(i.height * cw / i.width)
    t = i.resize((cw, h), Image.LANCZOS)
    ImageDraw.Draw(t).text((4, 2), os.path.basename(p).rsplit(".", 1)[0], fill=(255, 255, 120))
    th.append(t)
rows = [th[k:k + cols] for k in range(0, len(th), cols)]
H = sum(max(t.height for t in r) for r in rows)
o = Image.new("RGB", (cols * cw, H), (20, 20, 20))
y = 0
for r in rows:
    for k, t in enumerate(r):
        o.paste(t, (k * cw, y))
    y += max(t.height for t in r)
o.save(out)
print(out, o.size)
