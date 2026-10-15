I found **12 issues worth checking before release**. This is a source review; the suggested checks have not been run. Locations below use exact code-line quotations rather than guessed line numbers. Paths are relative to `src/RimMandrake/FlowWorks/Source/`.

**F1 — HIGH — Reload loses flow inputs that a one-shot flood never restores**

- **Where:** `RM_MapComponent_Excavation.cs`: `private readonly RM_DriverInputs driverInputs = new RM_DriverInputs();`; `Flood_FlowWorks.cs`: `placedLookup.Contains(c)`.
- **What happens:** Driver inputs affect source hops and flow direction but are not saved. Pumps can re-mark backed-up outlets; a flood’s already-placed cells are saved and never written again. Reload therefore loses those inputs permanently, potentially stalling a flat branch or changing its fill order.
- **Repro:** Enable pump-fed spread. Let a release fill an inlet to a flat, source-free channel; save before the next pulse. Compare the next pulses with and without reloading.
- **Suggested check:** **Offline SelfTest:** snapshot a flood-fed kernel scene, reconstruct it without driver inputs, and compare fills over several pulses using production `MayFlowBetween`.
- **Confidence:** medium. The persistence gap is definite; the exact resulting stall depends on the unshown `RM_DriverInputs` and `RM_StockMath`.

**F2 — MEDIUM — Reload forgets cells the flood permanently refused**

- **Where:** `Flood_FlowWorks.cs`: `placedLookup.Add(c);   // never offered again; spends no volume`; load rebuild: `placedLookup.Add(placedCells[i]);`.
- **What happens:** HandsOff and Refused cells enter only `placedLookup`, while successful placements enter the saved `placedCells`. Reload forgets the refusals, making the same release eligible to revisit cells it would permanently skip without reloading.
- **Repro:** Switch legacy flood-to-engine integration off. Allow an active release to attempt one adjacent channel cell, then save while other frontier options remain. Switch integration on and compare continued play against a reload followed by the same setting change.
- **Suggested check:** **Offline serialization case:** preserve successful and refused cells, round-trip the release, and assert identical eligibility for every previously offered cell.
- **Confidence:** high.

**F3 — MEDIUM — Dig-discovery cache retains a removed map**

- **Where:** `RM_DigDiscovery.cs`: `private static Map poolMap;` and `poolMap = map;`.
- **What happens:** The static cache holds a strong map reference with no removal/load cleanup shown. A discarded map, including its reachable object graph, remains rooted until another discovery rebuilds the pool. Reference equality correctly prevents reuse on a newly loaded map; the defect is retained memory.
- **Repro:** Trigger a discovery, then abandon that map or load another save. Make no further discoveries.
- **Suggested check:** **Cheap live state read:** inspect whether `poolMap` is absent from `Find.Maps` after removal. A managed-memory snapshot can confirm retained objects.
- **Confidence:** high.

**F4 — MEDIUM — Overlay meshes have no map-removal cleanup**

- **Where:** `RM_LiquidSurface.cs`: `mesh = new Mesh { name = "RM_LiquidSurface" };` and `meshPool[look] = mesh;`.
- **What happens:** Overlay drawing creates owned Unity meshes, but this component never destroys them. Dropping the managed map component does not provide explicit cleanup of those native Unity objects. Repeated map visits/removals or save loads can accumulate meshes.
- **Repro:** View a liquid with `overlay = true`, then repeatedly unload/reload its map.
- **Suggested check:** **Cheap live state read:** count meshes named `RM_LiquidSurface` using `UnityEngine.Resources.FindObjectsOfTypeAll<UnityEngine.Mesh>()` before and after repeated removals.
- **Confidence:** high for the missing cleanup; exposure depends on an overlay-enabled look.

**F5 — HIGH — An active fill-in job can finish over a pawn**

