# Implementation and instrument tickets

Proposal only; nothing filed or executed here. Keep source/defs/art/aliases. Default means this proposed version after application, not today's initializers. Each built-extra test requires state absence by default, state presence when enabled and a clean log. Shared neighbours remain active.

## T1: False-bank disguise/contact ambush — switch off

Scope/decoupling: Gate lying down, invisibility, CheckContact/strike and special reveal pause/letter including helper routes. Off reveals existing disguised vurraks readably; ordinary visible wildlife/predation remains. Enabled future behavior retains its ruled weight/contact/first-reveal rules.

Source/callers searched: src/RimMandrake/Greentide/Source/RM_CompBankAmbusher.cs; src/RimMandrake/Greentide/Source/Kernel/RM_VurrakKernel.cs; src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Vurrak.xml; RM_Vurrak.xml -> RM_CompBankAmbusher.CompTick/CheckContact; RM_VurrakKernel; validation.py direct proof helpers.

Reason: Designer decision (delegated): A second specialized bank ambush beside the kept aquatic hunter; visible vurraks remain in the cast.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T2: Zrrik vampiric stab — switch off

Scope/decoupling: Gate only damage-worker attacker healing, not ordinary dealt damage, saved bodies or leather. Off ordinary stab, on dealt-damage-gated healing. Do not remove any unseen neighbour placement.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Zrrik.xml; src/RimMandrake/Greentide/Source/RM_DamageWorker_Bloodlust.cs; src/RimMandrake/Greentide/Source/Kernel/RM_RulesKernel.cs; RM_Zrrik.xml -> RM_DamageWorker_Bloodlust; RM_RulesKernel; no inline RM_Greentide wildlife row.

Reason: Designer decision (delegated): A combat healing specialization with no role in holding a wet-jungle home; no roster row is removed.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T3: Giant-ant faction raids — switch off

Scope/decoupling: Gate every ant raid strategy/combat-group selection and producer through existing faction/kind applier, including derived-def restore. Preserve migrated RM identity, saved faction/pawns, typed aliases and protected art. Never reinstate the retired standalone package.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_GreentideAnts.xml; src/RimMandrake/Greentide/Defs/FactionDefs/RM_GreentideAnt_Faction.xml; src/RimMandrake/Greentide/Source/RM_GreentideAntRaidApplier.cs; RM_GreentideAnt_Faction.xml combat groups -> RM_GreentideAntRaidApplier; RM_GreentideMod settings; aliases.

Reason: Designer decision (delegated): An independent raid generator. Migration into the free tier remains intact.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T4: Ant carapace construction — switch off

Scope/decoupling: Gate fresh carapace-wall/material offers while preserving saved walls/leather and aliases. T3 supplies fresh enabled raid rewards. External armor/yield consumers are unavailable here: T41 must inventory them before reference changes.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_GreentideAnts.xml; RM_GreentideAnts.xml race leatherDef and wall stuff; historical external armor/yield patch consumers unavailable here.

Reason: Designer decision (delegated): An additional raid-fed construction economy; wood already supplies ordinary building material.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T5: Stench grenade — switch off

Scope/decoupling: Gate recipe/trade/loot, thrown projectile, RotStink/reaction suppression AND item damage-triggered explosion. Do not disable ordinary phorrik harvest or depend on the grenade to use retained resin. Existing weapons remain readable; no activation by damage while off.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs/RM_StenchGrenade_Items.xml; src/RimMandrake/Greentide/Defs/DamageDefs/RM_StenchGrenade_Combat.xml; src/RimMandrake/Greentide/Source/RM_Proj_GrenadeStenchSmoke.cs; src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml; RM_Phorrik harvest -> stench item/recipe -> RM_Proj_GrenadeStenchSmoke; item damage-triggered explosion is another route.

Reason: Designer decision (delegated): A portable combat tool. Retreat, prepared routes and blower aversion already answer the kept wildlife.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T6: Steam-devil vortices — switch off

Scope/decoupling: Gate BOTH shared RM_IncidentWorker_SteamDevil and RM_MapComponent_RoilVortexSpawner for Greentide, plus local incident offers. Keep terminal-owned defs/shared vortex and other-biome uses; never globally flip a shared kit default to implement this local cut.

Source/callers searched: src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_RoilVortexSpawner.cs; src/RimMandrake/EnvironmentalHazards/Source/RM_WanderingVortex.cs; src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_SteamDevil.cs; EnvironmentalHazards RM_IncidentWorker_SteamDevil AND RM_MapComponent_RoilVortexSpawner; shared RM_WanderingVortex; terminal content lookup.

Reason: Designer decision (delegated): An independent damaging weather incident; standing steam and Breaklight work without vortices.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T7: Mineable living Greatbole shelter — switch off

