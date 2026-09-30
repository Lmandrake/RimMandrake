# SOLAR_HEAT_EXPOSURE_1 — tranche 2 report

Status: LANDED, tranche 2. The item stays open for its quicktests and the owner's live sitting. 2026-09-29. Nothing was deployed or live-tested.

## Substrate read
- Tranche 1 (`cea416ce3..8a0ba70df`) and shade gear (`5769d2dd0`) are in this tree. `RM_MapComponent_ShadeGrid` keeps a per-cell `exposure` array on sun-heat maps and recomputes every 2000 ticks, or when gear changes.
- **Engine seams, checked in RimSage (decompiled 1.6):**
  - Core `Animal` ThinkTree: `Animal_PreMain` sits after Downed, Burning, both MentalState subtrees, ReactToCloseMeleeThreat, QueuedJob, ForcedGoto, RopedPawn and LordDuty, and before SatisfyBasicNeeds. `Animal_PreWander` sits just before the wander nodes.
  - `ThinkNode_SubtreesByTag` orders the trees that share a tag by `insertPriority`, highest first.
  - `HediffGiver_Heat.OnIntervalPassed`: when felt temperature is above SafeMax (comfortable max + 10), severity rises by `max(curve(over) × 6.45e-5, 0.000375)` each interval. The interval is 60 ticks (`Pawn_HealthTracker`, `IsHashIntervalTick(60)`). Recovery happens only below the comfortable max.
  - `Pawn_PathFollower.CostToMoveIntoCell` reads `curJob.locomotionUrgency` on every cell: Sprint is ×0.75, Jog ×1, Walk ×2 (minimum 50), Amble ×3 (minimum 60).
  - `GenDraw.DrawFieldEdges(List<IntVec3>, Color, …)`, and `Pawn.DrawExtraSelectionOverlays` (an override, so it can take a postfix).
  - Heatstroke becomes visible at 0.04 severity.

## §5 Shade-patch graph
- **`RM_ShadePatchGraph.cs`** uses System only, so the selftest compiles it directly.
  - **Patches** are 8-connected groups of walkable cells whose exposure is at or below `shadeExposureMax` (0.35), plus cells inside enclosed roofed rooms. A group smaller than `minPatchCells` (2) is a fleck and counts as open sun.
  - **Rims** are patch cells that touch walkable sun.
  - **The distance field** is a multi-source Dijkstra over walkable sun cells, starting from every rim. It uses a Dial bucket queue, costs 10 per cardinal step and 14 per diagonal, and stops at a cap.
  - **Edges** are placed where the fronts from two patches meet. Each edge keeps its cost and its leave-from and arrive-at rim cells.
  - **Cost:** O(cells), with no per-tick work.
- **In `RM_MapComponent_ShadeGrid`**:
  - `GridVersion` goes up on every recompute.
  - `PatchGraph` is lazy. The first request after a recompute rebuilds it, so it is built at most once per 2000 ticks, and only when a hop, an escape or the ring asks for it.
  - `ShadeHopsApply` gates it: the map must have sun heat, an exposure layer, and a heat kind other than ambient. On any other map the graph is never built.
  - The room lookup runs only on roofed, walkable, exposed cells.

## §5 Rest-dash-rest job givers
All of this is in `RM_ShadeHop.cs`, and both think trees are in `Defs/ThinkTreeDefs/RM_ThinkTree_ShadeHop.xml`.

**Who it applies to (`Eligible`):** wild animals only, meaning no faction, so tamed and drafted animals are excluded. The animal must not be downed, in a mental state (this excludes manhunters) or roped, and its race must not carry `RM_SunDashExtension.exempt`. The map must be a sun-heat map that is not ambient. Fleeing and melee reactions are started directly or sit earlier in the tree, so they still come first.

**`RM_JobGiver_SunEscape`** (Animal_PreMain, insertPriority 10):
- An animal standing in open sun sprints to the nearest shade within `maxDashCells`.
- "Nearest" comes from the graph's distance field, or from a lying mirrak's false shade.
- This runs before needs, so a grazer steps out to eat and then dashes back.

**`RM_JobGiver_ShadeHop`** (Animal_PreWander, insertPriority 10, so it runs before the existing ShadeSeekingWander):
- In shade, an animal rests if it is carrying at least half its dash budget as Heatstroke. Otherwise, with `hopChance` (0.35), it hops. The rest is a Wait job; the animal lies down if it is tired.
- A hop picks a neighbouring patch whose edge is within dash range, weighted by √(patch size). A lure also counts. The animal then does the following:
  1. walks to its own rim;
  2. pauses there for `rimPauseTicks` (45–120), facing the target;
  3. sprints across.
- If no patch is in range, the animal mills about inside its own patch or rests. It never wanders out.
- If it is in the sun at wander time and the escape found nothing, vanilla wander runs, with sun pathing.

