## spec
A detached run can end "success" with its item still open, and nothing says so. Seen 2026-11-15: run
`rm-detached-bench-rimmandrake-fix-pyrelands-round-six-seve-1794775111` landed all 17 Pyrelands gaps and the one re-pin
(26fe15df8b) and exited 0. Its item `RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS` stayed `proposed`: never claimed,
never closed. The final-look grant in `design/concepts/Pyrelands/stage.json` (`coverage_release_granted.after`) waits on
that item closing, so the one look would have stalled with nobody owing the close. BENCH closed it by hand with proof.
2826ca6878 now has the chain steward close a landed `after` item. The general hole is still open: a successful run that
leaves its item open.

Fix: when a detached run ends success and its item is not terminal, the run-end step (detached_helper) writes a plain note
on the item, and the tick status line names it as owed: "run X ended success; item Y is still <state>: close it with
its published sha or say what is left".

## verify
- Acceptance test: a selftest fixture where a run ends success with its item `proposed` shows that line on the item and on
  the status line. It fails on today's base. It passes with the fix. A mutant that drops the check goes red.
