# HugeFootprints performance: the code, the 70 ms/tick issue, the fix, and alternatives

Written 2026-10-10 (FOUNDRY, offline). Durable companion to `design/RimMandrake/giant_footprint_design_2026-10-07.md`
(what the feature is) and the brief for a GPT deep dive on alternative algorithms (§6).

**Owner ruling, 2026-10-10:** the Rot's density (2,811 footprint giants on a 250x250 map, ~7,400 trunk blockers,
~12% of cells, ~1,315 refused claims) **is intended and acceptable. The cost must be handled in code.** Nothing here
proposes thinning the roster or the biome's `plantDensity`.

Evidence labels: **MEASURED** (a number from a live run, with its source), **READ-FROM-CODE** (read in the source at
the cited line, at commit `f3774dd15`), **UNVERIFIED** (reasoning or an engine claim nobody has checked; a hypothesis
to test, never a fact to repeat).

Source paths (all under `src/RimMandrake/HugeThings/Source/`):

| file | holds |
|---|---|
| `MapComponent_HugeFootprints.cs` | the per-map component: claims, pending cells, realize, relabel, reconcile |
| `CompHugeFootprint.cs` | per-plant comp: signature, desired cells, planning window |
| `Kernel/RM_HugeClaimsKernel.cs` | Verse-free `ClaimLedger`, `Planner`, `ItemMover`, `FootprintSignature` |
| `Kernel/RM_HugeFootprintKernel.cs` | Verse-free draw transform and contact-cell geometry |
| `Building_TrunkBlocker.cs` | the invisible impassable edifice per blocked cell |
| `HugeThingsCore.cs` | opt-in, Harmony patches (`Plant.TickLong`, `PlantCollected`, zones, explosions, gravship) |
| `../Defs/ThingDefs/RM_HugeTrunkBlocker.xml` | the blocker def |
| `src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml` | generated per-species contact masks |

## 1. The feature, data model, lifecycle, old and new algorithm

### 1.1 What it is for

The Rot draws several fungi up to 20 cells wide, but RimWorld has no multi-cell plant: each is a one-cell `Plant`.
Owner ruling 2026-10-07 (option 1, then the rework card at 20:05): *"Solid trunk, open canopy"*; the selection rect
wraps the whole drawn picture; **pawns are blocked wherever the art touches the ground**, measured from the art,
never under the cap. Mechanism (design doc §Mechanism): each blocked cell gets one invisible impassable edifice
`RM_HugeTrunkBlocker`, so vanilla's path grid, regions, blueprint placement and sowing all treat it as solid with no
patches. Trunk cells give partial cover (`fillPercent` 0.4) and forward hits to the plant.

Why Things and not a path-cost patch (design doc §"Why not the alternatives", READ-FROM-CODE of the doc, engine
claims there are UNVERIFIED here): a cost patch would not refuse buildings or stop plants, and `Plant` cannot be
`size > 1`.

### 1.2 The species and their masks (READ-FROM-CODE, `RotGiants_HugeFootprint.xml` lines 18-259)

| def | drawn width | contact cells per variant | Rot `wildPlants` weight (`RM_TheRot_Biome.xml`) |
|---|---|---|---|
| `AB_AgariluxPrime` | 20 | 118 | 0.01 |
| `AB_DribblingCap` | 12 | 28 | 0.1 |
| `RM_Nogtyl` | 12 | 17 / 13 / 10 | (not in the lines read; UNVERIFIED) |
| `RM_Arpeau` | 10 | 4 / 7 / 10 | 0.4 |
| `AB_ArbuscularMycorrhiza` | 9 | 16 | 0.2 |
| `AB_AgaricusDomeCap` | 7 | 10 | 0.1 |
| `AB_GiantAgarilux` | 6 | **0** | **2** |
| `AB_WitchesOyster` | 6 | 9 | 0.5 |
| `RM_PaleTree` | 6 | 3 | 0.01 |

`AB_GiantAgarilux` carries the heaviest weight and **zero** contact cells, so it takes the `RootRule.RootImpassable`
route (`HugeThingsCore.cs:76-80`: the def itself is made `Impassable`) and never claims a cell. It is still a
registered owner (`CompHugeFootprint` is attached to every def with the extension, `HugeThingsCore.cs:303-306`), so it
counts in `comps` and in every per-tick walk of `comps.Keys` while contributing nothing to claims. The split of the
2,811 giants by species is **UNMEASURED**; it decides how much of n is dead weight (§5.1 counter `ownersWithClaims`).

### 1.3 Data model (READ-FROM-CODE)

Per map, `MapComponent_HugeFootprints` (`MapComponent_HugeFootprints.cs:27-38`):

| field | type | meaning |
|---|---|---|
| `comps` | `Dictionary<int, CompHugeFootprint>` | every registered giant, keyed by `thingIDNumber` (the owner id) |
| `dirty` | `SortedSet<int>` | owners whose footprint signature changed and must be re-taken |
| `ledger` | `ClaimLedger` | `cellOwners: Dictionary<long, SortedSet<int>>` and `ownerCells: Dictionary<int, HashSet<long>>` (`RM_HugeClaimsKernel.cs:20-21`) |
| `realized` | `Dictionary<long, Building_TrunkBlocker>` | the one blocker per closed cell |
| `pending` | `SortedSet<long>` | claimed cells with no blocker yet (refused or not yet planned) |
| `lastMoveTick` | `Dictionary<long, int>` | item-push rate limit per cell |
| `ownershipChanged` | bool | relabel blockers on the next tick |
| `rootsCache` | `List<long>` (new in `f3774dd15`) | every giant's root cell |

Cell keys are `long` = `(x << 32) | (uint)z` (`RM_HugeFootprintKernel.cs:56`).

Per plant, `CompHugeFootprint` (`CompHugeFootprint.cs:28-34`): the replayed `Plant.Print` random draws (jitter, flip,
variant), a one-entry `SignatureCache<CellRect>` for the selection rect, and `lastTaken`/`takenOnce`.

**What is saved:** almost nothing. The comp "holds no saved state; the map component rebuilds everything from the
plants and the blockers on load" (`CompHugeFootprint.cs:21-22`). The component has no `ExposeData`. The only Scribed
field is `Building_TrunkBlocker.owner` (`Building_TrunkBlocker.cs:28-32`), kept for labels before the first reconcile.
The blockers themselves are ordinary saved Things (7,400 of them on the Rot map).

### 1.4 Lifecycle and every entry point (READ-FROM-CODE)

