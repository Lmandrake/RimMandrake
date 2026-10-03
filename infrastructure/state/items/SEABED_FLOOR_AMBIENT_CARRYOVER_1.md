# SEABED_FLOOR_AMBIENT_CARRYOVER_1 — what the hatch's pocket map gave a floor that the layer map does not

Split from `SEABED_FLOOR_GENERATORS_1` (built cbc8adc7c). A seabed-layer floor map takes biome,
temperature and mutators from its TILE, so three things the hatch pocket maps carried in
`pocketMapProperties` are not on the layer floors yet.

## spec

1. **Ambient temperature per sea.** The Chill floor is -110 C on the hatch (`RM_ChillFireGate.ChillSeabedAmbientC`
   reads `OutdoorTemp`); a layer floor mirrors the surface tile's temperature (`RM_SeabedLayerUtility.PopulateTile`).
   Carry each sea's floor temperature (Scald 55, Grey 12, Twilight 8, Chill -110) onto the floor, e.g. a
   `floorTemperature` on `RM_SeabedFloorExtension` written in `PopulateTile` (seasonal swing is the tile's).
2. **Floor plants.** The vanilla `Plants` step reads `map.Biome`, and the floor biomes keep `plantDensity 0`. Give
   each floor biome its sea's `wildPlants`/`plantDensity` (data copy or a startup copy) once
   `Patch_SeabedPlantGrowthGuard` is proven live (or proven unneeded).
3. **Ongoing fauna.** The hatch maps add `RM_SeaFloorHabitat` (animalDensityFactor 30); floor biomes have
   `animalDensity 0`, so nothing respawns on a layer floor. Decide: floor biome animal density + cast, or the mutator.

## criteria

- A generated Chill layer floor reads about -110 C outdoors; the Twilight floor grows its flora; a cleared floor
  slowly repopulates.
