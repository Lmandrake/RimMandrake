SUBJECT: FlowWorks (RimWorld 1.6 mod, C# + XML defs). Slice: FlowWorks_4liquids.

Reviewed only the supplied text. Repros below include deliberately unusual def configurations. No RimWorld runtime tests were run; the blast-coverage arithmetic was checked with a direct translation of the supplied algorithm.

1. **Failed placement loses both the container and its paid contents**  
   **Severity:** data loss  
   **Location:** `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_FillBottle.cs`, `MakeNewToils`, final toil:
   ```cs
   carried.Destroy();
   filled.stackCount = 1;
   GenPlace.TryPlaceThing(filled, pawn.Position, Map, ThingPlaceMode.Near);
   ```
   The terrain debit has already succeeded. Placement failure leaves an unspawned, unowned replacement after destroying the input. The same unchecked placement exists in `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_EmptyBottleIntoTank.cs` and `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_WashBottle.cs`, also in their final toils. `FillBottleFromTank` already uses `PlacePaidFor`; these three do not.

   **Repro:**
   1. Start one of those jobs with valid inputs and sufficient stock.
   2. In a test patch, force its final `GenPlace.TryPlaceThing` call to return false without spawning or merging the replacement.
   3. Complete the job. Inspect the destroyed input, debited stock/credited tank, and unowned replacement.
   4. Save/load: the replacement has no persistent holder.

   **Confidence:** high. The mutations precede placement, and the return value is discarded.

2. **Tank acceptance overflows into negative stock**  
   **Severity:** data loss  
   **Location:** `src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidTank.cs`, `CanAccept` and `TryAddLiquid`:
   ```cs
   return storedUnits + units <= Capacity;
   storedUnits += units;
   ```
   A positive input can wrap the sum negative, pass the capacity check, and make an occupied tank report `Empty`.

   **Repro:**
   1. Give a tank one unit of a valid liquid.
   2. From a script, call `tank.TryAddLiquid(tank.storedLiquid, int.MaxValue)`.
   3. Under normal unchecked arithmetic, it returns true and sets `storedUnits` to `int.MinValue`.
   4. Inspect the tank: its previous contents have become inaccessible, and another liquid can pass the identity check because `Empty` is true.

   **Confidence:** high under unchecked compilation. Checked compilation would instead throw at this boundary; neither path safely refuses the input.

3. **Off-map reversion destroys contents when their holder rejects the replacement**  
   **Severity:** data loss  
   **Location:** `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_CompLiquidRevert.cs`, `Revert`:
   ```cs
   if (!owner.TryAdd(made) && !made.Destroyed)
   ```
   Its off-map fallback is:
   ```cs
   made.Destroy();
   ```
   The original has already been removed and destroyed. There is no rollback when the new def is unacceptable to the holder.

   **Repro:**
   1. Put a reverting stack in an off-map `ThingOwner` whose acceptance rules allow the original def but reject the target def.
   2. Advance its revert comp past the threshold.
   3. Check the owner and both things: the original is destroyed, and the refused replacement is destroyed too.
   4. Repeat with partial acceptance to exercise loss of the remaining stack.

   **Confidence:** high for rejecting off-map holders. This does not imply every ordinary caravan inventory rejects the replacement.

4. **Queued astrofuel blasts survive removal of their fuel and firefoam**  
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs`, `RunDetonation`, `ConsumeDetonatedCell`, and `NotifyExplosionAt`:
   ```cs
   while (ex.FillAt(c) > 0 && guardLv++ < 16 && BurnOf(BurnableFluidAt(map, ex, c)) == RM_FuelBurn.Detonation)
   ```
   The separate blast entry executes unconditionally:
   ```cs
   GenExplosion.DoExplosion(c, map, detRadius[done], DamageDefOf.Bomb, null,
   ```
   Consumption rechecks the fuel; the scheduled explosion does not. Firefoam removes ordinary burning/pending state but never cancels detonation entries.

   **Repro:**
   1. Ignite a sufficiently long astrofuel channel to queue future blast anchors.
   2. Pause before a distant anchor is due.
   3. Script-drain that anchor and replace its contents with water. Alternatively call `NotifyExplosionAt` there with `DamageDefOf.Extinguish`.
   4. Resume through its scheduled tick. Its Bomb explosion still executes.

   **Confidence:** high. The queue contains cell/kind/time/radius only, and neither fuel removal nor smothering invalidates blast entries.

5. **Empty and filled container rules can turn one bottle cycle into a liquid duplicator**  
   **Severity:** wrong behaviour  
   **Locations:**  
   `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_FillBottleFromTank.cs`, final toil:
   ```cs
   int units = RM_ContainerMaterials.UnitsIn(carried, liquid, size);
   ```
   `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_EmptyBottleIntoTank.cs`, final toil:
   ```cs
   int units = RM_ContainerMaterials.UnitsIn(carried, ext.liquid, ext.size);
   ```
   These calls inspect different ThingDefs. `RuleFor` reads each current def’s material extension, and no actual filled quantity is stored.

   **Repro:**
   1. Give a metal empty bottle a capacity factor of 1 and its filled sibling a factor of 2.
   2. Fill that empty bottle from a tank: a 1.5 L base bottle debits 15 units.
   3. Empty the resulting filled bottle into a Fill tank: it credits 30 units.
   4. Repeat. Reversing the factors destroys volume instead.

   **Confidence:** high for differing sibling rules. The supplied code neither enforces equal rules nor preserves the debited quantity. `MakeContainer` changing incompatible stuff can introduce the same mismatch.

6. **Reversion preserves item count without preserving represented volume**  
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_CompLiquidRevert.cs`, `Revert`:
   ```cs
   int count = parent.stackCount;
   Thing made = RM_LiquidBottleUtility.MakeContainer(to, parent);
   made.stackCount = count;
   ```
   Source and target liquids independently author litres per container. No validation requires their capacities to agree.

   **Repro:**
   1. Define liquid A with 1.5 L bottles and reversion to liquid B with 3 L bottles.
   2. Fill one A bottle from a tank, spending 15 units.
   3. Let it revert.
   4. Empty the B bottle into a tank: it contributes 30 units. Swap the capacities to demonstrate loss.

   **Confidence:** high for unequal authored capacities. This is a supported-schema edge case, not evidence that the unseen shipped registry currently contains that mismatch.

7. **Replacing burning liquid transfers the old liquid’s accumulated burn debt**  
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs`, `Maintain` and `BurnPulse`:
   ```cs
   FluidDef fluid = BurnableFluidAt(map, ex, c);
   if (fluid == null || IsSmothered(map, c) || (effects && RainDouses(map, c)))
   ```
   `BurnPulse` subsequently reuses:
   ```cs
   int acc = burning[i];
   ```
   `Maintain` never compares the current fluid with `burningFluid[i]`. A different burnable liquid retains the old accumulator.

   **Repro:**
   1. Ignite a tar-filled excavation.
   2. For a short scripted test, set its burning accumulator to 59,000 ticks.
   3. Between maintenance checks, drain it completely and refill it with chemfuel.
   4. Run maintenance and a burn pulse with inferno enabled.
   5. The new chemfuel inherits the tar’s accumulated ticks and can lose every level immediately at the 300-tick inferno rate.

   **Confidence:** high. Identity is recorded at ignition but never checked on this transition.

8. **Normal-ticking bottled defs never revert**  
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_CompLiquidRevert.cs`, injector constructor:
   ```cs
   if (from.tickerType == TickerType.Never)
   {
       from.tickerType = TickerType.Rare;
   ```
   The comp advances only through `CompTickRare` and `CompTickLong`; it has no `CompTick` override. Existing `TickerType.Normal` defs remain Normal.

   **Repro:**
   1. Before startup injection, make a reverting filled-container def use `TickerType.Normal`, as another ticking comp could require.
   2. Spawn it and wait several revert periods.
   3. Inspect `Age`: it remains zero.
   4. Change that fixture to Rare and repeat; reversion works.

   **Confidence:** high. The injector leaves precisely the unsupported ticking mode untouched.

9. **Missing fluid identity becomes a wildcard for carried burn progress**  
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs`, `TakeCarried`:
   ```cs
   bool same = !carriedFluid.TryGetValue(i, out FluidDef cf) || cf == null || cf == fluid;
   ```
   Both a missing entry and a null def explicitly match every fluid. This contradicts the stated purpose of saving fluid identity.

   **Repro:**
   1. Create a fresh carried-progress entry with a large accumulator and a current `carriedTick`.
   2. Leave its `carriedFluid` missing or null, representing incomplete legacy data or an unresolved removed def.
   3. Ignite a different burnable liquid on that cell or an adjacent cell within 600 ticks.
   4. It inherits the unrelated progress. A direct reflective call to `TakeCarried` also demonstrates the erroneous match.

   **Confidence:** high. The wildcard behaviour is explicit, including after the load guards create an empty identity dictionary.

10. **Reload resets the effects phase, allowing repeated saves to suppress fire effects**  
    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs`, field declarations, `ExposeData`, and `Tick`:
    ```cs
    private int checkCount;
    checkCount++;
    Maintain(map, ex, checkCount % EffectEvery == 0);
    ```
    `checkCount` is not scribed. The next-check time and burning state survive, but the alternating effects phase does not.

    **Repro:**
    1. Ignite ordinary liquid in dry weather. The first maintenance check increments the counter to 1 and skips effects.
    2. Save and reload before the next check.
    3. That next check again increments a fresh counter to 1 and skips effects.
    4. Repeat after each check. Heat, pawn ignition, and rain-douse rolls never execute while burning state persists.

    **Confidence:** high. This follows directly from the unsaved counter and persisted schedule.

11. **Blast-anchor coverage leaves holes in the supposedly continuous detonation**  
    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/RM_FuelFireMath.cs`, `ChooseAnchors` and `BlastRadiusFor`:
    ```cs
    if (Math.Max(Math.Abs(x[a] - x[k]), Math.Abs(z[a] - z[k])) < s)
    ```
    ```cs
    return Clamp(Math.Max(BlastRadius(scale), spacing * 0.8f), 1.9f, 7.9f);
    ```
    Anchor exclusion uses Chebyshev distance. The resulting circular blast radius does not guarantee coverage, especially at body boundaries or after spacing increases.

    **Repro:**
    1. Generate BFS-ordered coordinates for a 139×139 square, originating at a corner.
    2. Call `PlanDetonation` with production arguments: 1, 400, 4, 240, 3.
    3. Compute radii with scale 1.
    4. The translated algorithm returns spacing 10, 196 anchors, and radius 7.9. **363 consumed cells lie outside every blast radius.** For example, the far boundary cell at relative `(0,138)` is eight cells from its nearest anchor.
    5. A smaller counterexample is a 3×3 square at scale 0.1: its opposite corner escapes the sole radius-2.4 blast.

    **Confidence:** high. These are concrete geometric counterexamples checked against a direct translation of the supplied arithmetic.

12. **Per-tick detonation budgets do not budget the expensive planning work**  
    **Severity:** perf  
    **Locations:**  
    `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs`, `StartDetonation`:
    ```cs
    for (int head = 0; head < bfsCell.Count && bfsCell.Count < RM_FuelFireMath.MaxDetonationCells; head++)
    ```
    `src/RimMandrake/FlowWorks/Source/RM_FuelFireMath.cs`, `PlanDetonation`:
    ```cs
    int count = ChooseAnchors(x, z, spacing, anchor);
    ```
    One call synchronously walks up to 20,000 cells, allocates arrays/lists, repeatedly rebuilds anchor buckets while increasing spacing, sorts the schedule, and merges it. `AdvanceFront` permits eight new bodies in one check. The 400-cell/four-blast execution budgets do not constrain this work.

    **Repro:**
    1. Script eight disconnected, near-20,000-cell astrofuel regions on a sufficiently large test map.
    2. Queue one ignition in each for the same check.
    3. Profile that single `Tick`.
    4. Observe all eight full plans being constructed synchronously before their budgeted execution.

    **Confidence:** high about the concentrated work; medium about the resulting hitch magnitude, which requires an actual runtime profile.

### Outside this slice

- **Explosion provenance across reload:** `RM_LiquidFire` does not scribe `blastHops`, `blastFromSource`, or `blastTick`; `NotifyExplosionAt` treats an unknown explosion ID as direct ignition. Whether this produces a normal-save source-reach bypass requires the missing vanilla `Explosion` persistence and callback lifecycle.
- **Live-list mutation:** `LiquidIgnitionMapComponent.ScanForIgnition` traverses `ThingsOfDef(Fire)` while potentially spawning more fires. Corrosion likewise damages pawns while traversing `AllPawnsSpawned`. Runaway same-pass ignition or skipped pawns requires confirming those returned lists’ mutation semantics.
- **Planet layers:** both liquid-tag lookups discard everything except `tileId`. A cross-layer collision needs confirmation from the omitted `PlanetTile` implementation.
- The flow kernel, hose internals, pocket-grid/collapse logic, river implementation, River Colors settings migration, XML wiring, and removal handling are absent. The supplied design and validation prose cannot establish their correctness.