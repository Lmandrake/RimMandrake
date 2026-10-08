**The design is sound, but I would hold release for the planner safety defects, incomplete interaction-cell protection, and damage-event identity.** The rework fixes much of the earlier architecture; the remaining risks sit mainly in the game adapter and in guarantees the planner does not actually enforce.

This review uses only the supplied mod files. I checked current Odyssey-era engine source and exercised three small planner counterexamples in isolation. I did **not** run the DLL, the C# fuzz harness, texture previews, or `validation.py`. `Source/SelfTest/*` and `validation.py` were not inlined, so their reported results remain evidence from `REWORK.md`, not independently verified results.

## 1. **Concept review**

- **A1.1 — The central experience is strong.** Separating walkable canopy, solid ground contact, and picture-based selection gives giant plants physical presence without turning their whole image into a wall. Keeping ordinary plant jobs and plant health preserves familiar interactions.

- **A1.2 — Desired claims and realized collision are the right distinction.** A footprint can want a cell while deferring closure around occupants or infrastructure. The multi-owner ledger also gives overlapping giants sensible persistence when one is cut.

- **A1.3 — Players need to see the realized footprint.** Safety exclusions can leave substantial walkable holes inside apparently solid roots. Add a selection overlay showing solid cells and deferred cells, with a brief reason on inspection. Otherwise movement looks inconsistent.

- **A1.4 — The art measurement contains a design heuristic.** `BASE_ROWS`, `BAND_DEPTH`, closing radius, and coverage threshold infer ground contact from a projected image. Keep generated data, but require preview review: dangling lobes, shadows, and low branches can satisfy the same heuristic as roots.

- **A1.5 — Root-only solidity implements the owner’s ruling, with two consequences.** `ValidateRenderer` makes the entire species impassable at every growth stage, and the setting takes effect after restart. Document both. Also record actual root-cell coverage during measurement: zero retained non-root cells alone does not prove the art contacts the root.

- **A1.6 — The major complexity is justified; its hottest algorithm needs work.** Claims, reconstruction, and a pure kernel solve real problems. Repeated full-window floods for every candidate, followed by map-wide pending retries, are the part most likely to become over-expensive.

- **A1.7 — Canopy art should remain separate from shelter.** The current blockers deliberately provide movement obstruction and partial cover. Roof support, shade, rain shelter, fluid resistance, and fire spread should be separate opt-in mechanics with their own settings.

## 2. **Implementation review**

- **A2.1 — Structure is substantially improved.** `RM_HugeFootprintKernel` and `RM_HugeClaimsKernel` isolate decisions well; `FootprintMath` is a thin adapter. The map component now owns lifecycle and collision, while the comp supplies geometry. Namespace-scoped Harmony patching avoids the obvious double-`PatchAll` merge failure.

- **A2.2 — Save/load reconstruction is generally appropriate.** Claims and caches are derived, so they need not be scribed. `Building_TrunkBlocker.ExposeData` saves an owner reference, but reconciliation correctly reassigns ownership from claims. Map-wide indexing also catches blockers outside a plant’s current bounds.

- **A2.3 — Reconciliation still needs failure isolation.** `Reconcile` calls `Take` without the per-owner exception handling used during normal ticks. A throwing graphic or malformed extension can abort map initialization. `RealizePending` also lacks equivalent isolation around geometry and planning. Fail the affected owner safely, keep other owners operational, and retain recoverable work for retry.

- **A2.4 — The eight-refresh budget does not bound tick cost.** `RealizePending` visits every owner whenever any dirty work was processed. `RelabelOwners` then visits every realized blocker. Permanently refused claims around buildings or trees can therefore be repeatedly scanned during unrelated growth updates.

- **A2.5 — Entity count remains the principal scaling cost.** Five hundred mature elders can produce up to **59,000 blockers before overlap and safety exclusions**. Their registration, rare ticks, serialization, path changes, and region updates remain real work. RimWorld’s `PathGrid.NotifyCellDirtied` clears reachability and dirties regions when walkability changes. [Engine path-grid source](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/PathGrid.cs).

