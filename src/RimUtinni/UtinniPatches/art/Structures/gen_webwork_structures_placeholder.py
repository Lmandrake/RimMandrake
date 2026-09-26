#!/usr/bin/env python3
"""WEBWORK_WEB_STRUCTURES_1 — flat-colour placeholder art for the three
web-network structures (RUT_Webwork_Anchor/_Web/_Gutter) that currently ship
a retinted vanilla Hive texture (RUT_WebworkStructures.xml's own header
flags this as owed).

⚠️ THIS IS A PLACEHOLDER AND IS MEANT TO BE REPLACED. It exists so each of
the three reads as its own distinct shape instead of three retinted copies
of Hive, and so the defs can be loaded/tested — not because a filled
polygon is shipping-quality RimWorld art. Real bespoke art is QUEUED —
infrastructure/artpipe/pending/webwork_anchor.json, webwork_web.json,
webwork_gutter.json (webwork_design_render.csv, this same pass; 0 hits for
all three names in registry.jsonl/done/_artsrc at authoring time,
sanity-probed against "gutterplantain" per confident-wrong-numbers — that
hit is an unrelated plant, not this structure).

Same flat-fill-plus-outline shape as the sibling flora/fauna placeholders
(e.g. RM_Fellome_a.png, RM_Vennick_*.png — transparent / fill / outline),
adapted for architecture rather than a creature silhouette: each structure
is non-rotatable and non-directional (Graphic_Single, one file, no facing
suffix), so one canvas per def is enough.

    python3 src/RimUtinni/UtinniPatches/art/Structures/gen_webwork_structures_placeholder.py
"""

import os

from PIL import Image, ImageDraw

SIZE = 256
TEX_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "Textures", "Things", "Building", "Natural",
))

FILL_CREAM = (224, 220, 205, 255)
FILL_SHEET = (235, 230, 218, 235)
FILL_GUTTER = (196, 176, 140, 255)
OUTLINE = (110, 100, 84, 255)
WET_HIGHLIGHT = (150, 190, 200, 200)


def draw_anchor() -> Image.Image:
    """A thick taut catenary line strung corner to corner — architecture,
    not a loose cobweb strand."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = SIZE * 0.14
    p0 = (pad, pad)
    p1 = (SIZE - pad, SIZE - pad)
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + SIZE * 0.05)  # slight sag
    width = int(SIZE * 0.10)
    d.line([p0, mid], fill=FILL_CREAM, width=width, joint="curve")
    d.line([mid, p1], fill=FILL_CREAM, width=width, joint="curve")
    d.line([p0, mid], fill=OUTLINE, width=max(2, width // 6), joint="curve")
    d.line([mid, p1], fill=OUTLINE, width=max(2, width // 6), joint="curve")
    # anchor blobs at both fixed points
    r = SIZE * 0.05
    for p in (p0, p1):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r],
                   fill=FILL_CREAM, outline=OUTLINE, width=3)
    return img


def draw_web() -> Image.Image:
    """A broad, dense, opaque-reading sheet plane filling most of the
    tile — light-blotting, not a wispy lattice."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = SIZE * 0.10
    box = [pad, pad, SIZE - pad, SIZE - pad]
    d.rectangle(box, fill=FILL_SHEET, outline=OUTLINE, width=5)
    # a few structural weave lines so it reads as woven, not a flat card
    for frac in (0.33, 0.66):
        x = pad + (SIZE - 2 * pad) * frac
        d.line([(x, pad), (x, SIZE - pad)], fill=OUTLINE, width=2)
        y = pad + (SIZE - 2 * pad) * frac
        d.line([(pad, y), (SIZE - pad, y)], fill=OUTLINE, width=2)
    return img


def draw_gutter() -> Image.Image:
    """A directional woven trough/channel shape — plumbing, not a flat
    web — with a faint wet sheen down the middle."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = SIZE * 0.30
    bot = SIZE * 0.70
    box = [SIZE * 0.06, top, SIZE * 0.94, bot]
    d.rounded_rectangle(box, radius=int(SIZE * 0.10),
                         fill=FILL_GUTTER, outline=OUTLINE, width=5)
    inner = [SIZE * 0.10, top + (bot - top) * 0.32,
             SIZE * 0.90, top + (bot - top) * 0.68]
    d.rounded_rectangle(inner, radius=int(SIZE * 0.06), fill=WET_HIGHLIGHT)
    return img


STRUCTURES = [
    ("RUT_Webwork_Anchor", draw_anchor),
    ("RUT_Webwork_Web", draw_web),
    ("RUT_Webwork_Gutter", draw_gutter),
]


def main() -> None:
    os.makedirs(TEX_ROOT, exist_ok=True)
    for name, draw_fn in STRUCTURES:
        path = os.path.join(TEX_ROOT, f"{name}.png")
        draw_fn().save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