Scope/decoupling: Add Greentide-local next-version master gating living-bole extension/placement and local registry activation. Existing saved cores/heartwood stay readable/inert, never disappear. Keep root routes through existing fallback anchors and ordinary RM_Greatbole tree. Group T8–T14/T26 under the package master; shared neighbour living boles stay available.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs_Buildings/RM_Greatbole_Landmark.xml; src/RimMandrake/EnvironmentalHazards/Source/RM_CompLivingBoleMarker.cs; src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_LivingRegrowth.cs; src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_LivingBoles.cs; RM_Greentide_Biome.xml living-bole extension -> RM_GenStep_LivingBoles -> marker/regrowth; causeways read BoleCenters but have fallback anchors.

Reason: Designer decision (delegated): A second settlement system: mineable living rooms, crush, regrowth and sealing. Fellable Greatbole plants remain.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T8: Greatbole extraction ladder — switch off

Scope/decoupling: Gate core polling, Shaking/healing/catastrophe, fruit/grub/trunk/husk production, camera effects, letters and campaign goodwill behind T7 plus this setting. Core registration alone cannot enable it. Preserve future ruled threshold/radius/permanence/full-healing behavior; old-timer/no-latch and direct-yield stack truncation remain future repair risks, not current accepted behavior.

Source/callers searched: src/RimMandrake/Greentide/Source/RM_CompGreatboleHarvestLadder.cs; src/RimMandrake/Greentide/Source/Kernel/RM_LadderKernel.cs; src/RimMandrake/Greentide/Defs/ThingDefs_Buildings/RM_Greatbole_Landmark.xml; RM_GreatboleCore comp -> ladder -> regrowth API, fruit/grub/trunk/husk defs and optional faction binding.

Reason: Designer decision (delegated): A separate extraction, escalation and catastrophe economy attached to the deferred landmark.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T9: Greatbole Fruitfall — switch off

Scope/decoupling: Gate CanFireNow AND execution, not merely incident weighting. Enabled uses an actually registered enabled bole; default cannot generate fruit/grubs/letters. Ordinary tree felling never stands in for Fruitfall.

Source/callers searched: src/RimMandrake/Greentide/Source/RM_IncidentWorker_GreatboleFruitfall.cs; src/RimMandrake/Greentide/Defs/IncidentDefs/RM_Greentide_Spine_Incidents.xml; RM_Greentide_Spine_Incidents.xml -> incident worker -> living registry + fruit/grubs + letter.

Reason: Designer decision (delegated): A special harvest incident feeding the deferred landmark economy.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T10: Greatbole fruit processing — switch off

Scope/decoupling: Gate new butcher recipe, trade/loot producers and product offers. Keep saved fruit/products resolving. T8/T9 cannot indirectly bypass this gate. T11/T13 require this future economy; ordinary forage/catches/resin remain independent.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs/RM_GreatboleHarvest_Items.xml; src/RimMandrake/Greentide/Defs/RecipeDefs/RM_GreatboleHarvest_Recipes.xml; Fruitfall/ladder -> RM_GreatboleFruit -> RM_ButcherGreatboleFruit -> steak/RoyalRind/seed.

Reason: Designer decision (delegated): A butcher-and-material progression fed by deferred harvests.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T11: Royal Rind equipment — switch off

Scope/decoupling: Gate new coat/material offers and future custom hazard hooks while preserving saved apparel/material. Retained heat protection uses ordinary vanilla insulation, not this exceptional coat. Preserve future cross-biome/space constraints without adding current validation scope.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs/RM_GreatboleHarvest_Items.xml; design/RimMandrake/exposure_gear_matrix_spec.md; RM_GreatboleHarvest_Items.xml coat/material recipes consume Royal Rind; ordinary heat depends on vanilla insulation, not this item.

Reason: Designer decision (delegated): Cross-biome expedition equipment tied to deferred fruit; vanilla insulation remains available.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T12: Fruit-guarding grubs — switch off

Scope/decoupling: Gate new grub drops, breeding, fruit defence and famine manhunter through local future package. Saved grubs remain visible and safe from silent removal. Preserve shared behavior services for other species; no ordinary wild-grub roster row is evicted. On includes feeding/breeding AND food-loss aggression.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_GreatboleGrub.xml; src/RimMandrake/CreatureBehaviors/Source/RM_CompVerminBreeder.cs; Fruitfall/ladder -> RM_GreatboleGrub.xml -> shared eat/defend/breeder/famine behavior; no ordinary biome spawn row.

Reason: Designer decision (delegated): A breeding/fruit-defence system downstream of deferred harvests; event-only grubs are not a wildlife eviction.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T13: Plantable Greatbole seeds — switch off

Scope/decoupling: Default seed planting off, label next-start; gate CompPlantable patch and sown-tree water/fast-growth behavior. Keep seed defs/save aliases and ordinary wild plants independent. Enabled seeds still require adjacent water; no playable conversion into a mineable landmark.

