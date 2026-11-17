# Proposed work; nothing implemented on this pass

These are proposal-local tickets, not ledger entries. All implementation belongs after review and owner acceptance. Built code/defs remain in the tree. Each deferred feature gets a saved Mod Setting labelled **Next version**, default **off** in fields, Scribe fallbacks, reset defaults and composed UI. Gate every entry point, not only its menu or message. Its enabled arm is an activation check, not acceptance of its gameplay. Use disposable fresh-map copies with the same package/DLC/dependency/settings fingerprint; run through the natural triggering interval and state-read objects, jobs, letters, incidents, resources, abilities, menus and event counters independently of debug summaries. Check the log in both arms. Declarations alone do not establish inertness. Current old saves retain def/types and undergo explicit safe cleanup; no silent deletion of pawn identities.

## T1: Switch off rain flood releases and decouple the liquid link

Rows: floods, flow_link. Kept caller: Rain DoPhaseWork -> TryFloodRelease in RM_GameCondition_ForgeCycle.cs. Gate this call and any debug entry; preserve the rain ForceBurst and flash writes. Default cycle neither constructs Flood_FlowWorks nor needs its volume calculation. Compile references are coupling, not a reason to ship floods; keep compatibility or isolate the deferred adapter so an absent liquid dependency cannot break retained behaviour. Existing floods remain owned by FlowWorks, not deleted by Forge. Do not redesign water spreading.

Acceptance test: On a fresh default map through Rain and the following cycle, no Forge-created fluid-flood thing, pooling message or release event appears and log is clean; with Next version rain flooding on and its declared FlowWorks dependency loaded, an eligible rain produces actual flood things and release events. In both arms crust/garden/rain progression runs, and absence of an eligible release site is separately a no-op control.

## T2: Switch off the orchestral phase voices

Rows: phase_voices. Callers: cycle voices.Tick, End and GasWashWave’s optional cough in RM_GameCondition_ForgeCycle.cs; RM_ForgeVoices.cs sustainers and visual fallback. Preserve ordinary weather ambience and the necessary text warnings in the cycle. Ensure muting or disabling orchestration does not remove hiss/cracks information. The prior vanilla-audio waiver remains accepted; no new audio commission or re-proof of that waiver.

Acceptance test: Fresh defaults produce no Forge voice sustainers, stingers, cough/glass events or duplicated voice prose while actionable phase warnings remain and the log is clean; enabling Next version phase voices produces the matching phase events and stops sustainers on camera departure/off/End. Read emitter/event state; a subjective sound test is unnecessary for this activation check.

## T3: Switch off the supplementary dhuvvox run clock

Rows: dhuvvox_clock. Callers: ClockOn, run sound tick, UpdateSlowing, RunEndTick and CurlBack branches inside RM_CompForgeCycleDormancy.cs. Basic CompCanBeDormant wake/seal, identity and dormant body drawing remain on. Gate the slow hediff and click/scuttle schedule separately from core sealing; clean an old residual slowing hediff without destroying its pawn.

Acceptance test: At fresh defaults resident dhuvvox wake/seal normally but carry no run-slowing hediff, countdown field in inspect UI or clock sound/curl event, and the log is clean; enabling Next version run clock exposes its countdown, slow stage and sound/curl events during a valid wet interval. A matched pawn retains its identity through both arms.

## T4: Switch off injected dhuvvox mass eruptions

Rows: extra_swarm. Callers: EnterPhase Rain -> EruptSwarm, Freeze -> ResealSwarm, debug action and saved swarm list in RM_GameCondition_ForgeCycle.cs. Gates must prevent injection as well as the message. For an old active injected population, release surviving pawn identities into ordinary residents at shutdown, or complete an already promised readable lifecycle before marking the feature inactive; do not reuse resident resealing as permission to delete them. Keep the accepted resident-pawn nodule design and conditional swarm-budget waiver; no request to reopen either.

Acceptance test: Fresh default Rain creates no additional swarm-tagged pawn, eruption/reseal letter/message or scheduled deletion and log is clean; enabling Next version extra swarm on a valid map injects tracked animals and reaches its enabled lifecycle. Old-save off/reload retains surviving tame/dead identity records and provides explicit resolution of wild extras; baseline resident population is never mistaken for extra output.

