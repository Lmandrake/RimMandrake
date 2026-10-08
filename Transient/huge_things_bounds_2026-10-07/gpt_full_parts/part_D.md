## 1. **Concept review**

**D1.1 — Keep the merge. The player-facing concept is coherent.**  
“Size changes what you can click, where you can walk, what survives passage, and how you harvest the remains” is a strong identity. Keeping `mandrake.rm.hugethings`, existing namespaces and defNames is the right packaging decision. Two masters preserve the plant-only and animal-only use cases.

This review uses the inlined files only. The rework’s reported fixes and test results are evidence of progress, not independently verified runtime results. I do **not** carry forward the older `GPT_REVIEW.md` findings as current defects where `REWORK.md` explicitly records a fix. Newly consulted engine mirrors are not pinned to your installed build; uncertain engine details below are marked **“verify on 1.6.”**

**D1.2 — “Mass has consequences” currently means several independent things; expose that clearly.**  
Plant ground contact, pawn selection bounds, Large Pawns occupancy, tier assignment and wake reach are different contracts. That distinction is sound internally, but players need an inspect summary such as **“Colossal · 3×3 footprint · crushes furniture · avoids giant trunks.”** Otherwise a fifteen-cell drawing occupying four cells looks broken.

**D1.3 — GiantSmash is a good seam, but incidental contact does not deliver deliberate breakthrough.**  
The walk plan expressly says the titan routes around an impassable trunk and damages it while brushing past. That produces occasional collateral destruction; it does not reliably produce “the mountain-sized beast pushes through the fungus.” A narrow, owner-aware clearing job would make the fantasy dependable without granting indiscriminate passage through protected obstacles.

**D1.4 — The thick-roof implementation contradicts the binding design.**  
`TITANIC_CREATURES_MOD_1.md` rules **“a titan never paths under rock.”** The current settings and walk plan instead specify slow movement beneath rock, with route choice unaware of the penalty. This needs implementation correction: hard avoidance across the footprint, with an escape policy for titans already beneath a roof.

**D1.5 — The settings are extensive, but some switches describe a different effect from the one they control.**  
`plantTrunkDamageEnabled` leaves cover active when disabled; its checkbox begins “Trunks give cover…”. Rename it to **“Trunk hits damage the plant.”** A separate cover toggle and cover-strength tuning would satisfy the major-feature contract more honestly, retaining `0.4` as the default.

Likewise, “Destruction wake off” should describe **no wake damage**, rather than “walks through everything harmlessly”; actual collision remains dependent on footprints and obstacles.

**D1.6 — Safe growth creates exceptions to physical solidity; make those exceptions understandable.**  
Deferring cells around pawns, work access and unplaceable items is a sensible gameplay compromise. However, the same species can have visibly identical trunks with different realized collision. Show desired versus realized ground cells when selected, and a short explanation such as **“Growth leaves an access gap here.”**

**D1.7 — The corpse site is the strongest campaign feature, but needs a distinct salvage experience.**  
A temporary landmark that demands labour before resources spoil fits a scavenger clan exceptionally well. A generic rubble graphic and identical meat/leather sessions undersell it. Preserve creature identity, show the remaining work and spoilage outlook, and provide clear harvest authorization before expanding into scavenger encounters or quests.

**D1.8 — Automatic body-size tiering needs a roster audit, not a higher global threshold.**  
The shipped `4 / 8 / 20` ladder intentionally includes large vanilla creatures and the walk includes a mechanoid borehulk. Audit qualifying races for domestic animals, juveniles, machines, flyers and unusual modded races; use curated overrides for exceptions. Body size alone does not establish ground contact, edible remains or suitable destruction behaviour.

**D1.9 — The machinery is appropriately elaborate for collision safety; further generalization should follow actual consumers.**  
Claim ownership, reconciliation, transaction planning and independent geometry fuzzing solve real problems. Avoid immediately turning them into a universal framework for buildings, vehicles and moving terrain. The inexpensive next additions are diagnostics, stable queries and event notifications.

