# MessyConduit re-review 2026-10-03 (after fd826e8c1)

Prior findings: `Transient/review_messyconduit_20261003.md`. Full-file read of all four files.

## Core/CordBuilder.cs -- CLEAN
- FIXED: stub NodeType now in the cache key (CordBuilder.cs:134-135, `g.Nodes[v].Type` for both endpoints).
- Seed not in key: safe, `BuildOptions.Seed` is only ever the constant 1 (CordBuilder.cs:92; no other assignment in the mod).
- Remaining prior items are low perf only (VId cluster index K in key, PoseJunction O(J*E) at 352). No crash/correctness issue.

## SectionLayer_RM_MessyCords.cs -- CLEAN
- FIXED: `MapMeshFlagDefOf.Roofs` is now in relevantChangeTypes (line 32), so SwaysNow's roof read re-prints the section.
- Mesh cap, null guards (comp?.), whip range clamp all OK. Trivial: DrawLayer per-frame submesh loop (59-64) contradicts "zero cost per frame" header; Prefs.PlantWindSway toggled outside the mod's settings does not reprint (low).

## RM_MapComponent_CordGraph.cs -- FINDINGS, left DIRTY
- FIXED: per-frame rebuild. Patch (540-561) now only marks stale on NEWLY set mask bits per off-screen section (`seen`), cleared when flags reach 0 or the section is in view. Converges (one extra rebuild after DirtySection sets the RM_MessyCords bit; second build is all cache hits).
- NEW, medium-low (RM_MapComponent_CordGraph.cs:556-558): the bit-transition test drops later changes. An off-screen section already carrying the Buildings bit that gets a SECOND building/conduit change before it is viewed adds no new bit, so StaleOffscreen is never set and the pieces lag until the camera visits (the lane F bug, for the 2nd+ change). Fix: also compare a per-map change counter, or mark stale on any transition 0->dirty plus a throttle (e.g. at most one rebuild per 30 ticks while any seen entry exists).
- NEW, low (545): static `seen` keeps Section refs for off-screen dirty sections of maps that are later discarded (never cleared on map removal / new game). Clear it in the component's finalizer or key by map.
- STILL OPEN, low-medium perf (354 precedes the view test at 357): `GetRange` + `Reverse` allocate for every whipping strand on the whole map every frame, even off-screen, and the loop runs nv (<=8) times; line 350 `new[] {true,false}` allocs per strand. Test `view.Contains` on the tip before building the tail list.
- STILL OPEN, low: Sig() (177-180) recomputes GeometryHash for all pieces of touched sections (now rare, rebuilds are infrequent); liveEnds/thrownOf/downed never pruned; ComputeNetSeeds does not join nets across buried runs (cosmetic).
- Mesh lifetime: floorMeshes/faceMeshes/hiMesh created once per component and reused with Clear(); never destroyed on map removal (17 meshes max, low). Save safety OK (Prefix/Finalizer restore the component, also on exception).

## Hose/RM_MapComponent_Hoses.cs -- FINDINGS, left DIRTY
- FIXED: failed-lay re-lay every frame (104: guard is layKey alone; 162 clears layKey for lay==null every 250 ticks, so retry is rate-limited). Mesh leak fixed: DropMeshes/DestroyMeshes on re-lay, Deregister, replaced cache entry; transitioning meshes destroyed one frame later (236-238).
- STILL OPEN, low-medium (47-72, 162): World() is a full-map snapshot cached per TicksGame only; each laid reel triggers one every 250 ticks at its own phase, and while paused (TicksGame frozen) CheckInstall/EnsureLay reuse a stale snapshot. Fix: dirty-flag on edifice/terrain change or window to the lay corridor.
- NEW, low (170, 236-238): DrawAll's frameMeshes/oldFrame are only flushed when DrawAll runs to the end. On early return (hoses switched off, other map current) or a repeated exception, up to 3 meshes per transitioning hose linger undestroyed (bounded unless DrawAll throws every frame, where frameMeshes grows unbounded). Also meshes/oldFrame are not destroyed when the map is removed.
- STILL OPEN, low: per-frame string key concat (103) and Shape()/Tuning() allocs (205, 282).
