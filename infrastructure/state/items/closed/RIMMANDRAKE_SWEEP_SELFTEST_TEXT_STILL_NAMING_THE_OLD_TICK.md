# RIMMANDRAKE_SWEEP_SELFTEST_TEXT_STILL_NAMING_THE_OLD_TICK

## spec

Selftests pass at `./publish` and their file names are neutral, but 56 of them name Relentless or a `relentless_*`
module in docstrings, check labels or fixtures (census: 104 contain the word in any form). A reader of a test is told the
retired tick is what it guards. Do after `RIMMANDRAKE_RENAME_RUN_STORE_AND_POOL_OFF_TICK_PATH` (many hits are store
paths): rewrite each to what the test guards today; a fixture that replays a recorded Relentless event keeps it and says
so on the line ("recorded", "retired").

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    git grep -l -E '\bRelentless\b|relentless_[a-z]' -- '*selftest*.py'

prints nothing and exits 1 once done (a line that says the thing is retired or recorded may be exempted by a gate rule
instead; if so, the test becomes that gate's selftest). Watched failing 2026-11-19 BENCH at `fbdf50a5b2`: 56 files.

## criteria

- A1: no selftest names the tick as a live thing (the grep above, or an era_text rule over selftests).
- A2: every touched selftest is green.

## refs

file: src/RimMandrake/rimflow/era_text.py
