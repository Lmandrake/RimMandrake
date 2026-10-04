#!/usr/bin/env python3
"""Hose reel round 4 (owner review 2026-10-04, 16:29): "shouldn't have the little strip of small pale hose left on the
emptied reel after extension". Paints the pale hose out of Reel_Deployed.png - the one wrap left round the drum's
underside (x 122..212, y 148..178 of 256) and the length dropping from it through the base (x 155..179, y 148..213) -
and installs the result through the art ledger.

    python3 src/RimMandrake/Utils/mockups/messy_conduit/reel_round4_art.py [--dry-run] [--out preview.png]

Deterministic: the drum's bare red underside is rebuilt column by column from the drum just above the wrap (a cylinder
reads by rows, so each column's colours are stretched down and shaded darker toward its lower edge, ending on the
drum's own dark rim); under the drum the gap to the base rail is cleared to transparent and the rail is rebuilt from
its own pixels beside the drop (the rail is horizontal: every column of it is alike). Only pale-hose pixels are
touched: a pixel is hose when it is light and low-saturation (the hose is sack cloth, the reel is rusted red).
"""
import argparse
import colorsys
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
TEX = os.path.join(REPO, "src", "RimMandrake", "MessyConduit", "Textures", "RimMandrake", "MessyConduit", "Hose")
DEPLOYED = os.path.join(TEX, "Reel_Deployed.png")

WRAP = (122, 148, 213, 179)      # x0, y0, x1, y1 (exclusive) of the wrap round the drum's underside
DROP = (155, 148, 180, 214)      # the length hanging from it through the base


def is_hose(p):
    r, g, b, a = p
    if a < 40:
        return False
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return v > 0.38 and s < 0.42 and not (r > g * 1.35)          # pale cloth, not rust


def mask(im):
    """The hose by its known geometry (measured on a 5x pixel grid of the round-3 art): the whole wrap box between the
    drum's two flanges, plus the drop box; at the box edges only pixels that read as cloth or as its dark outline."""
    px = im.load()
    m = set()
    for (x0, y0, x1, y1) in (WRAP, DROP):
        for y in range(y0, y1):
            for x in range(x0, x1):
                p = px[x, y]
                if p[3] < 40:
                    continue
                inner = x0 + 4 <= x < x1 - 4 and y < y1 - 1
                if inner or is_hose(p) or max(p[:3]) < 70:
                    m.add((x, y))
    return m


def rebuild(im):
    im = im.convert("RGBA")
    src = im.copy()
    sp, px = src.load(), im.load()
    m = mask(src)
    # 1. the drum underside, column by column: the drum rows above the wrap stretched down, darkened toward the rim
    for x in range(WRAP[0], WRAP[2]):
        col = [y for y in range(WRAP[1], WRAP[3]) if (x, y) in m]
        if not col:
            continue
        top, bottom = min(col), WRAP[3] - 1
        above = [sp[x, y] for y in range(top - 14, top) if sp[x, y][3] > 200 and not is_hose(sp[x, y])]
        if len(above) < 4:
            continue
        span = max(1, bottom - top)
        for y in range(top, bottom + 1):
            t = (y - top) / span
            r, g, b, a = above[min(len(above) - 1, int(t * (len(above) - 1)))]
            k = 1.0 - 0.45 * t * t                                  # a cylinder darkens toward its underside
            if y >= bottom - 1:
                k = 0.28                                            # the drum's dark rim
            px[x, y] = (int(r * k), int(g * k), int(b * k), 255)
    # 2. under the drum: the gap to the base rail is see-through, the rail is copied from beside the drop
    w = DROP[2] - DROP[0]
    for y in range(WRAP[3], DROP[3]):
        for x in range(DROP[0], DROP[2]):
            ref = sp[x - w, y]                                      # the rail one drop-width to the left, texture intact
            px[x, y] = ref if ref[3] > 40 and not is_hose(ref) else (0, 0, 0, 0)
    return im, len(m)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    im, n = rebuild(Image.open(DEPLOYED))
    left = sum(1 for (x0, y0, x1, y1) in (WRAP, DROP) for y in range(y0, y1) for x in range(x0, x1) if is_hose(im.getpixel((x, y))))
    print("hose pixels repainted: %d; pale-hose pixels left in the wrap/drop boxes: %d" % (n, left))
    if a.out:
        im.save(a.out)
    if a.dry_run:
        return 0
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
    import artledger as L
    r = L.install_image(DEPLOYED, im, reason="script:src/RimMandrake/Utils/mockups/messy_conduit/reel_round4_art.py")
    print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
