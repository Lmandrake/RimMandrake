## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.9)
Verdict: CONFIRMED MINOR. extensions.py:746-753 tar lag asserts only 1<=wet<len(cells); no water control, normal-rate front also passes

### GPT finding (verbatim)
### FF_validation_suite_2.9 — Tar viscosity check accepts an ordinary water-speed partial front
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/extensions.py:746-753,763-779` (`_expect_tar_lag`, `tar_front_lags_water`)
- evidence:
  ```python
  wet = sum(1 for _, f in _state(t, cells) if (f or 0) >= 1)
  _expect(wet >= 1, "tar channel took no liquid at all: no front to compare (%d/%d wet)" % (wet, len(cells)))
  _expect(wet < len(cells), "tar wet front reached all %d cells: no viscosity lag" % len(cells))
  ```
- failure scenario: A regression makes tar advance at the ordinary one-cell-per-pulse rate. After this test’s six-pulse window, six wet cells in its ten-cell channel satisfy both assertions. No water control is measured. The supplied water-front check itself now expects gradual propagation, so “not all ten cells wet” no longer distinguishes viscosity from normal front pacing.
- confidence: high
