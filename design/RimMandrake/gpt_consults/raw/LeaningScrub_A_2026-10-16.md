SUBJECT: LeaningScrub (RimWorld 1.6 mod, C# + XML defs).

Slice: **LeaningScrub_A**. Static review of the supplied text; repros below were not executed. Locations use method names, as permitted.

**1. An aborted sweetline placement deletes existing items**

**Severity:** data loss.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_GenStep_SweetlineTrees.cs` — `Fits`, `Plant`.

Offending lines, in execution order:

```csharp
t.Destroy();
```

```csharp
if (c.GetThingList(map).Count > 0)
```

`Fits` permits a cell occupied by a pawn. `Plant` destroys its plants, items and filth, then discovers the remaining pawn and returns false. This affects live map-step reruns, including `ProofMapStep`.

**Repro:**

1. Pick a fertile, unroofed, standable cell satisfying the spacing checks.
2. Put a colonist and an item stack there.
3. Through a script/reflection, call `Fits(c, map, null, new List<IntVec3>())`; it accepts the cell.
4. Invoke `Plant(c, map)`.
5. It returns false, the colonist remains, and the item stack is destroyed.

**Confidence:** high. The destructive work precedes the final occupancy check, and the preceding validation does not reject pawns.

---

**2. A strangler can damage a building on another map**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs` — `RM_CompStrangler.CompTickLong`, `IsWrappable`.

```csharp
if (!IsWrappable(target) || !parent.Position.AdjacentTo8WayOrInside(target))
```

```csharp
target.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, parent));
```

The retained target must be spawned and coordinate-adjacent, but never has to share the strangler’s map. An `IntVec3` adjacency test cannot establish that relationship.

**Repro:**

1. On map A, let a grown strangler acquire an adjacent wall.
2. Pause. Despawn that wall and spawn the same object on map B at the same coordinates.
3. Invoke the strangler’s `CompTickLong`.
4. The wall on B loses HP while the strangler remains on A.

**Confidence:** high. Neither target validation nor the damage path checks `target.Map == parent.Map`.

---

**3. Disabled ripple cleanup misses newly arriving hidden pawns**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_Ripple.cs` — `RM_MapComponent_Ripple.Pass`.

```csharp
if (!on && !anyHidden)
{
    return 0;
```

`anyHidden` describes the previous scan. It cannot tell whether a pawn carrying `RM_RippleHidden` has subsequently arrived.

**Repro:**

1. With ripple enabled, hide a wild animal on map A.
2. Despawn it without removing its hediff.
3. Disable ripple and run `Pass()` on an empty map B, making `anyHidden` false.
4. Spawn the animal on B and call `Pass()` repeatedly.
5. The component returns early and leaves its saved hidden hediff attached.

**Confidence:** high for the missed cleanup. Whether the hediff eventually expires independently requires its omitted XML; this component will not remove it while that early return remains active.

---

**4. Captured campers retain free food and rest**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_ScrubInjections.cs` — `RM_MapComponent_ScrubCamps.MapComponentTick`.

```csharp
people.RemoveAll(p => p == null || p.Dead || p.Destroyed || p.MapHeld != map);
```

```csharp
if (p.needs.food != null) p.needs.food.CurLevel = p.needs.food.MaxLevel;
if (p.needs.rest != null) p.needs.rest.CurLevel = 1f;
```

Membership survives capture, departure from the camp lord and relocation elsewhere on the same map. A nonhostile prisoner still satisfies the replenishment checks.

**Repro:**

1. Generate a friendly camp.
2. Arrest a camper and move them into a colony prison.
3. Restore faction relations with dev tools if arrest made the faction hostile.
4. Reduce the prisoner’s food and rest.
5. Advance through a 2500-tick boundary. Both needs refill.
6. Save/load and repeat: the `people` reference list preserves the entitlement.

**Confidence:** high. There is no prisoner, lord-membership or camp-location check.

---

**5. Crown mob capacity depends on pawn iteration order**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_VenomvineRooms.cs` — `RM_MapComponent_CrownMob.MapComponentTick`.

```csharp
int held = 0;
```

```csharp
for (int i = 0; i < tmpPawns.Count && held < ext.maxMobbers; i++)
```

Existing residents are counted in the same loop that dispatches newcomers. Once dispatches reach the cap, later residents are never counted. Already inbound pawns outside the settling radius also contribute nothing.

**Repro:**

1. Use a crown with `maxMobbers = 30`.
2. Spawn 30 matching wild mobbers within drawing range but outside settling range.
3. Afterwards, spawn another 30 beside the crown.
4. Force the Stall and run a gathering pass.
5. The earlier distant animals can consume all 30 dispatch slots before the loop reaches the 30 existing residents, producing a crowd of 60.

**Confidence:** high. The capacity calculation is incremental and stops before completing its population census.

---

**6. Turning smother-craft off does not prevent an underway job from consuming a blanket and starting a claim**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_SmotherCraft.cs` — `RM_JobDriver_SmotherVenomvine.MakeNewToils`, finish action.

```csharp
Thing used = carried.SplitOff(1);
used.Destroy();
```

```csharp
comp.StartSmother();
```

The settings gate exists in the float-menu provider and maturation pass, but not in the job’s failure conditions or completion action.

**Repro:**

1. Order smothering and wait until the pawn is carrying the blanket or doing the 600-tick work.
2. Disable smother-craft, or disable the master switch.
3. Resume.
4. The blanket is consumed and a new claim is registered while disabled.
5. Re-enable the feature later; that claim can mature.

**Confidence:** high. This directly contradicts the settings description’s “Off: no new claims.”

---

**7. A successful pyre can report enough fires while creating no qualifying blaze**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_CallingPyre.cs` — `Ignite`, `RM_RitualOutcomeEffectWorker_CallingPyre.ApplyExtraOutcome`.

```csharp
zoned.SortBy(c => c.DistanceToSquared(center));
```

```csharp
if (FireUtility.TryStartFireIn(zoned[i], map, 0.6f, instigator)) lit++;
```

```csharp
string thin = lit < RM_MapComponent_FireStamp.MinOpenFires ? " Too little caught to draw the giants already on the map." : "";
```

Sorting does not enforce clustering. The warning tests total fires, whereas convergence requires five fires within six cells of one fire.

**Repro:**

1. Clear nearby vegetation around a ritual spot.
2. Place six isolated crop cells approximately ten cells from the spot, evenly spaced around it, with every pair more than six cells apart.
3. Ignite the six crops; repeat the fixture if necessary until `Ignite` returns six.
4. Keep an available stamper elsewhere on the map.
5. `FindBlaze()` returns invalid and convergence sends nobody, yet the outcome omits the insufficient-fire warning.

**Confidence:** high. The ignition and blaze-selection predicates are visibly different.

---

**8. Runway blooms interrupt active mental-state behaviour**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs` — `Bloom`, `Answer`, `StartSway`.

```csharp
a.jobs.StartJob(flee, JobCondition.InterruptForced);
```

```csharp
a.jobs.StartJob(hold, JobCondition.InterruptForced);
```

Neither queueing nor answering rejects `a.InMentalState`. A wild manhunter can therefore be handed fleeing or posture-wait jobs by canopy disturbance.

**Repro:**

1. Spawn a wild bloom species.
2. Force it into Manhunter and let it acquire an attack job.
3. Walk a humanlike through nearby canopy to trigger a bloom.
4. When the delayed answer runs, inspect its job: the bloom forcibly replaces the mental-state job with Flee or Wait_MaintainPosture.

**Confidence:** high. The forced job replacement is explicit, and both validation stages omit mental state.

---

**9. An eruptor already fleeing never receives its bloom takeoff**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs` — `Answer`, `FleeFrom`.

```csharp
if (a.CurJob != null && a.CurJob.def == JobDefOf.Flee)
```

```csharp
return null; // already running; leave it be
```

```csharp
RM_Flight.TryLaunch(a);
```

`Answer` returns when `FleeFrom` returns null. Its takeoff call is therefore unreachable for an already-fleeing eruptor, even when grounded and ready to fly.

**Repro:**

1. Use a bloom animal with response `Erupt` and flight available.
2. Give it a grounded Flee job.
3. Trigger a nearby bloom.
4. Its delayed response runs, but it remains grounded because `TryLaunch` is never called.

**Confidence:** high. Maintaining the existing flee job unnecessarily suppresses the separate flight response.

---

**10. Pyre and stamp proofs extinguish unrelated fires**

**Severity:** wrong behaviour; destructive diagnostic side effect.

**Locations:**

- `src/RimMandrake/LeaningScrub/Source/RM_CallingPyre.cs` — `RM_CallingPyreProof.ProofPyre`.
- `src/RimMandrake/LeaningScrub/Source/RM_FireStamp.cs` — `RM_FireStampProof.ProofStamp`, `finally`.

```csharp
if (!f.Destroyed && f.Position.InHorDistOf(spot, 30f)) f.Destroy();
```

```csharp
if (!f.Destroyed && spot.IsValid && f.Position.InHorDistOf(spot, 30f)) f.Destroy();
```

These sweeps do not distinguish fixture fires from fires present before the proof.

**Repro:**

1. Pause and create a valid flammable crop centre.
2. Place an unrelated fire 25 cells away.
3. Run `ProofPyre("fire@x,z")`.
4. The unrelated fire disappears.
5. For `ProofStamp`, put the unrelated fire outside its required clear 22-cell disc but inside its 30-cell cleanup radius.

**Confidence:** high. Both hooks explicitly destroy every fire in the cleanup radius.

---

**11. Every large wildfire triggers a quadratic search, even without stampers**

**Severity:** perf.

**Location:** `src/RimMandrake/LeaningScrub/Source/Kernel/RM_BlazeKernel.cs` — `FindBlaze`; caller in `RM_FireStamp.cs`, `ConvergePass`.

```csharp
for (int i = 0; i < n; i++)
```

```csharp
for (int j = 0; j < n; j++) if (InHorDist(xs[i], zs[i], xs[j], zs[j], radius)) c++;
```

`ConvergePass` finds the blaze before checking whether any available stamper exists. With the feature enabled, maps lacking stamper creatures still pay this cost every 600 ticks.

**Repro:**

1. Use a large open map with no stamper pawns.
2. Through a script, create successively 1000, 2000 and 4000 open fires.
3. Profile `ConvergePass(false)`, or the corresponding tick boundaries.
4. Distance checks grow from roughly one million to four million to sixteen million per pass.

**Confidence:** high. The nested full scans and unconditional call order are explicit.

---

**12. The static tree registry retains abandoned maps**

**Severity:** perf, memory retention.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_SweetlineScratching.cs` — `trees`, `Deregister`, `CheckGame`.

```csharp
private static readonly Dictionary<Map, List<Thing>> trees = new Dictionary<Map, List<Thing>>();
```

```csharp
treeCount--;
```

Deregistration removes the tree and decrements the count, but never removes an empty map entry. The static dictionary keeps a strong reference to that map until `Current.Game` changes.

**Repro:**

1. Enter a temporary map and spawn a sweetline tree.
2. Destroy the tree, ensuring normal deregistration occurs.
3. Leave and discard the map.
4. Repeat across temporary maps.
5. Inspect the private dictionary through reflection: empty entries accumulate for discarded maps. Those keys prevent the corresponding map objects from being collected.

**Confidence:** high. Empty-key retention does not depend on whether map removal itself despawns trees.

---

**13. Lean applicability remains stale after an in-place biome change**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/RM_TheLean.cs` — `RM_MapComponent_Lean.Applies`.

```csharp
if (!applies.HasValue)
{
    applies = map.Biome?.GetModExtension<RM_LeanExtension>() != null;
```

The result is cached for the component’s lifetime. Neither subsequent reads nor `PostLoadInit` invalidate it.

**Repro:**

1. Read `lean.Applies` on a marked biome, caching true.
2. With a dev script, remove `RM_LeanExtension` from that biome’s extension list.
3. Confirm the direct extension lookup now returns null.
4. `lean.Applies` remains true and `For(map)` still enables Lean behaviour.
5. The inverse test—cache false, then add the marker—remains false.

The same stale result applies when a map’s reported biome changes without replacing the component.

**Confidence:** high for cache invalidation failure. This does not assert that unmodified vanilla changes a map’s biome automatically.

---

**14. Lash cooldowns become immediately ready when their deadline overflows**

**Severity:** wrong behaviour.

**Location:** `src/RimMandrake/LeaningScrub/Source/Kernel/RM_FormsKernel.cs` — `LashReady`, `Poised`.

```csharp
public static bool Poised(int now, int readyTick) { return now >= readyTick; }
public static int LashReady(int now, int recoveryTicks, float recoveryFactor) { return now + Math.Max(60, (int)Math.Round(recoveryTicks * recoveryFactor)); }
```

Under normal unchecked integer arithmetic, a deadline crossing `int.MaxValue` becomes negative. The absolute comparison immediately treats it as elapsed.

**Repro:**

1. In a kernel script, set `now = int.MaxValue - 1000`.
2. Compute `ready = LashReady(now, 2500, 1f)`.
3. Call `Poised(now, ready)` without advancing time.
4. It returns true.
5. With the game clock positioned there, the map driver can strike again after 30 ticks instead of waiting 2500.

**Confidence:** high. This is a rare long-running-save/dev-clock edge, but the arithmetic failure is directly reproducible.

## Outside this slice

- **Mod removal safety and hediff lifetime:** the relevant XML and removal/migration machinery are absent. Permanent invisibility, missing-def load failures and safe uninstall cannot be established here.
- **Vanilla/DLC Harmony compatibility:** the original patched method bodies and other mods’ patches are absent. Specific lost fire-spread behaviour, additional shearability vetoes or patch-order conflicts would require that evidence.
- **Omitted runtime implementations:** the guardian implementation and six-form runtime file are missing. Their serialization, hoard pruning, contained-item release and map-load rebuilding cannot be judged from their kernels alone.