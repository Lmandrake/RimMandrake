#!/usr/bin/env python3
"""
survey_broken_sets.py — look at the two sets that need a north, beside the two
that already have one, all at the same scale.

survey_donor_north.py established the author's transform from his own complete
sets: NORTH IS THE STRAP WITH THE FRONT FURNITURE REMOVED. bandolier_double's
north is a bare X-cross where its south carries pouch blocks along both straps
(silhouette differs 4%, RGB 38% — the outline survives, the detail does not);
bandolier_knife's north is a bare strap and belt where its south carries knife
sheaths (silhouette 23%, because the sheaths break the outline).

What this script answers, which decides how the 20 files get built:
  * does chewbacca / traveler share a strap GEOMETRY with either healthy set?
  * what does each set's mask actually contain, per facing?
If a healthy north's strap already matches, the fix is a recolour of a real
donor asset rather than an invention.

    /home/mandrake/.venvs/art/bin/python survey_broken_sets.py
Output: Source/REVIEW_broken_sets.png (run artifact, regenerable)
"""

import os
import sys

from PIL import Image, ImageDraw

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3254370945/Textures/SWApparel/Accessories")
HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "REVIEW_broken_sets.png")
CELL = 180

SETS = ["bandolier_chewbacca", "bandolier_traveler", "bandolier_knife", "bandolier_double"]
COLS = [("south", "Apparel_Male_south.png"), ("south mask", "Apparel_Male_southm.png"),
        ("east", "Apparel_Male_east.png"), ("north", "Apparel_Male_north.png"),
        ("north mask", "Apparel_Male_northm.png")]


def load(s, name):
    p = os.path.join(DONOR, s, name)
    return Image.open(p).convert("RGBA") if os.path.isfile(p) else None


def describe(im):
    if im is None:
        return "absent"
    a = im.getchannel("A")
    drawn = sum(1 for p in a.getdata() if p > 0)
    cols = {p[:3] for p in im.getdata() if p[3] > 0}
    return (f"{im.size[0]}x{im.size[1]} {drawn:>6} px "
            f"({100*drawn/(im.width*im.height):5.2f}%) bbox {im.getbbox()} "
            f"{len(cols)} colours")


def main():
    for s in SETS:
        print(f"  {s}")
        for label, fn in COLS:
            print(f"      {label:<12} {describe(load(s, fn))}")

    sheet = Image.new("RGBA", (CELL * len(COLS) + 170, CELL * len(SETS) + 30), (32, 32, 36, 255))
    d = ImageDraw.Draw(sheet)
    for i, (label, _) in enumerate(COLS):
        d.text((170 + i * CELL + 4, 8), label, fill=(220, 220, 210, 255))
    for r, s in enumerate(SETS):
        y = 30 + r * CELL
        d.text((6, y + CELL // 2), s.replace("bandolier_", ""), fill=(200, 200, 190, 255))
        for i, (_, fn) in enumerate(COLS):
            im = load(s, fn)
            if im is None:
                d.text((170 + i * CELL + 50, y + CELL // 2), "absent", fill=(190, 90, 90, 255))
                continue
            t = im.copy()
            t.thumbnail((CELL - 8, CELL - 8))
            sheet.alpha_composite(t, (170 + i * CELL + 4, y + 4))
    sheet.save(SHEET)
    print(f"  sheet -> {SHEET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
