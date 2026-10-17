# FlowWorks review day log 2026-10-17 (FOUNDRY reviewer, scratch clone review)

base: 6fb91887a

## Files

(per-file entries appended below)
- RM_LevelPour.cs (94): read whole, reachable; nothing found -> CLEAN
- RM_LevelSolve.cs (514): read whole; solve conserves (children full before band laid, remainder < members); nothing found -> CLEAN
- RM_PondDepthMath.cs (253): CLEAN (keys bounded by MaxStorableDepth=250 byte grid)
- RM_BedMath.cs (410): CLEAN
- RM_LakeFloorMath.cs (686): CLEAN; note :501 WayOut can DEEPEN a shallow pillar (doc says passes only shallow), loop capped at 8 rounds -> not a bug
- RM_SwimMath.cs (232): CLEAN
- Swimming/RM_Swim.cs (1016): BUG fixed: Fingerprint() built a string on every IsSwimTerrain call (CanReach/path grid hot path), omitted swimPathCost (slider never re-read path grids until reload), and Reapply shared the tables fingerprint (an IsSwimTerrain call before Reapply hid the change). Now int table/applied fingerprints. SelfTest case Swim_reapply_fingerprint_no_alloc_and_cost. Note: lastWarn dict write-only (harmless).
- RM_RelativeRulesMath.cs (251): CLEAN
- RM_DigDepthMath.cs (111): CLEAN
- RM_ExcavationSanityMath.cs (180): CLEAN (dug depth cannot exceed 40: FirstCutDepth bounded by cap)
- RM_Volume.cs (290): CLEAN
- TakenByLand/RM_TakenByLandKernel.cs (121): CLEAN
- TakenByLand/RM_TakenByLand.cs (453): CLEAN (hold set before PassToWorld; rebuilt PostLoadInit; SafeReturn re-holds on throw)
- Sprinklers/RM_MapComponent_Sprinklers.cs (141): CLEAN
- RM_FlowKernel.cs (2158): diff-scoped review since clean mark 85e0fbeba (875 added lines: exact-level ResolveExact/ExactDomain/ExactSolveDomain, ReturnToPonds, TopUpWaterMouths, SeamSlot, 40-notch buckets): ledger closes to the dL, pacing products fit in long; nothing found -> CLEAN
- RM_PitFillEffects.cs (RM_Drowning, 234): read whole; DOUBT (not fixed): with swimming on, RM_Swim.Tick runs PerCheck on NATURAL shallow water (0.5 m): a downed person (lying head-under 0.35 m) drowns in ~1 h in any shallow river/lake edge, small animals (H 0.5) tire and drown in shallows. Owner-design question, left DIRTY.
- committed fix ed3b1b925 (rebased); running SelfTest
- SelfTest 542/542 on ed3b1b925; running vv_shipped_matrix
- vv_shipped_matrix: VERDICT FAIL only on AUTHORED Thirst_slime_last_resort_ruled = harness stage miss (ThirstChecks reads src/RimMandrake/Biomes.compose.json + other mods About/Defs, vv rsync stages FlowWorks only); not this change. All SHIPPED fuzz/rate rows 0 failures.
- rebuilding FlowWorks DLL
- DLL 10514dc26; 14 files marked CLEAN at 10514dc26. Left DIRTY: Swimming/RM_Swim.cs (fixed, design doubt above), RM_PitFillEffects.cs (same doubt); ~65 other files from today unreviewed (see report).
