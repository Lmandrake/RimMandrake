#!/usr/bin/env python3
"""Uvak flip-book stray-pixel cleanup (UVAK_WINGS_RESKIN_TO_CANON, defect pass 2026-10-20).

Recipe: Uvak_recolour.py SRC(842bca0^) RC Uvak.json -> flyer_cutout.py build Uvak.json --src RC --out OUT
        -> Uvak_cleanup.py OUT   (edits OUT in place; then art.py install).

Two strays come from the soft drop-shadow feather the master painting has round the hip: it falls inside the wing
cut, so a turned wing carries it off the body as a smudge.
  north 1      the hip feather swung out to x 149-172, y 120-142. Every non-plate pixel there is cleared and the
               hip-edge feather of frame 2 (the master pose, scale 0.97) is copied back, so the hip silhouette is
               the same as frames 2 and 4. The right wing in frame 1 ends at y 115: nothing of it is in the box.
  south 2, 4   the feather hanging off the right wing's trailing edge at x 176-185, y 153-166: non-plate pixels
               with alpha < 140 there are cleared (the edge's own anti-aliasing and the finger tip at x >= 186 stay).
Plate (body) pixels are never written: every edit is masked to plate alpha == 0.
The mangled east frame 3 was a pose fix in Uvak.json (sy -0.35 -> 0.25), not a cleanup.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

P = "Uvak_Flying_"


def load(d, n):
    return np.asarray(Image.open(d / f"{P}{n}.png").convert("RGBA")).copy()


def main():
    d = Path(sys.argv[1])
    plate_n = np.asarray(Image.open(d / f"_plate_{P}north.png").convert("RGBA"))
    plate_s = np.asarray(Image.open(d / f"_plate_{P}south.png").convert("RGBA"))

    # north 1
    f1, f2 = load(d, "1_north"), load(d, "2_north")
    ys, xs = slice(120, 143), slice(149, 173)
    free = plate_n[ys, xs, 3] == 0
    box1, box2 = f1[ys, xs], f2[ys, xs]
    before = int((box1[..., 3] > 0)[free].sum())
    box1[free] = 0
    hip = free & (box2[..., 3] > 0)
    hip[:, 4:] = False                      # only the frame-2 hip edge (x 149-152), never its wing
    box1[hip] = box2[hip]
    Image.fromarray(f1, "RGBA").save(d / f"{P}1_north.png")
    print(f"north 1: cleared {before} px, restored {int(hip.sum())} hip-edge px from frame 2")

    # south 2, 4
    ys, xs = slice(153, 167), slice(176, 186)
    for n in (2, 4):
        f = load(d, f"{n}_south")
        b = f[ys, xs]
        m = (b[..., 3] > 0) & (b[..., 3] < 140) & (plate_s[ys, xs, 3] == 0)
        b[m] = 0
        Image.fromarray(f, "RGBA").save(d / f"{P}{n}_south.png")
        print(f"south {n}: cleared {int(m.sum())} px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
