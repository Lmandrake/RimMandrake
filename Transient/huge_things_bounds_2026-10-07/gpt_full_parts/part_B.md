The merge is sound, but the titan half is not ready to close against the owner’s rulings. The main blockers are unsafe corpse conversion, destruction that cannot reliably clear a blocked route, and Large Pawns remaining a second destruction authority.

This is a static review of the supplied files; no game or selftests were run. Engine checks used a decompile whose [assembly metadata identifies RimWorld 1.6](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Properties/AssemblyInfo.cs). Large Pawns details rely on the supplied decompile findings; its installed runtime remains unverified.

## 1. **Concept review**

- **B1.1 — Merge: keep it.** One package, one settings tree, preserved namespaces/defNames, and one owner for plant-versus-titan interactions are sensible. Separating drawn selection size from physical mass is also correct: those measurements solve different problems.

- **B1.2 — The closed item overstates completion.** Thick-roof avoidance is explicitly replaced by slowing; reliable wall/plant breakthrough is missing; corpse camps and scavenger draw are absent. The provided code also contains no footfall presentation, spacing enforcement, or biome/event admission machinery. Distinguish binding card requirements from later design candidates, and reopen the unmet requirements.

- **B1.3 — “Smash through” currently means “damage while passing nearby.”** A titan can incidentally destroy a fungus while taking an available detour. It cannot reliably destroy the obstacle that prevents it obtaining a route. This is the central weakness of the merge seam.

- **B1.4 — Optional Large Pawns is a reasonable degradation, but changes the experience substantially.** Without it, even a body-size-40 titan has a one-cell ordinary wake. Its selection rectangle conveys enormous size while its destructive contact remains tiny. Describe that limitation clearly and validate the owner’s intended experience with Large Pawns enabled.

- **B1.5 — Friendly titans need readable consequences.** Colony ownership deliberately grants no protection from wake damage. That is consistent with the ruling, but players need a visible tier, footprint, destruction warning, and sufficiently wide husbandry routes before taming becomes a costly surprise.

- **B1.6 — Corpse harvesting needs more player control.** Automatic Mining work, one reservation, and a fixed batch size produce a repeated mining task rather than a managed expedition. Add harvest/pause control, useful remaining-work estimates, and a deliberate way to abandon the remains.

- **B1.7 — The corpse’s economic clock is weakly connected to the setting.** Daily percentage spoilage ignores freezing, refrigeration, exposure, and the frozen-world context. A bespoke pool clock is acceptable, but explain it as scavenging/degradation or make vanilla temperature influence actual spoilage.

- **B1.8 — Two tuning claims are misleading.** The yield curve jumps upward at T2, and untouched sites do not generally disappear in “roughly a week.” Before integer rounding, seven days leave about 32% of meat and 56% of leather at the defaults.

- **B1.9 — The implementation is mostly appropriately small.** Event-driven wake processing, declarative crush rules, and pure kernels are good choices. The invasive Large Pawns settings rewrite is the part most likely to require substantial maintenance.

## 2. **Implementation review**

- **B2.1 — The kernel boundary is useful but incomplete as a verification boundary.** Tier arithmetic, gates, and owner deduplication belong in pure C#. Fuzzing those functions cannot establish that a blocked titan ever reaches the movement hook, that corpse replacement is safe, or that an engine setting takes effect.

- **B2.2 — Wake cost is local, but allocation-heavy.** With the stated Large Pawns ceiling, ordinary processing visits at most 16 cells per move. Each cell allocates a `ToList()` snapshot; smashing adds a dictionary, lists, and a hash set. Gather unique targets once per step using reusable or pooled collections, with protection against nested damage callbacks.

- **B2.3 — Giant-query scaling remains unverified here.** `SmashGiantPlants()` requests a small rectangle, but `MapComponent_HugeFootprints.SolidCellsIn()` was not supplied in this part. Confirm it uses a spatial lookup; scanning every registered giant per moving titan would defeat the local-cost design.

- **B2.4 — The broad movement hook has avoidable overhead.** `Patch_Thing_Position_Wake.Postfix()` probes comps on every spawned pawn position assignment, including when giant animals are disabled. Check the wake gate first and capture whether the position actually changed.

