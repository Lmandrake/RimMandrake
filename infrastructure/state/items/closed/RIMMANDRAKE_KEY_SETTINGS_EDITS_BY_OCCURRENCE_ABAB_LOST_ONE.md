# RIMMANDRAKE_KEY_SETTINGS_EDITS_BY_OCCURRENCE_ABAB_LOST_ONE

## spec

Codex full-file review 2026-11-18 (D:\ClaudeWork\rimmandrake\lane_e\false_hands_codex_review.md point 2): maturation_hands.py settings-edit acts are keyed by a hash of the old and new values only, deduplicated against recorded acts, so a setting changed A->B, back to A, then to B again records the last change under the first change's id and it never appears (even if the first was folded).

## verify

Acceptance test (drafted, NOT yet watched failing): in selftest_maturation_hands acts section, observe max_live 4->6, 6->4, 4->6 on three ticks: three settings_edit acts. python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_hands. Watch it fail on the base first.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
