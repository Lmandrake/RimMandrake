# TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID — a vanished titanoslime stays in the cell grid

## what is wrong (MEASURED 2026-10-17, BENCH, 22-mod walk list + neku.largepawns + mandrake.rm.hugethings, quicktest map)

`Destroy(DestroyMode.Vanish)` on a living `RM_Titanoslime` (`jawa/pawn_force_incapacitate action=vanish`, which calls
exactly that) leaves something behind in the cells around where it stood:

- any later `jawa/spawn_pawn` in the 3x3 around it fails with an NRE in
  `Verse.PawnCollisionTweenerUtility.GetPawnsStandingAtOrAboutToStandAt` (a Muffalo too, not just slimes);
- `Root level exception in Update()` (draw: `DynamicDrawManager.ComputeCulledThings` -> `Pawn_DrawTracker.DrawPos` ->
  `PawnCollisionPosOffsetFor`) and `in OnGUI()` then throw every frame, and because the draw pass dies mid-way every later
  spawn/despawn logs "Cannot register drawable X while drawing is in progress" (1,200+ `AB_MycoticSpores` lines in one run).
  `Exception in BreadthFirstTraverse` from `ReachabilityWithinRegion.ThingFromRegionListerReachable` also appears: the
  destroyed pawn is still in region listers.

Repro matrix, 9 neighbour cells respawned with a Muffalo after the end action (2026-10-17):

| subject | end | respawn ok |
|---|---|---|
| titanoslime stage 1, no mass change | vanish | 1/9 |
| titanoslime stage 1 (mass re-set) | vanish | 0/9 |
| titanoslime stage 2 / 3 | vanish | 4/9, 4/9 |
| titanoslime stage 4 (mass 28) | vanish | 9/9 |
| titanoslime stage 1 / stage 4 | **kill** | 9/9, 9/9 |
| titanoslime stage 1, alive | none | 9/9 |
| Thrumbo, Elephant, Muffalo, RM_Gelatid | vanish | 9/9 each |

So it is titanoslime-specific and vanish-specific. No exception is logged at the destroy itself.

## suspects, unproven

The stage is locked AFTER spawn (`RM_CompEngulfer.PostSpawnSetup` -> `ApplyStage` -> `LockCurrentLifeStageIndex`), so
BodySize — and with it Large Pawns' footprint size and Huge Things' titan tier — changes while the pawn is spawned. If
something registers the pawn in cells by its size at spawn and deregisters by its size at despawn, the cells differ.
Why kill is clean and vanish is not is the first thing to explain.

## NEXT

Restart without `neku.largepawns` (then without `mandrake.rm.hugethings`) and rerun the matrix with
`Transient/afk_2026-10-17/titano_probe.py`'s `case()` harness; whichever removal makes vanish 9/9 owns the bug.
Player impact: vanilla rarely vanishes a live pawn, but any mod or dev action that does will poison the map.
`src/RimMandrake/GelatinousSlime/northstar/titanoslime_gates.py` kills slimes instead of vanishing them until this is fixed.
