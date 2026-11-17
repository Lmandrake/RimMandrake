# Build and containment tickets

These are proposal tickets. Each moved built capability receives its own containment task. Source and defs stay in the tree pending any owner retirement decision. Factory defaults and newly introduced opt-in gates default off, and the UI labels reversible extras as next version. Each test uses a fresh disposable full Rot map, all DLC and every retained mechanic enabled. Absence means runtime things/effects/jobs/letters/incident eligibility attributable to the extra. Reference-compatible defs remain loaded. Def presence alone is insufficient for the enabled arm.

Every containment ticket also covers a legacy-settings/save sibling, default-off missing fields, old true fields behind the new opt-in, ongoing effect suppression, held-state conservation and master-off. Required prerequisites of an explicitly enabled extra are enabled together for its positive arm. New game data and actual normal jobs/ticks establish presence. Log comparison covers new errors and exceptions. Numerical regression readings remain checks.

## T1: Disable forbidden planetary placement

Disposition is recommend_retire. Designer decision. Recommend retiring automated planetary placement under the standing worldgen ban. It is permanently out of scope, including the next version. Preserve reference-compatible inert stubs if needed.

Source and callers

- src/RimMandrake/TheRot/Source/RM_BiomeWorker_TheRot.cs
- CLAUDE.md

- RM_TheRot_Biome.xml workerClass and RM_TheRotBiomeRanges extension, RM_TheRotKernel biome score, proof worker

Permanent exclusion under the standing worldgen ruling. Make score/selection entry points inert and remove active planetary placement options. Keep the worker type and range extension reference-compatible for existing defs. Worldgen has no opt-in in any version.

Acceptance test: With default settings on a fresh map, state reads show zero automated placement jobs, prompts, incidents or altered world-tile assignments and a clean new log. Inspect worker/mutator eligibility directly in a pure/offline harness. Attempted feature enablement still leaves all planetary selection inert. Existing authored/save references resolve. This standing forbidden capability has no positive opt-in.

## T2: Contain Permanent condition bootstraps coating; weather/roof-gated ladder decays under shelter, gear slows gain, symbiosis stops it, saturation can seed spore flesh.

Disposition is next_version. Designer decision. A coating-to-infection hazard is an independent survival system. Wet emission land and metabolism function without it.

Source and callers

- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_SheenHediffs.xml
- src/RimMandrake/TheRot/Defs/GameConditionDefs/RM_SheenExposureLock.xml
- src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_SheenExposure.cs
- src/RimMandrake/TheRot/Defs/StatDefs/RM_SheenProtection.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Apparel/RM_RotSporeKit_ChitinSpiderHelmet.xml

- RM_SheenExposureLock.xml biomeMapConditions, EnvironmentalWeather bootstrap, RM_HediffComp_SheenExposure

Gate the biome condition bootstrap and existing coating advancement/infection. Keep wet emission weather enabled. Preserve pre-existing pawn health records and display inactive status on loaded coating. Symbiosis and hazard apparel readers must tolerate the dormant branch.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the sheen exposure extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T3: Contain Owned human and animal allergy incidents/diseases, also used by Contagion; separate from Sheen coating. Rot front gates incidence.

Disposition is recommend_retire. Designer decision. Random allergy duplicates a second spore illness beside the exposure ladder. Recommend retirement of the Rot-owned incidence as redundant illness pressure. Shared Contagion consumers retain ownership.

Source and callers

- src/RimMandrake/TheRot/Defs/BiomeDefs/RM_TheRot_Biome.xml
- src/RimMandrake/EnvironmentalHazards/Source/RM_SporeAllergyIncidents.cs

- BiomeDef disease pool, RM_SporeAllergyIncidents and TheRotFront sporeAllergy gate

Disable Rot incidence in both the biome disease pool and shared incident eligibility. Keep shared illness defs and other biome consumers. A clean Rot should retain ordinary vanilla diseases under storyteller rules.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the spore allergy extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T4: Contain Brewing vessel, ingredient/work/research costs, live ingredients and live-prep markers; cold ruin plus lifespan, strict/lenient temperature option retaining expiry.

Disposition is next_version. Designer decision. The defended medicine expedition has its own production and expiry loop. Ordinary food and metabolic shelter work without its vessel or clock.

Source and callers

- src/RimMandrake/TheRot/Defs/RecipeDefs/RM_RotSporeKit_LivePrepRecipes.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_RotSporeKit_BrewingVessel.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_GuardianGroves_Ingredients.xml
- src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_LivePrepViability.cs

- BrewingVessel recipeUsers, live-prep RecipeDefs, TemperatureRuinable and Lifespan, RM_Patch_LivePrepViability

The existing livePreparations bool relaxes strict viability, so add a real acquisition/effect gate. Hide special brewing vessel/build path, special recipe offers and trader/quest outputs. Dormant ingredients and drugs preserve save identity. Enabled preparations retain expiry and cold-ruin semantics and the existing strict/lenient control.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the brew and viability extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T5: Contain Age-reversal cup configured for five biological years, adult floor and once-per-year saturation; scarce grove ingredients gate production.

Disposition is next_version. Designer decision. Age reversal adds an expedition reward and dosing system beyond ordinary life and metabolism. Existing potency/annual-limit rulings bind its next-version design.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml
- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_LivePrepHediffs.xml
- design/Jawa/worldbuilding/biomes/kits/rot_kit_spec.md

- RM_Brew_AgelessBrew -> RM_Tea_AgeReversal ingestion doer -> age and saturation hediff

Gate recipe offers, all acquisition routes and ingestion benefit. Preserve the ruled annual saturation and adult floor. The next-version switch requires enabled vessel, defended source and viability. Never leave the cap as a safe unguarded prize.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the ageless brew extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T6: Contain Temporary bioregeneration hediff heals old wounds and boosts natural healing.

Disposition is next_version. Designer decision. Permanent-injury healing is a special medical reward. It is unnecessary to the retained food/shelter chain.

Source and callers

- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_LivePrepHediffs.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml

- RM_Brew_RegenerantBrew -> RM_Tea_Bioregeneration -> RM_Bioregenerating healer comp

Gate recipe/acquisition and healer benefit, with safe retained hediff state on old pawns. Require enabled defended veil and viable preparation. Verify natural bill completion and ingestion when enabled.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the regenerant brew extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T7: Contain Lussa crown cup gives chemical joy and a timed positive memory.

