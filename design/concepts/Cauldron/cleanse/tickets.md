# Cauldron proposal tickets

Design-only handoff; none executed here. Source reads establish presence, not current loaded proof. Each switch-off applies only to its named extra. Existing ledger items remain untouched. Before any implementation, the fresh reviewer and owner application step still apply.

## T1: Switch off placement_legacy

Capability: `placement_legacy`. Decision: Designer; recommend_retire.

Caller audit: RM_Cauldron.xml workerClass; RM_CauldronMod.cs biomeRarityFactor. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronBiome.cs.

Work: Make the alternative-world biome scorer nonplacing and remove the rarity/worldgen UI from supported use. Preserve source inert pending owner retirement; do not offer an enable switch or create any world. Local saved-map content is independent. Code and defs stay in the tree pending his decision. This prohibited capability has no next-version switch, opt-in mode or future enablement test.

Acceptance test: No alternative-world placement feature or rarity UI is available; read the inert worker with supplied fixture tile data and verify it cannot award placement. Load the intended fixed-world copy and verify ordinary local biome content still resolves. No world generation is run.

## T2: Switch off dew_beads

Capability: `dew_beads`. Decision: Designer; next_version.

Caller audit: RM_MapComponent_CauldronDewfall.MapComponentTick -> SpawnBeads. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronDewfallVisuals.cs.

Work: Set dewfallBeadsEnabled off in field defaults and Scribe fallback; gate bead spawning and expire only feature-owned saved beads normally. Leave the dewfall WeatherDef on. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Chemical-dew filth during dewfall outside the home area, bounded density and automatic expiry. no contact dose added by this visual. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T3: Switch off dew_saturation

Capability: `dew_saturation`. Decision: Designer; next_version.

Caller audit: RM_DewfallSaturation graphic/print hooks and weather flip remesh. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronDewfallVisuals.cs; src/RimMandrake/Cauldron/Textures/Things/Plant/RM_Dewfall/RM_CrystalFlower_dew.png.

Work: Set dewfallSaturationEnabled off; remesh once when disabling so saved accent graphics do not remain active. Preserve installed textures and the recorded dewfall no-green exception. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Installed dew variants for crystal flower, blood bouquet, red bugloss, keening cordax and giant toxic flower swap with weather and remesh through the saturation hook. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T4: Switch off shore_gardens

Capability: `shore_gardens`. Decision: Designer; next_version.

Caller audit: RM_MapComponent_CondensateGardens.MapGenerated and MapComponentTick -> TryColonize. Evidence: src/RimMandrake/Cauldron/Source/RM_CondensateGardens.cs.

Work: Set condensateGardensEnabled off for shore seeding and ticking. The kept vent MapGenerated path must call EnsureGenerated directly, with no need for gardens. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Roster-opted raven nettles colonise toxic-water shore cells at map creation and by slow sampling. existing zones/occupants respected. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T5: Switch off vent_gardens

Capability: `vent_gardens`. Decision: Designer; next_version.

Caller audit: RM_MapComponent_CondensateGardens.MapGenerated and MapComponentTick -> TryPlant; calls EnsureGenerated on kept vents. Evidence: src/RimMandrake/Cauldron/Source/RM_CondensateGardens.cs.

Work: Set ventGardensEnabled off, independently gate both map dressing and later spread; stop garden-triggered replacements. Keep vent temperament/output and ordinary wild flowers. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise State-keyed rings: crystal at stable vents, blood bouquet at leaks, giant toxic flower after blowout. mapgen replaces eligible wild non-trees, later fills empty space. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T6: Switch off kissaveth_gas

Capability: `kissaveth_gas`. Decision: Designer; next_version.

Caller audit: Vanilla damage -> CompGasOnDamage; PlantCollected -> RM_CompGasOnCut.PostDestroy. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronFloraExpansion.cs.

Work: Add an independent next-version gas setting: gate BOTH vanilla CompGasOnDamage and RM_CompGasOnCut.PostDestroy. Do not turn floraExpansionEnabled off or remove kissaveth from the roster. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Kissaveth releases toxic gas on external violence and plant cutting through damage and cut components. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T7: Switch off suush_burst

