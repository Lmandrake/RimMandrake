# P13 FISH_ROLL_MEND_PONDS_BORN_BARREN — build log

Scratch clone `/home/mandrake/rm/scratch/FOUNDRY/p13`, base 54fe4ef75. FOUNDRY offline builder, no bridge, no game.

## Stages
- [ ] 0 read docs + item
- [ ] 1 locate the three traps in game code
- [ ] 2 design
- [ ] 3 implement
- [ ] 4 tests
- [ ] 5 publish

## Log
- stage 0 started
- stage 0 done: item, plan, engine doc §2.3/§6 Q5-Q6 read.
- stage 1 done (RimSage, 1.6 source): WaterBodyTracker.Notify_TerrainChanged -> TryCreateBodyOrAddToExisting (new body Initialize()s
  at 1 cell: SetFishTypes rolls once, chance 0 under 75) / RemoveCellFromExistingBody (removes the zone cell first; body removed at 0
  cells; never splits). WaterBody.RecacheState re-rolls only if shouldHaveFish. FloodFillBody merges, never re-rolls.
  Plants: TerrainGrid.DoTerrainChangedEffects destroys a plant whose WildTerrainTags miss the new terrain (water plants have
  completelyIgnoreFertility, so only the tag path); Plant.DyingBecauseOfTerrainTags = slow death (0.005/tick).
  RM_WaterChestDeepStill already carries the shallow tags; WaterDeep and lakebeds do not; Mud keeps reeds only.
- stage 2 design: hook Notify_TerrainChanged (Playing only: ConstructBodies at mapgen untouched, no extra Rand at mapgen).
  Verse-free core RM_WaterBodyMath.cs (roll sizes, split components, plant verdict, fish memory book, orchestration over a
  view interface) shared by the game adapter and a SelfTest port of the vanilla tracker; python oracle mode "bodies".
- stage 3 (implement) built: Source/RM_WaterBodyMath.cs (Verse-free), Source/RM_WaterBodyMendGame.cs (settings, MapComponent
  RM_MapComponent_WaterMend, view, Notify_TerrainChanged prefix/postfix, DoTerrainChangedEffects transpiler on the one
  HashSet.Overlaps, Plant.DyingBecauseOfTerrainTags postfix); flip fix calls the split after Detach; settings wired. winbuild OK.
- stage 4 (tests) started: SelfTest port of the vanilla tracker + WaterBodyMendChecks; oracle mode "bodies".
- stage 4: SelfTest 551/551 (14 new Fish_/Body_/Plants_/WaterMend_ cases; each trap reproduced on the bare vanilla port first).
  Oracle mode "bodies" 3000/3000 PASS. Sanity probe (mends off in the oracle run): the vanilla port THREW "Sequence contains no
  matching element" in RemoveCellFromExistingBody: an unsplit body's piece swallowed by another body leaves a stale root; pinned
  as Body_split_stale_body_vanilla_throws_mended_clean (ported vanilla, not seen live).
- next: full oracle 3000 all modes, vv_shipped_matrix, run_selftests --only.
