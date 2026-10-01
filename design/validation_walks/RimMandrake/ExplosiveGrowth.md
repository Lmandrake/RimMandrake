# RimMandrake: Explosive Plant Growth — validation walk
subject: src/RimMandrake/ExplosiveGrowth  (packageId `mandrake.rm.explosivegrowth`)
deps: `brrainz.harmony` only (modDependencies); every soak route other than the debug action reads or is pushed by another mod (FlowWorks, Environmental Hazards, Flooded Canyon) and is reflection-soft
list: explosivegrowth_solo (modset_builder tier: the bridge + `mandrake.rm.explosivegrowth`, all five DLCs); the donor-plant tops run on a list carrying Alpha Biomes / `RG_` / Pyrelands plants
status-hint: EXPLOSIVE_PLANT_GROWTH_1 — water-soaked plants grow x10 on top of the ambient rate, a soaked plant that reaches full size charges (a fixed tell ladder) and ends in a TOP (Churn default; Burst, Tinder, Slime, Rupture, Flush are roster/extension data). Charge-clock fix live-proven 2026-09-27 on the 10-mod tier; nothing else has a recorded run. Script: `src/RimMandrake/ExplosiveGrowth/validation.py` (plan `northstar_plan.py`), first script owed by EXPLOSIVE_GROWTH_FIRST_SCRIPT_1.

Sources for every line below: the mod's `About/About.xml` description, `design/Jawa/worldbuilding/explosive_plant_growth_design.md` (rulings), `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md`, and the C# under `src/RimMandrake/ExplosiveGrowth/Source/`. The engine has no bridge tool; its live read-out is its debug menu (`Source/Debug/RM_ExplosiveGrowthDebugActions.cs`), read from each call's own `effects.logs`.

