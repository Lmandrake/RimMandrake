# RIMMANDRAKE_RETIRE_LEASE_GUARD_TWENTY_FIVE_GHOST_LEASES

## spec
`rimflow` calls `relentless.guard` (cli.py `_relentless_guard`) before every guarded verb (close, implemented, renew,
release, reclaim, claim, start). It refuses the verb when the Relentless store holds the item in a leased state
(running, stopping, candidate, checking, closing, retiring, game). The tick that settled those states is masked
(2026-11-13), so a leased item can never leave its state: measured 2026-11-18 14:50 PST, 25 store items sit leased
(19 game, 4 checking, 2 stopping). Any seat but the Conductor or an `--owner-said` is refused on them for good.
Remove `_relentless_guard` and its call from cli.py and `guard`/`GUARDED_VERBS`/`_conductor_carried` from wherever the
split put them (`RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` moves them unchanged), with
`selftest_conductor_authority.py`'s guard cases. Found by the Phase 2 reach walk
(design/RimMandrake/retired_eras_index_2026-11-18.md, "Phase 2: measured reach").

## verify
Acceptance test (fails on base 1cbd8a9689, watched: rc=1; passes when the guard is gone):
`bash -c '! grep -q "_relentless_guard" src/RimMandrake/rimflow/cli.py && ! git grep -qn "^def guard(verb" -- src/RimMandrake/rimflow/'`
Expected: exit 0. Plus `python3 src/RimMandrake/rimflow/selftest_conductor_authority.py` all ok.

## criteria
- C1: no rimflow verb consults the Relentless store before acting.
- C2: the acceptance test exits 0.
