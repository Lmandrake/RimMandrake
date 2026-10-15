Found **9 findings**. This is a source audit; the suggested checks have not been run. Paths are relative to `src/RimMandrake/FlowWorks/Source/`. Citations use exact code-line anchors as permitted.

**F1 — HIGH — Digging and restoring a pond can multiply its capacity**

**Where:** `RM_LiquidStock.cs`, `DetachBedCell` / `ReattachBedCell`:

```csharp
body.capacity = RM_StockMath.CapacityWithoutBed(body.capacity, bed, sum);
```

```csharp
if (!body.limitless && sum > 0)
```

Together with `RM_StockMath.cs`, `CapacityWithoutBed`:

```csharp
return bedSum <= 0 || bed <= 0 || bed >= bedSum ? capacity : capacity - capacity * bed / bedSum;
```

**What happens:** Removing the last square retains its capacity, but loses which bed depth that retained capacity represents. Reattaching a different square first makes subsequent capacity scaling wrong.

For example, a completely drained pond with bed depths **2 + 4**, capacity **6**, undergoes:

- Detach the 2-level square: capacity becomes 4.
- Detach the last, 4-level square: capacity stays 4.
- Reattach the 2-level square first: capacity stays 4.
- Reattach the 4-level square: capacity becomes **12**.

Repeating the sequence doubles it again. Refill or returned liquid can occupy this invented capacity.

**Repro:** Drain a mixed-depth pond completely; excavate its shallow squares before its last deep square; fill the shallow squares back to the surface first.

**Suggested check — offline SelfTest:** Chain the production capacity helpers through the sequence above. Assert that restoration in **every order** returns capacity 6.

**Confidence:** High.

---

**F2 — HIGH — Filling containers from terrain creates liquid without debiting the body**

**Where:** `LiquidTypes/JobDriver_FillBottle.cs`, completion:

```csharp
Thing filled = RM_LiquidBottleUtility.MakeContainer(filledDef, carried);
```

The preceding source check calls `RM_LiquidBottleUtility.TryGetLiquidAt`, whose implementation only reads terrain.

**What happens:** The job checks liquid identity, material compatibility and output def, then replaces the empty container. It never computes the material-scaled volume or debits `RM_LiquidStock`. Pumping and bottling therefore do not spend the same stock.

**Repro:** Disable refill, bottle water from a limited pond, and pour those containers into a tank. The tank gains liquid while the pond’s stock stays unchanged.

**Suggested check — cheap live state read:** Record body stock and tank units; fill and empty one barrel. Normalize stock through `volumePerTile` and the tank-unit conversion, then assert equal debit and credit.

**Confidence:** High.

---

**F3 — HIGH — Washing containers consumes no water**

**Where:** `LiquidTypes/JobDriver_WashBottle.cs`, completion:

```csharp
Thing empty = RM_LiquidBottleUtility.MakeContainer(emptyDef, carried);
```

The only water condition is:

```csharp
&& liquid == RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater;
```

**What happens:** Washing requires fresh-water terrain but never debits it. This contradicts the explicit “wash job consumes water” rule. It also permits washing against a source whose visible terrain remains wet while its usable stock is exhausted.

**Repro:** Disable refill and wash a stockpile of dirty containers beside a small fresh-water pond. Its stock never falls.

**Suggested check — cheap live state read:** Compare body stock before and after one completed wash. Assert the intended wash debit, and separately check refusal when that debit cannot be paid.

**Confidence:** High.

---

**F4 — HIGH — Switching source accounting off duplicates stock when transfers continue**

**Where:** `RM_LiquidStock.cs`, both `CanSupply` and `TryDebit`:

```csharp
if (!RimMandrakeFlowWorksSettings.sourceBudgetEnabled)
{
    return true;
}
```

**What happens:** Pumps and other callers can successfully withdraw liquid while the original stock remains untouched. Re-enabling the setting exposes that unchanged reserve again. There is no reconciliation in these methods. Under the brief’s conservation and mid-game-toggle laws, this is a design mismatch even if unlimited sources were historically intended by this switch.

**Repro:** Record a limited pond’s stock; disable source budgeting; pump several levels into a tank; re-enable budgeting. The tank gained liquid without a matching withdrawal.

**Suggested check — cheap live state read:** Run that toggle sequence with refill disabled and compare the combined normalized stock before and after.

**Confidence:** High.

---

**F5 — HIGH — Destruction has no disposition for tank contents or extracted drill liquid**

**Where:** `LiquidTypes/Building_LiquidTank.cs`:

```csharp
public int storedUnits;
```

`Drilling/Building_LiquidDrill.cs`:

```csharp
pendingUnits += survey.TryExtract(wantUnits);
```

Both complete classes contain serialization but no destruction handler that transfers these quantities elsewhere.

**What happens:** Tank contents remain exclusively on the tank object. Drill pending liquid has already been removed from the map reserve and remains exclusively on the drill. Destruction or deconstruction has no shown spill, recovery or refund path. Saving `pendingUnits` protects ordinary reloads, but does not protect removal of its owning building.

**Repro:** Deconstruct a stocked tank. Separately, use a slow drill cycle that leaves fractional `pendingUnits`, then deconstruct the drill before it emits a whole level.

**Suggested check — cheap live state read:** Sum reserve, pending volume, tank contents and emitted liquid before and after each removal. Assert that the removed building’s volume appears in another accounted destination.