Disposition is recommend_retire. Designer decision. Recommend retiring the special pleasure cup because vanilla chemical joy already supplies its named experience. It adds a separate brew reward with no indispensable role.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml
- src/RimMandrake/TheRot/Defs/ThoughtDefs/RM_RotSporeKit_LivePrepThoughts.xml

- RM_Brew_EuphoricBrew -> RM_Tea_Pleasure -> chemical joy and RM_EuphoricBrewMemory

Contain pending owner retirement decision. Gate cup recipe, acquisition, chemical joy and its custom thought. Require the enabled crown-defense/viability chain if opted in.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the pleasure brew extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T8: Contain Permanent fast-healing symbiont paired with increased hunger, live before ingestion.

Disposition is next_version. Designer decision. Healing/appetite symbiosis is a separate permanent bodily bargain.

Source and callers

- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_LivePrepHediffs.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml

- RM_Brew_QuickfleshSymbiont -> ingestible -> RM_Sym_Quickflesh stages

Gate recipe/acquisition and both healing/hunger effects together. An already joined legacy pawn keeps its identity and readable dormant health entry. Purging/recovery belongs to its own opt-in. Show prerequisites when enabling.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the quickflesh extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T9: Contain Sleep suppression paired with increased mental-break threshold and periodic mental-state risks.

Disposition is next_version. Designer decision. Sleep/mental-state symbiosis is a separate permanent bodily bargain.

Source and callers

- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_LivePrepHediffs.xml

- RM_Brew_NightwakeSymbiont -> ingestible -> RM_Sym_Nightwake stages

Gate recipe/acquisition, rest suppression and mental-state/thought effects together. No residual risk generator may tick in a default old-save load. Preserve state for explicit opt-in.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the nightwake extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T10: Contain Ingested symbiont grants Sheen immunity plus sunlight-scald stages; ordinary sun/shade systems own the surrounding environment.

Disposition is next_version. Designer decision. Immunity/sun intolerance is an extra bodily bargain coupled to deferred Sheen exposure. Its sun rule must keep the shared geometry.

Source and callers

- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_LivePrepHediffs.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml

- RM_Brew_SheenbloodSymbiont -> RM_Sym_Sheenblood sunlight comp and Sheen compatibility

Gate recipe/acquisition, compatibility and sunlight-scald as a complete pair. Keep the shared geometric sun model. Require its Sheen exposure and brew prerequisites to enter its active branch.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the sheenblood extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T11: Contain Mycoid resistance marker symbiont and toxic injection, with recipes and viability; the receiving Slime mod owns their anti-absorption effect.

Disposition is next_version. Designer decision. Slime resistance and injection serve a neighboring biome encounter. They add a separate export chain.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml
- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_LivePrepHediffs.xml

- RM_Brew_MycoidSymbiont / RM_Brew_ToxicInjection, ingestibles and receiving Slime consumers recorded historically, receiving source unavailable here

Gate resistance-symbiont/injection recipes, outputs and benefit markers. Coordinate receiver-facing behavior through existing contracts so an imported old marker is dormant by default. Source and receiving effect are separate evidence requirements.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the slime exports extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T12: Contain Selling marked Rot treasures gives a memory to colony symbiont hosts; culture starters are a distinct portable exception.

Disposition is next_version. Designer decision. Trade guilt depends on special symbionts and treasures. With those deferred the retained economy has no host requiring this event.

Source and callers

- src/RimMandrake/TheRot/Defs/Misc/RM_RotSporeKit_TreasureConscience.xml
- src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_TreasureSaleConscience.cs
- src/RimMandrake/TheRot/Defs/ThoughtDefs/RM_RotSporeKit_LivePrepThoughts.xml
- design/Jawa/worldbuilding/biomes/kits/rot_kit_spec.md

- RM_TreasureMarkerExtension on ingredients/preparations, RM_Patch_TreasureSaleConscience trade hook

Gate the sale hook by explicit next-version feature plus enabled host/treasure systems. Native ordinary product sales stay ordinary. Keep owner-set thought semantics in the enabled path and preserve culture-starter exception.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the treasure conscience extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T13: Contain Orlath cap, vekkra choker and grath elder carry active gas emitters; choking/toxic gas and damage defs supply their hazard.

Disposition is next_version. Designer decision. This row covers the ageless-cap prize defense only. Removing the special prize grove loses no ordinary food or metabolic shelter. Resident Prime/Skulltop defense remains in its own life row.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_GuardianGroves.xml
- src/RimMandrake/EnvironmentalHazards/Source/CompActiveGasEmitter.cs
- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml

- RM_AgelessCap CompActiveGasEmitter in GuardianGroves.xml, normal map plant ticking

Gate ageless-cap source appearance, valuable harvest, gas and all prize acquisition together. Preserve resident Prime and Skulltop gas. Source CompTick-on-Plant concern stays on the enabled next-version acceptance list.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the guardian gas extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T14: Contain Mirrash veil damage and false-fruit collection ring a network alarm routed through CreatureBehaviors reactions to tagged defenders.

Disposition is next_version. Designer decision. Summoned defenders for special live-prize groves add a separate expedition encounter.

Source and callers

- src/RimMandrake/CreatureBehaviors/Source/RM_CompPlantAlarm.cs
- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_GuardianGroves.xml

- RM_RegenerantVeil damage callback, RM_FalseFruit PlantCollected -> RM_CompPlantAlarm.TriggerAlarm -> reaction responder tags on native races

Gate veil source and harvest, its damage/collection alarm, and related responder wake events. Kept animals retain normal aggression. Empty-forest alarm success remains waived. Safe default must cover an old-map planted veil as well as new-map spawning.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the guardian alarm extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T15: Contain Pekk fruit has a custom collection trap, alarm and mat-grip lookup; lussa crown and false fruit are separately weighted wild plants.

Disposition is next_version. Designer decision. Custom lure/trap/ring is a special-prize encounter mechanic beyond ordinary predation.

Source and callers

- src/RimMandrake/CreatureBehaviors/Source/RM_Plant_FalseFruit.cs
- src/RimMandrake/TheRot/Defs/HediffDefs/RM_RotSporeKit_GuardianGroves_Hediffs.xml
- src/RimMandrake/TheRot/Defs/BiomeDefs/RM_TheRot_Biome.xml

- RM_FalseFruit thingClass RM_Plant_FalseFruit.PlantCollected -> RUT_MatGrip lookup and TriggerAlarm, BiomeDef independent spawn weight

