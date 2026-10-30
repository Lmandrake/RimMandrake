# ARENA_TASKS_VET_CHECK_FAILS_AT_BASE

## spec
arena_tasks.py census keeps any task whose fix changed or added a selftest, but never checks that the hidden check DISCRIMINATES: fails at base_sha (with the hidden body overlaid) and passes at the fix. A changed selftest that only edits comments or `assert True` lines passes on base, and the judge then credits every arm. Found by the BENCH review of 67094dc0f6 (GPT second read, finding 1). Measured 2026-10-30 on a seeded 10-task sample of the 241 pool (D:\ClaudeWork\rimmandrake\arena\review_tasks\audit3.log): every task had at least one test that failed at base and passed at the fix, but 2 of 14 individual hidden tests (selftest_reuse.py in RP_TESTQ_FIX_CANARY_PAUSE_IDLES_LANE, selftest_gimmesomeslack.py in RP_GSS_PROOF_DRIVERS_FIX_FALSE_PASS) passed at base. The main fixture also holds `assert True` test changes that the census keeps.
Add a census (or pre-freeze) step that runs each fix_test at the base with the hidden body overlaid and at the fix, in a private sparse --shared clone (binaries excluded unless the test's mod needs them), and records `discriminates: true/false` per check. Drop non-discriminating checks from scoring, and reject a task left with none. Rough cost: about 20 s per test.

## criteria
Done when: every frozen task's hidden.json records per-check base/fix exit codes; a fixture task whose only changed test is `assert True` is rejected; the real pool reports how many checks were dropped.
