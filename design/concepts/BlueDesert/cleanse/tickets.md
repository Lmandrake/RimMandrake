# Proposed tickets — none executed on this pass

All mutations below are future work after review and owner reading. Preserve code/defs/assets for every disabled built extra; introduce a persistent independent **Next version** setting default off, with truthful enable/disable scope. New fresh-default acceptance reads both actual state and clean log; code-presence tests are insufficient. Save migration keeps identities and visibly neutralizes in-flight optional behavior. All test maps are disposable; model definitions are in models.md. No ticket authorizes a planetary edit.

## T1: Disable the duplicate local Burner death action; recommend retirement

Caller search: RM_Krissek.race.deathAction and RUT_BurnerAscendant use RM_DeathActionWorker_BurnerBlast in BlueDesertLife.cs. RM_KrissekCharge is a separate death callback. Keep the shared class and propane-lake behavior; gate only the additional local death action, default off, with a next-version setting. Do not couple the propane-lake call to a local duplicate switch. One attributed fuel release must remain from the charge.

Acceptance test: On fresh defaults a killed local krissek has the attributed charge event and no additional death-action event, and log is clean; enable the labelled optional local action and both distinct paths are observable. Load the propane-lake consumer and verify its class and independent behavior remain intact. A nearby damaged witness alone does not pass.

## T2: Switch off char-lace manufacture without removing flora

Caller search: RM_Kethevar's killedLeavingDef is read by CompPlantCharge.PostDestroy under floraExpansionEnabled; no other source consumer found in bounded .cs/.xml search. Add separate output gate/default-off, preserve item/stuff definition, retain kethevar/wax/PlantCharge and default-on expansion roster. No char-lace reward from kinetic destruction by default either.

Acceptance test: Fresh defaults have kethevar and its normal wax harvest, no char-lace drops/jobs/letters after cut, flame, blast or kinetic destruction and clean log; optional setting on produces char-lace on its then-declared damage branch while safe harvest still produces wax only. Read source cause, not a pre-existing item count.

## T3: Switch off timed hazebell bloom

Callers: plant CompProperties_HazeBloom and RM_Plant_Hazebell.Graphic in RM_Hazebell.cs. Separate bloom setting from carbonGardenEnabled; retain plant/growth/wax/charge. Old saved open state closes visibly on the next labelled plant update, with no extra emissions. No plant deletion.

Acceptance test: Fresh defaults across real Haze and clear transitions have ordinary hazebells, no open-state timer/vapor job/letter/event and clean log; optional setting on opens and later closes the plant, and saved open-state off transition closes without disabling its charge.

## T4: Switch off block-counter thaw loot; recommend retirement

Callers: RM_BlueIceMineable CompProperties_BlueIceThaw, RM_CompBlueIceThaw.PostDestroy, Notify_BlockMined and ColdCuttingSuppresses. Gate the counter and roll default-off. Ordinary mineable yield and placement must not call or depend on the cold-cutting seam. Preserve component type and saved counter for load safety; no new count/heat mechanic.

Acceptance test: Fresh-default real mining beyond the configured roll interval yields only normal ice, no thaw loot/messages/incidents/jobs and clean log; on setting, a deterministic controlled roll produces the existing debris path. Same amount mined at different paces has no safety/loot distinction by default. A damage kill is not falsely counted as mining.

## T5: Switch off rack and its tint/groan affordances; recommend retiring appliance

Callers: RM_ColdSinkRack has refuelable/temp-control/ColdSink comps, RM_Building_ColdSinkRack.Graphic and RM_CompColdSink inspect/tick; retained loose ice has no caller of these classes. Gate build-menu availability, offers/loot/refuelling work and cooling under one next-version default-off setting; keep defs/class. Existing saved rack remains inert with ice retained and truthful disabled inspect. Do not gate ordinary water conversion or T17 loose-ice behavior with coldSinkEnabled.

Acceptance test: Fresh defaults have no available/placed rack, rack refuel jobs, groans or cooling events and clean log; loose ice still performs T17. Enable optional rack setting and its build/refuel/cooling/tint behavior is present. Disable a loaded existing rack and read unchanged fuel/no heat output plus labelled inactive state.

## T6: Switch off Haze-film exposure, retain Haze weather

