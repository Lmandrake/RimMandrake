#!/usr/bin/env python3
"""Regenerate the owner's review sheet for all three sled facings.

WHY IT IS A SCRIPT NOW. The first `REVIEW_all_three.png` was assembled by hand,
so re-reviewing after a fix meant rebuilding the layout from memory and the two
sheets did not line up. The owner reviews the same layout twice or the
comparison is worth nothing.

WHAT IT SHOWS, and it differs from the first sheet deliberately:

    LEFT of each pair   the DONOR's sled and its four dogs
    RIGHT of each pair  ours: the eopie team

**Both sides are drawn TINTED, the way RimWorld actually renders them** — the
donor under its own grey (71,71,71) and ours under the harness leather
(99,65,24) that `Patches/DogSledTint_Brown.xml` sets. The first sheet showed raw
PNGs, which is why the sled looked white in review and grey in game. A review
image that is not the rendered image is a trap.

The bottom strip is the same content at true in-game size, because 512 px of
sled is never the decision.

Run:  /home/mandrake/.venvs/art/bin/python Source/review_sheet.py
      (Pillow is not on the system python here; that venv has it.)
"""

import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
OURS = os.path.join(MOD, "Textures/Things/Vehicles/Land/Tier0/DogSled")
DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled")
OUT = os.path.join(HERE, "REVIEW_all_three.png")

FACINGS = ("north", "south", "east")
DONOR_GREY = (71, 71, 71)        # DogSled_VehiclePawn.xml L12, the donor default
OURS_BROWN = (99, 65, 24)        # LEATHER_MID, what our patch sets
TRUE_SCALE = 4                   # 512 -> 128, the strip the owner judges by


def tinted(folder: str, facing: str, colour: tuple) -> Image.Image:
    """Multiply the art by `colour` under the mask's RED region only.

    Red tints with the vehicle colour, black keeps the art's own colours. That
    is the whole reason the animals stay eopie-pink while the sled moves.
    """
    art = Image.open(os.path.join(folder, f"AV_DogSled_{facing}.png")).convert("RGBA")
    mask = Image.open(os.path.join(folder, f"AV_DogSled_{facing}m.png")).convert("RGBA")
    out = Image.new("RGBA", art.size, (0, 0, 0, 0))
    ap, mp, op = art.load(), mask.load(), out.load()
    fr, fg, fb = (c / 255.0 for c in colour)
    for y in range(art.height):
        for x in range(art.width):
            r, g, b, a = ap[x, y]
            if a == 0:
                continue
            mr, mg, mb, _ = mp[x, y]
            if mr > 128 and mg < 128 and mb < 128:
                op[x, y] = (int(r * fr), int(g * fg), int(b * fb), a)
            else:
                op[x, y] = (r, g, b, a)
    return out


def main() -> None:
    cell, pad, head = 512, 14, 34
    panels = []
    for facing in FACINGS:
        panels.append((f"{facing} — donor, 4 dogs", tinted(DONOR, facing, DONOR_GREY)))
        panels.append((f"{facing} — OURS, eopie pair", tinted(OURS, facing, OURS_BROWN)))

    small = cell // TRUE_SCALE
    cols = len(panels)
    w = cols * cell + (cols + 1) * pad
    h = head + cell + pad * 2 + head + small + pad
    sheet = Image.new("RGBA", (w, h), (128, 128, 128, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8),
           "EOPIE DOG SLED — all three facings, drawn AS RENDERED (donor tinted "
           "its grey 71,71,71; ours tinted harness leather 99,65,24). "
           "LEFT of each pair = donor's 4 dogs, RIGHT = our eopie team.",
           fill=(0, 0, 0, 255))

    x = pad
    for label, img in panels:
        sheet.alpha_composite(img, (x, head + pad))
        d.text((x, head + pad - 13), label, fill=(0, 0, 0, 255))
        s = img.resize((small, small), Image.LANCZOS)
        sheet.alpha_composite(s, (x, head + cell + pad * 2 + head))
        x += cell + pad

    d.text((pad, head + cell + pad * 2 + head - 15), "true in-game size:",
           fill=(0, 0, 0, 255))
    sheet.save(OUT)
    print("wrote", OUT, sheet.size)


if __name__ == "__main__":
    main()
