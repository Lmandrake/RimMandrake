#!/usr/bin/env python3
"""
gravship_terrain_ops.py — turn a saved gravship layout into terrain batch ops.

VERSION 1.0  (2026-08-20)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHY THIS EXISTS
---------------
B55 step (b): *"replay the layout's `terrainDef` cells through
`jawa/set_terrain_batch` — floors do NOT come with a mid-game Sketch spawn and
nothing errors when they are missing."*

A `ShipLayoutDefV2` stores a full grid, one entry per cell. Feeding that to the
bridge one cell at a time is thousands of calls; `jawa/set_terrain_batch` takes
RECTANGLES, and cost on that bridge tracks CALL COUNT, not cell count. So this
run-length-encodes each row into the widest rectangles it can and emits the ops
string the tool expects.

🔴 TWO GRIDS, AND THE ORDER IS NOT OPTIONAL.
A gravship cell carries BOTH a `foundationDef` (Substructure, the third grid
added in 1.6/Odyssey) and a `terrainDef` (the floor on top of it). They are two
separate `layer=` values on the same tool, and:

    **FOUNDATION MUST BE PAINTED FIRST.** `SetFoundation` is refused - silently,
    at the write - on any cell that already carries a floor. There is no retrofit
    and no inspection afterwards can see that it is missing; buildings that need
    `terrainAffordanceNeeded=Substructure` simply cannot be placed later.

So this emits TWO files and names them in the order they must be run.

⚠️ WHAT THIS DOES NOT DO. It does not place the ship's THINGS - walls, engine,
furniture - which are a separate part of the layout and a separate step. It only
paints the two floor grids.

⚠️ ORIENTATION IS THE CALLER'S TO CONFIRM. Coordinates come out RELATIVE to the
layout's own origin: `rows[0]` is z=0 and the first entry in a row is x=0. Add
your landing offset. **The check that costs nothing: the layout records
`gravEngineX` / `gravEngineZ`, so after painting, the engine cell should be at
`(offsetX + gravEngineX, offsetZ + gravEngineZ)`.** If it is not, the row order
is flipped and everything else is too.

USAGE
-----
    python3 src/RimMandrake/Utils/gravship_terrain_ops.py <layout.xml> [--out DIR]
    python3 src/RimMandrake/Utils/gravship_terrain_ops.py <layout.xml> --offset 100,120
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET

MAX_OPS = 4096          # jawa/set_terrain_batch's own cap; exceeding it is refused


def die(msg):
    print("FAIL: " + msg, file=sys.stderr)
    sys.exit(2)


def read_grid(path):
    """-> (width, height, engine, {(x, z): {'foundation': d, 'terrain': d}})"""
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        die("could not parse %s: %s" % (path, e))
    if root.tag != "ShipLayoutDefV2":
        die("root is <%s>, expected <ShipLayoutDefV2>" % root.tag)

    rows = root.find("rows")
    if rows is None:
        die("no <rows> in the layout")
    width = int(root.findtext("width") or 0)
    height = int(root.findtext("height") or 0)
    engine = (root.findtext("gravEngineX"), root.findtext("gravEngineZ"))

    cells = {}
    for z, row in enumerate(rows):
        for x, cell in enumerate(row):
            f = (cell.findtext("foundationDef") or "").strip()
            t = (cell.findtext("terrainDef") or "").strip()
            if f or t:
                cells[(x, z)] = {"foundation": f or None, "terrain": t or None}
    return width, height, engine, cells


def rle_rows(cells, key):
    """
    Widest-run-per-row rectangles. Rows are encoded independently: merging
    vertically as well would cut the op count further, but a wrong merge paints
    cells nobody asked for, and this is already far inside the cap.
    -> [(defName, x, z, w, h)]
    """
    by_z = {}
    for (x, z), v in cells.items():
        d = v.get(key)
        if d:
            by_z.setdefault(z, {})[x] = d

    ops = []
    for z in sorted(by_z):
        row = by_z[z]
        for x in sorted(row):
            d = row[x]
            if ops and ops[-1][0] == d and ops[-1][2] == z and ops[-1][1] + ops[-1][3] == x:
                name, ox, oz, w, h = ops[-1]
                ops[-1] = (name, ox, oz, w + 1, h)
            else:
                ops.append((d, x, z, 1, 1))
    return ops


def to_ops_string(ops, dx, dz):
    return ";".join("%s:%d,%d,%d,%d" % (d, x + dx, z + dz, w, h) for d, x, z, w, h in ops)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layout", help="a ShipLayoutDefV2 xml")
    ap.add_argument("--out", default=None, help="directory for the ops files")
    ap.add_argument("--offset", default="0,0",
                    help="x,z to add to every coordinate (the landing position)")
    args = ap.parse_args()

    if not os.path.isfile(args.layout):
        die("no such layout: " + args.layout)
    try:
        dx, dz = (int(v) for v in args.offset.split(","))
    except Exception:
        die("--offset wants 'x,z', e.g. --offset 100,120")

    width, height, engine, cells = read_grid(args.layout)
    print("layout : %s" % os.path.basename(args.layout))
    print("grid   : %d x %d, %d populated cell(s)" % (width, height, len(cells)))
    print("engine : gravEngineX=%s gravEngineZ=%s  ->  expect it at (%s, %s) after offset"
          % (engine[0], engine[1],
             int(engine[0]) + dx if engine[0] else "?",
             int(engine[1]) + dz if engine[1] else "?"))
    print()

    out_dir = args.out or os.path.dirname(os.path.abspath(args.layout))
    base = os.path.splitext(os.path.basename(args.layout))[0]
    stem = os.path.join(out_dir, base)

    # ORDER MATTERS: foundation first. See the module docstring.
    plan = [("foundation", "foundation", stem + ".foundation.ops.txt"),
            ("terrain", "top", stem + ".terrain.ops.txt")]

    written = []
    for key, layer, path in plan:
        ops = rle_rows(cells, key)
        cellcount = sum(w * h for _, _, _, w, h in ops)
        kinds = sorted({d for d, _, _, _, _ in ops})
        flag = "  🔴 OVER THE CAP" if len(ops) > MAX_OPS else ""
        print("  %-11s %5d cell(s) -> %4d rect op(s)%s   defs: %s"
              % (key, cellcount, len(ops), flag, ", ".join(kinds) or "none"))
        if not ops:
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(to_ops_string(ops, dx, dz))
        written.append((layer, path, len(ops), cellcount))

    if not written:
        print("\nNothing to paint.")
        return 0

    print("\nRUN THEM IN THIS ORDER - foundation is refused on any cell that already")
    print("carries a floor, silently, and cannot be retrofitted:\n")
    for i, (layer, path, nops, ncells) in enumerate(written, 1):
        print("  %d. jawa/set_terrain_batch  layer=%-10s  ops=@%s"
              % (i, layer, os.path.basename(path)))
        print("       %d ops, %d cells" % (nops, ncells))
    print("\n⚠️ `success: true` is not evidence. Read `cellsFailedVerify` on the response -")
    print("   the tool reads every cell back off the grid and that field is authoritative.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