Callers: BiomeDef.biomeMapConditions -> RM_BlueDesertHazeCarrier -> EnvironmentalHazards exposure component via gate registry. Current gate only prevents new carriers, not existing exposure. Use a local consumer adapter/cleanup under next-version default-off; do not redesign the shared exposure engine. Revise active weather description so it does not promise disabled lung illness. Existing films decay/removal must be visible and bounded, never keep accruing when switched off.

Acceptance test: Fresh defaults through natural Haze have no film carriers/severity, exposure jobs/letters/incidents and clean log; optional setting on gives exposed foreign pawns the existing film behavior with native exemption. Turn off on an already affected pawn: no further accrual and documented decay/removal occurs; Haze still rotates and renders.

## T7: Switch off murrek burial and reseeding as one extra

Callers: weather RM_MurrekReseedExtension -> RM_MapComponent_MurrekDrifts -> RM_MurrekBurrow/RM_MurrekBuried. Watchers reads the hediff as a cue but does not create it. Gate producers/jobs/hediff application default-off; preserve ordinary resident race, its food/death behavior and dormant defs. An existing buried pawn must emerge visibly with inspect/sign, without spawning a replacement or dying to cleanup.

Acceptance test: Fresh defaults across drift endings have no burrow jobs, buried hediffs, storm top-ups or related letters/incidents and clean log; ordinary murrek remain visible predators. Enable setting and a known viable drift produces the buried/reseed path; turning it off returns the same pawn IDs visibly, including reload during burial. Watchers loads without a dangling reference and sees no buried cue by default.

## T8: Switch off the ablation incident package

Callers: RM_AblationSalvage_* IncidentDefs -> worker -> RM_AblationEmergence.TickRare -> scavenger recruitment/circling/payload/letter. Scanner optionally reads marker. Gate incident eligibility AND marker producers/outputs default-off; static Wreckage remains independent. Old in-flight markers must show a cancelled/inactive state and finish bounded cleanup with no untested payload, forced scavenger jobs or silent pawn removal; release recruited existing animals normally. Existing automatic completion-while-off policy is insufficient.

Acceptance test: Fresh defaults over an incident-eligible history have no emergence markers, circling overrides, stage messages/letters/payloads/incidents/jobs and clean log; enabled deterministic incident exhibits staged states and payload. Disable at each saved stage and verify bounded inactive cleanup, no new payload/letter, same recruited pawn identities returned to ordinary AI. Independent static wreck salvage works in both arms.

## T9: Switch off bespoke acoustic payload; recommend retirement

Caller: RM_AcousticPayload_BlueDesert.xml guarded extension for native races, wrecks, ice and emergence marker; the general AcousticScanner owns consumption. Gate local payload independently, preserving engine and ordinary scanning; no deferred marker needed for retained discovery. Label restart scope if patched extensions are selected at startup.

Acceptance test: Fresh defaults with scanner present show no BlueDesert-specific narrative payload or related jobs/messages, with clean log; enable local next-version switch and the intended target returns its local payload. General scanner operation remains available, and disabled ablation is never created just to make a scanner target exist.

## T10: Switch off ColdStorage roe-processing adapter

Caller search found RM_QeshraRoe in ColdStorage/Defs/Seals/Seals_Recipes.xml and Seals_Frost.xml, including ingredient/output registrations. Gate those local integration paths default-off behind a labelled next-version consumer setting; preserve qeshra, raw roe, shared ColdStorage and saved recipe/item defs. Decouple retained native feed from preserved human-food recipes. Later enabled paths need explicit physiology/reactivity specs; current food preference is not the spec.

Acceptance test: Fresh defaults with ColdStorage present offer no roe seal-processing jobs/bills/auto-consumer entries and produce no processed-roe output or related letters/incidents, and log is clean; raw native roe still feeds a native safely in cold storage. Optional setting on exposes the existing consumer entries and a controlled bill processes its declared input. Existing saved pending bills become labelled unavailable/cancelled without deleting ingredient stacks.

## T11: Settings, truthful scopes and default migration

Retain major feature controls, searchable scrolling groups, reset, persistence and normal roster controls. Add independent switches for moved behaviors; replace gate-off-means-more-dangerous semantics, especially vhaulkHeatGateEnabled. Audio mute never removes the only readable sign. Explain Core ordinary weather effects that remain when scripted master is off. No new cross-biome feature or world-placement option. Update stale descriptions. Resolve missing setting keys on old saves to proposed defaults without silently treating an old all-true settings blob as informed opt-in to next-version features; explicit new-version opt-in is required.