Gate false-fruit appearance, custom collection trap, alarm and crown prize acquisition. Source currently looks up RUT_MatGrip while local def is RM_MatGrip. Fix/decouple that enabled path, and cover both cut and harvest entry points. A field of independently weighted fruit is insufficient to prove a protective ring later.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the false fruit extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T16: Contain Wounds mirror within RotSwarm or RotAgarikin cliques, wild and tame, with a severity gate and matching body-part paths; different tags do not mix.

Disposition is next_version. Designer decision. Damage redistribution is the runner-up signature. It creates an independent herd combat loop.

Source and callers

- src/RimMandrake/CreatureBehaviors/Source/RM_CompWoundLink.cs
- src/RimMandrake/TheRot/Defs/Fauna/RM_AgariPorts.xml
- src/RimMandrake/TheRot/Defs/Fauna/RM_Chittik.xml

- RM_AgariPorts.xml, RM_Chittik.xml wound link comps and tags -> CreatureBehaviors damage callback. TheRotFront.StripRotKinWiring when off

Use a Rot-specific gate covering live and saved natives, including campaign-injected tags when present. Keep all roster rows. Preserve unrelated kin tags. Current each-recipient mirror arithmetic needs an explicit next-version engine choice against the historical split spec before balancing. Source coupling to alarm tags is not a need to keep alarms enabled.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the kin wounds extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T17: Contain Body-size-proportional healing among sufficient same-tag kin: agarikin, wildkin and plobbum broodmates; LeaningScrub owns durrok/mullgoth bodies.

Disposition is next_version. Designer decision. Kin healing completes the runner-up herd signature. The retained fauna still feed, reproduce and yield ordinary products without it.

Source and callers

- src/RimMandrake/CreatureBehaviors/Source/RM_HediffComp_KinMending.cs
- src/RimMandrake/TheRot/Defs/HediffDefs/RM_KinMendingNetwork.xml
- src/RimMandrake/TheRot/Patches/RotSpecies_WoundSharing.xml

- RM_KinMendingNetwork hediff grants on Agari/Grellik, RotSpecies_WoundSharing.xml for external Durrok/Mullgoth -> CreatureBehaviors kin radius check

Gate grants, existing hediff advancement and tag discovery for Rot cliques, including durrok/mullgoth/Grellik. Keep ordinary reproductive/product comps and other biomes kin networks. Honor the ruled clique table on explicit opt-in.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the kin mending extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T18: Contain Chittik attacks can implant a tendable infection; severe infected-host death spawns hostile chittiks, blood and sound, stripping corpse gear before corpse destruction; mechs/ghouls reject it.

Disposition is next_version. Designer decision. Host implantation and death spawning add a secondary disease/population loop. Chittik ordinary small-prey hunting remains.

Source and callers

- src/RimMandrake/TheRot/Source/RM_HediffComp_SpawnOnDeath.cs
- src/RimMandrake/TheRot/Defs/Fauna/RM_Chittik.xml

- RM_Chittik.xml claw damage/implant hediff -> RM_HediffComp_SpawnOnDeath on severe infected host death

Gate implantation at ordinary attack and existing infected-host death-spawn entry points. Keep claws as ordinary attacks. Old infection state must be dormant and readable, with corpse gear conserved. Mech/ghoul exclusions continue on the enabled path.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the chittik infection extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T19: Contain Quellan tree uses vanilla natural meditation, lumma moss and a two-level psylink list; scream/thought on destruction and selection. Franchise wording belongs in campaign patch.

Disposition is next_version. Designer decision. Meditation, psylink progression and sacred-grove destruction thoughts are a separate psychic system. Existing cap and declined whitelist remain binding if enabled later.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_PaleTree.xml

- BiomeDef RM_PaleTree -> vanilla meditation/subplants/Psylinkable, moss, destruction sound/thought, TheRotFront spawn gate

Gate the entire psychic source appearance, player planting/acquisition, moss/progression, thought and destruction sound. This is a special tree addition with its whole psychic loop deferred. Retain defs and save identity. Opt-in keeps the ruled cap and declined whitelist. Standing random-anima exclusion still governs vanilla.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the pale tree extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T20: Contain Cultivated thurrom hearth and finite-life grown furnace

Disposition is next_version. Designer decision. This original row is narrowed to grown furnace cultivation. Portable heater manufacture adds a replacement/lifespan loop beyond the native floor/harvest chain. Gene is split below.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_RotSporeKit_GrownFurnace.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_FurnaceCap.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_FurnaceCap.xml
- src/RimMandrake/TheRot/Defs/GeneDefs/RM_RotSporeKit_Furnaceblood.xml

- RM_FurnaceCap harvest -> RM_LivingFurnaceCap -> RM_GrownFurnace heat/lifespan. Furnaceblood GeneDef has comfort offset

Gate cultivated hearth sowing, cap output, building recipe/build menu and finite-life heat source. Kept native mat and produce use EnvironmentalHazards directly, without relying on this furnace. Preserve raw cap/building state on old saves.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the grown furnace gene extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T21: Contain Thrumbungus thrown toxic-spore weapon

Disposition is next_version. Designer decision. This original row is narrowed to the lobbed thrumbungus weapon. Weapon crafting is independent of ordinary life. Blast fuel and protection apparel split below.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Weapons/RM_RotSporeKit_ThrumbungusShroom.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml
- src/RimMandrake/TheRot/Defs/RecipeDefs/RM_RotSporeKit_Recipes.xml
- src/RimMandrake/TheRot/Defs/DamageDefs/RM_RotSporeKit_DamageDefs.xml

- RM_ThrumbungusShroom projectile, RM_BlastpodShroom harvest -> RM_BlastSpore explosive projectile and RM_Make_ChemfuelFromBlastSpore

Gate thrown thrumbungus acquisition, equipping/throwing and projectile payload. Do not disable native thozzik toxin combat or resident fungal gas to gate a crafted weapon.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the spore weapons fuel extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T22: Contain Regional suffocating cloud uses EnvironmentalWeather, flesh/roof filters, density changes and weighted incident. The incident explicitly excludes RM_TheRot itself.

Disposition is next_version. Designer decision. The regional export incident has a separate suffocation/density loop and explicitly excludes Rot maps. It cannot be a home-biome signature.

Source and callers

- src/RimMandrake/TheRot/Defs/GameConditionDefs/RM_RotSporeKit_SporeCloud.xml

- RM_SporeCloud IncidentDef and condition extension -> EnvironmentalWeather, explicitly disallowed in RM_TheRot

Gate storyteller eligibility and existing condition effects through the Rot front. Keep existing home-biome exclusion. Shared EnvironmentalWeather consumers outside this incident retain their contracts.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the spore cloud extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T23: Contain Hwelgrue custom open-ground item/corpse grazing, bespoke cap and first-sighting letter

