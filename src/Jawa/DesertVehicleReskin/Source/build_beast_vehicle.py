#!/usr/bin/env python3
"""Composite a generated beast pair into an Alpha Vehicles Neolithic draught vehicle.

Generalises build_eopie_sled_south.py, which is DogSled-only and stays as it is --
it carries sled-specific rigging (trace stubs drawn onto a hitch) that none of the
other four vehicles need, because their reins are already drawn ABOVE the animal
band and survive the erase untouched.

WHAT IT DOES
  1. animal = opaque(art) AND black(mask). The shipped mask is the authority on
     which pixels are draught animal: (255,0,0) tints with the vehicle colour,
     (0,0,0) does not, and only the animals are untinted.
  2. Erase those pixels, but ONLY on rows inside the band. Rows above the band are
     copied verbatim, so the cart, its wheels and its reins register against the new
     art by construction rather than by eye.
  3. Stretch the generated pair to fill the band exactly and composite it in.
  4. Rebuild the mask so the new beast is untinted and everything else is unchanged.

WHY THE BAND IS A TABLE AND NOT COMPUTED
  It was measured per vehicle in Source/GEOMETRY.md section 3, and no single rule
  reproduces all four -- proven 2026-08-21 by trying:
    * a >=18-px-per-row filter gets Chariot and OxCart right and cuts the heads off
      WarChariot, whose necks are thinner than 18 px;
    * a connected-blob filter gets WarChariot and CoveredCarriage right and leaves
      the Chariot's rein attached, overstating its band by 141 rows.
  GEOMETRY.md says "do not re-measure" and it is right. These are its numbers.

WHY STRETCH AND NOT PAD
  A pad preserves the drawing and loses span. An 84%-width pad came out 17% narrow
  and validate_sprite.py rejected it: a variant may lose area but must still span
  its footprint. An 18% stretch on a top-down animal is invisible.
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3028675048/Textures/Things/Vehicles/Land/Tier0")
HERE = os.path.dirname(os.path.abspath(__file__))

# x0, x1, y0, y1 inclusive -- Source/GEOMETRY.md section 3, south facing.
BANDS = {
    ("Chariot", "south"):         (210, 301, 287, 468),
    ("WarChariot", "south"):      (165, 347, 200, 457),
    ("OxCart", "south"):          (155, 356, 282, 430),
    ("CoveredCarriage", "south"): (176, 335, 268, 484),
}

# DECIDE's ruling from measured baseBodySize. The ladder is the point; do not swap
# one beast for another without redoing the whole ladder.
BEASTS = {
    "Chariot":         ("dewback", 1),
    "WarChariot":      ("dewback", 2),
    "OxCart":          ("bantha", 2),
    "CoveredCarriage": ("ronto", 2),
}


def opaque_black(art, mask):
    """The draught animals, and nothing else."""
    return (art[..., 3] > 0) & (mask[..., 0] < 32) & (mask[..., 1] < 32) & (mask[..., 2] < 32)


def trim(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def build(vehicle, facing, pair_path, out_path, out_mask_path):
    band = BANDS.get((vehicle, facing))
    if band is None:
        sys.exit("no band measured for %s %s -- see GEOMETRY.md section 3" % (vehicle, facing))
    x0, x1, y0, y1 = band
    bw, bh = x1 - x0 + 1, y1 - y0 + 1

    src = os.path.join(DONOR, vehicle, "AV_%s_%s.png" % (vehicle, facing))
    srcm = os.path.join(DONOR, vehicle, "AV_%s_%sm.png" % (vehicle, facing))
    art = Image.open(src).convert("RGBA")
    mask = Image.open(srcm).convert("RGBA")
    A, M = np.array(art), np.array(mask)
    H, W = A.shape[:2]

    animal = opaque_black(A, M)
    inband = np.zeros_like(animal)
    inband[y0:y1 + 1, :] = True
    erase = animal & inband
    kept_above = int((animal & ~inband).sum())

    A[erase] = (0, 0, 0, 0)

    pair = trim(Image.open(pair_path).convert("RGBA"))
    pw, ph = pair.size
    # What the width WOULD be if we matched height and kept aspect; the ratio of the
    # band's actual width to that is the distortion we are accepting.
    stretch_w = bw / (pw * bh / ph)
    beast = pair.resize((bw, bh), Image.LANCZOS)
    B = np.array(beast)

    canvas = np.zeros((H, W, 4), np.uint8)
    canvas[y0:y1 + 1, x0:x1 + 1] = B
    new = (canvas[..., 3] > 0)

    # Composite: the beast sits UNDER nothing -- everything above the band was kept,
    # and the band itself is now empty, so a straight paste is exact.
    A[new] = canvas[new]

    # Faint fringe corrupts every later measurement. The validator rejects on it.
    faint = (A[..., 3] > 0) & (A[..., 3] < 32)
    A[faint] = (0, 0, 0, 0)

    M[new] = (0, 0, 0, 255)                    # the new beast does not tint
    M[erase & ~new] = (255, 0, 0, 255)         # anything we emptied tints if refilled

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(A).save(out_path)
    Image.fromarray(M).save(out_mask_path)

    ys, xs = np.nonzero(A[..., 3] > 0)
    print("  %s %s" % (vehicle, facing))
    print("    band       %dx%d at (%d,%d)" % (bw, bh, x0, y0))
    print("    erased     %6d px of donor animal   kept above band: %d" % (int(erase.sum()), kept_above))
    print("    pair       %dx%d -> %dx%d   width stretch %+.1f%%"
          % (pw, ph, bw, bh, (stretch_w - 1) * 100))
    print("    faint      %6d px cleared (alpha 1-31)" % int(faint.sum()))
    print("    subject    bbox (%d,%d,%d,%d)" % (xs.min(), ys.min(), xs.max(), ys.max()))
    print("    wrote      %s" % os.path.normpath(out_path))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("vehicle", choices=sorted(BEASTS))
    p.add_argument("--facing", default="south")
    p.add_argument("--pair")
    p.add_argument("--out")
    a = p.parse_args()

    beast, _n = BEASTS[a.vehicle]
    pair = a.pair or os.path.join(HERE, "art", "%s_pair_gen_%s.png" % (beast, a.facing))
    out = a.out or os.path.join(
        HERE, "..", "Textures", "Things", "Vehicles", "Land", "Tier0",
        a.vehicle, "AV_%s_%s.png" % (a.vehicle, a.facing))
    build(a.vehicle, a.facing, pair, out, out.replace(".png", "m.png"))


if __name__ == "__main__":
    main()
