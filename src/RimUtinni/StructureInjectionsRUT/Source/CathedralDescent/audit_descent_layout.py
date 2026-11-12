#!/usr/bin/env python3
"""Audit the SHIPPED descent site, read back from the committed XML in Defs/CathedralDescent/.

gen_descent_layout.py checks reachability on its in-memory grid before rendering; this re-derives
every property from the artifact, slot by slot:

  1. The layout is 250x250 and its terrain grid matches.
  2. Every symbol resolves to a real def: this site's SymbolDefs/ThingDefs, the rust kit
     (src/RimMandrake/RustCathedral/Defs), FlowWorks (src/RimMandrake/FlowWorks/Defs), or vanilla
     (read from the game's Data folder when present, else from the pinned list below: UNMEASURED).
  3. The terminus is placed exactly once, inside the bottom chamber, and the finishing gen step's
     terminusCell names that slot.
  4. A walk exists from the arrival edge to the terminus; the only standable map-edge cells are the
     arrival mouth.
  5. The line spans the map, west edge to east edge, solid but for its one crossing.
  6. A deep coolant channel runs from the east edge to the south edge, beside the bottom chamber.
  7. Every new defName is RUT_CathedralDescent_*; the terminus cannot be minified, deconstructed or
     broken; every patrol waypoint is reachable open floor.

Offline, no game, no bridge. Exits non-zero if any invariant fails.

    python3 src/RimUtinni/StructureInjectionsRUT/Source/CathedralDescent/audit_descent_layout.py [defs_dir]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, "..", ".."))
REPO = os.path.normpath(os.path.join(MOD, "..", "..", ".."))
DEFS = os.path.join(MOD, "Defs", "CathedralDescent")
KIT_DEFS = os.path.join(REPO, "src", "RimMandrake", "RustCathedral", "Defs")
FLOW_DEFS = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Defs")
GAME_DATA = os.environ.get("RIMWORLD_DATA", "/mnt/d/SteamLibrary/steamapps/common/RimWorld/Data")

# Restated on purpose: an audit that imported the generator's numbers would agree with it.
N = 250
PREFIX = "RUT_CathedralDescent_"
LAYOUT = "RUT_CathedralDescent_Halls"
FINISH = "RUT_CathedralDescent_GenStepFinish"
TERMINUS = "RUT_CathedralDescent_Terminus"
LINE_THINGS = {"RUT_CathedralDescent_LineHousing", "RUT_CathedralDescent_LineCarriage"}
ARRIVAL_COLS = range(113, 138)
LINE_ROWS = range(125, 132)
CHAMBER_INTERIOR = (217, 241, 11, 55)
DEEP = "RM_CoolantDeep"
WALKABLE_THING_PREFIX = "Filth_"
# Vanilla defs the layout uses, with the file that defines each (relative to the game's Data folder).
# Checked against the live Data folder when it is on this machine; otherwise this list is all there is.
VANILLA_PINNED = {
    "Gravel": ("TerrainDef", "Core/Defs/TerrainDefs/Terrain_Natural.xml"),
    "Filth_MachineBits": ("ThingDef", "Core/Defs/ThingDefs_Misc/Filth_Various.xml"),
    "Filth_RubbleBuilding": ("ThingDef", "Core/Defs/ThingDefs_Misc/Filth_Various.xml"),
    "Mech_Pikeman": ("PawnKindDef", "Core/Defs/ThingDefs_Races/Races_Mechanoid.xml"),
    "Mech_Lancer": ("PawnKindDef", "Core/Defs/ThingDefs_Races/Races_Mechanoid.xml"),
}


def defnames(paths, kinds=None):
    """{defName: def tag} for every def in the XML files under paths (kinds: restrict to these tags)."""
    out = {}
    for root_dir in paths:
        for f in glob.glob(os.path.join(root_dir, "**", "*.xml"), recursive=True):
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError:
                continue
            for d in root:
                name = (d.findtext("defName") or "").strip()
                if name and (kinds is None or d.tag in kinds):
                    out[name] = d.tag
    return out


def vanilla_check(name, tag, rel):
    """True/False if the live Data file says so, None when the game's Data folder is not here."""
    path = os.path.join(GAME_DATA, rel)
    if not os.path.isdir(GAME_DATA):
        return None
    if not os.path.isfile(path):
        return False
    return any((d.findtext("defName") or "").strip() == name and d.tag == tag for d in ET.parse(path).getroot())


def load(defs_dir):
    layout = terrain = None
    for d in ET.parse(os.path.join(defs_dir, "StructureLayoutDefs_CathedralDescent.xml")).getroot():
        if (d.findtext("defName") or "").strip() == LAYOUT:
            layout = [(li.text or "").strip().split(",") for li in d.find("layouts").find("li")]
            terrain = [(li.text or "").strip().split(",") for li in d.find("terrainGrid")]
    return layout, terrain


