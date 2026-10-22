# RimMandrake: Webwork — validation walk
subject: src/RimMandrake/Webwork  (packageId `mandrake.rm.webwork`)
deps: `mandrake.rm.creaturebehaviors` (the sun-scald hediff class lives there)
list: biomes tier; when folded into mandrake.rm.biomes it is active under the composed name 'RimMandrake: Baroque Biomes' (reads here are by def name and settings type)
status-hint: WEBWORK_FIRST_SCRIPT_1 — jungle biome, ollathrix species, nest and egg economy; first script drafted, never run live

Sources: `src/RimMandrake/Webwork/About/About.xml` description, `Defs/**`, `Source/*.cs`, `Patches/RM_WebworkNestScatter_MapGenPatch.xml`.

## must be true
- Every def the mod ships (biome, 16 plants, 5 animals and kinds, the ollathrix, nest wall, egg clutch, egg, spit weapon, damage defs, hediffs, sounds, nest gen step) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- Every Mod Settings field round-trips through the bridge (numbers numerically) and is read by some other source file. → settings_roundtrip.settings_probe_finds_fields
- `RM_Webwork` has animalDensity and plantDensity above zero so its roster and flora can spawn at all. → biome_wiring.animal_and_plant_density_positive
- The biome carries its six animal rows. → biome_wiring.roster_rows_present
- The nest scatter step is on the shared map generator, so a generated Webwork map gets its nest. → biome_wiring.nest_scatter_step_on_map_common_base
- The nest wall carries the egg-clutch relay comp; the egg clutch mines to the egg. → nest_egg_state.nest_wall_carries_the_relay_comp, nest_egg_state.clutch_mines_to_the_egg
- The egg is inert Sellable contraband and must NOT carry a hatcher comp (ban 1). → nest_egg_state.egg_is_inert_contraband_with_no_hatcher
- The ollathrix is dormant-capable (ambush burst) and carries the turret-gun comp (loom spit). → nest_egg_state.ollathrix_is_dormant_capable_with_a_turret_gun
- Sun-scald resolves to the CreatureBehaviors hediff class. → scald_binding.sun_scald_hediff_class_is_the_creature_behaviors_one
- A guaranteed nest is laid on every generated Webwork map, and none with `nestEnabled` off. → UNCOVERED: the bridge cannot generate a map (map_mechanics.nest_placed_at_mapgen records UNMEASURED)
- A mined-out clutch re-seeds every 20-30 days while an ollathrix lives. → UNCOVERED: needs 20-30 game days and a live ollathrix
- Destroying a comp-carrying harvest thing may spawn an ollathrix. → UNCOVERED: statistical, and no shipped def carries the comp yet
- Ollathrix take sun-scald in open sun and fire the loom spit. → UNCOVERED: needs a spawned ollathrix, light and ticks or a target
- `generateOnWorldgen` decides whether the biome competes for tiles. → UNCOVERED: inert (no worldgen feature, frozen world)
- A Webwork map is laid with thick web cables (slow to climb, never impassable, trees still grow through them), thinner sticky local webs near them, and silk carpet only within a few cells of the spider sites; the step lays nothing off-biome, and each of webNetworkEnabled / siteCarpetEnabled / localWebDensityMultiplier=0 turns its part off. → web_terrain_weather.web_network_laid
- Webfall sits in RM_Webwork's weather table at webfallCommonality, can be made the current weather, never dims the sun (the light-moat holds), and is gone with webfallEnabled off. → web_terrain_weather.webfall_in_biome_and_occurs
- The web and carpet appear on a really GENERATED Webwork map. → UNCOVERED: the bridge cannot generate an RM_Webwork map (biome on 0 tiles until the end paint); PlaceWeb runs on the current map instead
- Urraveth remains (WEBWORK_DEAD_GIANT_BUILD_1): at site chance 0 nothing is placed; at chance 1 one wrapped piece per layout row is laid (every `RM_Urraveth_*` def present). → urraveth_remains.site_chance_zero_places_none, urraveth_remains.site_places_every_piece_wrapped
- Reading a wrapped piece cuts its wrapping, records its chapter and drops thrixweave of the configured size beside it. → urraveth_remains.reading_one_piece_cuts_its_wrapping
- With every piece read, opening the skull completes the reading with the four chapters in order (pinned, bound, cut, eaten) and draws the outline. → urraveth_remains.all_read_then_skull_opens_complete
- An unloaded piece never creaks (60,000 ticks); a loaded rib creaks for the full warning window, and taking the load off ends it harmlessly. → urraveth_remains.unloaded_bones_never_creak, urraveth_remains.load_creaks_and_clearing_saves_it
- A rib left loaded past its window collapses into rubble, hurts who is under it, and the piece it held up starts creaking. → urraveth_remains.load_left_collapses_with_rubble_and_spreads
- The urraveth site is laid inside real Webwork mapgen at about 1 map in 4. → UNCOVERED: the bridge cannot generate an RM_Webwork map (0 tiles until the end paint); ProofSite runs the same PlaceSite on the current map
- Traction lance (WEBWORK_TRACTION_LANCE_BUILD_1; the pull is CreatureBehaviors' RM_CompTetherPull): a manned thrixweave lance reels a raider toward it; an unmanned one ropes nothing; a steel wall stops the pull with reason "wall"; a downed colonist is pulled in (friendly pull on). → traction_lance.manned_lance_pulls_a_raider, traction_lance.unmanned_lance_does_nothing, traction_lance.wall_stops_the_pull, traction_lance.downed_colonist_pulled_in
- The tether is fabric-tiered: a thrumbo snaps a cloth tether for mass, and cloth is snappier and shorter-reaching than thrixweave. → traction_lance.over_mass_target_snaps_a_cloth_tether, traction_lance.cloth_weaker_than_thrixweave
- Friendly pull OFF leaves a downed colonist (the production target choice, FindTarget, with the setting read on as the control then off); a wild ollathrix reeled by a thrixweave lance from a shaded cell (roofed: the canopy stand-in) ends on a cell the sun-scald predicate reads exposed; the gutter-junction and Sump draw-joint studies each finish RM_Research_TractionLance from unfinished and make RM_TractionLance buildable. → traction_lance.friendly_pull_off_leaves_a_downed_colonist, traction_lance.ollathrix_pulled_from_shade_into_sun, traction_lance.gutter_junction_study_teaches_the_lance, traction_lance.sump_drawjoint_study_teaches_the_lance
- Webwork siege (WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE): siegeEnabled off refuses the siege; on (test hook on) lets it fire; with the hook off a map that does not border the Webwork, or whose shade the grid cannot measure, or that is too little shaded, refuses with that reason (fails closed). → siege.setting_off_refuses, siege.unshaded_or_unbordered_map_refuses
- A forced siege arrives as one lord of awake RM_Ollathrix of the insect faction. → siege.fires_and_spawns_awake_ollathrix
- A siege spider given a spin job works its ticks and leaves one siege web, tagged with its siege, on a cell the sun-scald predicate reads unexposed. → siege.spider_spins_a_web_on_an_unexposed_cell
- Siege silk slicks a colonist standing in it and never an ollathrix. → siege.siege_web_slicks_others_not_ollathrix
- Cutting one siege's webs yields exactly min(cap, cuts x 2) thrixweave; silk broken by force yields none. → siege.cut_yield_is_capped_per_siege
- A wrapped door opens for no one until the wrap is cut; an unwrapped door beside it opens throughout. → siege.wrapped_door_shut_until_cut
- A downed colonist is taken into a cocoon; Open frees them alive; left past siegeCocoonDeathHours they die of silk suffocation, not a tick before. → siege.cocoon_cut_open_frees_the_colonist, siege.cocoon_kills_after_the_deadline
- Losing half the spiders breaks the siege (exit toil) with its letter. → siege.half_lost_breaks_the_siege
- A natural siege fires on a real shaded map bordering the Webwork. → UNCOVERED: the Webwork sits on 0 tiles until the end paint (CLAUDE.md); the test hook stands in
- Under the storyteller, spiders spin toward the colony over hours, press when their silk nears it, and leave after siegeMaxDays. → UNCOVERED: game hours of real ticks; watched in play

## the walk
Run `src/RimMandrake/Webwork/validation.py` (static: `python3 validation.py`); live via the modcheck suite on a tier that loads `mandrake.rm.biomes` (or standalone with CreatureBehaviors).

## north star
state: DRAFT
validated-hash:

### the experience  (OWNER'S WORDS)
"So quiet that you know you're in terrible danger. It makes treasure, it eats all, and it's coming for you."
(typed by the owner, 2026-10-20)

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); no check reads a tile count.
RULED OUT: "the egg should hatch" — S6 ruling / ban 1: inert cargo, no CompHatcher; nest_egg_state guards that no hatcher comp appears.
RULED OUT: "ProofLoad clear/idle can be reached as 'N|clear'" — jawa/static_call splits args on '|' into parameters; until 2026-10-22 ProofLoad split only on '|', so its modes were unreachable from the script (mock_urraveth's "pipe" case guards it).
RULED OUT: "the nest wall should register a web-node sense comp" — deliberately not wired (RM_CompSenseWebNode consumer unbuilt; WEBWORK_WEB_STRUCTURES_1 owns it).
