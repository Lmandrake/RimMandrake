## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.8)
Verdict: CONFIRMED MINOR. drawbridge_proof.py:509 health "same" is hediff COUNT only; a worsened or swapped hediff passes

### GPT finding (verbatim)
### FF_validation_suite_1.8 — Underpass safety compares injury counts rather than unchanged health
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py:509` (`raise_spares_underpass`)
- evidence:
  ```python
      same = ctx["at"](u0) == ctx["at"](u1) and len(_health(u1) or []) == len(_health(u0) or [])
  ```
- failure scenario: Raising the bridge worsens an existing injury or replaces one hediff with another while leaving the pawn in place. The hediff count remains equal, so the row can pass even though its stated requirement—unchanged health—was violated.
- confidence: high
