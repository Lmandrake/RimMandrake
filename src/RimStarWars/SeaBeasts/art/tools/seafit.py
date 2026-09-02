#!/usr/bin/env python3
"""seafit.py — fit a cut-out creature onto a square RimWorld sprite canvas.

Trims to the visible subject, scales so the LONG axis is FILL x canvas, and
centres it. Every facing of one creature uses the same canvas and the same
FILL, so the animal is ONE size across the whole Graphic_Multi set — that is
the property a per-file validator cannot check and a player sees instantly.

    python3 seafit.py --input cut.png --out Slug_south.png --canvas 512
    python3 seafit.py --input Slug_east.png --out Slug_west.png --canvas 512 --mirror

Exit 0 ok, 1 nothing visible in the input.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/skills/generating-images/scripts")
import pnglib  # noqa: E402

# Bounding box measured at alpha >= 32: a handful of near-invisible stray
# pixels at the frame edge would otherwise decide the scale factor and land the
# sprite undersized (the conform_sprite.py lesson, same number).
BBOX_FLOOR = 32
FILL = 0.85


def bbox(w, h, px, floor=BBOX_FLOOR):
    min_x, min_y, max_x, max_y = w, h, -1, -1
    for y in range(h):
        row = y * w
        for x in range(w):
            if px[(row + x) * 4 + 3] >= floor:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    if max_x < 0:
        return None
    return min_x, min_y, max_x, max_y


def crop(w, h, px, box):
    x0, y0, x1, y1 = box
    cw, ch = x1 - x0 + 1, y1 - y0 + 1
    out = bytearray(cw * ch * 4)
    for y in range(ch):
        s = ((y + y0) * w + x0) * 4
        d = y * cw * 4
        out[d:d + cw * 4] = px[s:s + cw * 4]
    return cw, ch, out


def mirror_h(w, h, px):
    out = bytearray(w * h * 4)
    for y in range(h):
        row = y * w * 4
        for x in range(w):
            s = row + x * 4
            d = row + (w - 1 - x) * 4
            out[d:d + 4] = px[s:s + 4]
    return out


def kill_fringe(px, floor=8):
    """Drop alpha 1..floor-1 to 0. Invisible pixels that corrupt every
    measurement the validator makes, and the one defect it grades hardest."""
    for i in range(3, len(px), 4):
        if 0 < px[i] < floor:
            px[i] = 0
            px[i - 3] = px[i - 2] = px[i - 1] = 0
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--canvas", type=int, required=True)
    ap.add_argument("--fill", type=float, default=FILL)
    ap.add_argument("--mirror", action="store_true")
    a = ap.parse_args()

    w, h, px = pnglib.read_png(a.input)
    box = bbox(w, h, px)
    if box is None:
        print("FAIL %s: no visible subject" % a.input, file=sys.stderr)
        return 1
    cw, ch, cpx = crop(w, h, px, box)

    target = int(round(a.canvas * a.fill))
    if cw >= ch:
        nw = target
        nh = max(1, int(round(ch * target / cw)))
    else:
        nh = target
        nw = max(1, int(round(cw * target / ch)))
    spx = pnglib.resize_rgba(cw, ch, cpx, nw, nh)
    if a.mirror:
        spx = mirror_h(nw, nh, spx)
    spx = kill_fringe(spx)

    n = a.canvas
    canvas = bytearray(n * n * 4)
    ox, oy = (n - nw) // 2, (n - nh) // 2
    for y in range(nh):
        d = ((y + oy) * n + ox) * 4
        s = y * nw * 4
        canvas[d:d + nw * 4] = spx[s:s + nw * 4]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pnglib.write_rgba(a.out, n, n, canvas)
    print("OK   %s  %dx%d canvas, subject %dx%d" % (a.out, n, n, nw, nh))
    return 0


if __name__ == "__main__":
    sys.exit(main())
