# The Conductor's decisions on the three questions of the testless-tickets page

Page: `design/specs/2026-11-26-testless-tickets/one_page.md`. Decided 2026-11-26 about 9:55 PM PST by the Conductor window.
These decisions are the Conductor's acts, not the owner's words. The owner's order is on
`RIMMANDRAKE_PROVE_TESTLESS_TICKETS_ROUTE_HE_WAS_TOLD_NONE`: "Please make sure there is a pathway to provide tests for all
tickets without them, given that I'm being told they can't participate in bundling otherwise. There may be other processes
already at work for this outcome."

Build ticket: `RIMMANDRAKE_CLOSE_TESTLESS_HOLES_HOMES_NOT_248_SHAPE_RUNS`. Its outcome check is
`python3 design/specs/2026-11-26-testless-tickets/holes_check.py` (exit 0 holds, 1 fails, 2 could not look).

## Question 1: the old tickets with no home. Decision: give each ticket a real home; do not name each ticket for Shape

- A Shape run is one model run for one ticket. To name each no-home ticket for Shape is one model run for each ticket. A run of
  2026-11-24 took 80 such namings off for that reason (notes on `RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD`).
- A work bundle is the unit of work for old tickets: one run works the tickets of one home. A ticket needs a real home to join a
  work bundle. A real home is a `mod:`, `pipeline:`, `machine:` or `game:` home.
- The build gives each old no-home ticket a real home, with no model run where a rule can decide:
  - A ticket with a `cause:` home takes the real home of the nearest parent in its chain of causes that has one.
  - A ticket with an `item:` home takes the home that the pass of 2026-11-23 recorded for it
    (`design/specs/2026-11-23-old-tickets-by-home/one_page.md`, `python3 src/RimMandrake/rimflow/list_home.py list`). That pass
    placed 1,103 of 1,105 old tickets. First find why the census reads no home for a ticket that the pass placed.
  - A ticket that no rule can place stays for a Shape run. The lane names such tickets for Shape, oldest first, from 2026-12-02.
- A ticket with a real home takes the state of that home: on a route, class off, mod not admitted or mod held. None of those
  states is a hole.
- The pace of the Shape runs for the tickets that no rule can place: 5 a day until the cost is measured. The danger that this
  pace guards: the cost of one Shape run is UNMEASURED, and the account room is short until the reset (his card of 2026-11-26).
  The build reads the cost of one Shape run from the run records and writes the measured figure beside the number.

## Question 2: the blocks with no kind and no end. Decision: yes, the age line takes them

- A block with no kind, no `--on` and no lift date, idle for 3 days, is due for a Shape run, whatever its `needs`.
- The Shape run gives the block its kind (`rimflow block --kind`) or lifts the block.
- The Shape run first checks that the ticket is still true (`CLAUDE.md` §Old work is filtered before any process takes it). It
  drops a stale or wrong ticket with its reason.
- The lane keeps its two slots. No new pace limit is added.
- The age line sends no ticket to Shape while the class of its home is off (`onboard_classes` in
  `src/RimMandrake/rimflow/list_dispatch.json`). This applies to every block that the age line reads, with a kind or without.
  The case: on 2026-11-26 the owner's card answer switched the class `game` off at 7:35 PM PST. At 9:51 PM PST the age line
  sent `BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL` (home `game:world-map`, a live block idle 3 days) to a Shape run. That run did
  the ticket's work and held ArchBig and ArchSmall for it. A selftest case plants that ticket shape and fails on today's code.

## Question 3: the ten tickets of Pyrelands and Wrecked Machines. Decision: not in this build

- The ten tickets wait. The Conductor decides the ledger-pilot status of Pyrelands when its 0.2.0 build run ends
  (`RIMMANDRAKE_DECIDE_PYRELANDS_LEDGER_PILOT_TEN_TICKETS_NO_ROUTE`). The readiness list of the mod gates that act.

## Rules for the build

- Write each test first and see it fail. Then build, and see the test pass.
- `testless_census.py` must read the new routes from the lane's own code. Do not change a hole flag by hand to pass the check.
  Each new rule has a selftest case that fails under a planted fault.
- Write the promises on the boundary page of the ticket lane before the code.
- The run on `RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX` changes the same lane files. Read its commits first.
- Change the park or hold of no ticket by hand. Do the work of no ticket.
