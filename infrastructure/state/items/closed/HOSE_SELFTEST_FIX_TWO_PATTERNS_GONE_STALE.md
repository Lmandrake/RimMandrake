## spec
found-by: PUMP_SOURCE_FIX_REJECTS_PARTIAL_DRAW worker, 2026-11-02, full `selftest_flowworks_stock.py --no-build` on base 767b3ccdcc (no Hose/ file touched by that item). Log: D:\ClaudeWork\rimmandrake\scratch\pspd\stock_full.txt (lines 754, 1039).
Two FlowWorks C# selftest cases fail on call-site regexes against hose source:
- `GptA_hoses_off_never_retract_on_obstacles`: pattern `if \(RM_HoseSettings\.enabled && r\.layKey != null` not found.
- `A3 a recycled world (Reset + refill, CopyFrom) ...`: pattern `CordWorld w = LegacyFrame \? World\(\) : World\(LayWorldMaxAge\);\s*if \(r\.trail\.Count > 0 && ...` not found.
NEXT: decide per case whether the hose code regressed (behaviour lost) or the pattern is stale after a refactor (recent: 79f7ac98fa cross-shadow / FrameLegacy); fix the code or the pattern accordingly.
