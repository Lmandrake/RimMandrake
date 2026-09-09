#!/usr/bin/env python3
"""gen_dark_tower_layout.py - generate SCALD_DARK_TOWER_1's KCSG
StructureLayoutDef: the dark tower, the Rakatan's ground-based high command,
rising from RUT_TheScald's crater lake.

Full spec: infrastructure/state/items/SCALD_DARK_TOWER_1.md (owner ruling,
2026-09-07). Precedent this follows, not duplicates: StructureInjectionsRUT/
Source/VaultDungeons/gen_vault_layouts.py (VAULT_DUNGEON_BUILD_1) - same KCSG
StructureLayoutDef/SymbolDef format, same "every third-party or our-own
ThingDef/PawnKindDef needs an explicit KCSG.SymbolDef wrapper, vanilla/DLC
content is safe bare" rule (read from KCSG's own ResolveSymbols(), see that
file's header for the full citation - not re-derived here).

WHAT MAKES THIS SITE DIFFERENT FROM ITS TWO SIBLINGS (dungeons_arc_spec.md's
arc), stated up front because it drove every layout choice below:

  - VAULT_DUNGEON_BUILD_1 type (1) "mechanoid garrison held": ONE wall ring,
    ONE garrison band, core 13-15 wide, footprint 51-61. Fixed, disciplined,
    but modest in scale - one vault among six.
  - ANCIENT_WAR_LAB_1: frozen/inert on arrival, a delivered AIPersonaCore is
    the thaw-gate that turns the guardians hostile - see that item's build
    spec.
  - THIS SITE is neither. SCALD_DARK_TOWER_1 names it the Rakatan's
    GROUND-BASED HIGH COMMAND, "fierce defenses... garrisons that never got
    the order to stand down" - i.e. ALREADY LIVE, no thaw-gate, no delivered
    item, nothing dormant. And it is explicitly NOT a small template: "a
    LARGE, vertically-emphasized structure." So this layout is built with
    TWO full wall rings and TWO full garrison wards (not one), a footprint
    (121) roughly double the largest vault (61), and an outer WATER MOAT
    band standing in for "rises from the crater lake" - RimWorld has no
    z-axis, so the "vertical emphasis" a top-down grid can actually deliver
    is the tiered/ascending ring grammar itself (moat -> curtain -> keep ->
    core, each band narrower and harder than the last, echoing the Rust
    Cathedral sheet's own "wall ladder" tiering); a true skyline silhouette
    (a tall spire graphic) is an ART pass, not attempted here - see the
    bottom of this docstring.

THE RUST CATHEDRAL TIE: the core holds ONE new building,
RUT_DarkTowerControlConsole (../ThingDefs_Buildings/
RUT_DarkTowerControlConsole.xml) - read that file's own header for why the
tie is authored as narrative/structural (a labelled, described building) and
NOT as a second mood/mechanic system: RUST_CATHEDRAL_MECHANICS_1 owns the
Cathedral's hum-mood attitude system and that C# is not built yet:
"reuse/extend that pattern rather than inventing a parallel one"
(SCALD_DARK_TOWER_1) forbids faking a parallel mechanic here.

🔴 HARD STOP HONOURED - the "ocular warped Assailants that pressed their way
inside" (SCALD_DARK_TOWER_1's own text) are NOT authored anywhere in this
file. The owner has not confirmed whether they are the Contagion's Ocular
lineage (the_contagion.md / OCULAR_OVERDRIVE_SITE_1) or a separate warped
variant, and SCALD_DARK_TOWER_1 says explicitly to confirm before authoring
that fauna. What this generator DOES place: a small trail of vanilla Filth
(Filth_Blood / Filth_MachineBits / Filth_BlastMark - all Core, auto-symbol'd
bare) cutting from the keep-wall door toward the core, in BREACH_TRAIL below
- pure environmental storytelling ("something forced its way in this far"),
no creature def, no PawnKindDef, no strain identity implied. Whoever builds
the real intruder threat after the owner rules the strain question should
site it along or past this trail, not invent a new entry point.

Run: python3 gen_dark_tower_layout.py
Writes: ../../Defs/DarkTower/StructureLayoutDefs_DarkTower.xml,
        ../../Defs/DarkTower/SymbolDefs_DarkTower.xml
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Defs", "DarkTower")

# --- Symbols this template needs that VaultDungeons/SymbolDefs_Vaults.xml
# does NOT already ship (same mod, mandrake.rut.injections - RUT_Symbol_
# MechLancer/MechCenturion/GravRailArtillery/SingularityCannon are already
# registered defNames from that sibling file and are used BARE below, by
# their own defName, exactly as the vault templates use them - no need to
# redefine a KCSG.SymbolDef that already exists in the loaded mod). -------
THING_SYMBOLS = [
    # (symbolDefName, thingDefName, note)
    ("RUT_Symbol_DarkTowerConsole", "RUT_DarkTowerControlConsole",
     "The Rust Cathedral tie (see that ThingDef's own header). Our own "
     "ThingDef -> needs this wrapper. Spawned factionless like "
     "RUT_Symbol_VaultHeart so the crew can claim it once the garrison "
     "outside is cleared."),
]
FACTIONLESS_THING_SYMBOLS = {"RUT_Symbol_DarkTowerConsole"}

SYMBOLDEF_THING_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <thing>{thing}</thing>{extra}
  </KCSG.SymbolDef>
"""


