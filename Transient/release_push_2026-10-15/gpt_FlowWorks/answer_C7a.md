Source review only; the checks below are proposed, not executed. Citations use exact code lines from the inlined files.

**F1 — MEDIUM — Free-end change events can lag nearly 120 ticks**

**Where:** `RM_MapComponent_Hoses.cs`, `FreeEndOf`:

```csharp
if (ends.TryGetValue(r, out var kv) && now - kv.Key < 60 && kv.Value.Cell == (r.laid ? r.far : IntVec3.Invalid)) return kv.Value;
```

`Watch` polls on a separate schedule:

```csharp
bool look = was != r.carry || !placedKind.ContainsKey(r) || (now + r.parent.thingIDNumber) % 60 == 0;
```

**What happens:** A draw or inspect read can populate the cache immediately after a scheduled poll. If the surroundings then change, the next poll can reuse that cached result; detection waits for the following poll. This is the brief’s stale-cache class, still present here, compounded by two independent schedules. Destroyed ports can also remain in the returned `HoseFreeEnd` during that interval. Hydraulic consequences depend on callers outside this slice.

**Repro:** On a subsequently unviewed map, populate the free-end cache just after its scheduled poll, then finish building or destroy an adjacent tank.

**Suggested check:** Cheap live read: record `FreeEnd().Port`, actual adjacent things, and `HoseEvents.Placed` at exact ticks through the next two polls.

**Confidence:** High.

---

**F2 — MEDIUM — A refused feeder still changes the receiving reel’s geometry**

**Where:** `RM_MapComponent_Hoses.cs`, relay-index construction:

```csharp
far.Add(r.laid && r.far.IsValid ? new Cell(r.far.x, r.far.z) : (Cell?)null);
```

The resulting feeder membership controls:

```csharp
V2? outward = !IsFed(r) ? r.Rect.Outward : null;
```

**What happens:** Relay adjacency includes a laid reel even when its current `lay` is null. A refused, nonconducting feeder therefore makes its receiver count as fed. That suppresses the receiver’s normal outward lead-out and the associated footprint-blocking branch. A hose that does not physically exist can change another hose’s accepted route.

This differs from merely retaining a visual relay association: the association changes production lay geometry.

**Repro:** Connect A toward B, then obstruct A so its lay fails while its laid end remains recorded. Rebuild B’s lay during that state.

**Suggested check:** Cheap live state read: capture A’s `laid`/`lay`, B’s feeder membership, and B’s `lay.Outlet`/geometry hash before and after removing A’s recorded connection. Repeat with A’s lay null.

**Confidence:** High.

---

**F3 — MEDIUM — An off-screen obstacle check leaves the rejected geometry active for another cycle**

**Where:** `RM_MapComponent_Hoses.cs`, obstacle handling:

```csharp
r.trail.Clear();
r.layKey = null;
continue;
```

The successful-replan branch likewise ends with:

```csharp
r.layKey = null;
```

Tick-driven reconstruction occurs only at:

```csharp
if ((now + r.parent.thingIDNumber) % 250 == 0) EnsureLay(r);
```

**What happens:** After detecting an obstacle, the component invalidates the key but retains `r.lay`. On the viewed map, drawing calls `EnsureLay` and repairs this promptly. On an unviewed map, reconstruction waits another 250 ticks. The old geometry remains non-null throughout that interval, despite the component having detected that its corridor changed.

The network’s exact treatment of that retained lay needs `RM_HoseLinks`, but the stale runtime state and dependence on map visibility are established here.

**Repro:** Put a wall across a walked hose while viewing another map. Sample immediately after its scheduled obstacle check.

**Suggested check:** Cheap live read: compare `layKey`, geometry hash and corridor hash after detection, then after 249 and 250 further ticks. Repeat while viewing the map.

**Confidence:** High.

---

**F4 — HIGH — Disabling hoses leaves destructive deployment maintenance running**

**Where:** `RM_MapComponent_Hoses.cs`, `MapComponentTick` has no enabled-setting guard around obstacle handling:

```csharp
r.trail.Clear();
```

and:

```csharp
r.Retract(why); Retracts++; continue;
```

Only drawing has the explicit disabled exit:

```csharp
if (!RM_HoseSettings.enabled || Find.CurrentMap != map || reels.Count == 0) { FlushFrameMeshes(); return; }
```

**What happens:** Turning hoses off hides them and triggers the intended held-liquid drainage, but also leaves rerouting, walked-trail deletion and automatic retraction active. Building over an invisible hose can therefore alter or remove its deployment before the player turns the feature back on.

The design says reels retain their ends through off/on; the later owner ruling adds drainage through open ends, rather than authorizing deployment loss.

**Repro:** Lay a hose, disable hoses, build an impassable obstruction across its route, advance through its obstacle check, then enable hoses.

**Suggested check:** Cheap live read: compare `laid`, `far`, `trail`, `Retracts` and retraction reason across that sequence. The off-state should drain held stock while preserving deployment.

**Confidence:** High at the maintenance call sites; `CompHoseReel.Retract` itself is outside the slice.

---

**F5 — MEDIUM — Retracting an end skips the advertised lift notification**

**Where:** `RM_MapComponent_Hoses.cs`, `Watch`:

