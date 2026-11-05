# Enact selftests: vacuous-check audit (ENACT_STALE_LANE_FIX_VACUOUS_CHECKS, 2026-11-05)

A check is vacuous when it passes with the code under test broken, because what it inspects is empty or never reached.
`selftest_enact_stale_lane.py` had 4+3 such checks after the 2026-10-26 newest-mark-wins rule. They were fixed in the
ART_X ban build (x_delete).

**Method.** Each of the other 13 `selftest_enact*.py` files was run with module-level `any()`/`all()` wrapped to log how many
items each call saw, line by line. Loop-guarded checks were run with prints injected in memory. Plain `x not in s` and
`.get()` checks were read beside their positive siblings. 16 calls saw an empty collection, and each one is the expected
state, backed by a positive check in the same statement or the same scenario.

| file | checks | vacuous | note |
|---|---|---|---|
| selftest_enact.py | 84 | 0 | 277: the whole plan installs nothing, so the `not any(install RM_Foo)` half was unproven. Now mutant 2 |
| selftest_enact_apply_whole_pick.py | 6 | 0 | `not retired` had no proof that L.retire is ever reached. Now mutant 1 |
| selftest_enact_foreign_retire.py | 3 | 0 | |
| selftest_enact_free_letter.py | 4 | 0 | |
| selftest_enact_missing_snapshot.py | 2 | 0 | |
| selftest_enact_review_fixes.py | 7 | 0 | |
| selftest_enact_seen_build.py | 18 | 0 | |
| selftest_enact_selfpurge.py | 12+1 | 0 | the keep loop (97) checked only the keeps it found. Added a guard that RM_Beet's keep exists; now mutant 3 |
| selftest_enact_slot_membership.py | 8 | 0 | 73/87/94: `inst` is [], and each is paired with a by-name conflict |
| selftest_enact_snaprev_git.py | 10 | 0 | |
| selftest_enact_v2.py | 28 | 0 | |
| selftest_enact_ws.py | ~40 | 0 | |
| selftest_enact_x_archives.py | ~10 | 0 | |

**Guard.** `selftest_enact_vacuity_mutants.py` rewrites one line of `enact.py`/`ingest.py` in memory for each of the
three gaps, runs the real selftest against it, and requires the named FAIL line. The unmutated run must pass, and a
missing anchor fails by name. To add a case, put a row in its `CASES` table.
