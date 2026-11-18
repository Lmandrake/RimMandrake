# RIMMANDRAKE_SEAL_SHOWCASE_EXIT_WHEN_PHASE_CRASHES_AFTER_PASSING

## spec
Codex review (2026-11-18, findings 7 and 8 on `src/RimMandrake/HugeThings/northstar/showcase_common.py`, during
`RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE`; `D:\ClaudeWork\rimmandrake\evidence\scene_snapshot\codex_round1.txt`):

- `Showcase.exit_code()` returns 0 when every required row is PASS, even when a phase raised after writing them:
  `run_phases` records `ph["error"]` and `stopped_by`, and `exit_code` checks neither. A crashed showcase exits clean.
- `Showcase.ordered()` skips every phase whose `startTick` is None, so a phase that RAN (its `startUtc` is set) with an
  unreadable clock proves nothing and still reads `phases_in_order=True`.

Fix: `exit_code` is never 0 while `stopped_by` is set; `ordered()` is False for a phase that ran, is not `foreignClock`,
and lacks either tick stamp. A gated phase (never ran, no `startUtc`) is still skipped.

## criteria
- `selftest_showcases.py` case `test_crashed_or_unstamped_phase_is_never_clean`: a phase that writes its PASS row and then
  raises exits non-zero; a phase run on an unreadable clock reads `ordered()` False. Watched failing on base be042db314.
- Acceptance command (exit 0 passes): `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_showcases`.

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_showcases` GREEN.

## refs
file: src/RimMandrake/HugeThings/northstar/showcase_common.py
file: src/RimMandrake/HugeThings/northstar/selftest_showcases.py
