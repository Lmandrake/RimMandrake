#!/usr/bin/env python3
"""
test_mask_recipe.py — before deriving 20 files, prove the recipe on the set the
author already finished.

THE RECIPE, read off the donor's own assets rather than invented:

  The south MASK is the author's own separation of the garment into two parts.
  RimWorld's CutoutComplex shader tints mask-RED by the apparel's stuff colour
  and leaves mask-BLACK alone, and in every one of these sets the red region is
  the leather STRAP and the black regions are the FURNITURE — the pouch blocks
  on bandolier_chewbacca, the knives on bandolier_knife, the buckle on
  bandolier_traveler. The author drew the split; we do not have to guess it.

  His north views are the strap with the furniture gone: bandolier_double's north
  is a bare X-cross where its south carries pouch blocks (silhouette differs 4%
  from a mirrored south, RGB 38%); bandolier_knife's north is a bare strap and
  belt where its south carries three sheathed knives (silhouette 23%).

  So:  north  =  mirror(south)  minus  the pixels the south mask paints BLACK,
                 with the hole refilled from the surrounding strap.

THE TEST. bandolier_knife has BOTH a south+mask and an author-drawn north. Run
the recipe on its south and score the prediction against what he actually drew.
If the recipe reproduces his north, it is his recipe and the 20 derived files
inherit that evidence. If it does not, this script says so and the derivation has
to be done another way.

    /home/mandrake/.venvs/art/bin/python test_mask_recipe.py
Output: Source/REVIEW_recipe_test.png (run artifact, regenerable)
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3254370945/Textures/SWApparel/Accessories")
HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "REVIEW_recipe_test.png")
BODIES = ["Male", "Female", "Thin", "Fat", "Hulk"]


def load(s, name):
    p = os.path.join(DONOR, s, name)
    return Image.open(p).convert("RGBA") if os.path.isfile(p) else None


def furniture_mask(mask_im, art_im):
    """Pixels the mask paints black-ish, i.e. NOT tinted by stuff colour.

    Judged as 'red channel dominates' rather than 'is pure red', because the
    author antialiases the mask edges. Restricted to pixels the art actually
    draws, so the transparent field outside the garment is never 'furniture'.
    """
    m = mask_im.convert("RGB")
    if m.size != art_im.size:
        m = m.resize(art_im.size, Image.NEAREST)
    out = set()
    w = art_im.width
    for i, (mp, ap) in enumerate(zip(m.getdata(), art_im.getdata())):
        if ap[3] == 0:
            continue
        r, g, b = mp
        if r < 128:                      # not tinted -> fixed-colour furniture
            out.add((i % w, i // w))
    return out


def strip_furniture(art, furn):
    """Delete the furniture and let a blurred copy of the strap grow back in.

    A median filter over the surviving strap is enough here: the strap is a
    smooth leather gradient with a black keyline, so the refill only has to be
    locally plausible, and anything it invents sits UNDER the keyline the
    silhouette already carries.
    """
    out = art.copy()
    px = out.load()
    for (x, y) in furn:
        px[x, y] = (0, 0, 0, 0)
    # Grow the strap back over the holes, three passes of median-on-alpha.
    for _ in range(3):
        blurred = out.filter(ImageFilter.MedianFilter(size=5))
        bp, op = blurred.load(), out.load()
        for (x, y) in furn:
            if op[x, y][3] == 0 and bp[x, y][3] > 0:
                op[x, y] = bp[x, y]
    return out


def alpha_set(im):
    w = im.width
    return {(i % w, i // w) for i, p in enumerate(im.getdata()) if p[3] > 0}


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def main():
    rows, cells = [], []
    for body in BODIES:
        south = load("bandolier_knife", f"Apparel_{body}_south.png")
        smask = load("bandolier_knife", f"Apparel_{body}_southm.png")
        truth = load("bandolier_knife", f"Apparel_{body}_north.png")
        if not (south and smask and truth):
            continue
        furn = furniture_mask(smask, south)
        pred = strip_furniture(south, furn).transpose(Image.FLIP_LEFT_RIGHT)

        j_pred = jaccard(alpha_set(pred), alpha_set(truth))
        j_naive = jaccard(alpha_set(south.transpose(Image.FLIP_LEFT_RIGHT)),
                          alpha_set(truth))
        rows.append((body, len(furn), j_naive, j_pred))
        cells.append((body, south, pred, truth))

    print(f"  {'body':<8}{'furniture px':>14}{'mirror only':>14}{'RECIPE':>10}   silhouette agreement with the author's north")
    for body, n, j0, j1 in rows:
        flag = "  BETTER" if j1 > j0 else "  no gain"
        print(f"  {body:<8}{n:>14}{j0:>13.1%}{j1:>10.1%}{flag}")
    if rows:
        m0 = sum(r[2] for r in rows) / len(rows)
        m1 = sum(r[3] for r in rows) / len(rows)
        print(f"\n  mean: mirror-only {m0:.1%} -> recipe {m1:.1%}")
        print("  VERDICT:", "recipe reproduces the author's north"
              if m1 >= 0.85 else "recipe is NOT the author's transform - do not ship it")

    cell = 190
    sheet = Image.new("RGBA", (cell * 3 + 90, cell * len(cells) + 30), (32, 32, 36, 255))
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(["south (input)", "RECIPE predicts", "author's real north"]):
        d.text((90 + i * cell + 4, 8), t, fill=(220, 220, 210, 255))
    for r, (body, a, b, c) in enumerate(cells):
        y = 30 + r * cell
        d.text((6, y + cell // 2), body, fill=(200, 200, 190, 255))
        for i, im in enumerate([a, b, c]):
            t = im.copy()
            t.thumbnail((cell - 8, cell - 8))
            sheet.alpha_composite(t, (90 + i * cell + 4, y + 4))
    sheet.save(SHEET)
    print(f"  sheet -> {SHEET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