Capability: `suush_burst`. Decision: Designer; next_version.

Caller audit: Vanilla CompExplosive damage wick/death. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_CauldronFauna.xml.

Work: Gate its CompExplosive activation, death backstop and wick. Turning off cancels any feature wick without deleting the suush; ordinary death still leaves its normal remains. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Bullet/Bomb starts wick, death backstop and toxic gas blast. melee is not a wick trigger. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T8: Switch off water_poisoning

Capability: `water_poisoning`. Decision: Designer; next_version.

Caller audit: RM_CompVexxissBehaviour.CompTick -> PoisonWaterAround -> MaybeWarnPoisonedWater. Evidence: src/RimMandrake/Cauldron/Source/RM_CompVexxissBehaviour.cs.

Work: Set vexxissPoisonsWater and vexxissWaterLetter off; no new terrain swaps or warning letters. Existing toxic terrain keeps its actual chemistry; do not cleanse saved water. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Vexxiss converts clean named water terrains around its feet to toxic equivalents. per-animal warning letter/cooldown and independent toggles. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T9: Switch off fire_warden

Capability: `fire_warden`. Decision: Designer; next_version.

Caller audit: RM_CompVexxissBehaviour.CompTick -> TryWardFire -> vanilla BeatFire/AttackMelee. Evidence: src/RimMandrake/Cauldron/Source/RM_CompVexxissBehaviour.cs.

Work: Set vexxissFireWardenEnabled and vexxissAttacksIgniter off. Cancel only feature-issued BeatFire/retaliation jobs before a further action; preserve unrelated combat and original gas instigator metadata. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Awake able vexxiss takes BeatFire or attacks reachable recorded igniter, spares same faction. bounded attack job. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T10: Switch off vent_drinking

Capability: `vent_drinking`. Decision: Designer; next_version.

Caller audit: RM_CompVexxissBehaviour.CompTick -> TryDrinkVent; RM_JobDriver_VexxissDrinkVent -> vent.Inhale. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs; src/RimMandrake/Cauldron/Source/RM_CompVexxissBehaviour.cs.

Work: Set vexxissDrinksVentsEnabled off; cancel feature walk/drink jobs. Keep saved suppression/silencedUntil readable and allow ordinary recovery; fresh vents are not suppressed. No collector depends on a drink job. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Wild vexxiss seek drinkable vents and accumulate suppression until the vent falls silent. Disabling vent drinking aborts its walk and drink job. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T11: Switch off vexxiss_tracks

Capability: `vexxiss_tracks`. Decision: Designer; next_version.

Caller audit: RM_CompVexxissBehaviour.CompTick -> RM_VexxissPrints.TryStep; shared track grid draw/hover. Evidence: src/RimMandrake/Cauldron/Source/RM_VexxissPrints.cs.

Work: Set vexxissPrintsEnabled off; stop new feature prints and maker/expiry hover activity, preserving the shared grid for other creatures. Saved owned prints expire, never clear neighbours’ tracks. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Walking vexxiss write prints to the CreatureBehaviors track grid. Cauldron saves maker and expiry metadata for hover identification and timed removal. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T12: Switch off tap_prying

Capability: `tap_prying`. Decision: Designer; next_version.

Caller audit: RM_JobDriver_VexxissDrinkVent tick -> capping tap TakeDamage. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs.

Work: Set vexxissPriesTaps off. Gate damage in RM_JobDriver_VexxissDrinkVent separately; enabling this extra also requires the deferred drinking switch, documented in UI. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Wild drinking damages ordinary scaffold. lined tap is pry-proof. prying toggle leaves drinking. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T13: Switch off ruin_site

Capability: `ruin_site`. Decision: Designer; next_version.

Caller audit: RM_CauldronRuinScatter_Register.xml -> EH scatterer -> RM_CompCauldronRuinKit; Oomo patch shrineDefs. Evidence: src/RimMandrake/Cauldron/Source/RM_CauldronRuinKit.cs; src/RimMandrake/Cauldron/Defs/GenStepDefs/RM_CauldronRuinScatter.xml; src/RimMandrake/Cauldron/Patches/RM_CauldronRuinScatter_Register.xml.

