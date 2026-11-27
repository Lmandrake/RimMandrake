# WB-item-RIMMANDRAKE-READ-FIX-C25DF44D64-WITH-FRESH-EYES-20261127-120423

All members are done. Nothing is next.

| member | outcome | commits |
|---|---|---|
| RIMMANDRAKE_READ_FIX_C25DF44D64_WITH_FRESH_EYES | closed. The reader found 2 promise-untested Problems and fixed them. Both files are FLAGGED. | fix 712d78153c; polish 8e930d2e99, aa3d87462d; flags d8c8e66a92 |

- selftest_clone_pack.py, timer-clones-from-unit-files: 2 mutants passed (ExecStart lines ignored, no walk-up from a
  path inside a tree). A unit with only an ExecStart= path inside a tree now makes both go red.
- selftest_detached_reap.py, a-child-of-another-users-process-does-not-blind-the-scan: 2 mutants passed (an
  unreadable parent ruled out, the pid-1 guard dropped). An unreadable-parent case and a pid-1-parent case now make
  them go red.
- Polish: a check that the pack prunes nothing (red on a planted `gc --prune=now`), and a wrapped long line.
