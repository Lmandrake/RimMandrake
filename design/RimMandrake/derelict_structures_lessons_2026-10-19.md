# Derelict temple, biolab and archonexus: what the donor teaches before we drop it

*Study, 2026-10-19, FOUNDRY. Read-only; no donor art or code was copied into the repo.*
*Asked for by the owner: "Please scan the DerelictKemeticTemple and DerelictBioLab and
DerelictArchonexus for the structure layouts and art for consideration in a design pass.
Anything useful for us to learn from here, or is it fairly straightforward? Let's learn as we
say goodbye."* These are the three Alpha Biomes mutators that
`design/RimMandrake/retired_mutators_port_2026-10-19.md` could not port. Ledger item:
`UNPORTED_MUTATORS_DECIDE_FOUR_ON_THE_STEP`.

## Short answer

All three are **easy machinery with very little design in them**. Each mutator is a single
`TileMutatorDef` that hands a list of pre-drawn layouts to a **Vanilla Expanded Framework**
spawner worker. VEF (`oskarpotocki.vanillafactionsexpanded.core`) is already on our active list,
and **we already write the same KCSG format** in `src/RimUtinni/StructureInjectionsRUT` (23
`KCSG.StructureLayoutDef`, 74 `KCSG.SymbolDef`). Nearly all the value is in the **art kits**, and
we can't keep those. The useful lessons are a handful of small techniques, listed in §6, plus
one larger point that has nothing to do with the donor: vanilla Odyssey's own procedural ruin
generator, which we don't use at all.

| structure | what it really is | needs C#? | verdict |
|---|---|---|---|
| Archonexus | 3 decorative impassable buildings × 5 fixed prefabs, 3–5 scattered per map | no (VEF worker) | **straightforward**: about 0.5 agent-day plus 3 sprites |
| Kemetic temple | one hand-drawn 31×56 KCSG layout of **vanilla** furniture reskinned by an Ideology style category | no (VEF worker) | **straightforward**: about 1 agent-day plus a style kit; the design value is in the floor plan, which is small |
| BioLab | 13 hand-drawn KCSG layouts (37×51 up to 85×93) with a 30-def "ruined machine" junk kit, loot-roller placeholders and a raid beacon | **yes**: 3 Alpha Genes comps | **some real design value** in how a ruin is dressed (§3); rebuilding is about 3–4 agent-days plus about 20 sprites |

## 1. Where they live and how they spawn

Files on disk (Steam Workshop, `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`):

| piece | file |
|---|---|
| all three TileMutatorDefs | `1841354677\1.6\Mods\Odyssey\Defs\TileMutators\TileMutators_ManMade.xml` (Alpha Biomes) |
| archonexus prefabs | `1841354677\1.6\Mods\Odyssey\Defs\PrefabDefs\MutatorPrefabs.xml` |
| archonexus buildings | `1841354677\1.6\Mods\Odyssey\Defs\ThingDefs_Buildings\Buildings_DerelictArchonexus_Odyssey.xml` |
| temple layout + symbols | `1841354677\1.6\Mods\AlphaMemes\Defs\CustomGenDefs\{LayoutDefs_KemeticTemple,Symbols_AlphaMemes}.xml` |
| temple art, stone, floor, gate | Alpha Memes `2661356814` (`StyleCategoryDefs_Kemetic.xml`, `Buildings_Art.xml`, `Terrain_Floors.xml`, `Various_Stone.xml`) |
| biolab layouts | Alpha Genes `2891845502\1.6\Defs\CustomGenDefs\BiotechLabs.xml` (886 KB), `Symbols.xml`, `Sites\BiotechLabs.xml` |
| biolab junk kit | Alpha Genes `2891845502\1.6\Defs\ThingDefs_Buildings\{Buildings_Junk,Buildings_Structure}.xml`, `Assemblies\AlphaGenes.dll` |

**The mutator layer.** Each def is about 15 lines:

- `workerClass` is `VEF.Maps.TileMutatorWorker_GenericKCSGSpawner` for the temple and the biolab
  (`KCSGStructuresToSpawn` list, `KCSGStructuresToSpawnAmount 1~1`). For the archonexus it is
  `VEF.Maps.TileMutatorWorker_GenericPrefabSpawner` (`prefabsToSpawn`, amount `3~5`).
