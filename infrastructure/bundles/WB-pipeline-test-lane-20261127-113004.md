# WB-pipeline-test-lane-20261127-113004

State: done. One member, one group.

| ticket | outcome | commit | live reading |
|---|---|---|---|
| HARNESS_REPAIR_CAUSE_AC81755A_4 | closed (class HARNESS) | 7c6c5f4d2d (with dbe3190599) | re-run J20261127T115103Z-6812f8 DONE 11 PASS 2 UNMEASURED (look owed); retest.py passed exits 0; negative control exits 1 |

Fixed with no ticket of its own (the filing gate set it on this run): FlowWorks `_prep_plot` repaints Soil with
`clearOverlays`, bcdf14415c. Live: J20261127T120244Z-fbb99f DONE, setup read back, `river_steam_biome_gate` PASS.
Polish: e2102e62bc (FlowWorks polish.md: one stale pointer, one duplicate line).
Not done: the pre-existing red of `src/RimMandrake/FlowWorks/northstar/selftest_extensions.py` (list drift, the
2026-11-26 line of FlowWorks polish.md), which this run did not cause.
