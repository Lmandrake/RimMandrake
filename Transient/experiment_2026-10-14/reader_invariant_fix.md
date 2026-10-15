# READER_BASELINE_REPAIR_OLD_ORDER_TRIPS — reader invariant fix

## Cause
`t_real_ledger_projects_as_before` built its baseline by `(ts, file rank)`. For two stamped
events in the same `ts` second in DIFFERENT shards that orders them by shard filename, not by
when they were written. OWNER's reassign of PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP
(ts 11:56:15Z, tsn ...575214677587) and BENCH's lease (same ts, tsn ~1.05 s later): BENCH.jsonl
sorts before OWNER.jsonl, so the baseline put the lease first and logged
`BENCH may not lease ...`. The reader (tsn order) was right; the baseline was wrong. Reader unchanged.

## Fix
`src/RimMandrake/rimflow/selftest_reader_invariant.py`:
- baseline is now the APPEND order, built without `canonical_order`: stable sort on
  `(ts, tsn, file rank)` keeping file position. Where `tsn` is absent (all events before
  2026-10-02 07:22Z; no `ts` second mixes stamped and unstamped events, measured) this is the
  old baseline exactly. The reader's own tie-breaks (subject, VERB_RANK, seat) stay absent
  from it, so the invariant is not weakened.
- new case `t_real_ledger_survives_union_scramble`: scratch copy of the real ledger, every
  file shuffled, 30 lines duplicated per file, lines moved between shards; must fold to the
  identical World.

## Proof it still catches divergence
Mutated copies of `rimflow/` in the scratchpad, run against the real ledger read-only
(md5 of every ledger file identical before/after):
| mutation of model.py | result |
|---|---|
| none (control) | 9/9 |
| reader orders same-ts events by SEAT before tsn (the old baseline's flaw, as a reader bug) | FAIL t_real_ledger_projects_as_before (only) |
| canonical_order does not dedupe | FAIL dedupe unit + both real-ledger cases |
| read() keeps file position (no sort) | FAIL 5 incl. both real-ledger cases |
| tsn dropped from order key | FAIL tsn unit case (real ledger has no tsn-only-sensitive pair) |

## Test results
run_selftests --only reader_invariant, model, concurrency, built_old_reader: PASS 4/4, GREEN.
selftest_reader_invariant.py itself: 9/9.

## Review / commits
Full-file review of selftest_reader_invariant.py: one fix during review (docstring said
"1.0 ms", is 1.05 s); nothing else found; marked CLEAN after commit.
