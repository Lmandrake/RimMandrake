#!/usr/bin/env python3
"""selftest_flowworks_pit_relative_terrain.py -- RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (was its acceptance test,
acceptance_pit_relative_terrain.py, renamed once green as the ticket asked).

WHY: on his walk of 2026-11-20 the owner dug a 3x3 pit with a step in its floor (save FLOWWORKS_OWNER_WALK_END_20261120,
cells x198-200: rows z124 and z123 at 7 notches = 3.5 m, row z122 at 11 notches = 5.5 m) and it drew as one flat floor.
His words: "Clearly you have not implemented the pit visuals as relative terrain representation, just "pit or no pit"
floor. That won't do. Need more generalization."

What the code did (read 2026-11-20, base 4f5b97b652; this file read 1 of 3 PASS there, watched red):
- The wall planner already keyed on the height difference between neighbours (RM_UnderLiquid.Exposed, drop = myDepth -
  neighbourDepth). Case `planner_faces_every_step` was GREEN.
- But the walls layer re-printed only when a square's floor TERRAIN changed, and every depth past 2 m is the same terrain,
  so a square cut deeper than 2 m never redrew itself or its neighbours. Case `deepening_redraws_walls` was RED.
- Past 2 m every floor was one colour. Case `floor_shade_follows_depth_past_two_metres` was RED.

The rebuild solved the geometry offline first (model/pitdraw.py, his standing preference) and ported it to
Source/RM_PitReliefMath.cs. This selftest now judges each case through BOTH: the model (which the sweep below reads over the
whole range of situations) and the shipped C# (its call sites, and the golden table SelfTest/PitReliefParityChecks.cs checks
RM_PitReliefMath against; `--write` regenerates that table from the model). The C# parity cases themselves run in the
FlowWorks C# SelfTest: `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only PitRelief_*`.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_pit_relative_terrain.py [--write]   exit 0 all PASS, 1 any FAIL, 2 could not read
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
UNDER = SRC / "Superdeep" / "RM_UnderLiquid.cs"
EXCAV = SRC / "RM_MapComponent_Excavation.cs"
DEPTH = SRC / "RM_ExcavationDepth.cs"
WALLS = SRC / "Superdeep" / "RM_ExcavationWalls.cs"
RELIEF = SRC / "RM_PitReliefMath.cs"
DECK = SRC / "Pits" / "Building_SpanDeck.cs"
PARITY = SRC / "SelfTest" / "PitReliefParityChecks.cs"
PROGRAM = SRC / "SelfTest" / "Program.cs"
TEST_CSPROJ = SRC / "SelfTest" / "RimMandrakeFlowWorks.SelfTest.csproj"
MOD_CSPROJ = SRC / "RimMandrake_FlowWorks.csproj"
PLANNER = HERE / "model" / "pitdraw.py"
BEGIN, END = "// BEGIN GOLDEN (selftest_flowworks_pit_relative_terrain.py --write)", "// END GOLDEN"

# his pit, north row first (notches of 0.5 m), inside a ring of undug ground
HIS_PIT = [[7, 7, 7], [7, 7, 7], [11, 11, 11]]


def _read(p: Path) -> str:
    return re.sub(r"//[^\n]*", "", p.read_text(encoding="utf-8"))


def _planner():
    spec = importlib.util.spec_from_file_location("pitdraw", PLANNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _padded(field):
    w = len(field[0])
    return [[0] * (w + 2)] + [[0] + row + [0] for row in field] + [[0] * (w + 2)]


def _differing_edges(h):
    out = []
    for r in range(len(h)):
        for c in range(len(h[0])):
            for dr, dc in ((1, 0), (0, 1)):
                r2, c2 = r + dr, c + dc
                if r2 < len(h) and c2 < len(h[0]) and h[r][c] != h[r2][c2]:
                    out.append(((r, c), (r2, c2)))
    return out


def _method(src: str, marker: str) -> str:
    """The body of the method whose text holds `marker` (two-tab method bodies, as the acceptance test read them)."""
    for m in re.finditer(r"\n\t\t[^\n]*\([^\n]*\)\s*\{((?:(?!\n\t\t\}).)*?)\n\t\t\}", src, re.S):
        if marker in m.group(1):
            return m.group(1)
    return ""


def planner_faces_every_step():
    """Every edge where two neighbours differ in height gets a face or a line from the deeper square (his pit, the model),
    and the shipped layer still reads every neighbour's depth for faces and outline."""
    h = _padded(HIS_PIT)
    mod = _planner()
    segs = mod.plan(h)
    have = {tuple(sorted(s["edge"])) for s in segs}
    missing = [e for e in _differing_edges(h) if tuple(sorted(e)) not in have]
    inner = [s for s in segs if s["kind"] == "north_face" and s["cell"][0] == 3]   # the 5.5 m row's face below the 3.5 m row
    walls = _read(WALLS)
    src_ok = ("NeighbourLevel(map, eng, c + IntVec3.North, d)" in walls and "Outline(c, d, north, south, west, east" in walls
              and "CornerLines(c, d, north, south, west, east, nw, ne, sw, se" in walls)
    ok = not missing and len(inner) == 3 and src_ok
    return ok, "planner: %d differing edges, %d without a segment; the 5.5 m row draws %d inner north faces (%.2f cells); source reads all 8 neighbours: %s" % (
        len(_differing_edges(h)), len(missing), len(inner), inner[0]["size"] if inner else 0.0, src_ok)


