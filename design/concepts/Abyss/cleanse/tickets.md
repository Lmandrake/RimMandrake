# Proposal tickets

No ticket is applied by this pass. Defaults must suppress behavior as well as creation. Imported old objects remain serializable; disabling never silently deletes a pawn. Cross-capability parent gates compose; a child toggle cannot bypass its next-version master. After a restart-only switch, the interface says so.

## T1: Switch off built extra — legacy weather ports

Designer disposition: recommend_retire. Unused donor compatibility weather set duplicates owned active weather and serves no present player experience. Keep inert pending owner retirement.

Evidence and callers: RM_Abyss_DonorPorts_Weathers.xml; no entries in active RM_Abyss weather table.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: legacy weather ports', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress compatibility weather transitions. No active weather list may reference these compatibility defs; they stay resolvable for old references. 

Acceptance test: at defaults a fresh map's weather history/state contains no compatibility weather and the log is clean; deliberate compatibility-def lookup resolves without a transition. Acceptance test for enabled gameplay: none, unused compatibility weather has no legitimate enabled experience.

## T2: Switch off built extra — placement worker

Designer disposition: recommend_retire. Worldgen is permanently forbidden by standing ruling, not next-version work. Recommend deleting placement/rareness UI; until approved suppress all placement.

Evidence and callers: RM_AbyssBiome.cs -> RM_DarkKernel.BiomeScore; RM_AbyssMod.cs rarity UI; BiomeDef workerClass.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: placement worker', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress biome worldgen scoring or rarity controls. Worldgen is permanently prohibited: this gate is not exposed as an enable option; remove rarity UI from shipped behavior and keep an inert worker pending owner's retirement decision. Test a direct scoring call and assert it never places this biome. Do not create any world. 

Acceptance test: on a fresh fixed-world map at defaults, no placement work or rarity control is active and the log is clean; a direct worker call is inert. No enabled-presence test exists because enabling worldgen is prohibited by standing ruling.

## T3: Switch off built extra — storm call

Designer disposition: next_version. An extra scheduled manhunter encounter; removing it leaves Witchfire land weather and the light economy complete.

Evidence and callers: RM_MapComponentDark.StormCallTick -> RM_StormKernel -> TrySpawnSumm.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: storm call', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress storm-call rumble/flash sequence, call letter and summoned manhunter. 

Acceptance test: with defaults on a fresh map, state-read that storm-call rumble/flash sequence, call letter and summoned manhunter are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that storm-call rumble/flash sequence, call letter and summoned manhunter are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T4: Switch off built extra — heat observation

Designer disposition: next_version. A bespoke discovery/research unlock; ordinary heaters already demonstrate warmth and remain usable.

Evidence and callers: RM_MapComponentDark.MapComponentTick -> RM_HeatFoldingDiscovery.Check; RM_AbyssGameComponent.FinalizeInit grants when disabled.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: heat observation', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress heat-folding observation completion, research offer and discovery letter. Off must neither fire Check nor silently grant a project in FinalizeInit; observation/research are hidden and inert. 

Acceptance test: with defaults on a fresh map, state-read that heat-folding observation completion, research offer and discovery letter are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that heat-folding observation completion, research offer and discovery letter are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T5: Switch off built extra — fold lamp

Designer disposition: next_version. A custom directional tool is unnecessary when ordinary heat clears rooms and living plants light farms.

Evidence and callers: RM_MapComponentDark.DarknessAt -> RM_MapComponent_FoldLanes.ClearanceAt; RM_AbyssLight.cs Rebuild; RM_FoldLamp.xml research/build menu.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: fold lamp', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress fold-lamp build/research entries and clearance lanes. Decouple Dark.DarknessAt: disabled lane contributes neutral clearance; hide lamp/designator/research rather than leaving a plain buildable heater-lamp. 

Acceptance test: with defaults on a fresh map, state-read that fold-lamp build/research entries and clearance lanes are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that fold-lamp build/research entries and clearance lanes are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T6: Switch off built extra — gill ash

Designer disposition: recommend_retire. Secondary chemfuel husbandry duplicates tholin recovery and vanilla refinery feedstocks; no essential food-chain or light function.

Evidence and callers: RM_Gharrek.xml CompProperties_Shearable -> RM_GillAsh; RM_Recipes_Chemfuel.xml refinery recipe.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: gill ash', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress gill-ash shearing product/job and its refinery bill. Remove only the shearable product/job/recipe affordance at startup, leaving gharrek feeding, meat and shell intact. 

