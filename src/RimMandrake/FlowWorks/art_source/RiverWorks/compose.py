#!/usr/bin/env python3
"""Offline composites of the bank stake line and the silt-trap as their Print overrides lay them out (RIVER_WEIR_ART_JUDGE_
CODEX_SQUINTS fixes 8 and 10). Synthetic ground and river, NOT the game's water shader: the in-game capture is owed.
Layout constants mirror RM_RiverMath.Stake*/SiltWedge* (C#). Scene per look, 128 px/cell, 9 x 6 cells:
  a stake line of five along the bank, turning north for two more (an L), one lone stake, and two silt traps -- one beside
  a south-flowing reach (wedge north of it), one beside an east-flowing reach (wedge west of it).
Writes out/composite_<Look>.png. Usage: compose.py [Look ...]"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
C = 128
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
POST_SIZE, POST_LIFT = 0.8, 0.18          # RM_RiverMath.StakePostSize / StakePostLift
RIDGE_H = (1.0, 0.375)                     # StakeRidgeH (48/128)
RIDGE_V = (0.5, 1.0)                       # StakeRidgeV (64/128)
TRAP_SIZE = 1.2


def ground(w, h, water):
    rng = np.random.default_rng(1)
    img = np.zeros((h * C, w * C, 4), np.uint8)
    for z in range(h):
        for x in range(w):
            y0 = (h - 1 - z) * C
            base = np.array([52, 96, 118]) if water(x, z) else np.array([120, 104, 74])
            noise = rng.integers(-10, 10, (C, C, 1))
            img[y0:y0 + C, x * C:(x + 1) * C, :3] = np.clip(base + noise, 0, 255)
            img[y0:y0 + C, x * C:(x + 1) * C, 3] = 255
    return Image.fromarray(img)


def put(canvas, im, cx, cz, size, h, angle=0.0):
    """Draw im centred at world (cx, cz) cells with size (sx, sz) cells; angle clockwise degrees (Printer_Plane)."""
    sx, sz = size
    im = im.resize((max(1, round(sx * C)), max(1, round(sz * C))), Image.LANCZOS)
    if angle:
        im = im.rotate(-angle, expand=True, resample=Image.BICUBIC)
    px = cx * C - im.size[0] / 2
    py = (h - cz) * C - im.size[1] / 2
    canvas.alpha_composite(im, (round(px), round(py)))


def scene(look):
    w, h = 9, 6
    river = lambda x, z: z <= 1 or (x >= 7 and z <= 4)
    cv = ground(w, h, river)
    d = OUT / look
    post = Image.open(d / "RM_BankStake.png").convert("RGBA")
    rh = Image.open(d / "RM_BankStakeRidge_h.png").convert("RGBA")
    rv = Image.open(d / "RM_BankStakeRidge_v.png").convert("RGBA")
    trap = Image.open(d / "RM_SiltTrap.png").convert("RGBA")
    wedge = Image.open(OUT / "RM_SiltWedge.png").convert("RGBA")
    stakes = {(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (5, 3), (5, 4), (1, 5)}
    # ridges first (a stake owns its east and north spans), then the posts, top row first so nearer posts overlap
    for (x, z) in sorted(stakes):
        if (x + 1, z) in stakes:
            put(cv, rh, x + 1.0, z + 0.5, RIDGE_H, h)
        if (x, z + 1) in stakes:
            put(cv, rv, x + 0.5, z + 1.0, RIDGE_V, h)
    for (x, z) in sorted(stakes, key=lambda c: -c[1]):
        put(cv, post, x + 0.5, z + 0.5 + POST_LIFT, (POST_SIZE, POST_SIZE), h)
    # silt traps: (cell, flow compass index of the nearest current)  0 = east, 6 = south
    for (x, z), flow in (((3, 4), 6), ((6, 4), 0)):
        up = (flow + 4) % 8
        ang = (90 - 45 * up) % 360
        ux, uz = math.cos(math.radians(45 * up)), math.sin(math.radians(45 * up))
        s = 1.0
        put(cv, wedge, x + 0.5 + ux * 0.55 * s, z + 0.5 + uz * 0.55 * s, (1.1 * s, 1.1 * s), h, ang)
        put(cv, trap, x + 0.5, z + 0.5, (TRAP_SIZE, TRAP_SIZE), h)
    cv.save(OUT / f"composite_{look}.png")


if __name__ == "__main__":
    for lk in (sys.argv[1:] or LOOKS):
        scene(lk)
