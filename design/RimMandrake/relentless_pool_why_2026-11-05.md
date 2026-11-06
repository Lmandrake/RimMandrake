# Why Operations' system items stay out of the Relentless pool — 2026-11-05

Item `RELENTLESS_POOL_DIAGNOSE_SYSTEM_NEVER_ENROLS`. A throughput probe listed 74 system items as `not-in-pool`
and could not say why. The instrument that answers now:

    python3 src/RimMandrake/rimflow/relentless_pool_why.py --items [--strict] [--verdict]

For each system item (Operations' ledger classifier, `ops_health.system_ids`; `--verdict` uses the fresh verdict) it
names every clause of the pool's own filters that keeps the item out, in `pool_order`'s order (`eligible`, target, the
concept gate, the first-touch hold), and checks that naming against the real `Effects.pool_order`. An item out of the
pool with no clause, or in it with one, prints UNEXPLAINED; `--strict` exits 1 on any. It files nothing (the first-touch
pass an item owes is reported, never filed). Test: `selftest_relentless_pool_why.py`.

**Result: no item is unexplained.** None of the 74 is a missed enrolment; each class is kept out by a rule.
`content_paused` counts only items in the pool order, so none of them pauses content either.

## The classes (reading of 2026-11-05 ~03:30Z; counts move, rerun the tool)

| class | of the probe's 74 (+16 it tagged REFUSED) | why it never enrols | right or wrong |
|---|---|---|---|
| `parked_by_owner` | 50 (7 of them also built/validated, 2 also kind=design) | blocked "PARKED by owner card (old workflow, stop now, may be useful after the replan)" | right: the owner parked them; `rimflow unblock` reverses |
| `first_touch` | the 16 REFUSED | the item names a mod (title/prose: FlowWorks, SeaShores, Antiquities, LuminousPigment, Baroque members) whose Designer pass is `proposed`, needs=owner | rule as written until 2026-11-05; SUPERSEDED, system items are now exempt (owner card 2026-11-05); these were harness/selftest/tooling repairs, so they wait on an owner sitting for a mod they do not change → `FIRST_TOUCH_DECIDE_HARNESS_NAMES_A_MOD` |
| `state=built` / `state=validated` | 10 not parked (17 built + 3 validated, less 7 parked, less the 3 TESTPILOT below) | the pool takes only `proposed`/`ready`; these were built by seats before Relentless and wait for a verify/close nobody owns now that FOUNDRY is retired | wrong: an orphan state → `BUILT_ORPHANS_WIRE_NOBODY_LEFT_TO_CHECK` |
| `state=doing` + `lease` | 3 (+3 TESTPILOT built with a lease) | taken by a seat process (pid tokens) whose lease expired days ago and was never released | wrong: abandoned work → `LAPSED_LEASES_REPAIR_GHOSTS_HOLD_THE_KEYS` |
| `owner=OWNER` | 4 | pool_seats is BENCH only | right: his items |
| `kind=design` / `kind=decide` | 2 | pool_kinds_exclude | right: the Designer's / Conductor's |
| `needs=harvest` | 1 | pool_needs is offline (+ game needs) | right by rules |
| `blocked` (not parked) | 1 | MODCHECK_SUITE_CORRECTIONS_1, blocked "needs bridge" | right: its own block |

Notes, measured with the tool:

- Most `state=doing` system items in the full list (45 of 161 at writing) are simply Relentless's own line (doing on the
  ledger, a store state); the probe excluded those, the tool tallies them as `state=doing`.
- Only a LIVE lease keeps an item out (`relentless.lease_live`, fixed 2026-11-06 by `LAPSED_LEASES_REPAIR_GHOSTS_HOLD_THE_KEYS`;
  before it a lapsed or released lease held `FLEETWATCH_REFRESH_BUILD_OUTLIVES_ITS_WINDOW`, a `ready` item, out). The 11 BENCH
  ghosts then on the ledger were released or reclaimed; `relentless_pool_why.py --leases` lists any that remain.
- Operations' classifier counts owner-parked items as system work. That inflates "system items waiting" readings
  (the probe's 74) but orders nothing: `pool_order` drops them first.
