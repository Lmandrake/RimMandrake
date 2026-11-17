# Build tickets proposed for after review, adoption and hold release

No ticket is executed on this pass. A clean log/loading/settings floor is inherited, never a new numerical passing bar. All code/defs stay in the tree for moved features; switches default off and say next version. For built extras a positive opt-in read is a diagnostic of presence, not certification of that future version. Shared-switch tickets are separate capability obligations and execute together. Retirement tickets neutralize forbidden/acquirable behaviour without deleting code or art; retirement itself remains the owner's decision.

## T1: Powered warmup, violet beam and sustained whole-map Burn on the Contagion; ordinary clear-sky condition on other surface maps; lapses after lost power.

Capability: repulsor. Fate: next_version. Switch/gate: cloudRepulsorEnabled.
Caller audit: CompCloudRepulsor.CompTick; RM_CloudRepulsor reward tags; RM_HelixCurators stock; ship hardpoint; warning work. Evidence: src/RimMandrake/Contagion/Source/CompCloudRepulsor.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero repulsor products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T2: Gravship hardpoint variant uses the same powered repulsor comp. Its deck placement was re-checked by BIOME_SHIP_CONTRIBUTIONS_1 (9fe1f933f0).

Capability: repulsor_ship. Fate: next_version. Switch/gate: cloudRepulsorEnabled.
Caller audit: RM_CloudRepulsorShip inherited comp; curator stock; gravship gift references. Evidence: src/RimMandrake/Contagion/Defs/ThingDefs/RM_CloudRepulsor.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero repulsor_ship products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T3: Unfinished death dissolves into slime and drops sterile mulch; no persistent ordinary corpse.

Capability: unfinished_mulch. Fate: next_version. Switch/gate: mulchDropsEnabled.
Caller audit: DeathActionWorker_RM_VanishToMulch.PawnDied -> RM_ContagionMulchUtility.Drop. Evidence: src/RimMandrake/Contagion/Source/RM_ContagionMulch.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Preserve staged Unfinished dissolution and readable non-resource residue; remove only fertilizer spawn.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero unfinished_mulch products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T4: One stationary organism may form after long Bloom outside home area; requires Burns enabled; placement clears plants and announces threat.

Capability: coalescence_formation. Fate: next_version. Switch/gate: coalescenceEnabled.
Caller audit: RM_MapComponent_ContagionSky.TryFormCoalescence; sky extension coalescenceDef. Evidence: src/RimMandrake/Contagion/Source/RM_MapComponent_ContagionSky.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Remove this feature from default touched contact and scanner target selection. Existing authored body/health state never silently vanishes when disabled.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero coalescence_formation products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T5: Saved mass, passive growth, staged graphics, explicit walk-to-ring absorption and on-arrival consumption; own emitted manhunters excluded; inspect and diagnostic counts.

Capability: coalescence_growth. Fate: next_version. Switch/gate: coalescenceEnabled.
Caller audit: Building_RM_Coalescence.Tick; RM_WalkIntoCoalescence job; scanner target. Evidence: src/RimMandrake/Contagion/Source/Building_RM_Coalescence.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Remove this feature from default touched contact and scanner target selection. Existing authored body/health state never silently vanishes when disabled.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero coalescence_growth products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T6: Stage-dependent manhunter emission with map-wide count cap.

Capability: coalescence_threat. Fate: next_version. Switch/gate: coalescenceEnabled.
Caller audit: Building_RM_Coalescence.TryEmit; emitted pawn provenance. Evidence: src/RimMandrake/Contagion/Source/Building_RM_Coalescence.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Remove this feature from default touched contact and scanner target selection. Existing authored body/health state never silently vanishes when disabled.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero coalescence_threat products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T7: Any active Burn collapses organism into Monstrous samples plus mulch; combat destruction gives less mulch and no samples.

Capability: coalescence_payoff. Fate: next_version. Switch/gate: coalescenceEnabled.
Caller audit: Building_RM_Coalescence.Collapse/Destroy; CompGenomeSample.monstrous; touched contactSources. Evidence: src/RimMandrake/Contagion/Source/Building_RM_Coalescence.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Remove this feature from default touched contact and scanner target selection. Existing authored body/health state never silently vanishes when disabled.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero coalescence_payoff products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T8: Pillar Arm: heavy melee/stun, reduced manipulation, slower movement and hunger/beauty costs; own directional body art

Capability: pillar_arm. Fate: next_version. Switch/gate: grownLimbsEnabled.
Caller audit: RM_InstallMonstrousLimbs recipes; AmoebaHostUtility limbPool; HediffComp_UnfinishedEmerge. Evidence: src/RimMandrake/Contagion/Defs/HediffDefs/RM_GrownLimbHediffs.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero pillar_arm products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T9: Lash: rapid stun melee with clumsy work, social-fight and beauty costs; twitching directional body art

