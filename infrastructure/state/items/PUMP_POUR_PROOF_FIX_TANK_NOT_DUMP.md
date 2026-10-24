## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.3)
Verdict: CONFIRMED MINOR. extensions.py:2811-2816 only flips the pump to pour; Building_LiquidPump.cs:427 pours Dump tanks only when tankModesEnabled (default true), new tank is not Dump -> false FAIL

### GPT finding (verbatim)
### FF_validation_suite_2.3 — Pump return test never marks its tank Dump
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/extensions.py:2811-2816` (`liquid_pump`, `pump_pours_back`)
- evidence:
  ```python
  lv0 = level()
  rd("pour")
  t.wait_ticks(600)
  ```
- failure scenario: The preceding setup builds a new tank and pumps water into it, leaving its default Store mode unchanged. Switching only the pump to Pour cannot drain that tank with shipped tank modes enabled. Correct production behavior therefore fails `pump_pours_back`.
  
  Cross-file confirmation opened: `Source/LiquidTypes/Building_LiquidPump.cs:425-427` filters Pour providers to Dump tanks; `Source/RM_NorthstarProofs.cs:621-627` changes only `pump.pourMode`. The supplied propane test correctly sets its tank to Dump.
- confidence: high
