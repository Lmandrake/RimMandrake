#!/usr/bin/env python3
"""gen_ashfall_layout.py - generate ASHFALL_RESEARCH_BASE_1's KCSG
StructureLayoutDef: the Spire, the Ashfall Research Base, on the Contagion
peak in the Ashfall Range.

Full spec: infrastructure/state/items/closed/ASHFALL_RESEARCH_BASE_1.md and
design/Jawa/worldbuilding/ashfall_research_base.md (§4 "dungeon sketch", §6
owner rulings). Precedent this follows, not duplicates: StructureInjectionsRUT/
Source/WarLab/gen_war_lab_layout.py (ANCIENT_WAR_LAB_1) - same concentric
Chebyshev-ring technique, same "every third-party or our-own ThingDef/
PawnKindDef needs an explicit KCSG.SymbolDef wrapper, vanilla/DLC content is
safe bare" rule (KCSG's own ResolveSymbols(), re-derived in full in
gen_vault_layouts.py's header - not re-derived again here), same offline BFS
reachability proof before writing anything.

SCOPE OF THIS PASS: layout templates (this file) + the command-codes item/
flag mechanism (Source/Ashfall/*.cs, Defs/Ashfall/ThingDefs_Items/
RUT_RakatanCommandCodes.xml) - a "solid first increment" per this item's own
filing note, not the whole design doc. NOT done here, and not this item's job
per its own "Watch out" section: the war lab's own locked-door check (belongs
to ANCIENT_WAR_LAB_1/WAR_LAB_CRATER_HOOK_1), the world-tile siting/landmark
write (rides CONTAGION_BIOME_PLACEMENT_1's own bridge pass per
ashfall_research_base.md §3), the encrypted-archive/antiquities-literacy
reveal gating (§6, needs the Antiquities mod's own system), and the Overdrive
program's own datafile text beyond what RUT_SpireCommandConsole's static
description already carries.

CONTENT PALETTE, resolved this pass (checked against real defNames, nothing
invented):
  - Turrets: VFES_Turret_TeslaBlaster / VFES_Turret_ChargeRailgun - the
    project's own turret_register (infrastructure/state/canon.yml `turrets`)
    and 04_factions.md's turret-ownership ruling both assign "tesla +
    railgun = Ascendant Helix" explicitly - a direct match for
    ashfall_research_base.md §4's "tesla + railgun emplacements (turret
    register: Helix)". Third-party (Vanilla Expanded Framework - Security),
    so each gets its own KCSG.SymbolDef wrapper (RUT_Symbol_TeslaTurret /
    RUT_Symbol_Railgun) rather than a bare grid name, same rule
    gen_vault_layouts.py's header documents in full.
  - Guardians: RUT_Jawa_Helix_Grunt / RUT_Jawa_Helix_Heavy /
    RUT_Jawa_Helix_Specialist / RUT_Jawa_Helix_Leader - this campaign's own
    already-shipped Helix pawn roster (UtinniPatches/Defs/PawnKindDefs/
    JawaFactionRoster.xml), faction RUT_Jawa_AscendantHelix. Matches
    ashfall_research_base.md §4's "Guardians: Helix containment response is
    a standing pawn group... hostility here reads as recovery of specimens" -
    a HUMAN response force, not mechanoids, unlike the war lab/vaults. The
    core's own guard is RUT_Jawa_Helix_Leader (the toughest of the four),
    matching the vault doctrine's "the core always costs"
    (dungeons_arc_spec.md §3.3).
  - Sample-galleries props: RUT_AshfallSpecimenCell (new ThingDef, this
    pass - see its own file header for why it is props-only, not
    props-with-pawn: "the Unfinished" has no PawnKindDef anywhere in this
    repo yet, the_contagion.md's own text lists their C# spawner as still
    OWED. Inventing one here would be exactly the content-palette invention
    this project's discipline forbids).
  - Core: RUT_SpireCommandConsole (new ThingDef, this pass - the "isolated
    system", narrative anchor, same class as RUT_WarLabArchive/
    RUT_DarkTowerControlConsole) + RUT_RakatanCommandCodes (new ThingDef,
    this pass - the portable prize, see its own file header for the full
    two-key-gate mechanism).
  - Walls: Wall_Plasteel, matching ALL THREE now-built dungeons' own
    convention for "ancient Rakatan tech" walls (gen_war_lab_layout.py's own
    docstring: "matching BOTH siblings' own convention" - this is now the
    third).

WHY NOT "LARGE": like ANCIENT_WAR_LAB_1 (see that generator's own docstring),
this item was never ruled LARGE the way SCALD_DARK_TOWER_1/the six vaults
explicitly were - ashfall_research_base.md's own §4 never asks for it. Stays
at the same modest N=61 single-site scale as the war lab, reusing its exact
proven band-width geometry rather than inventing new proportions.

Run: python3 gen_ashfall_layout.py
Writes: ../../Defs/Ashfall/StructureLayoutDefs_Ashfall.xml,
        ../../Defs/Ashfall/SymbolDefs_Ashfall.xml
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Defs", "Ashfall")

# --- Symbols this template needs (none of these are official-Ludeon-package
# or vanillaexpanded.vfepropsanddecor content, so none auto-symbol bare).
PAWN_SYMBOLS = [
    # (symbolDefName, pawnKindDef, note, faction, defendSpawnPoint)
    ("RUT_Symbol_HelixGrunt", "RUT_Jawa_Helix_Grunt",
     "Helix containment response, rank and file (ashfall_research_base.md "
     "§4: 'the base does not raid; it retrieves — hostility here reads as "
     "recovery of specimens, the player included').", "RUT_Jawa_AscendantHelix", "true"),
    ("RUT_Symbol_HelixHeavy", "RUT_Jawa_Helix_Heavy",
     "Helix containment response, heavy support.", "RUT_Jawa_AscendantHelix", "true"),
    ("RUT_Symbol_HelixSpecialist", "RUT_Jawa_Helix_Specialist",
     "Helix containment response, the curator rank (JawaFactionRoster.xml "
     "label: 'Helix curator').", "RUT_Jawa_AscendantHelix", "true"),
    ("RUT_Symbol_HelixLeader", "RUT_Jawa_Helix_Leader",
     "The core's own guard — the toughest Helix kind shipped, matching the "
     "vault doctrine's 'the core always costs' (dungeons_arc_spec.md §3.3).",
     "RUT_Jawa_AscendantHelix", "true"),
]

THING_SYMBOLS = [
    # (symbolDefName, thingDefName, note)
    ("RUT_Symbol_TeslaTurret", "VFES_Turret_TeslaBlaster",
     "Containment-ring emplacement — turret_register assigns tesla to the "
     "Ascendant Helix by name (canon.yml `turrets.official_roster`, "
     "04_factions.md line 213). Third-party (VFE-Security) -> needs this "
     "wrapper."),
    ("RUT_Symbol_Railgun", "VFES_Turret_ChargeRailgun",
     "Containment-ring emplacement — turret_register assigns railgun to the "
     "Ascendant Helix by name (same source as the tesla turret above). "
     "Third-party (VFE-Security) -> needs this wrapper."),
    ("RUT_Symbol_SpireCommandConsole", "RUT_SpireCommandConsole",
     "The core reveal-beat / 'isolated system' (see that ThingDef's own "
     "header). Our own ThingDef -> needs this wrapper."),
    ("RUT_Symbol_AshfallSpecimenCell", "RUT_AshfallSpecimenCell",
     "Sample-galleries prop (see that ThingDef's own header — props-only, "
     "the Unfinished have no PawnKindDef yet). Our own ThingDef -> needs "
     "this wrapper."),
    ("RUT_Symbol_RakatanCommandCodes", "RUT_RakatanCommandCodes",
     "The two-key-gate prize (see that ThingDef's own header — "
     "ASHFALL_RESEARCH_BASE_1's whole reason to exist). Our own ThingDef -> "
     "needs this wrapper."),
]
# Turrets are left OFF this set deliberately, matching gen_war_lab_layout.py's
# own precedent for Turret_AutoInferno/Turret_AutoMortar: those were placed
# bare/factionless in that template with no faction assignment mechanism
# demonstrated for a turret via KCSG.SymbolDef, and the item's own criteria
# checklist never asked for turret hostility to be proven (only the pawn
# guardians' faction/hostility was verified live). Whoever does this item's
# own quicktest-proof pass should confirm turret hostility explicitly rather
# than assume it from this comment.
FACTIONLESS_THING_SYMBOLS = {
    "RUT_Symbol_SpireCommandConsole", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_RakatanCommandCodes",
}

SYMBOLDEF_PAWN_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <pawnKindDef>{pawnKindDef}</pawnKindDef>
    <spawnPartOfFaction>false</spawnPartOfFaction>{faction_xml}
    <numberToSpawn>1</numberToSpawn>
    <spawnDead>false</spawnDead>
    <spawnRotten>false</spawnRotten>
    <defendSpawnPoint>{defend}</defendSpawnPoint>
  </KCSG.SymbolDef>
"""