Source/callers searched: src/RimMandrake/Greentide/Patches/RM_Greatbole_Crossovers.xml; src/RimMandrake/Greentide/Source/RM_Plant_Greatbole.cs; Butcher recipe -> seed -> RM_Greatbole_Crossovers.xml patch -> RM_Plant_Greatbole; wild plant remains independent.

Reason: Designer decision (delegated): A special propagation loop fed by deferred fruit. Wild fellable trees remain.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T14: Arboreal servants — switch off

Scope/decoupling: Retain already-off default and label next version. Gate startup TreeConnection/ritual-host substitutions and existing-core activation. Off must leave ordinary Gauranlen hosts/vanilla dryads unchanged; no Anima focus piggyback.

Source/callers searched: src/RimMandrake/Greentide/Patches/RM_Greatbole_Crossovers.xml; src/RimMandrake/Greentide/Source/RM_GreatboleServants.cs; src/RimMandrake/Greentide/Source/RM_PatchOperationGreentideSettingGate.cs; RM_Greatbole_Crossovers.xml -> setting gate -> RM_GreatboleServants; vanilla ritual host replacement.

Reason: Designer decision (delegated): An optional Ideology production crossover, not ordinary jungle life or growth defence.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T15: Acoustic Scanner payload — switch off

Scope/decoupling: Add local default-off guard alongside FindMod. Disable only Greentide payload registration/text; preserve Scanner and other biomes. Gall/ordinary tree references cannot keep landmark payload active. Enabled restores resolved future payloads.

Source/callers searched: src/RimMandrake/Greentide/Patches/RM_AcousticPayload_Greentide.xml; RM_AcousticPayload_Greentide.xml FindMod guard -> AcousticScanner pulse; reads bole/trunk/gall defs.

Reason: Designer decision (delegated): Optional tool payload; direct signs suffice for kept hazards.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T16: Unsupported cross-biome mud — switch off

Scope/decoupling: Keep existing unsupported crossBiomeEnabled=false, labels and controls; no new cross-biome switch. Verify old-map/new-component FinalizeInit and saved applied flag: off never repaints. On exercises existing explicitly unsupported local conversion, never planet generation or a new support promise.

Source/callers searched: src/RimMandrake/Greentide/Source/RM_MapComponent_CrossBiomeChurnmud.cs; src/RimMandrake/Greentide/Languages/English/Keyed/RM_Greentide_CrossBiome.xml; RM_MapComponent_CrossBiomeChurnmud.FinalizeInit -> AppliesToBiome; later terrain-driven mire/swallow; existing saved applied flag.

Reason: Designer decision (delegated): Existing unsupported expansion outside our validated biome; stays off and labelled.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T17: Extra plant interactions — future specification

Future contract prerequisite: Gorbeleth toxin attack: specify target/LOS/reach, telegraph, poison/retreat, cooldown, save/off and shared reuse. Ordinary toxin harvest remains. The other promised plant mechanics are separate tickets T42–T45.

Evidence: src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory active_plant_hazards; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T18: Mining-driven Greatbole song — future specification

Future contract prerequisite: Preserve greatbole_harvest_spec.md song beats: baseline bass, hollowing pitch, threshold dissonance, harmony after healing, unpleasant beat before breaking, plus sound-off warning. Specify scalar shared soundscape driver and actual listening calibration; no Thalquith count substitution.

Evidence: infrastructure/state/items/GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1.md; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory greatbole_song; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T19: Greatbole thermal sanctuary — future specification

Future contract prerequisite: Define future chamber temperature pull against ordinary room/air heat, enclosure, hollowing, core loss, reload/off and a state trace. Never create private Direct Sun.

Evidence: design/Jawa/worldbuilding/biomes/greatbole_atmosphere_crossovers_design_2026-10-02.md; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory greatbole_thermal; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T20: Greatbole pilgrim visits — future specification

Future contract prerequisite: Preserve prior pilgrim visit/advance-warning/open-wound/Shaking/relation constraints. Specify faction eligibility, timing, no-visitor cases, recovery, save/off; no event in the first version.

Evidence: infrastructure/state/items/GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1.md; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory greatbole_pilgrims; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T21: Anima crossover — future specification

Future contract prerequisite: Specify intentional default-off Greatbole focus/host/state independently from servants, preserving prior crossover constraints. Random anima trees remain forbidden.

Evidence: infrastructure/state/items/GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1.md; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory greatbole_anima; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T22: Seeding grenade and toxin weapons — future specification

Future contract prerequisite: Separately specify future seeding and toxin payload routes, targets, area, warning, persistence, native eligibility and settings before building; do not automatically promote them after stench proof or redesign the shared growth engine.

Evidence: infrastructure/state/items/closed/GREENTIDE_GRENADE_WEAPONS_1.md; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory seeding_toxin_weapons; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T23: Ceded Room rite — future specification

Future contract prerequisite: Keep the already-ruled rite deferral. Reconcile obsolete open item against later ruling; future spec names participants, site, interrupted ceremony, effect, save/off. No ritual jobs/letters/incident now.

