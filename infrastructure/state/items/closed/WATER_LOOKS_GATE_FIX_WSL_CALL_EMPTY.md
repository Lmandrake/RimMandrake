## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a). Class: HARNESS.
`python.exe src/RimMandrake/FlowWorks/northstar/water_looks_proof.py <out> --fresh-map`, run from a `git archive` export on
D: (`D:\ClaudeWork\rimmandrake\scratch\bridge_run_1b`, as BRIDGE_RUN_1.md §0.2 prescribes), writes all 9 rows
UNMEASURED/HARNESS "offline gate red: ['gate:no GATE_JSON (exit 2)']" (`Transient/bridge_run_1_20261023/water_looks.json`).
The same gate run directly in WSL (`python3 .../water_looks_proof.py --offline-gate` in that export) is green
(`GATE_JSON {"red": [] ...}`), and the live run with `--skip-offline` is 9/9 PASS (`water_looks2.json`).
So `offline_gate_from_windows()` (wsl.exe python3 PH._posix(abspath)) fails from a D: export (exit 2 = python could not
open the path, presumed: check what PH._posix returns for `D:\...` and the wsl.exe cwd). One other northstar script
shares the helper (grep offline_gate_from_windows). Done when the in-script gate reads green from a D: export.