Capability: lash. Fate: next_version. Switch/gate: grownLimbsEnabled.
Caller audit: RM_InstallMonstrousLimbs recipes; AmoebaHostUtility limbPool; HediffComp_UnfinishedEmerge. Evidence: src/RimMandrake/Contagion/Defs/HediffDefs/RM_GrownLimbHediffs.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero lash products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T10: Eyeburst: eye efficiency and aim with pain, rest, break-threshold and beauty costs; inherited bionic-eye art

Capability: eyeburst. Fate: next_version. Switch/gate: grownLimbsEnabled.
Caller audit: RM_InstallMonstrousLimbs recipes; AmoebaHostUtility limbPool; HediffComp_UnfinishedEmerge. Evidence: src/RimMandrake/Contagion/Defs/HediffDefs/RM_GrownLimbHediffs.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero eyeburst products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T11: Caudal Spring: spine replacement, jump ability and lasting mobility/pain/cold costs; placeholder tentacle art

Capability: caudal_spring. Fate: next_version. Switch/gate: grownLimbsEnabled.
Caller audit: RM_GrownLimbAbilities; RM_InstallMonstrousLimbs; AmoebaHostUtility limbPool. Evidence: src/RimMandrake/Contagion/Defs/HediffDefs/RM_GrownLimbHediffs.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero caudal_spring products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T12: Bellows: lung efficiency, toxin resistance and blind smoke ability with hunger/bleeding/beauty costs; no body render node

Capability: bellows. Fate: next_version. Switch/gate: grownLimbsEnabled.
Caller audit: RM_GrownLimbAbilities; RM_InstallMonstrousLimbs; AmoebaHostUtility limbPool. Evidence: src/RimMandrake/Contagion/Defs/HediffDefs/RM_GrownLimbHediffs.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero bellows products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T13: Surgical removal/replacement spawns stunned then manhunter Unfinished and a threat letter; ordinary missing-part consequences remain.

Capability: limb_removal. Fate: next_version. Switch/gate: grownLimbsEnabled.
Caller audit: RM_GrownLimbHediffs attaches HediffComp_UnfinishedEmerge; Notify_SurgicallyRemoved/Replaced. Evidence: src/RimMandrake/Contagion/Source/HediffComp_UnfinishedEmerge.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. All Grown Limbs, including natural arm/leg items and recipes, are deferred. Keep patched vanilla organ surgery and any independent kept mutation-removal semantics intact. Do not gate a shared organ helper solely because its filename says grown limb.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero limb_removal products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T14: Once-only scan of living Unfinished records rolled limbs, Monstrous status, extreme stat and failure; completed touch-range job may provoke; saved item label, inspect and market value.

Capability: draftprints. Fate: next_version. Switch/gate: draftprintsEnabled.
Caller audit: FloatMenuOptionProvider_SampleDraftprint; JobDriver_RM_SampleDraftprint; CompDraftprint transmit gizmo. Evidence: src/RimMandrake/Contagion/Source/CompDraftprint.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero draftprints products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T15: Quest asks for combinations; matching print is transmitted/consumed for silver and optional device via drop pod; only offered with a Contagion home.

Capability: helix_contracts. Fate: next_version. Switch/gate: draftprintsEnabled.
Caller audit: QuestScript RM_HelixDraftprintContract; QuestNode TestRunInt/RunInt; QuestPart transmit/drop rewards. Evidence: src/RimMandrake/Contagion/Source/QuestNode_RM_HelixDraftprintContract.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero helix_contracts products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T16: Curator caravan sells devices and buys appropriate goods; campaign patch owns actual Helix faction trader attachment. Since 2026-11-09 (9fe1f933f0) the curators stock the ship gift.

Capability: helix_trade. Fate: next_version. Switch/gate: nextVersionHelixTradeEnabled (new).
Caller audit: RM_Caravan_HelixCurators TraderKindDef stockGenerators; campaign faction attachment named in record.neighbours; standard Sunbeam stock must remain available. Evidence: src/RimMandrake/Contagion/Defs/TraderKindDefs/RM_HelixCurators.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Gate curator/faction attachment, not just draftprint quest TestRun. Preserve ordinary WeaponRanged/standard quest access to Sunbeam without restoring special Helix quests.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero helix_trade products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T17: Sterile mulch item builds fertile soil at three mulch per cell; no raw/sunned states or infection.

Capability: mulched_soil. Fate: next_version. Switch/gate: mulchDropsEnabled plus nextVersionFertilizerEnabled (new).
Caller audit: RM_ContagionMulch item; RM_MulchedSoil costList/designator; Unfinished death; deferred Coalescence drops. Evidence: src/RimMandrake/Contagion/Defs/ThingDefs/RM_ContagionMulch.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero mulched_soil products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T18: Biome scoring worker and rarity setting remain built in source; alternative-planet generation is outside project scope.

