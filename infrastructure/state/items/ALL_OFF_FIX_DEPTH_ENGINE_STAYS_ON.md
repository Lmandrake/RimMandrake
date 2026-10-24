## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.2)
Verdict: CONFIRMED MINOR. extensions.py:352-358 _setting_in writes depthEngineEnabled=False without depthEngineLiveForTests (only _setting:334-338 does); RimMandrakeFlowWorksMod.cs:49 engine stays on, all_off fixture not all off

### GPT finding (verbatim)
### FF_validation_suite_2.2 — “All off” bypasses the reload-sensitive engine-switch handling
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/extensions.py:352-359,1267-1268` (`_setting_in`, `all_off_still_digs`)
- evidence:
  ```python
  for cls, f, off in REG.all_off():
      stack.enter_context(_setting_in(t, cls, f, off))
  ```
- failure scenario: On a normal game loaded with the depth engine enabled, `_setting_in()` writes `depthEngineEnabled=False` without enabling `depthEngineLiveForTests`. The effective engine remains enabled. Thus the test does not exercise its advertised all-off runtime configuration and can report a mod failure when the still-running engine feeds its channel. The specialized `_setting()` already handles this distinction.
  
  Cross-file confirmation opened: `northstar/settings_registry.py:65-67` excludes internal switches from `all_off()`; `Source/RimMandrakeFlowWorksMod.cs:43-49` latches the effective engine setting until reload unless the internal test override is enabled.
- confidence: high