## T5: Switch off the elaborate dhokkur wake show

Rows: dhokkur_wake_show. Caller: DhokkurWays comp awake-transition effects. Keep basic dormant/walking art and the minimal wake information from the retained dormancy comp; gate groan/splash/dust/pour timers together. No dependency from basic dormancy to this show is retained.

Acceptance test: Fresh defaults and a natural wild-dhokkur wake produce no DhokkurWays splash/pour/groan event or extended timer, but the same pawn wakes visibly, with clean log; enabling Next version wake show produces those events on a sealed-to-awake transition and resets them on off/reload.

## T6: Switch off dhokkur roads and depressions

Rows: dhokkur_tracks. Callers: step and seal callbacks in DhokkurWays, path-memory MapComponent and fade logic; shoves read the same polished temp terrain. Disable accumulation, new polished layers, depression work and fade mutations at default. Preserve old serialized wear and foreign terrain. Do not change previously waived fade/wall choices or pretend saved wear makes a pawn return by that route.

Acceptance test: Fresh defaults through repeated dhokkur walks/seals create no polished-track/depression temp terrain or wear work and log is clean; enabling Next version dhokkur roads creates owned track state after its configured repeated-step conditions. Off/reload never removes foreign temp terrain or exposes a pawn to lava.

## T7: Switch off trail obstruction shoves

Rows: dhokkur_shove. Callers: DhokkurWays interval -> TryShove and RM_DhokkurKernel.Shove. Independently gate all move/minify/damage fallback effects, including a retained old polished trail. Do not reopen settled mode preferences. No new wall simulation is necessary for first-version acceptance because this mechanic is off.

Acceptance test: At defaults a fresh map with a seeded regression trail and obstructing artificial wall shows no dhokkur relocation, minification, damage or shove message and log is clean; enable Next version shoves plus its road prerequisite and a configured eligible obstruction reaches the appropriate effect. The giant still wakes/walks in both arms.

## T8: Switch off dhokkur vent routing without disabling sky life

Rows: dhokkur_columns. Callers: RM_JobGiver_SkyPastureWander.Leash and RM_JobGiver_SkyPastureHoming, DhokkurColumnsExtension. Gate the dhokkur branch only; sky drifter habitat stays enabled. This decoupling is necessary because both live in RM_ForgeSkyPastures.cs.

Acceptance test: Fresh defaults produce no dhokkur column-homing job while awake drifter habitat jobs still occur and log is clean; enabling Next version dhokkur vent routes produces a valid dhokkur homing job when a reachable column exists. Do not certify actual remembered-road return from nearest-column selection.

## T9: Switch off blue-gel production and access

Rows: bulloo_gel. Callers: both VEF AnimalProduct comps name RM_BlueGel; no consumer found across supplied src. Keep the item def and old inventory loadable but prevent generation, gather jobs and new procurement offers from this feature at default. Preserve ordinary animal feeding/floating. Remove or label battery/generator claims as next version; do not build consumers to justify a def.

Acceptance test: Fresh defaults through both product intervals contain no newly produced blue gel, matching gather job/letter/recipe/offer, and log is clean; enabling Next version blue gel with VEF loaded produces actual gel through the existing comp. A fresh start distinguishes new output from preserved old stacks.

## T10: Switch off special bulloo fission

Rows: bulloo_fission. Callers: VEF AsexualReproduction on small and greater bulloo. Gate both same-kind multiplication and greater-to-small conversion without disabling ordinary wild arrivals or hiding species. No fabricated escort AI is added.

Acceptance test: Fresh defaults through the longest configured fission interval create no fission event or parent conversion and log is clean; enabling Next version bulloo fission with VEF loaded reaches both configured lineage transitions on separately eligible specimens. Track parent/offspring IDs to distinguish ordinary wild spawn and require readable signs for any parent conversion.

## T11: Quarantine bulloo detonation; recommend retirement