Capability: legacy_placement_worker. Fate: recommend_retire. Switch/gate: permanently inert scoring binding and no rarity UI; never a next-version worldgen switch.
Caller audit: RM_Contagion.workerClass -> RM_BiomeWorker_Contagion.GetScore -> biomeRarityFactor (forbidden worldgen). Evidence: src/RimMandrake/Contagion/Source/RM_ContagionBiome.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Offline production-worker/def inspection: no tile-scoring or rarity capability can activate, no worldgen UI remains, all old def names still resolve. No positive worldgen arm: prohibited in every version. No new world or live map generation is run by this ticket.

## T19: Turning other plants in zhool haze, including crop opt-in

Capability: zhool_conversion. Fate: next_version. Switch/gate: zhoolConversionEnabled=false and zhoolConvertsCrops=false; keep zhoolHazeEnabled=true.
Caller audit: CompTick -> Scan -> Convert; RM_ContagionBulloos attaches comp. Evidence: src/RimMandrake/Contagion/Source/CompZhoolHaze.cs.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero zhool_conversion products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T20: Red sap item harvest and promised repellent/sealant use

Capability: sap_harvest. Fate: next_version. Switch/gate: nextVersionSapHarvestEnabled=false (new); plant remains rostered.
Caller audit: RM_Sapblister.harvestedThingDef -> RM_RedSap; no usable repellent/sealant comp found. Evidence: src/RimMandrake/Contagion/Defs/PlantDefs/RM_ContagionFlora.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero sap_harvest products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T21: Seed-fist item harvest and promised fertilizer action

Capability: seed_fist_harvest. Fate: recommend_retire. Switch/gate: nextVersionSeedFistHarvestEnabled=false (new), pending retirement decision.
Caller audit: RM_BloodyFist.harvestedThingDef -> RM_SeedFistFertilizer; no usable fertilizer comp found. Evidence: src/RimMandrake/Contagion/Defs/ThingDefs/RM_SeedFistFertilizer.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Fresh disposable map, defaults and all retained systems running through the situation generator and season: state-read zero seed_fist_harvest products/jobs/letters/incidents or activation; log clean. Enable only its labelled next-version switch, supply its declared prerequisites, perform its real trigger and read the specific feature present. Turn off again: no new effects, existing objects readable and save resolves.

## T22: Unrostered donor-port plants including berries-yielding TentacularPlant

Capability: legacy_unrostered_plants. Fate: recommend_retire. Switch/gate: no acquisition/roster binding; compatibility defs inert, no new enable switch for forbidden forage.
Caller audit: Not in RM_Contagion.wildPlants; possible old-save def references, no current map caller found. Evidence: src/RimMandrake/Contagion/Defs/RM_Contagion_DonorPorts.xml.
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults.
Acceptance test: Post-patch acquisition graph and saved-map state show no legacy plant in wild selection, sowing, rewards or incidents; no food from those defs on a fresh Contagion map; log clean. No positive arm: retirement recommendation is not an authorized forage feature.

## T23: Monstrous-first sample choice, exotic gestation dispatch and limbs-off fallback

Capability: monstrous_injection_policy. Switch: grownLimbsEnabled plus next-version sample-selection gate, default off.
Caller audit: FindSampleToInject used by float menu and JobDriver_RM_InjectGenomeSample; CompleteGestation -> RM_DraftprintKernel.Plan.
Work: ordinary selection and batch path operate without exotic priority/fallback. Keep source data and code inert; no default Monstrous sample producer or selection. Keep natural arm/leg definitions inert behind grownLimbsEnabled (T25); the default ordinary pool is kidney/liver/lung/heart only. Keep shared RM_DraftprintKernel functions: their name does not make scans necessary.
Acceptance test: fresh default Contagion map and real ordinary extraction/injection/gestation show no Monstrous sample priority, dispatch, fallback output, exotic products/jobs/letters/incidents; log clean. Opt in to exotic system and supply samples by its declared producer, then state-read priority and exotic path present. Disable again: ordinary path still completes and existing exotic state resolves readably.

## T-place: Prove ordinary land/life and finish smaller Zhool'Iza definition

Implements/reads place. Build only after adoption/hold release. Existing source def roster, terrain and flora/fauna are present; no new cast rebuild. Specify the commissioned smaller Zhool'Iza from its actual commissioning/reference record before creating body/art: same admitted native UV class unless explicit commission says otherwise, smaller visible body, ordinary physiology/diet and no independent ability. Keep promised graphic alternatives as art checks, not passing quota. Do not invent IP or rename a commissioned creature to enforce a broad naming impression. Inspect food eligibility and actual spawn/ground/build affordances at play zoom; record any resolved multi-home row without eviction.
Acceptance test: On ordinary full maps across place.range, spawned native IDs and live motion are observed, pictured flora/fauna have distinct readable bodies and no missing textures, roofs can be built, no native forage or human food path exists. Smaller Zhool'Iza is distinct beside zhool and uses no new independent mechanic; def/asset checks resolve all commissioned alternatives without an acceptance count. Vanilla forest/rain comparison fails the identity pictures. Log clean.

