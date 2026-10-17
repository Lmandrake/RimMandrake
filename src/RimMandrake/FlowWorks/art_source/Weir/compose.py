#!/usr/bin/env python3
"""Offline composites of the weir as RM_Building_BankWeir.Print lays it out (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS).
Synthetic river (not the game's water shader): ground, the water under-layer per wet cell (1 x 3 cells, under the wall),
the body per section (2 cells, seamless), the spill sheet per wet cell, a post (0.7 cell, lifted 0.08) at each FREE end.
Writes out/composite_<Look>.png: three scenes side by side at 128 px/cell --
  A  a lone bank weir (1x2, current flowing south): posts at both ends
  B  a joined wall of four sections bank to bank across a 6-cell river flowing south (East art)
  C  a joined wall of three sections across a river flowing east (North art)
and out/composite_<Look>_scene<X>.png per scene (for true-scale panels). Usage: compose.py [Look ...]"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
C = 128
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]


def ground(w, h, water):
    """w x h cells; water(x, z) -> bool. z=0 is the SOUTH row (bottom of the image)."""
    rng = np.random.default_rng(1)
    img = np.zeros((h * C, w * C, 4), np.uint8)
    for z in range(h):
        for x in range(w):
            y0 = (h - 1 - z) * C
            if water(x, z):
                base = np.array([52, 96, 118])
            else:
                base = np.array([168, 146, 108])
            n = rng.normal(0, 6, (C, C, 1))
            img[y0:y0 + C, x * C:(x + 1) * C, :3] = np.clip(base + n, 0, 255)
            img[y0:y0 + C, x * C:(x + 1) * C, 3] = 255
    return Image.fromarray(img)


def px(x, z, h):
    """Cell-space point (x right, z up, origin SW corner) -> image pixel."""
    return int(round(x * C)), int(round((h - z) * C))


def paste_centered(base, im, cx, cz, h):
    x, y = px(cx, cz, h)
    base.alpha_composite(im, (x - im.size[0] // 2, y - im.size[1] // 2))


def scene(look, w, h, water, sections, art):
    """sections: list of (cells [(x,z),(x,z)]) of one straight run; art: 'east' (E-W wall) or 'north' (N-S wall)."""
    lo = OUT / look
    body = Image.open(lo / f"RM_BankWeir_{art}.png").convert("RGBA")
    spill = Image.open(lo / f"RM_BankWeirSpill_{art}.png").convert("RGBA")
    cap = Image.open(lo / "RM_BankWeirCap.png").convert("RGBA").resize((int(C * 0.7), int(C * 0.7)), Image.LANCZOS)
    wat = Image.open(OUT / f"RM_BankWeirWater_{art}.png").convert("RGBA")
    img = ground(w, h, water)
    horizontal = art in ("east", "west")
    occupied = {c for s in sections for c in s}
    for s in sections:                      # under-layer first (FloorEmplacement), every section
        for (x, z) in s:
            if water(x, z):
                paste_centered(img, wat, x + 0.5, z + 0.5, h)
    for s in sections:
        cx = sum(c[0] for c in s) / 2 + 0.5
        cz = sum(c[1] for c in s) / 2 + 0.5
        paste_centered(img, body, cx, cz, h)
        for (x, z) in s:
            if water(x, z):
                if horizontal:
                    paste_centered(img, spill, x + 0.5, cz, h)
                else:
                    paste_centered(img, spill, cx, z + 0.5, h)
    for s in sections:
        cx = sum(c[0] for c in s) / 2 + 0.5
        cz = sum(c[1] for c in s) / 2 + 0.5
        if horizontal:
            xs = [c[0] for c in s]
            for end, beyond in ((min(xs), (min(xs) - 1, s[0][1])), (max(xs) + 1, (max(xs) + 1, s[0][1]))):
                if beyond not in occupied:
                    paste_centered(img, cap, end, cz + 0.08, h)
        else:
            zs = [c[1] for c in s]
            for end, beyond in ((min(zs), (s[0][0], min(zs) - 1)), (max(zs) + 1, (s[0][0], max(zs) + 1))):
                if beyond not in occupied:
                    paste_centered(img, cap, cx, end + 0.08, h)
    return img


def build(look):
    # A: river x 3..8 (flows south), a lone bank weir at the west bank, row z=2
    a = scene(look, 6, 5, lambda x, z: x >= 2, [[(1, 2), (2, 2)]], "east")
    # B: 10 x 5, river x 2..7; four sections bank to bank on row z=2
    b = scene(look, 10, 5, lambda x, z: 2 <= x <= 7, [[(1, 2), (2, 2)], [(3, 2), (4, 2)], [(5, 2), (6, 2)], [(7, 2), (8, 2)]], "east")
    # C: 5 x 8, river z 1..6 flowing east; three sections bank to bank on column x=2
    c = scene(look, 5, 8, lambda x, z: 1 <= z <= 6, [[(2, 0), (2, 1)], [(2, 2), (2, 3)], [(2, 4), (2, 5)], [(2, 6), (2, 7)]], "north")
    for k, im in (("A", a), ("B", b), ("C", c)):
        im.save(OUT / f"composite_{look}_scene{k}.png")
    W = a.size[0] + b.size[0] + c.size[0] + 2 * C // 2
    H = max(a.size[1], b.size[1], c.size[1])
    sheet = Image.new("RGBA", (W, H), (40, 40, 40, 255))
    x = 0
    for im in (a, b, c):
        sheet.alpha_composite(im, (x, 0))
        x += im.size[0] + C // 2
    sheet.save(OUT / f"composite_{look}.png")
    print(look, sheet.size)


if __name__ == "__main__":
    for look in (sys.argv[1:] or LOOKS):
        build(look)