| event | entry point | work |
|---|---|---|
| plant spawns (map gen, sowing, spread, load) | `CompHugeFootprint.PostSpawnSetup` -> `Register` (`CompHugeFootprint.cs:178-184`, component `:56-61`) | add to `comps` and `dirty`; drop `rootsCache` |
| plant despawns (cut, death, minify, gravship) | `PostDeSpawn` -> `Deregister` (`:186-191`, `:65-75`) | `ledger.Remove`, open freed cells, **`RelabelOwners()` at once (walks all ~7,400 blockers)** |
| plant grows | Harmony postfix `Plant.TickLong` (`HugeThingsCore.cs:173-181`) -> `Notify_PlantTickedLong` (`CompHugeFootprint.cs:196-199`) | recompute the signature (a `Roll()` with `Rand.PushState/PopState`, a graphic lookup, a string `Substring`) and `MarkDirty` if it changed. `Plant.TickLong` runs every 2,000 ticks per plant (comment at `CompHugeFootprint.cs:193`), so ~2,811/2,000 = **~1.4 giants per tick** hit this postfix |
| harvest | postfix `Plant.PlantCollected` (`HugeThingsCore.cs:235-243`) | `MarkDirty` |
| settings change | `RefreshAllMaps` -> `MarkAllDirty` (`:82-85`, `:528-535`) | every owner dirty; drained 8 per tick (~350 ticks for 2,811) |
| map load / init | `FinalizeInit` -> `Reconcile` (`:87-121`) | index every blocker, `Take` every owner, open strays, mark pending, then **one unfiltered whole-map `RealizePending()`** and a relabel |
| every tick | `MapComponentTick` (`:137-167`) | drain up to `RefreshesPerTick` = 8 dirty owners (`Take`), then realize (old/new below), then relabel if ownership changed |
| a blocker disappears by other means | `Building_TrunkBlocker.DeSpawn` -> `Notify_BlockerGone` (`Building_TrunkBlocker.cs:70-75`, component `:469-478`) | forget it; if still claimed, re-pend |
| every 250 ticks per blocker | `Building_TrunkBlocker.TickRare` (`:79-84`; def `tickerType` Rare) | ghost guard: `Map.GetComponent<>()`, `Owns`, `IsClaimed`. 7,400 / 250 = **~30 blockers per tick**. This runs in the thing tick lists, not the map-component stage, so `map_comp_timing` does not see it |
| shot / blast on a trunk | `PreApplyDamage`, explosion prefix | forward to the plant (not on the hot path) |
| gravship landing | `ClearArea` prefix -> `OwnersAt` (`:481-497`) | walks every owner's cells (O(total claims)); rare |
| titan smash | `SolidCellsIn` (`:503-525`) | walks the area only |
| click / selection | `CustomRectForSelector` postfix -> `SelectRect` | signature recompute each call (cached rect) |

`Take(c)` (`:170-182`): `c.DesiredKeys()` (signature + `ContactCells` over the scaled quad), bounds filter,
`HashSet before` copy of the owner's cells, `ledger.Set` (which allocates `want` HashSet, `drop`/`add` lists and a
`SortedSet<int>` per newly claimed cell), `Open(freed)`, new claims with no blocker go to `pending`, `MarkTaken()`
(**a second signature recompute**).

`RealizeOwner(id, c, roots)` (`:257-273`), the expensive unit:

1. `mine` = owner's cells that are pending (scan `CellsOf(id)` with `pending.Contains`, a `SortedSet` lookup each).
2. `window = Planner.Window(c.MaxKeys(), root)`: `MaxKeys()` recomputes the signature again (`CompHugeFootprint.cs:128-146`)
   though the result is constant for a plant at a given setting. Window = the full-growth picture/footprint box + 4.
3. `Flags(window)` (`:393-454`): scans the window grown by `InteractionScanMargin` = 8 on every side, calling
   `GetThingList` on every cell (interaction cells, door approaches), then a second pass over the window building a
   `Dictionary<long, CellFlags>` with one entry per window cell, again calling `GetThingList` and `Walkable` per cell.
   Allocates a `Dictionary`, a `HashSet<IntVec3>` and a `List<IntVec3>` per owner per call.
4. `PlanItemMoves` (`:278-308`) -> `Planner.Plan` (possibly several times through `ItemMover.AssignAndPlan`'s
   refuse-and-reassign loop, `RM_HugeClaimsKernel.cs:323-339`).
5. `Planner.Plan` (`RM_HugeClaimsKernel.cs:126-199`):
   - builds `bool[] pass` for the window (one `flagsAt` dictionary lookup per cell),
   - `before = Reach(pass)` (a 4-connected flood from the border: allocates a `bool[]` and a `Stack<int>`),
   - for **every root on the map** (`roots`, ~2,811) tests `window.Contains` (`:143-148`): O(n) per owner,
   - then a **fixpoint loop**: for each candidate cell, tentatively close it and run a **full `Reach` flood**
     (new `bool[]`, new `Stack`), then an O(window) comparison against `before`, then a root check
     (`rootIdx.Contains` is a linear `List<int>` search). Repeat whole passes until no cell is accepted in a pass.
6. `RealizeInOrder` spawns blockers in acceptance order and stops at the first failure.

Cheap refusals (`Pawn | Item | Protected`, or not passable) are skipped before the flood (`:169`). **A cell refused for
reachability costs a full flood on every pass of every attempt** and is never remembered as refused.

### 1.5 The OLD algorithm (before `f3774dd15`), pseudocode

```
MapComponentTick:
  n = 0
  while dirty nonempty and n < 8: Take(dirty.popMin()); n++
  if (n > 0 and pending nonempty) or (pending nonempty and (tick + mapId) % 250 == 0):
      RealizePending()                       # unfiltered
  if ownershipChanged: RelabelOwners()       # walks every blocker

RealizePending():
  owners = SortedSet()
  for k in pending: for o in ledger.OwnersOf(k): owners.add(o)        # ~1,315 cells -> owners
  roots = [Key(c.parent.Position) for c in comps.Values]              # rebuilt every call: ~2,811 longs
  for id in owners (ascending): RealizeOwner(id, comps[id], roots)    # full Flags + Plan per owner
```

**Why it cost ~70 ms/tick at this scale.** The trigger `n > 0` fires on any tick where a single dirty owner was
drained. `Plant.TickLong` reaches ~1.4 giants per tick and a growing plant's signature changes every TickLong
(`Visual` lerps with growth, `CompHugeFootprint.cs:96`), so on a freshly generated map with many still-growing giants
some owner is dirty on nearly every tick (READ-FROM-CODE inference; the fraction of ticks with n > 0 is UNMEASURED).
And because the ~1,315 refused cells are permanently pending (the density makes most of them permanently refusable),
`pending` is never empty. So nearly every tick re-planned **every owner holding a pending cell** (count UNMEASURED,
bounded by min(1,315, owners with claims)), each paying steps 2-5 above: two window scans with `GetThingList` per cell
over a window up to (24+16+8)^2 for the largest species, an O(n) roots walk, and a full flood per
reachability-refused candidate per fixpoint pass, with dozens of allocations per owner. Nothing was cached across
ticks, so the same refusals were re-derived from scratch about 60 times a second at speed 1. MEASURED result: 70.0 ms/tick
(§2). The diagnosis line is `Transient/foundry_tps_diagnose_20261010.md` 15:02.

### 1.6 The NEW algorithm (`f3774dd15`), pseudocode (READ-FROM-CODE, `MapComponent_HugeFootprints.cs:137-167, 216-255`)

```
MapComponentTick:
  refreshed = null
  while dirty nonempty and n < 8:
      id = dirty.popMin(); if comps has id: Take(comps[id]); refreshed.add(id)
  if pending nonempty:
      phase = (tick + mapId) mod 250
      RealizePending(filter = id in refreshed  or  id mod 250 == phase)
  if ownershipChanged: RelabelOwners()

RealizePending(filter):
  owners = SortedSet()
  for id in comps.Keys: if filter(id) and HasPending(id): owners.add(id)   # walk owners, not pending cells
  roots = rootsCache ?? rebuild                                            # invalidated on register/deregister only
  for id in owners: RealizeOwner(id, comps[id], roots)
```

So each tick re-plans (a) the owners it just refreshed and (b) the ~1/250 of owners whose id falls in this tick's
phase. Every owner is still retried once per 250 ticks, as before; the work is spread instead of repeated.
`Reconcile` (load) still calls the unfiltered form once.

