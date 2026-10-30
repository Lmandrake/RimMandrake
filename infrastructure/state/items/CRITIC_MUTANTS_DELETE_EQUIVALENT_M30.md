# CRITIC_MUTANTS_DELETE_EQUIVALENT_M30

Filed (BENCH): mutant m30 is equivalent: `zip(a[2:],b[2:])` sits only in the assert MESSAGE of
`selftest_reader_invariant._assert_same_world`; `assert a[1:]==b[1:]` still compares all, so no behaviour changes.
Delete or replace m30, rebuild the set, rescore. Serves ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST.

## verify
- L0: m30 is gone or replaced by a mutant that changes behaviour (its selftest goes red against it).
- L0: the mutant set rebuilt and the critic rescored; the item's note gives the before/after scores.
- Stopping point: finish.

## criteria
- A1 L0: no equivalent m30 in the rebuilt set; any replacement is killed by the selftest
- A2 L0: critic rescored on the rebuilt set, before/after recorded
