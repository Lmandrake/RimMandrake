## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.5)
Verdict: CONFIRMED MINOR. flow_bignet_live.py:49,60,131 only inland is restored from state; dig/pulse use default --size while cells come from st["size"]

### GPT finding (verbatim)
### FF_validation_suite_2.5 — Resumed large-network phases use command-line size instead of saved size
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/flow_bignet_live.py:60,97-110,131-138` (`main`)
- evidence:
  ```python
  ox, oz, n = 12, 20, a.size
  far = (ox + n - 1, oz + n - 1)
  cells = st["size"] ** 2
  ```
- failure scenario: Run `site --size 100`, then run the documented `dig` and `pulse` phases without repeating `--size`. Those phases use the default 80: they dig an 80×80 plot and inspect its corner, while the result reports 10,000 cells from saved state. The proof can PASS without digging or wetting the intended far corner. Only `inland` is restored from state.
- confidence: high