Acceptance test: with defaults on a fresh map, state-read that gill-ash shearing product/job and its refinery bill are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that gill-ash shearing product/job and its refinery bill are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T7: Switch off built extra — sorter rings

Designer disposition: next_version. Authored ring placement and memory are a parallel sign/lore system; ordinary sorter diet/hauling remain.

Evidence and callers: CompDurrgak.CompTickRare; CompDurrgakCairn.CompTickRare; AnnounceUnveiling currently targets cairns.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: sorter rings', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress new shard rings and ring memories. Unveiling keeps a generic physical-clearance notice with no ring look targets. Cairn memory comp must honor the gate on imported objects too. 

Acceptance test: with defaults on a fresh map, state-read that new shard rings and ring memories are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that new shard rings and ring memories are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T8: Switch off built extra — sorter sites

Designer disposition: next_version. Stocked den/cache set pieces are authored one-off interactions, unnecessary for ordinary life or Dark.

Evidence and callers: RM_Abyss.xml extraGenSteps -> RM_GenStep_DurrgakSigns.Generate; cryptid subclass calls Place directly.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: sorter sites', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress stocked den, ring row, salvage cache and supplied loot. 

Acceptance test: with defaults on a fresh map, state-read that stocked den, ring row, salvage cache and supplied loot are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that stocked den, ring row, salvage cache and supplied loot are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T9: Switch off built extra — summ hide

Designer disposition: next_version. Regeneration and UV injury are a separate megafauna husbandry mechanic; ordinary large native animal and Dark vision remain.

Evidence and callers: RM_Summ.xml -> CompRM_SummHide.CompTickRare -> Regenerate/Sun.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: summ hide', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress extra regeneration and RM_SummSunburn. Clean existing sunburn by normal decay when disabled, and preserve ordinary healing. 

Acceptance test: with defaults on a fresh map, state-read that extra regeneration and RM_SummSunburn are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that extra regeneration and RM_SummSunburn are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T10: Specify deferred promise — continuous growth

Designer disposition: next_version. Lifelong size/hunger/space escalation belongs to the deferred bane-and-boon beast, not ordinary native life stages. Preserve owner's no-plateau requirement there.

Evidence and callers: Brood item promise; RM_Summ.xml only finite life stages; no continuous implementation found.

Not built: retain the promise under a next-version switch that ships off; no first-version bar depends on it. Before implementation provide state/transition specification and a can-fail probe for lifelong growth escalation. No finite terminal life stage may be called lifelong growth. Scope follows the beast over its life; preserve expanding size, hunger and occupied-space consequences. 

Acceptance test: defaults produce no lifelong growth escalation; when implemented and enabled, a state trace must demonstrate the specified transition with an absent-cause control and save/load. Until then report unimplemented, never a passing def-presence check.

## T11: Switch off built extra — ship cover state

Designer disposition: next_version. Active gravship concealment is an independent stealth/cooldown system; existing sensor shadow and local obscuration supply first-version protection.

Evidence and callers: RM_MapComponentShipCover.cs MapComponentTick -> RM_CoverKernel; saved state; no outside dynamic API consumer found.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: ship cover state', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress active ship-cover accumulation, expiry and cover messages. Keep existing static EmpirePursuit shadow dependency; neutralize cover APIs and cooldown/output state while off. 

Acceptance test: with defaults on a fresh map, state-read that active ship-cover accumulation, expiry and cover messages are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that active ship-cover accumulation, expiry and cover messages are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T12: Switch off built extra — probe search

Designer disposition: next_version. Scheduled scout/report encounters belong with active cover, not to the ordinary Dark cycle.

Evidence and callers: RM_MapComponentShipCover.SpawnProbe/ProbeTick/Leave; Utinni Abyss_ProbeDroids.xml; militor fallback.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: probe search', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress Abyss-scheduled probes, their lords, report/departure messages. Off must stop the existing ProbeTick path and let any already spawned scout depart visibly; do not delete a pawn. 

Acceptance test: with defaults on a fresh map, state-read that Abyss-scheduled probes, their lords, report/departure messages are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that Abyss-scheduled probes, their lords, report/departure messages are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T13: Specify deferred promise — cover external effects

Designer disposition: next_version. Orbital trade isolation and dynamic pursuit response are deferred with active cover; do not mistake an exposed API for working consumers.

