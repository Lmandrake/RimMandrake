#!/usr/bin/env python3
"""Show what the ENGINE would draw for a facing we do not author, beside a real one.

The question this answers, and it cannot be answered by reading code: if we ship
south + east and let Vehicles.Graphic_Rgb derive north and west, does the result
look like a vehicle or like a mistake?

Graphic_Rgb.GetTextures, decompiled from Vehicles.dll 2026-08-21:
    north missing -> north = south,  drawRotatedExtraAngleOffset = 180
    west  missing -> west  = east,   westFlipped = DataAllowsFlip
So "derived north" is the south sprite turned 180 degrees, and "derived west" is
the east sprite mirrored. Both are simulated here exactly.

THE DOGSLED IS THE CONTROL. It is the one vehicle for which we authored a real
north, so it is the only place the derived north can be graded against the thing
it would replace. Whatever is true of the sled's derived north is true of the
other four, because the fallback is the same code path.

Row 1 is large, for craft. Row 2 is at sprite size, which is the only size that
decides whether art reads. Checkerboard behind, so transparency is not read as
black.
"""

import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "Textures", "Things", "Vehicles", "Land", "Tier0")
BIG, SMALL, PAD = 232, 96, 16
LABEL = 18


def checker(size, sq=8):
    im = Image.new("RGBA", (size, size), (210, 210, 210, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, size, sq):
        for x in range(0, size, sq):
            if (x // sq + y // sq) % 2:
                d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(170, 170, 170, 255))
    return im


def cell(img, size):
    bg = checker(size)
    bg.alpha_composite(img.resize((size, size), Image.LANCZOS))
    return bg


def main():
    sled = os.path.join(TEX, "DogSled")
    south = Image.open(os.path.join(sled, "AV_DogSled_south.png")).convert("RGBA")
    north = Image.open(os.path.join(sled, "AV_DogSled_north.png")).convert("RGBA")
    east = Image.open(os.path.join(sled, "AV_DogSled_east.png")).convert("RGBA")

    panels = [
        ("south (authored)", south),
        ("north AUTHORED", north),
        ("north DERIVED = south@180", south.rotate(180)),
        ("east (authored)", east),
        ("west DERIVED = east flipped", east.transpose(Image.FLIP_LEFT_RIGHT)),
        # The south-only regime: every mat collapses to south, ShouldDrawRotated is
        # then provably true, and the engine turns the one sprite per facing.
        # ⚠️ CCW, not CW. South leads with the team at the BOTTOM; east must lead with
        # it at the RIGHT, and only rotate(+90) takes bottom to right. The clockwise
        # version renders a west-facing sled and reads as the team pushing backwards.
        ("east DERIVED = south@90", south.rotate(90)),
    ]
    for v in ("OxCart", "CoveredCarriage", "WarChariot"):
        p = os.path.join(TEX, v, "AV_%s_south.png" % v)
        if os.path.exists(p):
            panels.append(("%s south NEW" % v, Image.open(p).convert("RGBA")))

    n = len(panels)
    W = PAD + n * (BIG + PAD)
    H = PAD + LABEL + BIG + PAD + LABEL + SMALL + PAD
    sheet = Image.new("RGBA", (W, H), (28, 28, 30, 255))
    d = ImageDraw.Draw(sheet)

    for i, (name, img) in enumerate(panels):
        x = PAD + i * (BIG + PAD)
        d.text((x, PAD - 2), name, fill=(235, 235, 235, 255))
        sheet.alpha_composite(cell(img, BIG), (x, PAD + LABEL))
        y2 = PAD + LABEL + BIG + PAD
        d.text((x, y2 - 2), "at sprite size", fill=(160, 160, 160, 255))
        sheet.alpha_composite(cell(img, SMALL), (x, y2 + LABEL))

    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "art", "review",
                                                             "derived_facings.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.convert("RGB").save(out)
    print("wrote %s  (%dx%d, %d panels)" % (os.path.normpath(out), W, H, n))

    beast_sheet(os.path.join(os.path.dirname(out), "beast_facings.png"))


# --- the second sheet: what we BUILT, beside the donor it has to sit next to --------

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3028675048/Textures/Things/Vehicles/Land/Tier0")
VEHICLES = ("OxCart", "CoveredCarriage", "WarChariot", "Chariot")


def beast_sheet(out):
    cols = [("donor north", None), ("OURS north", None), ("donor south", None),
            ("OURS south", None), ("donor east", None), ("OURS east", None)]
    W = PAD + len(cols) * (BIG + PAD)
    H = PAD + LABEL + len(VEHICLES) * (LABEL + BIG + PAD)
    sheet = Image.new("RGBA", (W, H), (28, 28, 30, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, _) in enumerate(cols):
        col = (140, 220, 160, 255) if name.startswith("OURS") else (235, 235, 235, 255)
        d.text((PAD + i * (BIG + PAD), PAD - 2), name, fill=col)

    for r, v in enumerate(VEHICLES):
        y = PAD + LABEL + r * (LABEL + BIG + PAD)
        d.text((PAD, y), v, fill=(200, 200, 120, 255))
        imgs = [
            Image.open(os.path.join(DONOR, v, "AV_%s_north.png" % v)).convert("RGBA"),
            Image.open(os.path.join(TEX, v, "AV_%s_north.png" % v)).convert("RGBA"),
            Image.open(os.path.join(DONOR, v, "AV_%s_south.png" % v)).convert("RGBA"),
            Image.open(os.path.join(TEX, v, "AV_%s_south.png" % v)).convert("RGBA"),
            Image.open(os.path.join(DONOR, v, "AV_%s_east.png" % v)).convert("RGBA"),
            Image.open(os.path.join(TEX, v, "AV_%s_east.png" % v)).convert("RGBA"),
        ]
        for i, im in enumerate(imgs):
            sheet.alpha_composite(cell(im, BIG), (PAD + i * (BIG + PAD), y + LABEL))

    sheet.convert("RGB").save(out)
    print("wrote %s  (%dx%d, %d rows)" % (os.path.normpath(out), W, H, len(VEHICLES)))


if __name__ == "__main__":
    main()
