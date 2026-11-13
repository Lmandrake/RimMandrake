## spec
GSS dense proofs (2026-11-12): switchboard rows SW1-SW6 in proof_all core (highlight, lod, breakReadout, sparksOnlyOverlay,
hideHookupWires, needlessLoops), each against a shared all-on control; gravship_scene on/off GS1 rows; the offline
selftest_gss_no_hose with planted faults. Built at 0bdcaf7d52. Plan: `D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\GSS\plan.md`.
Proof lines: `infrastructure/state/live_proofs/RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE.txt`.

## criteria
A1 L2: on SteveDesktop (tier gimmesomeslack), proof_all --live --no-shots --skip-offline gives rows with 0 FAIL, and every UNMEASURED row id is named in an item
A2 L2: gravship_scene on exits 0 (GS1 keepWiresOnGravship on: the aboard span flies)
A3 L2: gravship_scene off exits 0 (GS1 keepWiresOnGravship off: the aboard span is taken down)

## 2026-11-12 carryover (detached helper)
FAIL rows read and classified: `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\gss\progress.md`. Weak proofs were fixed
(4ff9d1df8b). MOD rows were filed: RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE, RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START,
RIMMANDRAKE_EXPLAIN_GSS_D2_SPLIT_ONCE_IN_TWELVE (noted), GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE (noted). A1 cannot pass while those MOD rows stand.
The settings reads are batched (3fbf950875 aerial probe, 71f90b1e96 matrix LiveBridge).
