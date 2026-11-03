## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.4)
Verdict: CONFIRMED MINOR. RM_SaltBreak.PotableReachable (RM_SaltBreak.cs:84-97) checks bottle/tank/terrain only, but JobGiver_RM_Drink also uses buckets/barrels and water items (RM_ThirstJobs.cs:38-41) -> brine break fires with fresh water in reach

### GPT finding (verbatim)
### FA_core_sim_3.4 — Salt-break eligibility overlooks reachable potable containers, water items and faucets
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Thirst/RM_SaltBreak.cs:84–96` (`PotableReachable`)
- evidence:
  ```csharp
  return RM_ThirstSettings.drinkFromTerrain
      && RM_ThirstUtility.TryFindDrinkCell(pawn, level, out _, out _, out _, out _, potable);
  ```
- failure scenario: A parched pawn in low mood has a reachable bucket of fresh water but no bottle, directly reachable tank, or terrain source. Normal drinking supports the bucket, yet `PotableReachable` checks only bottles, tanks and terrain. The pawn can qualify for the brine-drinking break and poison itself while potable water is available. Water items and accessible faucets supplied by inaccessible tanks have the same omission. The container/item paths are supplied here; I additionally opened `Thirst/Building_RM_PipeFaucet.cs` to confirm faucet selection.
- confidence: high