Rows: bulloo_detonation. Callers: vanilla SmallExplosion/BigExplosion deathAction workers, small-bulloo VEF ability and Odyssey specialTrainables in race/kind XML. A UI checkbox alone cannot gate a deathAction: use the existing feature-gating/def-application mechanism to select inert ordinary death behaviour at default, preserving corpse/butchery. Pending owner decision, keep definitions and no deletion. This is recommended because vanilla explosive livestock already supplies the experience.

Acceptance test: Fresh default bulloo and greater-bulloo deaths produce ordinary readable death/corpse state with no detonation damage/fire, no special detonation ability or trainable and a clean log; enabling Next version bulloo detonation restores configured explosion/ability activation. Check ordinary corpse and Bones/hide products still work in the default arm.

## T12: Switch off the metal-eating economy as a unit

Rows: metal_diet. Callers: VEF EatWeirdFood comp, its configured steel/silver/gold/ore/slag targets and unguarded VEF_AnimalWeirdEater thinkTreeMain. Default must use ordinary herbivore feeding and a valid normal think tree, including with VEF guards excluding its comps. The source name/descriptive metal-diet claim becomes labelled next version, not a false default food promise. Do not redesign the creature engine or evict the animal.

Acceptance test: Fresh defaults through hungry-animal feeding leave the test metal/ore stock unchanged, create no weird-food/dig job or slag and have a clean log while the animal eats ordinary allowed food; enabling Next version metal diet with VEF loaded creates its metal-feeding/fallback dig jobs and actual consumption in the separate eligible controls.

## T13a: Switch off camera-near ash spirals

Row: sky_spirals. Caller: ash-spiral branch in RM_ForgeSkyPastures.cs. Default-off next-version gate must remove events without disabling the retained static column haze, field or habitat jobs.

Acceptance test: A fresh default map with real columns produces no camera-near ash-spiral emitter/event and log is clean; enabling Next version ash spirals produces the existing events when viewed near columns. Static haze and habitat state remain in both arms.

## T13b: Switch off selected-animal column highlighting

Row: sky_highlight. Callers: selection draw and RebuildHighlight in RM_ForgeSkyPastures.cs. Gate this supplementary overlay independently of ordinary visible columns.

Acceptance test: Fresh defaults with a selected drifter show no selection-only column highlight state/draw list and log is clean; enabling Next version column highlight creates the existing selected-animal overlay, which clears on deselection. Ordinary haze/habitat remain active.

## T13c: Switch off column-biased prey scores

Row: jossur_hunt. Caller: prey-score Harmony postfix in RM_ForgeSkyPastures.cs. Preserve vanilla prey eligibility, ordinary predation and flight; no global predator switch.

Acceptance test: Fresh defaults give matched column/non-column prey the vanilla scoring contribution with no Forge bias and log is clean; enabling Next version column hunting adds its configured bias to eligible prey while leaving unrelated predators unchanged. Real hunting jobs remain possible at defaults.

## T13d: Switch off the special jossur stoop

Row: jossur_stoop. Caller: JossurStoop comp in RM_ForgeSkyPastures.cs and its race def. Preserve core MaxFlightTime and ordinary job-triggered flight; the special stoop is not the only permitted way for this bird to fly.

Acceptance test: Fresh defaults create no special distance/cooldown stoop request or comp event while independent flight-state evidence still establishes real flight, and log is clean; enabling Next version jossur stoop produces its qualifying request/state transition. Use flight-tracker state; respect the owner-presence rule for any deliberate live flight experiment and do not film flight.

## T14: Switch off the externally patched fungus study source

Rows: fungus_study. Caller discovered outside TheForge: RM_ShadeLessons_Sources.xml appends CompProperties_FoundTechStudy for RM_HeatsinkFungus under EnvironmentalHazards.ShadeLessons. Add a Forge-scoped next-version gate at this source/adapter; do not globally disable shade lessons or alter other biomes. Do not require the fungus to teach research in order to count as living flora.

Acceptance test: At fresh defaults an otherwise enabled shared ShadeLessons system exposes no study job, inspect progress or discovery letter sourced from this fungus, and log is clean; enabling Next version Forge fungus study makes that source available. A different valid shade-lesson source remains unaffected in both arms.