**Expected cost (UNVERIFIED until the proof run in `Transient/foundry_hugefix_prove_20261010.md` lands):** roughly
(owners with pending)/250 + (refreshed with pending) owners per tick, against all of them before; with a few hundred
pending owners that is ~2-10 `RealizeOwner` calls per tick instead of hundreds, i.e. a 20-100x cut, plus a fixed
O(n) walk of `comps.Keys` with one delegate call each (~2,811 per tick) and one closure allocation per tick.

**Invariants it keeps (READ-FROM-CODE):**
- The ledger is untouched: claims stay order-independent (`ClaimLedger.Set`).
- Per-owner retry cadence is unchanged (once per 250 ticks), so a refused cell is never starved.
- A refreshed owner is planned in the same tick it was taken (no added latency for growth).
- `RealizeOwner` per owner is unchanged, so its safety rules (no pawn/item/protected cell, no new pocket, root
  access) are unchanged.

**Risks:**
- **Latency for cross-owner unblocking.** A cell that becomes closable because a *different* owner's refresh changed
  the ground (or because an item left, or a pawn walked off) waits up to 250 ticks (~4 s at speed 1). Before, any
  refresh retried everyone. Visible: a trunk cell may stay walkable a few seconds longer. Acceptable by design; it
  matches the pre-existing slow-retry cadence.
- **Order dependence of the realized set.** The ledger is order-independent; the *realized* set is not. Owners plan
  one at a time against the current ground, and a blocker spawned by owner A changes owner B's flood. The old code
  planned all pending owners in ascending id each time; the new one plans a phase slice. Two overlapping giants can
  therefore end with a different realized set than the old code produced from the same start (UNVERIFIED whether
  this happens in practice; §5.3 differential test). Both results are safe; they may differ.
- **Conflicting claims between overlapping footprints.** Cells are shared through the ledger (one blocker per cell,
  primary owner = lowest id), unchanged. But each owner plans only *its* pending cells in *its* window: a cell
  claimed by A and B is planned by whichever runs first. Unchanged in kind, changed in timing.
- **Save/load.** No new saved state. `rootsCache` and the phase are derived. `Reconcile` still does one full
  unfiltered realize on load: a one-shot load hitch of the old per-tick size (~70 ms or more, UNMEASURED) per map.
  Determinism across save/load: phase = `(TicksGame + map.uniqueID) % 250` and owner ids are thingIDNumbers, both
  restored by load, so the schedule resumes identically; `dirty` is not saved but is rebuilt by Register (every owner
  dirty after load, drained 8 per tick: ~350 ticks of refreshes after every load, each re-planning its owner).
- **Map edges.** `Take` drops out-of-bounds keys (`:175`); `Flags` marks out-of-bounds window cells `None`
  (impassable), so the window border off-map is not a source of reach. Unchanged by the fix.
