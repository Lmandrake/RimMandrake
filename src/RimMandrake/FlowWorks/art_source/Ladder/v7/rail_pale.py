#!/usr/bin/env python3
"""Wooden rail ladder (RM_Ladder / RM_LadderRaised) retextured in the ground ladder's pale wood (RAIL_LADDER_REDRAW_FAT_RUNG_FENCE).

Owner 2026-10-24, on the v5 wood rail ladder: "Wood railing: Not bad, but it needs to be thicker because it's wood.
Perspectives are all good though, nice job." Then, on SHEET_ladder_portable.png: "Not the yellower wood option. That's
depricated. The paler ladder is much better and is thick enough." So: v5's approved geometry (art_source/Ladder/v5/draw.py
with the WOOD heft set -- every facing, offset, raise and perspective unchanged) and only the colour of the timber changed to
the pale weathered wood of RM_LadderPortableFlat. The yellow v5 wood (owner/wood.png, wood_v2.png) is never installed.

Retexture = a quantile map: each timber pixel (v5's warm pixels, grain included) keeps its brightness RANK among the
timber pixels and takes the ground ladder's wood colour at that rank (a 256-step ramp of the ground sprite's opaque wood,
iron plates left out). Shading, grain and highlights therefore keep their places; the palette and contrast become the
ground ladder's. Iron (hooks, brackets, bolts, clips, rails' anchor plates) is untouched. v5's warm dark outline becomes
the ground sprite's own dark edge colour (OUTLINE_PCT percentile of its wood).

    python3 rail_pale.py [out_dir]       # writes RM_Ladder_{n,e,s,w}.png + RM_LadderRaised_{n,e,s,w}.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent

def _load_v5():
    """v5/draw.py by path: it imports v4's module under the name `draw` itself, so it cannot be imported as `draw`."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ladder_v5_draw", HERE.parent / "v5" / "draw.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v5 = _load_v5()

FW = HERE.parents[2]
FLAT = FW / "Textures/Things/Building/FlowWorks/Canals/RM_LadderPortableFlat.png"
OUT = HERE / "out"
LUMA = np.array([0.299, 0.587, 0.114])
WARM_MIN = 8          # r - b above this: ground-ladder WOOD (its iron plates are r ~ b grey)
OUTLINE_PCT = 2       # the ground wood's dark edge colour
FACINGS = ("north", "east", "south", "west")


def ground_wood():
    """(N,3) float RGB of the ground ladder's opaque wood pixels (alpha >= 250, warm: iron plates excluded)."""
    a = np.asarray(Image.open(FLAT).convert("RGBA"), dtype=np.float64)
    p = a[a[..., 3] >= 250][:, :3]
    return p[(p[:, 0] - p[:, 2]) > WARM_MIN]


def ramp(n=256):
    """n colours of the ground wood, sorted by luma: ramp[i] = mean colour of the i-th luma quantile bin."""
    p = ground_wood()
    p = p[np.argsort(p @ LUMA, kind="stable")]
    return np.array([c.mean(0) for c in np.array_split(p, n)])


def timber_mask(a):
    """v5's timber pixels: warm (r - b > 30, as v5.wood_grain) and visible. v5's OUTL (34,20,10) is r - b 24: not timber."""
    return ((a[..., 0] - a[..., 2]) > 30) & (a[..., 3] > 0)


def outline_mask(a):
    o = np.array(v5.WOOD["OUTL"][:3], dtype=np.float64)
    return (np.abs(a[..., :3] - o).max(-1) <= 18) & (a[..., 3] > 0) & ~timber_mask(a)


def retexture(im, rp=None):
    rp = ramp() if rp is None else rp
    a = np.asarray(im.convert("RGBA"), dtype=np.float64).copy()
    t, o = timber_mask(a), outline_mask(a)  # both from v5's colours, before any write (the pale ramp's darkest
    lum = a[..., :3][t] @ LUMA
    rank = np.argsort(np.argsort(lum, kind="stable"), kind="stable") / max(len(lum) - 1, 1)
    a[..., :3][t] = rp[np.minimum((rank * len(rp)).astype(int), len(rp) - 1)]
    a[..., :3][o] = _dark_edge()  # ... shades sit within 18 of OUTL and would be flattened as outline)
    return Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8), "RGBA")


def _dark_edge():
    p = ground_wood()
    l = p @ LUMA
    return p[l <= np.percentile(l, OUTLINE_PCT)].mean(0)


def build(out_dir=OUT):
    """{name: image} for all 8 facings; written to out_dir unless it is None."""
    rp, made = ramp(), {}
    for raised, tag in ((False, "RM_Ladder"), (True, "RM_LadderRaised")):
        north = v5.rail_north(v5.WOOD, raised)
        east = v5.rail_east(v5.WOOD, raised)
        south = v5.rail_south(v5.WOOD, raised)
        for f, im in (("north", north), ("east", east), ("south", south)):
            made["%s_%s" % (tag, f)] = retexture(im, rp)
        made[tag + "_west"] = made[tag + "_east"].transpose(Image.FLIP_LEFT_RIGHT)
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        for k, im in made.items():
            im.save(out_dir / (k + ".png"))
    return made


if __name__ == "__main__":
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    for k, im in build(d).items():
        print(k, im.getchannel("A").getbbox())
