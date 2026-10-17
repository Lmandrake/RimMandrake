FlowWorks (RimWorld 1.6 mod, C# + XML defs) — slice `FlowWorks_2hose`.

Ranked source findings below. Repros were not executed; locations use method names from the supplied files.

1. **An old carry job can cancel a freshly reissued order**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Hose/Jobs/JobDriver_CarryHoseEnd.cs` — `OrderStillMine`, `OnFinish`

   ```csharp
   return (r.pending == HosePendingOrder.Deploy || r.pending == HosePendingOrder.Move) && r.pendingAt == Dest;
   ```
   ```csharp
   bool unreachable = !HoseOrderRules.KeepOrderAfterJob(cond == JobCondition.Incompletable || cond == JobCondition.Errored, OrderStillMine());
   ```
   ```csharp
   r.CancelOrder();
   ```

   Order ownership is identified only by destination and order category. It ignores `pendingFresh` and has no order generation identifier. The previous job can therefore mistake a replacement order for its own.

   **Repro:**
   1. Start carrying a hose toward a destination, then pause.
   2. Cancel the hose order; this drops the end without immediately ending the pawn’s job.
   3. Issue a new Move order to the same destination.
   4. Unpause. The old walk toil fails because `CarryingIt` is false. Its finish action identifies the new order as “still mine” and cancels it.

   **Confidence:** high. The cancellation, replacement, toil failure, and cancellation of the replacement are all visible in this slice.

2. **Repairing a failed lay can still trigger automatic retraction**

   **Severity:** wrong behaviour  
   **Locations:**  
   `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs` — `EnsureLay`, `MapComponentTick`  
   `src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs` — `CheckReplan`

   ```csharp
   if (r.layKey == key) return r.lay;
   ```
   ```csharp
   return layFailed ? (string.IsNullOrEmpty(layReason) ? "could not be laid" : layReason) : null;
   ```

   A failed lay remains cached after its obstruction disappears. At the corridor check, `CheckReplan` can establish that the route now fits, then still return the old failure because `layFailed` came from that cache.

   **Repro:**
   1. DEV-lay an unconnected reel toward an eastern target, leaving its trail empty.
   2. Block its western nozzle lead-out while keeping the ordinary route to the eastern target available.
   3. Let the corridor check invalidate the lay, then let drawing attempt and cache the failed replacement.
   4. Remove the obstruction before the next corridor check.
   5. Confirm a fresh `CheckInstall` succeeds. The next corridor check nevertheless retracts the hose using the cached failure.

   **Confidence:** high. Neither the cache key nor the failed-lay branch retries geometry before treating the old failure as current.

3. **The collision sampler accepts a pinched diagonal**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs` — `Clear`, used by `SegmentClear`

   ```csharp
   if (!ends && c.X != prev.X && c.Z != prev.Z && !w.IsWalkable(new Cell(c.X, prev.Z)) && !w.IsWalkable(new Cell(prev.X, c.Z)))
       return false;
   ```
   ```csharp
   if (!ends && WallDepth(w, q) > ClipTolerance) return false;
   ```

   The diagonal guard works only when one sampling step changes both coordinates. A sample landing barely inside one blocking cell splits the transition into two orthogonal changes; the penetration tolerance then permits it.

   **Repro script in the geometry test assembly:**
   1. Create a `3×3` `CordWorld`.
   2. Block cells `(1,0)` and `(0,1)`.
   3. Call `SegmentClear(w, new V2(0.5, 0.5), new V2(1.49, 1.56))`.
   4. It returns true despite passing between the two touching wall corners.

   The segment produces 30 sampling subdivisions. Its middle sample is `(0.995, 1.03)`: inside blocked cell `(0,1)`, but only `0.005` deep. The surrounding samples occupy `(0,0)` and `(1,1)`, so neither transition changes both coordinates.

   **Confidence:** high. This is a numerical counterexample to the exact visible predicate.

4. **Malformed legacy XML permanently consumes the one-time import**

   **Severity:** wrong behaviour  
   **Locations:**  
   `src/RimMandrake/FlowWorks/Source/Hose/RM_HoseLegacyMath.cs` — `ReadKeys`  
   `src/RimMandrake/FlowWorks/Source/Hose/RM_HoseLegacy.cs` — `ImportOnce`

   ```csharp
   catch (XmlException) { }
   ```
   ```csharp
   RM_HoseSettings.hoseSettingsImported = true;
   ```

   XML parse failure is converted into an empty, apparently successful import. Consequently, `ImportOnce` sets the completion flag instead of taking its advertised retry path.

   **Repro:**
   1. Set `hoseSettingsImported` false and provide a matching legacy settings file containing truncated XML.
   2. Run `ImportOnce`; it completes and sets the flag true.
   3. Repair the file and run `ImportOnce` again.
   4. The repaired settings are ignored because the flag now prevents importing.

   **Confidence:** high. Parsing failure is explicitly swallowed before the importer can distinguish it from valid empty settings.

5. **A non-finite migrated winding speed instantly completes retraction**

   **Severity:** wrong behaviour  
   **Locations:**  
   `src/RimMandrake/FlowWorks/Source/Hose/RM_HoseLegacyMath.cs` — `TryFloat`  
   `src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs` — `WindBy`

   ```csharp
   public static bool TryFloat(string s, out float v) => float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out v);
   ```
   ```csharp
   wound += System.Math.Max(0f, cells);
   ```
   ```csharp
   if (wound + 1e-4f < windTotal) return false;
   ```

   The importer accepts `NaN`; the winding path never rejects non-finite values. Once `wound` becomes NaN, the completion comparison is false and execution falls through to `ReelIn()`.

   **Repro:**
   1. Import a legacy hose file containing `<windCellsPerSecond>NaN</windCellsPerSecond>`.
   2. Deploy a long hose and order retraction.
   3. At the first winding pulse, the entire hose is stored.
   4. Alternatively, call `WindBy(currentWinder, float.NaN)` directly on a retracting reel.

   **Confidence:** high. The parser accepts non-finite floating-point values, and the visible completion test fails open for NaN.

6. **Interrupting winding grants extra retraction distance**

   **Severity:** wrong behaviour  
   **Locations:**  
   `src/RimMandrake/FlowWorks/Source/Hose/HoseCarry.cs` — `HoseTrail.ShortenBy`  
   `src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs` — `StopWind`

   ```csharp
   double target = PulledLength(w) - wound;
   while (Cells.Count > 1 && PulledLength(w) > target + 1e-9) Cells.RemoveAt(Cells.Count - 1);
   ```

   Winding progress is fractional, but interruption rounds the remaining trail downward by removing whole cells. The excess removal is neither retained as a fractional endpoint nor charged against subsequent winding.

   **Repro:**
   1. Lay a straight hose with an explicit cell trail.
   2. Set winding speed to `1` cell/second.
   3. Start retracting and interrupt immediately after one ten-tick winding pulse.
   4. Approximately `0.167` cells of work removes a full one-cell segment.
   5. Repeatedly resume and interrupt after one pulse to retract substantially faster than the configured speed.

   **Confidence:** high. A straight trail makes the rounding error directly measurable without involving the planner.

7. **Interrupting a long walked trail performs quadratic work**

   **Severity:** perf  
   **Location:** `src/RimMandrake/FlowWorks/Source/Hose/HoseCarry.cs` — `HoseTrail.ShortenBy`, `Pulled`

   ```csharp
   while (Cells.Count > 1 && PulledLength(w) > target + 1e-9) Cells.RemoveAt(Cells.Count - 1);
   ```
   ```csharp
   foreach (Cell c in Cells) if (pts.Count == 1 ? V2.Dist(c.Centre, Mouth) > 1e-9 : true) pts.Add(c.Centre);
   ```

   Every removed cell causes another complete reconstruction and pull of the remaining trail. Trail size is not bounded by pulled length: a pawn can walk many unique cells inside the hose’s radius.

   **Repro script:**
   1. Populate a trail with a non-repeating serpentine walk through an open `40×40` area, with maximum length `60`.
   2. Set wound distance to `PulledLength(w) - 0.01`.
   3. Profile `ShortenBy`, or install that trail on a retracting reel and call `StopWind`.
   4. Compare successively larger trails. Removing nearly the whole trail repeatedly traverses and allocates lists for the remaining cells.

   **Confidence:** high. The loop performs at least quadratic cell enumeration; the geometry work adds further cost.

8. **Pausing during a transition causes perpetual mesh rebuilding**

   **Severity:** perf  
   **Location:** `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs` — `DrawAll`

   ```csharp
   bool settled = !pi.Wobbling && (pi.Blend <= 0 || pi.Blend >= 1);
   string key = settled ? (pi.Blend >= 1 ? "P" : "F") + r.layKey + "@" + RankOf(r) : null;
   ```
   ```csharp
   else { frameMeshes.Add(fm); frameMeshes.Add(pm); frameMeshes.Add(sm); }
   ```

   Transition geometry depends on game ticks, but its meshes are recreated on every rendered frame. While paused, the pose cannot change and the hose cannot become “settled,” so this allocation/destruction cycle continues indefinitely.

   **Repro:**
   1. Lay several hoses and enable their debug flow.
   2. Advance a few ticks into Filling, then pause.
   3. Leave the map visible and inspect Unity’s profiler.
   4. Each frame creates and retires unchanged strand/shadow meshes despite an unchanged game tick.

   **Confidence:** high. The cache decision has no paused-state or same-tick reuse path.

9. **`EndPlaced` misses relocation when state and kind remain equal**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs` — `Watch`

   ```csharp
   if (placedKind.TryGetValue(r, out HoseEndKind k) && k == e.Kind && was == r.carry) return;
   placedKind[r] = e.Kind;
   HoseEvents.RaisePlaced(r, e);
   ```

   Placement tracking remembers only `HoseEndKind`. It does not remember the placed cell or port identity. Even after `FreeEndOf` discovers a changed endpoint, this comparison can suppress notification.

   **Repro:**
   1. Subscribe to `HoseEvents.EndPlaced` and log the reel’s endpoint.
   2. DEV-lay the hose on free ground and advance a tick.
   3. DEV-lay it on another free-ground cell while it remains Laid.
   4. Advance beyond 60 ticks: the new placement produces no event.
   5. The same suppression occurs when a sampled Port connection is replaced by another Port without an intervening sampled kind change.

   **Confidence:** medium. Suppression is certain; whether consumers require port-replacement notifications depends on their contracts. Relocation does fit the event’s documented placement purpose.

10. **One broken event subscriber starves every later subscriber**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/Hose/HoseEnds.cs` — `HoseEvents.RaisePlaced`, `RaiseLifted`

    ```csharp
    try { EndPlaced?.Invoke(r, e.Kind, e.Port, e.Port?.Faction); }
    catch (Exception ex) { if (!errorLogged) { errorLogged = true; Log.Error("[FlowWorks] a HoseEvents.EndPlaced subscriber failed: " + ex); } }
    ```

    The exception boundary surrounds the multicast invocation rather than each handler. A throwing handler prevents subsequent handlers from running on every invocation. The shared `errorLogged` flag also suppresses later diagnostics, including failures of the other event.

    **Repro:**
    1. Register an `EndPlaced` handler that throws.
    2. Register a second handler that increments a counter.
    3. Place several hose ends.
    4. The counter stays zero; only the first failure is logged.

    **Confidence:** high. This follows directly from multicast delegate exception propagation.

11. **Crossing bands collapse after rank 12—including ranks consumed by stored reels**

    **Severity:** cosmetic  
    **Locations:**  
    `src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs` — `CrossLift`  
    `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs` — `Layered`

    ```csharp
    public const int CrossRanks = 12;
    public static float CrossLift(int rank) => (float)(CrossBand * Math.Max(0, Math.Min(CrossRanks, rank)));
    ```
    ```csharp
    foreach (CompHoseReel r in reels) hs.Add(new HoseMath.LayeredHose { Id = r.parent.thingIDNumber, Lay = r.lay ?? new HoseLay() });
    ```

    Layering assigns distinct logical ranks to all reels, but rendering clamps every rank above 12 to the same altitude. Stored reels consume ranks too. Logical fitting suppression therefore continues distinguishing hoses whose actual depth bands are identical.

    **Repro:**
    1. Build twelve reels and leave them stored.
    2. Build two newer reels and lay their hoses across each other.
    3. With no extra layering constraints, they receive ranks 12 and 13.
    4. Both render at `CrossLift(12)`, losing the promised distinct crossing bands.

    **Confidence:** high for the altitude collision. The precise visible artifact depends on rendering order and overlap.

12. **Resetting thickness does not reset the actual width**

    **Severity:** cosmetic  
    **Location:** `src/RimMandrake/FlowWorks/Source/Hose/RM_HoseSettings.cs` — `ResetFields`, `ApplyThickness`

    ```csharp
    if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
    ```
    ```csharp
    public static void ApplyThickness() => HoseMath.WidthScale = Mathf.Clamp(thickness, 0.5f, 1f);
    ```

    Reset changes the setting field but never reapplies its derived static value. The fingerprint changes and can trigger relaying while geometry still uses the old `WidthScale`.

    **Repro:**
    1. Set thickness to `0.5` through the UI so `ApplyThickness` runs.
    2. Execute the probe’s `defaults` command.
    3. Read `thickness` and `HoseMath.WidthScale`: they are respectively `1` and `0.5`.
    4. Hoses remain narrow until another path calls `ApplyThickness`, such as drawing that settings group or exposing settings data.

    **Confidence:** high. The probe reset path shown here contains no compensating application call.

## Outside this slice

- **Liquid conservation and reload draining:** `heldUnits` is saved, but `flowUntil` is not. Whether loading can drain a still-operating hose before its next credit depends on the missing `RM_HoseHold`, spill, lease, and machine-cycle implementations.
- **Tint continuity:** `pendingSince` and `lastLiquid` are saved while `pendingUntil` is not; `EndLease` also leaves pending tint state intact. The consequences require `RM_LiquidNetKernel.TintStep`.
- **Hydraulic liveness and removal safety:** the network eligibility code, transfer implementation, reel/job XML defs, vanilla serialization, and shared style-picker bodies are absent. These files alone cannot establish full mod-removal safety or DLC/Harmony compatibility.
- **Pits, superdeep grids, bottles, river mechanics/colours, canal fill-in, and River Colors settings migration:** the supplied documents describe them, but their executable implementations are absent.