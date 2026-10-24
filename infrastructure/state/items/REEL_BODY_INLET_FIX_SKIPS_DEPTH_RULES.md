## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_1.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_1.6)
Verdict: CONFIRMED MINOR. Body coupling RawFind (HosePorts.cs:97-127) has no band check while free-end reach uses HoseBandMath.EndReaches (HosePorts.cs:200-207) -> reel on a pit lip couples to a tank on the floor below

### GPT finding (verbatim)
### FB_hose_gss_1.6 — Reel-body inlets bypass the depth restrictions enforced at free ends
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs:97–126 (`RawFind`),202–207 (`RawFindAt`)
- evidence:
  ```csharp
  int pick = HosePortRule.Pick(rect, cands, out side, out contact);
  int endBand = RM_HoseBands.BandAt(map, end);
  if (!HoseBandMath.EndReaches(endBand, RM_HoseBands.BandAt(map, c))) continue;
  ```
- failure scenario: A reel stands on a pit’s lip beside a tank or pipe on the floor below. `RawFind` accepts the shared horizontal edge without comparing bands or requiring a ladder/ramp, giving the hose a working inlet across the sheer wall. Putting the hose’s free end at the equivalent position correctly refuses that connection. Confirmed that `r.Port()` directly supplies the hydraulic inlet in `Source/Machinery/RM_LiquidNet.cs:1017–1025`—outside this part, opened.
- confidence: high
