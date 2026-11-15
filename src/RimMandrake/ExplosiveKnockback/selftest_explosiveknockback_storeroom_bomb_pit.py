#!/usr/bin/env python3
"""Offline check of sc_storeroom_bomb_pit, the showcase (design/concepts/ExplosiveKnockback/scenes.json;
RIMMANDRAKE_WRITE_STOREROOM_BOMB_PIT_SCENE_TABLE_NAMED_FIRST, 2026-11-15). The scene runs only in a game (its live command is in
version/test_table.json); this proves what can be read without one:
  N  storeroom_bomb_pit and its control lane are in RM_KnockbackProof.SceneNames, Build routes both to StoreroomBombPit, the
     csproj compiles its file, and scenes.json's entry point names it
  G  the builder carries the start assertions its scene names (INVALID guards) and its control lane
  O  the verdict reads every clause of the table's observes text (one needle per clause)
  K  the room's geometry, walked with a port of RM_KnockbackMath.Line/Resolve: the east colonist's 3-cell throw stops at the
     east wall two cells on, the south colonist's stops in the pit's near row, the steel's line reaches p4, no colonist's path
     crosses another colonist, and some floor stack's throw can end exactly on a near-row cell (the covered cell exists)
  T  test_table.json marks the entry present
    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storeroom_bomb_pit.py [--src DIR]
--src reads the mod's files from DIR (laid out like this folder) instead: the way it was watched red on the base commit.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPT = os.path.join(REPO, "design", "concepts", "ExplosiveKnockback")

GUARDS = ["FlowWorks not loaded", "LWM_WeaponsLocker", "lwm.deepstorage", "\"Shelf\"", "\"ShelfSmall\"", "InClosedContainer",
          "IsClosedContainer", "closedContainerMassLimit", "heavyGoodsMinMass", "WantCells(s, \"g_steel\", 2.9f) < 2",
          "RM_PitCover_WovenScrap", "Pit(O(s, -3, -5), 7, 2)", "the thing trace never ran", "not at rest", "p4 was reached",
          "planned path crosses", "put no", "was not planned onto", "storeroom_bomb_pit_control", "FillToSurface",
          "Blast(s.o, 2.9f)", "<= 900"]
OBSERVES = {
    "east colonist stops dead at the east wall with a wall hit": ["\"Wall\"", "O(sc, 3, 0)", "\"impact\""],
    "lands alive and stunned": ["!pE.Dead", "pE_stunned"],
    "south colonist carried about three cells straight south": ["pS.Position.x == s0.x", "s0.z - pS.Position.z <= 4"],
    "every stack with a throw request moved": ["\"request\"", "\"item_move\""],
    "arc, spin, wall rebounds": ["_maxH", "_spin", "\"item_rebound\""],
    "zero despawn-spawn pairs": ["_tele", "tele == 0"],
    "closed container contents unchanged, thrown at least one cell": ["\"container\"", "\"thrown\"", "Hp(sc.things[k]) == sc.numbers[k + \"Hp\"]"],
    "steel strikes the colonist in line, 2 to 5 blunt, a stagger, stops there": ["\"heavy_hit\"", "dmg >= 2f && dmg <= 5f", "stunTicks",
                                                                                "Cheb(st.Position, p4.Position) <= 1"],
    "goods and a colonist on the pit floor, one descent each": ["\"descent\"", "pawnDesc[k] == 1", "Desc(k) == 1"],
    "covered-cell stack falls through, cover destroyed": ["CoverAt(map, cover) == null", "Desc(\"g_cover\") == 1"],
    "control: nothing descends, land on the planned cells": ["falls == 0", "t.Position != plannedTo[k]"],
}

fails = []


def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + " " + what)
    if not ok:
        fails.append(code + " " + what)


# ── a port of RM_KnockbackMath.Line and the parts of Resolve the room meets (walls, diagonal corners, the first open pit cell) ──
def rnd(v):
    return int(v + 0.5) if v >= 0 else -int(-v + 0.5)   # MidpointRounding.AwayFromZero


def line(sx, sz, dx, dz, cells):
    m = max(abs(dx), abs(dz))
    if cells <= 0 or m < 1e-6:
        return []
    tx, tz = sx + rnd(dx / m * cells), sz + rnd(dz / m * cells)
    ddx, ddz = abs(tx - sx), abs(tz - sz)
    stx, stz = (1 if tx > sx else -1), (1 if tz > sz else -1)
    n = max(ddx, ddz)
    return [(sx + (0 if ddx == 0 else stx * rnd(ddx * i / n)), sz + (0 if ddz == 0 else stz * rnd(ddz * i / n))) for i in range(1, n + 1)]


WALLS = {(-4, z) for z in range(-3, 5)} | {(4, z) for z in range(-3, 5)} | {(x, 4) for x in range(-3, 4)}
PIT = {(x, z) for x in range(-3, 4) for z in (-5, -4)}


def resolve(sx, sz, cells, cover=None):
    """(dest, stop) of a throw from (sx, sz) away from the impact (0, 0); `cover` is a pit cell that is ground."""
    px, pz, stop = sx, sz, "Distance"
    for (x, z) in line(sx, sz, sx, sz, cells):
        if x != px and z != pz and ((x, pz) in WALLS or (px, z) in WALLS):
            return (px, pz), "Wall"
        if (x, z) in WALLS:
            return (px, pz), "Wall"
        px, pz = x, z
        if (x, z) in PIT and (x, z) != cover:
            return (px, pz), "Pit"
    return (px, pz), stop


def main():
    root = HERE
    if "--src" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--src") + 1])
    rd = lambda *p: open(os.path.join(root, *p), encoding="utf-8").read() if os.path.exists(os.path.join(root, *p)) else ""
    proof = rd("Source", "RM_KnockbackProof.cs")
    scene = rd("Source", "RM_KnockbackProof_StoreroomBombPit.cs")
    csproj = rd("Source", "RimMandrake_ExplosiveKnockback.csproj")
    if not proof:
        print("UNMEASURED: RM_KnockbackProof.cs not found under %s" % root)
        return 2
    names_m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = re.findall(r'"([a-z0-9_]+)"', names_m.group(1)) if names_m else []
    check("N0", len(names) > 20 and "calibration" in names, "SceneNames parsed (%d names)" % len(names))
    for n in ("storeroom_bomb_pit", "storeroom_bomb_pit_control"):
        check("N1 " + n, n in names, "%s is in SceneNames" % n)
    check("N2", 'case "storeroom_bomb_pit":' in proof and 'case "storeroom_bomb_pit_control":' in proof
          and "return StoreroomBombPit(s);" in proof, "Build routes both lanes to StoreroomBombPit")
    check("N3", 'Include="RM_KnockbackProof_StoreroomBombPit.cs"' in csproj, "the csproj compiles RM_KnockbackProof_StoreroomBombPit.cs")
    scenes = json.load(open(os.path.join(CONCEPT, "scenes.json"), encoding="utf-8"))
    ep = next((x.get("entry_point", "") for x in scenes["scenes"] if x["id"] == "sc_storeroom_bomb_pit"), "")
    check("N4", ep.endswith("RM_KnockbackProof.cs::storeroom_bomb_pit"), "scenes.json entry point is storeroom_bomb_pit (%s)" % (ep or "missing"))

    check("G0", "private static string StoreroomBombPit(Scene s)" in scene, "the builder StoreroomBombPit exists")
    for g in GUARDS:
        check("G " + g, g in scene, "builder/verdict carries %s" % g)
    for clause, needles in OBSERVES.items():
        miss = [n for n in needles if n not in scene]
        check("O " + clause, not miss, "the verdict reads: %s%s" % (clause, (" (missing " + ", ".join(miss) + ")") if miss else ""))
    check("R", "Item(s, " in scene and "ProofSchedule" in scene and "RunRestore" not in scene,
          "the scene spawns through Item/Track (Prepare and the disposable map clean up) and changes no setting or def")

    # K: the geometry, as the kernel walks it (calibration: a colonist one cell out is thrown 3 cells)
    (de, se) = resolve(1, 0, 3)
    check("K1", de == (3, 0) and se == "Wall", "pE (1,0) thrown 3 east stops at the east wall two cells on: %s %s" % (de, se))
    (ds, ss) = resolve(0, -1, 3)
    check("K2", ds == (0, -4) and ss == "Pit", "pS (0,-1) thrown 3 south lands in the pit's near row: %s %s" % (ds, ss))
    steel = line(1, 1, 1, 1, 2)
    check("K3", steel[-1:] == [(3, 3)], "the steel's 2-cell line from (1,1) reaches p4 at (3,3): %s" % steel)
    cols = {"pE": (1, 0), "pS": (0, -1), "pW": (-2, -2), "p4": (3, 3)}
    crossed = [(k, c) for k, (x, z) in cols.items() if k != "p4" for c in line(x, z, x, z, 3) if c in cols.values()]
    check("K4", not crossed, "no colonist's 3-cell path crosses another colonist's cell %s" % crossed)
    used = set(cols.values()) | {(0, 0), (-2, 0), (-3, 0), (1, 1), (-1, 1), (2, -1)}
    hits = []
    for z in range(-2, 1):
        for x in range(-2, 3):
            if (x, z) in used:
                continue
            for cells in range(1, 7):
                d, st = resolve(x, z, cells)
                if st == "Pit" and d[1] == -4 and d != (0, -4) and resolve(x, z, cells, cover=d)[0] == d:
                    hits.append(((x, z), cells, d))
    check("K5", bool(hits), "a floor cell within two cells throws exactly onto a near-row pit cell (%d ways, e.g. %s)"
          % (len(hits), hits[0] if hits else "none"))
    check("K6", (-3, 0) not in WALLS and (-4, 0) in WALLS, "the locker at (-2,0) has a free cell (-3,0) behind it, then the wall")

    tt = json.load(open(os.path.join(CONCEPT, "version", "test_table.json"), encoding="utf-8"))["tests"].get("sc_storeroom_bomb_pit", {})
    check("T", tt.get("entry") == "storeroom_bomb_pit" and tt.get("entry_exists") is True,
          "test_table.json sc_storeroom_bomb_pit entry_exists is %s" % tt.get("entry_exists"))
    print("%s: %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
