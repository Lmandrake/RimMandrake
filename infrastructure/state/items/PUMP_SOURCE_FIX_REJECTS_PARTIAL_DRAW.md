## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.5)
Verdict: CONFIRMED MINOR. PumpNext tank predicate asks FillPlan for a full cycle (Pump.cs:299; FillPlan null when room<units, LiquidNet.cs:435-442) so the partial-draw code never runs for a nearly-full tank; last part-level never pumped

### GPT finding (verbatim)
### FA_core_sim_1.5 — Pump source selection rejects affordable partial draws before reaching partial-draw code
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs`:296–299, 355–370 (`TryDraw`)
- evidence:
  ```csharp
  i => LiquidFor(sources[i].fluid) is LiquidDef lq && Machinery.RM_LiquidNet.FillPlan(this, lq, units) != null, cycle,
  ```
- failure scenario: With no Outflow ends, a source contains 900 dL and the connected tank has exactly 900 dL free. The transfer is affordable, but `PumpNext` demands a fill plan for the full 10,000 dL cycle before selecting the source. Consequently, the later code that reduces the draw to 900 dL is unreachable. The pump reports nothing to draw and strands the liquid. The same gate affects natural-body remainders. Outside this part, I opened `Source/RM_PumpMath.cs` to confirm the partial-draw contract.
- confidence: high
