SUBJECT: LeaningScrub (RimWorld 1.6 mod, C# + XML defs). Slice: LeaningScrub_B.

1. **The hoard proof deletes unrelated steel**
   
   **Severity:** data loss  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_VenomvineFormsProof.ProofForm`, hoard case and `finally`.
   ```csharp
   if (t.Position.InHorDistOf(pos, 4f)) { back += t.stackCount; made.Add(t); }
   ```
   ```csharp
   if (made[i] != null && !made[i].Destroyed) made[i].Destroy();
   ```
   The cleanup list includes every nearby steel stack, regardless of whether the proof created it. This happens even in `"off"` mode.

   **Repro:** 1) Invoke private `FindSpot(map)` through reflection. 2) Put an existing full steel stack three cells from that spot. Items do not disqualify the spot. 3) Run `ProofForm("hoard", "off")`. 4) The existing stack is destroyed during cleanup.

   **Confidence:** high. The broad collection and unconditional destruction are explicit.

2. **Proof fixture creation permanently destroys existing plants**
   
   **Severity:** data loss  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_VenomvineFormsProof.Stand`.
   ```csharp
   c.GetPlant(map)?.Destroy();
   ```
   `FindSpot` permits existing plants. `Stand` destroys them, and cleanup restores none of them. The proof can therefore destroy a productive or guarded tree, including its associated state.

   **Repro:** 1) Find the selected spot through reflection. 2) Dev-spawn an existing plant there. 3) Run `ProofForm("rearing", "off")`. 4) After cleanup, both the fixture and the original plant are gone.

   **Confidence:** high. There is no preservation or restoration path.

3. **The proofs operate on the entire live map**
   
   **Severity:** wrong behaviour, potentially pawn death or permanent world changes  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_VenomvineFormsProof.ProofForm`.
   ```csharp
   RM_EnvironmentalHazardsSettings.contactVenomEnabled = true;
   ```
   ```csharp
   comp.SweepThorns(now);
   ```
   These calls use the existing map component, whose sweeps include unrelated pawns and stands. Walking, shedding, hoarding and quenching have the same scope problem. Cleanup removes fixture objects but does not undo injuries, existing stands’ cooldowns, swallowed items, or walking activity elsewhere.

   **Repro:** 1) Leave a real pawn on mature marked thorns elsewhere on the map. 2) Disable contact venom and clear that pawn’s scratch clock through reflection. 3) Run the sworn proof. 4) The proof temporarily enables venom and scratches the real pawn as well as its controls.

   **Confidence:** high. The sweeps have no fixture filter.

4. **Hoarded perishables stop receiving their ticks**
   
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_CompHoard.Sweep` and the holder’s lifecycle.
   ```csharp
   t.DeSpawn();
   if (!held.TryAdd(t))
   ```
   Despawned contents require their holder to forward the appropriate `ThingOwner` ticks. Neither this comp, its base class, nor its map sweep does so. Deep-saving the owner preserves contents; it does not tick them.

   **Repro:** 1) Let a mature hoard absorb fresh meat. 2) Leave identical meat outside under matching temperature conditions. 3) Wait until the outside meat rots. 4) Cut the stand and inspect the returned meat’s rot progress. Repeat across save/load.

   **Confidence:** high. All holder and driver code is visible, and none forwards contained-item ticks.

5. **Destroy → save → load loses the guardian release wake-up**
   
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_SweetlineGuardians.cs` — `RM_CompGuardianRoost.PostDestroy`, `ReleaseAll`, `Prune`; `RM_CompRoostGuardian.CompTick`.
   ```csharp
   Prune();
   ```
   ```csharp
   || p.MapHeld != parent.MapHeld
   ```
   ```csharp
   if (homeTree != null)
   ```
   `ReleaseAll` prunes first. After the tree has despawned, its `MapHeld` is null, so surviving map pawns are removed before the wake/unbind loop. Saving before their next check leaves references to the destroyed tree. Once those resolve to null on load, the invalid-home branch skips `WakeUp` because waking is conditional on a non-null reference.

   **Repro:** 1) Use an isolated tree with sleeping wardens and no replacement roost nearby. 2) Pause, destroy the tree, and save before advancing ticks. 3) Reload. 4) Inspect the wardens: their home is null, but this code never performs the release wake-up.

   **Confidence:** high for the lost wake-up. How long dormancy persists depends on other wake mechanisms.

6. **A pawn transferred between maps can be scratched by its old map**
   
   **Severity:** wrong behaviour; potentially a grid exception  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_MapComponent_VenomvineForms.SweepThorns`.
   ```csharp
   if (p.Dead || !p.Spawned || p.Flying || IsImmune(p))
   ```
   ```csharp
   Plant plant = c.GetPlant(map);
   ```
   The pawn list is snapshotted, but the loop never rechecks `p.Map == map`. Damage to an earlier pawn can trigger a mod callback that transfers a later pawn. That pawn remains spawned, so its new position is queried against the old map.

   **Repro:** 1) Put two susceptible pawns in the sweep snapshot. 2) Install a test damage callback that moves the second pawn to another map when the first is scratched. 3) Put thorns at the second pawn’s destination coordinates on the original map. 4) Run the sweep: the transferred pawn receives damage sourced from the original map. Coordinates outside the original map additionally exercise unchecked grid access.

   **Confidence:** high for the wrong-map lookup; an exception depends on the resulting coordinates and grid accessor.

