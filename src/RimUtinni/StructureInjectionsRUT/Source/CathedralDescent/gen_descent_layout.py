#!/usr/bin/env python3
"""Generate the descent site (CATHEDRAL_DESCENT_REVEAL_SITE_1): every def in Defs/CathedralDescent/.

Deterministic: same source, same bytes. Run from anywhere:

    python3 src/RimUtinni/StructureInjectionsRUT/Source/CathedralDescent/gen_descent_layout.py

Writes, under src/RimUtinni/StructureInjectionsRUT/Defs/CathedralDescent/:
  StructureLayoutDefs_CathedralDescent.xml  the 250x250 KCSG layout RUT_CathedralDescent_Halls
  SymbolDefs_CathedralDescent.xml           symbols for the three things this site adds
  ThingDefs_CathedralDescent.xml            the terminus, the line housing, the line carriage
  SitePartDefs_CathedralDescent.xml         the site part and its two gen steps
  DutyDefs_CathedralDescent.xml             the patrol duty the sentinels walk

Layout grid: row 0 is the north edge (the first <li> KCSG reads), column 0 the west edge.
GenStep_CathedralDescent.cs does not trust that: it finds the terminus on the map and tries
both row orders, keeping the one that puts the arrival cells on open floor.

The map, top to bottom (rows):
  0-14     arrival mouth, the only open cells on any map edge (north, columns 113-137)
  15-84    first hall; a dead-smartsteel ridge (rows 49-51) runs from column 40 to the east wall,
           so the walk goes west round its end and back east
  85-99    ramp down, east side
  100-159  line gallery; the line (rows 125-131) crosses the whole map, west edge to east edge,
           solid but for one crossing at columns 12-14 (west), so the walk goes west and back east
  160-175  ramp down, east side
  176-215  coolant hall; a deep channel (rows 192-196) comes in from the east edge, turns south
           at columns 60-64 and leaves by the south edge, beside the bottom chamber
  216-242  bottom chamber (columns 10-56), the terminus inside it

Rock is RM_CathedralDeckPlate (the kit's rock) with seams of RM_MineableDeadSmartsteel. The
generator refuses to write if the terminus is unreachable from the arrival edge.
"""
import os
import random
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.normpath(os.path.join(HERE, "..", "..", "Defs", "CathedralDescent"))

N = 250
SEED = 1106250
P = "RUT_CathedralDescent_"

LAYOUT = P + "Halls"
SITE = P + "Site"
GENSTEP_STRUCTURE = P + "GenStepStructure"
GENSTEP_FINISH = P + "GenStepFinish"
DUTY = P + "Patrol"
TERMINUS = P + "Terminus"
HOUSING = P + "LineHousing"
CARRIAGE = P + "LineCarriage"
SYM_TERMINUS = P + "SymTerminus"
SYM_HOUSING = P + "SymLineHousing"
SYM_CARRIAGE = P + "SymLineCarriage"

# Kit and vanilla defs placed raw (KCSG resolves a bare ThingDef name).
ROCK = "RM_CathedralDeckPlate"          # mandrake.rm.rustcathedral (in mandrake.rm.biomes)
SEAM = "RM_MineableDeadSmartsteel"      # same kit
PILLAR = "RM_SacredWall_Conduit"        # same kit
FILTH = ["Filth_MachineBits", "Filth_RubbleBuilding"]   # Core
FLOOR = "RM_RustCathedral_PolymerFloor"     # kit
SOIL = "RM_RustCathedral_CrackedMetalSoil"  # kit
SHALLOW = "RM_CoolantShallow"   # mandrake.rm.flowworks
DEEP = "RM_CoolantDeep"         # mandrake.rm.flowworks (WaterDeepBase: impassable)
ROCK_TERRAIN = "Gravel"         # under rock only; never an open floor
OPEN_TERRAINS = [FLOOR, SOIL, SHALLOW, DEEP]

ARRIVAL_ROWS = (0, 14)
ARRIVAL_COLS = (113, 137)
LINE_ROWS = (125, 131)
CROSSING_COLS = (12, 14)
CHANNEL_ROWS = (192, 196)
CHANNEL_COLS = (60, 64)
CHAMBER = (216, 242, 10, 56)        # r0, r1, c0, c1 (walls on the border)
CHAMBER_DOOR_COLS = (30, 35)
TERMINUS_CELL = (232, 33)

# Patrol groups: pawn kinds (vanilla mechanoids) and a loop of waypoints, (row, col).
PATROLS = [
    (["Mech_Pikeman", "Mech_Pikeman"], [(30, 60), (30, 190), (70, 190), (70, 60)]),
    (["Mech_Lancer", "Mech_Lancer", "Mech_Pikeman"], [(115, 40), (115, 215), (145, 215), (145, 40)]),
    (["Mech_Pikeman", "Mech_Pikeman"], [(182, 200), (182, 30), (205, 30), (185, 120)]),
]

