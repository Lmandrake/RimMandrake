## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.9)
Verdict: CONFIRMED MINOR. ProofReadout returns eng.DepthReadoutAt only (RM_NorthstarProofs.cs:293), skipping the sheet-water and natural-liquid fallbacks of RM_MouseoverDepth.DepthSuffix (74-99) -> proof measures a different readout than the player sees

### GPT finding (verbatim)
### FA_core_sim_3.9 — The readout proof bypasses part of the actual mouseover implementation
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/RM_NorthstarProofs.cs:293` (`ProofReadout`); `src/RimMandrake/FlowWorks/Source/RM_MouseoverDepth.cs:75–104` (`DepthSuffix`)
- evidence:
  ```csharp
  return "OK " + (eng.DepthReadoutAt(c) ?? "-");
  ```
- failure scenario: Hover an undug square carrying spilled sheet water. The mouseover can obtain its text through `Sheet.RM_MapComponent_Sheet.ReadoutAt`, but `ProofReadout` never calls that fallback and returns `OK -` when the excavation readout is absent. It also bypasses the natural-liquid fallback. A validation using this advertised bridge form of the player readout therefore measures different behavior.
- confidence: high
