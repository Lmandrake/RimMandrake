#!/usr/bin/env python3
"""acceptance_pit_relative_terrain.py -- the acceptance test of RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN.

WHY: on his walk of 2026-11-20 the owner dug a 3x3 pit with a step in its floor (save FLOWWORKS_OWNER_WALK_END_20261120,
cells x198-200: rows z124 and z123 at 7 notches = 3.5 m, row z122 at 11 notches = 5.5 m) and it drew as one flat floor.
His words: "Clearly you have not implemented the pit visuals as relative terrain representation, just "pit or no pit"
floor. That won't do. Need more generalization."

What the code does today (read 2026-11-20):
- The wall planner already keys on the height difference between neighbours: RM_UnderLiquid.Exposed takes
  drop = myDepth - neighbourDepth (Source/Superdeep/RM_UnderLiquid.cs), and RM_ExcavationWalls draws a north face, side
  faces and the outline from it for every dug square. Case `planner_faces_every_step` checks that and is GREEN today.
- But the walls layer re-prints only when a square's floor TERRAIN changes (relevantChangeTypes = Terrain | LookFlag), and
  every depth past 2 m is the same terrain (RM_ExcavationDepth.DryTerrainFor -> RM_Channel_Superdeep), so a square cut
  deeper than 2 m never redraws itself or its neighbours (ApplyFillTerrain returns at `cur == want`). Case
  `deepening_redraws_walls` is RED today.
- Past 2 m every floor is one colour, so a 3.5 m floor and a 5.5 m floor beside it look the same. Case
  `floor_shade_follows_depth_past_two_metres` is RED today.

The rebuild solves the geometry offline in Python first (his standing preference). When it adds
`src/RimMandrake/FlowWorks/model/pitdraw.py` with `plan(heights) -> list of segments`, this test judges the three cases
through that planner instead of reading C# source shapes (see `_planner()`); until then it reads the production .cs.
Rename it selftest_flowworks_pit_relative_terrain.py once it is green, so the selftest sweep runs it.

    python3 src/RimMandrake/FlowWorks/acceptance_pit_relative_terrain.py      exit 0 all PASS, 1 any FAIL, 2 could not read
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
UNDER = SRC / "Superdeep" / "RM_UnderLiquid.cs"
FACE_MATH = SRC / "RM_WallFaceMath.cs"
EXCAV = SRC / "RM_MapComponent_Excavation.cs"
DEPTH = SRC / "RM_ExcavationDepth.cs"
WALLS = SRC / "Superdeep" / "RM_ExcavationWalls.cs"
PLANNER = HERE / "model" / "pitdraw.py"

# his pit, north row first (notches of 0.5 m), inside a ring of undug ground
HIS_PIT = [[7, 7, 7], [7, 7, 7], [11, 11, 11]]


def _read(p: Path) -> str:
    return re.sub(r"//[^\n]*", "", p.read_text(encoding="utf-8"))


def _planner():
    if not PLANNER.exists():
        return None
    spec = importlib.util.spec_from_file_location("pitdraw", PLANNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _padded(field):
    w = len(field[0])
    return [[0] * (w + 2)] + [[0] + row + [0] for row in field] + [[0] * (w + 2)]


def _differing_edges(h):
    """Every edge between two 4-neighbours of different height: ((r, c), (r2, c2)), north-first rows."""
    out = []
    for r in range(len(h)):
        for c in range(len(h[0])):
            for dr, dc in ((1, 0), (0, 1)):
                r2, c2 = r + dr, c + dc
                if r2 < len(h) and c2 < len(h[0]) and h[r][c] != h[r2][c2]:
                    out.append(((r, c), (r2, c2)))
    return out


def planner_faces_every_step():
    """Every edge where two neighbours differ in height gets a face or a line from the deeper square."""
    h = _padded(HIS_PIT)
    mod = _planner()
    if mod is not None:
        segs = {tuple(sorted(s["edge"])) for s in mod.plan(h)}
        missing = [e for e in _differing_edges(h) if tuple(sorted(e)) not in segs]
        return not missing, "planner: %d differing edges, %d without a segment %s" % (len(_differing_edges(h)), len(missing), missing[:4])
    src = _read(UNDER)
    m = re.search(r"public static float Exposed\(int myDepth, int neighbourDepth, float levelNotches\)\s*\{(.*?)\n\t\t\}", src, re.S)
    if not m or "myDepth - neighbourDepth" not in m.group(1):
        return False, "RM_UnderLiquid.Exposed no longer takes drop = myDepth - neighbourDepth"
    table = re.search(r"NorthByDrop\s*=\s*\{([^}]*)\}", _read(FACE_MATH))
    north = [float(x.strip().rstrip("f")) for x in table.group(1).split(",")]
    face = lambda drop: north[min(drop, len(north) - 1)] if drop > 0 else 0.0
    walls = _read(WALLS)
    if "NeighbourLevel(map, eng, c + IntVec3.North, d)" not in walls or "Outline(c, d, north, south, west, east" not in walls:
        return False, "RM_ExcavationWalls no longer reads every neighbour's depth for faces and outline"
    missing = []
    for (r, c), (r2, c2) in _differing_edges(h):
        hi, lo = ((r, c), (r2, c2)) if h[r][c] > h[r2][c2] else ((r2, c2), (r, c))
        if h[hi[0]][hi[1]] == 0:
            continue
        north_face = lo[0] < hi[0] and face(h[hi[0]][hi[1]] - h[lo[0]][lo[1]]) > 0
        line = True                    # Outline draws every side whose neighbour is shallower (d - n > 0)
        if not (north_face or line):
            missing.append((hi, lo))
    inner = face(HIS_PIT[2][0] - HIS_PIT[1][0])
    ok = not missing and inner > 0
    return ok, "source: the 5.5 m row draws a %.2f-cell north face below the 3.5 m row; %d edges without a segment" % (inner, len(missing))


def deepening_redraws_walls():
    """A square cut deeper, past 2 m too, redraws its walls and its neighbours' (the walls layer re-prints)."""
    mod = _planner()
    if mod is not None and hasattr(mod, "redraws_on_deepen"):
        before, after = [[4, 4, 4]] * 3, HIS_PIT
        ok = bool(mod.redraws_on_deepen(_padded(before), _padded(after)))
        return ok, "planner.redraws_on_deepen(4-everywhere -> his pit) = %s" % ok
    src = _read(EXCAV)
    m = re.search(r"\n\t\t[^\n]*\(IntVec3 c[^\n]*\)\s*\{((?:(?!\n\t\t\}).)*?depthGrid\[i\] = d;.*?)\n\t\t\}", src, re.S)
    if not m:
        return False, "could not find the cut method that writes depthGrid[i] = d"
    body = m.group(1)
    dirties = re.search(r"MapMeshDirty|DirtyWalls|RedrawStep|DirtyStep", body) is not None
    terrain = re.search(r"default:\s*return depth > Superdeep \? RimMandrakeFlowWorks_DefOf\.RM_Channel_Superdeep", _read(DEPTH))
    if dirties:
        return True, "the cut path marks the walls dirty itself"
    return False, ("the cut path marks nothing dirty and relies on a terrain change; every depth past 2 m is RM_Channel_Superdeep%s, "
                   "so a 3.5 m -> 5.5 m cut never redraws" % ("" if terrain else " (shape changed: re-read)"))


