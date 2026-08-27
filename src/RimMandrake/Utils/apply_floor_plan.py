#!/usr/bin/env python3
"""
apply_floor_plan.py - lay a gravship_floor_v2 plan onto the LIVE map.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

Run under WINDOWS python (`python.exe`); the bridge binds Windows loopback.

    python.exe apply_floor_plan.py --plan world/_ship/v2/plan_corrosion_halo.json --apply

THE ORDER IS NOT OPTIONAL
  1. thrusters      - build/destroy before anything reads the deck
  2. holes          - removeTop (pops the natural terrain back up and NULLS `under`)
                      then strip the foundation. Must precede painting, because
                      painting a floor WRITES `under`, and SetFoundation-adjacent
                      operations refuse a cell that carries one.
  3. floors         - one set_terrain_batch per TerrainDef
  4. floor colour   - jawa/set_terrain_layer layer='color' takes ONE rect per call,
                      so this is the expensive step: ~1,400 calls for this ship.

Everything is read back afterwards; `success: true` is not evidence.
"""

import argparse
import collections
import io
import json
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rimbridge_client import RimBridge, resolve_endpoint     # noqa: E402


def rle(cells):
    """[x,z] pairs -> widest horizontal runs (x, z, w, 1)."""
    byz = collections.defaultdict(list)
    for x, z in cells:
        byz[z].append(x)
    out = []
    for z in sorted(byz):
        xs = sorted(byz[z])
        s = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            out.append((s, z, prev - s + 1, 1))
            if x is not None:
                s = prev = x
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip-thrusters", action="store_true")
    ap.add_argument("--skip-holes", action="store_true")
    ap.add_argument("--skip-color", action="store_true")
    args = ap.parse_args()

    plan = json.load(open(args.plan))
    holes = [tuple(c) for c in plan["holes"]]
    print("plan %s: %d holes, %d floor defs, %d floor colours, %d wall cells"
          % (plan["treatment"], len(holes), len(plan["floors"]),
             len(plan["floorColor"]), sum(len(v) for v in plan["wallColor"].values())))
    if not args.apply:
        print("(dry run)")
        return 0

    t0 = time.time()
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=900.0) as rb:

        if not args.skip_thrusters:
            th = plan["thrusters"]
            east = ";".join("%d,%d,1,2" % (x, z) for x, z in th["remove_east"])
            r = rb.call("jawa/destroy_batch", {"rects": east, "categories": "Building"})
            print("thrusters: destroyed east %s" % r.get("destroyed"))
            r = rb.call("jawa/build_batch",
                        {"ops": ";".join("GravshipHull:%d,%d" % (x, z) for x, z in th["remove_east"]),
                         "stuff": "Steel", "faction": "PlayerColony", "readBack": 0})
            print("thrusters: east wall restored, placed %s" % r.get("placed"))
            west = ";".join("%d,%d" % (x, z) for x, z in th["add_west"])
            r = rb.call("jawa/destroy_batch", {"rects": west, "categories": "Building"})
            print("thrusters: cleared west wall %s" % r.get("destroyed"))
            r = rb.call("jawa/build_batch",
                        {"ops": ";".join("SmallThruster:%d,%d,1" % (x, z) for x, z in th["add_west"]),
                         "faction": "PlayerColony", "readBack": 0})
            print("thrusters: west placed %s failed %s" % (r.get("placed"), r.get("failed")))

        if not args.skip_holes:
            runs = rle(holes)
            ch = ref = 0
            for (x, z, w, h) in runs:
                r = rb.call("jawa/set_terrain_layer",
                            {"layer": "removeTop", "rect": "%d,%d,%d,%d" % (x, z, w, h),
                             "doLeavings": False, "readBack": 0})
                ch += r.get("changed") or 0
                ref += r.get("refusedCount") or 0
            print("holes: removeTop %d changed, %d refused over %d runs" % (ch, ref, len(runs)))
            ch = ref = 0
            for (x, z, w, h) in runs:
                r = rb.call("jawa/set_substructure_batch",
                            {"action": "remove", "rect": "%d,%d,%d,%d" % (x, z, w, h),
                             "doLeavings": False, "readBack": 0})
                ch += r.get("changed") or 0
                ref += r.get("refusedCount") or 0
            print("holes: substructure stripped %d, refused %d" % (ch, ref))

        for defn, cells in plan["floors"].items():
            ops = ";".join("%s:%d,%d,%d,%d" % (defn, x, z, w, h) for (x, z, w, h) in rle(cells))
            r = rb.call("jawa/set_terrain_batch", {"ops": ops, "layer": "top", "refresh": False})
            print("floor %-46s changed %s failedVerify %s"
                  % (defn, r.get("cellsChanged"), r.get("cellsFailedVerify")))

        if not args.skip_color:
            done = ref = calls = 0
            for col, cells in plan["floorColor"].items():
                for (x, z, w, h) in rle(cells):
                    r = rb.call("jawa/set_terrain_layer",
                                {"layer": "color", "rect": "%d,%d,%d,%d" % (x, z, w, h),
                                 "def": col, "readBack": 0})
                    done += r.get("changed") or 0
                    ref += r.get("refusedCount") or 0
                    calls += 1
                print("  colour %-40s %d cells" % (col, len(cells)))
            print("floor colour: %d cells set, %d refused, %d calls" % (done, ref, calls))

        rb.call("jawa/refresh_rect", {"rect": "83,59,86,133"})
        m = rb.call("jawa/map_commit", {})
        print("commit %s failedSteps %s   (%.0f s)"
              % (m.get("success"), m.get("failedSteps"), time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