**D1.10 — The accepted enclosure limitation needs an operational remedy.**  
The owner has accepted that chains of giants can seal regions larger than any planner window. Preserve that decision. Add a warning when important access disappears and a reachable way to cut the responsible owner; do not imply the local planner guarantees colony-wide connectivity.

## 2. **Implementation review**

**D2.1 — The assembly structure is sensible; patch discovery needs a durable check.**  
`HugeThingsStartup.PatchNamespace` prevents assembly-wide double patching while preserving both Harmony IDs. Its exact namespace equality also means a future patch moved into a child namespace silently stops loading. Validate the expected target methods and patch owners, rather than relying on the number of classes processed.

**D2.2 — Def-time comp injection is the correct boundary.**  
`RM_TitanicCreaturesMod.InjectWakeComps` modifies `ThingDef.comps` before pawn creation instead of modifying live `AllComps`. The engine initializes comps in `ThingWithComps.PostMake` and again during `ExposeData` loading; this also supports existing saved pawns gaining the injected comp on reload. [Engine implementation — verify on 1.6](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/ThingWithComps.cs).

**D2.3 — Preserved names reduce migration risk, but do not establish complete save safety.**  
`GenTypes.GetTypeInAnyAssembly` supports resolving retained type names across assemblies, corroborating the packaging strategy. The omitted corpse-site and map-component code still needs review for reference resolution, comp defaults, reconciliation timing and interrupted jobs. [Type resolution — verify on 1.6](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/GenTypes.cs).

Preserving settings field names alone would not migrate an old settings **file** into the new Mod class’s file. The design measured that no such files existed locally, so this is not a demonstrated local migration defect.

**D2.4 — Staggering improves steady state; entity creation remains the expensive part.**  
The reported signature cache and eight-refresh budget address synchronized polling. They do not eliminate building registration, path-grid updates, region rebuilding, rare ticking or serialization for every blocker. Five hundred elders at 118 cells imply **59,000 blockers before overlap and safety exclusions**. Measure dense-load reconciliation, settings changes and mass growth separately from ordinary TPS.

**D2.5 — The selection postfix adds recurring allocations outside the opt-in boundary.**  
`Patch_GenUI_ThingsUnderMouse.Postfix` constructs a `HashSet` and capturing predicate for every result list containing at least two things, including ordinary scenes. Profile this with the full list; if material, use an allocation-free duplicate removal for short lists or a safely pooled set. Preserve first-occurrence ordering.

**D2.6 — Renderer rejection and functional fallback are different guarantees.**  
`HugeThingsApi.ValidateRenderer` appropriately refuses unsupported blocking. Its claim that unsupported renderers retain “whole-quad selection” needs narrower documentation: a custom renderer’s actual picture cannot generally be inferred from vanilla’s quad. Asset replacements, alternate graphics and Harmony changes to `Plant.Print` require actual renderer agreement checks.

## 3. **Potential bugs**

**D3.1 — Thick roofs remain traversable, contrary to the ruled mechanic.**

- **File + symbol:** `RM_HugeThingsSettings.cs::roofAvoidanceEnabled` and its checkbox; documented behaviour of `Titanic/Footprint/Patch_ThickRoofAvoidance.cs`.
- **Engine mechanism:** `Pawn_PathFollower.CostToMoveIntoCell` determines movement execution cost; route requests are generated separately through `PathFinder.CreateRequest`. A follower-cost patch alone cannot establish route exclusion. [Engine implementation — verify on 1.6](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/Pawn_PathFollower.cs).
- **Severity / confidence:** **Visible / high** for the documented design mismatch; exact patch wiring is omitted.
- **Concrete fix:** Reject candidate positions whose occupied footprint intersects thick roof in the actual path-search validity mechanism. Keep execution validation consistent, and allow an already trapped titan to escape.

**D3.2 — GiantSmash can stop before the plant falls.**