- `chanceOnNonLandmarkTile 0.005` on all three.
- The biolab has `maxHilliness Flat`. The temple has `biomeWhitelist` Desert, ExtremeDesert,
  AridShrubland and two AB biomes.
- Each is gated by `MayRequire` on its art mod: `sarg.alphagenes`, Ideology and `Sarg.AlphaMemes`
  respectively. **That gate is why they could not be ported.** The layouts are data, but every
  symbol in them names a def from a mod we are retiring.

Our own mutators do the same job another way. A `TileMutatorDef.extraGenSteps` list feeds our
GenStep (`src/RimUtinni/StructureInjectionsRUT/Defs/TileMutatorDefs_Batch*.xml`), which also
needs no C#. Either route works. Ours keeps the spawner under our control.

## 2. Kemetic temple

**What it is.** A walled, roofed, Egyptian-style temple in pristine limestone, empty of life. A
grand gate in the north wall opens onto a pillared forecourt. A second gate leads to a dense
hypostyle hall (a forest of columns). A door leads into the sanctuary: twelve pews facing three
altars, an ideogram, shelves, dressers, torches and four 3×3 tables. **It has no loot, no
pawns, no traps and no hook.** It is set dressing, and its reward is whatever an Ideology player
gets from a ready-made ritual room.

**Numbers** (parsed from the def, one layer):

| | |
|---|---|
| layout size | 31 wide × 56 tall (1,736 cells) |
| walls | 434 · columns 86 · pews 12 · altars 3 · tables 4 · end tables 4 · shelves 4 · dressers 2 · torches 4 · ideogram 1 · grand gates 2 · doors 2 |
| floor | `AM_KemeticTilePristineLimestone` on 618 cells · roof on 580 cells · `forceGenerateRoof true` |
| rooms | 3, connected in a line: forecourt (about 27×14), hypostyle hall (about 27×10), sanctuary (about 27×17) |
| doors | 2 grand gates (3×3, centred in a 3-cell wall gap), 2 vanilla doors on the centre line between hall and sanctuary |

**Layout sketch** (rendered from the def, row 0 at top; `#` wall, `C` column, `G` grand gate,
`D` door, `P` pew, `A` altar, `T` table, `i` ideogram, `s` shelf/dresser, `*` torch):

```
...##..##..##.....##..##..##...      crenellated front: wall stubs
##############.G.##############      grand gate 1 (3x3, draws 7x7)
.#...........................#.
.#.C.......C.......C.......C.#.      FORECOURT: 4 x 7 columns
##...........................##
 ...  (columns every 2 rows)  ...
##..##..##..###.###..##..##..##      inner wall, notched
.##############.##############.
.##############.G.############.      grand gate 2
##...........................##
##C.C.C.C.C.C.....C.C.C.C.C.C##      HYPOSTYLE HALL: 6 rows x 12 columns,
.#C.C.C.C.C.C.....C.C.C.C.C.C#.      3-cell processional aisle down the middle
##C.C.C.C.C.C#...#C.C.C.C.C.C##
.##############D##############.      door
###############D###############      door (double wall)
##*.T.....................T.*##
.#........P....P....P........#.      SANCTUARY: 4 x 3 pews facing south
.#..........................s#.
##s.......P....P....P........##
##........P....P....P.......s##
.#s..........................#.
.#........P....P....P........#.
##s............i.............##      ideogram on the axis
.#..T...*.o...o.o...o.*...T..#.
.#.......A.....A.....A.......#.      three altars on the back wall
.##############################.
..###......#########......###..      rear buttresses
```

