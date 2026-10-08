# Huge Things — full GPT review (merged mod, 2026-10-07)

Item `HUGE_THINGS_GPT_REVIEW_1`. Owner's request (typed, 2026-10-07): *"After the mods are fully merged together and settled, then send the whole thing to GPT for a full review of the concepts, the implementation, and assessment of potential bugs, unforseen challenges to mitigate, possible opportunities to leverage, and extensions well beyond the mod for other related mods or game content."*

**How it was run.** The whole merged mod at `c954ccdca` (all 50 files of `src/RimMandrake/HugeThings` — Source, Defs, Languages, About, validation.py, measure tool, kernels, SelfTest fuzz — plus `TheRot/Patches/RotGiants_HugeFootprint.xml` and the five design docs) was sent to `gpt-6.1-sol` at high effort via `gpt_consult.py`, split into four parts sent in parallel with one shared context preamble (owner standing rules: all DLCs, Mod Settings, one heat, no worldgen; list of our 71 mods). Every file reached at least one part. Answers are kept verbatim below, numbered `<part><section>.<n>`.

**Engine citations.** GPT cited the `Chillu1/RimWorldDecompiled` GitHub mirror, which is not pinned to our build. Every bug claim that became a fix-now was re-checked against the 1.6 decompile through RimSage; see `GPT_FULL_REVIEW_TRIAGE.md` for verdicts. Treat engine links below as GPT's, not as measurements.

## Cross-part concordance (same finding, several parts)

| Theme | Findings |
|---|---|
| Smash is incidental, not a breakthrough | B1.3, B3.4, C1.3, C3.5, D1.3, D3.2 |
| Thick roof: slowing vs 'never paths under rock' | B3.5, B2.6, D1.4, D3.1 |
| Numeric settings not validated on load | B3.19, C3.6, D3.3 |
| Corpse-site lifecycle (death timing, identity, toggle-off) | B3.1–B3.3, B3.9, B3.13, D3.5, D4.7 |
| Yield curve jumps at T2 | B1.8, B3.14, C1.4 |
| Planner trapping / corridor split | A3.1, A3.2, C3.1, D1.10 |
| Life-stage size escapes comp qualification | B3.18, C3.4 |
| Flight / non-walking position changes crush ground | B3.8, C4.5, C4.6, D4.1 |
| Unmeasured alternate plant graphics | A3.10, D3.6, C2.2 |
| Settings file migration from TitanicCreatures | A2.8, B2.9, D2.3 |
| Trunk-damage checkbox wording | A2.7, D1.5 |
| Footprint overlay / queries / events | A1.3, A5.1–A5.3, B5.1, B5.3, C5.2–C5.4, D5.1–D5.3 |
| ThingsUnderMouse allocation | A2.6, C2.8, D2.5 |

## Part A — Giant-plant footprint system (core, comp, map component, trunk blocker, footprint+claims kernels, Rot patch, mask measurer) + prior REWORK/GPT_REVIEW status

**The design is sound, but I would hold release for the planner safety defects, incomplete interaction-cell protection, and damage-event identity.** The rework fixes much of the earlier architecture; the remaining risks sit mainly in the game adapter and in guarantees the planner does not actually enforce.

This review uses only the supplied mod files. I checked current Odyssey-era engine source and exercised three small planner counterexamples in isolation. I did **not** run the DLL, the C# fuzz harness, texture previews, or `validation.py`. `Source/SelfTest/*` and `validation.py` were not inlined, so their reported results remain evidence from `REWORK.md`, not independently verified results.

#### 1. **Concept review**

- **A1.1 — The central experience is strong.** Separating walkable canopy, solid ground contact, and picture-based selection gives giant plants physical presence without turning their whole image into a wall. Keeping ordinary plant jobs and plant health preserves familiar interactions.

- **A1.2 — Desired claims and realized collision are the right distinction.** A footprint can want a cell while deferring closure around occupants or infrastructure. The multi-owner ledger also gives overlapping giants sensible persistence when one is cut.

- **A1.3 — Players need to see the realized footprint.** Safety exclusions can leave substantial walkable holes inside apparently solid roots. Add a selection overlay showing solid cells and deferred cells, with a brief reason on inspection. Otherwise movement looks inconsistent.

- **A1.4 — The art measurement contains a design heuristic.** `BASE_ROWS`, `BAND_DEPTH`, closing radius, and coverage threshold infer ground contact from a projected image. Keep generated data, but require preview review: dangling lobes, shadows, and low branches can satisfy the same heuristic as roots.

- **A1.5 — Root-only solidity implements the owner’s ruling, with two consequences.** `ValidateRenderer` makes the entire species impassable at every growth stage, and the setting takes effect after restart. Document both. Also record actual root-cell coverage during measurement: zero retained non-root cells alone does not prove the art contacts the root.

- **A1.6 — The major complexity is justified; its hottest algorithm needs work.** Claims, reconstruction, and a pure kernel solve real problems. Repeated full-window floods for every candidate, followed by map-wide pending retries, are the part most likely to become over-expensive.

- **A1.7 — Canopy art should remain separate from shelter.** The current blockers deliberately provide movement obstruction and partial cover. Roof support, shade, rain shelter, fluid resistance, and fire spread should be separate opt-in mechanics with their own settings.

#### 2. **Implementation review**

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

#### 3. **Potential bugs**

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

#### 4. **Unforeseen challenges + mitigations**

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

#### 5. **Opportunities to leverage**

- **A5.1 — Expose distinct geometry queries.** Offer `DesiredGroundCells`, `RealizedGroundCells`, `PictureBounds`, and `OwnersAtCell`; consumers should choose the geometry matching their mechanic.

- **A5.2 — Emit small lifecycle events.** Notify footprint growth, shrinkage, deferred closure, owner damage, and removal with changed cells. Other mods can react locally.

- **A5.3 — Add a player-facing footprint overlay.** Color solid, proposed, and deferred cells; explain the reason a cell remains open.

- **A5.4 — Add an author diagnostic report.** List renderer support, alternate graphics, texture identity, root-only classification, maximum window area, and predicted blocker count.

