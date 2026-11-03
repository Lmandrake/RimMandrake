## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.8, FE_cs_selftests_4.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.8)
Verdict: CONFIRMED MINOR. SplitOff share = fb.Population*piece/totalBefore with fb.Population already reduced by earlier pieces while totalBefore is fixed (RM_WaterBodyMendGame.cs:366-368, RM_WaterBodyMath.cs:434) -> unequal fish split by order

### GPT finding (verbatim)
### FA_core_sim_3.8 — Three-way water-body splits distribute fish using a shrinking numerator
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/RM_WaterBodyMendGame.cs:366–368` (`RM_WaterBodyView.SplitOff`)
- evidence:
  ```csharp
  float share = totalBefore > 0 ? fb.Population * piece.Count / totalBefore : 0f;
  nb.Population = share;
  fb.Population -= share;
  ```
- failure scenario: Drying an articulation cell divides a pond into three equal pieces. With remaining population 90 and nine remaining cells, the first three-cell piece receives 30; the next receives 20 because the numerator is now 60; the keeper retains 40. Equal pieces should receive 30 each. Total population survives, but fishing yields become dependent on split processing order. I reproduced the `30,20,40` calculation.
- confidence: high

### verification (FE_cs_selftests_4.5)
Verdict: CONFIRMED MINOR. MERGE with FA_core_sim_3.8: WaterBodyMendChecks.cs:307-323 test model mirrors the same shrinking-numerator split, so the test cannot catch it

### GPT finding (verbatim)
### FE_cs_selftests_4.5 — Three-way water-body splits distribute fish using a shrinking numerator
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/SelfTest/WaterBodyMendChecks.cs:307–323,519` (`Model.SplitOff`, split-population assertion)
- evidence:
  ```csharp
  float share = totalBefore > 0 ? fb.population * piece.Count / totalBefore : 0f;
  nb.population = share;
  fb.population -= share;
  ```
- failure scenario: Removing a connector divides a body into three equal 30-cell pieces with 45 fish remaining. Repeated calls with `totalBefore == 90` allocate 15 fish, then 10 fish, leaving 20 in the retained piece. Equal pieces therefore acquire different densities according to processing order. The existing assertion checks only the population sum and passes.

  Cross-file dependency **opened**: production `Source/RM_WaterBodyMath.cs:427–434` passes the same original total to every split; production `Source/RM_WaterBodyMendGame.cs:366–368` contains the same allocation formula. Thus the offline model reproduces the production error rather than detecting it.
- confidence: high