## T-forecast: Instrument and complete natural warnings and covered lulls

Implements forecast and M1 calibration. Source has tells and clock, not recognition proof. Record natural clock, real drawn sink/shake/puffs/rustle and first weather/pressure events, actual near/distant paths and constant-weapon hit chance. Normal wet lulls must remain covered Bloom intervals in exposure classification without surprise clear Burns; preserve natural scheduler and rain locality, no new weather/heat type. Current production touch code only recognizes exact Bloom, so explicitly integrate lulls. No deadline jumps/frozen clear sky in positive proof.
Acceptance test: Natural elapsed-clock traces at forecast.range boundaries and interior cases show visible/audio cues preceding harm, ordered near workers sheltered, distant workers need improvisation, ordinary aim restored only by fog lifting. Mid-warning load preserves warning state; no passing arm disables retained mechanics. Identical-stage no-cue control is distinguishable; log clean.

## T-geometry: Consume shared refuge geometry and remove local sun fields

Implements refuge and integration R_shade. Source RM_ContagionSky.Exposed currently tests exact tree cell, and BiomeDef has heatKind/heatOffsetC. Replace local predicate with shared exposure/cover result for pressure, touch and Dive; integrate already ruled water via common service rather than a parallel local exception. No engine redesign: if provider lacks the contract, submit exact failing input/output to its owner. Retire local heat fields in later implementation, not on this pass. Build production-derived replay adapter for M3. Compare the predicate actually called by Pressure() and the sky-derived touched-dose code cell by cell to the shared grid; grid agreement alone is insufficient. Calibrate off-trunk shadow, trunk and open probes using actual Burn damage events and sky-derived touched dose, separately from contact.
Acceptance test: At refuge.range, compare each actual Burn Pressure() and sky-derived touched-dose exposure call to the shared grid cell by cell, not grid output alone; verify reachable-path results and correct geometry versions after tree/roof removal and load. Live equivalent-pawn probes in off-trunk shadow, on the trunk cell and in adjacent open ground confirm actual Burn damage and sky-derived touched dose follow cast shade; contact dose is separately recorded and drawn shadows agree with protection. Adjacent exposed pawn is actually harmed and shared heat is the same at the same solar geometry; no local heat-kind/offset survives. All retained effects on; log clean.

## T-crossing: Measure useful crossing under all retained harm

Implements crossing and M3 anchors. Existing dose counters are diagnostic, not proof of usable health. Read actual path, elapsed travel, pickup/rescue job, BurnDose/Heatstroke/touched, conscious arrival and work ability; propagate actor/door/terrain/canopy state. Do not implement a new dash ability or a fixed immunity timer.
Acceptance test: Across crossing.range normal cases, purposeful trip/rescue finishes alive and hurt, sheltered control stays protected from UV and long-stay control cannot continue ordinary work due to serious harm. Extreme heat controls are separately attributed. A zero-damage or all-immune mutant cannot pass; actual sun and touched pressure remain on, log clean.

## T-dive: Build the owed anticipatory native response

Implements native_response. closed CONTAGION_GPT_ENRICHMENT_1 Part 2 explicitly unstarted; current TryDive is post-damage. Reuse shared seek/path pieces, classify shy/leaker/armoured, start native response during tells, preserve motion and counter-movement. Add per-major-feature switch, default on, with current-life and disabled-job semantics. Shared sun-escape weather factor/arbitration correction belongs to its engine; expose inputs/expected outcome rather than invent another sun.
Acceptance test: Actual naturally warned job/position/capture traces in native_response.range show pre-injury movement, armoured counter-movement, leaker harm and no silent disappearance. Sealed nearby roofs do not permanently suppress reachable options. Downed/mental-state cases have readable cost. No teleports, no raw sun-dash under Bloom, no unattended flyer tests; all other kept mechanics on and log clean.

## T-deck: Build exposure/onset and applied-cost evidence harness

Implements body_change plus M1 production adapter. Add owed saved onset transition message before mutations, preserve finite cap/no-repeat and actual deck rules. Expose the pre-onset warned state to Sunbeam eligibility even if it uses a separate hediff; no first mutation is required for treatment. Verify cost/benefit effects separately from metadata. Expose body part and gene delta evidence, actual eligibility and notification reasons. Exact deck split/cap are checks; no new scalar pawn-value rule.
Acceptance test: Production-entry enumerator over body_change.range agrees with game health/notification anchors; real below-threshold state precedes mutation and already admits the held-beam treatment; a completed hold clears the warned progression before the first mutation and no first mutation follows without fresh exposure; an untreated sheltered control retains its warning state, while a separately naturally exposed control demonstrates onset/first change, per-progression onset only once across reload, actual cards have applied costs, no duplicate and exhaustion stable. Removing a cost or onset latch produces a witness. Real dose integration calibrated with retained sky/contact on, log clean.

## T-treatment: Finish visible Sunbeam intervention and ordinary access proof

