## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.7)
Verdict: CONFIRMED MINOR. Pick: alt stays -1 when a candidate is a cut, so MarkCuts (O(wet), BedMath.cs:367) re-runs per candidate -> O(n^2) on long thin bodies

### GPT finding (verbatim)
### FA_core_sim_2.7 — Recession can rerun its entire articulation scan for every rejected candidate

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_BedMath.cs:308–325` (`RM_RecessionSet.Pick`)
- evidence:
  ```csharp
  if (alt < 0)
  {
      MarkCuts();
  ```
- failure scenario: A long, one-square-wide wet body has channel-feeding cells at both ends. The endpoints are safe removal candidates but rank behind the non-feeding interior. Every interior square is an articulation point. Because rejecting one leaves `alt == -1`, the loop reruns the full Tarjan scan for every interior candidate. One recession pick becomes quadratic in body size, causing substantial tick stalls on large or winding bodies.
- confidence: high
