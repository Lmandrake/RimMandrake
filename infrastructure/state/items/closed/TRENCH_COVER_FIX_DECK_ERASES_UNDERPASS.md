## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.7)
Verdict: CONFIRMED MINOR. Trench cover GroundDepth reads 0 whenever RM_SpanUtility.DeckedAt (RM_TrenchCover.cs:44, Building_PitCover.cs:51-53), so a pawn on the hollow floor under a suspension deck (underpass feature) gets no trench cover

### GPT finding (verbatim)
### FA_core_sim_3.7 — Deck presence erases trench cover for occupants beneath an underpass
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_TrenchCover.cs:43–44,77–80` (`GroundDepthAt`, `BlockFor`)
- evidence:
  ```csharp
  int h = eng.HollowDepthAt(c);
  return RM_TrenchCoverMath.GroundDepth(h, h > 0 && Pits.RM_PitCoverUtility.IsCovered(map, c));
  ```
- failure scenario: A standing pawn occupies the dry floor beneath a suspension deck beside a raised bank. `IsCovered` makes the square read depth zero, so `BlockFor` immediately returns no trench cover, regardless of the pawn’s floor-band position. Sunken decks likewise lose their below-ground height. Outside this part, I opened `Pits/Building_PitCover.cs`: `IsCovered` delegates to `RM_SpanUtility.DeckedAt`, covering every intact deck. I also opened `Pits/Building_SpanDeck.cs` and confirmed that deck height is separately available; this caller discards it.
- confidence: high
