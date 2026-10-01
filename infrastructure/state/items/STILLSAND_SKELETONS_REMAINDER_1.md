# STILLSAND_SKELETONS_REMAINDER_1 — what STILLSAND_SKELETONS_TRACKS_1 left open

Parent: `STILLSAND_SKELETONS_TRACKS_1` (closed at `3843ba1f4`). That commit built the skeleton
buildings (RM: oommok, muurrok, guzzka, vozzik; RSW in SWBestiary: krayt, greater krayt,
war wyrm), the skull shade pocket `RM_GiantSkull`, the bone harp, the 0–2-per-map genstep, the
corpse-to-skeleton scan, the krayt graveyard upgrade + `RM_Stillsand` whitelist, the horizon
dust warning, and their Mod Settings ("Stillsand: skeletons and horizon"). Code:
`src/RimMandrake/Stillsand/Source/RM_GiantSkeletons.cs`, `RM_HorizonWarning.cs`,
`RM_SkeletonSettings.cs`.

## spec

1. **Tracks (parent §7)** — blocked on `FOOTPRINT_TRACK_GRID_1` (proposed, unbuilt when the
   parent closed). Once the grid ships: give the Stillsand sand `RM_TrackSurfaceExtension`, make
   the queued `RM_Filth_OommokPrint`, `RSW_Filth_CrawlerTread` and `RM_Filth_SandWake` the grid's
   per-race print sprites, and add the dunes-engine eraser (a cell whose sand depth changes past a
   threshold calls `ClearCell` and clears its scar filth; hook in the deposit step, shared with the
   gale). Track persistence toggle lives on the grid's settings.
2. **Dune burial (parent §4)** — the dunes engine should bury a ribcage to its top arcs and later
   strip it. Needs a hook in `MapComponent_DuneField`; not started.
3. **Art** — all seven skeleton defs and `RM_GiantSkull` render vanilla `RubblePile` as a
   placeholder. Wire the pending artpipe jobs (`RM_OommokSkeleton`, `RM_MuurrokSkeleton`,
   `RM_GuzzkaSkeleton`, `RM_VozzikSkeleton`, `RSW_KraytSkeleton`, `RSW_GreaterKraytSkeleton`,
   `RSW_WarWyrmSkeleton`) when they land. No skull art job exists yet: check artpipe first, then
   queue one for `RM_GiantSkull`.
4. **Giant bone** — add the one bone material to each skeleton's `leavings`
   (`RM_GiantSkeletonExtension`) once `DESIGN_MATERIALS_REVIEW_1` names it.
5. **Ribs' rendered shadow** — the ribs carry no `staticSunShadowHeight` because
   `RM_MapComponent_ShadeGrid.CasterHeight` turns any static shadow into full cast shade, which
   would erase the 0.5 lee stripe. A per-def cast-depth cap in the shade grid would let the ribs
   draw a shadow and still shade at 0.5.
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
