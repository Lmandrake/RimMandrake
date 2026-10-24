## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.1)
Verdict: CONFIRMED MAJOR. NearestFooting BFS (RM_Swim.cs:706-717) tests Walkable/Standable only, never whether the step between depths is climbable -> swimmer heads for an unreachable ledge

### GPT finding (verbatim)
### FA_core_sim_4.1 — Tired swimmers can repeatedly choose an unreachable shore
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs`:707–717 (`RM_Swim.NearestFooting`)
- evidence:
  ```csharp
  if (!n.InBounds(map) || seen.Contains(n) || !n.Walkable(map))
  if (!RM_RelativeRulesMath.HeadUnder(w, h, false, frac) && n.Standable(map))
  return n;
  ```
- failure scenario: A swimmer in a flooded pit has a dry ledge immediately beside it that is too high to climb, plus a reachable ramp farther away. The search accepts the ledge because it checks cell walkability without checking whether the pawn can traverse the cliff between cells. `HeadForShore` orders an impossible `Goto`; subsequent checks can select the same ledge again while the pawn exhausts and drowns.
- confidence: high
