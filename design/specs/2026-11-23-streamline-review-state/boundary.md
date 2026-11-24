# BOUNDARY: a close records its own evidence, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/cli.py` (`cmd_close`, `_close_evidence`). Item
`RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION`, written 2026-11-23. Why: a hand close wanted two commands
(`verify --level L0`, then `close`). 357 of the 364 code closes after 2026-11-21 noon UTC took neither: each is marked
`uncheckedLifted`. The test of the promise's name is in `src/RimMandrake/rimflow/selftest_close_gate.py`.

## ACCEPTS

- **a-close-with-evidence.** `rimflow close <ID> --sha <sha> --evidence "<what ran and its result, or a path>"`, with an
  optional `--level` (default L0) and `--config` (default `close`).

## DOES NOT SURVIVE

- **false-evidence.** The text is the closer's own word. No program reads it.
- **a-second-writer-in-the-gap.** The pass and the close are two events. A process killed between them leaves the pass.

## PROMISES

- **close-records-its-evidence.** The close writes a level-tagged pass on that sha with the evidence, and then the close,
  which is not marked `uncheckedLifted`. A close that is refused (an owed criterion, say) writes neither. A
  pass after a fail clears the fail, as a separate `verify` did. Blank
  evidence is no pass. With `--no-code`, the evidence is added to the `--no-code` words and no run is written. Evidence that
  the ledger cannot record as a run (the item is another seat's) is said in one line, and the close goes on unchecked.
