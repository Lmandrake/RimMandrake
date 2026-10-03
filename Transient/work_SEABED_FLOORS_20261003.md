# SEABED_PER_SEA_FLOORS_1 work log 2026-10-03
Mod folder edited: src/RimMandrake/DivingInteraction only (owns RM_SeabedLayer).
Choices: floor biome mapping = RM_SeabedAccessExtension.floorBiome (new field) on surface biomes, wired by
Patches/RM_SeabedFloorBiomeWiring.xml (FindMod terminalbiomes) to 4 new RM_SeabedFloor_<Sea> biomes
(Defs/PlanetLayerDefs/RM_SeabedFloorBiomes.xml). PopulateTile uses FloorBiomeFor, falling back to RM_SeabedFloor.
Four RM_ seas = Scald, Grey, Twilight, Chill. Propane Lake is RUT_ (UtinniPatches) - not touched.
Plant guard: Harmony finalizer on MapPlantGrowthRateCalculator.BuildFor(Map), seabed maps only. Decompiled
TileTemperaturesComp caches per layer, so original crash may not reproduce; unproven live.
Densities 0 on all floor biomes: floor plants/fauna wait on live proof of guard + floor map generator (Phase 2/3).