TEXT = {
    SITE: ("the long descent",
           "A mouth in the rock, and halls below it, one under another. Far down, a line of old machinery "
           "crosses them from wall to wall, and a channel of coolant runs beside it to the lowest room."),
    TERMINUS: ("dead relay mast",
               "A relay mast bolted to the floor of the lowest room. The dish is bent, the housing is cold and "
               "the cables at its foot are cut. It is fixed fast: nothing here lifts it, cuts it loose or breaks it."),
    HOUSING: ("line housing",
              "Plated housing around the line, rivet on rivet, too heavy to move and sealed shut."),
    CARRIAGE: ("line carriage",
               "A carriage stopped on the line, hooks lowered, its load long gone."),
}


def box(grid, r0, r1, c0, c1, value):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            grid[r][c] = value


def build():
    """Return (terrain, things): terrain[r][c] a terrain defName, things[r][c] a symbol or '.'."""
    terrain = [[ROCK_TERRAIN] * N for _ in range(N)]
    things = [[ROCK] * N for _ in range(N)]

    def open_(r0, r1, c0, c1, floor):
        box(terrain, r0, r1, c0, c1, floor)
        box(things, r0, r1, c0, c1, ".")

    open_(ARRIVAL_ROWS[0], ARRIVAL_ROWS[1], ARRIVAL_COLS[0], ARRIVAL_COLS[1], SOIL)
    open_(15, 84, 8, 241, FLOOR)
    box(things, 49, 51, 40, 241, SEAM)                 # the ridge
    box(terrain, 49, 51, 40, 241, ROCK_TERRAIN)
    open_(85, 99, 210, 235, SOIL)
    open_(100, 159, 8, 241, FLOOR)
    open_(160, 175, 210, 235, SOIL)
    open_(176, 215, 8, 241, FLOOR)

    # pillars in the halls, 3x3, kept off the walking lanes' ends
    for r0 in (24, 72, 108, 150, 182, 206):
        for c0 in range(28, 230, 24):
            if r0 in (182, 206) and c0 < 70:
                continue
            box(things, r0, r0 + 2, c0, c0 + 2, PILLAR)

    # the line: housing on every row of the band, a carriage every fourth cell of its middle row
    for r in range(LINE_ROWS[0], LINE_ROWS[1] + 1):
        for c in range(N):
            terrain[r][c] = FLOOR
            things[r][c] = HOUSING
    mid = (LINE_ROWS[0] + LINE_ROWS[1]) // 2
    for c in range(0, N, 4):
        things[mid][c] = CARRIAGE
    open_(LINE_ROWS[0], LINE_ROWS[1], CROSSING_COLS[0], CROSSING_COLS[1], SOIL)

    # coolant: deep channel from the east edge to the bend, then south to the south edge; shallow banks in the hall
    box(terrain, CHANNEL_ROWS[0] - 2, CHANNEL_ROWS[1] + 2, CHANNEL_COLS[0] - 2, 241, SHALLOW)
    box(things, CHANNEL_ROWS[0] - 2, CHANNEL_ROWS[1] + 2, CHANNEL_COLS[0] - 2, 241, ".")
    box(terrain, CHANNEL_ROWS[0] + 3, 215, CHANNEL_COLS[0] - 2, CHANNEL_COLS[1] + 2, SHALLOW)
    for r0, r1, c0, c1 in ((CHANNEL_ROWS[0], CHANNEL_ROWS[1], CHANNEL_COLS[0], N - 1),
                           (CHANNEL_ROWS[0], N - 1, CHANNEL_COLS[0], CHANNEL_COLS[1])):
        box(terrain, r0, r1, c0, c1, DEEP)
        box(things, r0, r1, c0, c1, ".")

    # bottom chamber: dead-smartsteel walls, one door in the north wall
    r0, r1, c0, c1 = CHAMBER
    open_(r0 + 1, r1 - 1, c0 + 1, c1 - 1, SOIL)
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if r in (r0, r1) or c in (c0, c1):
                things[r][c] = SEAM
                terrain[r][c] = ROCK_TERRAIN
    open_(r0, r0, CHAMBER_DOOR_COLS[0], CHAMBER_DOOR_COLS[1], SOIL)
    things[TERMINUS_CELL[0]][TERMINUS_CELL[1]] = TERMINUS

    rng = random.Random(SEED)
    for r in range(N):
        for c in range(N):
            if things[r][c] == ROCK and rng.random() < 0.03:
                things[r][c] = SEAM
            elif things[r][c] == "." and terrain[r][c] in (FLOOR, SOIL) and rng.random() < 0.012:
                if not (ARRIVAL_ROWS[0] <= r <= ARRIVAL_ROWS[1]) and abs(r - TERMINUS_CELL[0]) + abs(c - TERMINUS_CELL[1]) > 8:
                    things[r][c] = FILTH[rng.randrange(len(FILTH))]
    return terrain, things


