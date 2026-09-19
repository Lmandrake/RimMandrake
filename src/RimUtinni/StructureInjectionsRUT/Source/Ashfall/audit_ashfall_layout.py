#!/usr/bin/env python3
"""Audit the SHIPPED RUT_Ashfall_Spire StructureLayoutDef.

WHY THIS EXISTS, separately from gen_ashfall_layout.py's own reachable_core():
the generator proves reachability on its in-memory grid and THEN renders the
XML, so any fault in the rendering step -- a dropped row, a transposed axis, a
symbol written into the wrong cell -- is invisible to that proof. This reads the
committed artifact back and re-derives the property from it.

It also asks three things the generator's own BFS does not, and which its
docstring nevertheless claims:

  1. Each wall ring has EXACTLY ONE gap. reachable_core() returns True even if a
     ring had two gaps, so "never skippable" was asserted, not tested.
  2. Sealing either interior gap makes the core UNREACHABLE. That is what "the
     full outer->inner->core lap" actually means. reachable_core() starts one
     cell INSIDE the outer door, so it never tests the hull at all.
  3. The prize sits where the design says, and the symbol census matches what a
     live placement should produce -- the count to compare a jawa/list_things
     census against, so an undercount is visible instead of reassuring.

Offline, no game, no bridge. Exits non-zero if any invariant fails.

    python3 src/RimUtinni/StructureInjectionsRUT/Source/Ashfall/audit_ashfall_layout.py
"""

import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque

HERE = os.path.dirname(os.path.abspath(__file__))
LAYOUT_XML = os.path.normpath(
    os.path.join(HERE, "..", "..", "Defs", "Ashfall", "StructureLayoutDefs_Ashfall.xml")
)

DEFNAME = "RUT_Ashfall_Spire"
WALL = "Wall_Plasteel"

# The authored geometry, restated here on purpose: an audit that imported these
# from the generator would agree with the generator by construction. These are
# read from the design (61x61, hull at Chebyshev depth 0, inner hull at 7, core
# wall at 20, doors on the north/east/south faces) and the audit FAILS if the
# shipped artifact disagrees with them.
EXPECTED_N = 61
WALL_RINGS = ((0, "north"), (7, "east"), (20, "south"))
EXPECTED_GAPS = {0: (0, 30), 7: (30, 53), 20: (40, 30)}
EXPECTED_CENSUS = {
    WALL: 501,
    "RUT_Symbol_AshfallSpecimenCell": 4,
    "RUT_Symbol_TeslaTurret": 3,
    "RUT_Symbol_Railgun": 2,
    "RUT_Symbol_HelixGrunt": 2,
    "RUT_Symbol_HelixHeavy": 1,
    "RUT_Symbol_HelixSpecialist": 1,
    "RUT_Symbol_HelixLeader": 1,
    "RUT_Symbol_SpireCommandConsole": 1,
    "RUT_Symbol_RakatanCommandCodes": 1,
}


def load_grids(path, defname):
    root = ET.parse(path).getroot()
    for d in root.findall("KCSG.StructureLayoutDef"):
        if (d.findtext("defName") or "").strip() == defname:
            layout = [
                (li.text or "").strip().split(",")
                for li in d.find("layouts").find("li")
            ]
            terrain = [
                (li.text or "").strip().split(",") for li in d.find("terrainGrid")
            ]
            return layout, terrain
    raise SystemExit(f"{defname} not found in {path}")


def flood(n, blocked, start):
    """4-neighbour flood fill. `blocked(r, c) -> bool`."""
    seen = {start}
    q = deque([start])
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen and not blocked(nr, nc):
                seen.add((nr, nc))
                q.append((nr, nc))
    return seen


