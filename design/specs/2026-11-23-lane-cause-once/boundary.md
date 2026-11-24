# BOUNDARY: one SteveDesktop ticket per lane cause

Code: `src/RimMandrake/Utils/testq/lane_ticket.py`, `src/RimMandrake/Utils/testq/steward.py`.

## ACCEPTS

- A lane state and a reason reported by the lane, incident times in epoch seconds, and a ledger of tickets and claims.
- The steward and heartbeat watcher write the incident clock for Operations. Ingest reads finished jobs from the test queue.

## DOES NOT SURVIVE

- A restore that loses both queue and ledger loses their history. An unreadable incident time is unmeasured.

## LIFE CYCLES

- The steward waits for the existing recovery proof, or a fresh heartbeat for the watcher. A different fault starts its own incident while carrying the unowned escalation time of a continuous outage.
- A seat keeps work it holds. The steward lifts only its own cause wait. Terminal items keep their ledger keys and remain terminal.
- Operations reads time from the current incident's first rung, including when a due rung could not file. Old incident records use the ledger reading.
- Ingest notes sub-threshold self-healing sightings on the filler host. Those sightings still carry no verdict for the affected chain.

## LIMITS

- Three distinct jobs in the 24 hours through the current finish. The ticket counted 31 repair items in 21 days, including one-off faults the lane now heals.
- The steward's existing 10, 30 and 120 minute ladder and Operations' 30 minute target guard an unowned stall like the recorded 166-minute brake.

## PROMISES

- **cause-identity.** A changed state or cause gets a different ticket, even during a continuous outage.
- **incident-lifecycle.** Recovery ends the incident and leaves its cause ticket on a named wait. A return lifts the wait and notes the same ticket at the first rung.

The acceptance script exercises pure key identity and incident timing. The Operations clock and ingest threshold are exercised in `selftest_ops_watch.py` and `selftest_ingest.py`.