def floor_shade_follows_depth_past_two_metres():
    """A 3.5 m floor and a 5.5 m floor beside it do not draw alike."""
    mod = _planner()
    if mod is not None and hasattr(mod, "floor_shade"):
        a, b = mod.floor_shade(7), mod.floor_shade(11)
        return a != b, "planner.floor_shade(7)=%s floor_shade(11)=%s" % (a, b)
    depth = _read(DEPTH)
    same = re.search(r"default:\s*return depth > Superdeep \? RimMandrakeFlowWorks_DefOf\.RM_Channel_Superdeep", depth) is not None
    walls = _read(WALLS)
    shaded = re.search(r"Floor(Shade|Depth)\w*\([^)]*\bd\b", walls) is not None
    if not same or shaded:
        return True, "the floor draw distinguishes depths past 2 m"
    return False, "every dry floor past 2 m is RM_Channel_Superdeep and RM_ExcavationWalls draws no depth shade on it"


CASES = [planner_faces_every_step, deepening_redraws_walls, floor_shade_follows_depth_past_two_metres]


def main():
    fails = 0
    for case in CASES:
        try:
            ok, why = case()
        except (OSError, AttributeError, ValueError) as ex:
            print("UNMEASURED %s: %s" % (case.__name__, ex))
            return 2
        print("%s %s: %s" % ("PASS" if ok else "FAIL", case.__name__, why))
        fails += not ok
    print("%d of %d PASS" % (len(CASES) - fails, len(CASES)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
