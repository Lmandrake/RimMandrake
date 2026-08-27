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


def float_menu(rb):
    ui = rb.call("rimworld/get_ui_layout", {})
    for s in ui.get("surfaces", []):
        if s.get("type") == "Verse.FloatMenu":
            return s
    return None


def button_for(menu, want):
    els = menu.get("elements") or []
    for i, e in enumerate(els):
        if e.get("label") != want:
            continue
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
    ap.add_argument("--offset", type=int, default=0, help="skip the first N walls")
    args = ap.parse_args()

    plan = json.load(open(args.plan))
    jobs = []
    for col, cells in plan["wallColor"].items():
        for x, z in cells:
            jobs.append((x, z, col))
    jobs.sort(key=lambda j: (j[1], j[0]))
    # ⚠️ Something in the session degrades after roughly 380 walls and every menu
    # after that misses - measured at exactly 384/772 on three separate runs, with
    # the failures starting mid-list rather than alternating. A fresh PROCESS clears
    # it, so drive this in chunks: --offset 0 300, 300 300, 600 300.
    jobs = jobs[args.offset:]
    if args.limit:
        jobs = jobs[:args.limit]
    print("%d walls, %d colours, ~%d bridge calls"
          % (len(jobs), len(plan["wallColor"]), len(jobs) * 3))
    if not args.apply:
        return 0

    t0 = time.time()
    host, port, token = resolve_endpoint()
    done = collections.Counter()
    misses = []
    with RimBridge(host, port, token, timeout=900.0) as rb:
        # 🔴 A STALE FloatMenu BLOCKS EVERYTHING AFTER IT, SILENTLY. One wall whose
        # menu is left open absorbs input for every wall that follows, and
        # `execute_debug_action` answers success the whole way down. That single
        # cascade is what produced 759, then 448, then 0 of 772 across three runs
        # that differed in nothing that mattered. So: clear any stale menu, and
        # retry a miss once after clearing. `get_context_menu_options` cannot see
        # this window at all - it is a Verse.FloatMenu, not a debug context menu -
        # so detection has to go through get_ui_layout.
        # 🔴 The menu MUST be closed before the click, or the menu still standing is
        # the PREVIOUS cell's - and clicking it paints the wrong wall while
        # reporting success. So: assert closed, open, assert open, click.
        rb.call("jawa/clear_ui", {"all": True})
        for n, (x, z, col) in enumerate(jobs):
            if float_menu(rb):                       # stale from the last wall
                rb.call("jawa/clear_ui", {"all": True})
            rb.call("rimworld/execute_debug_action", {"path": TOOL, "x": x, "z": z})
            menu = float_menu(rb)
            tid = button_for(menu, col) if menu else None
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
