## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.10). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.10)
Verdict: CONFIRMED MINOR. lake_floor_stage.py:114 builds set(cells) inside a 9-neighbour lambda per candidate: O(9N^2) on a big lake

### GPT finding (verbatim)
### FF_validation_suite_2.10 — Lake-center selection repeatedly rebuilds the entire lake set
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/northstar/lake_floor_stage.py:114` (`main`)
- evidence:
  ```python
  c0 = max(cells, key=lambda c: sum((c[0] + dx, c[1] + dz) in set(cells) for dx in (-1, 0, 1) for dz in (-1, 0, 1)))
  ```
- failure scenario: For a lake containing N cells, this constructs an N-element set for each of nine neighbor checks for each candidate: approximately 9N² insertions. A 10,000-cell lake entails roughly 900 million insertions before the per-cell bridge measurements even begin, making natural-lake staging unnecessarily slow. Constructing the membership set once removes this cost.
- confidence: high