## T15: Quarantine the unsupported fungus-cooling promise; recommend retirement

Rows: fungus_cooling. A bounded exact-name/source-comp search found no implemented cooling, but generic external hooks have not been ruled out. Retain the plant, tolerance and flash growth. Recommend retiring its cooling claim as duplicate vanilla shelter/cooling; until decided label the behaviour next version and leave it inactive. Trace loaded generic temperature hooks before claiming no implementation. Do not implement a cooler just to satisfy old description text.

Acceptance test: With fresh defaults, matched rooms with/without the fungus have no fungus-attributed active cooling component or room-temperature effect and log is clean. Acceptance test for enabled cooling: none, no concrete implementation is located to activate; if runtime discovery finds one, identify its source and add positive/negative activation cases before enabling it. The plant description must not advertise cooling as shipped behaviour.

## T16: Define and supply ordinary surface foundry identity

Rows: ordinary_works, melt_machines; informs B1/B8. Missing promised behaviour, not an extra. Surface content must show whole standing manufactured towers (not merely generic ruined pebbles) and remnants such as bases/channels/yard edges which change ordinary resource paths while leaving permanent shelter/work connections. Use existing Wreckage placement, occupied-footprint and ordinary salvage contracts where applicable, no new loot ladder. Local-map placement on the fixed authored world is distinct from forbidden planetary worldgen; add no world selection, planet or variant feature. Do not claim an existing generic wreck field is Forge-specific content.

Minimal ambient nonliving melt machinery may convey the frozen always-true motion without a creature, combat AI, resource or interaction system. Its task is never explained in a name, inspect text or quest. Historic tower interiors, tenders as a garrison and plot explanations remain separate deferred content. Recover the existing art/content inventory before commissioning anything; no art is made on this pass.

Acceptance test: Ordinary surface journey captures plus exact footprint/path reads satisfy B1 with default extras off, including rain/fog and settled maps, and demonstrate safe permanent connections. Removing the surface-content placement in a control removes both recognisable manufactured form and the physical route effect. Nonliving background motion is readable and reveals no task; no portal job, custom quest/reward/incident or live tender encounter is exposed by default. Log is clean.

## T17: Close the retained cycle specification and transition gaps

Rows: ground, weather, flash_flora, cycle, gas, scald, crust, gardens, melt, telegraphs, arrival, dormancy, floatstone. This is core work, not a demand for more bars. Preserve natural seven-state timing and generic stuff construction; tune against experiences and existing economy constraints, not regression counts.

Required repairs/contracts: remove Forge heatKind/offset and false shade-irrelevance claims, connect only to the standing common Direct Sun rule; boiling rain must be the only liquid rain (neutralise the independent ordinary ash-rain branch without creating another mechanic); local master/pulse-off restores ordinary Forge plant growth rather than the shared outside-window penalty; premature End settles owned crust/gardens and saved phase state, not just sound; safe cleanup searches the permanent connected region and, when no valid landing exists, retains a labelled pending safe-support state rather than exposing living pawns/items to lava. Gentle mode may wither plants and deconstruct unsupported buildings, but must move/preserve leavings and explicitly report what happens. A resumed pending cleanup resolves before a fresh reward seed or restart. Never erase foreign temp terrain or transient projectiles.

Pin no new yield/phase number. Actual first-surprise survival, native exposure, connected opportunity and deadlines remain unknown until modeled and read. T27 provides instruments; the builder chooses the smallest compatible algorithm and attacks R2/R5 before weakening bars.

Acceptance test: B2/B3/B4/B6/B7 readers pass across their declared ranges at all-on defaults and deliberately failing controls are detected. Show exact object/layer ledger through each phase/off/End/reload boundary, including no-safe-cell cleanup, independent weather/HP reads, no ordinary rain, correct shared geometric sun and restored local-off growth. Log is clean; no debug phase jump or scald suppression qualifies as natural progression.

## T18: Close ordinary native sustenance and locomotion contracts

Rows: retained fauna, column_haze, sky_habitat, vapor_sustenance, framework. Snapshot merged loaded roster without eviction or renaming. Keep all inline species and optional campaign cast; annotate any multi-home placement and its known reason rather than inventing an allocation rule. Current checkout cannot establish other-biome memberships.

