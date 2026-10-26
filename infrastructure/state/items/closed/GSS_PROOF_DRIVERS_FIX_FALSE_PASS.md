# GSS_PROOF_DRIVERS_FIX_FALSE_PASS

GPT review findings FF_validation_suite_*, verified CONFIRMED by GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS (2026-10-26).
Raw findings: D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\F_validation_suite_<part>.md. Line numbers are at e101a7383a.
Each fix needs a selftest that fails before and passes after (see FlowWorks/northstar/selftest_gptfw_review_fixes.py for the pattern).

| finding | verdict | evidence | action |
|---|---|---|---|
| 9.1 | CONFIRMED | validation_style.py:687 S9e compares vs s10 snapshot; s12 D1/D7 (359-362, Z12=Z0+27) build inside SITE2 (341) after it | fix: snapshot just before save |
| 9.2 | CONFIRMED | GSS validation.py:1652 PASS ignores plog; ours errors-only | fix |
| 9.3 | CONFIRMED | GSS validation.py:880-890 M5 never requires far run changed / build ok | fix |
| 9.4 | CONFIRMED | validation_aerial.py:951,975 unfinished phase returns w/o row; run_theft aborted=None; main 1177 rc 0 | fix |
| 9.5 | CONFIRMED | validation_aerial.py:466-470 mixed_net printed only | fix: UNMEASURED SITE if not mixed |
| 9.7 | CONFIRMED | selftest_gimmesomeslack.py:77 cwd=/mnt/d/Luke/dev | fix |
| 9.8 | CONFIRMED | GSS validation.py:1074-1108 stub 70 cells off SITE; finally 1814 clears SITE only | fix |