Evidence: OWNER:1792755160877450458; design/RimMandrake/designer_codex_2026-11-09/Greentide/record.json inventory ceded_room; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T24: Illisk non-blast resistance — switch off

Scope/decoupling: Default shoalHideEnabled off; label next version. Off existing illisks get no special scaling; on non-blast scaling and configured blast passthrough resume. Keep ordinary shoal spawns/group/water role.

Source/callers searched: src/RimMandrake/Greentide/Source/RM_CompShoalHide.cs; RM_Illisk.xml -> PostPreApplyDamage.

Reason: Designer decision (delegated): Ordinary shoal movement and food role survive deleting damage scaling.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T25: Provoked thurrock wall attack — switch off

Scope/decoupling: Default thurrockProvokedWallDamage off; label next version. Update/read derived Hediff stages through RM_ThurrockAuraApplier. Off retains tree feeding/felling including during provocation but no special wall aura. On restores aura damage while sparing natural rock. Distinguish ordinary direct melee from this aura.

Source/callers searched: src/RimMandrake/Greentide/Source/RM_ThurrockAuraApplier.cs; RM_Thurrock.xml and its aura -> shared PeriodicAreaAttack; settings applier.

Reason: Designer decision (delegated): Tree feeding/felling remains whole without a separate wall-breaking attack.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T26: Living-bole toxin floor — switch off

Scope/decoupling: Separate ordinary sealed churnmud from living-bole toxin floor. Gate Greentide future offers/use under T7; retain shared terrain/refs for Fever Wood and other users named in source, aliases and saved floors. Never globally invalidate a neighbour.

Source/callers searched: src/RimMandrake/Greentide/Defs/TerrainDefs/RM_Greentide_SpineTerrains.xml; LivingRegrowth sealantTerrain; Fever Wood consumer noted in source comments.

Reason: Designer decision (delegated): The ordinary sealed-churnmud floor remains; living-bole anti-regrowth floor is unnecessary without that landmark. Preserve neighbour consumers.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T27: Unused sugar-famewort port — switch off

Scope/decoupling: Recommend retiring unused sugar-famewort only. Keep def/reference resolution pending owner action and do not add fresh Greentide roster/loot offers. T41 inspects post-patch callers; no deletion/eviction by this proposal.

Source/callers searched: src/RimMandrake/Greentide/Defs/RM_Greentide_DonorPorts.xml; No RM_Greentide wildPlants entry; definition stored only.

Reason: Designer decision (delegated): Unused donor filler duplicates ordinary sap/food roles; recommend retiring local unused content, not evicting roster life.

Acceptance test: With default settings on a fresh local Greentide map, state-read absence of this extra's activations and extra-owned generated things, jobs, letters, incidents and exclusive offers; log clean through its producer windows and save/reload. Defs/aliases, ordinary species and neighbour consumers still resolve. With its labelled next-version setting on (and explicitly named package prerequisites on), exercise the real producer and state-read its outcome/effect present; log clean. Include the alternate entry points and off-after-existing-state cases named above; checkbox readback alone fails. Reload baseline and restore prior settings/derived defs.

## T28: Moving causeways — future specification

Future contract prerequisite: Specify future local moving-road mutation, occupied/built cells, warnings, absence/reload, path preservation and off. Static lanes remain now; no planet edit or silent home destruction.

Evidence: design/Jawa/worldbuilding/biomes/kits/greentide_kit_spec.md M9 explicit deferral; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T29: River-course salinity simulation — future specification

Future contract prerequisite: Specify future salinity using fixed authored course data, fresh/brine/end states, terrain/catch/fertility, static-versus-dynamic scope, riverless graves, reload/off. No alternate world or basin connections.

Evidence: design/Jawa/worldbuilding/biomes/the_greentide.md Owed; no local salinity runtime found; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T30: Campaign settlement/dungeon templates — future specification

Future contract prerequisite: Specify campaign domes/enclaves at correct tier with windowless native architecture, blower approaches, water band, resources and safe local placement. No planet generation. Living-bole dungeons have T47.

Evidence: design/Jawa/worldbuilding/biomes/the_greentide.md sections 8/Owed; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T31: Canopy/underground travel — future specification

Future contract prerequisite: Specify ookala overhead travel support/start/landing/river-fall/carry/death/save/off; keep ordinary pawn now and correct overclaiming descriptions. Gristle is T46.

Evidence: src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_CanopySwinger.xml; src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Gristle.xml; no implementation/activation claimed.

Acceptance test: none, deferred absent mechanic has no current implementation to activate. Before its later build, review the explicit state/trigger/output/cost/warning/range/save/off contract against cited rulings, then build offline and actual-game tests with it. Default first-version producers remain absent.

## T32: Default ownership and graceful deactivation

Scope: Implement definition.md settings matrix under actual owners: local future-package gates without changing neighbour defaults, clear Now/new-map/next-start labels, saved aliases and safe existing-state cleanup.

