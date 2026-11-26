## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.4)
Verdict: CONFIRMED MINOR. depth_rebuild_proofs.py:526 returns 0 regardless of FAIL rows (only 163 returns 2); gates reading exit code see success

### GPT finding (verbatim)
### FF_validation_suite_1.4 — The depth rebuild suite exits successfully after failed checks
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:526` (`main`)
- evidence:
  ```python
      return 0
  ```
- failure scenario: Run `--only p5` with an incorrect liquid total or a nonlevel surface. The JSON contains FAIL rows, but the process exits zero. A shell gate or parent runner using the exit status reports success despite the failed proof.
- confidence: high
