## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.6)
Verdict: CONFIRMED MINOR. WorkGiver_FillBottleFromTank has no RM_BottleStock.Deficit gate; only the terrain WorkGiver_FillBottle.cs:40 checks it -> tanks drained into every empty bottle

### GPT finding (verbatim)
### FA_core_sim_1.6 — Automatic filling from tanks ignores the colony bottle stock target
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/LiquidTypes/WorkGiver_FillBottleFromTank.cs`:24–42, 50–67 (`HasJobOnThing`, `JobOnThing`)
- evidence:
  ```csharp
  if (RM_LiquidTankUtility.TryFindTankToDrain(pawn, t, ext.size, out tank, out liquid, out refusal, forced))
  {
      return true;
  ```
- failure scenario: The colony already has its configured stock of potable bottles. Leave empty bottles beside a stocked Store, Empty, or Dump tank. This work giver continues assigning automatic filling jobs until the empty containers or tank stock run out. Its terrain-source sibling explicitly checks `RM_BottleStock.Deficit`; this path never does. Outside this part, I opened `Source/Thirst/RM_ThirstContainers.cs` to confirm the stock target applies to automatic bottle filling generally.
- confidence: high