Acceptance test: State-read fresh defaults match definition.md; reset returns exactly those defaults; save/reload preserves deliberate per-feature choices and labels now/next-pulse/restart truthfully. Master and all-off stop every scripted local producer and leave identities/load clean. Toggle each major retained system off/on in its reachable active state, verify advertised effect and bounded cleanup, never broader detonation. An old settings file cannot auto-enable next-version producers.

## T12: Close lifecycle, warning and roster compatibility gaps

Use the documented source hooks, not new universal hazard engines. Persist plant warm state; produce locatable pre-ignition warning/progress and meaningful stop-heat response; generated native corpses, newborns and organic-product/held-state transitions retain fuel identity and reactivity. Wax refining follows R10’s ratified transition to ordinary Chemfuel at cold-room bill completion. Apply charges to newborns where startingHediffs-only generation misses them. Keep native ingestion safe, foreign flora/roe ingestion visibly incompatible. Adapt thunderbeast and campaign-added Vapaad locally without evicting either or globally rewriting their bestiary identity. Examine Bones output, shared growth exclusions, native environmental-water contract where liquid exists, and existing exit signs/blocked vhaulk behavior. If hydrocarbon compatibility cannot preserve Vapaad identity, report the standing conflict rather than invent an exemption; owner-page Q1 default retains roster with compatibility unsatisfied. Model generator informs exact adapter choice.

Acceptance test: Situation-generator witnesses calibrated to real game handlers find no warm-safe lifecycle bypass, wrong trigger or silent disappearance; reload after warning preserves debt/response, split/merge/held/newborn/generated-corpse paths preserve identity. Native ingestion is safe, foreign ingestion visibly incompatible. All enabled roster additions and shared outputs meet the same rule without roster removal; otherwise the relevant bar remains unpassed with the specific conflict. Real FlightTracker and departure state reads meet B2/B5; clean log. No result is credited from missing reader fields.

## T13: Ordinary discoverable work, water/fuel use and physical ancient context

Current mineable scatter is zero; Wreckage hull/frame placement exists, but a coherent quarry/ordinary ice placement caller was not found. Specify/build a minimal generic static abandoned extraction face with reachable ice and broken equipment using existing local placement ownership. It conveys an earlier attempt through spatial context, without study/epoch unlock, new campaign history, timed incident or planetary generation. Preserve ordinary salvage and Mine job. Implement the cold-wax bill on vanilla BiofuelRefinery, using the existing Abyss and TerminalBiomes recipeUsers examples as ownership evidence. Apply R10’s cold-workspace and ordinary Chemfuel output contract. Reconcile same ice mass and residual cold across can, bucket, melter and passive melt outputs; use FlowWorks water taxonomy. No new appliance or custom job.

The ordinary-work operating condition keeps input stacks and the interaction cell at or below the loaded RM_ColdWax.maxSafeTemperature, currently -1 °C from RM_ColdWax.xml. Keep the life brief’s ordinary bill with no added temperature interlock. Wax retains its normal warning/ruin/wick progress during work and interruptions, including cancellation and reload. A warm workroom ruins or wicks the input before the bill finishes. Completed cold-room work yields ordinary vanilla Chemfuel, with vanilla stack merging, refueling and consumption, as expressly specified by life brief section 7.

Acceptance test: On fresh received local-map fixtures across B7's placements, normal workers discover reachable physical old workings, salvage and mine without grants/unlocks/thaw rolls, and use traced recovered ice as potable-water input and native wax as ordinary fuel input. B1's look identifies an abandoned attempt. Conversion/split/load ledger conserves accounted water/cold, no duplicate product, clean log. A debug-spawned mineable alone fails placement acceptance. Read recipeUsers=BiofuelRefinery and trace actual cold-work completion with input/interaction cells below and at the loaded wax safe limit. Above-limit and warming-mid-bill witnesses must show input ruin/wick before completion, with progress preserved through cancellation/reload. Verify completed cold-work output is ordinary Chemfuel, including vanilla stacking and actual generator refueling/consumption. Compare its warming behavior with ordinary vanilla Chemfuel.

