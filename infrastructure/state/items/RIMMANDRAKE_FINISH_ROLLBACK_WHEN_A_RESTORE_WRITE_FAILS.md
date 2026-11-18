# RIMMANDRAKE_FINISH_ROLLBACK_WHEN_A_RESTORE_WRITE_FAILS

## spec
Codex review, 2026-11-18 (`D:\ClaudeWork\rimmandrake\evidence\pass_record\codex_round1.txt`, finding 4):
`src/RimMandrake/rimflow/maturation.py` `commit_move()` puts back every file already written when a later write fails, but
the put-back loop itself calls `write_text`; if one put-back write fails (ENOSPC, the same cause as the first failure), the
loop raises out and the files before it in `done` (the stage record first) stay written. A move can then read as made with
its journal unwritten. A process killed between writes leaves the same partial move (no journal of intent). Fix: attempt
every put-back even when one fails, and raise one error naming each file left unrestored; optionally a move-intent file
written first and cleared last, so a partial move is visible to the next reader.

## criteria
- A selftest case where the journal write fails and the put-back of the stage record also fails once: every other file is
  still restored, and the raised error names the stage record as unrestored.
- Acceptance test: that case in `src/RimMandrake/rimflow/selftest_maturation.py` (drafted here, not yet written or watched
  failing).

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation` GREEN with the new case.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
