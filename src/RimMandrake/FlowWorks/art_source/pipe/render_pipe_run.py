#!/usr/bin/env python3
"""Render a laid universal-pipe run offline as the game draws it: Graphic_Linked's atlas tile per cell by link mask, and on a
straight cell the straights-sheet variant that Machinery/PipeStraightVariants.cs picks from the cell (hash ported below and
pinned to the C# golden values). Map cell (x, z) = (X0 + col, Z0 - row): z grows north.

Library: run_image(atlas_png, straights_png_or_None, ppc) -> RGBA image of RUN on bare ground (no labels).
CLI: render_pipe_run.py ATLAS [STRAIGHTS] OUT.png [--ppc 64]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

X0, Z0 = 100, 100          # an arbitrary map origin, not chosen for a pretty pick
GROUND = (124, 100, 72, 255)

# a 12-cell east-west main; a tee at col 4 drops a branch 2 cells south, then an elbow runs it 4 cells east
RUN = {(c, 0) for c in range(12)} | {(4, 1), (4, 2)} | {(c, 2) for c in range(5, 9)}
GRID = (12, 3)

BUCKET = [0, 0, 0, 1, 1, 2, 3, 4]
NV = 4


def cell_hash(x, z):
    M = 0xFFFFFFFF
    h = (x * 0x8DA6B343) & M
    h ^= (z * 0xD8163841) & M
    h ^= h >> 13
    h = (h * 0x85EBCA6B) & M
    h ^= h >> 16
    return h


def pick(x, z):
    return BUCKET[cell_hash(x, z) & 7]


assert cell_hash(1, 0) == 0x3AEE2DBC and cell_hash(0, 1) == 0xE7D58B85 and cell_hash(-5, 9) == 0xE7A7C01B
assert pick(0, 0) == 0 and pick(1, 0) == 1 and pick(0, 1) == 2 and pick(37, 112) == 0 and pick(-5, 9) == 1


def _shown(img, x0, y0, T):
    P = T // 8
    return img.crop((x0 + P, y0 + P, x0 + T - P, y0 + T - P))


def run_image(atlas_png, straights_png, ppc, run=RUN, grid=GRID, pad=None):
    a = Image.open(atlas_png).convert("RGBA")
    T = a.width // 4
    s = Image.open(straights_png).convert("RGBA") if straights_png else None
    Ts = s.width // NV if s else None
    pad = ppc // 2 if pad is None else pad
    img = Image.new("RGBA", (2 * pad + grid[0] * ppc, 2 * pad + grid[1] * ppc), GROUND)
    for (c, r) in run:
        mask = ((c, r - 1) in run) * 1 + ((c + 1, r) in run) * 2 + ((c, r + 1) in run) * 4 + ((c - 1, r) in run) * 8
        k = pick(X0 + c, Z0 - r) if (s is not None and mask in (5, 10)) else 0
        if k:
            t = _shown(s, (k - 1) * Ts, 0 if mask == 10 else Ts, Ts)
        else:
            col, row = mask % 4, 3 - mask // 4
            t = _shown(a, col * T, row * T, T)
        img.alpha_composite(t.resize((ppc, ppc), Image.LANCZOS), (pad + c * ppc, pad + r * ppc))
    return img


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    ppc = int(sys.argv[sys.argv.index("--ppc") + 1]) if "--ppc" in sys.argv else 64
    args = [x for x in args if x != str(ppc)]
    atlas, out = args[0], args[-1]
    st = args[1] if len(args) == 3 else None
    run_image(atlas, st, ppc).save(out)
    print("wrote", out)
