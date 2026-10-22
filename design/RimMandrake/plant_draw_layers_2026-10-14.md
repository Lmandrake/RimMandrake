# Plant draw layers: ground cover under everything (2026-10-14)

**Item:** `ROT_MOSS_VERIFY_UNDER_THE_MUSHROOMS` (open: needs a game look).
**Owner, typed 2026-10-14:** *"Lower all such plants in all biomes. Small ground cover on the appropriate layer."*
**Tool:** `src/RimMandrake/Utils/plant_draw_layers.py` (selftest `selftest_plant_draw_layers.py`).

## Why ground cover went to FloorEmplacement (7)

Measured from decompiled 1.6 (`Verse/AltitudeLayer.cs`, `RimWorld/Plant.cs` `Print`):

- A plant draws at its def's `altitudeLayer`: FloorEmplacement 7 · Filth 8 · Zone 9 · SmallWire 10 · **LowPlant 11** · Building 15 · Item 18 (the default when a def names none).
- `Plant.Print` lifts the top edge of every plant quad by **0.1** in altitude (`topVerticesAltitudeBias`). Layers sit **0.366** apart (`Altitudes.LayerSpacing`; `AltInc` 0.0366 is a tenth of a layer), so the tilt never crosses a layer: any lower layer keeps a plant under every LowPlant plant. Top edge of a layer-7 plant: 7 × 0.366 + 0.1 = 2.66, under the LowPlant bottom edge 4.02. (The same fact makes a higher-layer plant cover a lower-layer one wherever they stand: `GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT`, `src/RimMandrake/BiomesShell/Source/RM_PlantDrawOrder.cs`.)
- Within one layer, which plant draws on top depends on a position hash. That is the reported "the moss is sometimes in front".
- No game logic reads a plant's `altitudeLayer` except drawing (source search for `altitudeLayer ==/</>` and `AltitudeLayer.LowPlant` found no hits outside drawing). Moving a plant changes **draw order only**: size, food, fertility and growth are untouched.

Every ground-cover plant goes to FloorEmplacement (7), the same layer as the hessuk moss (`1e6363c46`). Two ground-cover plants that overlap share that layer, so they keep the hash order between themselves, which is fine. Filth (8) draws over the cover, and so do zones (9) and wires (10).

## Census: what it counts

