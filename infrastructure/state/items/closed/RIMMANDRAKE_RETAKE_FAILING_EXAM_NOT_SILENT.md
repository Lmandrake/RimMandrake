# RIMMANDRAKE_RETAKE_FAILING_EXAM_NOT_SILENT

## spec

Seen 2026-11-15 on Pyrelands: the exam on file fails the gate added at 677d7dfdb4 (no Challenger scenario, no
exam_control/copy.json, control missed_ids unset; `designer_stage.exam_errors`). `coverage_judge.plan` then returns
"skip: the exam does not pass" inside a Designer run's pre-step, and nothing shows it: the Maturation tick read the
concept as a plain Designer wait.

Fix: the tick reads the exam's gate for a stage-5 concept that is not locked, not stopped and owes no chain. A failing
exam is owed work: one steward run (kind exam_retake, once per tree) whose brief is the exam retake by
roles/designer_exam.md in full, checked by `coverage_judge.py status` no longer reading "the exam does not pass". The
status line says "exam fails its gate: <errors>". The chain steward's brief carries the same retake rule.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` checks "exam gate": a stage-5
concept whose exam fails launches one exam_retake steward whose brief names roles/designer_exam.md and the errors, its
status says the exam fails its gate, a spent retake is PAUSED with that text, and a passing exam stays a Designer wait.
It fails on 437b7391b3.
