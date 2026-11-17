## spec
Dispatch launched two road-back fixers on ExplosiveKnockback a minute apart (2026-11-17, `design/concepts/ExplosiveKnockback/ledger/DISPATCH.jsonl`):
lease.grant run-1794896914 token 12 at 06:28:40Z, then lease.grant run-1794896974 token 13 at 06:29:41Z, whose run.end reads
never_started at 06:29:48Z. `modledger.grant` makes every new lease fence all older ones, so the live holder (run-1794896914)
had its 06:39 lease.renew counted as fenced and every later append refused ("stale token 12 ... this run must stop"),
its closing checkpoint included. Commit 9b5014c74e shows the same shape on run-1794896854.

Fix (choose one in `src/RimMandrake/rimflow/modledger.py` / `maturation_dispatch.py`): Dispatch refuses to launch a
second holder on a mod whose current lease is live (not released, last event under 45 min); or a never_started run's
end revokes its lease and `fenced()` ignores a revoked lease that never wrote, so the older live lease is current again.

## criteria
Acceptance test: `env -u RM_MODLEDGER_WRITER python3 src/RimMandrake/rimflow/fixtures/repro_modledger_never_started_fences_live_holder.py`
exits 0 printing `PASS live holder A still writes after B never started` (1 case). Watched red on 3792dbb557: exit 1,
`FAIL live holder A fenced by a never-started run: stale token 2`. If the fix is "refuse the second launch", the repro's
second `launch` raising is also a pass: adjust the repro to expect that refusal, never to skip A's append.

## verify
Run the repro and modledger's own selftests; check the next two-item road back on one mod launches one holder at a time.
