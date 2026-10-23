#!/usr/bin/env python3
"""Compose the Modern pump: generated pump body (no stubs) + four PVC port stubs cut from the network's own pipe strip,
exactly the drawn pipe width (0.136 cell = 70 px at 512 px/cell), centred on the four edge midpoints, each with a
slim union ring (1.25x pipe). Stubs go UNDER the body. Usage: pump_stubs.py BODY.png STRIP.png RING.png OUT.png"""
import sys
import numpy as np
from PIL import Image
body, strip, ring, out = sys.argv[1:5]
N = 512; W = round(0.136 * N); RW, RH = 20, round(W * 1.25)
b = Image.open(body).convert("RGBA").resize((N, N), Image.LANCZOS)
s = Image.open(strip).convert("RGBA"); a = np.asarray(s)[..., 3]
rows = np.where((a > 128).mean(1) > 0.95)[0]
band = s.crop((200, rows[0], 200 + 4 * (rows[-1] - rows[0] + 1), rows[-1] + 1)).resize((N // 2, W), Image.LANCZOS)
rg = Image.open(ring).convert("RGBA").resize((RW, RH), Image.LANCZOS)
c = Image.new("RGBA", (N, N), (0, 0, 0, 0))
L = round(0.26 * N)                                  # stub length from the edge, reaching under the body
h = Image.new("RGBA", (L, RH), (0, 0, 0, 0)); h.alpha_composite(band.crop((0, 0, L, W)), (0, (RH - W) // 2))
h.alpha_composite(rg, (L - RW - 46, 0))              # union ring just outside the port boss
for k, (x, y) in enumerate([(0, N // 2 - RH // 2)]):
    pass
west = h; east = h.transpose(Image.FLIP_LEFT_RIGHT)
north = h.rotate(-90, expand=True); south = north.transpose(Image.FLIP_TOP_BOTTOM)
c.alpha_composite(west, (0, N // 2 - RH // 2)); c.alpha_composite(east, (N - L, N // 2 - RH // 2))
c.alpha_composite(north, (N // 2 - RH // 2, 0)); c.alpha_composite(south, (N // 2 - RH // 2, N - L))
c.alpha_composite(b)
c.save(out); print(out, "stub px", W, "ring px", RH)