**Machinery.** It is entirely vanilla things: `Wall`, `Column`, `Door`, `Pew`, `Shelf`,
`Dresser`, `EndTable`, `Table3x3c`, `TorchLamp`, `TorchWallLamp`, `Altar_Medium`, `Ideogram`.
Each `KCSG.SymbolDef` carries `<stuff>AM_BlocksPristineLimestone</stuff>` and
`<styleCategory>AM_Kemetic</styleCategory>`. The **Ideology style system** does all the visual
work. `StyleCategoryDefs_Kemetic.xml` maps about 105 vanilla thingDefs (furniture, weapons,
apparel) to Kemetic graphics. The only donor-original things are `AM_GrandGate` (a 3×3
`Building_Art` drawn 7×7 at `MoteOverhead` altitude, so the lintel overhangs the wall) plus one
stone and one floor (both colour `(170,157,125)`).

**Art.** `2661356814\Textures\Things\Building\BuildingStyles\Kemetic\` holds 133 PNGs; the temple
shows about 12 of them. We looked at the grand gate (512×512): flat vector shapes with heavy
black outlines in vanilla style, sand and cream limestone, a grey winged sun-disk on the lintel,
orange accent bands and hieroglyph-panelled jambs. It is clean but generic "Egypt". The wall is a
320×320 atlas and the column is 128×256. The floor texture is 1024×1024, palettised. **All of it
is donor-original and leaves with the donor.**

**What is reusable for us.**
- The floor plan as an idea: a **processional axis through three rooms that rise in sanctity**
  (open court, then column forest, then sanctuary). The plan is legible from the outside because
  the gates and the doors sit on one line.
- **A style category as an art kit.** You draw about 12 sprites once, and every vanilla piece of
  furniture placed in that ruin picks them up. We already have one `StyleCategoryDef`
  (`src/RimMandrake/SacredGraffiti/Defs/StyleCategoryDefs_Salvation.xml`), but **no KCSG symbol
  of ours sets `styleCategory`** (0 hits in `src/`). That is cheap, and it would give each ruin
  family a look of its own.
- The overhanging gate: a small footprint with a large `drawSize` drawn above the walls.
- What it lacks, so don't copy it: there is no reason to enter. It needs a reward, a threat or a
  quest hook (see §7).

## 3. BioLab (Alpha Genes "abandoned biotech lab")

**What it is.** A collapsed, rusted gene-and-mech laboratory complex. Rows of smashed growth vats,
dead gene banks and assemblers, mech gestators, ruined hospital beds and vitals monitors,
flickering faulty lamps, desiccated corpses, burnt carpet and cracked concrete, with collapsed
rock pushing in through the walls. Scattered among the wreckage are **live loot rollers**
(genepacks and gene tools) and **one or two "ruined radio beacons" that call a raid** when you
come close. The same 13 layouts are also used by Alpha Genes as a world-map site
(`SitePartDef AG_AbandonedBiotechLab`, `KCSG.GenStep_CustomStructureGen`, with filth scatter
`Filth_Dirt`/`Filth_Trash`/`Filth_RubbleBuilding`).

**Numbers** (all 13 layouts parsed):

| | |
|---|---|
| sizes | Theta 37×51 (smallest) · Delta 55×48 · Gamma 55×60 · Alpha 69×74 · Nu 69×75 · Mu 85×93 (largest) |
| layers | 2–4 KCSG layers each (structure, then furniture, then items) plus a terrainGrid and a roofGrid |
| walls | `AG_RustedWall` in all 13 (5,981 cells in total); natural `Slate`/`Granite` in 2 (cave-cut labs) |
| doors | `AG_LabDoor` in all 13 (191 in total, so many small rooms) |
| set dressing (every lab) | ancient corpse ×152, growth vat ×70, faulty lamp ×56, lab lamp ×42, gene processor ×33, gene bank ×59, gene assembler ×37, shelves ×128 |
| set dressing (most labs) | mech gestators ×55, rechargers ×45, ruined hospital beds ×48, vitals monitors ×76, pollution pumps ×28, wastepack atomizers ×19, subcore ripscanners ×24 |
| **loot** | `AG_RandomGenepack` ×75 (in all 13, about 6 per lab), `AG_RandomGeneTool` ×46 (in all 13) |
| **threat** | `AG_RaidSpawner` ×15 (in all 13, 1–2 per lab); `AncientSecurityTurret` ×5, `TrapIED_HighExplosive` ×2, razor wire, sandbags and tank traps in the 2 "fortified" labs |
| floors | `AG_RustedTile`, `AG_CrackedConcrete` and `AG_BurntCarpet` dominate; one lab (Mu) uses thick roof (`3`) over 2,848 cells (a buried lab) |
| vanilla filler | about 60 vanilla `Ancient*` junk defs (cars, crates, vending machines, pipes, ATM), used lightly |

**Layout sketch: Eta** (42×60, Biotech; `#` wall, `D` door, `:` roofed floor, `,` loose floor,
`V` growth vat, `G` gene machine, `M` mech machine, `b` bed/monitor, `x` corpse, `$` loot roller,
`R` raid beacon, `s` shelf, `*` lamp, `%` collapse):