Work: Set ruinKitEnabled off; suppress EH scatter registration/runtime dressing for this kit. Gate tank/pipe/slag/rig rewards and shrine slot spawning. Local vent generation remains independent. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Mapgen corroded filter rig with once-only dressed tanks/toxic water, broken pipes/slag, kept-clear study interaction ring. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T14: Switch off study_research

Capability: `study_research`. Decision: Designer; next_version.

Caller audit: RM_FilterWorksResearch.requiredAnalyzed -> RM_CorrodedFilterRig.CompAnalyzableUnlockResearch. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Buildings/RM_CauldronRuins.xml; src/RimMandrake/Cauldron/Defs/ResearchProjectDefs/RM_FilterWorksResearch.xml.

Work: Add separate next-version discovery toggle; remove requiredAnalyzed from the default ordinary research path and gate the rig study interaction. When enabled restore analysis requirement; existing completed research is never revoked. Do not require a shrine or ruin to test default industry. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Study corroded rig in place using vanilla analysis system, unlock Filter-Works research, then normal research prerequisite. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T15: Switch off vexxith_door

Capability: `vexxith_door`. Decision: Designer; next_version.

Caller audit: Vanilla architect and construction; RM_VexxithDoorGate startup. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Buildings/RM_VexxithDoor.xml.

Work: Set vexxithDoorEnabled off at startup; remove only bespoke door availability. Existing doors remain ordinary saved objects and material immunity follows its kept switch. Ordinary doors remain available. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Plate-only acid-proof door, startup architect-menu gate, already built doors preserved. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T16: Switch off lined_machines

Capability: `lined_machines`. Decision: Designer; next_version.

Caller audit: RM_VexxithGearGate; FlowWorks converter; RM_PryProofExtension in drink job. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Buildings/RM_FilterWorks.xml; src/RimMandrake/Cauldron/Defs/ThingDefs_Buildings/RM_VentGasTap.xml.

Work: Split vexxithGearEnabled so default suit/container recipes stay available while RM_VexxithFilterWorks and RM_VentGasTapLined build menus are next-version off. Keep marker types loadable, ordinary tap and Filter-Works working. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Vexxith filter vessel gives quarter cartridge use and acid immunity. lined vent tap acid/pry protection. existing rates/processes retained. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T17: Switch off acid_hull

Capability: `acid_hull`. Decision: Designer; next_version.

Caller audit: RM_MapComponent_AcidAir.MapComponentTick -> BurnHull; RM_HullLinerExtension; RM_VexxithGearGate. Evidence: src/RimMandrake/Cauldron/Source/RM_AcidAir.cs; src/RimMandrake/Cauldron/Defs/ThingDefs_Buildings/RM_HullLinerRig.xml.

Work: Add a Cauldron-scoped next-version hull opt-in, default off, independently of kept BurnPawns. Preserve the existing acidAirHullEnabled service and its existing Forge behaviour; do not change its shared default merely to gate Cauldron. Gate Cauldron hull warning/damage with the local opt-in and make the liner available through the future hull feature without hiding kept suits/containers. The existing Forge consumer retains access to its existing protection and behaviour. Retain all saved ship buildings. Add a Forge state-read regression comparison as well as the Cauldron absence/opt-in cases. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Exposed player buildings on ship substructure slowly burn toward a 30% floor. warning once. vexxith immunity or one hull liner rig stops sampled damage. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T18: Switch off rhossak_sprout

Capability: `rhossak_sprout`. Decision: Designer; next_version.

Caller audit: RM_CompRhossakGrove.Check -> Sprout. Evidence: src/RimMandrake/Cauldron/Source/RM_CompRhossakGrove.cs.

Work: Set rhossakSproutEnabled off; stop Sprout only. Bind and edible galls continue; retain seed-bearing data for the next version. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Sleeping seed-bearing rhossak seeds nearby eligible non-tree plants from current biome roster. galled excluded. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T19: Switch off rhossak_grove

Capability: `rhossak_grove`. Decision: Designer; next_version.

Caller audit: RM_CompRhossakGrove.Check -> Grove -> TryRoot -> BindTo. Evidence: src/RimMandrake/Cauldron/Source/RM_CompRhossakGrove.cs.

