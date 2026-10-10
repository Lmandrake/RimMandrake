# Selftest leftovers 2026-10-10

1. Greentide churnmud row retired, acceptance_map GREEN, landed bd70c2696.
2. hugethings 16/16 PASS, landed bd70c2696 (art baea6351b on origin).
3. FlowWorks: origin already has the LiquidLooks BCL fix and the DLL (f70d2283b); nothing to land. Tree DLL rebuilt to match origin source.
4. ledger_lint: still FAIL, clone 49 behind origin; clears on pull, not possible with the dirty tree.
5. utinnipatches_dump: capture 08:23Z is from BENCH live game; BENCH commit 15c0b74c9 (on origin) renamed megatardi to thuffor. Stale clone; PASS against an origin/main export.
Final run_selftests: PASS 287/356, FAIL 2 (ledger_lint, utinnipatches_dump: both stale-clone).
