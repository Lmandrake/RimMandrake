## spec
Follow-up of RIMMANDRAKE_ROUTE_SOAK_READ_VIA_TAILNET_DESKTOP_SEES_NOTHING (second route landed e4db2787). A reader that gets UNREACHABLE twice in a row is a fault in the monitoring, not news about the CPU. `soak_read.py` keeps no memory between runs: write `soak_read_last.json` (under the agent-storage root) with the time of the first UNREACHABLE in the current streak; on UNREACHABLE print "instrument blind for N min (since <local time>)"; any whole reading clears the streak.

## refs
file: src/RimMandrake/Utils/steve_cpu_retest/soak_read.py
file: src/RimMandrake/Utils/steve_cpu_retest/selftest_soak_read.py

## verify
python3 src/RimMandrake/Utils/steve_cpu_retest/selftest_soak_read.py

## criteria
- A1: a second UNREACHABLE read 10 min after the first prints blind for 10 min, exit 3.
- A2: a whole reading in between clears the streak; the next UNREACHABLE starts at 0 min.

## acceptance
Acceptance test: two cases in selftest_soak_read.py with an injected clock and a temp state file; watched failing on base (no streak text). Live: none, offline-only.
