#!/usr/bin/env python3
"""Render what the in-game tint actually does, so a colour call costs no game load.

RimWorld never shows you AV_DogSled_*.png. It shows that PNG multiplied by the
vehicle's colour wherever the mask is RED, and left alone wherever the mask is
BLACK. So judging the sled's colour from the texture file is judging the wrong
image — the file is near-white and the sled has always rendered grey.

This script does the multiply offline and writes a side-by-side sheet:

    left   the donor's grey  (71, 71, 71)   <- what is on the map today
    right  harness leather   (99, 65, 24)   <- Patches/DogSledTint_Brown.xml

Both strips are also drawn at true in-game size, because 512 px of sled is not
the decision — 44 px of sled is.

Run:  /home/mandrake/.venvs/art/bin/python Source/preview_tint.py
      (Pillow is not on the system python here; that venv has it.)
"""

import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
TEX = os.path.join(MOD, "Textures/Things/Vehicles/Land/Tier0/DogSled")
OUT = os.path.join(HERE, "REVIEW_sled_brown.png")

FACINGS = ("north", "south", "east")

GREY = (71, 71, 71)          # donor default, DogSled_VehiclePawn.xml L12
BROWN = (99, 65, 24)         # LEATHER_MID, the harness colour in the build scripts

# drawSize is (7,7) and RimWorld draws 1 cell at ~64 px on a 512 px canvas that
# covers 8 cells, so the sprite lands at roughly 7/8 of 64 px per cell. The
# strip below is the same 1/8 reduction the earlier REVIEW sheet used.
TRUE_SCALE = 8


def tinted(facing: str, colour: tuple) -> Image.Image:
    """Multiply the art by `colour` under the mask's RED region only."""
    art = Image.open(os.path.join(TEX, f"AV_DogSled_{facing}.png")).convert("RGBA")
    mask = Image.open(os.path.join(TEX, f"AV_DogSled_{facing}m.png")).convert("RGBA")
    if art.size != mask.size:
        raise SystemExit(f"{facing}: art {art.size} != mask {mask.size}")

    out = Image.new("RGBA", art.size, (0, 0, 0, 0))
    ap, mp, op = art.load(), mask.load(), out.load()
    w, h = art.size
    fr, fg, fb = (c / 255.0 for c in colour)
    for y in range(h):
        for x in range(w):
            r, g, b, a = ap[x, y]
            if a == 0:
                continue
            mr, mg, mb, _ = mp[x, y]
            if mr > 128 and mg < 128 and mb < 128:      # RED -> tinted by colour
                op[x, y] = (int(r * fr), int(g * fg), int(b * fb), a)
            else:                                        # BLACK -> untinted
                op[x, y] = (r, g, b, a)
    return out


def main() -> None:
    cell = 512
    pad = 16
    header = 30
    cols = len(FACINGS) * 2
    sheet_w = cols * cell + (cols + 1) * pad
    strip_h = cell // TRUE_SCALE + pad * 2 + header
    sheet = Image.new("RGBA", (sheet_w, header + cell + pad * 2 + strip_h),
                      (128, 128, 128, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), "AV_DogSled tint preview — LEFT of each pair: donor grey "
                     "(71,71,71). RIGHT: harness leather (99,65,24). "
                     "Mask-accurate: the eopie team is black-masked and untinted "
                     "in both.", fill=(0, 0, 0, 255))

    x = pad
    for facing in FACINGS:
        for label, colour in (("grey", GREY), ("brown", BROWN)):
            img = tinted(facing, colour)
            sheet.paste(img, (x, header + pad), img)
            d.text((x, header + pad - 14), f"{facing} — {label}", fill=(0, 0, 0, 255))
            small = img.resize((cell // TRUE_SCALE, cell // TRUE_SCALE),
                               Image.LANCZOS)
            sheet.paste(small, (x, header + cell + pad * 2 + header), small)
            x += cell + pad

    d.text((pad, header + cell + pad * 2 + header - 16),
           "true in-game size:", fill=(0, 0, 0, 255))
    sheet.save(OUT)
    print("wrote", OUT, sheet.size)


if __name__ == "__main__":
    main()
