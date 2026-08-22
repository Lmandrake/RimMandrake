#!/usr/bin/env python3
"""Remove the detached black fragments floating around the desertified vehicles.

Written for `VEHICLE_SPRITE_ARTEFACT_CLEANUP_1`.
🔴 OWNER, 2026-08-22: *"Some of them have clearly truncated tails, or hovering black
pixels surrounding them. Clean them up."* This script is the second half. The
truncated tails are a CROP problem in the east builds and are not touched here.

WHAT IT REMOVES, AND WHY THAT IS SAFE
-------------------------------------
Every artefact measured in these sprites is a **detached** run of near-black pixels
sitting in open space beside the animal — leftover outline fragments the chroma-key
cut loose from a foot, a claw or a rein. Measured 2026-08-22 across the 15 art PNGs:

    file                        islands   stray px   largest island   main mass
    Chariot_south                     3        192               96      44,692
    CoveredCarriage_north             4        180               63      63,507
    CoveredCarriage_south             3         75               42      69,454
    OxCart_north                      9        150               26      59,614
    OxCart_south                      5        136               43      56,888
    WarChariot_north                  3        149               77      53,278
    WarChariot_south                  4         76               33      48,048

Every island is **≤ 96 px against a main mass of ≥ 44,692** — three orders of
magnitude apart — and every one measures pure `(0,0,0)` or `(18,18,18)`. The other
eight art PNGs have exactly one connected component and are left untouched.

🔑 THE TWO GUARDS ARE WHAT MAKE THIS A CLEANUP AND NOT A GAMBLE.
An island is removed only if BOTH hold:

  * it is under `MAX_ISLAND_FRAC` of the main mass — so a genuinely detached piece
    of art (a thrown rock, a separate wheel) is never silently deleted; and
  * it is nearly black — mean luminance under `MAX_LUMA` — so a coloured fragment
    of the animal survives even when it is small.

Anything that fails either guard is REPORTED and kept. ⛔ A run that removes
something is not automatically right: look at the before/after sheet.

    python3 despeckle.py            # measure and report, writes nothing
    python3 despeckle.py --apply    # rewrite the PNGs in place
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from collections import deque

try:
    from PIL import Image
    import numpy as np
except ImportError:                                    # pragma: no cover
    sys.exit("needs Pillow and numpy: pip install pillow numpy")

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "Textures", "Things", "Vehicles", "Land", "Tier0")

ALPHA_SOLID = 16        # below this a pixel is transparent for connectivity purposes
MAX_ISLAND_FRAC = 0.01  # an island over 1% of the main mass is ART, not a speck
MAX_LUMA = 40           # mean luminance; the measured artefacts are 0-18


def components(solid) -> list[list[tuple[int, int]]]:
    """8-connected components of a boolean mask, largest first."""
    h, w = solid.shape
    seen = np.zeros_like(solid, dtype=bool)
    out = []
    for y in range(h):
        for x in range(w):
            if solid[y, x] and not seen[y, x]:
                q = deque([(y, x)])
                seen[y, x] = True
                px = []
                while q:
                    cy, cx = q.popleft()
                    px.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and solid[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                q.append((ny, nx))
                out.append(px)
    out.sort(key=len, reverse=True)
    return out


def clean(path: str, apply: bool) -> tuple[int, int, list[str]]:
    """-> (islands removed, pixels removed, lines about anything KEPT)"""
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    comps = components(arr[..., 3] > ALPHA_SOLID)
    if len(comps) < 2:
        return 0, 0, []
    main = len(comps[0])
    removed = pixels = 0
    kept = []
    for c in comps[1:]:
        ys = [p[0] for p in c]
        xs = [p[1] for p in c]
        rgb = arr[ys, xs][:, :3].astype(float)
        luma = float((0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]).mean())
        big = len(c) > main * MAX_ISLAND_FRAC
        pale = luma > MAX_LUMA
        if big or pale:
            kept.append("      KEPT %4d px at y%d-%d x%d-%d luma %.0f  (%s)"
                        % (len(c), min(ys), max(ys), min(xs), max(xs), luma,
                           "over %.0f%% of the main mass" % (MAX_ISLAND_FRAC * 100)
                           if big else "not dark enough to be an artefact"))
            continue
        removed += 1
        pixels += len(c)
        if apply:
            arr[ys, xs] = (0, 0, 0, 0)
    if apply and removed:
        Image.fromarray(arr, "RGBA").save(path)
    return removed, pixels, kept


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="rewrite the PNGs; without it nothing is written")
    args = ap.parse_args()

    files = [f for f in sorted(glob.glob(os.path.join(TEX, "**", "*.png"), recursive=True))
             # ⚠️ `*m.png` is the TINT MASK, not art: it is opaque over the whole
             # canvas by design, so it has exactly one component and nothing to clean.
             if not f.endswith("m.png")]
    if not files:
        sys.exit("no textures under " + os.path.normpath(TEX))

    total_i = total_p = 0
    for f in files:
        n, px, kept = clean(f, args.apply)
        if n or kept:
            print("%-44s %2d island(s), %4d px" % (os.path.basename(f), n, px))
            for line in kept:
                print(line)
        total_i += n
        total_p += px
    verb = "removed" if args.apply else "would remove"
    print("\n%s %d island(s), %d pixel(s), across %d file(s)"
          % (verb, total_i, total_p, len(files)))
    if not args.apply:
        print("nothing was written — re-run with --apply")


if __name__ == "__main__":
    main()