- **Mod interactions.** Anything that spawns or despawns things inside a window (other mods' buildings, Large Pawns)
  changes flags; it is seen at the next retry. Gravship, explosions, zones are separate patches, unchanged.
- **GC.** The fix removes the per-tick `roots` list and the `pending`-cell walk, but `RealizeOwner` still allocates
  (Flags dictionary, HashSet, bool arrays and a Stack per flood, lists, closures). Fewer calls means less garbage, not
  none.
- **Still-present O(n) and O(blockers) paths:** the `comps.Keys` walk every tick; `Planner.Plan`'s walk of all roots
  per planned owner; `RelabelOwners` over all ~7,400 blockers on every tick where any blocker spawned or any claim
  moved; `Deregister` relabelling immediately (a mass die-off of k giants costs k x 7,400).
- **Refreshes that change nothing still re-plan.** A growing plant whose signature changed but whose desired cells
  did not (most TickLongs once the cells are stable) still gets a full `RealizeOwner` if it has a pending cell
  (`refreshed` is filled on any `Take`, `:150`).

## 2. Measurements so far and reproduction

### 2.1 Numbers (MEASURED 2026-10-10, old DLL, Rot quicktest, 550-mod list, speed Normal)

Source: `Transient/foundry_tps_diagnose_20261010.md` (lines 8, 14, 15, 18-23). That file is Transient (14-day shelf
life); the numbers are copied here so this doc does not depend on it.

| quantity | value | instrument |
|---|---|---|
| tick time | 93.6 ms/tick | always-on TPS record, 64 run windows, 3,247 ticks |
| map-component stage | 88.4 ms/tick (94% of tick) | same; `tl:Normal` 3.1, world 0.9, `mapPre` 0.7, rest < 0.2 |
| `MapComponent_HugeFootprints` | **70.0 ms/tick of 70.9 summed (99%)**, max 457 ms in one tick | `jawa/map_comp_timing`, 304 ticks |
| next component | `RM_MapComponent_AcceleratedRot` 0.13 ms/tick | same |
| GC | 12.8 collections/min running vs 5.3/min paused; 135 in 634 s (one per 4.7 s) | TPS record `gc` counter |
| managed heap | ~5.0 GB | TPS record `heapMB` |
| worst frame gap | 350-780 ms per window | TPS record `gapMaxMs` |
| process memory | 30.6 GB private, 24 GB commit headroom, 9 GB physical free: no paging evidence | OS counters |
| map | 250x250 `RM_TheRot`, 36.3k things, 19 pawns, ~230 map components | TPS record / bridge |
| giants | 2,811 footprint giants | `jawa/list_things` over the 9 defs |
| blockers | ~7,400 `RM_HugeTrunkBlocker` (~12% of 62,500 cells) | `jawa/list_things` |
| refused claims | ~1,315 pending cells | quoted in the diagnosis; **instrument not recorded** (there is no `PendingCount` reader on the bridge; `DebugCounts`, which the proof script calls, does not exist in the source: grep of `src/RimMandrake/HugeThings` finds no such method). Treat as UNVERIFIED until §5.1's counters exist |

Gap between 88.4 (stage) and 70.9 (component sum): the two instruments ran in different windows and the stage figure
includes the profiler's own per-call overhead and other overrides; the 99% share is the robust fact, not the absolute.

GC attribution to HugeFootprints is a **hypothesis** (diagnosis line 21): the old path allocated per owner per tick
(§3.3). On a ~5 GB heap each collection is expensive (UNVERIFIED engine fact: Unity's Mono runtime uses the
non-generational Boehm collector, so each collection marks the whole live heap; that would make pause length scale with
heap size and pause frequency scale with our allocation rate, which matches 350-780 ms gaps). The proof run must
measure GC/min with the fix to settle it.

### 2.2 The instrument: `jawa/map_comp_timing` (`91f9c0a14`)

`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchMapCompTiming.cs` (test-only, `JAWA_GM_TOOLS`). Parameters
`ticks` (default 300), `maxSeconds` (120), `top` (30). It Harmony-patches every distinct `MapComponentTick`
override on the current map with a prefix + finalizer `Stopwatch`, waits for N **real** ticks at whatever speed is
set (never changes speed, never ticks itself), then unpatches (`UnpatchAll` in a `finally`) and returns per-type
calls/total/max with the owning mod.

Limits (READ-FROM-CODE, header lines 1-16 and the timer):
- **Per component, not inside it.** It names `MapComponent_HugeFootprints`; it cannot say whether time is in `Take`,
  `Flags`, `Plan`'s floods, `RelabelOwners` or GC. That is what §5.1 is for.
- Wall time between prefix and finalizer: **GC pauses triggered anywhere inside count against the component that
  happened to be running**. A component that allocates little can be billed for a collection another caused.
- Only the outermost call on the main thread is timed (nested `base.MapComponentTick` not double-counted); other
  threads are counted as `Foreign` and skipped.
- Does not see thing ticks (`Building_TrunkBlocker.TickRare`, the `Plant.TickLong` postfix): those land in `tl:*`
  stages of the TPS record.
- Patching itself perturbs JIT/inlining slightly; compare runs made with the same tool, not across tools.

### 2.3 Reproduction procedure (Rot quicktest)

Only with the bridge held (`rimflow bridge take --for "<what>"`); all bridge scripts run under Windows `python.exe`
from the repo root (WSL cannot reach the bridge). Steps 1-3 are what the 2026-10-10 runs did; step 2's biome choice is
**UNVERIFIED** (the logs say the quicktest landed on `RM_TheRot` 250x250 but not how it was chosen).

1. Game up on the full list with the current HugeThings DLL deployed: `python.exe src/RimMandrake/bridgetools/launch_ready.py --profile full`
   (~15-20 min cold load; MEASURED 1,225 s on 2026-10-10). Check `Mods\HugeThings\Assemblies\RM_HugeThings.dll`
   matches `src/RimMandrake/HugeThings/Assemblies/RM_HugeThings.dll` (+ `.srchash`) before trusting a result.
2. Quicktest map: `rimworld/start_debug_game_ready` with `readiness=currentMap` (as `Transient/_rot/b_start.py`). If
   the map is not `RM_TheRot`, re-biome it the way `src/RimMandrake/bridgetools/prove_biome_quicktest.py` does:
   `jawa/world_tile_set tiles=<tile> biome=RM_TheRot`, `jawa/world_commit`, `rimworld/execute_debug_action
   path="Actions\Regenerate Current Map"`, wait for `Playing`. Confirm with `jawa/map_info` (`mapBiome`, size 250x250).
3. Census: `jawa/list_things defName=<the 9 giant defs>` and `defName=RM_HugeTrunkBlocker` (record `countMatched`).
4. Let it run ~60 s at Normal so map-gen growth refreshes settle into steady state (otherwise the first minute is
   dominated by `MarkAllDirty`-like draining after Register).
5. `jawa/set_game_speed speed=Normal`, then `jawa/map_comp_timing ticks=300 maxSeconds=120`.
6. Speed legs: Normal, Fast, Superfast, 45 s each after a 10 s settle; read TPS, GC/min, `gapMaxMs`, stage
   ms/tick from the TPS record (`%LOCALAPPDATA%Low\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\tps_*.jsonl`).
7. All of 3-6 is scripted in `Transient/foundry_hugefix_measure_20261010.py <label>` (writes
   `Transient/foundry_hugefix_measure_<label>_20261010.json`); copy it out of Transient into
   `src/RimMandrake/bridgetools/` if it is to outlive the 14-day shelf. Its `DebugCounts` call will report
   UNMEASURED until that method exists.
8. Release the bridge the moment the run ends (`rimflow bridge release`).

Map generation is random per quicktest, so giant count, blocker count and pending count differ run to run: always
record them beside the timing, and compare before/after on the **same** map (deploy needs a game restart: the DLL is
locked while the game runs, so a true A/B needs a save of the generated map, loaded under each DLL).

## 3. Complexity analysis

All READ-FROM-CODE; the sizes plugged in are estimates labelled as such.

### 3.1 Symbols

| symbol | meaning | Rot value |
|---|---|---|
| n | registered giants (`comps.Count`) | 2,811 (MEASURED) |
| n_c | giants with at least one claim | UNMEASURED (`AB_GiantAgarilux`, weight 2, claims none) |
| P | pending cells | ~1,315 (UNVERIFIED instrument) |
| O_p | owners holding >= 1 pending cell | UNMEASURED; <= min(P, n_c) |
| B | realized blockers | ~7,400 (MEASURED) |
| m | pending cells of one owner | 1 to 118 |
| A | planning window area | see 3.2 |
| S | `Flags` scan area = window grown by 8 per side | see 3.2 |
| R | fixpoint passes in `Planner.Plan` | >= 1; up to m |
| T | things per cell (`GetThingList` length) | ~0.6 average (36.3k things / 62.5k cells), skewed |

### 3.2 Window sizes (READ-FROM-CODE, estimated arithmetic)

`MaxKeys()` (`CompHugeFootprint.cs:128-146`) sizes the window for full growth **and the largest setting**,
`MaxTrunkScale` = 1.5 (`RM_HugeThingsSettings.cs:16`), whatever the player's setting is (default 1.0). The window is
the union of the full picture box and a blocking square of side 1.5 x drawn width, plus `Planner.Margin` 4.

| species (drawn width) | window side ~ (1.5 w + 8) | A | S side (+16) | S |
|---|---|---|---|---|
| AgariluxPrime (20) | ~38 | ~1,444 | ~54 | ~2,900 |
| DribblingCap, Nogtyl (12) | ~26 | ~680 | ~42 | ~1,760 |
| Arpeau (10) | ~23 | ~530 | ~39 | ~1,520 |
| 6-7 wide species | ~17-19 | ~300-360 | ~33-35 | ~1,100-1,200 |

(The window is not square in z for every mask; these are upper-envelope estimates.) At the default 1.0 setting the
window is ~2.25x larger in area than the cells that can actually be claimed need.

### 3.3 Cost of one `RealizeOwner` call

```
CellsOf scan with pending.Contains          O(|cells_o| log P)
MaxKeys -> Signature (Roll, graphic, substring, Find)       O(variants) + allocation
Flags(window)                               O(S * T)  + O(A * T)  GetThingList/Walkable/InteractionCellsWhenAt
                                            allocs: Dictionary(A entries), HashSet<IntVec3>, List<IntVec3>
PlanItemMoves -> AssignAndPlan              Plan runs (1 + refused item sources) times
Planner.Plan per run:
  build pass[]                              O(A) dictionary lookups
  Reach (before)                            O(A), allocs bool[A] + Stack
  roots filter                              O(n)  <-- every giant on the map, per planned owner
  fixpoint: per pass, per candidate (m):
     cheap reject (pawn/item/protected)     O(1) + flagsAt lookup
     else: Reach(after)                     O(A), allocs bool[A] + Stack
           compare before/after             O(A)
           rootIdx.Contains / RootServed    O(roots in window)
  passes R: each pass accepts >= 1 or ends  => worst O(m^2 * A); typical O(m * A) when everything is accepted in pass 1,
                                               but an owner with permanently refused-by-reach cells pays a full extra pass
                                               (R >= 2 always when any cell is refused: the loop ends only on a pass
                                               that accepts nothing)
RealizeInOrder                              O(accepted) spawns
```

So per owner: **O(S*T + n + R*m*A)**, with the flood term dominating for big species with many reach-refused cells
(AgariluxPrime: m up to 118, A ~1,444: one pass with all candidates reaching the flood is ~170k cell visits, and two
passes are guaranteed whenever a refusal exists).

### 3.4 Per tick

| path | old (`8b910b055`) | new (`f3774dd15`) |
|---|---|---|
| drain dirty | <= 8 x Take | same |
| owner selection | O(P * owners-per-cell) SortedSet walk + SortedSet inserts | O(n) delegate calls over `comps.Keys` + `HasPending` for ~n/250 owners |
| owners planned | **O_p every tick a refresh happened (~every tick)** | ~O_p/250 + refreshed-with-pending (<= 8) |
| roots list | rebuilt, O(n), every realize | cached |
| roots filter in Plan | O(n) per planned owner -> **O(n * O_p) per tick (n x O_p ~ 2,811 x hundreds ~ 10^6)** | O(n) per planned owner -> ~O(n * O_p / 250) |
| relabel | O(B) on any tick with a claim move or spawn | same |
| `TickRare` ghost guard (thing ticks) | ~B/250 = 30 blockers/tick x `GetComponent` | same |

**Quadratic or worse:**
1. `roots` walk inside `Plan`: O(n) per planned owner, so O(n * O_p) per full realize. Old: every tick. New: every
   tick on 1/250th of owners, still O(n * O_p) per 250-tick cycle (with O_p ~ 400, UNVERIFIED: ~1.1 M checks per
   cycle, ~4.5k per tick: small now, but the shape is still quadratic in density).
2. `Planner.Plan` fixpoint: O(m^2 * A) worst per owner (R up to m).
3. `Deregister` -> `RelabelOwners` immediately: k giants dying in one event (fire, blight, a titan rampage,
   gravship clearing) costs O(k * B) = k x 7,400 primary-owner lookups.
4. `ItemMover.AssignAndPlan`: re-runs the whole `Plan` once per refused item source: O(sources * Plan).
5. `OwnersAt` (gravship): O(C) over every claim; rare, not hot.
6. `Reconcile` on load: n `Take`s + one unfiltered realize (the old per-tick worst case, once).

### 3.5 What allocates (per `RealizeOwner`, READ-FROM-CODE)

`List<long> mine`; `MaxKeys` list and signature work (`Substring` string per call, `CompHugeFootprint.cs:75`);
`Flags`: `Dictionary<long, CellFlags>` sized A (rehash growth), `HashSet<IntVec3>`, `List<IntVec3>`, a `CellRect`
enumerator; `PlanItemMoves`: two dictionaries, closures; `Plan`: `bool[A]` pass, `bool[A]` + `Stack<int>` per
`Reach` (once for `before`, once per flood candidate), `List<int> rootIdx`, `List<long> order` + `HashSet<long>`, the
sort comparison delegate; `RootServed` allocates two `int[4]` arrays **per call** (`RM_HugeClaimsKernel.cs:221`).
Per `Take`: `HashSet before`, the `want` HashSet, `drop`/`add` lists, a `SortedSet<int>` per newly claimed cell, two
signature recomputes. Per tick: the filter closure, `refreshed` HashSet, the `owners` SortedSet.

Rough garbage per old-path tick (UNVERIFIED estimate): O_p x (A x ~40 B dictionary + (R*m + 1) x A bytes of bool
arrays + stacks) ~ hundreds of owners x tens of KB ~ several MB/tick, i.e. hundreds of MB/s at speed 1, which on a
non-generational collector fits 12.8 GC/min. The new path cuts this roughly by the same factor as the owner count.

## 4. Candidate alternative algorithms

Each is scored on: complexity, expected gain (UNVERIFIED until §5 measures it), memory, correctness risk,
implementation cost (S/M/L), how to test it, and what the player would see. They compose; §4.18 proposes a stack.

### 4.1 Refusal reasons + negative cache invalidated by region version (event-driven retry) — **top pick**

Today a refused cell is retried every 250 ticks forever, re-deriving the same answer. Record *why* each pending
cell was refused and what it depended on, and retry only when that changed:
- Keep a per-chunk version counter (e.g. 8x8-cell chunks, 32x32 = 1,024 ints for 250x250), bumped by Harmony
  postfixes on the events that can change a planner input: `ThingGrid.Register/Deregister` (things spawn/despawn),
  `TerrainGrid.SetTerrain`, `PathGrid.RecalculatePerceivedPathCostAt` (or whichever single choke point covers
  walkability; UNVERIFIED which is cheapest and complete in 1.6), plus our own spawn/despawn of blockers.
- When an owner's plan leaves cells refused, store the max/hash of the versions of the chunks its scan area S covers.
  On the retry slot, compare versions first; if unchanged, skip the owner in O(chunks) without building flags.
- Pawns move constantly and a pawn-occupied cell is a refusal reason: track pawn refusals separately (retry on the
  slow cadence, or listen to `Pawn_PathFollower` cell changes in the chunk) so pawn traffic does not invalidate
  every chunk every tick. A cheaper variant: pawns do not bump versions; cells refused *only* for a pawn keep the
  250-tick retry, everything else is version-gated.
- Complexity: steady state O(owners due this tick x chunks in S) ~ O(1) each; a full plan only after a real change.
- Gain: in a settled map most of the 1,315 refusals are permanent (trees, other giants' roots, unwalkable terrain,
  reach) and would cost ~nothing. Expected to take the residual cost after `f3774dd15` near zero.
- Memory: 1 int per chunk + a version stamp per owner.
- Risk: a missed invalidation source = a cell that never closes (fail-safe direction: stays walkable, never traps).
  Add a very slow unconditional retry (e.g. every 60,000 ticks per owner) as a backstop.
- Cost: M (Harmony hooks + bookkeeping). Test: differential vs. always-retry on scripted scenarios (§5.3); a fuzz
  where random edits are applied and the gated and ungated runs must converge to the same realized set.
- Player sees: nothing, except trunks fill in at the moment the obstruction leaves rather than up to 4 s later.

### 4.2 Classify permanent refusals and stop retrying them — **top pick (cheapest first step of 4.1)**

Split refusal reasons: **permanent until a despawn** (cell holds another giant's root, a tree, an indestructible
thing, unwalkable terrain, a building), **transient** (pawn, item, blueprint/frame in progress), **topological**
(closing it would cut reach or a root). Permanent cells are parked in a per-owner "blocked-by" list keyed by the
blocking Thing's id; they come back only when that Thing despawns (Thing despawn is already observable: the plant
`PostDeSpawn`, the blocker `DeSpawn`; for other things a `ThingGrid.Deregister` postfix filtered to the parked cells).
Topological refusals depend on the window's ground and are retried on any version change (4.1) or slow cadence.
- Complexity: removes parked cells from every retry. Gain depends on the reason histogram, which is UNMEASURED and
  is the first thing §5.1 must produce. If most of the 1,315 are "another giant stands there" (likely at 12%
  blocker density, UNVERIFIED), most work disappears.
