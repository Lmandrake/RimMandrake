## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_1.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_1.3)
Verdict: CONFIRMED MINOR. HoseFuzz.cs:138 a refused Lay returns null (success) and Report (44-46) asserts only Failures==0, so 0 laid hoses passes

### GPT finding (verbatim)
### FE_cs_selftests_1.3 — Hose fuzzing can pass with zero successfully laid hoses
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs:138 (`RunHose`), :45 (`Report`)
- evidence:
  ```csharp
  if (!lay.Ok) { if (BendCollect) lock (RefuseWhy) { RefuseWhy.TryGetValue(mode + " " + lay.Reason, out int rn); RefuseWhy[mode + " " + lay.Reason] = rn + 1; } return null; }     // an install the route check passed but the lay refused: the reel retracts with the reason (CheckReplan), not a fault
  ```
- failure scenario: If a planner regression makes `Lay` refuse every generated route, each refusal returns success to the fuzz driver. All endpoint, length, wall-clearance, bend and joint assertions are skipped. `Report` checks only `t.Failures == 0`, so the family can report PASS with `0 laid`. Individual geometric refusals may be legitimate, but the family needs a deterministic success fixture or a minimum successful-coverage assertion to prevent this complete loss of exercise.
- confidence: high
