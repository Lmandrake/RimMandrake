# SEABED_FLOOR_GENERATORS_1 — each sea's floor content generates on the seabed layer

Split from `SEA_DIVE_HATCH_RETIRE_1`. The four `RM_SeaDiveGenerator_*` MapGeneratorDefs
(`src/RimMandrake/DivingInteraction/Defs/MapGeneration/RM_SeaDiveGenerators.xml`) hold the floor content
and are today reached only by the leftover hatch's pocket map. The `RM_SeabedLayer` mirror gives every
floor tile `RM_SeabedFloor`/`RM_SeabedUnavailable` and no per-sea generator
(`GenStep_ChillReturnComb.cs` and `GenStep_ScaldVentField.cs` say so in their headers).

## spec

1. A floor tile under a sea uses that sea's generator content: per-sea seabed biomes or a generator
   chooser keyed on the surface tile's biome above (Phase 4 of the seabed plan decides biomes; this item
   may ship the chooser over the existing generators first).
2. Drop `pocketMapProperties` and `RM_PlaceSeaDiveExit` from the layer-path generators; keep every
   content genstep (terrain, vent field, return gallery, Grey Sea scatters, Chill comb, fauna).
3. Guard `MapPlantGrowthRateCalculator` before giving a floor real plants (SEABED_PLANET_LAYER_1 watch-out;
   `Patch_SeabedPlantGrowthGuard.cs` exists).

## criteria

- A generated floor tile under the Scald carries the Scald floor's terrain, vents and fauna, with no exit
  building; same for each of the four seas.