- **A2.6 — The selection cache leaves meaningful work uncached.** Every `SelectRect` call still performs `Roll`, graphic lookup, filename extraction, variant search, and a capturing delegate allocation. `GenUI.ThingsUnderMouse` scans the custom-rectangle lister and can query the getter twice per candidate. Cache stable per-position random values and graphic identities, then benchmark mouse movement through dense giant forests. [Engine mouse enumeration](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/GenUI.cs).

- **A2.7 — Plant settings are mostly well wired.** Master gates, shipped defaults, scale bounds, and asynchronous refresh are present. The damage checkbox wording conflates cover and damage: disabling it retains cover. Use “Hits on trunk cells damage the plant.” The settings text also needs translation keys.

- **A2.8 — Preserving Scribe keys does not establish settings migration.** Vanilla `Mod.GetSettings<T>` reads settings using the mod folder and concrete `Mod` class name. A merged settings tree needs an explicit migration path from the old Titanic Creatures configuration, unless another supplied part already provides it. [Engine settings loader entry point](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Mod.cs).

- **A2.9 — The measurement tool is useful but narrower than its coverage claim.** `rot_plants` detects local plants through an explicit `<plant>` element, so inherited-only plant defs can be omitted. Resolution also approximates selected patches and inheritance rather than consuming the final def database. Use RimDefDump’s resolved output as the measurement manifest, with configurable texture roots and fail-on-missing coverage.

The earlier review’s status is:

| Finding | Earlier `GPT_REVIEW.md` items | Current status |
|---|---|---|
| **A2.10** | **#1: entrapment and root access** | **Partly addressed.** Local border reachability is implemented, but existing enclosed components and corridor connectivity remain unsafe: A3.1–A3.3. The owner accepted large chain enclosures; these additional cases are distinct. |
| **A2.11** | **#2: item loss** | **Ordinary spawn wiping addressed.** Claims exclude destinations and blocker spawning checks items. Actual movement remains non-transactional, with unsafe exceptional recovery: A3.5–A3.6. |
| **A2.12** | **#3, #5, #7** | **Largely addressed in source.** Narrow zone exception, map-wide blocker indexing, exceptional spawn recording, derived bounds, and explicit draw-size restrictions are present. |
| **A2.13** | **#4: combat cover and damage** | **Forwarding implemented.** Explosion dedup uses the engine list; projectile/beam identity remains incorrect: A3.7. |
| **A2.14** | **#6: interaction cells** | **Partly addressed.** Single interaction cells and existing door approaches are considered; blueprints, frames, and multiple interaction cells need correction: A3.4. |
| **A2.15** | **#8: overlap order** | **Claim ownership addressed.** Final claims are order-independent. Realized collision can still depend on earlier safe closures; the supplied tests do not establish adapter-level permutation invariance. |
| **A2.16** | **#9: performance** | **Partly addressed.** Dirty refreshes and indexed membership help; pending realization, relabeling, initial load, and entity count remain unbounded or unbenchmarked. |
| **A2.17** | **#10, #11: topology and renderer limits** | **Still partly open.** Picture clipping and renderer checks help. Ground classification, unmeasured-state fallback, unsupported selection geometry, replacement art, and render suppression remain unresolved. |
| **A2.18** | **#12, #13: interaction contracts** | **Duplicates addressed; other issues remain.** Deterministic overlap priority is absent. Drag selection, designators, and menus were explicitly left unchanged. |
| **A2.19** | **#14, #16: refresh and caches** | **Mostly improved.** Position, scale, rect union, and RNG restoration are present. Growth notification ordering remains wrong; malformed extension handling and mutable measurement data remain gaps. |
| **A2.20** | **#15, #17: gravships and building semantics** | **Landing policy implemented; integration pending.** Partial fill and no roof support are pinned. Departure/transport, terrain changes, and shipping-build behavior still require tests. |