Implements arrest. Existing RM_SunbeamArrest hold has facing/progress but no drawn treatment beam. Add minimal readable light from actual lens/patient during real hold; retain injury and safe interruptibility. Eligibility includes pre-onset warned patients with zero mutations as well as actively mutating patients; audit RM_SunbeamArrest.IsTouched against T-deck's actual warning state. Do not add free cure, crafting, Helix quest or Bloom exemption. Verify ordinary WeaponRanged/standard reward hooks resolve after deferred trader gates; if no real producer can supply it, that is a concrete access defect, not permission for a developer-spawn passing arm. Define armour-blocked completed treatment as no priced-success until real injury or readable refusal, no fabricated biome heat.
Acceptance test: Across arrest.range ordinary purchase/reward yields usable item with all Helix trade off. A naturally warned zero-mutation patient can receive a completed hold that clears the actual warned progression state before the first mutation, with no first mutation afterward absent fresh exposure. A sheltered untreated control retains the warning state; a separately naturally exposed control reaches onset/first change. Absence of mutations alone cannot prove success below threshold; refusal or ineffective warning-stage treatment fails. Completed actual hold draws beam, arrests progression only, retains mutations and injury; cancellation/move/death/lost weapon refuses without cure. Landed damaging projectile can arrest; miss/deflection cannot. Re-exposure starts again, no extra enabled and log clean.

## T-lifecycle: Bound ordinary budding and preserve malformed lives

Implements unfinished_life. Current CompSpawnerUnfinished ignores Bloom/Burn state. Gate natural budding to covered intervals, suspend during Burn without catch-up burst, save deadline and rolled state; keep shared Rupture births as independent dependency producers. Preserve actual malformation, lifespan and readable death signs while fertilizer drop and detailed Bodyprint phases are off. Add switch for major variation behaviour without rerolling live bodies on load/toggle.
Acceptance test: Production-derived M1/M4 replay matches real cohort anchors: covered ordinary births, none from local budding during active Burn, no overdue burst on resume, actual nonvital impairment and finite life, no reload reroll. Distinguish wild arrival/Rupture birth; malformed cohorts leave owned traces with default fertilizer absent, log clean.

## T-tissue: Close ordinary sample/host/batch transaction and odds gaps

Implements tissue. Source extraction/injection/gestation/natural matching is built; precommit odds, full ordinary-time journey and atomic placement are not proven. Define odds UI from actual pool/count distribution; keep independent draws and useful misses from kidney/liver/lung/heart only. T25 removes RM_GrownArm/RM_GrownLeg from the default pool and gates their recipes while patched vanilla organ matching stays on. Commit sample only after successful real injection, retain donor/once-only completion and healthy blocked-birth entitlement. Off-map placement waits for actual map/readable pending status; premature killed host can lose batch once visibly. No exotic policy, target steering or factory reuse.
Acceptance test: Across tissue.range full extraction/carry/inject/elapsed-gestation/pickup/install or sale journey works with precommit wanted-part odds agreeing with production law. Cancellation spends nothing; blocked healthy completion cannot consume host without entitlement, reload cannot duplicate, dead donor stamp remains usable. Birth suppresses acid, killed host retains acid; ordinary tissue works with all extra flags false, log clean.

## T-remains: Complete readable native death signs without phased Bodyprints

Implements remains and readable_remains. Inspect each native death/departure worker and reuse ordinary corpses where available; supply only a recognizable non-butcherable bodily remnant/trace for goo classes and a departure ridge husk where missing. A generic invisible deletion or unrecognizable filth counter is insufficient. Bodyprint skin/print phases, timed fade, bespoke eater travel/consumption and final sampling stay unbuilt/off under their next-version gates. Add the required major-feature switch for readable native remains, default on, while retaining the standing sign on any actual disappearance. Serialize existing butcher/Bones/fire/decay claims under their existing owners, no duplicate loot; disable/resume preserves readable saved state.
Acceptance test: Across remains.range, an actual native death/departure produces a visible identifiable corpse, bodily remnant or husk with all Bodyprint/Draftprint extras off. No default collapsed-skin/print phases, timed-print-fade jobs, custom eater jobs, final-sample items/jobs or trade machinery are present in state. Save/load and concurrent ordinary butcher/fire/decay/death callbacks cannot duplicate or silently lose the source; goo classes never become normal persistent butcher corpses. Any later disappearance has a readable ordinary cause, log clean.

## T-season: Build unrestricted whole-map season evidence and recovery

Implements season. Replace isolated retiled/clear-sky pads as passing evidence with disposable authored-world full map. Instrument natural producers, weather, jobs, health, grows/charges, remains, notices and identity; preserve all engine defaults. Maintain baseline recovery snapshot and explicit settings/map fingerprints, no destructive pad cleanup. M2 predicts regimes; real season establishes the bar. Respect owner hold and flyer attendance restrictions when executing later.
Acceptance test: Season.range: full naturally ticked season, mid-transition save/reload and reordered main actions, with all kept systems unlocked and extras off, plus day-hundred accumulation probe. Every required action really completes and renewed native cohorts persist; no flood/desert/stall/error storm. Comparator fork tests invariants rather than identical RNG; restored disposable baseline verifies all saved state.

