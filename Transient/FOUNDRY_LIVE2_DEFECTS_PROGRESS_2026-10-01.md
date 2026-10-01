# FOUNDRY worker progress 2026-10-01 (live round 2 defects)

## MUURROK_BEAM_NO_DAMAGE_1
DONE f591714e5 (closed).
Mechanism (RimSage, decompiled 1.6): Verb.TryStartCastOn only sets Stance_Warmup; Pawn_JobTracker.EndCurrentJob->CleanupCurrentJob(cancelBusyStancesSoft) and StartJob(cancelBusyStances) cancel it on ANY job end/start, so WarmupComplete never runs: no shot, no exception. Hunt() also restarted the strike job 30 ticks into the 90-tick warmup. Geometry ruled out (sim: ~2/3 of bursts hit the target cell). Fix: verb casts via UseVerbOnThingStatic job; Hunt waits while cast job/burst runs. Built.

## SOORRAK_INSTANT_JOB_LOOP_1
DIAGNOSTIC COMMITTED, NOT FIXED (item stays open): EndCurrentJob prefix logs `[RM CreatureBehaviors] instant job loop:` naming J. Ruled-out list in the item prose. Ruled out (decompiled 1.6): vanilla Wander (guards own-cell), LayEgg, GetRest/LayDown, Ingest, ExitMapFlying, AttackMelee; RM SunEscape/ShadeHop/Mill (no own-cell targets). 4/6 left via LeaveIfWrongSeason->DangerousTemperature (felt-temp patch)->ExitMapFlying. Now sweeping installed mods' Animal_PreMain/PreWander inserts.

## RIMPLACE_STUFFLESS_THING_ROWS_1
DONE: GenStep_RimplacePlan StuffFor() supplies GenStuff.DefaultStuffFor for '-' rows (THING and RUN). Bedroll errors came from SW templates' '-' rows (dead_caravan, crashed_ship, beast_lair, road_warehouse), not the junkers templates (those name Cloth).

## Selftests
78/81; failures are the two known (walklint Pyrelands BAD_PACKAGEID, sound_paths Wasteland clip). Follow-up live item: LIVE_ROUND2_FIXES_PROOF_1.
