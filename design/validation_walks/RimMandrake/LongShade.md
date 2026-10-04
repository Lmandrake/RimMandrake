# RimMandrake: Long Shade — validation walk
subject: src/RimMandrake/LongShade  (packageId `mandrake.rm.longshade`)
deps: `mandrake.rm.flowworks` (modDependencies); loadAfter creaturebehaviors and environmentalhazards (shade grid, contact venom, mirrak ambush, pinned sun live there)
list: biomes tier; when folded into mandrake.rm.biomes it is active under the composed name 'RimMandrake: Baroque Biomes' (reads here are by def name and Harmony id)
status-hint: LONG_SHADE_FIRST_SCRIPT_1 — dayside desert biome; first script drafted, never run live

Sources: `src/RimMandrake/LongShade/About/About.xml` description, `Defs/**`, `Source/RM_LongShadeMod.cs`, `Source/RM_LongShadeMapgen.cs`, `Source/RM_Patch_DewfringeWildSpawnGate.cs`.

## must be true
- Every def the mod ships (biome, gen steps, creatures, plants, vorrel items/recipe/hediffs/thought, wrecks, think tree, sounds) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- `RM_LongShade` has animalDensity > 0 and plantDensity > 0, so its roster can spawn at all. → biome_wiring.animal_and_plant_density_positive
- Both map-generation steps (`RM_GenStep_CrawlerRoad`, `RM_GenStep_SunGraves`) resolve. → biome_wiring.gen_steps_resolve
- Every Mod Settings field (`modEnabled`, `dewfringeShadeLineGateEnabled`, `crawlerRoadEnabled`, `sunGravesEnabled`, `shipfallCommonsEnabled`) round-trips. → settings_roundtrip.modEnabled_round_trips, settings_roundtrip.dewfringeShadeLineGateEnabled_round_trips, settings_roundtrip.crawlerRoadEnabled_round_trips, settings_roundtrip.sunGravesEnabled_round_trips, settings_roundtrip.shipfallCommonsEnabled_round_trips
- The dewfringe rim gate postfix is attached to `WildPlantSpawner.CalculatePlantsWhichCanGrowAt`. → dewfringe_gate.rim_gate_postfix_attached
- The dewfringe grows only on shade-boundary cells. → dewfringe_gate.rim_gate_logic_wired; dewfringe_gate.rim_only_growth_on_a_long_shade_map (UNMEASURED: needs a generated Long Shade map)
- The Crawler Road is laid across the widest shade gap at map generation; off, none. → map_mechanics.crawler_road_wiring_and_gate, map_mechanics.crawler_road_laid_at_mapgen (UNMEASURED: map generation)
- The Long Carry's sun graves are laid at map generation; off, none. → map_mechanics.sun_graves_wiring_and_gate, map_mechanics.sun_graves_laid_at_mapgen (UNMEASURED: map generation)
- A landed gravship's shade draws wildlife in rungs and they scatter when a pilot takes the console. → map_mechanics.shipfall_commons_wiring_and_gate, map_mechanics.shipfall_commons_draws_wildlife (UNMEASURED: needs a landed gravship)
- The mirrak ambushes from false shade. → map_mechanics.mirrak_ambush_wiring, map_mechanics.mirrak_false_shade_ambush (UNMEASURED: CreatureBehaviors mechanism, live pawn needed)
- The vorrel runs its cycle. → map_mechanics.vorrel_cycle_chain_wired, map_mechanics.vorrel_cycle (UNMEASURED: game days)
- Every shipped creature and plant is in the biome roster and every PawnKindDef resolves. → roster_wiring.every_creature_and_plant_is_in_the_biome_roster, roster_wiring.every_pawnkind_resolves
- Nothing lives in the light and nothing survives leaving shelter (sun heat and shade gear). → UNCOVERED: owned by CreatureBehaviors / the SOLAR_HEAT_EXPOSURE_1 and SHADE_GEAR_FAMILY_1 items, not this mod
- The biome's tile count or painting. → UNCOVERED: the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); a zero count is expected

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml` (batches of 40): `foundCount` equals the request, `notFound` empty; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `RM_LongShadeSettings`   # settings_roundtrip
3. [D] `jawa/get_defs BiomeDef/RM_LongShade fields animalDensity,plantDensity`; the two GenStepDefs   # biome_wiring
4. [D] `jawa/harmony_patches WildPlantSpawner.CalculatePlantsWhichCanGrowAt`: postfix owner `mandrake.rm.longshade`   # dewfringe_gate
5. [B] map-generation, gravship and ticks mechanics   # map_mechanics (UNMEASURED until a drivable route exists)
X. [S] (human pass) the biome reads as a sunset desert where shade is the only refuge; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); no check here reads a tile count.
RULED OUT: "wildAnimals can be counted with `<li>`" — the roster uses the `<DefName>commonality</DefName>` shorthand; no check here counts `<li>`.
RULED OUT: "an unreadable roster means a missing roster" — `get_defs` returns record lists as bare type names unless deep=True and modExtensions as values; the roster is not asserted live, only the density gate.
