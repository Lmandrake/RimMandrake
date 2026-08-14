#!/usr/bin/env python3
"""thruster_placement_scan.py — where can a gravship thruster actually go?

This is the derivation behind the 2026-08-14 finding that killed a planned
stern deck re-lay. Keep it: the conclusion rests on a roof map that the export
does not contain, and this script is the only record of how that map was
produced.

THE PROBLEM. `CompGravshipThruster::get_CanBeActive` requires `outdoors == true`,
and `IsOutdoors` does NOT test the thruster's own cell — it tests the strip
directly AFT of it, along `rotation.Opposite`, width = the thruster's own width.
Every cell in that strip must sit in a room using outdoor temperature.

WHY A DERIVATION IS NEEDED. `ShipLayoutDefV2` has **no roof field** — the tag
census is foundationDef, foundationStuff, terrainDef, terrainStuff, things,
defName, stuffDef, rotInteger, quality, plantToGrowDef, exportedStorageSettings,
compSettings, width, height, gravEngineX/Z, label. Roofs are *regenerated at
import*: GravshipExport postfixes `Sketch.GetSuggestedRoofCells`
(`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`) to flood-fill every
non-roof-holder region inside the sketch's OccupiedRect and roof any region that
does not touch the rect edge, plus its bounding roof-holders. This re-implements
that flood-fill offline.

⚠️ SO THE ROOF MAP IS DERIVED, NOT OBSERVED. It is a simulation of import, not a
reading of a live map. That distinction is the whole caveat on the finding and
must survive into any report built on it.

RESULT WHEN WRITTEN: 4,049 of 4,057 substructure cells roofed — every standable
cell on the deck is indoors, so a thruster placed anywhere on the deck as
authored is blocked three ways at once (indoors, on substructure, behind a
wall), all from one cause.

THE FIX THIS FOUND. `ThrusterBase` is `holdsRoof true` + `fillPercent 1` +
`passability Impassable`, so it seals the room exactly as the hull wall it
replaces. Put the thruster IN the wall line: the interior stays enclosed and
roofed, and the cell `IsOutdoors` reads is the one beyond it, off-deck open sky.
Cost is ONE `GravshipHull` cell per SmallThruster, two per LargeThruster — not a
deck re-lay.

Usage:
    python3 src/RimMandrake/Utils/thruster_placement_scan.py [export.xml]
"""

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gravship_layout import Layout  # noqa: E402

DEFAULT_EXPORT = (
    "/mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/ship_build/"
    "exported/Gravship_v1.xml"
)

# Both hold roof, so both terminate a flood-fill region. GravshipHull is
# ParentName="Wall"; DoorBase sets holdsRoof too.
ROOF_HOLDERS = {"GravshipHull", "Door"}


def load(path):
    lay = Layout.load(path)
    sub, things, occupied = set(), {}, set()
    for z in range(lay.height):
        for x in range(lay.width):
            c = lay.cell(x, z)
            if c is None or c.empty():
                continue
            occupied.add((x, z))
            if c.foundationDef == "Substructure":
                sub.add((x, z))
            if c.things:
                things[(x, z)] = [t.defName for t in c.things]
    return lay, sub, things, occupied


def derive_roofs(things, occupied):
    """Re-run GravshipExport's own roof regeneration offline.

    A region that touches the OccupiedRect edge is open to the sky and gets no
    roof; anything fully enclosed is roofed along with its bounding holders.
    """
    holder = {k for k, v in things.items() if any(d in ROOF_HOLDERS for d in v)}
    xs = [p[0] for p in occupied]
    zs = [p[1] for p in occupied]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)

    def in_rect(p):
        return x0 <= p[0] <= x1 and z0 <= p[1] <= z1

    def on_edge(p):
        return p[0] in (x0, x1) or p[1] in (z0, z1)

    visited, roofed = set(), set()
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            p = (x, z)
            if p in visited or p in holder:
                continue
            region, q = [], collections.deque([p])
            visited.add(p)
            while q:
                cur = q.popleft()
                region.append(cur)
                for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (cur[0] + d[0], cur[1] + d[1])
                    if in_rect(n) and n not in visited and n not in holder:
                        visited.add(n)
                        q.append(n)
            if any(on_edge(c) for c in region):
                continue  # open to the sky
            for c in region:
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        n = (c[0] + dx, c[1] + dz)
                        if in_rect(n) and ((dx, dz) == (0, 0) or n in holder):
                            roofed.add(n)
    return holder, roofed, (x0, x1, z0, z1)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EXPORT
    lay, sub, things, occupied = load(path)
    holder, roofed, rect = derive_roofs(things, occupied)

    counts = collections.Counter(d for v in things.values() for d in v)
    print(f"export: {path}")
    print(f"grid {lay.width}x{lay.height} · {len(sub)} substructure · {len(things)} thing cells")
    print(f"occupiedRect x{rect[0]}-{rect[1]} z{rect[2]}-{rect[3]}")
    print(f"roofed (DERIVED, not observed): {len(roofed)}")
    print(f"substructure cells roofed: {len(sub & roofed)} of {len(sub)}")
    for d in ("SmallThruster", "LargeThruster", "PilotConsole", "ChemfuelTank"):
        print(f"  {d:16s} {counts.get(d, 0)}")

    print("\nstern zone, x38-52 z120-133   # hull · r roofed substructure · . bare substructure")
    for z in range(rect[3], 119, -1):
        row = ""
        for x in range(38, 53):
            p = (x, z)
            if p in holder:
                ch = "#"
            elif p in things:
                ch = "B"
            elif p in sub:
                ch = "r" if p in roofed else "."
            else:
                ch = " "
            row += ch
        print(f"{z:4d} {row}")


if __name__ == "__main__":
    main()
