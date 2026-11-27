#!/usr/bin/env python3
"""Bake the roofed-grass looks (wilting, withered, dead) as recoloured copies of the living grass sprites.

Why textures and not tints: a plant is drawn with the 'Custom/Plant cutout' shader through Plant.Print, and that path
ignores the material colour. Measured live on ArchSmall, 2026-11-27 (live_small.md, row rgd_3): 96 RM_FE_DeadGrass
(graphicData color 0.62,0.53,0.42) beside 96 ember grass in one frame read bright-pixel mean RGB 135.9,62.9,19.3 against
137.7,63.3,19.3; and a roofed patch with 103 of 188 plants dead and 85 at the withered stage read the same mean RGB as
the healthy patch a day earlier at the same hour (147.1,63.8,16.8 against 147.1,63.4,16.3). A blind judge saw no wilt
and no dead grass. So each look is its own texture, the same shapes in other colours.

Each look keeps the source's file order (Graphic_Random picks variant thingIDNumber % count over files sorted by name),
so a wilting blade is the same tuft it was when healthy. Outputs are siblings with a suffix (RM_FE_EmberGrass_Wilting),
never subfolders: ContentFinder.GetAllInFolder reads a folder's subfolders too.

    python3 src/RimMandrake/Pyrelands/wither_look_gen.py          # write
    python3 src/RimMandrake/Pyrelands/wither_look_gen.py --check  # exit 1 when any output is missing or stale
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures")

# (source graphic path, its dead-grass folder or None). Every graphic path a plant with CompWithersUnderRoof can show
# while alive and not leafless: ember grass (Graphic_Random), quickgrass tall, and quickgrass's staged art
# (PlantGrowthStages in Quickgrass.xml). The leafless art is already a dead look and stays as it is.
SOURCES = [
    ("Things/Plant/RM_FE_EmberGrass", "Things/Plant/RM_FE_DeadGrass"),
    ("Things/Plant/RM_FE_Quickgrass", "Things/Plant/RM_FE_DeadQuickgrass"),
    ("Things/Plant/RM_FE_QuickgrassStages/Half", None),
    ("Things/Plant/RM_FE_QuickgrassStages/Sprout", None),
]

# The looks, as an HSV pull on every opaque pixel: hue toward HUE (degrees) by H_PULL, saturation times S_MUL then capped
# at S_CAP, value times V_MUL. Invented colours (our own rule), judged live by sc_roofed_grass_declines' blind judge:
# wilting is a drying ochre that keeps some colour; withered is a dull brown; dead is a grey straw with no orange left.
LOOKS = {
    "Wilting": dict(HUE=40.0, H_PULL=0.40, S_MUL=0.72, S_CAP=0.70, V_MUL=0.90),
    "Withered": dict(HUE=34.0, H_PULL=0.85, S_MUL=0.40, S_CAP=0.38, V_MUL=0.80),
    "Dead": dict(HUE=30.0, H_PULL=1.00, S_MUL=0.30, S_CAP=0.24, V_MUL=0.62),
}


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-9
    rm = nz & (mx == r)
    gm = nz & (mx == g) & ~rm
    bm = nz & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6.0
    h[gm] = (b - r)[gm] / d[gm] + 2.0
    h[bm] = (r - g)[bm] / d[bm] + 4.0
    h = h * 60.0
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0.0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    c = v * s
    hp = (h % 360.0) / 60.0
    x = c * (1 - np.abs(hp % 2 - 1))
    z = np.zeros_like(h)
    k = np.floor(hp).astype(int) % 6
    r = np.choose(k, [c, x, z, z, x, c])
    g = np.choose(k, [x, c, c, x, z, z])
    b = np.choose(k, [z, z, x, c, c, x])
    m = v - c
    return np.stack([r + m, g + m, b + m], -1)


def recolour(img, look):
    """Pure: an RGBA PIL image in, the look's RGBA PIL image out (alpha untouched)."""
    p = LOOKS[look]
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255.0
    h, s, v = rgb_to_hsv(a[..., :3])
    dh = ((p["HUE"] - h + 180.0) % 360.0) - 180.0
    h2 = h + dh * p["H_PULL"]
    s2 = np.minimum(s * p["S_MUL"], p["S_CAP"])
    v2 = v * p["V_MUL"]
    out = a.copy()
    out[..., :3] = hsv_to_rgb(h2, s2, v2)
    return Image.fromarray(np.clip(np.round(out * 255.0), 0, 255).astype(np.uint8), "RGBA")


def source_files(path):
    d = os.path.join(TEX, path)
    return sorted(f for f in os.listdir(d) if f.lower().endswith(".png") and os.path.isfile(os.path.join(d, f)))


def look_name(fname, look):
    stem = fname[:-4]
    return "%s_%s.png" % (stem, look)


def plan():
    """[(source file, look, output file)] for every look of every source."""
    out = []
    for path, dead in SOURCES:
        for f in source_files(path):
            src = os.path.join(TEX, path, f)
            for look in ("Wilting", "Withered"):
                out.append((src, look, os.path.join(TEX, path + "_" + look, look_name(f, look))))
            if dead:
                out.append((src, "Dead", os.path.join(TEX, dead, look_name(f, "Dead"))))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    bad = 0
    for src, look, dst in plan():
        want = recolour(Image.open(src), look)
        if a.check:
            ok = os.path.exists(dst) and np.array_equal(np.asarray(Image.open(dst).convert("RGBA")), np.asarray(want))
            if not ok:
                bad += 1
                print("STALE or MISSING %s" % os.path.relpath(dst, HERE))
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        want.save(dst, optimize=True)
        print("wrote %s" % os.path.relpath(dst, HERE))
    n = len(plan())
    print("%d outputs, %d stale or missing" % (n, bad) if a.check else "%d outputs written" % n)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