def walkable(terrain, things, r, c):
    return terrain[r][c] != DEEP and (things[r][c] == "." or things[r][c].startswith("Filth_"))


def walk_lengths(terrain, things):
    """BFS from every arrival edge cell; return distance to a cell beside the terminus (None if unreachable)."""
    dist = {}
    q = deque()
    for c in range(ARRIVAL_COLS[0], ARRIVAL_COLS[1] + 1):
        dist[(0, c)] = 0
        q.append((0, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in dist and walkable(terrain, things, nr, nc):
                dist[(nr, nc)] = dist[(r, c)] + 1
                q.append((nr, nc))
    tr, tc = TERMINUS_CELL
    near = [dist[(tr + dr, tc + dc)] for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (tr + dr, tc + dc) in dist]
    return (min(near) if near else None), dist


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


HEADER = '<?xml version="1.0" encoding="utf-8"?>\n<!-- GENERATED by Source/CathedralDescent/gen_descent_layout.py: edit the generator, not this file. -->\n'


def render_layout(terrain, things):
    out = [HEADER, "<Defs>\n  <KCSG.StructureLayoutDef>\n", "    <defName>%s</defName>\n" % LAYOUT,
           "    <spawnConduits>false</spawnConduits>\n    <terrainGrid>\n"]
    sym = {TERMINUS: SYM_TERMINUS, HOUSING: SYM_HOUSING, CARRIAGE: SYM_CARRIAGE}
    out += ["      <li>%s</li>\n" % ",".join(row) for row in terrain]
    out.append("    </terrainGrid>\n    <layouts>\n      <li>\n")
    out += ["        <li>%s</li>\n" % ",".join(sym.get(s, s) for s in row) for row in things]
    out.append("      </li>\n    </layouts>\n  </KCSG.StructureLayoutDef>\n</Defs>\n")
    return "".join(out)


def render_symbols():
    out = [HEADER, "<Defs>\n"]
    for s, t in ((SYM_TERMINUS, TERMINUS), (SYM_HOUSING, HOUSING), (SYM_CARRIAGE, CARRIAGE)):
        out.append("  <KCSG.SymbolDef>\n    <defName>%s</defName>\n    <thing>%s</thing>\n"
                   "    <spawnPartOfFaction>false</spawnPartOfFaction>\n  </KCSG.SymbolDef>\n" % (s, t))
    out.append("</Defs>\n")
    return "".join(out)


THING = """  <ThingDef ParentName="BuildingBase">
    <defName>{name}</defName>
    <label>{label}</label>
    <description>{desc}</description>
    <thingClass>Building</thingClass>
    <graphicData>
      <texPath>{tex}</texPath>
      <graphicClass>{gclass}</graphicClass>
      <drawSize>{draw}</drawSize>
    </graphicData>
    <altitudeLayer>Building</altitudeLayer>
    <passability>Impassable</passability>
    <fillPercent>{fill}</fillPercent>
    <rotatable>false</rotatable>
    <size>(1,1)</size>
    <useHitPoints>false</useHitPoints>
    <destroyable>false</destroyable>
    <statBases>
      <Flammability>0</Flammability>
      <Beauty>-2</Beauty>
    </statBases>
    <building>
      <deconstructible>false</deconstructible>
      <claimable>false</claimable>
      <isInert>true</isInert>
    </building>
  </ThingDef>
"""

# Graphics reused as-is (no new art): Odyssey's ancient antenna, Core's ancient pipes and generator ruins.
GRAPHICS = {
    TERMINUS: ("Things/Building/Ancient/MilitaryCompound/AncientAntenna", "Graphic_Random", "(2,2)", "0.5"),
    HOUSING: ("Things/Building/Ruins/AncientPipes", "Graphic_Random", "(1,1)", "1"),
    CARRIAGE: ("Things/Building/Ruins/AncientGenerator", "Graphic_Random", "(2,2)", "1"),
}


def render_things():
    out = [HEADER, "<Defs>\n"]
    for name in (TERMINUS, HOUSING, CARRIAGE):
        tex, gclass, draw, fill = GRAPHICS[name]
        label, desc = TEXT[name]
        out.append(THING.format(name=name, label=esc(label), desc=esc(desc), tex=tex, gclass=gclass, draw=draw, fill=fill))
    out.append("</Defs>\n")
    return "".join(out)


def render_site():
    label, desc = TEXT[SITE]
    li = lambda xs, ind: "".join("%s<li>%s</li>\n" % (ind, x) for x in xs)
    patrols = []
    for kinds, points in PATROLS:
        patrols.append("          <li>\n            <kinds>\n%s            </kinds>\n            <waypoints>\n%s"
                       "            </waypoints>\n          </li>\n"
                       % (li(kinds, " " * 14), li(["(%d,%d)" % (c, r) for r, c in points], " " * 14)))
    return (HEADER + """<Defs>
  <SitePartDef>
    <defName>{site}</defName>
    <label>{label}</label>
    <description>{desc}</description>
    <siteTexture>World/WorldObjects/Sites/GenericSite</siteTexture>
    <expandingIconTexture>World/WorldObjects/Expanding/AncientStructure</expandingIconTexture>
    <minMapSize>({n},1,{n})</minMapSize>
    <wantsThreatPoints>false</wantsThreatPoints>
    <gravShipsCanLandOn>false</gravShipsCanLandOn>
    <considerEnteringAsAttack>false</considerEnteringAsAttack>
    <forceExitAndRemoveMapCountdownDurationDays>4</forceExitAndRemoveMapCountdownDurationDays>
    <tags>
      <li>{site}</li>
    </tags>
  </SitePartDef>
  <GenStepDef>
    <defName>{gs1}</defName>
    <linkWithSite>{site}</linkWithSite>
    <order>400</order>
    <genStep Class="KCSG.GenStep_CustomStructureGen">
      <fullClear>true</fullClear>
      <clearFogInRect>false</clearFogInRect>
      <structureLayoutDefs>
        <li>{layout}</li>
      </structureLayoutDefs>
    </genStep>
  </GenStepDef>
  <GenStepDef>
    <defName>{gs2}</defName>
    <linkWithSite>{site}</linkWithSite>
    <order>401</order>
    <genStep Class="RimMandrake.Utinni.StructureInjectionsRUT.GenStep_CathedralDescent">
      <layoutSize>{n}</layoutSize>
      <terminusDef>{terminus}</terminusDef>
      <terminusCell>({tc},{tr})</terminusCell>
      <arrivalRow>0</arrivalRow>
      <arrivalCols>({a0},{a1})</arrivalCols>
      <rockDef>{rock}</rockDef>
      <openTerrains>
{open}      </openTerrains>
      <lineDefs>
        <li>{housing}</li>
        <li>{carriage}</li>
      </lineDefs>
      <dutyDef>{duty}</dutyDef>
      <patrols>
{patrols}      </patrols>
    </genStep>
  </GenStepDef>
</Defs>
""").format(site=SITE, label=esc(label), desc=esc(desc), n=N, gs1=GENSTEP_STRUCTURE, gs2=GENSTEP_FINISH, layout=LAYOUT,
            terminus=TERMINUS, tc=TERMINUS_CELL[1], tr=TERMINUS_CELL[0], a0=ARRIVAL_COLS[0], a1=ARRIVAL_COLS[1],
            rock=ROCK, open=li(OPEN_TERRAINS, " " * 8), housing=HOUSING, carriage=CARRIAGE, duty=DUTY,
            patrols="".join(patrols))


def render_duty():
    return HEADER + """<Defs>
  <DutyDef>
    <defName>%s</defName>
    <thinkNode Class="ThinkNode_Priority">
      <subNodes>
        <li Class="RimMandrake.Utinni.StructureInjectionsRUT.JobGiver_CathedralDescentPatrol" />
      </subNodes>
    </thinkNode>
  </DutyDef>
</Defs>
""" % DUTY


def main():
    terrain, things = build()
    walk, dist = walk_lengths(terrain, things)
    if walk is None:
        print("REFUSED: the terminus is unreachable from the arrival edge")
        return 1
    for kinds, points in PATROLS:
        for p in points:
            if p not in dist:
                print("REFUSED: waypoint %s is not reachable open floor" % (p,))
                return 1
    os.makedirs(DEFS, exist_ok=True)
    files = {
        "StructureLayoutDefs_CathedralDescent.xml": render_layout(terrain, things),
        "SymbolDefs_CathedralDescent.xml": render_symbols(),
        "ThingDefs_CathedralDescent.xml": render_things(),
        "SitePartDefs_CathedralDescent.xml": render_site(),
        "DutyDefs_CathedralDescent.xml": render_duty(),
    }
    for name, text in sorted(files.items()):
        with open(os.path.join(DEFS, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("wrote %s (%d bytes)" % (name, len(text.encode("utf-8"))))
    print("walk arrival edge -> terminus: %d cells; map %dx%d" % (walk, N, N))
    return 0


if __name__ == "__main__":
    sys.exit(main())
