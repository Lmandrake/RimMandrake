#!/usr/bin/env python3
"""gen_vault_layouts.py - generate the three parameterized VAULT_DUNGEON_BUILD_1
KCSG StructureLayoutDef templates (type (1) mechanoid garrison, (2) flesh
weapon loose, (3) frozen Rakata) per dungeons_arc_spec.md SS3.3's concentric
ring grammar: outer ring (state, at a glance) -> garrison ring (the fight, or
near-silence for type 3) -> core (the payoff).

🔴 Format CORRECTED after reading KCSG's real resolver
(vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/Defs/
StructureLayoutDef.cs, ResolveSymbols()): every `layouts` grid cell is
resolved via `DefDatabase<SymbolDef>.GetNamedSilentFail(symbol)` - EVERY
cell must name a real KCSG.SymbolDef, not a bare ThingDef/PawnKindDef. The
Dragon lair precedent file (bare "Slate"/"Wall_HardScale"/etc cells) only
works because KCSG auto-generates one SymbolDef per ThingDef/PawnKindDef
owned by an OFFICIAL Ludeon package (Core/Royalty/Ideology/Biotech/Anomaly/
Odyssey) or `vanillaexpanded.vfepropsanddecor`
(StartupActions.cs:CreateSymbols/CreateSymbolsFor), with defName ==
`thing.defName` (bare item), `pawnKindDef.defName` (bare pawn), or
`{thing.defName}_{stuffDef.defName}` (stuff-based building, e.g.
"Wall_Plasteel"). A silent miss (a symbol that resolves to null) is logged
to StartupActions.AddToMissing and the cell is simply never spawned - no
crash, no error, just empty ground where content should be. So:
  - vanilla/DLC ThingDefs, PawnKindDefs, and Wall+official-stuff combos ->
    safe to use BARE (auto-generated).
  - any THIRD-PARTY mod's ThingDef/PawnKindDef (Alpha Animals, GravTech,
    VFE Insectoids 2, our own RUT_ content) -> needs an EXPLICIT
    KCSG.SymbolDef wrapping it via <thing> or <pawnKindDef>, defined below
    and referenced by ITS OWN defName in the grid, never the wrapped def's
    bare name.
terrainGrid cells ARE plain TerrainDef.GetNamedSilentFail lookups (no
SymbolDef indirection there) - vanilla terrain names are safe bare.

Run: python3 gen_vault_layouts.py
Writes: ../Defs/StructureLayoutDefs_Vaults.xml, ../Defs/SymbolDefs_Vaults.xml
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Defs")

# --- Pawn symbols (third-party/our-own PawnKindDefs only - vanilla/DLC
# PawnKindDefs like Mech_Lancer/Mech_Centurion are auto-symbol'd by KCSG
# itself and are used BARE in the grid, no wrapper needed here) -----------
PAWN_SYMBOLS = [
    # (symbolDefName, pawnKindDef, note)
    ("RUT_Symbol_GreenGoo", "AA_GreenGoo",
     "HorrorWastes-native (cast_assignment.csv) - bioweapon-adjacent guardian, not the Anomaly toolbox. Third-party (Alpha Animals) -> not KCSG-auto-symbol'd, needs this wrapper."),
    ("RUT_Symbol_Boomsnake", "GR_Boomsnake",
     "HorrorWastes-native (cast_assignment.csv). Third-party (Genesis Regrown) -> needs this wrapper."),
]

# --- Container symbols (VAULT_THAW_QUEST_FAMILY_1) -------------------------
# The sleepers are IN CASKETS, not standing at the core. The earlier
# RUT_Symbol_RakataSleeper wrapped `RUT_Jawa_RakataVaultSchooled`, which is a
# BackstoryDef (PawnFlavor/Defs/Backstories_Rakata_Sleepers.xml), not a
# PawnKindDef - KCSG would have resolved it to null and spawned nothing,
# silently. Replaced by a real cryptosleep casket whose contents KCSG fills
# via `containPawnKindAnyOf` (SymbolUtils.GeneratePawnForContainer, faction =
# map.ParentFaction when spawnPartOfFaction) - so the V6 Site's faction
# (AncientsHostile, set by the quest) is what makes the sleepers wake hostile
# with Building_AncientCryptosleepCasket's own assault lord. AncientSoldier is
# already patched to the Rakata xenotype (UtinniPatches/AncientsAreRakata.xml).
CONTAINER_SYMBOLS = [
    # (symbolDefName, thingDefName, containPawnKinds, note)
    ("RUT_Symbol_RakataCasket", "AncientCryptosleepCasket", ["AncientSoldier"],
     "V6 casket hall. spawnPartOfFaction stays TRUE (default) so the sleeper takes the "
     "Site faction; the quest sets that faction to AncientsHostile."),
]

SYMBOLDEF_CONTAINER_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <thing>{thing}</thing>
    <containPawnKindAnyOf>
{kinds}
    </containPawnKindAnyOf>
    <chanceToContainPawn>1</chanceToContainPawn>
  </KCSG.SymbolDef>
"""

