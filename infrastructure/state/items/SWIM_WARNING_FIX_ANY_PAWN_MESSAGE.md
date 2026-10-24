## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.5)
Verdict: CONFIRMED MINOR. depth_rebuild_proofs.py:233,243 any new swim/drown message from any pawn counts and warned<=under accepts same-sample

### GPT finding (verbatim)
### FF_validation_suite_1.5 — The swimming warning check accepts the drowning announcement as advance warning
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:233–244` (`main`, armoured swimmer poll)
- evidence:
  ```python
                      hit = [t for t in texts if t not in msgs0 and any(w in t.lower() for w in ("swim", "tired", "drown", "shore", "exhaust"))]
                  row("SWIM_armour_warned_before_under", "PASS" if warned and (under_at is None or warned[0] <= under_at) else
  ```
- failure scenario: The early tiring warning stops working, but the pawn still receives “exhausted and going under” or “is drowning.” That message matches the filter during the same sample that first observes submersion. Because equality is accepted, `SWIM_armour_warned_before_under` passes. Messages are also not restricted to the tested pawn. Dependency opened: `Source/Swimming/RM_Swim.cs`, confirming separate tiring, exhaustion, and drowning messages.
- confidence: high
