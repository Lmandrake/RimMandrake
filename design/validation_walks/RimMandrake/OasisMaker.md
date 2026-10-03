# RimMandrake: Oasis Maker — validation walk
subject: src/RimMandrake/OasisMaker  (packageId `mandrake.rm.oasismaker`)
deps: none beyond Core (loadAfter Ludeon.RimWorld); spec `design/RimMandrake/oasis_maker_machines_spec.md`
status-hint: OASIS_MAKER_FIRST_SCRIPT_1 — first script drafted, never run live; the site chains build a roofed sand pad ringed by rough granite

Sources: `src/RimMandrake/OasisMaker/About/About.xml` description, `Defs/ThingDefs_Buildings/RM_OasisMaker.xml`, `Source/RM_CompOasisMaker.cs`, `Source/RM_OasisPlacementScorer.cs`, `Source/RM_PlaceWorker_OasisMaker.cs`, `Source/RM_OasisMakerSettings.cs`.

## must be true
- `RM_OasisMaker` loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- Every Mod Settings field (`masterEnabled`, `shadeScoreFloor`, `rockScoreFloor`, `scoringRadius`, `shadeScoreExcellent`, `rockScoreExcellent`, `attuningDays`, `baseRingDays`, `ringGrowthFactor`, `minRadiusCap`, `maxRadiusCap`) round-trips. → settings_roundtrip.masterEnabled_round_trips, settings_roundtrip.shadeScoreFloor_round_trips, settings_roundtrip.rockScoreFloor_round_trips, settings_roundtrip.scoringRadius_round_trips, settings_roundtrip.shadeScoreExcellent_round_trips, settings_roundtrip.rockScoreExcellent_round_trips, settings_roundtrip.attuningDays_round_trips, settings_roundtrip.baseRingDays_round_trips, settings_roundtrip.ringGrowthFactor_round_trips, settings_roundtrip.minRadiusCap_round_trips, settings_roundtrip.maxRadiusCap_round_trips
- The machine is minifiable and sold as exotic goods, with our place worker, and is not buildable (trade or scenario start only). → def_wiring.minified_trade_tagged_and_placeworker_ours, def_wiring.not_buildable_trade_or_start_only
- On ground with no shade and no rock it stays Dormant. → dormant_on_bare_sand.no_shade_no_rock_stays_dormant
- On shaded ground beside standing rock it wakes (Attuning). → site_growth.valid_site_attunes
- With the master switch off it grows nothing. → site_growth.master_off_stops_growth
- It then grows an oasis ring by ring until it reads "The oasis is made." (checked at fast settings). → site_growth.fast_settings_finish_an_oasis
- The centre ends as shallow water and it never converts stone. → site_growth.centre_holds_water_and_rock_is_never_converted
- Losing shade freezes it (Dormant) and nothing already converted is taken back. → site_growth.losing_shade_freezes_and_nothing_reverses
- Placement is guided by a live green/red footprint and refuses below the floor with a reason. → placement_gate.ghost_is_red_below_the_floor_with_a_reason (UNMEASURED: needs a held placement ghost)
- The shipped 2-day attuning and 3-day first ring. → slow_timing.shipped_attuning_and_ring_times (UNMEASURED: game days)
- A grown pool cell fires `RM_OasisPoolIntegration.PoolCellCreated` for the Stocked Pool kit. → UNCOVERED: no subscriber exists yet (STOCKED_POOL_BUILD_1) and the bridge cannot read a C# event; a subscriber's own script owns it
- The comb-silhouette art. → UNCOVERED: placeholder texture; art is a separate sprite pass

## the walk
1. [D] `jawa/get_defs ThingDef/RM_OasisMaker`; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field   # settings_roundtrip
3. [D] `jawa/get_defs` deep: minifiedDef, tradeTags, placeWorkers, designationCategory, costList   # def_wiring
4. [D] clear a 25x25 pad of Sand, spawn the machine, wait 600 ticks, `jawa/inspect_string`   # dormant_on_bare_sand
5. [D] roof 19x19 and lay two rough-granite strips, spawn the machine, read Attuning; set masterEnabled off + fast settings, read not finished; on, read "The oasis is made."; `jawa/get_terrain_batch` for WaterShallow and intact strips; remove the roof, read Dormant and the pool intact; restore every setting   # site_growth
6. [B] placement ghost, game-day timing   # placement_gate, slow_timing (UNMEASURED)
X. [S] (human pass) the oasis reads as a patient weeping of damp ground; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "fast settings change the mechanism" — attuningDays 0 and baseRingDays 0.001 only shorten the clocks; they are restored in a finally and the shipped timing is its own UNMEASURED line.
RULED OUT: "the placement floor is a spawn check" — the PlaceWorker gates the designator only; spawn_batch routes through GenSpawn, so the bare-sand chain tests the comp's own ValidNow, never the refusal message.
