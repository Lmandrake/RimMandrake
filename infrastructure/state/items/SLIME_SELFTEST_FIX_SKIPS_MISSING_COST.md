## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_3.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_3.2)
Verdict: CONFIRMED MINOR. SlimeChecks.cs:119-124 non-greedy Singleline match: a missing pathCost either drops the case or reads the next def's cost

### GPT finding (verbatim)
### FE_cs_selftests_3.2 — Slime path-cost check silently skips a missing authored field
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/SlimeChecks.cs:119-124 (`Slime_shipped_data_and_wiring`)
- evidence:
  ```csharp
  foreach (Match t in Regex.Matches(terr, @"<defName>RM_Fill_Slime\w+_(Trace|Half|Brim|Superdeep)</defName>.*?<pathCost>(\d+)</pathCost>",
      RegexOptions.Singleline))
  {
  ```
- failure scenario: Remove `<pathCost>450</pathCost>` from the final `RM_Fill_SlimeYellow_Superdeep` terrain. Its cost assertion disappears instead of failing, allowing the terrain to inherit a cost without verifying the required 450. An in-memory mutation of the shipped XML reduced matches from 16 to 15 with zero failing comparisons. Require the expected colour/tier set and inspect each terrain’s own field. Outside-part dependency opened: `Defs/Canals/TerrainDefs/FlowWorks_SlimeTerrain.xml`.
- confidence: high
