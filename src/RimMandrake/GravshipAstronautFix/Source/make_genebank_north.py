#!/usr/bin/env python3
"""
make_genebank_north.py — derive GravshipGenebank_north.png for Vanilla Gravship
Expanded (ws 3609835606, packageId vanillaexpanded.gravship).

WHY THIS IS A ROTATION AND NOT A COMMISSION
===========================================
VGE's GravshipGenebank ThingDef (1.6/Mods/Biotech/Defs/ThingDefs_Buildings/
Buildings_Biotech.xml:212-229) declares graphicClass Graphic_Multi, size (1,1),
and inherits GeneBuildingBase, which sets no rotatable / visibleFacing / drawData
anywhere. ThingDef.rotatable defaults true, so all four rotations are placeable.

The donor ships _south and _east only. Because _east EXISTS and differs from the
north mat, Graphic_Multi's ShouldDrawRotated is false, so a north-facing gene bank
draws the SOUTH texture unrotated — its open front pointing at the viewer when it
should be showing its back. Silent: no log line is possible.

Graphic_Multi.Init's own null-north branch substitutes south at
drawRotatedExtraAngleOffset = 180f. That branch is dead here (east is present), so
this script produces the exact bitmap the engine would have produced itself. It is
the engine-sanctioned back view, not an invention.

Run with the venv that has Pillow — the system python3 has none:
    /home/mandrake/.venvs/art/bin/python make_genebank_north.py
"""

import os
import sys

from PIL import Image

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3609835606/Textures/Things/Structures/GravshipGenebank")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE),
                       "Textures", "Things", "Structures", "GravshipGenebank")
OUT = os.path.join(OUT_DIR, "GravshipGenebank_north.png")


def coverage(im):
    a = im.getchannel("A")
    return sum(1 for p in a.getdata() if p > 0) / (im.width * im.height)


def main():
    south = Image.open(os.path.join(DONOR, "GravshipGenebank_south.png")).convert("RGBA")
    east = Image.open(os.path.join(DONOR, "GravshipGenebank_east.png")).convert("RGBA")

    # Canvas contract: take it from the donor's own healthy siblings, never from
    # a number in a doc. Both are 128x128 as of 2026-08-13.
    if south.size != east.size:
        sys.exit(f"donor siblings disagree on canvas: {south.size} vs {east.size}")

    north = south.rotate(180)

    os.makedirs(OUT_DIR, exist_ok=True)
    north.save(OUT)

    # Validate against the donor, not against taste.
    checks = []
    checks.append(("canvas matches donor", north.size == south.size, f"{north.size}"))
    cov_s, cov_n = coverage(south), coverage(north)
    checks.append(("coverage preserved by rotation", abs(cov_s - cov_n) < 1e-9,
                   f"south {cov_s:.4f} / north {cov_n:.4f}"))
    checks.append(("real alpha present", north.getchannel("A").getextrema()[1] == 255,
                   f"max alpha {north.getchannel('A').getextrema()[1]}"))

    # The whole premise: south is NOT 180-symmetric, or this fix would be a no-op.
    diff = sum(1 for p, q in zip(south.getdata(), north.getdata()) if p != q)
    frac = diff / (north.width * north.height)
    checks.append(("differs from south (asymmetry is the premise)", frac > 0.25,
                   f"{frac:.1%} of pixels differ"))

    ok = all(c[1] for c in checks)
    for name, passed, detail in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}: {detail}")
    print(f"{'OK' if ok else 'REJECTED'} -> {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