- **File + symbol:** `huge_titan_walk_plan_2026-10-07.md::Build notes`; movement-driven `Titanic/Wake/Patch_Thing_Position_Wake.cs` / GiantSmash integration.
- **Engine mechanism:** In normal movement, `Pawn_PathFollower.TryEnterNextPathCell` changes `Pawn.Position` after entering a cell. A stopped pawn supplies no new movement event. [Engine implementation — verify on 1.6](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/Pawn_PathFollower.cs).
- **Severity / confidence:** **Visible / high** for the movement-only limitation described by the supplied plan.
- **Concrete fix:** Add a bounded clearing job that approaches a reachable trunk edge, strikes the **plant owner** on a timed cadence and replans after destruction. Test a completely blocked destination and a titan that stops beside a surviving plant.

**D3.3 — Most loaded numeric settings bypass validation.**

- **File + symbol:** `RM_HugeThingsSettings.cs::ExposeData`.
- **Engine mechanism:** `Scribe_Values.Look` restores scalar values through `ScribeExtractor.ValueFromNode`; it does not apply the UI slider ranges. Only the two scales and smash tier are sanitized here. [Scalar loading — verify on 1.6](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Scribe_Values.cs).
- **Severity / confidence:** **Visible / high** for accepting invalid settings; downstream crash consequences are unproven without the consumers.
- **Concrete fix:** Validate every numeric field after load: finite floats, bounded probabilities and spoilage rates, positive work duration and harvest counts, and ordered tier thresholds. Reuse the same normalization before persistence and runtime consumption.

**D3.4 — Corpse-site XML creates damage-proof partial cover unless the class compensates.**

- **File + symbol:** `Defs/ThingDefs/RM_TitanicCorpseSite.xml::RM_TitanicCorpseSite`.
- **Engine mechanism:** `fillPercent=0.6` supplies partial cover; ordinary `DamageWorker.Apply` reduces health only when `useHitPoints` is true. `MaxHitPoints=9999` does not override `useHitPoints=false`. [Cover calculation](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/CoverUtility.cs), [damage application — verify on 1.6](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/DamageWorker.cs).
- **Severity / confidence:** **Visible / medium**; the omitted building class could implement resource damage explicitly.
- **Concrete fix:** Define combat damage as loss of remaining resources/site integrity, or enable finite hit points and destruction handling. If damage-proof cover is intentional, document that decision and provide an explicit removal action.

**D3.5 — Existing corpse sites may violate the animal-master “off = vanilla” promise.**

- **File + symbol:** `RM_HugeThingsSettings.cs::CorpseSiteActive`, animal-master tooltip, and `RM_HugeThingsMod.WriteSettings`.
- **Engine mechanism:** A setting boolean does not transform an already spawned building back into a `Corpse`. The visible write hook only schedules plant-footprint refresh.
- **Severity / confidence:** **Visible / medium**; omitted corpse-site code may already implement a transition.
- **Concrete fix:** Specify existing-site behaviour explicitly. The safest graceful policy is to stop new conversions while existing sites remain harvestable, with the tooltip saying so. Any reverse conversion must preserve consumed yields and corpse identity to prevent duplication.

**D3.6 — Alternate graphics can acquire collision from a different picture.**

- **File + symbol:** `RotGiants_HugeFootprint.xml::RM_PaleTree` extension; the union fallback documented in `REWORK.md::Needs owner`.
- **Engine mechanism:** The supplied 1.6 measurement confirms `Plant.Graphic` can select an immature graphic independently of the measured adult texture.
- **Severity / confidence:** **Visible / high** for the documented fallback mismatch; frequency needs a playtest.
- **Concrete fix:** Measure and identify `TreeAnima_Immature` in the generator’s inputs and regenerate the patch. For genuinely unknown graphics, use an explicit reviewed fallback policy with an inspect warning; do not silently present adult-mask collision as measured agreement.

## 4. **Unforeseen challenges + mitigations**

**D4.1 — Flight, swimming and forced displacement are not footsteps.**  
A `Thing.Position` setter patch may observe flight, knockback, teleportation and recovery as well as walking. Exercise these with ExplosiveKnockback and native 1.6 flight; suppress ground crushing and roof holing while airborne, and define separately what a displaced grounded titan should damage. Flying species should receive `MaxFlightTime` as required by the owner’s rule.

