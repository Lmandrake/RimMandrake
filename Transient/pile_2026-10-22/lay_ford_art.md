# lay_ford_art — BENCH helper, 2026-10-22 — DONE (offline); ready for a live check

| item | state | notes |
|---|---|---|
| HOSE_TANK_LAY_FIX_ENDS_ON_LID | built 38d29be950; owes A2 L2 | root cause: ApproachIfOnPort read "solid" off the per-tick CordWorld snapshot, so a tank built while paused read walkable, the aim fell through and the end lay on the lid. Now reads the live path grid; no free square in front of the port -> refused naming it (HosePortRule.AimAtSolidPort). stock 840/840, hose 384/384 incl. 256 reel joints. DLL rebuilt, NOT deployed |
| FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE | built c22c6bb5bd; owes A2 L2 | tint (128,124,112) -> white. Offline render looked at: lay_ford_art/ford_tint_compare.png (pinned; assumes 10 cells per texture tile). NOT deployed |
| ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING | done 217dab3d98 + 031b4299a2 | install --by-card/--per-ruling/--why + `art.py correct-provenance`; 20 provenance_fix events (tanks fb34c9bc2d, ladder 41c06f6a2b, reel 694e9d2ddc/cfcdb0cbaf, reinstall edf89e6030/5bed576967, and 6199b2ed13 with the same defect). delegation_policy's `--reason "delegated: art …"` (refused by mechanical_refusal) corrected to --why |

## Filed
- CARD_PICKS_CORRECT_OLDER_ONES_STILL_SAID — 110 more owner keeps carry "by card" in said
- HOSE_WORLD_SNAPSHOT_FIX_STALE_WHILE_PAUSED — World() per-tick cache blind to builds while paused
- ARTLEDGER_SELFTEST_DIAGNOSE_CROWD_CRASH — selftest_art_ledger_fixes crashed once in a batch, green on re-run

## Code review
All touched files DIRTY (no full-file review done): CompHoseReel.cs, HoseMath.cs, HoseSelfTest.cs, RM_FordStones.xml, artledger.py, art.py, selftest_art_provenance.py.
