#!/usr/bin/env python3
"""Derive a canopy tree's TRUNK and CANOPY pools from its own whole-tree pool (CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD).

    python3 src/RimMandrake/BiomesShell/canopy_art.py <ThingDef defName> [--dry-run] [--sheet <png>]

Reads TREES below: the def's whole-tree Graphic_Random folder, the trunk and canopy folders the def's
RM_CanopyExtension names, and the def's largest visual size. For every variant letter it writes, through
artledger.install_image (reason script:<this file>; never a raw save into Textures):

  * <canopy folder>/<Prefix>Canopy<L>.png: the whole picture at CanopyMath.ArtPxPerCell (32) px per cell of the
    largest visual size (design/RimMandrake/canopy_zoom_investigation_2026-10-18.md §4.3: the canopy is only seen
    at 10 px per cell or less);
  * <trunk folder>/<Prefix>Trunk<L>.png: the same canvas, keeping only the bole and roots. The crown is found
    geometrically (the widest row in the upper 70%, then the first row below it narrower than 35% of that width:
    where the crown gives way to the bole); the bole keeps its own run of pixels and fades out upward over 10% of
    the canvas, so close up it reads as a trunk rising out of view. A colour mask was tried first and cannot work
    (the crown carries grey-green and gold, the bark gold highlights).

These are DERIVED stand-ins built by a script, not painted art: SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT tracks painting them.
The same letters in all three folders keep Graphic_Random's name-sorted variant index identical, so a tree's trunk and
canopy are always halves of one picture.
"""
import argparse
import io
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "Utils", "art"))

REASON = "script:src/RimMandrake/BiomesShell/canopy_art.py"
ART_PX_PER_CELL = 32      # CanopyMath.ArtPxPerCell (RM_Canopy.cs); selftest_canopy.py checks they agree

# defName -> (textures root, whole pool, trunk pool, canopy pool, largest visual size in cells)
TREES = {
    "RM_SweetlineTree": ("src/RimMandrake/LeaningScrub/Textures",
                         "Things/Plant/RM_SweetlineTree", "Things/Plant/RM_SweetlineTrunk",
                         "Things/Plant/RM_SweetlineCanopy", 16.0),
}


def letters(folder, prefix):
    out = []
    for n in sorted(os.listdir(folder)):
        if n.startswith(prefix) and n.endswith(".png"):
            out.append(n[len(prefix):-4])
    return out


def _run_at(row, x, gap_max):
    """The opaque run of `row` containing x (gaps under gap_max px bridged), as (lo, hi)."""
    if not row[x]:
        nz = np.nonzero(row)[0]
        if not len(nz):
            return None
        x = int(nz[np.argmin(abs(nz - x))])
    lo, gap = x, 0
    while lo > 0 and gap < gap_max:
        lo -= 1
        gap = 0 if row[lo] else gap + 1
    hi, gap = x, 0
    while hi < len(row) - 1 and gap < gap_max:
        hi += 1
        gap = 0 if row[hi] else gap + 1
    return lo, hi


def crown_base(alpha):
    """Row index where the crown gives way to the bole."""
    h = alpha.shape[0]
    op = alpha > 0.4
    w = np.zeros(h)
    for y in range(h):
        nz = np.nonzero(op[y])[0]
        w[y] = (nz[-1] - nz[0] + 1) if len(nz) else 0
    top = int(np.argmax(w[:int(h * 0.7)]))
    for y in range(top, h):
        if w[y] < 0.35 * w[top]:
            return y
    return int(h * 0.6)


def trunk_of(rgba):
    """rgba float array (H, W, 4) in 0..1 -> trunk-only copy and the crown-base row."""
    a = rgba[..., 3]
    h, w = a.shape
    op = a > 0.4
    y0 = crown_base(a)
    xs = np.nonzero(op[y0:y0 + max(1, int(h * 0.03))])[1]
    cx = int(xs.mean()) if len(xs) else w // 2
    run = _run_at(op[y0], cx, 6) or (cx - w // 20, cx + w // 20)
    half = (run[1] - run[0]) / 2 * 1.15
    cx = (run[0] + run[1]) / 2
    up, fade, flare = int(h * 0.16), int(h * 0.10), int(h * 0.06)
    xcol = np.arange(w)
    keep = np.zeros_like(a)
    for y in range(max(0, y0 - up), h):
        if y < y0 + flare:
            hw = half if y < y0 else half * (1 + (y - y0) / flare * 0.6)
            m = np.clip(1 - (abs(xcol - cx) - hw) / (w * 0.02), 0, 1)
            if y >= y0:
                r = _run_at(op[y], int(cx), 6)
                rm = np.zeros(w)
                if r:
                    rm[r[0]:r[1] + 1] = 1
                m = m * rm
        else:
            r = _run_at(op[y], int(cx), 20)
            m = np.zeros(w)
            if r:
                m[max(0, r[0] - 4):r[1] + 5] = 1
        keep[y] = m * np.clip((y - (y0 - up)) / fade, 0, 1)
    out = rgba.copy()
    out[..., 3] = a * keep
    return out, y0


def to_image(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


def build(def_name):
    """-> list of (dest path, PIL image) for every letter of the def's pool."""
    root, whole, trunk, canopy, cells = TREES[def_name]
    base = os.path.join(REPO, root, whole)
    prefix = os.path.basename(whole)
    tprefix, cprefix = os.path.basename(trunk), os.path.basename(canopy)
    side = int(round(cells * ART_PX_PER_CELL))
    out = []
    for L in letters(base, prefix):
        im = Image.open(os.path.join(base, prefix + L + ".png")).convert("RGBA")
        rgba = np.asarray(im).astype(np.float32) / 255.0
        t, _ = trunk_of(rgba)
        out.append((os.path.join(REPO, root, trunk, tprefix + L + ".png"), to_image(t)))
        out.append((os.path.join(REPO, root, canopy, cprefix + L + ".png"), im.resize((side, side), Image.LANCZOS)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("defName", choices=sorted(TREES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sheet", help="also write a contact sheet (trunk over canopy per letter) here, for the look")
    a = ap.parse_args(argv)
    pairs = build(a.defName)
    if a.sheet:
        tiles = [img.resize((160, 160), Image.LANCZOS) for _, img in pairs]
        n = len(tiles) // 2
        sheet = Image.new("RGBA", (160 * n, 320), (110, 120, 100, 255))
        for i in range(n):
            sheet.alpha_composite(tiles[2 * i], (160 * i, 0))
            sheet.alpha_composite(tiles[2 * i + 1], (160 * i, 160))
        sheet.save(a.sheet)
        print("SHEET", a.sheet)
    import artledger  # noqa: E402  (late: --sheet alone needs no ledger seat)
    for dest, img in pairs:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        r = artledger.install_image(dest, img, reason=REASON, dry_run=a.dry_run)
        print(r.get("status"), os.path.relpath(dest, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
