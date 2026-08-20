#!/usr/bin/env python3
"""
prove_set_terrain.py - prove jawa/set_terrain actually changes the map.

WHAT COUNTS AS PROOF
====================
Not `success: true`. The standing law of this bridge is that success means the
tool RAN, not that the game CHANGED - RimWorld's own `Set terrain (rect)` debug
action returns success and does nothing at all, which is the exact failure this
companion exists to fix. So the test never trusts the tool's own word:

  1. read the cell with rimworld/get_cell_info      -> terrainDefName BEFORE
  2. call jawa/set_terrain                          -> the claim
  3. read the cell again with get_cell_info         -> terrainDefName AFTER
  4. PASS only if step 3 shows the terrain we asked for

Step 3 is a different tool, in a different assembly, reading the grid fresh.
That is the independent channel.

It also screenshots before and after, because a grid value that is correct while
the screen still shows old ground is a real and specific risk that
`design/RimMandrake/map_authoring_decision.md` lists as an open question: terrain lives in a
cached map mesh, so a change can be true and invisible.

LEAVES NO TRACE
===============
Reverts to the original terrain by default, which doubles as a second proof
(set_terrain works in both directions). Pass --keep to leave the painted cell.

USAGE
  python src/RimMandrake/bridgetools/prove_set_terrain.py                    # centre of the map
  python src/RimMandrake/bridgetools/prove_set_terrain.py --x 130 --z 118
  python src/RimMandrake/bridgetools/prove_set_terrain.py --terrain Sand --keep
  python src/RimMandrake/bridgetools/prove_set_terrain.py --rect 8 8         # prove a rectangle
"""

import argparse
import json
import os
import sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "Utils"))
from rimbridge_client import RimBridge, RimBridgeError, resolve_endpoint  # noqa: E402

TOOL = "jawa/set_terrain"


def say(ok, label, detail=""):
    print("  [%s] %-42s %s" % ("PASS" if ok else "FAIL", label, detail))
    return ok


def terrain_at(rb, x, z):
    r = rb.call("rimworld/get_cell_info", {"x": x, "z": z}) or {}
    return (r.get("cell") or {}).get("terrainDefName")