def main():
    layout, terrain = load_grids(LAYOUT_XML, DEFNAME)
    n = len(layout)
    failures = []

    def check(ok, msg):
        print(("  ok   " if ok else "  FAIL ") + msg)
        if not ok:
            failures.append(msg)

    print(f"{DEFNAME}  <-  {LAYOUT_XML}")

    print("\n[shape]")
    check(n == EXPECTED_N, f"layout is {n} rows (expected {EXPECTED_N})")
    widths = sorted({len(r) for r in layout})
    check(widths == [EXPECTED_N], f"every layout row is {EXPECTED_N} wide (got widths {widths})")
    twidths = sorted({len(r) for r in terrain})
    check(
        len(terrain) == n and twidths == [EXPECTED_N],
        f"terrainGrid is {len(terrain)}x{twidths} and matches the layout",
    )
    terrains = sorted({s for row in terrain for s in row})
    check(terrains == ["Concrete"], f"terrain is uniform Concrete (got {terrains})")

    def dist(r, c):
        return min(r, c, n - 1 - r, n - 1 - c)

    # 1. one gap per ring -- the generator's BFS cannot see a second one.
    print("\n[wall rings: exactly one gap each]")
    for depth, face in WALL_RINGS:
        cells = [(r, c) for r in range(n) for c in range(n) if dist(r, c) == depth]
        gaps = [(r, c) for (r, c) in cells if layout[r][c] != WALL]
        check(
            len(gaps) == 1,
            f"d={depth:2d} ({face:5s} face): {len(cells) - len(gaps)}/{len(cells)} {WALL}, "
            f"gap(s) {gaps}",
        )
        if len(gaps) == 1:
            check(
                gaps[0] == EXPECTED_GAPS[depth],
                f"d={depth:2d} gap is at {gaps[0]} (expected {EXPECTED_GAPS[depth]})",
            )

    # 2. the lap is forced -- seal a door, lose the core.
    print("\n[the door lap is forced, not merely walkable]")
    is_wall = lambda r, c: layout[r][c] == WALL  # noqa: E731
    core = (n // 2, n // 2)
    outer_gaps = [(r, c) for r in range(n) for c in range(n) if dist(r, c) == 0 and layout[r][c] != WALL]
    check(len(outer_gaps) == 1, f"the hull has one entrance: {outer_gaps}")
    entry = outer_gaps[0]
    check(core in flood(n, is_wall, entry), f"core {core} is reachable from the hull entrance {entry}")
    for depth in (7, 20):
        seal = EXPECTED_GAPS[depth]
        blocked = lambda r, c, s=seal: layout[r][c] == WALL or (r, c) == s  # noqa: E731
        check(
            core not in flood(n, blocked, entry),
            f"sealing the d={depth} gap {seal} makes the core unreachable",
        )

    # 3. contents -- the numbers a live census must reproduce.
    print("\n[contents]")
    mid = n // 2
    check(
        layout[mid][mid] == "RUT_Symbol_SpireCommandConsole",
        f"centre ({mid},{mid}) holds the command console (got {layout[mid][mid]})",
    )
    check(
        layout[mid - 1][mid] == "RUT_Symbol_RakatanCommandCodes",
        f"({mid - 1},{mid}) holds the Rakatan command codes (got {layout[mid - 1][mid]})",
    )
    census = Counter(s for row in layout for s in row if s != ".")
    for sym, want in sorted(EXPECTED_CENSUS.items()):
        check(census.get(sym, 0) == want, f"{sym}: {census.get(sym, 0)} (expected {want})")
    unexpected = sorted(set(census) - set(EXPECTED_CENSUS))
    check(not unexpected, f"no unexpected symbols (found {unexpected})")

    pawn_syms = [s for s in census if "Helix" in s]
    print(
        "\n  A live placement should therefore show "
        f"{sum(census[s] for s in pawn_syms)} RUT_Jawa_Helix_* pawns and "
        f"{census['RUT_Symbol_AshfallSpecimenCell']} RUT_AshfallSpecimenCell. "
        "A lower live count is an undercount to explain, not a pass."
    )

    print()
    if failures:
        print(f"FAILED: {len(failures)} invariant(s) broken")
        return 1
    print("PASS: every invariant holds in the shipped def")
    return 0


if __name__ == "__main__":
    sys.exit(main())
