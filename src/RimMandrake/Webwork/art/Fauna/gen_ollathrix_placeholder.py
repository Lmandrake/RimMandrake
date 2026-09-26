#!/usr/bin/env python3
"""OLLATHRIX_OWNER_SPECIES_1 — flat-colour placeholder art for RM_Ollathrix.

⚠️ THIS IS A PLACEHOLDER AND IS MEANT TO BE REPLACED. It exists so the owner
species does not render magenta and so the def can be loaded/tested, not
because a filled ellipse is shipping-quality RimWorld art. Real art is OWED
— see infrastructure/artpipe/art_lists/webwork_fauna.csv (RM_Ollathrix_v1
row, filed this same pass; 0 hits for "ollathrix" in registry.jsonl at
authoring time, sanity-probed against "graniteslug"/"webwork", 30 hits each,
per confident-wrong-numbers).

Same flat-fill-plus-outline shape as WEBWORK_FAUNA_ROSTER_1's own placeholder
script (gen_webwork_fauna_placeholder.py) — bone-white/dead-silk-cream fill
per the design doc's own palette (§1a: "bone-white to dead-silk cream", no
abdomen marking), a dark blade-edge outline standing in for the leg-blades.
When real art lands, delete this script with the PNG it made.

    python3 src/RimMandrake/Webwork/art/Fauna/gen_ollathrix_placeholder.py
"""

import os

from PIL import Image, ImageDraw

SIZE = 256
TEX_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "Textures", "Things", "Pawn", "Animal",
))

NAME = "RM_Ollathrix"
FILL = (232, 225, 208, 255)      # bone-white / dead-silk cream, no marking
OUTLINE = (70, 62, 48, 255)      # dark blade-edge along the legs
AW, AH = 0.86, 0.50              # low, wide body under many sharp legs


def draw_facing(facing: str) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = SIZE / 2.0
    w = SIZE * AW
    h = SIZE * AH

    if facing == "east":
        w *= 0.82
        cx += SIZE * 0.03
    elif facing == "north":
        h *= 0.9
        cy -= SIZE * 0.02

    # Body: a low, wide ellipse — no abdomen mark of any kind (ban 5).
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    d.ellipse(box, fill=FILL, outline=OUTLINE, width=5)

    # Legs: a fan of thin blade-edged lines under the body, reading "too
    # many sharp legs" at a glance even as a flat placeholder.
    leg_count = 6
    leg_len = min(w, h) * 0.9
    for i in range(leg_count):
        t = (i - (leg_count - 1) / 2.0) / (leg_count / 2.0)
        lx = cx + t * w * 0.55
        ly = cy + h * 0.35
        ex = lx + t * leg_len * 0.6
        ey = ly + leg_len * 0.55
        d.line([(lx, ly), (ex, ey)], fill=OUTLINE, width=4)

    # Head-boss with a pale eye ring, carried low and forward (mouth-loom
    # reads at the front, per the silhouette FORM note).
    head_r = min(w, h) * 0.18
    if facing == "south":
        hx, hy = cx, cy + h / 2 - head_r * 0.5
    elif facing == "north":
        hx, hy = cx, cy - h / 2 + head_r * 0.5
    else:  # east
        hx, hy = cx + w / 2 - head_r * 0.5, cy
    d.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r],
              fill=FILL, outline=OUTLINE, width=3)

    return img


def main() -> None:
    out_dir = os.path.join(TEX_ROOT, NAME)
    os.makedirs(out_dir, exist_ok=True)
    for facing in ("south", "east", "north"):
        path = os.path.join(out_dir, f"{NAME}_{facing}.png")
        draw_facing(facing).save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
