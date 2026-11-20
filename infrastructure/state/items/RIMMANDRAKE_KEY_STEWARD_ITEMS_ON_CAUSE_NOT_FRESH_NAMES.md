## spec

The testq steward (`src/RimMandrake/Utils/testq/steward.py`, `_escalate` and `retire`) files a ticket under a fresh
random name (`mint`) for each lane incident, and drops it when the lane recovers. A cause that keeps coming back
therefore files a new ticket each time. Measured on the ledger: 13 `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_*` tickets
from 2026-11-12 to 2026-11-15. Each one read "filler brake on FlowWorks, Stillsand, Contagion, …", the same brake on
the same mod list. Most were dropped by the steward itself on recovery. About four took an agent's close. The lane has
been paused by hand since 2026-11-15, because SteveDesktop's CPU fault waits for an in-person BIOS visit. So the flood
is quiet now, and it comes back when the lane runs and the brake recurs.

Census and the reason this was not fixed in its own run: `design/specs/2026-11-19-one-fault-one-ticket/census.md`.
The fix is not known yet. Two constraints:

- A cause-keyed ticket must outlive `retire`. The ledger cannot reopen a dropped item.
- ops_watch's `steve.incident_unclaimed_min` (`ops_watch.steve_incident_unclaimed`) ages an open steward item from its
  creation. A reused old item would read days old and alarm at once.

A bad key here would merge two different stalls and silence the lane's only stall alarm.

## verify

Design first: how a recurring cause reopens one ticket without moving the unclaimed-age alarm (for example, the age
from the incident's start, not from the item's creation).

Acceptance test: none, because the design is owed first. The design must name the test: the same brake reason fed in
two incidents files one ticket, and a different reason files a second.

## criteria

- A recurring lane cause reopens or notes one ticket instead of minting a new name.
- Two different stall causes stay two tickets.
- `steve.incident_unclaimed_min` still reads the incident's own unowned age.

## refs

file: src/RimMandrake/Utils/testq/steward.py
file: src/RimMandrake/Utils/ops_watch.py