Acceptance test: A fingerprinted effective-gates manifest maps all census capabilities to actual owners; fresh default map and mid-cycle reload have no deferred activations. All-off stops new harm, releases Mired/hidden animals readably, stops old-mark protection, permits old-cache digging and never deletes objects/pawns. Test distinct sentinel setting effects/persistence/reset and derived-def restoration, not default equality.

## T33: Natural inhabited-approach integration

Scope: Close B3 on used plant-eligible unpaved field-edge, harvest and river routes serving an inhabited home, using current natural wet-native cycles and shared light/built-ground/suppression rules. Paving, including sealed churnmud, permanently excludes regrowth on covered cells. Entrance upkeep ends when its eligible approach is paved; no edge invasion or floor maintenance system is added. If existing defaults never contest access, specify/implement only a minimal local recurring-renewal opt-in through existing APIs, with natural source/water/light/suppression eligibility. No debug top, interior bypass or secret escalation.

Acceptance test: Natural default maintained/neglected used unpaved resource routes show plant-attributed path burden and visible recovery across first-day, established and forty-colonist regimes. Repair plus ordinary clearing restores access there. Replay early paving of home entrances with normal materials/work, leaving field/harvest/river routes unpaved: entrances remain exempt even without suppression, while untreated used eligible ground still renews. Fully paved used-route controls owe no regrowth upkeep; no compensating invasion or escalation. Empty eligible pools cannot prove the positive arm, and a firm rescue route remains reachable. M2 calibrates both paving and unpaved policies, never a growth-speed proxy.

## T34: All-kept-on situations and state adapter

Scope: Build M1 and read-only causal exports needed by B1–B8; reuse truthful kernels/scripts. Existing _site clears hostiles and locks Clear: retain as isolated checks only. Export plant sources, terrain/path/sight, conditions, suppression sources/expiry, jobs/reservations, complete objects/holders, health/study/wildlife and unique log signatures with fingerprints. Discover actual supported reads before adding minimal instruments; no bridge method names invented here.

Acceptance test: M1 partitions have asserted starts, actual-route witnesses, discriminating controls, mid-state Scribe and prior-settings/baseline restore. Broken emitter/inactive retained gate/failed medicine-use or job/wrong cache/dead density applier mutations cause refusal or UNMEASURED. Calibrate exact state/conservation and declared timing tolerances to actual game with every retained effect on and weather unlocked.

## T35: Rescue, native footing and conserved burial

Scope: Extend existing FreeMired/workgiver to complete usable firm-ground escape for both pawns; handle death/cancel/reservations/unreachable destination readably. Audit native/flying eligibility and live-off cleanup. Replace Thing destruction plus reduced tuple with saved complete ownership; keep exclusions, frozen buried time, stockpile scope and partial-merge/remainder accounting. Old reduced caches load honestly without fabricated lost fields.

Acceptance test: M1/M3 actual natural autonomous work witnesses show both subjects escaping to reachable firm ground, no immediate-retrap loop, safe refusal with no destination, correct native/airborne control. Full property fingerprints/quantity survive Scribe, blocked/partial placement, repeated dig and off. Old tuple saves load with explicit compatibility; no claim to restore historically lost state. Log clean.

## T36: Calibrated footing/field geometry

Scope: Implement M3 against actual field/plant/path/LOS/placement predicates and fallback root lanes. Field membership alone is insufficient; pair with natural growth outcomes.

Acceptance test: Exact actual-engine agreement over eligible/protected/blocked/reachable/placeable cell sets in declared geometry partitions; discrepancies yield minimal counterexample topology. Natural B3/B4 outcomes corroborate bounded protection; restored baseline verifies no scene leak.

## T37: Natural hosts and ordinary life witnesses

Scope: Add minimal naturally placed standalone gall near current sarquin/nemmer using shared bounded reaction service. Audit ordinary feeding/harvest/fishing/taming, tree fall sources, native water/mud, concealed hunt/reveal/hush ownership. Complete actual-flight state and directional whole-body assets without unattended flyer visuals; correct deferred-behavior overclaims.

Acceptance test: Default natural host-associated gall occurs without debug spawning; disturbance yields bounded source-tagged stings and retreat without deletion. Actual falls threaten workers and yield useful timber; hunt hushes biome ambience with visible sign and restores after last reason. Source-to-kitchen/tame witnesses, native water/footing and flight tracker controls cover B2 range with all kept effects active. No unattended visual flight claim.

## T38: Common heat and actual clearing return

Scope: Audit/correct legacy per-biome RM_SunHeatExtension active effect and misleading arrival/weather text; use common geometric sun/tree shade and vanilla air/room heat only. This proposal selects Direct Sun active on Greentide, conditional on the shared tree-shade model qualifying under the standing adopt-or-fall-back test (design/RimMandrake/tree_shade_model_2026-10-19.md §6). Establish qualification before accepting default-on evidence. Keep first-playable shade response and natural condition priority/return; implement M4. No local shade surrogate or silent off fallback if the shared dependency is unavailable; an off branch requires explicit proposal revision. Heat-law compliance is R7/C8 evidence, not B6 wording.