def shot(rb, name, x, z, pad):
    """Best-effort visual evidence. Never fail the run over a screenshot."""
    try:
        r = rb.call("rimworld/screenshot_cell_rect",
                    {"fileName": name, "cellX": x, "cellZ": z, "paddingCells": pad})
        return (r or {}).get("path") or (r or {}).get("filePath")
    except RimBridgeError as ex:
        print("    (screenshot skipped: %s)" % ex)
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--x", type=int, help="cell X (default: map centre)")
    ap.add_argument("--z", type=int, help="cell Z (default: map centre)")
    ap.add_argument("--terrain", default="Sand", help="TerrainDef to paint (default Sand)")
    ap.add_argument("--rect", nargs=2, type=int, metavar=("W", "H"), default=[1, 1])
    ap.add_argument("--keep", action="store_true", help="do not revert afterwards")
    ap.add_argument("--no-shots", action="store_true")
    args = ap.parse_args(argv)

    host, port, token = resolve_endpoint()
    if not token:
        return say(False, "bridge token found in Player.log", "is RimWorld running?") or 2

    w, h = args.rect
    failures = 0

    with RimBridge(host, port, token, timeout=120.0) as rb:
        # -- 1. is the companion even loaded? -----------------------------
        print("\n1. companion discovery")
        status = rb.call("rimbridge/get_bridge_status", {}) or {}
        comp = status.get("companions", {}) or {}
        sdk = status.get("sdk", {}) or {}
        diags = comp.get("diagnostics") or []

        if not say(comp.get("totalCount", 0) >= 1, "companion assemblies loaded",
                   "totalCount=%s registeredTools=%s" % (comp.get("totalCount"),
                                                         comp.get("registeredToolCount"))):
            failures += 1
        if diags:
            print("    diagnostics: %s" % json.dumps(diags)[:600])
        if sdk.get("companionErrorCount"):
            print("    SDK errors: %s" % sdk.get("companionErrorCount"))
            failures += 1

        names = [t.get("name") for t in rb.list_tools()]
        if not say(TOOL in names, "%s registered" % TOOL,
                   "%d tools total" % len(names)):
            print("\n    %s is NOT on the bridge. Check, in this order:" % TOOL)
            print("      - <RimWorld>/BridgeTools/JawaBench/JawaBench.BridgeTools.dll exists")
            print("      - Player.log for '[RimBridge]' companion discovery lines")
            print("      - the game was restarted AFTER the DLL was deployed")
            return 1

        # -- 2. where are we painting? ------------------------------------
        info = rb.call("rimworld/get_game_info", {}) or {}
        x, z = args.x, args.z
        if x is None or z is None:
            size = info.get("mapSize") or {}
            x = x if x is not None else int(size.get("x", 250)) // 2
            z = z if z is not None else int(size.get("z", size.get("y", 250))) // 2

        print("\n2. target cell (%d, %d), rect %dx%d, paint %s" % (x, z, w, h, args.terrain))
        before = terrain_at(rb, x, z)
        print("    terrain before: %s" % before)
        if before == args.terrain:
            print("    NOTE: cell is already %s - switching to Gravel so the test"
                  " can actually observe a change." % args.terrain)
            args.terrain = "Gravel" if args.terrain != "Gravel" else "Sand"

        before_shot = None if args.no_shots else shot(rb, "setterrain-before", x, z,
                                                      max(w, h) + 4)

        # -- 3. the call ---------------------------------------------------
        print("\n3. %s" % TOOL)
        t0 = time.perf_counter()
        res = rb.call(TOOL, {"x": x, "z": z, "terrainDef": args.terrain,
                             "width": w, "height": h}) or {}
        ms = (time.perf_counter() - t0) * 1000.0
        payload = {k: v for k, v in res.items() if k not in ("state", "operation")}
        print("    %.2f ms  %s" % (ms, json.dumps(payload)[:500]))
        if not say(res.get("success") is True, "tool reported success",
                   res.get("message", "")):
            failures += 1

        # -- 4. the independent channel ------------------------------------
        print("\n4. independent read-back (get_cell_info)")
        after = terrain_at(rb, x, z)
        if not say(after == args.terrain, "anchor cell is now %s" % args.terrain,
                   "%s -> %s" % (before, after)):
            failures += 1

        if w * h > 1:
            corner = terrain_at(rb, x + w - 1, z + h - 1)
            if not say(corner == args.terrain,
                       "far corner (%d,%d) is now %s" % (x + w - 1, z + h - 1, args.terrain),
                       str(corner)):
                failures += 1
            outside = terrain_at(rb, x + w, z + h)
            if not say(outside != args.terrain or outside == before,
                       "cell outside the rect untouched", str(outside)):
                failures += 1

        after_shot = None if args.no_shots else shot(rb, "setterrain-after", x, z,
                                                     max(w, h) + 4)

        # -- 5. revert ------------------------------------------------------
        if not args.keep and before:
            print("\n5. revert to %s" % before)
            rb.call(TOOL, {"x": x, "z": z, "terrainDef": before,
                           "width": w, "height": h})
            back = terrain_at(rb, x, z)
            if not say(back == before, "reverted cleanly", "%s" % back):
                failures += 1
        else:
            print("\n5. revert skipped (--keep); cell left as %s" % args.terrain)

    print("\n" + "=" * 64)
    if before_shot:
        print("before: file:///%s" % str(before_shot).replace("\\", "/").replace(" ", "%20"))
    if after_shot:
        print("after : file:///%s" % str(after_shot).replace("\\", "/").replace(" ", "%20"))
    print("RESULT: %s" % ("PASS - terrain painting works over the bridge"
                          if failures == 0 else "FAIL - %d check(s) failed" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