Evidence and callers: IsCovered/CoverLevel source search in src: no Abyss consumer beyond component/tests; EmpirePursuit uses static ShadowMultiplier.

Not built: retain the promise under a next-version switch that ships off; no first-version bar depends on it. Before implementation provide state/transition specification and a can-fail probe for dynamic cover suppression of trade and pursuit. Name actual pursuit/trade consumers; engine-start must break cover, reports require usable detection rather than radius through walls, and isolation must be temporary. 

Acceptance test: defaults produce no dynamic cover suppression of trade and pursuit; when implemented and enabled, a state trace must demonstrate the specified transition with an absent-cause control and save/load. Until then report unimplemented, never a passing def-presence check.

## T14: Switch off built extra — cryptid sites

Designer disposition: next_version. Additional deniable sites are lore set pieces, not ordinary habitat.

Evidence and callers: RM_Abyss.xml extraGenSteps -> RM_GenStep_AbyssRumorSites.Generate -> inherited Place.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: cryptid sites', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress additional rumor-site rings, dens and caches. All cryptid subfeatures inherit the next-version master; no Sith patch may activate the rulepack on its own. 

Acceptance test: with defaults on a fresh map, state-read that additional rumor-site rings, dens and caches are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that additional rumor-site rings, dens and caches are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T15: Switch off built extra — cryptid exchange

Designer disposition: next_version. Unwatched item exchange is a separate offering/reward interaction.

Evidence and callers: RM_MapComponent_AbyssCryptid.MapComponentTick -> ExchangePass -> Exchange.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: cryptid exchange', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress exchange item loss, rewards and letter. All cryptid subfeatures inherit the next-version master; no Sith patch may activate the rulepack on its own. 

Acceptance test: with defaults on a fresh map, state-read that exchange item loss, rewards and letter are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that exchange item loss, rewards and letter are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T16: Switch off built extra — cryptid phantom

Designer disposition: next_version. No-source clearing events are a parallel lore cause; warmth/weather already supply the Dark's physical transitions.

Evidence and callers: RM_AbyssCryptid.OpenPhantom; RM_MapComponentDark.DarknessAt -> PhantomClearanceAt.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: cryptid phantom', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress cryptid phantom clearance and phantom timers. Decouple Dark.DarknessAt with neutral clearance; remove existing in-memory phantoms when switched off. All cryptid subfeatures inherit the next-version master; no Sith patch may activate the rulepack on its own. 

Acceptance test: with defaults on a fresh map, state-read that cryptid phantom clearance and phantom timers are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that cryptid phantom clearance and phantom timers are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T17: Switch off built extra — cryptid lore

Designer disposition: next_version. Whispers/tales are extra lore events; keep the never-appear ban in all versions.

Evidence and callers: RM_InteractionWorker_AbyssWhisper; RM_AbyssCryptid RulePack; Abyss_CryptidSithWhisper.xml campaign patch.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: cryptid lore', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress cryptid interactions, tales and generated whispers. All cryptid subfeatures inherit the next-version master; no Sith patch may activate the rulepack on its own. 

Acceptance test: with defaults on a fresh map, state-read that cryptid interactions, tales and generated whispers are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that cryptid interactions, tales and generated whispers are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T18: Switch off built extra — cryptid dream

Designer disposition: next_version. A long-stay dream is a separate timed lore event; erosion already supplies the cost of staying.

Evidence and callers: RM_MapComponent_AbyssCryptid.DreamPass; map.AgeInDays rather than individual tenure.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: cryptid dream', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress RM_DreamtNoLight memories. All cryptid subfeatures inherit the next-version master; no Sith patch may activate the rulepack on its own. 

Acceptance test: with defaults on a fresh map, state-read that RM_DreamtNoLight memories are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that RM_DreamtNoLight memories are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T19: Switch off built extra — brood site

Designer disposition: next_version. Lightfall brood is a special expedition, not ordinary terrain or the light economy. Landmark geology remains external.

Evidence and callers: Patches/RM_BroodLair_MapGen.xml global step -> RM_GenStep_BroodLair.Generate -> MapWantsLair; RUT_Lightfall_BroodLair.xml.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: brood site', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress lair mother, clutch, great bones and associated wreck placement. Hide crafting/building/bill/use affordances as well as natural placement. Landmark/def references must remain load-safe. 

Acceptance test: with defaults on a fresh map, state-read that lair mother, clutch, great bones and associated wreck placement are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that lair mother, clutch, great bones and associated wreck placement are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T20: Switch off built extra — brood pressure