Acceptance test: Read effective Direct Sun active on this map and evidence of the shared tree-shade qualification. At matched positive sun angle, nonzero weather sun factor, equal outdoor air and gear, measured shared radiation contribution to felt temperature is positive on verified exposed cells and exceeds readings under both roof and canopy. Gate-off mutation and equal-radiation builds invalidate the evidence. Same geometry follows common sun inputs without Greentide offset; roof does not cool outdoor air, back-room blower cooling does not heat exhaust. Natural unforced shade-seeking, visible clearing and return survive reload/overlap with exact weather ordering and calibrated health/temperature trace. Missing shade qualification is UNMEASURED dependency work: no default-on readiness claim or local exception.

## T39: Ambient disease and obtainable medicine transitions

Scope: Retain ambient Frenzy surge/collapse/treatment fork and ordinary visible lace research/crafting/temporary bleed-stop. Add M1 actual completed-work, health, research/craft, use and bleeding adapters. T51/T52/T53 own deferred delivery/reward/discovery gates and decouple their callers; this ticket must not depend on enabling those extras, found-tech points or debug-unlocked recipes.

Acceptance test: With all next-version settings off, naturally sourced ambient illness produces real work surge, multi-day collapse and the coma-stage treatment/death fork across Scribe. No dose, mark award, resistance or branch study is required. An initially unresearched colony sees ordinary lace research after MedicineProduction, completes it without specimen/points and crafts with the authored materials; real self/doctor use stops total bleeding including stumps without tending/healing, with possible bleeding on expiry. Saved old marks confer no immunity under T52. Narrow already-ruled portability holds; default log clean.

## T40: Whole-season model and replay

Scope: Build/calibrate M2 and B8 full-map season, including maintained/neglected and early-paved-home-with-unpaved-resource-route policies plus fully paved used-route negative controls, mid-cycle reload and reverse action order; compression preserves actual ticks of growth/weather/jobs/hunger/health/spawns. Never pre-spawn harvest stock, force tops, remove threats or grant repeated supplies.

Acceptance test: Actual trace meets M2 calibration and B8 default full-season cycle, including natural growth and clearing/return; extend run until cycle completes. Maintained foothold stays productive/recoverable, neglected eligible-ground comparison loses access/work visibly; early-paved home entrances remain regrowth-free without suppression while unpaved resource routes still require care. Construction costs and terrain eligibility match actual state; fully paved used-route controls need no regrowth upkeep; no flood, barren regime, perpetual work stall or repeated errors. Effective gates evidenced start/mid/end; rare conditional effects get separate actual-route witnesses. Label prediction versus game observation.

## T41: Unavailable composition and post-patch cast

Scope: Historical src/RimUtinni/UtinniPatches paths are absent here. At implementation find actual owning sources or fingerprinted composed defs before claiming full membership. Inspect external ant-material/goodwill and Wreckage/native-water interfaces; never invent patches or alter naming tiers.

Acceptance test: Intended all-DLC post-patch state documents actual cast/multi-homing (no evictions), canon-tier additions, material refs and deferred activation guards. Free roster stays rich, aliases and neighbour consumers resolve, external patches cannot activate local deferred behavior. Missing composition remains explicitly UNMEASURED; zero tiles is never a finding.

## T42: Future mechanic contract

Scope: Specify maddrick contact trap: victim/telegraph, release/rescue geometry, native/airborne exceptions, interrupted/reserved jobs, save/off and shared reuse.

Evidence: current flora/fauna defs and the_greentide.md promises, partitioned from the compound historical inventory capability; behavior is absent.

Acceptance test: none, absent deferred mechanic. Before future implementation, complete this bounded contract and its own simultaneous offline/live test plan. Specification alone never promotes it into this version.

## T43: Future mechanic contract

Scope: Specify phorrik movement cloud trigger, envelope, duration/effect/retreat, cooldown, native eligibility, persistence/off and shared gas route. Not the grenade.

Evidence: current flora/fauna defs and the_greentide.md promises, partitioned from the compound historical inventory capability; behavior is absent.

Acceptance test: none, absent deferred mechanic. Before future implementation, complete this bounded contract and its own simultaneous offline/live test plan. Specification alone never promotes it into this version.

## T44: Future mechanic contract

Scope: Specify nemmer periodic fruitfall source, timing, blocked placement, produce identity/rot, gall host interaction, save/off and food-chain bound; ordinary harvest remains now.

Evidence: current flora/fauna defs and the_greentide.md promises, partitioned from the compound historical inventory capability; behavior is absent.

Acceptance test: none, absent deferred mechanic. Before future implementation, complete this bounded contract and its own simultaneous offline/live test plan. Specification alone never promotes it into this version.

