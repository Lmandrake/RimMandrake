# RIMMANDRAKE_BOOK_PIPE_VOID_BY_UNIT_NOT_RUN_ID

## spec
`control.void()` accepts a control run id (`run_<unit>`) or its unit and voids both in the store, but `_void_books`
forwards the raw argument to `void_books`, so `pipe void run_rm-detached-X --why ...` writes `"unit": "run_rm-detached-X"`
to run_void's voids.jsonl. The dispatch books key runs by unit, so the run's trial and stage spend stay charged there
while the store says void (found by Codex in the full-file review of 294dc94beb). Fix: `void()` returns the resolved
unit and `_void_books` books that.

## verify
`python3 src/RimMandrake/rimflow/selftest_control.py`: `t_void_books_by_run_id` — `pipe void <run id>` books the unit,
not the id (watched red on base: got ['run_rm-probe-books-2']).

## criteria
- a void by run id books the run's unit in voids.jsonl
- a void by unit, and a stopped run's books line, are unchanged

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py
