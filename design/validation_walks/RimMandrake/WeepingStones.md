# RimMandrake: Weeping Stones — validation walk
subject: src/RimMandrake/WeepingStones  (dev source folder, own About.xml packageId `mandrake.rm.weepingstones`, never deployed standalone: the biome ships COMPOSED inside `mandrake.rm.biomes`, RimMandrake: Baroque Biomes, so test that) <!-- walklint-ok: mandrake.rm.biomes is the GENERATED composed packageId of Biomes.compose.json; no About.xml under src/ declares it -->
feature: biome-core
deps: mandrake.rm.biomes (the composed biome, which carries FlowWorks, Alpha Biomes and Luminous Pigment as its own dependencies) <!-- walklint-ok: composed packageId mandrake.rm.biomes has no About.xml under src/ by design -->
list: modset_builder tier `weepingstones_solo` (BRIDGE + mandrake.rm.biomes + the five DLCs; NOT the older `weepingstones` tier, which adds the Utinni layer for the campaign fauna)
status-hint: the franchise-free oasis biome `RM_WeepingStones` (hand-placed, generatesNaturally=false) plus the Stocked Pool husbandry kit. Tile assignment is redone at the one planet-painting pass, so a tile count is never evidence about this biome. Script: `src/RimMandrake/WeepingStones/validation.py`; offline proof that every check can fail: `src/RimMandrake/WeepingStones/selftest_weepingstones.py`.

## must be true
Every line is sourced from the mod's About.xml description, its defs, or its C# (named in brackets). `→ chain.component` is the covering check in `validation.py`; `→ UNCOVERED: why` is a named boundary.

