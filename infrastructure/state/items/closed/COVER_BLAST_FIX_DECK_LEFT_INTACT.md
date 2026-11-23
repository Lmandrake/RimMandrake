## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.8)
Verdict: CONFIRMED MINOR. Cover killed by the blast drops only its own riders in DeSpawn (Building_PitCover.cs:152-163); the explosion postfix then finds no cover and the connected deck beyond the radius is not sprung

### GPT finding (verbatim)
### FC_pits_superdeep_1.8 — A blast that kills its first cover can leave the rest of the deck intact
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs:146-182,289-293` (`DeSpawn`, `RM_Patch_ExplosionBreaksPitCover.Postfix`)
- evidence:
  ```csharp
  Building_PitCover cover = RM_PitCoverUtility.CoverAt(map, c);
  if (cover == null)
  {
  ```
- failure scenario: A connected cover deck extends beyond an explosion’s radius. The explosion destroys the cover on an affected cell before the postfix runs. `DeSpawn` drops only that cell’s riders; it does not spring the connected deck. The postfix then finds no cover and returns, so covers and riders outside the blast remain standing. A weaker blast that leaves the first cover alive springs the whole deck, making the stronger blast produce less deck collapse.
- confidence: high
