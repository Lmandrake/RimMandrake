# Worker note: CONTAGION_FIRST_SCRIPT_1 (The Contagion, RimMandrake tier)

Status: READY TO RUN. Offline: selftest 58 components, healthy PASS 58/58, 44/44 breaks turn exactly their own
component red; `lint_calls.py` 0 problems over 58 literal calls; `--mock --mock-skip-site` runs to completion;
`modcheck floor` toggles uncovered = none (all 11 settings fields carry a covering component).

## Files
- `src/RimMandrake/Contagion/validation.py` (modcheck Suite, 45 bars + 13 fixture components, 11 settings round trips included in the 45)
- `src/RimMandrake/Contagion/northstar_plan.py` (USE_SUITE=True, EXPECT_MODS=`mandrake.rm.biomes`)
- `src/RimMandrake/Contagion/northstar_site.py` (preflight: map >= 150, DLCs, settings at defaults, map not already RM_Contagion)
- `src/RimMandrake/Contagion/selftest_contagion.py` (fake game; 44 breaks)
- `design/validation_walks/RimMandrake/Contagion.md` (60 `must be true` lines: 45 `→ chain.component`, 15 `→ UNCOVERED: why`; state DRAFT, no `## north star`, nothing owner-VALIDATED touched)

## Tier
`baroque_wave0` (existing, "2 wanted -> 9 with dependencies"). Contagion is composed (Biomes.compose.json, wave 0 <= compose_wave 2), so the
packageId a run must find active is `mandrake.rm.biomes`; the dev folder's own `mandrake.rm.contagion` is never loaded. No new tier was needed.

## LIVE-RUN SHEET
1. Bridge held by you (`rimflow bridge who`). Nothing else is needed from the owner.
2. One command (WSL, repo root, python3; it does stop game -> tier -> compose deploy -> launch -> quicktest -> driver):
   `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Contagion --tier baroque_wave0 --plan src/RimMandrake/Contagion/northstar_plan.py --compose`
   - Hand-run equivalent: kill the game; `python3 src/RimMandrake/Utils/modset_builder.py --tier baroque_wave0 --apply`; `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply`; launch via Steam; wait for `Bridge token:` in Player.log (~15 min cold, ~90 s quicktest); start a quicktest (`rimworld/start_debug_game_ready`); then
     `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Contagion --plan src/RimMandrake/Contagion/northstar_plan.py`
3. Launch wait: the `baroque_wave0` list is 9 mods (not measured here); `live_session.py` polls for `Bridge token:` itself.
4. Tick budget: about 25,000-40,000 game ticks of real waiting (repulsor arms 7,800; burn_forced about 9,000; natural 3,000 plus
   four clock JUMPS of 95,000 / 285,000 / 190,000 / 70,000 that simulate nothing; coalescence about 3,000; genome 3,000-15,000 if the extraction
   surgery needs retries). Roughly 10-15 minutes of wall time at the measured ~53 ticks/s; waits over 4,000 ticks run Ultrafast.
5. Site prerequisites: a quicktest map >= 150 cells on both axes (pads sit 45 from the centre; preflight checks), all five DLCs (tier sets them), no god mode
   needed, no pawns needed (the suite spawns its own colonists, natives and hosts), settings at shipped defaults (preflight checks). The suite
   RE-TILES the map's own tile to RM_Contagion (chain `site`) and puts it back at the end (chain `site_restore`); `site_restore` is
   registered last. The scratch map is throwaway; the retile never touches a save you care about. It also turns the storyteller and
   auto-home off for the session (`jawa/site_state`); a reload turns the storyteller back on.
6. Result: `Transient/northstar/Contagion_<ts>.json` plus a `[contagion]` progress line per component on stderr.

