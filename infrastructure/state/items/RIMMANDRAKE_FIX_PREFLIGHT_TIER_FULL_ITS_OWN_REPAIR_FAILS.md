## spec
Found by the detached run of RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS (2026-11-15). There is no `small`,
`wide` or `full` tier in `src/RimMandrake/Utils/modset_builder.py --list` [measured 2026-11-15]. Yet:
1. the E12 repair text (`ticket_preflight.E12_FIX`) proposes `tier: <small|wide>`, and the C4 repair proposes
   `tier: small`: a ticket that obeys the repair then fails C1 ("no tier modset_builder knows");
2. a ticket that writes `tier: full`, exactly as C4 and spec section 2.1 ask, fails C1 for the same reason.
The core acceptance fixture held a `full` tier, so the real table never saw it.
Fix: C1 reads `full` as the owner's Full list (PASS, with defs judged UNMEASURED against it, as no offline list holds
it); the two repair texts name "a tier from `modset_builder.py --list`" instead of invented names.

## refs
file: src/RimMandrake/rimflow/ticket_preflight.py
file: src/RimMandrake/rimflow/selftest_ticket_preflight.py

## verify
python3 src/RimMandrake/rimflow/selftest_ticket_preflight.py

## criteria
- A1: the selftest prints PASS and exits 0, including "C1 good: `tier: full` names the Full list" and "a repair
  proposes only real tiers".

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_ticket_preflight.py` exits 0 (`PASS`). Watched failing on
a56213203b plus the new clauses: `FAILED 2` (the two clauses above), exit 1.
