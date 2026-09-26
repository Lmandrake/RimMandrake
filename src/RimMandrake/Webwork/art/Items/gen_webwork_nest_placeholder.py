#!/usr/bin/env python3
"""WEBWORK_NEST_EGG_ECONOMY_1 — flat-colour placeholder art for the nest's
new Things: RM_OllathrixEgg (item icon) and RM_Webwork_NestWall (building).

⚠️ THESE ARE PLACEHOLDERS AND ARE MEANT TO BE REPLACED. They exist so the
defs do not render magenta and can be loaded/tested, not because a filled
ellipse is shipping-quality RimWorld art. Real art is OWED — see
infrastructure/artpipe/art_lists/webwork_nest.csv (0 hits for
"ollathrix"/"clutch"/"nestwall" in registry.jsonl at authoring time, 6594
lines, sanity-probed against "webwork", 36 hits — see confident-wrong-numbers
skill). RM_Webwork_EggClutch reuses the vanilla RockFlecked_Atlas texture
directly (ShokkweaveHarvestNodes.xml's own precedent for a mineable vein) and
needs no new art here.

Same flat-fill-plus-outline shape as OLLATHRIX_OWNER_SPECIES_1's own
gen_ollathrix_placeholder.py — bone-white/dead-silk-cream fill, dark
blade-edge outline. When real art lands, delete this script with the PNGs it
made.

    python3 src/RimMandrake/Webwork/art/Items/gen_webwork_nest_placeholder.py
"""

import os

from PIL import Image, ImageDraw

FILL = (232, 225, 208, 255)      # bone-white / dead-silk cream
OUTLINE = (70, 62, 48, 255)      # dark blade-edge


def _tex_root(*parts: str) -> str:
    return os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..",
        "Textures", *parts,
    ))


def draw_egg() -> Image.Image:
    """A single leathery egg — item icon, Graphic_Single, no facings."""
    size = 128
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size / 2.0, size / 2.0
    w, h = size * 0.62, size * 0.82
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    d.ellipse(box, fill=FILL, outline=OUTLINE, width=4)
    # a couple of faint silk-dust flecks, not an abdomen-style marking
    for dx, dy, r in ((-0.12, -0.18, 4), (0.10, 0.05, 3), (-0.05, 0.22, 3)):
        fx, fy = cx + dx * w, cy + dy * h
        d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=OUTLINE)
    return img


def draw_nest_wall() -> Image.Image:
    """A packed silk-and-hide wall — building icon, Graphic_Single."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size / 2.0, size / 2.0
    w, h = size * 0.9, size * 0.7
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    d.rounded_rectangle(box, radius=24, fill=FILL, outline=OUTLINE, width=6)
    # a few woven cross-strands to read as silk-packed, not a plain slab
    for i in range(4):
        y = box[1] + (i + 1) * h / 5.0
        d.line([(box[0] + 8, y), (box[2] - 8, y)], fill=OUTLINE, width=3)
    return img


def main() -> None:
    egg_dir = _tex_root("Things", "Item", "Resource", "RM_OllathrixEgg")
    os.makedirs(egg_dir, exist_ok=True)
    egg_path = os.path.join(egg_dir, "RM_OllathrixEgg.png")
    draw_egg().save(egg_path)
    print("wrote", egg_path)

    wall_dir = _tex_root("Things", "Building", "Natural", "RM_Webwork_NestWall")
    os.makedirs(wall_dir, exist_ok=True)
    wall_path = os.path.join(wall_dir, "RM_Webwork_NestWall.png")
    draw_nest_wall().save(wall_path)
    print("wrote", wall_path)


if __name__ == "__main__":
    main()