- **A5.5 — Generalize cell claims carefully.** A separate claim service could support rooted anomalies, immobile organisms, and irregular obstacles while keeping plant assumptions out of the generic API.

- **A5.6 — Resolve trunk interactions to the plant.** Owner-aware targeting could support trunk damage, cutting, inspection, and compatible designators consistently across the footprint.

- **A5.7 — Provide mass-aware harvesting.** A configurable work curve based on plant size or realized trunk area would make giant timber feel substantial while retaining familiar products.

- **A5.8 — Add repeatable engine probes.** Capture actual rendering, placement effects, damage-event identity, and zone preservation into a compact report that complements kernel fuzzing.

#### 6. **Extensions WELL beyond the mod**

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

## Part B — Titanic creatures half (tiering, wake/crush, butcher yield, corpse site, roof avoidance, Large Pawns bridge) + merge design, walk plan, owner rulings

The merge is sound, but the titan half is not ready to close against the owner’s rulings. The main blockers are unsafe corpse conversion, destruction that cannot reliably clear a blocked route, and Large Pawns remaining a second destruction authority.

This is a static review of the supplied files; no game or selftests were run. Engine checks used a decompile whose [assembly metadata identifies RimWorld 1.6](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Properties/AssemblyInfo.cs). Large Pawns details rely on the supplied decompile findings; its installed runtime remains unverified.

#### 1. **Concept review**

- **B1.1 — Merge: keep it.** One package, one settings tree, preserved namespaces/defNames, and one owner for plant-versus-titan interactions are sensible. Separating drawn selection size from physical mass is also correct: those measurements solve different problems.

- **B1.2 — The closed item overstates completion.** Thick-roof avoidance is explicitly replaced by slowing; reliable wall/plant breakthrough is missing; corpse camps and scavenger draw are absent. The provided code also contains no footfall presentation, spacing enforcement, or biome/event admission machinery. Distinguish binding card requirements from later design candidates, and reopen the unmet requirements.

- **B1.3 — “Smash through” currently means “damage while passing nearby.”** A titan can incidentally destroy a fungus while taking an available detour. It cannot reliably destroy the obstacle that prevents it obtaining a route. This is the central weakness of the merge seam.

- **B1.4 — Optional Large Pawns is a reasonable degradation, but changes the experience substantially.** Without it, even a body-size-40 titan has a one-cell ordinary wake. Its selection rectangle conveys enormous size while its destructive contact remains tiny. Describe that limitation clearly and validate the owner’s intended experience with Large Pawns enabled.

- **B1.5 — Friendly titans need readable consequences.** Colony ownership deliberately grants no protection from wake damage. That is consistent with the ruling, but players need a visible tier, footprint, destruction warning, and sufficiently wide husbandry routes before taming becomes a costly surprise.

- **B1.6 — Corpse harvesting needs more player control.** Automatic Mining work, one reservation, and a fixed batch size produce a repeated mining task rather than a managed expedition. Add harvest/pause control, useful remaining-work estimates, and a deliberate way to abandon the remains.

- **B1.7 — The corpse’s economic clock is weakly connected to the setting.** Daily percentage spoilage ignores freezing, refrigeration, exposure, and the frozen-world context. A bespoke pool clock is acceptable, but explain it as scavenging/degradation or make vanilla temperature influence actual spoilage.

- **B1.8 — Two tuning claims are misleading.** The yield curve jumps upward at T2, and untouched sites do not generally disappear in “roughly a week.” Before integer rounding, seven days leave about 32% of meat and 56% of leather at the defaults.

- **B1.9 — The implementation is mostly appropriately small.** Event-driven wake processing, declarative crush rules, and pure kernels are good choices. The invasive Large Pawns settings rewrite is the part most likely to require substantial maintenance.

#### 2. **Implementation review**

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

#### 3. **Potential bugs**

##### B3.1 — Corpse destruction occurs inside unfinished death handling

**File + symbol:** `Patch_CorpseSiteConversion.cs:Patch_Corpse_SpawnSetup_TitanicSite.Postfix`; `TitanicCorpseSiteUtility.cs:ConvertToSite`  
**Severity:** crash/data-loss. **Confidence:** high for invalid lifecycle; medium for a particular crash.

