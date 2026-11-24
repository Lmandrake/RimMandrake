# BOUNDARY: replay of wrap-up debts at release

Code: `src/RimMandrake/rimflow/wrapup.py` (`debts_keyed`, `owed_plans`, `restore`, `restore_at_release`) and
`src/RimMandrake/rimflow/cli.py` (the wrap-up replay before `bridge release`).
Tests are in `src/RimMandrake/rimflow/selftest_wrapup_restore_at_release.py`.

## ACCEPTS

- A local game released by its own holder, including `release --mine`. The release uses the selected bridge key.
- Planned setting debts, including legacy ArchBig debts without `game`.

## DOES NOT SURVIVE

- A remote release has no local replay. Replay failures leave the release free to proceed.

## PROMISES

- **replay-is-limited-to-the-released-game.** Preflight skips the subprocess when only another game has a plan.
  The restore command replays the plans of the game named by its environment.
- **answered-writes-pay-only-the-current-games-debt.** A setting key is tracked separately for each game. A write
  back to its original value settles that game's debt.
- **release-passes-the-selected-game-to-python.** The local release passes its game letter to the restore subprocess
  before freeing the hold, including when the shell's ambient game differs.
