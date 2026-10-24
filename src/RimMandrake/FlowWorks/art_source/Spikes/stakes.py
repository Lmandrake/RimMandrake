#!/usr/bin/env python3
"""Stake library for the pit spikes (PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE): writes Source/Superdeep/RM_SpikeStakes.cs.

Owner 2026-10-24: "you can see the spi[k]es aren't right. They should not be showing drawn over the paler walls, right? And
I needed deeper water to test the spikes. They should be shown as submerged rapidly."

The shipped art (Textures/.../Canals/RM_Spikes/RM_Spikes_{a,b,c}.png, owner-accepted 2026-10-21) is a field of separate
stakes drawn over the whole cell at Building altitude, so it covers the pit's far-wall face, side bevels and outline
(RM_ExcavationWalls, TerrainScatter altitude). The fix keeps the owner's stakes but lays them out at draw time
(RM_SpikeDrawMath.Layout) inside the floor the walls leave visible. This script cuts each variant's ISOLATED stakes (an
8-connected alpha component no taller than MAX_STAKE_PX, no wider than MAX_STAKE_W, not cut by the sprite's edge;
overlapping stakes merge into chains and are not used) and bakes them into a per-variant stake ATLAS, one stake per cell
with its neighbours' pixels cleared and GUTTER clear px round it -- a box cut straight from the sprite would carry slivers
of the stakes beside it (review s2c: 13 of 48). It writes the atlases to art_source/Spikes/atlas/ (art.py install copies
them to Textures/<ATLAS_REL>/), the UV library into RM_SpikeStakes.cs, and the variant's density (stakes per cell^2 =
opaque area / mean own-pixel stake area) so the layout keeps the original's look. Units: cells (256 px = 1 cell at
drawSize 1); UV is Unity's (v up).

    python3 stakes.py            # (re)writes atlas/RM_SpikeStakes_<v>.png and RM_SpikeStakes.cs
    python3 stakes.py --check    # exit 1 unless the .cs, atlas/ and the installed atlases are what this script makes and
                                 # every UV box holds exactly one stake (dirty_boxes; the offline selftest runs check())
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from label import components  # noqa: E402

FW = HERE.parents[1]
TEX = FW / "Textures/Things/Building/FlowWorks/Canals/RM_Spikes"
ATLAS_SRC = HERE / "atlas"                                                  # what this script writes (art.py install copies it)
ATLAS_REL = "Things/Building/FlowWorks/Canals/RM_SpikeStakes"               # NOT under RM_Spikes/: Graphic_Random would pick it
ATLAS_TEX = FW / "Textures" / ATLAS_REL
OUT = FW / "Source/Superdeep/RM_SpikeStakes.cs"
VARIANTS = "abc"
MAX_STAKE_PX = 52        # single stakes are 34..47 px tall, merged chains 72 px and up (measured on a, b, c): 52 splits them
MAX_STAKE_W = 16         # single stakes are 6..13 px wide; two side by side would be ~20 px and are not one stake
PAD = 1                  # px of transparent margin kept round each stake inside its UV box
GUTTER = 8               # px of clear alpha between atlas cells, so bilinear + the first mip levels never mix two stakes
ATLAS_W = 256


def atlas_name(variant):
    return "RM_SpikeStakes_%s" % variant


def _cut(variant):
    """The variant's isolated stakes: [(x0, y0, x1, y1, own_alpha_area, rgba_crop)] with each crop's foreign pixels cleared."""
    im = np.asarray(Image.open(TEX / ("RM_Spikes_%s.png" % variant)).convert("RGBA"))
    a = im[..., 3]
    S = a.shape[0]
    lab, bxs = components(a > 0)
    out = []
    for k, (x0, y0, x1, y1) in enumerate(bxs, 1):
        if y1 - y0 + 1 > MAX_STAKE_PX or x1 - x0 + 1 > MAX_STAKE_W:
            continue
        if x0 == 0 or y0 == 0 or x1 == S - 1 or y1 == S - 1:
            continue                                    # cut by the sprite's edge: not a whole stake
        X0, Y0, X1, Y1 = x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD
        crop = im[Y0:Y1 + 1, X0:X1 + 1].copy()
        own = lab[Y0:Y1 + 1, X0:X1 + 1] == k
        crop[..., 3] = np.where(own, crop[..., 3], 0)   # neighbours' pixels inside the box are not this stake
        out.append((X0, Y0, X1, Y1, int(own.sum()), crop))
    assert out, "variant %s: no isolated stake under %d px" % (variant, MAX_STAKE_PX)
    return out, a, S


def atlas(variant):
    """(rgba atlas array, [(w, h, u0, v0, u1, v1)] in cells / Unity UV of the atlas, (pitch_x, pitch_z)). Each stake sits in its
    own cell (4-px aligned for block compression) with GUTTER clear px round it; cells are packed in shelves ATLAS_W wide."""
    cut, a, S = _cut(variant)
    place, x, y, shelf = [], GUTTER, GUTTER, 0
    for (X0, Y0, X1, Y1, _, crop) in cut:
        h, w = crop.shape[:2]
        if x + w + GUTTER > ATLAS_W:
            x, y, shelf = GUTTER, y + shelf + GUTTER, 0
            y = -(-y // 4) * 4
        place.append((x, y))
        shelf = max(shelf, h)
        x = -(-(x + w + GUTTER) // 4) * 4
    H = 1
    while H < y + shelf + GUTTER:
        H *= 2
    img = np.zeros((H, ATLAS_W, 4), np.uint8)
    lib = []
    for (X0, Y0, X1, Y1, _, crop), (px, py) in zip(cut, place):
        h, w = crop.shape[:2]
        img[py:py + h, px:px + w] = crop
        lib.append((w / S, h / S, px / ATLAS_W, 1 - (py + h) / H, (px + w) / ATLAS_W, 1 - py / H))
    ys, xs = np.nonzero(a > 0)
    field = (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)
    per_cell2 = (a > 0).sum() / np.mean([c[4] for c in cut]) / field * S * S
    pitch = 1 / math.sqrt(per_cell2)
    return img, lib, (pitch, pitch)


def library(variant):
    """(stakes, (pitch_x, pitch_z)): stakes = [(w, h, u0, v0, u1, v1)] in cells / Unity UV of the variant's atlas."""
    _, lib, pitch = atlas(variant)
    return lib, pitch


