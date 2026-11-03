## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.5)
Verdict: CONFIRMED MINOR. JobDriver tank drink FailOn checks only QualityOf.HasValue (RM_ThirstJobs.cs:245) and finish drinks tank.storedLiquid without MayDrink re-check (253-259); a tank refilled with brine mid-job is drunk

### GPT finding (verbatim)
### FA_core_sim_3.5 — A tank drink can silently change into a forbidden liquid during the job
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstJobs.cs:245,254–259` (`JobDriver_RM_DrinkFromTank`)
- evidence:
  ```csharp
  LiquidDef liquid = tank?.storedLiquid;
  if (liquid == null || !tank.TryRemoveLiquid(RM_Volume.Units(RM_ThirstMath.TankDrinkLitres)))
  ```
- failure scenario: A pawn selects a fresh-water tank. While it walks there or waits, the tank empties and is refilled with brine or toxic water. The job’s continuing guard checks only whether the liquid has a thirst quality; completion drinks the tank’s current contents without rechecking `MayDrink`. An ordinary, non-desperate pawn can consequently drink a prohibited liquid outside the salt break.
- confidence: high
