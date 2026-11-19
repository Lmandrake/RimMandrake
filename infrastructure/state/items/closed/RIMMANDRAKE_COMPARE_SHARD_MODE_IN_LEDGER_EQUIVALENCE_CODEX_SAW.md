## spec
Codex FULL-FILE review 2026-11-18 of `src/RimMandrake/Utils/seat_sync.py` (review copy
`D:\ClaudeWork\rimmandrake\lane4_publish_sync\park_codex.md`, point 5; read, not reproduced): `shard_upstream()`
(~line 105) treats a local commit to a ledger shard as already upstream when the lines match, without comparing the
file mode. A local commit that only makes a non-union shard executable while upstream adds an unrelated file is then
called landed, and the sync resets it away from main.

## verify
Acceptance test: none yet, not watched failing. The builder first writes a selftest_seat_sync.py case for the scenario
above (only local commit = mode change on a shard; upstream adds another file) and asserts the sync does not report
the commit as upstream. Drop the item if the case passes on base (Codex's reading wrong).

## criteria
- A local commit whose only change is a shard's mode is never treated as already on origin/main.
