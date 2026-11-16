## spec
The Dispatch tick (`maturation_dispatch.py tick --apply`, run from /home/mandrake/rm/dispatch) decides and launches from
its own clone's tree, but measured the clone's distance from origin/main only AFTER launching. On 2026-11-16 the clone
sat 51 behind / 9 ahead for 51 min (last level 2:14 AM PST); cycle 6's record with its exit block landed at 02:57
(290ce0c736) and at 03:02 the tick, reading the 02:07 lane-1 copy (`## Exit (pending)`), filed and launched
RIMMANDRAKE_COMPLETE_GIMMESOMESLACK_CYCLE_SIX_RECORD_NO, a steward run for a record gap that did not exist.
Fix: measure the clone before the launch step; while it is measured behind past the OPS_DISPATCH_CLONE_BEHIND_UNSTICK
alarm's threshold (5 min), launch nothing (decision `stale_clone`, a Needs Conductor line) and hold the run seals,
run.end and spend rows (idempotent: the first level tick writes them). The same 02:59 publish from the stale clone
sealed JUDGE.judge-1794822790 as 0 lines (19 landed), flagged its run.end NO_VERDICTS (false: the judge wrote 19 lines)
and dropped the 02:31 re-seal line (DISPATCH:d5cbe4dc4bce5af2), so selftest_modledger_tree refused every publish;
repaired by re-sealing both shards from the landed tree and rebuilding the views (the false NO_VERDICTS flag stays in
that run.end line). Same root as RIMMANDRAKE_SEAL_JUDGE_SHARD_FROM_SYNCED_CLONE_SEALED_EMPTY. A lag under 5 min holds
nothing; an UNMEASURED fetch holds nothing (errs toward allowing, as before). Unjamming the clone stays Operations'
alarm (RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE).

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py` → rc 0, 0 FAIL (172 PASS).
Watched red on the base (rc 1: 1 FAIL "a clone 10 min behind launches nothing", 170 PASS; then the seal-hold check
red alone, 171 PASS).

## criteria
A tick whose clone is measured behind > 5 min launches no run and writes no seal, run.end or spend
row; the first tick behind still launches.
