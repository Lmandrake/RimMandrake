#!/usr/bin/env python3
"""Zoom sheet of render_joins.py output: per look, the N and S joiner and the N and S port coupling, 1 cell square each.
Usage: crop_ns.py RENDER.png OUT.png --px PX (the px render_joins.py used)"""
import argparse
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--px", type=int, default=256)
a = ap.parse_args(); px = a.px
src = Image.open(a.src); rows = 4; rh = src.height // rows; H = 2 * 1.6
cells = [(0.8 + 1.6 * 1, 2.4), (0.8 + 1.6 * 3, 2.4), (7.2 + 1.6 * 1, 0.8 - 0.25), (7.2 + 1.6 * 3, 0.8 + 0.25)]
out = Image.new("RGB", (4 * px, rows * px))
for r in range(rows):
    for c, (x, z) in enumerate(cells):
        cx, cy = x * px, r * rh + (H - z) * px
        out.paste(src.crop((int(cx - px / 2), int(cy - px / 2), int(cx + px / 2), int(cy + px / 2))), (c * px, r * px))
out.save(a.out); print(a.out, out.size)
