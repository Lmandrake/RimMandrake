SUBJECT: FlowWorks (RimWorld 1.6 mod, C# + XML defs).
Slice: `FlowWorks_5rivers`. Static review only; the repros below were not executed. Locations use method names rather than invented line numbers.

1. **Building the river-colour graph mutates the dictionary being enumerated**

   **Severity:** crash  
   **Location:** `src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs` — `RiverGradient.BuildTilePositions`, local `Find_`

   ```csharp
   foreach (int tileId in parent.Keys)
   ```
   ```csharp
   parent[x] = parent[parent[x]];
   ```

   `Find_(tileId)` performs path compression while the outer loop enumerates `parent.Keys`. On Mono/.NET Framework dictionary implementations, assigning an existing value also invalidates the enumerator. An ordinary connected river supplies non-root entries, so this can abort planet river-mesh generation.

   **Repro:** (1) Enable river colours on a world containing a connected river. (2) Force river-layer regeneration. (3) Check for “Collection was modified” originating in `BuildTilePositions`. A minimal runtime test is a dictionary `{0→1, 1→1}`, enumerated through the same compression loop.

   **Confidence:** high for the mutation defect; medium for the runtime exception because the runtime implementation was not supplied.

2. **Removing a silt swap makes rollback overwrite the player’s replacement floor**

   **Severity:** data loss  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_SiltTrapAndDrift.cs` — `RM_Building_SiltTrap.Clog`

   ```csharp
   TerrainDef rich = table?.RichFor(orig);
   if (rich == null || c.GetTerrain(Map) == rich)
   ```

   A missing extension or removed swap entry makes `rich == null`, which authorizes unconditional restoration. That defeats the stated protection against overwriting a floor built afterward.

   **Repro:** (1) Let a trap richen a cell. (2) Build a different floor there and save. (3) Remove that original terrain’s swap entry through an XML patch and reload. (4) Trigger `Clog()` or a nearby breach. The replacement floor is replaced with the recorded original terrain.

   **Confidence:** high; the destructive fallback is explicit.

3. **Diagonal current shoves pass through sealed wall corners**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs` — `StepOne`, `Move`

   ```csharp
   if (!next.Standable(map))
   ```
   ```csharp
   pawn.Position = next;
   ```

   Only the destination is checked. Neither orthogonal cell crossed by a diagonal step is checked, and movement is a teleport.

   **Repro:** (1) Paint a northeast current at `(x,z)` and its diagonal destination. (2) Dev-spawn walls at `(x+1,z)` and `(x,z+1)`. (3) Put a colonist at `(x,z)`. (4) Call `StepOne` or wait for the current. The pawn passes through the blocked corner.

   **Confidence:** high; the complete movement path is visible.

4. **A breach can destroy a stake after it has been moved to another map**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs` — `TickBreach`

   ```csharp
   if (stake != null && !stake.Destroyed)
   {
       stake.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, stake.MaxHitPoints));
   ```

   The scheduled reference is checked for destruction, but never for `Spawned`, map identity, or continued proximity to the breach.

   **Repro:** (1) Breach a weir with a downstream stake whose snap deadline is still ahead. (2) Through a script, despawn that stake and spawn the same object on another map. (3) Advance the original map past the deadline. The relocated stake takes the breach damage.

   **Confidence:** high; the missing ownership check and retained reference are explicit.

5. **Painted current keeps carrying things after its terrain becomes dry**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs` — `LaneAt`

   ```csharp
   int lane = Painted(c, out int pi) ? paintLane[pi] : RM_RiverCurrentLanes.LaneOf(c.GetTerrain(map));
   ```

   Painting checks `IsWater` when rebuilding, but consuming the painted lane does not. Between rebuilds, the cached paint overrides the live dry terrain.

   **Repro:** (1) Establish a painted current over shallow water. (2) Immediately after a paint rebuild, replace one painted cell with soil. (3) Before the next rebuild, query `LaneAt` and shove a pawn from that cell. It still has the painted current. The shown periodic invalidation permits a 250-tick window.

   **Confidence:** high for the stale-grid behaviour. A terrain-change invalidation hook elsewhere could shorten the window; none is shown here.

