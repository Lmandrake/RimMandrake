#!/usr/bin/env python3
"""gen_spire_layout.py - generate the one KCSG template of the Spire.

The Spire IS the Scald's dark tower (owner, 2026-10-10, story sitting card 6:
"They are the same building. It's in the mountains, visible from the huge
sea/lake of the Scald"). SPIRE_DUNGEONS_MERGE_DARK_TOWER folded two built
dungeons (SCALD_DARK_TOWER_1, ASHFALL_RESEARCH_BASE_1) into this one; design of
record: design/Jawa/worldbuilding/ashfall_research_base.md section 7.

Which layout survived: the dark tower's two-ward 121 grammar (it alone was ruled
LARGE). Its water moat went, because the building stands in the mountains and is
seen from the lake, not in it: the moat bands are a gravel apron now.

How the Helix study and the Rakatan high command share it, outside in:

  d 0-5    apron        bare gravel, nothing on it
  d 6      hull         RUT_SpireHullWall, one gap, filled by RUT_SpireSeal
  d 7-26   outer ward   the Helix study: containment line, specimen galleries
  d 27     keep wall    one real door, so the two garrisons never share sight
  d 28-48  inner ward   the Rakatan garrison that never stood down
  d 49     core wall    one gap
  d 50-54  command deck the Cathedral's control systems
  d 55     vault wall   one real door
  d 56+    isolated room  the command console and the codes

The garrisons sit behind a closed door because the Helix's pass over the
machines is fiction the engine does not carry here: a Mechanoid and a Helix in
sight of each other would simply fight.

Entry: the seal opens on the Cathedral's trust (Source/Spire/SpireEntry.cs). The
hull takes no damage and GenStep_SpireRoof roofs it with thick rock, so the seal
is the only way in; the codes are taken inside and nowhere else.

The ocular warped Assailants stay a filth trail past the keep door. The owner has
not said whether they are the Contagion's Ocular lineage, and no fauna exists.

Offline: refuses to write unless the core is reachable through the door lap.
Run: python3 gen_spire_layout.py
Writes: ../../Defs/Spire/StructureLayoutDefs_Spire.xml, ../../Defs/Spire/SymbolDefs_Spire.xml
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Defs", "Spire")
DEFNAME = "RUT_Spire_HighCommand"

PAWN_SYMBOLS = [
    # (symbolDefName, pawnKindDef, faction): RUT_Symbol_Mech* live in SymbolDefs_Vaults.xml
    ("RUT_Symbol_HelixGrunt", "RUT_Jawa_Helix_Grunt", "RUT_Jawa_AscendantHelix"),
    ("RUT_Symbol_HelixHeavy", "RUT_Jawa_Helix_Heavy", "RUT_Jawa_AscendantHelix"),
    ("RUT_Symbol_HelixSpecialist", "RUT_Jawa_Helix_Specialist", "RUT_Jawa_AscendantHelix"),
    ("RUT_Symbol_HelixLeader", "RUT_Jawa_Helix_Leader", "RUT_Jawa_AscendantHelix"),
]

THING_SYMBOLS = [
    # (symbolDefName, thingDefName, stuff, factionless)
    ("RUT_Symbol_TeslaTurret", "VFES_Turret_TeslaBlaster", None, False),
    ("RUT_Symbol_Railgun", "VFES_Turret_ChargeRailgun", None, False),
    ("RUT_Symbol_SpireHull", "RUT_SpireHullWall", None, True),
    ("RUT_Symbol_SpireSeal", "RUT_SpireSeal", None, True),
    ("RUT_Symbol_SpireDoor", "Door", "Plasteel", True),
    ("RUT_Symbol_SpireControlConsole", "RUT_SpireControlConsole", None, True),
    ("RUT_Symbol_SpireCommandConsole", "RUT_SpireCommandConsole", None, True),
    ("RUT_Symbol_AshfallSpecimenCell", "RUT_AshfallSpecimenCell", None, True),
    ("RUT_Symbol_RakatanCommandCodes", "RUT_RakatanCommandCodes", None, True),
]

SYMBOLDEF_PAWN_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <pawnKindDef>{pawnKindDef}</pawnKindDef>
    <spawnPartOfFaction>false</spawnPartOfFaction>
    <faction>{faction}</faction>
    <numberToSpawn>1</numberToSpawn>
    <spawnDead>false</spawnDead>
    <spawnRotten>false</spawnRotten>
    <defendSpawnPoint>true</defendSpawnPoint>
  </KCSG.SymbolDef>
"""

