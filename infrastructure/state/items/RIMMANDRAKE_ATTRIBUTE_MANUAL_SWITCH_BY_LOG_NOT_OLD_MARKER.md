# RIMMANDRAKE_ATTRIBUTE_MANUAL_SWITCH_BY_LOG_NOT_OLD_MARKER

## spec

Codex full-file review 2026-11-18 of src/RimMandrake/Utils/switching_plan.py (D:\ClaudeWork\rimmandrake\lane_e\checkpoint_signal_codex_review.md point 1), read not reproduced by us: manual_switch() treats a switch-log transition as the plan's own when any marker with the same from/to is under 2400 s old, including done and failed markers. If the plan switched lukas->system and the owner then switches system->lukas->system within that window, his last switch matches the old marker, manual_switch() returns None, and a later reset pull can undo his switch, against ACCOUNTPLAN_FIX_UNDOES_SWITCH_IN_FOUR_MIN's promise. A failed arm followed by his own identical transition is the same.

## verify

Acceptance test (drafted, NOT yet watched failing): in selftest_switching_plan manual_switch_cases, a done marker lukas->system at NOW, then switch-log use system->lukas at NOW+60 and lukas->system at NOW+120 (no new marker): manual_switch(last_switch(), markers, 'system') is not None. python3 src/RimMandrake/Utils/selftest_switching_plan.py. Watch it fail on the base first.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