def dirty_boxes(alpha, uvs):
    """How many UV boxes would draw something other than ONE stake: a box (grown by the 1 texel bilinear reads past its edge)
    that touches opaque pixels of more than one 8-connected component, or whose 1-texel ring is not clear. alpha is the
    sampled texture's alpha (row 0 = top), uvs are (u0, v0, u1, v1) Unity UV."""
    H, W = alpha.shape
    lab, _ = components(alpha > 0)
    bad = 0
    for (u0, v0, u1, v1) in uvs:
        x0, x1 = int(round(u0 * W)), int(round(u1 * W))           # texel columns [x0, x1)
        y0, y1 = int(round((1 - v1) * H)), int(round((1 - v0) * H))
        g = lab[max(0, y0 - 1):min(H, y1 + 1), max(0, x0 - 1):min(W, x1 + 1)]
        inner = lab[y0:y1, x0:x1]
        ring = g.copy()
        ring[1:-1, 1:-1] = 0
        if len(set(np.unique(g)) - {0}) != 1 or ring.any() or not inner.any():
            bad += 1
    return bad


def render():
    f = lambda v: "%.6ff" % v
    lines = [
        "// GENERATED by FlowWorks/art_source/Spikes/stakes.py from Textures/Things/Building/FlowWorks/Canals/RM_Spikes/ -- do not",
        "// edit; re-run the script (the offline selftest fails while this file, the atlases and the PNGs disagree).",
        "namespace RimMandrake.FlowWorks",
        "{",
        "\t/// <summary>PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE: each spike variant's isolated stakes as UV boxes in its stake atlas",
        "\t/// (Textures/%s/%s_&lt;v&gt;.png: one clean stake per cell, neighbours' pixels cleared) -- w, h in cells; u0, v0, u1, v1" % (ATLAS_REL, "RM_SpikeStakes"),
        "\t/// Unity UV -- and the grid pitch (cells) that keeps the variant's stake density. Verse-free.</summary>",
        "\tpublic static class RM_SpikeStakes",
        "\t{",
        "\t\tpublic const string Variants = \"%s\";" % VARIANTS,
        "\t\tpublic const string AtlasPath = \"%s/RM_SpikeStakes_\";" % ATLAS_REL,
    ]
    libs, pitches = [], []
    for v in VARIANTS:
        st, (px, pz) = library(v)
        libs.append("\t\t\tnew float[] {\n" + ",\n".join("\t\t\t\t" + ", ".join(f(q) for q in s) for s in st) + " },")
        pitches.append("\t\t\t{ %s, %s }," % (f(px), f(pz)))
    lines += ["\t\tpublic static readonly float[][] Stakes =", "\t\t{"] + libs + ["\t\t};",
              "\t\tpublic static readonly float[,] Pitch =", "\t\t{"] + pitches + ["\t\t};", "\t\tpublic const int Stride = 6;", "\t}", "}", ""]
    return "\n".join(lines)


def _px(path):
    return np.asarray(Image.open(path).convert("RGBA")) if path.exists() else None


def check():
    """[problem] -- empty when the .cs, the atlas sources and the installed atlases are current and every box is one stake."""
    bad = []
    if not OUT.exists() or OUT.read_text() != render():
        bad.append("RM_SpikeStakes.cs is STALE: re-run stakes.py")
    for v in VARIANTS:
        img, lib, _ = atlas(v)
        src, inst = _px(ATLAS_SRC / (atlas_name(v) + ".png")), _px(ATLAS_TEX / (atlas_name(v) + ".png"))
        if src is None or src.shape != img.shape or (src != img).any():
            bad.append("atlas/%s.png is STALE: re-run stakes.py" % atlas_name(v))
        if inst is None or inst.shape != img.shape or (inst != img).any():
            bad.append("Textures/%s/%s.png differs from atlas/: art.py install it" % (ATLAS_REL, atlas_name(v)))
        n = dirty_boxes(img[..., 3], [s[2:] for s in lib])
        if n:
            bad.append("variant %s: %d of %d stake boxes hold more than one stake" % (v, n, len(lib)))
    return bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        bad = check()
        print("\n".join(bad) if bad else "RM_SpikeStakes.cs + stake atlases are current; every box is one stake")
        sys.exit(1 if bad else 0)
    ATLAS_SRC.mkdir(exist_ok=True)
    for v in VARIANTS:
        img, lib, p = atlas(v)
        Image.fromarray(img, "RGBA").save(ATLAS_SRC / (atlas_name(v) + ".png"))
        print(v, len(lib), "stakes, pitch %.3f cell, atlas %dx%d" % (p[0], img.shape[1], img.shape[0]))
    OUT.write_text(render())
