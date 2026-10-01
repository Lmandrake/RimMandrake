# FOUNDRY worker progress 2026-10-01 (live round 2 defects)

## MUURROK_BEAM_NO_DAMAGE_1
Mechanism (RimSage, decompiled 1.6): Verb.TryStartCastOn only sets Stance_Warmup; Pawn_JobTracker.EndCurrentJob->CleanupCurrentJob(cancelBusyStancesSoft) and StartJob(cancelBusyStances) cancel it on ANY job end/start, so WarmupComplete never runs: no shot, no exception. Hunt() also restarted the strike job 30 ticks into the 90-tick warmup. Geometry ruled out (sim: ~2/3 of bursts hit the target cell). Fix: verb casts via UseVerbOnThingStatic job; Hunt waits while cast job/burst runs. Built.

## SOORRAK_INSTANT_JOB_LOOP_1
pending

## RIMPLACE_STUFFLESS_THING_ROWS_1
pending
