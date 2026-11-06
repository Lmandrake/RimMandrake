## spec
Plan P2 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`, risks
1 and 2). The owed live proofs of the built climb work (`PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP`,
`PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS`, `PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS`, the ladder) and the two unproven
risks. Script: `src/RimMandrake/FlowWorks/northstar/climb_proof.py` (§8.6 of
`design/RimMandrake/relative_depth_climb_design_2026-10-12.md`). Minimal list where it can; full list for the raid.
**Gates shipping `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT`, not coding it.**

## verify
- L2: pocket grid: a pawn in a sheer 2 m pocket cannot walk out; one beside a 0.5 m step can (state read of the path).
- L2: cliff masks: no path goes down or up a step taller than the pawn's climb limit; a ramp and a lowered ladder let it.
- L2: per-request mask swap holds under 1.6's multithreaded pathfinding while masks rebuild (dig during queued path
  requests; no pawn ever crosses a sheer wall).
- L2: a raid against a base ringed by a sheer trench: record what raiders do (stall, mill, leave, breach). Whether that
  is a bug or a feature is `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` (his Q7), not this item.
- Result recorded with modcheck; `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` and `PIT_SUPERDEEP_COLLAPSE_1` get the
  result path as their live evidence.