## T-settings: Complete default/gating transition and floor coverage

Add absent default-on major-feature switches for pre-Burn Dive, readable native remains and presently ungated major variant/combat behaviours; future detailed Bodyprint phases/eater/timed fade use a separate labelled next-version switch, default off; reuse existing fields for genome/touched/arrest/budding/haze look. Floor settings includes search/reset, clear scope labels and defaults; no rarity UI, no new unsupported cross-biome setting. Preserve living/health/ordinary transaction history on disable. Ordinary dependents can continue resolving without invoking disabled extras. Update validation.py DEFAULTS and opts-in only for deferred diagnostic sections; they cannot run in whole positive arm.
Acceptance test: Clean-config load, missing saved field, current persisted opt-in, group reset, roundtrip and all-off transition cases all give documented settings, no new effect from disabled features and no silent pawn/history loss. Positive default whole run has every kept major feature on, all moved systems absent in state and clean log; no world-generation capability displayed or activated.

## T-flyers: Finish missing real-flight assets and safe evidence

Current roster wires real flight; inventory identifies Blisterfloat/Gorekite flip-books as incomplete. Inspect actual art/source/check data before calling any frame absent, preserve owner-kept art and naming. Required directional whole-body assets are content work for a later authorized builder, never this design pass. Do not invoke art generation or live flight here.
Acceptance test: Offline actual defs/asset references resolve whole-body directional flip-books and proper flight stats/flags; grounded floaters are unchanged in kind. Runtime Pawn_FlightTracker evidence only under standing attendance rule; visual flight only in owner-attended session. No frame/variant count becomes a bar; log clean.

## T-M1: Implement situation/transition generator

Implement M1 with production adapters, exported identities/defs and exact game calibration; enumerate retained states and settings/commit interleavings, record unobservable cases. These models are specified first, not claimed built. Trigger and budget shape are in models.md.
Acceptance test: situation/transition model meets every assumption/input/calibration/output requirement in its named models.md entry, reports model/game disagreement as untrusted and supplies shortest counterexamples to its bars. A deliberately broken producer/claim/geometry/transition creates a discriminating witness. No live result is claimed from model output.

## T-M2: Implement coupled season predictor

Implement M2 without world generation or engine redesign; include Rupture host/jelly births and all retained sinks/jobs, classify uncertainty and validate on naturally ticked saves. These models are specified first, not claimed built. Trigger and budget shape are in models.md.
Acceptance test: coupled model meets every assumption/input/calibration/output requirement in its named models.md entry, reports model/game disagreement as untrusted and supplies shortest counterexamples to its bars. A deliberately broken producer/claim/geometry/transition creates a discriminating witness. No live result is claimed from model output.

## T-M3: Implement refuge/crossing sweep

Implement M3 by calling shared production geometry and combined real health/path laws; exact category and threshold witnesses, calibration against live cells/routes/health. Export the predicates actually called by Burn Pressure() and sky-derived touched-dose code, and compare them cell by cell to the shared grid. Live calibration includes off-trunk shadow, trunk and adjacent-open pawns, actual damage events and separated sky/contact dose; a correct unused grid cannot pass. These models are specified first, not claimed built. Trigger and budget shape are in models.md.
Acceptance test: refuge/crossing model meets every assumption/input/calibration/output requirement in its named models.md entry, reports model/game disagreement as untrusted and supplies shortest counterexamples to its bars. A deliberately broken producer/claim/geometry/transition creates a discriminating witness. No live result is claimed from model output.

## T-M4: Implement biological ownership walk

Implement M4 production callback/claim adapters, physical-arrival input, current Bones/butcher/acid semantics and save-edge interleavings. These models are specified first, not claimed built. Trigger and budget shape are in models.md.
Acceptance test: biological model meets every assumption/input/calibration/output requirement in its named models.md entry, reports model/game disagreement as untrusted and supplies shortest counterexamples to its bars. A deliberately broken producer/claim/geometry/transition creates a discriminating witness. No live result is claimed from model output.

## T-spec-sparkleech_cycle: Specify or decline future Sparkleech electrical feeding, crop ruin and grub transformation

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: Browser and flying adult/grub bodies remain ordinary life; a bespoke energy/crop/life-cycle engine is unnecessary to the weather/body chain. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T-spec-sloshbelly_water: Specify or decline future Sloshbelly portable red-water harvest and fill states

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: Ordinary animal remains; a portable water purification economy is independent of the signature. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T-spec-doublemaw_infection: Specify or decline future Doublemaw custom infecting bite

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: Ordinary bite wounds already support infection in vanilla; a separate contamination vector would add another exposure system. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T-spec-meltgut_digestion: Specify or decline future Meltgut bespoke corrosive corpse-digestion stages

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: Vanilla scavenging and shared corpse handling supply its ordinary diet; custom digestive timing is another system. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T-spec-fleshsop_coordination: Specify or decline future Fleshsop coordinated shielding formation

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: Ordinary retaliation and pack combat retain the ruled weapon-system identity; bespoke formation AI is unnecessary. The word line is descriptive, not a geometric demand. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T-spec-red_water_processing: Specify or decline future Collected red water sunlight purification and downstream simulation

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: The fixed world already has authored clean downstream rivers; FlowWorks owns fluid taxonomy. No new purification economy is needed here. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T-spec-gestation_steering: Specify or decline future Using Draftprints to choose a gestation outcome

