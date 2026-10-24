## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.4)
Verdict: CONFIRMED MINOR. Crop timer Stand[c] counts to CropKillPulses+1 and CropKilled fires only on ==, once per wet spell (RM_SheetMath.cs:548-551); a crop replanted under a standing sheet never drowns

### GPT finding (verbatim)
### FA_core_sim_4.4 — Crop drowning is a one-time puddle event rather than exposure of each crop
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:618–632 (`Effects`)
- evidence:
  ```csharp
  if (RM_SheetSettings.cropsDrownEnabled && rep.CropKilled.Count > 0)
  foreach (int k in rep.CropKilled)
  Plant plant = c.GetPlant(map);
  ```
- failure scenario: Keep a flooded growing area wet past the drowning delay. Its first crop dies, but crops replanted afterward can survive indefinitely while that sheet remains above the threshold. The kernel emits `CropKilled` only when the **cell’s** standing-water counter first reaches the delay, then saturates that counter. Conversely, a crop planted shortly before that crossing dies after much less than the configured exposure.
  
  Outside-part dependency opened: `Source/RM_SheetMath.cs`:538–553, which contains the cell counter and one-time equality test.
- confidence: high
