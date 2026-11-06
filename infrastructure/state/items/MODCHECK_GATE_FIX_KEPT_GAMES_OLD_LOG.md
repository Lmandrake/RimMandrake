## spec
`src/RimMandrake/Utils/modcheck/runner.py` `run()` calls `ensure_playing_map()` before `verify_loaded_list()`. The launch gate in `ensure_playing_map` reads the Player.log of whatever game is kept. A game left at the menu by a refused job therefore refuses every later job, even one whose composed list differs and would otherwise go `stale_load` and be restarted onto its own list by the worker (MODCHECK_STALE_KEEP_COMPOSED).
Seen 2026-11-06: J20261106T093115Z-46384f, J20261106T093117Z-97f464 (FlowWorks) and J20261106T094008Z-be8939 (Scarlands), load 2 s each, inherited Pyrelands' refusal; the filler braked and the lane went dark (STEVE_LANE_UNSTICK_BRAKED_UNOWNED_D283).
The bad load's own cause was fixed in 73760d1e3d. This item is the blame landing on the wrong job.

## verify
A selftest with a fake client: game at the menu, a log with a missing own type, running list different from the composed list. The run must end stale_load (restart onto the composed list), not `launch gate REFUSES`. Same scenario with the running list EQUAL to the composed list must still refuse.

## criteria
- a job whose composed list is not the running load never reports the running load's missing types as its own HARNESS fault;
- the launch gate still refuses a map on a load that is this job's own list.
