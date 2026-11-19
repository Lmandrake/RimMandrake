## spec
Codex full-file review of src/RimMandrake/rimflow/maturation_hands.py, 2026-11-18 (`D:\ClaudeWork\rimmandrake\evidence\finish_rollback\rb3_codex.txt`, second P2, pre-existing): `record` builds the act id as sha1(kind|mod|what|%d now): two `record` calls in the same second with the same kind, mod and what get one id; both print RECORDED but read_acts keeps only the first (and the second inherits its fold). Fix: hash time.time_ns(), the pid and --why too.

## verify
Acceptance test (drafted, NOT yet watched failing): two MH main(["record", ...]) calls with the same kind/mod/what and a pinned clock in one second: read_acts holds two manual acts. `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_hands`. Watch it fail on the base first.

## criteria
- Two record calls are two acts.
