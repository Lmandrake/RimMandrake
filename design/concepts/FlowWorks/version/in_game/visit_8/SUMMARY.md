# FlowWorks 0.1.0 — in-game acceptance, visit 8

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_EIGHT, ArchBig on Archmagi.
Started 2026-11-23 2:28 AM PST (bound 5:28 AM).

Why this visit: `rerun_relation.py` reads 30 of 31 checks touched by the C# since their rows (stepped pit relief
52182cca96, floor depth ladder 5c870d5a36, and others).

## Progress
- 02:28 bridge taken (ArchBig); skeleton written.
- 02:36-02:50 13 checks run: 12 PASS, sc_garden FAIL (GARDEN_filter_keeps_its_rate, 14 batches, window 32-33).
- 02:52-03:12 sc_garden diagnosed: converterRateMultiplier 4.1 -> 1 mid-window, by an outside `wrapup.py restore`
  replaying the live run's own setting debt (probe_conv_mult.py reproduced it bare). Class HARNESS (the pipeline's
  restore, not the mod). Fixed in wrapup.restore (RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT).
