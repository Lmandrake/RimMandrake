#!/usr/bin/env python3
"""
repaint_hull.py - paint the gravship hull with the VANILLA paint system.

    python.exe src/RimMandrake/Utils/repaint_hull.py --plan <plan.json>            # dry plan
    python.exe src/RimMandrake/Utils/repaint_hull.py --plan <plan.json> --apply
    python.exe src/RimMandrake/Utils/repaint_hull.py --census "83,59,86,133"       # read back

The dev "T: Set Color" UI route (~380-invocation session budget, then silent
FloatMenu misses) and the colour-as-material route are both dead ends; this is
the only wall-colour tool.

`jawa/paint_building` (companion surface 239, built 2026-08-28) calls
Building.ChangePaint(ColorDef) directly - the same persistent, savegame-scribed
paint as the in-game designator, one bridge call per colour chunk instead of three
per wall, no session budget, removable in play. GravshipHull inherits Wall's
paintable=true, so the hull can be an HONEST material (Steel, Plasteel) and carry
its Corrosion Halo as PAINT.

The plan format: {"wallColor": {"<ColorDef>": [[x,z],...]}}.
Colour names must be real ColorDefs (63 Structure_* names ship in Core); a wrong
name is refused by the tool with suggestions, never silently skipped.

⚠️ python.exe, never python3 - the bridge binds Windows loopback.
⚠️ The tool must be DEPLOYED first (game-down window, build.py --gm --apply) and the
   game restarted - a companion registers at startup only.
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rimbridge_client import RimBridge, resolve_endpoint     # noqa: E402

CHUNK = 300      # cells per bridge call - well under the batch conventions


def unwrap(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            return json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", help="wallColor plan JSON: {'wallColor': {'<ColorDef>': [[x,z],...]}}")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--census", metavar="RECT",
                    help="no painting: report current paint by def/colour over 'x,z,w,h'")
    ap.add_argument("--def-name", default="GravshipHull",
                    help="only paint this ThingDef (default GravshipHull); '' = everything paintable")
    args = ap.parse_args()

    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=900.0) as rb:
        if args.census:
            r = unwrap(rb.call("jawa/paint_building", {"rect": args.census}))
            print(json.dumps(r, indent=2)[:4000])
            return 0

        if not args.plan:
            ap.error("--plan or --census is required")
        plan = json.load(open(args.plan))
        groups = {col: [tuple(c) for c in cells]
                  for col, cells in plan["wallColor"].items()}
        total = sum(len(v) for v in groups.values())
        print("%d walls, %d colours, ~%d bridge calls"
              % (total, len(groups), sum((len(v) + CHUNK - 1) // CHUNK for v in groups.values())))
        if not args.apply:
            return 0

        grand = collections.Counter()
        for col, cells in groups.items():
            for i in range(0, len(cells), CHUNK):
                chunk = cells[i:i + CHUNK]
                r = unwrap(rb.call("jawa/paint_building", {
                    "cells": ";".join("%d,%d" % c for c in chunk),
                    "colorDef": col, "defName": args.def_name or None}))
                if not r.get("success"):
                    print("REFUSED %s: %s" % (col, r))
                    return 2
                for k in ("painted", "verified", "alreadyThatColor", "notPaintable"):
                    grand[k] += r.get(k) or 0
                grand[("colour", col)] += r.get("verified") or 0
        print("painted %(painted)d, verified %(verified)d, already %(alreadyThatColor)d, "
              "notPaintable %(notPaintable)d" % grand)
        for k, v in grand.items():
            if isinstance(k, tuple):
                print("  %-42s %d" % (k[1], v))
        if grand["verified"] != grand["painted"]:
            print("⚠️ verified != painted - read the census before trusting this run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
