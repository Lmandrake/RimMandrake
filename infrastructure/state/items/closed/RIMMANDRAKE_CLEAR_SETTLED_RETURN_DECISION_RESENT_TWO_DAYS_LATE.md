## spec

`src/RimMandrake/rimflow/designer_stage.py` close_run set `pending_decision` on a `return` and never cleared it. Graffiti's
2026-11-15 gap list (rm-coverage-judge-1794730911, 24 gaps, settled at that day's lock) was still in its stage.json and
was re-sent as "Returned here for this missing decision" to the 2026-11-17 stage-3 run (rm-role-designer-1794939319)
after a re-pin, while the live verdict (rm-coverage-judge-1794936862) had 2 different gaps.

Fix (done in the same run): a `done` close pops `pending_decision`; the first done after a return is the returned-to
stage's, so the decision is settled there.

## criteria

No packet names a returned decision after the stage that received it has closed done.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_stage.py` prints ALL PASS; its check "a done run
settles the returned decision" failed on 6632657a9e and passes with the fix.