- **A2.21 — The test strategy has improved, but reported mutation coverage is not engine coverage.** The independent compiled-kernel oracle described in `REWORK.md` is valuable. Python expression-string checks merely detect selected edits; they cannot prove lifecycle ordering, spawn rollback, interaction-cell resolution, or combat event identity.

## 3. **Potential bugs**

**A3.1 — Giants can trap pawns inside an already enclosed component.**

- **File + symbol:** `RM_HugeClaimsKernel.cs` → `Planner.Plan`, `Reach`, `RootServed`.
- **Mechanism:** Only cells initially reachable from the window border are protected. In a sealed room, `before` is false throughout; closing exits around a pawn passes the test. Roots in that component are also omitted from `rootIdx`. Vanilla recovery concerns an unwalkable occupied cell, not an isolated walkable pocket: `Pawn_PathFollower.TryRecoverFromUnwalkablePosition` **(verify on 1.6)**.
- **Severity / confidence:** **Visible; high** for the kernel defect.
- **Fix:** Preserve connectivity within every existing passable component, including components that never reached the border. Protect existing pawn and root access explicitly. Add enclosed-room cases to the independent oracle.

**A3.2 — A single giant can disconnect two accessible areas without creating a border-isolated pocket.**

- **File + symbol:** `RM_HugeClaimsKernel.cs` → `Planner.Plan`.
- **Mechanism:** `Reach` seeds every passable border cell independently. Closing the middle of a corridor succeeds when both resulting sides still touch different borders. Actual pawn paths cannot cross the new impassable cell; `PathGrid.CalculatedCostAt` enforces that obstruction.
- **Severity / confidence:** **Visible; high**.
- **Fix:** Preserve the connectivity relationship between relevant border entrances, pawns, and work-access anchors—not merely each cell’s ability to reach *some* border. Keep the separately accepted large-chain limitation documented.

**A3.3 — Sorting the accepted cells destroys the planner’s safe execution order.**

- **File + symbol:** `RM_HugeClaimsKernel.cs` → final `accepted.Sort`; `MapComponent_HugeFootprints.cs` → `RealizePending`.
- **Mechanism:** A corridor mouth can initially be refused, then accepted after its dead-end cell closes. The final sort can put the mouth first. If the later spawn fails, an open isolated pocket remains. `GenSpawn.Spawn` performs synchronous callbacks, so failure and observation during application are possible.
- **Severity / confidence:** **Visible; high**.
- **Fix:** Return dependency-preserving acceptance order. Revalidate each closure against actual state, and stop or replan when a prerequisite fails. Test every successful prefix and injected spawn failure—not only the completed set.

**A3.4 — Interaction-cell protection misses vanilla-supported cases.**

