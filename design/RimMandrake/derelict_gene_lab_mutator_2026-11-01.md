# The derelict gene lab: one more mutator, on vanilla's own ruin generator

Item `DERELICT_LABS_DESIGN_ONE_MORE_MUTATOR` · status: DESIGN, nothing built · 2026-11-01, relentless builder (gen 1).

**What the owner asked for**, 2026-10-19, on the derelict-study card: *"Another mutator that works just as
mutators do."* The item: a derelict gene lab as a normal world mutator that **replaces `AB_DerelictBioLab`**
(Alpha Biomes; 5 tiles in the canonical save, not reproduced by the port,
`design/RimMandrake/retired_mutators_port_2026-10-19.md`), designed from the derelict study
(`design/RimMandrake/derelict_structures_lessons_2026-10-19.md` §3, §6, §7.1) on **vanilla's procedural ruin
generator**. The title settles the study's §8 question 2 (fixed or varied plans): **varied per visit**.

## 1. The finding that shapes everything

Odyssey already ships five mutators of exactly this kind (`Odyssey/Defs/TileMutators/TileMutators_AncientStructures.xml`):
`AncientGarrison`, `AncientWarehouse`, `AncientChemfuelRefinery`, `AncientInfestedSettlement`, `AncientLaunchSite`.
Each is a `TileMutatorDef` with `ParentName="AncientStructureMutBase"`, `workerClass`
`TileMutatorWorker_AncientStructure`, and a `structureGenParms` block that names a `StructureLayoutDef`
(`Odyssey/Defs/LayoutDefs/Layouts_AncientRuins.xml`, `workerClass LayoutWorker_AncientRuins`). The layout def holds a
**weighted room table** (`roomDefs`: a bare number is a weight; `countRange` forces a count), `corridorShapes`,
`junkScaterrers` and damage `parts` (`Breached`, `Gore`). The mutator adds a perimeter (`perimeterWallDef`,
`perimeterTerrainDef`, `perimeterScatteredThings`) and exterior `scatteredPrefabs`.

So "a mutator that works just as mutators do" is literal: **`RM_DerelictGeneLab` is a sixth sibling of
`AncientWarehouse`**, written in XML against the vanilla worker. Every visit draws a new plan. It needs no KCSG,
no layout drawings, no generator script and, for its first version, no art.

## 2. The decisions in one table

| question | decision | why |
|---|---|---|
| What places the lab? | A `TileMutatorDef` `RM_DerelictGeneLab`, `ParentName="AncientStructureMutBase"`, `workerClass` `TileMutatorWorker_AncientStructure`, `structureGenParms.structureLayoutDef` `RM_DerelictGeneLab` | It is the vanilla pattern, used five times by Odyssey. The parent gives the `AncientStructure` category, so a tile carries one ancient structure at most, never a lab inside a garrison |
| What builds the plan? | A `StructureLayoutDef` `RM_DerelictGeneLab`, `LayoutWorker_AncientRuins`, `structureSizeRange` `40~55`, the room table of §3 | This is the generator the study found we had never used. Size sits inside Odyssey's own 35–65 band, close to the donor's labs (37×51 to 85×93, minus the biggest) |
| Which rooms? | Five **vanilla** lab-flavoured `LayoutRoomDef`s used as they are, plus three new ones of ours (§3) | Vanilla already has a lab (`AncientLab`), a mech gestator room (`AncientMechGestatorRoom`), an operating room (`AncientRuinsOperatingRoom` → `RoomContents_OperatingRoom`), a cryptosleep vault and a loot vault. Ours add only what vanilla lacks: genes |
| Where are the genes? | An openable crate `RM_AncientGeneCase` (`ParentName="LowTechCrateBase"`) whose `CompProperties_LootSpawn` rolls a `ThingSetMakerDef` `RM_Reward_DerelictGeneCase` (`ThingSetMaker_RandomOption`: one `Genepack`, or two, or a little `ComponentIndustrial`) | This is the donor's "loot roller" with no C#: Odyssey's `AncientBox_ComponentIndustrial` does exactly this with `Reward_AncientBox_ComponentIndustrial`. A case is opened, not mined, so the prize is a choice, not a census |
| What threatens? | Vanilla room parts only: `GestationTanks` (a `RoomPart_GestationTankDef` whose options are `Proximity` 0.2 / `Dormant` 0.3 / `Empty` 0.5) in the vat hall, and `DormantMechCluster` in the sealed vault | `Proximity` is the donor's proximity-triggered raid beacon, already in vanilla, already tied to exploration and not to a timer. The study's `RectTrigger`/`SignalAction_Ambush` plan is not needed |
| What does it look like? | **v1: vanilla ancient things only** (sterile and ancient tile, `AncientDisplayBank_Edge`, `OperatingTables`, mech gestators, emergency lights). **v2: a small "ruined Biotech machine" junk kit** (§4) | Phase 1 is shippable with zero sprites. The kit is the study's one real art idea ("the vanilla machine you know, broken") and goes through `art install` |
| Where can it appear? | The parent's `biomeWhitelist` (vanilla Desert, ExtremeDesert, AridShrubland and the rest); our arid biomes are added by a `PatchOperationConditional` in UtinniPatches, the way `RM_DerelictClusters` gets `RUT_RustCathedral` | No new mechanism; the twin-biome route is already used for every ported mutator |
| How does it reach the map? | **By hand, at the one painting.** `chanceOnNonLandmarkTile` is set to `0` explicitly | There is no worldgen of any kind. The 5 tiles that held `AB_DerelictBioLab` are the natural first candidates; a lab on 0 tiles before the painting is the expected state, not a defect |
| Tier, mod, name | RM tier, franchise-free (a gene lab is not Star Wars IP). Lives in `src/RimMandrake/StructureInjections` (`mandrake.rm.injections`, which already loads after Odyssey). Prefix `RM_` | The study's §7 said extend StructureInjections, not a new mod |

