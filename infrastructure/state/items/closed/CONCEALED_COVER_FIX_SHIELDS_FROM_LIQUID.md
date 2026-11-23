## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.5)
Verdict: CONFIRMED MAJOR. UnderDeck = InFloorBand only (RM_SuspensionPatches.cs:313-316); a pawn RM_PitCoverBeneath.IsBeneath a solid cover gets SplashShare 0 (320-326) -> immune to toxic/fill around it

### GPT finding (verbatim)
### FC_pits_superdeep_1.5 — Pawns beneath concealed covers are shielded from the liquid surrounding them
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs:313-326` (`UnderDeck`, `SplashShare`), `src/RimMandrake/FlowWorks/Source/RM_PitFillEffects.cs:80-83` (`Tick`)
- evidence:
  ```csharp
  return RM_SuspensionUnderpass.InFloorBand(p);
  return deck.Grated ? RM_SuspensionMath.GrateSplashChance(1f) : 0f;
  float share = Pits.RM_GrateEffects.SplashShare(Pits.RM_SpanUtility.DeckAt(map, c), p);
  ```
- failure scenario: Lay a concealed cover over a pawn already on the pit floor, then introduce toxic liquid or enough liquid to cover its head. The pawn is correctly marked `IsBeneath`, but `UnderDeck` recognizes only suspension floor-band pawns. The solid cover therefore gives it splash share zero, and `RM_PitFillEffects.Tick` skips both poisoning and drowning. Outside this part, opened `Source/Swimming/RM_Swim.cs`, which confirms that dug-cell drowning is delegated to this pass.
- confidence: high