Disposition is next_version. Designer decision. This row is narrowed to custom item/corpse grazing and bespoke first-sighting/cap behavior. Body and vanilla diet remain. Removing arbitrary-item digestion leaves an ordinary giant animal in the food web.

Source and callers

- src/RimMandrake/TheRot/Source/RM_Hwelgrue.cs
- src/RimMandrake/TheRot/Defs/Fauna/RM_Hwelgrue.xml

- RM_Hwelgrue.xml Animal_PreWander splice -> RM_JobGiver_GutGraze -> RM_JobDriver_GutGraze -> RM_CompGutDigest.Digest. Body accounted separately

Split ordinary hwelgrue body/diet/retaliation from the hwelgrue bool that currently strips its roster. Remove custom item/corpse graze jobs and first-sighting letter from defaults. RM_CompGutDigest cap runs before its bool check and destroys surplus with Vanish, so decouple cap from animal existence and use safe shared spawner admission. Keep any saved gut recoverable. Scanner ordinary body reading must lose the deferred metal-ring claim.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the hwelgrue body graze extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T24: Contain Metal-bearing things and corpse gear retained whole in saved gut, ordinary organics consumed; timed/death castings crack to return full-HP items, quality unchanged.

Disposition is next_version. Designer decision. Metal recovery and quality/HP restoration are a salvage economy. Ordinary native fauna and metabolic colony life require no gut inventory.

Source and callers

- src/RimMandrake/TheRot/Source/RM_Hwelgrue.cs:170

- RM_CompGutDigest.CompTick / Notify_Killed -> PassCasting / MakeCasting -> RM_CompSheenCasting and Crack open use effect

Gate Digest, timed/death castings, Crack-open recovery effects and their item acquisition together. Digest.Notify_Killed also calls RM_GutMother.DropSac, so keep that call independently gated. Freeze old gut/casting holders and provide safe explicit recovery, preserving item identity, quality and HP. Default animal corpse handling uses ordinary paths.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the hwelgrue castings extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T25: Contain Stationary, upright hwelgrue accelerates nearby rottables using temperature-dependent rot; it does not currently mark warm ground.

Disposition is recommend_retire. Designer decision. Recommend retiring the extra local rot aura because the map signature already performs decomposition. It adds a concealed overlapping radius without a distinct colony experience.

Source and callers

- src/RimMandrake/TheRot/Source/RM_Hwelgrue.cs:136

- RM_CompGutDigest.CompTick stationary test -> AccelerateRotAround -> RM_TheRotKernel.RotBoost

Contain pending owner retirement decision. Gate AccelerateRotAround independently of ordinary animal life. The global retained rot clock must have no call dependency on this aura. Opt-in test uses matched temperature and distance so ambient decay cannot masquerade as an aura.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the hwelgrue rest rot extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T26: Contain Downed-first graze takes one exposed pawn into a saved holder; inspect names it/time left; damage, downing, death or destruction can release it with earned acid; timeout kills and sorts remains; strangers may already be inside.

Disposition is next_version. Designer decision. Live swallowing, timed rescue and preloaded strangers form a separate encounter system. Ordinary giant diet needs none of it.

Source and callers

- src/RimMandrake/TheRot/Source/RM_HwelgrueSwallow.cs

- GutGraze job giver checks downed first -> GutSwallow job driver -> Swallow. CompTick timeout, damage/downed/killed/PostDestroy release

Gate graze selection of downed targets, GutSwallow jobs, stranger preloads, holder timers/damage/release effects and letters together. CompTick currently advances an existing held pawn without the setting check, so a default old-save load needs safe release or a readable recoverable frozen holder. Avoid digestion/death or lost items during containment. Never destroy the animal to hide the feature.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the swallow rescue extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T27: Contain Positional scheduled knocking stages or animal scrabbling diminish with remaining time; core ping/chirp pitch follows integrity. Existing audio uses borrowed vanilla clips.

Disposition is next_version. Designer decision. Urgency knocking and drive-core pings explain deferred encounters. Ordinary native calls remain with fauna.

Source and callers

- src/RimMandrake/TheRot/Source/RM_HwelgrueSwallow.cs:152
- src/RimMandrake/TheRot/Defs/Fauna/RM_Hwelgrue.xml
- src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_SwallowedDriveCore.xml

- RM_CompGutSwallow.Knock scheduled by kernel and swallowed-core Ping/Chirp. Body ordinary calls are separately retained

Gate scheduled knocking/scrabbling and navigator pings/chirps with their encounters. Preserve ordinary wildlife calls and wet weather audio. A muted sound alone leaves the encounter active and fails default absence.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the gut sound extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T28: Contain World-unique carrier/spent ledger, campaign tile restriction hook, stale-carrier reclamation preserving integrity, reappearing old-carrier demotion and no second death drop.

Disposition is next_version. Designer decision. The unique carrier ledger is part of the deferred ship treasure encounter.

Source and callers

- src/RimMandrake/TheRot/Source/RM_SwallowedCore.cs:122

- RM_CompSwallowedCore.CompTick -> TryClaim, world component ledger; campaignTile extension hook

Gate world claim/reclaim, carrier flags, pings and unique drop eligibility. Keep saved world ledger, integrity and spent state consistent while dormant. Ordinary hwelgrue must exist independently of this comp. Authored campaign tile picking retains its existing wait-for-paint ruling.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the core unique reclaim extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T29: Contain Ship-mounted-building damage lowers integrity; death yields minified core or ruin; linked core multiplies total engine range by configured bonus times integrity, ruin smelts as salvage.

Disposition is next_version. Designer decision. Ship weapon damage and engine-range reward are a second transport system beyond the biome.

Source and callers

- src/RimMandrake/TheRot/Source/RM_SwallowedCore.cs:195
- src/RimMandrake/TheRot/Patches/RM_SwallowedCore_Gravship.xml

- RM_CompSwallowedCore damage/death -> drop, RM_SwallowedCore_Gravship.xml -> RM_StatPart_SwallowedCore -> RangeFactor

Gate ship damage/integrity/drop and installed facility/stat contribution. RangeFactor currently omits theRotEnabled, so cover master-off as well as feature-off on an already installed core. Keep minified item identity and use independent removal/reinstall range reads in the enabled path.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the core damage range extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T30: Contain Engine-presence ping and saved schedule; fixed authored log advances at pings-per-entry, reveals salvage quests, last camp can reward a minified mat root, carrier death ends unread log.

