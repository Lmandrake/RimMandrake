A new gate inside a worker (steve preflight 5b84a35699 proof_lines) silently reds every selftest whose harness drives that worker with a fixture job; the gate's commit must run the worker's harness selftests (steve_worker_tier, steve_worker_reset_repair, relentless_live_tier) and give them the opt-out (TESTQ_PREFLIGHT=0). Also: a selftest that passes a real '--host' to a bridge verb goes over ssh to the real machine's guard (selftest_codex_seats).
item: RIMMANDRAKE_TRIAGE_TWENTY_TWO_REDS_BORN_AFTER_THE_NIGHTLY
home: NONE
