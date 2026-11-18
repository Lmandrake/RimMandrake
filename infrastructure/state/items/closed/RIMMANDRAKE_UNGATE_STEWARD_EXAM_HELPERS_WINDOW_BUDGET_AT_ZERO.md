# RIMMANDRAKE_UNGATE_STEWARD_EXAM_HELPERS_WINDOW_BUDGET_AT_ZERO

## spec
A detached maturation steward (AGENT_SEAT=BENCH, RM_ROLE_UNIT set) owes fresh agents for the Cold Reader exam
(Examiner, Challenger, two Readers, a control Reader: `roles/designer_exam.md`). `.claude/hooks/block_agent_over_slots.py`
maps it to the CONDUCTOR budget, and the Dispatcher budget of 2026-11-15T13:24:02-0800 read "CONDUCTOR 0 (session-only:
he is not in its window; last window message 33 min ago) ... RELENTLESS 10", so the steward of
RIMMANDRAKE_RETAKE_PYRELANDS_EXAM_AFTER_LOCKED_CHANGE (run bench-pyre-exam-st4-r7-20261115) was refused every spawn.
Its running count is also read from the Conductor window's project (`-home-mandrake-rm-bench`), not the run's own
subagents. The effect is that an unattended steward can only run its exam while he types in the Conductor window. That
conflicts with his 2026-10-30 ruling that his presence never gates a runner (CLAUDE.md §The bridge).

Which budget a detached role run's subagents draw on (RELENTLESS, the pipeline's? its own Dispatcher slot plus a fixed
small N?) is a slot-policy choice, so the steward did not make it: the Conductor decides, then a builder fixes it.

Acceptance test: none, the fix waits on the Conductor's slot-policy choice; once chosen, the test is a hook run with
AGENT_SEAT=BENCH, RM_ROLE_UNIT=<unit> and a budget of CONDUCTOR 0 that allows a spawn under the chosen rule.