7. **Nearby-roost exclusion is bypassed by initial spawning and adoption**
   
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_SweetlineGuardians.cs` — `RM_CompGuardianRoost.PostSpawnSetup`; `RM_CompRoostGuardian.TryRehome`.
   ```csharp
   SpawnOne(false);
   ```
   ```csharp
   bestRoost.Bind(pawn);
   ```
   The documented rule says the later nearby tree’s slots stay empty. `OtherRoostTooClose()` is consulted only during scheduled refill. Initial spawning and rehoming both bypass it.

   **Repro:** 1) Enable guardians and dev-spawn two sweetline trees five cells apart. 2) Observe that both receive wardens immediately. 3) Enable proximity disturbance and leave a person within both watch radii: both roosts can charge. Emptying the later roost also permits orphan adoption through the unchecked rehome path.

   **Confidence:** high. Both population paths visibly omit the exclusion check.

8. **Taming the lead warden temporarily disables trunk surveillance**
   
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_SweetlineGuardians.cs` — `RM_CompGuardianRoost.IsLead`.
   ```csharp
   if (p != null && p.Spawned && !p.Dead)
   {
       return p == pawn;
   ```
   Leadership ignores faction and `homeTree`. A newly tamed first guardian stops watching and clears its home, but remains the roster’s selected leader until pruning. Every remaining wild guardian consequently declines to watch. Routine pruning can take until the tree’s next 2,000-tick long tick.

   **Repro:** 1) Identify `Guardians[0]` on a tree with multiple wardens. 2) Immediately after a tree long tick, tame that pawn. 3) Deselect the tree—its inspect text calls `LiveCount`, which would prune and mask the bug. 4) Have a slow worker cut or harvest without completing the job. Work disturbance stops accumulating until pruning occurs.

   **Confidence:** high. The stale entry satisfies `IsLead` while its own comp exits through the faction branch.

9. **The master switch freezes the Gale edge detector**
   
   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_MapComponent_VenomvineForms.MapComponentTick`.
   ```csharp
   if (!RM_LeaningScrubSettings.modEnabled)
   {
       return;
   ```
   This return also prevents updating `wasGale`. Re-enabling can manufacture an onset halfway through an existing Gale, or miss a genuinely new Gale because the latch still describes an earlier one.

   **Repro:** 1) Let a non-Gale poll set `wasGale` false. 2) Disable the master switch. 3) Start a Gale and advance beyond 250 ticks. 4) Re-enable during that same Gale. 5) The next poll calls `GaleOnset`, although no weather transition occurred while enabled. Instrument that method to observe the call independently of the missing Lean implementation.

   **Confidence:** high. Weather observation and effect gating share the same early return.

10. **Save/load resets contact cooldowns**
    
    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_MapComponent_VenomvineForms` fields and `ExposeData`.
    ```csharp
    private readonly Dictionary<Pawn, int> nextThornTick = new Dictionary<Pawn, int>();
    private readonly Dictionary<Pawn, int> nextLitterTick = new Dictionary<Pawn, int>();
    ```
    Neither clock dictionary is saved. The source explicitly acknowledges an early post-load scratch. Thus reload frequency affects damage, and repeated reloads bypass the configured contact interval.

    **Repro:** 1) Let a stationary pawn receive one scratch. 2) Save immediately and reload. 3) Advance to the next 15-tick sweep, well before the normal cooldown expires. 4) Observe another scratch. Repeat for thorn litter.

    **Confidence:** high. The previous contact time has no serialized representation; this is an acknowledged tradeoff, but still a gameplay defect.

11. **Disabled venom still consumes scratch cooldowns**
    
    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `SweepThorns` and `Scratch`.
    ```csharp
    nextThornTick[p] = RM_FormsKernel.NextScratch(now, pr.contactIntervalTicks);
    ```
    ```csharp
    if (!RM_EnvironmentalHazardsSettings.contactVenomEnabled)
    ```
    ```csharp
    return;
    ```
    The caller commits the cooldown before discovering that damage is disabled. Zero damage multipliers have the same problem. Re-enabling venom therefore inherits cooldowns for contacts that caused no damage. Litter follows the same sequence.

    **Repro:** 1) Disable contact venom. 2) Put a pawn onto mature marked thorns and advance through a sweep. 3) Immediately enable venom. 4) The pawn remains protected until the already-consumed contact interval expires.

    **Confidence:** high. Cooldown commitment precedes both damage eligibility checks.

12. **Quench detection performs a global stand × fire scan**
    
    **Severity:** perf  
    **Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` — `RM_MapComponent_VenomvineForms.SweepQuench`.
    ```csharp
    foreach (RM_CompQuench q in quench)
    ```
    ```csharp
    for (int i = 0; i < fires.Count; i++)
    ```
    Every ready stand searches the entire map’s fire list until it finds a nearby fire. Disjoint stands and fires produce the worst case: \(Q \times F\) reach tests every 60 ticks, despite a default trigger radius of only 1.5 cells.

    **Repro:** 1) Script several thousand mature, ready quench stands on one side of a large map. 2) Spawn several thousand fires far away. 3) Profile `SweepQuench`, then double either population. 4) Observe multiplicative growth in sweep work and periodic long ticks, aggravated at higher simulation speeds.

    **Confidence:** high. The nested global scan is explicit.

### Outside this slice

- `RM_FormsKernel`, `RM_GuardianKernel` and `RM_LeanKernel` are absent. Walking destination collisions, cap accounting, corpse-transfer bookkeeping, numeric validation and forgiveness calculations cannot be established here.
- `RM_MentalState_ScopedAggression` is absent. Disabling guardians clears home references without explicitly cancelling rage, but whether aggression persists depends on that implementation.
- The venom severity clamp runs **after** `TakeDamage`. Whether lethal additional hediffs can kill before the clamp requires the actual damage definitions and damage-processing path.
- XML defs, Harmony patches and shared gate/pathfinding implementations are absent. DLC compatibility, actual comp wiring, biome-cache invalidation and safe mod removal cannot be certified from this slice.