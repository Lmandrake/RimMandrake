## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.2)
Verdict: CONFIRMED MINOR. Sheet water on undug soil: RM_Swim.Tick skips the cell (RM_Swim.cs:542-544) and RM_PitFillEffects adds drowning but sends DrownMessage only when swimming is off (RM_PitFillEffects.cs:59-63) -> silent drowning with swimming on

### GPT finding (verbatim)
### FA_core_sim_4.2 — Overflow can drown a pawn without sending the drowning warning
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs`:542–545 (`RM_Swim.Tick`)
- evidence:
  ```csharp
  if (exh == null && !dug && (t == null || !t.IsWater))
  {
      continue;   // the common case: dry ground, never swam
  ```
- failure scenario: A downed colonist lies in a sufficiently deep sheet of spilled water on ordinary soil. The overlay deliberately leaves the soil terrain unchanged, so this branch skips the pawn. The external `RM_PitFillEffects.Tick` does apply sheet drowning, but sends its warning only when deep swimming is **off**. With the shipped swimming default enabled, the pawn accumulates drowning without the promised “is drowning” message. Even an existing exhaustion hediff does not fix this: this swimming pass measures natural/dug water rather than sheet depth.
  
  Outside-part dependencies opened: `Source/RM_PitFillEffects.cs`:51–67 and `Source/RM_MapComponent_Excavation.cs`:2665–2681.
- confidence: high