## T14: Ordinary weather action and local ice-grain appearance

Use the owner-ruled Odyssey SandGrid mechanism from `BLUEDESERT_DESIGN_SITTING_1`, recorded in the biome sheet section 4b amendment. Add the local blue-white material adapter. Weather rotation and transitions must be unlocked, with drift read beside structure/hull approaches and real fog targeting/travel. Remove inactive optional descriptions and decouple murrek/exposure/shuttle producers under their own tickets.

B3’s required outcome is the thickest SandGrid buildup reaching wall, door or hull approach cells and applying its heaviest path cost until sand clearing or erosion. Read cells beside full-fillage footprints, which the engine clears of sand. Attribute the deposit effect with post-storm depth/path/travel reads before erosion, or matched deposited/deposit-free routes under the same weather. Tuning choices concern weather accumulation rates and durations within the ruled mechanism.

Acceptance test: Calibrated drift/route motifs and actual B3 histories show the thickest buildup beside structures, its path cost, clearing/erosion and fog range/movement recovery with all retained systems running. The local material looks like ice grains and other biome sand retains its own appearance. Unreadable depth or forced clear weather returns unmeasured. Clean log. A dusting or thin layer alone fails. RM_IceSandDrift’s own movement multiplier cannot supply deposition evidence. Clearing restores the deposit-free trip with pawn, topology and weather matched. Read fog slowing and targeting recovery separately on deposit-free matched routes.

## T15: Repair and extend the existing observer and recovery contract

Existing validation.py, northstar_plan/site, prove_* scripts, kernels/fuzz, fake-game and result-row gates are real partial tools. They do not provide whole-map or loose-ice acceptance. Fixed pad clears, overly wide flora placements, forced weather, restore-to-defaults and unbound historical rows can fake success. Separate bar evidence from tuning checks and optional-feature suites. Capture source/assembly/defs/art/settings/dependency/save fingerprints; trace source-attributed damage/blast/food/conversion/job events and actual current state. Snapshot the disposable baseline and settings, restore by reload and exact readback. No arbitrary scrubbing or swallowed cleanup failure. Support a real-look packet for B1, with no unattended flight image hunt.

Acceptance test: Each proposed bar has a witnessed start, positive action, discriminating control and recovery read; deliberately weakened/unmeasurable scenes cannot pass. Unreadable fields return UNMEASURED. A failed scene leaves a restorable baseline and verified unchanged original journal; settings return to the captured values. Optional suites cannot satisfy retained bars, and seasonal evidence cannot come from locked-sky pads. Clean log after restore.

## T16: Record the obsolete cold-cutting/study-suppression premise

The earlier ladder has no implementation and ColdCuttingSuppresses returns false. Keep its dormant seam load-safe while ordinary mining is decoupled under T4/T13. Recommend retiring cold-cutting as a mechanic because the later owner answer explicitly uses ordinary ice mining. The distinct optional archaeological reading remains T26. No request to re-approve this premise.

Acceptance test: Fresh defaults require no cold-cutting unlock and call no suppression/loot progression. There is no on-state implementation to test; no technique is invented to satisfy the old rehearsal question.

## T17: Loose-ice thermal behavior and cold-hold support

Owner answer two requires cooling from the ice itself. Current RM_BlueIce has no implementation. Define/build finite exchange/reserve on ordinary stacks, no target gizmo/rack requirement: ice warms sensibly, then melts while absorbing latent reserve, and returns ordinary water through agreed consumer ownership. Show remaining reserve/phase and which organics need response. Preserve mass/reserve under split/merge/haul/unload/save, with honest carried/off-map container policy and no recharge on recipe conversion. Thermal ledger is the first implementation design input, not the old rack constants.

A prepared closed cold hold with full ordinary reserves must stay cold on loose ice alone far beyond the time an available ordinary crew takes to repair cooling. Use the same fault, materials, heat input and approach route in repair/no-repair arms. Continue the unpowered arm well past actual repair completion and record substantial remaining reserve and cold holding. Partial reserve and intentionally excessive load are separate exhaustion stress cases.

