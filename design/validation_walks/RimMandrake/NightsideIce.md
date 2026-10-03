# RimMandrake: Nightside Ice — validation walk
subject: src/RimMandrake/NightsideIce  (packageId `mandrake.rm.nightsideice`)
deps: Odyssey, Anomaly loaded before it (loadAfter); wildAnimals rows are MayRequire-gated on sarg.alphaanimals, longshade and stillsand
list: biomes tier; when folded into mandrake.rm.biomes it is active under 'RimMandrake: Baroque Biomes' (reads here are by def name)
status-hint: NIGHTSIDE_ICE_FIRST_SCRIPT_1 — one BiomeDef and a master switch that gates nothing yet; first script drafted, never run live

Sources: `src/RimMandrake/NightsideIce/About/About.xml` description, `Defs/BiomeDefs/RM_NightsideIce.xml` (its own header carries the sheet's bans), `Source/RM_NightsideIceMod.cs`.

## must be true
- `RM_NightsideIce` loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- The one Mod Settings field (`masterEnabled`) round-trips. → settings_roundtrip.masterEnabled_round_trips
- `animalDensity` > 0 (0 makes the roster dead content) and `plantDensity` is 0; rivers off, roads on, no farming camps, extreme biome, vanilla `BiomeWorker_IceSheet`. → biome_doctrine.flags_and_worker_match_the_sheet
- Clear is the only weather with weight (no precipitation, no wind on the interior). → biome_doctrine.only_clear_weather_has_weight
- No plant of any kind is wired to the biome. → biome_roster.no_wild_plants
- Every animal row the game resolved carries the commonality its XML states; ungated rows are present. → biome_roster.animal_rows_carry_source_commonality
- The probe can say a creature is absent. → biome_roster.biome_probe_ready
- A generated nightside-ice map is all Ice with no ponds. → map_mechanics.generated_map_is_all_ice_without_water (UNMEASURED: map generation)
- The master switch gates behaviour. → UNCOVERED: it gates nothing yet (no kit mechanic is built; the settings screen says so)
- The biome's tile count or painting. → UNCOVERED: the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); a zero count is expected

## the walk
1. [D] `jawa/get_defs BiomeDef/RM_NightsideIce`; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on `masterEnabled`   # settings_roundtrip
3. [D] `jawa/get_defs` scalars and deep `baseWeatherCommonalities`   # biome_doctrine
4. [D] `jawa/biome_probe` animals and plants, with a control creature   # biome_roster
5. [B] generated-map terrain   # map_mechanics (UNMEASURED until a drivable route exists)
X. [S] (human pass) the biome reads as dirty ice, near-empty by design; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); no check here reads a tile count.
RULED OUT: "wildAnimals can be counted with `<li>`" — the roster uses the `<DefName>commonality</DefName>` shorthand; the roster check reads the XML node name and text, and biome_probe live.
RULED OUT: "a missing donor-gated animal row is a defect" — every row is MayRequire-gated on a mod that may not be on the tier; only rows the game resolved are compared.