**D4.2 — Wake damage rewards unnecessary movement.**  
An animal paced repeatedly beside a structure can produce more destruction than one standing on it. Deduplicate logical steps, then use purposeful clearing attacks for sustained obstacle damage. Test oscillating paths, follow jobs and repeated position assignments.

**D4.3 — Large Pawns is both a dependency of the fantasy and an external settings owner.**  
Reflection failure can leave a destructive one-cell titan; successful reconciliation can overwrite another mod’s or the player’s configuration. Show bridge status, apply changes idempotently, disable its competing wall clearing, and make restart requirements clear. “All off” cannot promise to reverse unrelated Large Pawns behaviour.

**D4.4 — Growth can preserve items while disrupting work.**  
Despawning and respawning the same item preserves identity but may interrupt hauling, reservations and destination assumptions. Test carried-to-stockpile jobs, quest objects and custom storage together; defer movement of actively manipulated items where needed, and ensure affected jobs recover cleanly.

**D4.5 — Broad category rules have a very large blast radius on a 600-mod list.**  
`ThingCategory.Building` and the `ThingCategoryDef Buildings` hierarchy are different classifications. The supplied sandbag control demonstrates the gap. Generate a resolved census of crushable defs, unmatched expected props and important infrastructure requiring exact protection rows.

**D4.6 — Plants can provide much more effective cover than one-cell tuning suggests.**  
Several trunk cells may lie along one shot’s route, while overlapping plants share physical blockers. Test firefights through actual giant stands, including blasters, beams and explosions. Preserve the owner’s damage rule and expose cover tuning before adjusting density to solve combat balance.

**D4.7 — Corpse conversion intersects systems that expect a real corpse and pawn.**  
Resurrection, quest targets, faction ownership, corpse consumption and modded corpse comps may depend on the original object. Decide which races and death contexts qualify; retain the necessary pawn state and redirect references deliberately. A rubble building must not quietly erase a persistent character.

**D4.8 — Multi-cell logistics fail in places the showcase lanes do not exercise.**  
Test sleeping, pen gates, roping, caravan departure, map edges, gravship boarding and narrow work approaches. Large Pawns’ 4×4 occupancy also does not prove adequate transport clearance for a fifteen-cell drawing.

**D4.9 — Multi-map persistence multiplies cost and stale-reference opportunities.**  
Include surface, pocket and `RM_SeabedLayer` maps in save/load and removal tests. Scope owners, claims and effects to the actual `Map`; do not connect equal coordinates across layers or use `IntVec3.y` as layer identity.

**D4.10 — The combined walk needs adversarial scenes and an unmanaged animal.**  
Keep the clear showcase grid, then add overlapping giants, a crowded stockpile, an injured pawn, a workstation approach, a roofed corridor and a landing clipping an off-ship plant. A free-roaming titan reveals problems that a colony-owned pawn executing `Goto` will miss.

## 5. **Opportunities to leverage**

**D5.1 — Publish footprint queries.**  
Expose desired cells, realized cells and owners at a cell. FlowWorks, landing previews and hazard mods can consume one authoritative answer instead of scanning invisible buildings.

**D5.2 — Publish coarse events.**  
Offer `Footstep`, `OwnerDamaged`, `OwnerDestroyed` and `CorpseSiteCreated` notifications with map and source identity. Sibling mods can add reactions without patching the position setter again.

**D5.3 — Add a useful selected overlay.**  
Draw contact cells, accessible root-work positions and deferred cells. This supports ordinary decisions and doubles as renderer/planner diagnostics.

**D5.4 — Give the settings page a live creature census.**  
Show how many resolved races fall into each tier, with curated inclusions and exclusions. Custom thresholds become understandable before a restart changes the roster.

**D5.5 — Audit the resolved crush table in dev mode.**  
A “Why does this survive?” query should show the exact/category rule and minimum tier. This would make the sandbag discrepancy immediately comprehensible.

**D5.6 — Preserve corpse provenance.**  
Store species, source pawn identity where applicable, death cause, death location and remaining resource pools. LoreStages, Aftermath and quests gain meaningful hooks without duplicate bookkeeping.

