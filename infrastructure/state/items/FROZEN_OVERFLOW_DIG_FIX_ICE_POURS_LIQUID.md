## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.5)
Verdict: CONFIRMED MINOR. HandOverTakenCells pours state.Dl into a newly dug channel/sink with no Tier.Ice check (RM_MapComponent_Sheet.cs:833-862) -> frozen sheet becomes liquid canal water

### GPT finding (verbatim)
### FA_core_sim_4.5 — Digging beneath frozen overflow transfers ice as liquid
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:833–862 (`HandOverTakenCells`)
- evidence:
  ```csharp
  int got = Credit(k, state.Dl[k], state.Fluid[k]);
  if (got > 0)
  HandOver(state, k, got, false);
  ```
- failure scenario: Water freezes on undug ground, then the player excavates that square. At the next pulse, the handover recognizes the new channel and pours the frozen sheet’s decilitres into it without checking `Tier.Ice` or waiting for thawing. This bypasses the kernel’s explicit rule that frozen sheets do not return or flow.
  
  Outside-part dependency opened: `Source/RM_SheetMath.cs`, including its ice contract and pulse ordering. In-part `EnginePulse` calls this handover before the kernel’s freeze/thaw pass.
- confidence: high
