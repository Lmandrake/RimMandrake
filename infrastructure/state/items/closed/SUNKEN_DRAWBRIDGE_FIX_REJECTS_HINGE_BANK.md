## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.3)
Verdict: CONFIRMED MINOR. Landing search starts on hinge anchors but passable rejects ClimbDepthAt>0 unless decked (RM_Drawbridges.cs:475-486) -> sunken drawbridge finds no bank

### GPT finding (verbatim)
### FC_pits_superdeep_1.3 — Sunken drawbridges reject their own hinge bank as a landing area
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs:470-493` (`Tip`)
- evidence:
  ```csharp
  return eng == null || eng.ClimbDepthAt(c) == 0 || RM_SpanUtility.DeckedAt(map, c);
  List<int> landings = RM_DrawbridgeMath.BankLandings(starts, neighbours, passable, free, RM_DrawbridgeMath.TipReach);
  ```
- failure scenario: Build a sunken drawbridge between dry ledges at depth four notches, over a deeper core. Raising it starts the landing search at its hinge anchors. Those squares have positive climb depth and contain anchors, not span decks, so `passable` rejects every start. No bank search occurs, even with ample free ledge space. Every rider becomes overflow and falls instead of being tipped safely onto the hinge bank.
- confidence: high
