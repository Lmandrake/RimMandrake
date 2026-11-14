# RIMMANDRAKE_RESUME_SWEPT_PAWN_STUCK_MID_RIVER

## spec

A pawn the FlowWorks river current shoves never walks again in its job. `RM_MapComponent_RiverCurrent.Move()` calls
`pather.StopDead()` + `Notify_Teleported(false)`: the pather stops with no path and the job is not ended, so a Goto
toil (completes only on PatherArrival) waits forever. The pawn rides the current to the next bend or edge and stands
frozen until drafted. Design §3.1 (`design/RimMandrake/river_works_mod_design_2026-10-03.md`) says a colonist told to
cross is *"dragged and re-path, repeatedly"* and an edge-lane pawn *"can still wade across or out"*. Found from code
while diagnosing `RIMMANDRAKE_FIND_RIVER_SWIM_BRUISES_FUEGO_HURT_FIVE_TIMES` (full write-up in that item, section
"Problem A"); live runs of 2026-11-12 match (Fuego ordered west went 58 cells south).

Likely fix: after the move, re-issue the pather toward the job's destination (or end the job so the pawn re-thinks);
check whether TerminalBiomes' sea shove (same idiom) has the same freeze.

Acceptance test: none offline (pather and job behaviour exist only in the running game; FlowWorks' selftest is
Verse-free). Live test, UNRUN: steps 3-4 of the run sheet in the parent item: after the first downstream shove an
undrafted Goto pawn must show `pather.Moving` true again within 60 ticks, and an edge-lane pawn must reach the bank.
