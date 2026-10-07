**Yes: the outlet blend can cause the reported tight bends. A laid hose can also exceed its maximum length.** Both are supported directly by the pasted code.

I reviewed only the inlined files. The referenced `CordGraph`, `CordBuilder`, cord drawer, aerial implementation, and MP registration code weren’t included. Locations below use method names and exact statements rather than invented line numbers. Findings are ranked by player impact.

1. **Hose validation and relay flow depend on drawing the map**

   **Location:** `Hose/RM_MapComponent_Hoses.cs`: `DrawAll`, `EnsureLay`, `MapComponentTick`; `Hose/HoseFlow.cs`: `RelayHoseFlow.Flowing`.

   Geometry is created through `DrawAll`, which runs only for the current, visible map with hoses enabled. After loading, `lay` and `layKey` are null. The corridor check requires `r.layKey != null`, so an unviewed hose receives no obstruction validation. Relay flow additionally requires `f.lay != null`, so an otherwise flowing feeder cannot feed its relay until geometry has been drawn.

   This makes simulation depend on map selection and whether an update frame occurred. It also delays automatic retraction after loading or after invalidation.

   **Confidence:** High.  
   **Check:** Load a saved hose chain and call map ticks without map updates. Give its feeder a true flow signal; compare downstream behavior before and after one draw/update. Similarly, obstruct a hose before its first post-load draw and check whether it retracts.

2. **A fitting route can be refused because the search chooses a cheaper, longer route**

   **Location:** `Hose/HoseMath.cs`: `RouteCells`, `RoutePulled`, `CheckInstall`.

   `RouteCells` minimizes `step + w.ExtraCost(q)`, while installation accepts or rejects the resulting route by physical length. The search bound is considerably larger than the usable hose length. It can therefore return a dry detour that exceeds the hose length even when a shorter route through water fits. `CheckInstall` immediately reports `"route too long"` without searching for a fitting alternative.

   Keeping only the cheapest label per cell also loses shorter, more expensive alternatives needed by a length-constrained search.

   **Confidence:** High.  
   **Check:** Construct two obstacle-separated corridors: a roughly 20-cell water route and a 32-cell dry route, with a 25-cell hose. Ensure string-pulling cannot shortcut between corridors. The fitting water route should be accepted; the current cost search can choose and reject the dry route.

3. **The maximum hose length does not include the compulsory outlet route**

   **Location:** `Hose/HoseMath.cs`: `CheckInstall`, `RoutePulled`, `Lay`, `LayAlong`, `LayOn`.

   `CheckInstall` measures a route from the mouth through a target-facing reel cell. Actual laying can instead require a westward outlet lead, travel around the reel’s now-blocked footprint, and approach a displaced relay endpoint.

   In `LayOn`, this statement caps only **additional slack**:

   ```csharp
   maxExtra = Math.Max(0, Math.Min(maxExtra, p.MaxLength / RouteMargin - L));
   ```

   If the compulsory route already exceeds the budget, it merely sets extra slack to zero. Neither `FlatLen` nor `PlumpLen` is rejected before `lay.Ok = true`.

   For example, a reel footprint beginning at `(20,20)` and target cell `(57,20)` passes the 40-cell route check on open ground: mouth-to-target distance is approximately 37.48 cells. A full 1.6-cell westward outlet run followed by travel to that target requires at least approximately **40.68 cells**, even before routing around the reel.

   **Confidence:** High.  
   **Check:** Use that open-ground scene, call `CheckInstall`, then `LayAlong` with the outlet and blocked reel footprint as `EnsureLay` does. Assert both final pose lengths are at most 40.

   **Fix:** Installation, carrying, replan checks, and `NeedFor` must account for the same compulsory outlet/endpoint geometry. Enforce the final length after all geometry changes.

4. **The reel’s inlet-port cache never initializes**

   **Location:** `Hose/CompHoseReel.cs`: `portTick` initializer and `Port`.

   ```csharp
   private int portTick = int.MinValue;
   if (!force && now - portTick < 60 && (port == null || port.Spawned))
       return port;
   ```

   In ordinary unchecked C# arithmetic, subtracting `int.MinValue` from a nonnegative game tick overflows to a negative number. At tick 100000, the result is `-2147383648`, which passes `< 60`. Since `port` initially equals null, ordinary calls return null without ever calling `HosePorts.Find`.

   Consequently, reels report “Not connected” and their short inlet-feed hose is never drawn, unless something explicitly calls `Port(true)`.

   **Confidence:** High.  
   **Check:** Spawn a reel beside an eligible pipe. Compare `Port()` with `Port(true)`. Initialize the cache with an explicit validity flag or handle the sentinel before subtraction.

