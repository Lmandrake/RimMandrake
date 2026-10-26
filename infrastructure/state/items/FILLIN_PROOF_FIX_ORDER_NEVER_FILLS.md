## spec
found-by: BENCH helper triaging FILL_IN_DESIGNATION_FIX_SCAN_INVALIDATED, 2026-10-26.

toggle_fill_in/fill_in_on FAILs and toggle_fill_in_displacement/fill_in_displacement_on reads UNMEASURED ("the fill-in never happened") on
SteveDesktop (J20261026T080819Z-17015d, J20261026T081140Z-d4950f, source_sha 9491fc29b7). That source already has the
"Collection was modified" fix (e46b187dc2), and the run record has no such exception, so this is a separate defect.

Evidence (runner ~/rm/runner/Transient/modcheck/FlowWorks_20261026T081114Z.json, fill_in_on evidence[3..87]):
- flowworks_job_probe at (129,131), forced: designationPresent, shouldSkip False, hasJobOnCell True, jobDef RM_FillInCanalJob.
  pawn.priority 0 / workActive False (Mining is not enabled for the spawned colonist, so it never takes the work on its own).
- jawa/ordered_job RM_FillInCanalJob targetA only: accepted, then curJob Skygaze with 0 ticks elapsed (game paused).
- depth reads 7 (not 1) at every one of 38 reads over 20,000 ticks.

Probable cause (HARNESS, unconfirmed): northstar/extensions.py _order_fill_in (~1183-1206) orders a bare job with targetA only. That skips
WorkGiver_FillInCanal.JobOnCell, which since DIG_SPOIL (e46b187dc2) attaches the fill material as targetB on an unpaid pit
(fillCostsSpoilEnabled defaults true). In JobDriver_FillInCanal.cs:67-77 the RM_FillPaidCheck toil then ends Incompletable at once
on an unpaid pit with no targetB. The other candidate is the FailOn(!RM_Shovels.Ready) at :66. Also, the precondition is wrong: the
chain digs with deepenLevels=1, yet the report reads D=7, so one fill could never reach D=0 within FILL_IN_TICKS_MAX.
Fix direction: ask the bridge to issue the job via the WorkGiver's JobOnCell (or pay the pit/stage material first), and
re-derive the dug depth before budgeting.
