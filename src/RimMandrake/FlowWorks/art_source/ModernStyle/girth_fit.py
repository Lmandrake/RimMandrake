#!/usr/bin/env python3
"""Girth fit of the Modern Flange and Coupler (MODERN_FIT_REDRAW_ROUND_FOUR_PENDING).

Measured 2026-11-05: the shipped Modern Flange ring is 33 px across the pipe on a 128 px canvas drawn at
LiquidJoinRule.FlangeSize 0.5 cell, i.e. 0.129 cell, and the Coupler's mated rings 31 px = 0.121 cell, both NARROWER than
the 0.136-cell bore of the pipe they join (RM_PipePoleMath: 18 of 132 displayed px). A flange ring must stand proud of its
pipe. This widens each ring across the pipe (canvas rows) to RING_CELLS by repeating its plain rows (rows with no silver
bolt pixel, away from the rounded caps), so bolts stay round and the profile along the pipe (columns, the anchor the C#
places: Flange flush to the right edge, Coupler centred) is untouched. Geometry only: colour comes from waterworks_blue,
installed = waterworks_blue.recolour(fit(red original)) pixel for pixel (selftest_fw_offline_art pins it).

Usage: girth_fit.py OUT_DIR    writes OUT_DIR/Joins/Modern/{Flange,Coupler}.png (blue, ready to install)"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

FLANGE_SIZE = 0.5                 # LiquidJoinRule.FlangeSize: the Flange and Coupler quads, cells
BORE = 0.136                      # cell: the universal pipe's bore, every look (fw_offline_checks.BORE)
RING_CELLS = 0.20                 # target ring extent across the pipe: ~1.47x the bore
PIECES = ("Joins/Modern/Flange.png", "Joins/Modern/Coupler.png")
ALPHA = 40                        # opaque for measuring
CAP = 3                           # rows at each rounded end never repeated


def across_cells(im, size=FLANGE_SIZE):
    """The ring's widest extent across the pipe (canvas rows), in cells."""
    a = np.asarray(im.convert("RGBA"))[..., 3] > ALPHA
    return float(a.sum(0).max()) / a.shape[0] * size


def _plain_rows(a, y0, y1):
    rgb = a[..., :3].astype(int)
    op = a[..., 3] > ALPHA
    silver = op & ((rgb.max(-1) - rgb.min(-1)) < 40)
    return [y for y in range(y0 + CAP, y1 - CAP) if op[y].any() and not silver[y].any()]


def fit(im, cells=RING_CELLS):
    """Widen the ring across the pipe to `cells` (rounded to whole px), centred on its old centre row."""
    a = np.asarray(im.convert("RGBA"))
    h = a.shape[0]
    rows = np.where((a[..., 3] > ALPHA).any(1))[0]
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    want = int(round(cells / FLANGE_SIZE * h))
    extra = want - (y1 - y0)
    if extra <= 0:
        return Image.fromarray(a.copy(), "RGBA")
    plain = _plain_rows(a, y0, y1)
    if not plain:
        raise ValueError("no plain row to repeat")
    reps = {y: extra // len(plain) for y in plain}
    for i in np.linspace(0, len(plain) - 1, extra % len(plain)).round().astype(int) if extra % len(plain) else []:
        reps[plain[i]] += 1   # the remainder spread evenly from the first plain row to the last
    out_rows = []
    for y in range(y0, y1):
        out_rows.extend([a[y]] * (1 + reps.get(y, 0)))
    band = np.stack(out_rows)
    top = int(round((y0 + y1) / 2.0 - len(band) / 2.0))
    out = np.zeros_like(a)
    out[top:top + len(band)] = band
    return Image.fromarray(out, "RGBA")


def build(rel):
    import waterworks_blue as wb
    red = Image.open(wb.RED / rel).convert("RGBA")
    return wb.recolour(fit(red), rel)[0]


def main(out):
    for rel in PIECES:
        p = Path(out) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        im = build(rel)
        im.save(p)
        print("%s  across %.3f cell (bore %.3f, x%.2f)" % (p, across_cells(im), BORE, across_cells(im) / BORE))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main(sys.argv[1])