Work: Set rhossakGroveEnabled off; stop Grove/TryRoot progress and rooting notifications. Keep bound-tree references and rebinding independent of togetherTicks; never remove an animal or existing tree. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Three nearby seed-bearing kin accumulate awake time, hold progress asleep, reset when apart. root thornwood with cooldown, bind trio and message. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T20: Switch off oomo_shrine

Capability: `oomo_shrine`. Decision: Designer; next_version.

Caller audit: Cauldron_OomoShrine.xml adds shrineDefs to RM_CorrodedFilterRig; RM_CompCauldronRuinKit dresses slot. Evidence: src/RimUtinni/UtinniPatches/Patches/Cauldron_OomoShrine.xml; src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_OomoGrudgingShrine.xml.

Work: Add Utinni-owned next-version shrine switch to both ruin shrine slot and any independent availability; do not remove the entire Utinni cast patch. The first version has no rig or shrine dependency. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Utinni-only grudging shrine patched into ruin-kit slot. Natural meditation focus and biome-local lore. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T21: Switch off scanner_payload

Capability: `scanner_payload`. Decision: Designer; recommend_retire.

Caller audit: RM_AcousticPayload_Cauldron.xml guarded scanner payload consumer. Evidence: src/RimMandrake/Cauldron/Patches/RM_AcousticPayload_Cauldron.xml.

Work: Pending owner retirement decision, gate Cauldron acoustic payload registration off behind a next-version setting; do not disable the shared scanner. Kept vent inspection supplies all signature information. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Optional AcousticScanner readings for vents, listening fauna, resin and hidden cavities. existing scanner owns the mechanic. and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T22: Switch off fexxil_venom

Capability: `fexxil_venom`. Decision: Designer; next_version.

Caller audit: RM_CauldronFloraGate removes contact comp when fexxilVenomEnabled is off; EH contact tick. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFloraExpansion.xml.

Work: Set fexxilVenomEnabled off and strip/gate only the EH ContactVenom comp at the advertised restart boundary; retain pathCost, shard yield, art and roster. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Contact scratch poison from the retained physical fexxil thicket and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T23: Switch off zisska_firespit

Capability: `zisska_firespit`. Decision: Designer; next_version.

Caller audit: VEF CompProperties_InitialAbility -> RM_FireSpit AbilityDef/projectile. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_CauldronFauna.xml.

Work: Add a next-version switch that gates the VEF initial ability AND removes/disables previously granted feature abilities on saved zisska. Ordinary tools, meat, butcher steel and roster stay. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise VEF fire-spit ability on zisska and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T24: Switch off bedbug_paralysis

Capability: `bedbug_paralysis`. Decision: Designer; next_version.

Caller audit: RM_ParalysingBite tool -> maneuver -> DamageDef -> EH RM_Paralysis. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_BedBug.xml.

Work: Add a next-version switch that routes retained bite tools to ordinary Bite without adding RM_Paralysis; keep DamageDef/tool identity loadable and restore the paralysis route when opted in. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Paralysis added by bedbug bites and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T25: Switch off crystalmit_bricks

Capability: `crystalmit_bricks`. Decision: Designer; recommend_retire.

Caller audit: VEF AnimalProduct -> RM_RandomBricks/randomItems; independent of EatWeirdFood. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_CrystalMit.xml.

Work: Pending owner retirement decision, gate only periodic AnimalProduct random bricks off behind a next-version switch. Keep EatWeirdFood/think tree, mineral diet and normal corpse products; no shared VEF change. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Periodic random manufactured stone blocks from crystalmit and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T26: Switch off garsulix_death_blast

Capability: `garsulix_death_blast`. Decision: Designer; next_version.

Caller audit: race.deathAction -> DeathActionWorker_SmallExplosion. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_Garsulix.xml.

Work: Gate race.deathAction for this species behind its own next-version setting; preserve normal corpse/death effects and VEF fission, jelly and floating. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Small explosion on garsulix death and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T27: Switch off ossrith_refinery

Capability: `ossrith_refinery`. Decision: Designer; next_version.

Caller audit: RM_RefineOssrithCrystal recipeUsers BiofuelRefinery. Evidence: src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_Radyak.xml.