Deferred design only; no implementation in first version. Evidence/callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Designer call: Optional suggestion never commissioned; would turn the retained uncertain batch into a new targeted factory. Before opt-in work define user trigger, actual effect, costs, every state/transition, shared-engine owner boundary, settings and discriminating producer/absence tests. Re-check whether ordinary vanilla/shared behaviour already suffices. Do not revive an uncommissioned optional mechanism merely because this ticket exists.
Acceptance test: Future specification states the player experience and deletion argument, bounded state/transition table, dependencies and default-off acquisition/activation plan with an actual positive/negative instrument, or explicitly recommends retirement with reason. Default first-version map state has no proposed custom mechanism/jobs/letters/incidents and log clean. No future promise is counted as implemented.

## T24: Switch off independent Sunbeam native-damage bonus

Capability: sunbeam_native_bonus. Keep Sunbeam item, weak ordinary projectile, UV injury, landed damaging-hit arrest and hold-the-lens treatment active. Ship native factor neutral and a labelled next-version bonus switch off; no special Bloom accuracy exemption. Audit DamageWorker_RM_UV.Apply and settings/Scribe/reset/suite defaults. If retaining the tuning dial, the disabled bonus must override it to neutral rather than merely hide the control.
Acceptance test: fresh default map with every kept mechanic on, ordinary projectile and treatment still work, while state-read native damage has no extra multiplier, no special bonus things/jobs/letters/incidents, and log clean. Enable the labelled next-version combat bonus and state-read the multiplier applied to the same native hit; turn off and ordinary arrest path still works.

## T-spec-halfmade_front: Specify future Halfmade Tree territorial advance during Bloom and retreat during Burn

Deferred design only, no first-version build authorization. Designer call: Deleting this moving infection boundary leaves ordinary halfmade alien flora and the weather/body signature whole. Source and callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Define actual trigger, affected state, duration, interrupt/load/toggle edges, dependency owner and measurable cost before anyone enables the extra; compare vanilla/shared behaviour and recommend retirement if no distinct necessary experience remains.
Acceptance test: future specification gives the complete interaction/state model, exact producer and default-off gate, actual positive/negative instrument and dependency agreement, or an explicit retirement recommendation. First-version default state has none of this mechanic, its jobs/letters/incidents and a clean log. An inert item or atmospheric prose cannot count as implementation.

## T-spec-lashgrass_footsteps: Specify future Lashgrass actively flinches in a wave from footsteps

Deferred design only, no first-version build authorization. Designer call: Removing the footprint-response animation leaves ordinary filament ground cover; it is an independent motion interaction, not the Burn tell. Source and callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Define actual trigger, affected state, duration, interrupt/load/toggle edges, dependency owner and measurable cost before anyone enables the extra; compare vanilla/shared behaviour and recommend retirement if no distinct necessary experience remains.
Acceptance test: future specification gives the complete interaction/state model, exact producer and default-off gate, actual positive/negative instrument and dependency agreement, or an explicit retirement recommendation. First-version default state has none of this mechanic, its jobs/letters/incidents and a clean log. An inert item or atmospheric prose cannot count as implementation.

## T-spec-eyebark_tracking: Specify future Eyebark eyes actively track passing pawns

Deferred design only, no first-version build authorization. Designer call: Removing target-following eyes leaves the pictured eyed canopy and shade intact; ordinary tree appearance does not require a new tracking controller. Source and callers: Promise in cited design; source/defs search found no bespoke implementation; vanilla tools are not proof of this behaviour. Define actual trigger, affected state, duration, interrupt/load/toggle edges, dependency owner and measurable cost before anyone enables the extra; compare vanilla/shared behaviour and recommend retirement if no distinct necessary experience remains.
Acceptance test: future specification gives the complete interaction/state model, exact producer and default-off gate, actual positive/negative instrument and dependency agreement, or an explicit retirement recommendation. First-version default state has none of this mechanic, its jobs/letters/incidents and a clean log. An inert item or atmospheric prose cannot count as implementation.

## T-spec-sap_medicine: Specify future Red sap used as insect repellent or wound sealant

