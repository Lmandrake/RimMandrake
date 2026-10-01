# RimMandrake: The Contagion — validation walk
subject: src/RimMandrake/Contagion  (packageId `mandrake.rm.contagion`)
deps: none beyond Core and the five DLCs (`RM_RustPuff` carries `MayRequire` on `mandrake.rm.therot`); ships composed inside the Baroque Biomes mod (Biomes.compose.json, wave 0)
list: baroque_wave0
status-hint: a storm-roofed mutation-engine biome — the Bloom and the Burn (sky clock), the Cloud Repulsor and Sunbeam (Helix devices), the Coalescence, the Unfinished spawner, and the genome/organ-growing loop with Monstrous grown limbs; script = `src/RimMandrake/Contagion/validation.py`, plan = `northstar_plan.py`, selftest = `selftest_contagion.py`

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`. Sources: the mod's About.xml description, `RM_ContagionMod.cs`, the mechanic `.cs` headers (`RM_MapComponent_ContagionSky`, `RM_GameCondition_ContagionBurn`, `CompCloudRepulsor`, `Building_RM_Coalescence`, `CompSpawnerUnfinished`, `AmoebaHostUtility`), `CONTAGION_RM_MOD_BUILD_1`, `CONTAGION_MECHANICS_BUILD_1`, `CONTAGION_UNFINISHED_SPAWNER_1`, `CONTAGION_GENOME_ORGAN_GROWING_1`, `CONTAGION_GROWN_LIMBS_BUILD_1`.

Load and wiring
- Every def this mod ships (the biome, 2 weathers, the Burn condition, creatures, flora, hediffs, recipes, items, abilities, the UV damage def) resolves in the live game; none is silently discarded for a missing comp or extension type. → defs.defs_resolve
- `RM_Contagion` has the Bloom as its standing weather and gives the Burn weather NO commonality (the Burn is reachable only through its condition), has `animalDensity` above 0, carries `RM_ContagionSkyExtension`, and names every rostered animal and the rattlegrope in its rosters. → defs.biome_table_and_roster
- The four vanilla organs (Kidney, Liver, Lung, Heart) carry `CompProperties_GenomeMatched` (the patch matched; a patch that matches nothing logs nothing). → defs.organ_patch_comps
- All 11 Mod Settings fields exist and read their shipped defaults; a nonexistent field fails loudly. → settings.defaults
- The log carries no `Contagion` error and no cross-reference error naming one of this mod's defs. → log.log_clean

Mod Settings (each is also exercised by the mechanic lines below)
- `biomeRarityFactor` exists, defaults to 1 and is writable. → settings_biomeRarityFactor.biomeRarityFactor_roundtrip
- `genomeOrganGrowingEnabled` exists, defaults on and is writable. → settings_genomeOrganGrowingEnabled.genomeOrganGrowingEnabled_roundtrip
- `unfinishedSpawnerEnabled` exists, defaults on and is writable. → settings_unfinishedSpawnerEnabled.unfinishedSpawnerEnabled_roundtrip
- `burnEnabled` exists, defaults on and is writable. → settings_burnEnabled.burnEnabled_roundtrip
- `burnTellsEnabled` exists, defaults on and is writable. → settings_burnTellsEnabled.burnTellsEnabled_roundtrip
- `burnFrequency` exists, defaults to 1 and is writable. → settings_burnFrequency.burnFrequency_roundtrip
- `burnDamageFactor` exists, defaults to 1 and is writable. → settings_burnDamageFactor.burnDamageFactor_roundtrip
- `cloudRepulsorEnabled` exists, defaults on and is writable. → settings_cloudRepulsorEnabled.cloudRepulsorEnabled_roundtrip
- `sunbeamNativeFactor` exists, defaults to 6 and is writable. → settings_sunbeamNativeFactor.sunbeamNativeFactor_roundtrip
- `coalescenceEnabled` exists, defaults on and is writable. → settings_coalescenceEnabled.coalescenceEnabled_roundtrip
- `grownLimbsEnabled` exists, defaults on and is writable. → settings_grownLimbsEnabled.grownLimbsEnabled_roundtrip
- `biomeRarityFactor` at 0 stops the biome generating on a NEW planet, and the default places a handful of peaks. → UNCOVERED: worldgen placement, a boundary (debug_process §4 "world, map, art authoring"; the project has no worldgen feature, CLAUDE.md); only the field round trip is checked

The Cloud Repulsor off the Contagion (a stock biome)
- With `cloudRepulsorEnabled` off a powered repulsor never warms: no clear-sky condition appears and it reads "Disabled in Mod Settings". → repulsor_clear.off_when_setting_off
- Warm and powered on a non-Contagion map it registers the `RM_RepulsorClearSky` condition (never a Burn) and reads "Holding the sky clear". → repulsor_clear.holds_sky_clear
- When its power goes off the condition lapses within its hold time (750 ticks). → repulsor_clear.lapses_without_power
- The weather actually turns Clear and rain stops. → UNCOVERED: that is vanilla's `GameCondition_ForceWeather`, not our code; the weather read is recorded as evidence only (holds_sky_clear note), never judged
- The violet beam is drawn while the effect is live. → UNCOVERED: visual; left to the judge pass (debug_process §4)

The Unfinished spawner (off the Contagion, on a stock biome: the comp does not depend on the biome)
- With `unfinishedSpawnerEnabled` off an amoeba host buds nothing even with its timer long overdue. → spawner.spawner_off_buds_nothing
- With it on the overdue timer fires and the host buds 1 to `maxNearby` (3) Unfinished. → spawner.spawner_buds_unfinished
- Each Unfinished rolls 1-3 random limb hediffs from the pool and carries the unraveling lifespan hediff. → spawner.unfinished_rolls_limbs_and_lifespan
- An Unfinished that reaches lethal severity dies and leaves no corpse. → spawner.unfinished_dissolves_on_death
- "Some roll a monster": 12% of Unfinished carry the Monstrous hediff. → UNCOVERED: a statistical effect (debug_process §4); only the hediff def resolving is checked (defs.defs_resolve)
- Unfinished are not in the biome's ambient roster. → UNCOVERED: a negative over the whole roster; defs.biome_table_and_roster checks the roster contains what it should, not what it must not

The site: a Contagion map
- The quicktest map's own tile can be re-tiled to `RM_Contagion` and the map's biome follows (`Map.Biome` is a live passthrough). → site.retile_to_contagion
- Afterwards the tile is put back to its original biome. → site_restore.restore_tile

The Burn (a Contagion map; the sky engine is gated on the biome extension)
- A warm, powered Cloud Repulsor forces the Burn: the condition appears, the repulsor reads "Holding the storm open: the Burn is forced", and the weather becomes `RM_ContagionBurn`. → burn_forced.repulsor_forces_burn
- At `burnDamageFactor` 0 the Burn is weather only: no one is dosed and no native is hurt. → burn_forced.burn_harmless_at_zero_damage
- At the shipped factor an exposed visitor gains `RM_BurnDose`; a roofed one does not. → burn_forced.burn_doses_the_exposed_visitor
- A UV-shy native caught in the open takes Burn damage; an armored one (Scaldhide) takes none. → burn_forced.burn_hurts_native_spares_armored
- A UV-shy native dives for a roof. → burn_forced.native_dives_for_roof
- With `burnEnabled` off the forced Burn still holds but harms no one ("its harm still follows the Burn settings"). → burn_forced.burn_off_means_no_harm
- With `cloudRepulsorEnabled` off the forced Burn lapses within its hold time. → burn_forced.repulsor_off_lapses_burn
- With `burnEnabled` off no Burn is ever scheduled. → burn_natural.burn_off_never_schedules
- `burnFrequency` scales the schedule: at 0.1 no Burn arrives within 285000 ticks (frequency 1 would have fired by 270000). → burn_natural.slow_frequency_defers_burn
- At `burnFrequency` 4 a natural Burn arrives within 70000 ticks (gap at most 67500). → burn_natural.natural_burn_arrives_on_schedule
- The forecast: shortly before a Burn the gawpsacks stop and settle as one, rattlegropes puff; `burnTellsEnabled` off removes the tell. → UNCOVERED: the only observable is a Wait job that is indistinguishable from ordinary idling and short-lived flecks; needs a bridge tool reading `RM_MapComponent_ContagionSky` (`NextBurnTick`/`TellsBegun`), follow-up CONTAGION_SKY_STATE_TOOL_1
- The Bloom is the standing weather (red fog, rain, thunder, ranged accuracy x0.4). → UNCOVERED: the weather's standing frequency is a statistical roll and its look is visual; only the biome table (defs.biome_table_and_roster) is checked
- The Burn actually tears the cloud open and the sky reads near-white. → UNCOVERED: visual; left to the judge pass (debug_process §4)

The Sunbeam
- A UV hit on a Contagion native is multiplied by `sunbeamNativeFactor` (about 6x), and a person is not. → uv.uv_native_multiplier
- The Sunbeam weapon fires `RM_Bullet_Sunbeam` in a 3-shot burst at 5 per shot. → UNCOVERED: needs a shooter with the weapon and a target in the open; only the damage def and the native multiplier are driven (a weapon fixture is a follow-up, CONTAGION_SUNBEAM_FIRE_FIXTURE_1)

The Coalescence (spawned on the site: its natural formation is a statistical roll after a 90000-tick Bloom)
- With `coalescenceEnabled` off it absorbs no Unfinished and does not grow. → coalescence.coalescence_off_absorbs_nothing
- Absorbed Unfinished raise its mass; at mass 6 it reads Stage 2. → coalescence.coalescence_absorbs_and_grows_a_stage
- It grows by itself over time (1 mass per 6000 ticks) and emits manhunter Unfinished. → coalescence.coalescence_emits_manhunters_and_grows_on_its_own
- Any Burn collapses it and spills `min(14, 2 + 2 x stage + mass / 4)` Monstrous genome samples. → coalescence.burn_collapses_it_into_monstrous_samples
- It forms by itself during a long Bloom, away from the home area, one at a time. → UNCOVERED: a statistical event (MTB 0.5 day after 90000 ticks of Bloom; debug_process §4); only a placed Coalescence is driven
- The three growth stages swap their graphic. → UNCOVERED: visual; left to the judge pass (debug_process §4)

The genome and organ-growing loop
- A surgery bill `RM_ExtractGenomeSample` on a colonist produces a genome sample recording its source. → genome.extraction_surgery_yields_sample
- With `genomeOrganGrowingEnabled` off the surgery gives nothing and the float-menu inject option never appears. → UNCOVERED: a failed surgery is indistinguishable from a refused one without a log line or a sample-count tool, and the float menu cannot be opened through the bridge; follow-up CONTAGION_EXTRACT_LOG_LINE_1. The toggle is covered by the round trip only
- Carrying a sample to a live bloody mess and running `RM_InjectGenomeSample` gives the host `RM_AmoebaGestation` and spends the sample. → genome.inject_starts_gestation
- A completed gestation kills the host (one batch only) and produces 2-4 organs or limbs from the organ pool, never a Monstrous limb. → genome.gestation_dies_producing_one_organ_batch
- A Monstrous sample grows exactly one grown limb and no organs. → coalescence.monstrous_gestation_grows_one_limb
- With `grownLimbsEnabled` off a Monstrous sample grows the normal organ batch. → coalescence.grown_limbs_off_grows_organs
- An organ carrying a source identity reads "matched" and gives the matched-install mood bonus when installed into that colonist. → UNCOVERED: install surgery on the matched patient needs the same surgery fixture plus a thought read; follow-up CONTAGION_LIMB_SURGERY_FIXTURE_1
- The five grown limbs (Pillar Arm, Lash, Eyeburst, Caudal Spring, Bellows) install and carry their trade-off stats and abilities. → UNCOVERED: the install recipes need the surgery fixture and the effects are tuning by feel (CONTAGION_LIMB_SURGERY_FIXTURE_1); only the defs resolving is checked (defs.defs_resolve)
- The Contagion's red valley, its flora and creatures read right in the art. → UNCOVERED: visual; left to the judge pass (debug_process §4)

## the walk
1. [B] Tier and launch in one command (Windows-side seat, bridge held): `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Contagion --tier baroque_wave0 --plan src/RimMandrake/Contagion/northstar_plan.py --compose`, which stops the game, applies the tier, deploys the composed biomes mod, launches via Steam, waits for `Bridge token:`, starts a quicktest world and runs the driver. (Exact steps and a hand-run alternative are in the worker note, `Transient/worker_notes_CONTAGION_FIRST_SCRIPT_1.md`.)
2. [B] Driver alone: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Contagion --plan src/RimMandrake/Contagion/northstar_plan.py` → results JSON in `Transient/northstar/`.
3. [L] Player.log after load has no `Contagion` error and no cross-reference error naming a Contagion def   # load-time
Offline: `python3 src/RimMandrake/Contagion/selftest_contagion.py` runs the suite against a scripted fake game: healthy, then once per mod behaviour broken, each of which must turn exactly its own component red.

