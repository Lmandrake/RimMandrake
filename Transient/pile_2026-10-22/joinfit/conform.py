#!/usr/bin/env python3
"""PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID: artpipe masters joinfitraw_<piece>_<look>_v1 (1024) -> game candidates on the quads
RM_LiquidJoins draws (LiquidJoinRule, unchanged): Flange and Coupler 128x128 = 0.5 cell (256 px/cell), Saddle 256x256 = 1 cell.
The masters draw collars 1.6-2x the pipe (not the 1.3x asked), so scaling the stub to the pipe's 0.102 cell put the collars at
0.18-0.21. Instead each piece is cropped to its COLLAR (columns standing taller than 1.2x the stub band, a 4% margin, no stub:
each side) and the collar's height is scaled to the joints study's size: flange 0.13 cell, coupler (union) 0.12, saddle 0.24.
The pipe atlas (0.102 cell) draws the pipe itself up to and under the collar.
  Flange : flush with the canvas RIGHT edge (its face on the shared cell edge), vertically centred.
  Coupler: centred (drawn centred on the edge two machines/tanks share; rot 0 joins left-right).
  Saddle : centred on the cell, pipe east-west through the middle.
    python3 conform.py   -> cand/<Look>_<Piece>.png + sizes.json
"""
import glob, json, os
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
SRC = "/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
CANVAS = {"Flange": 128, "Coupler": 128, "Saddle": 256}
PX_PER_CELL = 256
TARGET = {"Flange": 0.13, "Coupler": 0.12, "Saddle": 0.24}   # collar height, cells (joints_study.md D4)


def trim(im):
    return im.crop(im.split()[3].point(lambda v: 255 if v > 24 else 0).getbbox())


def band(t):
    a = t.split()[3]
    x = max(2, round(t.width * 0.03))
    rows = [y for y in range(t.height) if a.getpixel((x, y)) > 128]
    return rows[-1] - rows[0] + 1, (rows[0] + rows[-1]) / 2


def fit(im, w, h):
    return im.convert("RGBa").resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS).convert("RGBA")


def clean(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3] < 8:
                px[x, y] = (0, 0, 0, 0)
    return im


def collar(t, b):
    """Columns taller than 1.2x the stub band, widened by 4% of the band each side (anti-alias room; the atlas draws the pipe); -> the cropped image."""
    a = t.split()[3]
    tall = [x for x in range(t.width) if sum(1 for y in range(0, t.height, 2) if a.getpixel((x, y)) > 128) * 2 > 1.2 * b]
    m = round(0.04 * b)
    return t.crop((max(0, tall[0] - m), 0, min(t.width, tall[-1] + 1 + m), t.height))


def conform(piece, src, out):
    t = trim(Image.open(src).convert("RGBA"))
    b, mid = band(t)
    t = collar(t, b)
    k = TARGET[piece] * PX_PER_CELL / t.height
    s = fit(t, t.width * k, t.height * k)
    n = CANVAS[piece]
    c = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    y = round(n / 2 - mid * k)                      # the pipe's centreline on the canvas centreline
    x = n - s.width if piece == "Flange" else round((n - s.width) / 2)
    c.alpha_composite(s, (x, y))
    clean(c).save(out)
    bb = c.split()[3].getbbox()
    return {"master_pipe_band_px": b, "stub_girth_cells": round(b * k / PX_PER_CELL, 3), "scale": round(k, 4), "piece_w_cells": round((bb[2] - bb[0]) / PX_PER_CELL, 3),
            "piece_h_cells": round((bb[3] - bb[1]) / PX_PER_CELL, 3), "bbox": bb, "canvas": n}


if __name__ == "__main__":
    os.makedirs(os.path.join(H, "cand"), exist_ok=True)
    sizes = {}
    for piece in CANVAS:
        for look in LOOKS:
            for ver in ("v1", "v2"):
                job = f"joinfitraw_{piece.lower()}_{look.lower()}_{ver}"
                src = os.path.join(SRC, job, job + ".png")
                name = f"{look}_{piece}" + ("" if ver == "v1" else "_v2")
                if os.path.exists(src):
                    sizes[name] = conform(piece, src, os.path.join(H, "cand", name + ".png"))
    json.dump(sizes, open(os.path.join(H, "sizes.json"), "w"), indent=1)
    for k, v in sizes.items():
        print(k, v["piece_w_cells"], "x", v["piece_h_cells"], "cells; stub girth", v["stub_girth_cells"])