def main(argv):
    defs_dir = argv[1] if len(argv) > 1 else DEFS
    failures = []
    unmeasured = []

    def check(ok, msg):
        print(("  ok   " if ok else "  FAIL ") + msg)
        if not ok:
            failures.append(msg)

    layout, terrain = load(defs_dir)
    check(layout is not None, "layout %s present" % LAYOUT)
    if layout is None:
        print("FAIL: 1")
        return 1
    check(len(layout) == N and {len(r) for r in layout} == {N}, "layout is %dx%d" % (N, N))
    check(len(terrain) == N and {len(r) for r in terrain} == {N}, "terrainGrid matches the layout")
    if failures:
        print("FAIL: shape")
        return 1

    # --- 2. symbol resolution, per slot
    own = {}
    symbols = {}
    for f in glob.glob(os.path.join(defs_dir, "*.xml")):
        for d in ET.parse(f).getroot():
            name = (d.findtext("defName") or "").strip()
            if name:
                own[name] = d
                if d.tag == "KCSG.SymbolDef":
                    symbols[name] = (d.findtext("thing") or "").strip()
    kit = defnames([KIT_DEFS])
    flow = defnames([FLOW_DEFS])
    resolved = {}

    def resolve(sym, want):
        if sym in symbols:
            t = symbols[sym]
            return "site" if t in own and own[t].tag == "ThingDef" and want == "ThingDef" else None
        if sym in own:
            return "site" if own[sym].tag == want else None
        if sym in kit:
            return "kit" if kit[sym] == want else None
        if sym in flow:
            return "flowworks" if flow[sym] == want else None
        if sym in VANILLA_PINNED:
            tag, rel = VANILLA_PINNED[sym]
            if tag != want:
                return None
            live = vanilla_check(sym, tag, rel)
            if live is None:
                unmeasured.append(sym)
                return "vanilla (pinned, UNMEASURED)"
            return "vanilla" if live else None
        return None

    bad_slots = []
    for grid, want, skip in ((layout, "ThingDef", "."), (terrain, "TerrainDef", None)):
        for r in range(N):
            for c in range(N):
                s = grid[r][c]
                if s == skip:
                    continue
                if (s, want) not in resolved:
                    resolved[(s, want)] = resolve(s, want)
                if resolved[(s, want)] is None:
                    bad_slots.append((r, c, s))
    for (s, want), where in sorted(resolved.items()):
        print("         %-40s %-10s -> %s" % (s, want, where))
    check(not bad_slots, "every one of %d slots resolves to a real def (bad: %s)" % (2 * N * N, bad_slots[:5]))

    # --- 3. the terminus
    real = [[symbols.get(s, s) for s in row] for row in layout]
    spots = [(r, c) for r in range(N) for c in range(N) if real[r][c] == TERMINUS]
    check(len(spots) == 1, "terminus placed exactly once (%s)" % spots)
    if len(spots) != 1:
        print("FAIL: %d" % len(failures))
        return 1
    tr, tc = spots[0]
    r0, r1, c0, c1 = CHAMBER_INTERIOR
    check(r0 <= tr <= r1 and c0 <= tc <= c1, "terminus %s is inside the bottom chamber" % (spots[0],))
    check(tr > 200, "the bottom chamber is the far end from the arrival edge (row %d)" % tr)
    walls = [(r, c) for r in range(r0 - 1, r1 + 2) for c in range(c0 - 1, c1 + 2)
             if r in (r0 - 1, r1 + 1) or c in (c0 - 1, c1 + 1)]
    gaps = [(r, c) for r, c in walls if real[r][c] == "."]
    check(gaps and all(r == r0 - 1 for r, c in gaps), "the chamber is walled, its one opening in the north wall (%d cells)" % len(gaps))
    reveal = [(r, c) for r in range(tr - 6, tr + 7) for c in range(tc - 6, tc + 7) if (r, c) != (tr, tc)]
    check(all(real[r][c] == "." or real[r][c].startswith(WALKABLE_THING_PREFIX) for r, c in reveal) or
          all(r0 <= r <= r1 and c0 <= c <= c1 for r, c in reveal), "the 6-cell reveal radius round the terminus is chamber floor")

    finish = own.get(FINISH)
    gs = finish.find("genStep") if finish is not None else None
    check(gs is not None, "finishing gen step %s present" % FINISH)
    if gs is None:
        print("FAIL: %d" % len(failures))
        return 1
    m = re.match(r"\((\d+),(\d+)\)", gs.findtext("terminusCell") or "")
    check(m is not None and (int(m.group(2)), int(m.group(1))) == (tr, tc), "gen step terminusCell (col,row) names the terminus slot")
    check((gs.findtext("terminusDef") or "").strip() == TERMINUS, "gen step terminusDef is %s" % TERMINUS)

    # --- 4. the walk
    def walkable(r, c):
        return terrain[r][c] != DEEP and (real[r][c] == "." or real[r][c].startswith(WALKABLE_THING_PREFIX))

    edge = [(r, c) for r in range(N) for c in range(N) if (r in (0, N - 1) or c in (0, N - 1)) and walkable(r, c)]
    arrival = sorted(set((0, c) for c in ARRIVAL_COLS))
    check(sorted(edge) == arrival, "the only standable edge cells are the arrival mouth, north edge cols 113-137 (%d found)" % len(edge))
    dist = {p: 0 for p in arrival}
    q = deque(arrival)
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in dist and walkable(nr, nc):
                dist[(nr, nc)] = dist[(r, c)] + 1
                q.append((nr, nc))
    near = [dist[p] for p in ((tr + 1, tc), (tr - 1, tc), (tr, tc + 1), (tr, tc - 1)) if p in dist]
    walk = min(near) if near else None
    check(walk is not None, "a walk reaches the terminus from the arrival edge (%s cells)" % walk)
    check(walk is not None and walk >= 3 * N, "the walk is long: at least %d cells (%s)" % (3 * N, walk))
    arrival_clear = all(real[r][c] == "." for r in range(0, 15) for c in ARRIVAL_COLS)
    check(arrival_clear, "the arrival area (rows 0-14, cols 113-137) is clear")

    # --- 5. the line
    line_cols = [c for c in range(N) if all(real[r][c] in LINE_THINGS for r in LINE_ROWS)]
    open_cols = [c for c in range(N) if all(walkable(r, c) for r in LINE_ROWS)]
    check(len(line_cols) + len(open_cols) == N, "every column of rows 125-131 is line or crossing")
    check(0 in line_cols and N - 1 in line_cols, "the line runs out at both the west and the east edge")
    check(len(open_cols) == 3 and open_cols[-1] - open_cols[0] == 2, "one 3-wide crossing (%s)" % open_cols)

    # --- 6. coolant
    deep = {(r, c) for r in range(N) for c in range(N) if terrain[r][c] == DEEP}
    check(len(deep) > 0, "deep coolant present (%d cells)" % len(deep))
    seen = set()
    starts = [p for p in deep if p[1] == N - 1]
    q = deque(starts)
    seen.update(starts)
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (r + dr, c + dc)
            if p in deep and p not in seen:
                seen.add(p)
                q.append(p)
    check(starts and any(r == N - 1 for r, c in seen), "one channel joins the east edge to the south edge")
    besides = min((abs(c - (c1 + 1)) for r, c in deep if r0 <= r <= r1), default=99)
    check(besides <= 6, "the channel runs beside the bottom chamber (%d cells off its east wall)" % besides)
    on_path = any(p in dist for r, c in deep for p in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)))
    check(on_path, "the walk passes along the channel")

    # --- 7. names, terminus def, patrols
    new = sorted(own)
    check(all(n.startswith(PREFIX) for n in new), "all %d new defNames are %s*" % (len(new), PREFIX))
    t = own.get(TERMINUS)
    check(t is not None and t.tag == "ThingDef", "terminus ThingDef present")
    if t is not None:
        check(t.find("minifiedDef") is None, "terminus has no minifiedDef (not minifiable)")
        check((t.findtext("building/deconstructible") or "").strip() == "false", "terminus is not deconstructible")
        check((t.findtext("useHitPoints") or "").strip() == "false" and (t.findtext("destroyable") or "").strip() == "false",
              "terminus is unbreakable (useHitPoints false, destroyable false)")
        check((t.findtext("size") or "(1,1)").strip() == "(1,1)", "terminus is 1x1")
    groups = gs.findall("patrols/li")
    check(len(groups) >= 1, "patrol groups present (%d)" % len(groups))
    pawnkinds = 0
    for g in groups:
        for li in g.findall("kinds/li"):
            pawnkinds += 1
            k = (li.text or "").strip()
            check(resolve(k, "PawnKindDef") is not None, "patrol kind %s resolves" % k)
        for li in g.findall("waypoints/li"):
            mm = re.match(r"\((\d+),(\d+)\)", li.text or "")
            r, c = int(mm.group(2)), int(mm.group(1))
            check((r, c) in dist, "waypoint (col %d,row %d) is reachable open floor" % (c, r))
    for key in ("wantsThreatPoints", "considerEnteringAsAttack", "gravShipsCanLandOn"):
        site = own.get("RUT_CathedralDescent_Site")
        check(site is not None and (site.findtext(key) or "").strip() == "false", "site %s is false" % key)

    census = Counter(s for row in real for s in row if s != ".")
    for sym, count in sorted(census.items()):
        print("  %6d  %s" % (count, sym))
    print("walk: %s cells; terminus at row %d col %d; arrival north edge cols %d-%d; map %dx%d; sentinels %d" % (
        walk, tr, tc, ARRIVAL_COLS[0], ARRIVAL_COLS[-1], N, N, pawnkinds))
    if unmeasured:
        print("UNMEASURED: game Data folder not found at %s; vanilla defs taken from the pinned list: %s" % (
            GAME_DATA, sorted(set(unmeasured))))
    print("FAIL: %d" % len(failures) if failures else "PASS: every invariant holds")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
