# RIMMANDRAKE_COUNT_HAND_FIX_ON_UNBOOKED_ROAD_BACK_TICKET

## spec

Found by Codex's full-file review of maturation_hands.py (2026-11-18, D:\ClaudeWork\rimmandrake\lane_e\route_spent_codex_review.md point 6), read in code, not reproduced: `_fix_queue` takes the tick's fix tickets from the fixer book keys and road_back `items`/`ids`, but `_execute_one` writes road_back as only {caused_by, at, from}. A Conductor's hand fixer launched on a road-back item the steward just filed, before the tick books a fixer on it, is not "a fix on the tick's own ticket" and records no hand act.

## verify

Acceptance test (drafted, NOT yet watched failing): in selftest_maturation_hands, a mod with road_back {caused_by: ROUTE_X}, the ledger (fx) holding FIX_ME caused_by ROUTE_X, no fixers book, and a runs_seen run on FIX_ME not in the tick's units: observe records one hand_run act. Run: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_hands. Watch it fail on the base first; drop if it passes.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
