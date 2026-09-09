#!/usr/bin/env python3
"""gen_war_lab_layout.py - generate ANCIENT_WAR_LAB_1's KCSG StructureLayoutDef:
the war lab beneath the propane lake, over the Impact Site.

Full spec: infrastructure/state/items/ANCIENT_WAR_LAB_1.md ("build spec (FOUNDRY,
2026-09-08 — consolidated") and the frozen the_propane_lakes.md SS3/SS8. Precedent
this follows, not duplicates: StructureInjectionsRUT/Source/VaultDungeons/
gen_vault_layouts.py (VAULT_DUNGEON_BUILD_1) and .../DarkTower/
gen_dark_tower_layout.py (SCALD_DARK_TOWER_1) - same KCSG StructureLayoutDef/
SymbolDef format, same "every third-party or our-own ThingDef/PawnKindDef needs
an explicit KCSG.SymbolDef wrapper, vanilla/DLC content is safe bare" rule (KCSG's
own ResolveSymbols(), cited in full in gen_vault_layouts.py's header - not
re-derived here).

SCOPE OF THIS PASS, stated up front: the item's own build spec says the
ignition->crater world-tile mutation is split into WAR_LAB_CRATER_HOOK_1,
blocked on LIQUID_BIOMES_MAP_1's frozen propane-lake footprint (confirmed
STILL UNRESOLVED as of this pass - LIQUID_BIOMES_MAP_1 closed "done" but its
own closing note says the lake-proper tile subset was deliberately NOT
selected, and the two 2026-09-09 owner-ruled follow-ons that could have
settled it, PROPANE_LAKES_SELF_CONTAINED_BIOME_1 / PROPANE_LAKES_WORLD_SWITCH_1,
were both dropped by card ruling "do we really need it? / Drop both"). This
generator does NOT touch that footprint or the crater mechanism - only the
dungeon interior, which does not need a world tile to exist as authored XML.

WHY NO THAW-GATE: gen_dark_tower_layout.py's own docstring speculates "ANCIENT_
WAR_LAB_1: frozen/inert on arrival, a delivered AIPersonaCore is the thaw-gate
that turns the guardians hostile" - written 2026-09-07, BEFORE this item's own
"build spec (FOUNDRY, 2026-09-08 — consolidated)" section landed. That
consolidated spec describes the approach band as "powered... dark but not
breached" (i.e. ALREADY LIVE, not dead-until-fed) and never mentions a core,
a thaw quest, or a dormant state anywhere in its three-band layout or its
criteria list. the_propane_lakes.md SS8 calls the lab guardians "the last
watch" - continuously on duty, not woken by the player. This generator
follows the ITEM'S OWN current spec over the sibling's stale aside.

THE CONTENT PALETTE, resolved this pass (previously "still open, do not
invent, confirm at build time" per the item's own build-spec note):
  - AA_Slurrypede: PawnKindDef defName confirmed IDENTICAL to its ThingDef
    (both "AA_Slurrypede") by reading the donor mod's own file directly -
    /mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/
    1541721856/1.6/Defs/ThingDefs_Races/Races_Slurrypede.xml, lines 5 and
    120 - confirming the item's own "assumed identical... per Alpha Animals
    convention" note rather than leaving it a guess.
  - Lab guardians: Mech_Lancer/Mech_Centurion, reused BARE by their existing
    RUT_Symbol_MechLancer/RUT_Symbol_MechCenturion defNames already shipped
    in the SAME mod (mandrake.rut.injections) via VaultDungeons/
    SymbolDefs_Vaults.xml - no redefinition needed, same convention
    gen_dark_tower_layout.py already used for this exact pair. Roster
    choice matches MECHANOID_BIOME_PRESENCE_REVIEW_1's own 2026-09-09 draft
    table, which already reads AB_PropaneLakes/RUT_PropaneLake as
    "RULED ALLOW... the lab IS the danger" - not an invented placement.
  - Shielding/hull walls: Wall_Plasteel, matching BOTH siblings' own
    convention for "ancient Rakatan tech" walls (a real stuff-based Core
    combo, auto-symbol'd bare, safe) - not a new material invented here.
  - Study-records prop: RUT_WarLabArchive (new ThingDef, this pass - see
    its own file header for why it is narrative-anchor-only, matching
    RUT_DarkTowerControlConsole's precedent).
  - Live/trapped-specimen containment prop: RUT_WarLabContainmentCell (new
    ThingDef, this pass - see its own file header for why it is a sealed,
    non-openable prop rather than a props-with-pawn casket, and why that
    choice is flagged rather than silently invented).

Run: python3 gen_war_lab_layout.py
Writes: ../../Defs/WarLab/StructureLayoutDefs_WarLab.xml,
        ../../Defs/WarLab/SymbolDefs_WarLab.xml
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Defs", "WarLab")

# --- Symbols this template needs that SymbolDefs_Vaults.xml does NOT
# already ship (RUT_Symbol_MechLancer/MechCenturion ARE already shipped
# there, same mod, used BARE below by their own defName - never redefined).
PAWN_SYMBOLS = [
    # (symbolDefName, pawnKindDef, note, faction, defendSpawnPoint)
    ("RUT_Symbol_Slurrypede", "AA_Slurrypede",
     "Lab fauna, the prisoner-feeder (the_propane_lakes.md SS4: 'kept, "
     "re-read: a bio-mechanoid built to feed prisoners efficiently is lab "
     "fauna, the containment facility's feeder, still running'). Docile, "
     "'almost never hostile' per its own ThingDef description - "
     "spawnPartOfFaction false, no faction override needed (Animal-"
     "intelligence, unlike the Mech_Lancer/Mech_Centurion crash case "
     "documented in gen_vault_layouts.py, which is specific to Mechanoid-"
     "intelligence pawns on a null-ParentFaction map), defendSpawnPoint "
     "false to match its docile temperament rather than the guardians'.",
     None, "false"),
]

THING_SYMBOLS = [
    # (symbolDefName, thingDefName, note)
    ("RUT_Symbol_WarLabArchive", "RUT_WarLabArchive",
     "The study-records reveal-beat (see that ThingDef's own header). Our "
     "own ThingDef -> needs this wrapper. Spawned factionless like "
     "RUT_Symbol_VaultHeart/RUT_Symbol_DarkTowerConsole so the crew can "
     "claim it once the guardians are cleared."),
    ("RUT_Symbol_WarLabContainmentCell", "RUT_WarLabContainmentCell",
     "The live/trapped-specimen prop (see that ThingDef's own header - "
     "deliberately not claimable, not a props-with-pawn casket). Our own "
     "ThingDef -> needs this wrapper."),
]
FACTIONLESS_THING_SYMBOLS = {"RUT_Symbol_WarLabArchive", "RUT_Symbol_WarLabContainmentCell"}

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
# Concentric SQUARE rings by Chebyshev distance-to-border, same technique as
# gen_dark_tower_layout.py's dist(). Three bands, matching the item's own
# three-band spec exactly (approach / lab interior / core), each behind its
# own wall on a DIFFERENT face so reaching the core is always a full lap of
# both bands, never a straight line (same discipline as both siblings):
#
#   d  0        outer hull wall     Wall_Plasteel, door on the NORTH face
#   d  1.. 6    approach band       Concrete, powered/dark, NO guardians yet
#                                   ("shielding intact... dark but not
#                                   breached" - the item's own words; the
#                                   fight has not started here)
#   d  7        inner hull wall     Wall_Plasteel, door on the EAST face
#   d  8..19    lab interior band   Concrete, AA_Slurrypede pens + the
#                                   Forsaken Arsenal garrison (Mech_Lancer/
#                                   Mech_Centurion/turrets) - the fight
#   d 20        core wall           Wall_Plasteel, door on the SOUTH face
#   d >=21      core                Concrete: RUT_WarLabArchive at centre,
#                                   RUT_WarLabContainmentCell x4 around it,
#                                   two Turret_MiniTurret hugging the core
#                                   wall ("the last watch")
#
# N=61 matches VAULT_DUNGEON_BUILD_1 type-1's own footprint scale
# (dungeons_arc_spec.md's ruled floor is 325x325 map, this structure sits
# inside it) - this item was never ruled "LARGE" the way SCALD_DARK_TOWER_1
# explicitly was, so it stays at the modest single-vault scale rather than
# doubling up like the tower did.
N = 61
OUTER_WALL_D = 0
APPROACH_W = 6
INNER_WALL_D = OUTER_WALL_D + 1 + APPROACH_W                       # 7
LABINT_W = 12
CORE_WALL_D = INNER_WALL_D + 1 + LABINT_W                          # 20
CORE_START_D = CORE_WALL_D + 1                                     # 21
CORE_SIZE = N - 2 * CORE_START_D                                   # 19

OUTER_WALL_SYM = "Wall_Plasteel"
INNER_WALL_SYM = "Wall_Plasteel"
CORE_WALL_SYM = "Wall_Plasteel"
APPROACH_FLOOR = "Concrete"
LABINT_FLOOR = "Concrete"
CORE_FLOOR = "Concrete"

MID = N // 2  # 30
OUTER_DOOR = (OUTER_WALL_D, MID)                     # north face
INNER_DOOR = (MID, N - 1 - INNER_WALL_D)             # east face
CORE_DOOR = (N - 1 - CORE_WALL_D, MID)               # south face
DOORS = {OUTER_DOOR, INNER_DOOR, CORE_DOOR}

# Lab interior: AA_Slurrypede working its pens alongside the Forsaken
# Arsenal garrison roster the item names explicitly ("reuse the vault
# type-(1) Forsaken Arsenal garrison roster, e.g. Mech_Lancer/Mech_Centurion").
LABINT_CONTENTS = [
    "RUT_Symbol_MechLancer", "RUT_Symbol_Slurrypede",
    "RUT_Symbol_MechCenturion", "Turret_AutoInferno",
    "RUT_Symbol_MechLancer", "RUT_Symbol_Slurrypede",
    "Turret_AutoMortar", "RUT_Symbol_MechCenturion",
]

CORE_CONTAINMENT = ["RUT_Symbol_WarLabContainmentCell"] * 4
CORE_HUG_TURRETS = ["Turret_MiniTurret", "Turret_MiniTurret"]


def dist(r, c, n):
    return min(r, c, n - 1 - r, n - 1 - c)


def build():
    n = N
    layout = [["."] * n for _ in range(n)]
    terrain = [[APPROACH_FLOOR] * n for _ in range(n)]

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
                terrain[r][c] = APPROACH_FLOOR
            elif d < CORE_WALL_D:
                terrain[r][c] = LABINT_FLOOR
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

    # Approach band: deliberately left clear of guardians/props - "dark but
    # not breached", the fight has not begun here.
    scatter(band_cells(INNER_WALL_D + 1, CORE_WALL_D - 1), LABINT_CONTENTS)

    # Core: archive at dead centre, containment cells ringing it, two
    # turrets hugging the inside of the core wall (off the S door face).
    layout[MID][MID] = "RUT_Symbol_WarLabArchive"
    half = CORE_SIZE // 2
    containment_spots = [
        (MID - half + 2, MID - 2), (MID - half + 2, MID + 2),
        (MID + half - 2, MID - 2), (MID + half - 2, MID + 2),
    ]
    for sym, (r, c) in zip(CORE_CONTAINMENT, containment_spots):
        if layout[r][c] == "." and dist(r, c, n) >= CORE_START_D:
            layout[r][c] = sym

    hug_spots = [(MID, MID - half + 2), (MID, MID + half - 2)]  # W, E - off the S door
    for sym, (r, c) in zip(CORE_HUG_TURRETS, hug_spots):
        if layout[r][c] == "." and dist(r, c, n) >= CORE_START_D:
            layout[r][c] = sym

    return layout, terrain


def reachable_core(layout):
    """Offline BFS proof (same discipline as both siblings): the core is
    reachable ONLY by entering the outer door, walking the full approach
    band, through the inner door, the full lab-interior band, and the core
    door - never a straight line, never skippable. A cell blocks if it holds
    a wall symbol; everything else (open ground, guardians, props, turrets -
    none of which are impassable in KCSG's own placement sense) is walkable
    for this check, matching the vault/dark-tower precedent's own treatment
    of garrison guardians as non-blocking terrain for reachability purposes."""
    n = len(layout)
    wall_syms = {OUTER_WALL_SYM, INNER_WALL_SYM, CORE_WALL_SYM}
    start = (OUTER_WALL_D + 1, MID)  # one cell inside the outer door, in the approach band
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

    xml = render(layout, terrain, "RUT_WarLab_Complex")
    with open(os.path.join(OUT_DIR, "StructureLayoutDefs_WarLab.xml"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n")
        f.write(xml)
        f.write("</Defs>\n")

    with open(os.path.join(OUT_DIR, "SymbolDefs_WarLab.xml"), "w") as f:
        f.write(gen_symboldefs())

    print("wrote StructureLayoutDefs_WarLab.xml (1 template, %dx%d, core %dx%d) "
          "+ SymbolDefs_WarLab.xml (%d new symbols)"
          % (N, N, CORE_SIZE, CORE_SIZE, len(PAWN_SYMBOLS) + len(THING_SYMBOLS)))


if __name__ == "__main__":
    main()
