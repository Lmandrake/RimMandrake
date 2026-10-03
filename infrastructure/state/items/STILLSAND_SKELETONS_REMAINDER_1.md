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
2. **Dune burial (parent §4)** — the dunes engine should bury a ribcage to its top arcs and later
   strip it. Needs a hook in `MapComponent_DuneField`; not started.
3. **Art** — the seven skeleton sprites are wired (2655f315f). `RM_GiantSkull` still renders vanilla
   `RubblePile`; its artpipe job `RM_GiantSkull` FAILED validation 2026-10-03 (`failed/RM_GiantSkull.json`): requeue, then wire.
4. **Giant bone** — add the one bone material to each skeleton's `leavings`
   (`RM_GiantSkeletonExtension`) once `DESIGN_MATERIALS_REVIEW_1` names it.
5. **Ribs' rendered shadow** — DONE: `staticSunShadowHeight 0.5` on `RM_GiantSkeletonBase`. No shade-grid
   change was needed: `RM_MapComponent_ShadeGrid.CasterHeight` already skips any building carrying the
   shade-gear comp (since 2026-09-29), so the rendered shadow never turns into full cast shade.
6. **Wandering giants on the horizon** — herd migrations and thrumbo-style passes choose their own
   cells and ignore `parms.spawnCenter`, so the horizon warning covers raids and neutral groups
   only. Giants need their own hook.
7. **Harp clip** — `RM_BoneHarp` uses vanilla `Amb_Wind_Altitude1_Loop` pitched down as a
   placeholder grain.
8. **Live proof** (game-up, the parent's criteria): a Stillsand quicktest map carries 0–2
   skeletons; `RM_MapComponent_ShadeGrid.ShadeAt` reads 1 inside a skull; a dev-killed oommok
   becomes its skeleton (`RM_MapComponent_SkeletonRemains.Scan(ignoreDelay: true)` returns 1);
   a dev raid on a Stillsand map raises the "Dust on the horizon" letter and arrives from that
   bearing after the configured hours.