def gen_symboldefs():
    body = []
    for name, thing, note in THING_SYMBOLS:
        extra = "\n    <spawnPartOfFaction>false</spawnPartOfFaction>" if name in FACTIONLESS_THING_SYMBOLS else ""
        body.append(SYMBOLDEF_THING_TMPL.format(defName=name, thing=thing, extra=extra))
    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n" + "".join(body) + "</Defs>\n"


# --- Layout geometry -----------------------------------------------------
# Concentric SQUARE rings by Chebyshev distance-to-border d(r,c) =
# min(r, c, N-1-r, N-1-c). Band boundaries, outer to inner:
#
#   d  0.. 2   water, deep     RUT_ScaldWaterDeep     (3 cells)
#   d  3.. 5   water, shallow  RUT_ScaldWaterShallow  (3 cells)
#   d  6       outer wall      Wall_Plasteel, door on the NORTH face
#   d  7..26   ward 1 (curtain)   Concrete floor, Sentinel garrison   (20)
#   d  27      keep wall       Wall_Plasteel, door on the SOUTH face (offset
#                               180 deg from the outer door)
#   d 28..48   ward 2 (inner)  Concrete floor, denser garrison + doctrine
#                               turrets, closer to high command          (21)
#   d  49      core wall       Wall_Plasteel, door on the EAST face
#                               (offset again - three doors, three different
#                               faces: north -> south -> east forces a full
#                               lap of BOTH wards, never a straight line)
#   d >=50     core interior   Concrete floor, the console + a hugging
#                               point-defense ring (spawnConduits=true, same
#                               shape as RUT_VaultHeart's circuit)
#
# The water bands are not a new hazard: RUT_TheScald's own terrains already
# carry the boiling-lift burn-on-traversal mechanic (the_scald.md SS0/SS5) -
# reaching the tower at all means crossing water that already hurts. Nothing
# new is invented to make the moat a defense; it already is one.
N = 121
WATER_DEEP_W = 3
WATER_SHALLOW_W = 3
OUTER_WALL_D = WATER_DEEP_W + WATER_SHALLOW_W                      # 6
WARD1_W = 20
KEEP_WALL_D = OUTER_WALL_D + 1 + WARD1_W                           # 27
WARD2_W = 21
CORE_WALL_D = KEEP_WALL_D + 1 + WARD2_W                            # 49
CORE_START_D = CORE_WALL_D + 1                                     # 50
CORE_SIZE = N - 2 * CORE_START_D                                   # 21

OUTER_WALL_SYM = "Wall_Plasteel"
KEEP_WALL_SYM = "Wall_Plasteel"
CORE_WALL_SYM = "Wall_Plasteel"
WARD_FLOOR = "Concrete"
CORE_FLOOR = "Concrete"

MID = N // 2  # 60
OUTER_DOOR = (OUTER_WALL_D, MID)                    # north face
KEEP_DOOR = (N - 1 - KEEP_WALL_D, MID)               # south face
CORE_DOOR = (MID, N - 1 - CORE_WALL_D)               # east face
DOORS = {OUTER_DOOR, KEEP_DOOR, CORE_DOOR}