Sky nourishment is a promised gap: RM_CompVaporDrifter supplies geography/immunity, not calories. Use existing CreatureBehaviors feeding/needs interfaces and EnvironmentalHazards habitat field; request only the supported native-forage contract and provide Forge data/adapter wiring. Existing RM_FilterFeedExtension demonstrates terrain feeding, not a field-aware vapor metabolizer. Do not mislabel terrain membership alone as proof of gas feeding or design a chemical economy. Natives must be able to maintain ordinary needs at their own actual habitat, and their own environmental water must satisfy thirst where the shared system applies. Basic drifter movement yields to urgent food/rest and does not monopolise all job choice.

Core flight and permanent bulloo floating are retained even with combat/fission extras off. If VEF is the only working float provider, declare the actual required framework dependency for those animals instead of silently grounding them when its guard strips a comp; use the shared flight contract if already supported. Preserve greater-bulloo feeler animation as ordinary body motion (it is not a prohibited wing tree). Ummisk remains on standable banks, moves to a new edge if one is reachable, and falls back to ordinary safe wandering if none exists; no trail or lava-native life. Basic resident dormancy uses actual Awake/job/identity, not just an inspect line.

Acceptance test: B5 native identity/needs/habitat/flight-state readers and M3 held-out traces show living feeding and husbandry without debug need filling, magic immunity or endless hunger/homing loops; local-water tests satisfy native thirst without making player scald water potable. An off-extra/default comparison keeps core flight and habitat active. Track IDs through taming, injury, death, caravan and reload; log is clean. No unauthorised live visual flight experiment.

## T19: Switch off white moving plume fronts

Rows: plumes. Kept callback: FreezeBatch -> RM_MapComponent_PlumeFronts.NoteCrusted. Gate source creation, persisted front ticking, heat postfix, smoke/wet injection and announcement together; keep plain quench fog and visible ordinary steam. Purge only Forge-owned active field state on off, allowing vanilla gas/filth already created to expire normally. Do not leave a hidden heat modifier after the draw disappears.

The owner answer is settled for later enabled fronts: walls stop the immediate front; roofs alone do little against sideways steam; closed rooms still have ordinary air temperature. Current heat marking before the filled-cell guard is not compliant. Deferral does not grant an exception, and no new question about that rule is raised.

Acceptance test: Fresh defaults through Freeze show no plume fronts/owned heat cells, plume smoke or wet-filth injection, announcement or temperature postfix effect and log is clean; enabling Next version moving plumes exposes those effects in a valid quench region. Before enabled gameplay can be accepted, a wall/open-roof/enclosed-room geometry reader must satisfy the existing shared physical rule; the current through-wall implementation may fail that separate check.

## T20: Switch off dhoggur chemical swell

Rows: dhoggur_swell. Callers: damage comp callback, swell hediff/body/bite/health patches, render state, fire-spit grant and world-pawn registry. Preserve ordinary docile foraging/hide and old state keys. At off, reconcile an already swollen pawn through its existing shrink rules, with readable injury/death consequences, not silent hediff/state corruption. Do not reopen the settled attack trigger, real size/health/bite, duration, end-based cooldown, no-hit-refresh or accepted death-on-shrink rulings; they remain the enabled feature’s specification.

Acceptance test: Fresh default attacks create no swell state, fire-spit ability, swell-driven manhunter or body/health/stat scale change and log is clean; enabling Next version chemical swell makes a qualifying attack trigger the real saved reaction and cooldown. Environment-only damage stays nontriggering at its settled default. Old-swollen off/reload/caravan cases follow recorded shrink outcomes without lost identity.

## T21: Switch off spunstone discovery and research

Rows: spunstone_study. Callers: garden CompProperties_SpunstoneStudy, shared FoundTech study workgiver/hidden-project patch, RM_SpunstoneKnowledge legacy facade and historic campaign cache source. Keep RM_TheForgeStartup Harmony registration, save import and class names load-safe; a retained startup initializer sharing this file is not need for the study feature. The current off behaviour exposes the project, so simply flipping spunstoneStudyEnabled is insufficient: gate study jobs, project/menu availability, progress and discovery letters at defaults. Ordinary Stony building must never consult this project.

