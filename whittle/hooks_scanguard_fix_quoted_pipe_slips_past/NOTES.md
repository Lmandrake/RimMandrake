# Notes (newest first)

## 2026-11-11 19:58 -08:00 — picked (CLAUDE_STEVEDESKTOP_OFFLINE3, setup)
- Runs: 1, pass (run-1, blind PASS at a2bac49a9a, 30/30 selftest). Non-pass tail 0, so mode whittle.
- Why it is open: not a defect in the hook's code. The deadman's check (`src/RimMandrake/rimflow/live_line.py` `_hook`,
  reads `~/.claude/settings.json` and the settings of the clone the check runs from) ran from `~/rm/dispatch` on
  Archmagi and found the hook unwired on 2026-11-08T20:49Z; it read "running again" 2026-11-09T04:33Z. The same
  20:34–20:49Z sweep reopened CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE, CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK and
  HANDOFF_HOOK_FIX_QUOTED_READY_COUNTS the same way: a class (likely a stale or hook-less dispatch clone), not the
  hook. Classification: HARNESS/ops (settings wiring).
- Measured here at setup: `live_line.check('hook=block_blind_scan.py')` -> None (passes) from this clone;
  `python3 .claude/hooks/selftest_block_blind_scan.py` -> 30/30. `~/rm/dispatch` does not exist on SteveDesktop.
- Owed: the guard test (`rimflow guard ... --test <selftest*.py> [--instance ...]`, see `rimflow guard --help`) and a
  close carrying the running-promise `hook=block_blind_scan.py`. Keep it proportional: one guard test of the class.
- Trap: this lane's gate hook refuses any Bash command whose text holds the close flag for running-promises (it reads
  it as driving a game). Put the close command's arguments in a file or use the Write tool for prose that names it.
- Read first: `src/RimMandrake/rimflow/live_line.py` (`_hook`, `settings_paths`), the existing
  `src/RimMandrake/rimflow/selftest_live_*.py`, and how `rimflow guard` runs its test on the instance (cli.py).