# Ward 1 (curtain, the fight begins): the Arsenal roster shared with the
# vault type (1) template and ANCIENT_WAR_LAB_1's lab guardians - the same
# "Forgotten Sentinels" garrisoning everything Rakatan, per
# the_forgotten_war.md R-W1. RUT_Symbol_MechLancer/MechCenturion/
# GravRailArtillery/SingularityCannon are already defined in
# SymbolDefs_Vaults.xml (same mod) - reused bare, not redefined.
WARD1_GARRISON = [
    "RUT_Symbol_MechLancer", "RUT_Symbol_MechCenturion",
    "Turret_AutoInferno", "RUT_Symbol_MechLancer",
    "Turret_AutoMortar", "RUT_Symbol_MechCenturion",
    "RUT_Symbol_MechLancer", "Turret_AutoInferno",
    "RUT_Symbol_MechCenturion", "RUT_Symbol_GravRailArtillery",
]

# Ward 2 (inner, guarding high command directly): denser, and where the
# doctrine-tier emplacements concentrate - "fierce... same military register
# as the Forgotten Arsenal" (SCALD_DARK_TOWER_1) means the closer ring to
# the console is the harder one, not a repeat of ward 1.
WARD2_GARRISON = [
    "RUT_Symbol_MechCenturion", "RUT_Symbol_SingularityCannon",
    "RUT_Symbol_MechLancer", "RUT_Symbol_GravRailArtillery",
    "RUT_Symbol_MechCenturion", "Turret_AutoMortar",
    "RUT_Symbol_SingularityCannon", "RUT_Symbol_MechLancer",
    "RUT_Symbol_GravRailArtillery", "RUT_Symbol_MechCenturion",
    "Turret_AutoInferno", "RUT_Symbol_MechLancer",
]

# The breach trail (see the module docstring's HARD STOP section): a short
# line of vanilla Filth cutting from just inside the keep-wall door toward
# the core wall, in ward 2 - "something forced its way in this far and no
# further, authored." All three are Core ThingDefs (auto-symbol'd bare).
# Placed as explicit (row, col) offsets from KEEP_DOOR so they read as one
# continuous scuff mark rather than scattered noise.
BREACH_TRAIL = ["Filth_MachineBits", "Filth_BlastMark", "Filth_Blood",
                 "Filth_Blood", "Filth_MachineBits"]

CORE_HUG_TURRETS = ["Turret_MiniTurret", "Turret_MiniTurret",
                     "Turret_MiniTurret", "Turret_MiniTurret"]


def dist(r, c, n):
    return min(r, c, n - 1 - r, n - 1 - c)