5. **Outlet straightening reintroduces bends after stiffness enforcement**

   **Location:** `Hose/HoseMath.cs`: `LayOn`, `OutletLead`, `StraightenStart`, `StraightenEnd`.

   The offending sequence is precise:

   - Flat geometry passes through `Stiffen`.
   - Plump geometry passes through `Stiffen`.
   - Afterwards, `LayOn` assigns all three poses using `StraightenStart`.
   - `StraightenStart` reverses the path and invokes `StraightenEnd`.
   - `StraightenEnd` performs:

     ```csharp
     V2 line = end - inward * Math.Min(back, straight + blend);
     o[i] = P[i] + (line - P[i]) * w;
     ```

   This interpolates **positions**, using arc distances from the old curve. Smoothstep makes the interpolation weight smooth; it does not impose a curvature bound. Its changing weight can compress segments, reverse local travel, or produce a hairpin where the forced outlet line rejoins the original curve.

   `OutletLead = OutletStraight + 2 * radius` does not fix this: it inserts a planning waypoint, but subsequent settling and stiffening do not preserve that waypoint or the outlet tangent.

   I evaluated the exact blend formula independently. A perfectly straight input travelling 120° away from the west-facing outlet becomes a curve with a minimum discrete radius of approximately **0.076 cells**, using `straight = 1.6` and `blend = 2.4`. Thus, the blend itself can create tighter bends than either input curve. This supports the reported cause, although it does not establish the full pipeline’s failure frequency.

   **Confidence:** High.  
   **Check:** Add that isolated straight-input regression, then measure radius after each `LayOn` stage in the supplied failing scenes.

   **Correct fix:** Construct or solve a curvature-constrained transition with the outlet position and tangent held fixed. Preserve the straight outlet samples and tangent during subsequent relaxation. Validate the final resampled poses after outlet, endpoint, and joiner modifications. Increasing the blend distance or adding unconstrained smoothing is not a reliable fix.

6. **Final outlet and endpoint edits can bypass the wall-clearance checks**

   **Location:** `Hose/HoseMath.cs`: `LayOn`.

   The initial Flat and Plump poses are clearance-checked, but later endpoint straightening is not. For the outlet, the broad candidate is checked; if it fails, the code selects `bl = 0.5` and applies that shorter blend **without checking its result**:

   ```csharp
   if (!Clear(w, f) || !Clear(w, q)) bl = 0.5;
   ```

   It then eventually returns `lay.Ok = true`. A failed broad blend therefore does not establish that the chosen final hose is clear. Relay-end straightening has the same missing final validation.

   **Confidence:** High for the validation defect; medium for occurrence in a particular scene.  
   **Check:** Fuzz nearby wall arrangements with outlets and relay endpoints. Assert `lay.Ok` implies `Clear(w, lay.Flat)` and `Clear(w, lay.Plump)` after every final modification. Reject or reroute any failing final pose.

7. **Tree changes can alter a hose only after reloading**

   **Location:** `Hose/RM_MapComponent_Hoses.cs`: `World`, `CorridorHash`, `EnsureLay`; `Core/CordPlanner.cs`: `AStar`.

   Trees contribute routing cost in `World`, and A* reads that cost. However, `CorridorHash` includes only walkability and door status. Planting or cutting a tree can change which route the planner selects without invalidating an existing hose.

   Because the geometry is runtime-only, reloading reconstructs it using the changed costs. A hose the player already saw can therefore change shape on reload despite remaining unchanged before saving.

   **Confidence:** High.  
   **Check:** Lay a hose where tree costs select between two routes. Cut or plant the decisive trees, wait through corridor checks, save, and reload. Compare `GeometryHash`. Either preserve the chosen route or include every replanning input in invalidation.

8. **Changing the hose-length setting does not reapply the geometry budget**

   **Location:** `Hose/HoseSettings.cs`: `ShapeFingerprint`; `Hose/RM_MapComponent_Hoses.cs`: `EnsureLay`, `MapComponentTick`.

   `EnsureLay` supplies `sp.MaxLength = r.MaxLength`, but maximum length is absent from its cache key and `ShapeFingerprint`. Changing the length setting therefore leaves existing geometry cached. The periodic check also does nothing when the corridor hash is unchanged.

   Reducing the setting can leave an over-length hose deployed indefinitely; increasing it does not recalculate the available slack.

   **Confidence:** High.  
   **Check:** Deploy a long hose, change maximum length from 40 to 8, and wait more than 250 ticks. Check geometry, deployed state, and behavior after reload.

9. **Devices connected directly to transmitter buildings lose their drawn connection**

   **Location:** `CordWorldAdapter.cs`: `Snapshot`, connector loop.

   ```csharp
   if (parent?.parent == null ||
       !ConduitVisuals.IsTarget(parent.parent.def)) continue;
   ```

   A consumer whose `connectParent` is a battery or another transmitter building is omitted entirely. The model supports `MachineLinks`, but this adapter does not create them for ordinary direct connections. Transmitter buildings without adjacent conduit hookups are also omitted.

   Thus a valid direct building-to-building power connection can have no visible cord.

   **Confidence:** High for the supplied adapter.  
   **Check:** Connect a heater or lamp directly to a battery/transmitter, without an intervening target conduit. Inspect the resulting `CordWorld.Machines` and drawn connection.

