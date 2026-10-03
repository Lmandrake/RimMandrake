# RimMandrake: Moving Dunes — validation walk
subject: src/RimMandrake/MovingDunes  (packageId `mandrake.rm.movingdunes`)
deps: `brrainz.harmony`, Odyssey (the SandGrid is Odyssey's; without it the mod is inert)
status-hint: MOVING_DUNES_FIRST_SCRIPT_1 — first script drafted, never run live; needs a Desert/ExtremeDesert map for the engine chains

Sources: `src/RimMandrake/MovingDunes/About/About.xml` description, `Defs/**`, `Patches/BiomeBindings.xml`, `Source/MovingDunesMod.cs`, `Source/MovingDunesSettings.cs`, `Source/MovingDunesDebugActions.cs`, `Source/MapComponent_DuneField.cs`.

## must be true
- Every def the mod ships (the buried-cache ThingDef, the globals def, the sand material def) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- Every Mod Settings field (`duneEngineEnabled`, `transportRateMultiplier`, `burialEnabled`, `plantChokeEnabled`, `windLockEnabled`, `clearYieldEnabled`, `clearYieldMultiplier`) round-trips. → settings_roundtrip.duneEngineEnabled_round_trips, settings_roundtrip.transportRateMultiplier_round_trips, settings_roundtrip.burialEnabled_round_trips, settings_roundtrip.plantChokeEnabled_round_trips, settings_roundtrip.windLockEnabled_round_trips, settings_roundtrip.clearYieldEnabled_round_trips, settings_roundtrip.clearYieldMultiplier_round_trips
- The four Harmony rules are attached (sand holds on sand terrain, ambient decay suppressed, vanilla sand layer suppressed on skinned maps, shovelled drift yields): each is a patch owned by `mandrake.rm.movingdunes`. → harmony_rules.rule_sand_holds_on_sand_attached, harmony_rules.rule_ambient_decay_suppression_attached, harmony_rules.rule_vanilla_sand_layer_suppression_attached, harmony_rules.rule_clear_sand_yield_attached
- Vanilla Desert and ExtremeDesert carry the DuneFieldExtension. → biome_bindings.Desert_carries_dune_field_extension, biome_bindings.ExtremeDesert_carries_dune_field_extension
- A dune-field map has a wind that shifts, and the engine reports its rules armed. → dune_field_report.map_is_a_dune_field_and_rules_armed, dune_field_report.shift_wind_changes_the_wind (UNMEASURED unless the current map is a dune-field biome)
- Drift can be run and the sand total stays readable. → dune_field_report.batches_run_and_report_stays_readable
- Sand erodes off crests, hops downwind and banks behind shelter. → slow_crests_hop_downwind_and_bank_in_shelter.state_read (UNMEASURED: seed drift is a mouse tool; many game hours)
- Sand blowing off the downwind edge is gone and fresh sand arrives upwind. → slow_upwind_influx_and_downwind_loss.state_read (UNMEASURED: day-scale accumulator)
- Loose gear is buried, stops deteriorating, and comes back out when the drift erodes. → slow_loose_gear_buried_and_returns.state_read (UNMEASURED: game days)
- Plants under deep drift choke and die. → slow_deep_drift_kills_plants.state_read (UNMEASURED: game days)
- On the Stillsand the wind is locked to the sun bearing. → slow_wind_locked_to_the_sun_on_stillsand.state_read (UNMEASURED: needs an RM_Stillsand map)
- Shovelled drift yields the biome's sand item. → slow_shovelled_drift_yields_sand.state_read (UNMEASURED: needs a colonist job on an RM_Stillsand map)
- The vanilla ambient-decay and sandstorm constants the patches ride have not drifted. → UNCOVERED: `Source/selftest_moving_dunes_constants.py` reads the decompiled source offline

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `MovingDunesSettings`   # settings_roundtrip
3. [D] `jawa/harmony_patches` on the four target methods and a control method   # harmony_rules
4. [D] `jawa/get_defs BiomeDef/Desert,ExtremeDesert fields modExtensions`   # biome_bindings
5. [B] `rimworld/execute_debug_action` report / shift wind / run 100 batches, read from the call's own logs   # dune_field_report (UNMEASURED off a dune-field map)
6. [B] day-scale mechanics   # slow_* (UNMEASURED until a drivable route exists)
X. [S] (human pass) dunes look right and creep slowly; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the debug-action path is `Moving Dunes\\...`" — sibling mods (FloodedCanyon) drive `Actions\\<label>` whatever their category string; the report chain records UNMEASURED, never FAIL, if the path does not answer.
RULED OUT: "a wind that never changes is a defect on a still-wind map" — only RM_Stillsand locks it (windLockEnabled); the shift check runs on a normal dune field.
