#!/usr/bin/env python3
"""Stake library for the pit spikes (PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE): writes Source/Superdeep/RM_SpikeStakes.cs.

Owner 2026-10-24: "you can see the spi[k]es aren't right. They should not be showing drawn over the paler walls, right? And
I needed deeper water to test the spikes. They should be shown as submerged rapidly."

The shipped art (Textures/.../Canals/RM_Spikes/RM_Spikes_{a,b,c}.png, owner-accepted 2026-10-21) is a field of separate
stakes drawn over the whole cell at Building altitude, so it covers the pit's far-wall face, side bevels and outline
(RM_ExcavationWalls, TerrainScatter altitude). The fix keeps the owner's stakes but lays them out at draw time
(RM_SpikeDrawMath.Layout) inside the floor the walls leave visible.

Owner on that render (b6a4c87772 / 4f12810a3e): "spikes look great!". So the SELECTION, sizes and pitch are that
version's, unchanged (approved/RM_SpikeStakes_4f12810a3e.cs.txt pins them; the selftest compares): every 8-connected
alpha component no taller than MAX_STAKE_PX, its box grown by PAD and clipped to the sprite, the density from the
unpadded boxes' opaque area. The only change is what a box SAMPLES: a box cut straight from the sprite carries slivers
of the stakes beside it (review s2c), so each box's window is copied into its own CELL_W x CELL_H cell of a per-variant
ATLAS with the foreign pixels' alpha cleared and nothing else touched -- centred in a power-of-two cell, no mip level
up to MIP_CHECK mixes two stakes (review s3). The atlases go to art_source/Spikes/atlas/ (art.py install copies them to
Textures/<ATLAS_REL>/), the UV library into RM_SpikeStakes.cs. Units: cells (256 px = 1 cell at drawSize 1); UV is
Unity's (v up).

    python3 stakes.py            # (re)writes atlas/RM_SpikeStakes_<v>.png and RM_SpikeStakes.cs
    python3 stakes.py --check    # exit 1 unless the .cs, atlas/ and the installed atlases are what this script makes and
                                 # every UV box holds exactly one stake (dirty_boxes; the offline selftest runs check())
"""
import functools
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
MAX_STAKE_PX = 52        # the approved selection (4f12810a3e): a single stake is 34..47 px tall, merged chains taller
PAD = 1                  # px of the sprite kept round each component's box (clipped to the sprite), as approved
CELL_W, CELL_H = 64, 128  # one stake per cell, centred: power-of-two cells stay separate in every box-filtered mip level, and
                          # the margins (>= 24 px across, >= 37 px down) cover bilinear's one-texel reach up to mip 5
MIP_CHECK = 5            # dirty_boxes checks mips 0..5; at mip 5 a box (<= 15 px wide, measured) is half a texel
ATLAS_W = 512


def atlas_name(variant):
    return "RM_SpikeStakes_%s" % variant


@functools.lru_cache(maxsize=None)
def _cut(variant):
    """(stakes, pitch, S): stakes = [(X0, Y0, X1, Y1, window, foreign)] -- the approved padded box (inclusive sprite px), the
    sprite's RGBA inside it, and the mask of its pixels that belong to another component (the slivers); pitch in cells; S
    the sprite's size in px."""
    im = np.asarray(Image.open(TEX / ("RM_Spikes_%s.png" % variant)).convert("RGBA"))
    a = im[..., 3]
    S = a.shape[0]
    lab, bxs = components(a > 0)
    out, areas = [], []
    for k, (x0, y0, x1, y1) in enumerate(bxs, 1):
        if y1 - y0 + 1 > MAX_STAKE_PX:
            continue
        areas.append(int((a[y0:y1 + 1, x0:x1 + 1] > 0).sum()))
        X0, Y0, X1, Y1 = max(0, x0 - PAD), max(0, y0 - PAD), min(S - 1, x1 + PAD), min(S - 1, y1 + PAD)
        win = im[Y0:Y1 + 1, X0:X1 + 1].copy()
        l = lab[Y0:Y1 + 1, X0:X1 + 1]
        out.append((X0, Y0, X1, Y1, win, (l != 0) & (l != k)))
    assert areas, "variant %s: no isolated stake under %d px" % (variant, MAX_STAKE_PX)
    ys, xs = np.nonzero(a > 0)
    field = (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)
    per_cell2 = (a > 0).sum() / np.mean(areas) / field * S * S
    return out, 1 / math.sqrt(per_cell2), S