Acceptance test: In calibrated loaded/no-ice enclosed-room comparisons with positive heat input and power off, loose ice measurably absorbs finite heat and permits actual repair in the prepared repairable cases; no rack exists. Exhaustion is visible, water mass is accounted, and native warnings continue honestly after reload/split/container return. Outdoor/empty reserves do not supply unlimited cold; feature-off stops this scripted cooling without deleting ice. Clean log. The full-reserve closed-room arm still holds cargo cold with substantial reserve well after the ordinary repair arm finishes, under each declared supported load/weather regime. A full stockpile exhausted before repair, or only just outlasting it, fails B6. Continued positive heat input eventually exhausts the reserve honestly.

## T18: Switch off thunderbeast electrical toolkit, retain the animal

Callers: race.tools shock capacity/maneuver, VEF-guarded InitialAbility/arc projectile, EnvironmentalHazards flashstorm deathAction in RM_Thunderbeast.xml. Add an independently gated next-version toolkit, default off, with ordinary basic attack fallback and native fuel physiology supplied by T12. Preserve all defs, projectile/type references and roster membership. Do not disable shared EnvironmentalHazards storms globally or mistake a storm for a native fuel release.

Acceptance test: Fresh defaults have the same admitted animal but no electrical attack ability/job, static arc or death-summoned flashstorm, related letters/incidents, and clean log; ordinary attacks and native physiology work. Enable optional setting and the declared electrical toolkit appears, including VEF-conditional arc only when its existing dependency is installed. No absence-of-VEF test substitutes for the optional-on arm.

## T19: Switch off fog's independent shuttle veto

Caller: RM_IceFog.preventsShuttleLaunch is read by the Core launch predicate. Gate that behavior separately under next-version default-off, preserving fog overlay, aim, reach and travel modifiers. If applying to the WeatherDef requires a live adapter/settings-write update, state that scope honestly. No rule changes to the actual vanilla targeting limits.

Acceptance test: Fresh defaults in actual ice fog have no added weather launch-prohibition state, related blocked job/letter/incident, and clean log; all other launch prerequisites satisfied, the normal launch action remains offered. Optional setting on exposes the weather-specific veto. Fog still restricts its ordinary sight/travel in both arms.

## T20: Future quarry-to-Horrors delivery spec

Promised cross-call is absent; RUT_NightHorrors already owns proximity/temperature crysalises. Before a future version, define release source, reveal/retreat sign, containment and campaign tier using that owner, without a parallel engine. No default mining caller or extra release now.

Acceptance test: Fresh defaults expose no local mining-triggered crysalis release or related job/letter and log is clean; no on-state test exists until a future delivery spec/implementation is accepted.

## T21: Future dovvik safe-trail/minesweeping spec

Ordinary tame grazer exists; drain flag/temporary-safe tint/custom job do not. Future definition must settle target choice, temporary charge state, recovery/expiry, tame control, native/foreign ingestion and reload without making permanent safe fuel.

Acceptance test: Fresh defaults have no drain/sweep job or temporary-safe plant state; ordinary dovvik feeding remains and log is clean. Acceptance test for optional on-state: none, no implementation exists; a future version must define and test expiration/reload before enabling.

## T22: Future live vhaulk valve operation spec

No operation worker found. Future definition must specify the player interaction, valid body part, interruption/yield/cold handling and manhunter/EMP consequences; preserve the ruled death gates. It is not normal butchery.

Acceptance test: Fresh defaults offer no valve operation/job or product and log is clean; optional on-state test: none, no implementation exists and the operation is outside this version.

## T23: Future gravship-specific drift burial spec

No local ship burial/dig-out integration found beyond ordinary sand accumulation. Future definition must give hull geometry, interaction with vanilla launch/doors/pathing, dig-out task and save/transport behavior; reuse existing weather rather than a new snow engine.

Acceptance test: Fresh defaults have no ship-specific burial job/launch tax/letter and log is clean; generic B3 drift remains. Optional on-state test: none, no ship integration exists.

## T24: Future passage giant exposing buried ground

Later owner answer three supplies purpose, not a species selection or geometry/state spec. Do not resize the existing vhaulk or restore rime road. Future definition must choose existing passage dependency/eligible identity, exposure footprint and frequency, prior-ground ownership, find/hazard budget, notice and persistence. Ground discovery is the experience, not a new road buff.

Acceptance test: Fresh defaults have no new passage-exposure producer/letter/job/find and log is clean; existing vhaulk and its walk-off remain. Optional on-state test: none, no ground-exposure or selected visitor implementation exists.