- **Where:** `WorkGiver_FillInCanal.cs`: `if (c.GetFirstPawn(pawn.Map) != null)`; `JobDriver_FillInCanal.cs`: `excavation.FillIn(c);`.
- **What happens:** Occupancy is checked when offering the job, but neither its completion effect nor `FillIn` checks again. A pawn entering during the work can have the hole filled underneath them, contrary to the explicit “get them out first” rule.
- **Repro:** Start filling an empty pit cell. Force another pawn into it after work begins, leaving the designation intact, then let the job complete.
- **Suggested check:** **Cheap live scenario:** accelerate the worker’s MiningSpeed, introduce the occupant immediately before completion, then read depth and occupant position. Depth should remain unchanged.
- **Confidence:** high. The relevant vanilla continuation is `JobDriver_AffectFloor.MakeNewToils`; the shown subclass adds no occupancy failure/completion guard.

**F6 — MEDIUM — Panning finishes successfully after its water disappears**

- **Where:** `Quarry/RM_PlacerWorks.cs`, panning tick action: `if (w.IsValid) { pawn.rotationTracker.FaceCell(w); }`; completion: `RM_PlacerPanning.Session(pawn);`.
- **What happens:** Water adjacency is checked when selecting the job. During work it controls facing only, and `Session` never checks water. An existing session continues earning Mining XP and can produce ore after the only adjacent river cell becomes ineligible.
- **Repro:** Start panning, then remove or cover its only qualifying water cell before completion.
- **Suggested check:** **Cheap live scenario:** change that terrain through the bridge during a session, complete it with accelerated work, and read output and placer stock. Use maximum panning yield and a skilled pawn to eliminate a missed-roll ambiguity.
- **Confidence:** high.

**F7 — MEDIUM — Mining out the placer pool leaves endless unproductive panning**

- **Where:** `Quarry/RM_PlacerWorks.cs`: `units = RM_PlacerDraw.PlacerUnits(map);`; `ShouldSkip`: `return stock == null || stock.Stock < 1f;`; `Draw`: `if (p.Count == 0) { return null; }`.
- **What happens:** The stock ceiling retains the original geology, but the output pool scans currently surviving resource rocks. After the last eligible rock is mined, stock remains positive and regrows. Panners keep receiving jobs, earning XP and finishing with `pan=rivercarriesnothing`; those failed sessions never consume the stock that permits more jobs.
- **Repro:** Initialize a positive placer stock, mine every rock yielding a configured placer mineral, and leave a panning spot enabled.
- **Suggested check:** **Cheap live reads:** confirm `stock > 0`, `poolCount == 0`, and repeated panning jobs. Job selection should stop when no output is drawable.
- **Confidence:** high.

**F8 — HIGH — Fill-in destroys liquid beside a pond that has room**

- **Where:** `RM_MapComponent_Excavation.cs`, `Displace`: `if ((IsExcavated(n) || IsSourceCell(n)) && !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[n]))`.
- **What happens:** Displacement visits excavations and wet natural sources, excluding dry natural beds. The return leg can credit those beds, but displacement never reaches it. A completely drained pond therefore cannot receive displaced liquid even when its stock has ample capacity.
- **Repro:** Drain a pond completely. Fill a canal cell beside its dry bed with water, then fill that canal cell in. With no other receivers, the water is reported destroyed.
- **Suggested check:** **Offline adapter case:** place one full canal cell beside a compatible dry bed with available stock capacity. Filling in should credit the pond and leave the overflow total unchanged.
- **Confidence:** high.

**F9 — HIGH — The displacement walk declares overflow before searching the whole channel**

- **Where:** `RM_MapComponent_Excavation.cs`: `while (queue.Count > 0 && remaining > 0 && walked < MaxComponentCells)` followed by `ReportOverflow(from, remaining);`.
- **What happens:** After 6,000 visited cells, remaining liquid is destroyed even if the queue still leads to available channel capacity or a receptive pond. This violates the specified exception: destruction is allowed when there is nowhere to put the liquid, not when the search budget expires. This cap also ignores the configurable network cap used by the kernel.
- **Repro:** Make a connected channel whose only free capacity lies beyond the displacement walk’s limit. Fill in a full cell at the opposite end.
- **Suggested check:** **Offline SelfTest/python case:** a corridor just beyond the cap, full except for its final cell. Assert conservation and delivery to that cell.
- **Confidence:** high.