`Pawn.Kill()` continues using its corpse after placement, including reservation, forbidding, fire transfer, and rot handling. Conversion destroys that object during its nested `SpawnSetup()` call. The caller then resumes with a destroyed corpse. [1.6 Pawn.Kill](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

**Fix:** enqueue conversion for a later main-thread tick, after death/placement completes. Revalidate the corpse, map, eligibility, and settings before conversion; deduplicate queued entries.

##### B3.2 — Conversion destroys identity, equipment, and resurrection state

**File + symbol:** `TitanicCorpseSiteUtility.cs:ConvertToSite`  
**Severity:** data-loss. **Confidence:** high.

`corpse.Destroy()` is not merely removal from the map. `Corpse.Destroy()` clears its inner container and invokes `PostCorpseDestroy()`, which destroys held equipment/inventory/apparel and notifies health and ideology systems. The site retains only a label and two resource counters. [1.6 Corpse.Destroy](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Corpse.cs)

**Fix:** preserve the corpse in a scribed `ThingOwner` with a proper `IThingHolder` implementation, and define when harvesting makes destruction final. Explicitly support or exclude resurrection-sensitive and humanlike corpses.

##### B3.3 — Failed site placement loses the corpse; successful placement can erase protected structures

**File + symbol:** `TitanicCorpseSiteUtility.cs:ConvertToSite`; `RM_TitanicCorpseSite.xml`  
**Severity:** data-loss. **Confidence:** high.

The corpse is destroyed before the 4×4 spawn succeeds. `GenSpawn.Spawn()` rejects an out-of-bounds occupied rectangle and returns null. `VanishOrMoveAside` also performs ordinary spawn wiping, outside the crush table. The site defaults to an edifice because `BuildingProperties.isEdifice` defaults true. [1.6 GenSpawn](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/GenSpawn.cs), [BuildingProperties](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/BuildingProperties.cs)

**Fix:** preflight the entire footprint and every wipe conflict. Find a safe nearby location or retain the corpse. Make replacement transactional, check the spawn result, and never wipe a protected structure to make room.

##### B3.4 — Impassable obstacles prevent the wake that would destroy them

**File + symbol:** `TitanicWakeProcessor.cs:ProcessFootprint/SmashGiantPlants`; `Patch_Thing_Position_Wake.cs:Postfix`  
**Severity:** visible. **Confidence:** high.

Ordinary path requests can fail reachability before movement. Impassable trunks and walls therefore prevent the position assignments that drive destruction. An available detour need not hug the obstacle, either. [1.6 PathRequest.ValidateInt](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/PathRequest.cs)

**Fix:** add a deliberate obstacle-clearing action before movement: approach an eligible blocker, apply timed curated blows, wait until clearance exists, then repath. Integrate route/reachability decisions with that capability. Never physically enter an uncleared footprint.

##### B3.5 — Titans still enter overhead mountain

**File + symbol:** `Patch_ThickRoofAvoidance.cs:Postfix`  
**Severity:** visible. **Confidence:** high.

`CostToMoveIntoCell()` affects movement along a selected path, not route exclusion. It also checks only the anchor cell, allowing a multi-cell titan’s edge beneath rock.

**Fix:** supply footprint-aware roof exclusion before search. A concrete 1.6 integration point to evaluate is the per-request `providerCost` array after `PathGridDoorsBlockedJob.Execute()`; `PathFinderJob.IndexCost()` treats `ushort.MaxValue` as impassable. Compose existing restrictions, cache roof exclusion data, and handle already-invalid starting positions. A large soft avoidance cost cannot guarantee “never.” [PathGridDoorsBlockedJob](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/PathGridDoorsBlockedJob.cs), [PathFinderJob](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/PathFinderJob.cs)

##### B3.6 — Multi-cell things receive multiple blows in one step

**File + symbol:** `TitanicWakeProcessor.cs:ProcessCrushables`  
**Severity:** visible. **Confidence:** high.

`ThingGrid.Register()` registers a multi-cell building in every occupied cell. Processing each titan cell independently can hit the same surviving building repeatedly. A T2 overlap covering four cells can deal 240 damage rather than one 60-damage pass. [1.6 ThingGrid.Register](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/ThingGrid.cs)

**Fix:** deduplicate ordinary crush targets across the entire step before damage. If area-proportional damage is intended, calculate and expose it explicitly.

##### B3.7 — Assigning the existing position produces a false movement event

**File + symbol:** `Patch_Thing_Position_Wake.cs:Postfix`  
**Severity:** visible. **Confidence:** high.

`Thing.Position` returns early when the assigned value equals its current position. A Harmony postfix still executes after that return, so another mod’s redundant assignment can trigger damage and rubble without movement. [1.6 Thing.Position](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Thing.cs)

**Fix:** capture the previous position/map in prefix state; process only a real change on the same spawned map. Define teleport behavior separately.

##### B3.8 — Flying titans crush ground objects

**File + symbol:** `CompTitanicWake.cs:Notify_EnteredCell`; `TitanicWakeProcessor.cs:ProcessFootprint`  
**Severity:** visible. **Confidence:** high.

The wake checks spawning and tier, but not 1.6’s `Pawn.Flying` state. Position changes during flight therefore damage ground plants/buildings and create ground rubble. [1.6 Pawn.Flying](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

**Fix:** suppress ground-contact effects during flight. Add a separate, deliberate landing effect if desired; retain vanilla flight through `MaxFlightTime`.

##### B3.9 — Rotten or scaria-affected corpses can become fresh harvest pools

**File + symbol:** `Patch_CorpseSiteConversion.cs:Postfix`; `TitanicCorpseSiteUtility.cs:ConvertToSite`; `Building_TitanicCorpseSite.cs:SpawnSetup`  
**Severity:** visible. **Confidence:** high.

Conversion accepts any newly spawned T3 corpse and starts a new spoilage clock. Dropping an old rotten corpse can therefore create fresh meat. Immediate conversion also precedes `Pawn.Kill()`’s post-placement scaria/toxic rot handling.

**Fix:** defer conversion as in B3.1; then evaluate `CompRottable`, death age, and relevant eligibility. Carry the existing decay state into the pool and do not grant edible meat from ineligible remains.

##### B3.10 — T3 conversion drops additional butcher products

**File + symbol:** `TitanicCorpseSiteUtility.cs:ConvertToSite`  
**Severity:** data-loss. **Confidence:** high for declared extra products.

The utility promises exact vanilla yield but copies only meat and leather. `Pawn.ButcherProducts()` also includes base butcher products and life-stage body-part products; modded races can add further outputs. [1.6 Pawn.ButcherProducts](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

**Fix:** use a scribed product-pool abstraction with an explicit supported extraction contract. At minimum, preserve declared extra products and exclude unsupported races from automatic conversion. Avoid blindly enumerating arbitrary butcher iterators at death, since they can have side effects.

##### B3.11 — Failed product placement silently consumes yield

**File + symbol:** `Building_TitanicCorpseSite.cs:HarvestOneSession`; `JobDriver_HarvestTitanicCorpse.cs:MakeNewToils`  
**Severity:** data-loss. **Confidence:** high.

The pool is decremented—and possibly the site destroyed—before `GenPlace.TryPlaceThing()` succeeds. Placement can return false after partial placement, leaving an unspawned remainder that the driver abandons. [1.6 GenPlace.TryPlaceThing](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/GenPlace.cs)

**Fix:** retain pending products in a scribed holder and retry placement, or commit only quantities actually delivered. Preserve partial remainders. Oversized output alone is not the bug: vanilla placement can split stacks.

##### B3.12 — Missing yield defs create harvest jobs that extract nothing

**File + symbol:** `Building_TitanicCorpseSite.cs:ExposeData/HasYield/HarvestOneSession`  
**Severity:** visible. **Confidence:** high when a referenced def disappears.

`Scribe_Defs.Look()` can leave a removed meat/leather def unresolved while its saved counter stays positive. `HasYield` remains true, but harvesting never decreases that pool because its def is null.

**Fix:** reconcile counters and definitions during `PostLoadInit`, report invalid pools, and exclude them from available work. Destroy an empty site or preserve unresolved pool metadata for later recovery.

##### B3.13 — Disabling the corpse feature does not stop existing corpse mechanics

**File + symbol:** `Building_TitanicCorpseSite.cs:TickRare`; `WorkGiver_HarvestTitanicCorpse.cs:HasJobOnThing`; `JobDriver_HarvestTitanicCorpse.cs:MakeNewToils`  
**Severity:** visible. **Confidence:** high.

`CorpseSiteActive` gates only conversion. Existing buildings keep ticking, miners keep receiving jobs, and running jobs keep extracting after the feature or animal master is disabled.

**Fix:** implement an explicit transition policy. A graceful policy can stop conversion, pause decay, and allow clearly labelled recovery of existing yield; restoring ordinary corpses requires preserved bodies and accounting for already-extracted resources. Wire the selected policy into all three symbols.

##### B3.14 — The yield curve jumps upward at T2

**File + symbol:** `YieldCurveUtility.cs:SubLinearFactor`; `RM_TitanicKernel.cs:YieldFloor`  
**Severity:** visible. **Confidence:** high.

Immediately below body size 8, the multiplier approaches `sqrt(4/8) ≈ 0.707`; at T2 it resets to `sqrt(8/8) = 1`. An arbitrarily small size increase produces roughly 41% more yield.

**Fix:** use a continuous curve anchored at T1, or offset successive curve segments so they meet at tier boundaries. Test continuity, monotonicity, and configured floor behavior.

##### B3.15 — Large Pawns retains uncurated wall breaking

**File + symbol:** `LargePawnsBridge.cs:TryReconcile`  
**Severity:** visible. **Confidence:** high for missing enforcement; medium for runtime impact.

The supplied owner item requires disabling Large Pawns’ `PathClearingUtility` switches. The bridge writes thresholds and override rows only. Its independent movement patches may destroy objects that this mod protects, including while Huge Things’ wake is off.

**Fix:** resolve and disable the three clearing controls using the verified installed API, with diagnostics and explicit ownership. Implement B3.4 as the curated replacement; simply disabling the other clearing mechanism exposes the blocked-route problem.

##### B3.16 — Bridge failure leaves a partially rewritten configuration

**File + symbol:** `LargePawnsBridge.cs:TryReconcile/SetFloatField/PushOverrideRows`  
**Severity:** visible. **Confidence:** high.

Mutations occur before all fields, row members, and `NotifyEdited()` are validated. A later exception leaves earlier edits applied. Missing override support merely warns; missing notification silently skips refresh; the success message can still claim reconciliation. The catch’s “untouched ladder” claim is false.

**Fix:** validate the complete integration first, snapshot affected values/rows, apply atomically, and roll back on failure. Require refresh support before claiming success.

##### B3.17 — Large Pawns overrides can disagree with runtime tiers

**File + symbol:** `LargePawnsBridge.cs:PushOverrideRows`; `TitanicTierUtility.cs:GetTier`  
**Severity:** visible. **Confidence:** high for the structural mismatch.

Unowned Large Pawns override rows remain authoritative ahead of thresholds. Explicit force-in rows also fix size from race base size, while wake tier uses current pawn size. A juvenile can therefore retain an adult footprint while having a lower or absent wake tier.

**Fix:** define one shared instance-level footprint policy. Audit conflicting rows, and represent force-in as a minimum footprint combined with current tier rather than always pinning adult size. Use a verified resolver hook if the external override format cannot express that.

##### B3.18 — Comp qualification misses races that grow beyond their base size

**File + symbol:** `TitanicTierUtility.cs:DefQualifies`; `RM_TitanicKernel.cs:DefQualifies`; `RM_TitanicCreaturesMod.cs:InjectWakeComps`  
**Severity:** visible. **Confidence:** high for life stages above factor 1; medium for modded size changes.

The qualification check tests only base size. A below-threshold race with a sufficiently large life-stage factor can acquire a runtime tier without the comp required to trigger its wake.

**Fix:** inspect the maximum declared life-stage factor during qualification. For unpredictable size-changing mods, make the movement hook capable of checking current tier without depending exclusively on startup comp eligibility.

##### B3.19 — Most numeric settings lack load validation

**File + symbol:** `RM_HugeThingsSettings.cs:ExposeData`; `RM_TitanicKernel.cs:ThresholdsValid`  
**Severity:** visible; crash possible with extreme inputs. **Confidence:** high.

Only scales and smash tier are sanitized. Stale or edited settings can introduce non-finite work duration, zero extraction batches, negative damage, invalid spoilage, or invalid yield floors. `ThresholdsValid()` also accepts an infinite T3 threshold.

**Fix:** validate every numeric field on load and before committing edits. Require finite thresholds, positive work/batch sizes, and bounded damage/chance/spoilage/yield values.

#### 4. **Unforeseen challenges + mitigations**

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

#### 5. **Opportunities to leverage**

- **B5.1 — Add a tier/footprint inspector.** Show current body size, effective tier, physical footprint, selection bounds, and active behaviors. This serves players, validation, and compatibility diagnosis.

- **B5.2 — Expose crush-rule explanations.** A debug command answering “which rule protects or crushes this thing?” would cheaply reveal category gaps and conflicting overrides.

- **B5.3 — Emit small consequence events.** Publish successful crush, giant-plant smash, corpse creation, harvest, and exhaustion events. Other mods can react without patching the movement setter themselves.

- **B5.4 — Reuse footprint planning for placement previews.** Show whether an entrance, holding area, caravan staging point, or gravship unloading location fits the animal.

- **B5.5 — Expand the corpse pool once, generically.** Product defs, quantities, decay classes, and session costs would support chitin, bone, machine salvage, and modded products through the same job.

- **B5.6 — Use cached footprint differences.** Newly entered cells can drive trails and contact effects, reducing repeated rolls and footprint rescans. Keep repeated pressure damage as a separate deliberate behavior.

- **B5.7 — Add configurable content providers.** Corpse scavenger and camp providers can name PawnKindDefs/factions through XML, satisfying the ruling without hardcoding a particular creature or faction into the engine.

- **B5.8 — Build coherent settings presets.** “Full size consequences,” “plants and selection,” and “gentle wildlife” can set existing fields, show pending restart changes, and reduce settings-page complexity.

#### 6. **Extensions WELL beyond the mod**

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

## Part C — Seam, settings and test apparatus (kernels vs game fidelity, SelfTest fuzz, validation.py, offline selftest)

#### 1. **Concept review**

**C1.1 — Verdict: sound merge, incomplete proof of gameplay.** One engine for “size has consequences” is coherent, and the two master switches preserve plant-only and animal-only play. The kernels provide useful arithmetic and decision tests. They do **not** establish that the game supplies the correct inputs, applies decisions safely, or survives save/load.

This review uses the inlined files; I did not run the projects or the live suite. External engine cross-checks used an Odyssey-aware decompilation, whose exact build is not pinned to your installed binary. Build-sensitive conclusions below are marked **“verify on 1.6.”**

**C1.2 — The trunk/canopy distinction is the strongest design choice.** Blocking ground contact while allowing movement under the canopy gives giant plants a physical presence without turning their entire picture into a wall. Shared claims, deferred closure and item preservation support that experience.

**C1.3 — “Smashes while passing” and “smashes through” are different capabilities.** `GiantSmash.Owners` implements damage near an already-moving titan. It does not provide a route through an impassable obstruction or continued smashing while movement is stalled. The settings text currently promises more than this kernel establishes.

**C1.4 — The yield curve has a conspicuous tier discontinuity.** `YieldFloor` resets the reference floor at T2. With shipped thresholds, normalized yield rises from approximately **5.66 immediately below body size 8 to 8 at body size 8**: a 41% jump. The tests check monotonicity within each tier, hiding this boundary. This may be intentional, but a continuous curve would make animal growth and threshold tuning feel less arbitrary.

**C1.5 — Settings are extensive, but “superb” needs clearer effective-state feedback.** Add reset-to-defaults, localized labels, and a visible distinction between applied values and changes awaiting restart. The animal master promises vanilla behavior immediately even though the Large Pawns bridge is explicitly startup-only.

#### 2. **Implementation review**

**C2.1 — The project split is structurally good.** Both projects compile the same four production kernel files directly. The net8 harness excludes Verse, Unity and Harmony; the net472 mod excludes SelfTest. The explicit production compile list matches the supplied manifest. No obvious missing compile item appears here.

The remaining gap is substantial: a successful SelfTest build says nothing about compilation or execution of the adapters, Harmony patches, comps or jobs.

**C2.2 — Kernel fidelity is strongest for pure geometry, weakest at the game boundary.**

| Finding | What the tests establish | What remains unproved |
|---|---|---|
| **C2.2a — Footprint** | Transform arithmetic, contact mapping, containment and an independently expressed forward oracle. | Actual `Plant.Print` RNG replay, active graphic/variant selection, mesh alignment and renderer patches. |
| **C2.2b — Claims** | Claim-set union and deterministic primary ownership. | Safe physical blocker realization, owner reassignment, grid notifications and save/load reconstruction. |
| **C2.2c — Titanic** | Tier, damage, roof and pool formulas. | Correct race/runtime inputs, crush-rule precedence, actual damage application, job output and Scribe persistence. |
| **C2.2d — Seam/settings** | Boolean gate truth tables and owners selected from supplied `SolidCell` records. | Production gate consumers, collection of every overlapping owner, real movement and production source-key generation. |

The base single-mesh plant transform agrees with the inspected `Plant.Print` implementation. However, `Plant.Graphic` can select immature, leafless or polluted graphics; matching the transform alone does not establish matching masks. [Engine plant implementation](https://github.com/Chillu1/RimWorldDecompiled/blob/master/RimWorld/Plant.cs).

**C2.3 — `validation.py` proves a narrow smoke test.** Its driven behavior is principally def resolution, field access, patch-owner presence, one giant’s blocker counts, and an Elephant/Rat wake comparison. It explicitly leaves selection, damage forwarding, item movement, trapping, save/load, T2/T3 behavior, butcher yield, corpse harvesting, flight and Large Pawns unmeasured.

Running `python validation.py` executes **static checks only**. A `STATIC: PASS` must never be reported as in-game acceptance.

**C2.4 — The settings “roundtrip” does not test Scribe.** `settings_roundtrip` writes and reads static fields through reflection. It never demonstrates persistence, loading defaults for omitted keys, sanitization, or restart behavior. `Mod.GetSettings` and `LoadedModManager.ReadModSettings` use a separate serialized path. [Mod settings entry point](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Mod.cs), [settings serialization](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/LoadedModManager.cs).

**C2.5 — Several tests overstate their independence or coverage.**

- `CasePlanner` floods the **same planning window**, despite its introductory claim of a whole-board check.
- `CaseSmashStep` directly calls `DamageDedup` twice with a deliberately identical key; it never drives the production forwarding routes.
- `CaseCache.Fresh` returns `"-"` whenever blocking is disabled, discarding selection despite the independent selection toggle. It also never verifies that an equal signature avoids recomputation.
- The C# harness does not exercise `PawnHitbox`; Python tests its sizing helpers, not the complete footprint-union behavior.
- Checking measured output against the same measurement tool detects stale generated data, but cannot independently validate the tool’s interpretation of ground contact.

**C2.6 — Boundary fuzz excludes the cases it most needs to adjudicate.** `CaseBoundary` nudges by `1e-4`, while `CheckOracle` excludes cells within `2e-3` of relevant edges. Those nudges generally remain inside the ambiguity exclusion. Keep the double oracle, but add exact float boundary fixtures that specify inclusion at each side and at equality.

**C2.7 — Planner cost is the principal performance concern.** For window area `V` and `N` candidates, each attempted closure allocates and performs another flood over `V`. Fixpoint retries permit worst-case work approaching `O(N²V)`. `RootServed` also creates direction arrays repeatedly.

Reuse scratch buffers, use visitation stamps, move directions to static storage, and measure milliseconds and allocation per refresh. Budget by work performed as well as plants refreshed; one exceptionally large plant can exceed a per-plant budget.

**C2.8 — Selection has map-wide work even when features are disabled.** Startup keeps opted-in defs in `WithCustomRectForSelector`; `GenUI.ThingsUnderMouse` scans that group, and its property check can evaluate a custom rectangle twice. Your postfix adds a `HashSet` and predicate allocation to every result with two or more things.

First ensure disabled paths return cheaply; then profile dense Rot maps and stacked selections. A spatial candidate index is justified only if measurements show this path matters. [Engine mouse selection](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/GenUI.cs).

**C2.9 — Save compatibility is plausible, not demonstrated.** Preserving namespaces and def names is appropriate. Part C contains no tests of reference resolution, reconstruction order, orphan blockers, corpse pools or resumed jobs. The transient design’s assertion that existing saves load cleanly needs the specified cold-load exercise.

#### 3. **Potential bugs**

**C3.1 — Local-border reachability can permit a globally trapping closure.**

- **File + symbol:** `Kernel/RM_HugeClaimsKernel.cs` — `Planner.Plan`, `Planner.Reach`; `SelfTest/HugeThingsFuzz.cs` — `CasePlanner`.
- **Mechanism:** Every passable window-border cell is an independent flood seed. Close the middle of a narrow corridor crossing the window: both halves still reach a border, so closure passes. Outside the window, one half can terminate in a sealed cave containing a pawn. RimWorld’s actual `Reachability.CanReach` evaluates connectivity beyond this artificial border.
- **Severity:** visible. **Confidence:** high.
- **Fix:** Preserve relevant connectivity using map/region information or an adaptive search that resolves exterior connections. Add a larger-board corridor fixture whose far end lies beyond the planning window. A fixed larger margin cannot provide the advertised guarantee. [Engine reachability gate in `Pawn_PathFollower.StartPath`](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/Pawn_PathFollower.cs) — **verify on 1.6**.

**C3.2 — Item assignments can reserve capacity for cells the planner subsequently refuses.**

- **File + symbol:** `Kernel/RM_HugeClaimsKernel.cs` — `ItemMover.Assign`, `Planner.Plan`; `SelfTest/HugeThingsFuzz.cs` — `CaseItems`.
- **Mechanism:** The modeled sequence assigns destinations before deciding which sources close. Suppose source A sorts first, but closing it would remove a giant’s last accessible neighbor. A reserves the only destination; source B receives none. The planner rejects A and leaves B open. Repeating that sequence repeats the starvation while the destination remains unused.
- **Severity:** visible. **Confidence:** high for the modeled algorithm; medium for game impact because the map adapter is outside Part C.
- **Fix:** Recompute capacity assignments after excluding sources rejected for closure, until assignments and accepted closures agree. Preserve deferred claims. Add a liveness assertion showing B eventually closes without external intervention.

**C3.3 — Pawn hitboxes use the default body graphic rather than the active rendered graphic.**

- **File + symbol:** `HugeThingsCore.cs` — `HugeThingsApi.PawnHitbox`.
- **Mechanism:** It always reads `CurKindLifeStage.bodyGraphicData.drawSize`. `PawnRenderNode_AnimalPart.GraphicFor` can instead choose female or alternate graphics, and its mesh size follows that selected graphic. A larger female/alternate body therefore retains the smaller default hitbox.
- **Severity:** visible. **Confidence:** high for the mismatch.
- **Fix:** Resolve the active animal graphic and relevant rendered transform, then retain the existing union with `OccupiedRect`. Test differing default/female/alternate dimensions. [Animal graphic selection and mesh sizing](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/PawnRenderNode_AnimalPart.cs) — **verify on 1.6**.

**C3.4 — Def qualification does not actually answer whether a race can ever become tiered.**

- **File + symbol:** `Kernel/RM_TitanicKernel.cs` — `DefQualifies`; `SelfTest/TitanicFuzz.cs` — `Tier`.
- **Mechanism:** The tests feed the same `b` to def qualification and runtime tiering. The game distinguishes `RaceProps.baseBodySize` from `Pawn.BodySize`, which includes the current life-stage factor. A modded race with base size 3 and a stage factor 2 reaches T1 at runtime but fails startup qualification.
- **Severity:** visible. **Confidence:** medium; contingent on the production caller using base size as documented and on such content.
- **Fix:** Qualify against the maximum supported life-stage size, or attach a lightweight dormant wake comp broadly enough to cover runtime growth. Test base size and stage factor independently, including juvenile down-tiering. [Engine `Pawn.BodySize`](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Pawn.cs) — **verify on 1.6**.

**C3.5 — A movement-triggered smash cannot guarantee breaching a blocked route.**

- **File + symbol:** `Kernel/RM_HugeTitanKernel.cs` — `GiantSmash.Owners`, `Reach`; `SelfTest/HugeTitanFuzz.cs` — `CaseSmashStep`.
- **Mechanism:** The test manually advances the titan through all 32 positions. Normal `Pawn_PathFollower.StartPath` can reject an unreachable destination before movement starts. An impassable giant barrier can therefore prevent the steps that trigger damage. A surviving plant can also halt further useful smashing.
- **Severity:** visible. **Confidence:** medium; the movement adapter is not supplied here.
- **Fix:** Either describe this as incidental damage when brushing trunks, or add a breach behavior that approaches a reachable trunk, damages its owner while stationary, and retries the route after destruction. Test an obstruction with no alternate path. [Engine path-start checks](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/Pawn_PathFollower.cs) — **verify on 1.6**.

**C3.6 — Most numeric settings accept unsafe persisted values.**

- **File + symbol:** `RM_HugeThingsSettings.cs` — `ExposeData`.
- **Mechanism:** Only the two scales and smash tier are sanitized. Scribe-loaded values bypass sliders: negative session sizes can stop harvesting, invalid work times can break job expectations, and non-finite damage/yield values can reach downstream arithmetic. `ThresholdsValid` also accepts an infinite T3 threshold.
- **Severity:** visible; downstream crash risk depends on adapters. **Confidence:** high for the missing validation.
- **Fix:** Reject NaN/infinity and enforce documented ranges for every numeric field on load and at settings mutation boundaries. Keep the documented shipped-tier fallback for invalid ladders. Add malformed-config fixtures, including zero and infinity.

**C3.7 — Validation restores shipped defaults instead of the user’s original settings.**

- **File + symbol:** `validation.py` — `_restore`, `trunk`, `wake`.
- **Mechanism:** Wake fields restore from `DEFAULTS`; trunk restores `plantTrunkEnabled=True`. A validation run can therefore change an intentionally disabled feature or custom multiplier. The underlying static state is immediately gameplay-visible and may later be persisted.
- **Severity:** visible. **Confidence:** high.
- **Fix:** Snapshot original values before mutation, restore them in `finally`, verify restoration success, and restore the original pause state. Use a disposable test map/save for destructive staging.

**C3.8 — Some fuzz invocations pass without executing any cases.**

- **File + symbol:** `SelfTest/Program.cs` — `Main`; `HugeThingsFuzz.Run`, `HugeTitanFuzz.Run`.
- **Mechanism:** `--fuzz-only any --fuzz-scale 0` returns success; the seam families behave similarly. The Titanic runner instead rejects zero cases. With a replay seed and zero scale, plant/seam `Family` can even print “1 cases” although its loop ran zero times.
- **Severity:** minor, with material false-confidence risk. **Confidence:** high.
- **Fix:** Validate finite, nonnegative scale and arguments centrally. Let seed replay explicitly run one case. Report intentional zero-scale runs as skipped, and never print “ALL PASS” for zero checks. **Engine mechanism:** none; this defect occurs before Verse is involved.

**C3.9 — Python optimization can disable almost every offline assertion.**

- **File + symbol:** `selftest_hugethings_footprint.py` — decorated tests and `main`.
- **Mechanism:** `python -O` or `PYTHONOPTIMIZE` removes `assert` statements. The runner can increment every test’s success count despite incorrect measurements or geometry.
- **Severity:** minor, with false-confidence risk. **Confidence:** high.
- **Fix:** Refuse execution when `__debug__` is false, or use explicit check functions that raise independently of optimization. **Engine mechanism:** none; this is an offline runner defect.

**C3.10 — Explosion redirection bypasses an ignored blocker’s exclusion.**

- **File + symbol:** `HugeThingsCore.cs` — `Patch_DamageWorker_ExplosionDamageThing.Prefix`.
- **Mechanism:** The prefix replaces blocker `t` with its plant without inspecting `ignoredThings`. The original `DamageWorker.ExplosionDamageThing` then checks whether the **plant** is ignored. An explosion excluding the blocker alone can consequently damage its owner.
- **Severity:** visible. **Confidence:** high for that input condition.
- **Fix:** Respect an ignored original blocker before redirection, while retaining the owner dedup and the original explosion cell for falloff. Add fixtures excluding the blocker, owner and neither. [Engine explosion exclusion and damage path](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/DamageWorker.cs) — **verify on 1.6**.

#### 4. **Unforeseen challenges + mitigations**

**C4.1 — Rendering patches can invalidate measurements without overriding `Print`.** `ValidateRenderer` checks the declaring class, but a Harmony patch on vanilla `Plant.Print` still passes that check. Log relevant patch owners and provide an overlay comparing the replayed quad with measured contacts; disable blocking for known incompatible transforms.

**C4.2 — Dense overlapping plants need an integration model.** A ledger’s union is order-independent; physical realization involving per-owner planning windows and item moves need not be. Test shuffled registration/refresh orders through a model combining ledger, planner, mover and realized blockers.

**C4.3 — Runtime settings changes can leave mixed effective states.** Root-only plants retain startup-mutated passability until restart, and Large Pawns retains startup configuration. Show the effective state and pending restart explicitly; refresh every affected map after live changes without depending on the settings window being open.

**C4.4 — Save/load must preserve ownership, not merely blocker counts.** Verify overlapping plants, destruction of the primary owner, deferred cells, pushed items, corpse pools and an interrupted harvest job through save/load/save. Inspect owner identities and resource totals, plus subsequent pathing.

**C4.5 — A `Thing.Position` hook sees more than walking.** Unsticking, relocation and ExplosiveKnockback can set position too. Verify that the adapter distinguishes movement modes and does not invent damage along a teleport path. Dedup identity should match an action; a pawn ID plus tick may merge separate same-tick actions.

**C4.6 — Flight requires a ground-contact policy.** Flying titans should use vanilla 1.6 flight through `MaxFlightTime`. Their airborne movement should not automatically trample ground plants or leave rubble; test takeoff, landing, flight expiry and roof interactions.

**C4.7 — Live wake tests are vulnerable to randomness and repeated exposure.** Zero rubble after 15 single-cell rolls at 35% has probability about 0.16%. Conversely, several visits can kill a 5-HP plant even at two damage per visit. Use deterministic trail settings and one controlled movement event for damage assertions; verify starting counts, HP and actual movement.

**C4.8 — Deferred retries and disabled features need scale measurements.** Profile a sparse map, a dense Rot map, several loaded maps and the full modlist. Record refresh latency, worst tick, allocation, pending-cell count and selection cost; include all-off operation and a mass settings refresh.

**C4.9 — Exact-namespace patch discovery is a maintenance trap.** Moving a patch into a subnamespace silently excludes it from `PatchNamespace`. Add a startup assertion that every intended Harmony patch class has exactly one assigned owner and was installed once.

#### 5. **Opportunities to leverage**

**C5.1 — Add semantic debug probes.** Expose desired claims, realized blockers, owner sets, selection rectangles, runtime tiers and pending refusals. These would let validation measure currently unmeasured behavior without relying entirely on simulated clicks.

**C5.2 — Add a footprint inspection overlay.** Show claimed, realized and deferred cells, with refusal reasons such as pawn, item, protected object or access preservation. This would make art measurement and compatibility debugging much faster.

**C5.3 — Publish distinct read-only queries.** Other mods need to distinguish canopy coverage, desired ground contact, realized solid cells and owners. That prevents consumers from treating an unmaterialized claim as a wall.

**C5.4 — Emit sparse consequence events.** Plant smashed, titan breached an obstacle, corpse site created and harvest completed are useful hooks for Traces, Aftermath, RimProperty and ideology content. Emit events for consequences rather than polling every footprint.

**C5.5 — Improve the harness with coverage requirements.** Require full `PawnHitbox` tests, cross-tier yield boundaries, finite-value rejection, independent whole-map connectivity checks and a corpse-site state machine. Report skipped and ambiguous cases explicitly.

**C5.6 — Provide a small set of presets.** “Plants only,” “size and selection,” and “full consequences” could configure the existing controls. Preserve individual tuning and make the shipped preset exactly reproduce current defaults.

#### 6. **Extensions WELL beyond the mod**

**C6.1 — TheRot: decomposer cycles.** A corpse site attracts the Rot’s decomposers; their feeding transfers resources from the corpse pool into nearby fungal growth. Giant mushrooms then become obstacles those same titans can smash.

**C6.2 — ExplosiveGrowth: dramatic, safe expansion.** Feed rapid growth into the existing dirty-footprint queue. Its countdown can preview impending contact cells, letting colonists clear access before the plant expands.

**C6.3 — FlowWorks: trunks as hydraulic obstacles.** Realized contacts divert shallow flow; uprooting or smashing a giant releases a blocked channel. Keep hydraulic geometry separate from passability so fluid can seep through some root systems.

**C6.4 — OasisMaker and SolarMirrors: useful canopy geometry.** Canopy queries could influence oasis placement and reveal where mirrored sunlight reaches vegetation. Any resulting heat must feed vanilla temperature and heatstroke.

**C6.5 — CreatureBehaviors: controlled titan movement.** A reusable behavior steers friendly titans away from colony infrastructure and gives hostile ones explicit breach targets. This would also resolve the current movement-triggered-smash limitation.

**C6.6 — HostileFlora: anchored versus mobile stages.** An anchored plant claims a footprint; its mobile stage releases it and uses pawn behavior. Re-rooting uses the same safe realization checks, preserving items and access.

**C6.7 — Long Shade and Stillsand: titan migration incidents.** Warn of a grazer crossing the current map toward food or water. Migration supplies the in-game reason for temporarily leaving its single home biome.

**C6.8 — FloodedCanyon: flood-driven obstruction.** Floods uproot selected giants and deposit them as harvestable debris at narrow crossings. Map-generation and incidents can use authored placements on the existing frozen world.

**C6.9 — WeepingStones: stone-crab husbandry.** Gorrask breeding becomes a space-management challenge: adults need broad pens, and controlled breeding grounds offer valuable harvest sites without incidental colony destruction.

**C6.10 — Scarlands and RustCathedral: machinery with physical consequences.** Apply curated wake rules to giant machines, with salvage-site pools replacing meat and leather. WreckedMachines can supply dangerous residual mechanisms.

**C6.11 — Traces and Aftermath: readable aftermath.** Smash events leave species-appropriate splinters, fungal dust or bent metal; Aftermath records the titan’s contribution to a battle and resulting infrastructure losses.

**C6.12 — Inhabited and RimProperty: accountable damage.** Settlements remember a visiting titan and identify responsibility for destroyed property. Escort contracts can pay for a safe crossing and penalize damage.

**C6.13 — Quests: clear a living route.** A caravan requests a passage through giant vegetation before a deadline. Players can harvest an access corridor, redirect the travelers or enlist a titan to breach it.

**C6.14 — Factions: titan keepers.** A faction maintains carefully managed colossi, trades handling expertise and hires colonies to prepare suitable stopping grounds. Its animals keep species-specific biome homes.

**C6.15 — Items: guide stakes and restraint equipment.** Place bait, guide stakes or tether infrastructure to influence a titan’s next destination. They should affect behavior through CreatureBehaviors rather than erase its physical consequences.

**C6.16 — Ideology: reverence for giants.** Precepts reward preserving ancient plants or respectful corpse-site harvesting. Rituals could protect a mature giant or hold a communal harvest, with explicit history events for deliberate destruction.

**C6.17 — Gravship landing: inspect the actual clearance consequences.** Preview which giants the landing policy will remove and where colony-tamed titans can disembark. Test blocker cleanup against the exact 1.6 `GravshipPlacementUtility.ClearArea` contract.

**C6.18 — KeelHoist: giant cargo in portions.** Harvest or salvage sessions prepare manageable bundles for hoisting from inaccessible maps. Preserve one resource pool so repeated hoist/harvest actions cannot duplicate yield.

**C6.19 — `RM_SeabedLayer`: reefback falls.** Reefbacks and lanternwhales belong to their seabed habitat; their deaths create benthic harvest sites accessible through layer travel. Give seabed remains suitable decay and access rules instead of inheriting terrestrial assumptions.

**C6.20 — DivingInteraction and AcousticScanner: locating giant remains.** Acoustic sounding identifies a submerged carcass or root mass; a dive map exposes a limited work area linked to the parent site’s resource pool. Every extracted unit is deducted once across both maps.

## Part D — Concept and extensions (design docs, defs, settings, entry classes)

#### 1. **Concept review**

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

#### 2. **Implementation review**

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

#### 3. **Potential bugs**

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

#### 4. **Unforeseen challenges + mitigations**

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

#### 5. **Opportunities to leverage**

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

#### 6. **Extensions WELL beyond the mod**

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
