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

## the walk
Run `src/RimMandrake/Webwork/validation.py` (static: `python3 validation.py`); live via the modcheck suite on a tier that loads `mandrake.rm.biomes` (or standalone with CreatureBehaviors).

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); no check reads a tile count.
RULED OUT: "the egg should hatch" — S6 ruling / ban 1: inert cargo, no CompHatcher; nest_egg_state guards that no hatcher comp appears.
RULED OUT: "the nest wall should register a web-node sense comp" — deliberately not wired (RM_CompSenseWebNode consumer unbuilt; WEBWORK_WEB_STRUCTURES_1 owns it).