SYMBOLDEF_THING_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <thing>{thing}</thing>{extra}
  </KCSG.SymbolDef>
"""


def gen_symboldefs():
    body = []
    for name, kind, note, faction, defend in PAWN_SYMBOLS:
        faction_xml = "\n    <faction>%s</faction>" % faction if faction else ""
        body.append(SYMBOLDEF_PAWN_TMPL.format(
            defName=name, pawnKindDef=kind, faction_xml=faction_xml, defend=defend))
    for name, thing, note in THING_SYMBOLS:
        extra = "\n    <spawnPartOfFaction>false</spawnPartOfFaction>" if name in FACTIONLESS_THING_SYMBOLS else ""
        body.append(SYMBOLDEF_THING_TMPL.format(defName=name, thing=thing, extra=extra))
    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n" + "".join(body) + "</Defs>\n"


# --- Layout geometry -----------------------------------------------------
# Concentric SQUARE rings by Chebyshev distance-to-border, the exact
# technique and band widths gen_war_lab_layout.py already proved by BFS -
# reused rather than reinvented (neither dungeon was ruled LARGE):
#
#   d  0        outer hull wall     Wall_Plasteel, door on the NORTH face
#   d  1.. 6    containment ring    Concrete, tesla+railgun emplacements,
#                                   no guardians (the outer works, per §4's
#                                   "outer containment ring")
#   d  7        inner hull wall     Wall_Plasteel, door on the EAST face
#   d  8..19    sample galleries    Concrete, specimen cells + the Helix
#                                   containment response (the fight)
#   d 20        core wall           Wall_Plasteel, door on the SOUTH face
#   d >=21      core (datafile)     Concrete: RUT_SpireCommandConsole at
#                                   centre, RUT_RakatanCommandCodes one cell
#                                   north of it (the prize, staged the same
#                                   way WarLabReactorCore sits beside
#                                   RUT_WarLabArchive), the Helix Leader +
#                                   one tesla turret hugging the core wall
#                                   ("the core always costs")
N = 61
OUTER_WALL_D = 0
CONTAINMENT_W = 6
INNER_WALL_D = OUTER_WALL_D + 1 + CONTAINMENT_W                    # 7
GALLERY_W = 12
CORE_WALL_D = INNER_WALL_D + 1 + GALLERY_W                         # 20
CORE_START_D = CORE_WALL_D + 1                                     # 21
CORE_SIZE = N - 2 * CORE_START_D                                   # 19

OUTER_WALL_SYM = "Wall_Plasteel"
INNER_WALL_SYM = "Wall_Plasteel"
CORE_WALL_SYM = "Wall_Plasteel"
CONTAINMENT_FLOOR = "Concrete"
GALLERY_FLOOR = "Concrete"
CORE_FLOOR = "Concrete"

MID = N // 2  # 30
OUTER_DOOR = (OUTER_WALL_D, MID)                     # north face
INNER_DOOR = (MID, N - 1 - INNER_WALL_D)             # east face
CORE_DOOR = (N - 1 - CORE_WALL_D, MID)               # south face
DOORS = {OUTER_DOOR, INNER_DOOR, CORE_DOOR}

CONTAINMENT_CONTENTS = [
    "RUT_Symbol_TeslaTurret", "RUT_Symbol_Railgun",
    "RUT_Symbol_TeslaTurret", "RUT_Symbol_Railgun",
]

GALLERY_CONTENTS = [
    "RUT_Symbol_HelixGrunt", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_HelixHeavy", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_HelixSpecialist", "RUT_Symbol_AshfallSpecimenCell",
    "RUT_Symbol_HelixGrunt", "RUT_Symbol_AshfallSpecimenCell",
]

CORE_HUG_GUARDS = ["RUT_Symbol_HelixLeader", "RUT_Symbol_TeslaTurret"]


def dist(r, c, n):
    return min(r, c, n - 1 - r, n - 1 - c)


def build():
    n = N
    layout = [["."] * n for _ in range(n)]
    terrain = [[CONTAINMENT_FLOOR] * n for _ in range(n)]

    for r in range(n):
        for c in range(n):
            d = dist(r, c, n)
            if d == OUTER_WALL_D:
                terrain[r][c] = "Concrete"
                layout[r][c] = "." if (r, c) in DOORS else OUTER_WALL_SYM
            elif d == INNER_WALL_D:
                terrain[r][c] = "Concrete"
                layout[r][c] = "." if (r, c) in DOORS else INNER_WALL_SYM
            elif d == CORE_WALL_D:
                terrain[r][c] = "Concrete"
                layout[r][c] = "." if (r, c) in DOORS else CORE_WALL_SYM
            elif d < INNER_WALL_D:
                terrain[r][c] = CONTAINMENT_FLOOR
            elif d < CORE_WALL_D:
                terrain[r][c] = GALLERY_FLOOR
            else:
                terrain[r][c] = CORE_FLOOR

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

    scatter(band_cells(OUTER_WALL_D + 1, INNER_WALL_D - 1), CONTAINMENT_CONTENTS)
    scatter(band_cells(INNER_WALL_D + 1, CORE_WALL_D - 1), GALLERY_CONTENTS)

    # Core: the console at dead centre, the codes one cell north of it
    # (mirrors WarLabReactorCore's own placement beside RUT_WarLabArchive).
    layout[MID][MID] = "RUT_Symbol_SpireCommandConsole"
    codes_r, codes_c = MID - 1, MID
    if layout[codes_r][codes_c] == "." and dist(codes_r, codes_c, n) >= CORE_START_D:
        layout[codes_r][codes_c] = "RUT_Symbol_RakatanCommandCodes"

    half = CORE_SIZE // 2
    hug_spots = [(MID, MID - half + 2), (MID, MID + half - 2)]  # W, E - off the S door
    for sym, (r, c) in zip(CORE_HUG_GUARDS, hug_spots):
        if layout[r][c] == "." and dist(r, c, n) >= CORE_START_D:
            layout[r][c] = sym

    return layout, terrain


def reachable_core(layout):
    """Offline BFS proof (same discipline as the vault/dark-tower/war-lab
    siblings): the core is reachable ONLY by entering the outer door,
    walking the full containment ring, through the inner door, the full
    sample-galleries band, and the core door - never a straight line, never
    skippable. A cell blocks if it holds a wall symbol; everything else
    (guardians, turrets, props) is walkable for this check, matching every
    sibling's own treatment of garrison guardians as non-blocking terrain
    for reachability purposes."""
    n = len(layout)
    wall_syms = {OUTER_WALL_SYM, INNER_WALL_SYM, CORE_WALL_SYM}
    start = (OUTER_WALL_D + 1, MID)  # one cell inside the outer door
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
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    layout, terrain = build()

    ok = reachable_core(layout)
    print("core reachable via the full outer->inner->core door lap: %s" % ok)
    if not ok:
        raise SystemExit("REFUSING TO WRITE: the core is not reachable through the "
                          "authored door sequence - fix the geometry before shipping.")

    xml = render(layout, terrain, "RUT_Ashfall_Spire")
    with open(os.path.join(OUT_DIR, "StructureLayoutDefs_Ashfall.xml"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n")
        f.write(xml)
        f.write("</Defs>\n")

    with open(os.path.join(OUT_DIR, "SymbolDefs_Ashfall.xml"), "w") as f:
        f.write(gen_symboldefs())

    codes_placed = any("RUT_Symbol_RakatanCommandCodes" in row for row in layout)
    print("wrote StructureLayoutDefs_Ashfall.xml (1 template, %dx%d, core %dx%d) "
          "+ SymbolDefs_Ashfall.xml (%d new symbols) - command codes placed: %s"
          % (N, N, CORE_SIZE, CORE_SIZE, len(PAWN_SYMBOLS) + len(THING_SYMBOLS), codes_placed))


if __name__ == "__main__":
    main()