**Confidence:** High for the supplied classes; an external destruction hook could change this conclusion.

---

**F6 — HIGH — Failed replacement placement loses liquid after the original has been consumed**

**Where:** `LiquidTypes/JobDriver_FillBottleFromTank.cs`:

```csharp
if (filledDef == null || !tank.TryRemoveLiquid(units))
```

followed later by:

```csharp
carried.Destroy();
```

```csharp
GenPlace.TryPlaceThing(filled, pawn.Position, Map, ThingPlaceMode.Near);
```

Also `LiquidTypes/RM_CompLiquidRevert.cs`, `Revert`:

```csharp
parent.Destroy();
```

```csharp
GenPlace.TryPlaceThing(made, pos, map, ThingPlaceMode.Near);
```

**What happens:** The tank has already been debited, or the original filled stack destroyed, before placement succeeds. The placement return value is ignored. A rejected placement leaves the replacement unspawned and without an owner; there is no rollback or retained pending output. The held-item revert branch explicitly destroys its replacement if `owner.TryAdd(made)` fails.

**Repro:** Complete a tank-fill job or boiling-water reversion where nearby item placement is unavailable. A held-container owner that rejects the successor exercises the other branch.

**Suggested check — offline failure-injection case:** Force placement/owner insertion to return false. Assert that either the original survives, the debit is reversed, or the replacement remains in an accounted owner.

**Confidence:** High.

---

**F7 — HIGH — Disabling sticky limitless classification breaks truncated bodies’ finite capacity**

**Where:** `RM_StockMath.cs`, `IsLimitless`:

```csharp
if (!stickyEnabled)
{
    return false;
}
```

`RM_LiquidStock.cs`, formation:

```csharp
private const int MaxBodyCells = 4000;
```

and extension of an existing body:

```csharp
if (owned.truncated && !cellToBody.ContainsKey(fillFound[f]))
{
    owned.cells.Add(map.cellIndices.IndexToCell(fillFound[f]));
}
```

**What happens:** A truncated body can be classified **limited** when the setting is off. Its capacity is calculated from the initial bounded footprint. Later contacts append further cells without increasing capacity—the accompanying comment assumes every truncated body is limitless. The resulting finite body has more bed volume than its ledger permits, and recession uses that undersized capacity.

**Repro:** Disable sticky limitless classification before first contact with a body larger than 4,000 cells. Pump from it, then contact previously unindexed portions.

**Suggested check — offline integration case:** Exercise a body beyond the collection cap with the setting off. After extension, assert that a limited body’s capacity matches `CapacityOf(body, owner)`.

**Confidence:** High.

---

**F8 — MEDIUM — Unavailable water causes repeated radius searches for every empty or dirty container**

**Where:** `LiquidTypes/RM_LiquidBottleUtility.cs`, `TryFindLiquidCell`:

```csharp
foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, maxDist, true))
```

Called from `HasJobOnThing` in both `WorkGiver_FillBottle.cs` and `WorkGiver_WashBottle.cs`, with another search in `JobOnThing`.

**What happens:** The search is centered on the pawn, but repeated separately for each candidate container. With no suitable water, every candidate pays the complete radius search. With inaccessible water, candidates additionally repeat reachability queries. A bottle stockpile therefore multiplies an otherwise identical failed search across items and workers.

**Repro:** Give several colonists this work on a dry map, or behind an inaccessible pond, with a large empty/dirty-container stockpile.

**Suggested check — cheap live timing:** Measure one unsuccessful scanner pass with 1, 10 and 100 containers. Count liquid-cell lookups and `CanReach` calls; verify the repeated search cost.

**Confidence:** High.

---

**F9 — MEDIUM — Every container transition repairs damaged containers**

**Where:** `LiquidTypes/RM_LiquidBottleUtility.cs`, `MakeContainer`:

```csharp
return ThingMaker.MakeThing(def, stuff);
```

For example, `JobDriver_FillBottle.cs` then executes:

```csharp
carried.Destroy();
```

**What happens:** `MakeContainer` preserves compatible `Stuff` but copies no hit points. Each transition uses a fresh `ThingMaker.MakeThing` result and destroys the damaged original. Filling, washing, emptying or reverting therefore resets physical container damage rather than preserving the player’s container.

**Repro:** Damage a steel bottle, then fill it and empty it into a tank. Inspect the replacement empty bottle’s hit points.

**Suggested check — cheap live state read:** Record hit points and maximum hit points through empty → filled → empty, and dirty → washed. Assert preservation of the intended damage fraction or absolute damage.

**Confidence:** High.

## Outside this slice

The following needed implementations were not supplied:

- `RM_MapComponent_Excavation`: grid/bed serialization, load migration, terrain restoration, driver APIs, bounds checks and path/region invalidation.
- `RM_LiquidBody`: its actual `ExposeData`, `PerCellVolume` and `ActiveCellCount`.
- `RM_Volume`, `RM_FlowKernel`, transfer legs/service, liquid networks, hose accounting, spill handling and any external building-destruction hooks.
- Settings definitions and generated XML: container capacity-rule parity, adopted item forms, ticker types, tall/cargo tank definitions and work priorities.
- Harmony patches: no 1.6 targets or compatibility behavior could be audited here.

No supplied C# file appeared truncated. The ledger heads were explicitly abbreviated; several end mid-sentence by design.