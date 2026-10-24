## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.6)
Verdict: CONFIRMED MAJOR. LsMaxBands=8 clamps depth (kernel 1559) while dig ceiling is 40 (RM_DigDepthMath.cs:41); water in bands >8 uncounted -> laid!=volume early return, region never levels (non-exact mode)

### GPT finding (verbatim)
### FA_core_sim_2.6 — Whole-notch levelling silently stops working below eight bands

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs:1415,1559,1651–1653` (`LevelSetWetRegions`, `SolveRegion`)
- evidence:
  ```csharp
  private const int LsMaxBands = 8;
  ```
- failure scenario: Turn exact levelling off while retaining surface levelling and the level-set solver. Three adjacent depth-ten squares holding `[3,2,1]` levels cannot exchange through the neighbour pass because each adjacent surface difference is one. The level-set solver represents only bands 1–8, counts only part of that water, and silently returns at `laid != volume`. The one-metre surface difference remains indefinitely. Depth ten is within this part’s supported digging range.
- confidence: high
