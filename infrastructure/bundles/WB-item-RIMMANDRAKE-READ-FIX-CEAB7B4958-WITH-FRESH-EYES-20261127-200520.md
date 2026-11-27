# WB-item-RIMMANDRAKE-READ-FIX-CEAB7B4958-WITH-FRESH-EYES-20261127-200520

- `RIMMANDRAKE_READ_FIX_CEAB7B4958_WITH_FRESH_EYES`: done. Fresh read of the `./now` fix at ceab7b4958.
  - Problem (queue-head-listed): the count line named `cli.py queue BENCH`, a compact view that held 15 of 37 ranked
    items. Fixed at 4d724b8e1f: `./now --queue` lists the whole ranked queue, and the line names it. The red run of
    t_queue_head_listed was seen on the base.
  - READ-CLEAN: `boundary_check.py` (re-marked at 93073fd330 after another run added a PAGES row) and `./now`.
    FLAGGED: `now.py` and `selftest_now.py`.
  - Polish line: `design/specs/2026-11-19-clean-means-promises-tested/polish.md` (code_files skips the root `now`).
- Group size: one member. Nothing is next.