Disposition is next_version. Designer decision. The log, salvage itinerary and last-camp reward are quests beyond ordinary land and life.

Source and callers

- src/RimMandrake/TheRot/Source/RM_NavigatorLog.cs
- src/RimMandrake/TheRot/Defs/Misc/RM_NavigatorLog.xml

- RM_CompSwallowedCore.Ping -> RM_NavigatorLog.Notify_Ping -> ReadEntry/TryRevealSite -> last camp minified RM_LivingMatRoot reward

Gate Ping -> Notify_Ping -> ReadEntry/TryRevealSite and carrier-death letters. Last-camp SiteScriptFor reads portableWarmMat, so require explicit opt-in for both the log and its reward. Old saved progress stays resumable, with zero default new quests, letters or reveal events.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the navigator log sites extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T31: Contain Death sac, analysis-gated research and grown vat buildable using sac or starter on other maps.

Disposition is next_version. Designer decision. Study-sac research and growing a vat introduce a separate technology unlock.

Source and callers

- src/RimMandrake/TheRot/Source/RM_GutMother.cs:48
- src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_GutMother.xml

- RM_CompGutDigest.Notify_Killed -> RM_GutMother.DropSac -> CompAnalyzableUnlockResearch -> RM_GutMotherCulture -> vat build

Gate sac death drop, analysis unlock, research availability and vat acquisition. Digest.Notify_Killed calls DropSac even with an otherwise empty gut, so gate this producer directly. Preserve analyzed research flags and old held corpses safely.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the vat analysis extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T32: Contain One corpse at a time through work bills; raw-food fuel, fed digestion, hungry dormancy; returns spawnThingOnRemoved implants and gear with first-recovery letter.

Disposition is next_version. Designer decision. Implant recovery is a secondary corpse-processing economy.

Source and callers

- src/RimMandrake/TheRot/Source/RM_GutMother.cs:115

- RM_FeedGutMother bill -> RecipeWorker_RM_FeedGutMother -> RM_CompGutMotherDigest.TryAccept / CompTickRare / Finish

Gate feed-corpse bills, TryAccept, CompTickRare digestion and Finish products/first-recovery letter. Preserve legacy corpse holder and gear on disable/reload and offer safe recovery. Source methods callable directly must respect the gate. Enabled test waits fed natural digestion and compares empty dormancy.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the vat recovery extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T33: Contain Nutrition/time split makes tradeable non-rotting starter, temporarily resting the vat; portable culture exception has independent value setting.

Disposition is next_version. Designer decision. Starter splitting/trading adds a portable production economy.

Source and callers

- src/RimMandrake/TheRot/Source/RM_GutMother.cs:127
- src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_GutMother.xml

- RM_SplitGutMother bill -> Notify_Split, starter used in build costs, ApplyStarterValue on startup/settings save

Gate split bills, starter output/trader acquisition and starter-built vats together. ApplyStarterValue may remain reference data maintenance, while new runtime items stay absent by default. Preserve explicitly carried old starters.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the vat starters extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T34: Contain Drug-lab research/recipe, list/extension-driven parasite and symbiont purge, husks, sickness and optional organ scar; forces vanilla metalhorror emergence.

Disposition is next_version. Designer decision. Parasite purge, metalhorror emergence and organ scars are a separate medical interaction. No deferred symbiont is needed by the retained signature.

Source and callers

- src/RimMandrake/TheRot/Source/RM_Unjoining.cs
- src/RimMandrake/TheRot/Defs/Drugs/RM_UnjoiningDraught.xml

- Drug-lab recipe -> RecipeWorker_RM_UnjoiningDraught -> IngestionOutcomeDoer_RM_Unjoining -> RM_Unjoining.Purge. Rite call exists only as source commentary here

Gate recipe/research acquisition and ingestion, Purge calls, husks, organ scars and metalhorror side effects. Shared historical rite caller must honor this gate, and the rite remains tabled. Enabled branch follows the source/spec permanent-scar behavior for a clean patient and readable vanilla emergence. No additional rite requirement is invented.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the unjoining draught extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T35: Contain Minifiable quest reward grows mat while fed raw food off Rot, stops heating when hungry and later uncovers its recorded grown cells; food-free within Rot. Reinstall resets growth tracking.

Disposition is next_version. Designer decision. Earned portable floor spread and starvation are an export/reward system. Native floor remains free inside Rot under the later ruling.

Source and callers

- src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs

- Navigator last camp reward -> minify/install -> RM_LivingMatRoot.CompTickRare -> spread/starvation, with terrain ownership state

Gate last-camp reward, all root acquisition/build/refuel offers, spread/food/dieback and installed/minified ticking. Preserve existing root/floor ownership on move and reload. Native mat warmth remains directly supplied by EnvironmentalHazards. Disabled legacy floors cannot vanish to hide the feature.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the portable mat growth extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T36: Contain Qualifying fed mat rooms warm with bounded ordinary heat, no second push from roots in one interval, no duplicate biome push; well-fed clocks bud roots with food cost and installed/minified map cap.

Disposition is next_version. Designer decision. Portable heat and budding add portable upkeep and reproduction. They retain the ruled food, Rot exemption and travel semantics for the next version.

Source and callers

- src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs:198
- infrastructure/state/live_proofs/ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD.txt

- RM_LivingMatRoot.CompTickRare -> room heat and bud clock, Root counting includes installed and minified forms

Gate portable heat, budding and upkeep together with root acquisition. The source implements its own heat deduplication and map root cap, so verify no second contribution survives the off state. Keep the ruled Rot feed exemption and supported-anywhere status when opted in. Coordinate with the prior ticket for ordinary cadence, minification and ship-floor transfer.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the portable mat heat buds extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T37: Contain Moldy-environment mutator/condition and outdoor mood penalty

Disposition is recommend_retire. Designer decision. This original row is narrowed to moldy-environment mood. Recommend retiring it because a flat outdoors penalty duplicates the named hostile-spore experience and adds no distinct decision. Other mutators split below.

Source and callers

- src/RimMandrake/TheRot/Defs/RetiredMutatorPorts/RM_RetiredMutatorPorts_TheRot.xml
- CLAUDE.md

- TileMutatorDefs chance fields/extraGenSteps/additionalGameConditions -> Prime scatter, mold mood worker, collector place worker and powered spawner

Contain pending retirement decision. Gate moldy-environment attachment, thought and all acquisition/activation paths. Shared outdoors-during-condition worker stays valid for unrelated consumers. Existing authored condition stays dormant and readable.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the mutator content extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T38: Contain Furnaceblood comfort-range gene

