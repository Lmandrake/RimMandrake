# RIMMANDRAKE_STOP_RELENTLESS_SELFTEST_LOGGING_FAKE_CLONE_FAILURES

## spec

`scratch_clone.py report` said 1242 of 6114 clone calls failed, the last "pool full: 0 clones, cap 0". Measured
2026-11-16: 1210 of the 1242 (and all 15 of the last 48 h) were seat `clones`, purpose `relentless I0`, "cap 0":
selftest_relentless.py's "the pool's real refusal" fixture runs the real scratch_clone.py with RM_POOL_MAX_CLONES=0
but without RM_OBJSTORE_STATE, so every run of that test appended a fake failure to the live
~/.local/state/rm-objstore/uses.jsonl (watched: one run moved its `relentless I0` count 1211 -> 1212). The real pool
had 7 clones, cap 16. Fix: the fixture sets RM_OBJSTORE_STATE to its own dir and asserts the row lands there. The
1211 fake rows were removed from the live log (copy: D:\ClaudeWork\rimmandrake\backups\bench_cleanup_2026-11-16\
uses.jsonl.before_strip); 32 real failures remain, none in the last 48 h. Pre-existing and unrelated, still red in
the same test: "real: the pool is every eligible item, the proposed backlog included" (Relentless retired 2026-11-13).

## verify

`python3 src/RimMandrake/rimflow/selftest_relentless.py` then `grep -c 'relentless I0' ~/.local/state/rm-objstore/uses.jsonl`
unchanged by the run, and the line "the refused call is logged in the fixture's state" ok.

## criteria

- A selftest run adds nothing to the live uses.jsonl.
