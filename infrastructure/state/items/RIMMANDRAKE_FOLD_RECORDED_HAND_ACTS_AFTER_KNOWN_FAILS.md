# RIMMANDRAKE_FOLD_RECORDED_HAND_ACTS_AFTER_KNOWN_FAILS

## spec

Codex full-file review 2026-11-18 (D:\ClaudeWork\rimmandrake\lane_e\false_hands_codex_review.md point 3): the automatic fold (an act whose reason names a ledger item) runs only on acts collected this tick, so an act appended on a tick where the known-items read failed, or one recorded by hand with a reason naming an existing item, stays unfolded forever and keeps OPS_MATURATION_HAND_ACT_UNFOLDED raised.

## verify

Acceptance test (drafted, NOT yet watched failing): observe once with fx known raising, then again with known holding the named item: the act is folded on the second tick. python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_hands. Watch it fail on the base first.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
