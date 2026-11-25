# Work bundle WB-pipeline-judges-20261125-082122 (pipeline:judges): state

## Done
| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN | REAL | fixed: 3 new families (operations_alarm_stop, findings_judge_stop, rm_judge_stop) in src/RimMandrake/rimflow/stop_rule_calibration.py, all CALIBRATED 5/5; acceptance red 3/6 -> PASS 6/6 | 1b8e2202520f |
| RIMMANDRAKE_FIX_ART_BRIEF_POINTER_AT_ITS_RECALIBRATION | REAL | fixed: art_judge_brief.md E3 cites §2.2; art_judge_brief recalibrated CALIBRATED 14/14 | 1b8e2202520f |
| RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS | ALREADY FIXED (umbrella) | children T1 T2 T4 T5 T6 done; only T7 RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS open, home pipeline:test-lane (another system): close with --remainder T7 | - |

## Learned
- The first Operations question ("do you file an item for this fault, or fix it?") read as either/or: Sonnet said "I fix it rather than file" and answered no. The check was wrong; the question now names either act as yes.
- Each stop family's brief list holds stop_rule_calibration.py, so any edit of the cases resets all three families to UNTESTED.

## Context size after group 1
161,502 of 1,000,000 (work_bundle.py context: GO ON).

## Next
1. Fresh reader (step 4) of stop_rule_calibration.py and its selftest.
2. Live pass: the system runs live through `refusal_contract.py calibrate --model ...` (done, readings in judge_calibration.json last_run).
3. Close the three members.