```csharp
if (HoseCarryLoad.IsLaid(was) && r.carry == HoseCarryState.Carrying) { placedKind.Remove(r); HoseEvents.RaiseLifted(r); }
```

The component separately treats retracting as a held-end state:

```csharp
if ((r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) && (now + r.parent.thingIDNumber) % 30 == 0)
```

**What happens:** `EndLifted` is documented as notifying consumers when a colonist picks up a lying end. Transitioning directly from laid to retracting does not notify them. The end stops behaving as a lying connection, but an integration maintaining placement state receives no corresponding lift event.

No subscriber is included here, so a particular downstream gameplay failure cannot be attributed.

**Repro:** Place an end, then order it retracted directly rather than moved.

**Suggested check:** Cheap live read: record `HoseEvents.Lifted` and the carry-state transition. A laid → retracting pickup should produce one lift notification.

**Confidence:** Medium; the retract job’s exact transition sequence is outside this slice.

---

**F6 — MEDIUM — Walking a carried hose repeatedly rebuilds the entire map snapshot**

**Where:** `RM_MapComponent_Hoses.cs`, `DrawCarrying`, inside the changed-trail cache branch:

```csharp
List<V2> pulled = t.Pulled(World());
```

`World()` defaults to a zero-age cache and scans:

```csharp
for (int idx = 0; idx < w * h; idx++)
```

plus every plant.

**What happens:** The carried-prefix cache changes as the pawn walks. Each such rebuild can request a fresh whole-map snapshot, even though the relevant change is one additional trail cell. Multiple carriers walking on staggered ticks defeat snapshot sharing. The live-corridor optimization fixes settled-hose checks but does not address this path.

**Repro:** Have several colonists carry hose ends simultaneously on a large, tree-heavy map.

**Suggested check:** Cheap live read: measure `WorldBuilds` while carriers walk ten cells, against the same paused or idle scene. Record map dimensions and carrier count.

**Confidence:** High.

---

**F7 — MEDIUM — Every settled reel-to-port feed allocates a new native mesh every frame**

**Where:** `RM_MapComponent_Hoses.cs`, `DrawAll`:

```csharp
DrawFeed(r, y0);
```

`DrawFeed` always builds:

```csharp
Mesh feed = Ribbon(new List<V2> { from, (from + to) * 0.5, to }, (float)HoseMath.MeshWidthFlat(vis), y - 0.0008f, 0.37);
```

`Ribbon` allocates:

```csharp
var m = new Mesh { name = "RM_Hose" };
```

**What happens:** The short, stationary feed bypasses the settled mesh cache. Every connected reel creates a mesh and several managed lists every rendered frame, then destroys the previous frame’s mesh. Twenty connected reels at 60 FPS generate 1,200 feed meshes per second, including while paused.

**Repro:** View a stationary installation containing many reels coupled to tanks or pipes; pause the game.

**Suggested check:** Cheap live/profiler check: read `lastFeedDraws` and sample mesh allocations over 60 rendered frames without advancing ticks. Unchanged feeds should reuse geometry.

**Confidence:** High.

---

**F8 — MEDIUM — Corridor validation scales with the enclosing rectangle, not the hose corridor**

**Where:** `RM_MapComponent_Hoses.cs`, `CorridorHash`:

```csharp
for (int z = z0 - 2; z <= z1 + 2; z++)
    for (int x = x0 - 2; x <= x1 + 2; x++)
```

**What happens:** The bounds come from the entire hose, so a diagonal or widely bent hose hashes every cell inside its bounding rectangle. Cells far from the strand repeatedly incur live terrain, path-grid and thing-list reads. Work grows approximately quadratically with diagonal span, rather than with hose length.

Unrelated construction anywhere inside that rectangle also invalidates the hose’s hash and schedules unnecessary reconstruction.

**Repro:** Compare equal-length horizontal and diagonal hoses. Build a wall inside the diagonal hose’s bounding box but well away from its strand.

**Suggested check:** Offline SelfTest: pass a counting `sig` delegate to `CorridorHash`. Compare visited-cell counts for equal-length layouts and verify whether changing a distant interior cell invalidates the hash.

**Confidence:** High.

## Outside this slice

The following are needed to complete the highest-priority audit:

- **`CompHoseReel`**, its `ExposeData` and spawn/despawn hooks: saved held volume and liquid identity, lease/tint restoration, `layEnd` initialization, holder recovery, migration and registration.
- **`RM_HoseLinks`, `RM_LiquidNet` and its kernel/cache**: native-port filtering, same-tick route rejection, topology invalidation and map-reference lifetime.
- **`RM_HoseHold` and `RM_LiquidSpill`**: conservation during disabled-state drainage, capped/coupled ends, failed spill placement and reel destruction.
- **`RM_HoseEssentials` and its Harmony application code**: actual 1.6 targets and fallback behavior. The supplied save-skip patch body alone cannot establish target correctness.
- **`HosePortRule`, `HosePortKind`, settings fingerprints and carry/load helpers**: selection priorities, cache-key completeness and exact carry-state semantics.
- **Map teardown handling**: this class creates owned Unity meshes but shows no map-wide cleanup path. External teardown or asset unloading must be inspected before calling that a confirmed cross-load resource leak.
- **Event subscribers**: static subscriptions could retain old game/map state, but none are shown; that failure is not established here.

No inlined source file appeared truncated. The ledger explicitly describes its entries as truncated heads.