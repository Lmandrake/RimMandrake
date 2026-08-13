#!/usr/bin/env python3
"""
sheet.py — pack the four facings into one image for the model, and cut the
result back apart afterwards.

WHY A SHEET
===========
Asking for four facings in four separate conversations produces four
independently-imagined machines. The rust lands in different places, a hole
punched in the north face is absent from the south, and the four never look like
the same object. Handing the model **all four at once, in one image**, makes the
damage consistent by construction — it is drawing one machine, seen four ways,
in a single pass.

It also sidesteps a practical limit: an image model returns one image per turn.
One sheet is one turn.

LAYOUT
======
A 2x2 grid, reading order **north, east / south, west**, each facing centred in
a square cell sized to the largest facing. Cells are square and uniform even
though the facings are not (this machine is 512x640 north/south but 640x512
east/west), so the grid stays predictable no matter what the donor art does.

Gutters are transparent and generous. Nothing is drawn into the image — no
labels, no rules, no numbers — because anything drawn is something the model
will helpfully redraw, and then we would be cutting the sheet apart along lines
it moved.

CUTTING IT BACK UP
==================
`split` does not need to be pixel-exact, and this is the part that makes the
whole scheme safe. It maps cells **proportionally**, so a sheet that comes back
at a different resolution still cuts correctly; and each extracted facing is
then handed to `fit_sprite.py`, which registers it against its own reference and
corrects any residual drift. Sloppy cut, exact result.

USAGE
  python Source/sheet.py make AutomatedSmelter
  python Source/sheet.py split AutomatedSmelter --tier wrecked --sheet ~/Downloads/out.png
  python Source/sheet.py split AutomatedSmelter --tier wrecked --sheet out.png --then-fit
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import read_png, write_rgba, resize_rgba, PngError      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.path.join(MOD_ROOT, "art_source")

GRID = ["north", "east", "south", "west"]      # reading order, 2 across
COLS = 2
MARGIN = 40
GUTTER = 56
MAX_ASPECT_DRIFT = 0.06        # a returned sheet may not change shape by more than this


def facing_of(filename):
    stem = os.path.splitext(filename)[0]
    return stem.rsplit("_", 1)[-1].lower()


def make(short):
    mdir = os.path.join(ART_SOURCE, short)
    man = json.load(open(os.path.join(mdir, "MANIFEST.json"), encoding="utf-8"))
    by_facing = {facing_of(f): f for f in man["expected_files"]}
    missing = [f for f in GRID if f not in by_facing]
    if missing:
        sys.exit("This machine has no %s facing(s); the 2x2 sheet assumes all four."
                 % ", ".join(missing))

    loaded = {}
    for f in GRID:
        p = os.path.join(mdir, "restored", by_facing[f])
        if not os.path.isfile(p):
            sys.exit("Missing reference art %s — run grab_source_art.py." % p)
        loaded[f] = read_png(p)

    cell = max(max(w, h) for w, h, _ in loaded.values())
    rows = (len(GRID) + COLS - 1) // COLS
    sheet_w = MARGIN * 2 + COLS * cell + (COLS - 1) * GUTTER
    sheet_h = MARGIN * 2 + rows * cell + (rows - 1) * GUTTER
    canvas = bytearray(sheet_w * sheet_h * 4)

    cells = {}
    for n, f in enumerate(GRID):
        cx = MARGIN + (n % COLS) * (cell + GUTTER)
        cy = MARGIN + (n // COLS) * (cell + GUTTER)
        w, h, d = loaded[f]
        ox, oy = cx + (cell - w) // 2, cy + (cell - h) // 2
        for y in range(h):
            src = y * w * 4
            dst = ((oy + y) * sheet_w + ox) * 4
            canvas[dst:dst + w * 4] = d[src:src + w * 4]
        cells[f] = {"file": by_facing[f], "cell_xywh": [cx, cy, cell, cell],
                    "art_xywh": [ox, oy, w, h]}

    out_dir = os.path.join(mdir, "sheets")
    os.makedirs(out_dir, exist_ok=True)
    sheet_path = os.path.join(out_dir, "SOURCE_SHEET.png")
    write_rgba(sheet_path, sheet_w, sheet_h, canvas)
    layout = {"machine": short, "sheet_wh": [sheet_w, sheet_h], "cell": cell,
              "cols": COLS, "margin": MARGIN, "gutter": GUTTER,
              "order": GRID, "cells": cells}
    with open(os.path.join(out_dir, "SHEET_LAYOUT.json"), "w", encoding="utf-8") as fh:
        json.dump(layout, fh, indent=2)

    print("%s — source sheet" % short)
    print("  %d x %d, 2x2 grid of %dpx cells, order %s"
          % (sheet_w, sheet_h, cell, " / ".join(GRID)))
    for f in GRID:
        c = cells[f]
        print("     %-6s cell at (%d,%d)  art %dx%d" % (f, c["cell_xywh"][0],
              c["cell_xywh"][1], c["art_xywh"][2], c["art_xywh"][3]))
    print("  wrote sheets/SOURCE_SHEET.png + SHEET_LAYOUT.json")
    return layout


def split(short, tier, sheet_path, then_fit=False):
    mdir = os.path.join(ART_SOURCE, short)
    lay_path = os.path.join(mdir, "sheets", "SHEET_LAYOUT.json")
    if not os.path.isfile(lay_path):
        sys.exit("No SHEET_LAYOUT.json — run `sheet.py make %s` first." % short)
    lay = json.load(open(lay_path, encoding="utf-8"))
    if not os.path.isfile(sheet_path):
        sys.exit("No such sheet: %s" % sheet_path)

    sw, sh, sd = read_png(sheet_path)
    ow, oh = lay["sheet_wh"]
    kx, ky = sw / float(ow), sh / float(oh)
    drift = abs(kx - ky) / max(kx, ky)
    print("%s / %s — splitting %s" % (short, tier, os.path.basename(sheet_path)))
    print("  returned %dx%d against source %dx%d (scale %.3f x %.3f)"
          % (sw, sh, ow, oh, kx, ky))
    if drift > MAX_ASPECT_DRIFT:
        sys.exit("  ABORT: the sheet's aspect changed by %.1f%% (limit %.0f%%). It has "
                 "been cropped or stretched, so the cells no longer sit where the "
                 "layout says. Re-generate keeping the whole frame."
                 % (drift * 100, MAX_ASPECT_DRIFT * 100))

    tier_dir = os.path.join(mdir, tier)
    os.makedirs(tier_dir, exist_ok=True)
    written = []
    for f in lay["order"]:
        c = lay["cells"][f]
        cx, cy, cw, ch = c["cell_xywh"]
        x0, y0 = int(round(cx * kx)), int(round(cy * ky))
        x1, y1 = int(round((cx + cw) * kx)), int(round((cy + ch) * ky))
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(sw, x1), min(sh, y1)
        w, h = x1 - x0, y1 - y0
        if w < 8 or h < 8:
            print("     %-6s SKIPPED — cell fell outside the returned image" % f)
            continue
        tile = bytearray(w * h * 4)
        for y in range(h):
            src = ((y0 + y) * sw + x0) * 4
            tile[y * w * 4:(y + 1) * w * 4] = sd[src:src + w * 4]
        dst = os.path.join(tier_dir, c["file"])
        write_rgba(dst, w, h, tile)
        written.append(c["file"])
        print("     %-6s -> %s  (%dx%d)" % (f, c["file"], w, h))

    print("  %d facing(s) written into %s/" % (len(written), tier))
    print("  NOTE: these are raw cuts at sheet resolution. They are not final until "
          "fit_sprite conforms each one to its own reference.")
    if then_fit:
        print()
        os.system('%s "%s" %s --tier %s --apply'
                  % (sys.executable, os.path.join(HERE, "fit_sprite.py"), short, tier))
    else:
        print("\n  next:  python Source/fit_sprite.py %s --tier %s --apply" % (short, tier))
        print("         python Source/check_sprite.py %s --tier %s" % (short, tier))
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="build the source sheet to hand to the model")
    m.add_argument("machine")
    s = sub.add_parser("split", help="cut a returned sheet back into facings")
    s.add_argument("machine")
    s.add_argument("--tier", required=True)
    s.add_argument("--sheet", required=True, help="the image the model returned")
    s.add_argument("--then-fit", action="store_true", help="run fit_sprite --apply after")
    args = ap.parse_args()

    if args.cmd == "make":
        make(args.machine)
    else:
        split(args.machine, args.tier, args.sheet, args.then_fit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