## T45: Future mechanic contract

Scope: Specify repeatable mirrelbole sap tapping actor/tool/work, plant cost/regrowth/depletion, output, interrupted/reserved jobs, save/off and relation to ordinary resin.

Evidence: current flora/fauna defs and the_greentide.md promises, partitioned from the compound historical inventory capability; behavior is absent.

Acceptance test: none, absent deferred mechanic. Before future implementation, complete this bounded contract and its own simultaneous offline/live test plan. Specification alone never promotes it into this version.

## T46: Future mechanic contract

Scope: Specify gristle underground hunt entry/track/exit tells, terrain/path eligibility, target loss, combat/death/corpse, save/off; no silent pawn disappearance. Ordinary predator remains now.

Evidence: current flora/fauna defs and the_greentide.md promises, partitioned from the compound historical inventory capability; behavior is absent.

Acceptance test: none, absent deferred mechanic. Before future implementation, complete this bounded contract and its own simultaneous offline/live test plan. Specification alone never promotes it into this version.

## T47: Future mechanic contract

Scope: Specify inhabited-bole dungeons only with enabled complete landmark: sealed/carved rooms, occupants, capture/death/evacuation, regrowth/warnings and save/off. Map placement capability alone is not this experience.

Evidence: current flora/fauna defs and the_greentide.md promises, partitioned from the compound historical inventory capability; behavior is absent.

Acceptance test: none, absent deferred mechanic. Before future implementation, complete this bounded contract and its own simultaneous offline/live test plan. Specification alone never promotes it into this version.

## T48: Distance-to-river cooking/desiccation band — future specification

Scope: A separate spatial moisture/thermal simulation; ordinary supplied air heat, shade, firm footing and enclosure already define viable home siting. Before any future build, define the source/eligibility/trigger, costs, bounded spatial or target effect, readable signs, interaction with native life and shared growth/thermal services, save/reload and off-state. A distance band cannot invent a private sun or wet-bulb species; drip cannot change fixed-world rain by generating a planet; extract must call the existing growth service rather than duplicate it.

Acceptance test: none, absent deferred mechanic; the future specification and simultaneous offline/actual-game tests are prerequisites to implementation, not this version’s passing criteria. Current default producers remain absent.

## T49: Under-canopy condensation/dripping weather effect — future specification

Scope: An additional weather/visual interaction beyond the retained low steam and clearing; ordinary ambience remains, without promising permanent new precipitation. Before any future build, define the source/eligibility/trigger, costs, bounded spatial or target effect, readable signs, interaction with native life and shared growth/thermal services, save/reload and off-state. A distance band cannot invent a private sun or wet-bulb species; drip cannot change fixed-world rain by generating a planet; extract must call the existing growth service rather than duplicate it.

Acceptance test: none, absent deferred mechanic; the future specification and simultaneous offline/actual-game tests are prerequisites to implementation, not this version’s passing criteria. Current default producers remain absent.

## T50: Portable Greentide growth extract — future specification

Scope: A player-invoked growth tool/export beyond the natural lifecycle; the signature works without bottled activation or sabotage. Before any future build, define the source/eligibility/trigger, costs, bounded spatial or target effect, readable signs, interaction with native life and shared growth/thermal services, save/reload and off-state. A distance band cannot invent a private sun or wet-bulb species; drip cannot change fixed-world rain by generating a planet; extract must call the existing growth service rather than duplicate it.

Acceptance test: none, absent deferred mechanic; the future specification and simultaneous offline/actual-game tests are prerequisites to implementation, not this version’s passing criteria. Current default producers remain absent.


## T51: Portable Frenzy dosing — switch off and separate ambient gate

Scope/decoupling: Add a labelled **Next version — portable Frenzy dosing**, off by default, independent of retained ambient disease. Preserve dose/toxin defs, aliases and saved items. Gate local toxin harvest while its only consumers are disabled dose/weapon packages, refining recipes, generated stock/offers, drug-policy use and administer/take actions; guard the ingestion outcome as a final backstop. Existing saved items stay inspectable and inert, never silently consumed or deleted. Keep gorbeleth ordinary plant/wood roles. Review any composed external consumer under T41; do not disable a neighbour's independently enabled use. The existing shared frenzyEnabled cannot switch ambient off to achieve this deferral.

Source/callers searched: src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml gorbeleth harvestedThingDef; Defs/ThingDefs/RM_Frenzy_Items.xml toxin, recipeMaker, drug and outcomeDoer; Source/RM_IngestionOutcomeDoer_FrenzyDose.cs; Source/RM_GreentideMod.cs shared frenzyEnabled and dose tuning; Source/RM_IncidentWorker_FrenzyDisease.cs ambient route. Paths after the first are relative to src/RimMandrake/Greentide/.

