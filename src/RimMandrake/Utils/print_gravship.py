#!/usr/bin/env python3
"""
print_gravship.py - stamp a saved ShipLayoutDefV2 onto a LIVE map through the bridge.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

WHY THIS EXISTS
---------------
`skills/gravship-layout/SKILL.md` says mid-game import "does not exist" because
GravshipExport's own importer only runs at world creation. That is true of the
MOD's route. It is not true of the bridge: foundation, terrain and buildings are
three batch calls we already have, and a layout file is just a grid.

RUN FROM WINDOWS PYTHON (`python.exe`). The bridge binds Windows loopback.

THE ORDER IS NOT OPTIONAL
-------------------------
  0. strip UNDER-terrain over the footprint
  1. foundation (Substructure)
  2. terrain (the floors)
  3. things, LARGEST FOOTPRINT FIRST

(0) is the one nobody expects. `SetFoundation` is refused - reported per cell as
"cell has under-terrain; strip the floor first" - on any cell carrying an under
layer, and a natural top terrain cannot be removed at all
(`CanRemoveTopLayerAt` false). The way through is to lay a REMOVABLE floor and
then remove it: SetTerrain pushes the natural terrain down into `under`, and
RemoveTopLayer pops it back up and nulls `under`. Two calls, and the cell is
finally eligible for a foundation.

(3) matters because `jawa/build_batch` wipes what it lands on and reports
`placed` for both the survivor and its victim. Largest-first plus a read-back
diff is the only honest signal.

WHAT THIS DOES NOT DO
---------------------
The FOUR GATES (claim, power, batteries, astrofuel) still apply, and a colonist
must still inspect the engine. `faction=` covers gate 1 only. A printed ship is
geometry, not a working gravship - see the skill.

The exporter does NOT save the GravEngine (both of our exports contain zero);
the importer places it at the layout's `gravEngineX/Z`. `--engine` does the same
here, and is on by default.

USAGE
    python.exe print_gravship.py <layout.xml> --center 125,125 [--apply]
    python.exe print_gravship.py <layout.xml> --offset 81,58   [--apply]
Without --apply it prints the plan and touches nothing.
"""

import argparse
import collections
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gravship_layout import Layout                     # noqa: E402
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

# The companion's compiled-in guards. Exceeding either is refused, not truncated.
MAX_OPS = 4096
BUILD_CHUNK = 400

# Map litter the exporter swept into the capture. These are indestructible
# natural features that belong to the ORIGINAL map, not to the ship.
LITTER = {"SteamGeyser", "VHGE_GasGeyser"}


def rle_rows(cells):
    """cells: {(x,z): key} -> [(key, x, z, w, 1)] merging each row run."""
    out = []
    byz = collections.defaultdict(dict)
    for (x, z), k in cells.items():
        byz[z][x] = k
    for z in sorted(byz):
        row = byz[z]
        for x in sorted(row):
            k = row[x]
            if out and out[-1][0] == k and out[-1][2] == z and out[-1][1] + out[-1][3] == x:
                p = out[-1]
                out[-1] = (p[0], p[1], p[2], p[3] + 1, 1)
            else:
                out.append((k, x, z, 1, 1))
    return out