10. **Two pending orders can create a forbidden relay loop**

    **Location:** `Hose/CompHoseReel.cs`: `ResolveTarget`, `OrderDeploy`, `FinishCarry`; `Hose/RM_MapComponent_Hoses.cs`: `RelayOf`, `Loops`.

    Loop checking follows only currently laid hoses. Pending destinations are ignored, and `FinishCarry` does not repeat the check.

    With both reels stored, order A to feed B, then B to feed A before either finishes. Both checks pass. Once completed, the ring exists; `FeedersOf` excludes its connections, so the visibly connected chain does not propagate flow.

    **Confidence:** High.  
    **Check:** Queue those two orders before allowing colonists to execute them. Check again immediately before placing the second endpoint, or include accepted pending connections in loop detection.

11. **Turning off automatic resumption does not cover interrupted Move or Retract orders**

    **Location:** `Hose/Jobs/WorkGiver_HoseOrders.cs`: `JobFor`.

    The setting is consulted only here:

    ```csharp
    r.pending == HosePendingOrder.Deploy &&
    r.carry == HoseCarryState.Dropped
    ```

    Interrupted Move orders are automatically picked up despite the setting being off. Interrupted Retract orders also resume because `StopWind` retains their pending order and the Retract branch has no corresponding gate.

    **Confidence:** High.  
    **Check:** Disable automatic resumption, start Move and Retract jobs, interrupt their pawns, and release another hauling colonist. Track whether the order is newly issued or retained from interruption so explicit new orders can still execute.

12. **A rejected right-click job leaves a live colony order**

    **Location:** `Hose/Jobs/FloatMenuOptionProvider_Hose.cs`: `TargetThen`.

    `order(t.Cell)` changes the reel’s pending order before `JobFor` checks whether this pawn can perform it. If job construction fails, the code displays “Cannot carry the hose” but retains the order. Failure of `GiveForced` is likewise ignored.

    Another colonist can subsequently execute an action the player was told failed.

    **Confidence:** High.  
    **Check:** Right-click a destination unreachable by the selected pawn but reachable by another colonist. Inspect `pending` after the rejection and observe hauling work. Restore the previous order when dispatch fails, or explicitly report that the colony order remains queued.

13. **Path failures before pickup or winding leave orders dangling**

    **Location:** `Hose/Jobs/JobDriver_CarryHoseEnd.cs`: `OnFinish`; `JobDriver_RetractHose.cs`: finish action.

    Carry’s unreachable-order cleanup runs only if the pawn already holds the hose; otherwise `OnFinish` returns immediately. A failure while approaching or waiting to grab therefore retains the pending order. Retract’s finish action only stops an active winder and never clears an unreachable current order.

    The saved request can remain stranded or be repeatedly retried as reachability changes.

    **Confidence:** High.  
    **Check:** Accept a job, block the approach before grabbing or winding starts, and inspect the pending order after failure. Cleanup must distinguish interruption from failure even before ownership begins.

14. **Port choice still depends on thing-list order**

    **Location:** `Hose/HoseMath.cs`: `HosePortRule.Pick`; `Hose/HosePorts.cs`: `FindAt`.

    `Pick` keeps the first candidate when two candidates have the same kind, side, and contact rank. There is no final tie-break, despite the comment promising independence from candidate order.

    `FindAt` is stronger: for ports on the endpoint cell, it immediately returns the first eligible thing, bypassing even the Pipe-before-Tank preference. Overlapping eligible pipes/stores can therefore produce different connections when their list order changes.

    **Confidence:** High for the selection behavior.  
    **Check:** Reverse candidates sharing a contact cell. Separately, reverse an endpoint-cell list containing an eligible pipe and tank. Assert the selected identity and kind remain stable.

15. **The cord slack target is not actually an upper length bound**

    **Location:** `Core/CordLayer.cs`: `Sprawl`, `AddLoops`.

    Excursions can already exceed `target`; regular loops accept up to `target * 1.25`, and long-run end heaps have no target check. Afterwards:

    ```csharp
    double restLen =
        Math.Min(Lq + 0.8 * lost, Math.Max(Lq, target));
    ```

    When `Lq > target`, this gives `restLen == Lq`, preserving the excess rather than reducing it. With zero slack and zero extra budget, excursions are still generated. This contradicts the stated “path-tight” behavior and the comment claiming the settle preserves the slack budget.

    **Confidence:** High for the core function.  
    **Check:** Call `Sprawl` on open-floor straight paths with `slack = 0`, `maxExtra = 0`, and seeded default excursion parameters. Assert output length does not exceed the centreline length. Also test long-run heaps against the declared target.

The supplied code has findings in save/load consistency, determinism, cache invalidation, geometry, interface/orders, lifecycle, and settings. **Off-main-thread work and incorrect signatures in the shown Harmony patch: none found. Unintentional field-initializer/ExposeData/Reset default differences: none found.**

No explicit custom-class Scribe writer was found in these files; the hose MapComponent is deliberately excluded from saving. That does **not** establish that custom job-driver names are absent from saves—the inherited vanilla serialization path was not supplied. MP registration and grouped-gizmo dispatch also remain unverified.

I ran the isolated blend and overflow calculations, not a compiled mod or in-game test.