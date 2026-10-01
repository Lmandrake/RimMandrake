# Worker note BLUE_DESERT_FIRST_SCRIPT_1

## status
READY TO RUN, one expected RED named below. 58 walk bars (49 covered by components, 9 carry an UNCOVERED reason),
59 suite components (55 checks + 4 site-setup), 22 settings all covered by `suite.toggles`.
Offline: `python3 src/RimMandrake/BlueDesert/selftest_bluedesert.py` -> ALL OK (healthy + 55 mutants, 2 UNMEASURED
cases, defaults == C#, walk <-> suite, preflight tool list, schema lint). `lint_calls.py` 0 problems over 87 calls.
`northstar_driver run --mock --mod BlueDesert --plan ... --mock-skip-site` runs to completion (NOT GREEN, as every
sibling under the default mock). `modcheck floor --all`: BlueDesert walk yes, subject ok, DRAFT, `no bar` (the same
verdict every DRAFT sibling reads; `bar met` exists only for VALIDATED north stars, and this walk's `## north star` is
DRAFT with a blank hash, untouched by design). `modcheck lint`: 0 FAIL for this walk (the 1 FAIL left is
GelatinousSlime.md:4, not mine).

Files: `src/RimMandrake/BlueDesert/validation.py`, `northstar_plan.py`, `northstar_site.py`,
`selftest_bluedesert.py`, `design/validation_walks/RimMandrake/BlueDesert.md`.

## bars
Chains and components (walk lines end in `-> chain.component`):
- defs: defs_resolve, biome_weather_table, biome_carrier_condition, biome_roster_and_density, charge_comps_wired,
  rack_needs_no_power, ablation_and_murrek_wired
- settings: defaults + 7 round trips (burnerHalo, crackCue, murrekReseed, ablationSalvage, ablationPace,
  vhaulkRoadDays, vhaulkStayDays)
- fauna: natives_spawn_charged, vrisk_can_fly; flora: flora_spawns
- flora_chain: plant_death_chains / _toggle_off_no_chain / _master_off_no_chain
- flora_warm: warm_threshold_above_keeps_plants, warm_toggle_off_keeps_plants, warm_detonates_plants
- dorrak_hump: hump_hit_kills, leg_hit_does_not_kill, hump_toggle_off_ordinary_part
- krissek_blast: krissek_death_blasts, krissek_off_quiet
- vhaulk_gates: heat_kill_detonates, kinetic_kill_does_not, emp_on_living_detonates, heat_gate_off_any_death_detonates,
  emp_trap_off_is_ordinary_damage, native_toggle_off_no_blast, master_off_no_blast
- haze: haze_film_on_outdoor_colonist (+ roofed control), haze_spares_natives, haze_toggle_off_new_arrival_clean
- butane: foreign_grazer_takes_butane_gut, native_grazer_exempt, butane_toggle_off_clean
- cold_wax: wax_toggle_off_ruined_but_inert (control, runs first), wax_ruined_wicks_and_goes
- cold_rack: rack_cools_loaded_room_only (vs an empty rack in an identical room), rack_spends_ice_and_drips,
  rack_toggle_off_leaves_room_alone
- thaw: thaw_toggle_off_mines_cleanly, thaw_roll_finds_debris (48 blocks, 16 rolls, false RED 0.1%)
- vhaulk_road: road_laid_and_flora_cropped, road_toggle_off_walks_clean
- weather_apply: ruled_weathers_toggle_applies (through the real Mod Settings dialog)
- ablation_gate: ablation_only_in_blue_desert; vhaulk_departs: vhaulk_walks_off_with_a_letter; log: log_clean
UNCOVERED (reasons in the walk): burner halo and crack cue (VFX/audio, no state read), clouding tint and sounds,
melt-water recipe (no stove fixture), road lifetime (2-3 game days), vhaulk seam boom/frost, ice-sand drift sand and
ice-fog accuracy effects, ablation incident staging and murrek re-seed (need a Blue Desert map).
Past-bug guards: LOAD_ERRORS_FAUNA_FLORA_1 (Config errors naming our defs, in log_clean); vhaulk walk-off re-issue
(fd492b10f, in vhaulk_departs); ruled weathers exist (ab07b9140, biome_weather_table).

## tier
`baroque_wave0` (existing, `mandrake.rm.biomes` composed; BlueDesert is a wave-2 entry, `wave 2 <= compose_wave 2`).
EXPECT_MODS = `mandrake.rm.biomes`. No new tier was needed and `modset_builder` was not touched.

## LIVE-RUN SHEET
Holder: FOUNDRY holds the bridge (`python3 src/RimMandrake/rimflow/cli.py bridge who`). One command from the repo
root does everything (stop game, tier swap, compose deploy, Steam launch, wait for `Bridge token:`, quicktest world,
driver run):

    python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod BlueDesert --tier baroque_wave0 --plan src/RimMandrake/BlueDesert/northstar_plan.py --compose

- `--compose` is required: the dev folder's own packageId is never loaded; the composed `mandrake.rm.biomes` must
  carry the current BlueDesert DLL (`deploy_custom_mods.py --compose biomes --apply`).
- Launch wait: a 9-mod tier plus the five DLCs, expect a few minutes (the full list is ~15 min; do not wait on that).
- Site prerequisites: a FRESH quicktest world (the step-5 `prove_quicktest_world.py`), map >= 150 in both axes (the
  pads sit up to 62 cells from the centre), all five DLCs (the tier sets them). No colonists, no god mode: the suite
  spawns its own pawns and clears its own pads. `northstar_site.preflight` refuses a short map, a missing tool
  (35 listed), settings not at their shipped defaults, and unlocks the weather.
- Re-run on a FRESH world: fires, half-eaten flora and a wandering vhaulk from an earlier run read as noise.
- Tick budget: about 55,000 ticks without the walk-off (flora_warm 12,900, thaw 9,400, cold_wax ~7,000, haze 6,400,
  cold_rack 6,000, vhaulk_road 3,000, butane 2,700, vhaulk_gates 1,260, rest < 1,000) plus 12,000 to 42,000 for
  `vhaulk_departs` (it runs LAST; stay factor floor 0.1 x 2-5 days). Waits over 4,000 ticks run Ultrafast and poll
  the real clock; expect 15-40 minutes wall time.
- Results: `Transient/northstar/BlueDesert_<ts>.json` and `BlueDesert_session_<ts>.log`; progress lines
  `[bdesert]` / `[bdesert-note]` stream on stderr (a backgrounded run is not silent).
- Settings: every arm restores its field in a `finally`; `preflight` re-reads them at the next run.

What each verdict means (class guess in brackets):
- defs_resolve FAIL: a def silently discarded (MOD). biome_weather_table/carrier/roster FAIL: biome def wrong (MOD).
  biome_roster `zeroed`/`absent`: wildAnimals/wildPlants row missing or commonality 0 (MOD).
- charge_comps_wired FAIL: a comp type did not bind (MOD). UNMEASURED when `get_def` lists only the generic
  `Verse.CompProperties` for the wax's detonator (HARNESS: compClass unreadable).
- natives_spawn_charged FAIL: a native spawned without its `RM_<Kind>Charge` (MOD, kind/hediff def).
- plant_death_* FAIL: the neighbours' fate disagrees with the toggle (MOD). warm_*: FAIL = plants disagree with the
  threshold/toggle after 4,300 ticks (MOD). UNMEASURED = ambient unreadable or fewer than 3 plants (SITE).
- hump_*: UNMEASURED if the hump/leg was never destroyed by up to 1,920 Cut (SITE/HARNESS); FAIL otherwise (MOD).
- krissek_off_quiet: see the expected RED below. krissek_death_blasts FAIL: no blast or the control burned (MOD).
- vhaulk_gates trials: UNMEASURED if the vhaulk did not die of a kill trial (HARNESS damage tool); FAIL = blast
  presence disagrees with the rule (MOD). The control colonist 17 cells away burning FAILs the trial (radius 15).
- haze_*: UNMEASURED when the carrier is not in `weather_get.conditions` or the room is not roofed (SITE/HARNESS);
  FAIL = film/severity disagrees (MOD).
- butane_*: UNMEASURED when the bridge cannot order `Ingest` or the plant is not eaten in 900 ticks (HARNESS);
  FAIL = hediff presence disagrees (MOD).
- cold_wax_*: UNMEASURED if the OFF arm never reads "Ruined" and the wax is still there (SITE: not warm enough);
  FAIL = wax gone with the toggle off, or still standing with it on after ruin (MOD).
- cold_rack_*: UNMEASURED if Refuel is refused or the rack holds no cold (HARNESS/SITE: faction); FAIL = no cooling,
  no ice spent, no cans, or the toggle ignored (MOD).
- thaw_*: UNMEASURED if too few blocks were mined (SITE: idle miners); FAIL = debris with the toggle off, or none in
  16 rolls with it on (MOD; 0.1% by chance, rerun once on a RED).
- vhaulk_road_*: UNMEASURED when `Goto` is refused for a wild animal or the vhaulk barely moved (HARNESS); FAIL =
  road/crop disagrees with the toggle, or a path plant was destroyed (MOD).
- ruled_weathers_toggle_applies: UNMEASURED when no Mod Settings dialog wrote `Mod_*RM_BlueDesertMod.xml` (HARNESS);
  FAIL when it did and the table did not follow (MOD).
- vhaulk_walks_off_with_a_letter FAIL: still on the map after 42,000 ticks, or left without the letter (MOD).
- log_clean FAIL: an error naming BlueDesert / our defs (MOD or LOAD).

EXPECTED RED on the first run: `krissek_blast.krissek_off_quiet` (MOD, predicted from source). `RM_KrissekCharge` and
the eight other non-vhaulk charge hediffs carry the vanilla `HediffCompProperties_ExplodeOnDeath`, which never reads
`RM_BlueDesertSettings`, so with `nativeDetonationsEnabled` off a dying krissek still blasts (and with it on it blasts
twice: hediff and death-action). The About text and the settings tooltip say the opposite. The selftest models this
as the mutant `krissek_toggle_ignored`.
Live shapes the fake only ASSUMES (each reads UNMEASURED, never PASS, if the live bridge differs): `get_terrain_layers`
cells carry `temp`; `get_def` comps are class names; inspect lines `Cold held: N h` and `Growth N%`; `ordered_job`
accepts `Ingest` for an animal and `Goto` for a wild animal; `fire_incident dryRun` carries `canFireNow`; the dialog
for `mandrake.rm.biomes` writes `Mod_*RM_BlueDesertMod.xml`; `Refuel` accepts a `spawn_batch` rack after
`set_thing_props faction=PlayerColony`; `Mine` runs on a designated `spawn_batch` rock.

## how each check can fail
Proven by the selftest (`selftest_bluedesert.py`), one mutant per row; the fake game breaks ONE behaviour and the named
component must go FAIL while nothing outside its chain does. To break it live instead: flip the named setting's
behaviour in source, or remove the def/comp.
- defs_resolve: delete a def file / mistype a comp class. biome_weather_table: add `Rain` commonality. carrier: drop
  `biomeMapConditions`. roster: set a wildAnimals commonality to 0 or density to 0. charge_comps_wired: remove a comp.
  rack_needs_no_power: add `CompPowerTrader`. ablation_and_murrek_wired: empty `allowedBiomes` / drop the extension.
- defaults: start a run with a setting flipped. natives_spawn_charged: drop one `startingHediffs`. vrisk_can_fly:
  `MaxFlightTime` 0.
- plant_death_*: make `PostDestroy` skip the blast, or ignore either switch. warm_*: ignore the threshold, the toggle,
  or never detonate. dorrak_hump_*: stop killing on the hump, kill on any limb, ignore the toggle. krissek_*: no blast,
  or blast regardless of the toggle (the live defect). vhaulk_gates: never blast / always blast / ignore EMP / ignore
  each of the three switches. haze_*: no film, ignore the roof, hit natives, ignore the toggle. butane_*: never
  apply, no native exemption, ignore the toggle. cold_wax_*: never wick, wick with the toggle off. cold_rack_*: no
  cooling, no ice use, no drip, ignore the toggle. thaw_*: roll with the toggle off, never roll, no yield.
  vhaulk_road_*: no road, no crop, destroy the flora, ignore the toggle. departs: never leave, leave silently.
  weather_apply: `Apply()` a no-op. ablation_gate: drop the biome restriction. log_clean: any error line.
- UNMEASURED cases proven: dialog never writes the settings file; the bridge refuses ordered jobs.
- Every PASS arm has its own control inside the chain (witness vs control colonist, empty vs loaded rack, ON vs OFF
  toggle, plants above vs below the threshold), so a harness that sees nothing cannot pass.

## FOLLOW-UP ITEMS
- BLUE_DESERT_NATIVE_TOGGLE_LEAK_1: MOD defect predicted by `krissek_blast.krissek_off_quiet`; make
  `nativeDetonationsEnabled`/`masterEnabled` actually gate the vanilla `HediffComp_ExplodeOnDeath` on the nine native
  charge hediffs (a settings-aware subclass, the pattern of `RM_HediffComp_HeatGatedExplodeOnDeath`), drop the
  duplicate hediff blast on the krissek, then re-run `krissek_blast`.
- BLUE_DESERT_SITE_1: a Blue Desert northstar site recipe (re-tile a scratch-world tile to `RM_BlueDesert`, generate a
  250x250 map, reload; the Pyrelands `northstar_site.py` shape) so the ablation incident, murrek re-seed, ice-sand
  drift, ice fog and the biome's own Haze carrier can be driven for real.
- BLUE_DESERT_MELT_BILL_1: drive `RM_MeltBlueIce` through a fuelled campfire/stove bill (`jawa/do_bill_now`); needs a
  `northstar_driver.site` fixture "fuelled stove + cook".
- BLUE_DESERT_THAW_ROLL_SEED_1: a debug `[Tool]` that forces `RM_MapComponent_BlueIceThaw`'s roll (or seeds it) so the
  statistical 48-block arm becomes a 3-block deterministic one.
- BLUE_DESERT_WEATHER_EFFECT_READS_1: a companion read for sand-grid depth at a cell and for the current weather's
  accuracy factor / range cap, to cover ice-sand drift and ice fog effects.
- NORTHSTAR_SETTINGS_WRITE_TOOL_1: a `jawa/mod_settings_write` tool that calls `Mod.WriteSettings()` for a settings
  type (and a driver helper that proves the config file changed), replacing the open/close-dialog dance used by
  `weather_apply` and LuminousPigment's `_apply`, which cannot say which Mod handle a composed `modId` opens.
- NORTHSTAR_PAWN_REMOVE_TOOL_1: `session.sweep` kills tracked pawns with `Bomb 99999`, so every tracked native with an
  `ExplodeOnDeath` blasts at teardown (a krissek burns the fixtures beside it); a non-lethal `jawa/pawn_remove`
  (despawn and discard) would end that.