Disposition is next_version. Designer decision. A gene acquisition reward is independent of fungal land, ordinary life and storage metabolism.

Source and callers

- src/RimMandrake/TheRot/Defs/GeneDefs/RM_RotSporeKit_Furnaceblood.xml

- GeneDef enumeration, gene acquisition and pawn comfort stat

Gate gene acquisition and active comfort-offset effect. Keep GeneDef references for old xenotypes, showing dormancy instead of deleting pawn data. The deferred heat-pushing gene body has a separate spec ticket.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the furnaceblood extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T39: Contain Wild-only blastpod sac, explosive use and chemfuel recipe

Disposition is next_version. Designer decision. Explosive harvest and refining form a separate fuel/weapon economy. Keep the wild-only restriction whenever enabled.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml

- BiomeDef RM_BlastpodShroom -> RM_BlastSpore -> projectile / RM_Make_ChemfuelFromBlastSpore

Gate special harvest, explosive sac acquisition/use and chemfuel bill while preserving its flora identity if needed by existing saves. ExplosiveGrowth Churn enrollment can produce harvest independently, so its product path also requires gating. Opt-in retains wild-only planting restriction.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the blastpod fuel extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T40: Contain Chitin helmet with Sheen protection stat

Disposition is next_version. Designer decision. Special protective equipment is useful to the deferred coating hazard. Ordinary vanilla armor remains available for native fights.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Apparel/RM_RotSporeKit_ChitinSpiderHelmet.xml

- Apparel stat RM_SheenProtection -> shared exposure / hazard-apparel scorer

Gate special helmet acquisition and its extra protection behavior. Keep ordinary clothing/armor options and shared hazard stat reader valid. An already worn legacy helmet remains wearable, with its extra Sheen effect dormant.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the sheen helmet extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T41: Contain Ambrosyx intoxicant and source plant serving Slime dish

Disposition is next_version. Designer decision. An ambrosia-like drug and neighbor export are a separate experience beyond basic forage.

Source and callers

- src/RimMandrake/TheRot/Defs/Drugs/RM_RotSporeKit_Drugs.xml

- BiomeDef RM_AmbrosyxFungus -> RM_AmbrosyxShroom -> drug and external dish consumer

Gate the source spawn including bloom/cluster routes, harvest/drug acquisition, drug outcome and neighbor dish consumer. Existing ambrosyxSpawn only strips one native row at startup. Check old-map plants and external acquisition. Neighbor-facing consumer source is unavailable in this checkout, so resolve that integration before claiming enabled proof.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the ambrosyx extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T42: Contain Powered fungal hydroponic basin

Disposition is recommend_retire. Designer decision. Recommend retiring the duplicate hydroponic bench. Ordinary sowable fungi and vanilla controlled-growing infrastructure already supply the named cultivation experience.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_RotSporeKit_Buildings.xml

- RM_AdvancedFungi/Hydroponics research -> build menu -> Building_PlantGrower default RM_DulcisPlant

Contain pending retirement decision. Gate build menu, grower selection and job/power effects for the custom basin, while preserving old installed basin/plant state. Ordinary retained fungi remain usable through their supported normal sowing paths. Default research must not leak the basin.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the fungiponics extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T43: Contain Industrial medicine recipe from fungal medicine

Disposition is next_version. Designer decision. Ordinary harvested fungal medicine already supplies life. Industrial conversion adds an independent manufacturing shortcut.

Source and callers

- src/RimMandrake/TheRot/Defs/RecipeDefs/RM_RotSporeKit_Recipes.xml

- RM_IndustrialMedicineFromFungal RecipeDef -> worktable bills

Gate RM_IndustrialMedicineFromFungal bill availability and any automatic recipe injection. Keep ordinary fungal medicine harvest/use in the life economy.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the industrial medicine extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T44: Contain Cave-spider-head decorative trophy item

Disposition is recommend_retire. Designer decision. Recommend retiring decorative loot with no confirmed local source or named first-version experience.

Source and callers

- src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_Resources.xml

- ThingDef RM_CaveSpiderHead and style comp. No local yield or recipe caller located in TheRot defs

Contain pending retirement decision. Gate trader/loot/reward acquisition and special display actions. No confirmed local producer was located, so an enabled test must name its genuine producer or keep this acquisition unavailable and report the gap. Do not invent a new encounter to justify a trophy.

Acceptance test: With defaults on a fresh map, runtime trophy things, custom jobs, letters and incident eligibility are absent and the new log is clean. With explicit next-version opt-in, the reference-compatible trophy and its ordinary inspection resolve, and a verified existing acquisition route produces it. If no such route exists, record enabled acquisition as unproven and resolve the promised source before that future version ships. A forced developer spawn establishes inspection alone.

## T45: Contain Wayward Prime sprout on authored non-Rot tile

Disposition is next_version. Designer decision. An out-of-biome special encounter is independent of living in Rot. Automatic planetary chance is permanently forbidden and has its own retirement ticket.

Source and callers

- src/RimMandrake/TheRot/Defs/RetiredMutatorPorts/RM_RetiredMutatorPorts_TheRot.xml

- RM_AgariluxPrimeSprout TileMutatorDef -> RM_GenStep_AgariluxPrimeSprout scatter

Gate authored local outlier scatter and special encounter appearance behind next-version opt-in. All automatic planetary chance remains permanently disabled even with opt-in. Local map scatter uses an already authored site and leaves the fixed planet alone.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the prime outlier extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T46: Contain Edible airborne microfungi marker and powered food collector

Disposition is recommend_retire. Designer decision. Recommend retiring the passive food machine. Fungal forage already supplies food and vanilla hydroponics supplies powered production. Automatic placement chance is forbidden.

Source and callers

- src/RimMandrake/TheRot/Defs/RetiredMutatorPorts/RM_RetiredMutatorPorts_TheRot.xml

- RM_EdibleAirborneMicrofungi tile flag -> RM_MycoticCollector place worker -> powered CompSpawner

Contain pending retirement decision. Gate edible-microfungi acquisition flag use, collector build/place menu and powered CompSpawner output. Its planetary chance stays permanently disabled. Existing collector stays inert and save-compatible.

Acceptance test: With defaults on a fresh map, state reads at the ordinary producer and effect entry points named above show the air collector extra absent, including attributable runtime things, jobs, custom letters and eligible incidents, and the new log is clean. With its next-version setting on and declared prerequisites enabled, the same ordinary entry path produces the named things/effects or offers and completes the named jobs/incidents. A matched off-state control stays dormant. Repeat through restart where declared, then save/reload mid-transition and verify entity/holder conservation and master-off behavior. Kept land, life and signature remain active in both arms.