Deferred design only, no first-version build authorization. Designer call: pictured Sapblister and the sky/body/refuge cycle work without custom medicine; an item description is not a specified treatment. Source and callers: Plant harvest produces inert RM_RedSap; no usable repellent/sealant action or medicine comp found in Contagion source/defs. Define actual trigger, affected state, duration, interrupt/load/toggle edges, dependency owner and measurable cost before anyone enables the extra; compare vanilla/shared behaviour and recommend retirement if no distinct necessary experience remains.
Acceptance test: future specification gives the complete interaction/state model, exact producer and default-off gate, actual positive/negative instrument and dependency agreement, or an explicit retirement recommendation. First-version default state has none of this mechanic, its jobs/letters/incidents and a clean log. An inert item or atmospheric prose cannot count as implementation.

## T25: Switch off grown natural arms/legs and their install recipes

Capability: grown_natural_limbs. Switch: grownLimbsEnabled, labelled next version, default false. Caller audit: AmoebaHostUtility.CompleteGestation currently puts RM_GrownArm/RM_GrownLeg directly in the normal organPool; RM_GrownLimbs.xml defines them and RM_InstallGrownLimbs.xml routes their install recipes through Recipe_InstallGrownBodyPart. OrganInstallGenomeMatch.xml also uses that worker for retained vanilla organs, so gating the worker globally would break the kept path.
Work: Preserve built code/defs. Decouple the ordinary pool to kidney/liver/lung/heart when grownLimbsEnabled is off; gate both natural-limb install recipes and all item acquisition/producers, together with other Grown Limbs gates. Align initializers, Scribe missing-field fallbacks, clean-config reset and suite defaults. Keep CompGenomeMatched, patched vanilla organ recipes, Recipe_InstallGrownBodyPart and GenomeMatchBonusUtility available to the kept organ path. Existing saved limbs remain readable; no destructive cleanup.
Acceptance test: On a fresh map with defaults and every retained mechanic on, enumerate the actual resolved batch pool and ordinary trader/reward/recipe eligibility: no new RM_GrownArm/RM_GrownLeg item, install job/recipe, letter or incident is obtainable or active; pool is kidney/liver/lung/heart, log clean. Actual ordinary gestation/install still yields donor-labelled usable organs and successful matched vanilla organ surgery still grants feedback. With the labelled next-version switch enabled and its normal prerequisites, natural-limb production and installation are available again. Turn off: no new limb production/install, saved items readable and retained organ matching still works.

## T-spec-bodyprints: Specify or decline future phased Bodyprints and eater travel

Capability: bodyprints; absent/unbuilt. The 2026-10-16 this-sprint retention is not express 0.1.0 authority; d_dive_bodyprints_stay is a delegated version mapping. Defer collapsed-skin/print phases, ordinary-return-trip persistence, timed fade and bespoke Bloody Mess reach/consume under a labelled next-version switch, default off. No first-version implementation is commissioned. Keep the simple readable corpse/remnant/husk path independent under T-remains; final sampling stays separately deferred with Draftprints. Before future work, specify phase ownership, physical arrival, interruptions, save/toggle transitions, accumulation and the player experience that warrants the extra.
Acceptance test: The future spec either states that bounded state/claim model, dependency boundaries and default-off gate with positive/negative tests, or recommends retirement with reason. The default first-version map has no custom phase, print, timed-print-fade or eater jobs/items/letters/incidents, readable deaths still work and the log is clean. If implemented later, enabling the labelled next-version switch must produce the stated phases and actual arrival-before-consumption; disabling it must preserve saved history without new activation.

## T-water-cover: Request shared water-cell UV cover from CreatureBehaviors owner

Dependency owner: CreatureBehaviors. Need: “water cell counts as UV cover in ShadeAt/ExposureAt,” exposed consistently to Contagion UV protection and reachable-refuge selection. Measured gap: src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs ShadeAt/ExposureAt combine shade/light/gear/parasol/moving/glare layers without a terrain-water term; only src/RimMandrake/Contagion/Source/RM_ContagionSkyExtension.cs Exposed currently reads IsWater. record.d_burn_refuge_is_geometry incorrectly assumes that common grid term already exists.
Work: Route this contract request and its acceptance witness to the shared engine owner for implementation under that owner's process; Contagion does not redesign the engine or keep/add a local water predicate. The contract must make water UV cover available without adding drinking safety or a biome heat field and preserve ordinary ambient-heat behaviour. T-geometry consumes the delivered contract; the water part of refuge cannot pass until it exists.
Acceptance test: On the same real map/grid version with nonzero exposed Burn pressure, compare otherwise identical unroofed, unshaded traversable dry and water cells with no gear/parasol/moving caster. The shared ShadeAt/ExposureAt UV-cover contract must classify water protected and dry exposed; trace actual Burn pressure, sky-derived touched dose and route selection consuming that result, then observe water protection versus dry Burn harm and an actual reachable water refuge job. Change water to dry and back, rebuild, save/reload and require consistent classification. Today's ShadeAt lacks that water/dry distinction, so the witness fails before delivery. Existing roof/cast-shadow cases still agree and no local IsWater protection fallback, changed ambient-heat rule or dirty log can pass.