## T25: Do not build optional milelace reseeding; recommend retirement

Source search found only the optional Garden pitch. Ordinary wild growth already repopulates plants; no named experience requires a second storm seed producer. Keep the plain plant.

Acceptance test: Fresh-default storms produce no special milelace reseed state/producer/job/letter and log is clean; optional on-state test: none, no implementation exists and retirement is recommended.

## T26: Future quarry epochs, translations and rites integration

No study/epoch worker found. Keep the older campaign history as design input for next version, without adding it to RM static context. Future definition must distinguish visual epochs, deciphering steps, full reading, any hazard knowledge and the separate rites owner. Do not restore cold-cutting as a prerequisite by implication.

Acceptance test: Fresh defaults contain no epoch-study/translation/rite integration job, unlock, letter or incident and log is clean; optional on-state test: none, campaign progression needs its future definition and implementation.

## T27: Build situation and lifecycle generator instrument

Implement the first model in models.md; reuse existing kernels/fixture primitives where trustworthy. Export the real callback states it needs, mark absent readers unknown, and calibrate every handler class before interpreting offline output.

Acceptance test: A real trace for each declared transition class agrees under the model's calibration contract; deliberate missing corpse charge, warming serialization and optional producer gate mutations produce bar-specific counterexamples; missing state returns unmeasured. Report coverage and smallest witness, never “all fields match.”

## T28: Build whole-season coupled instrument

Implement Whole-season coupled map and a full-map state observer; retain actual-rate growth/weather/jobs/heat while only accelerating wall time. Core AI must be observed/replayed or explicitly conditional, never replaced by guessed probabilities credited as game evidence.

Acceptance test: Matched save histories satisfy model calibration; full 15-day traces include midpoint reload and both B8 orders at declared colony scales with all kept systems running and no locks. Injected silent reseed, hazard-off clear pad and repeated predation-extinction cases cannot be labelled passes. Report causal flood/desert/stall/error-storm witnesses and restored baseline.

## T29: Build containment geometry instrument

Implement Containment geometry sweep with actual blast/heat/path callbacks and captured local geometries. It must include moving/held/dead fuel bridges and ordinary clearing actions.

Acceptance test: All calibration motifs agree with real causal ignition/retreat traces; a dropped wax/body bridge and threshold corner change the predicted component rather than being rounded away. Prepared/unprepared arms use identical task/ignition; smallest failing placement is emitted, and no model-only forecast is presented as a measured game pass.

## T30: Build thermal ledger instrument

Implement Thermal reserve ledger with energy/mass accounting and reader quantization explicitly named; derive units from matched rooms before choosing physical constants.

Compare finite passive cold holding to actual ordinary cooler-repair traces, including storm-delayed access. Calibrate the unpowered loaded-room arm well beyond the repaired arm’s completion.

Acceptance test: Ice/no-ice/traffic/load/split calibration cases meet model agreement criteria, a secretly powered cooler and a reserve reset are caught, and an energy-creating conversion loop fails. Output feasible repair regimes and temperature/reserve/warning curves, each labelled modeled versus game-observed. Publish both repair completion and later ice-exhaustion witnesses with remaining cold holding/reserve at completion. A model that accepts a reserve merely beating repair must fail its B6 classifier.

## T31: Build drift and route instrument

Implement Drift and route geometry; use the real sand/path/targeting readers and captured grids, not a stand-in aerodynamic simulation.

Explicitly read the storm movement multiplier as a confounder. Deposit attribution uses post-storm histories before erosion or equal-weather deposited/deposit-free twins. Deep-buildup classification requires the thickest SandGrid category on permitted approach cells beside structures, with its added movement cost persisting until sand clearing or erosion.

Acceptance test: Representative wall/door/hull approach motifs agree cellwise in depth category/path cost within reader precision, and actual travel/shot consequences are attributed. An overlay-only, dusting-only or thin-layer-only build fails B3. Unavailable readers return unmeasured. If natural storms fail to reach the thickest category, report the weather trace and accumulation shortfall for tuning within the ruled SandGrid mechanism. A zero-deposit storm slowdown fails deposit attribution. Sand clearing restores the deposit-free trip under matched weather. Fog travel is isolated on deposit-free routes with identical pawn state and topology.