## anti-guessing notes
- RULED OUT: "the Burn needs a generated Contagion map" — `Map.Biome => TileInfo.PrimaryBiome` (decompiled `Verse/Map.cs:398`, RimSage 2026-10-01) and `jawa/map_info` says it is a live passthrough, so re-tiling the quicktest map's own tile reaches `RM_ContagionSky.ExtFor`. site.retile_to_contagion is the guard: if the map's biome does not follow, every Contagion chain records UNMEASURED, never PASS.
- RULED OUT: "the Coalescence passively grows once a day" — the source default is 60000 ticks but `RM_Coalescence.xml` sets `passiveGrowthTicks` 6000; the suite jumps 7000 and reads the mass.
- RULED OUT: "a natural Burn must be waited for" — the mod compares `TicksGame >= nextBurnTick`, so `jawa/time_set_ticks` (which simulates nothing) crosses it; gaps are 0.5-1.5 x 3 days / `burnFrequency`. The off arm jumps 285000 (past the longest frequency-1 gap) so a schedule that ignored `burnEnabled` could not hide behind a long roll.
- RULED OUT: "list_pawns hediffs are a flat list or substring-safe" — they are `row.health.hediffs[].def`, and `Burn` is a substring of `RM_BurnDose`; the suite compares exact defNames.
- RULED OUT: "destroy_batch Items can clear a pad between batches" — it also destroys a genome sample waiting to be injected; batches are counted as the NEW organ/limb thing ids.
- ASSUMED, not measured: the Cloud Repulsor can be powered with `jawa/power_net forcePowerOn` on an unconnected building (`powerOnAfter` is read back; a refusal records UNMEASURED); a bed lets `DoBillsMedicalHumanOperation` start the extraction surgery (the tool names the failing branch when it returns null); wild natives stay near their spawn cell for the ~800 ticks the Burn checks take.
- UNPROVEN live shapes (the first run settles them; each reads `UNMEASURED`, never PASS, when absent): `jawa/site_state` `conditions.map[]` rows carrying `def`; `get_defs` fields `baseWeatherCommonalities` (list of `{weather, commonality}`), `wildAnimals`, `wildPlants`, `modExtensions` (read as a JSON blob); `jawa/get_def` `comps` as a list of class names; `jawa/pawn_get` carrying the word `Manhunter` for a manhunter; `jawa/time_set_ticks` `ticksGameAfter`; `jawa/world_tile_set` accepting a biome without elevation/temperature.
- Not driven because no cheap fixture: the tells, the Sunbeam firing, the install surgeries and grown-limb effects, the float-menu inject option, natural Coalescence formation, worldgen, art.