## must be true
- The engine starts clean: the registry classifies plant defs (`N plant defs soak`, N > 0), no `[RM ExplosiveGrowth]` error is logged, and the startup line `charge clock self-test PASS` is present (its absence once meant the deployed DLL predated the fix). → boot_defs.startup_log_clean
- All five Harmony patches are attached by the engine's own id: `Plant.GrowthRate` getter (postfix, the soak multiplier), `Plant.Print` (prefix + finalizer, the overgrowth scale), `Plant.Graphic` getter (postfix, the hue), `Plant.YieldNow` (postfix, the jackpot), `Plant.PlantCollected` (prefix, the last-swing gamble). → boot_defs.harmony_patches_attached
- The four sound defs resolve (`RM_EG_Creak`, `RM_EG_Split`, `RM_EG_Pop`, `RM_EG_Rupture`). → boot_defs.sound_defs_resolve
- The registry reads plants and rosters: dozens of plant defs soak, the never-soak set is non-empty, roster rows naming an installed plant resolve (absent plants are skipped, never a def error), and the test map's biome is not a soak carve-out. → registry_report.report_reads_registry
- Soaking ground registers a footprint of cells in the soak grid (the debug action calls `ExplosiveGrowthAPI.SoakCells`, the surface other mods call by reflection). → soak_footprint.soak_cells_registered
- A soaked growing plant grows x10 on top of whatever ambient rate it already has, and an unsoaked neighbour is untouched. → soak_x10_default.soak_multiplies_growth_x10
- The multiplier is a Mod Setting and the setting drives it. → soak_multiplier_tuned.soak_multiplier_follows_setting
- The master switch off refuses the soak and leaves growth unmultiplied. → master_switch_off.master_off_refuses_soak
- A soak dries back after its length (`defaultSoakHours`, hours to a day) and not before. → soak_length.soak_expires_after_default_hours
- Salt, fungus, and plants whose slowness is a mechanic (anima, gauranlen, ambrosia) never soak; a roster `None` row never soaks; cave plants never soak while `cavePlantsNeverSoak` is on. → soak_exempt_plants.exempt_and_cave_plants_never_soak
- A soaked plant that reaches full size starts charging and keeps going until its top; the charge holds while the plant is dormant and relaxes when dry (the clock `StepCharge`). → churn_cycle.mature_soaked_plant_charges_then_churns
- The tell ladder starts on the ground: when a charge arms, the ground darkens and sprouts (one sprout beside a Churn plant). → ground_tell_on.ground_tell_sprouts_beside_arming_plant
- With the ground tell off the plant still charges and nothing sprouts at arming. → ground_tell_off.ground_tell_off_sows_nothing
- The charge clock length is a Mod Setting (`chargeHours`): at 1 h the top fires on its own within ~3500 ticks. → charge_hours.charge_hours_sets_the_clock
- The Churn top (the default): the plant splits and dies, drops its produce, and sows a ring of sprouts that keep going. → churn_cycle.mature_soaked_plant_charges_then_churns
- With Churn off a fully charged plant just relaxes back to normal size: it lives, no produce, no top. → churn_off.churn_off_plant_relaxes
- The tell ladder past the ground: the plant swells past natural size (up to `maxOvergrowthScale`), its hue shifts wrong, it trembles, it creaks, then goes silent. → UNCOVERED: visual and audio, judge pass or owner; the Print scale and Graphic tint are draw-time and no bridge tool reads them (`jawa/thing_graphic` is untested for tint)
- The Burst top (dry-adapted plants only): a pop, hay chaff, premium produce scattered, a sown ring that ignores zones; falls back to Churn when `burstEnabled` is off. → top_burst.burst_pops_leaves_chaff
- A Burst bruises and knocks down nearby pawns, never lethally, and `burstHurtsPawns` off spares them. → burst_hurts_pawns.burst_bruises_nearby_pawn
- The Tinder top: a burst whose debris is fuel (more hay); falls back to Churn when `tinderEnabled` is off. → top_tinder.tinder_leaves_fuel
- The Slime top: the ring turns the ground to slime; falls back to Churn when `slimeEnabled` is off. → top_slime.slime_turns_the_ground
- The Rupture top (contaminated plants): a gas cloud zone, blood, spawned things, sprouts; falls back to Churn when `ruptureEnabled` is off. → top_rupture.rupture_opens_a_cloud_zone
- Anyone in a Rupture cloud without a full vacuum seal can gain a mutation (`ruptureMutationChance`). → UNCOVERED: statistical, needs a pawn in the cloud and the Contagion hediffs; no bridge tool reads cloud-zone membership (named item to file: EXPLOSIVE_GROWTH_PROBE_TOOL_1)
- The Flush top (giant trees): the plant swells inside and survives, silently; falls back to Churn when `flushEnabled` is off. → top_flush.flush_plant_survives
- Harvesting a swollen plant pays extra, up to double at full charge (`harvestJackpotEnabled`). → UNCOVERED: needs a harvesting pawn and a read of `Plant.YieldNow` on a charging plant; no bridge tool reads it (named item to file: EXPLOSIVE_GROWTH_PROBE_TOOL_1)
- Cutting a charging plant defuses it, and once it trembles the last swing is a gamble (`lastSwingGambleEnabled`). → UNCOVERED: needs a cutting pawn and a deterministic gamble; random, same missing tool (EXPLOSIVE_GROWTH_PROBE_TOOL_1)
- Keeping ground dry works: suppression (grazing animals, a dry-air blower) dries the soaked cells, refuses new soak there, and a charging plant relaxes to zero alive. → suppression_on.suppression_dries_and_defuses
- With `suppressionEnabled` off, suppression does nothing. → suppression_off.suppression_off_is_inert
- With `burstHurtsPawns` off a burst leaves nearby pawns unhurt. → burst_hurts_pawns.burst_hurt_off_spares_pawn
- A disabled Burst top (`burstEnabled` off) behaves as Churn: no hay chaff. → top_burst.burst_off_falls_back_to_churn
- A disabled Tinder top (`tinderEnabled` off) behaves as Churn: no hay. → top_tinder.tinder_off_falls_back_to_churn
- A disabled Slime top (`slimeEnabled` off) behaves as Churn: no slime ground or filth. → top_slime.slime_off_falls_back_to_churn
- A disabled Rupture top (`ruptureEnabled` off) behaves as Churn: no cloud zone, no blood. → top_rupture.rupture_off_falls_back_to_churn
- A disabled Flush top (`flushEnabled` off) behaves as Churn: the giant dies. → top_flush.flush_off_falls_back_to_churn
- Irrigation soaks: a dug FlowWorks channel holding fresh water soaks the ground beside it; rivers and lakes never do (`irrigationSoakEnabled`). → UNCOVERED: needs FlowWorks on the list and a dug, filled channel; FlowWorks has its own tier and tools, a combined tier is not built
- A salt-line surge soaks the fresh side (`gradientSurgeSoakEnabled`). → UNCOVERED: needs Environmental Hazards' gradient axis running a surge
- A flood pushed in by Flooded Canyon soaks its cells. → UNCOVERED: pushed by another mod through `ExplosiveGrowthAPI`; that mod's script owns the flood, this one covers the API (`soak_footprint`)
- Soaking weather soaks open ground (`weatherSoakEnabled`). → UNCOVERED: no weather is named at the RM tier (`soakWeathers` is empty by design)
- The map-scale bloom: `RM_IncidentWorker_BloomBurst` soaks the flood footprint and sows the bloom plant. → UNCOVERED: the IncidentDef is the campaign layer's; the worker has no def at the RM tier
- Every Mod Settings field round-trips (write, then independent read-back), so a mistyped field name or a broken static fails; the fields below have no behavioural arm reachable in this suite and carry only this proof. → flip_minGrowDaysToSoak.minGrowDaysToSoak_setting_round_trips
- `irrigationSoakEnabled` round-trips (its effect needs FlowWorks, see the irrigation line). → flip_irrigationSoakEnabled.irrigationSoakEnabled_setting_round_trips
- `gradientSurgeSoakEnabled` round-trips (its effect needs the gradient axis). → flip_gradientSurgeSoakEnabled.gradientSurgeSoakEnabled_setting_round_trips
- `weatherSoakEnabled` round-trips (no soaking weather is named at the RM tier). → flip_weatherSoakEnabled.weatherSoakEnabled_setting_round_trips
- `maxOvergrowthScale` round-trips (its effect is the visual swell). → flip_maxOvergrowthScale.maxOvergrowthScale_setting_round_trips
- `reprintIntervalTicks` round-trips (visual cadence and the perf gate). → flip_reprintIntervalTicks.reprintIntervalTicks_setting_round_trips
- `hueShiftEnabled` round-trips (its effect is the visual hue). → flip_hueShiftEnabled.hueShiftEnabled_setting_round_trips
- `tellSoundsEnabled` round-trips (its effect is the creak). → flip_tellSoundsEnabled.tellSoundsEnabled_setting_round_trips
- `ruptureMutationChance` round-trips (statistical effect, see the mutation line). → flip_ruptureMutationChance.ruptureMutationChance_setting_round_trips
- `harvestJackpotEnabled` round-trips (see the harvest line). → flip_harvestJackpotEnabled.harvestJackpotEnabled_setting_round_trips
- `lastSwingGambleEnabled` round-trips (see the cut line). → flip_lastSwingGambleEnabled.lastSwingGambleEnabled_setting_round_trips
- A run leaves every setting at its shipped default. → settings_restored.all_settings_at_shipped_defaults

