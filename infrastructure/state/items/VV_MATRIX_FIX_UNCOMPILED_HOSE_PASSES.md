## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_4.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_4.3)
Verdict: CONFIRMED MAJOR. ShippedMatrixProbe.cs:171-173 + 229 a probe built without VV_HOSE returns (-1,0,...): record shows 0 failures, explanation dropped, exit 0

### GPT finding (verbatim)
### FE_cs_selftests_4.3 — Uncompiled hose families produce success-shaped matrix records
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs:171–173,229` (`Rates`, `HoseFamily`)
- evidence:
  ```csharp
  return (-1, 0, "hose family not compiled into this probe (VV_HOSE undefined)");
  ```
  ```csharp
  if (fails > 0) examples.Add(text.Length > 2500 ? text.Substring(0, 2500) : text);
  ```
- failure scenario: Run `rates --families hose` or `trail` in a probe built without `VV_HOSE`. The record reports `attempted = completed = -1`, zero failures, zero exceptions, and no timeout. The explanation is discarded because `fails == 0`; the process returns zero. A consumer using the failure/exception fields sees no problem even though no checks ran. No external file is needed to establish this behavior.
- confidence: high
