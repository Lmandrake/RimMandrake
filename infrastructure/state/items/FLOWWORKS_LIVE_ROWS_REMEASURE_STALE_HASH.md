---
state: proposed
needs: game-up
---

# FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

93 FlowWorks modcheck rows UNMEASURED for one cause: no live result recorded at the current mod hash (63 core/v2 rows: validation_v2.py --live --fresh-map; 30 hose rows: proof_hose.py --live), then modcheck record FlowWorks. Report Transient/modcheck/FlowWorks_20261024T191345Z.json

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH` history before building.

## latest ledger notes

- 2026-10-26: Driver wiring (4fb2a190a0..a833d3802c) proven on SteveDesktop J20261026T060806Z-63c715: core_live_rows 52 PASS/1 FAIL (J_workgiver_selection -> V2_FILLIN_SCENE_STAGE_FILL_MATERIAL)/3 UNMEASURED (charmap crash fixed a833d3802c; E6 rain 0; E9 sanity probe). hose_live_rows refused by offline gate: selftest_hose_port P9 26 vs 25 credit sites (ice melter a8f10174f1 untracked) -> fixed 3b43e416ab; rerun J20261026T063635Z-8976fd queued.
- 2026-10-26: hose gate second red: csharp_selftest S4 splice timing 26.0>25 ms (mean of 5) on loaded Steve -> best of 5 in 7b9c522bc8 (published d37eae0373). NEXT: read hose rerun J20261026T063635Z-8976fd (pulls both fixes); a gate red again means another offline step
- 2026-10-29: findings_fold S012337b6d8 retire at 2026-10-28T23:43:13Z: 3 passes in a row after the last FAIL (J20261028T171819Z-72dd17, J20261028T201332Z-519759, J20261028T233401Z-bffd54); count 1 (first 2026-10-26T06:27:53Z, last 2026-10-26T06:27:53Z); FlowWorks/core_live_rows/J_workgiver_selection: ExpectationFailed: [MOD] [('E#a_fillin', {'wg': {'def': 'RM_FillInCanalWorkGiver', 'shouldSkip': False, 'cellInPotentialWorkCells': True, 'h

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH` first: another commit may already do it.
