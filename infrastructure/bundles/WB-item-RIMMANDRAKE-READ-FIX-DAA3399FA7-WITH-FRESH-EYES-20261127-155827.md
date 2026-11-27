# WB-item-RIMMANDRAKE-READ-FIX-DAA3399FA7-WITH-FRESH-EYES-20261127-155827

Done. One member, one group.

| ticket | outcome | commits |
|---|---|---|
| RIMMANDRAKE_READ_FIX_DAA3399FA7_WITH_FRESH_EYES | fresh read done; one Problem (promise-untested) fixed test first; both files FLAGGED; `fresh_reader.py holds` exit 0 | 03a83fa126 (test), 7b2adbe8a7 and eddf945b0b (polish), 3a5486b96f (flags) |

- Problem: `a-test-worker-never-writes-this-machines-real-list` (page
  `design/specs/2026-11-23-steve-two-games-lane/boundary.md`). The test called `real_list_cmd` alone. A `tier_load` that
  bypassed it (the pre-fix shape, planted with sed) stayed green, 3 of 3 old checks. The new checks drive `tier_load`:
  red on the plant, green on the real build.
- Polish in worker.py: `tier_load` refuses a test's swap before the game down (new check red on the parent, green); the
  `cmd_stop` comment named KillMode=control-group, which is now `mixed`.
- Tests run: selftest_testq_steve2 (whole suite 39 ok after the test fix; after the order polish, its one changed test 7 of 7 ok), selftest_steve_worker_tier,
  selftest_steve_worker_reset_repair, selftest_stage6_checks: all PASS.
- Evidence logs: /mnt/d/ClaudeWork/rimmandrake/scratch/fr_daa3399/ (before, planted, real, after, order_parent,
  order_fix, tier, reset, stage6).
- Live pass: none owed. The change is offline worker logic and its selftest; the lane runs the published worker at its
  next job.