- **Load set:** `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (550 mods resolved, 1 missing: `vlvop.tormentmaster.expansion`). Every `mandrake.*` mod is read **from the repo**, so commits that are not yet deployed count. The composed `mandrake.rm.biomes` is mapped member by member.
- **Defs:** 9,534 def files. ThingDef and BiomeDef only, with top-level `MayRequire`/`MayRequireAnyOf` honoured.
- **Patches:** 2,010 patch files, 23,641 operations applied in load order with lxml (full XPath 1.0) and 0 xpath errors. 179 operations use a mod's own custom class (mod-settings gates and the like), so they were counted and skipped. Five of those mention a field this census reads, and none of them is about plants (Android/robot settings, a primitive-refinery option, ReGrowth retexture/visual-effect options).
- **Inheritance:** each field comes from the nearest `ParentName` ancestor that declares it.
- **Roster:** every `<wildPlants>` entry (both XML shapes, `MayRequire` honoured) of the **62 BiomeDefs defined by a mandrake.\* package**, after patches. Ownership was read from the defining package, never from the prefix. Plants whose own `plant/wildBiomes` names one of those biomes are included too. That gives **388 plants** with 0 dangling names.
- **Sanity probe:** checked against the 2026-10-04 def dump (the game's own post-load values). All **272/272** plants on LowPlant in XML are LowPlant in the dump. The only differences are:
  - 44 trees that are Building in XML and `Pawn` in the dump. A runtime C# change by a donor mod lifts tall trees. They are trees, so nothing here depends on it.
  - `AB_Bryolux`, which changed in `1e6363c46` after the dump.
  - 4 size edits made since the dump.
  - 34 newer `RM_` plants that the dump does not have yet.

## Criteria for "small ground cover"

A plant is **GROUND_COVER** only when all of these hold:

1. **C1** It is not a tree (`plant/treeCategory` unset or None, and it is not harvested for wood logs).
2. **C2** It is not sown (no `plant/sowTags`). Crops stand upright by design.
3. **C3** Its mature footprint `graphicData.drawSize.x × plant.visualSizeRange.max` is **≤ 1.2 cells**. Per `Plant.Print`, a plant is drawn as a square of that side.
4. **C4** It reads as low, spreading cover, judged from its name, label or description: moss, grass, turf, lichen, crust, film, mat, carpet, creeping or flat cover. It must **not** read as an upright form: caps or mushrooms, stalks, stems, shrubs, bushes, flowers, reeds, fronds, cacti, pods, spires.

- **UPRIGHT:** C1, C2 or C3 fails, or C4 hits only upright words.
- **BORDERLINE:** C1 to C3 hold, but C4 hits both kinds of word or neither. These are listed below and were **not changed**.

Where the word rules could not decide, I read the description and recorded the ruling with its reason in the script's `OVERRIDES` table.

**By owner ruling:** the item asked him about *"sagecrust, dewshrooms, fruiting bodies"* and he answered *"Lower all such plants"*. So `RM_Sagecrust`, `RM_Dewshrooms` (tiny caps in clusters) and `RM_FruitingBodies` are ground cover.

## Result

| class | plants | already low | lowered now |
|---|---|---|---|
| GROUND_COVER | 55 | 1 (`AB_Bryolux`, 1e6363c46) | 54 |
| BORDERLINE | 25 | — | 0 (owner's call) |
| UPRIGHT | 308 | — | 0 |

**How the 54 were lowered:**

- **44 owned defs** got `<altitudeLayer>FloorEmplacement</altitudeLayer>` in their own def file. These are 41 RimMandrake defs, 1 RimStarWars def (`RSW_SurraGrass`) and 4 RimUtinni defs (`RUT_DarkCrust`, `RUT_DosimeterLawn`, `RUT_Glower`, `RUT_Fuzz`).
- **10 donor defs** are changed by patches in the mod whose biome spawns them. Each patch first tests that the def exists, so a missing donor is a silent no-op. Each donor inherits its layer from a parent def, so the patch adds the field to the def itself.
  - `src/RimMandrake/TheForge/Patches/RM_TheForge_GroundCoverDrawLayer.xml`: `AB_TinkleGrass`, `IronScruff_PrimordialGrass`
  - `src/RimMandrake/Wastes/Patches/RM_Wastes_GroundCoverDrawLayer.xml`: `Plant_GrayGrass` (Biotech ashskal)
  - `src/RimMandrake/LeaningScrub/Patches/RM_LeaningScrub_GroundCoverDrawLayer.xml`: `RG_Plant_AridGrass`, `RG_Plant_CrimsonCushion`
  - `src/RimUtinni/UtinniPatches/Patches/RUT_GroundCoverDrawLayer.xml`: `AB_AlienGrass`, `AB_HardyGrass`, `AB_ToxiGrass`, `GRimMoss`, `RG_Plant_ToxiGrass` (spawned only by RUT biomes)
- A patch changes the def wherever it spawns, so these plants are lowered **in all biomes**, as ruled.
- No ground-cover plant is owned by Pyrelands, FlowWorks or GimmeSomeSlack, and none of those files was touched.

**Validation:**

- `validate_patch.py` ran with `--mods-config` set to the FULL list and the three `--defs` roots plus `src`.
  - The 4 patch files have 0 errors and 0 warnings, and each of the 10 Adds matches exactly 1 def.
  - The 31 edited def files have 0 errors from this change. The validator reports 2 errors in files I edited, but they predate this change: `RM_Plant_SlimeGrass` and `RM_GreentideGrass` name `leaflessGraphicPath Things/Plant/Grass_Leafless`, the vanilla texture in Core's packed assets, which the validator cannot see.
- Selftests for the touched mods (`run_selftests.py --only`, 29 files) all pass.
- A full re-census after the change shows all 55 ground-cover plants on FloorEmplacement.

### Borderline: the owner decides (nothing changed)

- **Tall grasses** (one question for all of them): `AB_TallSlimyGrass`, `IronScruff_PrimordialTallGrass`, `PoisonPlantTallGrass`, `RG_Plant_TallToxiGrass`, `RM_GreentideTallGrass`. Vanilla-style "tall grass" at 0.85 cells and 9 meshes. Grass, but tall.
- **Low but with body:** `RM_Qeshra` (knee-low bead cushion), `RM_Murkblush` (low round cushion), `RM_Vellamine` (dense clump of leaves, "groundcover" in its text), `RM_Venomvine` (low matted runners with thorns), `RM_Tullick` (low whorl over a domed tuber), `RM_Skelver` (plate rosette of fat leaves), `RM_Tsevrix` (low heap of bladders), `RM_Sessarix` (resin boils on rock), `RM_Steamfrond` (rosette of fronds round a vent), `RM_Halquin` (blades pressed flat against a trunk), `RM_Dewfringe` (low fringe of filaments).
- **Ambiguous text:** `AB_RedLeaves` (described as grass, labelled "ocular plant", 1.2 cells), `RM_Claithe` (flat rosette lifted on a root-plate), `RM_FE_Plant_EmberGrass` (grass, but "puts everything into height"), `RM_Ghostpane` (panes joined at angles), `RM_Wanlith` (sparse knee-high stalks, "the ground's baseline cover").
- **Unknown shape** (no form words in the text): `AB_FrostLeaf`, `AB_GargantuanLithops`, `AB_RimeNodules`, `Plant_Bubblespore_Wild`.

Any of these can be moved by adding its name to `OVERRIDES` as GROUND_COVER and giving it the same one-line edit or patch.

## What to look at in game (owner look list)

1. **Rot map at play zoom.** Hessuk moss, tavvik crust (`RM_Sagecrust`), pimmik mold (`RM_FruitingBodies`) and sikkra lure (`RM_Dewshrooms`) should be **under** every aumbri (`RM_TollukCap`), rukka cap (`RM_Wrinklecap`), pursk hood (`RM_VioletWimple`) and glowstool. Look for zero cases of cover drawn over a cap's stalk or base.
2. **Tiny caps under big caps.** Sikkra lure is now ground cover. Check that it still reads as glowing caps and does not look painted flat.
3. **One grass biome**, for example Wasteland (ashskal plus scumgrass) or Leaning Scrub (fuzz, whipfuzz, arid grass). Grass should sit under the shrubs and the stalked plants, never over their bases.
4. **Filth and zones over cover.** Blood or dirt on moss, and a stockpile zone over grass, should now draw *on top of* the cover. That is the expected result.
5. **Snow on ground cover** (Blue Desert palefloss, Nightside). The snow overlay rides on the same plane, so look for nothing odd.

## The census table

Regenerate with `python3 src/RimMandrake/Utils/plant_draw_layers.py --json <out> --md <table>` (≈5.5 min, full list). "layer now" is after this change.

### GROUND_COVER (55)

| defName | label | owner package | layer now | drawSize | visualSizeRange | mature cells | meshes | sowTags | tree | biomes | why |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `GRimMoss` | moss | grimterra.biomesmod | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RUT_CrackedLands | name: Moss |
| `IronScruff_PrimordialGrass` | primordial grass | ironscruff.primordialgeysers | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RM_TheForge, RUT_TheForge | name: Grass |
| `Plant_GrayGrass` | ashskal | ludeon.rimworld.biotech | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RM_Wastes, RUT_Wastes | name: Grass |
| `RM_Braskeen` | braskeen | mandrake.rm.biomes | FloorEmplacement (7) | 0.85 | 0.5~0.8 | 0.68 | 1 | - | - | RM_Miasma | desc: flat |
| `RM_CinderCrust` | cinder crust | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.2~0.5 | 0.5 | 9 | - | - | RM_TheForge | name: Crust |
| `RM_Cinderfelt` | cinderfelt | mandrake.rm.biomes | FloorEmplacement (7) | 1 | 0.4~0.7 | 0.7 | 4 | - | - | RM_Wastes | desc: felt |
| `RM_Cruststar` | cruststar | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.5~0.7 | 0.7 | 4 | - | - | RM_LeaningScrub | name: Cruststar |
| `RM_DarkCrust` | vein moss | mandrake.rm.biomes | FloorEmplacement (7) | 0.9 | 0.5~0.9 | 0.81 | 4 | - | - | RM_Cauldron | name: Crust |
| `RM_Dewshrooms` | sikkra lure | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.3~0.5 | 0.5 | 9 | - | - | RM_TheRot, RM_WeepingStones, RUT_TheRot, RUT_WeepingStones | owner named it (tiny caps in clusters, 0.5 cell, 9 meshes) |
| `RM_DosimeterLawn` | dosimeter lawn | mandrake.rm.biomes | FloorEmplacement (7) | 1.1 | 0.4~0.7 | 0.77 | 4 | - | - | RM_Wastes | desc: mat |
| `RM_FruitingBodies` | pimmik mold | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.3~0.5 | 0.5 | 25 | - | - | RM_TheRot, RUT_TheRot | owner named it (mold pins carpeting the floor) |
| `RM_Fuzz` | the fuzz | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.55~0.85 | 0.85 | 4 | - | - | RM_LeaningScrub | name: Fuzz |
| `RM_Glasscrust` | glasscrust | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.9~1.1 | 1.1 | 4 | - | - | RM_Stillsand | desc: crust |
| `RM_Glower` | the Glowers | mandrake.rm.biomes | FloorEmplacement (7) | 0.9 | 0.5~0.9 | 0.81 | 4 | - | - | RM_Warscar | desc: moss |
| `RM_GlowingGrass` | grass | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RM_Abyss, RUT_Abyss | name: Grass |
| `RM_GreentideGrass` | grass | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RM_Greentide | name: Grass |
| `RM_Grennick` | grennick | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.8~1 | 1.0 | 1 | - | - | RM_Webwork | desc: turf |
| `RM_Lashgrass` | lashgrass | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RM_Contagion | desc: carpeting |
| `RM_Leachmoss` | leachmoss | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.4~0.7 | 0.7 | 9 | - | - | RM_LongShade, RUT_Desert | desc: mat |
| `RM_LightPipeNub` | light-pipe nub | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.12~0.2 | 0.2 | 4 | - | - | RM_Stillsand, RUT_ExtremeDesert | desc: a glass knuckle flush with the sand, 0.2 cell |
| `RM_Lisqueth` | lisqueth | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.7~1 | 1.0 | 1 | - | - | RM_BlueDesert | desc: flat |
| `RM_Masonmat` | masonmat | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.8~1.1 | 1.1 | 1 | - | - | RM_GreySea | desc: a mat spreading across the sediment |
| `RM_Nemreth` | nemreth | mandrake.rm.biomes | FloorEmplacement (7) | 0.75 | 0.4~0.7 | 0.525 | 1 | - | - | RM_Miasma | desc: a low mat of hair-fine stalks |
| `RM_Palefloss` | palefloss | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.35~0.55 | 0.55 | 9 | - | - | RM_BlueDesert, RUT_BlueDesert | desc: grass |
| `RM_Pallasheen` | pallasheen | mandrake.rm.biomes | FloorEmplacement (7) | 0.55 | 0.5~0.8 | 0.44 | 1 | - | - | RM_Miasma | desc: one leaf pressed flat, never stands up |
| `RM_Pillowmoss` | pillowmoss | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.7~0.9 | 0.9 | 4 | - | - | RM_LeaningScrub | desc: a fat, low cushion of moss |
| `RM_Plant_SlimeGrass` | slime-grass | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.4~0.8 | 0.8 | 9 | - | - | RM_GelatinousSlime | name: Grass |
| `RM_Plennith` | plennith | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.8~1.1 | 1.1 | 1 | - | - | RM_FeverWood | desc: mat |
| `RM_Sagecrust` | tavvik crust | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.2~0.5 | 0.5 | 9 | - | - | RM_TheRot, RUT_TheForge, RUT_TheRot | owner named it (crust on rock and mat) |
| `RM_Scumgrass` | scumgrass | mandrake.rm.biomes | FloorEmplacement (7) | 0.9 | 0.4~0.8 | 0.72 | 4 | - | - | RM_Wastes | desc: grass |
| `RM_Selvix` | selvix | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.6~1 | 1.0 | 1 | - | - | RM_Cauldron | desc: flat |
| `RM_Simmerlace` | simmerlace | mandrake.rm.biomes | FloorEmplacement (7) | 1x1 | 0.8~1.1 | 1.1 | 1 | - | - | RM_TheScald | desc: flat |
| `RM_Skimmel` | skimmel | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.9~1 | 1.0 | 1 | - | - | RM_FeverWood | desc: film |
| `RM_Threllick` | threllick | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.8~1 | 1.0 | 1 | - | - | RM_Webwork | desc: a mat of surface roots, the ground itself |
| `RM_Toothmoss` | toothmoss | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.5~0.9 | 0.9 | 9 | - | - | RM_Contagion | desc: carpet |
| `RM_TwistingThorngrass` | twisting thorngrass | mandrake.rm.biomes | FloorEmplacement (7) | 1.15 | 0.4~0.6 | 0.69 | 4 | - | - | RM_FloodedCanyon, RUT_CrackedLands | grass with small thorns; grass habit |
| `RM_UltrissPad` | ultriss pad | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.35~0.65 | 0.65 | 9 | - | - | RM_Stillsand | desc: a flat pad flush with the ground |
| `RM_Verdimoss` | verdimoss | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.2~0.5 | 0.5 | 1 | - | - | RM_WeepingStones | desc: moss |
| `RM_Weepmat` | weep-mat | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.3~0.6 | 0.6 | 1 | - | - | RM_WeepingStones | name: mat |
| `RM_Wessaline` | wessaline | mandrake.rm.biomes | FloorEmplacement (7) | 1 | 0.8~1.1 | 1.1 | 1 | - | - | RM_Miasma | desc: a continuous skin over the salt pans |
| `RM_Whipfuzz` | whipfuzz | mandrake.rm.biomes | FloorEmplacement (7) | - | 0.9~1.1 | 1.1 | 4 | - | - | RM_LeaningScrub | desc: grass |
| `RM_Crowncarpet` | crowncarpet | mandrake.rm.luminouspigment | FloorEmplacement (7) | 0.85 | 0.5~0.9 | 0.765 | 1 | - | - | RM_TheScald | desc: algae |
| `RSW_SurraGrass` | surra grass | mandrake.rsw.swbestiary | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RUT_Desert | name: Grass |
| `RUT_Fuzz` | the fuzz | mandrake.rut.ashkarrflora | FloorEmplacement (7) | - | 0.55~0.85 | 0.85 | 4 | - | - | RUT_AridShrubland | name: Fuzz |
| `RUT_DarkCrust` | vein moss | mandrake.rut.patches | FloorEmplacement (7) | 0.9 | 0.5~0.9 | 0.81 | 4 | - | - | RUT_Cauldron | name: Crust |
| `RUT_DosimeterLawn` | dosimeter lawn | mandrake.rut.patches | FloorEmplacement (7) | 1.1 | 0.4~0.7 | 0.77 | 4 | - | - | RUT_Wastes | desc: mat |
| `RUT_Glower` | the Glowers | mandrake.rut.patches | FloorEmplacement (7) | 0.9 | 0.5~0.9 | 0.81 | 4 | - | - | RUT_Scarlands | desc: moss |
| `RG_Plant_AridGrass` |  | regrowth.botr.core | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RM_LeaningScrub, RUT_AridShrubland | name: Grass |
| `RG_Plant_CrimsonCushion` | crimson cushion | regrowth.botr.core | FloorEmplacement (7) | - | 0.5~0.9 | 0.9 | 16 | - | - | RM_LeaningScrub, RUT_AridShrubland | desc: carpet |
| `RG_Plant_ToxiGrass` | toxigrass | regrowth.botr.core | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RUT_Wastes | name: Grass |
| `AB_AlienGrass` | ocular grass | sarg.alphabiomes | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RUT_Contagion | name: Grass |
| `AB_Bryolux` | hessuk moss | sarg.alphabiomes | FloorEmplacement (7) | - | 0.82~0.95 | 0.95 | 4 | - | - | RM_TheRot, RUT_TheRot | name: moss |
| `AB_HardyGrass` | hardy grass | sarg.alphabiomes | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RUT_CrackedLands | name: Grass |
| `AB_TinkleGrass` | tinkle grass | sarg.alphabiomes | FloorEmplacement (7) | - | 0.6~0.9 | 0.9 | 9 | - | - | RM_TheForge, RUT_TheForge | name: Grass |
| `AB_ToxiGrass` | toxi grass | sarg.alphabiomes | FloorEmplacement (7) | - | 0.4~0.6 | 0.6 | 9 | - | - | RUT_BlueDesert | name: Grass |

### BORDERLINE (25)

| defName | label | owner package | layer now | drawSize | visualSizeRange | mature cells | meshes | sowTags | tree | biomes | why |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `IronScruff_PrimordialTallGrass` | primordial tall grass | ironscruff.primordialgeysers | LowPlant (11) | - | 0.7~0.85 | 0.85 | 9 | - | - | RM_TheForge, RUT_TheForge | words both/neither: +Grass -Tall |
| `RM_Claithe` | claithe | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RM_FeverWood | flat rosette, but on a root-plate that lifts clear of the mud |
| `RM_Dewfringe` | dewfringe | mandrake.rm.biomes | LowPlant (11) | - | 0.25~0.45 | 0.45 | 9 | - | - | RM_LongShade | a low sparse fringe of filaments (0.45 cell, 9 meshes) |
| `RM_FE_Plant_EmberGrass` | ember grass | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.85 | 0.85 | 9 | - | - | RM_Pyrelands | a grass, but desc: 'puts everything into height' |
| `RM_Ghostpane` | ghostpane | mandrake.rm.biomes | LowPlant (11) | 0.9 | 0.6~1 | 0.9 | 1 | - | - | RM_TheChill | hand-wide panes joined at angles: flat or standing? |
| `RM_GreentideTallGrass` | tall grass | mandrake.rm.biomes | LowPlant (11) | - | 0.7~0.85 | 0.85 | 9 | - | - | RM_Greentide | words both/neither: +Grass -Tall |
| `RM_Halquin` | halquin | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1 | 1.0 | 1 | - | - | RM_FeverWood | words both/neither: +flat -trunk |
| `RM_Murkblush` | murkblush | mandrake.rm.biomes | LowPlant (11) | - | 0.55~0.8 | 0.8 | 1 | - | - | RM_GreySea | words both/neither: + - |
| `RM_Qeshra` | qeshra | mandrake.rm.biomes | LowPlant (11) | - | 0.45~0.7 | 0.7 | 1 | - | - | RM_BlueDesert | words both/neither: +mat -stalk |
| `RM_Sessarix` | sessarix | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1 | 1.0 | 1 | - | - | RM_Cauldron | words both/neither: + - |
| `RM_Skelver` | skelver | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1 | 1.0 | 1 | - | - | RM_TheSump | words both/neither: + - |
| `RM_Steamfrond` | steamfrond | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.8 | 0.8 | 1 | - | - | RM_WeepingStones | words both/neither: +crusted -fronds |
| `RM_Tsevrix` | tsevrix | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | - | - | RM_Cauldron | words both/neither: + - |
| `RM_Tullick` | tullick | mandrake.rm.biomes | LowPlant (11) | - | 0.6~0.9 | 0.9 | 1 | - | - | RM_FeverWood | words both/neither: + - |
| `RM_Vellamine` | vellamine | mandrake.rm.biomes | LowPlant (11) | 0.9 | 0.5~0.9 | 0.81 | 1 | - | - | RM_Miasma | words both/neither: +groundcover -stem |
| `RM_Venomvine` | venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RM_LongShade, RUT_Desert | words both/neither: +matted -thorns |
| `RM_Wanlith` | wanlith | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.8 | 0.8 | 1 | - | - | RM_FeverWood | knee-high stalks, yet 'the ground's baseline cover' |
| `PoisonPlantTallGrass` | tall grass | mlie.advancedbiomes | LowPlant (11) | - | 0.7~0.85 | 0.85 | 9 | - | - | RUT_BlueDesert | words both/neither: +Grass -Tall |
| `Plant_Bubblespore_Wild` | wild bubble spore plant | mlie.starwarsanimalcollection | LowPlant (11) | - | 0.3~1 | 1.0 | 4 | - | - | RUT_Greentide | words both/neither: + - |
| `RG_Plant_TallToxiGrass` | tall toxigrass | regrowth.botr.core | LowPlant (11) | - | 0.7~0.85 | 0.85 | 9 | - | - | RUT_Wastes | words both/neither: +Grass -Tall |
| `AB_FrostLeaf` | frost leaf | sarg.alphabiomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RUT_FuelSnows, RUT_Umbra | words both/neither: + - |
| `AB_GargantuanLithops` | gargantuan lithops | sarg.alphabiomes | LowPlant (11) | - | 0.75~1 | 1.0 | 1 | - | - | RUT_CrackedLands | words both/neither: + - |
| `AB_RedLeaves` | ocular plant | sarg.alphabiomes | LowPlant (11) | - | 0.7~1.2 | 1.2 | 1 | - | - | RUT_Contagion | 'ocular plant' 1.2 cells; desc says grass, label says plant |
| `AB_RimeNodules` | rime nodules | sarg.alphabiomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RUT_FuelSnows, RUT_Umbra | words both/neither: + - |
| `AB_TallSlimyGrass` | tall slimy grass | sarg.alphabiomes | LowPlant (11) | - | 0.7~0.85 | 0.85 | 9 | - | - | RUT_Slime | words both/neither: +Grass -Tall |

### UPRIGHT (308)

| defName | label | owner package | layer now | drawSize | visualSizeRange | mature cells | meshes | sowTags | tree | biomes | why |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `IronScruff_Bindweed` | bindweed | ironscruff.primordialgeysers | LowPlant (11) | - | 0.4~0.5 | 0.5 | 25 | Ground | - | RM_TheForge, RUT_TheForge | sown crop |
| `Plant_Ambrosia` | ambrosia bush | ludeon.rimworld | LowPlant (11) | - | 0.6~1.1 | 1.1 | 1 | - | - | RM_WeepingStones, RUT_WeepingStones | name: bush |
| `Plant_Toxipotato` | toxipotato plant | ludeon.rimworld.biotech | LowPlant (11) | - | 0.5~1.05 | 1.05 | 1 | Ground,Hydroponic | - | RM_Wastes, RUT_Wastes | sown crop |
| `Plant_TreePolux` | polux tree | ludeon.rimworld.biotech | Building (15) | - | 1.5~2.1 | 2.1 | 1 | - | yes | RM_Wastes, RUT_Wastes | tree |
| `Plant_Fireweed` | fireweed | ludeon.rimworld.odyssey | LowPlant (11) | 1.5 | 0.3~0.4 | 0.6 | 4 | - | - | RM_TheForge, RUT_TheForge | desc: flowers |
| `Plant_MagmaCactus` | magma cactus | ludeon.rimworld.odyssey | LowPlant (11) | 2 | 0.4~0.65 | 1.3 | 1 | - | - | RM_TheForge, RUT_TheForge | mature 1.30 cells > 1.2 |
| `Plant_Reeds` | sarnreed | ludeon.rimworld.odyssey | LowPlant (11) | - | 0.7~0.8 | 0.8 | 4 | - | - | RM_WeepingStones, RUT_WeepingStones | name: Reeds |
| `RM_AgelessCap` | orlath cap | mandrake.rm.biomes | LowPlant (11) | - | 1.3~1.6 | 1.6 | 1 | - | - | RM_TheRot | mature 1.60 cells > 1.2 |
| `RM_Almslight` | almslight | mandrake.rm.biomes | LowPlant (11) | 1x1 | 0.9~1.3 | 1.3 | 1 | - | - | RM_TwilightSea | mature 1.30 cells > 1.2 |
| `RM_AmbrosyxFungus` | ambrosyx | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1.1 | 1.1 | 1 | - | - | RM_TheRot | desc: mushroom |
| `RM_Ammeth` | ammeth | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.4 | 1.4 | 1 | - | yes | RM_FeverWood | tree |
| `RM_Aphreen` | aphreen | mandrake.rm.biomes | LowPlant (11) | 1 | 0.6~1.1 | 1.1 | 1 | - | - | RM_Miasma | desc: upright |
| `RM_Arpeau` | churrun mast | mandrake.rm.biomes | Building (15) | - | 6~10 | 10.0 | 1 | VCE_Aquatic | yes | RM_TheRot, RUT_TheRot | tree |
| `RM_Bladderquill` | bladderquill | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | - | - | RM_WeepingStones | desc: standing |
| `RM_BlastpodShroom` | kabbrik pod | mandrake.rm.biomes | LowPlant (11) | - | 0.7~0.9 | 0.9 | 1 | - | - | RM_TheRot, RUT_TheRot | name: pod |
| `RM_BleedingTooth` | rhukk tooth | mandrake.rm.biomes | LowPlant (11) | - | 0.45~1.5 | 1.5 | 1 | - | - | RM_TheRot, RUT_TheRot | mature 1.50 cells > 1.2 |
| `RM_Bleedleaf` | bleedleaf | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1 | 1.0 | 4 | - | - | RM_Contagion | desc: shrub |
| `RM_BloodBouquet` | blood bouquet | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.5 | 1.5 | 4 | - | - | RM_Cauldron | mature 1.50 cells > 1.2 |
| `RM_BloodyFist` | bloody fist | mandrake.rm.biomes | Building (15) | - | 1.6~2 | 2.0 | 1 | - | - | RM_Contagion | mature 2.00 cells > 1.2 |
| `RM_Boilbulb` | boilbulb | mandrake.rm.biomes | LowPlant (11) | 0.85 | 0.5~0.9 | 0.765 | 4 | - | - | RM_Wastes | desc: a bulb swollen into a dome |
| `RM_Brakkel` | brakkel | mandrake.rm.biomes | LowPlant (11) | - | 2.5~4 | 4.0 | 1 | - | - | RM_Greentide | mature 4.00 cells > 1.2 |
| `RM_BrellikBulb` | brellik bulb | mandrake.rm.biomes | Building (15) | - | 0.3~0.7 | 0.7 | 1 | Ground,Decorative | - | RM_LanternDeeps | sown crop |
| `RM_Brelloch` | brelloch | mandrake.rm.biomes | Building (15) | - | 1~1.6 | 1.6 | 1 | Ground | yes | RM_Miasma | tree |
| `RM_Brennoth` | brennoth | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_Webwork | mature 1.30 cells > 1.2 |
| `RM_Brightbell` | tinnik bell | mandrake.rm.biomes | Building (15) | - | 0.64~1.5 | 1.5 | 1 | Ground,Decorative | - | RM_TheRot, RUT_TheRot | sown crop |
| `RM_Brimlock` | brimlock | mandrake.rm.biomes | LowPlant (11) | - | 1.8~2.4 | 2.4 | 1 | - | - | RM_Webwork | mature 2.40 cells > 1.2 |
| `RM_Brindeth` | brindeth | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.15 | 1.15 | 1 | - | yes | RM_TheSump | tree |
| `RM_BrineCrown` | brine crown | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.2 | 1.2 | 1 | - | - | RM_GreySea | desc: standing |
| `RM_Brinecomb` | brine comb | mandrake.rm.biomes | LowPlant (11) | - | 0.55~0.8 | 0.8 | 1 | - | - | RM_GreySea | desc: a row of standing teeth |
| `RM_Brunnock` | brunnock | mandrake.rm.biomes | Building (15) | - | 4~6 | 6.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_ChillStillbloom` | stillbloom | mandrake.rm.biomes | LowPlant (11) | 0.8 | 0.6~0.9 | 0.72 | 1 | RM_ChillBed | - | RM_TheChill | sown crop |
| `RM_Chimeglobe` | chimeglobe | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.1 | 1.1 | 1 | - | - | RM_BlueDesert, RUT_BlueDesert | desc: stalk |
| `RM_Cistrel` | cistrel | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RM_FeverWood | desc: standing |
| `RM_Corvath` | corvath | mandrake.rm.biomes | LowPlant (11) | - | 0.6~0.9 | 0.9 | 1 | - | - | RM_FeverWood | desc: spike |
| `RM_CrackedThornwood` | twisting thornwood | mandrake.rm.biomes | Building (15) | - | 1.3~3 | 3.0 | 1 | Ground | yes | RM_FloodedCanyon, RUT_CrackedLands | tree |
| `RM_CrimsonCap` | redsong | mandrake.rm.biomes | LowPlant (11) | - | 0.72~0.9 | 0.9 | 4 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `RM_CrownVenomvine` | crown venomvine | mandrake.rm.biomes | LowPlant (11) | - | 1~1 | 1.0 | 1 | - | - | RM_LeaningScrub | desc: stand |
| `RM_CruciblePod` | crucible pod | mandrake.rm.biomes | LowPlant (11) | - | 0.4~1 | 1.0 | 4 | - | - | RM_GreySea | name: Pod |
| `RM_CrystalFlower` | crystal flower | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.6 | 1.6 | 4 | - | - | RM_Cauldron | mature 1.60 cells > 1.2 |
| `RM_CubicSculpture` | cubic sculpture | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1.1 | 1.1 | 1 | - | - | RM_GreySea | desc: a geometric solid block |
| `RM_Cundral` | cundral | mandrake.rm.biomes | Building (15) | - | 1.2~2 | 2.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_DeepMycelium` | mycelium | mandrake.rm.biomes | LowPlant (11) | - | 0.2~0.4 | 0.4 | 4 | Ground | - | RM_LanternDeeps | sown crop |
| `RM_Dewblade` | dewblade | mandrake.rm.biomes | LowPlant (11) | - | 0.3~0.8 | 0.8 | 1 | - | - | RM_WeepingStones | desc: shin-high tufts standing edge-on |
| `RM_Dewgourd` | dewgourd | mandrake.rm.biomes | LowPlant (11) | - | 0.5~1.1 | 1.1 | 1 | Ground | - | RM_WeepingStones | sown crop |
| `RM_Dorvel` | dorvel | mandrake.rm.biomes | LowPlant (11) | - | 0.65~1 | 1.0 | 1 | Ground,Hydroponic | - | RM_TheSump | sown crop |
| `RM_Dripfringe` | dripfringe | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.8 | 0.8 | 1 | - | - | RM_WeepingStones | desc: a curtain hanging from overhangs |
| `RM_DrippingVenomvine` | dripping venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_Dulloth` | dulloth | mandrake.rm.biomes | LowPlant (11) | - | 4~5.2 | 5.2 | 1 | - | - | RM_Webwork | mature 5.20 cells > 1.2 |
| `RM_Eldspar` | eldspar | mandrake.rm.biomes | LowPlant (11) | 1.4 | 0.8~1.2 | 1.68 | 1 | RM_ChillBed | - | RM_TheChill | sown crop |
| `RM_Etchcap` | etchcap | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | Ground | - | RM_Abyss | sown crop |
| `RM_EuphoricCrown` | lussa crown | mandrake.rm.biomes | LowPlant (11) | - | 1.2~1.5 | 1.5 | 1 | - | - | RM_TheRot | mature 1.50 cells > 1.2 |
| `RM_Eyebark` | eyebark | mandrake.rm.biomes | Building (15) | - | 2.6~3.4 | 3.4 | 1 | - | yes | RM_Contagion | tree |
| `RM_FE_Plant_Quickgrass` | quickgrass | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.4 | 1.4 | 9 | - | - | RM_Pyrelands | mature 1.40 cells > 1.2 |
| `RM_FalseFruit` | pekk fruit | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.6 | 0.6 | 1 | - | - | RM_TheRot | desc: shaped to match the mushroom caps it mimics |
| `RM_Fellome` | fellome | mandrake.rm.biomes | LowPlant (11) | - | 1~1.4 | 1.4 | 1 | - | - | RM_Webwork | mature 1.40 cells > 1.2 |
| `RM_Fexxil` | fexxil | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RM_Cauldron | desc: shrub |
| `RM_FireLavender` | fire lavender | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 4 | Ground | - | RM_TheForge | sown crop |
| `RM_FlakespireFungus` | tarrusk spire | mandrake.rm.biomes | Building (15) | - | 0.6~2 | 2.0 | 1 | Ground | yes | RM_TheRot, RUT_TheRot | tree |
| `RM_Foamgorse` | foamgorse | mandrake.rm.biomes | LowPlant (11) | 0.9x0.9 | 0.7~1 | 0.9 | 1 | - | - | RM_TheScald | desc: a thicket straining upward |
| `RM_Fuselight` | fuselight | mandrake.rm.biomes | LowPlant (11) | 1 | 0.8~1.1 | 1.1 | 1 | RM_ChillBed | - | RM_TheChill | sown crop |
| `RM_Ghemmel` | ghemmel | mandrake.rm.biomes | Building (15) | - | 4~6 | 6.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_GiantAgariTox` | giant agaritox | mandrake.rm.biomes | LowPlant (11) | - | 3~4.5 | 4.5 | 1 | - | - | RM_Cauldron | mature 4.50 cells > 1.2 |
| `RM_GiantFibreStalk` | giant fibre stalk | mandrake.rm.biomes | BuildingOnTop (17) | - | 2.6~5 | 5.0 | 1 | Ground | yes | RM_Abyss, RUT_Abyss | tree |
| `RM_GiantGlowGlobe` | giant glow globe | mandrake.rm.biomes | LowPlant (11) | - | 1.5~2 | 2.0 | 1 | Ground | - | RM_Abyss, RUT_Abyss | sown crop |
| `RM_GiantLeaf` | giant leaf | mandrake.rm.biomes | LowPlant (11) | - | 0.5~1.3 | 1.3 | 9 | Ground | - | RM_FeverWood | sown crop |
| `RM_GiantToxicFlower` | giant toxic flower | mandrake.rm.biomes | LowPlant (11) | - | 1.4~2.2 | 2.2 | 1 | - | - | RM_Cauldron | mature 2.20 cells > 1.2 |
| `RM_GlassVeilKelp` | glass veil kelp | mandrake.rm.biomes | LowPlant (11) | 1.6x1.6 | 1.1~1.7 | 2.72 | 1 | - | - | RM_GreySea | mature 2.72 cells > 1.2 |
| `RM_Glassfern` | glassfern | mandrake.rm.biomes | LowPlant (11) | - | 0.6~0.9 | 0.9 | 1 | - | - | RM_BlueDesert, RUT_BlueDesert | desc: frond |
| `RM_Glimmerhusk` | glimmerhusk | mandrake.rm.biomes | LowPlant (11) | 1.1x1.1 | 0.9~1.2 | 1.32 | 1 | - | - | RM_TwilightSea | mature 1.32 cells > 1.2 |
| `RM_Gloamurn` | gloamurn | mandrake.rm.biomes | LowPlant (11) | 0.9x0.9 | 0.7~1.1 | 0.99 | 1 | - | - | RM_TwilightSea | desc: stands |
| `RM_GlowGlobe` | glow globe | mandrake.rm.biomes | Building (15) | - | 0.6~3 | 3.0 | 1 | Ground,Decorative | - | RM_Abyss, RUT_Abyss | sown crop |
| `RM_GlowberryBush` | glowberry bush | mandrake.rm.biomes | LowPlant (11) | - | 1.5~2 | 2.0 | 1 | Ground | - | RM_Abyss, RUT_Abyss | sown crop |
| `RM_Gorbeleth` | gorbeleth | mandrake.rm.biomes | Building (15) | - | 2~3 | 3.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Gorestalk` | gorestalk | mandrake.rm.biomes | Building (15) | - | 1.8~2.4 | 2.4 | 1 | - | - | RM_Contagion | mature 2.40 cells > 1.2 |
| `RM_Greatbole` | greatbole | mandrake.rm.biomes | Building (15) | - | 12~16 | 16.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Grellbush` | grellbush | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.8 | 0.8 | 1 | - | - | RM_LeaningScrub | desc: shrub |
| `RM_Grellspine` | grellspine | mandrake.rm.biomes | LowPlant (11) | - | 0.7~0.85 | 0.85 | 4 | - | - | RM_LeaningScrub | desc: shrub |
| `RM_GreyLady` | sylla lace | mandrake.rm.biomes | LowPlant (11) | - | 0.4~1 | 1.0 | 1 | Ground,RM_Fungiponics | - | RM_TheRot, RUT_TheRot | sown crop |
| `RM_HalfmadeTree` | halfmade tree | mandrake.rm.biomes | Building (15) | - | 2.3~3 | 3.0 | 1 | - | yes | RM_Contagion | tree |
| `RM_HalfmadeTreeBlighted` | blighted halfmade tree | mandrake.rm.biomes | Building (15) | - | 2~2.8 | 2.8 | 1 | - | yes | RM_Contagion | tree |
| `RM_Harrovaq` | harrovaq | mandrake.rm.biomes | Building (15) | - | 1.4~2.4 | 2.4 | 1 | Ground | yes | RM_FloodedCanyon | tree |
| `RM_HeatsinkFungus` | heatsink fungus | mandrake.rm.biomes | Building (15) | - | 0.25~0.6 | 0.6 | 4 | Ground | yes | RM_TheForge | tree |
| `RM_HoardVenomvine` | hoard venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.1 | 1.1 | 1 | - | - | RM_LeaningScrub | desc: man-high knot of canes |
| `RM_Hoarstock` | hoarstock | mandrake.rm.biomes | LowPlant (11) | - | 1.3~1.6 | 1.6 | 1 | - | - | RM_GreySea | mature 1.60 cells > 1.2 |
| `RM_HollowVenomvine` | hollow venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_HoolimbrePlant` | hoolimbre | mandrake.rm.biomes | LowPlant (11) | 1.1x1.1 | 0.7~1.1 | 1.21 | 4 | - | - | RM_TwilightSea | mature 1.21 cells > 1.2 |
| `RM_Hushcoral` | hushcoral | mandrake.rm.biomes | LowPlant (11) | 0.7x0.7 | 0.6~0.9 | 0.63 | 1 | - | - | RM_TwilightSea | desc: a coral |
| `RM_Ilbareen` | ilbareen | mandrake.rm.biomes | LowPlant (11) | - | 1.3~2 | 2.0 | 1 | - | - | RM_Miasma | mature 2.00 cells > 1.2 |
| `RM_Illurin` | illurin | mandrake.rm.biomes | LowPlant (11) | - | 4~7 | 7.0 | 1 | - | - | RM_Greentide | mature 7.00 cells > 1.2 |
| `RM_Immarel` | immarel | mandrake.rm.biomes | LowPlant (11) | 1 | 0.8~1.4 | 1.4 | 1 | - | - | RM_Miasma | mature 1.40 cells > 1.2 |
| `RM_Ismerrow` | ismerrow | mandrake.rm.biomes | LowPlant (11) | 0.85 | 0.5~1 | 0.85 | 1 | - | - | RM_Miasma | desc: stand |
| `RM_Ixalith` | ixalith | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.3 | 1.3 | 1 | - | - | RM_Cauldron | mature 1.30 cells > 1.2 |
| `RM_Kaddrath` | kaddrath | mandrake.rm.biomes | Building (15) | - | 6.5~9 | 9.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_KeeningCordax` | keening cordax | mandrake.rm.biomes | LowPlant (11) | - | 2~3 | 3.0 | 1 | - | - | RM_Cauldron | mature 3.00 cells > 1.2 |
| `RM_Kessaroth` | kessaroth | mandrake.rm.biomes | LowPlant (11) | - | 0.6~0.9 | 0.9 | 1 | - | - | RM_Webwork | desc: stem |
| `RM_Kethevar` | kethevar | mandrake.rm.biomes | LowPlant (11) | - | 0.6~0.9 | 0.9 | 1 | - | - | RM_BlueDesert | desc: a hand-high spiral coil |
| `RM_Kettlewick` | kettlewick | mandrake.rm.biomes | LowPlant (11) | 0.6x0.6 | 0.5~0.7 | 0.42 | 1 | - | - | RM_TheScald | desc: a single upright string |
| `RM_Kissaveth` | kissaveth | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.2 | 1.2 | 1 | - | - | RM_Cauldron | desc: stalks |
| `RM_KneelOllim` | kneel ollim | mandrake.rm.biomes | Building (15) | - | 1.6~2.6 | 2.6 | 1 | Ground | yes | RM_Stillsand | tree |
| `RM_Kollavane` | kollavane | mandrake.rm.biomes | LowPlant (11) | - | 3.3~4.8 | 4.8 | 1 | - | yes | RM_Webwork | tree |
| `RM_Korveth` | korveth | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.1 | 1.1 | 1 | - | - | RM_TheSump | desc: shrub |
| `RM_KuvraSpout` | kuvra spout | mandrake.rm.biomes | LowPlant (11) | - | 0.3~0.5 | 0.5 | 9 | - | - | RM_LanternDeeps | desc: an upside-down cone |
| `RM_Lanneth` | lanneth | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.05 | 1.05 | 1 | - | - | RM_TheSump | desc: stalks |
| `RM_Lanternstone_Sowable` | fast growing lanternstone | mandrake.rm.biomes | Building (15) | - | 0.4~0.8 | 0.8 | 1 | - | - | RM_LanternDeeps | a sown lanternstone, already on Building |
| `RM_Luqqim` | luqqim | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.8 | 0.8 | 1 | - | - | RM_FloodedCanyon | desc: clusters of tulip cups |
| `RM_Maddrick` | maddrick | mandrake.rm.biomes | LowPlant (11) | - | 2~3 | 3.0 | 1 | - | - | RM_Greentide | mature 3.00 cells > 1.2 |
| `RM_Maidenbloom` | maidenbloom | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | - | - | RM_LongShade | desc: flowers |
| `RM_Maulith` | maulith | mandrake.rm.biomes | LowPlant (11) | - | 1.3~1.9 | 1.9 | 1 | - | - | RM_FeverWood | mature 1.90 cells > 1.2 |
| `RM_Meatvine` | meatvine | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1.1 | 1.1 | 4 | - | - | RM_Contagion | desc: vine |
| `RM_Milkwell` | milkwell | mandrake.rm.biomes | LowPlant (11) | - | 1~1.3 | 1.3 | 1 | - | - | RM_GreySea | mature 1.30 cells > 1.2 |
| `RM_Mirrelbole` | mirrelbole | mandrake.rm.biomes | Building (15) | - | 3~4 | 4.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Mirrelin` | mirrelin | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_TheSump | mature 1.30 cells > 1.2 |
| `RM_MortalMorelPlant` | yullcomb | mandrake.rm.biomes | LowPlant (11) | - | 0.48~0.8 | 0.8 | 4 | - | - | RM_TheRot, RUT_TheRot | desc: mushroom |
| `RM_MosaicFanPalm` | mosaic fan palm | mandrake.rm.biomes | LowPlant (11) | 1.3x1.3 | 0.8~1.4 | 1.82 | 1 | - | - | RM_GreySea | mature 1.82 cells > 1.2 |
| `RM_Mournweft` | mournweft | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.2 | 1.2 | 1 | - | - | RM_GreySea | desc: a waist-high loom |
| `RM_Mourvel` | mourvel | mandrake.rm.biomes | Building (15) | - | 6~8 | 8.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Murkspindle` | murkspindle | mandrake.rm.biomes | LowPlant (11) | 0.8x0.8 | 0.7~1 | 0.8 | 1 | - | - | RM_TwilightSea | desc: Upright |
| `RM_Nabbuq` | nabbuq | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | Ground | - | RM_FloodedCanyon | sown crop |
| `RM_Nemmer` | nemmer | mandrake.rm.biomes | Building (15) | - | 3.5~5 | 5.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Neverset` | neverset | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.6 | 0.6 | 1 | - | - | RM_GreySea | desc: a small sprig |
| `RM_Nogtyl` | brommok timber | mandrake.rm.biomes | Building (15) | - | 7.2~12 | 12.0 | 1 | Ground | yes | RM_Miasma, RUT_Miasma | tree |
| `RM_NoothelmPlant` | noothelm | mandrake.rm.biomes | LowPlant (11) | 1.2x1.2 | 0.8~1.2 | 1.44 | 1 | - | - | RM_TwilightSea | mature 1.44 cells > 1.2 |
| `RM_Norrveth` | norrveth | mandrake.rm.biomes | LowPlant (11) | - | 2~2.8 | 2.8 | 1 | - | - | RM_Webwork | mature 2.80 cells > 1.2 |
| `RM_Nubrith` | nubrith | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1 | 1.0 | 1 | - | - | RM_FeverWood | desc: stalk |
| `RM_Nuitae` | nissik gill | mandrake.rm.biomes | LowPlant (11) | - | 0.67~1 | 1.0 | 1 | - | - | RM_TheRot, RUT_TheRot | desc: cap |
| `RM_NurrikGill` | nurrik gill | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.6 | 0.6 | 1 | - | - | RM_LanternDeeps | desc: cap |
| `RM_Nyssolet` | nyssolet | mandrake.rm.biomes | LowPlant (11) | 0.8 | 0.5~0.8 | 0.64 | 1 | - | - | RM_Miasma | desc: flower |
| `RM_Ollamane` | ollamane | mandrake.rm.biomes | Building (15) | - | 2~3.6 | 3.6 | 1 | Ground | yes | RM_Miasma | tree |
| `RM_Ollim` | ollim | mandrake.rm.biomes | Building (15) | - | 3.5~5.5 | 5.5 | 1 | Ground | yes | RM_Stillsand, RUT_ExtremeDesert | tree |
| `RM_Ommolyn` | ommolyn | mandrake.rm.biomes | LowPlant (11) | 0.6 | 0.4~0.7 | 0.42 | 1 | - | - | RM_Miasma | desc: flower |
| `RM_Ossagrel` | ossagrel | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.4 | 1.4 | 1 | - | - | RM_FeverWood | mature 1.40 cells > 1.2 |
| `RM_PaddleVine` | paddle vine | mandrake.rm.biomes | LowPlant (11) | - | 0.3~1.05 | 1.05 | 1 | Ground | - | RM_Abyss, RUT_Abyss | sown crop |
| `RM_PaleTree` | quellan tree | mandrake.rm.biomes | Building (15) | - | 4.32~6 | 6.0 | 1 | - | yes | RM_TheRot | tree |
| `RM_Pallick` | pallick | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_TheSump | mature 1.30 cells > 1.2 |
| `RM_Pavecrust` | pavecrust | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.4 | 1.4 | 1 | - | - | RM_LongShade | mature 1.40 cells > 1.2 |
| `RM_Pellareth` | pellareth | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.8 | 0.8 | 1 | - | - | RM_Webwork | desc: flowers |
| `RM_Phorrik` | phorrik | mandrake.rm.biomes | LowPlant (11) | - | 2~3 | 3.0 | 1 | - | - | RM_Greentide | mature 3.00 cells > 1.2 |
| `RM_Pitchpearl` | pitchpearl | mandrake.rm.biomes | LowPlant (11) | 0.9 | 0.7~1 | 0.9 | 1 | RM_ChillBed | - | RM_TheChill | sown crop |
| `RM_Plant_Bellows` | bellows | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.1 | 1.1 | 1 | - | - | RM_GelatinousSlime | desc: a knee-high sac |
| `RM_Plant_Readerbloom` | readerbloom | mandrake.rm.biomes | LowPlant (11) | 1.2 | 0.6~0.9 | 1.08 | 1 | - | - | RM_GelatinousSlime | desc: stalk |
| `RM_Plant_Thumbstalk` | thumbstalk | mandrake.rm.biomes | LowPlant (11) | 1.4 | 1~1.5 | 2.1 | 1 | - | yes | RM_GelatinousSlime | tree |
| `RM_PrennaLace` | prenna lace | mandrake.rm.biomes | LowPlant (11) | - | 0.4~1 | 1.0 | 1 | Ground | - | RM_LanternDeeps | sown crop |
| `RM_Pusberry` | pusberry | mandrake.rm.biomes | Building (15) | - | 0.8~1.6 | 1.6 | 1 | Ground | yes | RM_Wastes | tree |
| `RM_Pusmelon` | gubbra gourd | mandrake.rm.biomes | LowPlant (11) | - | 0.43~1 | 1.0 | 4 | - | - | RM_TheRot, RUT_TheRot | desc: a gourd-shaped fungus |
| `RM_Quathis` | quathis | mandrake.rm.biomes | Building (15) | - | 2.5~4 | 4.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_QuenchVenomvine` | quench venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_Quennath` | quennath | mandrake.rm.biomes | Building (15) | - | 1~1.8 | 1.8 | 1 | Ground | yes | RM_Miasma | tree |
| `RM_QuorrFern` | quorr fern | mandrake.rm.biomes | LowPlant (11) | 1.15 | 0.7~1.1 | 1.265 | 1 | - | - | RM_LanternDeeps | mature 1.26 cells > 1.2 |
| `RM_Rattlegrope` | rattlegrope | mandrake.rm.biomes | Building (15) | - | 1.6~2.1 | 2.1 | 1 | - | - | RM_Contagion | mature 2.10 cells > 1.2 |
| `RM_RavenNettle` | raven nettle | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.3 | 1.3 | 4 | - | - | RM_Cauldron | mature 1.30 cells > 1.2 |
| `RM_RearingVenomvine` | rearing venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_RedBugloss` | red bugloss | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.3 | 1.3 | 4 | - | - | RM_Cauldron | mature 1.30 cells > 1.2 |
| `RM_RegenerantVeil` | mirrash veil | mandrake.rm.biomes | LowPlant (11) | - | 1~1.3 | 1.3 | 1 | - | - | RM_TheRot | mature 1.30 cells > 1.2 |
| `RM_Rockfinger` | rockfinger | mandrake.rm.biomes | Building (15) | - | 2.25~4.8 | 4.8 | 1 | Ground | yes | RM_WeepingStones | tree |
| `RM_Ruddreth` | ruddreth | mandrake.rm.biomes | LowPlant (11) | - | 0.6~0.9 | 0.9 | 1 | - | - | RM_Webwork | desc: blooms |
| `RM_Ruqqal` | ruqqal | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1.1 | 1.1 | 1 | Ground | - | RM_FloodedCanyon | sown crop |
| `RM_RustPuff` | rustpuff | mandrake.rm.biomes | LowPlant (11) | - | 0.25~0.6 | 0.6 | 4 | - | - | RM_Contagion, RUT_Contagion | desc: puffball |
| `RM_SaltBladeGrey` | salt-rimed blade | mandrake.rm.biomes | LowPlant (11) | 1.4x1.4 | 1.1~1.8 | 2.52 | 1 | - | - | RM_GreySea | mature 2.52 cells > 1.2 |
| `RM_SaltBladeTwilight` | salt-rimed blade | mandrake.rm.biomes | LowPlant (11) | 1.4x1.4 | 1.1~1.8 | 2.52 | 1 | - | - | RM_GreySea | mature 2.52 cells > 1.2 |
| `RM_SaltChimneyVine` | salt chimney vine | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1.2 | 1.2 | 1 | - | - | RM_GreySea | name: Vine |
| `RM_Saltswoon` | saltswoon | mandrake.rm.biomes | LowPlant (11) | - | 0.7~0.95 | 0.95 | 1 | - | - | RM_GreySea | desc: stalk |
| `RM_Salvecomb` | salvecomb | mandrake.rm.biomes | LowPlant (11) | - | 0.4~0.7 | 0.7 | 1 | - | - | RM_WeepingStones | desc: one waist-high arched frond |
| `RM_Sapblister` | sapblister | mandrake.rm.biomes | Building (15) | - | 2~2.6 | 2.6 | 1 | - | - | RM_Contagion | mature 2.60 cells > 1.2 |
| `RM_Sarnstilt` | sarnstilt | mandrake.rm.biomes | Building (15) | - | 5~7 | 7.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Sarquin` | sarquin | mandrake.rm.biomes | LowPlant (11) | - | 2.5~4 | 4.0 | 1 | - | - | RM_Greentide | mature 4.00 cells > 1.2 |
| `RM_Sarrash` | sarrash | mandrake.rm.biomes | LowPlant (11) | 1 | 0.7~1.2 | 1.2 | 1 | - | - | RM_Miasma | desc: plumes |
| `RM_ScorchedStars` | scorched stars | mandrake.rm.biomes | LowPlant (11) | 1.15 | 0.7~1.1 | 1.265 | 1 | - | - | RM_Warscar | mature 1.26 cells > 1.2 |
| `RM_Seepcandle` | seepcandle | mandrake.rm.biomes | LowPlant (11) | 1x1 | 0.8~1.1 | 1.1 | 1 | - | - | RM_TheScald | desc: a dripstone candle |
| `RM_Seepril` | seepril | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1 | 1.0 | 1 | - | - | RM_FeverWood | desc: a barrel of a stem |
| `RM_Sellith` | sellith | mandrake.rm.biomes | LowPlant (11) | - | 0.7~1 | 1.0 | 1 | - | - | RM_Webwork | desc: hanging fringes under the lines |
| `RM_Sevvuq` | sevvuq | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | - | - | RM_FloodedCanyon | desc: skull-sized globes |
| `RM_Shadefern` | shadefern | mandrake.rm.biomes | LowPlant (11) | - | 0.3~0.7 | 0.7 | 1 | - | - | RM_WeepingStones | desc: fern |
| `RM_Shadespire` | shadespire | mandrake.rm.biomes | Building (15) | - | 2~3 | 3.0 | 1 | Ground | yes | RM_LongShade | tree |
| `RM_SheddingVenomvine` | shedding venomvine | mandrake.rm.biomes | LowPlant (11) | - | 1~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_Shinecap` | dremmik cap | mandrake.rm.biomes | Building (15) | - | 1.8~3 | 3.0 | 1 | Ground | yes | RM_TheRot, RUT_TheRot | tree |
| `RM_SicklyGlowMushroom` | sickly glow mushroom | mandrake.rm.biomes | Building (15) | - | 2~2.8 | 2.8 | 1 | Ground | yes | RM_Abyss, RUT_Abyss | tree |
| `RM_Skulltop` | vekkra choker | mandrake.rm.biomes | Building (15) | - | 0.3~0.7 | 0.7 | 1 | Ground | yes | RM_TheRot, RUT_TheRot | tree |
| `RM_Skyharp` | skyharp | mandrake.rm.biomes | LowPlant (11) | 1.2 | 0.7~1.1 | 1.32 | 1 | - | - | RM_TheChill | mature 1.32 cells > 1.2 |
| `RM_Slackwax` | slackwax | mandrake.rm.biomes | LowPlant (11) | 1.35 | 0.7~1.1 | 1.485 | 1 | - | - | RM_TheChill | mature 1.49 cells > 1.2 |
| `RM_SleeperVenomvine` | dead venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_Sodderel` | sodderel | mandrake.rm.biomes | LowPlant (11) | - | 1.4~2 | 2.0 | 1 | - | yes | RM_FeverWood | tree |
| `RM_Soffeth` | soffeth | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.85 | 0.85 | 1 | - | - | RM_TheSump | desc: stalks |
| `RM_Sorrivel` | sorrivel | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.2 | 1.2 | 1 | - | - | RM_Webwork | desc: flower |
| `RM_SpherePlant` | sphere plant | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.9 | 0.9 | 1 | - | - | RM_GreySea | desc: a helmet-sized sphere held clear on spines |
| `RM_Stonewater` | stonewater | mandrake.rm.biomes | LowPlant (11) | 1.35 | 0.9~1.3 | 1.755 | 1 | RM_ChillBed | - | RM_TheChill | sown crop |
| `RM_SwornVenomvine` | sworn venomvine | mandrake.rm.biomes | LowPlant (11) | - | 1~1.1 | 1.1 | 1 | Ground | - | RM_LeaningScrub | sown crop |
| `RM_TallScumgrass` | tall scumgrass | mandrake.rm.biomes | LowPlant (11) | 1.3 | 0.7~1.1 | 1.43 | 4 | - | - | RM_Wastes | mature 1.43 cells > 1.2 |
| `RM_Tanglefuzz` | tanglefuzz | mandrake.rm.biomes | LowPlant (11) | - | 1~1.3 | 1.3 | 4 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_Tarspool` | tarspool | mandrake.rm.biomes | LowPlant (11) | 1 | 0.8~1.1 | 1.1 | 1 | RM_ChillBed | - | RM_TheChill | sown crop |
| `RM_Tavrosk` | tavrosk | mandrake.rm.biomes | LowPlant (11) | - | 1.6~2.2 | 2.2 | 1 | - | - | RM_Webwork | mature 2.20 cells > 1.2 |
| `RM_Thalquith` | thalquith | mandrake.rm.biomes | Building (15) | - | 2.5~4 | 4.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_Thessamor` | thessamor | mandrake.rm.biomes | Building (15) | - | 1.8~3.4 | 3.4 | 1 | Ground | yes | RM_Miasma | tree |
| `RM_ThrakkCap` | thrakk cap | mandrake.rm.biomes | Building (15) | - | 1.5~2 | 2.0 | 1 | Ground | yes | RM_LanternDeeps | tree |
| `RM_Thrannock` | thrannock | mandrake.rm.biomes | LowPlant (11) | 1.3 | 1.2~2 | 2.6 | 1 | - | - | RM_Miasma | mature 2.60 cells > 1.2 |
| `RM_Threshreed` | threshreed | mandrake.rm.biomes | LowPlant (11) | 0.8x0.8 | 0.6~0.9 | 0.72 | 1 | - | - | RM_TheScald | desc: stands |
| `RM_Thulvane` | thulvane | mandrake.rm.biomes | LowPlant (11) | - | 2.6~3.5 | 3.5 | 1 | - | - | RM_FeverWood | mature 3.50 cells > 1.2 |
| `RM_Thurlsponge` | thurlsponge | mandrake.rm.biomes | LowPlant (11) | 1.1x1.1 | 0.9~1.3 | 1.43 | 1 | - | - | RM_TheScald | mature 1.43 cells > 1.2 |
| `RM_Tolleth` | tolleth | mandrake.rm.biomes | LowPlant (11) | - | 0.55~0.9 | 0.9 | 1 | - | - | RM_TheSump | desc: stem |
| `RM_TollukCap` | aumbri | mandrake.rm.biomes | LowPlant (11) | - | 0.5~1.1 | 1.1 | 4 | - | - | RM_TheRot, RUT_TheRot | name: Cap |
| `RM_TreeMartyr` | sarrowan | mandrake.rm.biomes | Building (15) | - | 1.3~3 | 3.0 | 1 | Ground | yes | RM_Cauldron | tree |
| `RM_TreeMushroom` | tree mushroom | mandrake.rm.biomes | Building (15) | - | 8~15.2 | 15.2 | 1 | Ground | yes | RM_Abyss, RUT_Abyss | tree |
| `RM_Tumbel` | tumbel | mandrake.rm.biomes | LowPlant (11) | - | 3~5 | 5.0 | 1 | - | - | RM_Greentide | mature 5.00 cells > 1.2 |
| `RM_TwistingThornweed` | twisting thornweed | mandrake.rm.biomes | LowPlant (11) | 1.15 | 0.7~1.1 | 1.265 | 1 | - | - | RM_FloodedCanyon, RUT_CrackedLands | mature 1.26 cells > 1.2 |
| `RM_TwistingThornwood` | twisting thornwood | mandrake.rm.biomes | Building (15) | - | 1.3~3 | 3.0 | 1 | Ground | yes | RM_Cauldron, RUT_Cauldron | tree |
| `RM_TwitcherVenomvine` | twitcher venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub | mature 1.30 cells > 1.2 |
| `RM_TwitchingPuffer` | twitching puffer | mandrake.rm.biomes | LowPlant (11) | - | 0.5~1.3 | 1.3 | 1 | Ground | - | RM_LanternDeeps | sown crop |
| `RM_Ullavess` | ullavess | mandrake.rm.biomes | LowPlant (11) | 1.1 | 0.8~1.3 | 1.43 | 1 | - | - | RM_Miasma | mature 1.43 cells > 1.2 |
| `RM_Varnoth` | varnoth | mandrake.rm.biomes | LowPlant (11) | - | 1.8~2.5 | 2.5 | 1 | - | yes | RM_FeverWood | tree |
| `RM_Varrisk` | varrisk | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_Webwork | mature 1.30 cells > 1.2 |
| `RM_Vashpuk` | vashpuk | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.1 | 1.1 | 1 | - | - | RM_BlueDesert | desc: a squat waist-high bladder |
| `RM_VaultRoot` | vault-root tree | mandrake.rm.biomes | Building (15) | 2 | 2.4~5.2 | 10.4 | 1 | Ground | yes | RM_Wastes | tree |
| `RM_Vekkfan` | vekkfan | mandrake.rm.biomes | LowPlant (11) | 1.8x1.8 | 1.4~2 | 3.6 | 1 | - | - | RM_TheScald | mature 3.60 cells > 1.2 |
| `RM_Velloch` | velloch | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_TheSump | mature 1.30 cells > 1.2 |
| `RM_VellokReed` | vellok reed | mandrake.rm.biomes | Building (15) | - | 1.5~2.5 | 2.5 | 1 | - | yes | RM_LanternDeeps | tree |
| `RM_Velluric` | velluric | mandrake.rm.biomes | LowPlant (11) | 0.7 | 0.4~0.7 | 0.49 | 1 | - | - | RM_Miasma | desc: flower |
| `RM_Veluthar` | veluthar | mandrake.rm.biomes | Building (15) | - | 7.5~10 | 10.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_VenomvineThicket` | venomvine thicket | mandrake.rm.biomes | LowPlant (11) | - | 0.9~1.3 | 1.3 | 1 | - | - | RM_LeaningScrub, RUT_AridShrubland | mature 1.30 cells > 1.2 |
| `RM_Veqma` | veqma | mandrake.rm.biomes | LowPlant (11) | - | 0.35~0.6 | 0.6 | 1 | - | - | RM_FloodedCanyon | desc: stems |
| `RM_Verrow` | verrow | mandrake.rm.biomes | LowPlant (11) | - | 1.1~1.6 | 1.6 | 1 | - | - | RM_FeverWood | mature 1.60 cells > 1.2 |
| `RM_Vessark` | vessark | mandrake.rm.biomes | LowPlant (11) | - | 1.4~2 | 2.0 | 1 | - | - | RM_Webwork | mature 2.00 cells > 1.2 |
| `RM_VioletWimple` | pursk hood | mandrake.rm.biomes | LowPlant (11) | - | 0.43~1 | 1.0 | 4 | - | - | RM_TheRot, RUT_TheRot | desc: capped |
| `RM_Virr` | virr | mandrake.rm.biomes | LowPlant (11) | - | 0.65~1 | 1.0 | 1 | - | - | RM_BlueDesert | desc: a hand-high branching tube |
| `RM_Vorrel` | vorrel | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.8 | 0.8 | 4 | - | - | RM_LongShade | desc: bush |
| `RM_Vurmeloth` | vurmeloth | mandrake.rm.biomes | Building (15) | - | 3.5~5 | 5.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_WalkingVenomvine` | walking venomvine | mandrake.rm.biomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RM_LeaningScrub | desc: man-high cane at the tail |
| `RM_Wartshrub` | wartshrub | mandrake.rm.biomes | LowPlant (11) | 1 | 0.7~1.1 | 1.1 | 1 | - | - | RM_Wastes | desc: shrub |
| `RM_WastesScorchedStars` | scorched stars | mandrake.rm.biomes | LowPlant (11) | 1.15 | 0.7~1.1 | 1.265 | 1 | - | - | RM_Wastes | mature 1.26 cells > 1.2 |
| `RM_Weircomb` | weircomb | mandrake.rm.biomes | LowPlant (11) | 1x1 | 0.8~1.1 | 1.1 | 1 | - | - | RM_TwilightSea | desc: upright |
| `RM_Wickwood` | wickwood tree | mandrake.rm.biomes | Building (15) | - | 2.6~3.6 | 3.6 | 1 | Ground | yes | RM_Abyss | tree |
| `RM_WildHealroot` | wild healroot | mandrake.rm.biomes | LowPlant (11) | - | 0.3~0.8 | 0.8 | 1 | - | - | RM_LeaningScrub | healroot habit: an upright herb |
| `RM_Wollick` | wollick | mandrake.rm.biomes | LowPlant (11) | - | 2.5~4 | 4.0 | 1 | - | - | RM_Greentide | mature 4.00 cells > 1.2 |
| `RM_Wombpod` | wombpod | mandrake.rm.biomes | LowPlant (11) | - | 0.5~0.8 | 0.8 | 1 | - | - | RM_Contagion | desc: pods |
| `RM_Wrinklecap` | rukka cap | mandrake.rm.biomes | LowPlant (11) | - | 0.74~0.9 | 0.9 | 4 | - | - | RM_TheRot, RUT_TheRot | name: cap |
| `RM_Xithess` | xithess | mandrake.rm.biomes | LowPlant (11) | - | 1~1.3 | 1.3 | 1 | - | - | RM_Cauldron | mature 1.30 cells > 1.2 |
| `RM_YearningFruit` | yearning fruit | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1 | 1.0 | 4 | - | - | RM_Greentide | desc: a heavy-fruiting bush |
| `RM_Zennaq` | zennaq | mandrake.rm.biomes | LowPlant (11) | - | 0.6~1.1 | 1.1 | 1 | - | - | RM_FloodedCanyon | desc: stands |
| `RM_Zhorrel` | zhorrel | mandrake.rm.biomes | Building (15) | - | 3.5~5 | 5.0 | 1 | Ground | yes | RM_Greentide | tree |
| `RM_ZivvitTaper` | zivvit taper | mandrake.rm.biomes | LowPlant (11) | 2x2 | 0.2~0.4 | 0.8 | 4 | - | - | RM_LanternDeeps | desc: mushroom |
| `RSW_Plant_Bloddle` | bloddle plant | mandrake.rsw.swbestiary | LowPlant (11) | - | 0.3~0.6 | 0.6 | 16 | Ground,Hydroponic | - | RUT_ExtremeDesert | sown crop |
| `RSW_Plant_Chakroot_Wild` | wild chak-root plant | mandrake.rsw.swbestiary | LowPlant (11) | - | 0.5~1.5 | 1.5 | 1 | - | - | RUT_Desert | mature 1.50 cells > 1.2 |
| `RSW_Plant_HubbaGourd_Wild` | wild hubba gourd plant | mandrake.rsw.swbestiary | LowPlant (11) | - | 0.5~1 | 1.0 | 1 | - | - | RUT_Desert | a gourd crop plant |
| `RSW_VellaraBloom` | vellara bloom | mandrake.rsw.swbestiary | LowPlant (11) | 1.5 | 0.7~1 | 1.5 | 1 | - | - | RUT_Desert | mature 1.50 cells > 1.2 |
| `RUT_Grellbush` | grellbush | mandrake.rut.ashkarrflora | LowPlant (11) | - | 0.4~0.8 | 0.8 | 1 | - | - | RUT_AridShrubland | desc: shrub |
| `RUT_Grellspine` | grellspine | mandrake.rut.ashkarrflora | LowPlant (11) | - | 0.7~0.85 | 0.85 | 4 | - | - | RUT_AridShrubland | desc: shrub |
| `RUT_WildHealroot` | wild healroot | mandrake.rut.ashkarrflora | LowPlant (11) | - | 0.3~0.8 | 0.8 | 1 | - | - | RUT_AridShrubland | healroot habit: an upright herb |
| `RUT_FireLavender` | fire lavender | mandrake.rut.patches | LowPlant (11) | - | 0.5~0.9 | 0.9 | 4 | Ground | - | RUT_TheForge | sown crop |
| `RUT_GiantLeaf` | giant leaf | mandrake.rut.patches | LowPlant (11) | - | 0.5~1.3 | 1.3 | 9 | Ground | - | RUT_FeverWood, RUT_Greentide | sown crop |
| `RUT_HeatsinkFungus` | heatsink fungus | mandrake.rut.patches | Building (15) | - | 0.3~0.7 | 0.7 | 1 | Ground | yes | RUT_TheForge | tree |
| `RUT_ScorchedStars` | scorched stars | mandrake.rut.patches | LowPlant (11) | 1.15 | 0.7~1.1 | 1.265 | 1 | - | - | RUT_Scarlands, RUT_Wastes | mature 1.26 cells > 1.2 |
| `RUT_TreeMartyr` | martyr tree | mandrake.rut.patches | Building (15) | - | 1.3~3 | 3.0 | 1 | Ground | yes | RUT_Cauldron | tree |
| `RUT_VaultRoot` | vault-root tree | mandrake.rut.patches | Building (15) | - | 1.2~2.6 | 2.6 | 1 | Ground | yes | RUT_Wastes | tree |
| `PoisonShrub` | poison shrub | mlie.advancedbiomes | LowPlant (11) | 1.15 | 0.7~1.1 | 1.265 | 1 | - | - | RUT_FuelSnows, RUT_Umbra | mature 1.26 cells > 1.2 |
| `Plant_Chakroot_Wild` | wild chak-root plant | mlie.starwarsanimalcollection | LowPlant (11) | - | 0.5~1.5 | 1.5 | 1 | - | - | RUT_FeverWood, RUT_Greentide | mature 1.50 cells > 1.2 |
| `Plant_FelucianGlowspore_Wild` | wild felucian glowspore | mlie.starwarsanimalcollection | Building (15) | - | 1~3 | 3.0 | 1 | - | yes | RUT_Greentide | tree |
| `Plant_HubbaGourd_Wild` | wild hubba gourd plant | mlie.starwarsanimalcollection | LowPlant (11) | - | 0.5~1 | 1.0 | 1 | - | - | RUT_Greentide | a gourd crop plant |
| `Plant_HydenockTree_Wild` | wild hydenock tree | mlie.starwarsanimalcollection | Building (15) | - | 1~2 | 2.0 | 1 | - | yes | RUT_FeverWood, RUT_Greentide | tree |
| `Plant_JoganTree_Wild` | wild jogan tree | mlie.starwarsanimalcollection | Building (15) | - | 1~2 | 2.0 | 1 | - | yes | RUT_FeverWood, RUT_Greentide | tree |
| `Plant_MujaFruit_Wild` | wild muja fruit bush | mlie.starwarsanimalcollection | LowPlant (11) | - | 0.7~1.5 | 1.5 | 1 | - | - | RUT_Greentide | mature 1.50 cells > 1.2 |
| `Plant_Nysyllin_Wild` | wild nysyllin plant | mlie.starwarsanimalcollection | LowPlant (11) | - | 0.7~1.3 | 1.3 | 9 | - | - | RM_LeaningScrub, RUT_AridShrubland | mature 1.30 cells > 1.2 |
| `Plant_TookeTrap_Wild` | wild tooke-trap plant | mlie.starwarsanimalcollection | LowPlant (11) | - | 0.3~1 | 1.0 | 1 | - | - | RUT_Greentide, RUT_Webwork | a carnivorous flowering plant |
| `Plant_Brambles` |  | regrowth.botr.core | LowPlant (11) | 1.7 | 0.7~0.85 | 1.445 | 4 | - | - | RM_LeaningScrub, RUT_AridShrubland | mature 1.45 cells > 1.2 |
| `RG_Plant_CreepStern` | creep stern | regrowth.botr.core | LowPlant (11) | - | 0.8~1.3 | 1.3 | 4 | - | - | RM_LeaningScrub, RUT_AridShrubland | mature 1.30 cells > 1.2 |
| `RG_Plant_Dervish` | dervish | regrowth.botr.core | LowPlant (11) | - | 0.3~0.5 | 0.5 | 16 | Ground | - | RM_LeaningScrub, RUT_AridShrubland | sown crop |
| `RG_Plant_TropicalChokevine` | chokevine | regrowth.botr.core | LowPlant (11) | 2.25 | 0.78~0.88 | 1.98 | 4 | - | - | RUT_Webwork | mature 1.98 cells > 1.2 |
| `AB_Aaklac` | aaklac | sarg.alphabiomes | LowPlant (11) | 1.5 | 0.7~1.1 | 1.65 | 1 | - | - | RUT_Webwork | mature 1.65 cells > 1.2 |
| `AB_AgaricusDomeCap` | skarrowdome | sarg.alphabiomes | LowPlant (11) | - | 5.25~7 | 7.0 | 1 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `AB_AgariluxPrime` | grath elder | sarg.alphabiomes | Skyfaller (30) | - | 19.88~20 | 20.0 | 1 | - | - | RM_TheRot, RUT_TheRot | mature 20.00 cells > 1.2 |
| `AB_AlienTree` | ocular tree | sarg.alphabiomes | Building (15) | - | 3~3.75 | 3.75 | 1 | Ground | yes | RUT_Contagion | tree |
| `AB_AlienTree_Polluted` | mutated ocular tree | sarg.alphabiomes | Building (15) | - | 3~3.75 | 3.75 | 1 | Ground | yes | RUT_Contagion | tree |
| `AB_ArbuscularMycorrhiza` | madruka | sarg.alphabiomes | BuildingOnTop (17) | - | 5.14~9 | 9.0 | 1 | Ground | yes | RM_TheRot, RUT_TheRot | tree |
| `AB_BloodBouquet` | blood bouquet | sarg.alphabiomes | Building (15) | - | 2~2.5 | 2.5 | 1 | - | - | RUT_Cauldron, RUT_Contagion | mature 2.50 cells > 1.2 |
| `AB_CrystalFlower` | crystal flower | sarg.alphabiomes | LowPlant (11) | - | 3~3.5 | 3.5 | 1 | - | - | RUT_Cauldron | mature 3.50 cells > 1.2 |
| `AB_CrystalHorn` | crystal horn | sarg.alphabiomes | LowPlant (11) | - | 0.8~1.2 | 1.2 | 1 | - | - | RUT_BlueDesert, RUT_FuelSnows, RUT_Umbra | desc: flower |
| `AB_DribblingCap` | amber weeper | sarg.alphabiomes | BuildingOnTop (17) | - | 8.4~12 | 12.0 | 1 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `AB_FirevineTree` | firevine tree | sarg.alphabiomes | BuildingOnTop (17) | - | 2.8~3.8 | 3.8 | 1 | Ground | yes | RM_TheForge, RUT_TheForge | tree |
| `AB_GiantAgariTox` | agaritox | sarg.alphabiomes | BuildingOnTop (17) | - | 3~5 | 5.0 | 1 | Ground | yes | RUT_Cauldron | tree |
| `AB_GiantAgarilux` | vokkun pillar | sarg.alphabiomes | BuildingOnTop (17) | - | 3.5~6 | 6.0 | 1 | Ground | yes | RM_TheRot, RUT_TheRot | tree |
| `AB_GiantToxicFlower` | giant toxic flower | sarg.alphabiomes | Building (15) | - | 2.8~3.8 | 3.8 | 1 | Ground | yes | RUT_Cauldron | tree |
| `AB_GlobularPlant` | globular aberration | sarg.alphabiomes | Building (15) | - | 2.3~3 | 3.0 | 1 | - | - | RUT_Contagion | mature 3.00 cells > 1.2 |
| `AB_GlowingAgarilux` | ithrani glowcap | sarg.alphabiomes | Building (15) | - | 2.6~4 | 4.0 | 1 | - | - | RM_TheRot, RUT_TheRot | mature 4.00 cells > 1.2 |
| `AB_Glowstool` | nubbik | sarg.alphabiomes | LowPlant (11) | - | 0.4~0.7 | 0.7 | 4 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `AB_Gomphoeria` | gomphoeria | sarg.alphabiomes | LowPlant (11) | - | 1.5~2 | 2.0 | 1 | - | - | RUT_FeverWood, RUT_Webwork | mature 2.00 cells > 1.2 |
| `AB_GreenRockFern` | green rock fern | sarg.alphabiomes | LowPlant (11) | - | 1~1.5 | 1.5 | 1 | - | - | RUT_WeepingStones | mature 1.50 cells > 1.2 |
| `AB_HalfAlienTree` | half transformed ocular tree | sarg.alphabiomes | Building (15) | - | 2.3~3 | 3.0 | 1 | - | yes | RUT_Contagion | tree |
| `AB_Iashiphus` | iashiphus | sarg.alphabiomes | LowPlant (11) | - | 1.5~2 | 2.0 | 1 | - | - | RUT_FeverWood | mature 2.00 cells > 1.2 |
| `AB_JungleTree` | deep jungle tree | sarg.alphabiomes | BuildingOnTop (17) | - | 2.8~3.8 | 3.8 | 1 | Ground | yes | RUT_Greentide, RUT_Webwork | tree |
| `AB_KeeningCordax` | keening cordax | sarg.alphabiomes | BuildingOnTop (17) | - | 1~2 | 2.0 | 1 | Ground | yes | RUT_Cauldron, RUT_FeverWood | tree |
| `AB_LargeSlimyTree` | large slimy tree | sarg.alphabiomes | BuildingOnTop (17) | - | 2.8~3.8 | 3.8 | 1 | Ground | - | RUT_Slime | sown crop |
| `AB_LilacBeacon` | quessa spire | sarg.alphabiomes | LowPlant (11) | - | 1.5~3 | 3.0 | 1 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `AB_MangrovePalm` | mangrove palm | sarg.alphabiomes | BuildingOnTop (17) | - | 1.8~2.5 | 2.5 | 1 | Ground | yes | RUT_Miasma | tree |
| `AB_MangroveTree` | mangrove tree | sarg.alphabiomes | BuildingOnTop (17) | - | 2.8~3.8 | 3.8 | 1 | Ground | yes | RUT_Miasma | tree |
| `AB_ParasiticMangrove` | parasitic mangrove | sarg.alphabiomes | LowPlant (11) | - | 1~2 | 2.0 | 1 | - | - | RUT_Miasma | mature 2.00 cells > 1.2 |
| `AB_RavenNettle` | raven nettle | sarg.alphabiomes | LowPlant (11) | 1.7 | 0.7~0.85 | 1.445 | 4 | - | - | RUT_Cauldron | mature 1.45 cells > 1.2 |
| `AB_RecurvedStropharia` | orrusk crook | sarg.alphabiomes | BuildingOnTop (17) | - | 3.5~5 | 5.0 | 1 | Ground | yes | RM_TheRot, RUT_TheRot | tree |
| `AB_RedBugloss` | red bugloss | sarg.alphabiomes | LowPlant (11) | - | 1.5~2 | 2.0 | 1 | - | - | RUT_Cauldron, RUT_Webwork | mature 2.00 cells > 1.2 |
| `AB_RedPlantsTall` | ocular plant | sarg.alphabiomes | LowPlant (11) | - | 0.7~1.2 | 1.2 | 1 | - | - | RUT_Contagion | name: Tall |
| `AB_Slimecasia` | slimecasia | sarg.alphabiomes | LowPlant (11) | 2 | 0.7~1.1 | 2.2 | 1 | - | - | RUT_Slime | mature 2.20 cells > 1.2 |
| `AB_SlimyFern` | slimy fern | sarg.alphabiomes | LowPlant (11) | 2 | 0.7~1.1 | 2.2 | 1 | - | - | RUT_Slime | mature 2.20 cells > 1.2 |
| `AB_SlimyPholiota` | sweetsnare | sarg.alphabiomes | BuildingOnTop (17) | - | 3.5~5 | 5.0 | 1 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `AB_SlimyTree` | slimy tree | sarg.alphabiomes | BuildingOnTop (17) | - | 2~2.8 | 2.8 | 1 | Ground | - | RUT_Slime | sown crop |
| `AB_SugarFamewort` | sugar famewort | sarg.alphabiomes | LowPlant (11) | - | 1.5~2 | 2.0 | 1 | - | - | RUT_Greentide | mature 2.00 cells > 1.2 |
| `AB_TangleTea` | tangle tea | sarg.alphabiomes | LowPlant (11) | - | 0.75~1 | 1.0 | 1 | - | - | RUT_Webwork | desc: flowers |
| `AB_TarPuddle` | tar puddle | sarg.alphabiomes | Skyfaller (30) | - | 1~1.3 | 1.3 | 1 | - | - | RUT_Sump | mature 1.30 cells > 1.2 |
| `AB_TentacularPlant` | tentacular aberration | sarg.alphabiomes | Building (15) | - | 2.3~3 | 3.0 | 1 | - | - | RUT_Contagion | mature 3.00 cells > 1.2 |
| `AB_ToxiBulb` | toxibulb | sarg.alphabiomes | Building (15) | - | 2~2.8 | 2.8 | 1 | Ground | yes | RUT_Wastes | tree |
| `AB_WeepingToxberry` | weeping toxberry | sarg.alphabiomes | LowPlant (11) | - | 1.5~2 | 2.0 | 4 | - | - | RUT_Wastes | mature 2.00 cells > 1.2 |
| `AB_WitchesOyster` | Tumrata's shelf | sarg.alphabiomes | LowPlant (11) | - | 3~6 | 6.0 | 1 | Ground | - | RM_TheRot, RUT_TheRot | sown crop |
| `VRE_PoluxBush` | polux bush | vanillaracesexpanded.phytokin | Building (15) | - | 0.75~1.7 | 1.7 | 1 | - | yes | RUT_Wastes | tree |