Designer disposition: next_version. Saved greed/wake pressure is the deferred expedition's risk system.

Evidence and callers: RM_MapComponent_BroodWake.Notify/MapComponentTick; egg theft and salvage recipe completions call Notify.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: brood pressure', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress pressure changes, stir/rumble letters and wake timer. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that pressure changes, stir/rumble letters and wake timer are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that pressure changes, stir/rumble letters and wake timer are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T21: Switch off built extra — brood wake

Designer disposition: next_version. Landscape mother transformation/manhunt is that expedition's consequence.

Evidence and callers: RM_MapComponent_BroodWake.WakeMother; Building_RM_BroodMother.PreApplyDamage.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: brood wake', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress sleeping-to-awake transformation, mother manhunt and threat letter. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that sleeping-to-awake transformation, mother manhunt and threat letter are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that sleeping-to-awake transformation, mother manhunt and threat letter are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T22: Switch off built extra — bone resources

Designer disposition: next_version. Special great-bone retrieval and SummBone stuff serve imprinting/expedition, not ordinary butcher bone.

Evidence and callers: RM_BroodLair.xml -> lair generator; RM_BroodEgg.GreatBoneAboard; place worker; special build entry.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: bone resources', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress special Summ great-bone placement/build option and lair bone resources. Hide crafting/building/bill/use affordances as well as natural placement. Landmark/def references must remain load-safe. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that special Summ great-bone placement/build option and lair bone resources are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that special Summ great-bone placement/build option and lair bone resources are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T23: Switch off built extra — egg theft return

Designer disposition: next_version. Egg theft/return is a bespoke expedition interaction.

Evidence and callers: RM_CompSummEgg.CompTick -> HeldByPlayer/LairMap -> wake.Notify.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: egg theft return', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress egg theft state/pressure/refund and return inspect changes. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that egg theft state/pressure/refund and return inspect changes are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that egg theft state/pressure/refund and return inspect changes are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T24: Switch off built extra — egg storm

Designer disposition: next_version. A carried egg's home-map weather/manhunter clock is a secondary encounter system.

Evidence and callers: RM_CompSummEgg.CompTick -> StormTick -> Witchfire transition and Summ spawn.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: egg storm', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress egg-caused storms and searching Summ arrivals. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that egg-caused storms and searching Summ arrivals are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that egg-caused storms and searching Summ arrivals are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T25: Switch off built extra — egg hatch imprint

Designer disposition: next_version. Bone-gated bonding is the expedition reward system.

Evidence and callers: RM_CompSummEgg.CompTick -> Decide/GreatBoneAboard/Hatch.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: egg hatch imprint', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress special egg hatch, bone-gated bond and bond inspect effects. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that special egg hatch, bone-gated bond and bond inspect effects are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that special egg hatch, bone-gated bond and bond inspect effects are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T26: Switch off built extra — summ bane

Designer disposition: next_version. Autonomous extra killing and hunger escalation belong to the bonded-beast package, not ordinary rostered Summs.

Evidence and callers: RM_Summ.xml attaches CompRM_SummBane to ALL Summs; CompTick adds hunger before baneEnabled guard.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: summ bane', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress RM_SummRuinousHunger and autonomous bane hunts. Move the hunger-hediff addition behind the gate too: merely setting baneEnabled=false leaves that side effect running. Keep ordinary tame Summ behavior. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that RM_SummRuinousHunger and autonomous bane hunts are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that RM_SummRuinousHunger and autonomous bane hunts are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T27: Switch off built extra — wreck salvage

Designer disposition: next_version. Finite rescue-wreck bill economy is an authored expedition reward, separate from ordinary Wreckage.

Evidence and callers: RM_GenStep_BroodLair.Generate -> Building_RM_ShipWreck -> RM_RecipeWorker_WreckSalvage.Notify_IterationCompleted.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: wreck salvage', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress rescue-wreck salvage bills, stock products and greed calls. Hide crafting/building/bill/use affordances as well as natural placement. Landmark/def references must remain load-safe. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that rescue-wreck salvage bills, stock products and greed calls are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that rescue-wreck salvage bills, stock products and greed calls are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T28: Switch off built extra — ship restore

Designer disposition: next_version. Fittings that repair a particular ship are that expedition's payoff, not ordinary salvage resources.

