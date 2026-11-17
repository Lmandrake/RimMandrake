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
Work: Preserve defs and code. Gate activation, menus, recipes, rewards, incident selection and all reachable producers, not only the tick. Do not change shared helpers still called by kept code. Reset and absent-config deserialization agree with the new defaults. Only exotic limbs are deferred: ordinary arm/leg install and any independent kept mutation-removal semantics remain intact. Do not gate a helper solely because its filename says grown limb.
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
Work: ordinary selection and batch path operate without exotic priority/fallback. Keep source data and code inert; no default Monstrous sample producer or selection. Keep ordinary natural arm/leg definitions and shared RM_DraftprintKernel functions: their name does not make scans necessary.
Acceptance test: fresh default Contagion map and real ordinary extraction/injection/gestation show no Monstrous sample priority, dispatch, fallback output, exotic products/jobs/letters/incidents; log clean. Opt in to exotic system and supply samples by its declared producer, then state-read priority and exotic path present. Disable again: ordinary path still completes and existing exotic state resolves readably.

## T-place: Prove ordinary land/life and finish smaller Zhool'Iza definition

Implements/reads place. Build only after adoption/hold release. Existing source def roster, terrain and flora/fauna are present; no new cast rebuild. Specify the commissioned smaller Zhool'Iza from its actual commissioning/reference record before creating body/art: same admitted native UV class unless explicit commission says otherwise, smaller visible body, ordinary physiology/diet and no independent ability. Keep promised graphic alternatives as art checks, not passing quota. Do not invent IP or rename a commissioned creature to enforce a broad naming impression. Inspect food eligibility and actual spawn/ground/build affordances at play zoom; record any resolved multi-home row without eviction.
Acceptance test: On ordinary full maps across place.range, spawned native IDs and live motion are observed, pictured flora/fauna have distinct readable bodies and no missing textures, roofs can be built, no native forage or human food path exists. Smaller Zhool'Iza is distinct beside zhool and uses no new independent mechanic; def/asset checks resolve all commissioned alternatives without an acceptance count. Vanilla forest/rain comparison fails the identity pictures. Log clean.

## T-forecast: Instrument and complete natural warnings and covered lulls

Implements forecast and M1 calibration. Source has tells and clock, not recognition proof. Record natural clock, real drawn sink/shake/puffs/rustle and first weather/pressure events, actual near/distant paths and constant-weapon hit chance. Normal wet lulls must remain covered Bloom intervals in exposure classification without surprise clear Burns; preserve natural scheduler and rain locality, no new weather/heat type. Current production touch code only recognizes exact Bloom, so explicitly integrate lulls. No deadline jumps/frozen clear sky in positive proof.
Acceptance test: Natural elapsed-clock traces at forecast.range boundaries and interior cases show visible/audio cues preceding harm, ordered near workers sheltered, distant workers need improvisation, ordinary aim restored only by fog lifting. Mid-warning load preserves warning state; no passing arm disables retained mechanics. Identical-stage no-cue control is distinguishable; log clean.

## T-geometry: Consume shared refuge geometry and remove local sun fields

Implements refuge and integration R_shade. Source RM_ContagionSky.Exposed currently tests exact tree cell, and BiomeDef has heatKind/heatOffsetC. Replace local predicate with shared exposure/cover result for pressure, touch and Dive; integrate already ruled water via common service rather than a parallel local exception. No engine redesign: if provider lacks the contract, submit exact failing input/output to its owner. Retire local heat fields in later implementation, not on this pass. Build production-derived replay adapter for M3.
Acceptance test: Cell-by-cell production sweep calibrated to running shared grid at refuge.range yields identical protection and reachable-path results; tree removal/roof removal/load updates correct versions. Adjacent exposed pawn actually harmed and shared heat same at same solar geometry; no local heat-kind/offset survives. All retained effects on; log clean.

## T-crossing: Measure useful crossing under all retained harm

Implements crossing and M3 anchors. Existing dose counters are diagnostic, not proof of usable health. Read actual path, elapsed travel, pickup/rescue job, BurnDose/Heatstroke/touched, conscious arrival and work ability; propagate actor/door/terrain/canopy state. Do not implement a new dash ability or a fixed immunity timer.
Acceptance test: Across crossing.range normal cases, purposeful trip/rescue finishes alive and hurt, sheltered control stays protected from UV and long-stay control cannot continue ordinary work due to serious harm. Extreme heat controls are separately attributed. A zero-damage or all-immune mutant cannot pass; actual sun and touched pressure remain on, log clean.

## T-dive: Build the owed anticipatory native response

Implements native_response. closed CONTAGION_GPT_ENRICHMENT_1 Part 2 explicitly unstarted; current TryDive is post-damage. Reuse shared seek/path pieces, classify shy/leaker/armoured, start native response during tells, preserve motion and counter-movement. Add per-major-feature switch, default on, with current-life and disabled-job semantics. Shared sun-escape weather factor/arbitration correction belongs to its engine; expose inputs/expected outcome rather than invent another sun.
Acceptance test: Actual naturally warned job/position/capture traces in native_response.range show pre-injury movement, armoured counter-movement, leaker harm and no silent disappearance. Sealed nearby roofs do not permanently suppress reachable options. Downed/mental-state cases have readable cost. No teleports, no raw sun-dash under Bloom, no unattended flyer tests; all other kept mechanics on and log clean.

## T-deck: Build exposure/onset and applied-cost evidence harness

