#!/usr/bin/env python3
"""Owner live sitting 2026-11-08 12:20 PM ("The modern cable is a bit of a mess"): the Modern power-strip PNGs had a black
cord tail drawn off the bar above each of the four sockets. Every plugged socket then showed our plug decal AND the drawn
tail (a small V at each plug, shot 121528) and every empty one a dead stub of cord going nowhere (121520).

Checked per PNG (PowerStrip.png, Styles/ExtCord/PowerStrip_Off.png, 64x32): nothing opaque above the bar (rows 0-13),
and no dark cord pixel in the bar's top border (rows 14-15, where the tails entered it); the four socket faces in the
bar (rows 16-21) are still there (instrument sanity: dark pixels round each StripHeads x).
Pure offline PNG measurement. Exit 0 PASS, 1 FAIL.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack")
PNGS = [os.path.join(TEX, "PowerStrip.png"), os.path.join(TEX, "Styles", "ExtCord", "PowerStrip_Off.png")]
ALPHA = 40
SOCKET_X = [10, 23, 36, 49]   # the socket faces' centres (CordBuilder.StripHeads on the 64 px bar)


def dark(c):
    return c[3] >= ALPHA and c[0] + c[1] + c[2] < 150


def main():
    fails = []
    for p in PNGS:
        im = Image.open(p).convert("RGBA")
        px = im.load()
        w, h = im.size
        name = os.path.relpath(p, TEX)
        if (w, h) != (64, 32):
            fails.append(f"{name}: canvas {w}x{h}, expected 64x32")
            continue
        above = sum(1 for y in range(14) for x in range(w) if px[x, y][3] >= ALPHA)
        border = sum(1 for y in (14, 15) for x in range(w) if dark(px[x, y]))
        faces = [sum(1 for y in range(16, 22) for x in range(sx - 2, sx + 3) if dark(px[x, y])) for sx in SOCKET_X]
        print(f"{name}: opaque above the bar {above}, dark in its top border {border}, socket-face dark px {faces}")
        if above:
            fails.append(f"{name}: {above} opaque px above the bar (drawn cord tails)")
        if border:
            fails.append(f"{name}: {border} dark px in the bar's top border (the tails' stems)")
        if min(faces) < 8:
            fails.append(f"{name}: a socket face is missing (dark px per socket {faces})")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