- Memory: a small dictionary. Risk: low (a parked cell is still claimed, so it closes when freed). Cost: S.
- Player sees: nothing.

### 4.3 O(1) local "simple point" test before the flood, and incremental reach — **top pick**

`Planner.Plan` runs a full-window flood for every candidate. Digital topology gives a constant-time **sufficient**
test: if the passable cells among c's 8 neighbours form exactly one 4-connected arc around c (the "simple point"
test, using the 4/8 connectivity pair consistently), removing c cannot change connectivity of the remaining
passable cells, so `before`/`after` reach is unchanged and the flood can be skipped. Only when the local test says
"might split" run the flood. Root access is local too (`RootServed` looks at 4 neighbours; only roots adjacent to c
can change, plus roots whose only reach went through c, which the split case covers).
- Complexity: most acceptances become O(1); floods only at genuine cut candidates. From O(R*m*A) toward O(m + cuts*A).
- Further: when a flood *is* needed, flood only from c's neighbours outward with early exit as soon as all of c's
  passable neighbours are reconnected to each other or to the border (bidirectional/meet-in-middle), instead of a
  full-window flood plus a full-window compare.
- Risk: the local test must be exactly right for 4-connected pathing in RimWorld (diagonal moves are blocked if
  either orthogonal neighbour is impassable in vanilla; UNVERIFIED for 1.6 whether reach for our purposes should be
  4- or 8-connected; today's `Reach` is 4-connected, so match that). A wrong local test = a pocket. The existing
  fuzz (`HugeThingsFuzz.cs` "planner" family checks "never cuts a cell off" against an independent flood) is exactly
  the oracle: run it with the shortcut enabled.
- Memory: none. Cost: S-M, Verse-free kernel only. Player sees: nothing (identical results if the test is sound).

### 4.4 Hard per-tick time budget with a round-robin cursor

Replace "owners in this tick's phase" with: a cursor over a stable ordered list of owners with work; plan owners
until a `Stopwatch` budget (e.g. 0.5-1 ms) is spent, resume next tick. Refreshed owners go to the front.
- Complexity: bounded per tick by construction. Gain: caps the worst tick (the 457 ms max) whatever the density.
- Risk: under overload the effective retry interval stretches beyond 250 ticks (fine: fail-safe). Determinism: a
  wall-clock budget makes the *schedule* machine-dependent, so the realized set can differ between machines and
  between a save and its reload. To keep determinism, budget in **work units** (cells flooded, owners planned)
  instead of milliseconds.
- Cost: S. Test: synthetic overload (§5.2) asserting max per-tick work units and eventual convergence.
- Player sees: nothing, or slower fill-in on a pathological map.

### 4.5 Planner buffers pooled, flags as arrays (zero-GC planning)

Keep one reusable `bool[]`/`byte[]` scratch for `pass`, `before`, `after` (sized to the largest window, max 512^2
guard already exists), one reusable `int[]` stack, a reusable `CellFlags[]` window array instead of
`Dictionary<long, CellFlags>`, static `dx/dz` arrays in `RootServed`, no closures in the hot path (pass a struct
`IFlagSource` or the array directly). Cache `MaxKeys()` per owner (constant for a plant at a setting; invalidate on
settings change).
- Complexity: same big-O, smaller constants (dictionary hashing -> array indexing is often 5-10x). Gain on GC: the
  dominant allocator becomes ~0 bytes/plan. Memory: one window-sized scratch per map component. Risk: very low.
  Cost: S. Test: allocation counter per tick (§5.1) must read ~0 in steady state; fuzz must stay green.
- Player sees: fewer GC hitches if the GC hypothesis holds.

### 4.6 Map-wide cell arrays instead of hashed ledgers (struct-of-arrays)

Index everything by `map.cellIndices.CellToIndex` (62,500 cells): `ushort ownerCount[]`, `int primaryOwner[]`
(maintained as min), `BitArray pending`, `Building_TrunkBlocker[] realizedAt`, and per owner a compact `int[]` of
cell indices instead of `HashSet<long>`. Shared cells with >1 owner (rare? UNMEASURED) keep a small side dictionary
of owner lists. `pending` as a bitset makes `HasPending` a word scan and removes the `SortedSet<long>`.
- Complexity: O(1) per cell op without hashing; `RelabelOwners` becomes a walk over changed cells only (4.9).
  Memory: ~62,500 x (2+4+8) B ~ 0.9 MB per map, less than the dictionaries it replaces (UNVERIFIED).
- Risk: medium (rewrite of `ClaimLedger`; the ledger's order-independence must hold; fuzz "ledger" family covers it).
  Cost: M. Player sees: nothing.

### 4.7 Incrementally maintained global flags grid

`Flags(window)` re-scans S cells with `GetThingList` per owner per attempt. Maintain one `byte[] cellFlags` per map,
updated on the same events as 4.1 (thing register/deregister, terrain change), including interaction-cell and
door-approach protection computed once per building at spawn (and removed at despawn; reference-counted, since
protections overlap). Planning then reads flags in O(A) array copies.
- Complexity: removes the O(S*T) term entirely. Gain: large for small species where Flags dominates. Memory: 62.5 KB.
- Risk: medium-high: every flag source must be hooked (blueprints, frames, minified things, quest items, pawns
  moving: pawns would stay a live `GetFirstPawn` check at realize time, which already exists in `Spawn`).
  Interaction cells of buildings from other mods with custom `InteractionCell` overrides could be missed.
- Cost: M-L. Test: a debug command that recomputes flags from scratch and diffs against the maintained grid,
  run in the fuzz and as a live state read.

### 4.8 Cluster overlapping owners (union-find) and plan per cluster with a canonical order

Union owners whose planning windows overlap (union-find over a spatial hash of windows); plan each cluster once, in
a canonical order (all pending cells of the cluster sorted by (z, x), one shared window = the cluster's bounding box,
capped). One flood structure serves the whole cluster instead of one per owner.
- Complexity: removes duplicated flag scans and floods where windows overlap (at 12% blocker density most do). Cost
  per cluster O(S_cluster + plan); clusters can merge into a map-sized blob at high density, so cap the cluster box
  (fall back to per-owner) or partition by tiles.
- Correctness bonus: the realized set becomes **independent of owner refresh order** within a cluster (one canonical
  plan), which the current per-owner sequence does not guarantee (§1.6 risk), and it makes save/load and the
  old-vs-new differential test well defined.
- Risk: medium (window semantics change: a bigger window sees a farther border, which the 2026-10-07 fuzz finding
  says changes answers: "a later pass would judge reachability against a nearer border", `RM_HugeClaimsKernel.cs:103-105`).
  Must keep each cluster's window fixed (not dependent on what is open). Cost: M.

### 4.9 Incremental relabel and deferred deregister work

`RelabelOwners` walks all B blockers whenever anything changed. Track the set of cells whose owner set changed
(from `ledger.Set` add/drop and `Open`/`Spawn`) and relabel only those. `Deregister` should queue its freed cells
and let the tick relabel them, so a mass die-off costs O(cells freed), not O(k * B).
- Complexity: O(B) -> O(changed). Risk: low (primary owner = min of a cell's set is local). Cost: S.
- Player sees: no hitch when a fire or titan kills many giants at once.

### 4.10 Skip owners that cannot have work: no-claim giants and unchanged refreshes

(a) Keep a separate list of owners that actually hold claims (n_c) and walk only that for retries; zero-contact
species (`AB_GiantAgarilux`) never enter it. (b) After `Take`, only add the owner to `refreshed` if its claims
actually changed (`ledger.Set` returned non-empty claimed/freed); a growth tick that moves the signature but not the
cells should not re-plan. (c) Cache the phase buckets: an array of 250 lists of owner ids, so a tick visits only its
bucket (O(n/250)) instead of filtering all n.
- Complexity: per-tick O(n) walk -> O(n/250). Gain: small but free. Risk: very low. Cost: S.

### 4.11 Bit-parallel flood and mask tests

Windows are at most ~38 cells wide for the largest species (§3.2), so each window row fits in one `ulong`. Flood
fill by row bitmasks: seed = border bits; repeat { row |= ((row << 1) | (row >> 1) | up | down) & passRow } until no
change; each sweep processes 64 cells per op. Typically 10-50x faster than the stack flood (UNVERIFIED for this
size). Mask overlap tests (is any of an owner's footprint over a protected cell) become AND of row words.
- Complexity: O(A/64 * iterations), iterations bounded by the longest path but usually small. Memory: tiny, no GC.
- Risk: low with the existing fuzz oracle. Cost: S-M. Composes with 4.3 (fewer floods, each cheaper).

### 4.12 Precompute placement at world freeze (the world is hand-made and shipped)

The owner's ruling is one frozen world shipped as a savegame (CLAUDE.md "no worldgen"). The giants on shipped maps
are fixed at freeze time; run the planner to convergence offline/at freeze and save the result. At runtime only
deltas (growth, cut, building) are planned.
- Complexity: shifts all initial cost out of play. Gain: removes the load-time `Reconcile` realize spike and the
  first-minutes churn on shipped maps. Does nothing for maps generated in play (quicktests, new settlements, sea
  floor layers, any other tile the player visits: map gen happens per visited tile, so this is only a partial
  answer).
- Requires saving component state (`ExposeData`: refusal cache, versions), which today is deliberately zero.
- Risk: medium (saved state can go stale against a mod change; `Reconcile` must remain authoritative). Cost: M.

### 4.13 No blocker Things at all: a cell flag consulted by pathing

Replace 7,400 `Building_TrunkBlocker` Things with a per-map bit array and Harmony patches at the engine's
walkability/edifice choke points (path grid cost calculation, `GenConstruct.CanPlaceBlueprintAt`, plant
`BlocksPlanting`/sowing, projectile intercept for cover, `CoverUtility`, region building). The design doc rejected a
*path-cost* patch for not refusing buildings or plants; this variant patches those too.
- Gain: 7,400 fewer Things (save size, `listerThings`, ~30 `TickRare` per tick, region/lister bookkeeping, spawn and
  despawn cost in `Spawn`/`Open`), and blocker spawn/despawn becomes a bit flip (cheap, so re-planning could be
  far more aggressive). Does not by itself make the planner cheaper.
- Risk: **high**. Regions and rooms in 1.6 are built from the path grid and edifice grid; every vanilla and modded
  consumer that asks "is there an edifice / impassable thing here" would need covering, and missing one = pawns
  walking through trunks or building inside them. Damage forwarding and cover would need reimplementation.
- Cost: L. Test: a battery of vanilla interactions per cell (path, build, sow, shoot, explode, zone, roof, fire).
- Player sees: if complete, nothing; partial = visible bugs. Recommend only after 4.1-4.5 if Things are still the
  dominant cost (profile `tl:Rare`, save/load time, lister cost first).

### 4.14 Use the vanilla region/reachability system instead of our own floods

Ask "does closing c split a region" using RimWorld's regions/rooms (precomputed connectivity) rather than flooding.
- Gain: potentially O(1) queries. Risk: high: regions only update after a thing actually spawns, so a tentative
  close cannot be asked without spawning; `RegionAndRoomUpdater` work per blocker spawn is itself costly. Probably
  not usable for tentative planning; noted for GPT to rule out or in.

### 4.15 Tick-interval sleep: plan on a coarse cadence, nothing between

Run the retry work every K ticks (e.g. 60) in a batch, or from a `TickRare`-like counter, and return immediately on
other ticks when there is no dirty owner. With 4.1/4.2 in place the batch is usually empty.
- Same total work as today's spread, so on its own it is a **regression** for frame smoothness (lumps) unless the
  batch is small; useful only as the "sleep when nothing changed" half of 4.1. Cost: S.

### 4.16 Exponential backoff for repeatedly refused cells (approximation)

Per owner, double its retry interval after each attempt that closed nothing (250, 500, 1,000 ... up to e.g.
16,000 ticks), reset on any version change (4.1) or on its own refresh. Without 4.1 it is a pure approximation: a
cell that became closable could stay open for up to the max interval (~4.4 min at speed 1).
- Complexity: steady-state work drops geometrically. Risk: low (fail-safe direction: open cells). Cost: S.
- Player sees: a trunk cell might stay walkable for minutes after an item or pawn leaves. Probably acceptable for
  rare cases; ask the owner if it becomes the shipped approach.

### 4.17 Plan only from `Plant.TickLong` (per-plant cadence), not from the map component

CLAUDE.md: `Plant` never overrides `Tick()`, only `TickLong()`. The growth check already runs from a `Plant.TickLong`
postfix. Move the per-owner retry there too: each giant retries its own pending cells in its TickLong (every 2,000
ticks per plant, ~1.4 plants per tick on the Rot), and the map component handles only events.
- Complexity: per tick ~1.4 owners instead of n/250 ~ 11; natural staggering by the engine's own TickLong hashing.
- Risk: retry interval becomes 2,000 ticks (8x slower than today) unless events (4.1) wake owners; TickLong runs in
  thing ticking, so the cost moves from `mapComp` to `tl:Long` in the TPS record (keep that in mind when reading it).
- Cost: S. Player sees: slower fill-in without 4.1.

### 4.18 Recommended stack, in order

1. **Measure first** (§5.1): refusal-reason histogram, per-scope timings, allocations per tick. Decides between the
   rest.
2. 4.10 + 4.9 + 4.5 (cheap, low-risk, remove the O(n) walk, the O(B) relabel and the garbage).
3. 4.2 then 4.1 (stop re-deriving permanent refusals; then version-gate the rest).
4. 4.3 + 4.11 inside `Planner.Plan` (make each plan that does run cheap).
5. 4.4 in work units as a hard cap.
6. 4.8 if the differential/determinism tests show order dependence matters; 4.12 and 4.13 only if Things or load
   time are still the problem afterwards.

## 5. Test plan

### 5.1 Instrumentation inside the component (proposed; nothing below exists yet)

A `HugeFootprintsProfile` static (compiled always, gated by one `static bool Enabled`, default off; zero cost when
off apart from a branch) with `Stopwatch.GetTimestamp()` scopes and counters, plus a bridge-readable
`public static string DebugCounts(string mapSpec)` (the name `Transient/foundry_hugefix_measure_20261010.py` already
calls through `jawa/static_call`), returning JSON.

Scopes (ticks of `Stopwatch`, summed and max per sample window):
`tick.total`, `tick.drain` (Take), `tick.select` (owner filter / HasPending), `realize.owner` total, and inside it
`maxkeys`, `flags.scan` (interaction/door pass), `flags.cells`, `plan.build`, `plan.reachBefore`, `plan.floods`,
`plan.compare`, `plan.roots`, `itemmover`, `spawn`, plus `relabel`, `deregister`, `reconcile`.

Counters per window: owners planned, owners skipped (no pending), refreshed owners, refreshes with unchanged claims,
pending cells examined, cells accepted, floods run, flood cells visited, fixpoint passes, blockers spawned/opened,
relabel cells walked, item moves planned/done; **refusal reasons** per pending cell (not passable, pawn, item,
protected-by-building, protected-by-tree/giant, interaction cell, door approach, indestructible, reach cut, root cut,
out of window, after-first-failure in `RealizeInOrder`), and how many of those reasons were the same as at the
previous attempt (the "re-derived answer" rate that 4.1/4.2 would save).

Allocations: `GC.GetTotalMemory(false)` delta around `MapComponentTick` is unreliable under Boehm (UNVERIFIED);
better is `GC.CollectionCount(0)` per sample window and, in the offline harness (5.2), exact byte counts via
`GC.GetAllocatedBytesForCurrentThread()` on .NET (not available on Unity Mono; UNVERIFIED for RimWorld's runtime).

Flame summary: `DebugCounts` returns the scopes as a nested breakdown (`self` vs `children`), so one bridge call gives
the flame. Shape: `{"window_ticks":300,"scopes":{"tick.total":{"ms":..,"max":..,"children":{...}}},"counters":{...},"refusals":{...}}`.

Also add the TPS-record cross-check: run with `Enabled` on and off and confirm the instrument's own overhead is
< 5% of `tick.total`.

### 5.2 Offline synthetic benchmark (Verse-free)

The planner, ledger and item mover are already Verse-free (`Kernel/RM_HugeClaimsKernel.cs`), compiled by the
self-test project `Source/SelfTest/RimMandrakeHugeThings.SelfTest.csproj`. The realize loop in
`MapComponent_HugeFootprints` is not: to benchmark it offline, extract the loop (owner selection, per-owner
window/flags/plan/realize, relabel) into the kernel behind an interface `IFootprintWorld` { flags at cell, spawn
blocker, item count, pawn at cell } with a fake grid implementation. That extraction is also what lets old and new
algorithms run side by side.

Scenarios (seeded, deterministic):
- Map 250x250. n = 500, 1,000, 2,811 giants, species mix from the Rot weights (§1.2) and the real contact masks read
  from `RotGiants_HugeFootprint.xml`.
- Placement: sparse (Poisson, min spacing = window), Rot-realistic (biome weights x `plantDensity` 0.6, overlapping
  allowed), adversarial (giants packed so windows overlap 4-8 deep, forcing reach refusals).
- Obstructions: 0%, 5%, 20% of cells holding "trees/buildings"; 20 wandering "pawns" moving one cell per tick.
- Phases: cold start (all dirty), growth (each owner's growth steps every 2,000 ticks), steady state, churn (k giants
  cut per 1,000 ticks), mass death (500 at once).
- Output per scenario: ms/tick mean/p99/max, work counters (§5.1), bytes allocated per tick, final realized count,
  pending count, refusal-reason histogram. Run on .NET with BenchmarkDotNet-style warmup or a plain loop; absolute ms
  differ from Mono in-game, so compare **ratios** between algorithms, and calibrate one scenario against the live
  number (70 ms on the Rot map, old code).

### 5.3 Differential tests (old vs new, and every alternative)

- Keep the old algorithm as a reference implementation in the self-test project (`RealizePendingAll`).
- For each scenario and seed: run old and candidate for the same event script, then **after quiescence** (no dirty
  owners, retries exhausted with no change) compare: (a) the ledger (must be identical: claims are order-independent
  by construction), (b) the realized set, (c) the pending set.
- Expected: (a) always equal. (b)/(c) may legitimately differ when order changes what is closable. So the test
  asserts the **safety** properties on both (no pawn/item/protected cell closed, no passable cell cut off from the
  window border, every root that had access keeps it: the existing fuzz "planner" oracle) and **reports** the
  difference size. A difference becomes a finding only if one side is unsafe or one side closes strictly fewer
  cells with no refusal reason (lost work).
- For alternatives that should be exact (4.3 local test, 4.5 pooling, 4.6 arrays, 4.9 relabel, 4.10 skips, 4.11
  bit flood): realized sets must be **identical** to the per-owner reference given the same schedule.
- For 4.1/4.2 (gated retries): after quiescence the gated run must equal an ungated run with the same schedule.

### 5.4 Determinism across save/load

- In the harness: snapshot (ledger, realized, pending, owner ids, tick) at tick T, rebuild a fresh component from
  the snapshot the way `Reconcile` does (plants + blockers only), run both to T + 5,000 with the same events, compare.
  Today `Reconcile` performs an unfiltered realize on load that the continuing run does not, so the two can diverge;
  the test makes that visible (either accept it as "load may close cells early", or make load mirror the schedule).
- Live: save the Rot quicktest map, load it, run 2,000 ticks at Normal, census blockers; repeat the load and compare
  counts (state read, no screenshots).

### 5.5 Live acceptance on the Rot map

Procedure §2.3, on one saved Rot map loaded under each DLL (same map for before/after). Pass bars (proposed, not yet
the owner's):
- `MapComponent_HugeFootprints` <= 1 ms/tick mean and <= 16 ms max over 300 ticks at Normal (`map_comp_timing`).
- map-component stage no longer the top stage in the TPS record.
- TPS at Normal / Fast / Superfast reported for the map (record the numbers; the target is the vanilla speed cap at
  Normal and Fast if nothing else dominates).
- GC/min running within 1.5x of paused.
- blockers and giants unchanged by the run (census before/after), pending count reported.
- No `[RimMandrake.HugeThings]` errors in `Player.log` during the run.

## 6. Open questions for GPT

1. Given the planner's contract (close a cell only if no passable cell loses reach to the window border and no root
   loses its open neighbour), what is the tightest **O(1) local test** (simple-point / Euler-characteristic) that is
   *sufficient* for 4-connected reach, and which configurations must still fall back to a flood? Is a 3x3 test
   enough or does root access need 5x5?
2. Is there an incremental connectivity structure (dynamic connectivity under deletions, e.g. offline reverse
   union-find over the acceptance order, or Holm-de Lichtenberg-Thorup) that fits a window of ~1,500 cells with up to
   ~120 deletions per plan and beats repeated floods in practice in Mono, or is bit-parallel flooding (4.11) the
   right engineering answer at this size?
3. The fixpoint loop repeats full passes until nothing is accepted. Is there an ordering (e.g. process cells by
   distance from the border, or by "peel from the outside in") that reaches the same fixpoint in one pass, and can
   we prove the result is order-independent?
4. Order dependence between overlapping owners: what canonical rule makes the realized set a function of the
   claimed set and the ground alone (independent of refresh order and of save/load), and what does it cost?
   Is cluster planning (4.8) the right shape, and how should the window be fixed so it does not depend on what is
   open (`RM_HugeClaimsKernel.cs:103-105`)?
5. For the negative cache (4.1): what is the minimal complete set of RimWorld 1.6 events that can change a planner
   input (walkability, things in cell, interaction cells, doors, terrain, roofs?), and the cheapest Harmony choke
   points for them? Is `ThingGrid.Register/Deregister` + `TerrainGrid.SetTerrain` complete?
6. Pawns: pawn-occupied cells are a refusal reason that changes every tick. What is the best way to retry those
   without versioning every chunk on every pawn step: listen to pawn arrival/departure at the specific parked
   cells, or keep a slow cadence only for pawn refusals?
7. Is the GC hypothesis plausible: on Unity Mono (RimWorld 1.6, Boehm, incremental or not?), does a ~5 GB heap make
   each collection cost scale with heap size so that our allocation rate directly sets the 350-780 ms gaps? What is
   the best in-game way to measure bytes allocated per tick on that runtime?
8. Should trunk blockers stay Things at all (4.13)? Which 1.6 systems would need patching if impassability came from
   a cell flag (path grid, regions/rooms, edifice grid, blueprints, sowing, cover, projectiles, explosions, fire,
   roofs, zones, minification/gravship), and is there a smaller, safer middle ground (e.g. a single `Thing` per giant
   that occupies a non-rectangular cell set)?
9. Window sizing: the window is built for `MaxTrunkScale` 1.5 at full growth (§3.2), ~2.25x the area needed at the
   default setting. Is shrinking it to the current setting safe given the "window must not depend on what is open"
   rule, and what does a settings change then require?
10. Is there a better approximation for the root-access rule than a flood (e.g. require that each root keep one open
    4-neighbour that is itself not a candidate this pass)?
11. Budgeting: deterministic work-unit budgets vs. wall-clock budgets: how to cap per-tick cost without making the
    realized set depend on machine speed?
12. Precompute at freeze (4.12): worth saving component state (refusal cache, versions) in the save, or is a fast
    `Reconcile` that trusts the saved blockers (and only verifies them lazily) better?
13. The `ItemMover.AssignAndPlan` loop re-runs the whole plan once per refused source. Can item assignment be folded
    into one plan pass?
14. What else in this design is quadratic in density that we have not seen, and which single counter would expose
    it first?
15. Given §5's harness, which 3 scenarios would best predict the live Rot number, so we stop needing 20-minute cold
    loads to evaluate an algorithm?
