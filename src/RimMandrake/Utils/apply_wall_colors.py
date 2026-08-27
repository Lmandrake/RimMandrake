#!/usr/bin/env python3
"""
apply_wall_colors.py - paint every hull wall of a gravship from a floor-plan.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Run under WINDOWS python (`python.exe`).

🔴 THERE IS NO BRIDGE TOOL FOR BUILDING COLOUR. The only route today is RimWorld's
own dev tool, and its source explains the one trap:

    Verse/DebugToolsGeneral.cs:549  SetColor()
        IntVec3 cell = UI.MouseCell();          <- the MOUSE cell, not a parameter
        ... Find.WindowStack.Add(new FloatMenu(list))
        SetColor_All -> every Thing at that cell gets Thing.SetColor

So it is three calls per wall: `execute_debug_action` (which puts the virtual
mouse on x/z and opens the menu), `get_ui_layout` to find the ColorDef's button —
its targetId is rebuilt every time, so it can never be cached — and
`click_ui_target`. ~2,300 calls for a 770-wall hull, about two minutes.

⚠️ `SetColor_All` colours EVERY thing in the cell, conduits included. Under a wall
that is invisible, but do not point this at a cell holding something you care about.

A companion `[Tool]` calling `Thing.SetColor` over a rect would make this one call.
That needs the game down to deploy, which is why it is not the route here.
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

TOOL = "Actions" + chr(92) + "T: Set Color"


def find_button(rb, want):
    ui = rb.call("rimworld/get_ui_layout", {})
    for s in ui.get("surfaces", []):
        if s.get("type") != "Verse.FloatMenu":
            continue
        els = s.get("elements") or []
        for i, e in enumerate(els):
            if e.get("label") != want:
                continue
            # ⚠️ A FloatMenu opened near the TOP of the screen lays out upward, and the
            # button then precedes its label instead of following it. Looking only
            # forward missed 13 of 772 walls, all on the ship's northern edge.
            for j in range(i + 1, min(i + 3, len(els))):
                if els[j].get("kind") == "button":
                    return els[j].get("targetId")
            for j in range(max(0, i - 2), i):
                if els[j].get("kind") == "button":
                    return els[j].get("targetId")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="stop after N walls (a smoke test)")
    args = ap.parse_args()

    plan = json.load(open(args.plan))
    jobs = []
    for col, cells in plan["wallColor"].items():
        for x, z in cells:
            jobs.append((x, z, col))
    jobs.sort(key=lambda j: (j[1], j[0]))
    if args.limit:
        jobs = jobs[:args.limit]
    print("%d walls, %d colours, ~%d bridge calls"
          % (len(jobs), len(plan["wallColor"]), len(jobs) * 4))
    if not args.apply:
        return 0

    t0 = time.time()
    host, port, token = resolve_endpoint()
    done = collections.Counter()
    misses = []
    with RimBridge(host, port, token, timeout=900.0) as rb:
        # 🔴 Centre the camera on every cell. Measured: a whole-ship view at
        # rootSize 42 dropped 324 of 772 (the 228-entry FloatMenu lands somewhere
        # get_ui_layout pairs differently), while a tight view dropped 13. One extra
        # call per wall buys a menu that always opens mid-screen.
        rb.call("rimworld/set_camera_zoom", {"rootSize": 20})
        for n, (x, z, col) in enumerate(jobs):
            rb.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
            rb.call("rimworld/execute_debug_action", {"path": TOOL, "x": x, "z": z})
            tid = find_button(rb, col)
            if not tid:
                misses.append((x, z, col))
                rb.call("jawa/clear_ui", {"all": True})
                continue
            rb.call("rimworld/click_ui_target", {"targetId": tid})
            done[col] += 1
            if n and n % 150 == 0:
                print("  %d/%d  (%.0f s)" % (n, len(jobs), time.time() - t0))
        rb.call("jawa/clear_ui", {"all": True})
        rb.call("jawa/map_commit", {})
    print("painted %d walls, %d missed the menu, %.0f s"
          % (sum(done.values()), len(misses), time.time() - t0))
    for k, v in done.most_common():
        print("  %-42s %d" % (k, v))
    if misses:
        print("first misses:", misses[:8])
    return 0


if __name__ == "__main__":
    sys.exit(main())