**D5.7 — Separate automatic work from permission to harvest.**  
A per-site harvest designation or allow/forbid control prevents Mining workers from consuming a sacred specimen or quest objective automatically. The current `WorkGiverDef` assigns this to **Mining**, so the interface should not describe it as ordinary hauling.

**D5.8 — Add bounded presence effects.**  
Distance-based thuds, dust and modest camera shake can sell a titan cheaply through movement events. Aggregate effects and expose audio/shake switches.

**D5.9 — Make corpse sites resource containers with adapters.**  
Organic meat/leather can remain the default; mechanical salvage, pigment or other curated yields should be supplied by consumer extensions. Reuse sessions, spoilage and reservations without forcing every titan into the same biology.

**D5.10 — Make hazards consume owner events.**  
TheRot and EnvironmentalHazards could release spores or fumes when a giant is damaged or felled. Trigger once for the owner, avoiding one release per blocker.

**D5.11 — Reuse claim bookkeeping for static, irregular objects selectively.**  
Large crystal roots or anchored wreck appendages could share multi-owner cell claims. Their render transforms and collision rules need separate adapters; the plant transform should remain plant-specific.

**D5.12 — Improve the release report.**  
Include supported giant defs, rejected renderers, unmatched graphic variants, bridge status and crush-table coverage. These diagnostics are especially valuable when the full modlist changes the resolved defs.

## 6. **Extensions WELL beyond the mod**

The following are proposals, not claims about existing sibling-mod APIs. Keep reusable mechanics in RimMandrake; place Jawa, krayt and other Star Wars content in the campaign layer. Each new major behaviour should have its own switch and meaningful tuning, with disabled behaviour leaving existing saves usable.

**D6.1 — Jawa “salvage shadow” expedition.**  
A warned titan passage breaches a buried wreck or ruins courtyard; the clan follows after it passes to recover newly accessible components. Huge Things supplies destruction events, Wreckage owns salvage, and Traces records the route.

**D6.2 — A krayt pearl expedition with several viable outcomes.**  
The clan can kill the beast, buy access to an existing carcass, or escort expert harvesters. A campaign-defined rare yield requires a special extraction session; ordinary harvest sessions cannot generate repeated pearls.

**D6.3 — “It is coming through the market.”**  
AcousticScanner detects a titan approaching an Inhabited settlement. The quest asks the clan to evacuate traders, redirect the creature or salvage after passage, with rewards tied to people and goods actually saved.

**D6.4 — Stranded convoy behind a living barrier.**  
Extend StrandedQuest with survivors isolated by giant vegetation and a nearby titan. Cutting a reachable root, negotiating a safe extraction route or waiting for a warned breakthrough produces different rescue costs.

**D6.5 — A harvest camp rather than an instant reward.**  
A valuable corpse site supports a temporary expedition camp: storage, cooling, guards and scheduled work compete with spoilage. Quest rewards recognize extracted value, not merely killing the creature.

**D6.6 — Competing claims to a carcass.**  
RimProperty tracks who owns the site; TheBazaar negotiates harvest rights, shares or access windows. Taking resources from a rival’s claimed remains creates a concrete dispute.

**D6.7 — Old friends at the remains.**  
Inhabited supplies recognizable harvesters and RaidRedesigner supplies persistent rivals. A previous bargaining partner can arrive seeking their agreed share instead of spawning an anonymous raid.

**D6.8 — Bonewright and salvage guild content.**  
A faction specializes in processing titanic remains, selling tools and contracting guards. Its economy should consume finite site resources rather than printing goods through repeated visits.

**D6.9 — A protected giant grove.**  
A local community treats particular plants as named landmarks. LoreStages reveals their history; harvesting or landing through the grove changes relationships through actual destroyed owners.

**D6.10 — Forewarning as playable information.**  
AcousticScanner distinguishes heavy footsteps from digging machinery and moving sand. Better sounding gives earlier warnings and a probable approach corridor, enabling relocation before structures are crushed.