Acceptance test: Fresh defaults expose no spunstone study job, progress, research project or discovery letter while actual garden harvesting/ordinary floatstone construction works and log is clean; enabling Next version spunstone discovery exposes the source/hidden-project progression and a real study interaction adds knowledge. Recovered campaign cache study observes the same local gate. Old knowledge loads without activating the feature or changing other found-tech projects.

## T22: Switch off the special floatstone door

Rows: special_door. Callers: startup RM_SpunstonePartsGate and RM_SpunstoneBonding prerequisite. Hide both new designators and any recipe/construction offer at default; preserve old installed instances and defs. Explain any next-launch-only change honestly; default-off must already be effective on a fresh launch. This is independent of ordinary floatstone doors available via vanilla stuff compatibility.

Acceptance test: Fresh-launch defaults expose no RM_FloatstoneDoor designator/build job, recipe or generated instance and log is clean; enabling Next version special door and applying the declared restart plus legitimate research in its separate copy exposes an actual build. Existing instances survive off/reload with no missing-def errors.

## T23: Switch off the special spunstone hull

Rows: special_hull. Callers: the same startup gate and bonding prerequisite, separately gated. Preserve the def and old hulls; no fuel-saving ring/keel/brace is restored or asked about.

Acceptance test: Fresh-launch defaults expose no RM_SpunstoneHull designator/job, recipe or new instance and log is clean; enabling Next version special hull, applying restart and completing the enabled research exposes its build. Default ordinary floatstone construction and old hull load safety remain intact.

## T24: Provide the proposed defaults/settings contract

Rows: settings; cross-cutting necessary exception. Retained major switches: master; pulse; grand cycle; gas; freeze; destructive melt; gardens; flash growth; basic dormancy; sky habitat/column display; ummisk bank movement/steam; physical surface remains and warnings where individually configurable. Keep useful tuning and restore defaults. Label dependency relationships and restart-only choices; disabling upstream features must not leave downstream penalties or actors stranded. A warning toggle may hide routine prose, but phase deadline/terrain/inspect and casualty evidence must remain readable. All-off changes mechanics, not roster existence or the fixed planet. Expose no world-creation controls and add no new cross-biome option.

Acceptance test: Floor C5 and M1 settings branches show saved/reset defaults matching this proposal, controls changing real effects, all-off safe outcomes and next-version switches all off; no unsupported feature is presented as active. Fresh/reloaded source/composed config reads agree and log is clean. Major-feature off/on changes must leave unrelated biomes/dependency settings unchanged.

## T25: Hide inert scaffolding controls; recommend retirement

Rows: scaffold_knobs. RM_TheForgeMod.cs header and UI show tibanna rate, vapor immunity, tower count, ring density and vent speed which do nothing. Do not wire extra gameplay to rescue these knobs. Recommend retiring the inert UI; pending decision preserve serialized keys and hide or label nonoperative next-version placeholders, never advertise them as shipped settings.

Acceptance test: Fresh default settings show no functioning-control claim for these inert fields and no associated actors/effects are activated; log is clean. Acceptance test for switching on operative behaviour: none, these are acknowledged unwired fields, not implemented features. If any remains visible it is explicitly nonoperative, next version and disabled; changing it cannot silently affect retained mechanics.

## T26: Switch off optional acoustic content

Rows: scanner. Caller: FindMod-guarded RM_AcousticPayload_TheForge.xml adds biome content consumed by external scanner. Use a Forge-specific next-version gate; the scanner engine and other biomes’ scans remain independent. Necessary arrival explanation stays on. Existing absent scanner is a no-op case, not proof of the gate.

Acceptance test: Fresh default state with the scanner actually installed provides no Forge acoustic payload/reading/scan-triggered content and log is clean; enabling Next version Forge acoustic payload produces the existing Forge readings through a legitimate scan. Scanner-absent copies load clean in either state, with no claim to test DLC absence.

## T27: Build the missing bar readers and models

