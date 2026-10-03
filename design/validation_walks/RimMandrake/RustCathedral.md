# RimMandrake: the Rust Cathedral — validation walk
subject: src/RimMandrake/RustCathedral  (packageId `mandrake.rm.rustcathedral`)
deps: `sarg.alphabiomes` (floor and world icon pixels), `mandrake.rm.creaturebehaviors` (roach eat-cleanable node)
list: biomes tier; when folded into mandrake.rm.biomes it is active under the composed name 'RimMandrake: Baroque Biomes' (reads here are by def name, Harmony id and settings type)
status-hint: RUST_CATHEDRAL_FIRST_SCRIPT_1 — mechanoid plateau biome plus the absorbed Hum and Walls kits and the roaches; first script drafted, never run live

Sources: `src/RimMandrake/RustCathedral/About/About.xml` description, `Defs/**`, `Source/RustCathedral/RM_RustCathedralMod.cs`, `Source/Hum/*`, `Source/Walls/*`, item `RUST_CATHEDRAL_MECHANICS_1`.

## must be true
- Every def the mod ships (biome, terrain, gen steps, bolts, roaches, eel, walls, curiosity, attitude def, hum sounds, coolant hediff, drill-response incident) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves, defs_resolve.namespaced_attitude_def_resolves
- Every Mod Settings field of the three settings classes (own, Hum, Walls) round-trips through the bridge and the absorbed fields are Scribed by the one registered settings class. → settings_roundtrip.settings_probe_finds_fields_in_all_three_classes
- `RM_RustCathedral` has animalDensity > 0 so its roster (roach, mecharat, living bolt) can spawn at all. → biome_wiring.animal_density_positive_and_deep_read_succeeds
- The biome carries its roster, the coolant-eel fish type and the two forced rock types. → biome_wiring.roster_fish_and_rock_rows_present
- The biome has NO wild plants (ruled zero, frozen sheet ban 7, never a gap). → biome_wiring.wild_plants_stay_empty_ruled_zero
- The two wall scatter steps are on the shared map generator so a generated Cathedral map lays its wall tiers. → biome_wiring.wall_scatter_steps_on_map_common_base
- The hum attitude def targets this biome with four thresholds (five bands). → hum_attitude.attitude_def_targets_this_biome
- The deep-scan live pattern metal gate, the watched-bolt hooks, the eel catch hook and the infestation replacement are installed as Harmony patches. → harmony_gates.CompDeepScanner_ChooseLumpThingDef_patched_by_rustcathedralwalls, harmony_gates.Pawn_Kill_patched_by_rustcathedralhum, harmony_gates.CompSpawner_TryDoSpawn_patched_by_rustcathedralhum, harmony_gates.WaterBodyTracker_Notify_Fished_patched_by_rustcathedralhum, harmony_gates.IncidentWorker_DeepDrillInfestation_CanFireNowSub_patched_by_rustcathedralhum
- The roach cleans only while `roachCleaningEnabled` is on: its think tree wraps the eat-cleanable node in the toggle node. → roach_gate.think_tree_carries_cleaning_toggle_node
- Bolts dance with the hum and freeze first at the worst band. → UNCOVERED: needs a generated Cathedral map or a bolt plus an attitude read tool, and game time (map_mechanics.bolts_dance_and_freeze_with_the_hum records UNMEASURED)
- Carrying a curiosity or killing a bolt irritates the hum silently. → UNCOVERED: no tool reads the attitude value
- Coolant eel catches carry a consequence. → UNCOVERED: needs a fishing job on a generated map
- The deep-drill response replaces the vanilla infestation. → UNCOVERED: fire_incident dry-run cannot give an honest read
- Deck plate, dead smartsteel and the sacred wall are laid at mapgen. → UNCOVERED: the bridge cannot generate a map
- The hum drains Forsaken goodwill at the worst band. → UNCOVERED: needs hours of game time and a faction relation
- Roaches seek filth to eat. → UNCOVERED: needs a spawned roach, filth and ticks; wiring is read in roach_gate

## the walk
Run `src/RimMandrake/RustCathedral/validation.py` (static: `python3 validation.py`); live via the modcheck suite on a tier that loads `mandrake.rm.biomes` (or the standalone mod). Reads are by def name, so the composed name does not matter.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1); no check reads a tile count.
RULED OUT: "empty wildPlants is a gap" — ruled zero (frozen sheet hard ban 7, roster flora_purged); biome_wiring guards that it stays empty.
RULED OUT: "the roaches belong to the hum mechanics" — owner 2026-09-07: leave them out for now; the roach gate reads only the cleaning toggle.
RULED OUT: "a second GetSettings<T>() persists the absorbed kits" — Verse.Mod caches one instance (RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1); static_checks asserts every absorbed field is Scribed by the one registered class.
