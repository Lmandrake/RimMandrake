# Alpha Biomes census: the rest of the names, decided (2026-11-01)

Item `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT`. Scope delegated offline by BENCH, 2026-10-23 (`--why "delegated: scope"`). Authority: the owner's card *"Should Alpha Biomes retire as a donor too -> Yes, retire it"*, and his 2026-10-19 order *"Reproduce the mutators into our own code, then proceed with deprecation of the donors."*

**Decision: nothing more gets ported.** Every terrain, weather, thought, biome, tile mutator and landmark Alpha Biomes defines now has one recorded answer. All the work this item feared was done by the ports of 2026-10-18 and 2026-10-19; what stayed behind is unused.

Data: `design/RimMandrake/alpha_biomes_census_2026-11-01.json`. Proof: `python3 src/RimMandrake/Utils/alpha_biomes_census.py check` and `src/RimMandrake/Utils/selftest_alpha_biomes_census.py`.

| category | donor defs | PORTED | VANILLA | DROPPED | UNPORTED |
|---|---|---|---|---|---|
| terrains | 115 | 26 | 2 | 87 | 0 |
| weather | 12 | 6 | 0 | 6 | 0 |
| thoughts | 16 | 5 | 0 | 11 | 0 |
| biomes | 12 | 10 | 0 | 2 | 0 |
| tile mutators | 91 | 17 | 0 | 71 | 3 |
| landmarks | 23 | 3 | 0 | 20 | 0 |

- **PORTED:** a def of ours, of the same def type, holds the role. `check` verifies that type.
- **VANILLA:** a base-game def holds it.
- **DROPPED:** gone with the donor. Nothing of ours places it, rolls it or fires it.
- **UNPORTED:** `AB_DerelictArchonexus`, `AB_DerelictBioLab`, `AB_DerelictKemeticTemple`, as `retired_mutators_port_map.json` already says. They sit only on the frozen 09-12 record save and clear at the one repaint.

## What the evidence is

- **src/ (measured 2026-11-01):** 223 distinct `AB_` tokens in tracked text. This is a wider instrument than the "146" of 2026-10-16, which read only XML and C# with comments stripped. Only one is a live reference: `AB_AlcyoniteChunk`, the inert row `retired_donor_refs.py` already allows. The rest are comments, tool tables, texture file names of ours, and About prose.
- **The canonical start (`ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`, `planet.start_savegame`):** 0 `AB_` tokens in a raw byte scan, with 463 `AM_` tokens as the control that the scan can see. `save_adoption_check.py` lists 86 unresolved names, none `AB_`, and its map terrain and under-terrain grids are clean. Those grids decode through the universe table only (INFERRED), so a cold load is still the final word; that load is `ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR` A3.
- **The frozen 09-12 record save** still holds `AB_` residue. It stays frozen; repairs are in `design/RimMandrake/donor_save_residue_2026-10-19.md`.

## Changes made with this census

