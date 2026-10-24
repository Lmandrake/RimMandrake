## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.2)
Verdict: CONFIRMED MAJOR. sink candidate filter uses FillAt (whole notches; Excavation.cs:1317) so part-notch water in partGrid (1335) is never drained

### GPT finding (verbatim)
### FA_core_sim_2.2 — An unlimited sink cannot remove fractional water

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/MapControls/RM_FlowTaps.cs:165–173` (`Building_RM_FlowSink.FlowPulse`)
- evidence:
  ```csharp
  int f = ex.FillAt(c);
  if (f > 0 && (filter == null || (ex.FluidAt(c) ?? ex.ActiveFluid) == filter))
  ```
- failure scenario: An unlimited sink stands beside a channel containing a sheet less than 0.5 m deep in every reachable square. Every `FillAt` returns zero, so the sink drains nothing indefinitely despite visible water. It also leaves fractional leftovers after draining larger amounts. Outside this part, opened `RM_MapComponent_Excavation.cs:1317–1330,2330–2360` confirms that these APIs read and remove whole notches; the separate decilitre API handles sheets.
- confidence: high
