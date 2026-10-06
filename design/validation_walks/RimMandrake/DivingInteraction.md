# RimMandrake: Deep Diving — validation walk
subject: src/RimMandrake/DivingInteraction  (packageId `mandrake.rm.divinginteraction`)
deps: Fold-aware: folded into `mandrake.rm.biomes` (Biomes.compose.json entry DivingInteraction); the composed mod's script covers it only through these lines. Reads TerminalBiomes' sea BiomeDefs and floor scatter GenSteps.
list: a tier carrying the composed biomes mod, all five DLCs, a world with the RM_SeabedLayer registered (any quicktest world)
status-hint: the sea-floor planet layer (RM_SeabedLayer), one floor biome + generator per sea, and the Scald/Chill floor content. Script: `src/RimMandrake/DivingInteraction/validation.py`. NEVER RUN LIVE. The floor-map chain needs the companion DLL with `jawa/world_tile_map_generate layer=` (source 2026-10-06; deploys at the next restart).

Sources: `Defs/PlanetLayerDefs/` (RM_SeabedLayer, RM_SeabedFloorBiomes), `Defs/MapGeneration/` (RM_SeabedGenerators, RM_SeaDiveGenerators), `Source/RM_SeabedSiteParent.cs`, `Patches/RM_SeabedFloorBiomeWiring.xml`, TerminalBiomes `RM_GreySea.xml` and `RM_GreySeaFloorScatter.xml`.

## must be true
- Each terminal sea's surface biome names its own floor biome, and every floor biome exists. → per_sea_floor_biomes.floor_biomes_defined, per_sea_floor_biomes.sea_biomes_name_their_floor
- Each floor biome names a layer generator carrying its hatch twin's content, never roofed, with no exit. → seabed_floor_generators.floor_biomes_name_layer_generators, seabed_floor_generators.layer_generators_match_hatch_content, seabed_floor_generators.live_floor_generates_sea_content
- Each floor holds its sea's temperature and carries the sea's flora and cast at startup. → seabed_floor_ambient_carryover.floor_temperature_matches_hatch, seabed_floor_ambient_carryover.floor_biomes_carry_sea_life
- A map made on the Grey Sea's floor tile runs the Grey generator, has salt pillars and at least two crystal colours, grows at least three of its ruled plants, carries its cast and no animal from outside it. → grey_floor_is_a_place.grey_roster_read_offline, grey_floor_is_a_place.grey_floor_map_generates, grey_floor_is_a_place.grey_floor_has_pillars_and_crystals, grey_floor_is_a_place.grey_floor_grows_its_flora, grey_floor_is_a_place.grey_floor_carries_its_cast, grey_floor_is_a_place.grey_floor_returns_home
- The Scald immersion berth never seals a ship or blocks launch. → scald_immersion_berth.scald_floor_biome_present, scald_immersion_berth.berth_never_seals_or_blocks_launch
- The Scald walker grazes the mat open and the crew follows the herd and backs off. → scald_walking_pasture.walker_def_present_and_in_scald_roster, scald_walking_pasture.walker_grazing_exposes_mat, scald_walking_pasture.crew_follows_herd_and_backs_off
- Scald vent fields warn before every discharge. → scald_vent_fields.vent_flora_and_sailor_defs, scald_vent_fields.scald_generator_lists_vent_field_only, scald_vent_fields.forecast_warns_before_every_discharge
- The Scald return gallery cannot reach live systems. → scald_return_gallery.gallery_defs, scald_return_gallery.scald_generator_lists_gallery_only, scald_return_gallery.gallery_cannot_reach_live_systems
- The Chill return comb is inert scenery laid on the live floor. → chill_return_comb.comb_defs, chill_return_comb.chill_generator_lists_comb_only, chill_return_comb.comb_is_inert_scenery, chill_return_comb.comb_laid_on_live_floor
- The Chill dive animal count follows its roster. → chill_dive_density_sampler.offline_sampler_reads_roster, chill_dive_density_sampler.weighted_draw_obeys_count, chill_dive_density_sampler.live_dive_animal_count
- Every Mod Settings toggle gates its behaviour. → toggle_gates.chill_fire_gate_is_wired_into_vanilla_fire, toggle_gates.sentinel_and_pool_share_one_consequence, toggle_gates.live_floor_content_and_animal_count

## anti-guessing notes
RULED OUT: "the Grey floor cannot be checked until the planet is painted" — the floor-map chain sets the layer tile's biome itself (`biome=`), so an unpainted world checks out; 0 RM_GreySea tiles is the expected mid-migration state (CLAUDE.md).
RULED OUT: "a floor map needs a gravship landing" — `world_tile_map_generate layer=RM_SeabedLayer` makes the layer's DefaultWorldObject (RM_SeabedSite), whose MapGeneratorDef override is the same one a landing uses (RM_SeabedSiteParent.cs).
RULED OUT: "the floor biome's animalDensity 0 means an empty floor" — RM_SeabedFloorLife copies the sea's cast at startup; only a live census of the floor map answers it.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
