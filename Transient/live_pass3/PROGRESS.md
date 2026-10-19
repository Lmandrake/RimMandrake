# FlowWorks live pass 3 — 2026-10-19 (BENCH live driver)
| step | state | note |
|---|---|---|
| bridge take | DONE | BENCH |
| deploy | DONE | HEAD export cc811a8178; FlowWorks DLL 3712ea5fe3, deployed .srchash md5 == committed (c6cda008) |
| tier flowworks | DONE | 11 active; launch token 25 s, first-exception gate clean |
| B5 dug ice | DONE PASS | run 1 FAIL "never thawed" = HARNESS (12k fixed thaw ticks, ~2 melts expected; 7 ThinIce left at 26 C); run 2 UNMEASURED = stale ice from run 1 (clear_zone keeps temp terrain); run 3 PASS: froze 10000 ticks at -17.9 C, 10->8 ice 5500 ticks after the cold, litres 10000 unchanged. Evidence Transient/live_session/pass3_20261019T0346_b5s/session.json |
| B4 rescue/fish + B7 | NOT RUN | owner wrap-up order |
| verify | DONE | DUG_ICE_DIAGNOSE_COLD_FEET_WARM_WATER run-1 pass |
| restore FULL, game down, release | DONE | 542 md5 a40bedf5, game DOWN (killed PID 46724), bridge FREE |
