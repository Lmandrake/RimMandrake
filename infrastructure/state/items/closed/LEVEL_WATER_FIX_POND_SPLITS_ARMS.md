## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.6)
Verdict: CONFIRMED MINOR. level_water.py:580-588 a touched pond adds its surface but the walk never continues through it, so arms joined via a pond are scored apart

### GPT finding (verbatim)
### FF_validation_suite_2.6 — Surface-gap reference does not connect canal arms through their pond
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/level_water.py:578-592` (`surface_gaps`)
- evidence:
  ```python
  touched.add(bid)
  for bid in sorted(touched):
      surfs.append(psurf[bid])
  ```
- failure scenario: The walk records a touched pond’s surface but never traverses that pond to its other wet mouths. Two canal arms connected through one pond are measured as separate bodies. For example, arm surfaces of −0.2575 m and −0.2425 m around a pond at −0.2500 m each produce a reported 0.0075 m gap, although their connected body spans 0.015 m and violates the 1 cm bar. This weakens the Python diagnostic/reference; equivalence of the production diagnostic was not assumed.
- confidence: high