## T47: Disable forbidden planetary placement

Disposition is recommend_retire. Designer decision. Standing worldgen ban is absolute. Disable automatic placement permanently, retaining reference-compatible defs for authored save content. No next-version permission exists.

Source and callers

- src/RimMandrake/TheRot/Defs/RetiredMutatorPorts/RM_RetiredMutatorPorts_TheRot.xml

- TileMutatorDef chanceOnNonLandmarkTile fields consumed by planetary selection

Permanent exclusion under the standing worldgen ruling. Remove effective automated chance from all retired-port TileMutatorDefs and any cached selection paths. Keep identifiers for authored/save references. The authored local outlier option cannot re-enable planetary chance.

Acceptance test: With default settings on a fresh map, state reads show zero automated placement jobs, prompts, incidents or altered world-tile assignments and a clean new log. Inspect worker/mutator eligibility directly in a pure/offline harness. Attempted feature enablement still leaves all planetary selection inert. Existing authored/save references resolve. This standing forbidden capability has no positive opt-in.

## T60: Specify and bind milk substrate land

Required by B1/B2/B3/B7. No dedicated substrate or placement binding was located in the parsed Rot terrain defs or milk/milky search of src. Specify pale shallow/deep local fungal medium, surface/readout, movement and bridge affordances, compatible wet fungal plants and native drinking. Use existing local terrain/map placement support. Keep the fixed world, ordinary room heat and shared water/soak contract. Milk does not introduce a new spreading substance or potable-water economy. Quantitative pond coverage is a tunable check.

Acceptance test: On an ordinary authored Rot map the actual terrain read identifies fungal milk, native marsh fungi occupy supported wet cells, bridge placement works on its declared support, and standing/beside natives maintain hydration. The visual B1 traverse sees milk under its actual light and the current settings. Dry-ground controls preserve ordinary affordances. Reload and freeze/thaw if the shared terrain supports it preserve ownership/planting/bridging. No planetary tile changes or new logs.

## T61: Build the retained situation and transition generator

Required by B2/B4/B5/B6/B7 and unknown corpse_ownership. Build M1 using current pure production seams and exported room/holder snapshots. Extend existing TheRotFuzz sequence/shrinking pattern only where reusable. Cover default settings migration, retained native bodies, safe legacy extra holders and the actual corpse reservation/destruction seam. Keep deferred-chain existing tests scoped as checks.

Acceptance test: M1 emits a complete coverage matrix for declared partitions, with minimized failures for planted wrong exposure, double corpse destruction, lost held gear and an open extra gate. Real game save/reload and normal job transitions agree exactly on identities/eligibility and within the declared tick lag. Unavailable seams report unknown, and the corresponding bar keeps its game-state obligation.

## T62: Build the complete-season trace and driver

Required by whole B7 and M4, with all kept mechanics on at factory defaults. Reuse validation.py and northstar_plan.py scaffolding. Existing map_mechanics rows are UNMEASURED and forced giant helpers are irrelevant to the retained colony proof. Trace active settings, weather, room contributions, ordinary job completion, plants/animals, losses, starting inputs and errors. Plan the owner-present flight session required by standing ruling.

Acceptance test: A disposable full-map season and a mid-season save/reload sibling plus reordered-action sibling are recorded with identical source/settings/art fingerprints. Logs and entity/resource accounts reconcile, no kept subsystem is locked, and output classifies B7 flood/desert/stall/error candidates by the declared visible experience. A deliberately disabled wet-native/gas subsystem invalidates the whole reading. Calibrate M4 on independent traces before trusting its forecasts.

## T63: Build the contact, substrate and reachability instrument

Required by B2 and forest_geometry/terrain_substrate unknown meetings. Build M3 from the existing generated masks and production HugeThings transformations. Include every supported topology change, edge class, overlapping contact and wet/bridge/build boundary. Keep giant size/density intent.

Acceptance test: M3 returns exact occupied cells, placement and selection identity for the calibrated game fixtures. A displaced contact mask, wrong flip and third obstacle closing a corridor each produce a counterexample. Normal work jobs pass along open under-cap ground and fail at visible solid contacts for the correct reason. Milk bridge/native plant checks join the same geometry sweep.

## T64: Build thermal/storage trace and calibrated sweep

Required by B4/B5/B6 and room_heat/storage_decay unknown meetings. Build M2 over ordinary room heat using production contributions and real leakage/cooling inputs. Capture enclosure/floor/stock swaps and tick phase/reload. Existing native mat comments are arithmetic estimates.

Acceptance test: Independent cold/middle/warm game traces meet M2 contribution, temperature and preservation agreement. Swapping products or floor membership moves the responsible contribution. Missing food attachment, duplicated heat and global temperature offsets fail the relevant oracle. Output includes both workable storage and failing pressure regimes after each tuning change.

## T65: Verify ordinary native ecology and composition

Required by B3 and B7. Bind a normal-life trace to actual resolved composed defs. External durrok/mullgoth bodies and historical canon roster patch are absent from this checkout. Verify their owning source/dependency before claiming merged life proof. Preserve rosters and historical multi-home annotations. RM_Thozziks is a native affiliation reference with raidsForbidden and canStageAttacks false. Its required-at-start/configuration fields must create no new planetary factions or raiding feature. Reuse existing faction in the authored save when relevant.

Acceptance test: Normal harvest, feeding, hunt, milk, silk, eggs, larva metamorphosis and Agari reproduction produce traceable ordinary outputs. Every fictional flyer has capability readback and an owner-present actual crossing judgment. Natives maintain hydration beside milk. Ordinary thozzik attacks retain affiliation while no new faction/worldgen/raid runs. Saved deaths/departures conserve identities with readable signs. If external references remain unresolved, report the actual load/composition defect for repair without eviction or replacement.

## T66: Restore living-food content binding

Required by B6. The component and extension class exist, but exact XML search under src finds zero RM_LivingProduceExtension attachments in this checkout. Bind RM_Glimmerslime and RM_RawDulcis through the existing product extension mechanism. Update the proof wording that currently calls this live-preparation warmth. Ordinary food and special tea viability are separate consumers.

Acceptance test: Normal harvesting/hauling produces marked glimmerslime and raw dulcis stacks. Actual production MapComponent ticks add their per-room contribution, with matched ordinary-food, empty and off-setting arms. Stack split/merge/move/consume and reload move or remove that contribution without duplication. M2/game traces agree. A direct helper PushHeat call supplies no acceptance.