**D6.11 — Traces that explain events after the creature leaves.**  
Footprints, broken walls and dragged remains tell the player where a titan went. AcousticScanner and Traces can disagree plausibly when a track is old, buried or interrupted.

**D6.12 — Aftermath records collateral damage.**  
A titan crossing a battle becomes part of the battle account: breached cover, ruined stores and casualties. Subsequent salvage or compensation quests reference the recorded event.

**D6.13 — Visibility responds to conspicuous operations.**  
A noisy corpse-processing camp or titan fight temporarily raises Colony Visibility. Small, dispersed work teams trade throughput for discretion.

**D6.14 — CreatureBehaviors owns investigation and avoidance.**  
Shared behaviours can make small animals flee footfalls, scavengers approach exposed remains and territorial creatures defend specific plants. Reactions should depend on nearby events, with bounded searches.

**D6.15 — HostileFlora uses the same size language.**  
A mobile plant gets pawn selection and tiered ground effects; its stationary relatives use measured plant footprints. Explicitly define uprooting and rooting so mobile and static collision never coexist accidentally.

**D6.16 — TheRot’s decomposer titan is an ecological bridge.**  
The hwelgrue follows decomposing material and works the edges of giant fungal stands. Its curated behaviour can damage selected growth without granting every T2 titan default permission to smash giant trunks.

**D6.17 — TheRot corpse succession.**  
Abandoned titanic remains progress through scavenging, spores and fungal colonization. TheRot owns the succession and new plant spawning; Huge Things supplies remaining resources and site lifecycle events.

**D6.18 — ExplosiveGrowth turns irrigation into a spatial decision.**  
Soaked giant plants grow toward their full footprint quickly enough to threaten access lanes. Use dirty notifications to refresh growth and preview the eventual footprint before the player routes water beside camp.

**D6.19 — FlowWorks gives trunks hydraulic consequences.**  
A chosen giant species can impede or divert a channel using realized ground cells, while its cap stays irrelevant to flow. FlowWorks owns depth and routing; collision alone must not create a hydraulic dam automatically.

**D6.20 — Miasma mangal roots make readable waterways.**  
Measured root contacts create navigable gaps between enormous mangrove bodies, with FlowWorks interpreting only opted-in hydraulic roots. Harvesting a tree can open both a walking route and a channel.

**D6.21 — Greentide uses giants as temporary anchors.**  
Large rooted organisms stabilize small patches against churnmud or moving growth. The biome controls that terrain effect; the footprint identifies which cells belong to the organism.

**D6.22 — Stillsand’s Oommok exposes old salvage.**  
Its warned passage leaves a temporary corridor through moving sand, revealing wreck fragments. MovingDunes can bury the route again, creating a natural salvage deadline.

**D6.23 — Long Shade’s Gloomcast creates a moving opportunity.**  
The clan follows a home-biome grazer that opens scrub routes and exposes objects. Any cooling or shade benefit needs an explicit environmental implementation; giant artwork alone supplies neither.

**D6.24 — Scarlands’ Totchak opens dangerous wreck approaches.**  
Its passage breaches ruined structures and changes access to WreckedMachines. A newly exposed machine may still be live, so the reward is access rather than guaranteed safe loot.

**D6.25 — Rust Cathedral’s borehulk leaves a mechanical site.**  
Use a curated mechanical-remains adapter for plates, components and damaged machinery. AssailantSalvage and WreckedMachines supply appropriate salvage rather than routing the mechanoid through meat/leather harvesting.

**D6.26 — Weeping Stones’ Gorrask participates in flood events.**  
FloodedCanyon can expose or strand a stone-crab during an explicitly scripted event. Keep its ordinary home biome unchanged; the displacement provides the in-game reason for the exception.

**D6.27 — OasisMaker rewards careful giant-root placement.**  
Show root contacts and nearby terrain suitability while placing an oasis machine. If a species affects seepage or stabilization, express that through an opt-in environmental extension rather than inferring it from size.

**D6.28 — SolarMirrors creates expensive cultivation choices.**  
Directed sun can affect a suitable giant through its ordinary growth conditions. Route resulting heat through vanilla temperature and heatstroke, and show the potential mature footprint near valuable machinery.

