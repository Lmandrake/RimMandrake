# PIT_FALL_MEND_SAVED_MIDAIR

FlowWorks: save in the jump tick loses the fall (lastCell not scribed)

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C3-F1** CONFIRMED LOW — Save in the same tick as a jump/forced fall loses the fall damage. RM_SuperdeepTrapState.lastCell is derived, never scribed (Superdeep/RM_SuperdeepTrap.cs:451-454); TryJumpInto teleports and defers the descent to the next detector pass (:422-425). Pause, jump, save, reload: no descent.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