def build():
    n = N
    layout = [["."] * n for _ in range(n)]
    terrain = [[WARD_FLOOR] * n for _ in range(n)]

    for r in range(n):
        for c in range(n):
            d = dist(r, c, n)
            if d < WATER_DEEP_W:
                terrain[r][c] = "RUT_ScaldWaterDeep"
            elif d < OUTER_WALL_D:
                terrain[r][c] = "RUT_ScaldWaterShallow"
            elif d == OUTER_WALL_D:
                terrain[r][c] = "Concrete"
                layout[r][c] = "." if (r, c) in DOORS else OUTER_WALL_SYM
            elif d == KEEP_WALL_D:
                terrain[r][c] = "Concrete"
                layout[r][c] = "." if (r, c) in DOORS else KEEP_WALL_SYM
            elif d == CORE_WALL_D:
                terrain[r][c] = "Concrete"
                layout[r][c] = "." if (r, c) in DOORS else CORE_WALL_SYM
            elif d >= CORE_START_D:
                terrain[r][c] = CORE_FLOOR
            else:
                terrain[r][c] = WARD_FLOOR

    def band_cells(lo, hi):
        cells = []
        for r in range(n):
            for c in range(n):
                d = dist(r, c, n)
                if lo <= d <= hi and layout[r][c] == "." and (r, c) not in DOORS:
                    cells.append((r, c))
        return cells

    def scatter(cells, symbols):
        if not cells or not symbols:
            return
        step = max(1, len(cells) // len(symbols))
        for i, sym in enumerate(symbols):
            idx = (i * step + step // 2) % len(cells)
            r, c = cells[idx]
            layout[r][c] = sym

    scatter(band_cells(OUTER_WALL_D + 1, KEEP_WALL_D - 1), WARD1_GARRISON)
    scatter(band_cells(KEEP_WALL_D + 1, CORE_WALL_D - 1), WARD2_GARRISON)

    # Breach trail: five cells walking diagonally inward from just past the
    # keep door, staying inside ward 2 and off the core footprint.
    kr, kc = KEEP_DOOR
    step_r = -1 if kr > MID else 1
    for i, sym in enumerate(BREACH_TRAIL):
        r = kr + step_r * (i + 1)
        c = kc + (i - len(BREACH_TRAIL) // 2)
        if 0 <= r < n and 0 <= c < n and layout[r][c] == "." and dist(r, c, n) < CORE_START_D:
            layout[r][c] = sym

    # Core: console at dead centre, four point-defense turrets hugging the
    # INSIDE of the core wall (one per face, off the door column/row) - same
    # shape as RUT_VaultHeart's ring in VaultType3, conduits carry the
    # console's circuit to them.
    layout[MID][MID] = "RUT_Symbol_DarkTowerConsole"
    half = CORE_SIZE // 2
    hug_spots = [
        (MID - half + 2, MID),          # north, inside core wall
        (MID, MID + half - 2),          # east is the door face - skip east
        (MID + half - 2, MID),          # south
        (MID, MID - half + 2),          # west
    ]
    # East is the core door face - do not hug that side, or a turret could
    # sit in the doorway. Use N/S/W plus one more offset west-of-centre.
    hug_spots = [
        (MID - half + 2, MID),
        (MID + half - 2, MID),
        (MID, MID - half + 2),
        (MID - half + 2, MID - 2),
    ]
    for sym, (r, c) in zip(CORE_HUG_TURRETS, hug_spots):
        if layout[r][c] == "." and dist(r, c, n) >= CORE_START_D:
            layout[r][c] = sym

    return layout, terrain


def reachable_core(layout):
    """Offline BFS proof (same discipline as VAULT_DUNGEON_BUILD_1's
    2026-09-02 pass): the core is reachable ONLY by entering the outer door,
    walking the full ward-1 band, through the keep door, the full ward-2
    band, and the core door - never a straight line, never skippable. A
    cell blocks if it holds a wall symbol; everything else (open ground,
    guardians, filth, turrets - none of which are impassable) is walkable
    for this check, matching how the vault's own proof treated garrison
    guardians as non-blocking terrain for reachability purposes."""
    n = len(layout)
    wall_syms = {OUTER_WALL_SYM, KEEP_WALL_SYM, CORE_WALL_SYM}
    start = (OUTER_WALL_D - 1, MID)  # one cell outside the outer door
    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen:
                if layout[nr][nc] in wall_syms:
                    continue
                seen.add((nr, nc))
                stack.append((nr, nc))
    return (MID, MID) in seen


def render(layout, terrain, defname):
    rows_xml = "\n".join("        <li>%s</li>" % ",".join(row) for row in layout)
    terr_xml = "\n".join("      <li>%s</li>" % ",".join(row) for row in terrain)
    return f"""  <KCSG.StructureLayoutDef>
    <defName>{defname}</defName>
    <spawnConduits>true</spawnConduits>
    <terrainGrid>
{terr_xml}
    </terrainGrid>
    <layouts>
      <li>
{rows_xml}
      </li>
    </layouts>
  </KCSG.StructureLayoutDef>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    layout, terrain = build()

    ok = reachable_core(layout)
    print("core reachable via the full outer->keep->core door lap: %s" % ok)
    if not ok:
        raise SystemExit("REFUSING TO WRITE: the core is not reachable through the "
                          "authored door sequence - fix the geometry before shipping.")

    xml = render(layout, terrain, "RUT_DarkTower_HighCommand")
    with open(os.path.join(OUT_DIR, "StructureLayoutDefs_DarkTower.xml"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n")
        f.write(xml)
        f.write("</Defs>\n")

    with open(os.path.join(OUT_DIR, "SymbolDefs_DarkTower.xml"), "w") as f:
        f.write(gen_symboldefs())

    print("wrote StructureLayoutDefs_DarkTower.xml (1 template, %dx%d, core %dx%d) "
          "+ SymbolDefs_DarkTower.xml (%d new symbol)"
          % (N, N, CORE_SIZE, CORE_SIZE, len(THING_SYMBOLS)))


if __name__ == "__main__":
    main()