## the walk
1. [L] Player.log after load: the `[RM ExplosiveGrowth] N plant defs soak (...)` line and `charge clock self-test PASS (...)`; no `[RM ExplosiveGrowth]` error, no crossref/ConfigError/patch failure naming this mod   # boot_defs
2. [B] `rimworld/execute_debug_action` `Actions\T: Soak 5x5 here` at a cell → its own `effects.logs` carries `[RMExplosiveGrowthDebug] soaked N cells around (x, y, z)`; `Actions\Report state (current map)` → `soaked=N charging=… | soaked plants: immature=… charging=… topNone/exempt=…`   # soak_footprint
3. [B] `jawa/inspect_string` on a soaked and an unsoaked plant of one def → the `Growth rate` percent ratio is `soakMultiplier`   # soak_x10_default
4. [B] a mature soaked rice plant, two passes (≥ 500 ticks), Report → tail `charging=1`; `Actions\Charge all charging plants to 0.9`, ≥ 2500 ticks → the plant is gone, `RawRice` and sprouts near its cell   # churn_cycle
5. [B] Suppress r2 on a charging plant → Report `suppressed` > 0 and `charging` 0 after ~1800 ticks, plant alive   # suppression_on

## anti-guessing notes
RULED OUT: "a soaked, mature plant never charges because the decay branch beats arming" — fixed 2026-09-26 (`StepCharge`: wet+growing advances, wet+dormant HOLDS, dry decays), live-proven 2026-09-27; `churn_cycle` asserts `charging=1` after two passes and the startup self-test line is a check.
RULED OUT: "charging=0 on a cold map means the mod is broken" — a dormant plant is wet but not growing and correctly never arms; every growth chain reads temperature and the control plant's own rate first and records UNMEASURED (SITE) when the plant cannot grow.
RULED OUT: "a debug action that logged nothing did nothing" — RimWorld stops all logging at 10,000 messages (`Reached max messages limit`, Transient/bridge_debugaction_noop_report.md); `_act` records UNMEASURED, never PASS or FAIL, when no `[RMExplosiveGrowthDebug]` line arrives.
RULED OUT: "read the debug line with `jawa/drain_log contains=`" — it returns a stale first message (skills/rimbridge/references/map-authoring.md); the suite reads the mutating call's own `effects.logs`.
RULED OUT: "the debug action's x/z are the target" — they only place the virtual mouse; the actions read `UI.MouseCell()` (skills/rimbridge/references/silent-failures.md), so each ToolMap action is given the cell of the subject it must act on.
RULED OUT: "a deployed DLL always matches the repo" — 2026-09-27 the game copy predated `RM_ChargeSelfTest` and the self-test line was silently absent; `startup_log_clean` fails when the line is missing.
RULED OUT: "the plantgrowth tier is the smallest tier" — `mandrake.rut.plantgrowth` is a campaign mod whose ambient x4/x10 band multiplies the same `GrowthRate`; the soak ratio cancels it but the RM-tier script must not depend on it, so the tier is `explosivegrowth_solo`.