Evidence and callers: part defs -> RM_CompUseEffect_FitToShip.CanBeUsedBy/DoEffect; WornShipBuildings uses substructure.

Keep code and defs in the tree. Gate this entire capability behind a Mod Setting labelled 'Next version: ship restore', shipped off, including startup defaults, Scribe defaults, reset and composed settings. No debug proof is allowed to make a default-map reading count as normal play. Suppress fit-to-ship use effects, repair/refusal gizmos and consumption. Hide crafting/building/bill/use affordances as well as natural placement. Landmark/def references must remain load-safe. All expedition subfeatures inherit the brood next-version master; test them separately under that master. 

Acceptance test: with defaults on a fresh map, state-read that fit-to-ship use effects, repair/refusal gizmos and consumption are absent/inactive, no jobs/letters/incidents from this capability occur through a season, and the log is clean; enable its labelled next-version setting and required parent next-version settings in a disposable map, perform its documented trigger, and state-read that fit-to-ship use effects, repair/refusal gizmos and consumption are present/active. Inspect def/menu affordances as well as spawned things. Restore defaults and discard the test map.

## T32: Specify deferred promise — Lirrith custom corpse decay/disease bite

Designer disposition: next version, switched off. Ordinary feeding/attacks suffice; corpse processing and infection are additional systems. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T33: Specify deferred promise — Moravatha bespoke low-rest behavior

Designer disposition: next version, switched off. Pack grazing does not need a special rest engine. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T34: Specify deferred promise — Ysvaltha bespoke blade/tail attack animation or ability

Designer disposition: next version, switched off. Existing melee tools already implement its predator role; shoulder blades are not a flight promise. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T35: Specify deferred promise — Sesserith ranged spine spray

Designer disposition: next version, switched off. Ranged spray is a second attack system beyond ordinary melee predation. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T36: Specify deferred promise — Ossumatha custom hungry digging and propagated group rage

Designer disposition: next version, switched off. Ordinary herd grazing/retaliation remains whole without custom terrain damage or propagation. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T37: Specify deferred promise — Glow-globe special poison when eaten

Designer disposition: next version, switched off. Light economy needs a living lamp, not an additional ingestion hazard. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T38: Specify deferred promise — Sickly mushroom bespoke spore-air exposure

Designer disposition: next version, switched off. Inherited pollution-ground plant behavior is sufficient ordinary life; a new exposure system is extra. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T39: Specify deferred promise — Paddle-vine tracking/turning toward light

Designer disposition: next version, switched off. A moving plant gimmick is unnecessary to fiber harvest or lighting. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T40: Specify deferred promise — Chemistry seep tapping and explosions

Designer disposition: next version, switched off. Separate fuel/explosion industry duplicates the kept collapsed-grain fuel cycle. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T41: Specify deferred promise — Harvested berry item emitting mobile light

Designer disposition: next version, switched off. The plant already gives RawBerries; inventory light is a new portable-light capability. No first-version work is authorized for this mechanic. Preserve ruled species/look; gate behavior and make descriptions distinguish dormant future behavior from current function. Before enabling, name states, triggers, readable consequences and reset/reload rules.

Acceptance test: default fresh-map state has no such custom effect and a clean log; after implementation, enabling its next-version setting and exercising the trigger produces the specified effect while an absent-cause control does not. Unimplemented is reported as unimplemented.

## T42: Locate and gate any campaign Abyss rites

Search the external rite implementation before any later build. If present, retain defs/code behind a next-version setting default off; no ritual job, letter, incident, menu or reward may run by default. This is not evidence that the rites are built. Do not revive already waived rites or cut gust-turbine work.

Acceptance test: fresh default campaign map has no Abyss rite offer/jobs/results and a clean log; if a binding exists, enabling the next-version setting makes that rite offer and its defined result present. If no implementation exists, record absent and require the state specification before enabling.

## T29: Instrument and display the local Dark boundary

Needed by land, Dark protection and the light-defense loop. No local spatial renderer was found; a sky palette is not one. Specify a read-only grid overlay/trace that samples the same final density queried by sight, lamps and audio, then the defined class-specific presentation: terrain and relief lose detail/contrast with density but keep readable relief and routes; buildings dim with retained outlines/footprints; player-owned colonists, tame animals and mechs stay fully drawn; wild animals, hostile pawns and neutral visitors dim but retain discernible silhouettes, never sprite culling. Selection outlines, inspect access, controls and warning text stay readable. Ordinary unexplored fog remains unchanged. A predator's retained dim silhouette plus its existing close-attack tell keeps it perceptible; no new warning system is required. Use existing art where possible; no art is made on this pass. It must work in both clear and dark sky palettes, across zoom and on the map edge. A debug overlay alone cannot satisfy the appearance bar.