6. **Reloading repeatedly postpones a pawn’s next shove indefinitely**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs` — `ExposeData`, `Scan`

   ```csharp
   Scribe_Values.Look(ref warnedThisMap, "rmRiverWarned", false);
   ```
   ```csharp
   nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, t.Position);
   ```

   Movement deadlines and cooldowns are not saved. Loading recreates the component, and its first scan assigns a fresh full cadence.

   **Repro:** (1) Leave a stationary pawn in a current with a long cadence. (2) Save shortly before its next shove. (3) Reload and advance fewer ticks than one full cadence. (4) Save/reload again. Repeat: the pawn never reaches its movement deadline.

   **Confidence:** high; the only persisted component field and the deadline initialization are visible.

7. **Ferry and pool settings can remain cached forever when surface current is disabled**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs` — `MapComponentTick`

   ```csharp
   if (!RM_RiversSettings.CurrentActive)
   ```
   ```csharp
   return;
   ```
   ```csharp
   worksDirty = true; // cheap: a weir's HP-driven re-arm or a settings flip shows up within 250 ticks
   ```

   The periodic setting refresh occurs below the current-off return. Once `worksDirty` has been consumed, later ferry/guide/bank-work setting changes do not trigger another rebuild through this path.

   **Repro:** (1) Build a ferry and let its rope/path costs initialize. (2) Disable surface current and let any pending rebuild finish. (3) Disable ferry guidance or bank works. (4) Advance well beyond 250 ticks. Inspect the cached rope set and previously zeroed perceived costs: no rope-delta notification is generated by this component.

   **Confidence:** high for cache starvation; the visible settings code supplies no alternate dirty notification.

8. **Timer boundary behaviour depends on control-definition order**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/MapControls/RM_MapControls.cs` — `PulseAll`; `src/RimMandrake/FlowWorks/Source/MapControls/RM_TimerSwitch.cs` — `Apply`

   ```csharp
   mc.FlowPulse(ex);
   ```
   ```csharp
   mc.SetActive(on);
   ```

   Timers run inside the same sequential pass as their targets. Targets processed before a timer act using the old state; targets processed afterward use the new state.

   **Repro:** (1) Link a source and sink to one timer. (2) Through the public `ControlDefs` list, arrange their definitions as source → timer → sink. (3) Pulse at the first OFF boundary: the source can pour before being switched off, while the sink does nothing. (4) Arrange timer → source → sink and repeat from identical state: neither operates.

   **Confidence:** high; the ordering dependency is entirely within the supplied code.

9. **Supported current settings request shoves faster than the processor can deliver**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs` — processing interval and `StepOne`

   ```csharp
   private const int ProcessIntervalTicks = 15;
   ```
   ```csharp
   nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, next);
   ```

   `Cadence` can return one tick, but `Process` runs only every fifteen ticks and performs one shove without catch-up. Faster settings therefore saturate; other cadences round upward to processing boundaries.

   **Repro:** (1) Use a long fast current with hazards disabled. (2) Set fast-lane cadence to 10 ticks, strength to 3, and disable size scaling. (3) Record movement timestamps. Despite a calculated cadence of about three ticks, movement occurs at fifteen-tick intervals.

   **Confidence:** high; both the supported settings and scheduler are shown.

