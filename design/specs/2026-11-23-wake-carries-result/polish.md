# Polish: the run-end wake's result and state block

- A `LEFT OPEN:` note on the ledger, with none in the result text, gives no owed line: the run stands in the second group.
- When `finish` could not read the item (or its clone is gone), `owed` is empty in the pending file; the log steps say
  UNMEASURED.
- `game_lock.py query all` ends 2 when one game is blind: the other game's answer then stands inside the COULD NOT LOOK line.
- The `ok=(0, 3, 75)` of the locks reader is wider than `query all` needs.
- Codex review 2026-11-24, not significant in ordinary operation (pipe-reason-counted-as-switch, `run_end_wake.py:235`): With no family switches OFF, run `./pipe off stage:in_game --why $'Compare with the previous output\nfamily:probe OFF: example from yesterday'`. On the next wake, the pipe block drops the second line of the stage reason and reports `switched OFF: 1 family`, even though the only switch is for the stage.
- Codex review 2026-11-24, not significant in ordinary operation (default-account-reader-untested, `selftest_run_end_wake_result.py:227`): Deleting the `accounts` entry from `default_readers` would leave the reviewed checks green. Every real wake would then omit the account reading, even when `account_usage.py now` would answer.
- Codex review 2026-11-24, not significant in ordinary operation (done-heading-untested, `selftest_run_end_wake_result.py:124`): Changing `== THE OTHER` to `== DONE` would pass the reviewed tests. A successful run whose whole result is `shall I ask him?` would then appear under a heading that calls it done.