## 3. The room table

Weights follow Odyssey's convention: a bare number is a weight; `countRange` is a guaranteed count.

| room | source | in the table | what it holds |
|---|---|---|---|
| `RM_GeneLabVatHall` | **new** | `countRange 1` | the lab's heart and its one threat: rows of `AncientMechGestator_Cluster` / `AncientLargeMechGestator` along the walls, `parts` `GestationTanks`, `floorTypes` `SterileTile`, scatter `ChunkMechanoidSlag`. v2 swaps the gestators for ruined growth vats |
| `RM_GeneLabGeneWing` | **new** | `countRange 1~2` | the reason to come: `AncientDisplayBank_Edge` along the walls, 1–3 `RM_AncientGeneCase`, `floorTypes` `SterileTile`; `parts` `Corpse` (the lab staff, vanilla's corpse part, not the donor's corpse-as-building) |
| `AncientLab` | vanilla (Ideology) | 2 | display banks and an operating table on sterile tile |
| `AncientRuinsOperatingRoom` | vanilla (Odyssey) | 2 | the ward: `RoomContents_OperatingRoom` |
| `AncientMechGestatorRoom` | vanilla (Biotech) | 1 | a second, quieter gestator bay (no tanks) |
| `RM_GeneLabSpecimenStore` | **new** | 1 | `IndustrialShelf_Edge` rows and one `RM_AncientGeneCase`; the donor's "loot in shelf alcoves" |
| `AncientRuinsRubble` | vanilla (Odyssey) | 3 | collapse: the ragged, broken edge the study asked for |
| `AncientRuinsEmpty` | vanilla (Odyssey) | 2 | quiet rooms, so the lab reads as abandoned and not as a dungeon |
| `AncientRuinsCryptosleepCasket` | vanilla (Odyssey) | 0.1 | a sealed subject vault (dormant mechs, spacer crates) |
| `AncientRuinsMechsWithLoot` | vanilla (Odyssey) | 0.1 | the rare guarded strongroom |

Layout-level fields, copied from `AncientWarehouse` and tuned: `minRoomWidth`/`minRoomHeight` 7 (labs are many
small rooms; the donor had 191 doors in 13 plans), `canDisconnectRooms` false, `ensureOneDoorUnlocked` true,
`wallLampDef` `AncientEmergencyLight_Blue`, `corridorShapes` `H, Cross, T`, `junkScaterrers` `Filth_RubbleBuilding`
and `ChunkSlagSteel`, `parts` `Breached` 0.1 and `Gore` 0.05. The mutator's perimeter: `perimeterWallDef`
`AncientFence` at `perimeterWallChance` 0.6 (a broken fence, not a garrison wall), `perimeterTerrainDef`
`AncientConcrete`, `perimeterScatteredThings` a few `ChunkSlagSteel` and `Filth_MachineBits`.

The new room defs are XML only: `prefabs`, `parts`, `scatter` and `floorTypes`, the fields vanilla rooms use
(§Cited machinery). No `roomContentsWorkerType` of our own.