**`RM_JobDriver_ShadeDash`** (JobDef `RM_ShadeDash`) walks to TargetA, pauses for `job.count` ticks facing TargetB, then sets `locomotionUrgency = Sprint` and goes to TargetB.

**Dash range (`RM_DashMath` + `RM_ShadeHop.RangeCost`):**
- It works from the animal's felt heat in full sun: outdoor temperature plus tranche 1's body-size-scaled offset. That is compared with its SafeMax, and vanilla's Heatstroke step per 60 ticks gives the time it can tolerate.
- The budget is `dashHeatstrokeBudget` (0.008) minus the Heatstroke it already has.
- Tolerated ticks are divided by its sprint ticks per cell (`TicksPerMoveCardinal` × 0.75).
- The result is multiplied by the strictness dial, then clamped to [3, 24] cells.
- If the sun never pushes the animal past its SafeMax, the range is the cap. An animal already out of budget gets 0 and stays in its shade.

**The mirrak:** a lying false-shade pawn counts as shelter for resting, and as a destination for escapes and hops. (This is the `PerceivedShadeAt` requirement from tranche 1.)

## §6 Drafted-pawn range ring
- **How it is drawn:** `RM_DashRing`, from a postfix on `Pawn.DrawExtraSelectionOverlays`. It appears only for a drafted pawn on a sun-heat map where the heat kind is not ambient. It is drawn with `GenDraw.DrawFieldEdges`, in orange.
- **What it marks:** the cells the pawn can reach and still get back into shade. For each cell, the straight-line (octile) distance out plus the field's walk back to shade must fit the range.
- **The range:**
  - Felt heat is net of worn shade, so a parasol widens the ring.
  - The budget is `ringHeatstrokeBudget` (0.035, just below visible Heatstroke) minus the Heatstroke it already has.
  - Speed is jog, not sprint.
  - The cap is `ringMaxCells` (60).
- **Cost:** the cell set is cached per pawn and rebuilt only when the pawn moves, when the grid version changes, or every 15 ticks. The scan covers only a (2r+1)² square.

## Mod Settings
These are in Creature Behaviors, entry 41, under Sun heat. All are on by default:
- **Animals hop shade to shade**: `shadeHopEnabled`.
- **How far they will dash**: `shadeHopRangeMultiplier`, from 25% to 200%. Lower is stricter.
- **Back-to-shade ring**: `dashRingEnabled`.

The new `RM_SunHeatExtension` fields are: `shadeExposureMax`, `minPatchCells`, `dashHeatstrokeBudget`, `min`/`maxDashCells`, `hopChance`, `restTicks`, `rimPauseTicks`, `ringHeatstrokeBudget` and `ringMaxCells`. There is also a new race extension, `RM_SunDashExtension`, with `exempt` and `rangeFactor`.

## Verification
- **Build:** `dotnet build` of Creature Behaviors (Release) succeeds with 0 errors and 0 warnings. The DLL and its `.srchash` are committed.
- **XML:** `RM_ThinkTree_ShadeHop.xml` and `RM_JobDefs.xml` both parse.
- **`selftest_sun_heat.py`: 28 of 28 pass**, 7 of them new:
  - graph edges, with cost measured rim to rim;
  - the cap and walls cut hops;
  - flecks are dropped;
  - diagonal steps cost 14 and edges are symmetric;
  - dash range grows with body size, is 0 when the animal is already hot, and is the cap when the sun is cool;
  - the strictness dial, and the step matching vanilla's heat giver;
  - the go-and-return ring.

  With the test's numbers (outdoor 30°C, SafeMax 40, budget 0.012) the dash range was 22 cells at size 0.3 and 40 (the cap) at size 1. So under the old default of 0.012/40, only small animals were limited by heat. **The defaults were tightened** to budget 0.008 and a 24-cell cap for that reason.
- **`run_selftests.py`: 77 of 79**, the same as the tranche 1 baseline. The one failure is the known `selftest_deployed_biome_refs`, and one test is unmeasured (`bridgetools/selftest_tool_metadata`).

## Unverified / remaining
- **Nothing has been run in the game.** Needs a quicktest on a Long Shade map:
  - animals rest, pause at the rim and sprint;
  - no think loop, and no animal starves in a patch with no food;
  - the ring draws around a drafted colonist;
  - the graph's rebuild cost on a full-size map.
- **Known gaps:**
  - A wild animal's `JobGiver_GetRest` (in SatisfyBasicNeeds, which runs before PreWander) may pick a sleeping spot in the sun. The animal dashes back when it wakes, but it heats while it sleeps.
  - Hunting and grazing trips still cross the sun, on sun-cost paths.
  - The graph ignores parasol shade and moving casters (the gloomcast).
- **Every number is an invented first value.** The owner-watched sitting in the item's criteria rules on strictness, meaning the dial, the budget and the cap.
