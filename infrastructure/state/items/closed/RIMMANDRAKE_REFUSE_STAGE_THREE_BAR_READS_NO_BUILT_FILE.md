## spec
DESIGN DECISION 2026-11-18 (on RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD, which this item replaces): the live "behaviour is built" signal is the test table the Stage 3 exit already reads, not record.json. A bar is built only when at least one of its DECIDING tests `reads` a built file, checked on disk when the gate runs: under `src/RimMandrake/`, a regular file, not a `.py`, not the test's own `file`.
- `maturation.bars_reading_no_built_file(root, tt)` (pure but for the file reads) -> the sorted bar ids that read none; `None` when the table cannot be read.
- The `offline_build` exit gains clause `every_bar_reads_built_code` (in `BUILD_CLAUSES`, so a builder can work it off): refused while that list is not empty, each bar named; `None` is its own refusal, "test table unread", never a pass. would_pass: each named bar's deciding test `reads` the shipped file that implements it. smallest_fix: build the behaviour, add its file to the deciding test's `reads`, remake the table.
- The gate applies to forward moves out of `offline_build` only; a mod already past Stage 3 is not re-gated. No bar, promise or locked file is changed.

## refs
file: src/RimMandrake/rimflow/maturation.py

## criteria
- The acceptance test passes 28 of 28; selftest_maturation*.py stay green; `maturation.py gate <Mod> --to blind_challenge` reads the same as today for ExplosiveKnockback, FlowWorks, GimmeSomeSlack and Pyrelands.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/stage_three_built_file_accept.py` (28 checks; on 69a05807c1 in a throwaway `git clone --shared`, watched: 28 red). Covers: a shipped file, a `:line` suffix, the test's own file, a `.py`, a missing file, a directory, a file outside `src/RimMandrake`, a path climbing out, no reads, reads of the wrong type, no deciders, an unknown decider, supports not counting, several deciders, no bars, sort order, four unreadable table shapes, the five real tables, the clause's place in `BUILD_CLAUSES`.
