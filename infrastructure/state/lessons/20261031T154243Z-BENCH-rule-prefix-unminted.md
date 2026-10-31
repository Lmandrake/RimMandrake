A mint prefix in ops_watch_rules.json is only proved by minting it: OPS_FINDINGS_TRIAGE had no intent word, and my rule stopped rm-ops-watch at its first crossing while every faked-mint selftest stayed green. selftest_ops_watch now mints each shipped name, and a mint failure stays PENDING instead of killing the pass.
home: src/RimMandrake/Utils/ops_watch_rules.json
