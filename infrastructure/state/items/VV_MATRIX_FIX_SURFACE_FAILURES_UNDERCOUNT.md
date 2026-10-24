## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_4.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_4.4)
Verdict: CONFIRMED MINOR. ShippedMatrixProbe.cs:165 failures=max(a,b,c), a lower bound exported as a count

### GPT finding (verbatim)
### FE_cs_selftests_4.4 — Surface-family “failures” is a lower bound presented as a count
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs:165` (`Rates`)
- evidence:
  ```csharp
  failures = Math.Max(a, Math.Max(b, c));   // lower bound of failing scenes; the per-check split is in the example
  ```
- failure scenario: Two scenes fail settling and two different scenes fail conservation. Four scenes failed, but the JSON and console report two failures out of 1,000. The implementation acknowledges the lower bound internally, while the exported field remains simply `failures`. This understates rates used to compare configurations and contradicts the probe’s stated uncapped failure-count contract. The original report retained in `examples` does not make the aggregate count exact.
- confidence: high