Acceptance test: at unchanged sky/time, a maintained heated room and cold outdoor control have density-matched visible boundaries, including the view through an open doorway. A cold reader finds the usable route and distinguishes density-scaled terrain/building detail loss from sky tint. Compare the same wild animal, hostile pawn and neutral visitor in clear/Dark cells: each dims but retains its silhouette; unchanged-render and full-sprite-culling mutations fail. Colony colonists, tame animals and mechs remain fully drawn; selection/inspect/UI/warning text remain readable. Repeat through Unveiling, room cooling after enclosure opens, map edges, supported zoom and reload, with next-version pockets/halo/release off and a clean log. The geometry model supplies worst-case capture sites.

## T30: Ground the black etched local relief without changing the planet

The owned sand is present; a forced obsidian rock/local relief consumer was not located. Read actual resolved rock choices and local-map output before calling it absent. Use the frozen sheet's black, etched standing relief, with walkable low ground and ordinary building affordances. Do not paint tiles, change hilliness or create alternative worlds. Existing authored map data is the input. A terrain tint over ordinary round boulders does not substantiate etched crags.

Acceptance test: local-map state identifies the actual rock/terrain definitions and building affordances; captures across the land range show black etched relief with traversable/buildable low ground, while a flat black-sand-only control is sorted as reject. Report implementation absent if no owned rock route exists, rather than citing donor comments or tile counts.

## T31: Implement shared ambient Dark and optical transitions

Needed by temperature clearance, obstruction, light and audio. Outdoor density follows the shared ordinary outdoor temperature; room density follows ordinary room temperature. No first-version outdoor microclimate is built or assumed. T43 gates the existing Perlin offset off, T5/T16 keep lane/phantom clearances neutral, and T44/T45 defer the unbuilt halo/release. Unveiling clears ambient Dark map-wide without changing geometry-based Direct Sun. Use a common ambient density query across retained consumers. Read and replace/justify the flat WeatherDef accuracy penalty so entirely clear warm-room paths regain ordinary aim while rays through outdoor Dark remain obstructed. A clear observer alone is not a clear ray. Room cooling after doors/enclosure change must follow the actual temperature update, not an independent optical timer.

Acceptance test: M3's geometry/order sweep agrees with actual density, ordinary temperature, target feasibility and glow reads for heated/unheated rooms, open/closed doors, enclosure removal, shared outdoor temperature transitions, warm rooms separated by Dark, Unveiling and save/load. At the same outdoor temperature/weather/settings, open-air cells have the same density regardless of position/time noise inputs. Fake-thermometer, flat blanket accuracy and endpoint-only targeting mutations are caught. Direct Sun inputs remain unchanged for the same tile/geometry across these weather transitions; no halo/release is required, no pawn vanishes and logs stay clean.

## T33A: Resolve ordinary plant and forage contracts

Read inherited/resolved defs and campaign tolerance patches before editing. Glow globe must sustain itself without sky dependence; the paddle vine may use living glow but must have a non-bootstrap wild establishment path. Glowing grass must visibly emit low local light, with no farm-strength overlight. Wickwood and the giant glow globe provide actual crop light; dark-adapted plants still need suitable temperature. Etchcap growth/sowing checks actual RM_EtchHollow terrain, not fertility alone (ordinary RM_ForsakenSand already passes the current threshold). Determine whether a legal wild hollow exists before the first rock erodes; use ordinary static local hollows if necessary, never make etchcap grow on plain sand to fill the roster. Giant fibre stalk must not yield workable premium fibre by inherited fields. Abstract foraging uses the biome's actual ordinary food (RawBerries), not an unsupported agave population. Poison, new spores and moving harvested berries remain deferred and descriptions must not promise active off mechanics.

Acceptance test: state traces of natural establishment, planted growth, berry/fungus harvest, timber and fibre harvest hold on both RM and campaign-resolved defs without sky light; an adjacent unlit ordinary crop fails growth while the lamp-lit warmed crop succeeds. Etchcap succeeds on hollow and fails on fertile plain sand. A grass glow-grid sample changes with grass presence without growing an ordinary crop. Resolve actual inherited stalk products. Reload and lamp destruction do not create free light or a food item unrelated to its source. Clean log.

