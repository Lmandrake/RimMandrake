SUBJECT: Cauldron (RimWorld 1.6 mod, C# + XML defs)

Slice: **Cauldron_A**. Findings are ranked by likely impact. Scripted edge cases are identified explicitly; I have not assumed missing XML wiring.

1. **Drift moves gas through sealed diagonal corners**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/Kernel/RM_VentGasKernel.cs` — `RM_VentGasCells.Drift`

   ```csharp
   int j = Neighbour(i, RM_VentGasKernel.HeadingDx[h], RM_VentGasKernel.HeadingDz[h]);
   if (j < 0 || !canMoveTo(j)) return false;
   ```

   Only the destination is checked. For diagonal movement, neither intervening cardinal cell must be open. A cloud can therefore cross a corner sealed against cardinal diffusion. `RM_MapComponent_VentGas.AddGas` has the same corner-crossing problem in its eight-neighbour overflow spill.

   **Repro:** (1) Create `new RM_VentGasCells(3, 3)`. (2) Call `Add(0, 100)`. (3) Call `Drift(0, 1, i => i != 1 && i != 3, null)`. Both cardinal exits are blocked, but cell `4` receives 25 gas.

   **Confidence: high.** This follows entirely from the supplied kernel; no engine behaviour is needed.

2. **A displaced drinker continues suppressing the vent and damaging its scaffold remotely**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` — `RM_JobDriver_VexxissDrinkVent.MakeNewToils`

   ```csharp
   tap.parent.TakeDamage(new DamageInfo(DamageDefOf.Blunt, RM_VentGasKernel.PryDamage, 0f, -1f, pawn));
   ...
   vent.Inhale(RM_VentKernel.DrinkPerTick(need));
   ```

   Touching the vent is established by the preceding goto toil. The subsequent 900-tick delay never checks distance again. Its continuing checks concern target despawning, silence and the drinking setting.

   **Repro:** (1) Start a vexxiss drinking at a capped vent. (2) During the drink toil, use a script to move the spawned pawn to a distant cell while preserving its job. (3) Advance through a pry interval. The distant scaffold still takes damage and suppression continues increasing.

   **Confidence: high.** Both effects directly target the vent without checking the pawn’s current position.

3. **Poisoning its own standing cell disables further contact poisoning**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/RM_CompVexxissBehaviour.cs` — `PoisonWaterAround`

   ```csharp
   if (SwapFor(pawn.Position.GetTerrain(map)) == null) return; // not wading
   ```

   With the documented shallow-water → toxic-water mapping, the first pulse converts the centre and its neighbours. The animal can then walk through those converted cells while touching additional clean water, but poisoning is disabled because its centre is already toxic water.

   **Repro:** (1) Use a large shallow-water pond and the documented one-way terrain swap. (2) Let a stationary vexxiss complete one poisoning pulse. (3) Move it one cardinal cell within the converted patch. (4) Wait another water interval. Clean water newly within its poison radius remains unchanged.

   **Confidence: high for the documented mapping.** The output terrain is being treated as “not wading.” Additional XML mappings could mask this, but are not supplied.

4. **Water interrupts the gas-burning chain**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/RM_VentGas.cs` — `Ignite`

   ```csharp
   if (!c.ContainsStaticFire(map) && (t == null || !t.IsWater))
   ```

   Gas is consumed on water, but the propagation fire is deliberately omitted. `BurnScan` propagates ignition exclusively from fires, so burning cannot continue through a water-only cloud.

   **Repro:** (1) Make a pond large enough that its centre is several cells from land. (2) Add thick vent gas across its centre using the supplied debug action. (3) Ignite the centre using the supplied ignition action. (4) Advance several burn scans. The clicked cell burns, but its water neighbours have no newly created fire to propagate ignition.

   **Confidence: high.** The missing propagation source follows directly from the water condition and the supplied burn scanner.

5. **Vent-garden map generation submits out-of-bounds planting cells**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/RM_CondensateGardens.cs` — `MapGenerated` and `TryPlant`

   ```csharp
   foreach (IntVec3 c in GenRadial.RadialCellsAround(vent.Position, ext.ventRadius, false))
       if (InVentRing(vent, c, ext)) TryPlant(c, plant, ext, ext.mapgenChance);
   ```

   ```csharp
   if (c.GetPlant(map) != null) return false;
   ```

   Unlike the ongoing vent-garden path, this path never checks `c.InBounds(map)`. Radius is configurable, while vent generation uses a fixed eight-cell margin. An otherwise supported larger garden radius therefore produces invalid map-grid queries.

   **Repro:** (1) Give a participating plant a vent habitat with radius 12 and positive mapgen chance. (2) Generate a qualifying map with a matching vent within 12 cells of an edge, or place one there before invoking this pass. (3) Break on `TryPlant` and observe calls with negative or oversized coordinates.

   **Confidence: high for invalid calls.** Whether these calls throw or are rejected by Verse accessors requires engine code absent from this slice.

6. **A long-lived print blocks expiration of later short-lived prints**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/Kernel/RM_VexxissKernel.cs` — `RM_PrintLedger.Tick`

   ```csharp
   while (Entries.Count > 0 && expiresOf(Entries[0]) <= now) { Expired++; ExpireFirst(clear); }
   ```

   Insertion order is expiration order only when every entry has the same lifetime. Lifetimes actually come from per-comp properties. Different definitions—or a lifetime change between saving and loading—can violate that assumption. `Rebuild` preserves the problematic order.

   **Repro:** (1) Add entry A expiring at tick 10,000. (2) Add entry B on another cell expiring at tick 500. (3) Call `Tick(500, clear)`. B remains indexed and uncleared until A expires. Repeat after rebuilding the ledger to demonstrate that rebuilding does not repair it.

   **Confidence: high.** This is reproducible using the supplied kernel alone.

7. **Turning off retaliation leaves an issued retaliation attack running**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/RM_CompVexxissBehaviour.cs` — `CompTick` and `TryWardFire`

   ```csharp
   if (RM_CauldronSettings.vexxissFireWardenEnabled && pawn.IsHashIntervalTick(Props.fireScanIntervalTicks))
       TryWardFire(pawn);
   ```

   ```csharp
   pawn.jobs.StartJob(attack, JobCondition.InterruptForced);
   ```

   The switches control issuing jobs. The issued vanilla attack contains no continuing check of either `vexxissAttacksIgniter` or `vexxissFireWardenEnabled`; disabling both can leave the animal attacking until the job ends, with a configured expiry of 2,500 ticks. Already-issued firefighting jobs similarly remain active.

   **Repro:** (1) Create a fire whose instigator is an attackable pawn. (2) Wait for the vexxiss to receive its retaliation job. (3) Pause and disable retaliation and fire wardening. (4) Resume: the existing attack continues.

   **Confidence: high.** The settings are checked before job creation, with no cancellation path in the supplied code.

8. **A large positive gas addition wraps around and deletes existing gas**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Cauldron/Source/Kernel/RM_VentGasKernel.cs` — `RM_VentGasCells.Add`

   ```csharp
   int v = RM_VentGasKernel.Adjusted(Density[i] + amount, out int overflow);
   ```

   The addition overflows before `Adjusted` can clamp it. Under ordinary unchecked arithmetic, the negative result is clamped to zero and overflow is reported as zero.

   **Repro:** (1) Create a one-cell grid. (2) Call `Add(0, 1)`. (3) Call `Add(0, int.MaxValue)`. The cell becomes empty instead of saturating at 255 and returning excess gas. A checked build throws instead.

   **Confidence: high.** This is a scripted numeric edge case, not a claim that stock emission settings reach this amount.

9. **The ignition limit does not bound burn-scan work**

   **Severity:** perf  
   **Location:** `src/RimMandrake/Cauldron/Source/RM_VentGas.cs` — `BurnScan`

   ```csharp
   for (int k = 0; k < fires.Count; k++) if (fires[k] is Fire f && f.Spawned) firesTmp.Add(f);
   ...
   for (int k = 0; k < firesTmp.Count && lit < RM_VentGasKernel.MaxIgnitionsPerScan; k++)
   ```

   Forty limits successful ignitions. If no candidate ignites, the scanner snapshots every spawned fire and tests nine cells per fire. A distant, below-threshold gas wisp is sufficient to keep this map-wide wildfire scan eligible every 30 ticks.

   **Repro:** (1) Create a large wildfire. (2) Keep one distant gas cell populated below `IgniteMin`. (3) Profile repeated `BurnScan` calls without advancing diffusion. (4) Increase fire count: work grows with the entire wildfire despite zero successful ignitions.

   **Confidence: high for the unbounded scan;** the resulting frame-time cost needs profiling.

10. **Print expiry bursts perform quadratic list shifting**

    **Severity:** perf  
    **Location:** `src/RimMandrake/Cauldron/Source/Kernel/RM_VexxissKernel.cs` — `ExpireFirst`

    ```csharp
    E e = Entries[0];
    Entries.RemoveAt(0);
    ```

    Every expired entry shifts every remaining entry. Expiring a full 1,500-entry ledger together performs 1,124,250 reference shifts, in addition to dictionary work and clear callbacks. Cap eviction also shifts the full retained list on each subsequent addition.

    **Repro:** (1) Fill a ledger with 1,500 entries expiring at tick 250. (2) Call `Tick(250, clear)` with a no-op callback. (3) Profile this against smaller batches: total shifting grows quadratically. Actual bridge callbacks add further work.

    **Confidence: high for the algorithmic cost;** the perceptible hitch depends on hardware and concurrent map activity.

### Outside this slice

- **Save removal safety:** XML defs, compatibility aliases and migration code are absent. The supplied `ExposeData` methods do not establish that disabling or removing the mod preserves saves.
- **Footprint ownership:** clearing and hover attribution identify a grid record solely by cell and tick. Whether another walker can replace it during that same tick—and subsequently be misidentified or cleared—requires the external grid’s implementation.
- **Reflection compatibility:** method discovery checks names and presence, without validating signatures or catching invocation failures. Specific incompatibilities require the actual CreatureBehaviors API.
- **Rendering and Harmony conflicts:** proving `SectionLayer_Gas.AddCell` parameter correctness, exact plant-overlay registration, or conflicts with other patches requires engine or other-mod code not supplied here.