def atlas(variant, cell_w=CELL_W, cell_h=CELL_H, atlas_w=ATLAS_W):
    """(rgba atlas array, [(w, h, u0, v0, u1, v1)] in cells / Unity UV of the atlas, (pitch_x, pitch_z)). Each stake's
    window sits centred in its own cell_w x cell_h cell, cells in rows atlas_w wide, the atlas height a power of two. The
    window is the sprite's pixels with only the foreign pixels' alpha cleared. The cell round the window and the cleared
    slivers carry the stake's mean colour (mips average straight-alpha RGB: no foreign colour leaks in); the window's own
    clear pixels keep the sprite's RGB (black), exactly as the approved render sampled them."""
    cut, pitch, S = _cut(variant)
    cols = atlas_w // cell_w
    H = 1
    while H < -(-len(cut) // cols) * cell_h:
        H *= 2
    img = np.zeros((H, atlas_w, 4), np.uint8)
    lib = []
    for i, (X0, Y0, X1, Y1, win, foreign) in enumerate(cut):
        h, w = win.shape[:2]
        assert w <= cell_w and h <= cell_h, "variant %s: a %dx%d stake does not fit a %dx%d cell" % (variant, w, h, cell_w, cell_h)
        cx, cy = (i % cols) * cell_w, (i // cols) * cell_h
        px, py = cx + (cell_w - w) // 2, cy + (cell_h - h) // 2
        wgt = np.where(foreign, 0, win[..., 3]).astype(np.float64)[..., None]
        mean = np.round((win[..., :3] * wgt).sum((0, 1)) / wgt.sum())
        img[cy:cy + cell_h, cx:cx + cell_w, :3] = mean
        crop = win.copy()
        crop[foreign] = np.append(mean, 0)
        img[py:py + h, px:px + w] = crop
        lib.append((w / S, h / S, px / atlas_w, 1 - (py + h) / H, (px + w) / atlas_w, 1 - py / H))
    return img, lib, (pitch, pitch)


def library(variant):
    """(stakes, (pitch_x, pitch_z)): stakes = [(w, h, u0, v0, u1, v1)] in cells / Unity UV of the variant's atlas."""
    _, lib, pitch = atlas(variant)
    return lib, pitch


def _reach(e0, e1, g, n):
    """Texel indices [lo, hi] a bilinear read at mip texel size g px touches for samples inside the px span [e0, e1]:
    every texel whose centre (i + 0.5) g lies within one texel of the span; clipped to n texels (nothing wraps)."""
    lo = math.floor(e0 / g - 1.5) + 1
    hi = math.ceil(e1 / g + 0.5) - 1
    return max(0, lo), min(n - 1, hi)


def dirty_boxes(alpha, uvs, levels=MIP_CHECK):
    """How many UV boxes would draw something other than ONE 8-connected component (the selection's notion of a stake:
    two touching stakes no taller than MAX_STAKE_PX are one) at some mip level 0..levels: the full-res pixels a
    bilinear read of that level can blend for a sample inside the box (the box grown to whole level texels plus one texel
    of reach) hold opaque pixels of more than one 8-connected component, or the box holds none. alpha is the sampled
    texture's alpha (row 0 = top); uvs are (u0, v0, u1, v1) Unity UV. Box-filtered mips of power-of-two textures keep each
    level texel's footprint the aligned g x g block, so the full-res labels inside those blocks are what it can mix."""
    H, W = alpha.shape
    lab, _ = components(alpha > 0)
    bad = 0
    for (u0, v0, u1, v1) in uvs:
        x0, x1, y0, y1 = u0 * W, u1 * W, (1 - v1) * H, (1 - v0) * H
        inner = lab[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))]
        own = set(np.unique(inner)) - {0}
        ok = len(own) == 1
        for L in range(levels + 1):
            g = 2 ** L
            if not ok or g > min(W, H):
                break
            cx0, cx1 = _reach(x0, x1, g, W // g)
            cy0, cy1 = _reach(y0, y1, g, H // g)
            ok = set(np.unique(lab[cy0 * g:(cy1 + 1) * g, cx0 * g:(cx1 + 1) * g])) - {0} == own
        bad += not ok
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
