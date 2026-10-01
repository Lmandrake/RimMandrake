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

## Source read 2026-10-01 (FOUNDRY, offline; no live run)
Read against decompiled 1.6 (RimSage) and our source. None of these gives a job that runs out of toils inside
`StartJob` for a standing wild animal, so none is J:
- vanilla `JobGiver_Wander` (an own-cell dest returns `Wait_Wander`, which would be visible), `JobGiver_LayEgg`
  (`Wait(500)`), `JobGiver_GetRest`/`JobDriver_LayDown`, `JobGiver_GetFood`, `JobGiver_ReactToCloseMeleeThreat`,
  `JobGiver_ExitMap*` (walking exit is `Goto`, which never gets the filler);
- ours: `RM_JobGiver_SunEscape` / `RM_JobGiver_ShadeHop` (`RM_ShadeDash` B is always another patch or a lure's side,
  never the pawn's cell; mill excludes the pawn's cell; rest is a timed `Wait`), every other `Animal_PreMain` /
  `Animal_PreWander` giver in `src/` (each is gated on an extension or comp the soorrak lacks, or on another biome).
- Installed mods' XML inserts at those tags (VFE Settlers chemshine, Alpha Animals exploding eggs, Biomes! unbeach,
  Vanilla Genetics hybrids, cleaner): gated on their own races. C#-only Harmony patches from other mods were not read.
- Why 4 of 6 left: `LeaveIfWrongSeason` -> `ThinkNode_ConditionalDangerousTemperature` reads `AmbientTemperature`,
  which our sun-heat postfix raises in open sun -> `JobGiver_ExitMapRandom` -> `ExitMapFlying` (unroofed + `CanEverFly`).
  Expected for the def's drinking trip.

So J is named in the log instead of guessed: `RM_FlightJobStartGuard.Prefix_EndCurrentJob` warns once per
(race, job, giver) after 20 same-tick Succeeded ends in a row on a standing animal. Deciding string, on a Stillsand
quicktest with wild RM_Soorrak: `[RM CreatureBehaviors] instant job loop: RM_Soorrak` (the line names the JobDef,
the giver class, the think tree and both targets). The fix follows from that line.