- `AmbientShrineGuardians.cs` still listed `AB_TarPits` in its no-guardians biome set, so the Sump had silently lost the rule when the donor left. It now names `RM_TheSump` and `RUT_Sump`, and the DLL is rebuilt. Offline only: the shrine resolver itself has never been proven at map generation (the file's own note on `SHRINE_GUARDIAN_BIOME_GATE_1`). Not deployed.
- `src/RimMandrake/Miasma/About/About.xml`: deleted the claim that `AB_FertileMud` still has a role.

## For the one repaint

The `BiomeDef` table below is the old-to-new biome list `BIOME_PAINT_ONCE_AT_THE_END_1` needs. `save_donor_rewrite.py --mutators-only` renames mutators only. `src/RimMandrake/Utils/world_biomes.py`, `planet_portrait.py`, `worldview.py` and `ashkarr_paint.py` still carry `AB_` colour and paint rows (`AB_GallatrossGraveyard` among them): harmless records of the old planet, and they paint nothing of the new world.

`AB_GallatrossGraveyard` and `AB_IdyllicMeadows` are the two biomes dropped outright: no freeze sheet, no twin, off the paint list. A new name with no decision makes `check` fail.

## The names

<!-- tables:begin (alpha_biomes_census.py md) -->

### TerrainDef (115)

| name | decision | successor | why |
|---|---|---|---|
| `AB_AlienWoodFloors_CrystalWood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_AlienWoodFloors_MushroomStalks` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_AlienWoodFloors_RedWood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ArtificialTar` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_AsphaltBridge` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_AsphaltFloor` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_BlackPebbles` | PORTED | `RM_BlackPebbles` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_BrokenPoolTiles` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_Calcified` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CandySand` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CerebrospinalFluidFlood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CerebrospinalFluid_Deep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CerebrospinalFluid_MovingChestDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CerebrospinalFluid_MovingShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CerebrospinalFluid_Shallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CeruleanSoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CeruleanSoilRich` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ChocolateSoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ChocolateSoilRich` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CompactedSand` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CorruptedIntrusion` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CrackedMud` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_Cream` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_CrystalWoodFloors_RedWood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_Crystallized` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_DarkGravel` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_DarkMud` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_DenseGrass` | PORTED | `RM_DenseGrass` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_DenseMud` | PORTED | `RM_DenseMud` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_DryFlowerySoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FertileGrassyFlowerySoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FertileGrassyFlowerySoil_Oversaturated` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FertileMarsh` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FertileMud` | PORTED | `RM_FertileMud` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_FineForsakenSand` | PORTED | `RM_FineForsakenSand` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_FineSand` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FinestoneCragstone` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FinestoneMudstone` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FinestoneObsidian` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FinestoneRoseQuartz` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FlagstoneCragstone` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FlagstoneMudstone` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FlagstoneObsidian` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_FlagstoneRoseQuartz` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ForsakenRock` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ForsakenSand` | PORTED | `RM_ForsakenSand` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_GauranlenSoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_GauranlenSoilRich` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_GrassyFlowerySoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_GrassySand` | PORTED | `RM_GrassySand` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_HardenedChocolate` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_HardenedGrass` | PORTED | `RM_HardenedGrass` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_HardenedGrassFertile` | PORTED | `RM_HardenedGrassFertile` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_LightRedFlood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LightRedWaterDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LightRedWaterMovingChestDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LightRedWaterMovingShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LightRedWaterOceanDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LightRedWaterOceanShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LightRedWaterShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LiquidCreamFlood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LiquidCream_Deep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LiquidCream_MovingChestDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LiquidCream_MovingShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LiquidCream_Shallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_LiquidLava` | VANILLA | `LavaDeep` | lava is Odyssey vanilla; our Forge and Pyrelands use it |
| `AB_LiquidSlime` | PORTED | `RM_Slime_Liquid` | our terrain took this role |
| `AB_LushGrass` | PORTED | `RM_LushGrass` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_MutagenicOcularWaterFlood` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_MycoticGrass` | PORTED | `RM_TheRotGrass` | our terrain took this role |
| `AB_MycoticSoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_MycoticSoilRich` | PORTED | `RM_TheRotSoilRich` | our terrain took this role |
| `AB_Obsidian` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_OdysseyFlesh` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_PackedIce` | PORTED | `RM_PackedIce` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_PackedSnow` | PORTED | `RM_PackedSnow` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ParchedEarth` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_PropaneLake` | PORTED | `RM_TheChillDeep` | our terrain took this role |
| `AB_Quicksand` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_RichCrackedMud` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_RichSlime` | PORTED | `RM_RichSlime` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_Slime` | PORTED | `RM_Slime` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_SlimeGrass` | PORTED | `RM_Slime_Grass` | our terrain took this role |
| `AB_SlimyMud` | PORTED | `RM_Slime_Mud` | our terrain took this role |
| `AB_SnowOverRocks` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_SoilOnCrackedMetal` | PORTED | `RM_RustCathedral_CrackedMetalSoil` | our terrain took this role |
| `AB_SolidPropane` | PORTED | `RM_SolidPropane` | our terrain took this role |
| `AB_SolidifiedLava` | VANILLA | `CooledLava` | RM_RetiredMutatorPorts_Pyrelands.xml maps it to vanilla |
| `AB_Strawberry` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_Tar` | PORTED | `RM_TarShallow` | our terrain took this role |
| `AB_TarMud` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_TarmacFloor` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_TileCragstone` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_TileMudstone` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_TileObsidian` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_TileRoseQuartz` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ToxicFertileGrassyFlowerySoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_ToxicFlowerySoil` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_VolcanicGravel` | DROPPED | - | no def of ours places it and the canon start holds none |
| `AB_WebbedMarshyTerrain` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_AlienSand` | PORTED | `RM_AlienSand` | plain XML port, DonorPorts files, 2026-10-18 |
| `GU_AlienSandFine` | PORTED | `RM_AlienSandFine` | plain XML port, DonorPorts files, 2026-10-18 |
| `GU_AlienSoftSand` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_MetalFloor1` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_MetalFloor2` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_MetalFloor3` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_MossyRed` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_Piping` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RedWaterDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RedWaterMovingChestDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RedWaterMovingShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RedWaterOceanDeep` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RedWaterOceanShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RedWaterShallow` | DROPPED | - | no def of ours places it and the canon start holds none |
| `GU_RichAlienSand` | PORTED | `RM_RichAlienSand` | plain XML port, DonorPorts files, 2026-10-18 |

### WeatherDef (12)

| name | decision | successor | why |
|---|---|---|---|
| `AB_AcidRainWeather` | DROPPED | - | no biome of ours rolls it; the base weather was ported where a biome wanted it |
| `AB_ForsakenNight` | PORTED | `RM_ForsakenNight` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ForsakenNight_Alternate` | DROPPED | - | no biome of ours rolls it; the base weather was ported where a biome wanted it |
| `AB_ForsakenRainyNight` | PORTED | `RM_ForsakenRainyNight` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ForsakenRainyNight_Alternate` | DROPPED | - | no biome of ours rolls it; the base weather was ported where a biome wanted it |
| `AB_ForsakenThunderstorm` | PORTED | `RM_ForsakenThunderstorm` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ForsakenThunderstorm_Alternate` | DROPPED | - | no biome of ours rolls it; the base weather was ported where a biome wanted it |
| `AB_PetalStorms` | DROPPED | - | no biome of ours rolls it; the base weather was ported where a biome wanted it |
| `AB_RedFog` | PORTED | `RM_RedFog` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ReddishRain` | DROPPED | - | no biome of ours rolls it; the base weather was ported where a biome wanted it |
| `AB_VolcanicAsh` | PORTED | `RM_VolcanicAsh` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_VolcanicAshRain` | PORTED | `RM_VolcanicAshRain` | plain XML port, DonorPorts files, 2026-10-18 |

### ThoughtDef (16)

| name | decision | successor | why |
|---|---|---|---|
| `AB_ForsakenNight` | PORTED | `RM_ForsakenNight` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ForsakenRain` | PORTED | `RM_ForsakenRain` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_ForsakenThunderstorm` | PORTED | `RM_ForsakenThunderstorm` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_GelatinousEchoes_Bad` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_GelatinousEchoes_Good` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_HealingSpringwaterThought` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_MoldyEnvironment` | PORTED | `RM_MoldyEnvironment` | plain XML port, DonorPorts files, 2026-10-18 |
| `AB_MutagenicOcularWater` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_PetalStorms` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_PsychotropicFungusHigh` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_PsychotropicFungusWithdrawal` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_Quicksand` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_RawRimeNodulesHigh` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_RedFogThought` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_RedFogThoughtPositive` | DROPPED | - | its weather, chemical or mutator is not ours, so nothing can fire it |
| `AB_VolcanicAshThought` | PORTED | `RM_VolcanicAshThought` | plain XML port, DonorPorts files, 2026-10-18 |

### BiomeDef (12)

| name | decision | successor | why |
|---|---|---|---|
| `AB_FeraliskInfestedJungle` | PORTED | `RM_Webwork`, `RUT_Webwork` | the Webwork; RUT_Webwork header: replaces this donor |
| `AB_GallatrossGraveyard` | DROPPED | - | no twin in any freeze sheet and off the paint list; only colour and paint-table rows in retired world tools |
| `AB_GelatinousSuperorganism` | PORTED | `RM_GelatinousSlime`, `RUT_Slime` | the Slime; RUT_Slime header: replaces this donor |
| `AB_IdyllicMeadows` | DROPPED | - | no twin in any freeze sheet and off the paint list; only colour and paint-table rows in retired world tools |
| `AB_MechanoidIntrusion` | PORTED | `RM_RustCathedral`, `RUT_RustCathedral` | the Rust Cathedral; twin header: replaces this donor |
| `AB_MiasmicMangrove` | PORTED | `RM_Miasma`, `RUT_Miasma` | the Miasma; twin header: replaces this donor |
| `AB_MycoticJungle` | PORTED | `RM_TheRot`, `RUT_TheRot` | the Rot; twin header: replaces this donor |
| `AB_OcularForest` | PORTED | `RM_Contagion`, `RUT_Contagion` | the Contagion; twin header: replaces this donor |
| `AB_PropaneLakes` | PORTED | `RM_TheChill`, `RUT_PropaneLake` | the Chill; RUT_PropaneLake took its tiles, RM_TheChill is the mod body |
| `AB_PyroclasticConflagration` | PORTED | `RM_TheForge`, `RM_Pyrelands`, `RUT_TheForge` | split: base of the Forge twin, mutators to Pyrelands |
| `AB_RockyCrags` | PORTED | `RM_Abyss`, `RUT_Abyss` | the Abyss, once the Forsaken Crags; twin header: replaces this donor |
| `AB_TarPits` | PORTED | `RM_TheSump`, `RUT_Sump` | the Sump; twin header: replaces this donor |

### TileMutatorDef (91)

| name | decision | successor | why |
|---|---|---|---|
| `AB_AgariluxPrime_Mutator` | PORTED | `RM_AgariluxPrimeSprout` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_AmbientRadiation` | PORTED | `RM_AmbientRadiation` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_AncientBloodRainVent` | PORTED | `RM_AncientBloodRainVent` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_AncientDeathPallVent` | DROPPED | - | retired_mutators_port_map.json: status dropped |
| `AB_AncientFreezingVent` | PORTED | `RM_AncientFreezingVent` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_AncientGreyPallVent` | PORTED | `RM_AncientGrayPallVent` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_AnimaDesertFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_AnimaFaunaDesert` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_AnimaSoilsDesert` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_BlizzariskNest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_BumbledroneNests` | PORTED | `RM_SwarmHiveNests` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_ButterflySwarms` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CalcifiedRemnants` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CalcifiedSoil` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CerebrospinalFluid` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CloverForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CorruptedIntrusion` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CorruptedMechFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DerelictArchonexus` | UNPORTED | - | on the frozen 09-12 record save only; left to the one repaint by the port map |
| `AB_DerelictBioLab` | UNPORTED | - | on the frozen 09-12 record save only; left to the one repaint by the port map |
| `AB_DerelictClusters` | PORTED | `RM_DerelictClusters` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_DerelictKemeticTemple` | UNPORTED | - | on the frozen 09-12 record save only; left to the one repaint by the port map |
| `AB_DerelictLibrary` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DerelictResort` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DessertTrees` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DigestiveSurface` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DiminutiveRegion` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DryClimate` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DryMeadows` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DryMeadowsFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DunealiskNest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_EdibleAirborneMicrofungi` | PORTED | `RM_EdibleAirborneMicrofungi` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_ExplodingAnimals` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ExtremeTemperatureFluctuations` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_FeraliskNest` | PORTED | `RM_OllathrixNest` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_FleshTerrain` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_FleshTrees` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GauranlenFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GauranlenSoil` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GelatinousMemoryEcho` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GeothermalHotspots` | PORTED | `RM_GeothermalHotspots` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_GiantFossils` | PORTED | `RM_GiantFossils` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_GinkgoForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GnawingSands` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GoldenTrees` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_HealingSprings` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_JadeiteChunksDesert` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_LivingAlcyonite` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_LivingCrystalBed` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_LocustPlagues` | PORTED | `RM_LocustPlagues` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_LuminescentTrees` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_MagmaVents` | PORTED | `RM_MagmaVents` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_MagmaticQuagmire` | PORTED | `RM_MagmaticQuagmire` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_MauvebloomFields` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_MauvebloomFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_MobileCacti` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_MoldyEnvironment` | PORTED | `RM_MoldyEnvironment` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_MutagenicSprings` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_NarrowRegion` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ObsidianExpanse` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ObsidianSpires` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_OcularDesertFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_OcularDesertSoil` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_OcularTransformation` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_OversaturatedSoil` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_PetalStorms` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_PollinationFrenzy` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_PropaneLakes` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_QuicksandPits` | PORTED | `RM_QuicksandPits` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_QuiveringSurface` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_RedFog` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ReddishRains` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ReddishWaters` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ResidualOverclocking` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_SterileGround` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_SugarChunks` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_SweetFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_SweetForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_SweetRocks` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_SymbioticNutrients` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_TarHoles` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_TarLakes` | PORTED | `RM_TarLakes` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_TechnoTrees` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ToxicMeadows` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ToxicMeadowsFlora` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_TumorousGrowths` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_UnshackledCompanionDryads` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_UnshackledDryads` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_WarpedStoneForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_WideRegion` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_WillowForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |

### LandmarkDef (23)

| name | decision | successor | why |
|---|---|---|---|
| `AB_AnimaDesert` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CalcifiedRemnants` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CloverForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_CorruptedIntrusion` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_DryMeadows` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_FleshMorass` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GauranlenGrove` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GinkgoForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_GnawingSands` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_HealingSprings` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_LivingCrystalBed` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_MagmaticQuagmire` | PORTED | `RM_MagmaticQuagmire` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_MauvebloomFields` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_MutagenicSprings` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_ObsidianExpanse` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_OcularDesert` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_PropaneLakes` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_QuicksandPits` | PORTED | `RM_QuicksandPits` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_SweetForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_TarLakes` | PORTED | `RM_TarLakes` | owner order 2026-10-19; retired_mutators_port_map.json |
| `AB_ToxicMeadows` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_WarpedStoneForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |
| `AB_WillowForest` | DROPPED | - | on no tile of the canonical save, so owner note 2026-10-19 needs no decision |

<!-- tables:end -->
