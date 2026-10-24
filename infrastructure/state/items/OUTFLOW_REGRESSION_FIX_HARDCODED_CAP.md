## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.4)
Verdict: CONFIRMED MINOR. fw_pond_outflow_regression.py:14 hardcodes CAP=30; capacity is bed levels x volumePerTile (RM_LiquidStock.cs:342-350, ShallowNotches=2), drained is inflated and channel fills never asserted

### GPT finding (verbatim)
### FF_validation_suite_2.4 — Stale pond capacity makes the outflow regression pass without drainage
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/live_probes/fw_pond_outflow_regression.py:14,33,39-42`
- evidence:
  ```python
  CAP = 30.0
  drained = None if stock is None else round(CAP - stock, 2)
  if drained <= 6.5:
  ```
- failure scenario: Six ordinary shallow-water cells hold 12 notch units under the current yardstick, rather than the assumed 30. An untouched, completely undrained pond can therefore report `drained=18`, exceeding the success threshold. If its inlet remains a source, every scored condition passes even when the channel receives nothing. The recorded channel fills are never asserted.
  
  Cross-file confirmation opened: `Source/RM_Volume.cs:162,180` defines shallow beds as two notches; `Source/RM_MapComponent_Excavation.cs:1294-1313` uses that conversion for unrecorded natural-water beds.
- confidence: high
