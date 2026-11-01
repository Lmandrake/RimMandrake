## Why
`relentless enrol` accepts an id filed locally but unpublished. `FX.item_state` reads the published ledger, so `retire()` sees `led is None`, treats it as closed from outside and ends it within one tick. `enrol_one` then returns the existing state, so the item cannot come back, and pool `enrol` skips it as already ours. On 2026-11-01 14:25:32Z this ended five items; repaired by hand under the store lock (journal lines "BENCH repair").

## Done when
Enrolling a filed but unpublished item either refuses with a clear message or stays queued until published; it is never retired. A selftest plants exactly this case and fails on the old code. A deliberately retired item can be re-enrolled by a named verb that journals why.
