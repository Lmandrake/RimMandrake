# BOUNDARY: the Designer's close, its blocks and open preview, the coverage judge's stale refusals and preview, the bar detector, and the gate blocks a filer writes, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/designer_stage.py` (`_ids`, `scene_errors`, `ask_errors`, `close_run`,
`closed_items`, `closed_blocker`, `lift_closed_block`, `unblock_closed`, `open_preview`, `refusals_since_loop`),
`src/RimMandrake/rimflow/coverage_judge.py` (`is_refusal`, `moved_inputs`, `_judge`, `stop_reason`, `look_balance`,
`plan`, `WOULD_JUDGE_EXIT`), `src/RimMandrake/rimflow/bar_rule.py` (`_TUNING`) and
`src/RimMandrake/rimflow/launch_checks.py` (`block_for`, `GATE_PREVIEWS`), with the one steward the code files for
these gates (`src/RimMandrake/rimflow/maturation_autonomy.py` `advance_checks`, the `exam_retake` row). Written 2026-11-19 by the lane
`RIMMANDRAKE_FIX_JUDGE_GATES_AND_DESIGNER_CLOSE_CRASHES` for its items `RIMMANDRAKE_REFUSE_MALFORMED_IDS_CLOSE_RUN_CRASHES_INSTEAD`,
`RIMMANDRAKE_UNBLOCK_CONCEPTS_WHOSE_BLOCKER_CLOSED_DAYS_AGO`, `RIMMANDRAKE_PREVIEW_THREE_GATES_READ_ONLY_FOR_LAUNCH_CHECKS`,
`RIMMANDRAKE_REVALIDATE_INPUTS_BEFORE_REFUSAL_STALE_THIRD_STRIKE` and `RIMMANDRAKE_SPARE_EXPERIENCE_GAPS_FROM_BAR_WORD_DETECTOR`.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_judge_gates_designer_close.py`. The gate
previews' own acceptance test is `src/RimMandrake/rimflow/acceptance/gate_previews_accept.py`. This page covers only
these rules; the rest of these files has other pages or none.

## ACCEPTS (the only inputs this is built for)

- **any-result-json.** A Designer run's `result.json` and the run files beside it, as any JSON a run can write.
- **a-block-reason-led-by-its-item.** A block that names a ledger item names it first: `ITEM_ID: why` (a Designer
  result's `on`, as the stage-5 Slime block reads).
- **one-ledger-fold.** `closed_items` reads the same ledger fold as `done_items` (one replay per ledger state).
- **judge-inputs-hashed-by-fresh-key.** A coverage judge's inputs are the files `fresh_key` hashes (INPUT_FILES and
  the tree without its stamp).

## DOES NOT SURVIVE (not handled)

- **a-block-that-names-its-item-later.** A reason that does not start with the item (`waiting on the ladder:
  SOME_ITEM`) is never lifted by a close: `designer_stage.py unblock` lifts it.
- **a-held-mod-never-opened.** A block whose item closed lifts when the concept is next opened, or by `designer_stage.py
  unblock-closed --apply`. On a mod nothing opens (an owner hold), the block stays in stage.json until one of them runs.
  The tick still pauses on it (`maturation_autonomy.py`, outside this page: `RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS`).
- **an-edit-after-the-judge-answers.** `moved_inputs` compares the inputs at the judge's start with the inputs when it
  answered. An edit between the answer and `record_round` is not seen.
- **a-stale-refusal-in-a-granted-look.** A stale refusal settles its look reservation as charged in the control store
  (`settle_look`); `look_balance` does not count it as a refusing look, so the grant is not spent by it.

## PROMISES (each one is owed a test of the same name)

- **close-run-rejects-non-string-ids.** A scene's `requirement` or `features` entry, or an ask's `about` entry, that is
  not a non-empty string is a rejection reason naming that entry. `scene_errors` and `ask_errors` return it; they never
  raise on it. `close_run` then returns `(False, reasons)` and clears `running`.
- **close-run-never-raises-on-a-result-shape.** When the result validator raises TypeError, AttributeError, KeyError,
  ValueError or IndexError on a result's shape, `close_run` records a rejection that names the exception, clears
  `running` and returns `(False, reasons)`. The run is never left open to be charged as a retry.
- **closed-block-lifts-at-open.** When a concept is blocked on an item that is done, dropped or superseded on the
  ledger, `open_run` lifts the block and reads the gate again. With commit, the lift is written with a history row
  that names the item and its state. A preview (`commit=False`) writes nothing.
- **closed-block-keeps-holds-stops-and-unread.** The block stands, and `open_run` refuses BLOCKED, when the ledger
  could not be read, when the item is open, when the reason says OWNER HOLD, when the item is the coverage alarm
  (`refusal_contract.ALARM_ID`), when a coverage stop or a cleanse block stands, or when the reason does not start
  with an item.
- **unblock-closed-sweep-reads-or-refuses.** `unblock_closed` returns every concept blocked on a closed item, and
  writes the lifts only with apply. When the ledger could not be read it refuses UNMEASURED and lifts nothing. A read
  ledger with nothing to lift is `[]`. The CLI exits 0 for both lists and 126 for the refusal.
- **open-preview-writes-nothing.** `designer_stage.py open <dir> --run <id> --preview` exits 0 when `open_run` would
  open, 1 when it refuses (its words printed), and 126 when it could not look. It prints no packet and leaves stage.json
  byte-identical.
- **stale-refusal-counts-no-strike.** A `not_covered` verdict whose inputs changed while the judge read it is
  recorded with `stale_inputs` (the moved files) and an advisory. It is no refusal: `stop_reason`, `look_balance`,
  `refusals_since_loop` and the second-refusal park do not count it. The round stops nothing and writes no block. The
  next `plan` judges again. A refusal on unchanged inputs still counts.
- **experience-gap-naming-a-def-word-blocks.** A gap whose demand is a player-visible failure that names a def word
  ("Repair its ingestible definition so the eating action completes") blocks. A demand that pins fields ("every
  rostered plant's ingestible and yield fields") stays advisory.
- **gate-preview-blocks-are-one-must-pass.** `launch_checks.block_for("designer_open"|"coverage_judge", mod=...)` and
  `block_for("certify", mod=..., owner_event="OWNER:<tsn>")` return a block that `parse` reads as one must-pass. A
  missing or malformed mod or event raises ValueError. A coverage plan value that `WOULD_JUDGE_EXIT` does not name
  exits 126 (could not look), never 0 or 1.
- **exam-retake-steward-carries-the-open-gate.** `maturation_autonomy.advance_checks` gives an `exam_retake` steward
  row exactly `block_for("designer_open", mod=<its mod>)`, so a retake on a concept the Designer gate refuses (blocked,
  parked, stopped) never launches. A `ready` row keeps its `advance` block; a routing steward (`exit_not_met`) gets
  none.

Later lists beside this page: `polish.md`.
