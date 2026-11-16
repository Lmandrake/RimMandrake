# RIMMANDRAKE_CHECK_ADVISORY_VERDICT_STILL_RAN_DESIGNER_TWICE

## spec

An unchanged advisory coverage verdict must stop the pre-launch step while the brief is uncalibrated. Once the current brief is calibrated, the concept receives a full coverage review. The old advisory checklist supplies no trusted delta baseline. Existing calibrated verdicts retain their changed-entry and claimed-gap behavior.

Cauldron run `rm-role-designercodex-1794843525` reproduced the unchanged-advisory skip after calibration was published and a later code change reset it. The Designer resolved the recorded implementation fork under the existing symmetric calibration requirement.

## verify

`selftest_coverage_delta.py` reproduces five failed transition assertions before the repair and passes after it. An additional contract-only advisory test fails before extending `stop_exit` and passes after that extension. The regressions cover uncalibrated covered and refused verdicts, skipped-step stopping, full review after calibration, all checklist rows, and removal of untrusted carried gaps. Existing calibrated delta skips remain covered.

The refusal-record fixture now supplies its own calibrated status so the live registry cannot alter its intended repeated-review cases. Its suite passes alongside coverage judge, loop, calibration and stage-five program suites. The delta fixture also accounts for the existing exam entry.

The repaired brief must pass the three planted calibration cases before the Cauldron review runs. Calibration and live coverage evidence will be recorded in the closing ledger entry.
