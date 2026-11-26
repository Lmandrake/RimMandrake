# WB-pipeline-bridge-20261126-100834 state

Worker run 1, 2026-11-26 from 2:13 AM PST (detached, Archmagi clone ADVANCEUNTIL_WIRE_PER_TICK_STOP.det).

## Done
| member | outcome | commit / reading |
|---|---|---|
| ADVANCEUNTIL_WIRE_PER_TICK_STOP | superseded by RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED (done) | bridge v2 built safe_advance until= with the exact stop (5cebf3567f, f0b11bc10a); runKey replaced by scene.attach |
| CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER | dropped, stale | an "Adapt to Lightspeed" capability; Lightspeed retired (d2a0462048); 3 of its 5 consumers dropped as dead |
| COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT | routed to the Conductor | re-level A1/A2 from L4 (owner level) to L2; L2 lane passes J20261125T203007Z-82a495, J20261125T205643Z-b87e32 (shape 7322f3bf4d) |
| BRIDGE_TPS_REVIEW2_FIXES_1 | REFUSED BY BUNDLE (C4 only) | C4 needs the full list, retired until integration |
| VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL | REFUSED BY BUNDLE (A2 only) | A2 needs the full list, retired until integration |
| MAP_AWARENESS_PROVE_ON_A_QUIET_MAP | REFUSED BY BUNDLE (A10 only) | A10 stages a drop-pod raid; raid tests paused |
| (no ticket) pipeline defect: a later RUNNER verify voided a bundle refusal, so 4 of yesterday's refused members came back today | fixed | c7dd53c26a, selftest_work_bundle red on the parent, green on the fix |

## Next, in order
Nothing. Every member has an outcome. No fresh reader ran on c7dd53c26a (a one-condition change; this brief bars subagents).