## 4. v2: the ruined-Biotech junk kit

The study's §3 lesson 1 and 2: a ruin is read by its broken machines, and junk that deconstructs to steel and slag
is a loot economy with no loot table, which suits Jawa scavengers exactly. Before drawing anything,
**reuse what `src/RimMandrake/WreckedMachines` already has** (its `RM_WM_*_Wrecked` family is a repair ladder, not
junk; check whether a plain junk base exists there or in `Wreckage`). The kit, each a 1-cell-thick dressing
building with `costList` steel plus `ChunkSlagSteel`, `PassThroughOnly`, drawn as the vanilla Biotech machine
broken:

| junk def (proposed) | ruined version of | replaces in the v1 table |
|---|---|---|
| `RM_RuinedGrowthVat` | `GrowthVat` | the gestator clusters in `RM_GeneLabVatHall` |
| `RM_RuinedGeneBank` | `GeneBank` | some display banks in `RM_GeneLabGeneWing` |
| `RM_RuinedGeneAssembler` | `GeneAssembler` | the second machine of the gene wing |
| `RM_RuinedLabBench` | the vanilla hi-tech research bench | dressing in `AncientLab`-like rooms |
| `RM_LabTileCracked` (terrain) | `SterileTile` | the floor of the new rooms |

About 5 sprites plus a terrain, through the art pipeline and its judge. The v1 lab is complete without them.

## 5. Mod Settings

Two switches in the existing `RM_StructureInjectionsSettings`, defaults = shipped behaviour:

- **Derelict gene labs** (on). Off: the tile's lab is not generated.
- **Gene-lab threats** (on). Off: the worker generates `RM_DerelictGeneLab_Quiet`, the same table with
  `GestationTanks`, `CryptosleepCasket` and `MechsWithLoot` removed.

Both need one small C# class: `RM_TileMutatorWorker_DerelictGeneLab`, a subclass of
`TileMutatorWorker_AncientStructure` that reads the settings and either returns or swaps the layout def. Which
virtual method it overrides is read from the decompiled worker at build time, never guessed. There is no
"loot density" knob: the room table and the crate's `ThingSetMakerDef` already set it, and a multiplier would be a
number nobody feels.

## 6. Build order and proof

1. **XML** in `src/RimMandrake/StructureInjections/Defs/DerelictGeneLab/`: the mutator, the two layout defs, the
   three room defs, the crate and its `ThingSetMakerDef`. `validate_patch.py --defs` on each file.
2. **C#** worker and the two settings.
3. **UtinniPatches**: add our arid biomes to the whitelist (conditional patch, as for `RM_DerelictClusters`).
4. **Script first**: a gene-lab row in `src/RimMandrake/StructureInjections/validation.py`. On a quicktest map with
   the mutator forced on the tile it reads: at least one `RM_GeneLabVatHall` and one `RM_GeneLabGeneWing` room, at
   least one `RM_AncientGeneCase`, and that opening a case yields a `Genepack` holding at least one gene. The last
   check is the one real unknown: vanilla traders stock a bare `Genepack` def and it arrives with genes, so a
   `ThingSetMaker` should too, but this is read, not assumed.
5. **Bookkeeping**: the `AB_DerelictBioLab` row of `design/RimMandrake/retired_mutators_port_map.json` gets
   `new: RM_DerelictGeneLab`, and the lab joins the paint list (`BIOME_PAINT_ONCE_AT_THE_END_1`).
6. **v2 kit** (§4) as its own item after v1 is proven.

Cost: about 1 agent-day for v1 (it is mostly copying a vanilla sibling), about 1 more for the kit and its art.

## 7. What this does not do

- No KCSG layouts, no `gen_*_layout.py`: the temple design keeps those because a temple is read by its fixed
  axis; a lab is read by its rooms, which is what a generator varies well
  (`design/RimMandrake/temple_ruins_several_faiths_2026-11-01.md` §1).
- No `RectTrigger` ambush and no raid beacon building: `GestationTanks` `Proximity` covers it.
- No donor content kept: no Alpha Genes layouts, art or comps.
- No world painting now, and no roll at world creation.

## Cited machinery

Checked by `python3 src/RimMandrake/Utils/check_design_citations.py design/RimMandrake/derelict_gene_lab_mutator_2026-11-01.md`.

