#!/usr/bin/env python3
"""HOSE_JOIN_REDRAW_STILL_SHOWS_ITS_BORE: repaint each look's Coupling_Bare.png threaded stub so it ends in a flat,
side-on cut (a lying coupling seen from above) instead of the 3/4 "D" face whose dark ellipse is the open bore (art
brief C6). The coupling is ONE sprite rotated to any heading (RM_MapComponent_Hoses.Piece), so a face drawn for the east
heading reads as looking into the pipe once it points south. Deterministic pixel edit of the shipped art: the stub's own
thread columns are tiled out to the original rightmost column (HoseMath.JoinerFace / HO9 geometry unchanged) and the
last column is a dark outline, as the stub's top and bottom edges are.
Usage: flat_face.py OUT_DIR [--src HOSE_TEXTURE_DIR]   writes OUT_DIR/<Look>/Coupling_Bare.png"""
import argparse
from pathlib import Path
from PIL import Image

HOSE = Path(__file__).resolve().parents[2] / "Textures/RimMandrake/FlowWorks/Hose"
# per look: (first stub column with the narrow extent, thread columns [a, b) to tile, thread period); measured on the
# 2026-10-23 shipped art (stub_zoom: the bright rim of the D face starts at b)
LOOKS = {"Scrapper": ("", 114, 110, 116, 3), "Industrial": ("Styles/Industrial", 116, 110, 117, 3),
         "Modern": ("Styles/Modern", 115, 106, 115, 3), "Futuristic": ("Styles/Futuristic", 116, 110, 116, 3)}


def flatten(im, xs, a, b, period):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    right = max(x for x in range(w) if any(px[x, y][3] > 128 for y in range(h)))
    rows = [y for y in range(h) if px[xs, y][3] > 128]
    r0, r1 = rows[0], rows[-1]
    out = im.copy()
    po = out.load()
    for x in range(b, w):
        for y in range(h):
            po[x, y] = (0, 0, 0, 0)
    for x in range(b, right + 1):
        sx = b - period + ((x - b) % period)
        for y in range(r0, r1 + 1):
            r, g, bl, al = px[sx, y]
            if x == right:                      # the cut edge: dark outline like the stub's top/bottom edge
                r, g, bl = int(r * 0.35), int(g * 0.35), int(bl * 0.35)
            elif x == right - 1:                # a faint shade before it so the end reads round, not sliced
                r, g, bl = int(r * 0.8), int(g * 0.8), int(bl * 0.8)
            po[x, y] = (r, g, bl, al)
    for y in (r0, r1):                          # soften the two outer corners
        r, g, bl, al = po[right, y]
        po[right, y] = (r, g, bl, al // 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--src", default=str(HOSE))
    a = ap.parse_args()
    for look, (sub, xs, ta, tb, per) in LOOKS.items():
        src = Path(a.src) / sub / "Coupling_Bare.png"
        dst = Path(a.out) / look / "Coupling_Bare.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        flatten(Image.open(src), xs, ta, tb, per).save(dst)
        print(dst)


if __name__ == "__main__":
    main()
