#!/usr/bin/env python3
"""
make_bark_female_wide_east.py — supply BarkSkinFemale_Wide_Normal_east.png for
Vanilla Races Expanded - Phytokin (ws 2927323805, vanillaracesexpanded.phytokin).

NO ART IS DRAWN HERE. The missing file already exists in the donor's own folder
under the wrong name: "BarkSkin_Wide_Normal_east copy.png". The artist saved the
FEMALE Wide east over the male's filename with " copy" appended, and the game
therefore never finds it.

This script does not take that on trust. It proves the claim from the donor's own
pixels before copying a single byte, using the four head sets that DO ship both
genders as controls:

    Average, ElongatedHead, Gaunt, Narrow  ->  male east + female east both present
    Wide                                   ->  male east + a mystery " copy"

The male->female edit in this mod is a fixed, RGB-only retouch in the lip region:
the alpha channels are identical, so the silhouettes match exactly and only a
small cluster of colour pixels moves. If " copy" is the female Wide east, then
its difference from the male Wide east must land in the SAME place, and with the
same footprint, as the male->female difference in every control set.

Run with the venv that has Pillow — the system python3 has none:
    /home/mandrake/.venvs/art/bin/python make_bark_female_wide_east.py
"""

import hashlib
import os
import shutil
import sys

from PIL import Image

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "2927323805/Textures/Things/Pawn/Humanlike/Heads")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE),
                       "Textures", "Things", "Pawn", "Humanlike", "Heads")
OUT = os.path.join(OUT_DIR, "BarkSkinFemale_Wide_Normal_east.png")

CONTROLS = ["Average_Normal", "ElongatedHead", "Gaunt_Normal", "Narrow_Normal"]
SUSPECT = "BarkSkin_Wide_Normal_east copy.png"


def load(name):
    return Image.open(os.path.join(DONOR, name)).convert("RGBA")


def diff_pixels(a, b):
    """Coordinates where two same-size images differ at all."""
    if a.size != b.size:
        sys.exit(f"size mismatch: {a.size} vs {b.size}")
    w = a.width
    pa, pb = list(a.getdata()), list(b.getdata())
    return {(i % w, i // w) for i, (x, y) in enumerate(zip(pa, pb)) if x != y}


def bbox(coords):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return (min(xs), min(ys), max(xs), max(ys))


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def main():
    male_wide = load("BarkSkin_Wide_Normal_east.png")
    suspect = load(SUSPECT)

    checks, notes = [], []

    # --- 1. It is a different file at all. A byte-identical "copy" would be an
    #        ordinary duplicate and would prove nothing.
    md5 = lambda n: hashlib.md5(open(os.path.join(DONOR, n), "rb").read()).hexdigest()
    m_a, m_b = md5("BarkSkin_Wide_Normal_east.png"), md5(SUSPECT)
    checks.append(("suspect differs from male Wide east", m_a != m_b,
                   f"{m_a[:8]}… vs {m_b[:8]}…"))

    # --- 2. The retouch is RGB-only in every control set, so silhouettes must be
    #        identical. If alpha moved, this is a different pose, not a gender edit.
    alpha_moved = any(p[3] != q[3] for p, q in zip(male_wide.getdata(), suspect.getdata()))
    checks.append(("silhouette identical (alpha untouched)", not alpha_moved,
                   "no alpha delta" if not alpha_moved else "ALPHA CHANGED"))

    # --- 3. The decisive test: does the suspect's delta from the male land where
    #        the male->female delta lands in the sets that ship both?
    suspect_delta = diff_pixels(male_wide, suspect)
    checks.append(("suspect delta is a small local cluster", 0 < len(suspect_delta) < 400,
                   f"{len(suspect_delta)} px, bbox {bbox(suspect_delta)}"))

    overlaps = []
    for c in CONTROLS:
        m = load(f"BarkSkin_{c}_east.png")
        f = load(f"BarkSkinFemale_{c}_east.png")
        d = diff_pixels(m, f)
        j = jaccard(suspect_delta, d)
        overlaps.append(j)
        notes.append(f"    control {c:<14} {len(d):>3} px  bbox {bbox(d)}  Jaccard {j:.2f}")

    best = max(overlaps)
    checks.append(("suspect delta co-locates with a known male->female edit", best >= 0.60,
                   f"best Jaccard {best:.2f} across {len(CONTROLS)} controls"))

    # --- 4. Canvas contract, taken from this set's OWN healthy siblings and not
    #        from the file we are about to copy.
    north = load("BarkSkinFemale_Wide_Normal_north.png")
    south = load("BarkSkinFemale_Wide_Normal_south.png")
    checks.append(("canvas matches this set's own north/south",
                   suspect.size == north.size == south.size, f"{suspect.size}"))
    checks.append(("real alpha present",
                   suspect.getchannel("A").getextrema() == (0, 255),
                   f"alpha extrema {suspect.getchannel('A').getextrema()}"))

    ok = all(c[1] for c in checks)
    for name, passed, detail in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}: {detail}")
    for n in notes:
        print(n)

    if not ok:
        print("REJECTED - nothing written")
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(os.path.join(DONOR, SUSPECT), OUT)   # bytes, not a re-encode
    print(f"OK -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