**F10 — HIGH — A terminating flood discards its unspent reservoir**

- **Where:** `Flood_FlowWorks.cs`: `if (Find.TickManager.TicksGame > ExpiryTick) { Destroy(); ... }` and the `frontier.Count == 0` destruction branch.
- **What happens:** Both branches destroy the release while `remainingVolume` can still be positive. Neither transfers, refunds, retains nor reports that remainder. Disabling the liquid mid-release makes all candidates fail, exhausts the frontier, and reaches this path.
- **Repro:** Start a release with more volume than its reachable cells can accept, or disable its liquid while it is spreading. Observe the release disappear with positive remaining volume.
- **Suggested check:** **Offline lifecycle case:** terminate a blocked release holding a known remainder and assert that the remainder survives in a reservoir or an explicit transfer.
- **Confidence:** medium. Discarding the recorded remainder is certain; the upstream `Configure` callers and their source debits were not supplied, so the complete liquid-ledger loss cannot be verified here.

**F11 — HIGH — Flood eligibility rejects partially filled channels and wet connecting cells**

- **Where:** `Flood_FlowWorks.cs`, `CanFloodInto`: `if (t == null || t.IsWater) { return false; }`.
- **What happens:** This test runs before engine ownership handling and reads `TerrainAt`, including temporary fill terrain. A partially filled water channel is rejected despite having room. An already-wet inlet also prevents the release from reaching dry channel cells beyond it. The depth-aware payment logic in `PlaceFluid` never gets a chance to handle either case.
- **Repro:** Put one water level in a deeper inlet cell, with empty channel cells beyond it. Start a compatible release beside the inlet and compare against an entirely dry inlet.
- **Suggested check:** **Offline flood-adapter case:** vary inlet fill from zero to partially full while keeping available capacity and release volume constant. Compatible wet cells should permit filling or onward traversal.
- **Confidence:** high.

**F12 — HIGH — Partial dig-find placement bypasses the loose-find budget**

- **Where:** `RM_DigDiscovery.cs`: `if (!GenPlace.TryPlaceThing(made, lip, map, ThingPlaceMode.Near, out Thing placed)) { return; }`, before `budgetLeft -= cost;`.
- **What happens:** Vanilla `GenPlace.TryPlaceThing` in Near mode can merge part of a stack and still return false—the supplied placer code explicitly handles that same behavior. Dig discovery instead returns without charging anything. Ore already merged onto the map is free, defeating the per-map extraction ceiling.
- **Repro:** Arrange a constrained bank with room for part of a find in an existing compatible stack but nowhere for the remainder. Trigger a successful find and compare stack growth against budget reduction.
- **Suggested check:** **Offline placement-shim case:** merge three units, leave the remainder unplaced, return false, and assert that the budget falls by exactly three.
- **Confidence:** high.

## Outside this slice

The missing implementations needed to close the remaining questions include `RM_LiquidStock`, `RM_StockMath`, `RM_DriverInputs`, `RM_Volume`, `FluidDef`, excavation settings/change handlers, pocket-grid and room invalidation, liquid fire/heat/fill effects, river-current helpers, and flood creation/debit callers. Terrain and Thing XML is also absent.

No actual Harmony patch implementations were supplied, so this review cannot validate their RimWorld 1.6 targets, pawnless behavior, PathFinder job/grid integration, or cache invalidation. I found no basis here to claim a new ID-keyed static-table reload bug.

No C# file appears truncated. `known_behaviours.md` intentionally contains truncated ledger heads. The natural-bodies design document also appears internally truncated/corrupted at **`- A source sca### 8.5 Tank sizes — ruled`**.