#!/usr/bin/env python3
"""SHRUBLAND_SCRAPNEST_BIRDS_1 - placeholder art for RSW_ScrapNest.

⚠️ THIS IS A PLACEHOLDER AND IS MEANT TO BE REPLACED. It exists so the nest
does not render magenta and so the def can be tested, not because a procedural
ring of pixels is shipping-quality RimWorld art. Real art is owed; when it
arrives, delete this script with the PNGs it made.

Why it exists at all rather than borrowing a vanilla texture: the obvious
borrow was Core's `Things/Building/Natural/Hive`, which resolves fine in game
but which validate_patch.py escalates to a hard ERROR, because SWBestiary
ships its own `Textures/Things/` root and the validator (correctly, in
general) refuses to distinguish a correct vanilla path from a typo once a mod
claims that namespace. Shipping three real PNGs removes the ambiguity instead
of arguing with the instrument.

Three variants because the def uses Graphic_Random, the same graphicClass
Core's Hive uses - a scatter of nests should not look stamped.

    python3 src/RimStarWars/SWBestiary/art/ScrapNest/gen_scrapnest_placeholder.py
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

SIZE = 128
OUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "Textures", "Things", "Building", "Natural", "ScrapNest",
)

# Dry woven vine: the nest body. Desaturated so the def's own <color> tint
# (a dusty umber) reads, per the same reskin convention the creature defs use.
VINE_DARK = (58, 48, 36)
VINE_MID = (96, 82, 60)
VINE_LIGHT = (134, 118, 88)

# The lining. arid_shrubland.md §4: "wire, lens-glass, chips of hull".
GLITTER = [
    (206, 214, 226),   # lens-glass
    (178, 186, 196),   # stripped wire
    (228, 202, 128),   # a bead of gold
    (150, 156, 164),   # hull flake
    (240, 244, 250),   # highlight
]


def draw_nest(seed: int) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = cy = SIZE / 2.0
    outer = SIZE * 0.42
    inner = SIZE * 0.20

    # Woven body: many short arcs at varying radii, so the rim reads as twigs
    # rather than as a drawn circle.
    for _ in range(260):
        r = rng.uniform(inner * 0.95, outer)
        a0 = rng.uniform(0, math.tau)
        span = rng.uniform(0.25, 0.75)
        squash = rng.uniform(0.82, 0.94)
        wobble = rng.uniform(-2.0, 2.0)
        col = rng.choice([VINE_DARK, VINE_DARK, VINE_MID, VINE_MID, VINE_LIGHT])
        box = [
            cx - r + wobble, cy - r * squash + wobble,
            cx + r + wobble, cy + r * squash + wobble,
        ]
        d.arc(box, math.degrees(a0), math.degrees(a0 + span),
              fill=col + (255,), width=rng.choice([2, 2, 3]))

    # The cup: darker inside, so the nest reads as a bowl seen from above.
    d.ellipse([cx - inner, cy - inner * 0.88, cx + inner, cy + inner * 0.88],
              fill=VINE_DARK + (235,))

    # The lining - the whole point of the thing. Bright flecks pooled in the
    # cup, a few caught in the rim.
    for _ in range(46):
        in_cup = rng.random() < 0.72
        rad = rng.uniform(0, inner * 0.85) if in_cup else rng.uniform(inner, outer * 0.95)
        ang = rng.uniform(0, math.tau)
        px = cx + math.cos(ang) * rad
        py = cy + math.sin(ang) * rad * 0.88
        s = rng.choice([1, 1, 2, 2, 3])
        d.rectangle([px, py, px + s, py + s], fill=rng.choice(GLITTER) + (255,))

    img = img.filter(ImageFilter.SMOOTH)
    return img


def main() -> None:
    out = os.path.normpath(OUT_DIR)
    os.makedirs(out, exist_ok=True)
    for i, suffix in enumerate(("a", "b", "c")):
        path = os.path.join(out, f"ScrapNest_{suffix}.png")
        draw_nest(seed=8100 + i).save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
