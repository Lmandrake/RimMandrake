#!/usr/bin/env python3
"""Owner live sitting 2026-11-08 12:20 PM ("The modern cable is a bit of a mess"): the Modern power-strip PNGs had a black
cord tail drawn off the bar above each of the four sockets. Every plugged socket then showed our plug decal AND the drawn
tail (a small V at each plug, shot 121528) and every empty one a dead stub of cord going nowhere (121520). He then called the
strip "very low quality (low res)" with "a stubby black wire coming out of it"; the art helper redrew it at 256x128 with no
cord at all (the code draws the feed, ending under the +X end cap).

Checked per PNG (PowerStrip.png, Styles/ExtCord/PowerStrip_Off.png, 256x128 = the old 64x32 x4):
  - nothing opaque outside the bar rect (x 12..231, y 56..99, the old bar x4): no tail above it, none below, no end stub;
  - no dark px in the band just inside the bar's top outline above any socket (rows 58..63, where the tails' stems entered;
    the 2 px outline itself, rows 56..57, is the new art's drawn edge);
  - the four socket faces are still there (instrument sanity: dark px round each socket, the old 8-of-30 density x area);
  - each socket's dark-pixel centroid sits on CordBuilder.StripHeads (read from the C#), so the plugs land on the sockets.
Pure offline PNG measurement. Exit 0 PASS, 1 FAIL.
"""
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack")
PNGS = [os.path.join(TEX, "PowerStrip.png"), os.path.join(TEX, "Styles", "ExtCord", "PowerStrip_Off.png")]
BUILDER = os.path.join(HERE, "Source", "Core", "CordBuilder.cs")
K = 4                                   # scale from the 64x32 art the old rows and columns were measured on
CANVAS = (64 * K, 32 * K)
BAR = (3 * K, 58 * K, 14 * K, 25 * K)   # x0, x1 (exclusive), y0, y1 (exclusive): the bar, x 12..231, y 56..99
STEM_ROWS = range(58, 64)               # just inside the top outline: where a drawn tail's stem would enter
ALPHA = 40
SOCKET_X = [x * K for x in (10, 23, 36, 49)]   # the socket faces' centres on the old 64 px bar, x4
FACE_ROWS, FACE_HALF = range(16 * K, 22 * K), 2 * K   # old rows 16-21, +-2 px, x4
FACE_MIN = round(8 * (2 * FACE_HALF + 1) * len(FACE_ROWS) / (5 * 6))   # the old 8 dark of a 5x6 window, per area
CENTROID_HALF, CENTROID_TOL = 13, 0.015  # px window round each socket; canvas widths (about 4 px)


def dark(c):
    return c[3] >= ALPHA and c[0] + c[1] + c[2] < 150


def strip_heads():
    m = re.search(r"StripHeads\s*=\s*\{([^}]*)\}", open(BUILDER, encoding="utf-8").read())
    return [float(v) for v in m.group(1).split(",")]


def main():
    fails = []
    heads = strip_heads()
    for p in PNGS:
        im = Image.open(p).convert("RGBA")
        px = im.load()
        w, h = im.size
        name = os.path.relpath(p, TEX)
        if (w, h) != CANVAS:
            fails.append(f"{name}: canvas {w}x{h}, expected {CANVAS[0]}x{CANVAS[1]}")
            continue
        x0, x1, y0, y1 = BAR
        outside = sum(1 for y in range(h) for x in range(w) if px[x, y][3] >= ALPHA and not (x0 <= x < x1 and y0 <= y < y1))
        stems = sum(1 for y in STEM_ROWS for sx in SOCKET_X for x in range(sx - 12, sx + 13) if dark(px[x, y]))
        faces = [sum(1 for y in FACE_ROWS for x in range(sx - FACE_HALF, sx + FACE_HALF + 1) if dark(px[x, y])) for sx in SOCKET_X]
        cents = []
        for sx in SOCKET_X:
            pts = [x for y in FACE_ROWS for x in range(sx - CENTROID_HALF, sx + CENTROID_HALF + 1) if dark(px[x, y])]
            cents.append((sum(pts) / len(pts) - w / 2) / w if pts else float("nan"))
        print(f"{name}: opaque outside the bar {outside}, dark stem px above the sockets {stems}, socket-face dark px {faces} "
              f"(min {FACE_MIN}), socket centres {[round(c, 3) for c in cents]} vs StripHeads {heads}")
        if outside:
            fails.append(f"{name}: {outside} opaque px outside the bar (drawn cord tails or an end stub)")
        if stems:
            fails.append(f"{name}: {stems} dark px just inside the bar's top edge above a socket (the tails' stems)")
        if min(faces) < FACE_MIN:
            fails.append(f"{name}: a socket face is missing (dark px per socket {faces})")
        if len(heads) != 4 or any(not abs(c - hx) <= CENTROID_TOL for c, hx in zip(cents, heads)):
            fails.append(f"{name}: socket centres {cents} off CordBuilder.StripHeads {heads} by more than {CENTROID_TOL}")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
