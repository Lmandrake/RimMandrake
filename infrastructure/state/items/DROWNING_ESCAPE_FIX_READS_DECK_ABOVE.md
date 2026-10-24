## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.6)
Verdict: CONFIRMED MINOR. ExitInReach reads StepDepthAt of the decked square at deck height (RM_PitFillEffects.cs:222,232) -> floor-band pawn under a bridge judged able to step to the undug bank

### GPT finding (verbatim)
### FC_pits_superdeep_1.6 — Drowning escape checks use the deck above a floor-band pawn
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_PitFillEffects.cs:220-238` (`RM_Drowning.ExitInReach`)
- evidence:
  ```csharp
  int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
  int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, n);
  if (RM_RelativeRulesMath.ExitInReach(fromD, toD, k, joined, w, h, RimMandrakeFlowWorksSettings.pitDrowningHeadFraction))
  ```
- failure scenario: A standing, non-swimming pawn is beneath a surface bridge in a four-metre pit, beside an undug bank, with water over its head. For example, disable deep swimming for a human pawn. `StepDepthAt` reads the current square at the deck’s surface height, zero, and the bank also reads zero. The drowning rule concludes that safe footing is one climbable step away, although the pawn is underneath a four-metre wall, and adds no drowning severity. Outside this part, opened `Source/Superdeep/RM_SuperdeepTrap.cs` to verify `StepDepthAt`, and `Source/RM_RelativeRulesMath.cs` to verify the exit predicate.
- confidence: high
