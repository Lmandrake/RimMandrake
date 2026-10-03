# RimMandrake: Proximity Hatch — validation walk
subject: src/RimMandrake/ProximityHatch  (packageId `mandrake.rm.proximityhatch`)
deps: none (Harmony-free engine comp); behaviour is read on a carrier egg a campaign mod wires it onto (`RM_DrazzikEggFertilized`, `RM_GuzzkaEggFertilized` in Stillsand; `RSW_DrazzikEggFertilized` and `RSW_ProtovermesEggFertilized` via SWBestiary patch; BrainWorms `RSW_BrainWormEggCluster`)
list: a tier carrying this mod plus Stillsand or SWBestiary (any carrier egg), plain open map
status-hint: PROXIMITY_HATCH_FIRST_SCRIPT_1 — engine comp only, ships no defs; first script drafted, never run live

Sources: `src/RimMandrake/ProximityHatch/About/About.xml`, `Source/CompProximityHatch.cs`, `Source/CompProperties_ProximityHatch.cs`, `Source/RM_ProximityHatchMod.cs`; carrier eggs found by scanning the repo XML for the comp class.

## must be true
- A control def name reads notFound, so the def probe can say no; the mod ships no defs of its own and at least one carrier egg resolves. → defs_resolve.control_probe_can_say_absent, defs_resolve.mod_ships_no_defs_and_a_carrier_resolves
- Every Mod Settings field (`enabled`, `radiusMultiplier`, `scanIntervalMultiplier`, `aggroEnabled`) round-trips. → settings_roundtrip.enabled_round_trips, settings_roundtrip.radiusMultiplier_round_trips, settings_roundtrip.scanIntervalMultiplier_round_trips, settings_roundtrip.aggroEnabled_round_trips
- A carrier egg carries the proximity comp. → carrier_wiring.carrier_egg_reads_the_proximity_comp
- An egg with no pawn near it stays an egg. → hatch_behaviour.control_egg_alone_does_not_hatch
- A live flesh pawn inside the radius forces an early hatch and the hatchling is aggroed (ManhunterPermanent). → hatch_behaviour.pawn_in_range_hatches_early_and_ambushes
- With `enabled` off the egg only ever hatches on its own timer. → hatch_behaviour.enabled_off_egg_stays
- `radiusMultiplier` scales each egg's own trigger radius. → hatch_behaviour.radius_multiplier_shrinks_trigger
- With `aggroEnabled` off the egg still hatches early but the hatchling is not manhunter. → hatch_behaviour.aggro_off_hatchling_not_manhunter
- `scanIntervalMultiplier` slows the scan (higher = checks less often). → not_driven.scan_interval_multiplier_slows_the_scan (UNMEASURED: needs a countdown reader)
- `hatchFired` survives save/load so a re-entrant tick cannot double-fire. → not_driven.hatch_fired_persists_through_save_load (UNMEASURED: save/load)
- A cold egg spoils into an unfertilized egg instead of hatching (CompHatcher's own branch, reused). → not_driven.cold_egg_spoils_not_hatches (UNMEASURED: cold site)
- A litter-mate of the same kind standing on the egg's cell is never aggroed by mistake (the `preHatch` snapshot, commit 9411247f8). → UNCOVERED: needs two eggs hatching in one tick and a way to read which of two identical pawns is manhunter; filed as a gap, not a missing tool

## the walk
1. [D] `jawa/get_defs` on a bogus egg: notFound; on the derived carrier list: at least one found   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on the four fields   # settings_roundtrip
3. [D] `jawa/get_defs ThingDef/<carrier> fields comps deep=True`   # carrier_wiring
4. [B] clear 24x24; spawn the carrier egg; colonist at distance 1; wait 150 ticks; `jawa/list_things` for the egg, `jawa/list_pawns` for the hatchling, `jawa/pawn_mental` list for its state; repeat per setting   # hatch_behaviour
5. [B] cadence, save/load, cold   # not_driven (UNMEASURED)
X. [S] (human pass) the hatch reads as an ambush: the hatchling comes at you the moment you step in; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the mod ships defs to resolve" — About.xml and the folder have no Defs/; the engine is one comp type, so the carrier egg is the only def surface.
RULED OUT: "a colonist beside the egg hatches it by walking in on a later scan" — `ticksUntilScan` starts at 0, so the first tick scans; the checks wait 150 ticks (two scans) and read the egg, not a cadence.