Reason: Ambient Frenzy supplies disease danger without voluntary delivery. Preserve the ruled stockpilable portable dose for the future enabled package, not an un-stockpilable plant-interaction substitute.

Acceptance test: On a fresh default map, state-read no generated dose-only toxin/dose stock, active refinement/administer/take offers, dose jobs or dose-specific notifications/incidents; log clean. Ambient illness still fires and reaches collapse/care with this setting off. On mid-save reload saved doses remain present/readable but produce no illness, automatic consumption or deletion while off. With the setting on and retained disease enabled, ordinary gorbeleth harvest/refining produces the portable item and completed take/administer infects the chosen pawn, including after travel; disease master off blocks it. Distinct gate flips persist/reset correctly. No debug dose stock is positive producer proof.

## T52: Fever survivor marks and resistance — switch off

Scope/decoupling: Use a labelled **Next version — fever survivor reward**, off by default, to govern new awards, earned-mark messages and every immunity consumer. The current feverMarkEnabled/feverMarkGrantsImmunity split misses the master in incident and dose selection. Both existing and newly reached-collapse state must obey the effective gate. Preserve saved mark hediffs and reached-collapse data as inert readable history while off; never delete a pawn or badge to implement disabling. Ambient illness retains its full work/collapse/treatment contract.

Source/callers searched: src/RimMandrake/Greentide/Defs/HediffDefs/RM_Greentide_Hediffs.xml attaches the survivor comp to RM_Frenzy and defines RM_FeverMark; Source/RM_HediffComp_MarksFeverSurvivor.cs saves reachedGateStage and awards mark/message on removal; Source/RM_IncidentWorker_FrenzyDisease.cs filters candidates; Source/RM_IngestionOutcomeDoer_FrenzyDose.cs checks immunity; Source/RM_GreentideMod.cs persists both toggles; Source/Kernel/RM_RulesKernel.cs calculates their outcomes. Relative paths have the same root as the first.

Reason: A permanent qualification/re-exposure reward is an independent progression bargain. Dangerous ambient disease and useful medicine still work without it; previous selection is preserved, not a necessity argument.

Acceptance test: On a fresh default map, naturally recovered coma survivors receive no mark, resistance, reward message, specialist job or incident; log clean. Reload an old marked save: the badge is readable, but the pawn remains eligible for ambient Frenzy and, in the separate T51-on arm, deliberate dosing. With survivor reward on, surviving actual collapse awards a visible persistent mark and, with immunity enabled, excludes repeat ambient/dose exposure; early removal or death awards nothing. Turning the master off defeats immunity even with its subtoggle on, without deleting badges; reload/persistence/reset remain clean. No general disease immunity or new expedition job is introduced.

## T53: Stellock branch discovery — switch off without blocking lace

Scope/decoupling: Label the branch-discovery setting **Next version — stellock specimen discovery**, default off, independently of retained lace availability/use. Existing stellockLaceEnabled currently drives RM_CompStellockBranchDrop and the registered Greentide.StellockLace found-tech gate: its name is not evidence of a lace-use master. Split/label actual responsibilities. Disable branch drops, study offers/jobs/points and reveal letters locally, and leave the lace project visible for ordinary research after MedicineProduction. Retain research cost, material chain, self/doctor use and temporary bleed-stop. Keep branch/project defs, aliases, saved branches and counters; old branches are readable and unstudiable off. Do not globally disable shared found-tech or reset researched projects. On restores ruled discovery for an unlearned colony, without re-hiding completed research.

Source/callers searched: src/RimMandrake/Greentide/Patches/RM_StellockLace_Patches.xml attaches tree drop comps and doctor recipe; Source/RM_StellockLace.cs PostDestroy checks the shared lace flag; Defs/ThingDefs/RM_StellockLace_Items.xml branch study comp, recipe prerequisite and MedicineProduction project; Source/RM_GreentideMod.cs registers the gate. These relative paths use src/RimMandrake/Greentide/. Shared src/RimMandrake/EnvironmentalHazards/Source/RM_FoundTechStudy.cs builds the registry from branch comps, gates study, and hides unfinished unrevealed research only with its gate enabled. Retain that shared service for neighbours.

Reason: The unique medicine reward is actual usable lace. Removing specimen discovery does not remove it once ordinary research remains reachable; current shared-key coupling proves a decoupling task only.

Acceptance test: On a fresh default map, natural qualifying felling yields no branch; no stellock study job/offer, points, reveal letter or incident is active and log is clean. A colony with no specimen/knowledge can see, ordinarily research and craft lace after MedicineProduction; real use meets B7. Mid-save branches/counters remain saved but inert off and cannot hide the project. With discovery on in a separately unlearned baseline, natural felling yields a rotting branch, completed study independently reveals the project and its letter, research/crafting/use then work; another found-tech project's counters are unchanged. Switching off mid-study cancels/relinquishes work cleanly and leaves research available; completed research is never revoked. Gate persistence/reset and loaded-def fingerprints agree.
