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
- Drift speed scales transport attempts; sand actually moves on a dune-field map under wind (UNMEASURED off one / in calm); banking in a wall lee stays UNMEASURED (no seed tool). → slow_crests_hop_downwind_and_bank_in_shelter.transport_attempts_scale_with_the_drift_slider, .sand_actually_moves_on_a_dune_field, .banking_in_a_wall_lee_state_read
- Influx baseline scales with the drift slider once and the loss term is not squared by it; engine-off gate reads duneEngineEnabled; day-scale edge loss UNMEASURED. → slow_upwind_influx_and_downwind_loss.influx_baseline_scales_with_the_drift_slider_once, .loss_term_is_not_squared_by_the_slider, .engine_off_gate_reads_duneEngineEnabled
- Loose gear is buried by the real burial API, only wild unforbidden items qualify, burialEnabled off buries nothing (dune map). → slow_loose_gear_buried_and_returns.burial_api_caches_the_thing_and_removes_it_from_the_map, .only_wild_unforbidden_loot_is_a_burial_candidate, .burialEnabled_off_arm_buries_nothing; advancing-drift burial and wind-turn return stay UNMEASURED (game days)
- Plant choke sizing kills a buried plant in plantChokeDays and the gate reads plantChokeEnabled. → slow_deep_drift_kills_plants.choke_sample_rate_scales_with_the_drift_slider, .choke_damage_kills_a_buried_plant_in_plantChokeDays, .plant_choke_gate_reads_plantChokeEnabled
- The wind-lock gate (setting AND a locking biome) and the sun-bearing wind index. → slow_wind_locked_to_the_sun_on_stillsand.lock_applies_only_with_setting_and_a_locking_biome, .locked_wind_follows_the_sun_bearing; the live Stillsand wind read stays UNMEASURED
- Shovelled drift yields depth x per-depth x slider, nothing when off. → slow_shovelled_drift_yields_sand.yield_scales_with_depth_removed_and_multiplier, .clearYieldEnabled_off_arm_yields_nothing; the colonist job stays UNMEASURED
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