**D6.29 — EnvironmentalHazards supplies species-specific aftermath.**  
A felled fungus might release spores; mechanical remains might leak an existing configured hazard. Huge Things dispatches one owner-level event, while the hazard kit owns exposure and mitigation.

**D6.30 — Gravship landing preview shows what will be lost.**  
GravshipLanding highlights giant owners whose root or realized blockers intersect the clear area. An edge contact should visibly mark the entire plant for removal before the landing destroys it.

**D6.31 — Titan cargo becomes a ship-layout problem.**  
Provide a loading-clearance preview for giant animals: doors, deck space, boarding route and destination disembarkation. KeelHoist can handle curated extracted cargo without implicitly transporting a whole titan.

**D6.32 — Sea-floor wreck beside living colossi.**  
On `RM_SeabedLayer`, a reefback or lanternwhale patrols its designated home waters around a Wreckage site. AcousticScanner gives advance movement information, letting the clan plan a landing and recovery window.

**D6.33 — A whale fall becomes a seabed expedition.**  
A sea-colossus death creates a species-specific harvest landmark on its own map, with underwater work access and scavenger succession. Do not apply land-style rubble trails or roof holing indiscriminately to swimming movement.

**D6.34 — Reef giants use the plant system selectively.**  
Anchored kelp holdfasts or fungal coral can opt into measured contact cells when their renderer fits the contract. DivingInteraction supplies access; broader sea-floor structures need their own geometry adapter.

**D6.35 — Surface clues lead to a lower-layer recovery site.**  
A quest supplies coordinates and acoustic evidence for remains on `RM_SeabedLayer`; the gravship flies there to investigate. Persist the specific layer and map target, rather than treating matching tile coordinates as one location.

**D6.36 — Layer-specific hazards make the same job feel different.**  
Seabed harvesting may require protected access and specialist equipment, while desert harvesting demands cooling and water logistics. Warcasket and EnvironmentalHazards can supply established protections without adding a second heat system.

**D6.37 — “Waste nothing” ideology precept.**  
A scavenger ideology values recovering a meaningful share of a titanic site before abandonment. Judge opportunities the colony actually had; inaccessible remains should not produce unavoidable mood punishment.

**D6.38 — “Leave the elder standing” precept.**  
Selected giant plants are sacred, with mood and relationship consequences for deliberate felling. Distinguish player choices from incidental damage by a wild titan.

**D6.39 — First Cut ritual.**  
A ritual at a newly claimed corpse site grants a modest, one-time harvest benefit or commemorative object. Persist completion on the site so repeat sessions cannot farm the reward.

**D6.40 — Passing-of-the-Giant memorial.**  
Graffiti or SacredGraffiti records a destroyed named giant or harvested titan. LoreStages can update the memorial as the clan learns how it lived and died.

**D6.41 — Useful scavenger tools and cargo.**  
Introduce processing winches, insulated spoilage containers and species-specific cutting tools through the campaign’s crafting content. Their bonuses affect work, preservation or access; keep the resource pool finite.

**D6.42 — Kinetic weapons offer redirection with consequences.**  
KineticArms can move smaller hazards or disrupt an approach while enormous mass limits displacement. Integrate forced-movement semantics first so knockback cannot accidentally generate a long sequence of walking crushes.

**D6.43 — StructureInjections builds encounters around access.**  
A map-generation plan can place a salvage camp, work bays and wide extraction approaches beside a chosen giant landmark. This uses map generation on the existing frozen world and needs no planet-generation changes.

**D6.44 — LoreStages and Oracle report state, not invent mechanics.**  
A named giant’s description can reflect injury, previous passage or harvest progress. Oracle may narrate those recorded facts through the established `claude -p` subprocess; deterministic gameplay systems remain responsible for the outcome.

**D6.45 — Start with three campaign integrations that exercise different foundations.**  
A warned desert salvage passage tests movement and destruction; a contested corpse camp tests resources and ownership; a seabed whale fall tests layers, landing and access. Together they reveal much more than adding another giant species alone.