## spec
Codex's full-file review of the seven claim fixes (32098a6e2c; raw
`D:\ClaudeWork\scratch\control_claims_review_20261118\codex.txt`) refused on items that touch those same promises:
- its 6: a unit-targeted write-now/at-easy-spot stop of a run that had not started cancelled it, then still wrote a
  stop order with run=NULL and an escalation timer for it; nothing ends that order. And `_mark(..., "killed")` left
  the run's earlier orders pending. Fix: no cooperative order for a run just cancelled before start; `_mark` (any
  terminal move) finishes the run's pending/seen orders.
- its 9: `stop()` released live runs' trials as faults without `_fault_alarm`. Fix: alarmed after the commit.
- its 7: the hook's mark could turn a `done` order back to `seen`. Fix: the update is conditional on pending/seen and a
  hook that lost that race says nothing.
- its 12-14: the claim 4 guard did not observe the payload (now a marker the payload would write); the claim 7 spy
  could not tell an in-transaction alarm (now reads faults through its own connection); claim 8 had no reservation and
  accepted any non-live state (now exactly refused, released, one fault, idempotent).
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` (t_review_claims_eight) prints no FAIL; its
three new cases ("a write-now stop of an unstarted run ...", "a run recorded killed leaves no pending stop order",
"a stop that releases a live run's trial as a fault sounds the alarm") watched red on d2a046204 [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- the three new cases red on base, the whole selftest_control green.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
