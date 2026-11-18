# RIMMANDRAKE_FIX_DENIED_REFUSAL_LOST_WHEN_LOG_FAILS

## spec
Split from `DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE` (Codex round 4, claim 1), verified red on 28e44286c3.
`denied_runs()` advances `denied_seen` in `_refused_last()` before `do_conductor()`; when that raises (the Conductor log unavailable), execute() records incident_failed and the tick saves the advanced mark, so the refusal is never handed on. Fix: give the marks back when the hand-off raises, then re-raise.

## refs
file: src/RimMandrake/rimflow/dispatcher.py
file: src/RimMandrake/rimflow/selftest_dispatcher_incident_bells.py

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_dispatcher_incident_bells.py` exits 0 (its "claim 1" lines ok). Watched red on base 28e44286c3: the next pass handed nothing on (`[]`).

## criteria
- a do_conductor failure still raises to execute; the next pass with a working log hands the same refusal on, once.

## review
Codex review of the fix, two looks (`D:\ClaudeWork\rimmandrake\scratch\dispatcher_incident_bells_review_20261118\codex_review_1.md`, `codex_review_2.md`); every flaw it found was given a test, watched red, and repaired in the same sha.
- a beat cut (StepCut) during the told read or the hand-off gives the marks back too.
