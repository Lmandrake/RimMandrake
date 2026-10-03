# RimMandrake: The Rot — validation walk
subject: src/RimMandrake/TheRot  (packageId `mandrake.rm.therot`)
deps: `mandrake.rm.environmentalhazards`, `mandrake.rm.creaturebehaviors` (modDependencies)
list: biomes tier; when folded into mandrake.rm.biomes it is active under the composed name (reads here are by def name)
status-hint: THE_ROT_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimMandrake/TheRot/About/About.xml`, `Defs/**`, `Source/RM_TheRotMod.cs`, `Source/RM_BiomeWorker_TheRot.cs`.

## must be true
- Every def the mod ships loads and resolves; a bogus name reads notFound. → defs_resolve.every_deployed_def_resolves
- `RM_TheRot` has animalDensity > 0 and plantDensity > 0 and its worker class is `RM_BiomeWorker_TheRot`. → biome_wiring.animal_and_plant_density_positive, biome_wiring.biome_worker_class_loaded
- Every Mod Settings field of `RM_TheRotSettings` round-trips. → settings_roundtrip.*
- Sheen exposure, accelerated rot, warm ground, live preparations, guardian groves, health sharing, pale tree, spore cloud, cross-biome mode. → map_mechanics.* (UNMEASURED: need a generated map and ticks)
- The settings screen does not yet gate the shared environmentalhazards mechanics. → UNCOVERED: stated in the settings class header (owed consolidation)

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `RM_TheRotSettings`   # settings_roundtrip
3. [D] `jawa/get_defs BiomeDef/RM_TheRot fields animalDensity,plantDensity,workerClass`   # biome_wiring
4. [B] map-generation, weather and ticks mechanics   # map_mechanics (UNMEASURED)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1).
