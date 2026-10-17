SUBJECT: FlowWorks (RimWorld 1.6 mod, C# + XML defs). Slice: FlowWorks_4machinery.

Static review of the supplied code only. The repros below were not executed. Locations use method names rather than invented line numbers.

1. **A pipe API that mutates and then throws duplicates or destroys liquid** — **data loss**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidPipeAdapter.cs`, `CompTickRare`, both boundary callbacks.

   ```csharp
   try { if (ask > 0f) addResource.Invoke(storage, new object[] { ask }); }
   catch (Exception) { broken = true; return 0; }
   ```

   An exception is treated as proof that nothing crossed the boundary. The saved storage balance is never read back after that exception. `Move` consequently restores the FlowWorks side even if the external mutation already happened. The drawing callback has the inverse failure.

   **Repro:** (1) Add a test storage comp exposing the expected reflection API. (2) Implement `AddResource(float)` to increase `AmountStored`, then throw. (3) Open a feeding adapter and run one rare tick. Its input tank is restored while external storage retains the addition. (4) Repeat with `DrawResource` subtracting before throwing: external resource disappears without reaching the tank.

   **Confidence: high.** Both exception paths and the corresponding rollback behaviour are visible.

2. **Composite transfers conceal failed internal rollbacks** — **data loss**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidTransfer.cs`, `RM_TransferLeg.Split`; also `All`.

   ```csharp
   for (int j = i - 1; j >= 0; j--) undo(j, partUnits(j));
   return 0;
   ```

   Failed internal undo results are discarded. The outer `Move` receives zero and cannot report that the composite leg left mutations behind. `RM_MoveOutcome.Lost` remains zero.

   **Repro:** (1) Create a reversible source containing ten units. (2) Create a destination `Split` with two five-unit parts. Make the first addition succeed, the second refuse, and the first part’s undo refuse. (3) Call `Move(10, ...)`. The source gets its ten units back, the first destination retains five, and the outcome reports no loss. The analogous source-side failure deletes units.

   **Confidence: high.** This is reproducible entirely with the supplied transfer classes and test closures.

3. **Destroying an adapter discards its fractional credit or debt** — **data loss**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidPipeAdapter.cs`, `carry`, `PostExposeData`; no destruction settlement exists in the class.

   ```csharp
   public float carry;
   Scribe_Values.Look(ref carry, "RM_adapterCarry", 0f);
   ```

   Carry is real resource according to the boundary invariant. Saving preserves it; destroying the adapter does not settle it anywhere. Positive carry is destroyed resource. Negative carry is an unpaid resource delivery whose debt disappears.

   **Repro:** (1) Use a test storage API that partially accepts or supplies a request, leaving nonzero carry. For normalized `perUnit = 1`, a 0.75-unit partial send leaves negative carry while the tank units are restored. (2) Deconstruct the adapter. (3) Rebuild and reopen it. The external net keeps that delivery, but the replacement adapter owes nothing. A partial take demonstrates the loss of positive carry.

   **Confidence: high.** Settlement arithmetic and saved ownership are explicit; the class has no destruction recovery.

4. **Foreign machines can still consume player tanks with theft disabled** — **wrong behaviour**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs`, `MapGraph.OriginPipeCells`.

   ```csharp
   if (!(origin is Thing t) || !t.Spawned)
   IEnumerable<IntVec3> around = RoleOfThing(t) == RM_NetRole.Tank ? GenAdj.CellsAdjacentCardinal(t) : GenAdj.CellsAdjacent8Way(t);
   ```

   `RoleOfThing` correctly returns `None` for excluded foreign machinery. This origin path nevertheless seeds its adjacent pipes. `RM_NetComponents.AttachNodes` also accepts those seeds, allowing the excluded machine to reach player tanks without appearing among component members.

   **Repro:** (1) Spawn a foreign converter beside a pipe run containing player input and output tanks. (2) Supply its power/fuel requirements. (3) Disable liquid theft. (4) Run its rare ticks. Its pipe-origin search still reaches the player tanks and can process their liquid.

   **Confidence: high.** The excluded role is never checked before origin seeding, and converter operation has no faction guard.

5. **Owners using their own connected tank are charged as player theft** — **wrong behaviour**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidTheft.cs`, `TheftTick`.

   ```csharp
   bool touched = t.theftSeenUnits >= 0 && RM_LiquidTheftMath.Touched(t.theftSeenUnits, t.theftSeenLiquid, t.storedUnits, t.storedLiquid);
   if (!touched || victim == null || victim.defeated || !PlayerReaches(t))
   ```

   Player reachability establishes only that theft was possible. It does not establish who changed the tank. An owner’s converter changing its own tank passes this test whenever an idle player attachment shares the network.

   **Repro:** (1) Give a foreign faction a functioning converter and its own supplied tank. (2) Attach an idle player tank to the same pipe component; disable all player consumers. (3) Establish the theft baseline. (4) Let the foreign converter operate while an awake owner witnesses its tank. The player receives the accusation and subsequent charges.

   **Confidence: high.** Actor attribution is replaced by stock difference plus potential reachability.

6. **Hose routing changes with the first client queried, and can charge an avoidable hose** — **wrong behaviour**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs`, `Visit`, `RouteIn`.

   ```csharp
   if (nodeOf.TryGetValue(v, out KeyValuePair<RM_NetComponent, int> e))
   List<RM_NetLink> p = Path(c, i, j);
   if (best == null || p.Count < best.Count) best = p;
   ```

   Routing minimizes hose count only over paths in the chosen BFS tree. Cycle edges are discarded. That tree minimizes neither hose count nor query-order dependence.

   **Repro:** (1) Use an injected graph with pipe cells `P0—P1—P2—P3—P4`, plus one hose directly connecting `P0` and `P4`. Attach endpoint tanks and a middle client at `P2`. (2) Query an endpoint first: BFS incorporates the hose shortcut, and the endpoint route contains it despite an all-pipe route. (3) Recreate the cache and query the middle client first: both endpoint pipe paths enter the tree, yielding a zero-hose route. (4) With hose holding enabled, these routes produce different hose filling and eventual spills.

   **Confidence: high.** The graph and traversal are entirely expressible through the supplied kernel interface.

7. **A blocked small recipe permanently prevents a larger converter recipe accruing enough budget** — **wrong behaviour**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidConverter.cs`, `CompTickRare`, candidate budgeting.

   ```csharp
   float capped = RM_ConversionMath.CapAccrued(accrued, step.InputUnits, perTick);
   accrued = cand[pick >= 0 ? pick : 0].capped;
   ```

   When nothing runs, the first candidate decides the machine’s retained budget—even when that candidate is blocked by output capacity. A larger runnable recipe may therefore never reach its batch threshold.

   **Repro:** (1) Configure one converter with a 10 L recipe and a 100 L recipe, accruing 1 L per rare tick. (2) Arrange the 10 L input first in tank order. Keep its output full. (3) Supply the 100 L input and ample output room. (4) Wait indefinitely: retained budget stays capped at 10 L. Removing the first input lets the second recipe eventually run.

   **Confidence: high.** The first blocked candidate repeatedly truncates the shared accumulator.

8. **A converter whose competitor empties the input never registers starvation** — **wrong behaviour**

   File: `src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidConverter.cs`, `CompTickRare`, candidate enumeration.

   ```csharp
   if (tank.Empty || !seen.Add(tank.storedLiquid))
   {
       continue;
   ```

   Rotation is notified only after discovering a nonempty input candidate. A competitor taking the last batch erases the evidence needed to register the waiting converter.

   **Repro:** (1) Connect two identical converters to the same input store and give both sufficient processing budget. (2) In a script, replenish exactly one batch, then tick converter A followed by B. (3) Repeat. A consumes the entire input; B discovers no input candidate and never calls `Starved`. A therefore never yields.

   **Confidence: high.** Empty-store handling bypasses all rotation bookkeeping.

9. **Shared tanks do not imply shared rotation keys** — **wrong behaviour**

   Files:
   - `src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidConverter.cs`, `CompTickRare`
   - `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs`, `RM_ConsumerRotation.Key`

   ```csharp
   int storeId = tanks.Count > 0 ? tanks.Min(t => t.thingIDNumber) : 0;
   public static object Key(object liquid, int storeId) => liquid == null ? null : (object)(liquid, storeId);
   ```

   Overlapping stores can have different lowest tank IDs. Two consumers competing for the same liquid in the same tank then have unrelated fairness records.

   **Repro:** (1) Place two converters touching one shared input tank. (2) Give each a separate, older private tank; ensure those private tanks are not mutually reachable. They may contain unrelated output liquids. (3) Their minimum tank IDs differ. (4) Keep a small input remainder so the losing converter does register `Starved`. Its different key still cannot make the winning converter yield.

   **Confidence: high.** This also follows directly from calling `Served`, `Starved`, and `MayDraw` with the two generated keys.

10. **Budget caps silently reduce configured processing rates** — **wrong behaviour**

    Files:
    - `src/RimMandrake/FlowWorks/Source/Machinery/RM_ConversionMath.cs`, `CapAccrued`
    - `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_LiquidReaction.cs`, `CompTickRare`

    ```csharp
    return Math.Min(accrued, Math.Max(inputUnits, perTick));
    accrued = System.Math.Min(accrued + perTick, System.Math.Max(1f, perTick));
    ```

    Both machines truncate newly earned budget before spending whole batches. Fractional overshoot is discarded even during continuous, fully supplied operation.

    **Repro:** (1) Run a converter with a 300-unit input batch and 200 units accrued per rare tick. It processes 300 units every two ticks, although those ticks earned 400. (2) Run a reactor accruing 0.3 batches per tick. Every fourth tick, 1.2 becomes 1 before processing, permanently losing 0.2. (3) Compare long-run output with the configured rates.

    **Confidence: high.** These examples require only the supplied arithmetic. An idle-backlog cap should not discard the current working interval’s remainder.

11. **A reactor stops on a yielded recipe instead of trying another runnable reaction** — **wrong behaviour**

    File: `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_LiquidReaction.cs`, `CompTickRare`.

    ```csharp
    if (n <= 0)
    {
        status = "RMFlow_ReactorWorking".Translate(r.reactantA.label, r.reactantB.label, r.ProductLabel);
    ```

    The immediately following statement is `return`. Once the first sufficiently supplied reaction loses its rotation turn, later independent reactions are ignored.

    **Repro:** (1) Configure reactions A+B and C+D, in that order. Supply both pairs and one batch of accrued budget. (2) Arrange a competing consumer so rotation refuses the first reaction this tick. (3) Tick the reactor. It idles despite C+D being runnable. Repeating competition repeatedly wastes available reaction opportunities.

    **Confidence: high.** The rotation refusal sets `n = 0`, and this branch exits the entire candidate loop.

12. **Heat sampling loses power when the per-room cap is reached** — **wrong behaviour**

    Files:
    - `src/RimMandrake/FlowWorks/Source/RM_LiquidHeat.cs`, `Push`, `Apply`
    - `src/RimMandrake/FlowWorks/Source/RM_LiquidHeatMath.cs`, `RoomEnergy`

    ```csharp
    RM_LiquidHeatMath.CellEnergy(k, RM_LiquidHeatMath.NaturalCellLevels, strength) * natScale);
    float e = RM_LiquidHeatMath.RoomEnergy(kv.Value, room.Temperature, room.CellCount, strength);
    return Math.Max(0f, Math.Min(Math.Min(summed, cap), room));
    ```

    Scaling sampled energy preserves its average only before nonlinear room caps and target clamps. Applying those limits afterward systematically loses energy.

    **Repro:** (1) Model two rooms containing 3,000 natural hot cells each, ordered as two contiguous groups in the natural list. Keep both comfortably below 50°C. (2) `SplitBudget(0, 6000, ...)` visits 3,000 cells at scale two. (3) Each interval heats only one room, capped at approximately 700 energy. The next interval heats the other. (4) Processing all sources would give approximately 700 to **each** room every interval. Sampling halves total delivered heat here.

    **Confidence: high.** This counterexample follows directly from the supplied budget and clamp functions.

13. **Saving during the residue delay permanently cancels pending stains** — **wrong behaviour**

    File: `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_FluidResidue.cs`, `RM_MapComponent_FluidResidue.ExposeData`.

    ```csharp
    Scribe_Values.Look(ref statResidueCells, "RM_residueCells", 0);
    ```

    Only the statistic is saved. Neither pending list is serialized or reconstructed.

    **Repro:** (1) Add a test fluid carrying `RM_FluidResidueExtension`, with chance one and valid filth—the slice says no shipped def currently carries it. (2) Remove its temporary terrain just after a 250-tick boundary. (3) Save and reload before the next boundary. (4) Advance past that boundary. The stain appears without reloading, but disappears from the sequence after reloading.

    **Confidence: high.** The pending event exists exclusively in unsaved component lists.

14. **Repeated residue notifications multiply one cell’s stain probability** — **wrong behaviour**

    File: `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_FluidResidue.cs`, `Pending`.

    ```csharp
    cells.Add(c);
    fluids.Add(fluid);
    ```

    Notifications are not deduplicated. At processing time, every queued entry independently rolls against the cell’s final terrain. Intermediate level changes followed by a real drain can therefore produce several rolls for one drained cell.

    **Repro:** (1) Use the residue test def above with chance 0.35. (2) Before a processing boundary, call `Pending(c, fluid)` four times for one now-dry cell, representing repeated removals/refills. (3) Process the queue. Its chance of at least one stain becomes approximately 82%, versus 35% for one notification; multiple successful filth additions are also attempted.

    **Confidence: high.** The queue loop performs one roll per entry and never removes duplicate cell/fluid pairs.

15. **Turning residue off does not stop already queued residue** — **wrong behaviour**

    File: `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_FluidResidue.cs`, `MapComponentTick`.

    ```csharp
    if (cells.Count == 0 || Find.TickManager.TicksGame % 250 != 0)
    ```

    The setting is checked when collecting notifications, but never when executing them.

    **Repro:** (1) With the residue test def enabled and chance one, drain a cell between processing boundaries. (2) Pause and disable `fluidResidueEnabled`. (3) Resume through the next boundary. The queued stain is still created.

    **Confidence: high.** The processing path contains no setting guard.

16. **A legal zero-cost bath recipe still requires a nonempty liquid source to start** — **wrong behaviour**

    File: `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_LiquidBath.cs`, `TryFindSource`, `BenchHasLiquid`.

    ```csharp
    if (have >= ext.UnitsPerCraft && have > 0)
    return bill.billStack?.billGiver is Thing bench && TryFindSource(bench, ext, out _, out _);
    ```

    Zero litres is explicitly allowed by configuration validation and classified as `NoNeed` by `RM_LiquidBathMath.Pay`. The start gate nevertheless requires positive stock or qualifying ground.

    **Repro:** (1) Create a bath recipe naming a valid liquid, no terrains, and `litresPerCraft = 0`. (2) Put the bill on a dry bench with no supplied tank. (3) Compare `PayNow`, which returns `NoNeed`, with `BenchHasLiquid`, which returns false. The `ShouldDoNow` postfix blocks the bill.

    **Confidence: high.** The two supplied eligibility paths directly contradict each other.

17. **Consumer-rotation records grow for the entire lifetime of a map** — **perf**

    File: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs`, `RM_ConsumerRotation`.

    ```csharp
    private readonly Dictionary<object, KeyValuePair<int, int>> served = new Dictionary<object, KeyValuePair<int, int>>();
    private readonly Dictionary<object, Dictionary<int, int>> starved = new Dictionary<object, Dictionary<int, int>>();
    private readonly Dictionary<object, Dictionary<int, int>> forfeitUntil = new Dictionary<object, Dictionary<int, int>>();
    ```

    `Window` expires claims logically, but does not remove them. Demolished stores leave outer keys behind; demolished waiting machines leave inner records behind. Topology revisions do not replace this rotation object.

    **Repro:** (1) Keep one map loaded. (2) Repeatedly build/use/remove independent tank stores and consumers, or script `Served` and `Starved` with fresh store and machine IDs. (3) Advance far beyond `Window`. (4) Inspect dictionary counts: expired records remain. Repeatedly replacing waiting consumers on one persistent store also lengthens `MayDraw` scans.

    **Confidence: high** for unbounded retention; **medium** for the practical performance impact without a long-running fixture.

## Outside this slice

These are unresolved checks, not additional confirmed findings:

- **Bath completion atomicity:** `RM_Patch_LiquidBathCompleted.Postfix` can silently return when `DrawPlan` fails and cannot retract products. Whether ordinary play reaches that unpaid-completion path requires the missing vanilla `JobDriver_DoBill` completion order and other completion patches.
- **Tank material acceptance:** `RM_LiquidNet.Views`/`FillPlan` model capacity and liquid identity, without calling `CanAccept`. Whether an unsuitable empty tank blocks a suitable later tank requires `Building_LiquidTank` and its material rules.
- **Fractional pond credit:** `RM_LiquidSpill.ReturnToPond` rounds partial accepted stock upward with `Ceiling`. If `TryCredit` can accept a nonintegral tank-unit equivalent, the caller subtracts more units than the pond received. The stock and conversion implementations are missing.
- **Topology patch installation:** spawn/despawn/faction hooks are tagged with `universalPipesEnabled`, although hose-only and touching stores also need invalidation. Whether starting with pipes disabled removes those hooks depends on the missing `PatchFeature` implementation.
- Actual mod-removal safety, XML/MayRequire wiring, river currents/weirs, River Colors migration, and pit/pocket-grid behaviour cannot be established from this machinery slice.