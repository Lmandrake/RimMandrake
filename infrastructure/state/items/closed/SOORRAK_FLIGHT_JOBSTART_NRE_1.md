# SOORRAK_FLIGHT_JOBSTART_NRE_1 — RM_Soorrak throws on every job start (Pawn_FlightTracker.Notify_JobStarted)

Found 2026-10-01, FOUNDRY live session (RM_Stillsand quicktest, full list, deployed commit `cc4bc992243`).
One wild `RM_Soorrak` was spawned and left alone. Its flight state was only READ (`jawa/pawn_flight
action=report`), which gave canEverFly true, MaxFlightTime 30 and flightStartChanceOnJobStart 0.3. Over the
session it logged **59** `Exception ticking RM_Soorrak111919: System.NullReferenceException` at
`RimWorld.Pawn_FlightTracker.Notify_JobStarted`, called from `Pawn_JobTracker.StartJob`. The only prefix on
that method is `XylRacesCore.Patches.Patch_Pawn_FlightTracker:Notify_JobStarted_Prefix`. The log is at
`Transient/livesession_20261001/Player.session.log`.

Likely area (not confirmed): the soorrak's flying setup on its PawnKindDef (animation frames or draw size),
or the XylRacesCore prefix. Read the decompiled `Notify_JobStarted` before changing anything.

## criteria
- A spawned soorrak runs 5,000 ticks with no `Exception ticking RM_Soorrak` in `Player.log`. Check this by log
  and state read only. Watching it fly needs the owner present (CLAUDE.md flyer rule).
