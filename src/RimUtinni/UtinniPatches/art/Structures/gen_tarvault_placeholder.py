#!/usr/bin/env python3
"""SUMP_TAR_VAULT_1 — flat-colour placeholder art for RUT_TarVault (the
building) and RUT_TarRuinedGoods (the failed-extraction stand-in resource).

⚠️ THIS IS A PLACEHOLDER AND IS MEANT TO BE REPLACED. Checked
infrastructure/artpipe/done, _artsrc and registry.jsonl for "tarvault"/
"tar vault"/"larder" first (0 hits) per CLAUDE.md's "check for existing
regenerated art before queuing more" — nothing exists to reuse. Same flat-
fill-plus-outline shape as every other sibling placeholder in this Sump
build wave (gen_webwork_structures_placeholder.py is the direct template).

    python3 src/RimUtinni/UtinniPatches/art/Structures/gen_tarvault_placeholder.py
"""

import os

from PIL import Image, ImageDraw

SIZE = 256
UTINNI_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
))

TAR_BLACK = (28, 24, 20, 255)
TAR_SHEEN = (70, 62, 52, 255)
RACK_BROWN = (92, 66, 42, 255)
OUTLINE = (14, 12, 10, 255)
RUIN_LUMP = (46, 38, 30, 255)
RUIN_HIGHLIGHT = (80, 66, 52, 200)


def draw_tar_vault() -> Image.Image:
    """A sunk barrel-rack: two dark barrel-tops rimmed with a wooden frame,
    a wide black tar sheen filling the gap between them."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    frame = [SIZE * 0.05, SIZE * 0.30, SIZE * 0.95, SIZE * 0.85]
    d.rounded_rectangle(frame, radius=int(SIZE * 0.05), fill=RACK_BROWN, outline=OUTLINE, width=5)

    pool = [SIZE * 0.10, SIZE * 0.36, SIZE * 0.90, SIZE * 0.80]
    d.rounded_rectangle(pool, radius=int(SIZE * 0.04), fill=TAR_BLACK, outline=OUTLINE, width=3)

    # two barrel-top ellipses breaking the surface, rimmed in a lighter sheen
    for cx in (SIZE * 0.32, SIZE * 0.68):
        r = SIZE * 0.13
        cy = SIZE * 0.58
        d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=TAR_SHEEN, outline=OUTLINE, width=3)

    return img


def draw_ruined_goods() -> Image.Image:
    """A single fused black lump — the failed extraction's own stand-in,
    same Graphic_StackCount shape as every other loose resource icon."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = SIZE * 0.22
    box = [pad, pad, SIZE - pad, SIZE - pad]
    d.ellipse(box, fill=RUIN_LUMP, outline=OUTLINE, width=5)

    hi = [pad + SIZE * 0.10, pad + SIZE * 0.08, SIZE * 0.55, SIZE * 0.45]
    d.ellipse(hi, fill=RUIN_HIGHLIGHT)

    return img


def main() -> None:
    vault_dir = os.path.join(UTINNI_ROOT, "Textures", "Things", "Building", "RUT_TarVault")
    goods_dir = os.path.join(UTINNI_ROOT, "Textures", "Things", "Item", "Resource", "RUT_TarRuinedGoods")
    os.makedirs(vault_dir, exist_ok=True)
    os.makedirs(goods_dir, exist_ok=True)

    vault_path = os.path.join(vault_dir, "RUT_TarVault.png")
    draw_tar_vault().save(vault_path)
    print("wrote", vault_path)

    goods_path = os.path.join(goods_dir, "RUT_TarRuinedGoods.png")
    draw_ruined_goods().save(goods_path)
    print("wrote", goods_path)


if __name__ == "__main__":
    main()
