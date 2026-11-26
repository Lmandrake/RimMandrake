Before you edit a number or a comment in rimflow/coverage_judge.py, or any brief or clause text a calibrated gate reads, read the family's `brief` list in infrastructure/state/judge_calibration.json: that whole file is the judge's calibrated brief, so any edit moves the brief hash and resets coverage_judge to UNTESTED, silently, and only a paid calibration brings it back. Pass the value from the caller (role_launch.JUDGE_TIMEOUT_S) instead. The same holds for evidence_gate.py and maturation.py, whose calibration is free (refusal_contract.py calibrate). After you edit any file in a judge_calibration.json row's brief list, rerun that family's check in the same run, before the first publish.

- Filed 2026-11-25: a brief or clause text that a calibrated gate reads (refusal_contract.py: a why_sound or a clause line of maturation.py's advance checks) changes the brief hash; ./publish then goes red on selftest_calibration_rows_current.py until you run refusal_contract.py calibrate and land infrastructure/state/judge_calibration.json with the change. Run calibrate before the first publish when you edit such text.
- 2026-11-25: b39aa9f4e1 (the builder-role merge) moved the hash of four CALIBRATED judge briefs, so their refusals bound nobody until a later calibrate --model run re-earned them.
- A full calibrate also resets other seats' families: recalibrate only your row (lesson 20261115T132719Z-BENCH-calibrate-no-run-writes-registry.md).
item: RIMMANDRAKE_MEASURE_EVERY_UNMEASURED_TIME_BUDGET_HE_CALLED_IT_LAZINESS
item: RIMMANDRAKE_RUN_LIVE_CHECKS_IN_BUILDER_RUN_WHEN_GAME_FREE
item: RIMMANDRAKE_RULE_ART_FIRST_PASS_WEAK_IS_NO_VERDICT
home: skills/clone-landing-commits/SKILL.md
home: design/RimMandrake/standing_rulings.md §A refusal carries its path to pass
