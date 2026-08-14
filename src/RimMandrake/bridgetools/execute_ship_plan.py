#!/usr/bin/env python3
"""Execute ship_bridge.json against a live map. THE MISSING HALF.

shipbuild.py has emitted a complete build plan -- foundation, terrain, spawn,
in a `buildOrder` -- since it was written, and nothing in this repo has ever
executed it. The v1 gravship has been hand-fed call by call. This is the
executor.

    python.exe src/RimMandrake/bridgetools/execute_ship_plan.py --dry-run
    python.exe src/RimMandrake/bridgetools/execute_ship_plan.py --go
    python.exe src/RimMandrake/bridgetools/execute_ship_plan.py --go --only foundation

FAILURE POLICY -- owner's ruling, 2026-08-13: **stop and report, leave prior
steps applied.** No rollback. Rollback would need snapshot state the companion
does not have, and inventing it is how you paint the wrong map after a load.
A half-built ship on a scratch map is cheap; a stateful companion is not.

⚠️ THE PLAN IS MAP-SPECIFIC. `origin` says "centred on a 250x250 map", and
mapCells run x 82..167, z 58..190. On a smaller map every op silently lands
out of bounds, and `set_terrain_batch` reports cellsOutOfBounds rather than
failing -- which reads as success at a glance. --dry-run checks the extent
against the live map BEFORE writing anything.

⚠️ NEVER RUN THIS ON THE CAMPAIGN SAVE. Quicktest maps only.
"""
import argparse
import json
import os
import sys
import time

# Windows console defaults to cp1252 and dies on any emoji in a print --
# UnicodeEncodeError, mid-run, after the call has already gone out. This must
# run under python.exe (the bridge is unreachable from WSL), so it is not
# avoidable by choosing an interpreter.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))

PLAN = os.path.join(_ROOT, "design", "Jawa", "worldbuilding", "ship_build",
                    "ship_bridge.json")
MAX_CELLS = 70000
MAX_OPS = 4096


def probe_map_size(rb):
    """No companion reply carries mapSize -- measured 2026-08-13, and
    NEXT_RELOAD.md's claim that one does is wrong. Bounds-probe instead:
    read a 1-cell-tall strip wider than any plausible map and let
    cellsOutOfBounds tell us where the edge is."""
    r = rb.call("jawa/get_terrain_batch", {"rects": "0,0,500,1"})
    if not isinstance(r, dict) or r.get("success") is not True:
        raise SystemExit("could not probe map width: %r" % (r,))
    w = r.get("cellsRead", 0)
    r = rb.call("jawa/get_terrain_batch", {"rects": "0,0,1,500"})
    h = r.get("cellsRead", 0)
    return w, h


def op_count(ops):
    return len([o for o in ops.replace("\n", ";").split(";") if o.strip()])


def extent_of(ops):
    """Bounding box over an ops string, so we can compare plan against map."""
    x0 = z0 = 10 ** 9
    x1 = z1 = -10 ** 9
    for o in ops.replace("\n", ";").split(";"):
        o = o.strip()
        if not o:
            continue
        _, _, co = o.rpartition(":")
        p = [q.strip() for q in co.split(",")]
        if len(p) < 2:
            continue
        x, z = int(p[0]), int(p[1])
        w = int(p[2]) if len(p) > 2 else 1
        h = int(p[3]) if len(p) > 3 else 1
        x0, z0 = min(x0, x), min(z0, z)
        x1, z1 = max(x1, x + w - 1), max(z1, z + h - 1)
    return x0, z0, x1, z1


