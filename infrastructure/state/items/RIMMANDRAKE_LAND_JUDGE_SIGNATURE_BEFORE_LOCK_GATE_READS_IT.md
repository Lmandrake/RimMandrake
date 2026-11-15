# RIMMANDRAKE_LAND_JUDGE_SIGNATURE_BEFORE_LOCK_GATE_READS_IT — a covered Lock was refused "no coverage signature on the ledger"

(The name records the first theory, a landing race; the measured cause is below. The name is not changed.)

## evidence (2026-11-15)

- rm-coverage-judge-1794753924 judged Graffiti `covered`, `signed: True`; its ledger note reads
  `coverage-signed concept=design/concepts/Graffiti tree=a6eedf87… sheet=40637a73…` (path relative to the concept's clone,
  `/home/mandrake/rm/bench`).
- Lock runs rm-role-designer-1794753910 (14:53Z) and rm-role-designer-1794754884 (15:03Z) were both rejected
  `gate: no coverage signature on the ledger`.
- Cause, measured: the Dispatcher closes from `/home/mandrake/rm/dispatch` (`role_launch.stage_close` →
  `designer_stage.close_run(repo=DS.REPO)` → `result_errors` → `CT.gate(d, repo)`), and `CT.concept_rel(d, repo)` made the
  wanted text `concept=../bench/design/concepts/Graffiti`, which no signature can ever match.

## spec

`designer_stage.result_errors` stage 5 calls `CT.gate(d, clone_of(d) or repo)`, as `coverage_judge.plan` already does.

## verify

`python3 src/RimMandrake/rimflow/selftest_designer_stage.py`: check "stage 5: closed from another clone, the gate reads the
concept's own clone" (1 FAIL on base, watched; all pass after). Live: the next Graffiti Lock run's close.
