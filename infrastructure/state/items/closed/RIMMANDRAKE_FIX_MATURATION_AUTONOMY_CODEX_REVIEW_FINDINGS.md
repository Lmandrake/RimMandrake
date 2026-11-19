# RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS

## spec
Codex full-file review 2026-11-17 of `maturation_autonomy.py` at HEAD (the working tree carried a peer's uncommitted
edits; 2 chunks; raw `/mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_ma_0.txt`, `r_ma_1.txt`). Lines are the HEAD file's.
Items 1,2 confirmed by reading; 3-5 plausible, not probed. Not fixed at filing.
1. (med) l.131 `seed_and_land`: a `land.sh` hang past the 300 s timeout raises TimeoutExpired before the cleanup, leaving the seeded record; later ticks read "had a record" and never retry.
2. (med) l.490 autolock writes both files before its rollback `try`: failure creating the delegated dir leaves VERSION.json locked without the record; `version_locked()` then reads true.
3. (med) l.819 road-back fixer: a first transient launch failure leaves `s["fixers"][id]` with `failed` set; the filter excludes it, so the row reads `fixer_spent` and `_gate` retry is bypassed.
4. (high, per reviewer) l.1488 pilot steward: `MD.ledger_after` raising after a successful launch lands in the handler, which records `unit=None`/`launch_failed` for an active run; the road-back link is lost and a retry may duplicate work.
5. (med) l.1440 a non-transient launch exception omits `cfg["_code"]` from the book entry, so `_gate` never sees a fresh code after the fix.
Acceptance: per finding a case in selftest_maturation_autonomy.py that fails on base.

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Each finding has a selftest that failed on base and passes after, or is ruled not-a-bug with the reason.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy
