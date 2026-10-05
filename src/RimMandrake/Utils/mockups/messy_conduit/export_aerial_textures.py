#!/usr/bin/env python3
"""Messy Conduit aerial lines -- PROCEDURAL PLACEHOLDER textures (PIL), matte-black Jawa scrap family.

Placeholders until the artpipe jobs RM_MessyConduit_Jawa_AerialMast / _AerialMastTop / _AerialLampMast /
_WallBracket / _TapClamp finish; the swap is dropping the finished PNGs over these same paths
(src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Aerial/). Spans reuse Strand_Jawa (no new art).

Geometry contract with the C# (Building_AerialAnchor / AerialAnchorExtension, RM_AerialAnchors.xml):
  * AerialMast / AerialLampMast: 128x256 drawn at drawSize (1,2), drawOffset z +0.5 -> the canvas covers the
    anchor cell and the cell above it; the base plate sits in the bottom cell.
  * AerialMastTop: 128x128 drawn at z +1.0 above the cell centre (covers the upper cell) ABOVE pawns; the wire hangs
    from attachZ 1.15 -> 0.65 of the top canvas from its bottom (pixel row ~45 from the top), insulators at
    x = 0.5 +- 0.13 cell (+-17 px) and the centre.
Usage:  export_aerial_textures.py [--out <dir>] [--check]
"""
import argparse
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
OUT = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Textures", "RimMandrake", "GimmeSomeSlack", "Aerial")
SS = 4
SIZES = {"AerialMast.png": (128, 256), "AerialMastTop.png": (128, 128), "AerialLampMast.png": (128, 256),
         "WallBracket.png": (128, 128), "TapClamp.png": (64, 64)}

BLACK = (22, 20, 19, 255)
BLACK_HI = (48, 44, 40, 255)
RUST = (92, 52, 30, 255)
RUST_DK = (60, 36, 22, 255)
TAPE = (110, 84, 44, 255)
GLASS = (72, 92, 58, 235)
GLASS_HI = (120, 140, 96, 235)
CERAMIC = (128, 112, 92, 255)
COPPER = (150, 88, 48, 255)
AMBER = (196, 132, 52, 255)


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def finish(im, w, h, seed):
    im = im.resize((w, h), Image.LANCZOS)
    im.putdata([(r, g, b, a) if a > 8 else (0, 0, 0, 0) for (r, g, b, a) in im.getdata()])
    rnd = random.Random(seed)
    px = im.load()
    for y in range(h):                          # grime: tiny value noise on opaque pixels, never lighter than 60
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0:
                d = rnd.randint(-6, 6)
                px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)), a)
    return im


def S(*v):
    return [c * SS for c in v]


def insulator(d, cx, cy, glass=True):
    c = GLASS if glass else CERAMIC
    d.ellipse(S(cx - 5, cy - 7, cx + 5, cy + 3), fill=c, outline=BLACK)
    d.ellipse(S(cx - 3, cy - 6, cx, cy - 2), fill=GLASS_HI if glass else (150, 136, 116, 255))
    d.rectangle(S(cx - 2, cy + 2, cx + 2, cy + 6), fill=BLACK)


def crossarm(d, w, row):
    d.polygon(S(18, row - 3, w - 18, row - 6, w - 18, row + 1, 18, row + 4), fill=RUST_DK, outline=BLACK)
    d.line(S(22, row, w - 22, row - 3), fill=BLACK_HI, width=SS)
    for x in (34, w - 34):                       # rivets / tape wraps
        d.rectangle(S(x - 2, row - 5, x + 2, row + 3), fill=TAPE)