## T34A: Align real wind, feeder survival and sensory pulses

The current gust controller detects excursions of vanilla wind; it does not create intermittent wind. Specify/verify actual wind history in the existing climate, including Witchfire, against the frozen no-steady-wind ruling. Use the existing shared gust signal for feeding, visible openness and sound. No turbine echo: owner already cut it. Warm/low-wind regimes must not make native gharreks permanently dormant and starving, and reloading a gust must not feed twice. Fan-opening state must be player-readable without needing a new bespoke harvest.

Acceptance test: M4 compares unforced game wind to detected gusts, gharrek nutrition/dormancy and sound-event timestamps through stillness/storm transitions and reload; continuous wind with cosmetic gust audio, fabricated forced-only gusts, duplicate feeding and population starvation all fail. Normal pauses/speed changes preserve game-tick relationships; the log is clean.

## T35A: Complete the light-thief and predator response boundary

Keep the LightLedger engine. Krizzak requires a reachable settling position with an unobstructed local path to the actual emitting light; current nearby branch lacks that check. It feeds on emitted light, not power, hull or all lamps on the map; warm air interrupts feeding, tame/dead/downed/despawned individuals do not feed. Native plants resist ambient Dark but can be fed on; deepfire is exempt from ambient Dark dimming, not automatically from the animal. Overlight must contract with effective usable crop light, or lamp-thief crop pressure is false. Light aversion is a reachable-darkness response, not guaranteed invulnerability. Ombrathia's readable rattle/text precedes the close attacking opportunity even if its hunt began out of range; it must not spam per job oscillation. Keep ordinary walls, cooldowns and visible retreat.

Acceptance test: a sealed-room/through-wall feeder cannot dim a glower; opening access permits ordinary approach and feeding. A warmed lit plot supports growth; local feeding reduces usable lit plot and removing feeders restores it without cancelling ambient or another ledger share. Actual nearby predator behavior differs with light restored; a cornered predator is not declared magically safe. Hunger, taming, death, moving/removing a lamp, power changes and mid-feed reload are covered. The warning trace orders player-readable sign before close damage and logs are clean. A direct forced Feed call alone is not acceptance evidence.

## T36A: Make shipped settings express this proposal and preserve state safely

Parent and child next-version gates compose; defaults, ExposeData defaults, reset, startup and the BiomesShell surface agree. Do not simply flip current fields: CompRM_SummBane adds hunger before baneEnabled, FoldLanes leaves a buildable lamp, discovery-off silently grants research, ring memories do not read sorter toggle, and old probes tick before Applies. Remove active worldgen/rareness affordances. Add a labelled default-off gate for built outdoor noise pockets; halo/release remain unimplemented next-version promises, not first-version build obligations. Explanations say when a restart/new map is needed. Muffle ships on under the existing owner card; no renewed listening approval. The current Sample.Update postfix returns early when all-sounds muffling is disabled and when a sample is no longer on an Abyss map: neutralize only the Abyss-owned filter contribution on those transitions, including long-lived/pooled samples, rather than leaving stale muffling or destroying another mod's filter. No destructive save migrations and no new cross-biome toggle. Imported old extras stay loadable and inactive; placed pawns leave/continue ordinary life with signs instead of vanishing.

Acceptance test: default fresh-map state has exactly kept behavior enabled and all deferred capabilities inactive, including menu/bill/letter/job access; reset and reloading settings preserve that state. Each major feature off disables its behavior at its labelled scope and clears only its own transient contribution. All-off leaves an ordinary playable terrain/life/weather map and clean log. A legacy settings/save fixture loads without new orphaned effects; deliberate opted-in extras retain their choices only under explicit next-version parents. A settings-only screenshot is not proof.

## T37A: Replace proof-by-def-presence with the bar instruments

Keep existing kernels, fuzz and lint as checks. Add the situation generator, geometry and whole-map models defined in models.md; a model is untrusted until game agreement is recorded. Add read-only state instruments for actual temperature/density, crop growth/glow/overlight, animal jobs/flight/food, warning-to-damage ordering, terrain erosion/roof coverage, defaults and external pursuit timer consumption. Capture input hashes and actual composed RM/campaign defs. Old ProofSigns places content and ProofGust forces events: neither establishes ordinary new-map wiring or natural timing. No off-map or force-created success counts as whole play. Every disturbance uses disposable maps, scoped save fixtures and deterministic reset; no canonical save or world mutation.

