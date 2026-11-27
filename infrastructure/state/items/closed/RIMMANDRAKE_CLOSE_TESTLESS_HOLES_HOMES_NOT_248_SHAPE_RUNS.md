# RIMMANDRAKE_CLOSE_TESTLESS_HOLES_HOMES_NOT_248_SHAPE_RUNS

Close two holes of the open tickets with no test, in the code of the ticket lane. A hole is a state that no program and
no act of the owner or the Conductor ends. The census of 2026-11-26 found the holes:
`design/specs/2026-11-26-testless-tickets/one_page.md`.

The owner's order (2026-11-26, on `RIMMANDRAKE_PROVE_TESTLESS_TICKETS_ROUTE_HE_WAS_TOLD_NONE`): "Please make sure there is a
pathway to provide tests for all tickets without them, given that I'm being told they can't participate in bundling
otherwise. There may be other processes already at work for this outcome."

## spec

`design/specs/2026-11-26-testless-tickets/conductor_decisions.md` holds the Conductor's decisions and the rules for the
build. In short:

1. Give each old ticket with no home a real home (`mod:`, `pipeline:`, `machine:` or `game:`) by rule, with no model run.
   Then the work bundle of that home takes the ticket. Name for Shape only the tickets that no rule can place, oldest
   first, from 2026-12-02.
2. A block with no kind, no `--on` and no lift date, idle for 3 days, is due for a Shape run. The Shape run gives the
   block its kind or lifts the block. The Shape run first drops a stale or wrong ticket with its reason.
3. The ten tickets of Pyrelands and Wrecked Machines are not in this build
   (`RIMMANDRAKE_DECIDE_PYRELANDS_LEDGER_PILOT_TEN_TICKETS_NO_ROUTE`).

## verify

`python3 design/specs/2026-11-26-testless-tickets/holes_check.py`: 1 check. Exit 0 holds, exit 1 fails, exit 2 could not
look.

Watched failing on base 8a4263dc29 at 2026-11-26 9:53 PM PST, for the reason that this ticket names: 266 no-home holes
and 76 untyped-block holes of 1,067 open tickets with no test. The check counts a hole at any depth of a ticket's park
or hold, so its no-home count is higher than the 248 of the page.

## criteria

- `holes_check.py` exits 0 on the live ledger.
- `testless_census.py` reads each new route from the lane's own code. No hole flag is changed by hand.
- Each new rule has a selftest case that is red under a planted fault and green on the real code.
- The age line sends no ticket to Shape while the class of its home is off. A selftest case with a `game:` ticket under a
  live block, idle 3 days, with the class `game` off, is red on base 8a4263dc29 and green after the fix.
- The boundary page of the ticket lane holds the new promises, written before the code.
- The cost of one Shape run is measured from the run records and written beside the pace of 5 a day.
- No park or hold of a ticket is changed by hand, and the work of no ticket is done.
