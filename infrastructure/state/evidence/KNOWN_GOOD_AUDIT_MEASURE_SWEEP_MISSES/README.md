# KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES evidence

`run/FlowWorks_20261106T062717Z.json`: the measuring run. SteveDesktop full-list FlowWorks --full sweep, gate shadow,
purpose sweep, sha 5e04961389 (testq J20261106T011656Z-15b610, attempt a2). sha256
274834e10a208b018eac21758d1a7f3c4071f64b6f07a3605b691c4c81d2bdfe. Rows PASS 539, FAIL 13, UNMEASURED 99.

`gate.py audit` (MODCHECK_GATE_HISTORY=records/): **chains 93, would_skip 51 (skip rate 55%), misses 3 in 1 chain
(miss rate 2%)**. The 3 misses are all `plot_C_limitless_canal` rows that read UNMEASURED now and PASS in the record:
a Fingerspike stabbed a pawn mid-advance (`safe_advance stopped after 240 of 250 ticks: hurt`), a site surprise, so
they are lost PASSes, not valid FAILs. **Valid FAILs on a would-skip chain: 0.** None of the run's 13 FAILs is on a
would-skip chain. 9 more would-skip chains show drift only (`<site hold>` absent -> UNMEASURED: drivers past the
worker's 7200 s budget).

`records/FlowWorks_20261106T040918Z.json`: the record every one of the 51 would-skip chains cites (gate.record.file);
the earlier full-list shadow sheet on Steve, same sha (attempt a1 of the same job).
`records/FlowWorks_20261106T011621Z.json`: the first full-list shadow sheet (J20261105T221601Z-a1ac86, rerun of
J20261105T195743Z-57a7ef). sha256 ba7870035d129df397b97e29cdb5035ca4fbae838ec57cd66ea37c16cf28f121. On its own it
audited to would_skip 0: the profile is in the gate key and every earlier FlowWorks record on Steve was
targeted-profile, so the first full-list run had nothing to reuse. Kept as history; no chain cites it.
