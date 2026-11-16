## spec
The Contagion-touched progression promises one transition message at active change, but `RM_ContagionTouched.cs` sends
only the "Contagion mutation:" letter (line 242) and the arrest message (line 262) (grep, 2026-11-16). Build one message
sent when severity first crosses the active-change threshold, never again on a dip and re-rise. Owed by Contagion
coverage gap g6 (`rm-coverage-judge-1794821839`); the record's inventory row is `touched_transition_message`, and
`sc_touched_reads_early` asserts this build in its start.

## verify
The acceptance test below passes on the deployed DLL, and the scene's live arm is recorded (UNRUN until Stage 6).

## criteria
Acceptance test: a fake-game selftest raising RM_ContagionTouched severity across the active-change threshold, dipping
and raising it again: exactly one message at the first crossing and none below the threshold: 2 passes. Drafted at
filing and not yet runnable; the building run writes it first and watches it fail on the base (no message exists).
Live: scene `sc_touched_reads_early` (design/concepts/Contagion/scenes.json).
