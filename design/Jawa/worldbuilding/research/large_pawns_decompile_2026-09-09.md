# Large Pawns (`neku.largepawns`) — decompile findings

For **TITANIC_CREATURES_MOD_1**, the ride-vs-absorb decision. Offline research,
2026-09-09. Every claim below is from the decompiled IL, never the workshop
description (where the two disagree, that is called out).

**Artifact**: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3777700657\Current\Assemblies\LargePawns.dll`
(127,488 bytes, mtime 2026-09-03, modVersion **0.24.16**, supportedVersions `1.6`,
depends `brrainz.harmony`, `loadAfter` MemeGoddess.GiddyUp / Krkr.rule56 /
Aoba.Exosuit.Framework). Decompiled with `ilspycmd` 8.2 → 9,378 lines C#.
`Defs/Placeholder.xml` is an empty comment block; the mod ships **no defs at all**.
`archive/` is empty. Namespaces: `LargePawns`, `LargePawns.Patches`.

**VERDICT: ride-with-config.** Details in §7.

---

## 1. Harmony patch inventory

`Main` is `[StaticConstructorOnStartup]`; its static ctor does
`new Harmony("neku.largepawns").PatchAll()`. **68 attribute-declared patches** on
vanilla types, plus reflection-applied compat patches (§1.5) attached from the
`Main(ModContentPack)` ctor via `MountedSizePatch.EnsureApplied` and
`CaiCompatHelper.EnsureApplied`. There is **no conditional/`Prepare` gating on the
vanilla 68** — they all apply unconditionally, and each guards at runtime with
`LargePawnUtility.IsLarge/IsEffectiveLarge` (which returns fast for size 1).

### 1.1 Pathfinding / movement (17)
| Target | Kind |
|---|---|
| `Pawn_PathFollower.SetupMoveIntoNextCell` | Postfix (door opening) **and** Prefix (empty-path guard) — two separate patches |
| `Pawn_PathFollower.TryEnterNextPathCell` | door opening on arrival |
| `Pawn_PathFollower.PawnCanOccupy` | square-aware |
| `Pawn_PathFollower.NeedNewPath` | square-aware |
| `Pawn_PathFollower.StartPath` | square gate |
| `Pawn_PathFollower.CostToMoveIntoCell` | square cost |
| `Pawn_PathFollower.PatherTick` | unstuck handling |
| `Pawn_PathFollower.PatherFailed` | (Giddy-Up-conditional, §1.5) |
| `PathFinder.CalculateDestinationRect` | large-target dest rect |
| `PathFinder.ParameterizePathJob` | dest rect |
| `PathFinder` (`CreateRequest`) | injects `LargePawnGridCustomizer` |
| `PathGridDoorsBlockedJob.Execute` | Postfix, square-aware |
| `GenGrid.WalkableBy(IntVec3,Map,Pawn)` | Prefix, whole-square walkability |
| `GenGrid.StandableBy` | Prefix, whole-square |
| `JobGiver_MoveToStandable.TryGiveJob` | square-aware |
| `WalkPathFinder.TryFindWalkPath` | square-aware |
| `JobGiver_AIWaitAmbush.TryGiveJob` / `JobGiver_Manhunter.TryGiveJob` (wander cell) | square-aware |

### 1.2 Reachability / regions (12)
`Reachability.CanReach` · `Reachability.CanReachMapEdge` ·
`Reachability.CanReachUnfogged` · `ReachabilityImmediate.CanReachImmediate` (two
patches: `_L3Patch` and `_SquarePatch`) · `ReachabilityWithinRegion.ThingFromRegionListerReachable` ·
`RegionAndRoomQuery.GetRegion` · `RegionAndRoomQuery.GetDistrict` ·
`RegionTraverser.WithinRegions` · `RegionListersUpdater.RegisterInRegions` ·
`RegionListersUpdater.DeregisterInRegions` · `GenAdj.OccupiedRect(Thing)`.

Plus cell-finders that must land a whole square: `RCellFinder.BestOrderedGotoDestNear`,
`.CanWanderToCell`, `.RandomWanderDestFor`, `.IsGoodDestinationFor`,
`.TryFindRandomCellInRegionUnforbidden`, `CellFinder.TryFindRandomReachableNearbyCell`.

**The mod runs its own parallel region graph.** `LargePawnRegionGrid` /
`LargePawnRegion` / `LargePawnDistrict` / `LargePawnRegionRegistry` — a full
flood-filled anchor-region graph, **one grid per `(size, fenceBlocked)` pair**
(so up to 8 per map: sizes 1–4 × fences on/off), each sized
`map.cellIndices.NumGridCells`. This is the single largest thing to be aware of;
it is not a thin wrapper over vanilla regions.

### 1.3 Combat / hit detection (11)
`AttackTargetFinder.BestAttackTarget` · `CastPositionFinder.EvaluateCell` ·
`.CastPositionPreference` · `.TryFindCastPosition` · `ShootLeanUtility.CalcShootableCellsOf` ·
`CoverUtility.CalculateOverallBlockChance` · `CoverUtility.CalculateCoverGiverSet` ·
`ShotReport.HitReportFor` · `GenSight.LineOfSightToThing` ·
`Verb.TryFindShootLineFromTo` (large melee) · `Toils_Combat.FollowAndMeleeAttack`
(melee zone) · `PawnUtility.PawnBlockingPathAt`.

Also `JobGiver_AIFightEnemy.TryGiveJob`, `JobGiver_Berserk.TryGiveJob`,
`JobGiver_Manhunter.TryGiveJob` — these three are the **path-clearing** patches
(§4b), each gated by its own ModSetting bool.

### 1.4 Rendering / interaction / reservation (10)
`Pawn_DrawTracker.get_DrawPos` (square-centre) · `Thing.get_CustomRectForSelector` ·
`SelectionDrawer.DrawSelectionBracketFor` (smooth) · `Thing.GetGizmos` (debug
visualiser gizmos) · `ThingGrid.Register` / `ThingGrid.Deregister` (registers the
pawn in **every** footprint cell) · `Building_Trap.Tick` (Postfix; adds a large
pawn to `touchingPawns` if its square covers the trap) · `CompAssignableToPawn_Bed.CanAssignTo` ·
`RestUtility.IsValidBedFor` · `Toils_LayDown.LayDown` · `JobDriver_CarryDownedPawn.MakeNewToils` ·
`StoreUtility.IsGoodStoreCell` · `HaulAIUtility.HaulablePlaceValidator` ·
`GenSpawn.Spawn` (footprint placement on spawn).

⚠️ **No reservation-manager patches.** `ReservationManager`/`Pawn_JobTracker` are
untouched — reservations remain single-cell.

### 1.5 Third-party compat, applied by reflection at ctor time
- **Giddy-Up** (`MountedSizePatch.EnsureApplied`): patches
  `GiddyUp.Jobs.JobDriver_Mounted.RiderShouldDismount`, `GiddyUp.MountUtility`
  (mount rebuild-path + `TryAutoMount`), and vanilla `Pawn_PathFollower.PatherFailed`.
  Keeps a `RemountBlock` dictionary with a 600-tick cooldown.
- **CombatAI / CAI-5000** (`CaiCompatHelper.EnsureApplied`): `CombatAI.CoverPositionFinder`,
  `CombatAI.PawnPathUtility.GetMovingShiftedPosition`, `CombatAI.SightGrid.GetShiftedPosition`,
  `CombatAI.SightGrid.TryCastSight`.
- **Exosuit Framework** (`ExosuitCompat`): resolves `Exosuit.Exosuit_Core` by name;
  supplies an external size override.
- **Vehicle Framework**: not patched — instead `IsVehicleDef` resolves
  `Vehicles.VehicleDef` and **forces size 1**, i.e. vehicles are explicitly excluded
  rather than supported. (The description's "fully compatible" means "stays out of
  the way".)

---

## 2. Footprint computation — thresholds ARE configurable, and there IS a per-def table

`LargePawns.Settings : ModSettings`:

```csharp
public float size2Min = 2.5f;   // -> 2x2
public float size3Min = 4.5f;   // -> 3x3
public float size4Min = 10f;    // -> 4x4
public bool  maxCostMode = true;             // max-over-square vs sum-over-square path cost
public bool  pathClearingManhunter = true;
public bool  pathClearingBerserk   = true;
public bool  pathClearingAIFight   = true;
public List<SizeOverride>  sizeOverrides;    // { defName, size }  size 1..4, 0 = "no override"
public List<SpriteOffset>  spriteOffsets;    // { defName, x, z }
```

`LargePawnUtility.GetSize(Pawn)` resolution order:
1. size 1 if disabled / null / **dead** / **unspawned** / `IsVehicleDef`;
2. `settings.GetSizeOverride(def.defName)` if in **1..4** — a hard per-def
   override **in both directions** (1 = force single-cell opt-OUT, 2–4 = opt-IN);
3. `ExternalOverrideSize` (Exosuit only);
4. an early-out: if `def.race.baseBodySize < size2Min` **and** lifestage
   `bodySizeFactor <= 1` **and** the pawn has no genes → size 1 (so a gene/lifestage
   swelling past the threshold still counts, but a small base can't be pushed over
   by a bonus alone);
5. otherwise `pawn.BodySize` against `size4Min` / `size3Min` / `size2Min`.

**Ceiling is 4×4.** There is no size-5 branch anywhere. Our T3 ("4x4+") cannot go
higher inside this mod.

**How the per-def table is populated — this is the friction point.**
`LargePawnUtility.EnsureDefTables()` runs from the `Main` ctor and **appends a
`SizeOverride` (size 0) and a `SpriteOffset` (0,0) row for EVERY `ThingDef` with
`category == Pawn`**, then calls `ModSettings.Write()`. On a ~590-mod list that is
several thousand rows written into
`…\Config\Mod_neku.largepawns_LargePawns.xml` at startup, and it re-runs whenever
the mod list grows. Consequences for us:

- ⚠️ **The override table lives in the user's ModSettings, not in mod XML.** There
  is **no `DefModExtension`, no XML patch surface, no def-driven opt-in** — `grep`
  for `DefModExtension`/`GetModExtension` in the assembly returns **zero hits**.
  A mod cannot ship its size decisions as data; it must write that config or poke
  `Main.settings` at runtime.
- The settings UI (`Main.DoSettingsWindowContents`) is a tabbed, scrolling table of
  every pawn def with float buffers — hand-curating thousands of rows is not viable.

---

## 3. Doors and 1-tile gaps — **blocked, never squeezed**

`SquareStandableOrOpenableDoorForEffective(pawn, center)` walks **every** cell of
the `CellRect` and returns false unless each is in-bounds and
`CellWalkableRaw`; a non-standable cell is only forgiven if it holds a
`Building_Door` the pawn `PawnCanOpen` and is not forbidden to pass. Likewise
`GenGrid_WalkableBy_LargePawnPatch` fails the whole cell the moment any footprint
cell is unwalkable. **A 2×2 pawn therefore needs a 2-wide opening; a 1-tile gap or
a single vanilla door blocks it.** (The description's "opens double/triple doors"
is accurate; "reaches beds through narrow corridors" only means the region graph
finds *square-wide* corridors.)

Door mechanics when the square does fit: `SetupMoveIntoNextCell` Postfix opens
**all** openable doors under the destination square at once
(`StartManualOpenBy` + `CheckFriendlyTouched`), and if any is `SlowsPawns` with
`TicksTillFullyOpened > 0` it applies a `Stance_Cooldown` for the slowest one.
`TryEnterNextPathCell` re-opens doors under the square on arrival.

**The author's own known-hard area is exactly this.** The mod folder ships two
Russian-language Python simulations at its root —
`REGION-CONNECTIVITY-TEST.py` and `REGION-DOOR-TEST.py` — that model
`LargePawnRegionGrid` on a synthetic map to chase a bug labelled **PAWN-048**
("Reachable cells passes, Regions(pawn) does not, for a 2×2 pawn through a
2-wide door"), sweeping opening widths 1..4. They are debugging scaffolding
left in a shipped mod; treat door/portal region connectivity as the least
settled part of the framework.

---

## 4. Pens, caravans, saving/loading, fragility

**a. Pens: no handling at all.** Zero patches on `CompAnimalPenMarker`,
`AnimalPenUtility`, `PenFoodCalculator`, roping or `Pawn_RopeTracker`. Fences are
honoured only *indirectly*: the region grid and the path customizer are keyed on
`pawn.ShouldAvoidFences` (`map.pathing.FenceBlocked` vs `.Normal`), and the
reachability walk checks `GridsUtility.GetFence`. So a 3×3 animal will *path*
respecting fences, but pen enclosure/escape logic is vanilla and single-cell —
**predicted defect: a titan can be assigned to a pen whose gate its square cannot
physically pass.** Not observed; flagged as the first thing to test if we ride.

**b. Caravans: no handling at all.** No `CaravanFormingUtility`, no gathering-spot
or exit-cell patches. Caravan forming is vanilla and unaware of footprints.

**c. Saving/loading: nothing is scribed into the save.** The only `ExposeData` in
the assembly are `Settings`, `SizeOverride` and `SpriteOffset` — i.e. ModSettings
only. There is no `GameComponent`, no `WorldComponent`, no `Scribe_Deep`/
`Scribe_References`. `LargePawnsMapComponent` holds only caches and debug state and
overrides no `ExposeData`. **Uninstalling is clean and there is no save-migration
risk** — a strong point in favour of riding.

**d. Swallowed exceptions: only two `catch` blocks in 9,378 lines**, both around
reflection resolution (Giddy-Up type/field lookup), and both null the refs rather
than hide a failure. **Zero `TODO`/`FIXME`/`HACK`/`XXX`.** No `Log.Error`,
`Log.Warning` or `ErrorOnce` anywhere — the only logging is two
`Log.Message` lines in `EnsureDefTables`. So: the code is *not* littered with
swallowed failures, but it is also **silent by construction** — when a size or a
region is wrong there is nothing in the log to tell you.

**e. Reentrancy guards** on `GenGrid.WalkableBy` (`reentrancyGuard` +
`[ThreadStatic] InWalkableByPatchContext`) — a signal that the whole-square
walkability prefix is recursive-by-nature and was made safe by hand.

---

## 5. Perf shape — event-driven, with one genuine per-tick scan

**Event-driven (good):** `LargePawnRegionRegistry.EnsureSubscribed()` hooks
`map.events.BuildingSpawned`, `BuildingDespawned` and `TerrainChanged`; a building
change dirties its `OccupiedRect.ExpandedBy(1)`. Rebuilds are **deferred** to
`MapComponentTick` (`if (regionRegistry.HasAnyPendingRebuild) RebuildAllPending()`).

**Per-tick (the cost):** `MapComponentTick` calls `UpdateLargePawnsCache()`
**unconditionally every tick**, iterating `map.mapPawns.AllPawnsSpawned` and
calling `GetSize` on each — which does a dictionary lookup keyed on `defName`
(string) per pawn, per tick. O(all spawned pawns) every tick, on every map.

**Rebuild cost:** each dirty pass re-runs a flood fill over an
`LargePawnRegion[NumGridCells]` array per grid; `RebuildAll()` marks **every cell
on the map** dirty. With up to 8 grids per map (4 sizes × fenced/unfenced) a
wall being built can trigger several partial rebuilds in one tick. `Rebuild()`
has a `working` re-entrancy flag.

**Caches:** two static reach/LOS caches capped at 512 entries with a **60-tick
TTL**, pruned by full enumeration when over cap; a per-grid `reachCache` capped at
4096 that is **cleared wholesale** when exceeded (thrash risk on a busy map).
`Building_Trap.Tick` gets a Postfix on **every trap, every tick**, but it only
reads `GetThingList` at the trap's own cell — cheap.

Net: the architecture matches our own perf rail (event-driven, no per-tick map
scans) **except** for the per-tick all-pawns size scan, which is the one thing to
measure before shipping on a 590-mod list.

---

## 6. License / redistribution

**There is no license statement anywhere.** `About/` contains only `About.xml`,
`Preview.png`, `PublishedFileId.txt`; no LICENSE, no README, no `.txt` of any
kind in the mod tree; `About.xml` has no license, url or permissions field. The
description says nothing about reuse. Steam Workshop's default is
all-rights-reserved to the author (Neku).

⇒ **Copying the assembly's code into `RM_TitanicCreatures` is not licensed.**
"Absorb" may only mean *independent reimplementation of the approach* (the ideas
here are also the obvious ones — whole-square walkability, ThingGrid registration
across the rect, a per-size region graph), never lifting the decompiled source.
Riding the mod as a dependency raises no licensing question at all.

---

## 7. Verdict — **ride-with-config**

**The one strongest reason:** the mod already implements the exact configuration
surface our card #2 demands — *tiers auto-attach by bodySize with a curated
per-def override in both directions* — as three public tunable floats
(`size2Min/3Min/4Min`) plus a per-def `sizeOverrides` table where `1` forces
opt-out and `2–4` force opt-in, consulted **before** bodySize. Reimplementing that
means reimplementing 68 patches into `PathFinder`, `Reachability`, the region
graph, `CoverUtility`, `ShootLeanUtility` and `ThingGrid` — months of work against
engine internals, for a capability we would end up with byte-for-byte the same
semantics of. Nothing in the code argues for a fork: no swallowed failures, no
save-state entanglement, no dead-end architecture.

### Integration surface our mod would use

1. **Footprint read — use vanilla, not their API.** `GenAdj.OccupiedRect(Thing)`
   is Prefix-patched to return the multi-cell square for any large pawn. So our
   destruction-wake comp iterates `pawn.OccupiedRect()` and gets the true
   footprint **with zero reference to LargePawns**, degrading correctly to 1×1 if
   the mod is absent. This is the integration point — it costs us no dependency.
2. **Size ladder reconciliation (the ⛔ "no two ladders" rail) — write their
   settings, don't fight them.** `LargePawns.Main.settings` is a `public static`
   field and `Settings.size2Min/3Min/4Min`, `GetSizeOverride`, `sizeOverrides` and
   `NotifyEdited()` are all public. At startup (soft, reflection-only, `MayRequire`-
   style so we never hard-depend) we set the three floats to our T1/T2/T3
   boundaries and push one `SizeOverride` row per def on our curated override list,
   then `NotifyEdited()`. Our tier table stays the single authority; their ladder
   becomes a projection of it. ⚠️ Race: do this **after** their `EnsureDefTables()`
   has populated the rows, and re-`Write()`.
3. **Direct utility calls if ever needed:** `LargePawnUtility.GetSize(Pawn)`,
   `.IsLarge`, `.OccupiedSquare(Pawn, IntVec3)`, `.GetEffectiveSize` are all
   `public static` on a `public static class` — reflection-reachable. Prefer (1).

### What riding does NOT give us, and stays ours to build
- **4×4 is the ceiling** — bs 20 ElderSando, bs 32 Reefback and bs 40 Lanternwhale
  all land on the same 4×4. If T3 must be visibly bigger than T2, that is our
  patch, not theirs.
- **Everything in card #1 except the footprint**: thin-roof destruction, thick-roof
  aversion, the curated crush table, footfall, corpse-as-site, yield curves,
  spacing caps. None of it exists here.
- ⚠️ **Their path-clearing partly overlaps our destruction wake and must be
  reconciled, not stacked.** `PathClearingUtility.TryGiveWallClearingJob` makes a
  large pawn in manhunter / berserk / `JobGiver_AIFightEnemy` take a
  `DigUtility.PassBlockerJob` (melee, `ignoreDesignations`) against the first
  building blocking its path. That is a *job-driven* wall-break, not a
  crush-on-transit; ours is the latter. Decide one owner. The three settings
  bools (`pathClearingManhunter/Berserk/AIFight`) let us switch theirs off
  wholesale, which is probably the right call.
- **Pens and caravans are unhandled** (§4a, §4b) — if our titans are ever penned
  or caravanned, that work is ours regardless.

### Live-verification still owed (nothing here proves runtime behaviour)
Per the item's ⚠️: this is a static read of the IL on disk. It does not prove the
mod works on our 590-mod list. The quicktest from the item stands unchanged — spawn
a bs 12 creature, prove multi-cell occupancy with a getter, prove a 1-tile gap
blocks. Add two checks this decompile earned:
- **the settings file** — confirm `Mod_neku.largepawns_LargePawns.xml` exists and
  holds thousands of `sizeOverrides` rows (proves `EnsureDefTables` ran on our list);
- **a 2-wide door** — the PAWN-048 scaffolding says portal-region connectivity for a
  2×2 pawn through a 2-wide door was still being debugged at 0.24.16.
