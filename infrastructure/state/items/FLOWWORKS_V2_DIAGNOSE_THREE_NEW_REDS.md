# FLOWWORKS_V2_DIAGNOSE_THREE_NEW_REDS

Class: MOD (presumed, untraced). A PRIOR PASS NOW FAILS: validation_v2 was 61/0/0 twice on DLL 6699957b8; on the
FlowWorks DLL of ccf36a9af7 (deployed md5 9035a401, flowworks tier 11 mods, fresh TemperateForest quicktest) it reads
58 PASS / 3 FAIL. Result: `Transient/live_session/20261018T232207/validation_v2_result.json` (BENCH live 2026-10-19).

- S3_classification: W4 `{'limitless': True, 'cellCount': 40, ...}` (want limited cap 80.0) - a 40-cell body read LIMITLESS.
  Check whether W4's site touched the map edge on this map (SITE) before calling it the classifier.
- P3f_forced_entry_falls: control walk-in refused True; the forced flyer landed in the 2 m cell, "own descents 0 fall []",
  held True, lip 0/8 - it never fell.
- P4f_ladder_frees_forced: follows from P3f (forced pawn held False, own descents 0).

Bar: v2 61/0/0 again on the shipped DLL, or each red traced to SITE/HARNESS with the check that proves it.
