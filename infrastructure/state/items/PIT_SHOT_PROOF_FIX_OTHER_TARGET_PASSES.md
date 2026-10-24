## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.6)
Verdict: CONFIRMED MINOR. depth_rebuild_proofs.py:419-420 PASS when picked!=eb, another hostile picked also passes

### GPT finding (verbatim)
### FF_validation_suite_1.6 — Choosing another attack target is treated as proof that the intended target is unhittable
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:418–421` (`P7_shoot_between_7m_pits_refused`)
- evidence:
  ```python
                  row("P7_shoot_between_7m_pits_refused", "UNMEASURED" if not (allowed and sa and eb and at2.get("success") is True)
                      else ("PASS" if picked(at2) != eb.replace("Thing_", "") else "FAIL"), {"shooter": sa, "target": eb, "probe": t2[:700],
  ```
- failure scenario: Shooting between deep pits regresses and `eb` becomes a legal target, but the AI selects another hostile—for example, the earlier trench-control target still present in this scene. The row passes because `eb` was not selected. The successful control establishes that target selection works; it does not establish why this particular target lost selection.
- confidence: high
