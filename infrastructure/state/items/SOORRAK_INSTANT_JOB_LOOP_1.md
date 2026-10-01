# SOORRAK_INSTANT_JOB_LOOP_1 — a wild soorrak never moves; its job ends the moment it starts

Found by the FOUNDRY live session round 2 (`Transient/LIVE_SESSION_2_2026-10-01.md`), while proving
`SOORRAK_FLIGHT_JOBSTART_NRE_1` (the NRE itself is gone: 0 exceptions over 5,000+ ticks).

## What was seen (state reads only, `jawa/pawn_flight action=report kind=RM_Soorrak`; no flight was watched)
- 6 wild RM_Soorrak spawned on a 48 C RM_Stillsand quicktest. 4 left the map within 700 ticks (no corpse; consistent
  with `canLeaveMapFlying`, not verified as flight).
- The 2 that stayed read `curJobDef = Wait_MaintainPosture` at **every** sample (10 x 500 ticks, 25 x 4 ticks, 12 x 7 ticks)
  and did not move one cell in 5,000+ ticks. Oorriks and vekkas on the same map read `Wait` / `RM_ShadeDash` and moved.
- Both carried `Heatstroke` 0.037 and nothing else.
- Engine (`Pawn_JobTracker`, decompiled 1.6, ~l.461): `Wait_MaintainPosture` with count 1 is the filler started when a job
  ENDS `Succeeded` while the pather is idle. Reading it at every sample means the following job also ends at once, every
  cycle. Which JobDef that is cannot be read from outside (only the filler is ever current). This is the instantly-ending
  job `SOORRAK_FLIGHT_JOBSTART_NRE_1` suspected.

## Next
Find the job: a debug `[Tool]` or a temporary `Log.Message` in `RM_FlightJobStartGuard.Prefix_Notify_JobStarted` that
records `job.def` for RM_Soorrak, or read the soorrak's think tree / `RM_` job givers for one whose first toil succeeds
(e.g. a goto to its own cell, a shade or water search that returns the current cell).

## criteria
- A wild RM_Soorrak on a Stillsand quicktest shows a JobDef other than `Wait_MaintainPosture` and changes cell within
  2,500 ticks, without any flight being watched.