- **File + symbol:** `MapComponent_HugeFootprints.cs` → `Flags`.
- **Mechanism:** The code reads `t.def.hasInteractionCell` and one `t.InteractionCell`. Vanilla `GenConstruct.NotBlockingAnyInteractionCells` resolves blueprint/frame `entityDefToBuild` and enumerates `ThingUtility.InteractionCellsWhenAt`, including multiple offsets. [Engine construction checks](https://github.com/Chillu1/RimWorldDecompiled/blob/master/RimWorld/GenConstruct.cs), [interaction-cell enumeration](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/ThingUtility.cs).
- **Severity / confidence:** **Visible; high**.
- **Fix:** Resolve the built def, enumerate every interaction cell, and derive the required scan bounds. Include planned door approaches and test rotated multi-cell buildings.

**A3.5 — Actual item movement can be partial or leave an item unsaved after failure.**

- **File + symbol:** `MapComponent_HugeFootprints.cs` → `MoveItems`.
- **Mechanism:** Earlier items remain moved when a later destination fails. `DeSpawn` lies outside the `try`; fallback spawning is unguarded. A second failure can leave the item unspawned and outside any persistent holder. `GenSpawn.Spawn` performs wiping and lifecycle callbacks. [Engine spawning](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/GenSpawn.cs).
- **Severity / confidence:** **Data-loss on exceptional paths; medium**.
- **Fix:** Preflight the whole source cell, preserve rotation, and use a recoverable transaction. Roll back completed moves on failure; retain any unplaced item in a scribed holding container until restoration succeeds. Replan dependent closures.

**A3.6 — A gentle item push emits real despawn lifecycle events.**

- **File + symbol:** `MapComponent_HugeFootprints.cs` → `MoveItems`.
- **Mechanism:** `Thing.DeSpawn` releases physical interaction reservations, deselects the thing, notifies storage, and emits the quest-tagged `Despawned` signal. Keeping the same `Thing` preserves its fields but does not suppress those events. [Engine despawn lifecycle](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Thing.cs).
- **Severity / confidence:** **Visible, potentially quest-state loss; high** for event emission.
- **Fix:** Defer quest-sensitive or actively interacted items. Provide a tested relocation path for eligible ordinary items, and verify hauling/reservation behavior. Avoid globally suppressing legitimate despawn signals.

**A3.7 — Damage dedup merges distinct projectiles and misses direct-root overlap.**

- **File + symbol:** `Building_TrunkBlocker.cs` → `SourceKey`, `ForwardToPlant`; `RM_HugeClaimsKernel.cs` → `DamageDedup`.
- **Mechanism:** Two projectiles from the same launcher, weapon def, and damage def landing in one tick share a key. The second legitimate hit is suppressed. Conversely, a direct hit on the plant bypasses this dedup. Each projectile is a separate engine object with its own impact lifecycle. [Engine projectile source](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Projectile.cs).
- **Severity / confidence:** **Visible; high**.
- **Fix:** Dedup by explicit event identity: projectile instance, beam application, titan step, or explosion instance. Include direct-root damage in events that can affect multiple cells. Ordinary single-impact projectiles generally need no tick-based dedup.

**A3.8 — Growth is checked before vanilla applies that tick’s growth.**

- **File + symbol:** `CompHugeFootprint.cs` → `CompTickLong`.
- **Mechanism:** `Plant.TickLong` calls `base.TickLong` before updating `growthInt`; the base dispatches `CompTickLong`. A first or isolated growth transition can therefore remain unmarked until the next long tick. [Engine plant tick order](https://github.com/Chillu1/RimWorldDecompiled/blob/master/RimWorld/Plant.cs), [comp dispatch](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/ThingWithComps.cs).
- **Severity / confidence:** **Visible; high**.
- **Fix:** Check changes after `Plant.TickLong` completes. Keep the harvest hook and cover external growth changes. Correct the outdated comment: the inspected 1.6 source also uses `Plant.TickInterval`.

**A3.9 — Unsupported renderers still receive an unsupported selection prediction.**

- **File + symbol:** `HugeThingsCore.cs` → `ValidateRenderer`; `CompHugeFootprint.cs` → `Signature`, `SelectRect`.
- **Mechanism:** Validation disables blocking only. Selection still predicts one vanilla quad and may use a measured crop for a multi-mesh plant or custom `Print` override. That rectangle need not contain the actual render.
- **Severity / confidence:** **Visible; high**.
- **Fix:** Track selection support separately. Supply a renderer-specific bounds adapter, or retain vanilla selection with a clear diagnostic. Do not promise whole-picture coverage for a rejected rendering contract.

**A3.10 — Unknown graphic states create invented collision.**

- **File + symbol:** `Extensions.cs` → `Union`, `MaskFor`; `CompHugeFootprint.cs` → `DrawnVariant`.
- **Mechanism:** An unmeasured graphic receives the union of mature contact cells. `Plant.Graphic` can switch to immature, leafless, or polluted art whose ground contact differs. The current renderer validation does not reject this fallback.
- **Severity / confidence:** **Visible; high** for fallback behavior, **medium** for shipped visual mismatch.
- **Fix:** Measure supported alternate states. Until then, use a reviewed fallback policy—preferably selection-only for unknown art—and warn once per def/state. This remains an unresolved `REWORK.md` decision.

**A3.11 — Pending realization can defeat the refresh budget.**

- **File + symbol:** `MapComponent_HugeFootprints.cs` → `MapComponentTick`, `RealizePending`, `RelabelOwners`.
- **Mechanism:** Any processed dirty owner triggers a pass over all owners and pending claims. `Planner.Plan` repeatedly allocates flood buffers; realized blocker relabeling also runs globally. The tick manager receives all this work synchronously.
- **Severity / confidence:** **Visible stalls; high** for unbounded work, **medium** for practical stall magnitude.
- **Fix:** Maintain owners with pending work, schedule bounded owner transactions independently, back off unchanged protected cells, and relabel only ownership changes. Budget initial reconciliation separately.

**A3.12 — Malformed opt-in data can escape validation and fail startup or planning.**

- **File + symbol:** `Extensions.cs` → `ConfigErrors`; `HugeThingsCore.cs` → `ValidateRenderer`; `CompHugeFootprint.cs` → `MaxKeys`.
- **Mechanism:** Null variants/contact lists are dereferenced. Config errors do not enforce runtime rejection, and actual draw/window dimensions remain insufficiently bounded. Invalid or enormous values can reach allocation and iteration.
- **Severity / confidence:** **Crash; medium**, conditional on another mod supplying malformed data.
- **Fix:** Validate an immutable runtime descriptor before opting in. Reject nonfinite dimensions, null entries, invalid contact coordinates, and excessive window area; disable the affected footprint safely while continuing startup.

## 4. **Unforeseen challenges + mitigations**

- **A4.1 — Dense forests will expose the entity model’s cost.** Benchmark sparse and dense existing maps, cold load, save size, mass cutting, settings changes, and mouse movement. Record worst tick duration and allocations, alongside average TPS.

- **A4.2 — Realized geometry can retain historical choices.** Earlier closures constrain later overlapping plants; reconstruction can choose different safe holes. Specify whether history-dependent collision is acceptable, then test registration, refresh, and save/load permutations at the adapter level.

- **A4.3 — A 600-mod list will contain patched vanilla renderers.** Checking `Print.DeclaringType` does not detect Harmony changes to `Plant.Print`. Add renderer capability diagnostics and capture actual vertices/material/UVs in an integration probe.

- **A4.4 — Texture replacement can silently invalidate masks.** Filename and draw size can remain unchanged while the art changes. Store full asset path, measurement version, and texture hash in generated data; diagnose mismatches.

- **A4.5 — Snow, sand, fog, and frozen water complicate visible selection.** Confirm `SectionLayer_Things` eligibility and plant overlays on the installed build **(verify on 1.6)**. Define whether physically present but visually suppressed plants retain expanded click rectangles.

- **A4.6 — Flight requires a deliberate ground-obstacle policy.** In 1.6, flying path grids bypass an impassable thing only when `forcePassableByFlyingPawns` permits it. This blocker leaves that flag false. Classify low roots versus tall trunks explicitly and test flight using vanilla `MaxFlightTime`. [Flight-aware path costs](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/PathGrid.cs), [flag default](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/BuildableDef.cs).

- **A4.7 — Stockpile capacity is not item-specific suitability.** `Capacity` does not check the moved item’s storage filter, footprint, or specialized container behavior. Make destination validation item-aware, and defer incompatible items.

- **A4.8 — Terrain and external construction can invalidate retained blockers.** `Take` revisits desired geometry, but retained cells receive no renewed suitability check. Subscribe to relevant local changes or audit affected cells gradually; avoid scanning whole maps.

- **A4.9 — Gravship departure deserves its own test matrix.** The supplied landing policy is clear. Verify `GravshipPlacementUtility.ClearArea` argument semantics, departure, owner transport, and blocker transport on the installed DLL **(verify on 1.6)**. Treat blockers as derived state across transport.

- **A4.10 — Raids need a credible response to giant obstacles.** Non-targetable blockers cannot serve as ordinary attackable walls. Route relevant obstacle decisions to the owner plant; test sappers, melee attacks, fire, and movement beneath canopies.

- **A4.11 — Root access is not identical to workable colony access.** An open adjacent cell may be outside a pawn’s permitted area or reachable only from the wrong side of an obstruction. Show unreachable cut/harvest status and provide an owner-aware work-access diagnostic.

- **A4.12 — The mask tool needs portable inputs.** Its hardcoded WSL workshop path fails on other layouts. Add explicit donor/content-root arguments, a resolved-def manifest, and reproducible dependency versions.

## 5. **Opportunities to leverage**

- **A5.1 — Expose distinct geometry queries.** Offer `DesiredGroundCells`, `RealizedGroundCells`, `PictureBounds`, and `OwnersAtCell`; consumers should choose the geometry matching their mechanic.

- **A5.2 — Emit small lifecycle events.** Notify footprint growth, shrinkage, deferred closure, owner damage, and removal with changed cells. Other mods can react locally.

- **A5.3 — Add a player-facing footprint overlay.** Color solid, proposed, and deferred cells; explain the reason a cell remains open.

- **A5.4 — Add an author diagnostic report.** List renderer support, alternate graphics, texture identity, root-only classification, maximum window area, and predicted blocker count.

- **A5.5 — Generalize cell claims carefully.** A separate claim service could support rooted anomalies, immobile organisms, and irregular obstacles while keeping plant assumptions out of the generic API.

- **A5.6 — Resolve trunk interactions to the plant.** Owner-aware targeting could support trunk damage, cutting, inspection, and compatible designators consistently across the footprint.

- **A5.7 — Provide mass-aware harvesting.** A configurable work curve based on plant size or realized trunk area would make giant timber feel substantial while retaining familiar products.

- **A5.8 — Add repeatable engine probes.** Capture actual rendering, placement effects, damage-event identity, and zone preservation into a compact report that complements kernel fuzzing.

## 6. **Extensions WELL beyond the mod**

Each major mechanic below should have its own toggle and meaningful tuning. Habitat content should be placed on maps or through authored save content.

- **A6.1 — TheRot: a falling elder opens the forest.** Cutting or titan-smashing an elder exposes a scavenging site and releases a locally configured spore event; reuse owner removal and changed cells.

- **A6.2 — ExplosiveGrowth: visible swelling with consequences.** Soaking accelerates footprint growth; deferred cells show where items or infrastructure prevent closure. Explosive failure can clear a route through the resulting thicket.

- **A6.3 — FlowWorks: roots resist different fluids.** Realized trunk cells contribute configurable resistance rather than automatic watertightness. Water erosion shrinks roots; oil pooling increases fire risk.

- **A6.4 — FloodedCanyon: upstream debris catches.** Giant roots collect floodborne wreckage and salvage. A blocked channel raises local pressure until debris is cleared or the plant breaks.

- **A6.5 — OasisMaker: place water where giants can survive.** Show soil, water, canopy, and future footprint together when choosing an oasis site; mature plants provide shade through a separate mechanic.

- **A6.6 — SolarMirrors: steer giant growth.** Redirected sunlight changes vanilla temperature and plant growth, gradually opening or closing passages. Feed heat into ordinary temperature and heatstroke.

- **A6.7 — MovingDunes: buried roots and revealed routes.** Sand accumulation conceals low contact art while trunks remain obstacles; erosion reveals forgotten paths and items lodged among roots.

- **A6.8 — FeverWood and Webwork: living passageways.** Map-local growth events constrict wet forest routes over days. Players maintain access by pruning selected plants rather than clearing whole forests.

- **A6.9 — Miasma and TerminalBiomes: rooted aquatic landmarks.** Mangrove bases and giant aquatic fungi obstruct chosen movement modes while fluid and hazard systems remain independently configured.

- **A6.10 — RM_SeabedLayer: underwater giant groves.** Sea-floor plants offer salvage routes, collection sites, and creature ambush cover. Keep every ledger attached to its actual `Map`; coordinates alone must not identify the layer.

- **A6.11 — Gravship landing: preserve or clear an ancient grove.** Preview intersecting giant owners before landing. A quest can reward landing outside a sacred grove and approaching its research target on foot.

- **A6.12 — AcousticScanner: hear the roots below.** Sounding reveals concealed root extent, hollow chambers, or salvage lodged beneath an elder; discoveries become local map targets.

- **A6.13 — KeelHoist and Deep Diving: reach isolated specimens.** A hoist lowers workers into inaccessible giant-root pockets; underwater excursions gather samples from their sea-floor counterparts.

- **A6.14 — CreatureBehaviors: animals choose canopy habitat.** Shelter-seeking animals rest beneath suitable canopies and nest near trunks. Each species keeps one biome unless migration or life stage explains otherwise.

- **A6.15 — HostileFlora: rooted threats with vulnerable parts.** Extend owner-backed targeting to anchored hostile organisms: exposed roots take damage that disables a stalk, feeding organ, or defensive attack.

- **A6.16 — Watchers: peek around trunks.** Watchers use nearby trunk edges as observation positions. Movement collision and partial cover provide different inputs to their behavior.

- **A6.17 — Titanic creatures: reliable crossing routes.** Titans repeatedly using a path leave durable gaps in a grove; plants reclaim the route gradually. Make route persistence separate from immediate smash damage.

- **A6.18 — Conservation quests.** Protect a named elder from fire, a titan, or a timed harvest party. Success checks the owner plant’s survival and health, never the survival of proxy blockers.

- **A6.19 — Rescue quests.** A caravan shelters beneath a giant cap while hostile creatures circle outside. Players choose between pruning a route, fighting through, or using another local entrance.

- **A6.20 — Factions: woodland custodians and timber contractors.** Persistent NPCs from Inhabited can own particular groves; agreements authorize harvesting selected owners or maintaining access paths.

- **A6.21 — RimProperty: property follows the organism.** Root harvesting, tapping, and damage resolve to the owner plant’s claim. Proxy blocker interactions must not create independent theft or destruction events.

- **A6.22 — Ideology: ancient-grove stewardship.** Precepts distinguish pruning, sustainable harvest, and destroying mature giants. Rituals occur at reachable perimeter positions and recognize a named elder.

- **A6.23 — Items: taps, braces, and surveying stakes.** Taps collect sap over time; braces modify a configured damage response; stakes display a plant’s potential footprint before cultivation.

- **A6.24 — Traces and Aftermath: forests remember combat.** Owner damage produces scars; titan passages and felled elders become recorded battle changes with persistent local traces.

- **A6.25 — Graffiti and LoreStages: marks on living landmarks.** Attach inscriptions and staged descriptions to the plant owner. Growth or variant changes reposition their presentation without losing the recorded story.

- **A6.26 — Wreckage and WreckedMachines: salvage trapped in roots.** A giant grows around an ancient machine; pruning exposes components while machinery failure threatens the grove.

- **A6.27 — EnvironmentalHazards: hazardous canopy regions.** Opted-in plants emit spores, dripping chemicals, or static around their canopy. Keep hazard area, solid ground contact, and plant selection independent.

- **A6.28 — Incidents: root heave and canopy collapse.** A localized event changes selected owners’ health or growth, moves eligible loose items through the safe relocation service, and exposes a temporary work site.

- **A6.29 — StructureInjections: authored giant-root ruins.** Map structures place giant plants with reviewed passage geometry around an observatory, shrine, or flooded ruin; placement validates access before realizing blockers.