### What PASS / FAIL / UNMEASURED of each bar means (each bar can fail; the break that proves it is in `selftest_contagion.py`)
| bar | PASS means | FAIL means | how to break it to prove it can fail |
|---|---|---|---|
| defs.defs_resolve | all 108 shipped defs resolve, absent probe is reported | a def silently discarded (missing comp/extension type) | add a def naming a missing comp class |
| defs.biome_table_and_roster | Bloom standing, Burn has no commonality, density>0, sky extension, roster present | any of those wrong | give `RM_ContagionBurn` a baseWeatherCommonalities row; delete the sky extension |
| defs.organ_patch_comps | 4 vanilla organs carry GenomeMatched | patch matched nothing | break the xpath in `OrganGenomeComps.xml` |
| settings.defaults + 11 round trips | fields exist, shipped defaults, write+read-back | field missing/wrong default | rename a field in `RM_ContagionSettings` |
| repulsor_clear.off_when_setting_off | disabled repulsor never makes the condition | condition appears with the toggle off | drop the `cloudRepulsorEnabled` gate in `CompCloudRepulsor.CompTick` |
| repulsor_clear.holds_sky_clear | warm+powered registers RM_RepulsorClearSky (no Burn) | none registered / a Burn forced off-biome | remove the `RegisterCondition` branch |
| repulsor_clear.lapses_without_power | condition gone <= 1200 ticks after power off | condition persists | make `holdTicks` huge |
| spawner.spawner_off_buds_nothing | overdue host buds 0 with toggle off | buds | drop the gate in `CompSpawnerUnfinished.CompTick` |
| spawner.spawner_buds_unfinished | 1..3 Unfinished after toggle on | none, or > 3 | `maxNearby` 99 or comp not on the host |
| spawner.unfinished_rolls_limbs_and_lifespan | 1-3 pool limbs + unraveling | missing | empty `limbPool` |
| spawner.unfinished_dissolves_on_death | no pawn alive, no corpse | survives / corpse persists | remove `DeathActionProperties_Vanish` |
| site.retile_to_contagion | map biome follows the tile | biome unchanged | n/a (a harness fact; failure poisons every Contagion chain to UNMEASURED) |
| burn_forced.repulsor_forces_burn | Burn condition + inspect line + weather RM_ContagionBurn | no condition / wrong weather | remove `ForcedWeather` override |
| burn_forced.burn_harmless_at_zero_damage | no dose, no Burn injury at factor 0 | any harm | ignore `burnDamageFactor` |
| burn_forced.burn_doses_the_exposed_visitor | open visitor dosed, roofed visitor not | no dose / roofed dosed | break `Exposed` |
| burn_forced.burn_hurts_native_spares_armored | UV-shy native has Burn injury, Scaldhide none | the reverse | remove the `armoredNatives` skip |
| burn_forced.native_dives_for_roof | native stands under the roof patch | elsewhere | remove `TryDive` |
| burn_forced.burn_off_means_no_harm | forced Burn persists, no dose with `burnEnabled` off | vanished / dosed | drop the `burnEnabled` check in `Pressure` |
| burn_forced.repulsor_off_lapses_burn | condition gone <= 1200 ticks with the repulsor off | lingers | as above |
| burn_natural.* (3) | off never schedules (jump 285000); freq 0.1 defers (jump 95000 then 285000); freq 4 arrives (jump 70000) | the opposite | ignore `burnEnabled` / `burnFrequency` in `RollGap` |
| uv.uv_native_multiplier | native hit at 6x is >= 3x a 1x hit and >= 3x a person's | no multiplier / person multiplied | remove the factor in `DamageWorker_RM_UV` |
| coalescence.* (4) | off absorbs nothing; absorbing 6 reaches Stage 2; passive growth + manhunter emission after +7000; a Burn collapses it into exactly `min(14, 2+2*stage+mass/4)` Monstrous samples | each reversed | remove the `coalescenceEnabled` gates / change `samplesBase` |
| coalescence.monstrous_gestation_grows_one_limb, grown_limbs_off_grows_organs | exactly 1 limb and no organs; with the toggle off 2-4 organs and no limb | reversed | drop the `grownLimbsEnabled` check |
| genome.* (3) | surgery yields a sample with a source; inject gives gestation and spends the sample; completion kills the host and yields 2-4 non-limb items | each reversed | break `Recipe_ExtractGenomeSample` / `CompleteGestation` |
| log.log_clean | no Contagion error, no cross-reference error naming our defs | any | n/a |

UNMEASURED (never PASS): a read that cannot be completed (condition shape, repulsor power refusal, retile not landed, no sample after a surgery that
could not start, clock unreadable). FAIL poisons the rest of THAT chain to UNMEASURED (chains are independent).

## What the first live run is most likely to teach (UNPROVEN shapes; each degrades to UNMEASURED, not PASS)
- `jawa/site_state` `conditions.map[]` row shape (read as `def`/`defName`); `get_defs` field shapes for the biome; `get_def` `comps`.
- `jawa/power_net forcePowerOn` holding on an unconnected `CompPowerTrader` (if refused, every repulsor bar is UNMEASURED; fixture fix: spawn a battery/generator).
- The extraction surgery starting through `DoBillsMedicalHumanOperation` (the bed is spawned; `jobOnThingReturnedNull` names the failing branch).
- Wild natives wandering during the ~800-tick Burn read (native_dives_for_roof reads the final position; a wanderer reads FAIL or UNMEASURED, rerun to tell).
- Contagion's ongoing `WildAnimalSpawner` (animalDensity 3) can drop real natives into a pad after the retile; clear the pad and rerun that chain.
- Time jumps: nothing is simulated across them; `site_restore` and the following chains do not depend on the clock.
- Known weak spot: the `Burn` injury read uses the hediff defName `Burn` (DamageDefOf.Burn's hediff). If a native dies before the read, `burn_hurts_native_spares_armored` counts death as hurt; `native_dives_for_roof` records UNMEASURED.

## Boundaries (walk UNCOVERED lines)
tells, the standing Bloom's frequency/look, natural Coalescence formation (MTB), Sunbeam firing, install surgeries and limb effects, float-menu inject,
worldgen placement, extraction-off arm (a failed surgery is indistinguishable from a refused one), art.

## FOLLOW-UP ITEMS
- CONTAGION_SKY_STATE_TOOL_1: a `jawa/` bridge tool (or `[Tool]` on the companion) reading `RM_MapComponent_ContagionSky.NextBurnTick` / `TellsBegun`
  and the Coalescence mass, so the tells and the schedule can be checked without clock jumps; unlocks the `burnTellsEnabled` toggle check.
- CONTAGION_EXTRACT_LOG_LINE_1: have `Recipe_ExtractGenomeSample` log one `[RMContagion] extract ...` line (accepted/refused) so the
  `genomeOrganGrowingEnabled` OFF arm can be proven (`expect_log_contains`).
- CONTAGION_LIMB_SURGERY_FIXTURE_1: a site recipe that makes a surgery patient + bed + doctor deterministic (also covers the install recipes,
  matched-organ mood bonus, and grown-limb stat/ability reads).
- CONTAGION_SUNBEAM_FIRE_FIXTURE_1: a shooter fixture to fire `RM_Sunbeam` at a native and read the burst damage.
- Harness note for the schema file: `jawa/damage` documents `allowColonists`; the suite relies on it for the person control.