SYMBOLDEF_THING_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <thing>{thing}</thing>{extra}
  </KCSG.SymbolDef>
"""


def gen_symboldefs():
    body = []
    for name, kind, faction in PAWN_SYMBOLS:
        body.append(SYMBOLDEF_PAWN_TMPL.format(defName=name, pawnKindDef=kind, faction=faction))
    for name, thing, stuff, factionless in THING_SYMBOLS:
        extra = ""
        if stuff:
            extra += "\n    <stuff>%s</stuff>" % stuff
        if factionless:
            extra += "\n    <spawnPartOfFaction>false</spawnPartOfFaction>"
        body.append(SYMBOLDEF_THING_TMPL.format(defName=name, thing=thing, extra=extra))
    return '<?xml version="1.0" encoding="utf-8"?>\n<Defs>\n' + "\n".join(body) + "</Defs>\n"


N = 121
MID = N // 2  # 60
HULL_D = 6
KEEP_WALL_D = 27
CORE_WALL_D = 49
VAULT_WALL_D = 55

HULL_SYM = "RUT_Symbol_SpireHull"
SEAL_SYM = "RUT_Symbol_SpireSeal"
DOOR_SYM = "RUT_Symbol_SpireDoor"
WALL_SYM = "Wall_Plasteel"

APRON_FLOOR = "Gravel"
FLOOR = "Concrete"

HULL_GATE = (HULL_D, MID)                 # north face, the seal
KEEP_DOOR = (N - 1 - KEEP_WALL_D, MID)    # south face, a door
CORE_GAP = (MID, N - 1 - CORE_WALL_D)     # east face, open
VAULT_DOOR = (MID, VAULT_WALL_D)          # west face, a door

# Every wall's opening: an entry past each ring means walking the whole ward.
OPENINGS = {
    HULL_GATE: SEAL_SYM,
    KEEP_DOOR: DOOR_SYM,
    CORE_GAP: ".",
    VAULT_DOOR: DOOR_SYM,
}

OUTER_WARD = [
    "RUT_Symbol_TeslaTurret", "RUT_Symbol_HelixGrunt", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_Railgun", "RUT_Symbol_HelixHeavy", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_TeslaTurret", "RUT_Symbol_HelixSpecialist", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_Railgun", "RUT_Symbol_HelixGrunt", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_TeslaTurret", "RUT_Symbol_HelixHeavy", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_Railgun", "RUT_Symbol_HelixGrunt", "RUT_Symbol_AshfallSpecimenCell",
]

# The Helix's officer holds the keep door from the study side.
KEEP_DOOR_GUARD = ("RUT_Symbol_HelixLeader", (KEEP_DOOR[0] + 2, MID))

INNER_WARD = [
    "RUT_Symbol_MechLancer", "RUT_Symbol_MechCenturion", "Turret_AutoInferno",
    "RUT_Symbol_MechLancer", "Turret_AutoMortar", "RUT_Symbol_MechCenturion",
    "RUT_Symbol_MechLancer", "Turret_AutoInferno", "RUT_Symbol_MechCenturion",
    "RUT_Symbol_GravRailArtillery", "RUT_Symbol_MechCenturion", "RUT_Symbol_SingularityCannon",
    "RUT_Symbol_MechLancer", "RUT_Symbol_GravRailArtillery", "RUT_Symbol_MechCenturion",
    "Turret_AutoMortar", "RUT_Symbol_SingularityCannon", "RUT_Symbol_MechLancer",
    "RUT_Symbol_GravRailArtillery", "RUT_Symbol_MechCenturion", "Turret_AutoInferno",
    "RUT_Symbol_MechLancer",
]

BREACH_TRAIL = ["Filth_MachineBits", "Filth_BlastMark", "Filth_Blood",
                "Filth_Blood", "Filth_MachineBits"]

CONTROL_CONSOLE = ("RUT_Symbol_SpireControlConsole", (52, MID))
COMMAND_CONSOLE = ("RUT_Symbol_SpireCommandConsole", (MID, MID))
CODES = ("RUT_Symbol_RakatanCommandCodes", (MID - 1, MID))
DECK_TURRETS = [("Turret_MiniTurret", (52, 57)), ("Turret_MiniTurret", (52, 63)),
                ("Turret_MiniTurret", (68, MID)), ("Turret_MiniTurret", (MID, 52))]


def dist(r, c):
    return min(r, c, N - 1 - r, N - 1 - c)


def band_cells(layout, lo, hi):
    cells = []
    for r in range(N):
        for c in range(N):
            if lo <= dist(r, c) <= hi and layout[r][c] == ".":
                cells.append((r, c))
    return cells


def scatter(layout, cells, symbols):
    step = max(1, len(cells) // len(symbols))
    for i, sym in enumerate(symbols):
        r, c = cells[(i * step + step // 2) % len(cells)]
        layout[r][c] = sym


def build():
    layout = [["."] * N for _ in range(N)]
    terrain = [[FLOOR] * N for _ in range(N)]

    rings = {HULL_D: HULL_SYM, KEEP_WALL_D: WALL_SYM, CORE_WALL_D: WALL_SYM, VAULT_WALL_D: WALL_SYM}
    for r in range(N):
        for c in range(N):
            d = dist(r, c)
            if d < HULL_D:
                terrain[r][c] = APRON_FLOOR
            elif d in rings:
                layout[r][c] = OPENINGS.get((r, c), rings[d])

    # The cells around the openings stay clear, so nothing scattered plugs a door.
    def clear_of_doors(cells):
        return [(r, c) for r, c in cells
                if all(abs(r - o[0]) + abs(c - o[1]) > 3 for o in OPENINGS)]

    guard_sym, (gr, gc) = KEEP_DOOR_GUARD
    layout[gr][gc] = guard_sym
    scatter(layout, clear_of_doors(band_cells(layout, HULL_D + 1, KEEP_WALL_D - 1)), OUTER_WARD)
    scatter(layout, clear_of_doors(band_cells(layout, KEEP_WALL_D + 1, CORE_WALL_D - 1)), INNER_WARD)

    # Five cells walking inward from past the keep door: something forced its way
    # this far and no further.
    kr, kc = KEEP_DOOR
    for i, sym in enumerate(BREACH_TRAIL):
        layout[kr - (i + 2)][kc + i - len(BREACH_TRAIL) // 2] = sym

    for sym, (r, c) in [CONTROL_CONSOLE, COMMAND_CONSOLE, CODES] + DECK_TURRETS:
        layout[r][c] = sym

    return layout, terrain


def blocks(sym):
    """Pawns, filth, codes and doors are walkable; every building here is not."""
    return not (sym == "." or sym == DOOR_SYM or sym.startswith("Filth_")
                or sym in (CODES[0], KEEP_DOOR_GUARD[0])
                or sym in {p[0] for p in PAWN_SYMBOLS}
                or sym.startswith("RUT_Symbol_Mech"))


def reachable_core(layout):
    """The codes' cell, entered through the opened seal, by walking only."""
    start = (HULL_GATE[0] + 1, MID)
    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in seen and not blocks(layout[nr][nc]):
                seen.add((nr, nc))
                stack.append((nr, nc))
    return CODES[1] in seen


def render(layout, terrain):
    rows_xml = "\n".join("        <li>%s</li>" % ",".join(row) for row in layout)
    terr_xml = "\n".join("      <li>%s</li>" % ",".join(row) for row in terrain)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <KCSG.StructureLayoutDef>
    <defName>{DEFNAME}</defName>
    <spawnConduits>false</spawnConduits>
    <terrainGrid>
{terr_xml}
    </terrainGrid>
    <layouts>
      <li>
{rows_xml}
      </li>
    </layouts>
  </KCSG.StructureLayoutDef>
</Defs>
"""


def main():
    layout, terrain = build()
    if not reachable_core(layout):
        raise SystemExit("REFUSING TO WRITE: the codes are not reachable through the door lap.")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "StructureLayoutDefs_Spire.xml"), "w", newline="\n") as f:
        f.write(render(layout, terrain))
    with open(os.path.join(OUT_DIR, "SymbolDefs_Spire.xml"), "w", newline="\n") as f:
        f.write(gen_symboldefs())
    print("wrote %s %dx%d and %d symbols" % (DEFNAME, N, N, len(PAWN_SYMBOLS) + len(THING_SYMBOLS)))


if __name__ == "__main__":
    main()
