## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_3.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_3.1)
Verdict: CONFIRMED MINOR. Program.cs:118-122 AssertClose: Math.Abs(NaN-want)>eps is false, so NaN passes

### GPT finding (verbatim)
### FE_cs_selftests_3.1 — Shared numeric assertion silently accepts NaN
- severity: MINOR
- where: src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs:119-123 (`AssertClose`)
- evidence:
  ```csharp
  if (Math.Abs(got - want) > eps)
      throw new Exception($"{msg}: got {got}, want {want}");
  ```
- failure scenario: A production arithmetic regression returns `float.NaN` for an expected finite capacity, refill, heat, damage, or other numeric result. `Math.Abs(NaN) > eps` is false, so the assertion reports success. This affects every case relying on this shared helper unless another assertion independently rejects the result. Reject nonfinite values explicitly before comparing the difference.
- confidence: high