```
          ,%## ### ,,,,
            #,,:,,##,,,  ,, ,,       ,,
            #:,::,,#%,,,,,,,,   ,, ,      ,,,,,,,,
            #::%:,## ,#### ,,#### , ####  ,,,,,  ,,,
            #::::,,#,##s:##,##s$##,##s$## ,,,######,,,
            #:::%::###::::###::::###::::######::::####
            #:%%::::#::::::::::::::::::::#:G::G::G:::#   gene wing
            #:::::::D::G::x:::G::::::G:::#:::::::::::#
            ##DD###:#::::::::::::::::::::#:V:V:V:V:V:##  vat row
            #::::::###::::###::::###::::##::::::::::::#
            #:::::##:##:s##:##:s##:##:s###::::::::::::#
            #::::##:M:####:M:####:M:######:::::::::::M#  mech bays
            #::::#*::::::::::::::::::::::#::G:::G:::::#
            #::::#:::::M::::::M::*:::M:::#:::::::::*###
            #:::::D:::::::::::::R:::x:::::D::::p::::#    R = raid beacon,
            #::::##*:::::::::::::::::::::##::::::::s#        dead centre
            #::::#::::::M:::*::M::::::M::#::G:::G:::###
            #::::##:M:####:M:####:M:####:#::::::::::::#
          ::D:::::#####::#####::#####::#D#:::::::x:::M#
          ::#:::::::::::::::#::::::::::::#::::x:::::::#
          ::#:::::::::::::::D:::::M:::::*#:::::::::::##
          ###::::$s::::::::*#::::::::::::#::G::::G:::#
             ##################:::::::::::#:::::::::::#
                             ################::::::::#
```

The pattern repeats across the 13 layouts: a **west service corridor**, a **central hall
ringed by alcove bays** (one machine per bay), a **gene/vat wing** to the east, and the **raid
beacon in the most central, most-walked room**. Loot rollers sit in shelf alcoves and dead ends.
The edges are deliberately ragged: loose floor tiles (`,`) outside the walls, rock collapse
(`%`), and corpses outside.

**Machinery.**
- XML-only: the KCSG layouts and symbols, and about 25 junk ThingDefs. These are all
  `AG_JunkBuildingBase` (vanilla `BuildingBase`), `PassThroughOnly`, `pathCost 50`, and
  `costList` of steel plus `ChunkSlagSteel` so that deconstructing one yields scrap. The bed and
  shelf are real `Building_Bed`/`Building_Storage`; the lamps are real `CompGlower`.
- C# (Alpha Genes):
  - `CompProperties_RandomItemSpawner`, a 1×1 placeholder building that rolls a weighted item list
    (Genepack / AG_Alphapack / AG_Mixedpack, or three gene tools). `canPlaceOverWall`, not an
    edifice.
  - `CompProperties_RandomRaidSpawner` (empty properties, so the logic is hard-coded) with
    `PlaceWorker_ShowSpawnerRadius`. That placeworker implies a **proximity trigger with a radius
    shown when selected**; the exact radius and the raid points are inside the DLL and were not
    measured.
- Corpses are **1×1 junk buildings with `Graphic_Random`** (5 variants, 128×128, drawn at
  1.5×1.5). They never rot, never cause thoughts, and cost no pawn generation.

