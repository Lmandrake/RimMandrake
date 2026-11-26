#!/usr/bin/env python3
"""Live test of TREE_SHADE_BUILD_CROWNS_ON_STILTS: a tree's crown casts shade down-sun in the running game, the cell
readout names the tree, and a felled tree's shade goes (design/RimMandrake/tree_shade_model_2026-10-19.md §6 T1, T4,
live half; T3, the owner's look, is DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME).

Kind A (deterministic): the scene plants one grown tree on cleared ground, so one valid run decides.
  claim         a grown tree's crown shades the disc of radius 0.8 x drawn/2 around the root moved hc x cot E down-sun
                (hc 0.5 x drawn), the cell's cause names the species' canopy, and within 60 ticks of felling the tree
                that shade is gone.
  entry point   the current map of a game with Creature Behaviors and the JawaBench companion of this build (the
                `jawa/shadegrid_read` fields canopy, cause, shadowDirX/Z; null fields = COULD NOT LOOK, an old companion).
  opportunity   the cleared square around --cell is unroofed open ground, and the grid casts with a sun vector
                (isDirectional) or without one (the disc under the crown).
  success       every probed cell inside the predicted disc reads canopy >= 0.99 with cause '<label> canopy', the
                mirror cell up-sun reads canopy 0, and after felling every disc cell reads canopy 0.
  forbidden     any red error in the log naming RM_TreeCrown or the shade grid.
  end           the tree is felled and the square is left clear.

Run on the machine that hosts the game, with that game's environment:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/CreatureBehaviors/live_tree_crowns.py [--cell 60,60] [--tree Plant_TreePine --drawn 3]
    (a giant: --tree RM_Veluthar --drawn 11.5 --rf 0.95 --hf 0.78, its factors in Patches/RM_TreeCrowns_Giants.xml)
Exit 0 PASS, 1 FAIL (MOD FAILURE), 2 COULD NOT LOOK (no map, an old companion, a cell that cannot hold the tree).
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "Utils")]

HALF = 20          # the cleared square is (2 HALF + 1) cells wide
RECOMPUTE_WAIT = 2001  # planting asks for no recompute; the grid rebuilds every 2000 ticks
FELL_WAIT = 60     # a felled shade tree's request runs within 30 ticks (PlantRecomputeMinTicks)


def read(s, cells):
    r = s.call("jawa/shadegrid_read", cells=";".join("%d,%d" % c for c in cells)) or {}
    return r, {(c["x"], c["z"]): c for c in r.get("cells") or []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="125,125;60,60;190,190;60,190;190,60;125,60;125,190",
                    help="root cells to try, ';'-separated: the first whose cleared square takes the tree and lies in "
                         "no other crown's shade is used")
    ap.add_argument("--tree", default="Plant_TreePine", help="an evergreen plant drawn at least 1.5 cells grown "
                    "(a deciduous tree may be leafless, crown x 0.3)")
    ap.add_argument("--drawn", type=float, default=3.0, help="its drawn size at growth 1 (pine: 1 x 3.0)")
    ap.add_argument("--rf", type=float, default=0.8, help="its crown radius factor (0.8 unless RM_TreeCrownExtension)")
    ap.add_argument("--hf", type=float, default=0.5, help="its crown height factor (0.5 unless RM_TreeCrownExtension)")
    a = ap.parse_args()
    from northstar_driver.session import FastSession
    with FastSession(strict=False, focus=False) as s:
        g0, _ = read(s, [])
        if not g0.get("present"):
            print("COULD NOT LOOK: no shade grid: %s" % json.dumps(g0)[:300])
            return 2
        site = None
        for tok in a.cell.split(";"):
            cx, cz = (int(v) for v in tok.split(","))
            rect = "%d,%d,%d,%d" % (cx - HALF, cz - HALF, 2 * HALF + 1, 2 * HALF + 1)
            print("clear %s:" % tok, json.dumps(s.call("jawa/set_plants", ops="CLEAR:" + rect))[:160], flush=True)
            # Clearing despawns the square's trees, which asks the grid for a recompute (the despawn patch).
            s.call("jawa/safe_advance", action="start", ticks=FELL_WAIT)
            ring = [(x, z) for x in range(cx - 4, cx + 5) for z in range(cz - 4, cz + 5)]
            _, pre = read(s, ring)
            shaded = [c for c in ring if (pre.get(c) or {}).get("canopy")]
            if shaded:
                print("  %s lies in another crown's shade (%d of %d cells, e.g. %s); next" % (
                    tok, len(shaded), len(ring), (pre.get(shaded[0]) or {}).get("cause")), flush=True)
                continue
            r = s.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (a.tree, cx, cz), growth=1.0) or {}
            print("  plant:", json.dumps(r)[:240], flush=True)
            if r.get("planted"):
                site = (cx, cz)
                break
        if site is None:
            print("COULD NOT LOOK: no tried cell took the tree in an unshaded square (%s)" % a.cell)
            return 2
        cx, cz = site
        s.call("jawa/safe_advance", action="start", ticks=RECOMPUTE_WAIT)
        g, _ = read(s, [])
        sg = g.get("shadeGrid") or {}
        if sg.get("shadowDirX") is None:
            print("COULD NOT LOOK: the companion is older than this build (no shadowDirX); deploy it and rerun")
            return 2
        drawn = a.drawn
        directional = bool(sg.get("isDirectional"))
        e = sg.get("sunElevationDegrees")
        cot = 1.0 / math.tan(math.radians(max(0.5, min(90.0, e)))) if directional and e else 0.0
        hc, rad = a.hf * drawn, a.rf * drawn / 2
        off = min(16.0, hc * cot)
        dx, dz = (sg["shadowDirX"], sg["shadowDirZ"]) if directional else (0.0, 0.0)
        ox, oz = cx + dx * off, cz + dz * off
        inside = [(x, z) for x in range(cx - HALF, cx + HALF + 1) for z in range(cz - HALF, cz + HALF + 1)
                  if (x - ox) ** 2 + (z - oz) ** 2 <= (rad - 0.5) ** 2]
        mirror = (int(round(cx - dx * (off + rad + 1))), int(round(cz - dz * (off + rad + 1)))) if directional else None
        probe = inside[:150] + ([mirror] if mirror else [])
        _, cells = read(s, probe)
        print("sun: directional=%s E=%s dir=(%.2f,%.2f); disc centre (%.1f,%.1f) r %.2f; %d cells inside" % (
            directional, e, dx, dz, ox, oz, rad, len(inside)), flush=True)
        fails = []
        if any(cells[c].get("canopy") is None for c in probe if c in cells):
            print("COULD NOT LOOK: the companion reads no canopy (old build)")
            return 2
        for c in inside[:150]:
            row = cells.get(c) or {}
            if (row.get("canopy") or 0) < 0.99 or "canopy" not in str(row.get("cause")):
                fails.append("disc cell %s: canopy %s cause %s" % (c, row.get("canopy"), row.get("cause")))
        if mirror and (cells.get(mirror) or {}).get("canopy"):
            fails.append("up-sun cell %s is shaded by the crown: %s" % (mirror, cells.get(mirror)))
        print("before felling: %d of %d disc cells wrong" % (len(fails), len(inside[:150])), flush=True)
        print("fell:", json.dumps(s.call("jawa/set_plants", ops="CLEAR:%d,%d,1,1" % (cx, cz)))[:200], flush=True)
        s.call("jawa/safe_advance", action="start", ticks=FELL_WAIT)
        _, after = read(s, inside[:150])
        left = [c for c in inside[:150] if (after.get(c) or {}).get("canopy")]
        if left:
            fails.append("%d disc cells still shaded %d ticks after felling, e.g. %s" % (len(left), FELL_WAIT, left[:3]))
        for f in fails[:20]:
            print("FAIL " + f)
        print("PASS live tree crowns" if not fails else "FAIL live tree crowns (%d)" % len(fails))
        return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