10. **Chained silt upgrades roll back in the wrong order**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_SiltTrapAndDrift.cs` — `RichenOne`, `Clog`

    ```csharp
    richened.Add(c);
    originals.Add(here);
    ```
    ```csharp
    for (int i = 0; i < richened.Count; i++)
    ```

    The extension permits chained swaps, and the same cell can be recorded repeatedly. Forward rollback skips the oldest transformation because the cell still holds the newest terrain, then restores only the intermediate terrain.

    **Repro:** (1) Supply swaps Sand → Soil and Soil → SoilRich. (2) Make the nearest eligible cell sand. (3) Call `RichenOne()` twice, producing rich soil on that cell. (4) Call `Clog()`. It ends as soil, rather than the original sand, and the rollback records are cleared.

    **Confidence:** high; no restriction forbids chained swap tables.

11. **A weir’s wet and bank ends change after save/load without the building moving**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs` — `ResolveEnds`, `SpawnSetup`

    ```csharp
    if (waterCell.IsValid || !Spawned)
    ```
    ```csharp
    waterCell = IntVec3.Invalid;
    ```

    End classification is cached for the entire spawned lifetime. Terrain changes do not invalidate it, whereas loading does.

    **Repro:** (1) Build a valid weir and read `WaterCell`. (2) Replace its wet-end terrain with soil and its bank-end terrain with moving river water. (3) Read `WaterCell` again: it remains the old cell. (4) Save/reload: it resolves to the other cell. Fish lookup, pool origin and wash origin consequently change on reload.

    **Confidence:** high; the cache lifecycle is explicit.

12. **Painted still water is absent from the predicate used to place weirs and pair ferries**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_RiverWorks.cs` — `IsWaterCell`

    ```csharp
    if (t != null && (t.IsRiver || (t.affordances != null && t.affordances.Contains(TerrainAffordanceDefOf.MovingFluid))))
    ```

    Despite the method’s comment, its built-in checks never consult the surface-current component. Painted still water qualifies only if some additional registered rule supplies that integration.

    **Repro:** (1) Use a still-water pond without `MovingFluid`. (2) Paint a current over it and verify `HasCurrent` is true. (3) With no external current-cell rule registered, try a bank-edge weir or ferry crossing. `IsWaterCell` rejects the painted water, preventing those features from recognizing it.

    **Confidence:** high for the missing built-in integration; an unseen registration could compensate.

13. **The levee postfix resurrects flood cells another Harmony patch rejected**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/Rivers/RM_FerryAndLevee.cs` — `LeveePostfix`

    ```csharp
    if (potentially != null && (bool)potentially.Invoke(__instance, new object[] { cell }))
    {
        __result = true;
    ```

    A false result carries no provenance. This postfix assumes the stake caused the rejection and replaces it using a weaker eligibility test, including when another mod deliberately prevented the original method from running.

    **Repro:** (1) Install a test Harmony prefix on `CanFloodSpreadInto` that sets `__result = false` and returns false for a protected stake cell. (2) Disable `stakeLineLevee` while bank works remain active. (3) Choose a cell accepted by `CanFloodPotentiallySpreadInto`. (4) Invoke the patched spread check: FlowWorks changes the protected rejection to true.

    **Confidence:** high; this conflict follows directly from the result overwrite.

