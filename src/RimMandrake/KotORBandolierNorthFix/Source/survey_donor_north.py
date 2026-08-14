#!/usr/bin/env python3
"""
survey_donor_north.py — learn how THIS author draws a bandolier's back view,
before drawing one for the two sets that are missing it.

The two broken sets are bandolier_chewbacca and bandolier_traveler in Star Wars
KotOR Resources and Materials (ws 3254370945, guy762.MM.KotORCore): each ships
east + south for all five body types, and no north and no north mask. 20 files.

The two healthy sets in the same folder — bandolier_double and bandolier_knife —
were drawn by the same artist and DO ship north. They are the specification. This
script does not guess at a recipe; it measures theirs:

  * how close is north to a horizontal MIRROR of south, in silhouette and in RGB
  * which regions survive the front->back transform and which are repainted
  * what the masks do differently between facings

and writes one contact sheet per healthy set so the transform can be SEEN, not
just scored. Art judged only by numbers is art nobody looked at.

Run with the venv that has Pillow — the system python3 has none:
    /home/mandrake/.venvs/art/bin/python survey_donor_north.py
Output: Source/REVIEW_donor_north.png (a run artifact; regenerable, not committed)
"""

import os
import sys

from PIL import Image, ImageDraw

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3254370945/Textures/SWApparel/Accessories")
HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "REVIEW_donor_north.png")

HEALTHY = ["bandolier_double", "bandolier_knife"]
BROKEN = ["bandolier_chewbacca", "bandolier_traveler"]
BODIES = ["Male", "Female", "Thin", "Fat", "Hulk"]
CELL = 160


def path(s, name):
    return os.path.join(DONOR, s, name)


def load(s, name):
    p = path(s, name)
    return Image.open(p).convert("RGBA") if os.path.isfile(p) else None


def alpha_set(im):
    """Coordinates carrying any opacity."""
    w = im.width
    return {(i % w, i // w) for i, p in enumerate(im.getdata()) if p[3] > 0}


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def rgb_diff_frac(a, b):
    """Fraction of jointly-opaque pixels whose RGB differs."""
    both = shared = 0
    for p, q in zip(a.getdata(), b.getdata()):
        if p[3] > 0 and q[3] > 0:
            both += 1
            if p[:3] != q[:3]:
                shared += 1
    return shared / both if both else 0.0


def report():
    """Measure north against mirrored-south on the sets that have both."""
    rows = []
    for s in HEALTHY:
        for body in BODIES:
            north = load(s, f"Apparel_{body}_north.png")
            south = load(s, f"Apparel_{body}_south.png")
            if not north or not south:
                continue
            mirror = south.transpose(Image.FLIP_LEFT_RIGHT)
            sil = 1.0 - jaccard(alpha_set(north), alpha_set(mirror))
            rgb = rgb_diff_frac(north, mirror)
            rows.append((s, body, north.size, sil, rgb))
    print(f"  {'set':<20}{'body':<8}{'canvas':<12}{'silhouette diff':>16}{'RGB diff':>10}")
    for s, body, size, sil, rgb in rows:
        print(f"  {s:<20}{body:<8}{str(size):<12}{sil:>15.1%}{rgb:>10.1%}")
    return rows


def contact_sheet():
    """south | mirrored south | the author's actual north | mask, per healthy set."""
    cols = ["south", "south mirrored", "AUTHOR'S north", "north mask"]
    n_rows = len(HEALTHY) * len(BODIES)
    sheet = Image.new("RGBA", (CELL * len(cols) + 150, CELL * n_rows + 30), (32, 32, 36, 255))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cols):
        d.text((150 + i * CELL + 4, 8), c, fill=(220, 220, 210, 255))

    r = 0
    for s in HEALTHY:
        for body in BODIES:
            south = load(s, f"Apparel_{body}_south.png")
            north = load(s, f"Apparel_{body}_north.png")
            if not south or not north:
                continue
            mask = load(s, f"Apparel_{body}_northm.png")
            y = 30 + r * CELL
            d.text((6, y + CELL // 2), f"{s.split('_')[1]}\n{body}", fill=(200, 200, 190, 255))
            for i, im in enumerate([south, south.transpose(Image.FLIP_LEFT_RIGHT), north, mask]):
                if im is None:
                    d.text((150 + i * CELL + 40, y + CELL // 2), "none", fill=(160, 90, 90, 255))
                    continue
                t = im.copy()
                t.thumbnail((CELL - 8, CELL - 8))
                sheet.alpha_composite(t, (150 + i * CELL + 4, y + 4))
            r += 1
    sheet.save(SHEET)
    print(f"  sheet -> {SHEET}")


def inventory():
    """Confirm what the two broken sets are actually short of, on disk today."""
    for s in BROKEN:
        missing = [f"Apparel_{b}_{k}.png" for b in BODIES for k in ("north", "northm")
                   if not os.path.isfile(path(s, f"Apparel_{b}_{k}.png"))]
        have = load(s, "Apparel_Male_south.png")
        print(f"  {s}: {len(missing)} missing, canvas {have.size if have else '?'}")


def main():
    print("INVENTORY — what is actually absent")
    inventory()
    print("\nTRANSFORM — the author's own north against a mirrored south")
    report()
    print("\nCONTACT SHEET")
    contact_sheet()
    return 0


if __name__ == "__main__":
    sys.exit(main())