- Every def the mod ships loads in the running game and resolves to this mod, not to a donor: biome, 17 race ThingDefs + 17 PawnKindDefs, 35 items, 10 plants, 5 recipes, 8 thoughts, 5 jobs, 5 work givers, the rare-catch set maker. A def that fails to load is dropped whole and silently (a missing type, an XML comment with a double hyphen). [About.xml wave notes; `Defs/`] → defs_resolve.defs_resolve_race_things, defs_resolve.defs_resolve_pawnkinds, defs_resolve.defs_resolve_items, defs_resolve.defs_resolve_plants, defs_resolve.defs_resolve_recipes, defs_resolve.defs_resolve_thoughts, defs_resolve.defs_resolve_jobs, defs_resolve.defs_resolve_workgivers, defs_resolve.defs_resolve_set_makers, defs_resolve.defs_resolve_biome
- The def-probe instrument itself can say "not found". [method] → defs_resolve.resolve_probe_sees_absence
- Jobs read their outputs by name (`RM_<Kind>Meat`, `<Kind>BreedingStock`) with a silent-fail lookup, so every stocked species has both defs. [`RM_JobDriver_HarvestPoolPen.cs`, `RM_PoolBreederUtility.cs`] → defs_resolve.defs_pair_up_by_convention
- The load log names no config error, unresolved cross-reference, missing type or exception for this mod's content (guards the 2026-09-20..24 defects: a stale EnvironmentalHazards dll discarding the BiomeDef, lifeStages counts, dangling body-part groups). [commit `55d52a2fe`, `953181dc9`] → log_clean.player_log_names_no_weepingstones_error
- `RM_WeepingStones` is placed by hand, never by natural worldgen, and its animal and plant densities are above zero (a zero animalDensity makes the whole roster dead content). [About.xml; engine gate MEASURED 2026-09-26] → biome_roster.biome_flags_and_densities
- The biome's wild animals are the 6 stocked-pool species, the 8 invented natives, the canyon crab and the two inline donor rows, at the commonalities in the XML. [About.xml; `RM_WeepingStones_Biome.xml`] → biome_roster.wild_animals_wired
- The biome's wild plants are `Plant_Reeds`, `Plant_Ambrosia`, `RM_Shadefern`, `RM_Dewshrooms` and the nine other invented flora, at the XML commonalities. [About.xml] → biome_roster.wild_plants_wired
- `RM_Vhorrin` is never an ambient wild animal: it is the mismanagement state made flesh, produced only inside a pen. [spec 2d, `RM_Vhorrin` header] → biome_roster.vhorrin_never_ambient_and_probe_is_honest
- Every stocked catch item has its living pawn on the biome's roster (two-def law). [biome XML header, STOCKED_POOL spec 0/2] → biome_roster.stocked_catch_has_living_counterpart
- The biome's `fishTypes` carry the wild six, the six stocked catches and the rare-catch set, and `maxFishPopulation` is 660. [About.xml] → biome_roster.fish_types_wired
- The biome carries the water-truce `modExtensions` block (`RM_WaterTruceExtension`, radius 10). [About.xml; WATER_TRUCE_RETRIBUTION_1] → biome_roster.water_truce_extension_present
- The five stocked-pool recipes reach both the electric and the fuelled stove (a patch that matches nothing logs nothing). [`RM_StockedPoolRecipeWiring.xml`] → cuisine_wiring.recipes_on_both_stoves
- Every stocked-pool item carrying a Rottable comp has a ticker, so it actually rots (RM_HulduFat once did not). [commit `55d52a2fe`] → cuisine_wiring.rottable_items_tick
- The one Mod Setting, `stockedPoolsEnabled`, ships ON and its assembly is loaded. [`RM_WeepingStonesSettings.cs`] → settings_and_designator.setting_default_on_and_assembly_loaded
- With the setting ON the "Pool pen" zone designator is on the vanilla Zone tab (a patch that matches nothing logs nothing); with it OFF the designator is hidden. [`RM_PoolPenZoneOrdersPatch.xml`, `RM_Designator_ZoneAdd_PoolPen.cs`] → settings_and_designator.designator_listed_when_on, settings_and_designator.designator_hidden_when_off
- A pool pen can only be drawn over open water: a rect over dry floor makes no zone, and a rect straddling the shoreline makes one whose cells are exactly the water. [`RM_Designator_ZoneAdd_PoolPen.CanDesignateCell`] → pen_zone.pen_refuses_dry_floor, pen_zone.pen_covers_exactly_the_water
- NET: a handler nets a wild stockable pawn and it becomes its carryable breeding-stock item. [`RM_JobDriver_NetPoolBreeder.cs`] → job_net.net_turns_wild_pawn_into_breeding_stock
- STOCK: a handler carries breeding stock into a pen and releases a live pawn of its species there; the item is consumed. [`RM_JobDriver_StockPoolPen.cs`] → job_stock.stock_releases_species_pawn_into_pen
- STOCK refuses to release outside a pen. [the job's zone re-check] → job_stock_outside_pen.stock_outside_pen_releases_nothing
- FEED: a handler carries food to the pen and it is consumed there. [`RM_JobDriver_FeedPoolPen.cs`] → job_feed.feed_consumes_food_at_the_pen
- HARVEST: a handler takes a stocked pawn out of the pen and 2-4 units of the species meat appear. [`RM_JobDriver_HarvestPoolPen.cs`] → job_harvest.harvest_yields_species_meat
- CULL: a handler culls a vhorrin and 18-24 units of vhorrin meat appear (an enormous single harvest, sized to clear the Cull Feast alone). [`RM_JobDriver_CullVhorrin.cs`] → job_cull.cull_yields_enormous_harvest
- The invented flora that name a custom harvested item yield it: `RM_Bladderquill` gives `RM_BladderFruit`, `RM_Steamfrond` gives `RM_SeepSalt`, `RM_Dewgourd` gives `RM_DewgourdFruit`. [`RM_WeepingStonesNativeFlora.xml`] → flora_RM_Bladderquill.harvest_yields_RM_BladderFruit, flora_RM_Steamfrond.harvest_yields_RM_SeepSalt, flora_RM_Dewgourd.harvest_yields_RM_DewgourdFruit
- The pen's READ gauge reads Healthy, Thin, Silent or Vhorrin from a census of the pawns in the pen. → UNCOVERED: only `RM_Zone_PoolPen.GetInspectString` shows it and no bridge tool reads a Zone's inspect string; needs a companion `[Tool]`, to be filed as `POOL_ZONE_INSPECT_TOOL_1`.
- Not feeding a pen for 2 days thins it and for 3 days kills a resident; a crowded or crashed pen can grow a vhorrin; a pen holding vizhik loses one to an escape. → UNCOVERED: per-pulse random chances (3%, 2%/1%, 5% every 2500 ticks), statistical, no Boolean check (debug_process.md section 4). The sampling method is owed once one exists.
- With the setting OFF the pen bookkeeping pulse and the five work givers are inert. → UNCOVERED: the pulse is statistical (above) and forced jobs bypass the work-giver scanner; autonomous offering needs a day of game time with a due pen.
- `RM_BiomeWorker_WeepingStones.GetScore` scores hot, low-relief desert near water. → UNCOVERED: inert by `generatesNaturally=false`, so no map can exercise it.
- Kirruk and mirrik fly. → UNCOVERED: flyers are verified by a `Pawn_FlightTracker` state read only, never live unattended (CLAUDE.md, ruled 3 times); no such tool is declared for these species yet.
- The art is the placeholder retinted vanilla bodies; the Utinni fauna patch (`WildAnimals_WeepingStones.xml`) adds the Star Wars rows. → UNCOVERED: `visual` (art is the judge pass's) and the Utinni patch belongs to the UtinniPatches script, not this mod's.

## the walk
Run the script, not the prose: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod WeepingStones --plan src/RimMandrake/WeepingStones/northstar_plan.py` on the `weepingstones_solo` tier (live-run sheet: `Transient/worker_notes_WEEPING_STONES_FIRST_SCRIPT_1.md`). The 47 components run in 20 chains; a FAIL inside a setup component leaves the rest of its chain UNMEASURED.

## anti-guessing notes
- RULED OUT: "the pen needs a building, not a zone" — `RM_Zone_PoolPen : Zone` and the designator is a `Designator_ZoneAdd` on the vanilla Zone tab (`RM_Zone_PoolPen.cs`); the suite creates it through the real designator.
- RULED OUT: "a fish stays unwired because its wildAnimals row is missing" — the six stocked rows are wired and `RM_Murrin` is left off by design pending `FISH_BY_BIOME_1`'s successor (biome XML header); only `RM_Vhorrin` is asserted absent.
- RULED OUT: "About.xml says stocked pools ship OFF" — the C# default is `true` (`RM_WeepingStonesSettings.cs`, flipped in wave 4); the stale sentence was corrected in About.xml and `setting_default_on_and_assembly_loaded` pins the default.
- RULED OUT: reading `<wildAnimals>` through `jawa/get_defs` — a non-public list it cannot serialise (Pyrelands, 2026-10-01); the suite uses `jawa/biome_probe`, which reads the runtime caches.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
