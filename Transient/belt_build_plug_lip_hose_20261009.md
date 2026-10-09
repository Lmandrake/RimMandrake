# belt build: hose bend / pit lip / vault seal plug 2026-10-09

## GIMMESOMESLACK_HOSE_BEND_TRACE_1
Verdict: NOT a MinBendRadius metric bug (metric is vertex seg/turn, sound; 10-04 runs read 1.25-5.0). The 0.19 radii in
foundry_gss_proof_20261006 predate the lead-out fix (b59ebcfec, 22:07 10-06; old U-turn blend bent to ~0.02). Today, scenes with
the matrix maxLength ceil(L*1.3) are REFUSED offline ('route too long': west nozzle, end east = lead-out + U-turn needs ~L+10),
and when laid (hose L+10) min bend = 1.26 >= 1.14. Fix: design_spec.hose_max_length = ceil(L*1.3)+14 (PROVISIONAL) + offline
HoseSelfTest.MatrixScenes (laid bar + can-fail). Corner/water scenes not reproduced offline; rerun H0-H8 when game is up.

## FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1
(pending)

## GELATINOUSSLIME_VAULT_SEAL_PLUG_1
(pending)