def deepening_redraws_walls():
    """A square cut deeper (or filled), past 2 m too, redraws its walls and its neighbours': in the model (locality) and in the
    shipped cut and fill paths (RedrawStep on every depth write), and a deck laid or lifted redraws too."""
    mod = _planner()
    before, after = [[4, 4, 4]] * 3, HIS_PIT
    model_ok = bool(mod.redraws_on_deepen(_padded(before), _padded(after)))
    src = _read(EXCAV)
    deepen = _method(src, "depthGrid[i] = d;")
    fill = _method(src, "depthGrid[i] = newD;")
    deck = _read(DECK)
    spawn = _method(deck, "base.SpawnSetup(map, respawningAfterLoad);")
    despawn = _method(deck, "base.DeSpawn(mode);")
    walls = _read(WALLS)
    helper = re.search(r"public static void RedrawStep\(Map map, IntVec3 c\)\s*\{(.*?)\n\t\t\}", walls, re.S)
    # the 4-argument form: the 2-argument MapMeshDirty dirties the neighbours' sections only for FogOfWar|Buildings|Roofs (1.6)
    # RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM: the cast shadow reads two squares toward the sun, so the
    # helper may dirty each of the 3x3 (GenAdj.AdjacentCellsAndInside) with its adjacent cells: the 5x5; a low sun reaches 2
    # squares (step 3, 2026-11-22), so the helper dirties each of the 5x5 (dx, dz in -2..2) with its adjacent cells: the 7x7
    body = helper.group(1) if helper else ""
    helper_ok = bool(helper and ("MapMeshDirty(c," in body or ("MapMeshDirty(q," in body and (
        "AdjacentCellsAndInside" in body or re.search(r"dx = -2; dx <= 2.*dz = -2; dz <= 2|dz = -2; dz <= 2.*dx = -2; dx <= 2", body, re.S))))
                     and "regenAdjacentCells: true" in body)
    calls = {name: "SectionLayer_RMExcavationWalls.RedrawStep(map, " in body
             for name, body in (("deepen", deepen), ("fill_in", fill), ("deck_spawn", spawn), ("deck_despawn", despawn))}
    ok = model_ok and helper_ok and all(calls.values())
    return ok, "model redraws_on_deepen(4-everywhere -> his pit) = %s; RedrawStep dirties the mesh: %s; calls %s" % (model_ok, helper_ok, calls)


def floor_shade_follows_depth_past_two_metres():
    """A 3.5 m floor and a 5.5 m floor beside it do not draw alike: in the model and in the shipped layer's floor shade."""
    mod = _planner()
    a, b = mod.floor_shade(7), mod.floor_shade(11)
    walls = _read(WALLS)
    dry = re.search(r"FloorShade\(c, d, ww, ew, h, wnw, hnw, wne, hne,", walls) is not None
    # a drowned floor is the dry pit's floor under one sheet (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE): the
    # same floor shade runs for a square under a clear liquid
    wet = "ReliefCell(map, eng, c, d, sp, note == 0 || sheet, sc, y);" in walls and "if (note == 0 || sheet)" in walls
    ok = a != b and dry and wet
    return ok, "model floor_shade(7)=%s floor_shade(11)=%s; layer shades dry floors %s, drowned floors %s" % (a, b, dry, wet)


def model_sweep():
    """The model over the whole range of situations (pitdraw.sweep): every check's worst value within its limit."""
    rows, fails = _planner().sweep()
    worst = [r for r in rows if r[0].startswith("random fields")]
    return not fails, "%d checks, %d failures%s; random fields: %d cases" % (len(rows), len(fails), (" first " + str(fails[0])[:160]) if fails else "",
                                                                              worst[0][3] if worst else 0)


# ── the golden tables for the C# parity checks ──

def _f(x):
    return "%sf" % repr(round(float(x), 5))


