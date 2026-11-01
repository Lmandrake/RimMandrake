## Why
Requirement OP3, OP4, RO4 in `design/RimMandrake/operating_requirements_2026-11-01.md`. Read that entry first; it names the signal, threshold file and owner.

## Done when
Reader silent: next reader rung on time. Reader acks 'investigating', fault stays, reader killed: escalates anyway. One outage tripping 10 metrics: one incident, one ring, one run. Recovery then relapse: reopens. An alarm kind missing from the routing table fails a selftest; `file --for` an unwoken reader is refused. A ring or a read never counts as an ack. Phone push stays off: the last agent writes the RimPulse line he sees.

Proved by the planted fault on the real path, not by a statement.