- **B2.5 — The harvest job’s basic persistence is sound.** `workLeft` is scribed, and the toil uses elapsed `delta` for both work and experience. Do not assume its `initAction` automatically resets work on reload: `JobDriver.ExposeData()` reconstructs toils through `SetupToils()`, separately from starting the next toil. Verify an actual mid-session save/load. [1.6 JobDriver](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse.AI/JobDriver.cs)

- **B2.6 — Roof documentation contains a significant engine error.** The route-versus-step-cost distinction is correct, but the claimed 40-hour freeze is not supported by this 1.6 implementation. `Pawn_PathFollower.CostToPayThisTick()` enforces a minimum payment of `nextCellCostTotal / 450`; raising the returned cost to 100000 does not itself create a 100000-tick step. The current 2000 also does not mean a 2000-tick step. [1.6 Pawn_PathFollower](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse.AI/Pawn_PathFollower.cs)

- **B2.7 — Def authoring needs validation.** Add `ConfigErrors()` for finite, increasing tier thresholds; exactly one crush selector; valid minimum tiers; and duplicate exact-def rules. Category rules need explicit priority or specificity rather than first-loaded precedence.

- **B2.8 — “Restart” settings should behave consistently.** Thresholds affect runtime tiering immediately, while comp injection and Large Pawns reconciliation remain startup decisions. Freeze the effective ladder until restart, or implement complete reconciliation. Display effective versus pending values.

- **B2.9 — Preserving field keys does not migrate separate settings files.** The merged class no longer reads the former Titanic settings file automatically. The design measured no files on the owner’s machine, so this is not an immediate local blocker; previously deployed configurations still need an explicit migration policy.

- **B2.10 — Namespace preservation helps save compatibility, but proves only part of it.** Retaining saved type names and defNames is correct. The supplied part cannot verify `HugeThingsStartup.PatchNamespace()`, assembly contents, comp-injection ordering relative to pawn-creating mods, or absence of duplicate patches. Those remain cold-load checks.

- **B2.11 — The walk’s obstacle expectations need correction.** The open wall lines invite detours, while fully blocked lanes may never trigger the wake. A mining-capable pawn must perform the corpse session; a generic hauler is insufficient. The documented “crates” are shelves, and the current table does not crush their item stacks.

## 3. **Potential bugs**

### B3.1 — Corpse destruction occurs inside unfinished death handling

**File + symbol:** `Patch_CorpseSiteConversion.cs:Patch_Corpse_SpawnSetup_TitanicSite.Postfix`; `TitanicCorpseSiteUtility.cs:ConvertToSite`  
**Severity:** crash/data-loss. **Confidence:** high for invalid lifecycle; medium for a particular crash.

