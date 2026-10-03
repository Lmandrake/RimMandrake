# Review 4 - MessyConduit CordGraph + Hoses (content identical at 15a154dfe and HEAD)

## Fix verification
- MapMeshDirty prefix: engine (decompiled 1.6 MapDrawer) has MapMeshDirty(IntVec3, ulong, bool, bool); patch signature matches. The 2-arg overload forwards to the 4-arg, so the prefix fires exactly once per dirty event. MapMeshFlagDef has an implicit ulong operator, so the mask casts compile and are valid at runtime.
- No loop: the mask excludes RM_MessyCords, and Rebuild/Flip/DirtySection only dirty with that flag; the prefix only sets a bool. One rebuild per frame max (builtFrame guard).
- Whip: tip tested before GetRange alloc; start/end indices correct (Pts[cnt-1] / Pts[Count-cnt]).
- FlushFrameMeshes: called on the early exit and on exception; the normal path rotates frameMeshes -> oldFrame.
- Hose cache key includes ShapeFingerprint (incl. plumpAmount), so no stale cached meshes.

## Findings
None significant. Notes (non-blocking): prefix on-screen margin is view+3 but vanilla regenerates at view+1, so a dirty 2-3 cells outside view whose section misses view+1 skips the stale flag until the camera nears it; liveEnds never pruned; WholeMapChanged bypasses the prefix (load path regenerates anyway).

Both files: CLEAN-marked.
