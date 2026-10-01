# OORRIK_PAWNGEN_NRE_1 — RM_Oorrik cannot be generated (NullReferenceException)

Found live 2026-10-01 (FOUNDRY live session, RM_Stillsand quicktest, full list, deployed commit `cc4bc992243`).
`jawa/spawn_pawn kindDef=RM_Oorrik` fails twice with `NullReferenceException`. Of the 21 Stillsand
`RM_` kinds, only this one fails; the other 20 spawned.

`Player.log`: `Error while generating pawn. Rethrowing.`, after a run of `Error while determining if
RM_Oorrik… should have Need …`. The first stack is `Pawn_HealthTracker.ShouldBeDead`, reached from
`LifeStageWorker.Notify_LifeStageStarted` through `Pawn_AgeTracker.RecalculateLifeStageIndex`. DeathRattle,
VEF and BigAndSmall postfixes are on that path. The def is `Stillsand/Defs/ThingDefs_Races/RM_SandBusters.xml`
(body `Rat`). The root cause is not identified.

## criteria
- `jawa/spawn_pawn RM_Oorrik` spawns on the full list with no exception in `Player.log`. The sand-buster
  eruption incident's spawner then works too.
