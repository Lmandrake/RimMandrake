## spec
The ROUTE is one `LordToil` moving one duty's FOCUS: worksite by day, barracks
from 22:00 to 06:00, and pinned to the pawn's own position while
`lord.lastPawnHarmTick` is recent.
⚠️ There is no `TileMutatorDef` naming `Inhabited_Cast` yet, so the cast will not
appear on a map by itself. Land on the place created by the debug action, or
spawn the pawns and lord by hand.

## verify
watch the clock roll past 22:00 and past 06:00.

## criteria
they work by day and are at the barracks at night; a save/load mid-day does not
scatter them or leave anyone standing still; being shot at pulls them off the
schedule and they do not walk home mid-firefight.
⚠️ **Report anything that reads as a crowd rather than as residents** — everyone
sleeping in one heap, or nobody sleeping at all. `JobGiver_SleepAtNight` prefers
a real bed via `RestUtility.FindBedFor` and only then a ground spot near the
duty focus, so a place with no beds will look like a camp. That may be correct.

## notes
**from:** BUILD, 2026-08-20, `f0a9f6c`. Depends on `ROSTER_SOAK_100_DAYS_1` passing.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