def steps_from(plan, only=None):
    """Flatten the plan into (phase, label, tool, params, expect) tuples."""
    out = []
    for phase in plan["buildOrder"]:
        if only and phase != only:
            continue
        if phase == "foundation":
            f = plan["foundation"]
            out.append((phase, "Substructure", f["tool"],
                        {"ops": f["ops"], "terrainDef": f["terrainDef"],
                         "layer": f["layer"], "refresh": False},
                        {"cells": f["cells"]}))
        elif phase == "terrain":
            for name, t in plan["terrain"].items():
                out.append((phase, name, "jawa/set_terrain_batch",
                            {"ops": t["ops"], "terrainDef": name,
                             "layer": "top", "refresh": False},
                            {"cells": t["cells"]}))
        elif phase == "spawn":
            for s in plan["spawn"]:
                p = {"ops": s["ops"], "defName": s["defName"]}
                if s.get("stuff"):
                    p["stuff"] = s["stuff"]
                # ⚠️ The plan writes rot: 0 for everything, including the four
                # machines it ALSO flags needsManualRotation -- the flag is the
                # emitter saying "I could not decide this, a human must".
                # CREATE's ruling (row8_build_order.md): those four spawn at
                # rot=1, one call each, no separate rotation step. Honour the
                # FLAG over the zero, or they land facing the wrong way and
                # nothing errors.
                rot = 1 if s.get("needsManualRotation") else s.get("rot")
                if rot:
                    p["rot"] = rot
                out.append((phase, s["defName"], s["tool"], p,
                            {"count": s.get("count")}))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=PLAN)
    ap.add_argument("--go", action="store_true",
                    help="actually write. Without it, this is a dry run.")
    ap.add_argument("--only", choices=["foundation", "terrain", "spawn"])
    ap.add_argument("--stop-on-fail", default=True)
    a = ap.parse_args()

    plan = json.load(open(a.plan))
    steps = steps_from(plan, a.only)
    mc = plan["mapCells"]
    print("plan %s" % a.plan)
    print("  origin %s" % plan["origin"])
    print("  hull %sx%s, mapCells x %d..%d z %d..%d"
          % (plan["hullExtent"]["w"], plan["hullExtent"]["h"],
             mc["x0"], mc["x1"], mc["z0"], mc["z1"]))
    print("  %d steps across %s" % (len(steps), plan["buildOrder"]))
    for c in plan.get("footprintConflicts", []):
        print("  ⚠️ known conflict: %s at %s inside %s"
              % (c.get("type"), c.get("at"), c.get("insideMachine")))

    # RimBridge() alone connects to nothing useful: the constructor takes an
    # explicit host/port/token and does NOT open the socket, and the token is
    # regenerated every game start. resolve_endpoint scrapes it out of
    # Player.log, which is what the CLI does.
    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint(None, None, None, None)
    if not token:
        raise SystemExit("no bridge token found -- is RimWorld running?")
    rb = RimBridge(host, port, token, timeout=120.0)
    rb.connect()

    mw, mh = probe_map_size(rb)
    print("\nlive map measured %dx%d" % (mw, mh))
    if mc["x1"] >= mw or mc["z1"] >= mh:
        raise SystemExit(
            "🔴 PLAN DOES NOT FIT. Plan needs x..%d z..%d, map is %dx%d.\n"
            "   Every op past the edge would be counted out-of-bounds and the\n"
            "   call would still report success. Refusing."
            % (mc["x1"], mc["z1"], mw, mh))
    print("   fits.")

    # Budget preflight across the WHOLE plan, not per call -- the per-call
    # guard in the companion cannot see that step 12 follows step 11.
    print("\nbudget preflight:")
    bad = False
    for phase, label, tool, params, expect in steps:
        n = op_count(params["ops"])
        x0, z0, x1, z1 = extent_of(params["ops"])
        flag = ""
        if n > MAX_OPS:
            flag = " 🔴 OVER MaxOps %d" % MAX_OPS
            bad = True
        if x1 >= mw or z1 >= mh or x0 < 0 or z0 < 0:
            flag += " 🔴 OUT OF BOUNDS"
            bad = True
        print("  %-10s %-22s %5d ops  x %3d..%3d z %3d..%3d%s"
              % (phase, label, n, x0, x1, z0, z1, flag))
    if bad:
        raise SystemExit("refusing: fix the plan or the map first.")

    if not a.go:
        print("\nDRY RUN. Nothing written. Re-run with --go.")
        return

    print("\nexecuting -- stop on first failure, no rollback")
    applied = []
    t0 = time.time()
    for i, (phase, label, tool, params, expect) in enumerate(steps, 1):
        r = rb.call(tool, params)
        ok = isinstance(r, dict) and r.get("success") is True
        # Read-back: the companion already returns counts. Trust the COUNT,
        # never the flag alone.
        got = (r or {}).get("cellsChanged")
        if got is None:
            got = (r or {}).get("spawned", (r or {}).get("thingsSpawned"))
        oob = (r or {}).get("cellsOutOfBounds", 0)
        print("  %2d/%2d %-10s %-22s success=%-5s changed=%-6s oob=%s"
              % (i, len(steps), phase, label, ok, got, oob))
        if not ok:
            print("     message: %s" % (r or {}).get("message"))
            print("\n🔴 STOPPED at step %d of %d. %d steps applied and LEFT "
                  "APPLIED (owner's ruling: no rollback)."
                  % (i, len(steps), len(applied)))
            print("   Applied: %s" % ", ".join(applied))
            sys.exit(1)
        if oob:
            print("     ⚠️ %d cells out of bounds -- silently dropped by the "
                  "game. This step is INCOMPLETE despite success=true." % oob)
        applied.append("%s/%s" % (phase, label))

    print("\nall %d steps applied in %.1fs" % (len(steps), time.time() - t0))
    print("⚠️ Applied is not verified. Refresh the mesh and LOOK at it:")
    print("   jawa/refresh_rect, then jump_camera_to_cell + take_screenshot.")


if __name__ == "__main__":
    main()
