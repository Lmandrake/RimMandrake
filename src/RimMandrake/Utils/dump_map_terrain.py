#!/usr/bin/env python3
"""Dump the WHOLE map's top terrain in one read-only bridge call.

Written during the 2026-08-13 cold load so the live session spends seconds on
this instead of minutes. It answers two v1-adjacent questions from ONE call:

  v1 row 7 -- is this ordinary desert worldgen? -> the terrain histogram.
  B-v1     -- where is the Geological Landforms dry-lake footprint? -> the
              SoftSand cells, which we then flood-fill OFFLINE.

WHY A DUMP AND NOT A LIVE SEARCH. The dry-lake footprint is NOT stored anywhere
at runtime: GL evaluates it into TerrainGrid during worldgen and discards the
mask (GeologicalLandforms.BiomeGrid has no landform field). So the footprint has
to be recovered from the terrain itself. And it cannot be recovered by "select
all SoftSand" -- vanilla Desert and ExtremeDesert scatter SoftSand map-wide via
perlin terrainPatchMakers, so a map-wide sweep would repaint dunes and erase the
desert. The discriminator is CONTIGUITY: the lake bed is one large connected
blob, the dune patches are many small ones. That is a flood-fill, it is pure
arithmetic, and it belongs offline where it costs nothing.

READ-ONLY. This script writes nothing to the game. It cannot damage a map.

    python.exe src/RimMandrake/Utils/dump_map_terrain.py
    python.exe src/RimMandrake/Utils/dump_map_terrain.py --layer under
    python3 src/RimMandrake/Utils/dump_map_terrain.py --analyse <dump.json>

⚠️ Must run under WINDOWS python.exe to reach the bridge -- RimBridge binds
Windows loopback and WSL2 is NAT-mode, so python3 cannot see it at all. The
--analyse mode is pure offline arithmetic and runs fine under either.
"""
import argparse
import json
import os
import sys
from collections import Counter, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Budgets are enforced server-side in JawaBenchTerrainTools.cs (MaxOps 4096,
# MaxCells 70000). A 250x250 map is 62,500 cells, so a whole map fits in ONE
# call -- but 300x300 is 90,000 and does NOT. We therefore read the size first
# and split into horizontal bands rather than assuming it fits.
MAX_CELLS = 70000
MAX_OPS = 4096


def fetch(layer="top", out_path=None):
    from rimbridge_client import RimBridge, RimBridgeError
    rb = RimBridge()

    info = rb.call("rimworld/get_game_info") or {}
    size = info.get("mapSize") or {}
    mx, mz = size.get("x"), size.get("z")
    if not mx or not mz:
        raise SystemExit(
            "could not read mapSize off rimworld/get_game_info -- got %r.\n"
            "Not guessing a map size: a dump aimed at the wrong extent looks "
            "complete and is silently short." % (size,))
    print("map %dx%d = %d cells, layer=%s" % (mx, mz, mx * mz, layer))

    # Split into bands that respect the cell budget.
    rows_per_band = max(1, MAX_CELLS // mx)
    bands, z = [], 0
    while z < mz:
        h = min(rows_per_band, mz - z)
        bands.append((0, z, mx, h))
        z += h
    print("%d call(s), %d rows each" % (len(bands), rows_per_band))

    chunks = []
    for i, (x, z0, w, h) in enumerate(bands, 1):
        resp = rb.call("jawa/get_terrain_batch",
                       {"rects": "%d,%d,%d,%d" % (x, z0, w, h), "layer": layer})
        if not isinstance(resp, dict) or resp.get("success") is not True:
            raise SystemExit("band %d/%d failed: %r" % (i, len(bands), resp))
        # ⚠️ Assert on the COUNT, not on success. A call that reads zero cells
        # and reports success is the exact failure this project keeps hitting.
        read = resp.get("cellsRead", 0)
        if read != w * h:
            print("  ⚠️ band %d: cellsRead=%d, expected %d" % (i, read, w * h))
        chunks.append(resp)
        print("  band %d/%d: %d cells" % (i, len(bands), read))

    dump = {"mapSize": {"x": mx, "z": mz}, "layer": layer,
            "cellsRead": sum(c.get("cellsRead", 0) for c in chunks),
            "bands": chunks}
    out_path = out_path or ("observed/terrain_%s_%dx%d.json" % (layer, mx, mz))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(dump, fh)
    print("wrote %s (%d cells)" % (out_path, dump["cellsRead"]))
    return out_path


def parse_ops(dump):
    """ops grammar -> {(x,z): terrain}. 'Name:x,z,w,h', ';' or newline sep."""
    cells = {}
    for band in dump["bands"]:
        for op in (band.get("ops") or "").replace("\n", ";").split(";"):
            op = op.strip()
            if not op:
                continue
            name, _, coords = op.rpartition(":")
            parts = [p.strip() for p in coords.split(",")]
            if len(parts) < 2:
                continue
            x, z = int(parts[0]), int(parts[1])
            w = int(parts[2]) if len(parts) > 2 else 1
            h = int(parts[3]) if len(parts) > 3 else 1
            for dz in range(h):
                for dx in range(w):
                    cells[(x + dx, z + dz)] = name
    return cells


def blobs(cells, want):
    """Connected components (4-way) of cells whose terrain == want."""
    members = {c for c, t in cells.items() if t == want}
    seen, out = set(), []
    for start in members:
        if start in seen:
            continue
        comp, q = [], deque([start])
        seen.add(start)
        while q:
            x, z = q.popleft()
            comp.append((x, z))
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in members and n not in seen:
                    seen.add(n)
                    q.append(n)
        out.append(comp)
    out.sort(key=len, reverse=True)
    return out


def analyse(path, target="SoftSand"):
    with open(path) as fh:
        dump = json.load(fh)
    cells = parse_ops(dump)
    print("parsed %d cells (dump says %d)" % (len(cells), dump.get("cellsRead", -1)))

    hist = Counter(cells.values())
    print("\nterrain histogram -- v1 row 7 evidence:")
    for name, n in hist.most_common(20):
        print("  %-28s %6d  %5.1f%%" % (name, n, 100.0 * n / max(1, len(cells))))

    comps = blobs(cells, target)
    if not comps:
        print("\nno %s on this map -- no dry lake here, or the layer is wrong."
              % target)
        return
    print("\n%s: %d cells in %d blob(s)" % (target, sum(len(c) for c in comps),
                                            len(comps)))
    for i, comp in enumerate(comps[:6], 1):
        xs = [c[0] for c in comp]
        zs = [c[1] for c in comp]
        print("  blob %d: %6d cells  bbox x %d-%d, z %d-%d" %
              (i, len(comp), min(xs), max(xs), min(zs), max(zs)))

    big = len(comps[0])
    rest = sum(len(c) for c in comps[1:])
    print("\nVERDICT: largest blob %d cells, all others %d." % (big, rest))
    if big > rest * 2:
        print("  Separable. The lake bed is the largest component; a repaint")
        print("  bounded to it will NOT touch the perlin dune patches.")
        print("  -> B-v1 needs no new C#: feed blob 1's bbox rows to")
        print("     jawa/set_terrain_batch as Jawa_SaltCrust ops.")
    else:
        print("  NOT cleanly separable. Do NOT repaint on contiguity alone --")
        print("  ask VISION for a bounding rect before touching anything.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layer", default="top", choices=["top", "under", "foundation"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--analyse", metavar="DUMP", default=None,
                    help="offline: analyse an existing dump, no game needed")
    ap.add_argument("--target", default="SoftSand",
                    help="terrain to flood-fill (default SoftSand)")
    a = ap.parse_args()

    if a.analyse:
        analyse(a.analyse, a.target)
        return
    analyse(fetch(a.layer, a.out), a.target)


if __name__ == "__main__":
    main()