Acceptance test: each bar's instrument rejects its explicit wrong-build control, records the starting state and all default feature states, and resets without residue. Existing static, fuzz and mutation checks remain separately labelled, including tests for next-version opt-in. A complete natural full-map season trace includes mid-cycle save/load, reversed main-action ordering and state/capture evidence linked to the bars. Pursuit delay is read at the timer consumer against same-state absent-shadow input; no assertion rests on a cover API or biome label alone.

## T43: Switch off built extra — outdoor drifting pockets

Designer disposition: next version, switched off. Evidence/callers: RM_MapComponent_Dark.DarknessAt reads GetTemperature and PerlinNoise, then RM_DarkKernel.DarknessAt adds PocketOffset; MurkPass, LampPass and RM_AbyssSoundscape.ValueFor consume the result. RM_HeatFoldingDiscovery.AmbientDarkness reads OutdoorTemp directly. Code coupling is not a need: removing outdoor noise leaves the ambient temperature curve, warm rooms, Unveiling, light feeders and grain functional.

Keep the offset code in the tree behind a Mod Setting labelled 'Next version: outdoor drifting pockets', off in initialization, Scribe/load, reset and composed settings. Decouple the retained ambient query from this unconditional offset and all disabled lane/phantom effects. The off path supplies zero offset (not a zero noise sample, which currently means a negative offset). Do not introduce a new heat kind or advertise an effective-temperature offset as ordinary warmth. Before a supported later release, specify a cause and readable cue consistent with ordinary temperature and the frozen collapse mechanism; opt-in prototype variation alone is not proof of that future spec.

Acceptance test: on a fresh default map in Dark weather at a fixed transition-band outdoor temperature, a state sweep across unroofed cells/time reports no noise contribution and uniform outdoor density; room density still follows room temperature, no pocket-owned jobs/letters/incidents occur, and the log is clean. Enable its next-version setting on a disposable map: the built offset and spatial/temporal density variation are present under the same fixed outdoor input. Disable again and reload: only that contribution clears, the ambient curve and light/audio consumers remain functional, and no unrelated share changes. This enabled reading proves gating only, not a physically valid warm pocket.

## T44: Specify deferred promise — nevarithia carried Dark

Designer disposition: next version, switched off; absent, not first-version implementation work. RM_Nevarithia.xml's description promises the knot, while its header explicitly says it is owed and no halo comp exists. Nevarithia stays rostered as ordinary life. Deleting the player-facing knot leaves land, life and the ambient Dark/light/feeder/grain chain whole. The frozen description still requires a future knot carried even where ambient Dark cannot form; deferral changes no ruling.

Before enabling in a later version, specify footprint/movement, overlapping ambient/carried density, warm/Unveiled air, light/target/audio consumers, warning/presentation, downed/carried/map-exit transitions, settings-off cleanup and save/reload. Pair it with T45; no global eclipse. Shipped descriptions must distinguish this dormant promise from the working ordinary grazer.

Acceptance test: default fresh-map state contains the ordinary grazer but no carried density, light/aim/audio contribution or halo jobs/letters/incidents, with a clean log. After future implementation only, enabling its labelled next-version parent and exercising movement produces the specified local knot while a matched absent-grazer control does not; disabling clears only the owned contribution without deleting the grazer. Until implemented, report the enabled behavior absent, never as a passing future feature.

## T45: Specify deferred promise — nevarithia death release

Designer disposition: next version, switched off; absent, not first-version implementation work. RM_Nevarithia.xml promises release but omits the donor death action and contains no owned replacement. Death release depends on the separately deferred carried knot; it is unnecessary when no knot exists. No unrelated death cloud is added to ordinary first-version life.

Before future enabling, specify local release versus ambient clearance, bounded dispersal with readable sign/corpse, overlap/ownership, death/despawn/map-exit distinctions, reload and cleanup. Preserve the existing death-release description and halo ruling as future constraints, without resurrecting the donor eclipse. The release cannot activate independently of its next-version halo parent.

Acceptance test: at defaults an ordinary nevarithia death leaves a corpse/combat evidence and no release density/light/aim/audio effect, jobs/letters/incidents or log errors. After future implementation only, enabling halo and release settings and killing a halo-bearing beast produces the specified local dispersing release; a no-halo death control produces none, corpse/sign remains and reload/disable leaves no stale contribution. Until implemented, report this enabled effect absent rather than demanding it for this version.