`Pawn.Kill()` continues using its corpse after placement, including reservation, forbidding, fire transfer, and rot handling. Conversion destroys that object during its nested `SpawnSetup()` call. The caller then resumes with a destroyed corpse. [1.6 Pawn.Kill](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

**Fix:** enqueue conversion for a later main-thread tick, after death/placement completes. Revalidate the corpse, map, eligibility, and settings before conversion; deduplicate queued entries.

### B3.2 — Conversion destroys identity, equipment, and resurrection state

**File + symbol:** `TitanicCorpseSiteUtility.cs:ConvertToSite`  
**Severity:** data-loss. **Confidence:** high.

`corpse.Destroy()` is not merely removal from the map. `Corpse.Destroy()` clears its inner container and invokes `PostCorpseDestroy()`, which destroys held equipment/inventory/apparel and notifies health and ideology systems. The site retains only a label and two resource counters. [1.6 Corpse.Destroy](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Corpse.cs)

**Fix:** preserve the corpse in a scribed `ThingOwner` with a proper `IThingHolder` implementation, and define when harvesting makes destruction final. Explicitly support or exclude resurrection-sensitive and humanlike corpses.

### B3.3 — Failed site placement loses the corpse; successful placement can erase protected structures

**File + symbol:** `TitanicCorpseSiteUtility.cs:ConvertToSite`; `RM_TitanicCorpseSite.xml`  
**Severity:** data-loss. **Confidence:** high.

The corpse is destroyed before the 4×4 spawn succeeds. `GenSpawn.Spawn()` rejects an out-of-bounds occupied rectangle and returns null. `VanishOrMoveAside` also performs ordinary spawn wiping, outside the crush table. The site defaults to an edifice because `BuildingProperties.isEdifice` defaults true. [1.6 GenSpawn](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/GenSpawn.cs), [BuildingProperties](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/BuildingProperties.cs)

**Fix:** preflight the entire footprint and every wipe conflict. Find a safe nearby location or retain the corpse. Make replacement transactional, check the spawn result, and never wipe a protected structure to make room.

### B3.4 — Impassable obstacles prevent the wake that would destroy them

**File + symbol:** `TitanicWakeProcessor.cs:ProcessFootprint/SmashGiantPlants`; `Patch_Thing_Position_Wake.cs:Postfix`  
**Severity:** visible. **Confidence:** high.

Ordinary path requests can fail reachability before movement. Impassable trunks and walls therefore prevent the position assignments that drive destruction. An available detour need not hug the obstacle, either. [1.6 PathRequest.ValidateInt](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/PathRequest.cs)

**Fix:** add a deliberate obstacle-clearing action before movement: approach an eligible blocker, apply timed curated blows, wait until clearance exists, then repath. Integrate route/reachability decisions with that capability. Never physically enter an uncleared footprint.

### B3.5 — Titans still enter overhead mountain

**File + symbol:** `Patch_ThickRoofAvoidance.cs:Postfix`  
**Severity:** visible. **Confidence:** high.

`CostToMoveIntoCell()` affects movement along a selected path, not route exclusion. It also checks only the anchor cell, allowing a multi-cell titan’s edge beneath rock.

**Fix:** supply footprint-aware roof exclusion before search. A concrete 1.6 integration point to evaluate is the per-request `providerCost` array after `PathGridDoorsBlockedJob.Execute()`; `PathFinderJob.IndexCost()` treats `ushort.MaxValue` as impassable. Compose existing restrictions, cache roof exclusion data, and handle already-invalid starting positions. A large soft avoidance cost cannot guarantee “never.” [PathGridDoorsBlockedJob](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/PathGridDoorsBlockedJob.cs), [PathFinderJob](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/PathFinderJob.cs)

### B3.6 — Multi-cell things receive multiple blows in one step

**File + symbol:** `TitanicWakeProcessor.cs:ProcessCrushables`  
**Severity:** visible. **Confidence:** high.

`ThingGrid.Register()` registers a multi-cell building in every occupied cell. Processing each titan cell independently can hit the same surviving building repeatedly. A T2 overlap covering four cells can deal 240 damage rather than one 60-damage pass. [1.6 ThingGrid.Register](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/ThingGrid.cs)

**Fix:** deduplicate ordinary crush targets across the entire step before damage. If area-proportional damage is intended, calculate and expose it explicitly.

### B3.7 — Assigning the existing position produces a false movement event

**File + symbol:** `Patch_Thing_Position_Wake.cs:Postfix`  
**Severity:** visible. **Confidence:** high.

`Thing.Position` returns early when the assigned value equals its current position. A Harmony postfix still executes after that return, so another mod’s redundant assignment can trigger damage and rubble without movement. [1.6 Thing.Position](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Thing.cs)

**Fix:** capture the previous position/map in prefix state; process only a real change on the same spawned map. Define teleport behavior separately.

### B3.8 — Flying titans crush ground objects

**File + symbol:** `CompTitanicWake.cs:Notify_EnteredCell`; `TitanicWakeProcessor.cs:ProcessFootprint`  
**Severity:** visible. **Confidence:** high.

The wake checks spawning and tier, but not 1.6’s `Pawn.Flying` state. Position changes during flight therefore damage ground plants/buildings and create ground rubble. [1.6 Pawn.Flying](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

**Fix:** suppress ground-contact effects during flight. Add a separate, deliberate landing effect if desired; retain vanilla flight through `MaxFlightTime`.

### B3.9 — Rotten or scaria-affected corpses can become fresh harvest pools

**File + symbol:** `Patch_CorpseSiteConversion.cs:Postfix`; `TitanicCorpseSiteUtility.cs:ConvertToSite`; `Building_TitanicCorpseSite.cs:SpawnSetup`  
**Severity:** visible. **Confidence:** high.

Conversion accepts any newly spawned T3 corpse and starts a new spoilage clock. Dropping an old rotten corpse can therefore create fresh meat. Immediate conversion also precedes `Pawn.Kill()`’s post-placement scaria/toxic rot handling.

**Fix:** defer conversion as in B3.1; then evaluate `CompRottable`, death age, and relevant eligibility. Carry the existing decay state into the pool and do not grant edible meat from ineligible remains.

### B3.10 — T3 conversion drops additional butcher products

**File + symbol:** `TitanicCorpseSiteUtility.cs:ConvertToSite`  
**Severity:** data-loss. **Confidence:** high for declared extra products.

The utility promises exact vanilla yield but copies only meat and leather. `Pawn.ButcherProducts()` also includes base butcher products and life-stage body-part products; modded races can add further outputs. [1.6 Pawn.ButcherProducts](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

**Fix:** use a scribed product-pool abstraction with an explicit supported extraction contract. At minimum, preserve declared extra products and exclude unsupported races from automatic conversion. Avoid blindly enumerating arbitrary butcher iterators at death, since they can have side effects.

### B3.11 — Failed product placement silently consumes yield

**File + symbol:** `Building_TitanicCorpseSite.cs:HarvestOneSession`; `JobDriver_HarvestTitanicCorpse.cs:MakeNewToils`  
**Severity:** data-loss. **Confidence:** high.

The pool is decremented—and possibly the site destroyed—before `GenPlace.TryPlaceThing()` succeeds. Placement can return false after partial placement, leaving an unspawned remainder that the driver abandons. [1.6 GenPlace.TryPlaceThing](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/GenPlace.cs)

**Fix:** retain pending products in a scribed holder and retry placement, or commit only quantities actually delivered. Preserve partial remainders. Oversized output alone is not the bug: vanilla placement can split stacks.

### B3.12 — Missing yield defs create harvest jobs that extract nothing

**File + symbol:** `Building_TitanicCorpseSite.cs:ExposeData/HasYield/HarvestOneSession`  
**Severity:** visible. **Confidence:** high when a referenced def disappears.

`Scribe_Defs.Look()` can leave a removed meat/leather def unresolved while its saved counter stays positive. `HasYield` remains true, but harvesting never decreases that pool because its def is null.

**Fix:** reconcile counters and definitions during `PostLoadInit`, report invalid pools, and exclude them from available work. Destroy an empty site or preserve unresolved pool metadata for later recovery.

### B3.13 — Disabling the corpse feature does not stop existing corpse mechanics

**File + symbol:** `Building_TitanicCorpseSite.cs:TickRare`; `WorkGiver_HarvestTitanicCorpse.cs:HasJobOnThing`; `JobDriver_HarvestTitanicCorpse.cs:MakeNewToils`  
**Severity:** visible. **Confidence:** high.

`CorpseSiteActive` gates only conversion. Existing buildings keep ticking, miners keep receiving jobs, and running jobs keep extracting after the feature or animal master is disabled.

**Fix:** implement an explicit transition policy. A graceful policy can stop conversion, pause decay, and allow clearly labelled recovery of existing yield; restoring ordinary corpses requires preserved bodies and accounting for already-extracted resources. Wire the selected policy into all three symbols.

### B3.14 — The yield curve jumps upward at T2

**File + symbol:** `YieldCurveUtility.cs:SubLinearFactor`; `RM_TitanicKernel.cs:YieldFloor`  
**Severity:** visible. **Confidence:** high.

Immediately below body size 8, the multiplier approaches `sqrt(4/8) ≈ 0.707`; at T2 it resets to `sqrt(8/8) = 1`. An arbitrarily small size increase produces roughly 41% more yield.

**Fix:** use a continuous curve anchored at T1, or offset successive curve segments so they meet at tier boundaries. Test continuity, monotonicity, and configured floor behavior.

### B3.15 — Large Pawns retains uncurated wall breaking

**File + symbol:** `LargePawnsBridge.cs:TryReconcile`  
**Severity:** visible. **Confidence:** high for missing enforcement; medium for runtime impact.

The supplied owner item requires disabling Large Pawns’ `PathClearingUtility` switches. The bridge writes thresholds and override rows only. Its independent movement patches may destroy objects that this mod protects, including while Huge Things’ wake is off.

**Fix:** resolve and disable the three clearing controls using the verified installed API, with diagnostics and explicit ownership. Implement B3.4 as the curated replacement; simply disabling the other clearing mechanism exposes the blocked-route problem.

### B3.16 — Bridge failure leaves a partially rewritten configuration

**File + symbol:** `LargePawnsBridge.cs:TryReconcile/SetFloatField/PushOverrideRows`  
**Severity:** visible. **Confidence:** high.

Mutations occur before all fields, row members, and `NotifyEdited()` are validated. A later exception leaves earlier edits applied. Missing override support merely warns; missing notification silently skips refresh; the success message can still claim reconciliation. The catch’s “untouched ladder” claim is false.

**Fix:** validate the complete integration first, snapshot affected values/rows, apply atomically, and roll back on failure. Require refresh support before claiming success.

### B3.17 — Large Pawns overrides can disagree with runtime tiers

**File + symbol:** `LargePawnsBridge.cs:PushOverrideRows`; `TitanicTierUtility.cs:GetTier`  
**Severity:** visible. **Confidence:** high for the structural mismatch.

Unowned Large Pawns override rows remain authoritative ahead of thresholds. Explicit force-in rows also fix size from race base size, while wake tier uses current pawn size. A juvenile can therefore retain an adult footprint while having a lower or absent wake tier.

**Fix:** define one shared instance-level footprint policy. Audit conflicting rows, and represent force-in as a minimum footprint combined with current tier rather than always pinning adult size. Use a verified resolver hook if the external override format cannot express that.

### B3.18 — Comp qualification misses races that grow beyond their base size

**File + symbol:** `TitanicTierUtility.cs:DefQualifies`; `RM_TitanicKernel.cs:DefQualifies`; `RM_TitanicCreaturesMod.cs:InjectWakeComps`  
**Severity:** visible. **Confidence:** high for life stages above factor 1; medium for modded size changes.

The qualification check tests only base size. A below-threshold race with a sufficiently large life-stage factor can acquire a runtime tier without the comp required to trigger its wake.

**Fix:** inspect the maximum declared life-stage factor during qualification. For unpredictable size-changing mods, make the movement hook capable of checking current tier without depending exclusively on startup comp eligibility.

### B3.19 — Most numeric settings lack load validation

**File + symbol:** `RM_HugeThingsSettings.cs:ExposeData`; `RM_TitanicKernel.cs:ThresholdsValid`  
**Severity:** visible; crash possible with extreme inputs. **Confidence:** high.

Only scales and smash tier are sanitized. Stale or edited settings can introduce non-finite work duration, zero extraction batches, negative damage, invalid spoilage, or invalid yield floors. `ThresholdsValid()` also accepts an infinite T3 threshold.

**Fix:** validate every numeric field on load and before committing edits. Require finite thresholds, positive work/batch sizes, and bounded damage/chance/spoilage/yield values.

## 4. **Unforeseen challenges + mitigations**

- **B4.1 — The walk can pass while breakthrough remains broken.** Add both an open-detour lane and a completely sealed lane. Assert movement and obstacle damage; merely reaching the destination proves little.

- **B4.2 — Protected objects require negative tests.** Put an exact-protected building, a protected descendant category, a chunk, a quest object, and a trunk beside crushable furniture. Repeat with Large Pawns clearing enabled and disabled.

- **B4.3 — Corpse conversion needs a lifecycle matrix.** Test hunted, burning, scaria, rotten, carried, container-held, resurrectable, equipped, map-edge, and structure-overlapping corpses; save during queued conversion and partial harvesting.

- **B4.4 — The full modlist will expose competing size authorities.** Record the effective tier, `OccupiedRect()`, external override, selection bounds, and active Harmony owners for each test pawn. Include juveniles and forced overrides.

- **B4.5 — Destruction causes secondary costs.** Roof updates, region rebuilding, explosions, haul jobs, and cleaning can dominate the wake’s own loop. Measure crowded-base transit separately from an empty-map benchmark.

- **B4.6 — Rubble density is much higher than the label suggests.** At 4×4 and 35%, each step makes 16 rolls: 5.6 expected attempts, with about 99.9% probability of at least one success. Rename the setting “chance per footprint cell,” or roll once per step/newly entered cell.

- **B4.7 — Tamed titan wandering can become continuous colony maintenance.** Show destructive status in inspection/training UI and make allowed-area planning practical. Preserve the owner’s rule that player buildings remain vulnerable.

- **B4.8 — Pens, doors, and caravans remain separate integration problems.** Test narrow exits, roping, caravan assembly, unloading, and destination arrival. A correct occupancy getter alone does not validate those workflows.

- **B4.9 — Layer transitions need destination-aware admission.** Check room, footprint, roof, and biome permissions after gravship or pocket-map arrival. Apply sea-colossus events explicitly to `RM_SeabedLayer`; do not let ordinary wildlife generation spread them across layers.

- **B4.10 — Harvest interruptions can waste substantial labor.** Work survives saving the current job, but a replaced job loses its session progress. Consider site-owned progress for long configurable sessions, especially workers repeatedly interrupted by danger or needs.

- **B4.11 — Settings ownership can persist across sessions unexpectedly.** Verify whether Large Pawns’ `NotifyEdited()` saves the rewritten values. Store provenance and restore only bridge-owned changes when relinquishing control.

- **B4.12 — Migration claims need a real old-save check.** Load one pre-merge save containing an actual corpse site and an active harvest job. Check resource counters, job-driver types, settings, and missing-reference logs—not only trunk blockers.

## 5. **Opportunities to leverage**

- **B5.1 — Add a tier/footprint inspector.** Show current body size, effective tier, physical footprint, selection bounds, and active behaviors. This serves players, validation, and compatibility diagnosis.

- **B5.2 — Expose crush-rule explanations.** A debug command answering “which rule protects or crushes this thing?” would cheaply reveal category gaps and conflicting overrides.

- **B5.3 — Emit small consequence events.** Publish successful crush, giant-plant smash, corpse creation, harvest, and exhaustion events. Other mods can react without patching the movement setter themselves.

- **B5.4 — Reuse footprint planning for placement previews.** Show whether an entrance, holding area, caravan staging point, or gravship unloading location fits the animal.

- **B5.5 — Expand the corpse pool once, generically.** Product defs, quantities, decay classes, and session costs would support chitin, bone, machine salvage, and modded products through the same job.

- **B5.6 — Use cached footprint differences.** Newly entered cells can drive trails and contact effects, reducing repeated rolls and footprint rescans. Keep repeated pressure damage as a separate deliberate behavior.

- **B5.7 — Add configurable content providers.** Corpse scavenger and camp providers can name PawnKindDefs/factions through XML, satisfying the ruling without hardcoding a particular creature or faction into the engine.

- **B5.8 — Build coherent settings presets.** “Full size consequences,” “plants and selection,” and “gentle wildlife” can set existing fields, show pending restart changes, and reduce settings-page complexity.

## 6. **Extensions WELL beyond the mod**

- **B6.1 — AcousticScanner: approaching footfalls.** A landed gravship detects increasingly strong tremors before a scripted titan arrival, giving direction and an evacuation window.

- **B6.2 — CreatureBehaviors: deliberate passage clearing.** Supply reusable titan jobs for approaching, breaking, and repathing around obstacles. Smaller tiers avoid trunks; eligible tiers clear them.

- **B6.3 — TheRot: decomposer succession.** An exhausted organic site becomes a temporary nutrient patch. Local decomposers and fungi arrive through explicit providers, with footprint claims preventing overlapping solid growth.

- **B6.4 — ExplosiveGrowth: corpse-fed growth.** Rain soaking the ground around titanic remains accelerates nearby plants’ existing growth countdowns, making harvest camps need active vegetation management.

- **B6.5 — FlowWorks: carcass obstruction.** A large corpse obstructs a channel; workers excavate a bypass or remove sections. Leave liquid movement and depth calculations in FlowWorks.

- **B6.6 — FloodedCanyon: seasonal carcass salvage.** A scripted flood carries remains onto a reachable bank. The next flood threatens the harvest operation, creating a timed logistical quest.

- **B6.7 — Stillsand: an Oommok passage forecast.** Warn that one Oommok will cross a defined corridor. Players redirect activity or clear a passage; spawn only through an explicit event outside its home biome.

- **B6.8 — LongShade: Gloomcast protection contract.** A faction pays to keep a particular grazer alive through a crossing. Letting it die offers a valuable corpse site but breaches the contract.

- **B6.9 — Scarlands: battlefield traversal.** A Totchak crosses an active battlefield, crushing curated defenses and altering the fight’s geography without becoming another indiscriminate combat damage aura.

- **B6.10 — WeepingStones: Gorrask bottleneck.** A stone-crab blocks access to a mineral seam. Players lure it away, wait for departure, or hunt it and accept a difficult excavation site.

- **B6.11 — RustCathedral/WreckedMachines: machine remains.** Giant mechanical corpses become salvage sites with components and metal pools rather than empty meat/leather sites.

- **B6.12 — AssailantSalvage: owned salvage profiles.** Curated mechanical corpse profiles yield the family’s existing salvage objects through the generic extraction pool.

- **B6.13 — Aftermath: titan-caused battle consequences.** Record destroyed fortifications and a titan’s involvement in a battle. The aftermath can distinguish combat damage from a creature’s destructive passage.

- **B6.14 — Traces: persistent evidence.** Successful wake events create tracks, crushed vegetation, and breached-wall traces. Acoustic signs can precede visible traces along an event corridor.

- **B6.15 — Inhabited: disputed harvesting rights.** Nearby persistent NPCs identify the remains as their hunt, sacred animal, or communal resource, opening negotiations around the harvest camp.

- **B6.16 — RimProperty: harvest ownership.** Resource extraction and site access use existing ownership/theft machinery; a corpse need not become universally free loot simply because it is a building.

- **B6.17 — RaidRedesigner: returning claimants.** An established NPC returns to collect an agreed share of the carcass, or disputes a previous bargain, using the persistent roster.

- **B6.18 — TheBazaar: salvage information.** Trade coordinates, carcass age, safe approaches, and predicted remaining yield as information whose reliability matters.

- **B6.19 — GravshipLanding: footprint-aware unloading.** Reserve a safe multi-cell unloading area for titans and warn when thick roofs or trunks obstruct it. Keep ground wakes inactive during flight.

- **B6.20 — KeelHoist: staged corpse extraction.** Lift harvested batches or detachable sections from inaccessible remains. Harvest progress unlocks transportable pieces instead of hoisting an entire 4×4 building.

- **B6.21 — RM_SeabedLayer: whale-fall expeditions.** A lanternwhale corpse supports a multi-day seabed harvest and decomposer succession, with layer-specific access and scavengers.

- **B6.22 — DivingInteraction: surface-to-seabed retrieval.** A quest begins with a reported sinking titan, then sends workers to a dedicated underwater pocket map to recover material before scavengers consume it.

- **B6.23 — Sea-floor construction: protected infrastructure.** Curate reefback interactions with seabed conduits, research stations, and salvage props. Protected quest machinery remains protected through the same rule resolver.

- **B6.24 — Watchers: warning behavior.** Nearby watchers retreat before heavy footfalls, giving attentive players an ecological warning before direct sight.

- **B6.25 — ShipVermin: expedition contamination.** Supplies loaded after a corpse expedition can carry configured vermin. Feed the existing infestation engine through extraction events.

- **B6.26 — HostileFlora: competing consumers.** Mobile plants converge on nutrient-rich remains and threaten workers. Their behavior consumes corpse events rather than adding another map-wide scanner.

- **B6.27 — EnvironmentalHazards: excavation hazards.** Species profiles opt into gas pockets, unstable carcass sections, or decay exposure using existing hazard components. Any heat feeds vanilla temperature and heatstroke.

- **B6.28 — Ideology: “the great remains belong to all.”** A precept rewards sharing a titan harvest and penalizes monopolizing it, using actual extracted quantities and ownership.

- **B6.29 — Ideology: funerary excavation ritual.** A colony honors a named tamed titan before harvesting. Success affects mood or relationships; preserving the original pawn enables meaningful identity.

- **B6.30 — Graffiti/SacredGraffiti/LoreStages: remembered landmarks.** Harvest camps acquire marks, memorial inscriptions, and staged descriptions reflecting the hunt, bargain, or loss.

- **B6.31 — Equipment: expedition tools.** Specialized cutting tools improve extraction speed or batch handling through a dedicated stat, with explicit tradeoffs in carried mass and maintenance.

- **B6.32 — Events: scavenger pressure with warning.** A configurable provider schedules local scavengers after a corpse appears. Announce evidence first, cap arrivals, and give players meaningful choices about protection versus abandonment.