Rows: proof_tools; instruments for B1–B8. Implement M1–M4 as specified in models.md, reusing useful kernels/debug/schema adapters, not inheriting the old suite’s disabled-damage claims. Add independent world-object/terrain/needs/health/material ledgers, natural job/clock and weather-unlock preflight, mid-cycle save/reload, action-order scheduling, loss attribution and complete copy-disposal/reset journal. Make every failing control actually fail its intended reader. A debug counter or self-consistent mock is only a check. Add one B1 paused ground-view recipe; no flight filming or unauthorised flight experiment. No instrument is built during this design pass.

Acceptance test: Each reader sorts bars.json accept/reject fixtures correctly and kills its named false-positive/mutation; M1–M4 meet their stated real-game calibration before predictions are trusted. An uncalibrated model reports unknown, not measured/pass. The default natural season run refuses locked weather, disabled scald/dependency growth, phase jumps or missing fingerprints and can be rerun from disposable original saves without leaked state. Validate only relevant checks once instruments exist.

## T28: Recover and gate unavailable campaign integration points

Rows: campaign_cast, campaign_towers, campaign_gas, campaign_ore. Current checkout has no RimUtinni/RimStarWars source or roster directory; earlier record provides historical inventory, not current binary proof. Locate the real loaded source/defs when the build stage can access them, record its fingerprint and merged cast, and leave all species placements intact. Retain ordinary external ore without designing a new system.

Tower interior portals/dungeon/garrison/salvage-study and tibanna harvesting/embargo are next-version content for Forge, default off. Gate actual exterior portal interactions, local scatter/incident/tap jobs and discovery letters, not the necessary physical tower silhouette or ordinary beldon creature. Do not globally break campaign systems owned elsewhere. Beldons remain the only permitted tibanna source if the deferred harvest is enabled. No restoration of struck vent-industry, heat-exchanger or fireweed economy follows from recovery.

Acceptance test: On a fresh default campaign-capable Forge map with actual recovered integrations loaded, ordinary retained cast/ore/surface works are present but no tower portal travel job/interior generation, tender encounter, salvage-study letter, gas tap/output or embargo incident is activated by Forge, and log is clean; enabling each relevant next-version setting exposes its existing entry point with necessary dependencies. Verify cast inclusion and annotation without eviction. Current evidence cannot execute this test; mark it unmeasured until source is recovered, rather than assuming the historic integrations absent.

## T29: Switch off Contagion test incidents and dynamic ring

Rows: campaign_ring. Present caller RM_IncidentWorker_ContagionProbe targets RM_TheForge; historical edge-band/die-off/IncidentDef wiring is not in supplied src. Gate CanFire/TryExecute and recovered scatter/spread/death/letter entry points locally. Existing Contagion elsewhere remains governed by its own mod. Inert environmental dead traces may express lore as land; no continuing invasion system is needed in first-version Forge.

Acceptance test: Fresh default Forge across repeated eligibility checks and direct incident-attempt negative control has no probe-triggered creep actor/spread, death timer, incident or letter and log is clean; enabling Next version Forge Contagion probes with recovered content loaded produces the actual incident and its readable dying patch. A non-Forge Contagion scenario is unchanged. Unavailable IncidentDef wiring must be recovered before claiming positive activation.

## T30: Make forbidden world-scoring inert; recommend obsolete-code retirement

Rows: legacy_world_scoring. RM_BiomeWorker_TheForge.GetScore and source comments explicitly permit automatic alternative-world assignment. Standing no-worldgen ruling already prohibits that promise in every version. Recommend removing obsolete scorer implementation/comments when the owner accepts retirement, but this proposal retires nothing itself. Required compliance is no exposed world-creation feature and no active automatic assignment; retain a load-compatible inert worker if the def needs its type. Never create a Next version worldgen toggle.

Acceptance test: Static and resolved configuration reads show no alternative-planet/seed/automatic-assignment entry point, worldgen UI or promise, and an invoked worker returns only its nonassigning result; the authored Forge def still resolves and the log is clean. Acceptance test for enabled worldgen: none, prohibited by the standing ruling in every version. No world tile count is tested or treated as a defect.
