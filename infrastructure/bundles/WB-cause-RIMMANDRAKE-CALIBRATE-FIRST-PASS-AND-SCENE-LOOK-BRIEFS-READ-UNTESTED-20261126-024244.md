# WB-cause-RIMMANDRAKE-CALIBRATE-FIRST-PASS-AND-SCENE-LOOK-BRIEFS-READ-UNTESTED-20261126-024244

Bundle state (builder role, Work Bundle setting). One member, one group.

| ticket | class | outcome | commit | reading |
|---|---|---|---|---|
| RIMMANDRAKE_RULE_ART_FIRST_PASS_WEAK_IS_NO_VERDICT | REAL | fixed | b035119bee (rule), fc8f4c89fe (rerun), be599c23ee (polish) | `calibrate --model art_eval_first_pass`: CALIBRATED, 0 of 9 wrong, 1 of 3 pass and 3 of 6 refuse decided, 5 second look |

- Fix: registry row field `abstain` {answer "second look", decided_share {refuse 0.5}}, read by `refusal_contract.judge_row`
  (owner's option A, note of 2026-11-26 02:36 UTC). Test `t_weak_is_no_verdict`, red before, green after.
- Found on the way: b39aa9f4e1 edited the briefs of findings_judge_stop, operations_alarm_stop, rm_judge_stop and
  scene_look_judge_brief, so they read UNTESTED live. Reran their model checks: all CALIBRATED again (683cc94b0b).
  code_review and set_down_judge stay UNTESTED; neither was CALIBRATED before.
- Fresh reader (rm-builder, Opus): nothing significant; two nits done as polish.
- Live pass: the calibrate runs are the part running for real; no in-game check applies.
