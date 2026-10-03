# MessyConduit review 2026-10-03
## Core/CordBuilder.cs
In csproj (line 42), reachable (called by RM_MapComponent_CordGraph). Status DIRTY (never marked clean).
- CordBuilder.cs:131-137 cache key omits the endpoint stub's NodeType: Classify (CordGraph.cs:576-579) picks StubWall/StubRock/StubWater/StubDevice/StubHidden from World.BuriedKind(hid), but the key only has VId.T 's' + cells + positions. If the buried block kind changes under an unchanged conduit (wall->rock, wall->device) the cached piece keeps the old decal (StubWall vs StubRock vs PowerStrip) and LiveKeys. Fix: append nd.Type to the key (or LaySig). Low-medium.
- Cache key chain uses VId.ToString (CordGraph.cs:42), which for tangle/blob includes cluster index K = position in a sorted component list (CordGraph.cs:169-178). An unrelated new dense field earlier in sort order renumbers K and misses the cache for every edge touching a cluster: perf only, replan is bit-identical because ekey/seed use cell+pos. Low.
- No Seed in key (opt.Seed feeds CordRng); safe only if Seed is constant per map (check component section).
- Tick cost: Build re-runs Reduce over the whole map each call; PoseJunction (343-364) walks g.CordEdges() per junction => O(J*E) per build. Low unless huge networks.
- Null/bounds: EndDecor 460-466 uses nd.Machine unguarded (AttachEnd guards it); safe because machine nodes always get Machine in Classify. TanglePiece comp[r.Int(0,Count-1)] relies on non-empty cluster (guaranteed, comp>=4 or two). No Scribe state here.
- Otherwise: LaySig/CorridorHash design is sound (live flags L/D in key for Terminal/WallTerminal/StubDevice cover every isLive use in LayEdge/EndDecor).
Verdict: findings (1 low-medium cache-key omission); no crash bugs found.
## Core/CordGraph.cs
In csproj (line 39), reachable. Status DIRTY.
- CordGraph.cs:474-479 Deg(v) is O(E) and is called in PruneSpurs per candidate end (516, 519, 526) and in Classify per kept node (561); PruneSpurs restarts its foreach after each removal (553) => roughly O(E^2..E^3) on spur-heavy networks, O(N*E) in Reduce. Matters because Reduce reruns on every rebuild. Fix: maintain a degree dictionary. Perf, medium-low.
- 621 Away(): Edges.First throws InvalidOperationException if a Terminal-classified cell has Deg>0 but no edge; guarded by d==0 -> Isolated (598) so not reachable today.
- Determinism: HashSet<Cell> iteration (152-183) feeds adj insertion order, but adj lists are sorted (220) and Chains walk sorted keys, so output is stable.
- MergeStubs (259-338) correct: all dictionary reads (comp[a.B], adj[s]) are keyed on live data; dropped stubs fully unlinked.
- No Scribe/Verse state. Verdict: CLEAN-CANDIDATE for correctness; perf finding only.
## RM_MapComponent_CordGraph.cs
In csproj (line 55), reachable (MapComponent auto-instantiated; Harmony patches class-attributed). Status DIRTY.
- RM_MapComponent_CordGraph.cs:544-553 + 504-510 PER-FRAME FULL REBUILD: Section.TryUpdate prefix sets StaleOffscreen whenever ANY off-screen section carries Buildings/PowerGrid/Terrain/FogOfWar/RM_MessyCords dirty flags; vanilla leaves those flags set until the section is viewed, and nothing here clears them, so MapComponentUpdate runs Rebuild() (CordWorldAdapter.Snapshot + CordGraph.Reduce + Sig() GeometryHash over all pieces twice) EVERY frame until the camera visits that section. FogOfWar/Terrain flags off-screen make this common. Fix: throttle (e.g. at most once per N ticks) or only set StaleOffscreen on a flag-transition; and cache GeometryHash on LaidPiece.
- 177-180 Sig() recomputes GeometryHash + string.Join for every piece of every touched section on every Rebuild (also for reused cached pieces); cache the hash in LaidPiece.
- 350 `new[] { true, false }` allocates per strand per frame in DrawMotion; the whip/sway loops also walk all pieces once per strand variant (nv up to 8) per frame. Perf, low-medium.
- 32/447/282 liveEnds, thrownOf, downed are never pruned when ends disappear (slow leak, low).
- ComputeNetSeeds (74-108) unions only visible-cord pieces by EndA/EndB; two sides of a buried run (hidden edges are not pieces) get different net seeds, so "one colour per net" breaks across walls. Cosmetic, low. Machine nodes use hookup[0] cell so a multi-hookup machine does not join its nets.
- Save safety OK: component skipped on Saving and restored in Finalizer (also on exception); nothing Scribed; FillComponents' fresh instance is dropped. No NRE paths found (comp null-checked at section layer; DrawHighlight sets hiMesh via Fresh before use). DripState has 4 values = DownedHist length 4, OK.
Verdict: findings (per-frame rebuild, medium).
## SectionLayer_RM_MessyCords.cs
In csproj (line 56); reachable by engine (SectionLayer subclasses auto-instantiated per Section). Status DIRTY.
- SectionLayer_RM_MessyCords.cs:31-33 relevantChangeTypes has no Roofs flag, but Regenerate bakes RM_MapComponent_CordGraph.SwaysNow(Map, s) (98), which reads map.roofGrid.Roofed. A roof added later over a lifted wall tail: static mesh printed it (no longer sways since roofed? no: now roofed => SwaysNow false, component stops drawing it, yet the static mesh omitted it at the earlier regenerate) so the tail vanishes until some other flag regenerates; roof removed => tail drawn both printed-never and swaying is fine, but toggling Prefs.PlantWindSway likewise leaves it stale. Fix: add MapMeshFlagDefOf.Roofs to relevantChangeTypes (and to the Patch mask) or have the component draw non-swaying lifted strands too.
- 59-65 DrawLayer loops all submeshes per section per frame (IsLod material lookup); header claims zero per-frame cost. Trivial.
- Mesh cap handling (176, 206) drops instead of corrupting, safe. Null guards fine (comp?.). No Scribe state.
Verdict: 1 low-medium finding (Roofs flag).
## Hose files (all six in csproj lines 77-82; reachable: HoseMath/Settings/Reel/Flow/Component/Probe reference each other, Reel is the def's compClass)
Status DIRTY for all six (never marked clean).
### Hose/RM_MapComponent_Hoses.cs  (findings)
- RM_MapComponent_Hoses.cs:100-115 EnsureLay: the cache guard is `r.lay != null && r.layKey == key`, but a FAILED lay sets r.lay = null while storing layKey, so the guard never hits and an unroutable hose re-runs World() (full-map snapshot) + HoseMath.Lay (Stiffen 3x1500 iters, EaseOffObstacles) EVERY FRAME from DrawAll (Relays++ each frame). Fix: guard on layKey == key alone (return r.lay, null for failed) and let the 250-tick corridor check clear layKey. Medium-high perf.
- 47-72 World() snapshots the whole map (w*h, plus every plant) and is cached per TicksGame only; MapComponentTick (162) calls it per reel every 250 ticks at a per-reel phase, so N reels = N full snapshots per 250 ticks. Also while paused the cached snapshot goes stale for CheckInstall. Fix: dirty-flag or window the snapshot to the lay corridor. Low-medium.
- 113 + 40-42: meshes.Remove(r) in EnsureLay and Deregister drop the cached Mesh objects without Object.Destroy (DestroyMeshes exists but is not called): Unity Mesh leak on every re-lay / reel despawn. Low-medium.
- 103 string concat + ShapeFingerprint() (3 float ToStrings) per reel per frame; Shape()/Tuning() allocate per call (DrawEnds calls Shape() per coupling per frame). GC churn, low.
- Save safety OK (component skipped in Saving, restored in Finalizer incl. exception; fresh FillComponents instance dropped).
### Hose/CompHoseReel.cs  (CLEAN-CANDIDATE)
- Scribe fields all have defaults, sm fields saved by ref (class fields, fine), lay/layKey runtime-only and rebuilt lazily; PostSpawnSetup/PostDeSpawn pair registers/deregisters. Nothing found. (Observation, not a bug: PostDeSpawn clears laid, so any despawn, e.g. a gravship move, reels the hose in.)
### Hose/HoseFlow.cs  (CLEAN-CANDIDATE)
- HoseFlow.cs:54-76 FlowWorksPumpFlow.Flowing runs EVERY tick per laid reel: CellsAdjacent8Way iterator + GetThingList + per-thing/per-comp reflection-cache lookups while useFlowWorksPumps is on (default) and no pump exists. Throttle to the pulse interval if profiling shows it. Perf only.
### Hose/HoseMath.cs  (CLEAN-CANDIDATE)
- Pure functions; ResampleN/Couplings indexes safe (n>=8, Count>=2). Cosmetic: HoseStateMachine.ResetFlat (95-100) leaves Since/Transitions, so a reel re-laid within WobbleTicks (T+60) of its last transition draws the fill wobble on a Flat hose (Info(), RM_MapComponent_Hoses.cs:191). Low.
### Hose/HoseSettings.cs  (CLEAN-CANDIDATE)
- Scribe defaults match field defaults; ShapeFingerprint covers every Shape() input (plumpAmount, bend, slack, spacing), so the mesh cache key is complete.
### Hose/HoseProbe.cs  (CLEAN-CANDIDATE)
- Test channel; exceptions caught in Service; Census calls EnsureLay (inherits the per-frame relay only via DrawAll, not here).