# --- Building/item symbols for third-party ThingDefs (same reasoning:
# vanilla/DLC things like Plasteel/Uranium/ComponentSpacer/Shard/Wall+
# official-stuff are auto-symbol'd and used BARE; everything below is a
# third-party mod's own ThingDef and needs an explicit wrapper) -----------
THING_SYMBOLS = [
    # (symbolDefName, thingDefName, note)
    ("RUT_Symbol_BlackJellyWall", "AA_BlackJellyWall",
     "Type-2 outer/garrison perimeter, per the item's own draft skeleton (SS3.6)."),
    ("RUT_Symbol_Fleshmass", "Fleshmass",
     "Type-2 breach scarring, per the draft skeleton."),
    ("RUT_Symbol_InfestedShipPart", "VFEI2_InfestedShipPart",
     "Type-2 wreckage where the thing got out, per the draft skeleton."),
    ("RUT_Symbol_InfestedShipChunk", "VFEI2_InfestedShipChunk",
     "Type-2 wreckage, per the draft skeleton."),
    ("RUT_Symbol_GravRailArtillery", "GTbc_GravRailArtillery",
     "Type-1 garrison doctrine turret - named explicitly in dungeons_arc_spec.md SS3.3 "
     "('grav-rail artillery... per the canon turret roster'). GravTech - Big Cannons "
     "(third-party) -> needs this wrapper. turret_register state=rework (numbers not final; "
     "defName/placement is what this pass decides, not the damage tuning)."),
    ("RUT_Symbol_SingularityCannon", "GTbc_TheSingularityCannon",
     "Type-1 garrison doctrine turret - named explicitly in dungeons_arc_spec.md SS3.3 "
     "('Singularity Cannon class'). Third-party -> needs this wrapper. state=rework, same "
     "caveat as the grav-rail artillery above."),
    ("RUT_Symbol_VaultHeart", "RUT_VaultHeart",
     "V6 thaw socket (VAULT_THAW_QUEST_FAMILY_1): a dead power plant whose only fuel is "
     "AIPersonaCore - the same core the Assailant complex takes (ruled 2026-09-01). Feeding "
     "it is the thaw. Our own ThingDef -> needs this wrapper; spawned factionless so the "
     "crew can claim and then refuel it (RefuelWorkGiverUtility.CanRefuel needs same faction)."),
]

# Symbols that must spawn with NO faction even on a faction-owned site.
FACTIONLESS_THING_SYMBOLS = {"RUT_Symbol_VaultHeart"}

