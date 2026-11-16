# RIMMANDRAKE_UNPIN_RETAKE_DONE_FROM_A_RESULT_NEVER_WRITTEN

Caused by RIMMANDRAKE_RETAKE_CONTAGION_EXAM_FAILING_ITS_GATE (2026-11-16).

## spec

CRITERION FLAW in the exam_retake steward brief (`maturation_autonomy.py` `steward_brief`): "Done when
`designer_stage.py check design/concepts/<Mod>` passes and …". That command validates an open Designer run's
`result.json` (`result_errors`); a steward retake opens no Designer run, so it reads "no result.json (a closing message
is not a result)" for every correct retake. The bar's meaning (the exam gate passes) is unchanged: the done clause now
reads only `coverage_judge.py status` no longer saying "the exam does not pass", which runs `exam_errors`.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` exits 0 (97 PASS). Watched failing
before the brief edit: "exam gate: the retake brief's done clause is the exam gate a steward can meet … never
`designer_stage.py check`" FAILed.

## criteria

The retake brief names a done condition a correct steward retake can meet, and no other.
