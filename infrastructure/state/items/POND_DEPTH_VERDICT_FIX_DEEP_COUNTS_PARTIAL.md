## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.7)
Verdict: CONFIRMED MINOR. liquid_checks.py:375 counts deep (TerrainDefOf.WaterDeep, RM_PromotionProofs.cs:28) as a part-depth stage, so all-original water passes

### GPT finding (verbatim)
### FF_validation_suite_2.7 — Pond-shallowing predicate accepts an unchanged deep-water appearance
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/liquid_checks.py:374-377` (`pond_depth_verdict`)
- evidence:
  ```python
  if last.get("s", 0) >= 1 and c.get("chest", 0) + c.get("shallow", 0) + c.get("thin", 0) + c.get("deep", 0) == 0:
      return "FAIL", "MOD", dict(det, why="the surface fell but no square shows a part-depth stage")
  return "PASS", "MOD", det
  ```
- failure scenario: A body’s reported surface falls while a terrain-update regression leaves every square drawn as deep water. A final census containing only `deep:100` passes this condition. The predicate therefore does not establish its stated requirement that chest/shallow/thin stages appear instead of only full original water.
- confidence: high
