# Review batch 9 — 2026-10-06 (offline, full-file)

No edits, no rebuilds. Engine facts checked against decompiled 1.6 via RimSage where stated.

## RM_LongShadeMiddens.cs — CLEAN (marked)
- Job giver: gated on toggles, map/dead/downed/awake, hostiles, hunger, rest. Returns null when the heap is on cooldown or full, so the vrekka cannot loop. Heap list is fetched again before the spawn, so nothing is changed while it is being iterated.
- Cell choice: in bounds, standable, not fogged, outside Home, unroofed, no edifice or item, shade at least minBuildShade, spacing respected, reachable. Heap is PassThroughOnly, so it cannot trap a pawn.
- Tend driver reserves nothing (by design). The final toil re-checks Spawned and CanTendNow, so two vrekka cannot tend the same heap twice. Props falls back to a default after a load.
- Search: the yields table is all non-stuff vanilla defs, so MakeThing with null stuff is safe. Stacks are split by stackLimit.
- Save/load: all four comp fields are saved. No tick method is needed (no timer, by design).

## RM_ForgeSpunstoneParts.cs — CLEAN (marked)
- RimSage: DesignationCategoryDef.ResolveReferences queues ResolveDesignators through ExecuteWhenFinished, and that only adds defs whose designationCategory == this. Nulling the category plus RemoveAll covers both orders.
- Neither DoorBase nor Wall carries designatorDropdown, so the `is Designator_Build` match is complete. Settings load in the Mod ctor (GetSettings), which runs before StaticConstructorOnStartup.

## RM_ForgeSpunstone.cs — CLEAN (marked)
- The legacy keys are read only in LoadingVars and folded in through Shared.Import at LoadedGame, when GameComponents exist. Nothing is written back afterwards, so the import happens once. The Flora XML sets `<project>`, and the gate key is registered in RM_TheForgeMod.ExposeData.

## RM_FoundTechStudy.cs — already CLEAN (96f8113e9, today), unchanged; its API was read to check the Spunstone callers.

## RM_TreeFallUtility.cs — CLEAN (marked, #3)
- The FellingNow try/finally is correct. The damage loop copies the thing list and skips destroyed things and the tree itself. Explosions from things killed in the swath are delayed by a tick, so the tree cannot be destroyed twice in one tick.

## RM_WarscarMod.cs — SKIPPED
- The real path is src/RimMandrake/Scarlands/Source/ (not Warscar-or-Scarlands). It has had no commits since 3cdd35bc0, so per the brief it was not reviewed.
