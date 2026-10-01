# RimMandrake: Blue Desert — validation walk
subject: src/RimMandrake/BlueDesert  (packageId `mandrake.rm.bluedesert`)
deps: `mandrake.rm.environmentalhazards`, `brrainz.harmony`; ships composed inside the Baroque Biomes mod (Biomes.compose.json, wave 2)
list: baroque_wave0
status-hint: a hydrocarbon-ice plateau biome kit — ten fuel-charge natives (dorrak, krissek, vekkit, zhaaz, vrisk, dovvik, utikka, vhaulk, murrek, ossivel), four transparent fractal flora, cold wax, blue ice and its thaw roll, the blue-ice cold rack, the Haze/ice-sand-drift/ice-fog weathers, the vhaulk's gated cistern, rime road and walk-off, the staged ablation salvage and the murrek re-seed; script = `src/RimMandrake/BlueDesert/validation.py`, plan = `northstar_plan.py`, selftest = `selftest_bluedesert.py`

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`. Sources: the mod's About.xml description, `RM_BlueDesertMod.cs` (the 22 settings), the mechanic `.cs` headers (`BlueDesertLife.cs`, `RM_VhaulkDetonation.cs`, `RM_BlueIceThaw.cs`, `RM_ColdSink.cs`, `RM_AblationSalvage.cs`, `RM_VhaulkRoad.cs`, `RM_MurrekDrift.cs`, `RM_BlueDesertWeatherTable.cs`), `BLUEDESERT_MECHANICS_BUILD_1`, `BLUEDESERT_GPT_ENRICHMENT_1`, `LOAD_ERRORS_FAUNA_FLORA_1` (044381748).

Load and wiring
- Every def this mod ships (the biome, ten races and kinds, four flora, the charge hediffs, the Haze carrier and film, three weathers, blue ice and its mineable, cold wax, the rack, the meltwater can, the melt recipe, the rime road, three salvage incidents, sounds, the halo effecter, the burrow job) resolves in the live game; none is silently discarded for a missing comp or extension type. → defs.defs_resolve
- `RM_BlueDesert` runs Clear plus the three ruled weathers (Haze, ice-sand drift, ice fog) and carries no commonality for fog, rain, thunder or snow. → defs.biome_weather_table
- `RM_BlueDesert` carries the Haze carrier condition in `biomeMapConditions` (the film reaches a real Blue Desert map). → defs.biome_carrier_condition
- `RM_BlueDesert` has `animalDensity` and `plantDensity` above 0 and all ten natives and four flora read `spawning` in the resolved biome roster. → defs.biome_roster_and_density
- The blue-ice mineable carries the thaw comp, cold wax the ruined-detonator comp, the rack the cold-sink comp, and all four flora the plant-charge comp. → defs.charge_comps_wired
- The rack carries no power comp (it works in a blackout). → defs.rack_needs_no_power
- The three salvage incidents are restricted to `RM_BlueDesert` (`allowedBiomes`) and the ice-sand drift weather carries the murrek re-seed extension. → defs.ablation_and_murrek_wired
- All 22 Mod Settings fields exist and read their shipped defaults; a nonexistent field fails loudly. → settings.defaults
- The log carries no `BlueDesert` or `RimMandrake.BlueDesert` error, no cross-reference error and no Config error naming one of this mod's defs (the `LOAD_ERRORS_FAUNA_FLORA_1` class: tool body-part groups the BodyDef lacks, zero-nutrition edible plants). → log.log_clean

The natives
- Each of the ten natives spawns a living pawn carrying its own charge hediff (`RM_<Kind>Charge`), the thing that makes it detonate. → fauna.natives_spawn_charged
- The vrisk can fly (`MaxFlightTime` above 0). State read only; flight in the air is never live-tested unattended. → fauna.vrisk_can_fly
- All four flora stand when placed at full growth. → flora.flora_spawns
- Destroying a dorrak's Hump kills it outright. → dorrak_hump.hump_hit_kills
- Destroying a dorrak's leg does not. → dorrak_hump.leg_hit_does_not_kill
- With `nativeDetonationsEnabled` off the Hump is an ordinary part and destroying it leaves the dorrak alive. → dorrak_hump.hump_toggle_off_ordinary_part
- A dying krissek's blast burns a colonist 2 cells away and not one outside its 2.9-cell radius. → krissek_blast.krissek_death_blasts
- With `nativeDetonationsEnabled` off a krissek dies like an ordinary animal (no blast). → krissek_blast.krissek_off_quiet
- The krissek's blue-fire halo shows while it runs, hunts or fights, and not when `burnerHaloEnabled` is off. → UNCOVERED: an effecter has no state read (visual, left to the judge pass); the setting exists and is writable → settings.burnerHaloEnabled_roundtrip

The flora
- A palefloss killed by damage detonates (radius 1.1, 40 flame) and takes its neighbours with it. → flora_chain.plant_death_chains
- With `floraChainReactionsEnabled` off the same kill leaves the four neighbours standing. → flora_chain.plant_death_toggle_off_no_chain
- With `masterEnabled` off the same kill leaves the four neighbours standing. → flora_chain.plant_death_master_off_no_chain
- Ambient above `warmDetonationThresholdC` on two consecutive long ticks kills a plant (and so detonates it). → flora_warm.warm_detonates_plants
- With the threshold above the ambient the same plants live. → flora_warm.warm_threshold_above_keeps_plants
- With `floraChainReactionsEnabled` off warm plants live. → flora_warm.warm_toggle_off_keeps_plants
- A warming plant cracks audibly one long tick before it goes off, and not when `crackCueEnabled` is off. → UNCOVERED: audio has no state read; the setting exists and is writable → settings.crackCueEnabled_roundtrip
- A water-based grazer (muffalo) that eats the flora takes `RM_ButaneGut`. → butane.foreign_grazer_takes_butane_gut
- A native (dorrak) that eats the same flora does not. → butane.native_grazer_exempt
- With `butaneGutEnabled` off the muffalo takes none. → butane.butane_toggle_off_clean

Cold wax and the cold rack
- Cold wax ruined by a warm room starts its own wick and is gone. → cold_wax.wax_ruined_wicks_and_goes
- With `coldWaxWarmReactiveEnabled` off the ruined wax just stays, ruined. → cold_wax.wax_toggle_off_ruined_but_inert
- A rack loaded with blue ice pulls a warm sealed room well below an identical room holding an empty rack. → cold_rack.rack_cools_loaded_room_only
- It spends its ice doing so, the cold held scales with `coldSinkCapacityFactor` (x0.25 spends four times as fast, so a drip fits in the run) and the melt drips into cans of meltwater. → cold_rack.rack_spends_ice_and_drips
- With `coldSinkEnabled` off the same warm room is left alone and the ice is not spent. → cold_rack.rack_toggle_off_leaves_room_alone
- The ice clouds from deep blue to white as the cold runs out, and the rack groans and drips. → UNCOVERED: a tint and sounds (visual/audio; the "Ice:" inspect stage needs a run that spends 50% of 30 blocks, which the budget does not afford)
- The `RM_MeltBlueIce` recipe melts 5 blue ice into 3 cans at a campfire or stove. → UNCOVERED: driving a bill needs a fuelled stove and a cook (the recipe is checked only to resolve, defs.defs_resolve); follow-up BLUE_DESERT_MELT_BILL_1

Blue-ice quarrying
- Blue ice mines to its item (15 per block) and, with `thawRollEnabled` off, mines cleanly with no debris. → thaw.thaw_toggle_off_mines_cleanly
- With the roll on, every third block mined rolls 35% for a fallen-debris find (steel, slag, components, plasteel): 48 blocks find some. → thaw.thaw_roll_finds_debris

The vhaulk
- Fire, a burn, heatstroke or lightning kills it and its cistern detonates (radius 15). → vhaulk_gates.heat_kill_detonates
- A kinetic or cold kill leaves the carcass intact. → vhaulk_gates.kinetic_kill_does_not
- Any EMP hit on the living vhaulk sets it off at once. → vhaulk_gates.emp_on_living_detonates
- With `vhaulkHeatGateEnabled` off any death detonates it. → vhaulk_gates.heat_gate_off_any_death_detonates
- With `vhaulkEmpTrapEnabled` off an EMP hit is ordinary damage. → vhaulk_gates.emp_trap_off_is_ordinary_damage
- With `nativeDetonationsEnabled` off a heat kill detonates nothing. → vhaulk_gates.native_toggle_off_no_blast
- With `masterEnabled` off a heat kill detonates nothing. → vhaulk_gates.master_off_no_blast
- A walking vhaulk presses a temporary rime road (temp-terrain layer) and crops the flora it passes to growth 0.08 without destroying it. → vhaulk_road.road_laid_and_flora_cropped
- With `vhaulkRoadEnabled` off it walks like any animal. → vhaulk_road.road_toggle_off_walks_clean
- The road lasts a few days (`vhaulkRoadDaysFactor`). → UNCOVERED: 2-3 game days (120,000+ ticks) is beyond the run budget; the factor is read/write only → settings.vhaulkRoadDaysFactor_roundtrip
- A wild vhaulk walks off the map after its stay (`vhaulkStayDaysFactor`, `vhaulkDepartsEnabled`) with a letter and never silently despawns. → vhaulk_departs.vhaulk_walks_off_with_a_letter
- The `vhaulkStayDaysFactor` field exists and is writable (it is also driven by the walk-off run). → settings.vhaulkStayDaysFactor_roundtrip
- Its seams boom at long intervals and frost hangs in its wake. → UNCOVERED: an audio one-shot and a dust fleck have no state read

Weather
- An unroofed colonist under the Haze carrier takes `RM_HazeFilm` and its severity climbs; a roofed one's does not. → haze.haze_film_on_outdoor_colonist
- The ten natives are immune. → haze.haze_spares_natives
- With `hazeExposureEnabled` off a colonist who arrives afterwards takes no film. → haze.haze_toggle_off_new_arrival_clean
- `ruledWeathersEnabled` off, once the Mod Settings dialog closes (`WriteSettings`), zeroes the three ruled weathers in the biome's table without touching Clear; back on, the authored values return. → weather_apply.ruled_weathers_toggle_applies
- Ice-sand drift adds sand to the sand grid; ice fog halves accuracy and caps range at 22.9 cells. → UNCOVERED: weather effect fields are def-level (source, `validate_patch.py`, `defs.defs_resolve` for presence) and the sand grid has no cheap read; follow-up BLUE_DESERT_WEATHER_EFFECT_READS_1

The ablation line and the murrek
- The ablation incidents fire only on a Blue Desert map (a dry run on this ordinary map says `canFireNow` false). → ablation_gate.ablation_only_in_blue_desert
- A crack sounds map-wide; hours later a shape shows under thinning ice with vekkit and vrisk circling; hours later the ice gives way and the payload and a letter arrive; `ablationSalvageEnabled` and `ablationPaceFactor` gate and scale it. → UNCOVERED: needs a map whose biome is `RM_BlueDesert` (IncidentDef.allowedBiomes), BLUE_DESERT_SITE_1; the two settings are read/write only → settings.ablationSalvageEnabled_roundtrip, settings.ablationPaceFactor_roundtrip
- When an ice-sand drift ends, murrek dig into fresh drifts and lie hidden until prey comes close, clearing the sand flushes one, and `murrekReseedEnabled` stops it. → UNCOVERED: `RM_MurrekDrift.IsBlueDesert` keys on the map's biome and the drift needs sand-grid depth (BLUE_DESERT_SITE_1); the setting is read/write only → settings.murrekReseedEnabled_roundtrip

## the walk
1. [B] Tier: `python3 src/RimMandrake/Utils/modset_builder.py --tier baroque_wave0 --apply` (Windows-side seat only), `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply`, launch via Steam, wait for `Bridge token:` in Player.log, start a quicktest map (150 cells or larger).
2. [B] `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod BlueDesert --plan src/RimMandrake/BlueDesert/northstar_plan.py` → results JSON in `Transient/northstar/`. One command for steps 1-2: `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod BlueDesert --tier baroque_wave0 --plan src/RimMandrake/BlueDesert/northstar_plan.py --compose` (bridge held by FOUNDRY).
3. [L] Player.log after load has no cross-reference error and no Config error naming a BlueDesert def   # load-time
Offline: `python3 src/RimMandrake/BlueDesert/selftest_bluedesert.py` runs the suite against a scripted fake game: healthy, then once per mod behaviour broken, each of which must turn exactly its own component red.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned. The visual questions (does the krissek's halo read as blue fire, do the flora read as transparent, does the rime road read as pressed ice) are his to rule.

## anti-guessing notes
- SUSPECTED, source-read and awaiting the live run: `krissek_blast.krissek_off_quiet` goes red. `RM_KrissekCharge` (and the eight other non-vhaulk charge hediffs) carry the vanilla `HediffCompProperties_ExplodeOnDeath`, which never reads `RM_BlueDesertSettings`, while the Mod Settings text says natives "die like an ordinary animal" with the toggle off. Only the death-action worker (krissek, `RUT_BurnerAscendant`) and the dorrak hump-kill honour it. The check reads what the player sees (does the killer's neighbour burn), so it goes red for the reported reason.
- RULED OUT: "the vhaulk blast fires from `Notify_PawnKilled`, which has no DamageInfo to gate on" — `RM_HediffComp_HeatGatedExplodeOnDeath` suppresses that hook and explodes from `Notify_PawnDied(dinfo, culprit)`; the heat/kinetic trials (`heat_kill_detonates`, `kinetic_kill_does_not`) read the blast's effect on a witness, so a regression to the vanilla hook goes red on the kinetic trial.
- RULED OUT: "the warm detonation can run on `CompTick`" — plants only `TickLong` (CLAUDE.md, RimSage-confirmed); the comp overrides `CompTickLong`. `warm_detonates_plants` waits two long ticks plus slack and goes red if the plants live.
- RULED OUT: "laying the rime road kills the flora under it, and a dead plant detonates" — `TerrainGrid.DoTerrainChangedEffects` only vanishes a plant and the charge comp fires on `KillFinalize` only; `road_laid_and_flora_cropped` counts the path plants after the walk and goes red if any is gone.
- RULED OUT: "`jawa/mod_settings_field` applies a setting" — it writes the static and never calls `WriteSettings`, so `ruledWeathersEnabled` (applied in `RM_BlueDesertWeatherTable.Apply` on `WriteSettings`) is driven through the real Mod Settings dialog; if the dialog never writes this mod's config file the component is UNMEASURED, never a pass and never a mod fail.
- RULED OUT: reading `<wildAnimals>` through `jawa/get_defs` — a non-public list it cannot serialise (Pyrelands, 2026-10-01); the suite uses `jawa/biome_probe`, which reads the runtime caches and says `spawning`, `zeroed` or `absent`.
- RULED OUT: "the quicktest map is a Blue Desert" — it is not. The ablation incident, murrek re-seed and the biome's Haze carrier are keyed on the biome; the carrier is started by hand for `haze.*` and the others are UNCOVERED (BLUE_DESERT_SITE_1).
- ASSUMED (source comments, not measured here): the Haze film's exposure gate reads `onlyDuringWeather` and `!Position.Roofed`; `haze_film_on_outdoor_colonist` compares an unroofed with a roofed colonist so the assumption is its own control.
- UNPROVEN live shapes (the first run settles them; each reads `UNMEASURED`, never PASS, when absent): `jawa/get_terrain_layers` rows carry a `temp` key naming the temporary terrain; `jawa/get_def` lists comp CLASS names (the wax's detonator is a generic `Verse.CompProperties` with a custom compClass); the inspect lines `Cold held: N h` (rack) and `Growth N%` (plant); `jawa/ordered_job Ingest` for an animal and `Goto` for a wild animal are accepted; `jawa/fire_incident dryRun` carries `canFireNow`; the Mod Settings dialog for `mandrake.rm.biomes` writes `Mod_*RM_BlueDesertMod.xml`. <!-- walklint-ok: mandrake.rm.biomes is the GENERATED composed packageId of Biomes.compose.json; no About.xml under src/ declares it -->