14. **Ambient steam consumes the gameplay RNG stream**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs` — `FindVents`, `MapComponentTick`, `ThrowRibbon`

    ```csharp
    nextPuffTick[i] = Find.TickManager.TicksGame + Rand.Range(0, settings.ticksBetweenPuffs.max);
    ```
    ```csharp
    data.velocityAngle = settings.velocityAngle.RandomInRange;
    ```

    These and the other ribbon rolls use shared `Rand` without an isolated state. A “purely visual” setting, fog visibility and map initialization therefore change subsequent random draws.

    **Repro:** (1) In a seeded script, initialize an opted-in map and run a due steam tick. Record the next `Rand.Value`. (2) Reset to the same seed/state and repeat with steam disabled, or its due vents fogged. (3) Compare the next value: the random stream has advanced differently.

    **Confidence:** high for RNG-stream interference; no multiplayer-specific claim is needed.

15. **River steam permanently misses newly created rivers and retains the old biome’s configuration**

    **Severity:** cosmetic  
    **Location:** `src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs` — `FinalizeInit`, `FindVents`, `MapComponentTick`

    ```csharp
    settings = map.Biome.GetModExtension<RiverSteamBiomeExtension>();
    ```
    ```csharp
    if (!cell.Fogged(map) && cell.GetTerrain(map).IsRiver)
    ```

    Initialization caches both configuration and vent locations. Ticking can silence removed river cells, but cannot discover replacement rivers or notice a changed biome. Only the dev rescan fixes either.

    **Repro:** (1) Load an opted-in biome map with no river cells. (2) Paint moving river terrain and advance time: no vents appear. Alternatively, change an initialized steaming map to a non-opted-in biome while retaining its river terrain; steam continues. (3) Reload or invoke `Rescan()` and compare.

    **Confidence:** high; the only ordinary scan is `FinalizeInit`.

16. **Planet colours ignore biome, elevation and river-network changes until the world object changes**

    **Severity:** cosmetic  
    **Location:** `src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs` — `EnsureBuilt`

    ```csharp
    if (world == null || world == cachedWorld)
        return;
    ```

    Regenerating the rendering layer does not invalidate the classification graph. Its biome anchors, elevations and connectivity remain those from its first build.

    **Repro:** (1) After addressing finding 1 where applicable, initialize the gradient. (2) Change a river tile’s biome to an anchor biome, or change its elevation, within the same world instance. (3) Regenerate the river mesh and query its colour: the cached position remains. (4) Save/reload and compare.

    **Confidence:** high; world identity is the sole invalidation condition.

17. **The flow meter combines incompatible histories into fictitious daily flow**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/FlowWorks/Source/MapControls/RM_FlowMeter.cs` — `FlowPulse`, `Read`

    ```csharp
    float amount = kind == "channel" ? held : (kind == "body" ? bodyStock : 0f);
    ```
    ```csharp
    perDay = RM_MapControlMath.PerDay(amount - sampleAmounts[0], now - sampleTicks[0]);
    ```

    Samples retain neither measurement kind nor body identity. Switching from a natural body to a channel compares body stock units with channel levels; switching bodies compares unrelated reservoirs.

    **Repro:** (1) Sample a known limited pond with a meter for several pulses. (2) Dig an empty channel cell in the meter’s reach, making `Read` choose channel mode. (3) Take the next sample. The old pond stock is treated as lost channel levels and reported as drainage. Save/load preserves the contaminated history.

    **Confidence:** high; measurement selection and history persistence are visible.

18. **A missing gradient entry silently becomes the headwater colour**

    **Severity:** cosmetic  
    **Location:** `src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs` — `ColorFor`

    ```csharp
    float t = 0.5f;
    if (tilePosition != null)
        tilePosition.TryGetValue(tile.tileId, out t);
    ```

    Failed `TryGetValue` overwrites `t` with zero. The apparent midpoint fallback works only when the entire dictionary is null, not when an individual tile is absent.

    **Repro:** (1) Build a nonempty gradient dictionary. (2) Call `ColorFor` for a tile absent from that dictionary, such as a tile without potential river links. (3) It returns the headwater anchor instead of the initialized midpoint. Compare with a world having no graph, which retains the midpoint.

    **Confidence:** high; this is direct `out`-parameter behaviour. Whether such a tile gets rendered as a river depends on the caller’s data.

## Outside this slice

- The flow kernel, stock implementation, transfers, hoses, containers, pumps and pit mechanics are absent. Conservation, convergence, collapse and transactional rollback cannot be established from their callers.
- New swept-away pawns immediately enter the missing `TakenByLand` service. Its persistence, ownership, return-map selection and removal safety remain unreviewed.
- `RiverGradient.ColorFor` discards `PlanetTile.Layer` and uses surface-grid positions. Whether a non-surface river layer reaches this prefix requires the missing world-layer implementation.
- River Colors explicitly documents discarding standalone preferences, but the old settings schema and migration implementation are absent. The visible new keys are distinct; preservation of old values is unproven.
- Mod-removal safety needs the omitted defs, type aliases and cleanup code. The validation walk itself marks removal testing unbuilt.