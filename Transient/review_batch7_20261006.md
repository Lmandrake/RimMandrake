# Review batch 7 — Watchers C# (commit 0d480998d), 2026-10-06

Scope: every .cs in src/RimMandrake/Watchers/Source/. Offline only. Engine facts checked with RimSage
(decompiled 1.6): Pawn.DeSpawn calls jobs.StopAll (so finish actions clean up on death, caravan, map
exit and ship departure); JobDriver.ExposeData re-runs SetupToils at PostLoadInit (finish actions survive
save-load); ThingWithComps.Tick loops CompTick; Designator_Hunt.CanDesignateThing faction rule.
No Harmony in this assembly.

## Per-file verdicts
| file | verdict |
|---|---|
| RM_WatcherUtility.cs | FIXED (F1) — uncommitted, DIRTY until committed + re-marked |
| RM_JobGiver_Watch.cs | FIXED (F2) — uncommitted, DIRTY until committed + re-marked |
| RM_CompWatcher.cs | CLEAN (marked) |
| RM_Flush.cs | CLEAN (marked) |
| RM_JobDriver_Watch.cs | CLEAN (marked) |
| RM_JobGiver_WanderInMedium.cs | CLEAN (marked) |
| RM_WatcherExtension.cs | CLEAN (marked) |
| RM_WatcherSign.cs | CLEAN (marked) |
| RM_WatchersDefOf.cs | CLEAN (marked) |
| RM_WatchersMod.cs | CLEAN (marked) |

## Findings
- **F1 (RM_WatcherUtility.Flush):** flushing a TAMED (player-faction) watcher's sign put a Hunt
  designation on the colony's own animal, so hunters would kill the pet. Fixed by applying vanilla
  Designator_Hunt's rule: only mark when `watcher.Faction == null || !watcher.Faction.def.humanlikeFaction`.
- **F2 (RM_JobGiver_Watch):** a watcher below `emergeWhenFoodBelow` with no reachable food (GetFood above
  it fails) got the watch job, hid on any nearby pawn, emerged-and-ended on the next 30-tick step (hungry),
  and was re-issued the job: a hide/emerge loop every ~60 ticks with sign spawn/destroy and dust puffs.
  Fixed: the giver returns null below that threshold (consistent with "hungry: it comes up to feed").

Rebuilt: `winbuild.py Watchers` succeeded, 0 warnings. Nothing committed.
