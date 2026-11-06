# KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES evidence

`run/FlowWorks_20261106T011621Z.json`: SteveDesktop full-list FlowWorks --full sweep, gate shadow, purpose sweep,
sha 5e04961389 (testq J20261105T221601Z-a1ac86, the rerun of J20261105T195743Z-57a7ef, which died INVALID with a
Windows access violation in modcheck status.py after 7986 s). sha256 ba7870035d129df397b97e29cdb5035ca4fbae838ec57cd66ea37c16cf28f121.
Rows PASS 425, FAIL 6, UNMEASURED 227.

`gate.py audit`: chains 93, would_skip 0 (skip rate 0%), misses 0. Why the zero (probed against Steve's gate_index.jsonl,
2944 rows, 96 keys seen in more than one run, so the instrument can match): 90 chains read "no record at this key", 2
inputs unknown, 1 open gate miss (pump_ports_one_per_side). The profile (the composed test list) is in the key, and
every earlier FlowWorks record on Steve is targeted-profile (testq: 768 targeted jobs, 4 full-list). So the first
full-list run has nothing to reuse. The measuring run is the second full-list shadow sweep at the same sha,
J20261106T011656Z-15b610, which this run's records feed.

`records/`: the record files cited by the would_skip chains (none for this run).