def ops_string(runs):
    return ";".join("%s:%d,%d,%d,%d" % r for r in runs)


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("layout")
    ap.add_argument("--center", help="map cell the ship's footprint centres on, 'x,z'")
    ap.add_argument("--offset", help="explicit layout->map offset, 'x,z'")
    ap.add_argument("--faction", default="PlayerColony",
                    help="faction defName owning every building. '' = factionless.")
    ap.add_argument("--sizes", default=os.path.join(HERE, "..", "..", "..",
                                                    "observed", "def_sizes.json"),
                    help="def_sizes.json, used only to order largest-first")
    ap.add_argument("--no-engine", action="store_true",
                    help="do not place a GravEngine at gravEngineX/Z")
    ap.add_argument("--engine-def", default="GravEngine")
    ap.add_argument("--strip-whole-map", action="store_true",
                    help="strip under-terrain over the WHOLE map, not just the footprint")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    lay = Layout.load(args.layout)

    # footprint of the non-empty cells, which excludes the 1-cell margin
    xs, zs = [], []
    for z in range(lay.height):
        for x in range(lay.width):
            c = lay.cell(x, z)
            if c is not None and not c.empty():
                xs.append(x)
                zs.append(z)
    minx, maxx, minz, maxz = min(xs), max(xs), min(zs), max(zs)

    if args.offset:
        ox, oz = [int(v) for v in args.offset.split(",")]
    elif args.center:
        cx, cz = [int(v) for v in args.center.split(",")]
        ox = cx - (minx + maxx) // 2
        oz = cz - (minz + maxz) // 2
    else:
        ox = oz = 0

    foundation, terrain = {}, {}
    things = []                      # (area, defName, x, z, rot, stuff)
    skipped = collections.Counter()
    sizes = {}
    try:
        import json
        sizes = json.load(open(os.path.normpath(args.sizes)))
    except Exception as exc:
        print("WARN: no def_sizes.json (%s); ordering falls back to 1x1" % exc)

    for z in range(lay.height):
        for x in range(lay.width):
            c = lay.cell(x, z)
            if c is None or c.empty():
                continue
            mx, mz = x + ox, z + oz
            if c.foundationDef:
                foundation[(mx, mz)] = c.foundationDef
            if c.terrainDef:
                terrain[(mx, mz)] = c.terrainDef
            for t in c.things:
                if t.defName in LITTER:
                    skipped[t.defName] += 1
                    continue
                w, h = sizes.get(t.defName, [1, 1])[:2]
                things.append((w * h, t.defName, mx, mz, t.rot or 0, t.stuffDef))

    if not args.no_engine and lay.gravEngineX is not None:
        ex, ez = lay.gravEngineX + ox, lay.gravEngineZ + oz
        w, h = sizes.get(args.engine_def, [3, 3])[:2]
        things.append((w * h, args.engine_def, ex, ez, 0, None))

    things.sort(key=lambda t: -t[0])          # largest footprint first

    rect = "%d,%d,%d,%d" % (minx + ox, minz + oz, maxx - minx + 1, maxz - minz + 1)
    fnd_ops = ops_string(rle_rows(foundation))
    ter_runs = rle_rows(terrain)

    print("layout   %s  %dx%d  engine(local) %s,%s"
          % (lay.defName, lay.width, lay.height, lay.gravEngineX, lay.gravEngineZ))
    print("offset   %d,%d   footprint on map %s" % (ox, oz, rect))
    print("cells    foundation %d  terrain %d" % (len(foundation), len(terrain)))
    print("things   %d in %d ops (largest first: %s)"
          % (len(things), len(things), things[0][1] if things else "-"))
    if skipped:
        print("skipped  map litter caught in the export: %s" % dict(skipped))
    if not args.no_engine:
        print("engine   %s at %d,%d (the export never contains one)"
              % (args.engine_def, lay.gravEngineX + ox, lay.gravEngineZ + oz))
    for ops, what in ((fnd_ops, "foundation"),):
        n = ops.count(";") + 1 if ops else 0
        if n > MAX_OPS:
            print("NOTE: %s is %d ops, chunking against MAX_OPS=%d" % (what, n, MAX_OPS))
    if not args.apply:
        print("\n(dry run - pass --apply to write)")
        return 0

    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=900.0) as rb:

        # 0. strip under-terrain so SetFoundation is not refused
        strip = "0,0,%d,%d" % (250, 250) if args.strip_whole_map else rect
        rb.call("jawa/set_terrain_batch",
                {"ops": "MetalTile:%s" % strip, "layer": "top", "refresh": False})
        r = rb.call("jawa/set_terrain_layer",
                    {"layer": "removeTop", "rect": strip,
                     "doLeavings": False, "readBack": 0})
        print("strip    changed %s refused %s" % (r.get("changed"), r.get("refusedCount")))

        # 1. foundation
        allf = rle_rows(foundation)
        changed = failed = 0
        for part in chunks(allf, MAX_OPS):
            r = rb.call("jawa/set_terrain_batch",
                        {"ops": ops_string(part), "layer": "foundation", "refresh": False})
            changed += r.get("cellsChanged") or 0
            failed += r.get("cellsFailedVerify") or 0
        print("foundation changed %d failedVerify %d (want %d)"
              % (changed, failed, len(foundation)))

        # 2. terrain
        changed = failed = 0
        for part in chunks(ter_runs, MAX_OPS):
            r = rb.call("jawa/set_terrain_batch",
                        {"ops": ops_string(part), "layer": "top", "refresh": False})
            changed += r.get("cellsChanged") or 0
            failed += r.get("cellsFailedVerify") or 0
        print("terrain    changed %d failedVerify %d (want %d)"
              % (changed, failed, len(terrain)))

        # 3. things, grouped by stuff (a per-CALL parameter), largest first
        placed = 0
        bystuff = collections.OrderedDict()
        for area, d, x, z, rot, stuff in things:
            bystuff.setdefault(stuff, []).append("%s:%d,%d,%d" % (d, x, z, rot))
        for stuff, ops in bystuff.items():
            for part in chunks(ops, BUILD_CHUNK):
                p = {"ops": ";".join(part), "readBack": 0}
                if stuff:
                    p["stuff"] = stuff
                if args.faction:
                    p["faction"] = args.faction
                r = rb.call("jawa/build_batch", p)
                placed += r.get("placed") or 0
                for f in (r.get("failed") or [])[:5]:
                    print("   build failed:", f)
        print("things     placed(reported) %d of %d" % (placed, len(things)))

        m = rb.call("jawa/map_commit", {})
        print("commit     %s failedSteps %s" % (m.get("success"), m.get("failedSteps")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