SYMBOLDEF_PAWN_TMPL = """  <KCSG.SymbolDef>
    <defName>{defName}</defName>
    <pawnKindDef>{pawnKindDef}</pawnKindDef>
    <spawnPartOfFaction>false</spawnPartOfFaction>
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
    for name, kind, note in PAWN_SYMBOLS:
        body.append(SYMBOLDEF_PAWN_TMPL.format(defName=name, pawnKindDef=kind))
    for name, thing, note in THING_SYMBOLS:
        extra = ""
        if name in FACTIONLESS_THING_SYMBOLS:
            extra = "\n    <spawnPartOfFaction>false</spawnPartOfFaction>"
        body.append(SYMBOLDEF_THING_TMPL.format(defName=name, thing=thing, extra=extra))
    for name, thing, kinds, note in CONTAINER_SYMBOLS:
        kinds_xml = "\n".join("      <li>%s</li>" % k for k in kinds)
        body.append(SYMBOLDEF_CONTAINER_TMPL.format(defName=name, thing=thing, kinds=kinds_xml))
    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n" + "".join(body) + "</Defs>\n"


# --- Layout grid generation --------------------------------------------

def build_grid(size, outer_wall, outer_thick, garrison_floor, garrison_thick,
                garrison_symbols, core_wall, core_size, core_floor, core_items,
                door_material=None, core_wall_hugging=None, core_corner_item=None):
    """Concentric square grid: outer wall ring -> garrison band -> inner wall
    ring -> core room. Each wall ring gets exactly ONE door, offset 90
    degrees from the other ring's door, so the core is reachable only by
    walking around inside the garrison band - never a straight line in.

    core_wall_hugging: symbols placed in the band on cells ADJACENT to the
    core wall ring (one per side, N/E/S/W order, away from the S door).
    core_corner_item: one symbol placed just inside the core's NW corner.
    Both exist for the powered type-3 pieces: KCSG spawnConduits lays
    conduits under impassables (walls), and a CompPowerTrader connects to a
    transmitter in any adjacent cell (PowerConnectionMaker), so anything
    touching the core wall shares the heart's circuit.
    """
    n = size
    grid = [["."] * n for _ in range(n)]
    terrain = [["Gravel"] * n for _ in range(n)]

    def rect_wall(r0, c0, r1, c1, material, door_side):
        for c in range(c0, c1 + 1):
            grid[r0][c] = material
            grid[r1][c] = material
        for r in range(r0, r1 + 1):
            grid[r][c0] = material
            grid[r][c1] = material
        mid_c = (c0 + c1) // 2
        mid_r = (r0 + r1) // 2
        d = door_material or material
        if door_side == "N":
            grid[r0][mid_c] = "."
            terrain[r0][mid_c] = "Gravel"
        elif door_side == "S":
            grid[r1][mid_c] = "."
        elif door_side == "E":
            grid[mid_r][c1] = "."
        elif door_side == "W":
            grid[mid_r][c0] = "."

    # outer boundary (perimeter, door on the North face)
    rect_wall(0, 0, n - 1, n - 1, outer_wall, "N")
    for r in range(1, n - 1):
        for c in range(1, n - 1):
            terrain[r][c] = garrison_floor

    # garrison band interior fills to the core boundary; scatter guardians
    core_r0 = (n - core_size) // 2
    core_c0 = (n - core_size) // 2
    core_r1 = core_r0 + core_size - 1
    core_c1 = core_c0 + core_size - 1

    # inner (core) wall ring, door on the South face (offset from outer's N
    # door - a raider entering North must walk the full garrison band to
    # reach the South-side core door)
    rect_wall(core_r0, core_c0, core_r1, core_c1, core_wall, "S")

    # core interior
    for r in range(core_r0 + 1, core_r1):
        for c in range(core_c0 + 1, core_c1):
            grid[r][c] = "."
            terrain[r][c] = core_floor
    for i, item in enumerate(core_items):
        rr = core_r0 + 2 + (i // max(1, (core_size - 4)))
        cc = core_c0 + 2 + (i % max(1, (core_size - 4)))
        if core_r0 < rr < core_r1 and core_c0 < cc < core_c1:
            grid[rr][cc] = item
    if core_corner_item:
        grid[core_r0 + 1][core_c0 + 1] = core_corner_item
    if core_wall_hugging:
        q = core_size // 4
        spots = [
            (core_r0 - 1, core_c0 + q),        # N face, outside
            (core_r0 + q, core_c1 + 1),        # E face, outside
            (core_r1 + 1, core_c1 - q),        # S face, outside (off the door column)
            (core_r1 - q, core_c0 - 1),        # W face, outside
        ]
        for sym, (r, c) in zip(core_wall_hugging, spots):
            if grid[r][c] == ".":
                grid[r][c] = sym

    # scatter garrison guardians/turrets evenly through the band between the
    # two rings, skipping the core footprint entirely
    band_cells = []
    for r in range(outer_thick, n - outer_thick):
        for c in range(outer_thick, n - outer_thick):
            if core_r0 <= r <= core_r1 and core_c0 <= c <= core_c1:
                continue
            if grid[r][c] == "." and terrain[r][c] == garrison_floor:
                band_cells.append((r, c))
    step = max(1, len(band_cells) // max(1, len(garrison_symbols)))
    for i, sym in enumerate(garrison_symbols):
        idx = (i * step + step // 2) % len(band_cells)
        r, c = band_cells[idx]
        grid[r][c] = sym

    return grid, terrain


def render(grid, terrain, defname, spawn_conduits="false"):
    rows_xml = "\n".join(
        "        <li>%s</li>" % ",".join(row) for row in grid
    )
    terr_xml = "\n".join(
        "      <li>%s</li>" % ",".join(row) for row in terrain
    )
    return f"""  <KCSG.StructureLayoutDef>
    <defName>{defname}</defName>
    <spawnConduits>{spawn_conduits}</spawnConduits>
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

    # Type 1: mechanoid garrison held - disciplined+powered outer, the fight
    # inside, materials/weapons-only core loot (never chassis). Mech_Lancer/
    # Mech_Centurion/Turret_AutoInferno/Turret_AutoMortar/Plasteel/Uranium/
    # ComponentSpacer/Shard/Wall_Plasteel are all Core -> KCSG auto-symbols
    # them bare; the two GravTech cannons are third-party -> wrapped symbols.
    g1, t1 = build_grid(
        size=61, outer_wall="Wall_Plasteel", outer_thick=6,
        garrison_floor="Concrete", garrison_thick=20,
        garrison_symbols=[
            "Mech_Lancer", "Mech_Centurion",
            "Mech_Lancer", "RUT_Symbol_GravRailArtillery",
            "RUT_Symbol_SingularityCannon", "Turret_AutoInferno",
            "Turret_AutoMortar", "Mech_Centurion",
        ],
        core_wall="Wall_Plasteel", core_size=15, core_floor="Concrete",
        core_items=["Plasteel", "Plasteel", "ComponentSpacer", "Uranium", "Shard"],
    )
    type1 = render(g1, t1, "RUT_VaultType1_MechanoidGarrison")

    # Type 2: flesh weapon loose - torn open, bioweapon guardians, no direct
    # loot ladder (survival + the route to type-3 knowledge only). Every
    # named element here is third-party -> wrapped symbols throughout;
    # Flesh/terrain names are TerrainDef (no SymbolDef indirection needed).
    g2, t2 = build_grid(
        size=51, outer_wall="RUT_Symbol_BlackJellyWall", outer_thick=5,
        garrison_floor="Flesh", garrison_thick=15,
        garrison_symbols=[
            "RUT_Symbol_GreenGoo", "RUT_Symbol_Boomsnake",
            "RUT_Symbol_GreenGoo", "RUT_Symbol_InfestedShipPart",
            "RUT_Symbol_InfestedShipChunk", "RUT_Symbol_Fleshmass",
        ],
        core_wall="RUT_Symbol_BlackJellyWall", core_size=11, core_floor="Flesh",
        core_items=["RUT_Symbol_Fleshmass", "RUT_Symbol_InfestedShipChunk"],
    )
    type2 = render(g2, t2, "RUT_VaultType2_FleshWeaponLoose")

    # Type 3: frozen Rakata - dark, frost-locked, near-silent garrison ring,
    # the scene at the core. VAULT_THAW_QUEST_FAMILY_1 makes the "frost-locked,
    # no power" state MECHANICAL (the Assailant complex's frozen-first-impact
    # model, dungeons_arc_spec.md SS2.3): nothing here is a live hostile on
    # arrival. The garrison ring is four Turret_MiniTurret (Core, 80W,
    # CompPowerTrader) hugging the core wall - dark and harmless until the
    # crew feeds an AIPersonaCore into RUT_VaultHeart, the dead power plant
    # just inside the core's NW corner; then the ring wakes. The core floor is
    # four ancient caskets (RUT_Symbol_RakataCasket) with Rakata-xenotype
    # AncientSoldier sleepers, opened by the Open designator like any casket.
    # spawn_conduits="true" is what carries the heart's circuit under the
    # core wall to the turrets. The two live Mech_Centurion units are gone:
    # a live hostile would make Site.AllEnemiesDefeated/NoActiveThreats
    # meaningless for the quest, and "Mech_Centurion" is both a ThingDef and
    # a PawnKindDef name in KCSG's auto-symbol table (same caveat applies to
    # type 1's Mech_Lancer/Mech_Centurion cells - not this pass's file).
    g3, t3 = build_grid(
        size=55, outer_wall="Wall_Plasteel", outer_thick=6,
        garrison_floor="Ice", garrison_thick=18,
        garrison_symbols=[],  # deliberately silent - "thin... mostly silence" per SS3.3
        core_wall="Wall_Plasteel", core_size=13, core_floor="Ice",
        # a casket is (1,2) with its interaction cell one to the east - a gap
        # between each keeps every casket openable
        core_items=["RUT_Symbol_RakataCasket", ".", "RUT_Symbol_RakataCasket", ".",
                    "RUT_Symbol_RakataCasket", ".", "RUT_Symbol_RakataCasket"],
        core_corner_item="RUT_Symbol_VaultHeart",
        core_wall_hugging=["Turret_MiniTurret", "Turret_MiniTurret",
                           "Turret_MiniTurret", "Turret_MiniTurret"],
    )
    type3 = render(g3, t3, "RUT_VaultType3_FrozenRakata", spawn_conduits="true")

    with open(os.path.join(OUT_DIR, "StructureLayoutDefs_Vaults.xml"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n")
        f.write(type1)
        f.write(type2)
        f.write(type3)
        f.write("</Defs>\n")

    with open(os.path.join(OUT_DIR, "SymbolDefs_Vaults.xml"), "w") as f:
        f.write(gen_symboldefs())

    print("wrote StructureLayoutDefs_Vaults.xml (3 templates) + SymbolDefs_Vaults.xml (%d symbols)"
          % (len(PAWN_SYMBOLS) + len(THING_SYMBOLS)))


if __name__ == "__main__":
    main()
