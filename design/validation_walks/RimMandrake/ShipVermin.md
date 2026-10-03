# RimMandrake: Ship Vermin — validation walk
subject: src/RimMandrake/ShipVermin  (packageId `mandrake.rm.shipvermin`)
deps: `mandrake.rm.biomes` (carries CreatureBehaviors: breeder, pressure/seek/gnaw extensions, alert base), `mandrake.rsw.swbestiary` (RSW_Mynock); the wreck-nest wiring is `mandrake.rut.patches` + Odyssey (`ShipChunk_Mech`)
list: a tier carrying ShipVermin + SWBestiary + the composed biomes mod; add UtinniPatches and Odyssey for the wreck_nest chain (UNMEASURED without them); plain open map
status-hint: SHIP_VERMIN_FIRST_SCRIPT_1 — patch + alert + wreck-nest comp, no Defs/ of its own; first script drafted, never run live (WRECKAGE_VERMIN_SPAWN_1's own live verify is still owed)

Sources: `About/About.xml`, `Patches/RSW_Mynock_ShipVermin.xml`, `Source/RM_ShipVerminMod.cs` (8 settings, nest roster), `RM_Alert_ShipVermin.cs`, `RM_CompVerminNest.cs`, `RM_CompProperties_VerminNest.cs`, `Source/Debug/RM_ShipVerminDebugActions.cs`, `src/RimUtinni/UtinniPatches/Patches/WreckVerminNest_ShipChunk.xml`.

## must be true
- The mod ships no Defs; a bogus def reads notFound, and the patch target `RSW_Mynock` (ThingDef and PawnKindDef) resolves. → defs_resolve.control_probe_can_say_absent, defs_resolve.patch_target_species_resolves
- Every Mod Settings field (`alertEnabled`, `wreckSpawningEnabled`, `wreckSpawnRateMultiplier`, `spawnMynock`, `spawnScavrat`, `spawnWompRat`, `spawnFuelmite`, `spawnRat`) round-trips. → settings_roundtrip.alertEnabled_round_trips, settings_roundtrip.wreckSpawningEnabled_round_trips, settings_roundtrip.wreckSpawnRateMultiplier_round_trips, settings_roundtrip.spawnMynock_round_trips, settings_roundtrip.spawnScavrat_round_trips, settings_roundtrip.spawnWompRat_round_trips, settings_roundtrip.spawnFuelmite_round_trips, settings_roundtrip.spawnRat_round_trips
- The breeder comp and pressure extension (tag ShipVermin, soft cap 3, hard cap 12) reached RSW_Mynock; a control def has no ShipVermin tag. → mynock_patch.breeder_and_pressure_extension_reached_the_mynock
- The mynock lives outside a hull (VacuumResistance in its stats). → mynock_patch.mynock_is_vacuum_proof
- The nest can always spawn something (Rat resolves), no roster species is a dead row, and the Mynock row matches the ported species. → nest_roster.rat_always_resolves_so_the_roster_is_not_dead, nest_roster.roster_resolution_reported, nest_roster.mynock_row_matches_the_ported_species
- The population alert is absent with no mynock aboard, present with mynocks, and hidden by `alertEnabled` off. → alert.absent_with_no_mynock_present_with_mynocks, alert.alert_off_hides_it
- Wreckage can be a nest: the wreck def carries the nest comp; a forced attempt spawns a wild pawn. → wreck_nest.wreck_carries_the_nest_comp, wreck_nest.forced_attempt_spawns_a_wild_pawn
- The per-species checkboxes decide what a nest produces (none = nothing; only Rat = a Rat). → wreck_nest.all_species_off_spawns_nothing, wreck_nest.only_rat_on_spawns_a_rat
- A nest and a breeding population press against ONE hard cap of 12. → wreck_nest.hard_cap_refuses_a_spawn
- The rate multiplier shortens the next-spawn countdown. → wreck_nest.rate_multiplier_shortens_next_spawn
- Mynocks breed under the soft cap, gnaw conduits/lights/floor, and drift to the hull. → not_driven.mynock_breeds_under_the_soft_cap, not_driven.mynock_gnaws_conduits_lights_and_floor, not_driven.mynock_seeks_the_substructure_hull (UNMEASURED: game days / forced-job tool / landed gravship)
- `wreckSpawningEnabled` off stops the nest timer. → not_driven.wreck_spawning_off_stops_the_timer (UNMEASURED: days; the debug path bypasses the gate)
- A nest's countdown survives save/load. → not_driven.nest_countdown_survives_save_load (UNMEASURED: save/load)
- The mynock art. → UNCOVERED: no bespoke sprite ships yet (About.xml says the art pass is future work)

## the walk
1. [D] `jawa/get_defs` bogus def; `ThingDef/RSW_Mynock`, `PawnKindDef/RSW_Mynock`   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on all 8 fields   # settings_roundtrip
3. [D] `jawa/get_defs fields comps,modExtensions deep=True` on RSW_Mynock vs the Rat control; `statBases`   # mynock_patch
4. [D] `jawa/get_defs PawnKindDef/<each roster name>`   # nest_roster
5. [B] spawn 2 `RSW_Mynock`, wait 320 ticks, `jawa/alerts_list`; toggle off   # alert
6. [B] spawn `ShipChunk_Mech`; `rimworld/execute_debug_action` "Force nest spawn attempt (click wreck)" at its x,z, read `effects.logs` and `jawa/list_pawns`   # wreck_nest
7. [B] days-of-ticks, gnaw, gravship, save/load   # not_driven (UNMEASURED)
X. [S] (human pass) a wreck feels infested by something you can hunt, not a spawner you can see; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the mod ships defs to resolve" — About.xml and the folder have no Defs/; its surface is a patch onto RSW_Mynock, an alert class and a comp, so the checks read the patched def, the alert list and the nest.
RULED OUT: "the debug attempt proves the wreckSpawningEnabled gate" — `AttemptSpawn` never reads it, only `CompTick` does; the toggle's effect is listed UNMEASURED rather than inferred from a forced attempt.
RULED OUT: "a failed get_defs on `modExtensions` means the patch is missing" — get_defs returns record lists as bare type names unless deep=True and modExtensions as values; the check fails only on a readable, empty list.
