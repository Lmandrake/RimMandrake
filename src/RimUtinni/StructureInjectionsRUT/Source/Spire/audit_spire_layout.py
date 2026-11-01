#!/usr/bin/env python3
"""Audit the SHIPPED RUT_Spire_HighCommand layout, read back from the committed XML.

gen_spire_layout.py proves reachability on its in-memory grid before rendering, so
a fault in the rendering is invisible to it. This re-derives the properties from the
artifact, and asks what that BFS does not:

  1. Each ring has exactly one opening, of the kind the design says.
  2. The hull is unbroken RUT_SpireHullWall: the seal is the only way past it.
  3. Sealed, the codes cannot be reached from outside; opened, they can, and each
     inner opening is forced (shut it, lose the codes).
  4. The codes are in the isolated room with the command console, and only there.
  5. The Helix and the Rakatan garrison are in different wards, a door apart.

Offline, no game, no bridge. Exits non-zero if any invariant fails.

    python3 src/RimUtinni/StructureInjectionsRUT/Source/Spire/audit_spire_layout.py [layout.xml]
"""
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque

HERE = os.path.dirname(os.path.abspath(__file__))
LAYOUT_XML = os.path.normpath(os.path.join(HERE, "..", "..", "Defs", "Spire", "StructureLayoutDefs_Spire.xml"))

DEFNAME = "RUT_Spire_HighCommand"
HULL = "RUT_Symbol_SpireHull"
SEAL = "RUT_Symbol_SpireSeal"
DOOR = "RUT_Symbol_SpireDoor"
WALL = "Wall_Plasteel"
CODES = "RUT_Symbol_RakatanCommandCodes"
COMMAND = "RUT_Symbol_SpireCommandConsole"
CONTROL = "RUT_Symbol_SpireControlConsole"

# Restated on purpose: an audit that imported the generator's numbers would agree with it.
N = 121
RINGS = {6: (HULL, (6, 60), SEAL), 27: (WALL, (93, 60), DOOR), 49: (WALL, (60, 71), "."), 55: (WALL, (60, 55), DOOR)}
OUTER_WARD = (7, 26)
INNER_WARD = (28, 48)
ISOLATED_FROM = 56
TERRAINS = ["Concrete", "Gravel"]
WALKABLE_PREFIXES = ("Filth_", "RUT_Symbol_Helix", "RUT_Symbol_Mech")


def dist(r, c):
    return min(r, c, N - 1 - r, N - 1 - c)


def load_grids(path):
    for d in ET.parse(path).getroot().findall("KCSG.StructureLayoutDef"):
        if (d.findtext("defName") or "").strip() == DEFNAME:
            layout = [(li.text or "").strip().split(",") for li in d.find("layouts").find("li")]
            terrain = [(li.text or "").strip().split(",") for li in d.find("terrainGrid")]
            return layout, terrain
    raise SystemExit("%s not found in %s" % (DEFNAME, path))


def walkable(sym):
    return sym in (".", DOOR, CODES) or sym.startswith(WALKABLE_PREFIXES)


def flood(layout, start, shut=()):
    seen = {start}
    q = deque([start])
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in seen:
                if (nr, nc) not in shut and walkable(layout[nr][nc]):
                    seen.add((nr, nc))
                    q.append((nr, nc))
    return seen


def main(argv):
    layout, terrain = load_grids(argv[1] if len(argv) > 1 else LAYOUT_XML)
    failures = []

    def check(ok, msg):
        print(("  ok   " if ok else "  FAIL ") + msg)
        if not ok:
            failures.append(msg)

    check(len(layout) == N and {len(r) for r in layout} == {N}, "layout is %dx%d" % (N, N))
    check(len(terrain) == N and {len(r) for r in terrain} == {N}, "terrainGrid matches the layout")
    terrains = sorted({s for row in terrain for s in row})
    check(terrains == TERRAINS, "no lake left in the terrain: %s" % terrains)
    if failures:
        print("FAIL: shape")
        return 1

    for depth, (wall, gap, kind) in RINGS.items():
        cells = [(r, c) for r in range(N) for c in range(N) if dist(r, c) == depth]
        odd = [(r, c) for r, c in cells if layout[r][c] != wall]
        check(odd == [gap], "ring d=%d is unbroken %s but for %s (got %s)" % (depth, wall, gap, odd))
        check(layout[gap[0]][gap[1]] == kind, "ring d=%d opening is %s" % (depth, kind))

    where = {}
    for r in range(N):
        for c in range(N):
            where.setdefault(layout[r][c], []).append((r, c))
    check(len(where.get(CODES, [])) == 1, "exactly one set of codes")
    check(len(where.get(COMMAND, [])) == 1, "exactly one command console")
    check(len(where.get(CONTROL, [])) == 1, "exactly one control console")
    if failures:
        print("FAIL: census")
        return 1
    codes = where[CODES][0]
    command = where[COMMAND][0]
    control = where[CONTROL][0]
    check(dist(*codes) >= ISOLATED_FROM and dist(*command) >= ISOLATED_FROM,
          "codes and command console are in the isolated room")
    check(abs(codes[0] - command[0]) + abs(codes[1] - command[1]) == 1, "codes sit beside the command console")
    check(dist(*control) < 55, "the Cathedral's controls are outside the isolated room")

    outside = (0, 0)
    sealed = flood(layout, outside)
    check(codes not in sealed, "sealed: the codes cannot be reached from outside")
    check(not any(dist(r, c) > 6 for r, c in sealed), "sealed: nothing past the hull is reachable")
    seal = RINGS[6][1]
    opened = list(map(list, layout))
    opened[seal[0]][seal[1]] = "."
    check(codes in flood(opened, outside), "opened: the codes are reachable from outside")
    for depth in (27, 49, 55):
        gap = RINGS[depth][1]
        check(codes not in flood(opened, outside, shut={gap}), "the d=%d opening is forced" % depth)

    helix = [p for s, ps in where.items() if s.startswith("RUT_Symbol_Helix") for p in ps]
    mechs = [p for s, ps in where.items() if s.startswith("RUT_Symbol_Mech") for p in ps]
    check(len(helix) >= 7 and len(mechs) >= 12, "probe: both garrisons present (%d, %d)" % (len(helix), len(mechs)))
    check(all(OUTER_WARD[0] <= dist(*p) <= OUTER_WARD[1] for p in helix), "the Helix hold the outer ward only")
    check(all(INNER_WARD[0] <= dist(*p) <= INNER_WARD[1] for p in mechs), "the Rakatan garrison holds the inner ward only")
    check(len(where.get("RUT_Symbol_AshfallSpecimenCell", [])) == 6, "six specimen cells")

    census = Counter(s for row in layout for s in row if s != ".")
    for sym, count in sorted(census.items()):
        print("  %5d  %s" % (count, sym))
    print("FAIL: %d" % len(failures) if failures else "PASS: every invariant holds")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