Work: Gate RM_RefineOssrithCrystal recipe availability and queued feature bills behind next-version setting; preserve shed crystals, ordinary milk and existing stock. Code, defs and installed assets stay in the tree. Label the switch ‘Next version’; default off in both field initializers and saved-setting fallbacks. Preserve old saved objects without allowing their feature actions; never use global all-off as the gate.

Acceptance test: With shipped defaults on a fresh disposable local Cauldron map, read loaded settings, active comps/abilities/recipes, feature-owned things, jobs, letters and incidents: this extra contributes none, while the retained species/land/signature callers still work and the log is clean. With only this labelled next-version setting enabled (and its documented provider/prerequisite switches), exercise Biofuel-refinery recipe for turning shed ossrith crystal into uranium and read attributable presence/activity. Disable during its active state, save/reload, and verify no new extra activity, no lost retained stock, no unintended pawn deletion and a clean log. Inert loaded defs are not active things; existing saved objects are preserved.

## T28: Define persistent metal and real purge

Existing item CAULDRON_METAL_PERSIST_MEDICAL_PURGE. Replace -0.08/day natural clearance. Designer default: a normal medical bill uses MedicineUltratech, consumes it only according to vanilla surgery accounting, and removes positive load on success, including hidden saved traces. Ordinary medicine/tending never removes it. Failure/interruption leaves load and readable vanilla operation consequences; no silent off-switch cure. Numeric cost, skill/work tuning are builder checks, not bars.

Acceptance test: Actual bloom causes load; shelter, ordinary care, travel and reload retain it; unavailable medicine blocks normally; completed advanced treatment consumes real medicine and clears it. Low positive trace remains selectable and failed/interrupted treatment never silently succeeds.

## T29: Define acid permanence and full seal

Existing items CAULDRON_ACID_ENDURING_PART_INJURIES and CAULDRON_FULL_SEAL_AMBIENT_PROTECTION. Acid must have a real injury path to disfiguring and sensory-organ lasting harm, not a label. Reuse vanilla permanent injury/part loss and capacity UI; no guaranteed organ destruction per dose. A functional full suit/helmet seal or roof blocks ambient acid and bloom. Direct liquid contact and toxic combustion smoke remain separate shared routes.

Acceptance test: Paired exposed/protected eligible bodies across factions have real exposure opportunities; only ambient exposed controls acquire new load/burns. Finite enumerated damage outcomes include causally traced lasting facial and sensory injuries; healed ordinary burn controls recover. Reload preserves scars/part loss and capacities; exceptional healing follows vanilla.

## T30: Define independent warning clock

Existing item CAULDRON_FALTER_MATCH_RULED_HOUR. Designer default: nominal 2500 ticks from readable falter start to full bloom; measure separately from 4000-tick weather interpolation and from first dose. Cue persists through a mid-falter save. Local source falls quiet; only awake idle wild eligible suush/zisska/eskith hush, never combat, sleep, downed or owned work. Warning text is retained as necessary readability.

Acceptance test: Tick-stamped cue and bloom times meet the declared approximate-hour check; exposed dose starts after onset, not during warning. A worker on the declared route can reach shelter; matched unprotected worker later takes dose. Mid-falter reload preserves remaining warning rather than restarting or skipping it.

## T31: Preserve gas topology and active combustion saves

Existing item CAULDRON_GAS_RELOAD_AND_SEALED_BOUNDARIES. Audit emission overflow, drift, fire-neighbour ignition and saved flame-front state together. Use passability plus both orthogonal side cells for diagonal movement/ignition; no through-wall 3x3 offer. Serialize pending burn cells and original instigators, or an equivalent causal continuation. Changes belong to Cauldron adapters; retain ExplosiveKnockback engine ownership.

Acceptance test: Single-spark water and bare-ground chains continue past the first clump; maintained empty corridor and straight/diagonal sealed compartments stop it. Mid-front reload matches uninterrupted reachability and instigator, with goods displacement attributable to shared bursts, not harness movement. Other gases remain independently unchanged except deliberately produced toxic smoke.

## T32: Bind intended pools and close fluid accounting