def golden_block(mod) -> str:
    floor = ["\t\t\t{ %s, %s }," % (_f(d), _f(mod.floor_shade(d))) for d in range(0, 45)]
    feet = [0, 2, 4.5, 5, 5.25, 5.5, 6, 7, 8, 10, 11, 12.75, 15, 20, 30, 40, 60]
    foot = ["\t\t\t{ %s, %s }," % (_f(e), _f(mod.face_foot_shade(e))) for e in feet]
    corner = []
    for d in (1, 3, 4, 7, 11, 40):
        for dn in sorted({d - 1, d, d + 3}):
            for ds in sorted({d - 1, d, d + 2}):
                for dd in sorted({0, d - 1, d, d + 1}):
                    for lv in (0.0, 0.5, float(d)):
                        if min(dn, ds, dd) < 0:
                            continue
                        w, h = mod.corner_piece(d, dn, ds, dd, lv)
                        closes = mod.corner_line(d, dn, ds, dd)
                        corner.append("\t\t\t{ %s }," % ", ".join(_f(v) for v in (d, dn, ds, dd, lv, w, h, 1 if closes else 0)))
    rects = []
    cases = [(0, 0, 0, 0, 0, 0, 0), (0.17, 0.06, 0.35, 0, 0, 0, 0), (0, 0, 0, 0.17, 0.35, 0, 0), (0, 0, 0, 0, 0, 0.29, 0.62),
             (0, 0, 0, 0.11, 0.23, 0.29, 0.62), (0.29, 0.29, 0.62, 0, 0, 0, 0), (0, 0.29, 0, 0.29, 0.62, 0, 0),
             (0.6, 0.6, 0, 0, 0, 0, 0), (0, 0, 1.0, 0, 0, 0, 0), (0.06, 0, 0, 0.17, 0.35, 0.17, 0.35), (0, 0, 0.12, 0, 0, 0, 0),
             (0.23, 0.11, 0.5, 0, 0, 0, 0)]
    for c in cases:
        out = mod.floor_rects(*c)
        vals = list(c) + [len(out)] + [v for r in out for v in r] + [0.0] * (8 - 4 * len(out))
        rects.append("\t\t\t{ %s }," % ", ".join(_f(v) for v in vals))
    return "\n".join([
        BEGIN,
        "\t\t// floor depth d (notches) -> FloorShade(d)",
        "\t\tinternal static readonly float[,] FloorGolden =", "\t\t{", *floor, "\t\t};",
        "\t\t// exposed drop e (notches) -> FaceFootShade(e)",
        "\t\tinternal static readonly float[,] FootGolden =", "\t\t{", *foot, "\t\t};",
        "\t\t// d, north, side, diagonal, level -> corner piece width, height; ClosesCorner(d, north, side, diagonal)",
        "\t\tinternal static readonly float[,] CornerGolden =", "\t\t{", *corner, "\t\t};",
        "\t\t// ww, ew, h, wnw, hnw, wne, hne -> count, then up to two rects x0, z0, x1, z1",
        "\t\tinternal static readonly float[,] RectGolden =", "\t\t{", *rects, "\t\t};",
        "\t\t" + END,
    ])


def _current_gold(text: str) -> str:
    i, j = text.find(BEGIN), text.find(END)
    if i < 0 or j < 0:
        raise ValueError("PitReliefParityChecks.cs has no golden markers")
    return text[i:j + len(END)]


def write_golden():
    text = PARITY.read_text(encoding="utf-8")
    new = text.replace(_current_gold(text), golden_block(_planner()))
    PARITY.write_text(new, encoding="utf-8")


def csharp_matches_model():
    """The C# parity table is the model's (no drift), and the parity checks and the new file are compiled and run."""
    text = PARITY.read_text(encoding="utf-8")
    want = golden_block(_planner())
    same = _current_gold(text) == want
    reg = ("PitReliefParityChecks.Run(Case)" in PROGRAM.read_text(encoding="utf-8")
           and 'Include="PitReliefParityChecks.cs"' in TEST_CSPROJ.read_text(encoding="utf-8")
           and 'Include="..\\RM_PitReliefMath.cs"' in TEST_CSPROJ.read_text(encoding="utf-8")
           and 'Include="RM_PitReliefMath.cs"' in MOD_CSPROJ.read_text(encoding="utf-8"))
    walls = _read(WALLS)
    uses = {k: k in walls for k in ("RM_PitReliefMath.CornerPiece(", "RM_PitReliefMath.ClosesCorner(", "RM_PitReliefMath.FloorRects(",
                                     "RM_PitReliefMath.FaceFootShade(", "RM_PitReliefMath.ReliefFaces(", "RM_PitReliefMath.AddUnderLine(",
                                     "RM_PitReliefMath.DrawsPitArt(", "RM_PitReliefMath.CornerPoly(")}
    concealed_skip = "if (!DrawsPitArt(map, eng, c, d))" in walls and "BordersOpenCut(map, eng, c)" in walls
    ok = same and reg and all(uses.values()) and concealed_skip
    return ok, "golden table = model: %s; compiled and registered: %s; layer reads RM_PitReliefMath: %s; concealed squares skipped: %s" % (
        same, reg, [k for k, v in uses.items() if not v] or "all", concealed_skip)


CASES = [planner_faces_every_step, deepening_redraws_walls, floor_shade_follows_depth_past_two_metres, model_sweep, csharp_matches_model]


def main(argv):
    if "--write" in argv:
        write_golden()
        print("wrote the golden table into %s" % PARITY)
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
    sys.exit(main(sys.argv[1:]))
