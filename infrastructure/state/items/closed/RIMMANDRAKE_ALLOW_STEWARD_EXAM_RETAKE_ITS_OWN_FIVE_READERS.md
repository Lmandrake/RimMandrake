# RIMMANDRAKE_ALLOW_STEWARD_EXAM_RETAKE_ITS_OWN_FIVE_READERS

Caused by RIMMANDRAKE_RETAKE_CONTAGION_EXAM_FAILING_ITS_GATE (2026-11-16).

## spec

The Maturation Pipeline launches a detached steward (`rm-detached-bench-rimmandrake-retake-<mod>-exam-…`) to retake a
failing Cold Reader exam: five fresh agents (Examiner, Challenger, two Readers, Control) by `roles/designer_exam.md`.
`block_agent_over_slots.py` gave the Designer role run its own allowance (`slot_rules.json` `role_runs`,
RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS) but not the steward's retake, which was counted
against the shared CONDUCTOR budget. Measured 2026-11-16 09:12 PST: Contagion's retake had its Challenger and its control
Reader refused ("CONDUCTOR already has 3 helper(s) running … N=3"); with the owner out of the window CONDUCTOR goes to
N=0 and the retake could never run. Fix: `role_runs` gains `"rm-detached-bench-rimmandrake-retake-": 5`.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_exam_slots.py` exits 0 (19 PASS). Watched failing
before the rules change: the check "a steward's exam retake asks for its control reader -> allowed under its own
allowance" FAILed (deny, CONDUCTOR N=3 text); any other detached run stays gated (N=0 -> deny).

## criteria

A retake steward's helpers are capped at 5 on its own session; other detached runs keep the Conductor budget; his
slot_override word still caps it.