Existing item CAULDRON_SITE_POOL_IDENTITY_THROUGH_USE. Read the intended fixed-world local site, not tile counts. Resolve ToxicWater* versus RM_WaterPoisoned* to one actual FlowWorks liquid/fluid identity through contact, filling, pumping, tank, detox and output. Supply necessary authored local pools through existing content preparation, never a new world generator.

Acceptance test: A naturally delivered intended-site pool is found, labelled hazardous and retains its actual hazard in filled/pumped stock; matched fresh-water route stays fresh. Real conversion makes safe output only after power/cartridge/input work; full output, incompatible tank and interruption neither delete nor duplicate stock.

## T33: Separate kept availability and publish the settings contract

The old vexxithGearEnabled startup gate controls suit, containers, upgraded machines and hull liner together. Split gates and label application time. Ordinary research requires Electricity and bench completion with rig off. Keep floraExpansionEnabled on while independent fexxil/kissaveth effects are off. Direct Sun remains the shared geometric rule; no biome-specific exemption or hot vent.

Acceptance test: At defaults normal research, suit/helmet, containers, ordinary tap and Filter-Works are reachable with all extras absent. Live/restart/new-local-map boundaries match UI. All-off/re-enable and saved nondefault values preserve fluids, products, health and animal identity; feature-off prevents new effects without granting treatment or research.

## T34: Implement the situation generator and independent observer

Instrument gap: reuse site_spec.py, validation.py, northstar_site.py and Verse-free kernels without treating fake-game tests as runtime evidence. Implement the Situation generator model with manifest, generated cases, independent state readers and a durable disposable-save checkpoint before any staging. Missing read, missing DLC/provider, lost log or wrong candidate is UNMEASURED.

Acceptance test: Mutate a known read value, suppress a read, substitute a candidate hash and interrupt after staging: each is detected, never PASS. Recover the checkpoint and exact entry settings on normal and interrupted exits; compare actor/state manifests. Full shipped composition is used, sky unlocked, other kept systems on.

## T35: Implement gas geometry model and trace export

Instrument gap: Gas geometry and save walk in models.md; current fuzz covers isolated kernel rules and does not certify the adapter wall test or save of active fronts.

Acceptance test: Export actual passability, density, fronts, fire/instigator and displacement events from declared cases. Calibrate model against those traces, then enumerate topology/door/reload regimes with forbidden crossings reported by case and cell, including overflow corners.

## T36: Implement the whole-mod seasonal work instrument

Instrument gap: Coupled season and work model, retaining true event order and ecology, then a live whole-default run. Reuse healthy isolated chains only as calibration. No god mode, need removal, clear-sky lock or silent auto-refill.

Acceptance test: Full-map run lasts a RimWorld season with a real halfway save/reload and both action orders. Emit health, weather, gas/fire, food/water, jobs, stock and log traces, plus ordinary-zoom observations. Calibrated simulation names worst regimes; actual work makes usable output and prepared routine remains possible without refills or vanished wildlife.

## T37: Implement fluid ledger and medical state instruments

Instrument gap: Liquid ledger and interruption walk; Exposure and treatment state walk. Existing source assertions and generic health/centroid reads cannot settle transfer identity, inaccessible trace treatment or acid permanent-part causation.

Acceptance test: Use real action events and component reads to calibrate exact identity/conservation and health transition models. Reject copied expected constants, debug wounds/products and comparison arms with no dose/action. Trace hidden positive load and advanced treatment through reload and interrupted jobs.

## T38: Preserve native livelihood across the full roster

Spec gap: resolved roster food/water/locomotion truth. Never evict an animal. Cauldron-native creatures can drink their own environmental water under the standing 2026-11-01 ruling; raw native meat is toxic/prized where applicable. Maintain shared ownership and correct fictional flight, including floating predators and patch-added flyers. The free RM roster must live without the campaign patch; provider-complete optional/campaign runs extend it.

Acceptance test: Read resolved native food/water acceptance and flight tracker states through normal use across age/faction/life states. Mineral eaters actually feed, atmospheric feeders do not acquire a spurious food need, natives do not dehydrate beside their water, animals die with readable remains/signs. Toxic native-meat routes and safe tsevrix roast are demonstrated without debug food or health immunity. Unsupported shared-provider effects are not counted as a missing species.
