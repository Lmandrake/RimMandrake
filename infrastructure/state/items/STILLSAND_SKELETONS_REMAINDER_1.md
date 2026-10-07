# STILLSAND_SKELETONS_REMAINDER_1 — what STILLSAND_SKELETONS_TRACKS_1 left open

Parent: `STILLSAND_SKELETONS_TRACKS_1` (closed at `3843ba1f4`). That commit built the skeleton
buildings (RM: oommok, muurrok, guzzka, vozzik; RSW in SWBestiary: krayt, greater krayt,
war wyrm), the skull shade pocket `RM_GiantSkull`, the bone harp, the 0–2-per-map genstep, the
corpse-to-skeleton scan, the krayt graveyard upgrade + `RM_Stillsand` whitelist, the horizon
dust warning, and their Mod Settings ("Stillsand: skeletons and horizon"). Code:
`src/RimMandrake/Stillsand/Source/RM_GiantSkeletons.cs`, `RM_HorizonWarning.cs`,
`RM_SkeletonSettings.cs`.

## spec

1. **Tracks (parent §7)** — DONE. Sand + RM_DeepSand carry `RM_TrackSurfaceExtension` for RM_Stillsand
   (`Patches/RM_TrackSurface_Stillsand.xml`), the dunes eraser is `Source/RM_DuneTrackEraser.cs`, and
   the wake (`RM_SandWake`) and oommok print (`RM_OommokPrint`) sprites are wired
   (`STILLSAND_SKELETON_ART_TRACKS_WIRING_1`, 2655f315f). The sandcrawler tread art has no walking race.
2. **Dune burial (parent §4)** — BUILT offline 2026-10-07, never loaded. `Building_GiantSkeleton` samples
   `Map.sandGrid` (which the dunes engine writes) under its footprint every 2500 ticks; the bury/strip
   hysteresis (bury at mean 0.6, strip at 0.3, PROVISIONAL) is `Source/RM_SkeletonBurialLogic.cs`. Buried:
   drawn sand-tinted, bone harp silent, inspect line, a message on each change; scribed. Toggle
   `duneBurialEnabled`. L0: `Utils/selftest_skeleton_burial.py` (C#, 28 checks, mutation-tested).
3. **Art** — DONE: the seven skeleton sprites are wired (2655f315f) and `RM_GiantSkull` has its own sprite
   (requeued job landed, wired).
4. **Giant bone** — add the one bone material to each skeleton's `leavings`
   (`RM_GiantSkeletonExtension`) once `DESIGN_MATERIALS_REVIEW_1` names it.
5. **Ribs' rendered shadow** — DONE: `staticSunShadowHeight 0.5` on `RM_GiantSkeletonBase`. No shade-grid
   change was needed: `RM_MapComponent_ShadeGrid.CasterHeight` already skips any building carrying the
   shade-gear comp (since 2026-09-29), so the rendered shadow never turns into full cast shade.
6. **Wandering giants on the horizon** — BUILT offline 2026-10-07, never loaded. `RM_HorizonWarning.cs`
   now delays HerdMigration/ThrumboPasses workers too, and a one-shot `[ThreadStatic]` entry cell armed
   in an `IncidentWorker.TryExecute` prefix answers the worker's first `RCellFinder.TryFindRandomPawnEntryCell`,
   so they enter from the announced bearing (`PassersHonoured` counts it). Toggle `horizonPassersEnabled`.
8. **Live proof** (game-up, the parent's criteria): a Stillsand quicktest map carries 0–2
   skeletons; `RM_MapComponent_ShadeGrid.ShadeAt` reads 1 inside a skull; a dev-killed oommok
   becomes its skeleton (`RM_MapComponent_SkeletonRemains.Scan(ignoreDelay: true)` returns 1);
   a dev raid on a Stillsand map raises the "Dust on the horizon" letter and arrives from that
   bearing after the configured hours; a dev herd migration does the same and `PassersHonoured` rises;
   sand piled over a skeleton's footprint (`sandGrid.SetDepth` to 0.7, then `UpdateBurial()`) reads
   Buried and its harp stops, and clearing it strips it.