**Art** (all Alpha Genes originals, `2891845502\Textures\Things\Building\`). About 55 sprites:
19 machines, most with 3 facings; a 640×640 rusted wall atlas; a 128×128 door; 5 corpses; 2
lamps; a beacon; 2 loot icons; and 3 terrains (cracked concrete, rusted biotech tile, burnt
carpet). We looked at several. The style is **faithful ruined versions of the vanilla Biotech
machines**: the same silhouettes, desaturated into grey-green, with red-brown rust streaks,
shattered glass (the large mech gestator's dome is jagged translucent shards) and heavy black
outlines. The wall atlas is dark charcoal blocks with rust drip along the lit lower edge. The kit
is competent and consistent. Its trick is that **each sprite is "the vanilla machine you know,
broken"**, so the player reads what the room was for with no text.

**What is reusable for us.**
1. **Ruin vocabulary = familiar machine + broken.** For our labs, a "ruined X" kit of vanilla
   and Star Wars machines the player already recognises tells the room's story for free.
2. **Junk buildings that deconstruct to scrap** (`costList` steel + slag): a loot economy with no
   loot tables. It suits Jawa scavengers exactly.
3. **Placeholder loot rollers.** A 1×1 symbol rolls its prize at spawn, so one layout yields
   different loot each time without needing 13 layouts. Vanilla can do this without C# in two
   ways: a KCSG symbol pointing at an `AncientHermeticCrate`-style container, or a vanilla
   `StructureLayoutDef` room using `ThingSetMakerDef` contents.
4. **The raid beacon in the busiest room.** The threat is tied to exploration, not to a timer.
   Vanilla gives us this with no C#: `RectTrigger` + `SignalAction_Ambush`, or
   `CompSendSignalOnMotion` (both are in the vanilla source; `RectTrigger` is in
   `Source/Verse/RectTrigger.cs`). Our `VaultDungeons` already wires sleepers with
   `MapComponent_VaultSleepers`.
5. **Corpses as buildings**: cheap, permanent and moodless. They could hold a
   `CompProperties_Forbiddable` "search" interaction later.
6. **Ragged edges**: loose floor tiles and rock collapse outside the footprint make it read as
   ruin, not as a prefab dropped in.

## 4. Archonexus

**What it is.** A field of 3–5 inert, vine-choked archotech ruins scattered across the map.
There are three building types, each `destroyable false`, `useHitPoints false`,
`Impassable`, `fillPercent 0.75` and `neverBuildable`:

| def | footprint | texture | look |
|---|---|---|---|
| `AB_DerelictArchotechTower` | 5×5 | `AB_DerelictArchonexusA.png` 512×512 | broken square tower, grey-green panels, circuit-trace lines, vines, red-rust weeping |
| `AB_DerelictMajorArchotechStructure` | 7×7 | `…B.png` 378×512 | taller slab, the same treatment |
| `AB_DerelictArchonexusCore` | 11×11 | `…C.png` 876×1024 | vanilla archonexus core silhouette (corner bastions, the arc glyph), shattered top, overgrown |

**The five prefabs** (vanilla `PrefabDef`; no walls, floor, loot or pawns, only these buildings):

```
Gamma 5x5      Beta 11x11      Alpha 21x23              Delta 43x43 (8 towers ring a core)
  [T]            [CORE]          . T .                    . . . T . . .
                                 T [M] T                  . T . . . T .
                                 . T .                    T . [CORE]. T
                                                          . T . . . T .
                                                          . . . T . . .
Epsilon 77x74: 4 major structures at the compass points, 8 towers in two rings, core at centre.
```

**Machinery.** Pure XML: vanilla `PrefabDef` + `ThingDef` + VEF `GenericPrefabSpawner`. Note that
its parent `AB_JunkBuildingBase` is in Alpha Biomes. **Art:** 3 donor-original repaints in the
vanilla Ideology archotech style. They are very good. They are also the only thing here worth
missing, and they are **not ours to keep**.

**What is reusable for us.** Not much. The one idea is **a ruin that is a set of one big piece
plus satellites in a geometric ring (radial symmetry)**, which reads as a former single
installation once you see it from a distance. Indestructible, impassable, unhit-able landmarks
are a fine pattern for a "you cannot strip-mine the wonder" ruin. The pattern already exists as
vanilla Ideology's real archonexus.

## 5. How the three relate

They are unrelated except by authorship (Sarg / Oskar's Alpha mods) and delivery (the same VEF
spawner worker, the same chance). Each is a thin Alpha Biomes wrapper around content that lives
in a sister mod: Alpha Memes (temple), Alpha Genes (lab), and Alpha Biomes' own Odyssey folder
(archonexus). None shares symbols, art or loot with the others. **None needs Alpha Biomes C#.**
Only the biolab needs any C#, and that C# belongs to Alpha Genes.

## 6. Compared with what we already have

| technique | donor | us (search of `src/`, 2026-10-19) |
|---|---|---|
| KCSG hand-drawn layouts + SymbolDefs | temple, lab | **already used**: WarLab, VaultDungeons, DarkTower and Ashfall in `src/RimUtinni/StructureInjectionsRUT/`, each with a `gen_*_layout.py` **generator** (better than the donor's hand-typed 886 KB file) |
| pawn symbols in layouts | (lab via the raid comp) | already used: `RUT_Symbol_MechLancer`, Helix Jawa kinds |
| vanilla `PrefabDef` | archonexus | used in 4 files (`RUT_ScarlandsSprungDangers`, `JawaGroundHulk`, …) |
| our own plan replayer | none | `src/RimMandrake/StructureInjections` (`GenStep_RimplacePlan`, rimplace plan text), which the donor has no equivalent of |
| mutator → structure | VEF GenericKCSG/Prefab spawner worker | `TileMutatorDef.extraGenSteps` → our GenStep (no C#) |
| **KCSG symbol `styleCategory`** (style kit reskins vanilla furniture) | temple | **not used** (0 hits) |
| **ruined-machine junk kit that deconstructs to scrap** | lab | partly: `src/RimMandrake/WreckedMachines` (wrecked machines) and `Wreckage`; check before building another |
| **spawn-time loot roller symbol** | lab (C#) | **not used** as a symbol pattern |
| **proximity-triggered ambush** (`RectTrigger`/`SignalAction_Ambush`/`CompSendSignalOnMotion`) | lab (C#) | not used by name; VaultDungeons has its own sleeper component |
| corpse-as-building, `Graphic_Random` | lab | `Graphic_Random` is widely used; corpse dressing not found |
| **vanilla `StructureLayoutDef` + `LayoutRoomDef` + `RoomContents_*`** (Odyssey's procedural ruin generator: weighted room table, `shouldDamage`, junk scatterers) | **neither donor uses it** | **not used** (0 vanilla `StructureLayoutDef`/`LayoutRoomDef` in `src/`) |

**The technique we're missing is vanilla's, not the donor's.** Odyssey ships a full procedural
ruin generator. `Defs/Odyssey/LayoutDefs/Layouts_AncientRuins.xml` `AncientRuins_Scarlands` uses
`LayoutWorker_AncientRuins` with `shouldDamage true` and a **weighted room table**:
Empty 5, Rubble 3, IndustrialStorage 2, OperatingRoom 1, ReactorToxicWaterRoom 2, SecureRoom 1,
MechsWithLoot 0.1, InsectHive 0.1, CryptosleepCasket 0.05, and so on. Rooms are filled by
`RoomContents_*` workers (OperatingRoom, ReactorCorpseRoom, Stockpile, CryptosleepCaskets_Hostile,
ControlRoom, …). A derelict lab is close to "this generator with a lab-flavoured room table and a
ruined-machine kit": **no hand-drawn layouts, and every visit is different**. The donor shipped 13
fixed drawings to fake that variety. One caution: our world is a fixed, frozen savegame, but each
site's map is generated when you first visit, so procedural rooms don't conflict with the
no-worldgen ruling. Whether the owner wants a site's floor plan fixed or varied is a question for
him (§8).

## 7. Design brief: our versions

Names follow `design/NAMING_SCHEME_PLAN.md`. All ride the existing
`TileMutatorDef.extraGenSteps` hook. A new mod is not needed; extend `StructureInjections`
(RM tier) and `StructureInjectionsRUT` (RUT tier).

1. **`RM_DerelictGeneLab` (RM tier, franchise-free).** A ruined bio-lab.
   - **Generator:** a vanilla `StructureLayoutDef` with `LayoutWorker_AncientRuins` and our own
     room table:

     | room | weight |
     |---|---|
     | vat hall | 3 |
     | gene wing | 2 |
     | ward | 2 (vanilla `RoomContents_OperatingRoom` style) |
     | specimen store | 1 (shelves plus a loot crate) |
     | collapsed | 3 |
     | sealed vault | 0.1 (mechs with loot) |

   - **Kit:** about 12 "ruined vanilla Biotech machine" junk buildings that deconstruct to steel
     and slag, a corpse dressing set, and a rusted-tile floor.
   - **Threat:** a `RectTrigger` → `SignalAction_Ambush` in the central room (vanilla, no C#).
   - **Mod settings:** on/off; ambush on/off; loot density.
   - **Cost:** about 3 agent-days plus about 15 sprites (art goes through `art install`).
2. **Precursor nexus, RUT tier: `RUT_RakatanNexusRuin`.** This is the archonexus idea re-cast as
   the Rakatan ruin our campaign already has (WarLab, Ashfall, the Rakatan Trace).
   - One core plus a ring of satellites as a vanilla `PrefabDef`: indestructible, impassable,
     unhit-able.
   - Optionally a buried `RUT_` KCSG chamber under the core that links to the existing Rakatan
     command-code chain.
   - **Cost:** about 1 agent-day plus 3 sprites.
3. **Desert temple.** The tier depends on the owner's answer (§8).
   - The **canon Egyptian-coded** architecture in Star Wars is the Sith tombs of the Valley of
     the Dark Lords (Korriban/Moraband), which would make this an RSW-tier canon build (an IP
     route) placed by RUT.
   - An invented Ash'karr temple would be `RM_` (franchise-free, per the 2026-09-22 Q11a ruling).
   - **Plan:** the three-room processional axis from §2, as a `gen_temple_layout.py` KCSG
     generator. Its look comes from a `StyleCategoryDef` kit (about 12 sprites reskinning wall,
     column, door, pew, altar, torch and table), set on each symbol. Give it a reason to enter:
     a reliquary loot roller, a sleeper ambush, or a quest hook into an existing arc.
   - **Cost:** about 1.5 agent-days plus about 12 sprites.

## 8. Questions only the owner can answer

1. **Desert temple: which kind?**
   - (a) A Sith-tomb temple, canon Korriban-style (RSW tier, IP route).
   - (b) An invented Ash'karr cult temple (RM tier).
   - (c) Skip temples entirely.
   - (d) Write-in.
2. **Derelict lab floor plans: fixed or varied?**
   - (a) Varied per visit (vanilla procedural room table; cheaper to build, never the same twice).
   - (b) A few fixed, authored plans (like the donor; more art direction, and the player can learn
     them).
   - (c) Both: a fixed core with procedural wings.
3. **Archonexus: rebuild it?**
   - (a) Re-cast as a Rakatan precursor ruin (RUT).
   - (b) Drop it. Vanilla Ideology's real archonexus already covers the look.
   - (c) Keep a franchise-free `RM_` version.
4. **Should any of these ruins attack?**
   - (a) A proximity ambush in the central room, like the donor.
   - (b) Sleepers that only wake if disturbed (our VaultDungeons pattern).
   - (c) No threat, scavenging only.

## 9. Recommendation

Let the donor go with nothing kept. Nothing in these three mutators is worth carrying except
ideas, and every idea is buildable from vanilla machinery we already load.

- **Order of work:**
  1. **`RM_DerelictGeneLab` on Odyssey's procedural ruin generator**, because it teaches us the
     one vanilla technique we have not used, and every later ruin can reuse it.
  2. **The Rakatan nexus**, because it is cheap and fits the arc.
  3. **The temple**, once the owner answers question 1.
- **Close the four-mutator item** `UNPORTED_MUTATORS_DECIDE_FOUR_ON_THE_STEP` for these three by
  pointing at this brief. Their replacements become new items only if the owner picks them.
