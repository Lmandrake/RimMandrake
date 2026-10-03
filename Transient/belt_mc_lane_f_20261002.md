# BELT MC lane F 2026-10-02

Helper: FOUNDRY lane F. Tasks: (1) ring/aerial determinism defect offline (2) live session (3) hose screenshots.

## Progress
- skeleton written 19:30
- 19:34 step1: hypothesis = tree ExtraCost not in CorridorHash (trees planted LAST, after cords cached). Wrote northstar_matrix/det_export.py + SelfTest/DeterminismChecks.cs (staged replay). Running red-first.
- 19:37 step1 ROOT CAUSE (ring): CordBuilder cache reused a piece whose key (endpoints+chain+live+lay) matched but LayEdge's 'parallel' input did not: heater hooks ring -> 2 parallel J-J halves; lamp splits one; the other half keeps key, reused with parallel route. Red offline 4/64 (exactly F12-F15, edge J27,19-J32,19) -> fix LaySig (parallel+knots) in reuse test -> 64/64; SelfTest 393/393, matrix selftest 50/50 (DS6+DS6n). Aerial (not reproduced offline): RimSage Section.TryUpdate regenerates only on-screen sections -> off-screen changes never rebuilt the comp; fix = TryUpdate prefix marks StaleOffscreen, MapComponentUpdate rebuilds once (to be proven live). Built.
- 19:38 step2: killed RimWorld PID 37864
- 19:44 step2: deployed (4 files), tier messyconduit, Steam launch -> Bridge token in 15s, PID 38348. Running validation.py --live --fresh-map
- 19:47 validation.py --live --fresh-map: 40 PASS / 3 UNBUILT / 3 UNCOVERED, 0 FAIL. Running validation_hose.py --live
- 19:50 hose --live: 5 PASS / 7 FAIL; root cause MOD: CompHoseReel.TryLay used comp?.CheckInstall(..) ?? "no hose component" -- CheckInstall returns null on success, so every valid lay was refused (H2-H9 cascade). Fixed + rebuilt; cycling game.
- 19:54 validation.py rerun after DLL fix: 39 PASS + Z_log_budget FAIL = geyser in clear rect (HARNESS) -> excluded like run_live.py. Running hose --live.
- 19:56 hose --live: 12/12 PASS. Save-load next (MC_laneF_hose, then MC_laneF_cords).
- 19:57 save-load: hose 3/3 PASS, cords M4 3/3 PASS. Starting full matrix run (background, ~26 min), progress -> Transient/mc_matrix_live_20261002/laneF_progress.txt
- 19:58 matrix running; hose shots from take_screenshot show reels but NO hose (per-frame DrawMesh not captured) -> will use system_screenshot after matrix, on save MC_laneF_hose
- 20:24 MATRIX full live: 100 PASS / 9 UNBUILT (hose, placer cannot place hoses), D2_fresh_builder_same PASS on all 19 boards (ring B12-B15 16/16,21/21,16/16,16/16 same; aerial B16 36/36 same, 0 missing; offscreenRebuilds counter 154 by B16). Result northstar/matrix_live_20261002T202406.json
- 20:25 step3 screenshots: system_screenshot on save MC_laneF_hose, same camera: hose_A_h1plump_h2flat.png / hose_B_h1flat_h2plump.png (state reads in hose_AB_state_reads.json: Plump 5.41x wire, Flat 4.42x). take_screenshot frames hose_01/02 show reels but NOT the per-frame hose.
- 20:27 removal checks on flowworks tier: hose H11 PASS, cords M9 PASS. modcheck record (matrix_live_20261002T202406.json): REFUSED at de203d7634ba -- 111 PASS, 0 FAIL, 9 UNBUILT hose bars (refusal is the UNBUILT rule, not a failure). Game UP on flowworks tier. DONE.