| name | root | used for |
|---|---|---|
| `TileMutatorDef` | vanilla | the mutator |
| `AncientStructureMutBase` | vanilla | parent: category and biome whitelist |
| `TileMutatorWorker_AncientStructure` | vanilla | the worker |
| `structureGenParms` | vanilla | mutator → layout |
| `structureLayoutDef` | vanilla | mutator → layout |
| `structureSizeRange` | vanilla | footprint |
| `AncientWarehouse` | vanilla | the sibling we copy |
| `LayoutWorker_AncientRuins` | vanilla | the procedural generator |
| `roomDefs` | vanilla | weighted room table |
| `corridorShapes` | vanilla | layout |
| `junkScaterrers` | vanilla | layout (vanilla's spelling) |
| `canDisconnectRooms` | vanilla | layout |
| `ensureOneDoorUnlocked` | vanilla | layout |
| `minRoomWidth` | vanilla | layout |
| `wallLampDef` | vanilla | layout |
| `AncientEmergencyLight_Blue` | vanilla | wall lamps |
| `perimeterWallDef` | vanilla | perimeter |
| `perimeterWallChance` | vanilla | perimeter |
| `perimeterTerrainDef` | vanilla | perimeter |
| `perimeterScatteredThings` | vanilla | perimeter |
| `AncientFence` | vanilla | perimeter wall |
| `AncientConcrete` | vanilla | perimeter floor |
| `Filth_MachineBits` | vanilla | perimeter scatter |
| `ChunkSlagSteel` | vanilla | scatter, junk cost |
| `Filth_RubbleBuilding` | vanilla | junk scatter |
| `Breached` | vanilla | layout damage part |
| `Gore` | vanilla | layout damage part |
| `chanceOnNonLandmarkTile` | vanilla | set to 0: no roll |
| `AncientLab` | vanilla | room |
| `AncientRuinsOperatingRoom` | vanilla | room |
| `RoomContents_OperatingRoom` | vanilla | its contents worker |
| `AncientMechGestatorRoom` | vanilla | room |
| `AncientRuinsRubble` | vanilla | room |
| `AncientRuinsEmpty` | vanilla | room |
| `AncientRuinsCryptosleepCasket` | vanilla | room |
| `AncientRuinsMechsWithLoot` | vanilla | room |
| `LayoutRoomDef` | vanilla | our three rooms |
| `floorTypes` | vanilla | room field |
| `countPerTenEdgeCells` | vanilla | room prefab field |
| `SterileTile` | vanilla | floor |
| `AncientDisplayBank_Edge` | vanilla | gene-wing prefab |
| `OperatingTables` | vanilla | prefab |
| `IndustrialShelf_Edge` | vanilla | specimen-store prefab |
| `AncientMechGestator_Cluster` | vanilla | vat-hall prefab |
| `AncientLargeMechGestator` | vanilla | vat-hall prefab |
| `ChunkMechanoidSlag` | vanilla | vat-hall scatter |
| `GestationTanks` | vanilla | the proximity threat |
| `RoomPart_GestationTankDef` | vanilla | its def class |
| `Proximity` | vanilla | its triggered option |
| `DormantMechCluster` | vanilla | vault threat |
| `Corpse` | vanilla | dead staff room part |
| `LowTechCrateBase` | vanilla | the gene case's parent |
| `AncientBox_ComponentIndustrial` | vanilla | the loot-roller pattern |
| `CompProperties_LootSpawn` | vanilla | loot roll on opening |
| `Reward_AncientBox_ComponentIndustrial` | vanilla | the ThingSetMaker pattern |
| `ThingSetMakerDef` | vanilla | the case's reward |
| `ThingSetMaker_RandomOption` | vanilla | weighted reward |
| `ThingSetMaker_StackCount` | vanilla | counted reward |
| `Genepack` | vanilla | the prize |
| `ComponentIndustrial` | vanilla | the lesser prize |
| `GrowthVat` | vanilla | v2 ruined machine |
| `GeneBank` | vanilla | v2 ruined machine |
| `GeneAssembler` | vanilla | v2 ruined machine |
| `PassThroughOnly` | vanilla | v2 junk passability |
| `PatchOperationConditional` | src | biome whitelist patch (engine class; our patches use it) |
| `RM_DerelictClusters` | src | the ported-mutator precedent |
| `RUT_RustCathedral` | src | twin biome added by patch |
| `RM_StructureInjectionsSettings` | src | where the two switches go |
| `mandrake.rm.injections` | src | the host mod |
| `RM_WM_PowerCell_Wrecked` | src | WreckedMachines, check before a new kit |