def pole(d, w, top, bottom):
    cx = w // 2
    # slightly bent scrap pipe: two segments with a welded patch
    d.polygon(S(cx - 6, bottom, cx + 6, bottom, cx + 5, (top + bottom) // 2, cx - 5, (top + bottom) // 2), fill=BLACK)
    d.polygon(S(cx - 5, (top + bottom) // 2, cx + 5, (top + bottom) // 2, cx + 7, top, cx - 3, top), fill=BLACK)
    d.line(S(cx - 2, bottom - 4, cx - 1, top + 4), fill=BLACK_HI, width=SS)
    d.rectangle(S(cx - 7, (top + bottom) // 2 - 4, cx + 7, (top + bottom) // 2 + 4), fill=RUST)
    for y in (bottom - 40, top + 30):
        d.rectangle(S(cx - 7, y - 3, cx + 7, y + 3), fill=TAPE)


def base_plate(d, w, y):
    cx = w // 2
    d.ellipse(S(cx - 26, y - 12, cx + 26, y + 12), fill=(0, 0, 0, 70))
    d.polygon(S(cx - 20, y - 6, cx + 20, y - 6, cx + 24, y + 8, cx - 24, y + 8), fill=RUST_DK, outline=BLACK)
    for x in (cx - 15, cx + 15):
        d.ellipse(S(x - 3, y - 2, x + 3, y + 4), fill=BLACK_HI)


def mast(lamp=False):
    w, h = 128, 256
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    base_plate(d, w, 236)
    pole(d, w, 44, 234)
    crossarm(d, w, 50 + 0)                 # same crossarm as the top canvas (row 50 of the upper cell)
    for x in (47, 64, 81):
        insulator(d, x, 46, glass=(x != 64))
    if lamp:
        d.line(S(64, 90, 98, 76), fill=BLACK, width=5 * SS)
        d.polygon(S(92, 70, 118, 70, 112, 92, 98, 92), fill=BLACK, outline=RUST_DK)
        d.ellipse(S(98, 84, 112, 96), fill=AMBER)
    # a guy-wire stub
    d.line(S(64, 120, 30, 226), fill=(30, 28, 26, 200), width=SS)
    return finish(im, w, h, 11 if not lamp else 12)


def mast_top():
    w, h = 128, 128
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.polygon(S(59, 128, 69, 128, 70, 56, 58, 56), fill=BLACK)     # pole tip continues below
    crossarm(d, w, 50)
    for x in (47, 64, 81):
        insulator(d, x, 46, glass=(x != 64))
        d.line(S(x - 4, 47, x + 4, 47), fill=COPPER, width=SS)       # wire lashing
    return finish(im, w, h, 13)


def wall_bracket():
    w, h = 128, 128
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle(S(40, 96, 88, 120), fill=RUST_DK, outline=BLACK)     # plate bolted to the wall (south = behind)
    for x in (48, 80):
        d.ellipse(S(x - 4, 104, x + 4, 112), fill=BLACK_HI)
    d.polygon(S(58, 100, 70, 100, 70, 52, 58, 52), fill=BLACK)
    d.polygon(S(58, 56, 70, 56, 86, 40, 76, 34), fill=RUST)
    insulator(d, 64, 44, glass=True)
    return finish(im, w, h, 14)


def tap_clamp():
    w, h = 64, 64
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.polygon(S(10, 22, 40, 26, 40, 38, 10, 42), fill=RUST, outline=BLACK)     # jaws
    d.polygon(S(6, 26, 14, 26, 14, 38, 6, 38), fill=COPPER)
    d.polygon(S(38, 24, 58, 18, 60, 26, 40, 34), fill=BLACK)                    # handles
    d.polygon(S(38, 30, 60, 38, 58, 46, 38, 40), fill=BLACK)
    d.rectangle(S(46, 18, 52, 46), fill=TAPE)
    d.line(S(56, 42, 62, 60), fill=BLACK, width=3 * SS)                          # our cord leaves the handle
    return finish(im, w, h, 15)


MAKERS = {"AerialMast.png": lambda: mast(False), "AerialLampMast.png": lambda: mast(True), "AerialMastTop.png": mast_top,
          "WallBracket.png": wall_bracket, "TapClamp.png": tap_clamp}


def check(out):
    bad = []
    for n, (w, h) in SIZES.items():
        p = os.path.join(out, n)
        if not os.path.exists(p):
            bad.append("%s missing" % n)
            continue
        im = Image.open(p)
        if im.mode != "RGBA" or im.size != (w, h):
            bad.append("%s mode %s size %s" % (n, im.mode, im.size))
            continue
        a = im.getchannel("A")
        lo, hi = a.getextrema()
        if lo != 0 or hi < 200:
            bad.append("%s alpha extrema %s (needs real transparency and an opaque body)" % (n, (lo, hi)))
        rgba = im.convert("RGBA")
        if any(max(px[:3]) >= 250 for px in rgba.getdata() if px[3] > 8):
            bad.append("%s contains near-white (Jawa family: no white)" % n)
    for b in bad:
        print("FAIL", b)
    print("aerial textures: %d/%d OK" % (len(SIZES) - len(bad), len(SIZES)))
    return not bad


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if not a.check:
        os.makedirs(a.out, exist_ok=True)
        for n, mk in MAKERS.items():
            mk().save(os.path.join(a.out, n))
    return 0 if check(a.out) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
