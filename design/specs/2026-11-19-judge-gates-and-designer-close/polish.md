# Polish beside the judge-gates and Designer-close boundary page

One line each. These lines are not part of passing (lane `RIMMANDRAKE_FIX_JUDGE_GATES_AND_DESIGNER_CLOSE_CRASHES`, 2026-11-19).

- bar_rule: a demand that mixes an experience with a yield rate ("the player cannot harvest it; set its yield rate to 8") is still made advisory whole by `detect`; a split of such a demand is not built.
- coverage_judge: `pipe show` (`pipeline_control.py:471` and `:625`) counts every `not_covered` round, a stale one included, so its strike count can read one higher than `stop_reason`'s; pipeline_control.py belongs to lane CTL.
- maturation_autonomy: the tick's `designer_blocked` branch reads stage.json and does not call `designer_stage.closed_blocker`; that hook is `RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS` (lane CTL).
- maturation_autonomy: the `exam_retake` steward (`maturation_autonomy.py:1149`) does not yet write `launch_checks.block_for("designer_open", mod=...)` into its item; the file belongs to lane CTL.