Implements body_change plus M1 production adapter. Add owed saved onset transition message before mutations, preserve finite cap/no-repeat and actual deck rules. Verify cost/benefit effects separately from metadata. Expose body part and gene delta evidence, actual eligibility and notification reasons. Exact deck split/cap are checks; no new scalar pawn-value rule.
Acceptance test: Production-entry enumerator over body_change.range agrees with game health/notification anchors; real below-threshold state precedes mutation, per-progression onset only once across reload, actual cards have applied costs, no duplicate and exhaustion stable. Removing a cost or onset latch produces a witness. Real dose integration calibrated with retained sky/contact on, log clean.

## T-treatment: Finish visible Sunbeam intervention and ordinary access proof

Implements arrest. Existing RM_SunbeamArrest hold has facing/progress but no drawn treatment beam. Add minimal readable light from actual lens/patient during real hold; retain injury and safe interruptibility. Do not add free cure, crafting, Helix quest or Bloom exemption. Verify ordinary WeaponRanged/standard reward hooks resolve after deferred trader gates; if no real producer can supply it, that is a concrete access defect, not permission for a developer-spawn passing arm. Define armour-blocked completed treatment as no priced-success until real injury or readable refusal, no fabricated biome heat.
Acceptance test: Across arrest.range ordinary purchase/reward yields usable item with all Helix trade off. Completed actual hold draws beam, arrests progression only, retains mutations and injury; cancellation/move/death/lost weapon refuses without cure. Landed damaging projectile can arrest; miss/deflection cannot. Re-exposure starts again, no extra enabled and log clean.

## T-lifecycle: Bound ordinary budding and preserve malformed lives

Implements unfinished_life. Current CompSpawnerUnfinished ignores Bloom/Burn state. Gate natural budding to covered intervals, suspend during Burn without catch-up burst, save deadline and rolled state; keep shared Rupture births as independent dependency producers. Preserve actual malformation, lifespan and readable staged death while fertilizer drop is off. Add switch for major variation behaviour without rerolling live bodies on load/toggle.
Acceptance test: Production-derived M1/M4 replay matches real cohort anchors: covered ordinary births, none from local budding during active Burn, no overdue burst on resume, actual nonvital impairment and finite life, no reload reroll. Distinguish wild arrival/Rupture birth; malformed cohorts leave owned traces with default fertilizer absent, log clean.

## T-tissue: Close ordinary sample/host/batch transaction and odds gaps

Implements tissue. Source extraction/injection/gestation/natural matching is built; precommit odds, full ordinary-time journey and atomic placement are not proven. Define odds UI from actual pool/count distribution; keep independent draws and useful misses, natural arms/legs. Commit sample only after successful real injection, retain donor/once-only completion and healthy blocked-birth entitlement. Off-map placement waits for actual map/readable pending status; premature killed host can lose batch once visibly. No exotic policy, target steering or factory reuse.
Acceptance test: Across tissue.range full extraction/carry/inject/elapsed-gestation/pickup/install or sale journey works with precommit wanted-part odds agreeing with production law. Cancellation spends nothing; blocked healthy completion cannot consume host without entitlement, reload cannot duplicate, dead donor stamp remains usable. Birth suppresses acid, killed host retains acid; ordinary tissue works with all extra flags false, log clean.

## T-remains: Build phased Bodyprints without deferred trade dependency

Implements remains. Enrichment Part 3 is explicitly unstarted; vanilla vanish/slime is not proof. Define native death class adapters, carcass/nonbutcherable goo remnant -> collapsed skin -> anatomical print, actual Bloody Mess reach/consume, ridge husk and final inspectable anatomical sample record/job. No contract/transmit/payment metadata or new currency. Add default-on per-major-feature toggle and phase/return-time tuning. Serialize existing butcher/Bones/fire claims; use existing engine semantics, no duplicated loot. Make disables/resume readable, never delete live pawns/old remains silently.
Acceptance test: Across remains.range visibly follow each phase at normal speed, actual eater arrival precedes consume, unreachable print survives ordinary return opportunity and final sample job works with draftprints/curators/contracts off. Save during each claim and concurrent butcher/fire/sample/eat cannot duplicate or silently lose source; goo classes never become normal persistent butcher corpses, log clean.

## T-season: Build unrestricted whole-map season evidence and recovery

Implements season. Replace isolated retiled/clear-sky pads as passing evidence with disposable authored-world full map. Instrument natural producers, weather, jobs, health, grows/charges, remains, notices and identity; preserve all engine defaults. Maintain baseline recovery snapshot and explicit settings/map fingerprints, no destructive pad cleanup. M2 predicts regimes; real season establishes the bar. Respect owner hold and flyer attendance restrictions when executing later.
Acceptance test: Season.range: full naturally ticked season, mid-transition save/reload and reordered main actions, with all kept systems unlocked and extras off, plus day-hundred accumulation probe. Every required action really completes and renewed native cohorts persist; no flood/desert/stall/error storm. Comparator fork tests invariants rather than identical RNG; restored disposable baseline verifies all saved state.

## T-settings: Complete default/gating transition and floor coverage

Add absent default-on major-feature switches for pre-Burn Dive, Bodyprints/final sampling and presently ungated major variant/combat behaviours; reuse existing fields for genome/touched/arrest/budding/haze look. Floor settings includes search/reset, clear scope labels and defaults; no rarity UI, no new unsupported cross-biome setting. Preserve living/health/ordinary transaction history on disable. Ordinary dependents can continue resolving without invoking disabled extras. Update validation.py DEFAULTS and opts-in only for deferred diagnostic sections; they cannot run in whole positive arm.
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

Implement M3 by calling shared production geometry and combined real health/path laws; exact category and threshold witnesses, calibration against live cells/routes/health. These models are specified first, not claimed built. Trigger and budget shape are in models.md.
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
