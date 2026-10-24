## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.4)
Verdict: CONFIRMED MINOR. ProofCensus (FluidIdentity.cs:79) and FlowMeter.Read (81-84) skip FillAt==0 cells so part-notch sheets count dry

### GPT finding (verbatim)
### FA_core_sim_2.4 — Wet-cell diagnostics report fractional sheets as dry

- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/RM_FluidIdentity.cs:79` (`ProofCensus`); `src/RimMandrake/FlowWorks/Source/MapControls/RM_FlowMeter.cs:81–87` (`Read`)
- evidence:
  ```csharp
  if (ex.ExcavatedDepthAt(c) == 0 || ex.FillAt(c) == 0) continue;
  ```
- failure scenario: Fill a basin with positive decilitre quantities below one notch per square. `ProofCensus` reports zero wet cells and zero unrecorded cells, even if such cells have missing identities. The flow meter similarly reports zero held levels and labels the channel dry. These reports can conceal the exact-mode failures they are meant to expose. Outside this part, opened `RM_MapComponent_Excavation.cs:1317–1330` confirms the truncating read.
- confidence: high
