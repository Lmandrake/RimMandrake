## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.3)
Verdict: CONFIRMED MINOR. RM_Dehydration has no severity comp; only Need_RM_Thirst.NeedInterval moves it (Need_RM_Thirst.cs:46-57); when the need is removed by Reapply/ShouldHaveNeed the hediff stays forever

### GPT finding (verbatim)
### FA_core_sim_3.3 — Disabling thirst leaves existing dehydration permanently attached
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstProvider.cs:85–94` (`Reapply`); `src/RimMandrake/FlowWorks/Source/Thirst/Need_RM_Thirst.cs:46–56` (`NeedInterval`)
- evidence:
  ```csharp
  if (!RM_ThirstProvider.OursLive || IsFrozen)
  {
      return;
  ```
- failure scenario: A pawn has severe dehydration when FlowWorks thirst is disabled, animal thirst is disabled for that pawn, or the save changes to the DBH provider. The need stops updating or is removed, but its dehydration hediff remains. Drinking can no longer trigger the negative severity updates, leaving the pawn’s consciousness and movement penalties indefinitely. Outside this part, I opened `Defs/Thirst/RM_Dehydration.xml`: it has no independent recovery comp. I also checked the settings-change caller in `RimMandrakeFlowWorksMod.cs`; it only reapplies needs.
- confidence: high
