## spec
`src/RimMandrake/rimflow/repeat_guard.py` `_EXIT` includes `^\s*return\b`, so `grown_from` reads any added `return`, including one inside a helper def nested in a new test function, as a line that ends the test early, and refuses the guard. Measured: OPS_JAM_UNNAMED_DIAGNOSE_NEW_KIND_KUQY's close at dc28f8dfe848 was refused over `        return past_gate, acts` in `selftest_jam_classes.py`.

Done when: a return inside a nested def added to a red test passes `grown_from`, a return at the test function's own level or at module level is still refused (selftest shows both). OPS_JAM_UNNAMED_DIAGNOSE_NEW_KIND_KUQY waits on this item's close.
