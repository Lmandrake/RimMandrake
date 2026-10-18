# validation_v2 triage log — FOUNDRY helper, 2026-10-18 (offline, no bridge)

Scratch clone `/home/mandrake/rm/scratch/FOUNDRY/v2triage` at origin e23ef031a. Evidence: day-3 result
`src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261017T180214.json` (32/24/5) against the last green
run BEFORE P3..P13: `Transient/fw_mouth_live_20261016/validation_v2_result_20261016T231546.json` (61/0/0, 10-16 23:11).

## Group 1 — pond / flow rows (S3, E2, E3, E5, G, R, E6) — classified
- Cause: the live harness's PulseOracle was still the WHOLE-NOTCH model (`level_exact` never passed at the site), while
  the shipped engine is exact-level since P3 (levelExactEnabled, owner by card 2026-10-17), AND the painted WaterShallow
  ponds now get a P11 lake floor (0.5 m shelf on the outer ring) at classification.
- Proof (offline replay, `Transient/fw_scenes/v2_replay_day3.py`): MockBridge with an exact-level game + P11 shelf beds, harness
  unchanged, reproduces day 3 nearly verbatim: S3 caps 1/4/5/56/100; E2 {4,4,4,None}; E3b final [0,0,0,0] stock 2.0
  (live 2.0094 = refill); E5_sink, E3, E3n mismatch lists cell-for-cell; E4_engine_on_scheduled and E6n diff lists
  identical. So these are SITE (floors) + STALE (oracle), not engine regressions.
- Needed for the replay: level_water's pond node key did `N + bid` (bid an int); the harness names bodies "W2" — fixed
  (`level_water.pond_key`, the live body id).
## Group 2 — scheduler rows (E4, E1c, E6n) + jobs (E7a/E7b/E8) — classified
- E4_on/E6n diffs identical to the replay = stale oracle. E4_off: the 309-tick step ran 0 ticks (live-only); E1c's
  leads {9,69,129,189} are exactly that (the 251 pulse still pending). Jobs: no colonist moved.
## Group 3 — pits (P1, P4, P4f, P4b, P5n) + walking (X2, X3, X4) — classified (c), unresolved
- All clean in the mock; live no pawn moved (P3f launched from its spawn cell; 10-16 it had moved one). X1 drew 1.2 at
  D4: not a draw regression. Root cause not found offline; candidates listed in the triage file.
## Group 4 — X6, X10, E9 — classified
- X6 (b): exact level puts the water row at 0.6 notch, junction 1.6 (mock reproduces live). X10 (b): F=0 is not spent
  under dL burning. E9 (a): dead-log branch discarded 2,123 collected lines.
## Edits + offline runs — DONE
- validation_v2: exact oracle (site, mock, oracle_for), deepBedsEnabled pinned off for the site, rows restated, E4/E1c
  hardened, X6/X10 restated, E9 keeps evidence, O5/O7 exact, faults pond_sheds_squares + lake_floor_on_site.
- Offline tier all PASS (O-NEG 16/16, O-LIVE-NEG 44 faults); --mock GREEN 61/0/0; run_selftests --only 10/10 GREEN
  (incl. selftest_flowworks_kernel_oracle). No C# changed.
## Publish — committing (no C#: no DLL rebuild)
