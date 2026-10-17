SUBJECT: FlowWorks (RimWorld 1.6 mod, C# + XML defs).

Slice: `FlowWorks_1core`. Ranked findings from the supplied code only; repros are test recipes, not claimed execution results.

**1. Moving a drill can permanently delete its pending liquid**

Severity: **data loss**.

Location: `src/RimMandrake/FlowWorks/Source/Drilling/Building_LiquidDrill.cs`, `Destroy()` and `TickRare()`; `src/RimMandrake/FlowWorks/Source/Drilling/RM_MapComponent_SubsurfaceLiquid.cs`, `ReturnUnits()`.

```csharp
Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>()?.ReturnUnits(pendingUnits);
pendingUnits = 0f;
```

Pending liquid remembers neither its fluid nor its original deposit. Destruction refunds the **current map’s** deposit, whose `ReturnUnits()` silently refuses deposits with no yield. The drill clears its pending amount anyway.

Repro: (1) On map A, use fractional drill output to accumulate less than one level in `pendingUnits`. (2) Script `DeSpawn()` followed by spawning that drill on surveyed, dry map B. (3) Destroy it. Map A remains debited; map B accepts nothing. Moving it to a map yielding another liquid instead lets that liquid consume the pending amount.

Confidence: **high**. Both the missing provenance and unconditional clearing are visible.

**2. A blocked flood deletes its entire unspent reservoir**

Severity: **data loss**.

Location: `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`, `Tick()`, the empty-frontier and expiry branches.

```csharp
CoolFrontToGlass();
Destroy();
return;
```

The empty-frontier branch destroys a release even with positive `remainingVolume`. Expiry does the same. Neither path returns that volume nor records a conservation exit.

Repro: (1) Configure a release with volume 10. (2) Spawn it somewhere with no eligible neighbouring cells. (3) Advance through its first spread interval and the following tick. The frontier empties and all 10 unplaced units disappear with the Thing.

Confidence: **high**. There is no refund or remaining-volume handling in either termination path.

**3. Removing a FluidDef can multiply an existing pond’s drawable volume**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs`, `SyncFluidIdentity()` and `RM_IFlowWorld.TryDebitLevel()`; `src/RimMandrake/FlowWorks/Source/RM_LiquidBody.cs`, `ExposeData()`.

```csharp
b.fluid = ActiveFluid;
```

A missing body fluid becomes the map default while its saved `stock`, `capacity` and `levelUnit` retain the old fluid’s units. Subsequent debits use the replacement fluid’s `volumePerTile`.

Repro: (1) With budget multiplier 1, classify one deep natural cell using a custom fluid with `volumePerTile = 2`; its full stock is 8. (2) Save, then remove that FluidDef while retaining its terrain. (3) Reload with default water at `volumePerTile = 1`. With recession disabled for measurement, the body now pays eight water levels instead of the original four. A body-only case need not trigger the palette-loss warning.

Confidence: **high**. The reassignment performs no corresponding stock conversion.

**4. Fractional flood volumes become whole, unfunded 1,000 L levels**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_StockMath.cs`, `FloodFillTarget()`; `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`, `PlaceFluid()`.

```csharp
int payable = volumePerTile > 0f ? (int)Math.Ceiling(remainingVolume / volumePerTile) : depth;
```

The release rounds its purchasing power **up**, writes whole levels, then permits its remaining volume to go negative.

Repro: (1) Use `volumePerTile = 1`. (2) Give a release volume `0.01f` and an adjacent empty excavation. (3) Let it spread once. `FloodFillTarget(4, 0, 0.01f, 1f)` returns 1: 10 L funds a 1,000 L level, creating 990 L.

Confidence: **high**. The overdraw is explicit arithmetic, including an enforced minimum of one level.

**5. The level-set solver permanently stalls a shallow pump-fed inlet**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs`, `CellKey()`, `IsLiveMouth()` and `PickDonor()`.

```csharp
long wet = fill[c] > 0 && !IsLiveMouth(c) ? 0 : 1;
```

`IsLiveMouth()` recognises natural sources only. A pump/drill inlet therefore gets “already wet” priority over every dry neighbour, even when `externalInput` marks it. Meanwhile, `PickDonor()` forbids the one-unit surface drop that could move its water.

Repro: (1) Enable surface levelling and level-set solving; disable rain and sinks. (2) Feed an otherwise dry D=1 canal through a pump or drill. (3) After its first level, the inlet remains full and the rest stays dry. Minimal kernel fixture: depth `[1,1,1,1]`, fill `[1,0,0,0]`, `externalInput = c => c == 0`.

Confidence: **high**. Wet priority precedes source distance, and the neighbour pass cannot break the stalemate.

**6. A sink behind a closed sluice can stall the upstream canal**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs`, `SolveRegion()`, `CellKey()` and `ComputeFlowOrder()`; `src/RimMandrake/FlowWorks/Source/RM_StockMath.cs`, `CollectComponent()`.

```csharp
bool drains = sinkHops.Count > 0;
```

Component collection walks through sealed excavations. Sink hops correctly stop at the gate, but **any** downstream sink makes every upstream region use sink ordering. Unreachable upstream cells all receive the same `Far` distance, defeating the natural-mouth progression rule.

Repro: (1) Make an eastward D=1 canal from a natural source. (2) Put a closed sluice before its downstream edge sink. (3) Enable level-set solving. The source-side inlet can remain at `1,0,0,…` despite open upstream space. A kernel fixture is source 0, excavations 1–6, sealed cell 4, sink 6.

Confidence: **high**. Collection ignores sealing, while the draining decision is component-wide rather than region-reachable.

**7. Driver pours and drills bypass closed sluice sealing**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs`, `CanPourLevel()` and `TrySetDriverFillOutcome()`; `src/RimMandrake/FlowWorks/Source/Drilling/Building_LiquidDrill.cs`, `TickRare()`.

```csharp
return f < DepthAt(c) && InputAllowed(fluid) && RM_StockMath.FluidsCompatible(f > 0, FluidAt(c), fluid);
```

Neither this eligibility check nor the driver writer consults `SealsLiquid`. The drill also performs no seal check before extracting and writing.

Repro: (1) Put a shut sluice on an empty excavated drill outlet. (2) Operate a powered drill with a valid reserve. (3) Its outlet receives liquid inside the sealed cell. Directly calling `CanPourLevel()` followed by `TryPourLevel()` demonstrates the same bypass.

Confidence: **high**. The visible drill-to-writer path contains no sealing guard.

**8. Save/load forgets flood refusals and changes which branches can fill**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`, `PlaceFluid()` and `ExposeData()`.

```csharp
placedLookup.Clear();
for (int i = 0; i < placedCells.Count; i++)
```

Refused and HandsOff cells enter `placedLookup` without entering `placedCells`. Loading reconstructs only the latter, erasing “never offered again” decisions.

Repro: (1) Give a water release one eligible neighbour already holding tar. (2) Let one spread attempt refuse it, then pause and save before the next interval. (3) Drain the tar and continue without reloading: the cell remains excluded. (4) Reload that save, perform the same drain and advance: the cell can now fill.

Confidence: **high**. The unsaved exclusion is explicit; the resulting eligibility difference needs no omitted implementation.

**9. Networks containing exactly 7,919 excavated cells never rotate their seams**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs`, `ResolveRotatedNetwork()`.

```csharp
long slot = (pulseCount % n) * 7919L % n;
int start = networkExcavated[(int)slot];
```

When `n == 7919`, `slot` is always zero. Multiples of 7,919 also visit only a restricted subset of starts. The supposedly moving partition boundary can remain permanently fixed.

Repro: (1) In a kernel harness, use width 7,920, height 1: source at 0, D=1 excavations at 1–7,919. (2) Set cap 6,000, seam rotation on, sinks off. (3) Fill the first partition and leave the second dry. (4) Pulse repeatedly. The same partitions recur and liquid cannot cross their seam.

Confidence: **high**. This follows directly from modular arithmetic and the partition-membership donor restriction.

**10. Engine-filled flood cells never receive the flood’s recession timer**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`, `PlaceFluid()`, Applied driver branch.

```csharp
floodedTileCount++;
remainingVolume -= RM_StockMath.FloodLevelDebit(oldFill, excavation.FillAt(c), fluidDef.volumePerTile);
return;
```

That return bypasses `QueueRemoveTerrain()`. No replacement recession action is recorded for engine-filled cells. On ordinary maps, the flood’s confinement rules direct eligible excavations through precisely this branch.

Repro: (1) Make an isolated D=4 excavation away from sinks and natural beds. (2) Fill it through a four-unit release with engine integration enabled. (3) Disable rain and other inputs; wait beyond `floodedTicks` and the release’s expiry. Its four levels remain indefinitely.

Confidence: **high**. The supplied closed-cell flow code has no passive drainage that substitutes for the skipped timer.

**11. One incompatible neighbouring pond blocks return flow to a compatible pond**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs`, `RunIntoBeds()`.

```csharp
beds.Add(n);
break;
```

The first geometrically qualifying bed wins before fluid compatibility or available capacity is checked. A later refusal does not try the other neighbours.

Repro: (1) Place a full canal cell containing fluid A beside a dry fluid-B pond bed to its north. (2) Put a dry, empty fluid-A pond bed to its east. (3) Enable hollows and the return leg; disable refill. North wins cardinal ordering and fails `CanReturnLevels()`. East can accept the level but is never attempted.

Confidence: **high**. Candidate selection and acceptance are separated by an unconditional `break`.

**12. A post-return hook exception can cancel a scheduled death permanently**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/TakenByLand/RM_TakenByLand.cs`, `Return()` and `SafeReturn()`.

```csharp
GenSpawn.Spawn(p, cell, map, WipeMode.VanishOrMoveAside);
policy.AfterReturn(r, p);
if (outcome == TakenOutcome.SpawnThenKill && !p.Dead) p.Kill(null);
```

If `AfterReturn()` throws, the pawn is already spawned. `SafeReturn()` consequently returns `true`, dropping the record while skipping the death and return letter.

Repro: (1) Register a test policy with `AliveChance = 0` and an `AfterReturn()` override that throws. (2) Take a player pawn and call `ReturnAllNow()`. (3) The pawn stays alive and spawned, with no pending record to finish the intended outcome.

Confidence: **high** for this extension-hook failure. The catch explicitly treats already-spawned pawns as completed.

**13. Dropping an unrestorable pond cell leaves a ghost hollow until reload**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs`, `Restore()`; `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs`, `RestoreOriginalTerrain()` and `RebuildBedGrid()`.

```csharp
body.receded.RemoveAt(body.receded.Count - 1);
```

On `NoRecord`, Restore permanently removes the cell from the refill stack. The unsuccessful terrain restore does **not** clear its existing `bedGrid` entry. Reloading does clear it, because the bed grid is rebuilt from the now-shorter receded list.

Repro: (1) Recede a pond cell. (2) Script removal of its original-terrain record, representing the supported missing-record case. (3) Refill the body until Restore drops that cell with its warning. (4) Compare `IsNaturalBed()`/`HollowDepthAt()` before and after saving and reloading.

Confidence: **high** for the state inconsistency; it requires a legacy, missing or removed terrain record.

**14. Panning still awards ore after its river disappears during the job**

Severity: **wrong behaviour**.

Location: `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerWorks.cs`, `JobDriver_PanForPlacer.MakeNewToils()` and `RM_PlacerPanning.Session()`.

```csharp
this.FailOn(() => !RM_QuarrySettings.PanningActive);
```

The running job checks the setting and spot existence, but never fails when adjacent river water disappears. `Session()` likewise does not revalidate water before generating output.

Repro: (1) Start a normal panning job with stock and ore available. (2) During its wait toil, script all adjacent river cells to soil while retaining the spot. (3) Let it finish. For a guaranteed hit, use Mining 20 and yield multiplier 10. Ore is still awarded on the dry bank.

Confidence: **high**. Water is checked when work is offered, not when the session completes.

**15. Pond mouseovers apply depletion twice**

Severity: **cosmetic**.

Location: `src/RimMandrake/FlowWorks/Source/RM_MouseoverDepth.cs`, `DepthSuffix()`.

```csharp
return RM_Volume.DepthReadout(bed * frac, bed * frac * RM_Volume.LitresPerLevel);
```

Recession has already reduced the number of wet cells to match stock. Scaling each surviving wet cell by the original body-wide fraction understates the remaining liquid again.

Repro: (1) Use two deep pond cells, budget multiplier 1 and `volumePerTile = 1`: capacity 8. (2) Set stock to 4 and settle recession so one deep cell remains wet. (3) Hover that cell. It reports 1 m / 2 kL, although its read-through fill is four levels and the body still holds 4 kL.

Confidence: **high**. The readout contradicts both the remaining stock and the supplied source-cell adapter.

## Outside this slice

- Tank, hose, bottle, container-material, river-current, weir, river-colour and merged River Colors settings-migration implementations are absent. Their correctness cannot be established here.
- `RM_SlimeSlip.Tick()` has no visible caller, but an omitted component could call it; that is insufficient evidence to declare the feature disconnected.
- The off/on engine scheduler can call full-interval `BurnPulse()` operations on consecutive ticks. Whether that double-consumes fuel depends on the omitted fire implementation.
- Loading with **FlowWorks entirely disabled**, XML def validity, and actual Harmony/DLC conflicts require omitted definitions, patches and loader behaviour. This slice does not establish removal safety.