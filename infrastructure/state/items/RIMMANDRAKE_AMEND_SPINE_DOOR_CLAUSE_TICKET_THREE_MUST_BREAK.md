## spec
A flawed criterion, for a NEUTRAL fixer (not the builder of RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS, whose
pass it blocks; refusal-contract rule, standing_rulings.md §A refusal carries its path to pass).

Two filed acceptance tests contradict each other; no honest build passes both:
- `src/RimMandrake/rimflow/acceptance/preflight_spine_accept.py` (ticket 1, RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH,
  closed), clause "no door is touched: cmd_claim, cmd_file, relentless.py, detached_helper.py never call
  ticket_preflight", reads the WHOLE of `detached_helper.py` for the string `ticket_preflight`.
- `src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py` (ticket 3) requires `detached_helper.launch` to contain
  `ticket_preflight` (the helper-launch door runs the preflight in shadow, spec section 7 ticket 3), AND requires
  `preflight_spine_accept.py` and `preflight_core_accept.py` (which reruns the spine test) to still pass.
The spine clause was true for ticket 1 ("No door is touched", spec section 7 row 1) and outlived it: ticket 3's job is
to touch the doors. Measured on the ticket-3 build: spine `PASS 29/30`, core `PASS 36/37`, shadow `PASS 19/21`, the
three failures being this one clause and the two "still passes" clauses that rerun it.

Smallest fix (a proposal; the fixer judges): narrow the clause to what still holds after ticket 3, i.e. keep "no
relentless*.py file calls ticket_preflight" and drop the `cmd_claim`/`cmd_file`/`detached_helper.py` half, which
ticket 3's own clauses now cover ("file never refuses", "claim is shadow", "start is shadow"). Ticket 4
(RIMMANDRAKE_ENFORCE_PREFLIGHT_AT_CLAIM_DECLARED_FACTS_ONLY) makes the doors refuse, so a clause asserting "never
called" cannot come back.

## refs
file: src/RimMandrake/rimflow/acceptance/preflight_spine_accept.py
file: src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py
item: RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS
item: RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH

## verify
python3 src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py

## criteria
- A1: with the ticket-3 build landed, the shadow test prints `PASS 21/21`, the spine test `PASS 30/30` and the core
  test `PASS 37/37`, each exiting 0.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py` exits 0 with `PASS 21/21`.
Watched failing on the ticket-3 build: `PASS 19/21`, exit 1 (the spine door clause, and the two "still passes" clauses).