## T67: Fulfil proposed frozen digestive loss and enclosure contract

Required by B5 under the delegated frozen-digestion default in owner-pages Q1. Current RM_MapComponent_AcceleratedRot intentionally skips rate <= 0 and uses UsesOutdoorTemperature, consistent with kit M2 temperature scaling and the sheet's starving Frostcaps. Request a change to the existing EnvironmentalHazards contract to extend the exposed-meat deadline through freezing, preserving the owner walled-plus-roofed exemption. This is proposed behavior, not a settled owner requirement or a demonstrated code defect. If the owner chooses cold-edge preservation, narrow the frozen expectations in B5/C4 and this ticket, the inspection contract in T68 and definition.md, and recalibrate M1/M2/M4 instead. Engine implementation remains its owner responsibility. Preserve vanilla indoor preservation, corpse gear and held/reserved-object consistency.

Acceptance test: Under the Q1 default, normal tick reads on exposed meat across -42..24 C reach digestive destruction by the proposed 60000-tick deadline, with readable digestive state. Matched enclosed frozen stores retain ordinary preservation. Lean-to, roof gap, wall breach and enclosure changes agree with the owner predicate. Human/animal corpse gear and Bones/hauling/butcher outputs reconcile through reload and job cancellation. M1 and M2 identify the current frozen-zero candidate as failing the proposed default, without presenting that default as settled lore.

## T68: Expose retained causes through ordinary inspection

Required by B1/B4/B5/B6/B7. Use existing item/room/temperature/terrain panels to show digestive exposure including frozen food, native mat contribution and marked food load. Distinguish deferred legacy content as dormant. Supply an inspection/state adapter for tests where current public instruments are blind. No new letter stream is needed.

Acceptance test: A reader can locate actual causes in the normal inspect/temperature surfaces before and after enclosure/floor/stock changes. Serialized text/state fixtures follow the real status rather than global labels. The live traverse can identify food, native gas and the reason a frozen exposed stack is being lost. Off/legacy states remain readable. Test adapters report actual production state and reject missing or locked preconditions.

## T69: Verify normal plant gas cadence through the shared engine

Required by B3/B7 and resident predatory fungi life. The retained Prime/Skulltop carry CompActiveGasEmitter with CompTick, while Plant uses TickLong. Ask the existing gas engine to fulfill automatic emission under real plant ticking. Ordinary animal gas-on-damage remains its own native combat mechanism.

Acceptance test: With ordinary Prime/Skulltop present and every kept mechanic active, normal plant ticks emit local gas and an exposed approach records the corresponding health effect. A safe-distance/compatible-protection control avoids that local effect. Direct Burst is recorded as helper-only. Cut, death, weather transition and reload preserve expected emissions and clean logs. The generator catches a deliberately unticked plant emitter.

## T70: Specify the deferred gourmet line

Promised by the frozen sheet and partly suggested by existing ambrosyx and ordinary brogg milk. Define any future named dishes, source products, costs, player action and trade role against the deferred scope before building. Preserve ordinary milk and forage.

Acceptance test: The future spec identifies an actual source and normal recipe/trade path, state transitions, off-by-default acquisition gate and enabled/disabled acceptance cases. It names what remains ordinary forage. Any source still unavailable is explicitly unknown, with no claim that the complete cuisine already exists.

## T71: Specify the deferred heat-pushing gene body

Existing Furnaceblood widens comfort through a stat offset. Kit explicitly defers actual pawn-to-room thermogenesis. Define its future acquisition, cost, ordinary heat contract, persistence and gate before any implementation.

Acceptance test: The future spec identifies the room-heat contribution and safe enable/disable/save cases, retains the local-benefit-only gene rule and separates the current comfort gene regression check. A game comparison and heat-budget model are specified before treating a comfort offset as emitted heat.

## T72: Keep rituals and faction-grove wiring explicitly deferred

The answered Unjoining question tables the rite. Discovery, learned faith integration and Wildsteam sacred paths remain extras. No waiver or missing answer is inferred. Specify future dependency on found-rite machinery when that version begins.

Acceptance test: The deferred spec preserves the owner tabled state and lists discovery/learning/performance/research effects with explicit next-version off gates. Default-map inspection shows zero added ritual/discovery jobs, letters or incidents. No first-version bar requires a rite.

## T73: Specify the deferred found set-pieces

Found brewing shrines, pilgrim paths and special gene-rich digestion sites are promised dressing/encounters. Ordinary Wreckage content already has an engine and stays. Define future map placements, clearance, acquisition and loot rules before building.

Acceptance test: The future spec names authored local placement inputs, ordinary entry actions, guarded-prize requirements and dormant default acceptance. It creates no planetary generation, general gene archive or free special harvest. Existing ordinary Rot wreck field still resolves independently.

## T74: Specify the deferred giant warm-ground trail

RM_Hwelgrue.cs explicitly records no warm-ground marking API. If revisited, specify the player-facing rest/trail benefit, geometry, duration, ordinary heat and off behavior against the existing engine contract. Native mat requires no such trail.

Acceptance test: The future spec names a useful distinct experience, an existing engine integration or explicit feasibility gap, and a matched stationary/moving heat comparison with save/reload and default-off controls. Until then, giant warm-ground marking is absent and is never credited to B4.

## T75: Specify deferred local gene rewards and acquisition

Frozen sheet promises locally beneficial heat/compatibility/vigor genepacks. Current checkout supplies Furnaceblood but no complete local acquisition chain. Define exact future gene/content admission, normal acquisition, source guardianship and next-version gate. Keep the general genetic archive reserved to Slime.

Acceptance test: The future spec identifies available and missing gene defs and a real source for each reward, states eligible/ineligible effects, includes ordinary acquisition and opt-in/off tests, and retains the no-general-bank restriction. Default first-version maps expose none of this extra acquisition chain.

## T76: Specify deferred crown and false-fruit placement

The independent wild weights currently cannot establish the promised protective ring. Before enabling the special crown prize, define a local placement/approach contract using the shared placement tools. Name the cue, ordinary cut/harvest trigger, traversable retreat, partial blockage and no-defender cases. Preserve the accepted empty-forest alarm waiver. This is a next-version encounter.

Acceptance test: The future spec defines which crown approaches are defended, with pass/fail diagrams for open terrain, pond edge, giant contact, map edge and an empty defender roster. A local placement sweep can enumerate all supported approach partitions and ordinary jobs can trigger the declared trap. Default first-version maps contain no crown prize or false-fruit ring. No automatic planetary placement is introduced.
